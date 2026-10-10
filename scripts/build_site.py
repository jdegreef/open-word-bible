"""Build the static site into site/ from content/ and data/grc/.

Usage: python3 scripts/build_site.py [-o DIR]

Needs only the repository: the Greek words come from the committed extracts
in data/grc/ (see scripts/extract_tokens.py), so a deploy never fetches the
full sources.
"""
import argparse
import functools
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import markup, refs  # noqa: E402

BOOK_NAMES = {"JHN": {"en": "John", "es": "Juan"},
              "PHP": {"en": "Philippians", "es": "Filipenses"}}
LANGUAGES = ("en", "es")
SITE_NAME = "Open Word Bible"
# The site's home (Render serves it on openwordbible.org and redirects www).
# Canonical links, the sitemap and link previews use it.
SITE_URL = "https://openwordbible.org"
DESCRIPTION = ("A free translation of the Bible from Hebrew and Greek, "
               "with the reasoning behind every sentence.")
GITHUB_URL = "https://github.com/jdegreef/open-word-bible"

# The open-book mark: the favicon, and the logo in the header and footer
# (where style.css colours it from the current colour mode).
BOOK_PATH = ("M30 19C24 15.5 17 14.5 10 15.5v31c7-1 14 0 20 3.5zM34 19c6-3.5 13-4.5 20-3.5v31"
             "c-7-1-14 0-20 3.5z")
MARK = (f'<svg class="mark" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14"/>'
        f'<path d="{BOOK_PATH}"/></svg>')
MENU_ICON = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2" stroke-linecap="round" aria-hidden="true">'
             '<path d="M4 7h16M4 12h16M4 17h16"/></svg>')


# Colour modes (see web/style.css and web/site.js): value, label, and the
# background and accent its swatch shows. "auto" follows the device.
COLOUR_MODES = (("auto", "Automatic", "#fbfaf7", "#171614"),
                ("light", "Light", "#fbfaf7", "#7a4b14"),
                ("sepia", "Sepia", "#f4ecd8", "#74450f"),
                ("dark", "Dark", "#171614", "#e0a96a"),
                ("night", "Night", "#000000", "#c9965a"),
                ("contrast", "High contrast", "#ffffff", "#000000"))

# Applies the saved colour mode before the first paint, so a page never
# flashes the default colours. Mirrors web/site.js.
BOOT_SCRIPT = ("try{var t=localStorage.getItem('owb-theme');"
               "if(['light','sepia','dark','night','contrast'].indexOf(t)>=0)"
               "document.documentElement.setAttribute('data-theme',t)}catch(e){}")

GEAR = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83'
        'l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4'
        'a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1'
        'H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06'
        'A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 '
        '1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4'
        'h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>')

COLOUR_MENU = (
    '<div class="prefs">'
    '<button type="button" class="prefs-btn" aria-expanded="false" aria-controls="colour-menu" '
    f'aria-label="Colours" title="Colours">{GEAR}</button>'
    '<div id="colour-menu" class="prefs-menu" role="group" aria-labelledby="colour-menu-label" hidden>'
    '<p class="prefs-label" id="colour-menu-label">Colours</p>'
    '<div role="radiogroup" aria-labelledby="colour-menu-label">'
    + "".join(
        f'<button type="button" role="radio" aria-checked="{"true" if v == "auto" else "false"}" '
        f'tabindex="{0 if v == "auto" else -1}" data-theme-option="{v}">'
        f'<span class="swatch" style="--sw-bg:{bg};--sw-accent:{accent}" aria-hidden="true"></span>'
        f'{label}<span class="check" aria-hidden="true">&#10003;</span></button>'
        for v, label, bg, accent in COLOUR_MODES)
    + '</div></div></div>')


