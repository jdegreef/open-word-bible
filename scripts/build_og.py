"""Draw the link-preview images (og:image) into web/og/.

Usage: python3 scripts/build_og.py [--check]

Social apps and chat show a page's og:image when a link is shared, and most
of them ignore SVG, so each card is drawn as HTML and photographed with
headless Chrome or Chromium, then saved as JPEG (sips or ImageMagick). The images are
committed: the site build only copies them. Run this after changing a
passage's opening verse, an article's title or summary, or the template;
web/og/manifest.json records what each image was drawn from, and the tests
fail when a card is stale. --check only reports stale or missing cards.

Cards: one per passage (its opening verse in English and in Greek or Hebrew), one per
article (section, title, summary), and "site" for every other page.
"""
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402

OUT = ROOT / "web" / "og"
MANIFEST = OUT / "manifest.json"
WIDTH, HEIGHT = 1200, 630
MAC_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def chrome():
    """Chrome or Chromium: $OWB_CHROME, then the PATH, then the macOS app."""
    for candidate in (os.environ.get("OWB_CHROME"), shutil.which("google-chrome"),
                      shutil.which("chromium"), shutil.which("chromium-browser"), MAC_CHROME):
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def to_jpeg(png, jpg):
    """sips on macOS, ImageMagick elsewhere."""
    if shutil.which("sips"):
        cmd = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", str(png), "--out", str(jpg)]
    elif shutil.which("magick"):
        cmd = ["magick", str(png), "-quality", "82", str(jpg)]
    elif shutil.which("convert"):
        cmd = ["convert", str(png), "-quality", "82", str(jpg)]
    else:
        raise SystemExit("needs sips (macOS) or ImageMagick to make JPEGs")
    subprocess.run(cmd, check=True, capture_output=True)
# Bump when the template changes, so every card is drawn again.
TEMPLATE_VERSION = 5


def font_faces():
    """The site's own @font-face rules (web/style.css), pointed at the font
    files on disk, so a card is drawn in exactly the site's fonts."""
    css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
    faces = "\n".join(re.findall(r"@font-face \{.*?\}", css, re.S))
    return faces.replace("url(/fonts/", f"url({(ROOT / 'web' / 'fonts').as_uri()}/")


def cards():
    """{name: spec} for every card. A spec holds only what the card shows."""
    specs = {"site": {"kind": "site", "title": "The Bible, translated from Hebrew and Greek, "
                                               "with its reasoning shown."}}
    for book, chapter in build_site.chapters():
        records, words = build_site.load_chapter(book, chapter)
        record, verse = build_site.opening(records, chapter)
        mine = set(record["source"]["tokens"])
        english = build_site.opening_verse(records, chapter)
        spec = {"kind": "passage", "eyebrow": build_site.chapter_title(records, book, chapter),
                "title": english}
        if build_site.source_language(book) == "hbo":
            # Hebrew prefixes join their word, so the morphemes run together.
            spec["hebrew"] = "".join(w["text"] + w["after"] for w in words[verse]
                                     if w["id"] in mine).strip()
        else:
            spec["greek"] = " ".join(w["text"] + w["after"].strip() for w in words[verse]
                                     if w["id"] in mine)
        specs[build_site.og_card_chapter(book, chapter)] = spec
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
    faces = font_faces()
    if spec["kind"] == "passage":
        size = 52 if len(spec["title"]) < 90 else 44 if len(spec["title"]) < 140 else 38
        main = (f'<p class="eyebrow">{e(spec["eyebrow"])}</p>'
                f'<p class="quote" style="font-size:{size}px">“{e(spec["title"])}”</p>'
                + (f'<p class="hebrew" lang="hbo" dir="rtl">{e(spec["hebrew"])}</p>' if "hebrew" in spec
                   else f'<p class="greek" lang="grc">{e(spec["greek"])}</p>'))
    elif spec["kind"] == "article":
        size = 64 if len(spec["title"]) < 50 else 54 if len(spec["title"]) < 80 else 46
        main = (f'<p class="eyebrow">Article &middot; {e(spec["eyebrow"])}</p>'
                f'<h1 style="font-size:{size}px">{e(spec["title"])}</h1>'
                f'<p class="summary">{e(spec["summary"])}</p>')
    else:
        main = (f'<h1 style="font-size:58px">{e(spec["title"])}</h1>'
                f'<p class="summary">Every sentence shows the original words, a word-for-word '
                f'gloss, and why each word was chosen.</p>')
    mark = build_site.MARK.replace('class="mark"', 'class="mark" width="56" height="56"')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{faces}
html, body {{ margin: 0; width: {WIDTH}px; height: {HEIGHT}px; overflow: hidden; }}
body {{ box-sizing: border-box; padding: 78px 72px 56px; display: flex; flex-direction: column;
  position: relative; background: #faf6ef; color: #221c15;
  font-family: "Gentium Book Plus", Georgia, serif; }}
body::before {{ content: ""; position: absolute; top: 0; left: 0; right: 0; height: 14px;
  background: linear-gradient(90deg, #3f3d9a 0%, #3f3d9a 55%, #b07d22 100%); }}
.mark rect {{ fill: #3f3d9a; }} .mark path {{ fill: #faf6ef; }}
.mark .quotes {{ fill: #3f3d9a; }}
.brand {{ display: flex; align-items: center; gap: 16px; font-family: "Fraunces", Georgia, serif;
  font-size: 36px; font-weight: 600; letter-spacing: -.01em; }}
.brand em {{ font-style: italic; font-weight: 500; color: #3f3d9a; }}
main {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }}
p, h1 {{ margin: 0; }}
.eyebrow {{ font-family: "Hanken Grotesk", Arial, sans-serif; font-size: 24px; font-weight: 700;
  letter-spacing: .12em; text-transform: uppercase; color: #b07d22; margin-bottom: 18px; }}
h1 {{ font-family: "Fraunces", Georgia, serif; font-weight: 600; line-height: 1.12; letter-spacing: -.02em; }}
.quote {{ line-height: 1.3; }}
.greek {{ font-size: 30px; color: #6e6358; margin-top: 22px; line-height: 1.4; }}
.hebrew {{ font-family: "Noto Serif Hebrew", serif; font-size: 32px; color: #6e6358; margin-top: 22px;
  line-height: 1.5; text-align: right; }}
.summary {{ font-size: 30px; line-height: 1.4; color: #6e6358; margin-top: 20px; }}
footer {{ display: flex; justify-content: space-between; font-family: "Hanken Grotesk", Arial, sans-serif;
  font-size: 22px; font-weight: 500; color: #6e6358; }}
</style></head><body>
<div class="brand">{mark}<span>Open Word <em>Bible</em></span></div>
<main>{main}</main>
<footer><span>openwordbible.org</span><span>Free &middot; public domain &middot; reasoning shown</span></footer>
</body></html>"""


def draw(name, spec, tmp, browser):
    page = tmp / f"{name}.html"
    page.write_text(card_html(spec), encoding="utf-8")
    png = tmp / f"{name}.png"
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={WIDTH},{HEIGHT}", "--virtual-time-budget=5000",
                    f"--screenshot={png}", page.as_uri()],
                   check=True, capture_output=True)
    to_jpeg(png, OUT / f"{name}.jpg")


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
    browser = chrome()
    if todo and not browser:
        raise SystemExit("needs Chrome or Chromium: set OWB_CHROME to its path")
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name in todo:
            draw(name, specs[name], Path(tmp), browser)
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
