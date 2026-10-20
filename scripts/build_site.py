"""Build the static site into site/ from content/, data/grc/, data/hbo/ and i18n/.

Usage: python3 scripts/build_site.py [-o DIR]

Needs only the repository: the Greek words come from the committed extracts
in data/grc/ (see scripts/extract_tokens.py), so a deploy never fetches the
full sources. Every page is built in each interface language: English at
the root, the others under their codes (/es/, /fr/, /sw/, /vi/, /ko/).
"""
import argparse
import base64
import datetime
import functools
import hashlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from typing import NamedTuple  # noqa: E402

from owb import crossrefs, export, languages as owb_languages, markup, morph, refs, translit, validate, versification  # noqa: E402
from owb.export import record_verses  # noqa: E402

# The interface languages, English first (data/languages.json; see catalog below).
LANGUAGES = owb_languages.CODES
# Every book's name in each interface language and its number of chapters
# (data/books.json). All 66 are listed, so adding a book needs no edit here.
_BOOKS = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))["books"]
BOOK_NAMES = {code: {k: v for k, v in b.items() if k not in ("chapters", "chapter_names")}
              for code, b in _BOOKS.items()}
# Short names for references in tight places (data/book_abbreviations.json).
BOOK_ABBREVIATIONS = json.loads((ROOT / "data" / "book_abbreviations.json").read_text(encoding="utf-8"))["books"]
# A book whose chapters go by another name: "Psalm 23", not "Psalms 23".
CHAPTER_NAMES = {code: b["chapter_names"] for code, b in _BOOKS.items() if "chapter_names" in b}
# Chapters in each book, for "2 of 21 chapters" and a book's completeness.
BOOK_CHAPTERS = {code: b["chapters"] for code, b in _BOOKS.items()}
SITE_NAME = "Open Word Bible"
# The site's home (Render serves it on openwordbible.org and redirects www).
# Canonical links, the sitemap and link previews use it.
SITE_URL = "https://openwordbible.org"
GITHUB_URL = "https://github.com/jdegreef/open-word-bible"
# The Django API (backend/), for accounts and search. OWB_API_URL points a
# local build at a local API.
API_URL = os.environ.get("OWB_API_URL", "https://api.openwordbible.org").rstrip("/")

# The open-book mark: the favicon, and the logo in the header and footer
# (where style.css colours it from the current colour mode).
BOOK_PATH = ("M30 19C24 15.5 17 14.5 10 15.5v31c7-1 14 0 20 3.5zM34 19c6-3.5 13-4.5 20-3.5v31"
             "c-7-1-14 0-20 3.5z")
# Quotation marks on its pages, opening on the left and closing on the right:
# the book is a Word that speaks. Cut out in the tile's colour.
_QUOTE = ("M{x0} 31a3.6 3.6 0 1 0 7.2 0a3.6 3.6 0 1 0-7.2 0zM{x0} 31q0-7.5 6.6-9.8l1.2 1.7"
          "q-4.4 2.2-4.2 8.1z")
QUOTES_PATH = _QUOTE.format(x0=13.4) + _QUOTE.format(x0=21.4)
QUOTES = (f'<path class="quotes" d="{QUOTES_PATH}" fill="{{fill}}"/>'
          f'<path class="quotes" d="{QUOTES_PATH}" transform="rotate(180 32 31)" fill="{{fill}}"/>')
# Sized and filled in its own attributes too, so a page whose stylesheet has
# not loaded shows a small mark rather than a black square across the header.
MARK = (f'<svg class="mark" width="32" height="32" viewBox="0 0 64 64" aria-hidden="true">'
        f'<rect width="64" height="64" rx="14" fill="#3f3d9a"/><path d="{BOOK_PATH}" fill="#faf6ef"/>'
        f'{QUOTES.format(fill="#3f3d9a")}</svg>')


def icon(paths, size=18, cls="icon"):
    """A line icon in the header's style (24-unit grid, drawn in currentColor)."""
    return (f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{paths}</svg>')


ICONS = {
    "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    "book": '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
    "articles": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
    "cross": '<path d="M12 3v18M6 8.5h12"/>',
    "key": '<circle cx="8" cy="15" r="4.5"/><path d="m11.2 11.8 9.3-9.3M17 6l3 3M14.5 8.5l2.5 2.5"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "gift": '<path d="M20 12v9H4v-9M2 7h20v5H2zM12 21V7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7zM12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/>',
    "languages": '<path d="M5 8h8M9 5v3c0 4-2 7-5 8M7 12c1.5 2 3.5 3.5 6 4"/><path d="m13 21 4-9 4 9M14.5 18h5"/>',
    "sliders": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "scale": '<path d="M12 3v18M7 21h10M5 7h14"/><path d="m5 7-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
    "code": '<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6 6 0 0 1 3.5 6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "bookmark": '<path d="M6 3h12v18l-6-4-6 4z"/>',
    "listen": '<path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/>',
    "download": '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "feed": '<path d="M5 11a8 8 0 0 1 8 8"/><path d="M5 5a14 14 0 0 1 14 14"/><circle cx="6" cy="18" r="1"/>',
    "github": '<path d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12.3 12.3 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/>',
}


# The site's interface languages. English is served at the root and every
# other language under its own prefix (/es/...), as Ochorus does; each page
# is built once per language. Interface text lives in i18n/<lang>.json.
I18N = ROOT / "i18n"


@functools.lru_cache(maxsize=None)
def catalog(lang):
    return json.loads((I18N / f"{lang}.json").read_text(encoding="utf-8"))


def t(lang, key, **values):
    """Interface text in lang. Catalog values are trusted HTML; {name}
    placeholders are filled from values, which the caller escapes."""
    text = catalog(lang)[key]
    return text.format(**values) if values else text


def tn(lang, key, n):
    """A count in lang: key's "_one" form for one, key itself otherwise."""
    return t(lang, f"{key}_one" if n == 1 else key, n=n)


def url(lang, path):
    """A site path ("/read/") in a language: English has no prefix."""
    return path if lang == "en" else f"/{lang}{path}"


@functools.lru_cache(maxsize=None)
def asset(name):
    """The URL of a file from web/, with its content hash as a version.
    Browsers keep style.css and the scripts for hours; a new version is a
    new URL, so a deploy can never pair new pages with old styles."""
    digest = hashlib.sha256((ROOT / "web" / name).read_bytes()).hexdigest()[:10]
    return f"/{name}?v={digest}"


# Colour modes (see web/style.css and web/site.js): value, and the
# background and accent its swatch shows. Labels are in i18n/ (theme.*).
# "light" (Paper) is the default; "auto" follows the device.
COLOUR_MODES = (("auto", "#faf6ef", "#16130f"),
                ("light", "#faf6ef", "#3f3d9a"),
                ("sepia", "#f4ecd8", "#3f3d9a"),
                ("dark", "#16130f", "#9c9af2"),
                ("night", "#000000", "#e0b45c"),
                ("contrast", "#ffffff", "#000000"))

# The gear menu's settings after the colour mode (see web/style.css): name,
# default, and the values in the menu's order. A choice is kept as
# owb-<name> and applied as data-<name> on <html>. Size, font and leading
# are the reading text's; motion "auto" follows the device. They change how
# the page looks, never the text's wording. Labels are in i18n/
# (prefs.<name>, <name>.<value>).
DISPLAY_PREFS = (("size", "m", ("s", "m", "l", "xl")),
                 ("font", "serif", ("serif", "sans", "readable")),
                 ("leading", "normal", ("compact", "normal", "spacious")),
                 ("motion", "auto", ("auto", "reduce")))

# Applies the saved colour mode and display settings before the first paint,
# so a page never flashes the default colours or text. Mirrors web/site.js.
BOOT_SCRIPT = ("try{var d=document.documentElement,t=localStorage.getItem('owb-theme');"
               "if(['auto','light','sepia','dark','night','contrast'].indexOf(t)>=0)"
               "d.setAttribute('data-theme',t);"
               "var p={" + ",".join(f"{name}:{[v for v in values if v != default]!r}"
                                   for name, default, values in DISPLAY_PREFS) + "};"
               "for(var k in p){var v=localStorage.getItem('owb-'+k);"
               "if(p[k].indexOf(v)>=0)d.setAttribute('data-'+k,v)}"
               # Signed in (web/account.js): the header's "Sign in" stays hidden.
               "if(localStorage.getItem('owb.account'))d.classList.add('signed-in')"
               "}catch(e){}")

# A reader who picked a language in the footer (web/site.js keeps it as
# owb-lang) is taken to this page in that language before the first paint,
# so a link shared in English still opens in Spanish for them. Only the
# languages the page is in count, from its owb-langs meta tag: an article
# not yet translated into the reader's language stays in its own. The
# script reads the tag rather than naming the languages so that it is the
# same on every page, and the Content-Security-Policy in render.yaml can
# allow it by its hash (BOOT_SCRIPT_HASH; tests/test_headers.py).
BOOT_SCRIPT += ("try{var m=document.querySelector('meta[name=owb-langs]'),"
                "l=localStorage.getItem('owb-lang'),h=document.documentElement.lang;"
                "if(m&&l&&l!==h&&m.content.split(' ').indexOf(l)>=0){"
                "var p=h==='en'?location.pathname:location.pathname.slice(h.length+1);"
                "location.replace((l==='en'?'':'/'+l)+p+location.search+location.hash)}}catch(e){}")
BOOT_SCRIPT_HASH = "sha256-" + base64.b64encode(hashlib.sha256(BOOT_SCRIPT.encode()).digest()).decode()

# With JavaScript off, a chapter page's server-rendered disputed notes hide
# their "reasoning" buttons (only reader.js can open the reasoning). It is the
# site's one <style> element, so render.yaml's Content-Security-Policy allows
# it by its hash in style-src-elem (NOSCRIPT_STYLE_HASH; tests/test_headers.py).
NOSCRIPT_STYLE = ".disputed-note .fn-pop-more { display: none; }"
NOSCRIPT_STYLE_HASH = "sha256-" + base64.b64encode(hashlib.sha256(NOSCRIPT_STYLE.encode()).digest()).decode()


def langs_meta(translated):
    """The tag naming the languages a page is in, for the boot script."""
    return f'<meta name="owb-langs" content="{" ".join(translated)}">'

GEAR = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83'
        'l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4'
        'a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1'
        'H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06'
        'A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 '
        '1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4'
        'h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>')


def account_menu(lang):
    """Signed out, a "Sign in" button; signed in, the reader's initial,
    opening a menu with their name, the account page and signing out
    (web/site.js swaps them, from the copy of the account web/account.js
    keeps). The sign-in link gets ?redirect=<this page> when it is used."""
    return (
        '<div class="account-menu">'
        f'<a class="sign-in-btn" href="{url(lang, "/login/")}" data-login>'
        f'{icon(ICONS["user"])}<span>{t(lang, "tools.sign_in")}</span></a>'
        '<button type="button" class="tool-btn avatar-btn" aria-expanded="false" aria-controls="account-pop" '
        f'aria-label="{t(lang, "tools.your_account")}" title="{t(lang, "tools.your_account")}" hidden>'
        '<span class="account-initial"></span></button>'
        f'<div class="account-pop" id="account-pop" role="group" aria-label="{t(lang, "tools.your_account")}" hidden>'
        '<p class="who"><strong class="who-name"></strong><span class="who-email"></span></p>'
        f'<a class="pop-item" href="{url(lang, "/account/")}">{t(lang, "tools.account")}</a>'
        f'<a class="pop-item admin-link" href="/admin/" hidden>{t(lang, "tools.admin")}</a>'
        f'<button type="button" class="pop-item sign-out">{t(lang, "tools.sign_out")}</button>'
        '</div></div>')


def leading_sample(gap):
    """Three lines of text, gap apart, for a line-spacing tile."""
    ys = [13 - gap, 13, 13 + gap]
    lines = "".join(f'<line x1="2" x2="{24 if i < 2 else 16}" y1="{y}" y2="{y}"/>' for i, y in enumerate(ys))
    return ('<svg width="26" height="26" viewBox="0 0 26 26" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" aria-hidden="true">{lines}</svg>')


LEADING_GAPS = {"compact": 5, "normal": 7, "spacious": 9}


def language_menu(lang, path=None, translated=LANGUAGES):
    """The header's language switch: the page's language, opening the
    language links (language_items). Each link carries its language's own
    offer to read in it, which web/site.js shows a first-time visitor whose
    browser prefers that language."""
    label = t(lang, "footer.languages")
    items = language_items(lang, path, translated, '<span class="check" aria-hidden="true">&#10003;</span>')
    for code in LANGUAGES:
        items = items.replace(f'data-lang="{code}">', f'data-lang="{code}" data-offer="{html.escape(t(code, "lang.offer"))}" '
                                                     f'data-offer-no="{html.escape(t(code, "lang.offer_no"))}">', 1)
    return ('<div class="lang-menu">'
            f'<button type="button" class="tool-btn lang-btn" aria-expanded="false" aria-controls="lang-pop" '
            f'aria-label="{label}" title="{label}">{icon(ICONS["languages"])}<span class="lang-code">{lang.upper()}</span></button>'
            f'<div id="lang-pop" class="lang-pop" role="group" aria-label="{label}" hidden>'
            f'<ul class="prefs-langs">{items}</ul></div></div>')


def colour_menu(lang, path=None, translated=LANGUAGES):
    """The gear menu: the colour mode, the display settings (DISPLAY_PREFS),
    then the languages (language_items, as in the footer). web/site.js
    runs it."""
    label = t(lang, "tools.display")

    def option(value, default, face, name):
        on = value == default
        return (f'<button type="button" role="radio" aria-checked="{"true" if on else "false"}" '
                f'tabindex="{0 if on else -1}" data-value="{value}">'
                f'{face}{name}<span class="check" aria-hidden="true">&#10003;</span></button>')

    def group(pref, heading, default, options):
        return (f'<p class="prefs-label" id="prefs-{pref}">{heading}</p>'
                f'<div role="radiogroup" aria-labelledby="prefs-{pref}" data-pref="{pref}" data-default="{default}">'
                + "".join(option(v, default, face, name) for v, face, name in options) + '</div>')

    theme = group("theme", t(lang, "tools.theme"), "light", [
        (v, f'<span class="swatch" style="--sw-bg:{bg};--sw-accent:{accent}" aria-hidden="true"></span>',
         t(lang, "theme." + v)) for v, bg, accent in COLOUR_MODES])
    def sample(pref, value):
        if pref == "motion":
            return ""
        inner = leading_sample(LEADING_GAPS[value]) if pref == "leading" else "Aa"
        return f'<span class="sample" aria-hidden="true">{inner}</span>'

    rows = [group(pref, t(lang, "prefs." + pref), default,
                  [(v, sample(pref, v), t(lang, f"{pref}.{v}")) for v in values])
            for pref, default, values in DISPLAY_PREFS]
    check = '<span class="check" aria-hidden="true">&#10003;</span>'
    languages = (f'<p class="prefs-label" id="prefs-lang">{t(lang, "footer.languages")}</p>'
                 f'<ul class="prefs-langs" aria-labelledby="prefs-lang">{language_items(lang, path, translated, check)}</ul>')
    return (
        '<div class="prefs">'
        '<button type="button" class="tool-btn prefs-btn" aria-expanded="false" aria-controls="colour-menu" '
        f'aria-label="{label}" title="{label}">{GEAR}</button>'
        f'<div id="colour-menu" class="prefs-menu" role="group" aria-label="{label}" hidden>'
        + theme + "".join(rows) + languages + '</div></div>')


OG = ROOT / "web" / "og"


def og_card_chapter(book, chapter):
    """The name of a passage's link-preview image in web/og/ (scripts/build_og.py)."""
    return f"{book.lower()}-{chapter}"


def og_card_article(article):
    return f"article-{article['slug']}"


def page(lang, title, body, path=None, current="", description="", card="site", card_alt=None,
         translated=LANGUAGES, unlisted=None, head=""):
    """A full HTML page in lang. path is the page's URL path without the
    language ("/read/"); pages with one get a canonical link, hreflang links
    to the page in each language in translated (the languages it exists in),
    and link-preview tags, and go in the sitemap. card names the
    page's preview image in web/og/; a card not drawn yet falls back to the
    site's. card_alt says what the card shows. An unlisted page (the account
    page) has no path: it is not indexed and has no preview, but unlisted
    names its path, so the language switch still leads to it. head is more
    for the <head> (the articles page's feed link)."""
    full_title = f"{title} · {SITE_NAME}" if title != SITE_NAME else SITE_NAME
    description = description or t(lang, "meta.description")
    meta = ""
    if path is not None:
        own = html.escape(SITE_URL + url(lang, path))
        canonical = own
        alternates = "".join(
            f'\n<link rel="alternate" hreflang="{code}" href="{html.escape(SITE_URL + url(code, path))}">'
            for code in translated)
        default = url("en" if "en" in translated else translated[0], path)
        alternates += f'\n<link rel="alternate" hreflang="x-default" href="{html.escape(SITE_URL + default)}">'
        if not (OG / f"{card}.jpg").is_file():
            card, card_alt = "site", None
        card_alt = card_alt or t(lang, "meta.card_alt")
        image = html.escape(f"{SITE_URL}/og/{card}.jpg")
        meta = f"""
<link rel="canonical" href="{canonical}">{alternates}
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:type" content="website">
<meta property="og:url" content="{own}">
<meta property="og:locale" content="{lang}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{html.escape(card_alt)}">
<meta name="twitter:card" content="summary_large_image">"""
    here = path if path is not None else unlisted
    if unlisted is not None:
        meta += '\n<meta name="robots" content="noindex">'
    if here is not None:
        meta += "\n" + langs_meta(translated)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">{meta}{head}
<meta name="owb-api" content="{API_URL}">
<meta name="owb-search" content="{search_source(lang)}" data-ui="{search_ui_url(lang)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<meta name="theme-color" content="#f4eee3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#2a241c" media="(prefers-color-scheme: dark)">
<script>{BOOT_SCRIPT}</script>
<link rel="preload" href="/fonts/hanken-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/gentium-book-plus-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset("style.css")}">
<script src="{asset("site.js")}" defer></script>
<script src="{asset("search.js")}" defer></script>
</head>
<body>
<a class="skip" href="#main">{t(lang, "skip")}</a>
{site_header(lang, current, path, here, translated)}
<main class="wrap" id="main" tabindex="-1">
{body}
</main>
{site_footer(lang, here, translated)}
{palette(lang)}
</body>
</html>
"""


def languages_label(records):
    """"English · Español": the languages every sentence of a passage is in,
    each in its own name."""
    return " &middot; ".join(owb_languages.native(code) for code in LANGUAGES
                             if all(code in r["renderings"] for r in records))


MENU_ARTICLES = 4  # articles per section in the header menu
MENU_BOOKS_PER_COLUMN = 8  # a testament with more books takes two columns


@functools.lru_cache(maxsize=None)
def nav_menus(lang):
    """The header's dropdowns in lang, as [(key, label, icon, href, panel
    html)]. Built once per build and language; site_header marks the
    current one."""
    def row(href, title, note="", ico=None, ext=False):
        lead = f'<span class="dd-ico">{icon(ICONS[ico])}</span>' if ico else ""
        note = f'<span class="dd-note">{note}</span>' if note else ""
        rel = ' rel="noopener"' if ext else ""
        return (f'<a class="dd-item" href="{href}"{rel}>{lead}'
                f'<span class="dd-text"><span class="dd-title">{title}</span>{note}</span></a>')

    def all_link(href, label):
        return f'<a class="dd-all" href="{href}">{label} {icon(ICONS["arrow"], 16)}</a>'

    # Each book on one line with its progress, under its testament; its
    # chapters are one click further on, on the Read page. A testament with
    # many books takes two columns.
    def book_row(book, chaps):
        done, total, progress = book_progress(book, chaps, lang)
        return (f'<a class="dd-item dd-book" href="{url(lang, f"/read/#{book.lower()}")}" data-book="{book.lower()}">'
                f'<span class="dd-title">{BOOK_NAMES[book][lang]}</span>'
                f'<span class="dd-count" aria-hidden="true">{done}/{total}</span>'
                f'<span class="sr-only">, {progress}</span></a>')

    have = books(lang)
    testaments = []
    for key, codes in (("old_testament", refs.OT_CODES), ("new_testament", refs.BOOK_CODES[39:])):
        rows = [book_row(book, chaps) for book, chaps in have if book in codes]
        if rows:
            cols = 1 if len(rows) <= MENU_BOOKS_PER_COLUMN else 2
            testaments.append(f'<div class="dd-col" style="--cols: {cols}"><p class="dd-head">{t(lang, "footer." + key)}</p>'
                              f'<div class="dd-books">{"".join(rows)}</div></div>')
    read = (f'{resume_link(lang, "dd-resume")}<div class="dd-testaments">{"".join(testaments)}</div>'
            f'<div class="dd-alls">{all_link(url(lang, "/plans/"), t(lang, "nav.plans"))}'
            f'{all_link(url(lang, "/read/"), t(lang, "nav.all_books"))}</div>')

    # The first few articles of each section, by their short menu titles;
    # the rest are on the articles page.
    articles = sorted(load_articles(lang), key=lambda a: a["order"])
    cols = []
    for key in SECTIONS:
        section = [a for a in articles if a["section"] == key]
        if not section:
            continue
        more = (f'<a class="dd-more" href="{url(lang, "/articles/")}#{key}">'
                f'{t(lang, "nav.section_all", n=len(section))} {icon(ICONS["arrow"], 14)}</a>'
                if len(section) > MENU_ARTICLES else "")
        cols.append(f'<div class="dd-col"><p class="dd-head">{catalog(lang)["sections"][key]}</p>'
                    + "".join(row(url(lang, article_url(a)), display(a.get("nav_title") or a["title"]))
                              for a in section[:MENU_ARTICLES])
                    + f"{more}</div>")
    arts = (f'<div class="dd-cols" style="--cols: {len(cols)}">{"".join(cols)}</div>'
            f'{all_link(url(lang, "/articles/"), t(lang, "nav.all_articles"))}')

    about = ("".join((
        row(url(lang, "/about/"), t(lang, "nav.about_project"), t(lang, "nav.about_project_note"), "info"),
        row(url(lang, "/about/beliefs/"), t(lang, "nav.beliefs"), t(lang, "nav.beliefs_note"), "cross"),
        row(url(lang, "/terms/"), t(lang, "nav.terms"), t(lang, "nav.terms_note"), "key"),
        row(url(lang, "/about/#credits"), t(lang, "nav.credits"), t(lang, "nav.credits_note"), "scale"),
        row(url(lang, "/#help"), t(lang, "nav.help"), t(lang, "nav.help_note"), "users"),
        row(GITHUB_URL, t(lang, "nav.source"), t(lang, "nav.source_note"), "code", ext=True),
    )))
    # A language with no articles of its own yet has no articles menu.
    return (("read", t(lang, "nav.read"), "book", "/read/", read, "dd-read"),
            *((("articles", t(lang, "nav.articles"), "articles", "/articles/", arts, "dd-wide"),) if articles else ()),
            ("about", t(lang, "nav.about"), "info", "/about/", about, "dd-about"))


def site_header(lang, current, path=None, lang_path=None, translated=LANGUAGES):
    """Logo, the main links with their dropdowns, and the tools. On narrow
    screens the links fold into a panel behind the menu button, where each
    dropdown opens in place (web/site.js). The section trigger for current
    is lit, and the dropdown link to this page (path) is aria-current. The
    gear menu's language links go to lang_path, as the footer's do."""
    home_on = current == "/"
    home = url(lang, "/")
    items = [f'<li><a class="nav-link" href="{home}"{" aria-current=page" if home_on else ""}>'
             f'{icon(ICONS["home"])}<span>{t(lang, "nav.home")}</span></a></li>']
    for key, label, ico, href, panel, cls in nav_menus(lang):
        on = current == href
        if path:
            here = url(lang, path)
            panel = panel.replace(f'class="dd-item" href="{here}"', f'class="dd-item" href="{here}" aria-current="page"')
            panel = panel.replace(f'class="dd-all" href="{here}"', f'class="dd-all" href="{here}" aria-current="page"')
            # On a chapter page, its book in the Read menu is the current one.
            book = re.match(r"/([a-z0-9]{3})/\d+/", path)
            if book:
                panel = panel.replace(f'data-book="{book[1]}"', f'data-book="{book[1]}" aria-current="true"')
        items.append(
            f'<li class="nav-item">'
            f'<button type="button" class="nav-link nav-trigger{" active" if on else ""}" '
            f'aria-expanded="false" aria-controls="dd-{key}">'
            f'{icon(ICONS[ico])}<span>{label}</span>{icon(ICONS["chevron"], 15, "icon caret")}</button>'
            f'<div class="dropdown {cls}" id="dd-{key}" hidden>{panel}</div></li>')
    return f"""<header class="site"><div class="wrap bar">
<a class="brand" href="{home}"{" aria-current=page" if home_on else ""}>{MARK}<span class="brand-name">Open Word <em>Bible</em></span></a>
<nav class="primary" id="site-nav" aria-label="{t(lang, "nav.main")}"><ul class="nav-list">{"".join(items)}</ul></nav>
<div class="tools">
<a class="tool-btn search-btn" href="{url(lang, "/search/")}" aria-label="{t(lang, "nav.search")}" title="{t(lang, "nav.search")}" aria-keyshortcuts="Control+K Meta+K">{icon(ICONS["search"])}<span class="search-label">{t(lang, "nav.search")}</span><kbd class="search-kbd" hidden>Ctrl K</kbd></a>
{account_menu(lang)}
{language_menu(lang, lang_path, translated)}
{colour_menu(lang, lang_path, translated)}
<button type="button" class="tool-btn menu-btn" aria-expanded="false" aria-controls="site-nav" aria-label="{t(lang, "nav.menu")}">{icon(ICONS["menu"], 22)}{icon(ICONS["close"], 22)}</button>
</div>
</div></header>"""


@functools.lru_cache(maxsize=None)
def footer_links(lang):
    """The footer's link columns in lang. Built once per build and language."""
    def items(pairs):
        return "".join(f'<li><a href="{href}"{f" lang={tl}" if tl and tl != lang else ""}>{label}</a></li>'
                       for href, label, tl in pairs)

    start = sorted((a for a in load_articles(lang) if a["section"] == "method"), key=lambda a: a["order"])[:3]
    learn = [(url(lang, article_url(a)), display(a["title"]), None) for a in start]
    if start:
        learn.append((url(lang, "/articles/"), t(lang, "nav.all_articles"), None))
    learn.append((url(lang, "/terms/"), t(lang, "nav.terms"), None))
    project = [(url(lang, "/about/"), t(lang, "footer.about"), None),
               (url(lang, "/about/beliefs/"), t(lang, "nav.beliefs"), None),
               (url(lang, "/about/status/"), catalog(lang)["status"]["nav"], None),
               (url(lang, "/download/"), catalog(lang)["download"]["nav"], None),
               (url(lang, "/about/#credits"), t(lang, "nav.credits"), None),
               (url(lang, "/#help"), t(lang, "nav.help"), None),
               (GITHUB_URL, t(lang, "nav.source"), None),
               (GITHUB_URL + "/issues/new", t(lang, "footer.report"), None),
               (url(lang, "/about/privacy/"), t(lang, "nav.privacy"), None),
               (url(lang, "/about/terms-of-use/"), t(lang, "nav.terms_of_use"), None)]
    project = items(project).replace('/issues/new"', '/issues/new" data-report', 1)
    learn = f'<nav aria-labelledby="foot-learn"><h2 id="foot-learn">{t(lang, "footer.learn")}</h2><ul>{items(learn)}</ul></nav>\n'
    return (f'{learn}'
            f'<nav aria-labelledby="foot-project"><h2 id="foot-project">{t(lang, "footer.project")}</h2><ul>{project}</ul></nav>')


def book_name(book, lang):
    """A book's name in lang, drafted or not."""
    return BOOK_NAMES[book][lang]