def page(title, body, path=None, current="", description=""):
    """A full HTML page. path is the page's URL path ("/read/"); pages with
    one get a canonical link and link-preview tags, and go in the sitemap."""
    nav = [("/read/", "Read"), ("/articles/", "Articles"), ("/about/", "About")]
    links = "".join(
        f'<a href="{href}"{" aria-current=page" if href == current else ""}>{label}</a>'
        for href, label in nav)
    links += f'<a class="nav-ext" href="{GITHUB_URL}">GitHub</a>'
    full_title = f"{title} · {SITE_NAME}" if title != SITE_NAME else SITE_NAME
    description = description or DESCRIPTION
    meta = ""
    if path is not None:
        url = html.escape(SITE_URL + path)
        meta = f"""
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta name="twitter:card" content="summary">"""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">{meta}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<script>{BOOT_SCRIPT}</script>
<link rel="stylesheet" href="/style.css">
<script src="/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap bar">
<a class="brand" href="/"{" aria-current=page" if current == "/" else ""}>{MARK}<span>{SITE_NAME}</span></a>
<nav class="primary" id="site-nav" aria-label="Main">{links}</nav>
<div class="tools">
{COLOUR_MENU}
<button type="button" class="menu-btn" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">{MENU_ICON}</button>
</div>
</div></header>
<main class="wrap" id="main" tabindex="-1">
{body}
</main>
{site_footer()}
</body>
</html>
"""


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


def curl_record(r):
    """The record with curly quotes in every text a reader sees. content/
    stores straight ones; curling here, the one loader, covers the reader,
    the home page and articles alike."""
    for levels in r["renderings"].values():
        for level, text in levels.items():
            levels[level] = smart_quotes(text)
    r["literal_gloss"] = smart_quotes(r["literal_gloss"])
    for d in r["decisions"]:
        d["choice"] = smart_quotes(d["choice"])
        d["alternatives"] = [smart_quotes(a) for a in d["alternatives"]]
        d["reason"] = smart_quotes(d["reason"])
    return r


def load_chapter(book, chapter):
    records = []
    for path in sorted((ROOT / "content" / book).glob("*.json")):
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
            first = refs.parse(r["refs"][0])
            if first.chapter == chapter:
                records.append(curl_record(r))
    records.sort(key=lambda r: refs.parse(r["refs"][0]).sort_key() + (r["id"],))
    words = json.loads((ROOT / "data" / "grc" / f"{book}.{chapter}.json")
                       .read_text(encoding="utf-8"))["verses"]
    return records, words


def chapters():
    """Every (book, chapter) with content, in canonical order."""
    found = set()
    for path in (ROOT / "content").glob("*/*.json"):
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
            ref = refs.parse(r["refs"][0])
            found.add((ref.book, ref.chapter))
    return sorted(found, key=lambda bc: refs.Ref(bc[0], bc[1], 1).sort_key())


def chapter_url(book, chapter):
    return f"/{book.lower()}/{chapter}/"


def chapter_title(records, book, chapter, lang="en"):
    verses = [refs.parse(v).verse for r in records for v in r["refs"]]
    return f"{BOOK_NAMES[book][lang]} {chapter}:{min(verses)}–{max(verses)}"


def chapter_page(book, chapter):
    records, words = load_chapter(book, chapter)
    title = {lang: chapter_title(records, book, chapter, lang) for lang in LANGUAGES}
    languages = [lang for lang in LANGUAGES
                 if all(lang in r["renderings"] for r in records)]
    data = {"book": book, "chapter": chapter, "title": title, "languages": languages,
            "records": records,
            "words": {vid: words[vid] for r in records for vid in r["refs"]}}
    # "</" cannot appear inside a script element.
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    # Labels are English here; reader.js swaps in the reading language's
    # labels (data-i18n keys) once the page loads.
    def seg(name, options):
        buttons = "".join(
            f'<button type="button" data-value="{v}"{f" data-i18n={key}" if key else ""}>{label}</button>'
            for v, label, key in options)
        return f'<span class="seg" data-setting="{name}">{buttons}</span>'

    def label(key, text):
        return f'<span data-i18n="{key}">{text}</span>'

    lang_labels = {"en": "English", "es": "Español"}
    body = f"""
<p class="notice" data-i18n="notice">Sample passage. Every line is an AI draft that has not yet been checked by a reviewer who reads Greek.</p>
<button type="button" class="settings-toggle" id="settings-toggle" aria-expanded="false" aria-controls="settings">
  <span data-i18n="settings">Reading settings</span> <span class="settings-summary" id="settings-summary"></span>
