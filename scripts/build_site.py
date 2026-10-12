"""Build the static site into site/ from content/, data/grc/, data/hbo/ and i18n/.

Usage: python3 scripts/build_site.py [-o DIR]

Needs only the repository: the Greek words come from the committed extracts
in data/grc/ (see scripts/extract_tokens.py), so a deploy never fetches the
full sources. Every page is built in each interface language: English at
the root, Spanish under /es/, French under /fr/, Swahili under /sw/.
"""
import argparse
import functools
import hashlib
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from typing import NamedTuple  # noqa: E402

from owb import markup, morph, refs  # noqa: E402

BOOK_NAMES = {"GEN": {"en": "Genesis", "es": "Génesis", "fr": "Genèse", "sw": "Mwanzo"},
              "MAT": {"en": "Matthew", "es": "Mateo", "fr": "Matthieu", "sw": "Mathayo"},
              "JHN": {"en": "John", "es": "Juan", "fr": "Jean", "sw": "Yohana"},
              "ROM": {"en": "Romans", "es": "Romanos", "fr": "Romains", "sw": "Warumi"},
              "1CO": {"en": "1 Corinthians", "es": "1 Corintios", "fr": "1 Corinthiens", "sw": "1 Wakorintho"},
              "2CO": {"en": "2 Corinthians", "es": "2 Corintios", "fr": "2 Corinthiens", "sw": "2 Wakorintho"},
              "GAL": {"en": "Galatians", "es": "Gálatas", "fr": "Galates", "sw": "Wagalatia"},
              "EPH": {"en": "Ephesians", "es": "Efesios", "fr": "Éphésiens", "sw": "Waefeso"},
              "PHP": {"en": "Philippians", "es": "Filipenses", "fr": "Philippiens", "sw": "Wafilipi"},
              "COL": {"en": "Colossians", "es": "Colosenses", "fr": "Colossiens", "sw": "Wakolosai"},
              "PHM": {"en": "Philemon", "es": "Filemón", "fr": "Philémon", "sw": "Filemoni"},
              "JAS": {"en": "James", "es": "Santiago", "fr": "Jacques", "sw": "Yakobo"},
              "1PE": {"en": "1 Peter", "es": "1 Pedro", "fr": "1 Pierre", "sw": "1 Petro"},
              "2PE": {"en": "2 Peter", "es": "2 Pedro", "fr": "2 Pierre", "sw": "2 Petro"},
              "1JN": {"en": "1 John", "es": "1 Juan", "fr": "1 Jean", "sw": "1 Yohana"},
              "2JN": {"en": "2 John", "es": "2 Juan", "fr": "2 Jean", "sw": "2 Yohana"},
              "3JN": {"en": "3 John", "es": "3 Juan", "fr": "3 Jean", "sw": "3 Yohana"},
              "PSA": {"en": "Psalms", "es": "Salmos", "fr": "Psaumes", "sw": "Zaburi"}}
# A book whose chapters go by another name: "Psalm 23", not "Psalms 23".
CHAPTER_NAMES = {"PSA": {"en": "Psalm", "es": "Salmo", "fr": "Psaume", "sw": "Zaburi"}}
# Chapters in each book, for "2 of 21 chapters" and a book's completeness.
BOOK_CHAPTERS = {"GEN": 50, "MAT": 28, "JHN": 21, "ROM": 16, "1CO": 16, "2CO": 13, "GAL": 6, "EPH": 6, "PHP": 4, "COL": 4, "PHM": 1, "JAS": 5, "1PE": 5, "2PE": 3, "1JN": 5, "2JN": 1, "3JN": 1, "PSA": 150}
# The interface languages, English first (see catalog below).
LANGUAGES = ("en", "es", "fr", "sw")
SITE_NAME = "Open Word Bible"
# The site's home (Render serves it on openwordbible.org and redirects www).
# Canonical links, the sitemap and link previews use it.
SITE_URL = "https://openwordbible.org"
GITHUB_URL = "https://github.com/jdegreef/open-word-bible"
# The Django API (backend/), for accounts. OWB_API_URL points a local build
# at a local API.
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
    "download": '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
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
# "auto" follows the device.
COLOUR_MODES = (("auto", "#faf6ef", "#16130f"),
                ("light", "#faf6ef", "#3f3d9a"),
                ("sepia", "#f4ecd8", "#3f3d9a"),
                ("dark", "#16130f", "#9c9af2"),
                ("night", "#000000", "#e0b45c"),
                ("contrast", "#ffffff", "#000000"))

# The reading text's settings in the gear menu (see web/style.css): name,
# default, and the values in the menu's order. A choice is kept as
# owb-<name> and applied as data-<name> on <html>. They change how the text
# looks, never its wording. Labels are in i18n/ (prefs.<name>, <name>.<value>).
READING_PREFS = (("size", "m", ("s", "m", "l", "xl")),
                 ("font", "serif", ("serif", "sans", "readable")),
                 ("leading", "normal", ("compact", "normal", "spacious")))

# Applies the saved colour mode and reading settings before the first paint,
# so a page never flashes the default colours or text. Mirrors web/site.js.
BOOT_SCRIPT = ("try{var d=document.documentElement,t=localStorage.getItem('owb-theme');"
               "if(['light','sepia','dark','night','contrast'].indexOf(t)>=0)"
               "d.setAttribute('data-theme',t);"
               "var p={" + ",".join(f"{name}:{[v for v in values if v != default]!r}"
                                   for name, default, values in READING_PREFS) + "};"
               "for(var k in p){var v=localStorage.getItem('owb-'+k);"
               "if(p[k].indexOf(v)>=0)d.setAttribute('data-'+k,v)}}catch(e){}")

# A reader who picked a language in the footer (web/site.js keeps it as
# owb-lang) is taken to this page in that language before the first paint,
# so a link shared in English still opens in Spanish for them. Only the
# languages the page is in are named: an article not yet translated into
# the reader's language stays in its own.
def lang_script(translated):
    return ("try{var l=localStorage.getItem('owb-lang'),h=document.documentElement.lang;"
            f"if(l&&l!==h&&{list(translated)!r}.indexOf(l)>=0){{"
            "var p=h==='en'?location.pathname:location.pathname.slice(h.length+1);"
            "location.replace((l==='en'?'':'/'+l)+p+location.search+location.hash)}}catch(e){}")

GEAR = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83'
        'l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4'
        'a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1'
        'H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06'
        'A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 '
        '1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4'
        'h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>')

