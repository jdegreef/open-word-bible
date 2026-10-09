"""Write the MACULA Greek words for every verse in content/ to data/grc/.

The site is built from these extracts, so a deploy never needs the full
source clones. Each file holds one chapter: data/grc/JHN.1.json. The extracts
are derived from MACULA Greek (CC BY 4.0) and are credited in CREDITS.md.

Usage: python3 scripts/extract_tokens.py [--check]

--check exits non-zero if any extract is missing or out of date.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import refs  # noqa: E402
from owb.sources import macula_greek, sblgnt  # noqa: E402

FIELDS = ("id", "position", "text", "after", "lemma", "morph", "gloss", "english", "strong")


def content_refs():
    """Every verse id named by a record in content/."""
    out = set()
    for path in sorted((ROOT / "content").rglob("*.json")):
        for record in json.loads(path.read_text(encoding="utf-8"))["records"]:
            out.update(record["refs"])
    return out


def extracts():
    """Return {relative path: file text} for every chapter in content/."""
    by_chapter = {}
    for vid in content_refs():
        ref = refs.parse(vid)
        by_chapter.setdefault((ref.book, ref.chapter), []).append(ref)
    files = {}
    for (book, chapter), verse_refs in by_chapter.items():
        verses = {}
        for ref in sorted(verse_refs, key=lambda r: r.verse):
            verses[str(ref)] = [{f: getattr(t, f) for f in FIELDS}
                                for t in macula_greek.load_tokens(ref)]
        data = {"text_id": sblgnt.TEXT_ID, "source": "MACULA Greek (CC BY 4.0)",
                "verses": verses}
        files[f"data/grc/{book}.{chapter}.json"] = (
            json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    stale = []
    for rel, text in sorted(extracts().items()):
        path = ROOT / rel
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == text:
            continue
        if args.check:
            stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {rel}")
    if stale:
        print("out of date: " + ", ".join(stale) + " (run scripts/extract_tokens.py)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