</button>
<div class="settings" id="settings">
<div class="controls">
  <div class="control">{label("language", "Language")} {seg("lang", [(l, lang_labels[l], None) for l in languages])}</div>
  <div class="control">{label("level", "Level")} {seg("level", [("L", "Literal", "L"), ("B", "Balanced", "B"), ("R", "Readable", "R")])}</div>
  <div class="control">{label("gender", "Gender")} {seg("gender", [("0", "Inclusive", "inclusive"), ("1", "Traditional", "traditional")])}</div>
  <div class="control">{label("title", "Title")} {seg("christos", [("0", "Christ", "christ"), ("1", "Messiah", "messiah")])}</div>
  <div class="control">{label("pronouns", "Pronouns for God")} {seg("deity_pronoun", [("0", "he", "he"), ("1", "He", "He")])}</div>
  <div class="control" data-only-lang="es" hidden>{label("plural", "Plural you")} {seg("plural_you", [("0", "ustedes", None), ("1", "vosotros", None)])}</div>
</div>
<p class="hint"><span id="hint-level"></span> <span id="hint-gender"></span> <span id="hint-christos"></span> <span id="hint-deity_pronoun"></span> <span id="hint-plural_you"></span></p>
</div>
<div class="reader">
  <article class="passage">
    <h1 id="title">{html.escape(title["en"])}</h1>
    <p class="sub" data-i18n="sub">Translated from the SBL Greek New Testament. Tap a verse to see why it reads as it does. &dagger; marks a verse with a footnote.</p>
    <div class="text" id="text"></div>
  </article>
  <aside class="panel" id="panel" aria-live="polite" tabindex="-1"></aside>
</div>
<script type="application/json" id="owb-data">{blob}</script>
<script src="/reader.js"></script>
"""
    return page(title["en"], body, path=chapter_url(book, chapter), current="/read/",
                description=f"{title['en']} translated from the Greek, with the reasoning behind every verse.")


def passage_card(book, chapter):
    """A passage as a card in the article-card style: its opening verse at
    the default settings, and how much of it is translated and recorded."""
    records = load_chapter(book, chapter)[0]
    verses = sorted({refs.parse(v).verse for r in records for v in r["refs"]})
    decisions = sum(len(r["decisions"]) for r in records)
    uncertain = sum(d["uncertain"] for r in records for d in r["decisions"])
    first = records[0]
    opening = plain(markup.VERSE.split(first["renderings"]["en"]["B"])[0])   # its first verse
    languages = " &middot; ".join(name for code, name in (("en", "English"), ("es", "Espa\u00f1ol"))
                                  if all(code in r["renderings"] for r in records))
    meta = (f"{len(verses)} verses &middot; {len(records)} sentences &middot; "
            f"{decisions} decisions, {uncertain} marked uncertain")
    return (f'<li><a class="a-card p-card" href="{chapter_url(book, chapter)}">'
            f'<span class="a-section">{BOOK_NAMES[book]["en"]} &middot; {languages}</span>'
            f'<span class="a-title">{html.escape(chapter_title(records, book, chapter))}</span>'
            f'<span class="p-opening">&ldquo;{display(opening)}&rdquo;</span>'
            f'<span class="a-meta">{meta}</span>'
            f'<span class="p-status"><span class="status">AI draft, not yet reviewed</span></span></a></li>')


def read_page():
    cards = "".join(passage_card(b, c) for b, c in chapters())
    body = f"""