def leading_sample(gap):
    """Three lines of text, gap apart, for a line-spacing tile."""
    ys = [13 - gap, 13, 13 + gap]
    lines = "".join(f'<line x1="2" x2="{24 if i < 2 else 16}" y1="{y}" y2="{y}"/>' for i, y in enumerate(ys))
    return ('<svg width="26" height="26" viewBox="0 0 26 26" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" aria-hidden="true">{lines}</svg>')


LEADING_GAPS = {"compact": 5, "normal": 7, "spacious": 9}


def colour_menu(lang):
    """The gear menu: the colour mode, then the reading text's settings
    (READING_PREFS). web/site.js runs it."""
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

    theme = group("theme", t(lang, "tools.theme"), "auto", [
        (v, f'<span class="swatch" style="--sw-bg:{bg};--sw-accent:{accent}" aria-hidden="true"></span>',
         t(lang, "theme." + v)) for v, bg, accent in COLOUR_MODES])
    def sample(pref, value):
        inner = leading_sample(LEADING_GAPS[value]) if pref == "leading" else "Aa"
        return f'<span class="sample" aria-hidden="true">{inner}</span>'

    rows = [group(pref, t(lang, "prefs." + pref), default,
                  [(v, sample(pref, v), t(lang, f"{pref}.{v}")) for v in values])
            for pref, default, values in READING_PREFS]
    return (
        '<div class="prefs">'
        '<button type="button" class="tool-btn prefs-btn" aria-expanded="false" aria-controls="colour-menu" '
        f'aria-label="{label}" title="{label}">{GEAR}</button>'
        f'<div id="colour-menu" class="prefs-menu" role="group" aria-label="{label}" hidden>'
        + theme + "".join(rows) + '</div></div>')


OG = ROOT / "web" / "og"


def og_card_chapter(book, chapter):
    """The name of a passage's link-preview image in web/og/ (scripts/build_og.py)."""
    return f"{book.lower()}-{chapter}"


def og_card_article(article):
    return f"article-{article['slug']}"


def page(lang, title, body, path=None, current="", description="", card="site", card_alt=None,
         translated=LANGUAGES, unlisted=None):
    """A full HTML page in lang. path is the page's URL path without the
    language ("/read/"); pages with one get a canonical link, hreflang links
    to the page in each language in translated (the languages it exists in),
    and link-preview tags, and go in the sitemap. card names the
    page's preview image in web/og/; a card not drawn yet falls back to the
    site's. card_alt says what the card shows. An unlisted page (the account
    page) has no path: it is not indexed and has no preview, but unlisted
    names its path, so the language switch still leads to it."""
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
    boot = BOOT_SCRIPT + (lang_script(translated) if here is not None else "")
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">{meta}
<meta name="owb-api" content="{API_URL}">
<meta name="owb-search" content="{search_index_url(lang)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="/manifest.webmanifest">
<script>{boot}</script>
<link rel="preload" href="/fonts/hanken-grotesk-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/gentium-book-plus-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset("style.css")}">
<script src="{asset("site.js")}" defer></script>
<script src="{asset("search.js")}" defer></script>
</head>
<body>
<a class="skip" href="#main">{t(lang, "skip")}</a>
{site_header(lang, current, path)}
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
    return " &middot; ".join(t(code, "language_name") for code in LANGUAGES
                             if all(code in r["renderings"] for r in records))


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

    rows = []
    for book, chaps in books(lang):
        name = BOOK_NAMES[book][lang]
        progress = book_progress(book, chaps, lang)[2]
        rows.append(f'<div class="dd-book">{row(url(lang, f"/read/#{book.lower()}"), name, progress, "book")}'
                    f'<div class="dd-chaps" aria-label="{t(lang, "nav.book_chapters", book=name)}">'
                    f'{chapter_pills(chaps, lang)}</div></div>')
    read = (f'<p class="dd-head">{t(lang, "nav.books_so_far")}</p>{"".join(rows)}'
            f'{all_link(url(lang, "/read/"), t(lang, "nav.all_books"))}')

    articles = sorted(load_articles(lang), key=lambda a: a["order"])
    groups = "".join(
        f'<div class="dd-col"><p class="dd-head">{catalog(lang)["sections"][key]}</p>'
        + "".join(row(url(lang, article_url(a)), display(a["title"]), t(lang, "article.min_read", n=a["minutes"]))
                  for a in articles if a["section"] == key)
        + "</div>"
        for key in SECTIONS if any(a["section"] == key for a in articles))
    arts = f'<div class="dd-cols">{groups}</div>{all_link(url(lang, "/articles/"), t(lang, "nav.all_articles"))}'

    about = ("".join((
        row(url(lang, "/about/"), t(lang, "nav.about_project"), t(lang, "nav.about_project_note"), "info"),
        row(url(lang, "/about/#credits"), t(lang, "nav.credits"), t(lang, "nav.credits_note"), "scale"),
        row(url(lang, "/#help"), t(lang, "nav.help"), t(lang, "nav.help_note"), "users"),
        row(GITHUB_URL, t(lang, "nav.source"), t(lang, "nav.source_note"), "code", ext=True),
    )))
    # A language with no articles of its own yet has no articles menu.
    return (("read", t(lang, "nav.read"), "book", "/read/", read, "dd-read"),
            *((("articles", t(lang, "nav.articles"), "articles", "/articles/", arts, "dd-wide"),) if articles else ()),
            ("about", t(lang, "nav.about"), "info", "/about/", about, "dd-about"))