@functools.lru_cache(maxsize=None)
def book_index(lang):
    """The footer's index of the books, by testament. A book with chapters
    in lang links to it on the Read page (dashed while some chapters are
    still missing); the books not started yet are one greyed-out chip that
    says how many, linking to the Read page, which lists them all. (Every
    page carries the footer, so naming each of them cost every page.)"""
    have = dict(books(lang))

    def chip(book):
        done, total, progress = book_progress(book, have[book], lang)
        return (f'<li><a class="book-chip{"" if done == total else " part"}" '
                f'href="{url(lang, f"/read/#{book.lower()}")}" title="{progress}">{book_name(book, lang)}</a></li>')

    def testament(key, codes):
        started = sum(b in have for b in codes)
        missing = [b for b in codes if b not in have]
        # A last book not started is named; more are counted.
        more = (f'<li><span class="book-chip none">{book_name(missing[0], lang)}'
                f'<span class="sr-only"> ({t(lang, "footer.key_none")})</span></span></li>' if len(missing) == 1 else
                f'<li><a class="book-chip none" href="{url(lang, "/read/")}">'
                f'{t(lang, "footer.not_started", n=len(missing))}</a></li>' if missing else "")
        return (f'<section class="testament" aria-labelledby="foot-{key}"><div class="testament-head">'
                f'<h3 id="foot-{key}">{t(lang, "footer." + key)}</h3>'
                f'<span>{t(lang, "footer.started", done=started, total=len(codes))}</span></div>'
                f'<ul class="book-chips">{"".join(chip(b) for b in codes if b in have)}{more}</ul></section>')

    key = "".join(f'<span><span class="book-chip{cls}" aria-hidden="true"></span>{t(lang, "footer.key_" + k)}</span>'
                  for k, cls in (("done", ""), ("part", " part"), ("none", " none")))
    return (f'<nav class="foot-books" aria-labelledby="foot-read"><h2 id="foot-read">{t(lang, "footer.read")}</h2>'
            f'<div class="testaments">{testament("old_testament", refs.OT_CODES)}'
            f'{testament("new_testament", refs.BOOK_CODES[39:])}</div>'
            f'<p class="foot-key">{key}<a href="{url(lang, "/plans/")}">{t(lang, "nav.plans")}'
            f'{icon(ICONS["arrow"], 15)}</a><a href="{url(lang, "/read/")}">{t(lang, "nav.all_books")}'
            f'{icon(ICONS["arrow"], 15)}</a></p></nav>')


def language_items(lang, path, translated=LANGUAGES, mark=""):
    """Each language in its own name, as list items: the current one as plain
    text (followed by mark) and the others as links to this page in that
    language: the home page from a page without a path, the plans or
    articles page from a plan or article not in that language, and the Read
    page from a book's page not in that language. web/site.js remembers
    the choice."""
    def target(code):
        if path is None:
            return "/"
        if code in translated:
            return path
        if path.startswith("/plans/"):
            return "/plans/"
        return "/articles/" if path.startswith("/articles/") else "/read/"

    return "".join(
        f'<li><span lang="{code}" aria-current="true">{owb_languages.native(code)}{mark}</span></li>' if code == lang
        else f'<li><a href="{url(code, target(code))}" lang="{code}" hreflang="{code}" data-lang="{code}">'
             f'{owb_languages.native(code)}</a></li>'
        for code in LANGUAGES)


def language_links(lang, path, translated=LANGUAGES):
    """The footer's language switch, as Ochorus has it (language_items)."""
    return (f'<nav class="foot-langs" aria-labelledby="foot-langs">'
            f'<h2 id="foot-langs">{t(lang, "footer.languages")}</h2>'
            f'<ul>{language_items(lang, path, translated)}</ul></nav>')


def site_footer(lang, path=None, translated=LANGUAGES):
    """The footer on every page, in three tiers: the project and a box to go
    to a passage; an index of every book; then the first articles to read,
    the project's links and the language switch."""
    home = url(lang, "/")
    placeholder = html.escape(catalog(lang)["search.ui"]["palette_placeholder"])
    return f"""<footer class="site"><div class="wrap">
<div class="foot-top">
<div class="foot-about">
<a class="brand" href="{home}">{MARK}<span class="brand-name">Open Word <em>Bible</em></span></a>
<p>{t(lang, "footer.tagline")}</p>
<p class="foot-licence"><span class="pill">CC0</span> {t(lang, "footer.licence")}</p>
</div>
<div class="foot-find">
<h2 id="foot-find">{t(lang, "footer.find")}</h2>
<form class="foot-search" action="{url(lang, "/search/")}" method="get" role="search" aria-labelledby="foot-find">
<input type="search" name="q" id="foot-q" autocomplete="off" spellcheck="false" enterkeyhint="go" placeholder="{placeholder}" aria-labelledby="foot-find">
<button class="button" type="submit">{t(lang, "footer.go")}</button>
</form>
{resume_link(lang, "foot-resume", names=True)}
</div>
</div>
{book_index(lang)}
<div class="foot-grid">
{footer_links(lang)}
{language_links(lang, path, translated)}
</div>
<div class="foot-base">
<p class="foot-review">{t(lang, "footer.review")}</p>
<p>{t(lang, "footer.licences")}</p>
</div>
</div></footer>"""


def markdown(text):
    """The small subset of Markdown that CREDITS.md uses."""
    def inline(s):
        s = html.escape(s, quote=False)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
        s = re.sub(r"&lt;(https?://[^&\s]+)&gt;", r'<a href="\1">\1</a>', s)
        return re.sub(r"(?<![\"'>])(https?://[^\s<)]+)", r'<a href="\1">\1</a>', s)

    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        if block.startswith("#"):
            level = len(block) - len(block.lstrip("#"))
            out.append(f"<h{level}>{inline(block.lstrip('#').strip())}</h{level}>")
        elif lines[0].startswith("- "):
            items, cur = [], []
            for line in lines:
                if line.startswith("- ") and cur:
                    items.append(" ".join(cur))
                    cur = []
                cur.append(line[2:] if line.startswith("- ") else line.strip())
            items.append(" ".join(cur))
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
        else:
            out.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")
    return "\n".join(out)


def alignment_links(r):
    """A record's alignments as the reader uses them: for each language and
    level, [start, end, token ids] ranges into the rendering. Curling quotes
    keeps every character in place, so the ranges hold afterwards too."""
    groups = {}
    for al in r.get("alignments", []):
        groups.setdefault((al["language"], al["level"]), []).append(al)
    links = {}
    for (lang, level), als in groups.items():
        ranges = markup.alignment_ranges(r["renderings"][lang][level], [a["target_span"] for a in als])
        links.setdefault(lang, {})[level] = [[s, e, a["tokens"]] for (s, e), a in zip(ranges, als)]
    return links


def curl_record(r):
    """The record with curly quotes in every text a reader sees. content/
    stores straight ones; curling here, the one loader, covers the reader,
    the home page and articles alike."""
    r["links"] = alignment_links(r)
    for levels in r["renderings"].values():
        for level, text in levels.items():
            levels[level] = smart_quotes(text)
    r["literal_gloss"] = smart_quotes(r["literal_gloss"])
    for d in r["decisions"]:
        d["choice"] = smart_quotes(d["choice"])
        d["alternatives"] = [smart_quotes(a) for a in d["alternatives"]]
        d["reason"] = smart_quotes(d["reason"])
    return r


def source_language(book):
    """hbo for an Old Testament book (Hebrew, with some Aramaic), grc for the New."""
    return "hbo" if book in refs.OT_CODES else "grc"


def words_path(book, chapter):
    """A chapter's word extract (scripts/extract_tokens.py)."""
    return ROOT / "data" / source_language(book) / f"{book}.{chapter}.json"


def grammar_key(word):
    """The key of a word's grammar in the reader data. Aramaic verb stems
    share letters with Hebrew ones but not names, so they are kept apart."""
    return ("A:" if word.get("lang") == "A" else "") + word["morph"]


def describe(word, lang):
    if "lang" in word:   # MACULA Hebrew
        return morph.describe_hebrew(word["morph"], lang, word["lang"])
    return morph.describe(word["morph"], lang)


# What search_documents reads of a record, and of a decision. The API's
# search rebuild (backend/translation/search.py) sets SEARCH_ONLY, so the
# records it holds keep only these: all of content/ in memory otherwise
# outgrows the API's 512 MB.
SEARCH_DECISION_KEYS = ("layer", "language", "category", "choice", "alternatives", "reason")
SEARCH_ONLY = False


def search_only(r):
    return {"id": r["id"], "refs": r["refs"], "renderings": r["renderings"],
            "decisions": [{k: d[k] for k in SEARCH_DECISION_KEYS} for d in r["decisions"]]}


@functools.lru_cache(maxsize=None)
def _book_records(book):
    """A book's records, read once, by every chapter each one touches."""
    by_chapter = {}
    for path in sorted((ROOT / "content" / book).glob("*.json")):
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
            r = curl_record(r)
            if SEARCH_ONLY:
                r = search_only(r)
            for ch in {refs.parse(v).chapter for v in r["refs"]}:
                by_chapter.setdefault(ch, []).append(r)
    return by_chapter


@functools.lru_cache(maxsize=None)
def _chapter_words(book, chapter):
    return json.loads(words_path(book, chapter).read_text(encoding="utf-8"))["verses"]


def chapter_records(book, chapter):
    """A chapter's records, in order, without its words (see load_chapter)."""
    return sorted(_book_records(book).get(chapter, []),
                  key=lambda r: refs.parse(r["refs"][0]).sort_key() + (r["id"],))


@functools.lru_cache(maxsize=None)
def chapter_verses(book, chapter):
    """The verse ids in a chapter's word extract. Listing the chapters needs
    only these: the words themselves are hundreds of megabytes for the whole
    Bible, more than the API's search rebuild has room for."""
    return tuple(json.loads(words_path(book, chapter).read_text(encoding="utf-8"))["verses"])


def load_chapter(book, chapter):
    """A chapter's records, and the Greek words of every verse they cover. A
    sentence that runs into the next chapter (John 7:53-8:1) belongs to both:
    without it the next chapter would lose a verse, and John 8 would open
    without the bracket and the note that begin the disputed passage.
    Each book is read once (a build asks for every chapter a dozen times);
    the lists are fresh, the records shared, so don't change them."""
    records = chapter_records(book, chapter)
    words = {}
    for ch in sorted({chapter} | {refs.parse(v).chapter for r in records for v in r["refs"]}):
        words.update(_chapter_words(book, ch))
    return records, words


# Pe and samekh, the codex's paragraph signs (written as escapes: Hebrew in
# this project is only ever copied from the source data).
HEBREW_PARAGRAPH = re.compile("[\u05e4\u05e1]")


def paragraph_starts(records, words):
    """The ids of the records that open a paragraph. SBLGNT marks a
    paragraph by capitalising its first word, but it also capitalises the
    start of a quotation, which follows a raised dot or a comma. So a record
    opens a paragraph when its first word is capitalised (and is not a name,
    whose dictionary form is capitalised too) and the word before it ends a
    sentence with a full stop. The Hebrew codex has no capitals; it marks a
    paragraph's end with an open or closed paragraph sign (petuchah, pe;
    setumah, samekh) after the last word, which MACULA keeps in "after".
    A chapter's first record always opens one."""
    order = [w for verse in words.values() for w in verse]
    by_id = {w["id"]: w for w in order}
    before = {b["id"]: a for a, b in zip(order, order[1:])}
    starts = []
    for i, r in enumerate(records):
        first = r["source"]["tokens"][0]
        word = by_id.get(first)
        prev = before.get(first)
        if i == 0 or prev is None or HEBREW_PARAGRAPH.search(prev["after"]) or (
                word and word["text"][:1].isupper() and word["lemma"][:1].islower()
                and prev["after"].strip().endswith(".")):
            starts.append(r["id"])
    return starts


@functools.lru_cache(maxsize=None)
def word_uses():
    """Every dictionary form in the translated sentences, with the verses it
    is in, in canonical order: the reader's "elsewhere" list for a word. As
    JSON, and its URL with a content hash, so a deploy is never served an old
    copy. Pages fetch it only when a reader taps a word."""
    uses = {}
    for book, chapter in chapters():
        records, words = load_chapter(book, chapter)
        lemma = {w["id"]: w["lemma"] for ws in words.values() for w in ws}
        verse_of = {w["id"]: vid for vid, ws in words.items() for w in ws}
        for r in records:
            for token in r["source"]["tokens"]:
                verse = verse_of.get(token)
                if token in lemma and verse:
                    uses.setdefault(lemma[token], set()).add(verse)
    # A chapter's records need not come in verse order (a passage the
    # manuscripts place differently), so sort each list.
    uses = {k: sorted(v, key=lambda vid: refs.parse(vid).sort_key()) for k, v in uses.items()}
    text = json.dumps(uses, ensure_ascii=False, separators=(",", ":"))
    return text, f"/word-uses.json?v={hashlib.sha256(text.encode()).hexdigest()[:10]}"


@functools.cache
def headings():
    """Section headings by the record they stand above (data/headings/, one
    file per book), each in the languages it has, with curly quotes."""
    return {rid: {lang: smart_quotes(text) for lang, text in h.items()}
            for path in sorted((ROOT / "data" / "headings").glob("*.json"))
            for rid, h in json.loads(path.read_text(encoding="utf-8"))["headings"].items()}


@functools.cache
def summaries():
    """Chapter summaries by (book, chapter) (data/summaries/, one file per
    book, keyed by chapter number), each in the languages it has."""
    return {(path.stem, int(ch)): {lang: smart_quotes(text) for lang, text in s.items()}
            for path in sorted((ROOT / "data" / "summaries").glob("*.json"))
            for ch, s in json.loads(path.read_text(encoding="utf-8"))["summaries"].items()}


def chapter_summary(book, chapter, records, lang):
    """The chapter's summary paragraph, or "" if it has none to show. Like a
    heading, a summary is shown in the language the text is shown in: the
    page's, or English where no sentence has the page's language yet (the
    whole chapter then reads in English)."""
    summary = summaries().get((book, chapter), {})
    shown = lang if any(lang in r["renderings"] for r in records) else "en"
    if shown not in summary:
        return ""
    return f'<p class="chapter-summary"{lang_attr(shown, lang)}>{html.escape(summary[shown])}</p>'


def chapters():
    """Every (book, chapter) with content, in canonical order."""
    found = set()
    for path in (ROOT / "content").glob("*/*.json"):
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
            for v in r["refs"]:
                ref = refs.parse(v)
                found.add((ref.book, ref.chapter))
    return sorted(found, key=lambda bc: refs.Ref(bc[0], bc[1], 1).sort_key())


class Passage(NamedTuple):
    """One chapter with content: its records, and whether every verse of the
    chapter in the word extract is translated. name is the English one;
    chapter_name gives it in another language."""
    book: str
    chapter: int
    url: str
    name: str
    records: list
    verses: int
    complete: bool


@functools.lru_cache(maxsize=None)
def passages():
    """Every chapter with content, in canonical order. Built once per build;
    the header, Read page, home page, footer and reader all list it."""
    out = []
    for b, c in chapters():
        records = chapter_records(b, c)
        verses = len(own_verses(records, c))
        total = sum(refs.parse(v).chapter == c for v in chapter_verses(b, c))
        out.append(Passage(b, c, chapter_url(b, c), chapter_name(records, b, c), records,
                           verses, verses == total))
    return tuple(out)


def passages_in(lang):
    """The chapters with sentences in lang, each holding only those
    sentences: a chapter is complete in lang only if every sentence of it
    is in lang."""
    out = []
    for p in passages():
        records = [r for r in p.records if lang in r["renderings"]]
        if len(records) == len(p.records):
            out.append(p)
        elif records:
            out.append(p._replace(records=records, verses=len(own_verses(records, p.chapter)),
                                  complete=False))
    return out


def books(lang=None):
    """The books with content, in canonical order, as (book, [Passage]);
    with lang, only the books and chapters with sentences in lang."""
    grouped = {}
    for p in (passages() if lang is None else passages_in(lang)):
        grouped.setdefault(p.book, []).append(p)
    return list(grouped.items())


def book_progress(book, chapters_, lang="en"):
    """"4 of 4 chapters, complete" / "2 of 21 chapters" / "1 chapter,
    complete" (Philemon): a book's progress."""
    done = sum(p.complete for p in chapters_)
    total = BOOK_CHAPTERS[book]
    key = "progress.one" if total == 1 else "progress.complete" if done == total else "progress.chapters"
    return done, total, t(lang, key, done=done, total=total)


def chapter_pills(chaps, lang="en", current=None, total=None):
    """A pill per chapter, linked; a dashed one for a chapter only partly
    translated, and the current chapter marked. Given the book's number of
    chapters, the ones not yet translated are shown too, greyed out."""
    def pill(p):
        return (f'<a class="chap{"" if p.complete else " part"}" href="{url(lang, p.url)}"'
                f'{" aria-current=page" if p.chapter == current else ""} '
                f'title="{html.escape(chapter_name(p.records, p.book, p.chapter, lang))}">{p.chapter}</a>')
    if total is None:
        return "".join(pill(p) for p in chaps)
    have = {p.chapter: p for p in chaps}
    missing = t(lang, "reader.not_translated")
    return "".join(pill(have[n]) if n in have else
                   f'<span class="chap none" title="{missing}" aria-label="{n}: {missing}">{n}</span>'
                   for n in range(1, total + 1))


def meter(done, total):
    """A progress meter, done of total (decorative: the text says it too)."""
    return f'<span class="meter" aria-hidden="true"><span style="width:{100 * done / total:.0f}%"></span></span>'


def chapter_url(book, chapter):
    return f"/{book.lower()}/{chapter}/"


def own_verses(records, chapter):
    """The verses of this chapter the records cover; a record that runs on
    into the next chapter (John 7:53-8:1) does not count its verses there."""
    return {v for r in records for v in r["refs"] if refs.parse(v).chapter == chapter}


def chapter_book(book, lang="en"):
    """The book's name before a chapter number: "Psalm" in "Psalm 23"."""
    return CHAPTER_NAMES.get(book, BOOK_NAMES[book])[lang]


def chapter_title(records, book, chapter, lang="en"):
    verses = [refs.parse(v).verse for v in own_verses(records, chapter)]
    return f"{chapter_book(book, lang)} {chapter}:{min(verses)}–{max(verses)}"


def chapter_name(records, book, chapter, lang="en"):
    """What the site calls a passage: "Philippians 2" for a whole chapter,
    "John 1:1–18" for part of one. (Share cards keep chapter_title.)"""
    total = len(chapter_verses(book, chapter))
    verses = own_verses(records, chapter)
    return f"{chapter_book(book, lang)} {chapter}" if len(verses) == total else chapter_title(records, book, chapter, lang)


def text_lang(record, lang):
    """The language a record is shown in on a page in lang: lang if the
    record has it yet, otherwise English, which runs ahead of the others."""
    return lang if lang in record["renderings"] else "en"


def lang_attr(text_language, lang):
    """A lang attribute for text that is not in the page's language."""
    return f' lang="{text_language}"' if text_language != lang else ""


def transliterated(verse_words, source):
    """A verse's words for the reader, each with its transliteration
    (owb.translit) for the word panel's Transliteration setting. Hebrew is
    transliterated morpheme by morpheme, in one style for the whole Old
    Testament; MACULA's own column has gaps and is not used."""
    if source == "hbo":
        latin = translit.hebrew_words(verse_words)
    else:
        latin = {w["id"]: translit.greek(w["text"]) for w in verse_words}
    return [{**{k: v for k, v in w.items() if k != "transliteration"}, "translit": latin[w["id"]]}
            for w in verse_words]


def footnote_letter(n):
    """The reader's footnote letters: a..z, then aa, ab, ... (n from 0)."""
    out = ""
    n += 1
    while n > 0:
        out = chr(97 + (n - 1) % 26) + out
        n = (n - 1) // 26
    return out


def footnote_decisions(r, lang):
    """A record's decisions with a footnote, in the reader's order: its
    meaning decisions, then lang's Balanced rendering decisions."""
    meaning = [d for d in r["decisions"] if d["layer"] == "meaning"]
    rendering = [d for d in r["decisions"] if d["layer"] != "meaning"
                 and d.get("language") == lang and "B" in d.get("levels", [])]
    return [d for d in meaning + rendering if d.get("footnote")]


def verse_range(r, chapter):
    """A record's verses as reader.js's verseRange() writes them: "12",
    "12\u201313", or "7:53\u20138:1" across a chapter break."""
    ends = [refs.parse(r["refs"][0]), refs.parse(r["refs"][-1])]
    across = ends[0].chapter != ends[1].chapter
    names = [f"{e.chapter}:{e.verse}" if across or e.chapter != chapter else str(e.verse) for e in ends]
    return names[0] if names[0] == names[1] else f"{names[0]}\u2013{names[1]}"


def note_html(d, lang):
    """A footnote's text as reader.js's noteText() writes it: the choice,
    the alternatives, and whether it is uncertain. Meaning decisions are
    written in English, so on another language's page their words say so
    (the labels between them are in the page's language)."""
    ui = catalog(lang)["reader.ui"]

    def words(text):
        text = html.escape(markup.render(text), quote=False)
        return f'<span lang="en">{text}</span>' if d["layer"] == "meaning" and lang != "en" else text

    out = words(d["choice"])
    alts = d.get("alternatives", [])
    if alts:
        label = "fn_other" if d["category"] == "text_variant" else "fn_or" if d.get("uncertain") else "also"
        out += ". " + html.escape(ui[label], quote=False) + words("; ".join(alts))
    if d.get("uncertain"):
        out += f" ({html.escape(ui['uncertain'], quote=False)})"
    return out + "."


def chapter_notes(records, chapter, lang="en"):
    """The notes section under the chapter, with its footnotes listed as
    reader.js's drawNotes() first lists them. Written into the page so the
    footnotes are there without JavaScript (and for crawlers and AI search,
    which mostly read a page as served); the reader redraws the section in
    place."""
    esc = html.escape
    label = f'aria-label="{esc(t(lang, "reader.notes"))}"'
    notes = [(r, d) for r in records for d in footnote_decisions(r, lang)]
    if not notes:
        return f'<section class="notes" id="notes" {label} hidden></section>'
    items = "".join(f'<li><span class="note"><span class="note-mark">{footnote_letter(i)}</span>'
                    f'<span class="note-ref">{esc(verse_range(r, chapter))}</span>'
                    f'<span class="note-text">{note_html(d, lang)}</span></span></li>'
                    for i, (r, d) in enumerate(notes))
    heading = esc(catalog(lang)["reader.ui"]["notes"], quote=False)
    return (f'<section class="notes" id="notes" {label}><div class="notes-head">'
            f'<h2>{heading}</h2></div><ol>{items}</ol></section>')


def chapter_text(records, chapter, paragraphs, disputed_info, lang="en"):
    """The chapter as reader.js's drawText() first draws it: Balanced, every
    setting at its default, headings shown, Study view. Written into the
    page so it has its text without JavaScript (and for crawlers); the
    reader redraws the same markup in place. Each sentence is in lang, or
    in English while it has no lang yet (text_lang)."""
    def verse_of(vid):
        ref = refs.parse(vid)
        return str(ref.verse) if ref.chapter == chapter else f"{ref.chapter}:{ref.verse}"

    def marker_verse(r, n):
        vid = next((v for v in r["refs"] if refs.parse(v).verse == int(n)), None)
        return verse_of(vid) if vid else n

    esc = html.escape
    starts = set(paragraphs)
    disputed_ids = set(disputed_info["records"]) if disputed_info else set()
    ui = catalog(lang)["reader.ui"]
    out, para, shown, in_disputed, notes = [], None, None, False, 0

    def close():
        if para is not None:
            out.append("".join(para) + "</p>")

    for r in records:
        if (r["id"] in disputed_ids) != in_disputed:
            close()
            para = None
            in_disputed = not in_disputed
            if in_disputed:
                note = ui["disputed_note"].replace("{ref}", disputed_info["ref"])
                # The reader's button to the note's reasoning, so the text
                # below does not move when it is drawn; it does nothing
                # without JavaScript, and is hidden then (chapter_page).
                why = (f'<button type="button" class="fn-pop-more">{esc(ui["fn_reasoning"], quote=False)} \u2192</button>'
                       if disputed_info["note"] else "")
                out.append(f'<div class="disputed-block"><div class="disputed-note"><p>{esc(note, quote=False)}</p>{why}</div>')
            else:
                out.append("</div>")
        heading = headings().get(r["id"])
        tl = text_lang(r, lang)
        hlang = next((code for code in (lang, tl) if heading and heading.get(code)), None)
        if hlang:
            close()
            para = None
            cls = "section-head" + ("" if hlang == lang else " fallback")
            out.append(f'<h2 class="{cls}"{lang_attr(hlang, lang)}>{esc(markup.render(heading[hlang]), quote=False)}</h2>')
        if para is None or heading or r["id"] in starts:
            close()
            para = ['<p class="para">']
        # Footnote letters, counted through the page as the reader counts them.
        marks = []
        for _ in footnote_decisions(r, lang):
            marks.append(footnote_letter(notes))
            notes += 1
        parts = markup.VERSE.split(r["renderings"][tl]["B"])
        verses = [(verse_of(r["refs"][0]), parts[0].lstrip())]
        verses += [(marker_verse(r, n), text) for n, text in zip(parts[1::2], parts[2::2])]
        cls = "verse" if tl == lang else "verse fallback"
        for i, (v, text) in enumerate(verses):
            sup = f"<sup>{esc(v)}</sup>" if v != shown else ""
            shown = v
            fn = ""
            if marks and i == len(verses) - 1:
                fn = ('<sup class="fn" aria-hidden="true">'
                      + "".join(f'<span class="fn-mark">{m}</span>' for m in marks) + "</sup>")
            para.append(f'<span class="{cls}"{lang_attr(tl, lang)} data-v="{esc(v)}" data-record="{esc(r["id"])}">'
                        f'{sup}{esc(markup.render(text), quote=False)}{fn}</span> ')
    close()
    if in_disputed:
        out.append("</div>")
    return "".join(out)


# The text each testament is translated from, for the pages' linked data.
SOURCE_TEXTS = {
    "grc": {"@type": "Book", "name": "SBL Greek New Testament (SBLGNT)", "inLanguage": "grc",
            "url": "https://github.com/LogosBible/SBLGNT"},
    "hbo": {"@type": "Book", "name": "Westminster Leningrad Codex (Open Scriptures Hebrew Bible)",
            "inLanguage": "hbo", "url": "https://github.com/openscriptures/morphhb"},
}
CC0_URL = "https://creativecommons.org/publicdomain/zero/1.0/"


def chapter_ld(records, book, chapter, title, lang="en"):
    """schema.org data for a chapter page, as a script element."""
    source = SOURCE_TEXTS[source_language(book)]
    data = {
        "@context": "https://schema.org",
        "@type": "Chapter",
        "name": title,
        "url": SITE_URL + url(lang, chapter_url(book, chapter)),
        "inLanguage": lang,
        "isPartOf": {"@type": "Book", "name": SITE_NAME, "url": SITE_URL + url(lang, "/"),
                     "license": CC0_URL},
        "license": CC0_URL,
        # Nothing is reviewed until a named human reviewer approves it.
        "creativeWorkStatus": "Draft" if any(r["status"] == "ai_draft" for r in records) else "Published",
        "translationOfWork": source,
        "isBasedOn": source,
    }
    return ld_script(data)


def ld_script(data):
    """schema.org data as a script element. Every "<" is written as an
    escape, so nothing in it can close the element."""
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{text}</script>'


ORGANIZATION = {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL}


def page_records(records, lang):
    """The records as a page in lang carries them: every language's
    renderings (the reader sets two side by side), but only the meaning
    decisions and lang's own rendering decisions, the only ones the reader
    shows. Each language's decisions would otherwise weigh on every page.
    The source is left out: it is the same on every language's page, so it
    comes with the chapter's shared data (chapter_shared)."""
    return [{**{k: v for k, v in r.items() if k != "source"},
             "decisions": [d for d in r["decisions"] if d["language"] in (None, lang)]}
            for r in records]


# The reader data that is the same on every language's page of a chapter,
# one script a chapter (chapter_shared), and the reader data that is the
# same on every chapter page of a language, one script a language
# (reader_shared). A page loads both before reader.js, which adds them to
# the page's own data. Built into every page, they were most of the site:
# the words alone were six copies of about 100 MB.
CHAPTER_DATA_DIR = "chapter-data"