<header class="page-head">
<p class="eyebrow">Read</p>
<h1>Passages translated so far</h1>
<p class="dek">Each passage is translated from the SBL Greek New Testament into English and
Spanish, at three levels, with the reasoning behind every sentence. All are AI drafts until a
reviewer who reads Greek approves them.</p>
</header>
<ul class="a-grid">{cards}</ul>
<section class="how" aria-labelledby="how-h">
<h2 id="how-h">How the reader works</h2>
<ol class="steps">
<li><b>Choose how it reads.</b> Literal, Balanced or Readable, and your wording settings: inclusive or
traditional language, &ldquo;Christ&rdquo; or &ldquo;Messiah&rdquo;, he or He.</li>
<li><b>Tap any verse.</b> The Greek appears with a word-for-word gloss beside the translation.</li>
<li><b>See every decision.</b> What the original means, what else was considered, why this wording
was chosen, and which calls are uncertain.</li>
</ol>
</section>
"""
    return page("Read", body, path="/read/", current="/read/",
                description="Passages translated in Open Word Bible so far, with the reasoning behind every sentence.")


def all_records():
    """Every record in content/, in canonical order."""
    return [r for b, c in chapters() for r in load_chapter(b, c)[0]]


def plain(text):
    """Rendering text as a reader sees it with the default settings."""
    return markup.VERSE.sub("", markup.render(text)).strip()


# The worked example on the home page: a record and one of its decisions.
EXAMPLE = ("JHN", 1, "JHN.1.1.s1", "m4")


def example_html():
    """John 1:1 at every level, with one decision and its Greek words marked.
    Everything comes from content/ and data/grc/, so it stays in step with
    the translation."""
    book, chapter, record_id, decision_id = EXAMPLE
    records, words = load_chapter(book, chapter)
    record = next(r for r in records if r["id"] == record_id)
    decision = next(d for d in record["decisions"] if d["id"] == decision_id)
    marked = set(decision["tokens"])
    greek = " ".join(
        (f'<mark>{html.escape(w["text"])}</mark>' if w["id"] in marked else html.escape(w["text"]))
        + html.escape(w["after"].rstrip())
        for vid in record["refs"] for w in words[vid] if w["id"] in record["source"]["tokens"])
    levels = "".join(
        f'<div class="lvl"><span class="tag">{name}</span><p>{html.escape(plain(record["renderings"]["en"][code]))}</p></div>'
        for code, name in (("L", "Literal"), ("B", "Balanced"), ("R", "Readable")))
    ref = refs.parse(record["refs"][0])
    also = "; ".join(html.escape(a) for a in decision["alternatives"])
    return f"""
<section class="example" aria-labelledby="example-h">
<h2 id="example-h">See the work: {BOOK_NAMES[book]["en"]} {ref.chapter}:{ref.verse}</h2>
<div class="example-grid">
<div>
<p class="label">Greek (SBL Greek New Testament)</p>
<p class="greek" lang="grc">{greek}</p>
<p class="label">Word for word</p>
<p class="gloss">{html.escape(plain(record["literal_gloss"]))}</p>
<p class="label">Three levels, one meaning</p>
{levels}
</div>
<div class="card decision">
<p class="label">Decision</p>
<p class="choice">&ldquo;{html.escape(plain(decision["choice"]))}&rdquo;</p>
<p class="alts">Also considered: {also}</p>
<p class="why">{html.escape(decision["reason"])}</p>
</div>
</div>
<p><a href="{chapter_url(book, chapter)}">Open {BOOK_NAMES[book]["en"]} {chapter} and tap any verse &rarr;</a></p>
</section>
"""


def progress_html():
    records = all_records()
    decisions = sum(len(r["decisions"]) for r in records)
    reviewed = sum(r["status"] != "ai_draft" for r in records)
    passages = "".join(
        f'<li><a href="{chapter_url(b, c)}">{html.escape(chapter_title(load_chapter(b, c)[0], b, c))}</a></li>'
        for b, c in chapters())
    return f"""
<section class="progress" aria-labelledby="progress-h">
<h2 id="progress-h">Where the work stands</h2>
<div class="stats">
<div><b>{len(records)}</b><span>sentences translated</span></div>
<div><b>{decisions}</b><span>decisions recorded</span></div>
<div><b>{reviewed}</b><span>reviewed by a scholar so far</span></div>
</div>
<p>Everything published so far is an <strong>AI draft</strong>, in English and Spanish. Nothing is
marked reviewed until named reviewers who read Hebrew or Greek approve it, and the reader always
shows each sentence's status.</p>
<p class="label">Passages so far</p>
<ul class="passages">{passages}</ul>
</section>
"""


def home_page():
    body = f"""