def site_header(lang, current, path=None):
    """Logo, the main links with their dropdowns, and the tools. On narrow
    screens the links fold into a panel behind the menu button, where each
    dropdown opens in place (web/site.js). The section trigger for current
    is lit, and the dropdown link to this page (path) is aria-current."""
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
            panel = re.sub(rf'(class="chap(?: part)?" href="{re.escape(here)}")', r'\1 aria-current="page"', panel)
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
<a class="tool-btn account-btn" href="{url(lang, "/account/")}" aria-label="{t(lang, "tools.sign_in")}" title="{t(lang, "tools.sign_in")}" data-signed-in="{t(lang, "tools.your_account")}">{icon(ICONS["user"])}<span class="account-initial" hidden></span></a>
<a class="tool-btn" href="{GITHUB_URL}" aria-label="{t(lang, "tools.github")}" title="GitHub">{icon(ICONS["github"])}</a>
{colour_menu(lang)}
<button type="button" class="tool-btn menu-btn" aria-expanded="false" aria-controls="site-nav" aria-label="{t(lang, "nav.menu")}">{icon(ICONS["menu"], 22)}{icon(ICONS["close"], 22)}</button>
</div>
</div></header>"""


@functools.lru_cache(maxsize=None)
def footer_links(lang):
    """The footer's link columns in lang. Built once per build and language."""
    def items(pairs):
        return "".join(f'<li><a href="{href}"{f" lang={tl}" if tl and tl != lang else ""}>{label}</a></li>'
                       for href, label, tl in pairs)

    read = [(url(lang, f"/read/#{book.lower()}"), BOOK_NAMES[book][lang], None) for book, _ in books(lang)]
    read.append((url(lang, "/read/"), t(lang, "nav.all_books"), None))
    start = sorted((a for a in load_articles(lang) if a["section"] == "method"), key=lambda a: a["order"])[:3]
    learn = [(url(lang, article_url(a)), display(a["title"]), None) for a in start]
    learn.append((url(lang, "/articles/"), t(lang, "nav.all_articles"), None))
    project = [(url(lang, "/about/"), t(lang, "footer.about"), None),
               (url(lang, "/about/#credits"), t(lang, "nav.credits"), None),
               (url(lang, "/#help"), t(lang, "nav.help"), None),
               (GITHUB_URL, t(lang, "nav.source"), None),
               (GITHUB_URL + "/issues/new", t(lang, "footer.report"), None)]
    learn = (f'<nav aria-labelledby="foot-learn"><h2 id="foot-learn">{t(lang, "footer.learn")}</h2><ul>{items(learn)}</ul></nav>\n'
             if start else "")
    return (f'<nav aria-labelledby="foot-read"><h2 id="foot-read">{t(lang, "footer.read")}</h2><ul>{items(read)}</ul></nav>\n'
            f'{learn}'
            f'<nav aria-labelledby="foot-project"><h2 id="foot-project">{t(lang, "footer.project")}</h2><ul>{items(project)}</ul></nav>')


def language_links(lang, path, translated=LANGUAGES):
    """The footer's language switch, as Ochorus has it: each language in its
    own name, the current one as plain text and the others as links to this
    page in that language: the home page from a page without a path, and
    the articles page from an article not in that language. web/site.js
    remembers the choice."""
    def target(code):
        if path is None:
            return "/"
        return path if code in translated else "/articles/"

    links = "".join(
        f'<li><span lang="{code}" aria-current="true">{t(code, "language_name")}</span></li>' if code == lang
        else f'<li><a href="{url(code, target(code))}" lang="{code}" hreflang="{code}" data-lang="{code}">'
             f'{t(code, "language_name")}</a></li>'
        for code in LANGUAGES)
    return (f'<nav class="foot-langs" aria-labelledby="foot-langs">'
            f'<h2 id="foot-langs">{t(lang, "footer.languages")}</h2><ul>{links}</ul></nav>')


def site_footer(lang, path=None, translated=LANGUAGES):
    """The footer on every page: the passages, the first articles to read,
    the project's links, and the language switch."""
    home = url(lang, "/")
    return f"""<footer class="site"><div class="wrap">
<div class="foot-grid">
<div class="foot-about">
<a class="brand" href="{home}">{MARK}<span class="brand-name">Open Word <em>Bible</em></span></a>
<p>{t(lang, "footer.tagline")}</p>
<p class="foot-licence"><span class="pill">CC0</span> {t(lang, "footer.licence")}</p>
</div>
{footer_links(lang)}
</div>
{language_links(lang, path, translated)}
<div class="foot-base">
<p>{t(lang, "footer.review")}</p>
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


def load_chapter(book, chapter):
    """A chapter's records, and the Greek words of every verse they cover. A
    sentence that runs into the next chapter (John 7:53-8:1) belongs to both:
    without it the next chapter would lose a verse, and John 8 would open
    without the bracket and the note that begin the disputed passage."""
    records = []
    for path in sorted((ROOT / "content" / book).glob("*.json")):
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
            if any(refs.parse(v).chapter == chapter for v in r["refs"]):
                records.append(curl_record(r))
    records.sort(key=lambda r: refs.parse(r["refs"][0]).sort_key() + (r["id"],))
    words = {}
    for ch in sorted({chapter} | {refs.parse(v).chapter for r in records for v in r["refs"]}):
        words.update(json.loads(words_path(book, ch).read_text(encoding="utf-8"))["verses"])
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
    """Section headings by the record they stand above (data/headings.json),
    each in the languages it has, with curly quotes."""
    data = json.loads((ROOT / "data" / "headings.json").read_text(encoding="utf-8"))
    return {rid: {lang: smart_quotes(text) for lang, text in h.items()}
            for rid, h in data["headings"].items()}


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
        records, words = load_chapter(b, c)
        verses = len(own_verses(records, c))
        total = sum(refs.parse(v).chapter == c for v in words)
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
    """"4 of 4 chapters, complete" / "2 of 21 chapters": a book's progress."""
    done = sum(p.complete for p in chapters_)
    total = BOOK_CHAPTERS[book]
    return done, total, t(lang, "progress.complete" if done == total else "progress.chapters",
                          done=done, total=total)


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
    total = len(json.loads(words_path(book, chapter).read_text(encoding="utf-8"))["verses"])
    verses = own_verses(records, chapter)
    return f"{chapter_book(book, lang)} {chapter}" if len(verses) == total else chapter_title(records, book, chapter, lang)


def text_lang(record, lang):
    """The language a record is shown in on a page in lang: lang if the
    record has it yet, otherwise English, which runs ahead of the others."""
    return lang if lang in record["renderings"] else "en"


def lang_attr(text_language, lang):
    """A lang attribute for text that is not in the page's language."""
    return f' lang="{text_language}"' if text_language != lang else ""


# Reader settings whose control only some languages have.
PLURAL_YOU = {"es"}


