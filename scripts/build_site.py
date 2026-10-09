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

from owb import refs  # noqa: E402

BOOK_NAMES = {"JHN": {"en": "John", "es": "Juan"}}
LANGUAGES = ("en", "es")
SITE_NAME = "Open Word Bible"


def page(title, body, current="", description=""):
    nav = [("/", "Home"), ("/jhn/1/", "Read"), ("/about/", "About")]
    links = "".join(
        f'<a href="{href}"{" aria-current=page" if href == current else ""}>{label}</a>'
        for href, label in nav)
    full_title = f"{title} · {SITE_NAME}" if title != SITE_NAME else SITE_NAME
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
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


def chapter_page(book, chapter):
    records, words = load_chapter(book, chapter)
    verses = [refs.parse(r["refs"][0]).verse for r in records]
    span = f"{chapter}:{min(verses)}–{max(verses)}"
    title = {lang: f"{BOOK_NAMES[book][lang]} {span}" for lang in LANGUAGES}
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
</div>
<p class="hint"><span id="hint-level"></span> <span id="hint-gender"></span> <span id="hint-christos"></span> <span id="hint-deity_pronoun"></span></p>
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
    return page(title["en"], body, current="/jhn/1/",
                description="John 1:1-18 translated from the Greek, with the reasoning behind every verse.")


def home_page():
    body = """
<section class="hero">
<h1>The Bible, translated from Hebrew and Greek, with its reasoning shown.</h1>
<p>Open Word Bible is a free translation for every reader. Tap any verse to see the original words,
a word-for-word gloss, and why each word was chosen. Everything is released under CC0.</p>
<a class="button" href="/jhn/1/">Read John 1:1&ndash;18</a>
</section>
<section class="points">
<div><h2>Three levels</h2><p>Literal follows the original closely, Balanced reads naturally, and Readable uses plain modern language. The meaning is the same at every level.</p></div>
<div><h2>Your settings</h2><p>Choose inclusive or traditional gender language, and &ldquo;Christ&rdquo; or &ldquo;Messiah&rdquo;. Settings change wording, never meaning.</p></div>
<div><h2>Every decision shown</h2><p>Each verse records what the original says, what we chose, what else we considered, and why. Uncertain decisions are marked as uncertain.</p></div>
<div><h2>Honest about its status</h2><p>The current text is an AI draft. Nothing is marked reviewed until named reviewers who read Hebrew or Greek approve it.</p></div>
</section>
"""
    return page(SITE_NAME, body, current="/",
                description="A free translation of the Bible from Hebrew and Greek, with the reasoning behind every verse.")


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
    return page("About", body, current="/about/",
                description="Licences and source credits for Open Word Bible.")


def not_found_page():
    return page("Not found", '<div class="prose"><h1>Page not found</h1>'
                '<p><a href="/">Go to the home page</a>.</p></div>')


def build(out):
    if out.exists():
        shutil.rmtree(out)
    files = {
        "index.html": home_page(),
        "jhn/1/index.html": chapter_page("JHN", 1),
        "about/index.html": about_page(),
        "404.html": not_found_page(),
    }
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