<section class="hero">
<h1>The Bible, translated from Hebrew and Greek, with its reasoning shown.</h1>
<p>Open Word Bible is a free translation for every reader. Open any sentence to see the original
words, a word-for-word gloss, and why each word was chosen. Everything is released under CC0,
so anyone may use it for anything.</p>
<p class="actions"><a class="button" href="/read/">Start reading</a>
<a class="button ghost" href="#example-h">See how it works</a></p>
</section>
{example_html()}
<section class="points" aria-label="Principles">
<div><h2>Free for everyone</h2><p>The translation, its notes and its data are public domain (CC0). Quote it, print it, put it in an app, or build on it without asking.</p></div>
<div><h2>From the original languages</h2><p>Every language is translated from the Hebrew, Aramaic and Greek, never from English, using fixed, openly licensed source texts.</p></div>
<div><h2>Three levels, your settings</h2><p>Literal, Balanced or Readable; inclusive or traditional gender language; &ldquo;Christ&rdquo; or &ldquo;Messiah&rdquo;. Settings change wording, never meaning.</p></div>
<div><h2>Every decision shown</h2><p>Each sentence records what the original says, what we chose, what else we considered, and why. Uncertain calls are marked uncertain.</p></div>
</section>
{progress_html()}
<section class="latest" aria-labelledby="latest-h">
<h2 id="latest-h">From the articles</h2>
<ul class="a-grid">{article_list(sorted(load_articles(), key=lambda a: a["order"])[:3])}</ul>
<p><a href="/articles/">All articles &rarr;</a></p>
</section>
<section class="involve" id="help" aria-labelledby="involve-h">
<h2 id="involve-h">Help make it</h2>
<ul>
<li><strong>Read Greek or Hebrew?</strong> Reviewers check each sentence and its decisions before it is marked reviewed.</li>
<li><strong>Native Spanish speaker?</strong> Check that the Spanish reads naturally at each level.</li>
<li><strong>Build software?</strong> The site, validator and data tools are open source (MIT).</li>
<li><strong>Making something?</strong> Use the text and its reasoning records in your own app, study or project.</li>
</ul>
<p><a class="button ghost" href="https://github.com/jdegreef/open-word-bible">The project on GitHub</a></p>
</section>
"""
    return page(SITE_NAME, body, path="/", current="/", description=DESCRIPTION)


def about_page():
    credits = markdown((ROOT / "CREDITS.md").read_text(encoding="utf-8"))
    # Demote the file's headings one level to sit under the page's h1.
    for n in (2, 1):
        credits = credits.replace(f"<h{n}>", f"<h{n + 1}>").replace(f"</h{n}>", f"</h{n + 1}>")
    credits = credits.replace("<h2>Credits</h2>", '<h2 id="credits">Credits</h2>', 1)
    body = f"""