def shared_script(name, data):
    """A script that sets window.<name> to data, and a content hash for its
    URL, so a page is never paired with another deploy's copy."""
    text = (f"window.{name}="
            + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n")
    return text, hashlib.sha256(text.encode()).hexdigest()[:10]


def chapter_data_path(book, chapter):
    return f"/{CHAPTER_DATA_DIR}{chapter_url(book, chapter).rstrip('/')}.js"


@functools.cache
def chapter_shared(book, chapter):
    """A chapter's reader data in no language: the source words of each
    verse, each sentence's source and the cross-references. As a script,
    and its URL."""
    records, words = load_chapter(book, chapter)
    source = source_language(book)
    text, digest = shared_script("OWB_CHAPTER", {
        "words": {vid: transliterated(words[vid], source) for r in records for vid in r["refs"]},
        "sources": {r["id"]: r["source"] for r in records},
        "crossrefs": chapter_crossrefs(records)})
    return text, f"{chapter_data_path(book, chapter)}?v={digest}"


@functools.cache
def reader_shared(lang):
    """A language's reader data for every chapter: the reader's interface
    text, the book names notes link by (book_refs) and the names before a
    chapter number. As a script, and its URL."""
    text, digest = shared_script("OWB_LANG", {
        "ui": catalog(lang)["reader.ui"],
        "bookRefs": book_refs(lang),
        # Names before a chapter number ("Psalm 23:1"), for "Book 1:2" links.
        "books": {b: chapter_book(b, lang) for b, _ in books()}})
    return text, f"/reader-{lang}.js?v={digest}"


def chapter_data_files():
    """{path: text} of every chapter's and every language's shared reader
    data (chapter_shared, reader_shared)."""
    files = {chapter_data_path(b, c).lstrip("/"): chapter_shared(b, c)[0] for b, c in chapters()}
    files.update({f"reader-{lang}.js": reader_shared(lang)[0] for lang in LANGUAGES})
    return files


def chapter_page(book, chapter, lang="en"):
    records, words = load_chapter(book, chapter)
    title = chapter_name(records, book, chapter, lang)
    # Every language any sentence has: English may run ahead of the others,
    # and the reader shows a sentence not yet translated in English.
    languages = [code for code in LANGUAGES
                 if any(code in r["renderings"] for r in records)]
    source = source_language(book)
    # What is the same on other pages comes in chapter_shared and reader_shared.
    data = {"book": book, "chapter": chapter, "title": title, "lang": lang, "languages": languages,
            "source": source, "records": page_records(records, lang),
            "paragraphs": paragraph_starts(records, words),
            "disputed": disputed_block(records, lang),
            "compare": comparison_verses(records, lang),
            "cards": word_cards(records, words, lang),
            "headings": {r["id"]: headings()[r["id"]] for r in records if r["id"] in headings()},
            # Where previews of other verses come from (verse_files), and the
            # comparison edition for verses not translated yet: the page
            # language's, then the World English Bible.
            "compare_url": compare_url(lang),
            # Signing in to send a suggestion or question (reader.js noteBox).
            "login": url(lang, "/login/"),
            "word_url": word_url(lang),
            "verses": {"url": f"/{VERSES_DIR}/",
                       "compare": [list(COMPARISON.get(lang, COMPARISON_DEFAULT)), list(COMPARISON_DEFAULT)]}}
    # Each morphology code's description in every language, once per page.
    data["uses"] = word_uses()[1]
    data["saved"] = url(lang, "/saved/")
    # The reader shows a word's grammar in the page's language only.
    data["grammar"] = {grammar_key(w): {lang: describe(w, lang)}
                       for r in records for vid in r["refs"] for w in words[vid]}
    # "</" cannot appear inside a script element.
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    # Without JavaScript (and for crawlers) the page still has its text.
    text = chapter_text(records, chapter, data["paragraphs"], data["disputed"], lang)
    partial = any(lang not in r["renderings"] for r in records)

    def seg(name, options):
        buttons = "".join(f'<button type="button" data-value="{v}">{label}</button>' for v, label in options)
        return f'<span class="seg" data-setting="{name}">{buttons}</span>'

    def control(key, name, options, cls=""):
        return f'<div class="control{cls}"><span>{t(lang, "reader." + key)}</span> {seg(name, options)}</div>'

    # Old Testament pages name the Hebrew where New Testament ones name the Greek.
    suffix = "_hbo" if source == "hbo" else ""
    # The Old Testament has the divine name (the LORD or Yahweh); the New
    # Testament has the title Christ (Christ or Messiah).
    if source == "hbo":
        title_setting = "divine_name"
        title_control = control("name", "divine_name", [("0", t(lang, "reader.lord")), ("1", t(lang, "reader.yahweh"))])
    else:
        title_setting = "christos"
        title_control = control("title", "christos", [("0", t(lang, "reader.christ")), ("1", t(lang, "reader.messiah"))])
    levels = catalog(lang)["levels"]
    # Reader settings whose control only some languages have (data/languages.json).
    own = owb_languages.settings(lang)
    plural = ("\n  " + control("plural", "plural_you", list(enumerate(own["plural_you"])))
              if "plural_you" in own else "")
    # Measures (modern or original units) only where a passage has them.
    has_units = any("{{units:" in text for r in records
                    for levels_ in r["renderings"].values() for text in levels_.values())
    units = ("\n  " + control("measures", "units", [("0", t(lang, "reader.modern")),
                                                     ("1", t(lang, "reader.original"))])
             if has_units else "")
    body = f"""
<button type="button" class="settings-toggle" id="settings-toggle" aria-expanded="false" aria-controls="settings">
  <span>{t(lang, "reader.settings")}</span> <span class="settings-summary" id="settings-summary"></span>
</button>
<div class="settings" id="settings">
<div class="controls">
  {control("level", "level", [(code, levels[code]) for code in "LBR"])}
  <div class="wording-wrap">
  <button type="button" class="wording-toggle" id="wording-toggle" aria-expanded="false" aria-controls="wording">
    <span class="wording-label">{t(lang, "reader.wording")}</span> <span class="wording-summary" id="wording-summary"></span>
  </button>
  <div class="wording" id="wording">
  {control("gender", "gender", [("0", t(lang, "reader.inclusive")), ("1", t(lang, "reader.traditional"))])}
  {title_control}
  {control("pronouns", "deity_pronoun", [("0", t(lang, "reader.he")), ("1", t(lang, "reader.He"))])}{units}{plural}
  {control("headings", "headings", [("0", t(lang, "reader.show")), ("1", t(lang, "reader.hide"))])}
  {control("crossrefs", "crossrefs", [("0", t(lang, "reader.show")), ("1", t(lang, "reader.hide"))])}
  </div>
  </div>
  {control("view", "view", [("0", t(lang, "reader.study")), ("1", t(lang, "reader.reading")),
                            ("2", t(lang, "reader.parallel")), ("3", t(lang, "reader.interlinear"))], " view-control")}
</div>
<p class="hint"><span id="hint-level"></span> <span id="hint-gender"></span> <span id="hint-{title_setting}"></span> <span id="hint-deity_pronoun"></span> <span id="hint-units"></span> <span id="hint-plural_you"></span> <span id="hint-headings"></span> <span id="hint-crossrefs"></span> <span id="hint-view"></span></p>
</div>
<div class="reader">
  <article class="passage">
    {chapter_strip(book, chapter, lang)}
    <h1 id="title">{html.escape(title)}</h1>
    {chapter_summary(book, chapter, records, lang)}
    <p class="print-only print-head" id="print-head"></p>
    <p class="sub">{t(lang, "reader.sub" + suffix)}</p>
    <p class="notice" id="partial"{"" if partial else " hidden"}>{html.escape(catalog(lang)["reader.ui"]["partial"]) if partial else ""}</p>
    <noscript><p class="notice">{t(lang, "reader.noscript", level=levels["B"])}</p><style>{NOSCRIPT_STYLE}</style></noscript>
    <div class="xr-margin" id="xr-margin"></div>
    <div class="text" id="text">{text}</div>
    {chapter_notes(records, chapter, lang)}
    {plan_bar(book, chapter, lang)}
    {chapter_turns(book, chapter, lang)}
    {chapter_articles_html(book, chapter, lang)}
  </article>
  <aside class="panel" id="panel" aria-live="polite" tabindex="-1"></aside>
</div>
{edge_turns(book, chapter, lang)}
<script type="application/json" id="owb-data">{blob}</script>
{chapter_ld(records, book, chapter, title, lang)}
{breadcrumb_ld(lang, book_crumbs(book, lang) + [(title, chapter_url(book, chapter))])}
<script src="{reader_shared(lang)[1]}"></script>
<script src="{chapter_shared(book, chapter)[1]}"></script>
<script src="{asset("markup.js")}"></script>
<script src="{asset("reader.js")}"></script>
{plans_script()}
"""
    return page(lang, title, body, path=chapter_url(book, chapter), current="/read/",
                card=og_card_chapter(book, chapter),
                card_alt=t(lang, "meta.chapter_card_alt" + suffix, title=title,
                           verse=opening_verse(records, chapter, lang)),
                description=t(lang, "meta.chapter_description" + suffix, title=title))


def chapter_crossrefs(records):
    """The cross-references of every verse on a chapter page (owb/crossrefs.py),
    by verse id, most voted first; the reader shows them in the margin."""
    out = {}
    for r in records:
        for vid in r["refs"]:
            found = crossrefs.load(vid.split(".")[0]).get(vid)
            if found:
                out[vid] = found
    return out


def reader_passages(book, chapter, lang="en"):
    """The passages a reader page in lang links to: those with sentences in
    lang, or every passage on a page not yet in lang, which is shown in
    English."""
    ps = passages_in(lang)
    if any((p.book, p.chapter) == (book, chapter) for p in ps):
        return ps
    return list(passages())


# A book's introduction: data/intros/<BOOK>.md in English and
# data/intros/<lang>/<BOOK>.md in another language, each with a front
# matter block holding its summary, then Markdown as in an article. A book
# has a page (/<book>/) in each language its introduction is written in.
INTROS = ROOT / "data" / "intros"


@functools.lru_cache(maxsize=None)
def load_intro(book, lang="en"):
    """A book's introduction in lang ({"summary", "body"}), or None."""
    path = (INTROS if lang == "en" else INTROS / lang) / f"{book}.md"
    if not path.is_file():
        return None
    m = re.match(r"---\nsummary: (.*?)\n---\n(.*)", path.read_text(encoding="utf-8"), re.S)
    if not m:
        raise SystemExit(f"{path.name}: needs a front matter block with its summary")
    return {"summary": smart_quotes(m[1]), "body": m[2]}


def book_url(book):
    return f"/{book.lower()}/"


@functools.lru_cache(maxsize=None)
def book_languages(book):
    """The languages a book's page is built in: those its introduction is
    written in and that have some of its chapters."""
    return tuple(code for code in LANGUAGES
                 if load_intro(book, code) and any(b == book for b, _ in books(code)))


def breadcrumb_ld(lang, crumbs):
    """schema.org data for the trail to a page: (name, path) pairs from the
    home page down, the page itself last."""
    return ld_script({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": name, "item": SITE_URL + url(lang, path)}
        for i, (name, path) in enumerate(crumbs, 1)]})


def book_crumbs(book, lang):
    """The trail to a book: the home page, Read, then the book where it has
    a page."""
    crumbs = [(SITE_NAME, "/"), (t(lang, "read.title"), "/read/")]
    if lang in book_languages(book):
        crumbs.append((BOOK_NAMES[book][lang], book_url(book)))
    return crumbs


def book_page(book, lang="en"):
    """A book: its introduction, an outline of its chapters from the section
    headings, and the articles that read it. Like the translation, the
    introduction is a draft until a named reviewer has checked it."""
    intro = load_intro(book, lang)
    ui = catalog(lang)["book_page"]
    name = BOOK_NAMES[book][lang]
    chaps = dict(books(lang))[book]
    outline = []
    for p in chaps:
        heads = [markup.render(headings()[r["id"]][lang]) for r in p.records
                 if r["id"] in headings() and headings()[r["id"]].get(lang)]
        sections = f'<span class="outline-heads">{html.escape(" · ".join(heads))}</span>' if heads else ""
        outline.append(f'<li><a href="{url(lang, chapter_url(book, p.chapter))}">'
                       f'{html.escape(ui["chapter"].replace("{n}", str(p.chapter)))}</a>{sections}</li>')
    articles = [a for a in sorted(load_articles(lang), key=lambda a: a["order"])
                if any(b == book for b, _, _ in a["passages"])]
    more = (f'<section class="more" aria-labelledby="book-articles-h"><h2 id="book-articles-h">'
            f'{html.escape(ui["articles"].replace("{book}", name))}</h2>'
            f'<ul class="a-grid">{article_list(articles, lang)}</ul></section>' if articles else "")
    body = f"""
<div class="book-layout">
<article class="article book-intro">
<header class="article-head">
<p class="eyebrow"><a href="{url(lang, "/read/")}">{t(lang, "read.title")}</a></p>
<h1>{html.escape(name)}</h1>
<p class="dek">{display(intro["summary"])}</p>
<p class="notice">{ui["draft"]}</p>
<p class="actions"><a class="button" href="{url(lang, chapter_url(book, chaps[0].chapter))}">{ui["start"]}&nbsp;&rarr;</a></p>
</header>
<div class="article-body">
{article_html(intro["body"], None, lang, lang)}
</div>
<section aria-labelledby="book-chapters-h">
<h2 id="book-chapters-h">{ui["chapters"]}</h2>
<ol class="book-outline">{"".join(outline)}</ol>
</section>
</article>
</div>
{more}
{breadcrumb_ld(lang, book_crumbs(book, lang))}
"""
    return page(lang, ui["title"].replace("{book}", name), body, path=book_url(book), current="/read/",
                description=intro["summary"], translated=book_languages(book))


def chapter_strip(book, chapter, lang="en"):
    """Above a passage: its book, how far the book has got, and a pill for
    each chapter translated so far, this one marked."""
    chaps = [p for p in reader_passages(book, chapter, lang) if p.book == book]
    name = BOOK_NAMES[book][lang]
    progress = book_progress(book, chaps, lang)[2]
    return (f'<nav class="chapstrip" aria-label="{t(lang, "reader.strip", book=name)}">'
            f'<a class="chap-book" href="{url(lang, book_url(book) if lang in book_languages(book) else f"/read/#{book.lower()}")}">'
            f'{icon(ICONS["book"], 16)}{name}</a>'
            f'<span class="chap-pills">{chapter_pills(chaps, lang, chapter, BOOK_CHAPTERS[book])}</span>'
            f'<button type="button" class="chap-goto" data-open-search aria-keyshortcuts="/">'
            f'{icon(ICONS["search"], 15)}{t(lang, "reader.goto")}</button>'
            f'<button type="button" class="chap-goto chap-listen" id="listen-start" hidden>'
            f'{icon(ICONS["listen"], 15)}{t(lang, "reader.listen")}</button>'
            f'<span class="chap-progress">{progress}</span></nav>')


def neighbours(book, chapter, lang="en"):
    """The passages before and after this one in lang, across books (None
    at the ends); see reader_passages."""
    ps = reader_passages(book, chapter, lang)
    i = next(n for n, p in enumerate(ps) if (p.book, p.chapter) == (book, chapter))
    return (ps[i - 1] if i > 0 else None), (ps[i + 1] if i + 1 < len(ps) else None)


def edge_turns(book, chapter, lang="en"):
    """Arrows at the sides of the window on wide screens, for the previous
    and next passages; the reader's arrow keys follow them (web/reader.js)."""
    prev, nxt = neighbours(book, chapter, lang)

    def arrow(p, rel, label, glyph):
        if p is None:
            return ""
        name = html.escape(chapter_name(p.records, p.book, p.chapter, lang))
        return (f'<a class="edge-turn {rel}" href="{url(lang, p.url)}" data-turn="{rel}" '
                f'aria-label="{plain_label(label)}: {name}" title="{name}">{glyph}</a>')

    return (arrow(prev, "prev", t(lang, "reader.prev"), "&lsaquo;")
            + arrow(nxt, "next", t(lang, "reader.next"), "&rsaquo;"))


def plain_label(label):
    """A button label without its arrow entity, for an aria-label."""
    return re.sub(r"\s*&[lr]arr;\s*", "", label)


def chapter_turns(book, chapter, lang="en"):
    """Below a passage: the previous and next passages, across books."""
    prev, nxt = neighbours(book, chapter, lang)

    def turn(p, rel, label):
        if p is None:
            return '<span class="turn-gap"></span>'
        return (f'<a class="turn {rel}" href="{url(lang, p.url)}" rel="{rel}">'
                f'<span class="turn-label">{label}</span>'
                f'<span class="turn-name">{display(chapter_name(p.records, p.book, p.chapter, lang))}</span></a>')

    return (f'<nav class="turns" aria-label="{t(lang, "reader.turns")}">'
            f'{turn(prev, "prev", t(lang, "reader.prev"))}{turn(nxt, "next", t(lang, "reader.next"))}</nav>')


# Passages whose place in the text is disputed, translated in [square
# brackets] (docs/john-terms.md), as (first verse, last verse). A chapter's
# cards quote the first verse outside them.
DISPUTED = (("JHN.7.53", "JHN.8.11"),)


def disputed(vid):
    key = refs.parse(vid).sort_key()
    return any(refs.parse(a).sort_key() <= key <= refs.parse(b).sort_key() for a, b in DISPUTED)


@functools.lru_cache(maxsize=None)
def name_cards():
    """data/names.json (people, places and peoples), by (Strong's number,
    lemma). Each has one or more senses; a sense with "verses" is the one
    for those verses, a sense without is the one for every other verse."""
    path = ROOT / "data" / "names.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {(n["strong"], n["lemma"]): n["senses"] for n in data["names"]}


def word_strong(word):
    """A word's Strong's number as names.json keys it: G or H and digits."""
    prefix = "H" if word["id"].startswith("o") else "G"
    return prefix + (word.get("strong") or "").lstrip("0")


def term_english(term):
    """A key term's settled English words, every level's, without repeats:
    what the reader's card says it is always rendered by."""
    allowed = term["english"]
    words = [w for level in validate.LEVELS for w in allowed.get(level, [])] if isinstance(allowed, dict) else allowed
    return list(dict.fromkeys(words))


def term_card_rule(term, lang):
    """What a reader's card says of a key term whose English differs by
    level (gospel): each level's words, levels with the same words together."""
    ui, levels = catalog(lang)["reader.ui"], catalog(lang)["levels"]
    groups = {}
    for level in validate.LEVELS:
        groups.setdefault(tuple(term["english"].get(level, [])), []).append(levels[level])
    parts = "; ".join(ui["card_term_level"].format(levels=", ".join(names), words=", ".join(words))
                      for words, names in groups.items() if words)
    return ui["card_term_levels"].format(words=parts)


def word_cards(records, words, lang="en"):
    """The key terms and the people, places and peoples among this page's
    words: {"list": [card, ...], "tokens": {token id: index into list}}.
    A key term is found by its Strong's number and source language, as
    owb.validate checks it, and its card links to the term's page. A name
    used of more than one person resolves to the sense for its verse."""
    names = name_cards()
    mine = {t for r in records for t in r["source"]["tokens"]}
    cards, index, tokens = [], {}, {}
    for vid, ws in words.items():
        for w in ws:
            if w["id"] not in mine:
                continue
            card = None
            term = validate.key_term(w["id"], w.get("strong") or "")
            if term:
                key = ("term", term_key(term))
                card = {"type": "term", "lemma": term["lemma"], "title": term["sense"],
                        "english": term_english(term), "note": term.get("note", ""),
                        "href": url(lang, term_path(term))}
                if isinstance(term["english"], dict):
                    card["rule"] = term_card_rule(term, lang)
            senses = names.get((word_strong(w), w["lemma"]))
            if senses and not card:
                sense = next((s for s in senses if vid in s.get("verses", [])), None) \
                    or next((s for s in senses if "verses" not in s), None)
                if sense:
                    key = ("name", w["lemma"], sense["name"])
                    card = {"type": "name", "lemma": w["lemma"], "title": sense["name"],
                            "kind": sense["kind"], "note": sense["note"]}
            if card:
                if key not in index:
                    index[key] = len(cards)
                    cards.append(card)
                tokens[w["id"]] = index[key]
    return {"list": cards, "tokens": tokens}


@functools.lru_cache(maxsize=None)
def book_refs(lang="en"):
    """What the reader needs to link "Mark 14:54" in a note: every book's
    names (English, which the notes are written in, and this language's)
    and the chapters translated so far, which link into the reader; others
    go to search, which says they are not translated yet."""
    names = {}
    for code, name in refs.BOOK_NAMES.items():
        names[name] = code
        local = BOOK_NAMES.get(code, {}).get(lang)
        if local:
            names[local] = code
        # The name before a chapter number too: "Psalm 2:7".
        # In a fixed order: the reader's data is a file named by its hash.
        for form in dict.fromkeys((chapter_book(code), chapter_book(code, lang))):
            names[form] = code
    chapters = {b: sorted(p.chapter for p in ps) for b, ps in books()}
    # For the quotation tags in the text: each book's short name and the
    # name it says in full ("Deut", "Deuteronomy").
    abbr = {code: [forms.get(lang) or chapter_book(code, lang), chapter_book(code, lang)]
            for code, forms in BOOK_ABBREVIATIONS.items()}
    return {"names": names, "chapters": chapters, "search": url(lang, "/search/"), "abbr": abbr}


# A note's reference to a chapter not translated yet shows that verse from a
# public-domain Bible for comparison (data/comparison/, written by
# scripts/extract_comparison.py): the Reina-Valera 1909 on Spanish pages,
# the World English Bible elsewhere. Never Open Word Bible wording.
COMPARISON = {"es": ("rv1909", "Reina-Valera 1909", "es")}
COMPARISON_DEFAULT = ("web", "World English Bible", "en")
# A range in a note ("9:9-15") brings at most this many verses.
COMPARE_MAX_VERSES = 4


@functools.lru_cache(maxsize=None)
def comparison_text(code):
    path = ROOT / "data" / "comparison" / f"{code}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


@functools.lru_cache(maxsize=None)
def ref_pattern(lang):
    """The reader's pattern for "Mark 14:54" or "2 Corinthians 7:9-10" in a
    note (refPattern in reader.js), over the same book names."""
    names = sorted(book_refs(lang)["names"], key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r") (\d+):(\d+)(?:[-–](\d+))?")


def note_texts(record):
    """Every note text the reader links references in: each decision's
    choice, alternatives and reason."""
    for d in record["decisions"]:
        yield d["choice"]
        yield from d["alternatives"]
        yield d["reason"]


def comparison_verses(records, lang="en"):
    """The comparison text for the verses this page's notes name in chapters
    not translated yet, and the edition's name: {"name", "verses":
    {"DEU.25.4": text}, "lang"}. Only the verses the notes need, so the
    page stays small; None when there are none."""
    have = book_refs(lang)["chapters"]
    names = book_refs(lang)["names"]
    code, name, compare_lang = COMPARISON.get(lang, COMPARISON_DEFAULT)
    text = comparison_text(code)
    if not text:
        code, name, compare_lang = COMPARISON_DEFAULT
        text = comparison_text(code)
    verses = {}
    for r in records:
        for note in note_texts(r):
            for m in ref_pattern(lang).finditer(note):
                book, chapter, first = names[m[1]], int(m[2]), int(m[3])
                if chapter in have.get(book, []):
                    continue
                last = int(m[4]) if m[4] and int(m[4]) > first else first
                for v in range(first, min(last, first + COMPARE_MAX_VERSES - 1) + 1):
                    vid = f"{book}.{chapter}.{v}"
                    if vid in text:
                        verses[vid] = text[vid]
    return {"name": name, "lang": compare_lang, "verses": verses} if verses else None


def disputed_block(records, lang="en"):
    """The reader's view of a disputed passage on this page: its records, its
    reference, and the manuscript-reading decision that explains it (shown
    from the note above the passage). None when the page has none."""
    ids = [r["id"] for r in records if any(disputed(v) for v in r["refs"])]
    if not ids:
        return None
    first = next(r for r in records if r["id"] == ids[0])
    note = next((d["id"] for d in first["decisions"] if d["category"] == "text_variant"), None)
    a, b = next((refs.parse(x), refs.parse(y)) for x, y in DISPUTED if disputed(first["refs"][0]))
    span = f"{a.chapter}:{a.verse}\u2013" + (f"{b.verse}" if a.chapter == b.chapter else f"{b.chapter}:{b.verse}")
    return {"records": ids, "ref": f"{BOOK_NAMES[a.book][lang]} {span}", "note": note}


def psalm_title(vid):
    """True for a verse that is only a psalm's title ("A psalm of David ..."),
    which the Hebrew text counts as a verse and English Bibles do not number.
    A chapter's cards quote the psalm itself."""
    return not versification.to_english(refs.parse(vid))


def opening(records, chapter):
    """(record, verse id) for the verse a chapter's cards quote: its first
    verse outside a disputed passage and not a psalm's title, or its first
    verse if every one is skipped."""
    first = None
    for r in records:
        for vid in r["refs"]:
            if refs.parse(vid).chapter == chapter:
                if not disputed(vid) and not psalm_title(vid):
                    return r, vid
                first = first or (r, vid)
    return first


def opening_verse(records, chapter, lang="en"):
    """A passage's opening verse (see opening), Balanced, at the default
    settings: what its Read-page card and its share card quote. In English
    when that sentence is not yet in lang."""
    return verse_text(*opening(records, chapter), lang)


# Previews of other verses (web/reader.js, cross-references): one small file
# per chapter, /verses/<BOOK>/<chapter>.json, fetched only when a reader
# points at a reference into it. Our text at every level, in every language
# it has, with its reader-setting spans and poetry lines kept so the preview
# follows the reader's settings; a verse we have not translated yet has the
# comparison text instead (data/comparison/), in our verse numbering and
# labelled as not ours by the reader.
#   {"v": {"16": {"en": {"L": ..., "B": ..., "R": ...}, ...}},
#    "c": {"web": {"17": "..."}, "rv1909": {"17": "..."}}}
VERSES_DIR = "verses"
COMPARISON_EDITIONS = ("web", "rv1909")


@functools.cache
def comparison_ours(code):
    """A comparison edition's verses by our verse Ref (owb/versification.py):
    English Psalm 3:1 is our PSA.3.2; two English verses that make one of
    ours are joined."""
    moved = {}
    for eid, text in comparison_text(code).items():
        for ref in versification.to_source(refs.parse(eid)):
            moved[ref] = f"{moved[ref]} {text}" if ref in moved else text
    return moved


def verse_files():
    """{path: text} for every chapter of the Bible (see VERSES_DIR)."""
    ours, seen = {}, set()
    for book, chapter in chapters():
        for r in chapter_records(book, chapter):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            for vid, langs in record_verses(r).items():
                into = ours.setdefault(vid, {})
                for lang, levels in langs.items():
                    # Two sentences in one verse (Philippians 4:5): one text.
                    have = into.setdefault(lang, {})
                    for level, text in levels.items():
                        have[level] = f"{have[level]} {text}" if level in have else text
    by_chapter = {}
    for vid, langs in ours.items():
        ref = refs.parse(vid)
        by_chapter.setdefault((ref.book, ref.chapter), {"v": {}})["v"][str(ref.verse)] = langs
    for code in COMPARISON_EDITIONS:
        for ref, text in comparison_ours(code).items():
            if str(ref) in ours:
                continue
            entry = by_chapter.setdefault((ref.book, ref.chapter), {"v": {}})
            entry.setdefault("c", {}).setdefault(code, {})[str(ref.verse)] = text
    return {f"{VERSES_DIR}/{book}/{chapter}.json": json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
            for (book, chapter), entry in by_chapter.items()}


# Dictionary-word pages (/word/?w=<lemma>, web/word.js): each dictionary
# form in the translation so far, with its glosses, how often and where it
# occurs, and the translation decisions that name it. One page per language
# reads the word from its address; the words are in WORD_SHARDS files,
# /words/<n>.json, a word's n being word_shard() of its lemma, which
# web/word.js computes the same way (tests/word_shard_vectors.json holds
# the two to the same answers). Glosses are MACULA's Berean and Cherith
# glosses; its word-sense fields are never used.
WORDS_DIR = "words"
WORD_SHARDS = 256
WORD_VERSES = 40      # verses listed on a word's page; the rest are counted
WORD_DECISIONS = 30   # decisions listed
WORD_GLOSSES = 6


def word_shard(lemma):
    """FNV-1a (32-bit) of the lemma's UTF-16 code units, modulo WORD_SHARDS:
    what JavaScript's charCodeAt sees, so web/word.js agrees."""
    h = 0x811C9DC5
    data = lemma.encode("utf-16-le")
    for i in range(0, len(data), 2):
        h ^= data[i] | (data[i + 1] << 8)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h % WORD_SHARDS