def chapter_page(book, chapter, lang="en"):
    records, words = load_chapter(book, chapter)
    title = chapter_name(records, book, chapter, lang)
    # Every language any sentence has: English may run ahead of the others,
    # and the reader shows a sentence not yet translated in English.
    languages = [code for code in LANGUAGES
                 if any(code in r["renderings"] for r in records)]
    source = source_language(book)
    data = {"book": book, "chapter": chapter, "title": title, "lang": lang, "languages": languages,
            "source": source, "ui": catalog(lang)["reader.ui"], "records": records,
            "words": {vid: words[vid] for r in records for vid in r["refs"]},
            "paragraphs": paragraph_starts(records, words),
            "headings": {r["id"]: headings()[r["id"]] for r in records if r["id"] in headings()}}
    # Each morphology code's description in every language, once per page.
    data["uses"] = word_uses()[1]
    # Names before a chapter number ("Psalm 23:1"), for "Book 1:2" links.
    data["books"] = {b: chapter_book(b, lang) for b, _ in books()}
    data["grammar"] = {grammar_key(w): {l: describe(w, l) for l in LANGUAGES}
                       for ws in data["words"].values() for w in ws}
    # "</" cannot appear inside a script element.
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

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
    plural = ("\n  " + control("plural", "plural_you", [("0", "ustedes"), ("1", "vosotros")])
              if lang in PLURAL_YOU else "")
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
  {control("gender", "gender", [("0", t(lang, "reader.inclusive")), ("1", t(lang, "reader.traditional"))])}
  {title_control}
  {control("pronouns", "deity_pronoun", [("0", t(lang, "reader.he")), ("1", t(lang, "reader.He"))])}{units}{plural}
  {control("headings", "headings", [("0", t(lang, "reader.show")), ("1", t(lang, "reader.hide"))])}
  {control("view", "view", [("0", t(lang, "reader.study")), ("1", t(lang, "reader.reading"))], " view-control")}
</div>
<p class="hint"><span id="hint-level"></span> <span id="hint-gender"></span> <span id="hint-{title_setting}"></span> <span id="hint-deity_pronoun"></span> <span id="hint-units"></span> <span id="hint-plural_you"></span> <span id="hint-headings"></span> <span id="hint-view"></span></p>
</div>
<div class="reader">
  <article class="passage">
    {chapter_strip(book, chapter, lang)}
    <h1 id="title">{html.escape(title)}</h1>
    <p class="sub">{t(lang, "reader.sub" + suffix)}</p>
    <p class="notice" id="partial" hidden></p>
    <div class="text" id="text"></div>
    <section class="notes" id="notes" aria-label="{t(lang, "reader.notes")}" hidden></section>
    {chapter_turns(book, chapter, lang)}
  </article>
  <aside class="panel" id="panel" aria-live="polite" tabindex="-1"></aside>
</div>
{edge_turns(book, chapter, lang)}
<script type="application/json" id="owb-data">{blob}</script>
<script src="{asset("reader.js")}"></script>
"""
    return page(lang, title, body, path=chapter_url(book, chapter), current="/read/",
                card=og_card_chapter(book, chapter),
                card_alt=t(lang, "meta.chapter_card_alt" + suffix, title=title,
                           verse=opening_verse(records, chapter, lang)),
                description=t(lang, "meta.chapter_description" + suffix, title=title))


def reader_passages(book, chapter, lang="en"):
    """The passages a reader page in lang links to: those with sentences in
    lang, or every passage on a page not yet in lang, which is shown in
    English."""
    ps = passages_in(lang)
    if any((p.book, p.chapter) == (book, chapter) for p in ps):
        return ps
    return list(passages())


def chapter_strip(book, chapter, lang="en"):
    """Above a passage: its book, how far the book has got, and a pill for
    each chapter translated so far, this one marked."""
    chaps = [p for p in reader_passages(book, chapter, lang) if p.book == book]
    name = BOOK_NAMES[book][lang]
    progress = book_progress(book, chaps, lang)[2]
    return (f'<nav class="chapstrip" aria-label="{t(lang, "reader.strip", book=name)}">'
            f'<a class="chap-book" href="{url(lang, f"/read/#{book.lower()}")}">{icon(ICONS["book"], 16)}{name}</a>'
            f'<span class="chap-pills">{chapter_pills(chaps, lang, chapter, BOOK_CHAPTERS[book])}</span>'
            f'<button type="button" class="chap-goto" data-open-search aria-keyshortcuts="/">'
            f'{icon(ICONS["search"], 15)}{t(lang, "reader.goto")}</button>'
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


# Verses that are only a psalm's title ("A psalm of David ..."), which the
# Hebrew text counts as verse 1. A chapter's cards quote the psalm itself.
TITLES = {"PSA.3.1", "PSA.4.1", "PSA.5.1", "PSA.6.1"}


def opening(records, chapter):
    """(record, verse id) for the verse a chapter's cards quote: its first
    verse outside a disputed passage and not a psalm's title, or its first
    verse if every one is skipped."""
    first = None
    for r in records:
        for vid in r["refs"]:
            if refs.parse(vid).chapter == chapter:
                if not disputed(vid) and vid not in TITLES:
                    return r, vid
                first = first or (r, vid)
    return first


def opening_verse(records, chapter, lang="en"):
    """A passage's opening verse (see opening), Balanced, at the default
    settings: what its Read-page card and its share card quote. In English
    when that sentence is not yet in lang."""
    r, vid = opening(records, chapter)
    # split keeps each marker's verse number: [text, "13", text, "14", text].
    parts = markup.VERSE.split(r["renderings"][text_lang(r, lang)]["B"])
    numbers = [str(refs.parse(r["refs"][0]).verse)] + parts[1::2]
    return plain(parts[2 * numbers.index(str(refs.parse(vid).verse))].strip())


# A quoted verse in each language's quotation marks (English curly quotes
# otherwise). French sets its guillemets off with no-break spaces.
QUOTES_AROUND = {"es": "&laquo;{}&raquo;", "fr": "&laquo;&nbsp;{}&nbsp;&raquo;"}


def passage_card(book, chapter, lang="en"):
    """A passage as a card in the article-card style: its opening verse at
    the default settings, and how much of it is translated into lang and
    recorded (its meaning decisions and its rendering decisions for lang)."""
    every = load_chapter(book, chapter)[0]
    records = [r for r in every if lang in r["renderings"]] or every
    verses = own_verses(records, chapter)
    shown = [d for r in records for d in r["decisions"] if d["language"] in (None, lang)]
    r0 = opening(records, chapter)[0]
    quote = opening_verse(records, chapter, lang)
    meta = t(lang, "card.meta", verses=len(verses), sentences=len(records),
             decisions=len(shown), uncertain=sum(d["uncertain"] for d in shown))
    if len(records) < len(every):
        meta += " &middot; " + t(lang, "card.coverage", n=len(records), total=len(every))
    q = QUOTES_AROUND.get(lang, "&ldquo;{}&rdquo;")
    if lang not in QUOTES_AROUND:   # inside double quotes, speech takes single ones
        quote = quote.replace("\u201c", "\u2018").replace("\u201d", "\u2019")
    return (f'<li><a class="a-card p-card" href="{url(lang, chapter_url(book, chapter))}">'
            f'<span class="a-section">{BOOK_NAMES[book][lang]} &middot; {languages_label(every)}</span>'
            f'<span class="a-title">{display(chapter_name(records, book, chapter, lang))}</span>'
            f'<span class="p-opening"{lang_attr(text_lang(r0, lang), lang)}>{q.format(display(quote))}</span>'
            f'<span class="a-meta">{meta}</span></a></li>')


def resume_link(lang):
    """A link back to the verse the reader was last at, hidden until
    web/site.js finds one saved by web/reader.js (owb.place). It carries the
    book names in lang, so the link names the passage in the page's language."""
    names = json.dumps({b: BOOK_NAMES[b][lang] for b, _ in books()}, ensure_ascii=False)
    return (f'<a class="button" data-resume hidden data-label="{html.escape(t(lang, "resume.link"))}" '
            f'data-prefix="{url(lang, "")}" data-books="{html.escape(names)}" href="{url(lang, "/read/")}">'
            f'{icon(ICONS["book"])}<span></span></a>')


