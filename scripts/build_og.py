"""Draw the link-preview images (og:image) into web/og/.

Usage: python3 scripts/build_og.py [--check]

Social apps and chat show a page's og:image when a link is shared, and most
of them ignore SVG, so each card is drawn as HTML and photographed with
headless Chrome, then saved as JPEG (sips, on macOS). The images are
committed: the site build only copies them. Run this after changing a
passage's opening verse, an article's title or summary, or the template;
web/og/manifest.json records what each image was drawn from, and the tests
fail when a card is stale. --check only reports stale or missing cards.

Cards: one per passage (its opening verse in English and Greek), one per
article (section, title, summary), and "site" for every other page.
"""
import argparse
import hashlib
import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from owb import markup  # noqa: E402

OUT = ROOT / "web" / "og"
MANIFEST = OUT / "manifest.json"
WIDTH, HEIGHT = 1200, 630
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Bump when the template changes, so every card is drawn again.
TEMPLATE_VERSION = 2
# The site's fonts, from the same pinned packages as web/fonts/.
FONT_CSS = ("https://cdn.jsdelivr.net/npm/@fontsource/gentium-book-plus@5.2.7/index.css",
            "https://cdn.jsdelivr.net/npm/@fontsource/gentium-book-plus@5.2.7/greek.css",
            "https://cdn.jsdelivr.net/npm/@fontsource/gentium-book-plus@5.2.7/greek-ext.css",
            "https://cdn.jsdelivr.net/npm/@fontsource/gentium-book-plus@5.2.7/400-italic.css")


def cards():
    """{name: spec} for every card. A spec holds only what the card shows."""
    specs = {"site": {"kind": "site", "title": "The Bible, translated from Hebrew and Greek, "
                                               "with its reasoning shown."}}
    for book, chapter in build_site.chapters():
        records, words = build_site.load_chapter(book, chapter)
        first = records[0]
        verse = first["refs"][0]
        mine = set(first["source"]["tokens"])
        greek = " ".join(w["text"] + w["after"].strip() for w in words[verse] if w["id"] in mine)
        english = build_site.plain(markup.VERSE.split(first["renderings"]["en"]["B"])[0])
        specs[build_site.og_card_chapter(book, chapter)] = {
            "kind": "passage", "eyebrow": build_site.chapter_title(records, book, chapter),
            "title": english, "greek": greek}
    for a in build_site.load_articles():
        specs[build_site.og_card_article(a)] = {
            "kind": "article", "eyebrow": build_site.SECTIONS[a["section"]],
            "title": a["title"], "summary": a["summary"]}
    return specs


def digest(spec):
    blob = json.dumps({"v": TEMPLATE_VERSION, **spec}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def card_html(spec):
    e = html.escape
    links = "".join(f'<link rel="stylesheet" href="{u}">' for u in FONT_CSS)
    if spec["kind"] == "passage":
        size = 52 if len(spec["title"]) < 90 else 44 if len(spec["title"]) < 140 else 38
        main = (f'<p class="eyebrow">{e(spec["eyebrow"])}</p>'
                f'<p class="quote" style="font-size:{size}px">“{e(spec["title"])}”</p>'
                f'<p class="greek" lang="grc">{e(spec["greek"])}</p>')
    elif spec["kind"] == "article":
        size = 64 if len(spec["title"]) < 50 else 54 if len(spec["title"]) < 80 else 46
        main = (f'<p class="eyebrow">Article &middot; {e(spec["eyebrow"])}</p>'
                f'<h1 style="font-size:{size}px">{e(spec["title"])}</h1>'
                f'<p class="summary">{e(spec["summary"])}</p>')
    else:
        main = (f'<h1 style="font-size:70px">{e(spec["title"])}</h1>'
                f'<p class="summary">Every sentence shows the original words, a word-for-word '
                f'gloss, and why each word was chosen.</p>')
    mark = build_site.MARK.replace('class="mark"', 'class="mark" width="56" height="56"')
    return f"""<!doctype html><html><head><meta charset="utf-8">{links}<style>
html, body {{ margin: 0; width: {WIDTH}px; height: {HEIGHT}px; overflow: hidden; }}
body {{ box-sizing: border-box; padding: 64px 72px 56px; display: flex; flex-direction: column;
  background: #fbfaf7; color: #1f1d1a; font-family: "Gentium Book Plus", Georgia, serif;
  border-top: 14px solid #7a4b14; }}
.mark rect {{ fill: #7a4b14; }} .mark path {{ fill: #fbfaf7; }}
.brand {{ display: flex; align-items: center; gap: 16px; font-size: 34px; }}
main {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }}
p, h1 {{ margin: 0; }}
.eyebrow {{ font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; font-size: 24px; font-weight: 700;
  letter-spacing: .08em; text-transform: uppercase; color: #7a4b14; margin-bottom: 18px; }}
h1 {{ font-weight: normal; line-height: 1.12; letter-spacing: -.01em; }}
.quote {{ line-height: 1.3; }}
.greek {{ font-size: 30px; color: #6b665e; margin-top: 22px; line-height: 1.4; }}
.summary {{ font-size: 30px; line-height: 1.4; color: #6b665e; margin-top: 20px; }}
footer {{ display: flex; justify-content: space-between; font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-size: 22px; color: #6b665e; }}
</style></head><body>
<div class="brand">{mark}<span>Open Word Bible</span></div>
<main>{main}</main>
<footer><span>openwordbible.org</span><span>Free &middot; public domain &middot; reasoning shown</span></footer>
</body></html>"""


def draw(name, spec, tmp):
    page = tmp / f"{name}.html"
    page.write_text(card_html(spec), encoding="utf-8")
    png = tmp / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={WIDTH},{HEIGHT}", "--virtual-time-budget=5000",
                    f"--screenshot={png}", page.as_uri()],
                   check=True, capture_output=True)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82",
                    str(png), "--out", str(OUT / f"{name}.jpg")], check=True, capture_output=True)


def stale(specs, manifest):
    return sorted(n for n, s in specs.items()
                  if manifest.get(n) != digest(s) or not (OUT / f"{n}.jpg").is_file())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="only report stale or missing cards")
    args = ap.parse_args()
    specs = cards()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    todo = stale(specs, manifest)
    if args.check:
        print("\n".join(todo) or "all cards current")
        return 1 if todo else 0
    if todo and not Path(CHROME).is_file():
        raise SystemExit(f"needs Google Chrome at {CHROME}")
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name in todo:
            draw(name, specs[name], Path(tmp))
            print(f"drew {name}.jpg")
    for old in OUT.glob("*.jpg"):
        if old.stem not in specs:
            old.unlink()
            print(f"removed {old.name}")
    MANIFEST.write_text(json.dumps({n: digest(s) for n, s in sorted(specs.items())}, indent=1) + "\n",
                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