def word_entries():
    """{lemma: entry} for every dictionary form in the translated sentences:
    {"s": Strong's, "lang": "grc"/"hbo"/"arc", "tr": transliteration (Greek),
     "g": [[gloss, count], ...], "n": occurrences, "b": [[book, verses], ...],
     "v": [verse id, ...] (the first WORD_VERSES), "d": [decision, ...],
     "t": key-term slug}. A decision is {"v": verse id, "layer", "c":
     category, "ch": choice, "lang": its language or null, "u": uncertain}."""
    entries, seen = {}, set()
    terms = {term_key(term): term_slug(term) for term in validate.KEY_TERMS.values()}
    for book, chapter in chapters():
        records, words = load_chapter(book, chapter)
        by_id = {w["id"]: (vid, w) for vid, ws in words.items() for w in ws}
        for r in records:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            for token in r["source"]["tokens"]:
                if token not in by_id:
                    continue
                vid, w = by_id[token]
                language = "grc" if book in refs.CODE_TO_SBLGNT else ("arc" if w.get("lang") == "A" else "hbo")
                e = entries.setdefault(w["lemma"], {"s": w.get("strong", ""), "lang": language, "glosses": {},
                                                    "n": 0, "verses": [], "d": []})
                e["n"] += 1
                if not e["verses"] or e["verses"][-1] != vid:
                    e["verses"].append(vid)
                gloss = (w.get("english") or w.get("gloss") or "").replace(".", " ").strip()
                if gloss:
                    e["glosses"][gloss] = e["glosses"].get(gloss, 0) + 1
            for d in r["decisions"]:
                lemmas = []
                for token in d["tokens"]:
                    if token in by_id and by_id[token][1]["lemma"] not in lemmas:
                        lemmas.append(by_id[token][1]["lemma"])
                for lemma in lemmas:
                    if lemma in entries and len(entries[lemma]["d"]) < WORD_DECISIONS:
                        vid = by_id[next(t for t in d["tokens"] if t in by_id)][0]
                        entries[lemma]["d"].append({"v": vid, "layer": d["layer"], "c": d["category"],
                                                    "ch": plain(d["choice"]), "lang": d.get("language"),
                                                    "u": bool(d.get("uncertain"))})
    out = {}
    for lemma, e in entries.items():
        verses = sorted(set(e["verses"]), key=lambda vid: refs.parse(vid).sort_key())
        books_ = {}
        for vid in verses:
            books_[vid.split(".")[0]] = books_.get(vid.split(".")[0], 0) + 1
        entry = {"s": e["s"], "lang": e["lang"], "n": e["n"],
                 "g": sorted(e["glosses"].items(), key=lambda g: (-g[1], g[0]))[:WORD_GLOSSES],
                 "b": list(books_.items()), "v": verses[:WORD_VERSES], "d": e["d"]}
        if e["lang"] == "grc":
            entry["tr"] = translit.greek(lemma)
        slug = terms.get(("hbo" if e["lang"] == "arc" else e["lang"], e["s"]))
        if slug:
            entry["t"] = slug
        out[lemma] = entry
    return out


def word_files():
    """{path: text} for the WORD_SHARDS shards of word_entries()."""
    shards = {}
    for lemma, entry in word_entries().items():
        shards.setdefault(word_shard(lemma), {})[lemma] = entry
    return {f"{WORDS_DIR}/{n}.json": json.dumps(shards.get(n, {}), ensure_ascii=False, separators=(",", ":"))
            for n in range(WORD_SHARDS)}


def word_url(lang, lemma=None):
    return url(lang, "/word/") + (f"?w={urllib.parse.quote(lemma)}" if lemma else "")


def word_page(lang="en"):
    ui = catalog(lang)["word.ui"]
    reader = catalog(lang)["reader.ui"]
    data = {"lang": lang, "ui": ui, "category": reader["category"], "notesLanguage": reader.get("notes_language", ""),
            "wordsUrl": f"/{WORDS_DIR}/", "shards": WORD_SHARDS, "chapterUrl": url(lang, "/"),
            "termUrl": url(lang, "/terms/"), "searchUrl": url(lang, "/search/"),
            "books": {code: chapter_book(code, lang) for code in refs.BOOK_CODES},
            "bookNames": {code: BOOK_NAMES[code][lang] for code in refs.BOOK_CODES if code in BOOK_NAMES}}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = f"""
<header class="page-head word-head">
<p class="eyebrow">{t(lang, "word.title")}</p>
<h1 id="word-title">{t(lang, "word.heading")}</h1>
<p class="dek" id="word-dek">{t(lang, "word.dek")}</p>
</header>
<noscript><p class="notice">{t(lang, "word.noscript")}</p></noscript>
<p class="sr-only" id="word-status" aria-live="polite"></p>
<div class="word" id="word"></div>
<script type="application/json" id="word-data">{blob}</script>
<script src="{asset("word.js")}"></script>
"""
    return page(lang, t(lang, "word.title"), body, path="/word/", current="/read/", description=t(lang, "word.dek"))


# The comparison page (/compare/, web/compare.js): one verse of ours at its
# three levels beside public-domain Bibles, with the decisions that say why
# ours reads as it does. One page per language takes the verse from its
# address (?v=JHN.3.16), so there is no page per verse. Our text and the
# decisions come from the verse's chapter page (its owb-data); the other
# Bibles from /editions/<BOOK>/<chapter>.json, in our verse numbering.
# They are for comparison only, never the basis of our wording.
EDITIONS_DIR = "editions"
EDITIONS = (("bsb", "Berean Standard Bible", "en"), ("web", "World English Bible", "en"),
            ("rv1909", "Reina-Valera 1909", "es"))


def editions_files():
    """{path: text} for every chapter: each edition's verses there."""
    by_chapter = {}
    for code, _, _ in EDITIONS:
        for ref, text in comparison_ours(code).items():
            by_chapter.setdefault((ref.book, ref.chapter), {}).setdefault(code, {})[str(ref.verse)] = text
    return {f"{EDITIONS_DIR}/{book}/{chapter}.json": json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
            for (book, chapter), entry in by_chapter.items()}


def compare_url(lang, vid=None):
    return url(lang, "/compare/") + (f"?v={vid}" if vid else "")


def compare_page(lang="en"):
    ui = catalog(lang)["compare.ui"]
    reader = catalog(lang)["reader.ui"]
    # The Spanish page sets its own Bible first.
    editions = sorted(EDITIONS, key=lambda e: e[2] != lang)
    data = {"lang": lang, "ui": ui, "levels": catalog(lang)["levels"],
            "category": reader["category"], "notesLanguage": reader.get("notes_language", ""),
            "editions": [list(e) for e in editions], "editionsUrl": f"/{EDITIONS_DIR}/",
            "chapterUrl": url(lang, "/"), "books": {code: chapter_book(code, lang) for code in refs.BOOK_CODES},
            "names": book_refs(lang)["names"], "chapters": book_refs(lang)["chapters"],
            "counts": BOOK_CHAPTERS,
            "start": "JHN.3.16"}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = f"""
<header class="page-head compare-head">
<p class="eyebrow">{t(lang, "compare.title")}</p>
<h1 id="cmp-title">{t(lang, "compare.heading")}</h1>
<p class="dek">{t(lang, "compare.dek")}</p>
</header>
<form class="search-box cmp-form" id="cmp-form" action="{url(lang, "/compare/")}" method="get">
{icon(ICONS["search"], 20)}
<input type="search" name="ref" id="cmp-ref" autocomplete="off" spellcheck="false" placeholder="{html.escape(ui["pick"])}" aria-label="{html.escape(ui["pick"])}">
</form>
<noscript><p class="notice">{t(lang, "compare.noscript")}</p></noscript>
<p class="sr-only" id="cmp-status" aria-live="polite"></p>
<div class="cmp" id="cmp"></div>
<script type="application/json" id="cmp-data">{blob}</script>
<script src="{asset("markup.js")}"></script>
<script src="{asset("compare.js")}"></script>
"""
    return page(lang, t(lang, "compare.title"), body, path="/compare/", current="/read/",
                description=t(lang, "compare.dek"))


def verse_text(r, vid, lang="en"):
    """One verse of a record, Balanced, at the default settings, in lang or
    in English when the sentence is not yet in lang."""
    # split keeps each marker's verse number: [text, "13", text, "14", text].
    parts = markup.VERSE.split(r["renderings"][text_lang(r, lang)]["B"])
    numbers = [str(refs.parse(r["refs"][0]).verse)] + parts[1::2]
    return plain(parts[2 * numbers.index(str(refs.parse(vid).verse))].strip())


# A quoted verse in each language's quotation marks (English curly quotes
# otherwise). French sets its guillemets off with no-break spaces.
def inner_quotes(text):
    """A verse to be shown inside double quotes: its own speech takes single
    quotes, and speech inside that speech (Exodus 4:1) double ones. Speech
    that runs on into the next verse (Genesis 9:1) is closed, so the marks
    stay balanced. A closing single quote with no quotation open, or between
    letters, is an apostrophe (Moses’ father-in-law, Aaron’s sons) and stays."""
    out, open_ = [], []
    for i, ch in enumerate(text):
        if ch in "\u201c\u2018":
            open_.append(ch)
            out.append("\u2018" if ch == "\u201c" else "\u201c")
        elif ch == "\u201d":
            if open_ and open_[-1] == "\u201c":
                open_.pop()
            out.append("\u2019")
        elif ch == "\u2019" and open_ and open_[-1] == "\u2018" and not (
                text[i - 1:i].isalpha() and text[i + 1:i + 2].isalpha()):
            open_.pop()
            out.append("\u201d")
        else:
            out.append(ch)
    out += ["\u2019" if ch == "\u201c" else "\u201d" for ch in reversed(open_)]
    return "".join(out)


def passage_card(book, chapter, lang="en"):
    """A passage as a card in the article-card style: its opening verse at
    the default settings, and how much of it is translated into lang and
    recorded (its meaning decisions and its rendering decisions for lang)."""
    every = chapter_records(book, chapter)
    records = [r for r in every if lang in r["renderings"]] or every
    verses = own_verses(records, chapter)
    shown = [d for r in records for d in r["decisions"] if d["language"] in (None, lang)]
    r0 = opening(records, chapter)[0]
    quote = opening_verse(records, chapter, lang)
    meta = t(lang, "card.meta", verses=len(verses), sentences=len(records),
             decisions=len(shown), uncertain=sum(d["uncertain"] for d in shown))
    if len(records) < len(every):
        meta += " &middot; " + t(lang, "card.coverage", n=len(records), total=len(every))
    # Each language's marks around a quoted verse (data/languages.json);
    # inside English-style double quotes, a quote's own marks become single.
    q = owb_languages.READING[lang]["quotes"]
    if q.startswith("&ldquo;"):
        quote = inner_quotes(quote)
    return (f'<li><a class="a-card p-card" href="{url(lang, chapter_url(book, chapter))}">'
            f'<span class="a-section">{BOOK_NAMES[book][lang]} &middot; {languages_label(every)}</span>'
            f'<span class="a-title">{display(chapter_name(records, book, chapter, lang))}</span>'
            f'<span class="p-opening"{lang_attr(text_lang(r0, lang), lang)}>{q.format(display(quote))}</span>'
            f'<span class="a-meta">{meta}</span></a></li>')


def resume_link(lang, cls="button", names=False):
    """A link back to the verse the reader was last at, hidden until
    web/site.js finds one saved by web/reader.js (owb.place). The footer's
    (names) carries the book names in lang, so that every such link on the
    page names the passage in the page's language; one copy per page is
    enough, and every page has the footer."""
    books_attr = ""
    if names:
        names = json.dumps({b: BOOK_NAMES[b][lang] for b, _ in books()}, ensure_ascii=False)
        books_attr = f' data-books="{html.escape(names)}"'
    return (f'<a class="{cls}" data-resume hidden data-label="{html.escape(t(lang, "resume.link"))}" '
            f'data-prefix="{url(lang, "")}"{books_attr} href="{url(lang, "/read/")}">'
            f'{icon(ICONS["book"])}<span></span></a>')


def save_button(book, chaps, lang):
    """A book's "Save for offline" button on the Read page: web/site.js
    stores the pages it names in the owb-books cache, which web/sw.js reads
    when there is no connection, and the chapters' shared reader data
    (chapter_shared). Hidden where the browser cannot."""
    pages = json.dumps([url(lang, chapter_url(p.book, p.chapter)) for p in chaps])
    data = json.dumps([chapter_shared(p.book, p.chapter)[1] for p in chaps])
    labels = "".join(f' data-{k}="{html.escape(t(lang, "offline." + k))}"'
                     for k in ("save", "saving", "saved", "failed"))
    return (f'<button type="button" class="save-book" hidden data-book="{book}" '
            f'data-name="{html.escape(BOOK_NAMES[book][lang])}" data-pages="{html.escape(pages)}" '
            f'data-files="{html.escape(data)}"{labels}>'
            f'{icon(ICONS["download"], 16)}<span>{t(lang, "offline.save")}</span></button>')


def offline_files(lang):
    """What a saved book needs besides its pages and what web/sw.js keeps
    anyway: the reader, its data for the language, the word index and the
    fonts."""
    fonts = sorted(f"/fonts/{f.name}" for f in (ROOT / "web" / "fonts").glob("*.woff2"))
    return [url(lang, "/read/"), asset("markup.js"), asset("reader.js"), reader_shared(lang)[1],
            word_uses()[1]] + fonts


def read_page(lang="en"):
    """Every book translated so far: first an index of the books under their
    testaments, then each book with a pill per chapter and, folded away, a
    card per chapter with its opening verse."""
    groups, tiles = [], {"old_testament": [], "new_testament": []}
    for book, chaps in books(lang):
        done, total, progress = book_progress(book, chaps, lang)
        name = BOOK_NAMES[book][lang]
        # The book's name leads to its page, where it has one.
        heading = f'<a href="{url(lang, book_url(book))}">{name}</a>' if lang in book_languages(book) else name
        testament = "old_testament" if book in refs.OT_CODES else "new_testament"
        tiles[testament].append(
            f'<li><a class="book-tile" href="#{book.lower()}"><span class="book-tile-name">{name}</span>'
            f'<span class="book-progress{" done" if done == total else ""}">{progress}</span>'
            f'{meter(done, total)}</a></li>')
        groups.append(
            f'<section class="book-group" id="{book.lower()}" aria-labelledby="book-{book.lower()}">'
            f'<div class="book-head"><h2 id="book-{book.lower()}">{heading}</h2>'
            f'<span class="book-progress{" done" if done == total else ""}">{progress}</span>'
            f'{meter(done, total)}{save_button(book, chaps, lang)}</div>'
            f'<div class="chap-pills">{chapter_pills(chaps, lang, total=total)}</div>'
            f'<details class="previews"><summary>{t(lang, "read.previews")}</summary>'
            f'<ul class="a-grid">{"".join(passage_card(p.book, p.chapter, lang) for p in chaps)}</ul>'
            f'</details></section>')
    index = "".join(
        f'<section class="book-index-group" aria-labelledby="ix-{key}"><h2 class="label" id="ix-{key}">'
        f'{t(lang, "footer." + key)}</h2><ul class="book-tiles">{"".join(items)}</ul></section>'
        for key, items in tiles.items() if items)
    cards = f'<nav class="book-index" aria-label="{t(lang, "read.books")}">{index}</nav>\n' + "".join(groups)
    body = f"""
<header class="page-head" data-offline-files="{html.escape(json.dumps(offline_files(lang)))}">
<p class="eyebrow">{t(lang, "read.title")}</p>
<h1>{t(lang, "read.heading")}</h1>
<p class="dek">{t(lang, "read.dek")}</p>
<p class="actions">{resume_link(lang)}<a class="button ghost" href="{url(lang, "/saved/")}">{icon(ICONS["bookmark"])}{t(lang, "saved.title")}</a>
<a class="button ghost" href="{url(lang, "/plans/")}">{icon(ICONS["calendar"])}{t(lang, "nav.plans")}</a></p>
</header>
{cards}
<section class="how" aria-labelledby="how-h">
<h2 id="how-h">{t(lang, "read.how")}</h2>
<ol class="steps">
<li>{t(lang, "read.step1")}</li>
<li>{t(lang, "read.step2")}</li>
<li>{t(lang, "read.step3")}</li>
</ol>
</section>
"""
    return page(lang, t(lang, "read.title"), body, path="/read/", current="/read/",
                description=t(lang, "meta.read_description"))


# Reading plans (data/plans.json, web/plans.js): a book or a few, a day's
# chapters at a time. A plan is offered in a language only when every chapter
# in it is translated in that language. A reader's progress is kept in this
# browser only (owb.plans), by web/plans.js.
PLAN_DATA = ROOT / "data" / "plans.json"


class Plan(NamedTuple):
    id: str
    name: dict
    days: tuple  # of tuples of (book, chapter)


@functools.lru_cache(maxsize=None)
def load_plans():
    """Every plan in data/plans.json, in its order."""
    out = []
    for p in json.loads(PLAN_DATA.read_text(encoding="utf-8"))["plans"]:
        days = tuple(tuple((ref.split(".")[0], int(ref.split(".")[1])) for ref in day) for day in p["days"])
        out.append(Plan(p["id"], p["name"], days))
    return tuple(out)


def drafted_chapters(lang):
    """The (book, chapter) pairs a reader can read whole in lang: every verse
    translated, every sentence in lang."""
    return {(p.book, p.chapter) for p in passages_in(lang) if p.complete}


def plan_readable(plan, drafted):
    """Whether every chapter of plan is among drafted (drafted_chapters)."""
    return all(bc in drafted for day in plan.days for bc in day)


def available_plans(lang):
    """The plans offered in lang: those it can read whole."""
    drafted = drafted_chapters(lang)
    return [p for p in load_plans() if plan_readable(p, drafted)]


def plan_url(plan):
    return f"/plans/{plan.id}/"


def plan_ref(book, chapter, lang="en"):
    """A whole chapter's name in a plan: "Mark 7", "Psalm 23"."""
    return f"{chapter_book(book, lang)} {chapter}"


def plan_length(plan, lang="en"):
    """"16 days · a chapter a day"."""
    daily = all(len(day) == 1 for day in plan.days)
    return t(lang, "plans.length", n=len(plan.days)) + (f" &middot; {t(lang, 'plans.daily')}" if daily else "")


def plan_books(plan, lang="en"):
    """The books a plan reads, in its order: "Galatians · Ephesians"."""
    codes = list(dict.fromkeys(b for day in plan.days for b, _ in day))
    return " &middot; ".join(BOOK_NAMES[b][lang] for b in codes)


def plan_dek(plan, lang="en"):
    """Under a plan's name: its books, unless it reads one book (its name
    says which), then its length."""
    books_ = {b for day in plan.days for b, _ in day}
    lead = f"{plan_books(plan, lang)} &middot; " if len(books_) > 1 else ""
    return lead + plan_length(plan, lang)


@functools.lru_cache(maxsize=None)
def plans_json(lang):
    """What web/plans.js needs for the plans offered in lang: its labels,
    and each plan's name, page and days, each chapter with its name and
    address in lang."""
    plans = {p.id: {"name": p.name[lang], "url": url(lang, plan_url(p)),
                    "days": [[{"b": b, "c": c, "n": plan_ref(b, c, lang), "u": url(lang, chapter_url(b, c))}
                              for b, c in day] for day in p.days]}
             for p in available_plans(lang)}
    return json.dumps({"ui": catalog(lang)["plans.ui"], "plans": plans}, ensure_ascii=False, separators=(",", ":"))


@functools.lru_cache(maxsize=None)
def plans_json_url(lang):
    digest = hashlib.sha256(plans_json(lang).encode("utf-8")).hexdigest()[:10]
    return f"/plans-{lang}.json?v={digest}"


def plans_attrs(lang):
    """Where web/plans.js finds the plans: in lang, and in English for a plan
    started in English that lang cannot offer yet."""
    return f'data-plans="{plans_json_url(lang)}" data-plans-en="{plans_json_url("en")}"'


def plans_script():
    return f'<script src="{asset("plans.js")}" defer></script>'


def plan_today(lang):
    """The reader's current plan, filled in by web/plans.js: its name, the
    day reached, a tick per day and a button to read that day's chapters.
    Hidden without one."""
    return (f'<section class="plan-today" data-plan-today {plans_attrs(lang)} '
            f'data-plans-page="{url(lang, "/plans/")}" hidden aria-labelledby="plan-today-h"></section>')


def plan_bar(book, chapter, lang="en"):
    """At the end of a chapter that is the day's reading in the reader's
    plan: the day, a button to mark it done, then the next day's chapter
    (web/plans.js). Hidden otherwise."""
    return (f'<div class="plan-bar" data-plan-bar data-book="{book}" data-chapter="{chapter}" '
            f'{plans_attrs(lang)} aria-live="polite" hidden></div>')


def plan_card(plan, lang="en"):
    return (f'<li><a class="a-card plan-card" href="{url(lang, plan_url(plan))}" data-plan-card="{plan.id}">'
            f'<span class="a-section">{plan_books(plan, lang)}</span>'
            f'<span class="a-title">{html.escape(plan.name[lang])}</span>'
            f'<span class="a-meta">{icon(ICONS["calendar"], 15)}{plan_length(plan, lang)}'
            f'<span class="plan-mine" hidden> &middot; {t(lang, "plans.yours")}</span></span></a></li>')


# The plans the home page suggests first, where they are offered in its
# language: a gospel, psalms and the beginning; then any others.
HOME_PLANS = ("john", "psalms-1-50", "genesis-1-11", "romans", "hebrews")


def home_plans(lang="en"):
    """Three reading plans to start from, with a link to them all; nothing
    where no plan is offered in lang yet."""
    plans = available_plans(lang)
    if not plans:
        return ""
    order = {pid: i for i, pid in enumerate(HOME_PLANS)}
    shown = sorted(plans, key=lambda p: order.get(p.id, len(order)))[:3]
    return f"""<section class="home-plans" aria-labelledby="plans-h">
{sec_head("plans-h", "calendar", t(lang, "plans.heading"), url(lang, "/plans/"), t(lang, "nav.section_all", n=len(plans)))}
<ul class="a-grid plan-list">{"".join(plan_card(p, lang) for p in shown)}</ul>
</section>
"""


def plans_page(lang="en", plans=None):
    """The plans offered in lang (available_plans), or, with none, a plain
    word that none is ready yet and a link to the English ones."""
    plans = available_plans(lang) if plans is None else plans
    if plans:
        listing = f'<ul class="a-grid plan-list">{"".join(plan_card(p, lang) for p in plans)}</ul>'
    else:
        listing = (f'<p class="plans-none">{t(lang, "plans.none", language=owb_languages.native(lang))} '
                   f'<a href="{url("en", "/plans/")}" hreflang="en">{t(lang, "plans.none_link")}</a></p>')
    body = f"""
<header class="page-head">
<p class="eyebrow">{t(lang, "plans.title")}</p>
<h1>{t(lang, "plans.heading")}</h1>
<p class="dek">{t(lang, "plans.dek")}</p>
</header>
{plan_today(lang)}
<section class="plans" aria-labelledby="plans-h">
<h2 id="plans-h" class="sr-only">{t(lang, "plans.title")}</h2>
{listing}
</section>
{plans_script()}
"""
    return page(lang, t(lang, "plans.title"), body, path="/plans/", current="/read/",
                description=t(lang, "meta.plans_description"))


def plan_page(plan, lang="en", translated=LANGUAGES):
    """One plan: its days, each with its chapters; buttons to start or stop
    it and to mark days done (web/plans.js). translated is the languages
    that offer it."""
    n = len(plan.days)
    days = []
    for i, day in enumerate(plan.days, 1):
        links = ", ".join(f'<a href="{url(lang, chapter_url(b, c))}">{plan_ref(b, c, lang)}</a>' for b, c in day)
        days.append(f'<li class="plan-day" data-day="{i}"><span class="plan-day-n">{t(lang, "plans.day", n=i)}</span>'
                    f'<span class="plan-day-chs">{links}</span>'
                    f'<button type="button" class="plan-tick" data-plan-toggle aria-pressed="false" hidden '
                    f'aria-label="{html.escape(t(lang, "plans.day_done", n=i))}">{icon(ICONS["check"], 16)}</button></li>')
    name = html.escape(plan.name[lang])
    body = f"""
<header class="page-head">
<p class="eyebrow"><a href="{url(lang, "/plans/")}">{t(lang, "plans.title")}</a></p>
<h1>{name}</h1>
<p class="dek">{plan_dek(plan, lang)}</p>
<div class="plan-controls" data-plan-page="{plan.id}" data-total="{n}" {plans_attrs(lang)}>
<p class="actions">
<button type="button" class="button" data-plan-start data-continue="{html.escape(t(lang, "plans.continue"))}">{t(lang, "plans.start")}</button>
<a class="button" data-plan-read hidden href="#"></a>
<button type="button" class="button ghost" data-plan-stop hidden>{t(lang, "plans.stop")}</button>
<button type="button" class="button ghost" data-plan-restart hidden>{t(lang, "plans.restart")}</button>
</p>
<p class="plan-status" data-plan-status aria-live="polite"></p>
<p class="plan-kept">{t(lang, "plans.kept")}</p>
</div>
</header>
<section class="plan-days-wrap" aria-labelledby="plan-days-h">
<h2 id="plan-days-h">{t(lang, "plans.days")}</h2>
<ol class="plan-days">
{"".join(days)}
</ol>
</section>
{plans_script()}
"""
    return page(lang, plan.name[lang], body, path=plan_url(plan), current="/read/", translated=translated,
                description=t(lang, "meta.plan_description", name=plan.name[lang], days=n))


def all_records():
    """Every record in content/, in canonical order, once each (a sentence
    across a chapter break is on both chapters' pages)."""
    return list(_all_records())


@functools.lru_cache(maxsize=None)
def _all_records():
    seen = {}
    for b, c in chapters():
        for r in chapter_records(b, c):
            seen.setdefault(r["id"], r)
    return tuple(seen.values())


def plain(text):
    """Rendering text as a reader sees it with the default settings, on one
    line: verse markers dropped, poetic line breaks (\\q) read as spaces."""
    return markup.flat(markup.VERSE.sub("", markup.render(text))).strip()


# The worked examples on the home page, one Greek, one Hebrew and one call
# marked uncertain: a record and one of its decisions each.
EXAMPLES = (("JHN", 1, "JHN.1.1.s1", "m4"), ("PSA", 23, "PSA.23.1.s1", "m2"), ("JHN", 1, "JHN.1.16.s1", "m1"))
EXAMPLE = EXAMPLES[0]
# The examples' gloss and decision in other languages (content/ keeps
# decisions in English), from data/home_examples.json.
HOME_EXAMPLES = json.loads((ROOT / "data" / "home_examples.json").read_text(encoding="utf-8"))["examples"]


def example_translation(example, lang, words):
    """An example's word-for-word gloss, word glosses and decision in lang,
    with {w:id} and {l:id} filled from the source words; None where it has
    none (English, or a language not yet given one)."""
    _, _, record_id, decision_id = example
    tr = HOME_EXAMPLES.get(record_id, {}).get(decision_id, {}).get(lang)
    if not tr:
        return None
    by_id = {w["id"]: w for ws in words.values() for w in ws}

    def fill(text):
        return re.sub(r"\{([wl]):(\w+)\}",
                      lambda m: by_id[m[2]]["text" if m[1] == "w" else "lemma"], text)
    return {**tr, "reason": fill(tr["reason"]), "choice": fill(tr["choice"]),
            "alternatives": [fill(a) for a in tr["alternatives"]]}


def examples(lang="en"):
    """The worked examples a page in lang shows: those whose sentence is
    translated into lang, so none is shown in another language; all of
    them while lang has none."""
    return [e for e in EXAMPLES if any(r["id"] == e[2] and lang in r["renderings"]
                                       for r in chapter_records(e[0], e[1]))] or list(EXAMPLES)
# The reader settings an example can switch, with the reader's labels for
# the setting and its options.
EXAMPLE_SETTINGS = {"divine_name": ("reader.name", ("reader.lord", "reader.yahweh")),
                    "christos": ("reader.title", ("reader.christ", "reader.messiah"))}


def sec_head(hid, ico, title, href=None, more=None):
    """A home-page section heading: icon and title, with an "all" link on
    the right (the Ochorus shelf heading)."""
    link = f'<a class="sec-more" href="{href}">{more} {icon(ICONS["arrow"], 16)}</a>' if href else ""
    return (f'<div class="sec-head"><h2 id="{hid}"><span class="sec-ico">{icon(ICONS[ico])}</span>'
            f'{title}</h2>{link}</div>')