<div class="prose">
<h1>About</h1>
<p>Open Word Bible translates the Bible from its original languages into modern ones,
English and Spanish first. Every sentence carries a record of the original words and the reasoning
behind each translation decision.</p>
<h2>Licences</h2>
<p>The translation, its reasoning records and the alignments are dedicated to the public domain
under <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>.
The code is MIT-licensed. The source texts keep their own licences, credited below.</p>
<p>Source code and data: <a href="https://github.com/jdegreef/open-word-bible">github.com/jdegreef/open-word-bible</a>.</p>
{credits}
</div>
"""
    return page("About", body, path="/about/", current="/about/",
                description="Licences and source credits for Open Word Bible.")


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


def _owb(m):
    """{{OWB:JHN.1.1.s1:B}}: our English for a sentence, with default settings."""
    record_id, level = m[1], m[2]
    ref = refs.parse(record_id.rsplit(".s", 1)[0])
    record = next((r for r in load_chapter(ref.book, ref.chapter)[0] if r["id"] == record_id), None)
    if record is None:
        raise SystemExit(f"no record {record_id} in content/")
    return html.escape(plain(record["renderings"]["en"][level]))


def smart_quotes(s):
    """Curly quotes and apostrophes for straight ones in plain text."""
    s = re.sub(r'(^|[\s(\[\u2014-])"', "\\1\u201c", s)
    s = s.replace('"', "\u201d")
    s = re.sub(r"(^|[\s(\[\u2014-])'", "\\1\u2018", s)
    return s.replace("'", "\u2019")


LEVEL_NAMES = {"L": "Literal", "B": "Balanced", "R": "Readable"}


@functools.lru_cache(maxsize=None)
def translated_verses():
    """Every verse id with a record, so article links only go to verses the
    reader has."""
    return frozenset(v for r in all_records() for v in r["refs"])


def verse_link(book, chapter, verse):
    """The reader URL for a verse, or None when it is not translated yet."""
    if f"{book}.{chapter}.{verse}" not in translated_verses():
        return None
    return f"{chapter_url(book, chapter)}#v{verse}"


def verse_name(book, chapter, verse):
    return f"{BOOK_NAMES[book]['en']} {chapter}:{verse}"


def _quote_figure(body, inner):
    """A blockquote that is just one {{GREEK:..}} or {{OWB:..}} placeholder
    becomes a figure captioned with its source, linked to the reader."""
    m = _GREEK.fullmatch(body)
    if m:
        book, chapter, verse = m[1], int(m[2]), int(m[3])
        source = "Greek, SBL Greek New Testament"
    else:
        m = _OWB.fullmatch(body)
        if not m:
            return f"<blockquote><p>{inner}</p></blockquote>"
        ref = refs.parse(m[1].rsplit(".s", 1)[0])
        book, chapter, verse = ref.book, ref.chapter, ref.verse
        source = f"Open Word Bible, {LEVEL_NAMES[m[2]]}"
    kind = "greek-quote" if source.startswith("Greek") else "owb-quote"
    link = verse_link(book, chapter, verse)
    more = f' <a href="{link}">Read it with the reasoning&nbsp;&rarr;</a>' if link else ""
    return (f'<figure class="quote {kind}"><blockquote><p>{inner}</p></blockquote>'
            f"<figcaption>{verse_name(book, chapter, verse)} &middot; {source}{more}</figcaption></figure>")


def _slug(text, taken):
    base = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-") or "section"
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1
    taken.add(slug)
    return slug


def article_html(text, toc=None):
    """Markdown for articles: ## and ### headings, paragraphs, - lists,
    > quotes, **bold**, *italic*, [links](url), and placeholders that pull
    Greek words ({{GREEK:..}}, {{LEMMA:..}}) and our own translation
    ({{OWB:..}}) from the data, so none of it is typed by hand."""
    fills = []

    def hold(html_text):
        fills.append(html_text)
        return f"\x00{len(fills) - 1}\x00"

    def inline(s):
        s = _GREEK.sub(lambda m: hold(_greek(m)), s)
        s = _LEMMA.sub(lambda m: hold(_lemma(m)), s)
        s = _OWB.sub(lambda m: hold(_owb(m)), s)
        s = re.sub(r"\]\(([^)\s]+)\)", lambda m: "](" + hold(html.escape(m[1])) + ")", s)
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
            out.append(_quote_figure(body, inline(body)))
        else:
            out.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(out)


# Article sections, in the order the articles page shows them.
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


def passage_label(book, chapter, verses):
    """"John 1:1, 14, 16–18": consecutive verses become ranges."""
    runs = []
    for v in verses:
        if runs and v == runs[-1][1] + 1:
            runs[-1][1] = v
        else:
            runs.append([v, v])
    return f"{BOOK_NAMES[book]['en']} {chapter}:" + ", ".join(
        str(a) if a == b else f"{a}\u2013{b}" for a, b in runs)


def load_articles():
    """Every article in articles/, newest first, then by its order number.
    A file starts with a front matter block: title, summary, date, order,
    section (a key of SECTIONS)."""
    articles = []
    for path in sorted(ARTICLES.glob("*.md")):
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
        articles.append({**meta, "slug": path.stem, "body": m[2], "order": int(meta["order"]),
                         "minutes": max(1, round(words / 220)),
                         "passages": article_passages(m[2])})
    return sorted(articles, key=lambda a: (a["date"], -a["order"]), reverse=True)


def article_url(article):
    return f"/articles/{article['slug']}/"


def _date(iso):
    import datetime
    return datetime.date.fromisoformat(iso).strftime("%-d %B %Y")


def display(text):
    """Escaped text for the page, with a verse range's dash ("4:6–7") kept
    on one line. Only the visible HTML gets the word joiners; titles and
    link previews keep the plain text."""
    return re.sub(r"(\d)\u2013(\d)", "\\1\u2060\u2013\u2060\\2", html.escape(text))


def article_meta(a):
    """"6 min read · John 1:1, 14": what a card or byline says about length
    and which verses an article reads."""
    parts = [f"{a['minutes']} min read"] + [passage_label(*p) for p in a["passages"]]
    return " &middot; ".join(html.escape(p) for p in parts)


def article_card(a, featured=False):
    return (f'<li><a class="a-card{" featured" if featured else ""}" href="{article_url(a)}">'
            f'<span class="a-section">{SECTIONS[a["section"]]}</span>'
            f'<span class="a-title">{display(a["title"])}</span>'
            f'<span class="a-summary">{display(a["summary"])}</span>'
            f'<span class="a-meta">{article_meta(a)}</span></a></li>')


def article_list(articles):
    return "".join(article_card(a) for a in articles)


def articles_page(articles):
    by_order = sorted(articles, key=lambda a: a["order"])
    featured, rest = by_order[0], by_order[1:]
    sections = "".join(
        f'<section class="a-group" id="{key}" aria-labelledby="{key}-h">'
        f'<h2 id="{key}-h">{label}</h2>'
        f'<ul class="a-grid">{article_list([a for a in rest if a["section"] == key])}</ul></section>'
        for key, label in SECTIONS.items())
    body = f"""