def save_button(book, chaps, lang):
    """A book's "Save for offline" button on the Read page: web/site.js
    stores the pages it names in the owb-books cache, which web/sw.js reads
    when there is no connection. Hidden where the browser cannot."""
    pages = json.dumps([url(lang, chapter_url(p.book, p.chapter)) for p in chaps])
    labels = "".join(f' data-{k}="{html.escape(t(lang, "offline." + k))}"'
                     for k in ("save", "saving", "saved", "failed"))
    return (f'<button type="button" class="save-book" hidden data-book="{book}" '
            f'data-name="{html.escape(BOOK_NAMES[book][lang])}" data-pages="{html.escape(pages)}"{labels}>'
            f'{icon(ICONS["download"], 16)}<span>{t(lang, "offline.save")}</span></button>')


def offline_files(lang):
    """What a saved book needs besides its pages and what web/sw.js keeps
    anyway: the reader, the word index, the search index and the fonts."""
    fonts = sorted(f"/fonts/{f.name}" for f in (ROOT / "web" / "fonts").glob("*.woff2"))
    return [url(lang, "/read/"), asset("reader.js"), word_uses()[1], search_index_url(lang)] + fonts


def read_page(lang="en"):
    groups = []
    for book, chaps in books(lang):
        done, total, progress = book_progress(book, chaps, lang)
        groups.append(
            f'<section class="book-group" id="{book.lower()}" aria-labelledby="book-{book.lower()}">'
            f'<div class="book-head"><h2 id="book-{book.lower()}">{BOOK_NAMES[book][lang]}</h2>'
            f'<span class="book-progress{" done" if done == total else ""}">{progress}</span>'
            f'{meter(done, total)}{save_button(book, chaps, lang)}</div>'
            f'<ul class="a-grid">{"".join(passage_card(p.book, p.chapter, lang) for p in chaps)}</ul></section>')
    cards = "".join(groups)
    body = f"""
<header class="page-head" data-offline-files="{html.escape(json.dumps(offline_files(lang)))}">
<p class="eyebrow">{t(lang, "read.title")}</p>
<h1>{t(lang, "read.heading")}</h1>
<p class="dek">{t(lang, "read.dek")}</p>
<p class="actions">{resume_link(lang)}</p>
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


def all_records():
    """Every record in content/, in canonical order, once each (a sentence
    across a chapter break is on both chapters' pages)."""
    seen = {}
    for b, c in chapters():
        for r in load_chapter(b, c)[0]:
            seen.setdefault(r["id"], r)
    return list(seen.values())


def plain(text):
    """Rendering text as a reader sees it with the default settings."""
    return markup.VERSE.sub("", markup.render(text)).strip()


# The worked example on the home page: a record and one of its decisions.
EXAMPLE = ("JHN", 1, "JHN.1.1.s1", "m4")


def sec_head(hid, ico, title, href=None, more=None):
    """A home-page section heading: icon and title, with an "all" link on
    the right (the Ochorus shelf heading)."""
    link = f'<a class="sec-more" href="{href}">{more} {icon(ICONS["arrow"], 16)}</a>' if href else ""
    return (f'<div class="sec-head"><h2 id="{hid}"><span class="sec-ico">{icon(ICONS[ico])}</span>'
            f'{title}</h2>{link}</div>')


def example_html(lang="en"):
    """John 1:1 at every level, with one decision and its Greek words marked.
    Everything comes from content/ and data/grc/, so it stays in step with
    the translation. Decision notes are in English for now."""
    book, chapter, record_id, decision_id = EXAMPLE
    records, words = load_chapter(book, chapter)
    record = next(r for r in records if r["id"] == record_id)
    decision = next(d for d in record["decisions"] if d["id"] == decision_id)
    marked = set(decision["tokens"])
    greek = " ".join(
        (f'<mark>{html.escape(w["text"])}</mark>' if w["id"] in marked else html.escape(w["text"]))
        + html.escape(w["after"].rstrip())
        for vid in record["refs"] for w in words[vid] if w["id"] in record["source"]["tokens"])
    shown = text_lang(record, lang)
    levels = "".join(
        f'<div class="lvl"><span class="tag">{name}</span>'
        f'<p{lang_attr(shown, lang)}>{html.escape(plain(record["renderings"][shown][code]))}</p></div>'
        for code, name in catalog(lang)["levels"].items())
    ref = refs.parse(record["refs"][0])
    also = "; ".join(html.escape(a) for a in decision["alternatives"])
    open_url = url(lang, chapter_url(book, chapter))
    passage = f"{chapter_book(book, lang)} {chapter}"
    en = lang_attr("en", lang)
    note = f'<p class="alts">{t(lang, "notes_in_english")}</p>' if lang != "en" else ""
    return f"""
<section class="example" aria-labelledby="example-h">
{sec_head("example-h", "book", t(lang, "home.example", ref=f"{chapter_book(book, lang)} {ref.chapter}:{ref.verse}"), open_url, t(lang, "home.example_open", passage=passage))}
<div class="example-grid">
<div>
<p class="label">{t(lang, "home.example_greek")}</p>
<p class="greek" lang="grc">{greek}</p>
<p class="label">{t(lang, "home.example_gloss")}</p>
<p class="gloss"{en}>{html.escape(plain(record["literal_gloss"]))}</p>
<p class="label">{t(lang, "home.example_levels")}</p>
{levels}
</div>
<div class="card decision">
<p class="label">{t(lang, "home.example_decision")}</p>
<p class="choice"{en}>&ldquo;{html.escape(plain(decision["choice"]))}&rdquo;</p>
<p class="alts">{t(lang, "home.example_also", alts=f"<span{en}>{also}</span>")}</p>
<p class="why"{en}>{html.escape(decision["reason"])}</p>
{note}
</div>
</div>
<p class="example-foot">{t(lang, "home.example_foot")} <a href="{open_url}">{t(lang, "home.example_foot_link", passage=passage)}</a></p>
</section>
"""


def progress_html(lang="en"):
    """The home page's progress: sentences, decisions, books and chapters
    in the page's language only. A sentence's decisions in lang are its
    meaning decisions and its rendering decisions for lang."""
    records = [r for r in all_records() if lang in r["renderings"]]
    decisions = sum(d["language"] in (None, lang) for r in records for d in r["decisions"])
    rows = []
    for book, chaps in books(lang):
        done, total, progress = book_progress(book, chaps, lang)
        rows.append(f'<li class="book-row"><a class="book-name" href="{url(lang, f"/read/#{book.lower()}")}">'
                    f'{BOOK_NAMES[book][lang]}</a>{meter(done, total)}'
                    f'<span class="book-progress{" done" if done == total else ""}">{progress}</span>'
                    f'<span class="chap-pills">{chapter_pills(chaps, lang)}</span></li>')
    return f"""
<section class="progress" aria-labelledby="progress-h">
{sec_head("progress-h", "check", t(lang, "home.progress"), url(lang, "/read/"), t(lang, "home.all_books"))}
<div class="stats">
<div><b>{len(records)}</b><span>{t(lang, "home.stat_sentences")}</span></div>
<div><b>{decisions}</b><span>{t(lang, "home.stat_decisions")}</span></div>
<div><b>{len(LANGUAGES)}</b><span>{t(lang, "home.stat_languages")}</span></div>
</div>
<p>{t(lang, "home.progress_text")}</p>
<p class="label">{t(lang, "nav.books_so_far")}</p>
<ul class="book-rows">{"".join(rows)}</ul>
</section>
"""


def home_page(lang="en"):
    def point(ico, n):
        return (f'<li class="point"><span class="tile">{icon(ICONS[ico], 22)}</span>'
                f'<h3>{t(lang, f"home.point{n}")}</h3><p>{t(lang, f"home.point{n}_text")}</p></li>')

    def helper(ico, n):
        return (f'<li><span class="tile sm">{icon(ICONS[ico])}</span>'
                f'<p><strong>{t(lang, f"home.helper{n}")}</strong> {t(lang, f"home.helper{n}_text")}</p></li>')

    first = sorted(load_articles(lang), key=lambda a: a["order"])[:3]
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
<p class="actions">{resume_link(lang)}<a class="button" href="{url(lang, "/read/")}">{icon(ICONS["book"])}{t(lang, "home.start")}</a>
<a class="button ghost" href="#example-h">{t(lang, "home.how")}</a></p>
<ul class="trust">
<li>{icon(ICONS["gift"], 16)}{t(lang, "home.trust_free")}</li>
<li>{icon(ICONS["scale"], 16)}{t(lang, "home.trust_cc0")}</li>
<li>{icon(ICONS["languages"], 16)}{t(lang, "home.trust_languages")}</li>
</ul>
</section>
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
{progress_html(lang)}
{latest}<section class="involve" id="help" aria-labelledby="involve-h">
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
"""
    return page(lang, SITE_NAME, body, path="/", current="/")


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
"""
    return page(lang, t(lang, "about.title"), body, path="/about/", current="/about/",
                description=t(lang, "meta.about_description"))


ARTICLES = ROOT / "articles"
_GREEK = re.compile(r"\{\{GREEK:([A-Z0-9]+)\.(\d+)\.(\d+):(\d+)(?:-(\d+))?\}\}")
_LEMMA = re.compile(r"\{\{LEMMA:([A-Z0-9]+)\.(\d+)\.(\d+):(\d+)\}\}")
_OWB = re.compile(r"\{\{OWB:([A-Z0-9.]+\.s\d+):([LBR])\}\}")


def _verse_words(book, chapter, verse):
    """The MACULA words of one verse, from the committed extract."""
    path = ROOT / "data" / "grc" / f"{book}.{chapter}.json"
    verses = json.loads(path.read_text(encoding="utf-8"))["verses"]
    vid = f"{book}.{chapter}.{verse}"
    if vid not in verses:
        raise SystemExit(f"{vid} is not in {path.name}; add it with scripts/extract_tokens.py")
    return verses[vid]


def _greek(m):
    """{{GREEK:JHN.1.1:14-17}}: words 14 to 17 of John 1:1 as the data has them."""
    book, chapter, verse, a, b = m[1], int(m[2]), int(m[3]), int(m[4]), int(m[5] or m[4])
    words = [w for w in _verse_words(book, chapter, verse) if a <= w["position"] <= b]
    text = " ".join(w["text"] + (w["after"].rstrip() if w["position"] < b else "") for w in words)
    return f'<span class="greek" lang="grc">{html.escape(text)}</span>'


def _lemma(m):
    """{{LEMMA:JHN.1.14:17}}: the dictionary form of word 17 of John 1:14."""
    word = next(w for w in _verse_words(m[1], int(m[2]), int(m[3])) if w["position"] == int(m[4]))
    return f'<span class="greek" lang="grc">{html.escape(word["lemma"])}</span>'


def _owb(m, lang="en"):
    """{{OWB:JHN.1.1.s1:B}}: our translation of a sentence in lang (English
    if it is not in lang yet), with default settings."""
    record_id, level = m[1], m[2]
    ref = refs.parse(record_id.rsplit(".s", 1)[0])
    record = next((r for r in load_chapter(ref.book, ref.chapter)[0] if r["id"] == record_id), None)
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
    """A blockquote that is just one {{GREEK:..}} or {{OWB:..}} placeholder
    becomes a figure captioned with its source, linked to the reader. The
    caption is in the article's language; the link goes to the reader in
    the page's."""
    m = _GREEK.fullmatch(body)
    if m:
        book, chapter, verse = m[1], int(m[2]), int(m[3])
        source = t(text_language, "article.greek_source")
        kind = "greek-quote"
    else:
        m = _OWB.fullmatch(body)
        if not m:
            return f"<blockquote><p>{inner}</p></blockquote>"
        ref = refs.parse(m[1].rsplit(".s", 1)[0])
        book, chapter, verse = ref.book, ref.chapter, ref.verse
        source = t(text_language, "article.owb_source", level=catalog(text_language)["levels"][m[2]])
        kind = "owb-quote"
    link = verse_link(book, chapter, verse, lang)
    more = f' <a href="{link}">{t(text_language, "article.read_with_reasoning")}</a>' if link else ""
    return (f'<figure class="quote {kind}"><blockquote><p>{inner}</p></blockquote>'
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
    Greek words ({{GREEK:..}}, {{LEMMA:..}}) and our own translation
    ({{OWB:..}}) from the data, so none of it is typed by hand. The text is
    in text_language, on a page in lang: links to the site go to its pages
    in lang."""
    fills = []

    def hold(html_text):
        fills.append(html_text)
        return f"\x00{len(fills) - 1}\x00"

    def href(target):
        return url(lang, target) if target.startswith("/") else target

    def inline(s):
        s = _GREEK.sub(lambda m: hold(_greek(m)), s)
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
SECTIONS = {"method": "How it is made", "passage": "Reading the text"}


def article_passages(body):
    """The verses an article quotes, from its placeholders, as
    [(book, chapter, [verses])] in canonical order."""
    found = set()
    for m in _GREEK.finditer(body):
        found.add((m[1], int(m[2]), int(m[3])))
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
    summary, date, order, section (a key of SECTIONS)."""
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
    meta["title"], meta["summary"] = smart_quotes(meta["title"]), smart_quotes(meta["summary"])
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


def article_meta(a, lang="en"):
    """"6 min read · John 1:1, 14": what a card or byline says about length
    and which verses an article reads."""
    parts = [html.escape(t(lang, "article.min_read", n=a["minutes"]))]
    parts += [html.escape(passage_label(*p, lang)) for p in a["passages"]]
    return " &middot; ".join(parts)


def article_card(a, lang="en", featured=False):
    section = catalog(lang)["sections"][a["section"]]
    return (f'<li><a class="a-card{" featured" if featured else ""}" href="{url(lang, article_url(a))}">'
            f'<span class="a-section">{section}</span>'
            f'<span class="a-title">{display(a["title"])}</span>'
            f'<span class="a-summary">{display(a["summary"])}</span>'
            f'<span class="a-meta">{article_meta(a, lang)}</span></a></li>')


def article_list(articles, lang="en"):
    return "".join(article_card(a, lang) for a in articles)


def articles_page(articles, lang="en"):
    """The articles in lang, or a note that none is translated yet."""
    by_order = sorted(articles, key=lambda a: a["order"])
    if by_order:
        featured, rest = by_order[0], by_order[1:]
        sections = "".join(
            f'<section class="a-group" id="{key}" aria-labelledby="{key}-h">'
            f'<h2 id="{key}-h">{catalog(lang)["sections"][key]}</h2>'
            f'<ul class="a-grid">{article_list([a for a in rest if a["section"] == key], lang)}</ul></section>'
            for key in SECTIONS if any(a["section"] == key for a in rest))
        listing = f'<ul class="a-feature">{article_card(featured, lang, featured=True)}</ul>\n{sections}'
    else:
        listing = f'<p class="notice">{t(lang, "articles.none")}</p>'
    body = f"""
<header class="page-head">
<p class="eyebrow">{t(lang, "articles.title")}</p>
<h1>{t(lang, "articles.heading")}</h1>
<p class="dek">{t(lang, "articles.dek")}</p>
</header>
{listing}
"""
    return page(lang, t(lang, "articles.title"), body, path="/articles/", current="/articles/",
                description=t(lang, "meta.articles_description"))


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
    body = f"""
<div class="article-layout">
<article class="article">
<header class="article-head">
<p class="eyebrow"><a href="{url(lang, "/articles/")}#{article["section"]}">{section}</a></p>
<h1>{display(article["title"])}</h1>
<p class="dek">{display(article["summary"])}</p>
<p class="byline">{MARK}<span>Open Word Bible &middot; {_date(article["date"], lang)} &middot; {t(lang, "article.min_read", n=article["minutes"])}</span></p>
</header>
<div class="article-body">
{content}
</div>
{passage}
</article>
{f'<nav class="toc" aria-labelledby="toc-h"><h2 id="toc-h">{t(lang, "article.on_this_page")}</h2><ol>{contents}</ol></nav>' if len(toc) > 1 else ""}
</div>
<section class="more" aria-labelledby="more-h"><h2 id="more-h">{t(lang, "article.keep_reading")}</h2>
{f'<ul class="a-grid">{article_list(more, lang)}</ul>' if more else ""}
<p><a href="{url(lang, "/articles/")}">{t(lang, "article.all")}</a></p></section>
"""
    return page(lang, article["title"], body, path=article_url(article), current="/articles/",
                card=og_card_article(article),
                card_alt=t(lang, "meta.article_card_alt", section=section,
                           title=article["title"], summary=article["summary"]),
                description=article["summary"],
                translated=article_languages(article))


def account_page(lang="en"):
    """Sign in by email link, and the signed-in account (web/account.js).
    Not in the sitemap, and not indexed."""
    def a(key):
        return t(lang, "account." + key)

    messages = json.dumps(catalog(lang)["account.ui"], ensure_ascii=False).replace("</", "<\\/")
    body = f"""
<section class="account" id="account" aria-live="polite">
<header class="page-head">
<p class="eyebrow">{a("title")}</p>
<h1 id="account-title">{t(lang, "tools.sign_in")}</h1>
</header>

<div data-state="signed-out" hidden>
<p class="dek">{a("signed_out_dek")}</p>
<form class="account-form" id="link-form" novalidate>
<label for="email">{a("email")}</label>
<div class="field-row">
<input id="email" name="email" type="email" autocomplete="email" inputmode="email" required>
<button class="button" type="submit">{a("send")}</button>
</div>
<p class="form-error" id="link-error" role="alert" hidden></p>
</form>
<p class="fine">{a("privacy")}</p>
</div>

<div data-state="sent" hidden>
<p class="dek">{a("sent_dek")}</p>
<p><button class="button ghost" type="button" id="different-email">{a("different")}</button></p>
</div>

<div data-state="confirm" hidden>
<p class="dek">{a("confirm_dek")}</p>
<p><button class="button" type="button" id="finish">{a("finish")}</button></p>
</div>

<div data-state="signed-in" hidden>
<dl class="account-facts">
<div><dt>{a("fact_email")}</dt><dd id="me-email"></dd></div>
<div><dt>{a("fact_roles")}</dt><dd id="me-roles"></dd></div>
<div><dt>{a("fact_joined")}</dt><dd id="me-joined"></dd></div>
</dl>
<form class="account-form" id="name-form">
<label for="display-name">{a("display_name")} <span class="fine">{a("display_name_note")}</span></label>
<div class="field-row">
<input id="display-name" name="display_name" maxlength="80" autocomplete="name">
<button class="button ghost" type="submit">{a("save")}</button>
</div>
<p class="form-note" id="name-note" role="status"></p>
</form>
<div class="soon">
<h2>{a("soon")}</h2>
<p>{a("soon_text")}</p>
</div>
<p><button class="button ghost" type="button" id="sign-out">{a("sign_out")}</button></p>
</div>
</section>
<script type="application/json" id="account-text">{messages}</script>
<script src="{asset("account.js")}" defer></script>
"""
    return page(lang, a("title"), body, unlisted="/account/")


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
        "icons": [{"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
    }, indent=2) + "\n"


def service_worker():
    """web/sw.js with the files to keep from the start (the styles, the
    scripts and each language's offline page). Its version is a hash of the
    whole, so a deploy that changes any of them installs a new worker."""
    shell = [asset(n) for n in ("style.css", "site.js", "search.js", "reader.js")]
    shell += ["/favicon.svg", "/manifest.webmanifest"] + [url(lang, "/offline/") for lang in LANGUAGES]
    offline = {("" if lang == "en" else lang): url(lang, "/offline/") for lang in LANGUAGES}
    current = [asset(n) for n in ("style.css", "site.js", "search.js", "reader.js", "account.js")]
    current += [word_uses()[1]] + [search_index_url(lang) for lang in LANGUAGES]
    text = ((ROOT / "web" / "sw.js").read_text(encoding="utf-8")
            .replace("__PRECACHE__", json.dumps(shell)).replace("__OFFLINE__", json.dumps(offline))
            .replace("__CURRENT__", json.dumps(current)))
    return text.replace("__VERSION__", hashlib.sha256(text.encode()).hexdigest()[:10])


FAVICON = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#3f3d9a"/>
<path d="{BOOK_PATH}" fill="#faf6ef"/>
{QUOTES.format(fill="#3f3d9a")}
</svg>
"""


# Search (web/search.js). The site is static, so the build writes an index
# of everything a reader can find, one file per interface language, and the
# browser searches it: the /search/ page, and the palette that Ctrl K or
# Cmd K opens on any page, as on Ochorus. An index holds what that
# language's pages show: each sentence in the language the reader shows it
# in, its notes, the articles and the passages.

# Book abbreviations a reader may type besides each book's names, its USFM
# code and its OSIS id ("Phil"); and prefixes of the names, from three
# letters, in canonical order (so "phil" is Philippians, not Philemon).
BOOK_ALIASES = {"JHN": ["jn"], "PHP": ["flp", "fil"], "1JN": ["1jn"], "2JN": ["2jn"], "3JN": ["3jn"]}
# The palette's page shortcuts, by catalog key.
SEARCH_PAGES = (("nav.home", "/"), ("nav.read", "/read/"), ("nav.articles", "/articles/"),
                ("nav.about_project", "/about/"), ("nav.credits", "/about/#credits"),
                ("nav.help", "/#help"), ("tools.sign_in", "/account/"))


def fold(text):
    """Text as search compares it: lower case, without accents."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(c))


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
                   "x": r["renderings"][shown]}
            if shown != lang:
                doc["l"] = shown
            docs.append(doc)
            for d in r["decisions"]:
                if d["layer"] == "rendering" and d["language"] != shown:
                    continue
                docs.append({"k": "n", "bk": p.book, "c": p.chapter,
                             "v": verse, "u": url(lang, p.url), "y": d["layer"], "g": d["category"],
                             "t": d["choice"], "al": d["alternatives"], "s": d["reason"],
                             "l": "en" if d["layer"] == "meaning" else d["language"]})
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
def search_index(lang):
    """The search index for pages in lang, as JSON text (search_documents)."""
    return json.dumps(search_documents(lang), ensure_ascii=False, separators=(",", ":"))


@functools.lru_cache(maxsize=None)
def search_index_url(lang):
    digest = hashlib.sha256(search_index(lang).encode("utf-8")).hexdigest()[:10]
    return f"/search-{lang}.json?v={digest}"


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
<ul class="palette-list" id="palette-list" role="listbox" aria-label="{t(lang, "nav.search")}"></ul>
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
<div class="search-layout" id="search-results" hidden data-error="{html.escape(ui["error"])}" data-retry="{html.escape(ui["retry"])}" data-remove="{html.escape(ui["remove"])}"></div>
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
    for cached in (nav_menus, footer_links, passages, asset, translated_verses, catalog, search_documents, search_index,
                   search_index_url, word_uses):
        cached.cache_clear()
    if out.exists():
        shutil.rmtree(out)
    pages, indexed = {}, []
    for lang in LANGUAGES:
        def add(path, text, index=True):
            pages[url(lang, path)] = text
            if index:
                indexed.append(url(lang, path))

        add("/", home_page(lang))
        add("/read/", read_page(lang))
        add("/about/", about_page(lang))
        add("/search/", search_page(lang))
        for book, chapter in chapters():
            add(chapter_url(book, chapter), chapter_page(book, chapter, lang))
        articles = load_articles(lang)
        add("/articles/", articles_page(articles, lang), index=bool(articles))
        for article in articles:
            add(article_url(article), article_page(article, articles, lang))
        add("/account/", account_page(lang), index=False)
        add("/offline/", offline_page(lang), index=False)
    files = {(p.strip("/") + "/index.html").lstrip("/"): text for p, text in pages.items()}
    files["404.html"] = not_found_page()
    files["sitemap.xml"] = sitemap(indexed)
    files["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    files["favicon.svg"] = FAVICON
    files["manifest.webmanifest"] = manifest()
    files["sw.js"] = service_worker()
    files["word-uses.json"] = word_uses()[0]
    for lang in LANGUAGES:
        files[f"search-{lang}.json"] = search_index(lang)
    for rel, text in files.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for name in ("style.css", "reader.js", "site.js", "account.js", "search.js"):
        shutil.copy(ROOT / "web" / name, out / name)
    shutil.copytree(ROOT / "web" / "fonts", out / "fonts")
    shutil.copytree(OG, out / "og", ignore=shutil.ignore_patterns("manifest.json"))
    return sorted(files) + ["reader.js", "search.js", "site.js", "style.css"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--output", default=str(ROOT / "site"))
    args = ap.parse_args()
    for rel in build(Path(args.output)):
        print(f"built {rel}")


if __name__ == "__main__":
    main()