def example_piece(raw):
    """Part of a rendering as the example shows it: verse markers dropped,
    line breaks read as spaces, and each reader setting a span holding its
    default, with its options for web/site.js to switch (only the settings
    an example has a switch for; others show their default)."""
    raw = markup.LINE.sub(" ", markup.VERSE.sub("", raw))
    out, at = [], 0
    for m in markup.SPAN.finditer(raw):
        options = m[2].split("|")
        out.append(html.escape(raw[at:m.start()]))
        if m[1] not in EXAMPLE_SETTINGS:
            out.append(html.escape(options[0]))
            at = m.end()
            continue
        out.append(f'<span class="set" data-set="{m[1]}" data-o="{html.escape(json.dumps(options, ensure_ascii=False))}">'
                   f'{html.escape(options[0])}</span>')
        at = m.end()
    out.append(html.escape(raw[at:]))
    return "".join(out)


def example_rendering(text, alignments=()):
    """A rendering for the example, with each aligned span marked with the
    source words it renders, so tapping a word lights up its English."""
    ranges = markup.alignment_ranges(text, [a["target_span"] for a in alignments])
    out, at = [], 0
    for (start, end), a in zip(ranges, alignments):
        out.append(example_piece(text[at:start]))
        out.append(f'<span class="al" data-t="{" ".join(a["tokens"])}">{example_piece(text[start:end])}</span>')
        at = end
    out.append(example_piece(text[at:]))
    return "".join(out).strip()


def example_panel(example, lang, n):
    """One worked example: the source sentence, its words to tap, the
    word-for-word gloss, the three levels and one decision. Everything comes
    from content/ and data/, so it stays in step with the translation.
    Decision notes are in English, except where data/home_examples.json
    gives the example in the page's language."""
    book, chapter, record_id, decision_id = example
    records, words = load_chapter(book, chapter)
    record = next(r for r in records if r["id"] == record_id)
    decision = next(d for d in record["decisions"] if d["id"] == decision_id)
    tr = example_translation(example, lang, words)
    source = record["source"]["language"]
    marked = set(decision["tokens"])

    def word(w):
        gloss = tr["words"].get(w["id"]) if tr else None
        attrs = (f'data-t="{w["id"]}" data-g="{html.escape(gloss or w.get("english") or w.get("gloss") or "")}" '
                 f'data-l="{html.escape(w["lemma"])}"')
        text = html.escape(w["text"])
        if w["id"] in marked:
            text = f"<mark>{text}</mark>"
        return f'<button type="button" class="w" {attrs}>{text}</button>'

    hebrew = source in ("hbo", "arc")
    tokens = [w for vid in record["refs"] for w in words[vid] if w["id"] in record["source"]["tokens"]]
    original = ""
    for i, w in enumerate(tokens):
        after = w["after"].rstrip()
        if i + 1 < len(tokens):
            # The morphemes of one Hebrew word ("and" + "he called") share
            # its position and are not spaced; a maqaf joins two words.
            if not (hebrew and (tokens[i + 1]["position"] == w["position"] or after.endswith("\u05be"))):
                after += " "
        original += word(w) + html.escape(after)
    shown = text_lang(record, lang)
    aligned = record.get("alignments", [])
    levels = "".join(
        f'<div class="lvl"><span class="lvl-tag">{name}</span>'
        f'<p{lang_attr(shown, lang)}>'
        f'{example_rendering(record["renderings"][shown][code], [a for a in aligned if a["language"] == shown and a["level"] == code])}'
        f'</p></div>'
        for code, name in catalog(lang)["levels"].items())
    present = [k for k in EXAMPLE_SETTINGS if any(f"{{{{{k}:" in v for v in record["renderings"][shown].values())]
    switches = ""
    for key in present:
        label, options = EXAMPLE_SETTINGS[key]
        buttons = "".join(f'<button type="button" data-v="{i}" aria-pressed="{"true" if i == 0 else "false"}">{t(lang, o)}</button>'
                          for i, o in enumerate(options))
        switches += (f'<div class="ex-switch" data-switch="{key}"><span>{t(lang, label)}</span>'
                     f'<span class="seg" role="group" aria-label="{t(lang, label)}">{buttons}</span></div>')
    # What the decision says: in the page's language where the example has
    # a translation, otherwise content/'s English, marked as such.
    said = tr or decision
    also = "; ".join(html.escape(a) for a in said["alternatives"])
    # An uncertain call names its other reading as "Or:", as the reader's
    # footnotes do, and says what the mark means.
    unsure = decision["uncertain"]
    ui = catalog(lang)["reader.ui"]
    open_url = url(lang, chapter_url(book, chapter))
    passage = f"{chapter_book(book, lang)} {chapter}"
    en = "" if tr else lang_attr("en", lang)
    note = f'<p class="alts">{t(lang, "notes_in_english")}</p>' if lang != "en" and not tr else ""
    return f"""<div class="ex-panel" id="ex-{n}" role="tabpanel" aria-labelledby="ex-tab-{n}">
<div class="example-grid">
<div>
<p class="label">{t(lang, "home.example_hebrew" if hebrew else "home.example_greek")}</p>
<p class="{"hebrew" if hebrew else "greek"}" lang="{source}"{' dir="rtl"' if hebrew else ""}>{original}</p>
<p class="w-info" aria-live="polite"><span class="w-hint">{t(lang, "home.example_tap")}</span></p>
<p class="label">{t(lang, "home.example_gloss")}</p>
<p class="gloss"{en}>{html.escape(tr["gloss"] if tr else plain(record["literal_gloss"]))}</p>
<p class="label">{t(lang, "home.example_levels")}</p>
{levels}
{switches}
</div>
<div class="card decision{" uncertain" if unsure else ""}">
<p class="label">{t(lang, "home.example_decision")}{f' <span class="unsure-tag">{ui["uncertain"]}</span>' if unsure else ""}</p>
<p class="choice"{en}>&ldquo;{html.escape(plain(said["choice"]))}&rdquo;</p>
{f'<p class="alts">{html.escape(ui["fn_or"])}<span{en}>{also}</span></p>' if unsure and also else
 f'<p class="alts">{t(lang, "home.example_also", alts=f"<span{en}>{also}</span>")}</p>' if also else ""}
{f'<p class="unsure-note">{t(lang, "home.example_uncertain")}</p>' if unsure else ""}
<p class="why"{en}>{html.escape(said["reason"])}</p>
{note}
</div>
</div>
<p class="example-foot">{t(lang, "home.example_foot")} <a href="{open_url}">{t(lang, "home.example_foot_link", passage=passage)}</a></p>
</div>"""


def example_html(lang="en"):
    """The worked examples, a tab each: John 1:1 from the Greek, Psalm 23:1
    from the Hebrew, and John 1:16, a call marked uncertain. Without
    JavaScript all are shown, one after another (web/site.js makes the
    tabs)."""
    tabs, panels = [], []
    for n, example in enumerate(examples(lang)):
        book, chapter, record_id, _ = example
        ref = refs.parse(record_id.rsplit(".", 1)[0])
        decision = next(d for r in chapter_records(book, chapter) if r["id"] == record_id
                        for d in r["decisions"] if d["id"] == example[3])
        script = ("home.tab_uncertain" if decision["uncertain"] else
                  "home.tab_hebrew" if book in refs.OT_CODES else "home.tab_greek")
        tabs.append(f'<button type="button" role="tab" id="ex-tab-{n}" aria-controls="ex-{n}" '
                    f'aria-selected="{"true" if n == 0 else "false"}"{"" if n == 0 else " tabindex=-1"}>'
                    f'<b>{chapter_book(book, lang)} {ref.chapter}:{ref.verse}</b><span>{t(lang, script)}</span></button>')
        panels.append(example_panel(example, lang, n))
    return f"""
<section class="example" aria-labelledby="example-h" data-example>
{sec_head("example-h", "book", t(lang, "home.example_heading"))}
<div class="ex-tabs" role="tablist" aria-labelledby="example-h" hidden>{"".join(tabs)}</div>
{"".join(panels)}
</section>
"""


def book_map(lang="en"):
    """The home page's map of the whole Bible: a tile per book, by
    testament, filled as far as its chapters are drafted in lang. A book
    with chapters in lang links to it on the Read page; one not started is
    a greyed-out tile. 66 tiles say what 34 progress bars could not: how
    much of the Bible there is still to do."""
    have = dict(books(lang))

    def tile(book):
        name = book_name(book, lang)
        abbr = BOOK_ABBREVIATIONS[book].get(lang, name)
        if book not in have:
            return (f'<li><span class="map-book none" title="{name}: {t(lang, "footer.key_none")}">'
                    f'<span aria-hidden="true">{abbr}</span><span class="sr-only">{name}: '
                    f'{t(lang, "footer.key_none")}</span></span></li>')
        done, total, progress = book_progress(book, have[book], lang)
        fill = 100 * len(have[book]) / total
        return (f'<li><a class="map-book{"" if done == total else " part"}" '
                f'href="{url(lang, f"/read/#{book.lower()}")}" title="{name}: {progress}" style="--fill:{fill:.0f}%">'
                f'<span aria-hidden="true">{abbr}</span><span class="sr-only">{name}: {progress}</span></a></li>')

    def testament(key, codes):
        started = sum(b in have for b in codes)
        return (f'<section class="map-testament" aria-labelledby="map-{key}"><div class="testament-head">'
                f'<h3 id="map-{key}">{t(lang, "footer." + key)}</h3>'
                f'<span>{t(lang, "footer.started", done=started, total=len(codes))}</span></div>'
                f'<ul class="map-books">{"".join(tile(b) for b in codes)}</ul></section>')

    key = "".join(f'<span><span class="map-book{cls}" aria-hidden="true"></span>{t(lang, "footer.key_" + k)}</span>'
                  for k, cls in (("done", ""), ("part", " part"), ("none", " none")))
    return (f'<div class="book-map">{testament("old_testament", refs.OT_CODES)}'
            f'{testament("new_testament", refs.BOOK_CODES[39:])}</div>'
            f'<p class="map-key">{key}</p>')


def progress_html(lang="en"):
    """The home page's progress: sentences, decisions, and the map of the
    books, in the page's language only. A sentence's decisions in lang are
    its meaning decisions and its rendering decisions for lang."""
    records = [r for r in all_records() if lang in r["renderings"]]
    decisions = sum(d["language"] in (None, lang) for r in records for d in r["decisions"])
    return f"""
<section class="progress" aria-labelledby="progress-h">
{sec_head("progress-h", "check", t(lang, "home.progress"), url(lang, "/read/"), t(lang, "home.all_books"))}
<div class="stats">
<div><b>{len(records)}</b><span>{t(lang, "home.stat_sentences")}</span></div>
<div><b>{decisions}</b><span>{t(lang, "home.stat_decisions")}</span></div>
<div><b>{len(LANGUAGES)}</b><span>{t(lang, "home.stat_languages")}</span></div>
</div>
<p>{t(lang, "home.progress_text")}</p>
{book_map(lang)}
</section>
"""


# The verse of the day (data/verse_of_the_day.json).
VERSES_OF_THE_DAY = json.loads((ROOT / "data" / "verse_of_the_day.json").read_text(encoding="utf-8"))["refs"]


def votd_record(vid):
    ref = refs.parse(vid)
    return next(r for r in chapter_records(ref.book, ref.chapter) if vid in r["refs"])


@functools.lru_cache(maxsize=None)
def votd_refs(lang="en"):
    """The verses of the day in lang: those already translated into it, in
    the list's order, so a page never shows a verse in another language;
    the whole list while lang has none of them yet."""
    return tuple(v for v in VERSES_OF_THE_DAY if lang in votd_record(v)["renderings"]) or tuple(VERSES_OF_THE_DAY)


def verses_of_the_day(lang="en"):
    """Each verse of the day as the home page shows it: its reference, its
    Balanced text in lang (or English, marked, while lang has none of the
    verses), and links to its notes and its chapter."""
    out = []
    for vid in votd_refs(lang):
        ref = refs.parse(vid)
        r = votd_record(vid)
        item = {"r": f"{chapter_book(ref.book, lang)} {ref.chapter}:{ref.verse}", "t": verse_text(r, vid, lang),
                "u": url(lang, chapter_url(ref.book, ref.chapter)) + f"#v{ref.verse}"}
        if text_lang(r, lang) != lang:
            item["l"] = text_lang(r, lang)
        out.append(item)
    return out


def verse_of_the_day(lang="en"):
    """The verse of the day: the build day's verse, which web/site.js swaps
    for the reader's own day from the list in the page."""
    verses = verses_of_the_day(lang)
    v = verses[(datetime.date.today() - datetime.date(1970, 1, 1)).days % len(verses)]
    data = json.dumps(verses, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    la = f' lang="{v["l"]}"' if "l" in v else ""
    return f"""<section class="votd" aria-labelledby="votd-h" data-votd>
<p class="eyebrow" id="votd-h">{icon(ICONS["calendar"], 16)}{t(lang, "home.votd")}</p>
<blockquote><p class="votd-text"{la}>{html.escape(v["t"])}</p>
<footer><a class="votd-ref" href="{v["u"]}">{html.escape(v["r"])}</a>
<a class="votd-why" href="{v["u"]}">{t(lang, "home.votd_why")} {icon(ICONS["arrow"], 15)}</a></footer></blockquote>
<p class="votd-feed"><a href="{votd_feed_url(lang)}">{icon(ICONS["feed"], 15)}{t(lang, "home.votd_feed")}</a></p>
<script type="application/json" class="votd-data">{data}</script>
</section>"""


# The verse of the day as an Atom feed, one per language: the last
# VOTD_FEED_DAYS days up to the day the site was built, the same verse each
# day as the home page shows. Each entry has the verse, the notes that say
# why it reads as it does, and a link to the verse in the reader, which
# opens its reasoning. The site is rebuilt on every deploy, so the feed is
# as fresh as the last one.
VOTD_FEED_DAYS = 14


def votd_feed_url(lang):
    return url(lang, "/verse-of-the-day.xml")


def votd_for_day(day, lang="en"):
    """The verse id of the day (a datetime.date) in lang: the home page's rule."""
    verses = votd_refs(lang)
    return verses[(day - datetime.date(1970, 1, 1)).days % len(verses)]


def votd_notes(r, lang):
    """The decisions a verse of the day's entry explains it with: those the
    reader footnotes (every meaning decision with a footnote, and this
    language's Balanced wording decisions with one), or else its meaning
    decisions; at most three."""
    noted = [d for d in r["decisions"] if d.get("footnote") and (
        d["layer"] == "meaning" or (d.get("language") == text_lang(r, lang) and "B" in d.get("levels", [])))]
    return (noted or [d for d in r["decisions"] if d["layer"] == "meaning"])[:3]


def votd_feed(lang="en", today=None):
    """The Atom feed of the verse of the day in lang."""
    def esc(text):
        return html.escape(text, quote=False)
    today = today or datetime.date.today()
    ui = catalog(lang)["reader.ui"]
    entries = []
    for back in range(VOTD_FEED_DAYS):
        day = today - datetime.timedelta(days=back)
        vid = votd_for_day(day, lang)
        ref = refs.parse(vid)
        r = votd_record(vid)
        name = f"{chapter_book(ref.book, lang)} {ref.chapter}:{ref.verse}"
        link = SITE_URL + url(lang, chapter_url(ref.book, ref.chapter)) + f"#v{ref.verse}"
        tl = text_lang(r, lang)
        body = [f"<blockquote{lang_attr(tl, lang)}><p>{html.escape(verse_text(r, vid, lang))}</p></blockquote>"]
        notes = votd_notes(r, lang)
        if notes:
            body.append(f"<p><strong>{html.escape(t(lang, 'home.votd_why'))}</strong></p>")
            if ui.get("notes_language"):
                body.append(f"<p><em>{html.escape(ui['notes_language'])}</em></p>")
            items = "".join(
                f"<li><strong>{html.escape(plain(d['choice']))}</strong>"
                + (f" ({html.escape(ui['category'][d['category']])})" if d["category"] in ui.get("category", {}) else "")
                + f": {html.escape(plain(d['reason']))}</li>" for d in notes)
            body.append(f'<ul lang="en">{items}</ul>')
        body.append(f'<p><a href="{html.escape(link)}">{html.escape(t(lang, "votd.read"))}</a></p>')
        entries.append(
            f"<entry><title>{esc(name)}</title>"
            f'<link href="{html.escape(link)}"/>'
            f"<id>{esc(SITE_URL + votd_feed_url(lang))}#{day.isoformat()}</id>"
            f"<updated>{day.isoformat()}T00:00:00Z</updated>"
            f'<content type="html">{esc("".join(body))}</content></entry>\n')
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            f'<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{lang}">\n'
            f"<title>{esc(SITE_NAME + ' · ' + t(lang, 'home.votd'))}</title>\n"
            f'<link href="{html.escape(SITE_URL + url(lang, "/"))}"/>\n'
            f'<link rel="self" href="{html.escape(SITE_URL + votd_feed_url(lang))}"/>\n'
            f"<id>{esc(SITE_URL + votd_feed_url(lang))}</id>\n"
            f"<updated>{today.isoformat()}T00:00:00Z</updated>\n"
            f"<author><name>{SITE_NAME}</name></author>\n"
            f"{''.join(entries)}</feed>\n")


def data_html(lang="en"):
    """The home page's offer to builders: the whole translation to
    download, the API, and the data model, all CC0."""
    api = f"{API_URL}/api/passages/JHN/1/"
    cards = (
        ("download", f"{GITHUB_URL}/archive/refs/heads/main.zip", "home.data_zip", t(lang, "home.data_zip_text")),
        ("code", api, "home.data_api", f'{t(lang, "home.data_api_text")} <code>{html.escape(api.split("//", 1)[1])}</code>'),
        ("info", f"{GITHUB_URL}/blob/main/schema/sentence-record.schema.json", "home.data_schema",
         t(lang, "home.data_schema_text")))
    items = "".join(f'<li><a class="data-card" href="{href}"><span class="tile sm">{icon(ICONS[ico])}</span>'
                    f'<span><strong>{t(lang, key)}</strong><span>{text}</span></span></a></li>'
                    for ico, href, key, text in cards)
    return f"""<section class="data" aria-labelledby="data-h">
{sec_head("data-h", "scale", t(lang, "home.data"))}
<p class="data-text">{t(lang, "home.data_text")}</p>
<ul class="data-cards">{items}</ul>
</section>
"""


def hero_search(lang="en"):
    """The home page's search box: a verse to go to or words to find, as
    the /search/ page takes them, with the search page's examples to try."""
    ui = catalog(lang)["search.ui"]
    tries = "".join(f'<li><a href="{url(lang, "/search/")}?q={html.escape(q.replace(" ", "+"))}">{html.escape(q)}</a></li>'
                    for q in catalog(lang)["search.examples"])
    return (f'<form class="hero-search" action="{url(lang, "/search/")}" method="get" role="search">'
            f'<label class="sr-only" for="hero-q">{t(lang, "footer.find")}</label>'
            f'<span class="hero-search-ico" aria-hidden="true">{icon(ICONS["search"])}</span>'
            f'<input type="search" name="q" id="hero-q" autocomplete="off" spellcheck="false" enterkeyhint="go" '
            f'placeholder="{html.escape(ui["palette_placeholder"])}">'
            f'<button class="button" type="submit">{t(lang, "footer.go")}</button></form>'
            f'<div class="hero-try"><span>{t(lang, "home.try")}</span><ul>{tries}</ul></div>')


def home_page(lang="en"):
    def point(ico, n):
        return (f'<li class="point"><span class="tile">{icon(ICONS[ico], 22)}</span>'
                f'<h3>{t(lang, f"home.point{n}")}</h3><p>{t(lang, f"home.point{n}_text")}</p></li>')

    def helper(ico, n):
        return (f'<li><span class="tile sm">{icon(ICONS[ico])}</span>'
                f'<p><strong>{t(lang, f"home.helper{n}")}</strong> {t(lang, f"home.helper{n}_text")}</p></li>')

    # One article from each kind, in the catalog's order of kinds: how it
    # is made, reading the text, how we got the Bible (the footer already
    # lists the first few on method).
    ordered = sorted(load_articles(lang), key=lambda a: a["order"])
    first = [a for a in (next((a for a in ordered if a["section"] == kind), None)
                         for kind in catalog(lang)["sections"]) if a][:3]
    latest = f"""<section class="latest" aria-labelledby="latest-h">
{sec_head("latest-h", "articles", t(lang, "home.latest"), url(lang, "/articles/"), t(lang, "nav.all_articles"))}
<ul class="a-grid">{article_list(first, lang)}</ul>
</section>
""" if first else ""
    body = f"""
<section class="hero">
<p class="eyebrow">{t(lang, "home.eyebrow")}</p>
<h1>{t(lang, "home.heading")}</h1>
<p class="hero-sub">{t(lang, "home.sub")}</p>
{plan_today(lang)}
<p class="actions">{resume_link(lang)}<a class="button" href="{url(lang, "/read/")}">{icon(ICONS["book"])}{t(lang, "home.start")}</a>
<a class="button ghost hero-how" href="#example-h">{t(lang, "home.how")}</a></p>
{hero_search(lang)}
<ul class="trust">
<li>{icon(ICONS["gift"], 16)}{t(lang, "home.trust_free")}</li>
<li>{icon(ICONS["scale"], 16)}{t(lang, "home.trust_cc0")}</li>
<li>{icon(ICONS["languages"], 16)}{t(lang, "home.trust_languages")}</li>
</ul>
</section>
{verse_of_the_day(lang)}
{example_html(lang)}
<section class="points-wrap" aria-labelledby="points-h">
{sec_head("points-h", "info", t(lang, "home.points"))}
<ul class="points">
{point("gift", 1)}
{point("languages", 2)}
{point("sliders", 3)}
{point("check", 4)}
</ul>
</section>
{home_plans(lang)}
{progress_html(lang)}
{home_terms(lang)}
{latest}{data_html(lang)}<section class="involve" id="help" aria-labelledby="involve-h">
<div class="involve-text">
<h2 id="involve-h">{t(lang, "home.involve")}</h2>
<p>{t(lang, "home.involve_text")}</p>
<p><a class="button" href="{GITHUB_URL}">{icon(ICONS["github"])}{t(lang, "home.involve_github")}</a></p>
</div>
<ul class="helpers">
{helper("languages", 1)}
{helper("users", 2)}
{helper("code", 3)}
{helper("sliders", 4)}
</ul>
</section>
{plans_script()}
"""
    feed = (f'\n<link rel="alternate" type="application/atom+xml" '
            f'title="{html.escape(SITE_NAME + " · " + t(lang, "home.votd"))}" href="{votd_feed_url(lang)}">')
    return page(lang, SITE_NAME, body, path="/", current="/", head=feed)


def about_page(lang="en"):
    credits = markdown((ROOT / "CREDITS.md").read_text(encoding="utf-8"))
    # Demote the file's headings one level to sit under the page's h1.
    for n in (2, 1):
        credits = credits.replace(f"<h{n}>", f"<h{n + 1}>").replace(f"</h{n}>", f"</h{n + 1}>")
    # The credits are written in English, as their sources publish them; on
    # a page in another language a note says so, and is the #credits target.
    if lang == "en":
        credits = credits.replace("<h2>Credits</h2>", '<h2 id="credits">Credits</h2>', 1)
    else:
        credits = (f'<p id="credits" class="fine">{t(lang, "about.credits_language")}</p>\n'
                   f'<div lang="en">{credits}</div>')
    body = f"""
<div class="prose">
<h1>{t(lang, "about.title")}</h1>
<p>{t(lang, "about.intro")}</p>
<h2>{t(lang, "about.licences")}</h2>
<p>{t(lang, "about.licences_text")}</p>
<p>{t(lang, "about.source")} <a href="{GITHUB_URL}">github.com/jdegreef/open-word-bible</a>.</p>
{credits}
</div>
{dataset_ld() if lang == "en" else ""}
"""
    return page(lang, t(lang, "about.title"), body, path="/about/", current="/about/",
                description=t(lang, "meta.about_description"))


def dataset_ld():
    """schema.org data describing the translation's records as a dataset,
    for dataset search. It is given once, on the English about page. The
    translation is CC0, but each record also holds the original-language
    words of its source, which keep their own licences, so the description
    says so."""
    langs = [code for code in LANGUAGES if any(code in r["renderings"] for r in _all_records())]
    return ld_script({
        "@context": "https://schema.org", "@type": "Dataset",
        "name": "Open Word Bible reasoning records",
        "description": ("A Bible translation from Hebrew and Greek with the reasoning behind every sentence. "
                        "Each record holds one source sentence: its original-language words, a literal gloss, "
                        "the translation at three levels (Literal, Balanced, Readable) in each language, and each "
                        "translation decision with its alternatives and reason. Every record is an AI-assisted "
                        "draft until a named human reviewer approves it. The translation, notes, records and "
                        "alignments are CC0; the original-language words come from the SBL Greek New Testament, "
                        "the Open Scriptures Hebrew Bible and the MACULA datasets, which keep their own licences "
                        "(credited on this page)."),
        "url": SITE_URL + "/about/", "sameAs": GITHUB_URL,
        "license": CC0_URL, "isAccessibleForFree": True,
        "creator": ORGANIZATION, "publisher": ORGANIZATION,
        "inLanguage": langs, "creativeWorkStatus": "Draft",
        "isBasedOn": list(SOURCE_TEXTS.values()),
        "keywords": ["Bible", "Bible translation", "Greek New Testament", "Hebrew Bible", "translation notes"],
        "distribution": [{"@type": "DataDownload", "encodingFormat": "application/zip",
                          "contentUrl": GITHUB_URL + "/archive/refs/heads/main.zip"}],
    })


# Review statuses in the schema's order; the last two mean a named reviewer
# has approved the sentence's wording.
REVIEW_STATUSES = tuple(validate._PROPS["status"]["enum"])
APPROVED = REVIEW_STATUSES[2:]


@functools.lru_cache(maxsize=None)
def status_counts():
    """The records counted for the status page and llms.txt: in all, by
    review status, by language and by book (in canonical order)."""
    records = _all_records()
    statuses = dict.fromkeys(REVIEW_STATUSES, 0)
    by_lang = dict.fromkeys(LANGUAGES, 0)
    by_book = {}
    for r in records:
        statuses[r["status"]] += 1
        for code in r["renderings"]:
            by_lang[code] += 1
        counts = by_book.setdefault(refs.parse(r["refs"][0]).book, {"all": 0, "approved": 0})
        counts["all"] += 1
        counts["approved"] += r["status"] in APPROVED
    order = {code: i for i, code in enumerate(refs.BOOK_CODES)}
    return {"all": len(records), "statuses": statuses, "drafts": statuses[REVIEW_STATUSES[0]],
            "approved": sum(statuses[k] for k in APPROVED),
            "languages": {code: n for code, n in by_lang.items() if n},
            "books": dict(sorted(by_book.items(), key=lambda kv: order[kv[0]]))}


def number(n, lang):
    """A count with the language's thousands separator."""
    return f"{n:,}".replace(",", catalog(lang)["status"]["thousands"])


REVIEW_ARTICLE = "ai-assisted-translation-and-human-review"


def status_page(lang="en"):
    """Where the translation stands: how many sentences are drafted and how
    many a named reviewer has approved, counted from content/ at every
    build, so it cannot fall out of date or claim more than the records."""
    s = catalog(lang)["status"]
    labels = catalog(lang)["reader.ui"]["review_status"]
    c = status_counts()
    esc = html.escape

    def table(key, head, rows):
        heads = "".join(f'<th scope="col">{h}</th>' for h in head)
        cells = "".join(f'<tr><th scope="row">{row[0]}</th>{"".join(f"<td>{x}</td>" for x in row[1:])}</tr>'
                        for row in rows)
        return (f'<h2 id="{key}">{s[key]}</h2>\n<table class="status-table" aria-labelledby="{key}">'
                f'<thead><tr>{heads}</tr></thead><tbody>{cells}</tbody></table>')

    by_status = table("by_status", (s["status"], s["count"]),
                      [(esc(labels[k]), number(n, lang)) for k, n in c["statuses"].items()])
    by_lang = table("by_language", (s["language"], s["count"]),
                    [(f'<span lang="{code}">{owb_languages.native(code)}</span>', number(n, lang))
                     for code, n in c["languages"].items()])
    by_book = table("by_book", (s["book"], s["count"], s["reviewed"]),
                    [(f'<a href="{url(lang, "/read/")}#{book.lower()}">{esc(BOOK_NAMES[book][lang])}</a>',
                      number(n["all"], lang), number(n["approved"], lang))
                     for book, n in c["books"].items()])
    # The article on review, in the page's language where it has one.
    article = next((a for a in load_articles(lang) if a["slug"] == REVIEW_ARTICLE), None)
    article_lang = lang if article else "en"
    article = article or next(a for a in load_articles("en") if a["slug"] == REVIEW_ARTICLE)
    attr = "" if article_lang == lang else ' hreflang="en" lang="en"'
    body = f"""
<div class="prose status">
<p class="eyebrow">{s["title"]}</p>
<h1>{s["heading"]}</h1>
<p class="dek">{s["dek"]}</p>
<div class="stats">
<div><b>{number(c["all"], lang)}</b><span>{s["sentences"]}</span></div>
<div><b>{number(c["drafts"], lang)}</b><span>{s["drafts"]}</span></div>
<div><b>{number(c["approved"], lang)}</b><span>{s["reviewed"]}</span></div>
</div>
<p><a href="{url(article_lang, article_url(article))}"{attr}>{s["how"]}&nbsp;&rarr;</a></p>
<p>{s["report"].replace("{issues}", GITHUB_URL + "/issues/new")}</p>
{by_status}
{by_lang}
{by_book}
</div>
"""
    return page(lang, s["title"], body, path="/about/status/", current="/about/", description=s["description"])