<header class="page-head">
<p class="eyebrow">Articles</p>
<h1>How the translation is made, and why it reads as it does</h1>
<p class="dek">Short pieces on the method behind Open Word Bible and close readings of the passages
translated so far. Like the translation, every article is a draft until a reviewer has checked it.</p>
</header>
<ul class="a-feature">{article_card(featured, featured=True)}</ul>
{sections}
"""
    return page("Articles", body, path="/articles/", current="/articles/",
                description="Articles on how Open Word Bible is translated and why it reads as it does.")


def article_page(article, articles):
    toc = []
    content = article_html(article["body"], toc)
    same = [a for a in articles if a is not article and a["section"] == article["section"]]
    other = [a for a in articles if a is not article and a["section"] != article["section"]]
    more = sorted(same, key=lambda a: a["order"])[:2] + sorted(other, key=lambda a: a["order"])[:1]
    contents = "".join(f'<li><a href="#{slug}">{label}</a></li>' for slug, label in toc)
    links = [(passage_label(b, c, vs), next(filter(None, (verse_link(b, c, v) for v in vs)), None))
             for b, c, vs in article["passages"]]
    read = "".join(f'<a class="chip" href="{href}">{html.escape(label)}&nbsp;&rarr;</a>'
                   for label, href in links if href)
    passage = (f'<aside class="read-card"><h2>Read the passage</h2><p>Open it in the reader, '
               f'tap any verse, and every decision behind it is there.</p><p>{read}</p></aside>'
               if read else "")
    body = f"""
