"""Build the static site into site/ from content/ and data/grc/.

Usage: python3 scripts/build_site.py [-o DIR]

Needs only the repository: the Greek words come from the committed extracts
in data/grc/ (see scripts/extract_tokens.py), so a deploy never fetches the
full sources.
"""
import argparse
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


def page(title, body, path=None, current="", description=""):
    """A full HTML page. path is the page's URL path ("/read/"); pages with
    one get a canonical link and link-preview tags, and go in the sitemap."""
    nav = [("/", "Home"), ("/read/", "Read"), ("/about/", "About")]
    links = "".join(
        f'<a href="{href}"{" aria-current=page" if href == current else ""}>{label}</a>'
        for href, label in nav)
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
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="/">{SITE_NAME}</a>
<nav>{links}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site"><div class="wrap">
The translation and its reasoning are released under CC0: free for anyone to use.
Source texts are credited on the <a href="/about/">About</a> page.
</div></footer>
</body>
</html>
"""


def markdown(text):
    """The small subset of Markdown that CREDITS.md uses."""
    def inline(s):
        s = html.escape(s, quote=False)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
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


def load_chapter(book, chapter):
    records = []
    for path in sorted((ROOT / "content" / book).glob("*.json")):
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
            first = refs.parse(r["refs"][0])
            if first.chapter == chapter:
                records.append(r)
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
<div class="controls">
  <div class="control">{label("language", "Language")} {seg("lang", [(l, lang_labels[l], None) for l in languages])}</div>
  <div class="control">{label("level", "Level")} {seg("level", [("L", "Literal", "L"), ("B", "Balanced", "B"), ("R", "Readable", "R")])}</div>
  <div class="control">{label("gender", "Gender")} {seg("gender", [("0", "Inclusive", "inclusive"), ("1", "Traditional", "traditional")])}</div>
  <div class="control">{label("title", "Title")} {seg("christos", [("0", "Christ", "christ"), ("1", "Messiah", "messiah")])}</div>
  <div class="control">{label("pronouns", "Pronouns for God")} {seg("deity_pronoun", [("0", "he", "he"), ("1", "He", "He")])}</div>
  <div class="control" data-only-lang="es" hidden>{label("plural", "Plural you")} {seg("plural_you", [("0", "ustedes", None), ("1", "vosotros", None)])}</div>
</div>
<p class="hint"><span id="hint-level"></span> <span id="hint-gender"></span> <span id="hint-christos"></span> <span id="hint-deity_pronoun"></span> <span id="hint-plural_you"></span></p>
<div class="reader">
  <article class="passage">
    <h1 id="title">{html.escape(title["en"])}</h1>
    <p class="sub" data-i18n="sub">Translated from the SBL Greek New Testament. Tap a verse to see why it reads as it does. &dagger; marks a verse with a footnote.</p>
    <div class="text" id="text"></div>
  </article>
  <aside class="panel" id="panel" aria-live="polite"></aside>
</div>
<script type="application/json" id="owb-data">{blob}</script>
<script src="/reader.js"></script>
"""
    return page(title["en"], body, path=chapter_url(book, chapter), current="/read/",
                description=f"{title['en']} translated from the Greek, with the reasoning behind every verse.")


def read_page():
    items = "".join(
        f'<li><a href="{chapter_url(b, c)}">'
        f'{html.escape(chapter_title(load_chapter(b, c)[0], b, c))}</a></li>'
        for b, c in chapters())
    body = f"""
<div class="prose">
<h1>Read</h1>
<p>Sample passages so far, each translated from the SBL Greek New Testament into English and
Spanish with the reasoning behind every sentence. All are AI drafts awaiting review.</p>
<ul>{items}</ul>
</div>
"""
    return page("Read", body, path="/read/", current="/read/",
                description="Passages available in Open Word Bible.")


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
<section class="involve" aria-labelledby="involve-h">
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
    body = f"""
<div class="prose">
<h1>About</h1>
<p>Open Word Bible translates the Bible from its original languages into modern ones,
English and Spanish first. Every verse carries a record of the original words and the reasoning
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


def not_found_page():
    return page("Not found", '<div class="prose"><h1>Page not found</h1>'
                '<p><a href="/">Go to the home page</a>.</p></div>')


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="12" fill="#7a4b14"/>
<path d="M18 16h12a6 6 0 0 1 6 6v28a5 5 0 0 0-5-5H18zM46 16H34a6 6 0 0 0-6 6v28a5 5 0 0 1 5-5h13z" fill="#fbfaf7"/>
</svg>
"""


def sitemap(paths):
    urls = "".join(f"<url><loc>{html.escape(SITE_URL + p)}</loc></url>\n" for p in paths)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}</urlset>\n")


def build(out):
    if out.exists():
        shutil.rmtree(out)
    pages = {"/": home_page(), "/read/": read_page(), "/about/": about_page()}
    for book, chapter in chapters():
        pages[chapter_url(book, chapter)] = chapter_page(book, chapter)
    files = {(p.strip("/") + "/index.html").lstrip("/"): text for p, text in pages.items()}
    files["404.html"] = not_found_page()
    files["sitemap.xml"] = sitemap(pages)
    files["robots.txt"] = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    files["favicon.svg"] = FAVICON
    for rel, text in files.items():
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for asset in ("style.css", "reader.js"):
        shutil.copy(ROOT / "web" / asset, out / asset)
    return sorted(files) + ["reader.js", "style.css"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--output", default=str(ROOT / "site"))
    args = ap.parse_args()
    for rel in build(Path(args.output)):
        print(f"built {rel}")


if __name__ == "__main__":
    main()