# Ready-made downloads of the text (owb/export.py, which the admin's Export
# uses for one file at a time): every reading language at every level, as
# USFM books and as JSON, at the default settings, for Bible software and
# apps. Each is a zip holding the text, its manifest, a README and the
# licence. Zipping the JSON as well keeps the set near 25 MB (the JSON alone
# would be 54 MB). The files are named for what they hold, not the deploy,
# so a link to one keeps working; the service worker leaves them alone.
DOWNLOADS_DIR = "downloads"
DOWNLOAD_FORMATS = ("usfm", "json")


def build_commit():
    """(commit, ISO date) of the build's source, or ("", "") outside git."""
    commit = os.environ.get("RENDER_GIT_COMMIT", "")
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%H %cI", *([commit] if commit else [])], cwd=ROOT,
                             capture_output=True, text=True, timeout=10, check=True).stdout.split()
        return out[0], out[1]
    except (OSError, subprocess.SubprocessError, IndexError):
        return commit, ""


def download_readme(m, fmt):
    missing = m["missing"]["count"]
    what = ("one USFM file per book, numbered in canonical order" if fmt == "usfm"
            else f"{m['edition']}.json: the books, chapters and verses as JSON")
    return f"""{m["title"]}, {m["language_name"]}, {m["level_name"]}
{"=" * 40}

{m["verses"]:,} verses; {missing:,} not yet translated (listed in manifest.json).
This zip holds {what}, and manifest.json, which describes the edition: its
numbering, the reader settings it uses, review status counts and the
source commit.

{m["note"]}

Licence: {m["licence"]} ({m["licence_url"]}). See LICENSE.
Please credit "{m["credit"]}" where you can; you don't have to.

The latest files and the reasoning behind every sentence: {m["url"]}
Built {m["generated_at"] or "from a working copy"}{f" from commit {m['commit']}" if m["commit"] else ""}.
"""


@functools.lru_cache(maxsize=None)
def downloads():
    """{(lang, level, fmt): (filename, zip bytes, manifest)} for every reading
    language with text, at every level, in every format."""
    records = _all_records()
    expected = [v for book, chapter in chapters() for v in chapter_verses(book, chapter)]
    commit, date = build_commit()
    licence = (ROOT / "LICENSE").read_text(encoding="utf-8")
    have = status_counts()["languages"]
    out = {}
    for lang in owb_languages.READING:
        if lang not in have:
            continue
        for level in export.LEVELS:
            for fmt in DOWNLOAD_FORMATS:
                name, _, data, m = export.build(records, lang, level, fmt, expected=expected,
                                                generated_at=date, commit=commit)
                buf = io.BytesIO()
                if fmt == "usfm":
                    buf.write(data)   # manifest.json and the books, to which the README and licence are added
                    mode = "a"
                else:
                    mode, name = "w", name.replace(".json", "-json.zip")
                with zipfile.ZipFile(buf, mode, zipfile.ZIP_DEFLATED) as z:
                    def put(path, text):
                        info = zipfile.ZipInfo(path, export.ZIP_DATE)
                        info.compress_type = zipfile.ZIP_DEFLATED
                        z.writestr(info, text.encode())
                    if fmt == "json":
                        put(f"{m['edition']}.json", data.decode())
                        put("manifest.json", json.dumps(m, ensure_ascii=False, indent=1) + "\n")
                    put("README.txt", download_readme(m, fmt))
                    put("LICENSE", licence)
                out[lang, level, fmt] = (name, buf.getvalue(), m)
    return out


def download_url(name):
    return f"/{DOWNLOADS_DIR}/{name}"


def file_size(size, lang):
    """A file's size in MB (or KB under one MB), in lang's way of writing numbers."""
    d = catalog(lang)["download"]
    if size < 1024 * 1024:
        return d["kb"].format(n=number(max(1, round(size / 1024)), lang))
    return d["mb"].format(n=f"{size / 1024 / 1024:.1f}".replace(".", d["decimal"]))


def download_page(lang="en"):
    """/download/: the ready-made files, the page's language first."""
    d = catalog(lang)["download"]
    levels = catalog(lang)["levels"]
    files = downloads()
    langs = sorted({code for code, _, _ in files}, key=lambda code: code != lang)
    sections = []
    for code in langs:
        rows = []
        for level in export.LEVELS:
            cells = []
            for fmt in DOWNLOAD_FORMATS:
                name, data, _ = files[code, level, fmt]
                cells.append(f'<td><a href="{download_url(name)}" download>{d[fmt]}</a> '
                             f'<span class="fine">{file_size(len(data), lang)}</span></td>')
            rows.append(f'<tr><th scope="row">{html.escape(levels[level])}</th>{"".join(cells)}</tr>')
        m = files[code, "B", "usfm"][2]
        counts = d["counts"].format(verses=number(m["verses"], lang), missing=number(m["missing"]["count"], lang))
        sections.append(f'<h2 id="dl-{code}"><span lang="{code}">{owb_languages.native(code)}</span></h2>\n'
                        f'<p>{counts}</p>\n'
                        f'<table class="status-table" aria-labelledby="dl-{code}"><thead><tr>'
                        f'<th scope="col">{d["level"]}</th><th scope="col">{d["usfm"]}</th>'
                        f'<th scope="col">{d["json"]}</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')
    m = next(iter(files.values()))[2]
    built = d["built"].format(date=m["generated_at"][:10]) if m["generated_at"] else ""
    body = f"""
<div class="prose status">
<p class="eyebrow">{d["title"]}</p>
<h1>{d["heading"]}</h1>
<p class="dek">{d["dek"]}</p>
<p class="notice">{d["draft"].replace("{status}", url(lang, "/about/status/"))}</p>
<ul>
<li>{d["usfm_note"]}</li>
<li>{d["json_note"]}</li>
<li>{d["settings_note"]}</li>
</ul>
<p>{d["licence"]}</p>
{"".join(sections)}
<p class="fine">{built}</p>
</div>
"""
    return page(lang, d["title"], body, path="/download/", current="/about/", description=d["description"])


def llms_txt():
    """/llms.txt: a short Markdown guide to the site for AI tools
    (https://llmstxt.org): what it is, how its pages are laid out, where the
    method and the data are, and how far review has got."""
    c = status_counts()
    other = ", ".join(f"/{code}/" for code in LANGUAGES if code != "en")
    method = sorted((a for a in load_articles("en") if a["section"] == "method"), key=lambda a: a["order"])
    articles = "".join(f"- [{a['title']}]({SITE_URL}{article_url(a)}): {a['summary']}\n" for a in method)
    names = ", ".join(owb_languages.READING[code]["name"] for code in c["languages"])
    intros = "".join(f"- [{BOOK_NAMES[b]['en']}]({SITE_URL}{book_url(b)}): {load_intro(b)['summary']}\n"
                     for b, _ in books("en") if "en" in book_languages(b))
    return f"""# {SITE_NAME}

> A free Bible translation from Hebrew and Greek with the reasoning behind every sentence. The translation, its notes and its reasoning records are in the public domain (CC0 1.0). Every sentence is drafted with AI help and stays marked as a draft until a named human reviewer who reads the original language approves it.

At this build, {c["all"]:,} sentences are drafted and {c["approved"]:,} are reviewed by a person. Languages so far: {names}. Quote a sentence as a draft unless its page says it is reviewed.

## Reading the site

- A chapter is at {SITE_URL}/<book>/<chapter>/, with the book's three-letter code in lower case: {SITE_URL}/jhn/3/ is John 3. Other languages have a prefix ({other}).
- A chapter page has the Balanced text and its footnotes as HTML. The full reasoning record of each sentence (the original words, a literal gloss, three levels of translation and every decision with its alternatives and reason) is in the page's data and opens beside the verse in the reader.
- Old Testament verses are numbered as in the Hebrew text, so a psalm's title is verse 1.

## Key pages

- [Read]({SITE_URL}/read/): every book and chapter translated so far.
{intros}- [Translation status]({SITE_URL}/about/status/): sentences drafted and reviewed, by language and book.
- [Key terms]({SITE_URL}/terms/): the key Greek and Hebrew words and the English each keeps.
- [Articles]({SITE_URL}/articles/): the method, close readings and the history of the Bible's text.
- [About]({SITE_URL}/about/): licences and source credits.
- [What we believe]({SITE_URL}/about/beliefs/)

## Method

{articles}
## Data

- [Source code and data]({GITHUB_URL}): one JSON file of reasoning records per passage in content/.
- The original-language words come from the SBL Greek New Testament, the Open Scriptures Hebrew Bible and the MACULA datasets, which keep their own licences: {SITE_URL}/about/#credits
"""


def beliefs_page(lang="en"):
    """What we believe: the Apostles' Creed first, then the vision, mission
    and values that grow out of it. All of it comes from the catalog's
    "beliefs" entry, so each language has its own wording."""
    b = catalog(lang)["beliefs"]
    creed = "".join(f"<p>{p}</p>" for p in b["creed"][:-1])
    creed += f'<p>{b["creed"][-1]} <span class="amen">{b["amen"]}</span></p>'
    values = "".join(f"<li><strong>{name}:</strong> {text}</li>" for name, text in b["values"])
    body = f"""
<div class="prose beliefs">
<p class="kicker">{b["kicker"]}</p>
<h1>{b["heading"]}</h1>
<div class="creed">{creed}</div>
<p class="creed-note">{b["scripture"]}</p>
<hr class="ornament">
<div class="aims">
<section><h2>{b["vision_title"]}</h2><p>{b["vision"]}</p></section>
<section><h2>{b["mission_title"]}</h2><p>{b["mission"]}</p></section>
</div>
<hr class="ornament">
<h2>{b["values_title"]}</h2>
<ul class="guides">{values}</ul>
</div>
"""
    return page(lang, b["title"], body, path="/about/beliefs/", current="/about/",
                description=b["description"])


def legal_page(lang, key, path):
    """The privacy notice (key "privacy") or the terms of use
    ("terms_of_use"), from the catalog entry of that name: a heading, the
    date it last changed, then titled sections of paragraphs. A paragraph
    may be a list; {account}, {credits}, {issues}, {source} and {privacy}
    become links in lang."""
    c = catalog(lang)[key]
    links = {"account": url(lang, "/account/"), "credits": url(lang, "/about/#credits"),
             "issues": GITHUB_URL + "/issues", "source": GITHUB_URL, "privacy": url(lang, "/about/privacy/")}

    def block(text):
        text = text.format(**links)
        return text if text.startswith("<ul>") else f"<p>{text}</p>"

    sections = "".join(f"<h2>{heading}</h2>{''.join(map(block, paragraphs))}" for heading, paragraphs in c["sections"])
    body = f"""
<div class="prose legal">
<h1>{c["heading"]}</h1>
<p class="fine">{c["updated"]}</p>
<p class="dek">{c["dek"]}</p>
{sections}
</div>
"""
    return page(lang, c["title"], body, path=path, current="/about/", description=c["description"])


# The key-terms glossary: /terms/ lists every key term (data/key_terms.json)
# and /terms/<slug>/ shows one with every place it is used in the drafted
# text, so a reader can check that the translation keeps its word.

def term_key(term):
    """A key term's identity: its source language and Strong's number
    (Greek and Hebrew numbers overlap), as owb.validate keys it."""
    return (term.get("language", "grc"), term["strong"])


def term_strong(term):
    """A key term's Strong's number as it is usually cited: G1391, H3068."""
    return ("H" if term_key(term)[0] == "hbo" else "G") + term["strong"].lstrip("0")


def term_slug(term):
    """A key term's page slug: the "slug" set in data/key_terms.json, which
    never changes, so links to the page keep working."""
    return term["slug"]


def term_path(term, book=None):
    """A key term's page, or the page of its uses in one book."""
    return f"/terms/{term_slug(term)}/" + (f"{book.lower()}/" if book else "")


class TermUse(NamedTuple):
    """One sentence that uses a key term: the record, the term's words in
    it (token ids) and the verses they are in, the English levels that do
    not use a settled word, and the decisions that explain why
    (owb.validate.explaining_decisions)."""
    record: dict
    tokens: list
    verses: list
    departs: list
    decisions: list


@functools.lru_cache(maxsize=None)
def term_uses():
    """Every use of every key term in the drafted text, by term_key, in
    canonical order: one TermUse per sentence (a sentence across a chapter
    break counts once). Words are matched by Strong's number and language,
    as owb.validate matches them."""
    uses, seen, by_id, loaded = {key: [] for key in validate.KEY_TERMS}, set(), {}, set()
    # The records are passages()' (built once); only the word extracts are
    # read here, each once.
    for p in passages():
        for r in p.records:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            for ref in {(refs.parse(v).book, refs.parse(v).chapter) for v in r["refs"]} - loaded:
                loaded.add(ref)
                for vid, ws in json.loads(words_path(*ref).read_text(encoding="utf-8"))["verses"].items():
                    by_id.update((w["id"], (vid, w.get("strong") or "")) for w in ws)
            found = {}
            for tid in r["source"]["tokens"]:
                if tid not in by_id:
                    continue
                vid, strong = by_id[tid]
                term = validate.key_term(tid, strong)
                if term:
                    found.setdefault(term_key(term), []).append((tid, vid))
            if not found:
                continue
            explained = validate.explaining_decisions(r)
            english = r["renderings"].get("en", {})
            for key, hits in found.items():
                term = validate.KEY_TERMS[key]
                departs = [level for level in validate.LEVELS if level in english and not
                           validate.key_term_pattern(validate.key_term_words(term, level)).search(english[level])]
                decisions = list({d["id"]: d for tid, _ in hits for d in explained.get(tid, [])}.values())
                verses = sorted({vid for _, vid in hits}, key=lambda v: refs.parse(v).sort_key())
                uses[key].append(TermUse(r, [tid for tid, _ in hits], verses,
                                         departs if decisions else [], decisions if departs else []))
    return uses


def term_count(term):
    """How many times a key term's word is in the drafted text."""
    return sum(len(u.tokens) for u in term_uses()[term_key(term)])


def emphasise(text, words):
    """Escaped text with the key term's English words marked. Words in the
    term's own case ("LORD") win over the same letters in another case
    ("Lord"); with none, any case will do ("Grace" opening a sentence)."""
    text = html.escape(text, quote=False)
    if not words:
        return text
    exact = validate.key_term_pattern(words, 0)
    pattern = exact if exact.search(text) else validate.key_term_pattern(words)
    return pattern.sub(r'<mark class="term-hit">\g<0></mark>', text)


def term_english_html(term, lang):
    """The settled English words, one line for every level or one per level."""
    allowed = term["english"]
    levels = catalog(lang)["levels"]
    if not isinstance(allowed, dict):
        return (f'<p class="term-words"><span class="term-level">{t(lang, "terms.every_level")}</span> '
                f'<span lang="en">{", ".join(html.escape(w) for w in allowed)}</span></p>')
    return "".join(f'<p class="term-words"><span class="term-level">{levels[level]}</span> '
                   f'<span lang="en">{", ".join(html.escape(w) for w in allowed.get(level, []))}</span></p>'
                   for level in validate.LEVELS)


def term_lemma(term, cls="term-lemma"):
    return f'<span class="{cls}" lang="{term_key(term)[0]}">{html.escape(term["lemma"])}</span>'


def term_row(term, lang="en"):
    """A key term in a list: its lemma, sense, settled English and uses."""
    english = ", ".join(term_english(term))
    return (f'<li><a class="term-row" href="{url(lang, term_path(term))}">'
            f'{term_lemma(term)}'
            f'<span class="term-sense"{lang_attr("en", lang)}>{html.escape(term["sense"])}</span>'
            f'<span class="term-english"{lang_attr("en", lang)}>{html.escape(english)}</span>'
            f'<span class="term-count">{tn(lang, "terms.count", term_count(term))}</span></a></li>')


def home_terms(lang="en"):
    """The home page's key terms: six of the most used, up to two of them
    Hebrew, with a link to them all."""
    terms = list(validate.KEY_TERMS.values())

    def top(code):
        return sorted((x for x in terms if term_key(x)[0] == code), key=term_count, reverse=True)
    hebrew = top("hbo")[:2]
    shown = top("grc")[:6 - len(hebrew)] + hebrew
    return f"""<section class="home-terms" aria-labelledby="terms-h">
{sec_head("terms-h", "key", t(lang, "terms.heading"), url(lang, "/terms/"), t(lang, "nav.section_all", n=len(terms)))}
<p class="terms-text">{t(lang, "home.terms_text")}</p>
<ul class="term-list">{"".join(term_row(term, lang) for term in shown)}</ul>
</section>
"""


def terms_page(lang="en"):
    """Every key term, Greek and then Hebrew, with its settled English and
    how often the drafted text uses it."""
    def row(term):
        return term_row(term, lang)

    groups = []
    for code in ("grc", "hbo"):
        terms = sorted((term for term in validate.KEY_TERMS.values() if term_key(term)[0] == code),
                       key=lambda term: term["sense"].lower())
        if terms:
            groups.append(f'<section class="term-group" id="{code}" aria-labelledby="{code}-h">'
                          f'<h2 id="{code}-h">{t(lang, "terms.group_" + code)}</h2>'
                          f'<ul class="term-list">{"".join(row(term) for term in terms)}</ul></section>')
    note = f'<p class="fine">{t(lang, "notes_in_english")}</p>' if lang != "en" else ""
    body = f"""
<header class="page-head">
<p class="eyebrow">{t(lang, "terms.title")}</p>
<h1>{t(lang, "terms.heading")}</h1>
<p class="dek">{t(lang, "terms.dek")}</p>
</header>
<nav class="a-jump" aria-label="{t(lang, "terms.title")}"><ul>{"".join(
        f'<li><a href="#{code}">{t(lang, "terms.group_" + code)}</a></li>' for code in ("grc", "hbo"))}</ul></nav>
{note}
{"".join(groups)}
"""
    return page(lang, t(lang, "terms.title"), body, path="/terms/", current="/about/",
                description=t(lang, "meta.terms_description"))


# A term with more uses than this has each book's list folded away.
TERM_OPEN_USES = 40


def term_use_html(term, use, lang):
    """One sentence: its verse links, its Balanced English with the term's
    word marked, and the decision that explains a different word."""
    links = []
    for vid in use.verses:
        ref = refs.parse(vid)
        links.append(f'<a href="{url(lang, chapter_url(ref.book, ref.chapter))}#v{ref.verse}">'
                     f'{verse_name(ref.book, ref.chapter, ref.verse, lang)}</a>')
    english = use.record["renderings"].get("en", {})
    level = "B" if "B" in english else next(iter(english), "B")
    sentence = emphasise(plain(english.get(level, "")), validate.key_term_words(term, level))
    why = ""
    if use.decisions:
        levels = catalog(lang)["levels"]
        why = "".join(
            f'<div class="term-why"><p class="term-why-head">{t(lang, "terms.otherwise", levels=", ".join(levels[lv] for lv in use.departs))}</p>'
            f'<p class="term-why-text"{lang_attr("en", lang)}><strong>{html.escape(plain(d["choice"]))}</strong> '
            f'{html.escape(plain(d["reason"]))}</p></div>'
            for d in use.decisions)
    return (f'<li class="term-use{" departs" if use.decisions else ""}">'
            f'<p class="term-ref">{" ".join(links)}</p>'
            f'<p class="term-text"{lang_attr("en", lang)}>{sentence}</p>{why}</li>')


# A term with more uses than this gives each book's sentences a page of
# their own (/terms/<slug>/<book>/), so no page grows with the whole Bible.
TERM_SPLIT_USES = 300


def term_books(term):
    """A key term's uses by book, in canonical order."""
    by_book = {}
    for u in term_uses()[term_key(term)]:
        by_book.setdefault(refs.parse(u.verses[0]).book, []).append(u)
    return by_book


def term_split(term):
    """Whether a key term's sentences are on one page per book."""
    return term_count(term) > TERM_SPLIT_USES


def term_head(term, lang, heading, eyebrow):
    code = term_key(term)[0]
    return f"""
<header class="page-head term-head">
<p class="eyebrow">{eyebrow}</p>
<h1{heading[1]}>{heading[0]}</h1>
<p class="term-id">{term_lemma(term, "term-lemma big")}
<span class="term-strong">{t(lang, "terms.language_" + code)} &middot; Strong&rsquo;s {term_strong(term)}</span></p>
</header>"""


def term_book_chips(term, lang, current=None):
    """Each book's count of uses, linking to its list: further down the
    page, or to the book's own page when the term is split."""
    def href(book):
        return url(lang, term_path(term, book)) if term_split(term) else f"#{book.lower()}"
    return (f'<nav class="a-jump term-books" aria-label="{t(lang, "terms.by_book")}"><ul>'
            + "".join(f'<li><a href="{href(book)}"{" aria-current=page" if book == current else ""}>'
                      f'{book_name(book, lang)} <span>{sum(len(u.tokens) for u in us)}</span></a></li>'
                      for book, us in term_books(term).items())
            + "</ul></nav>")


def term_page(term, lang="en"):
    """One key term: its lemma, Strong's number and sense, its settled
    English at each level and the note on it, then its uses: counts by
    book, the exceptions, and every sentence by book (or, for a term with
    many uses, a link to each book's page)."""
    uses = term_uses()[term_key(term)]
    total = term_count(term)
    by_book = term_books(term)
    note = f'<p class="fine">{t(lang, "notes_in_english")}</p>' if lang != "en" else ""
    if uses:
        departs = [u for u in uses if u.decisions]
        exceptions = (f'<section class="term-section" aria-labelledby="otherwise-h">'
                      f'<h2 id="otherwise-h">{t(lang, "terms.exceptions")} <span class="term-count">{len(departs)}</span></h2>'
                      f'<p class="fine">{t(lang, "terms.exceptions_dek")}</p>'
                      f'<ol class="term-uses">{"".join(term_use_html(term, u, lang) for u in departs)}</ol></section>'
                      if departs else "")
        if term_split(term):
            sentences = f'<p class="fine">{t(lang, "terms.books_dek")}</p>'
        else:
            openly = " open" if total <= TERM_OPEN_USES else ""
            books_html = "".join(
                f'<details class="term-book" id="{book.lower()}"{openly}><summary>{book_name(book, lang)} '
                f'<span class="term-count">{tn(lang, "terms.count", sum(len(u.tokens) for u in us))}</span></summary>'
                f'<ol class="term-uses">{"".join(term_use_html(term, u, lang) for u in us)}</ol></details>'
                for book, us in by_book.items())
            sentences = (f'<section class="term-section" aria-labelledby="uses-h"><h2 id="uses-h">{t(lang, "terms.uses")}</h2>'
                         f'<p class="fine">{t(lang, "terms.uses_dek")}</p>{books_html}</section>')
        listing = (f'<p>{t(lang, "terms.summary", times=tn(lang, "terms.times", total), books=tn(lang, "terms.books", len(by_book)))}</p>'
                   f'{term_book_chips(term, lang)}'
                   + (f'{sentences}{exceptions}' if term_split(term) else f'{exceptions}{sentences}'))
    else:
        listing = f'<p class="notice">{t(lang, "terms.none")}</p>'
    head = term_head(term, lang, (html.escape(term["sense"]), lang_attr("en", lang)),
                     f'<a href="{url(lang, "/terms/")}">{t(lang, "terms.title")}</a>')
    body = f"""{head}
<section class="term-section" aria-labelledby="settled-h">
<h2 id="settled-h">{t(lang, "terms.settled")}</h2>
{term_english_html(term, lang)}
<p class="term-note"{lang_attr("en", lang)}>{html.escape(term.get("note", ""))}</p>
{note}
</section>
<section class="term-section" aria-labelledby="where-h">
<h2 id="where-h">{t(lang, "terms.where")}</h2>
{listing}
</section>
"""
    return page(lang, f'{term["sense"]} · {t(lang, "terms.title")}', body, path=term_path(term),
                current="/about/",
                description=t(lang, "meta.term_description", sense=term["sense"], lemma=term["lemma"]))


def term_book_page(term, book, lang="en"):
    """Every sentence in one book that uses a key term with many uses."""
    us = term_books(term)[book]
    name = book_name(book, lang)
    eyebrow = (f'<a href="{url(lang, "/terms/")}">{t(lang, "terms.title")}</a> &middot; '
               f'<a href="{url(lang, term_path(term))}"{lang_attr("en", lang)}>{html.escape(term["sense"])}</a>')
    note = f'<p class="fine">{t(lang, "notes_in_english")}</p>' if lang != "en" else ""
    body = f"""{term_head(term, lang, (name, ""), eyebrow)}
<section class="term-section" aria-labelledby="uses-h">
{term_book_chips(term, lang, book)}
<h2 id="uses-h">{t(lang, "terms.uses")} <span class="term-count">{tn(lang, "terms.count", sum(len(u.tokens) for u in us))}</span></h2>
<p class="fine">{t(lang, "terms.uses_dek")}</p>
{note}
<ol class="term-uses">{"".join(term_use_html(term, u, lang) for u in us)}</ol>
</section>
"""
    return page(lang, f'{term["sense"]} · {name} · {t(lang, "terms.title")}', body,
                path=term_path(term, book), current="/about/",
                description=t(lang, "meta.term_book_description", sense=term["sense"],
                              lemma=term["lemma"], book=name))


ARTICLES = ROOT / "articles"
_ORIGINAL = re.compile(r"\{\{(GREEK|HEBREW):([A-Z0-9]+)\.(\d+)\.(\d+):(\d+)(?:-(\d+))?\}\}")
_LEMMA = re.compile(r"\{\{LEMMA:([A-Z0-9]+)\.(\d+)\.(\d+):(\d+)(?:\.(\d+))?\}\}")
_OWB = re.compile(r"\{\{OWB:([A-Z0-9.]+\.s\d+):([LBR])\}\}")

# How articles show each source language: the placeholder that quotes it,
# the class and attributes of its spans, and how the data's words join.
# Greek "after" holds punctuation that may lack its space; Hebrew "after"
# is the exact join between parts of a word and between words (maqaf).
ORIGINAL = {
    "grc": {"tag": "GREEK", "name": "greek", "attrs": 'lang="grc"',
            "join": lambda ws: " ".join([w["text"] + w["after"].rstrip() for w in ws[:-1]] + [ws[-1]["text"]])},
    "hbo": {"tag": "HEBREW", "name": "hebrew", "attrs": 'lang="hbo" dir="rtl"',
            "join": lambda ws: "".join(w["text"] + w["after"] for w in ws[:-1]) + ws[-1]["text"]},
}


@functools.lru_cache(maxsize=None)
def _chapter_words(book, chapter):
    return json.loads(words_path(book, chapter).read_text(encoding="utf-8"))["verses"]


def _verse_words(book, chapter, verse):
    """The MACULA words of one verse, from the committed extract: data/grc/
    for the New Testament, data/hbo/ for the Old. A Hebrew word can be
    several entries (prefixes, the word, suffixes) sharing one position."""
    verses = _chapter_words(book, chapter)
    vid = f"{book}.{chapter}.{verse}"
    if vid not in verses:
        raise SystemExit(f"{vid} is not in {words_path(book, chapter).name}; add it with scripts/extract_tokens.py")
    return verses[vid]


def _original_span(book, text):
    spec = ORIGINAL[source_language(book)]
    return f'<span class="{spec["name"]}" {spec["attrs"]}>{html.escape(text)}</span>'