<div class="article-layout">
<article class="article">
<header class="article-head">
<p class="eyebrow"><a href="/articles/#{article["section"]}">{SECTIONS[article["section"]]}</a></p>
<h1>{display(article["title"])}</h1>
<p class="dek">{display(article["summary"])}</p>
<p class="byline">{MARK}<span>Open Word Bible &middot; {_date(article["date"])} &middot; {article["minutes"]} min read
<span class="status">Draft, not yet reviewed</span></span></p>
</header>
<div class="article-body">
{content}
</div>
{passage}
</article>
{f'<nav class="toc" aria-labelledby="toc-h"><h2 id="toc-h">On this page</h2><ol>{contents}</ol></nav>' if len(toc) > 1 else ""}
</div>
<section class="more" aria-labelledby="more-h"><h2 id="more-h">Keep reading</h2>
<ul class="a-grid">{article_list(more)}</ul>
<p><a href="/articles/">All articles &rarr;</a></p></section>
"""
    return page(article["title"], body, path=article_url(article), current="/articles/",
                description=article["summary"])


def not_found_page():
    return page("Not found", '<div class="prose"><h1>Page not found</h1>'
                '<p><a href="/">Go to the home page</a>.</p></div>')


FAVICON = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="12" fill="#7a4b14"/>
<path d="{BOOK_PATH}" fill="#fbfaf7"/>
</svg>
"""


@functools.lru_cache(maxsize=None)
def site_footer():
    """The footer on every page: the passages, the first articles to read,
    and the project's links. Built once per build."""
    def items(pairs):
        return "".join(f'<li><a href="{href}">{html.escape(label)}</a></li>' for href, label in pairs)

    passages = [(chapter_url(b, c), chapter_title(load_chapter(b, c)[0], b, c)) for b, c in chapters()]
    start = sorted((a for a in load_articles() if a["section"] == "method"), key=lambda a: a["order"])[:3]
    learn = [(article_url(a), a["title"]) for a in start] + [("/articles/", "All articles")]
    project = [("/about/", "About"), ("/about/#credits", "Sources and credits"),
               ("/#help", "Help make it"), (GITHUB_URL, "Source code"),
               (GITHUB_URL + "/issues/new", "Report a problem")]
    return f"""<footer class="site"><div class="wrap">
<div class="foot-grid">
<div class="foot-about">
<a class="brand" href="/">{MARK}<span>{SITE_NAME}</span></a>
<p>A free Bible translated from Hebrew and Greek, with the reasoning behind every sentence shown.</p>
<p class="foot-licence"><span class="pill">CC0</span> Public domain: quote it, print it, build on it.</p>
</div>
<nav aria-labelledby="foot-read"><h2 id="foot-read">Read</h2><ul>{items(passages + [("/read/", "All passages")])}</ul></nav>
<nav aria-labelledby="foot-learn"><h2 id="foot-learn">Learn</h2><ul>{items(learn)}</ul></nav>
<nav aria-labelledby="foot-project"><h2 id="foot-project">Project</h2><ul>{items(project)}</ul></nav>
</div>
<div class="foot-base">
<p>Every sentence is an AI draft until a named reviewer who reads the original language approves it.</p>
<p>Translation and notes CC0 &middot; Code MIT &middot; Source texts keep their own licences</p>
</div>
</div></footer>"""


def sitemap(paths):
    urls = "".join(f"<url><loc>{html.escape(SITE_URL + p)}</loc></url>\n" for p in paths)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}</urlset>\n")


def build(out):
    site_footer.cache_clear()
    translated_verses.cache_clear()
    if out.exists():
        shutil.rmtree(out)
    pages = {"/": home_page(), "/read/": read_page(), "/about/": about_page()}
    for book, chapter in chapters():
        pages[chapter_url(book, chapter)] = chapter_page(book, chapter)
    articles = load_articles()
    pages["/articles/"] = articles_page(articles)
    for article in articles:
        pages[article_url(article)] = article_page(article, articles)
    files = {(p.strip("/") + "/index.html").lstrip("/"): text for p, text in pages.items()}
    files["404.html"] = not_found_page()
    files["sitemap.xml"] = sitemap(pages)
    files["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    files["favicon.svg"] = FAVICON
    for rel, text in files.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for asset in ("style.css", "reader.js", "site.js"):
        shutil.copy(ROOT / "web" / asset, out / asset)
    return sorted(files) + ["reader.js", "site.js", "style.css"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--output", default=str(ROOT / "site"))
    args = ap.parse_args()
    for rel in build(Path(args.output)):
        print(f"built {rel}")


if __name__ == "__main__":
    main()