def _original(m):
    """{{GREEK:JHN.1.1:14-17}}: words 14 to 17 of John 1:1 as the data has
    them; {{HEBREW:GEN.1.1:1-3}} the same for the Old Testament. The last
    word's punctuation (a Hebrew verse's sof pasuq) is left off."""
    tag, book, chapter, verse, a = m[1], m[2], int(m[3]), int(m[4]), int(m[5])
    b = int(m[6] or a)
    want = ORIGINAL[source_language(book)]["tag"]
    if tag != want:
        raise SystemExit(f"{m[0]}: {book} is quoted with {{{{{want}:..}}}}")
    words = [w for w in _verse_words(book, chapter, verse) if a <= w["position"] <= b]
    if not words:
        raise SystemExit(f"{m[0]}: no such words")
    return _original_span(book, ORIGINAL[source_language(book)]["join"](words))


def _lemma(m):
    """{{LEMMA:JHN.1.14:17}}: the dictionary form of word 17 of John 1:14.
    A Hebrew word made of several parts names the part:
    {{LEMMA:GEN.1.1:1.2}} is the second part of word 1 of Genesis 1:1."""
    book = m[1]
    parts = [w for w in _verse_words(book, int(m[2]), int(m[3])) if w["position"] == int(m[4])]
    chosen = parts[int(m[5]) - 1:int(m[5])] if m[5] else parts
    if len(chosen) != 1:
        found = ", ".join(f"{m[4]}.{i}" for i in range(1, len(parts) + 1))
        raise SystemExit(f"{m[0]}: word {m[4]} has {len(parts)} parts; name one ({found})")
    return _original_span(book, chosen[0]["lemma"])


def _owb(m, lang="en"):
    """{{OWB:JHN.1.1.s1:B}}: our translation of a sentence in lang (English
    if it is not in lang yet), with default settings."""
    record_id, level = m[1], m[2]
    ref = refs.parse(record_id.rsplit(".s", 1)[0])
    record = next((r for r in chapter_records(ref.book, ref.chapter) if r["id"] == record_id), None)
    if record is None:
        raise SystemExit(f"no record {record_id} in content/")
    return html.escape(plain(record["renderings"][text_lang(record, lang)][level]))


def smart_quotes(s):
    """Curly quotes and apostrophes for straight ones in plain text."""
    s = re.sub(r'(^|[\s(\[\u2014-])"', "\\1\u201c", s)
    s = s.replace('"', "\u201d")
    s = re.sub(r"(^|[\s(\[\u2014-])'", "\\1\u2018", s)
    return s.replace("'", "\u2019")


@functools.lru_cache(maxsize=None)
def translated_verses():
    """Every verse id with a record, so article links only go to verses the
    reader has."""
    return frozenset(v for r in all_records() for v in r["refs"])


def verse_link(book, chapter, verse, lang="en"):
    """The reader URL for a verse, or None when it is not translated yet."""
    if f"{book}.{chapter}.{verse}" not in translated_verses():
        return None
    return f"{url(lang, chapter_url(book, chapter))}#v{verse}"


def verse_name(book, chapter, verse, lang="en"):
    return f"{chapter_book(book, lang)} {chapter}:{verse}"


def _quote_figure(body, inner, lang, text_language):
    """A blockquote that is just one {{GREEK:..}}, {{HEBREW:..}} or {{OWB:..}} placeholder
    becomes a figure captioned with its source, linked to the reader. The
    caption is in the article's language; the link goes to the reader in
    the page's."""
    m = _ORIGINAL.fullmatch(body)
    if m:
        book, chapter, verse = m[2], int(m[3]), int(m[4])
        spec = ORIGINAL[source_language(book)]
        kind, attrs = f'{spec["name"]}-quote', f' {spec["attrs"]}'
        source = t(text_language, f'article.{spec["name"]}_source')
    else:
        m = _OWB.fullmatch(body)
        if not m:
            return f"<blockquote><p>{inner}</p></blockquote>"
        ref = refs.parse(m[1].rsplit(".s", 1)[0])
        book, chapter, verse = ref.book, ref.chapter, ref.verse
        source = t(text_language, "article.owb_source", level=catalog(text_language)["levels"][m[2]])
        kind, attrs = "owb-quote", ""
    link = verse_link(book, chapter, verse, lang)
    more = f' <a href="{link}">{t(text_language, "article.read_with_reasoning")}</a>' if link else ""
    return (f'<figure class="quote {kind}"><blockquote{attrs}><p>{inner}</p></blockquote>'
            f"<figcaption>{verse_name(book, chapter, verse, text_language)} &middot; {source}{more}</figcaption></figure>")


def _slug(text, taken):
    base = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-") or "section"
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1
    taken.add(slug)
    return slug


def article_html(text, toc=None, lang="en", text_language="en"):
    """Markdown for articles: ## and ### headings, paragraphs, - lists,
    > quotes, **bold**, *italic*, [links](url), and placeholders that pull
    Greek and Hebrew words ({{GREEK:..}}, {{HEBREW:..}}, {{LEMMA:..}}) and our own translation
    ({{OWB:..}}) from the data, so none of it is typed by hand. The text is
    in text_language, on a page in lang: links to the site go to its pages
    in lang."""
    fills = []

    def hold(html_text):
        fills.append(html_text)
        return f"\x00{len(fills) - 1}\x00"

    def href(target):
        # An article not written in lang yet is linked in English.
        m = re.fullmatch(r"/articles/([\w-]+)/", target)
        if m and lang != "en" and not (ARTICLES / lang / f"{m[1]}.md").is_file():
            return target
        return url(lang, target) if target.startswith("/") else target

    def inline(s):
        s = _ORIGINAL.sub(lambda m: hold(_original(m)), s)
        s = _LEMMA.sub(lambda m: hold(_lemma(m)), s)
        s = _OWB.sub(lambda m: hold(_owb(m, text_language)), s)
        s = re.sub(r"\]\(([^)\s]+)\)", lambda m: "](" + hold(html.escape(href(m[1]))) + ")", s)
        s = html.escape(smart_quotes(s), quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                   lambda m: f'<a href="{m[2]}">{m[1]}</a>', s)
        return re.sub("\x00(\\d+)\x00", lambda m: fills[int(m[1])], s)

    taken = set()
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line.rstrip() for line in block.splitlines()]
        if lines[0].startswith("#"):
            level = len(lines[0]) - len(lines[0].lstrip("#"))
            heading = inline(lines[0].lstrip("#").strip())
            if level == 2:
                slug = _slug(heading, taken)
                if toc is not None:
                    toc.append((slug, heading))
                out.append(f'<h2 id="{slug}">{heading}</h2>')
            else:
                out.append(f"<h{level}>{heading}</h{level}>")
        elif lines[0].startswith("- "):
            items, cur = [], []
            for line in lines:
                if line.startswith("- ") and cur:
                    items.append(" ".join(cur))
                    cur = []
                cur.append(line[2:] if line.startswith("- ") else line.strip())
            items.append(" ".join(cur))
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
        elif lines[0].startswith(">"):
            body = " ".join(line.lstrip(">").strip() for line in lines)
            out.append(_quote_figure(body, inline(body), lang, text_language))
        else:
            out.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(out)


# Article sections, in the order the articles page shows them. Their names
# in each language are in i18n/ (sections).
SECTIONS = {"method": "How it is made", "passage": "Reading the text", "history": "How we got the Bible",
            "translation": "The Bible in translation", "compare": "Comparing translations"}


def article_passages(body):
    """The verses an article quotes, from its placeholders, as
    [(book, chapter, [verses])] in canonical order."""
    found = set()
    for m in _ORIGINAL.finditer(body):
        found.add((m[2], int(m[3]), int(m[4])))
    for m in _LEMMA.finditer(body):
        found.add((m[1], int(m[2]), int(m[3])))
    for m in _OWB.finditer(body):
        ref = refs.parse(m[1].rsplit(".s", 1)[0])
        found.add((ref.book, ref.chapter, ref.verse))
    chapters_ = {}
    for book, chapter, verse in sorted(found, key=lambda f: refs.Ref(*f).sort_key()):
        chapters_.setdefault((book, chapter), []).append(verse)
    return [(b, c, vs) for (b, c), vs in chapters_.items()]


def passage_label(book, chapter, verses, lang="en"):
    """"John 1:1, 14, 16–18": consecutive verses become ranges."""
    runs = []
    for v in verses:
        if runs and v == runs[-1][1] + 1:
            runs[-1][1] = v
        else:
            runs.append([v, v])
    return f"{chapter_book(book, lang)} {chapter}:" + ", ".join(
        str(a) if a == b else f"{a}–{b}" for a, b in runs)


def _read_article(path):
    """One article file. It starts with a front matter block: title,
    summary, date, order, section (a key of SECTIONS), and optionally
    nav_title, a shorter title for the header menu, and part (a key of
    PARTS), the part of a series it belongs to."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing the --- front matter block")
    meta = {}
    for line in m[1].splitlines():
        if line.strip():
            key, value = line.split(": ", 1)
            # A value may be JSON-quoted when it contains quotation marks.
            meta[key] = json.loads(value) if value.startswith('"') else value
    for key in ("title", "summary", "date", "order", "section"):
        if key not in meta:
            raise SystemExit(f"{path.name}: front matter needs {key!r}")
    if meta["section"] not in SECTIONS:
        raise SystemExit(f"{path.name}: section must be one of {', '.join(SECTIONS)}")
    if "part" in meta and meta["part"] not in PARTS:
        raise SystemExit(f"{path.name}: part must be one of {', '.join(PARTS)}")
    meta["title"], meta["summary"] = smart_quotes(meta["title"]), smart_quotes(meta["summary"])
    if "nav_title" in meta:
        meta["nav_title"] = smart_quotes(meta["nav_title"])
    words = len(re.findall(r"\w+", re.sub(r"\{\{[^}]*\}\}", "", m[2])))
    return {**meta, "slug": path.stem, "body": m[2], "order": int(meta["order"]),
            "minutes": max(1, round(words / 220)), "passages": article_passages(m[2])}


def load_articles(lang="en"):
    """The articles written in lang, newest first, then by their order
    number. An English article is articles/<slug>.md and its translation
    articles/<lang>/<slug>.md; a language shows only its own articles, never
    the English of one not translated yet."""
    folder = ARTICLES if lang == "en" else ARTICLES / lang
    articles = [{**_read_article(path), "lang": lang}
                for path in sorted(folder.glob("*.md")) if (ARTICLES / path.name).is_file()]
    return sorted(articles, key=lambda a: (a["date"], -a["order"]), reverse=True)


def article_languages(article):
    """The languages an article is written in, English first."""
    return tuple(code for code in LANGUAGES
                 if (ARTICLES if code == "en" else ARTICLES / code).joinpath(f"{article['slug']}.md").is_file())


def article_url(article):
    return f"/articles/{article['slug']}/"


def _date(iso, lang="en"):
    import datetime
    day = datetime.date.fromisoformat(iso)
    return t(lang, "date", d=day.day, month=catalog(lang)["months"][day.month - 1], y=day.year)


def display(text):
    """Escaped text for the page, with a verse range's dash ("4:6–7") kept
    on one line. Only the visible HTML gets the word joiners; titles and
    link previews keep the plain text."""
    return re.sub(r"(\d)\u2013(\d)", "\\1\u2060\u2013\u2060\\2", html.escape(text))


# Sections that are series, read in order: their articles are numbered parts.
SERIES = ("history", "translation")


@functools.lru_cache(maxsize=None)
def series_numbers():
    """Each series article's part number and its series' length, from the
    English articles, so a part keeps its number in every language:
    {slug: (n, total)}."""
    numbers = {}
    english = sorted(load_articles("en"), key=lambda a: a["order"])
    for key in SERIES:
        parts = [a["slug"] for a in english if a["section"] == key]
        numbers.update({slug: (n, len(parts)) for n, slug in enumerate(parts, 1)})
    return numbers


def article_meta(a, lang="en"):
    """"6 min read · John 1:1, 14": what a card or byline says about length
    and which verses an article reads; for a part of a series, "7 min read ·
    Part 4 of 20"."""
    parts = [html.escape(t(lang, "article.min_read", n=a["minutes"]))]
    if a["slug"] in series_numbers():
        n, total = series_numbers()[a["slug"]]
        parts.append(html.escape(t(lang, "article.part", n=n, total=total)))
    parts += [html.escape(passage_label(*p, lang)) for p in a["passages"]]
    return " &middot; ".join(parts)


def article_card(a, lang="en"):
    """An article's card on the home page and under "Keep reading"."""
    return (f'<li><a class="a-card" href="{url(lang, article_url(a))}">'
            f'<span class="a-section">{catalog(lang)["sections"][a["section"]]}</span>'
            f'<span class="a-title">{display(a["title"])}</span>'
            f'<span class="a-summary">{display(a["summary"])}</span>'
            f'<span class="a-meta">{article_meta(a, lang)}</span></a></li>')


def article_list(articles, lang="en"):
    return "".join(article_card(a, lang) for a in articles)


def feed_url(lang):
    return url(lang, "/articles/feed.xml")


def articles_feed(articles, lang="en"):
    """An Atom feed of the articles in lang, newest first."""
    def esc(text):
        return html.escape(text, quote=False)
    newest = max(a["date"] for a in articles)
    entries = "".join(
        f"<entry><title>{esc(a['title'])}</title>"
        f'<link href="{html.escape(SITE_URL + url(lang, article_url(a)))}"/>'
        f"<id>{esc(SITE_URL + url(lang, article_url(a)))}</id>"
        f"<updated>{a['date']}T00:00:00Z</updated>"
        f"<summary>{esc(a['summary'])}</summary></entry>\n"
        for a in articles)
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            f'<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{lang}">\n'
            f"<title>{esc(SITE_NAME + ' · ' + t(lang, 'articles.title'))}</title>\n"
            f'<link href="{html.escape(SITE_URL + url(lang, "/articles/"))}"/>\n'
            f'<link rel="self" href="{html.escape(SITE_URL + feed_url(lang))}"/>\n'
            f"<id>{esc(SITE_URL + url(lang, '/articles/'))}</id>\n"
            f"<updated>{newest}T00:00:00Z</updated>\n"
            f"<author><name>{SITE_NAME}</name></author>\n"
            f"{entries}</feed>\n")

# Parts a series can be split into (an article's "part" front matter).
PARTS = ("ot", "nt", "today")


def _duration(minutes, lang="en"):
    """"45 min" or "2 h 20 min"."""
    h, m = divmod(minutes, 60)
    return t(lang, "articles.hours", h=h, m=m) if h else t(lang, "articles.minutes", m=m)


def index_row(a, lang="en", number=None, minutes=True):
    """An article's row on the articles page. The title is the link and
    covers the row; the verses it reads are links of their own."""
    refs = []
    for b, c, vs in a["passages"]:
        label = html.escape(passage_label(b, c, vs, lang))
        href = next(filter(None, (verse_link(b, c, v, lang) for v in vs)), None)
        refs.append(f'<a class="a-ref" href="{href}">{label}</a>' if href else f'<span class="a-ref">{label}</span>')
    meta = html.escape(t(lang, "article.min_read", n=a["minutes"])) if minutes else ""
    num = f'<span class="a-num" aria-hidden="true">{number}</span>' if number else ""
    return (f'<li class="a-item{" numbered" if number else ""}">{num}<div class="a-body">'
            + (f'<p class="a-refs">{"".join(refs)}</p>' if refs else "")
            + f'<a class="a-title" href="{url(lang, article_url(a))}">{display(a["title"])}</a>'
            f'<span class="a-summary">{display(a["summary"])}</span>'
            + (f'<span class="a-meta">{meta}</span>' if meta else "") + '</div></li>')


def _section(key, items, lang="en"):
    """A section of the articles page: its heading with how many articles
    and how long they take, then a row for each. When most of a section's
    articles take the same time, a row says its time only if it differs."""
    names = catalog(lang)["sections"]
    times = [a["minutes"] for a in items]
    common = max(set(times), key=times.count)
    usual = times.count(common) >= .75 * len(times) and len(times) > 2
    sub = t(lang, "articles.count_time", n=len(items), time=_duration(sum(times), lang))
    numbers = {id(a): i for i, a in enumerate(items, 1)}

    def rows(part_items):
        return "".join(index_row(a, lang, number=numbers[id(a)] if key in SERIES else None,
                                 minutes=not usual or a["minutes"] != common)
                       for a in part_items)
    head = f'<div class="a-group-head"><h2 id="{key}-h">{names[key]}</h2><span>{sub}</span></div>'
    cls = f'a-rows{" series" if key in SERIES else ""}'
    if any("part" in a for a in items):
        # A series in parts: a heading for each, numbers running on.
        parts = catalog(lang)["parts"]
        body = ""
        for part in PARTS:
            group = [a for a in items if a.get("part") == part]
            if group:
                first, last = numbers[id(group[0])], numbers[id(group[-1])]
                span = f"{first}\u2013{last}" if last > first else f"{first}"
                body += (f'<div class="a-part"><h3>{parts[part]} <span>{span}</span></h3>'
                         f'<ol class="{cls}" start="{first}">{rows(group)}</ol></div>')
        return f'<section class="a-group" id="{key}" data-section="{key}" aria-labelledby="{key}-h">{head}{body}</section>'
    return (f'<section class="a-group" id="{key}" data-section="{key}" aria-labelledby="{key}-h">{head}'
            f'<ol class="{cls}">{rows(items)}</ol></section>')


def articles_page(articles, lang="en"):
    """The articles in lang, or a note that none is translated yet: the
    first article with the next few to read, then every other article under
    its section. web/site.js turns the section links into filters and shows
    a search box."""
    by_order = sorted(articles, key=lambda a: a["order"])
    head_extra = ""
    if by_order:
        featured, rest = by_order[0], by_order[1:]
        names = catalog(lang)["sections"]
        # The featured article opens the page, so its section starts after it.
        groups = [(key, [a for a in rest if a["section"] == key]) for key in SECTIONS]
        groups = [(key, items) for key, items in groups if items]
        # Links to each section, with how many articles it has; with
        # JavaScript they filter the list, and a search box narrows it.
        chips = [f'<li><a href="#" data-filter="all">{t(lang, "articles.all")} <span>{len(rest)}</span></a></li>']
        chips += [f'<li><a href="#{key}" data-filter="{key}">{names[key]} <span>{len(items)}</span></a></li>'
                  for key, items in groups]
        tools = (f'<div class="a-tools">'
                 f'<nav class="a-jump" aria-label="{t(lang, "articles.sections")}"><ul>{"".join(chips)}</ul></nav>'
                 f'<label class="a-search" hidden><span class="sr-only">{t(lang, "articles.search")}</span>'
                 f'{icon(ICONS["search"], 16)}'
                 f'<input type="search" id="a-search" placeholder="{html.escape(t(lang, "articles.search_placeholder"))}" autocomplete="off"></label>'
                 f'</div>')
        # The first article, with the next few of its section to read after it.
        after = [a for a in rest if a["section"] == featured["section"]][:3]
        path = "".join(f'<li><a href="{url(lang, article_url(a))}">{display(a.get("nav_title", a["title"]))}</a></li>'
                       for a in after)
        start = (f'<div class="a-start" id="a-start"><a class="a-card featured" href="{url(lang, article_url(featured))}">'
                 f'<span class="a-section">{t(lang, "articles.start_here")}</span>'
                 f'<span class="a-title">{display(featured["title"])}</span>'
                 f'<span class="a-summary">{display(featured["summary"])}</span>'
                 f'<span class="a-meta">{article_meta(featured, lang)}</span></a>'
                 + (f'<nav class="a-path" aria-labelledby="a-path-h"><h2 id="a-path-h">{t(lang, "articles.then_read")}</h2>'
                    f'<ol>{path}</ol></nav>' if after else "")
                 + '</div>')
        sections = "".join(_section(key, items, lang) for key, items in groups)
        feed = (f'<p class="a-feed"><a href="{feed_url(lang)}">{icon(ICONS["feed"], 16)}'
                f'{t(lang, "articles.feed")}</a></p>')
        listing = (f'{start}\n<div class="a-index" id="a-index">{tools}\n'
                   f'<p class="notice" id="a-none" role="status" hidden>{t(lang, "articles.no_match")}</p>\n'
                   f'{sections}</div>\n{feed}')
        head_extra = (f'\n<link rel="alternate" type="application/atom+xml" '
                      f'title="{html.escape(SITE_NAME + " · " + t(lang, "articles.title"))}" href="{feed_url(lang)}">')
    else:
        listing = f'<p class="notice">{t(lang, "articles.none")}</p>'
    body = f"""
<header class="page-head compact">
<p class="eyebrow">{t(lang, "articles.title")}</p>
<h1>{t(lang, "articles.heading")}</h1>
<p class="dek">{t(lang, "articles.dek")}</p>
</header>
{listing}
"""
    return page(lang, t(lang, "articles.title"), body, path="/articles/", current="/articles/",
                description=t(lang, "meta.articles_description"), head=head_extra)


def series_nav(article, articles, lang="en"):
    """For a part of a series: its number, and the parts before and after it
    that are written in lang."""
    if article["slug"] not in series_numbers():
        return ""
    n, total = series_numbers()[article["slug"]]
    parts = sorted((a for a in articles if a["slug"] in series_numbers() and a["section"] == article["section"]),
                   key=lambda a: a["order"])
    i = parts.index(article)

    def turn(a, cls, key):
        if a is None:
            return ""
        m = series_numbers()[a["slug"]][0]
        return (f'<a class="s-turn {cls}" href="{url(lang, article_url(a))}">'
                f'<span class="s-dir">{t(lang, "article." + key)} &middot; {t(lang, "article.part_short", n=m)}</span>'
                f'<span class="s-title">{display(a["title"])}</span></a>')
    before = parts[i - 1] if i > 0 else None
    after = parts[i + 1] if i + 1 < len(parts) else None
    section = catalog(lang)["sections"][article["section"]]
    return (f'<nav class="series" aria-labelledby="series-h">'
            f'<div class="series-head"><h2 id="series-h">{section} &middot; {t(lang, "article.part", n=n, total=total)}</h2>'
            f'<a href="{url(lang, "/articles/")}#{article["section"]}">{t(lang, "article.series_all", n=total)}</a></div>'
            f'{meter(n, total)}'
            f'<div class="s-turns">{turn(before, "prev", "previous")}{turn(after, "next", "next")}</div></nav>')


def article_page(article, articles, lang="en"):
    """An article on a page in its own language, lang."""
    toc = []
    content = article_html(article["body"], toc, lang, lang)
    same = [a for a in articles if a is not article and a["section"] == article["section"]]
    other = [a for a in articles if a is not article and a["section"] != article["section"]]
    more = sorted(same, key=lambda a: a["order"])[:2] + sorted(other, key=lambda a: a["order"])[:1]
    contents = "".join(f'<li><a href="#{slug}">{label}</a></li>' for slug, label in toc)
    links = [(passage_label(b, c, vs, lang), next(filter(None, (verse_link(b, c, v, lang) for v in vs)), None))
             for b, c, vs in article["passages"]]
    read = "".join(f'<a class="chip" href="{href}">{html.escape(label)}&nbsp;&rarr;</a>'
                   for label, href in links if href)
    passage = (f'<aside class="read-card"><h2>{t(lang, "article.read_passage")}</h2>'
               f'<p>{t(lang, "article.read_passage_text")}</p><p>{read}</p></aside>'
               if read else "")
    section = catalog(lang)["sections"][article["section"]]
    part = ""
    if article["slug"] in series_numbers():
        n, total = series_numbers()[article["slug"]]
        part = " &middot; " + t(lang, "article.part", n=n, total=total)
    body = f"""
<div class="article-layout">
<article class="article">
<header class="article-head">
<p class="eyebrow"><a href="{url(lang, "/articles/")}#{article["section"]}">{section}</a>{part}</p>
<h1>{display(article["title"])}</h1>
<p class="dek">{display(article["summary"])}</p>
<p class="byline">{MARK}<span>Open Word Bible &middot; {_date(article["date"], lang)} &middot; {t(lang, "article.min_read", n=article["minutes"])}</span></p>
</header>
<div class="article-body">
{content}
</div>
{passage}
{series_nav(article, articles, lang)}
</article>
{f'<nav class="toc" aria-labelledby="toc-h"><h2 id="toc-h">{t(lang, "article.on_this_page")}</h2><ol>{contents}</ol></nav>' if len(toc) > 1 else ""}
</div>
<section class="more" aria-labelledby="more-h"><h2 id="more-h">{t(lang, "article.keep_reading")}</h2>
{f'<ul class="a-grid">{article_list(more, lang)}</ul>' if more else ""}
<p><a href="{url(lang, "/articles/")}">{t(lang, "article.all")}</a></p></section>
{article_ld(article, lang)}
"""
    return page(lang, article["title"], body, path=article_url(article), current="/articles/",
                card=og_card_article(article),
                card_alt=t(lang, "meta.article_card_alt", section=section,
                           title=article["title"], summary=article["summary"]),
                description=article["summary"],
                translated=article_languages(article))


def article_ld(article, lang):
    """schema.org data for an article. Its author is the project: every
    article is drafted with AI help, as the articles page says, so it names
    no person."""
    data = {"@context": "https://schema.org", "@type": "Article",
            "headline": article["title"], "description": article["summary"],
            "url": SITE_URL + url(lang, article_url(article)), "inLanguage": lang,
            "datePublished": article["date"], "author": ORGANIZATION, "publisher": ORGANIZATION,
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + url(lang, "/")}}
    card = og_card_article(article)
    if (OG / f"{card}.jpg").is_file():
        data["image"] = f"{SITE_URL}/og/{card}.jpg"
    return ld_script(data)


@functools.lru_cache(maxsize=None)
def chapter_articles(lang):
    """The articles in lang that read each chapter: {(book, chapter): [article]},
    in the articles' order."""
    found = {}
    for a in sorted(load_articles(lang), key=lambda a: a["order"]):
        # article_passages gives each chapter once.
        for b, c, _ in a["passages"]:
            found.setdefault((b, c), []).append(a)
    return found


def chapter_articles_html(book, chapter, lang="en"):
    """Under a chapter: the articles that read it closely."""
    items = chapter_articles(lang).get((book, chapter))
    if not items:
        return ""
    return (f'<aside class="chapter-articles" aria-labelledby="ch-articles-h">'
            f'<h2 id="ch-articles-h">{t(lang, "reader.articles")}</h2>'
            f'<ul class="a-grid">{article_list(items, lang)}</ul></aside>')


GOOGLE_G = ('<svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">'
            '<path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 '
            '14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>'
            '<path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 '
            '5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>'
            '<path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19'
            'C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>'
            '<path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 '
            '2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>')


def _ui_json(lang, key):
    return json.dumps(catalog(lang)[key], ensure_ascii=False).replace("</", "<\\/")


def _password_field(lang, field_id, label, autocomplete):
    """A password input with a Show/Hide button and the rule under it."""
    return f"""<label for="{field_id}">{label}</label>
<div class="pw-field">
<input id="{field_id}" name="password" type="password" minlength="8" autocomplete="{autocomplete}" required aria-describedby="{field_id}-hint">
<button type="button" class="pw-toggle" aria-controls="{field_id}" aria-pressed="false">{t(lang, "login.show")}</button>
</div>
<p class="fine" id="{field_id}-hint">{t(lang, "login.password_hint")}</p>"""


def login_page(lang="en"):
    """Signing in, creating an account and asking for a reset link, one page
    in three modes (?mode=signup, ?mode=reset), as on Ochorus; and where the
    links in sign-in and confirmation emails, and Google, land (#token=,
    #google=). web/account.js runs it. Not in the sitemap, and not indexed."""
    def l(key):
        return t(lang, "login." + key)

    def modes(**text):
        return "".join(f'<span data-for="{m}"{"" if m == "sign-in" else " hidden"}>{v}</span>'
                       for m, v in text.items())

    body = f"""
<section class="auth" id="login" data-mode="sign-in">
<div data-view="form">
<header class="auth-head">
{MARK}
<h1>{modes(**{"sign-in": l("title_sign_in"), "sign-up": l("title_sign_up"), "reset": l("title_reset")})}</h1>
<p class="auth-dek">{l("dek")}</p>
</header>
<form class="auth-card" id="login-form" novalidate>
<div class="google" data-for="sign-in sign-up" hidden>
<button class="button ghost wide google-btn" type="button" id="google">{GOOGLE_G}<span>{l("google")}</span></button>
<p class="or"><span>{l("or")}</span></p>
</div>
<label for="email">{l("email")}</label>
<input id="email" name="email" type="email" autocomplete="email" inputmode="email" placeholder="you@example.com" required aria-describedby="login-error">
<div class="pw" data-for="sign-in sign-up">
{_password_field(lang, "password", l("password"), "current-password")}
</div>
<p class="form-error" id="login-error" role="alert"></p>
<button class="button wide" type="submit">{modes(**{"sign-in": l("submit_sign_in"), "sign-up": l("submit_sign_up"), "reset": l("submit_reset")})}</button>
<div class="auth-alt" data-for="sign-in sign-up">
<button class="button ghost wide" type="button" id="magic">{l("magic")}</button>
</div>
<p class="forgot" data-for="sign-in"><a href="?mode=reset" data-mode-link="reset">{l("forgot")}</a></p>
</form>
<p class="auth-switch" data-for="sign-in">{l("new")} <a href="./" data-mode-link="sign-up">{l("create")}</a></p>
<p class="auth-switch" data-for="sign-up" hidden>{l("have")} <a href="./" data-mode-link="sign-in">{l("sign_in")}</a></p>
<p class="auth-switch" data-for="reset" hidden><a href="./" data-mode-link="sign-in">{l("back")}</a></p>
<p class="fine auth-privacy">{l("privacy")} <a href="{url(lang, "/about/privacy/")}">{t(lang, "nav.privacy")}</a> &middot; <a href="{url(lang, "/about/terms-of-use/")}">{t(lang, "nav.terms_of_use")}</a></p>
</div>

<div class="auth-card auth-message" data-view="sent" hidden>
<p class="badge" aria-hidden="true">&#9993;</p>
<h2 tabindex="-1">{l("check_title")}</h2>
<p id="sent-text"></p>
<p class="fine">{l("resend_prompt")}</p>
<p><button class="button ghost" type="button" id="resend">{l("resend")}</button></p>
<p class="form-note" id="resend-note" role="status"></p>
<p><a href="./" data-mode-link="sign-in">{l("back")}</a></p>
</div>

<div class="auth-card auth-message" data-view="confirm" hidden>
<p class="badge" aria-hidden="true">&#9993;</p>
<h2>{l("confirm_title")}</h2>
<p>{l("confirm_text")}</p>
<p><button class="button wide" type="button" id="finish">{l("finish")}</button></p>
</div>
</section>
<script type="application/json" id="login-text">{_ui_json(lang, "login.ui")}</script>
<script src="{asset("account.js")}" defer></script>
"""
    return page(lang, t(lang, "tools.sign_in"), body, unlisted="/login/")


def reset_page(lang="en"):
    """Choosing a new password, from the link in a reset email
    (#token=); web/account.js runs it. Not indexed."""
    def r(key):
        return t(lang, "reset." + key)

    body = f"""
<section class="auth" id="reset">
<div data-view="form" hidden>
<header class="auth-head">
{MARK}
<h1>{r("title")}</h1>
<p class="auth-dek">{r("dek")}</p>
</header>
<form class="auth-card" id="reset-form" novalidate>
{_password_field(lang, "new-password", r("new_password"), "new-password")}
<p class="form-error" id="reset-error" role="alert"></p>
<button class="button wide" type="submit">{r("submit")}</button>
</form>
</div>
<div class="auth-card auth-message" data-view="done" hidden>
<p class="badge" aria-hidden="true">&#10003;</p>
<h2>{r("done_title")}</h2>
<p>{r("done_text")}</p>
<p><a class="button wide" href="{url(lang, "/")}">{r("continue")}</a></p>
</div>
<div class="auth-card auth-message" data-view="missing" hidden>
<h2>{r("missing_title")}</h2>
<p>{r("missing_text")}</p>
<p><a class="button wide" href="{url(lang, "/login/")}?mode=reset">{r("request")}</a></p>
</div>
</section>
<script type="application/json" id="login-text">{_ui_json(lang, "login.ui")}</script>
<script src="{asset("account.js")}" defer></script>
"""
    return page(lang, r("title"), body, unlisted="/reset-password/")


def account_page(lang="en"):
    """The signed-in account, laid out like Ochorus's settings: who you are,
    your data, and a danger zone (web/account.js). Signed out, it sends you
    to /login/. Not in the sitemap, and not indexed."""
    def a(key):
        return t(lang, "account." + key)

    body = f"""
<section class="account" id="account" aria-live="polite" hidden>
<header class="page-head">
<p class="eyebrow">{a("title")}</p>
<h1>{t(lang, "tools.your_account")}</h1>
<p class="dek">{a("dek")}</p>
</header>

<section class="set-block">
<h2>{a("title")}</h2>
<p class="signed-as">{a("signed_in_as")} <strong id="me-name"></strong></p>
<dl class="account-facts">
<div><dt>{a("fact_email")}</dt><dd id="me-email"></dd></div>
<div><dt>{a("fact_roles")}</dt><dd id="me-roles"></dd></div>
<div><dt>{a("fact_joined")}</dt><dd id="me-joined"></dd></div>
<div><dt>{a("fact_password")}</dt><dd><span id="me-password"></span> <a id="set-password" href="{url(lang, "/login/")}?mode=reset" hidden>{a("set_password")}</a></dd></div>
</dl>
<form class="account-form" id="name-form">
<label for="display-name">{a("display_name")} <span class="fine">{a("display_name_note")}</span></label>
<div class="field-row">
<input id="display-name" name="display_name" maxlength="80" autocomplete="name">
<button class="button ghost" type="submit">{a("save")}</button>
</div>
<p class="form-note" id="name-note" role="status"></p>
</form>
<p class="synced">{a("synced")} <a href="{url(lang, "/saved/")}">{a("synced_link")}</a></p>
<p><button class="button ghost" type="button" id="sign-out">{a("sign_out")}</button></p>
</section>
<section class="set-block" id="my-messages" hidden data-books="{html.escape(json.dumps({b: chapter_book(b, lang) for b in BOOK_CHAPTERS}, ensure_ascii=False))}">
<h2>{a("messages")}</h2>
<p>{a("messages_text")}</p>
<ul class="my-messages" id="messages-list"></ul>
</section>
<div class="soon">
<h2>{a("soon")}</h2>
<p>{a("soon_text")}</p>
</div>

<section class="set-block">
<h2>{a("data")}</h2>
<p>{a("data_text")}</p>
<p><button class="button ghost" type="button" id="download">{a("download")}</button></p>
</section>

<section class="set-block danger">
<h2>{a("danger")}</h2>
<div class="danger-row">
<div><h3>{a("clear_title")}</h3><p>{a("clear_text")}</p></div>
<button class="button ghost" type="button" id="clear-device">{a("clear")}</button>
</div>
<div class="danger-row">
<div><h3>{a("delete_title")}</h3><p>{a("delete_text")}</p></div>
<button class="button ghost" type="button" id="delete-account">{a("delete")}</button>
</div>
<p class="form-note" id="danger-note" role="status"></p>
</section>
</section>
<script type="application/json" id="account-text">{_ui_json(lang, "account.ui")}</script>
<script src="{asset("account.js")}" defer></script>
"""
    return page(lang, a("title"), body, unlisted="/account/")


def admin_page():
    """The admin (web/admin.js), after Ochorus's: one page whose sections
    (#coverage, #team, ...) the script draws from the API (backend/staff/),
    showing only the parts the signed-in account's roles open. In English
    only, as Ochorus's admin is. Not in the sitemap, and not indexed."""
    lang = "en"
    body = f"""
<div class="admin" id="admin" data-site="{html.escape(SITE_URL)}" data-github="{html.escape(GITHUB_URL)}">
<nav class="admin-rail" id="admin-rail" aria-label="Admin sections" hidden></nav>
<section class="admin-main" id="admin-main" aria-live="polite">
<header class="page-head compact">
<p class="eyebrow">Admin</p>
<h1>Open Word Bible admin</h1>
<p class="dek" id="admin-status">Loading&hellip;</p>
</header>
<noscript><p class="notice">The admin needs JavaScript.</p></noscript>
</section>
</div>
<script src="{asset("admin.js")}" defer></script>
"""
    head = f'\n<link rel="stylesheet" href="{asset("admin.css")}">'
    return page(lang, "Admin", body, unlisted="/admin/", translated=(lang,), head=head)


def not_found_page():
    """One 404 page serves every address, so it speaks each language."""
    lang = "en"
    others = "".join(
        f'<p class="hero-sub" lang="{code}">{t(code, "404.heading")} '
        f'<a href="{url(code, "/")}">{t(code, "404.home")}</a></p>'
        for code in LANGUAGES if code != lang)
    return page(lang, t(lang, "404.title"), f"""
<section class="hero lost">
<p class="eyebrow">404</p>
<h1>{t(lang, "404.heading")}</h1>
<p class="hero-sub">{t(lang, "404.sub")}</p>
<p class="actions"><a class="button" href="/read/">{icon(ICONS["book"])}{t(lang, "404.passages")}</a>
<a class="button ghost" href="/">{t(lang, "404.home")}</a></p>
{others}
</section>""")


def saved_page(lang="en"):
    """The reader's bookmarks, highlights and notes, from owb.marks in this browser
    (web/reader.js keeps them, web/site.js lists them here). The page
    carries the book names and canonical order in lang, and its labels."""
    order = [b for b, _ in books()]
    names = {b: chapter_book(b, lang) for b in order}
    data = {"order": order, "names": names,
            "chapters": {b: url(lang, chapter_url(b, 0)).replace("/0/", "/{c}/") for b in order},
            "remove": t(lang, "saved.remove"), "bookmark": t(lang, "saved.bookmark"),
            "note": t(lang, "saved.note"), "confirm": t(lang, "saved.confirm")}
    filters = "".join(f'<button type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">'
                      f'{t(lang, "saved." + k)}</button>' for k in ("all", "bookmarks", "highlights", "notes"))
    return page(lang, t(lang, "saved.title"), f"""
<header class="page-head">
<p class="eyebrow">{t(lang, "saved.title")}</p>
<h1>{t(lang, "saved.heading")}</h1>
<p class="dek">{t(lang, "saved.dek")}</p>
</header>
<section class="saved" id="saved" data-saved="{html.escape(json.dumps(data, ensure_ascii=False))}">
<div class="seg saved-filter" role="group" aria-label="{t(lang, "saved.show")}">{filters}</div>
<p class="saved-empty" hidden>{t(lang, "saved.empty")}</p>
<div class="saved-list"></div>
</section>""", unlisted="/saved/")


def offline_page(lang="en"):
    """What web/sw.js shows for a page not saved on the device, with the
    books that are (filled in by web/site.js)."""
    return page(lang, t(lang, "offline.title"), f"""
<section class="hero lost">
<p class="eyebrow">{t(lang, "offline.title")}</p>
<h1>{t(lang, "offline.heading")}</h1>
<p class="hero-sub">{t(lang, "offline.sub")}</p>
<p class="actions">{resume_link(lang)}<a class="button" href="{url(lang, "/")}" data-if-saved hidden>{t(lang, "404.home")}</a></p>
</section>
<section class="saved-books" id="saved-books" hidden aria-labelledby="saved-h">
<h2 id="saved-h">{t(lang, "offline.saved_books")}</h2>
<ul class="book-rows"></ul>
</section>""", unlisted="/offline/")


def manifest():
    return json.dumps({
        "name": SITE_NAME, "short_name": SITE_NAME, "start_url": "/", "scope": "/",
        "display": "standalone", "background_color": "#faf6ef", "theme_color": "#3f3d9a",
        # PNGs too (web/icons/, scripts/build_icons.py): phones install from those.
        "icons": [{"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
                  {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/icons/maskable-512.png", "sizes": "512x512", "type": "image/png",
                   "purpose": "maskable"}],
    }, indent=2) + "\n"


def service_worker():
    """web/sw.js with the files to keep from the start (the styles, the
    scripts and each language's offline page). Its version is a hash of the
    whole, so a deploy that changes any of them installs a new worker."""
    shell = [asset(n) for n in ("style.css", "site.js", "search.js", "markup.js", "reader.js", "plans.js")]
    shell += ["/favicon.svg", "/manifest.webmanifest"] + [url(lang, "/offline/") for lang in LANGUAGES]
    offline = {("" if lang == "en" else lang): url(lang, "/offline/") for lang in LANGUAGES}
    current = [asset(n) for n in ("style.css", "site.js", "search.js", "markup.js", "reader.js", "account.js", "plans.js",
                                  "compare.js", "word.js")]
    current += [word_uses()[1]] + [search_ui_url(lang) for lang in LANGUAGES]
    current += [plans_json_url(lang) for lang in LANGUAGES]
    current += [reader_shared(lang)[1] for lang in LANGUAGES]
    # The static search indexes the site no longer builds: copies kept
    # before are dropped.
    dropped = [f"/search-{lang}.json" for lang in LANGUAGES]
    text = ((ROOT / "web" / "sw.js").read_text(encoding="utf-8")
            .replace("__PRECACHE__", json.dumps(shell)).replace("__OFFLINE__", json.dumps(offline))
            .replace("__CURRENT__", json.dumps(current)).replace("__DROPPED__", json.dumps(dropped)))
    return text.replace("__VERSION__", hashlib.sha256(text.encode()).hexdigest()[:10])


FAVICON = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#3f3d9a"/>
<path d="{BOOK_PATH}" fill="#faf6ef"/>
{QUOTES.format(fill="#3f3d9a")}
</svg>
"""


# Search (web/search.js): the /search/ page, and the palette that Ctrl K or
# Cmd K opens on any page, as on Ochorus. The API answers each search
# (GET /api/search/, backend/translation/search.py) from the documents
# search_documents lists. An index holds what that language's pages show:
# each sentence in the language the reader shows it in, its notes, the
# articles and the passages. search.js gets the interface text and page
# shortcuts it needs from a small file per language (search_ui).
#
# Until the API had search, the build wrote each language's whole index
# (search-<lang>.json, 22 MB) and the browser searched it. It is no longer
# built; the service worker drops copies it kept.

# Book abbreviations a reader may type besides each book's names, its USFM
# code and its OSIS id ("Phil"); and prefixes of the names, from three
# letters, in canonical order (so "phil" is Philippians, not Philemon).
BOOK_ALIASES = {"JHN": ["jn"], "PHP": ["flp", "fil"], "1JN": ["1jn"], "2JN": ["2jn"], "3JN": ["3jn"]}
# The palette's page shortcuts, by catalog key.
SEARCH_PAGES = (("nav.home", "/"), ("nav.read", "/read/"), ("nav.plans", "/plans/"), ("nav.articles", "/articles/"),
                ("nav.about_project", "/about/"), ("nav.terms", "/terms/"), ("nav.credits", "/about/#credits"),
                ("nav.help", "/#help"), ("tools.sign_in", "/login/"))


def fold(text):
    """Text as search compares it: lower case, without accents, Vietnamese
    "đ" as "d". The rest is composed again, so a Korean syllable stays one
    character (NFD splits it into its letters)."""
    import unicodedata
    return unicodedata.normalize("NFC", "".join(
        c for c in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(c))).replace("\u0111", "d")


def book_aliases(code, names):
    out = {fold(n).replace(" ", "") for n in names}
    out |= {code.lower(), next(o for c, o, _ in refs.BOOKS if c == code).lower()}
    out |= set(BOOK_ALIASES.get(code, []))
    return sorted(out)


def article_text(body, lang="en"):
    """An article's words without markup, for the index: quoted sentences
    in full, other {{...}} tokens (Greek words) left out."""
    text = _OWB.sub(lambda m: html.unescape(_owb(m, lang)), body)
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[#*_`>|]", "", text)
    return smart_quotes(re.sub(r"\s+", " ", text).strip())


@functools.lru_cache(maxsize=None)
def search_documents(lang):
    """Everything search can find on pages in lang: interface text, the
    books, page shortcuts, and the documents. Kinds: "c" a passage, "v" a
    sentence (its text at each level, with the settings spans left in for
    the browser to render), "n" a note (a decision), "a" an article. The
    API (backend/translation/search.py) indexes these same documents, so
    the site and the API find the same things. Callers must not change
    the result: it is cached."""
    ui = dict(catalog(lang)["search.ui"])
    ui["levels"] = catalog(lang)["levels"]
    ui["category"] = catalog(lang)["reader.ui"]["category"]
    ui["read_url"] = url(lang, "/read/")
    content = {b for b, _ in books()}
    names = {code: BOOK_NAMES.get(code, {}).get(lang, name) for code, name in refs.BOOK_NAMES.items()}
    book_list = []
    for code in refs.BOOK_CODES:
        known = BOOK_NAMES.get(code, {})
        entry = {"code": code, "name": names[code],
                 "aliases": book_aliases(code, [refs.BOOK_NAMES[code], *known.values(),
                                                       *CHAPTER_NAMES.get(code, {}).values()])}
        if code in content:
            entry["chapters"] = {str(p.chapter): {"url": url(lang, p.url), "verses": sorted(
                {refs.parse(v).verse for r in p.records for v in r["refs"]})}
                for p in dict(books())[code]}
        book_list.append(entry)
    docs = []
    for p in passages():
        title = chapter_name(p.records, p.book, p.chapter, lang)
        docs.append({"k": "c", "bk": p.book, "c": p.chapter, "t": title, "u": url(lang, p.url), "s": html.unescape(languages_label(p.records)),
                     "h": " ".join([title, refs.BOOK_NAMES[p.book], *BOOK_NAMES[p.book].values()])})
        for r in p.records:
            # A sentence that runs into the next chapter (John 7:53-8:1) is
            # found once, in the chapter it starts in.
            if refs.parse(r["refs"][0]).chapter != p.chapter:
                continue
            shown = text_lang(r, lang)
            verse = refs.parse(r["refs"][0]).verse
            doc = {"k": "v", "bk": p.book, "c": p.chapter, "v": verse,
                   "vv": [refs.parse(v).verse for v in r["refs"]], "u": url(lang, p.url),
                   # Search shows and matches text on one line: no line markers.
                   "x": {level: markup.flat(text) for level, text in r["renderings"][shown].items()}}
            if shown != lang:
                doc["l"] = shown
            docs.append(doc)
            for d in r["decisions"]:
                if d["layer"] == "rendering" and d["language"] != shown:
                    continue
                docs.append({"k": "n", "bk": p.book, "c": p.chapter,
                             "v": verse, "u": url(lang, p.url), "y": d["layer"], "g": d["category"],
                             "t": d["choice"], "al": d["alternatives"], "s": d["reason"],
                             # Notes are written in English for now, whatever
                             # language a wording note is about.
                             "l": "en"})
    for a in sorted(load_articles(lang), key=lambda a: (a["section"] != "method", a["order"])):
        docs.append({"k": "a", "t": a["title"], "s": a["summary"], "x": article_text(a["body"], a["lang"]),
                     "u": url(lang, article_url(a)), "sec": catalog(lang)["sections"][a["section"]],
                     "l": a["lang"]})
    for d in docs:
        if d.get("l") == lang:
            del d["l"]
    return {"lang": lang, "ui": ui, "books": book_list, "docs": docs,
            "pages": [[html.unescape(t(lang, key)), url(lang, path)] for key, path in SEARCH_PAGES]}


@functools.lru_cache(maxsize=None)
def search_ui(lang):
    """What search.js needs besides the API's answers, as JSON text: the
    interface text, the palette's page shortcuts and the book names (a few
    kilobytes)."""
    data = search_documents(lang)
    return json.dumps({"lang": lang, "ui": data["ui"], "pages": data["pages"],
                       "names": {b["code"]: b["name"] for b in data["books"]}},
                      ensure_ascii=False, separators=(",", ":"))


@functools.lru_cache(maxsize=None)
def search_ui_url(lang):
    digest = hashlib.sha256(search_ui(lang).encode("utf-8")).hexdigest()[:10]
    return f"/search-ui-{lang}.json?v={digest}"


def search_source(lang):
    """Where search.js searches (<meta name="owb-search">): the API."""
    return f"{API_URL}/api/search/"


def palette(lang):
    """The search palette (web/search.js), on every page: a dialog with a
    box that searches as the reader types. Without the script the header's
    search button is a link to /search/."""
    ui = catalog(lang)["search.ui"]
    return f"""<div class="palette" id="palette" hidden>
<div class="palette-box" role="dialog" aria-modal="true" aria-label="{t(lang, "nav.search")}">
<form class="palette-form" action="{url(lang, "/search/")}" method="get" role="search">
{icon(ICONS["search"], 20)}
<input type="search" name="q" id="palette-q" autocomplete="off" spellcheck="false" placeholder="{html.escape(ui["palette_placeholder"])}" aria-label="{t(lang, "search.label")}" role="combobox" aria-expanded="true" aria-controls="palette-list" aria-autocomplete="list">
<kbd class="palette-esc">esc</kbd>
</form>
<ul class="palette-list" id="palette-list" role="listbox" aria-label="{t(lang, "nav.search")}" data-error="{html.escape(ui["error"])}" data-offline="{html.escape(ui["offline"])}"></ul>
<p class="palette-foot" aria-hidden="true"><span><kbd>&uarr;</kbd><kbd>&darr;</kbd> {html.escape(ui["navigate"])}</span><span><kbd>&crarr;</kbd> {html.escape(ui["open"])}</span><span><kbd>esc</kbd> {html.escape(ui["close"])}</span></p>
</div>
</div>"""


def search_page(lang="en"):
    """/search/: the box, then results as the reader types (web/search.js).
    The query lives in the address (?q=), so a search can be shared. Before
    a search the page offers recent searches, examples, and the passages."""
    examples = "".join(f'<li><a class="tag" href="{url(lang, "/search/")}?q={html.escape(q.replace(" ", "+"))}">'
                       f'{html.escape(q)}</a></li>' for q in catalog(lang)["search.examples"])
    browse = "".join(
        f'<div class="browse-book"><a class="browse-name" href="{url(lang, f"/read/#{book.lower()}")}">'
        f'{icon(ICONS["book"], 16)}{BOOK_NAMES[book][lang]}</a>'
        f'<span class="chap-pills">{chapter_pills(chaps, lang)}</span></div>'
        for book, chaps in books())
    ui = catalog(lang)["search.ui"]
    body = f"""
<header class="page-head search-head">
<p class="eyebrow">{t(lang, "search.title")}</p>
<h1>{t(lang, "search.heading")}</h1>
<p class="dek">{t(lang, "search.dek")}</p>
</header>
<div class="search-bar">
<form class="search-box" id="search-form" action="{url(lang, "/search/")}" method="get" role="search">
{icon(ICONS["search"], 20)}
<input type="search" name="q" id="search-q" autocomplete="off" spellcheck="false" placeholder="{t(lang, "search.placeholder")}" aria-label="{t(lang, "search.label")}" aria-describedby="search-status">
</form>
</div>
<p class="sr-only" id="search-status" aria-live="polite"></p>
<noscript><p class="notice">{t(lang, "search.noscript")}</p></noscript>
<div class="search-layout" id="search-results" hidden data-error="{html.escape(ui["error"])}" data-offline="{html.escape(ui["offline"])}" data-loading="{html.escape(ui["loading"])}" data-retry="{html.escape(ui["retry"])}" data-remove="{html.escape(ui["remove"])}"></div>
<div class="ways-in" id="search-start">
<section class="ways" id="search-recent" hidden aria-labelledby="recent-h">
<div class="ways-head"><h2 class="label" id="recent-h">{t(lang, "search.recent")}</h2><button type="button" class="link-btn" id="recent-clear">{t(lang, "search.clear")}</button></div>
<ul class="tags" id="recent-list"></ul>
</section>
<section class="ways" aria-labelledby="try-h">
<h2 class="label" id="try-h">{t(lang, "search.try")}</h2>
<ul class="tags">{examples}</ul>
</section>
<section class="ways" aria-labelledby="browse-h">
<h2 class="label" id="browse-h">{t(lang, "search.browse")}</h2>
{browse}
</section>
</div>
"""
    return page(lang, t(lang, "search.title"), body, path="/search/", current="/search/",
                description=t(lang, "meta.search_description"))


def sitemap(paths):
    urls = "".join(f"<url><loc>{html.escape(SITE_URL + p)}</loc></url>\n" for p in paths)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}</urlset>\n")


def build(out):
    for cached in (load_intro, book_languages, status_counts, _book_records, _chapter_words, chapter_verses, _all_records, nav_menus, footer_links, passages, asset, translated_verses, catalog, book_refs, name_cards, term_uses,
                   search_documents, word_uses, series_numbers, chapter_articles, load_plans, plans_json, plans_json_url,
                   downloads, chapter_shared, reader_shared):
        cached.cache_clear()
    if out.exists():
        shutil.rmtree(out)
    pages, indexed, feeds = {}, [], {}
    for lang in LANGUAGES:
        def add(path, text, index=True):
            pages[url(lang, path)] = text
            if index:
                indexed.append(url(lang, path))

        add("/", home_page(lang))
        add("/read/", read_page(lang))
        add("/about/", about_page(lang))
        add("/about/beliefs/", beliefs_page(lang))
        add("/about/status/", status_page(lang))
        add("/download/", download_page(lang))
        add("/about/privacy/", legal_page(lang, "privacy", "/about/privacy/"))
        add("/about/terms-of-use/", legal_page(lang, "terms_of_use", "/about/terms-of-use/"))
        add("/search/", search_page(lang))
        add("/compare/", compare_page(lang))
        add("/word/", word_page(lang))
        plans = available_plans(lang)
        add("/plans/", plans_page(lang, plans), index=bool(plans))
        add("/terms/", terms_page(lang))
        for term in validate.KEY_TERMS.values():
            add(term_path(term), term_page(term, lang))
            if term_split(term):
                for book in term_books(term):
                    add(term_path(term, book), term_book_page(term, book, lang))
        for book, chapter in chapters():
            add(chapter_url(book, chapter), chapter_page(book, chapter, lang))
        for book, _ in books(lang):
            if lang in book_languages(book):
                add(book_url(book), book_page(book, lang))
        articles = load_articles(lang)
        add("/articles/", articles_page(articles, lang), index=bool(articles))
        if articles:
            feeds[feed_url(lang).lstrip("/")] = articles_feed(articles, lang)
        feeds[votd_feed_url(lang).lstrip("/")] = votd_feed(lang)
        for article in articles:
            add(article_url(article), article_page(article, articles, lang))
        add("/account/", account_page(lang), index=False)
        add("/login/", login_page(lang), index=False)
        add("/reset-password/", reset_page(lang), index=False)
        add("/offline/", offline_page(lang), index=False)
        add("/saved/", saved_page(lang), index=False)
    # The admin is in English only (admin_page).
    pages["/admin/"] = admin_page()
    # A plan's page is in the languages that offer it.
    offered = {code: {p.id for p in available_plans(code)} for code in LANGUAGES}
    for plan in load_plans():
        langs = tuple(code for code in LANGUAGES if plan.id in offered[code])
        for code in langs:
            path = plan_url(plan)
            pages[url(code, path)] = plan_page(plan, code, langs)
            indexed.append(url(code, path))
    files = {(p.strip("/") + "/index.html").lstrip("/"): text for p, text in pages.items()}
    files.update(feeds)
    files["404.html"] = not_found_page()
    files["sitemap.xml"] = sitemap(indexed)
    files["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    files["llms.txt"] = llms_txt()
    files["favicon.svg"] = FAVICON
    files["manifest.webmanifest"] = manifest()
    files["sw.js"] = service_worker()
    files["word-uses.json"] = word_uses()[0]
    files.update(verse_files())
    files.update(editions_files())
    files.update(word_files())
    files.update(chapter_data_files())
    for lang in LANGUAGES:
        files[f"search-ui-{lang}.json"] = search_ui(lang)
        files[f"plans-{lang}.json"] = plans_json(lang)
    for rel, text in files.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    blobs = {f"{DOWNLOADS_DIR}/{name}": data for name, data, _ in downloads().values()}
    for rel, data in blobs.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    for name in ("style.css", "markup.js", "reader.js", "site.js", "account.js", "search.js", "plans.js", "compare.js",
                 "word.js", "admin.js", "admin.css"):
        shutil.copy(ROOT / "web" / name, out / name)
    shutil.copytree(ROOT / "web" / "fonts", out / "fonts")
    shutil.copytree(ROOT / "web" / "icons", out / "icons")
    shutil.copytree(OG, out / "og", ignore=shutil.ignore_patterns("*.digest"))
    return sorted(files) + sorted(blobs) + ["admin.css", "admin.js", "compare.js", "word.js", "markup.js", "plans.js", "reader.js",
                            "search.js", "site.js", "style.css"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--output", default=str(ROOT / "site"))
    args = ap.parse_args()
    for rel in build(Path(args.output)):
        print(f"built {rel}")


if __name__ == "__main__":
    main()
