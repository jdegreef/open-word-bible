"""Write the MACULA words for every chapter in content/ to data/grc/ (Greek)
and data/hbo/ (Hebrew and Aramaic).

The site is built from these extracts, so a deploy never needs the full
source clones. Each file holds one whole chapter, translated or not, so the
site can tell a part-translated chapter from a complete one: data/grc/JHN.1.json,
data/hbo/GEN.1.json. A Hebrew entry is one morpheme, so a word with a prefix
has two. The extracts are derived from MACULA Greek and MACULA Hebrew (both
CC BY 4.0) and are credited in CREDITS.md.

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
from owb.sources import macula_greek, macula_hebrew, sblgnt  # noqa: E402

FIELDS = ("id", "position", "text", "after", "lemma", "morph", "gloss", "english", "strong")
# lang is H (Hebrew) or A (Aramaic): the two use different verb stems.
HEBREW_FIELDS = FIELDS[:4] + ("transliteration",) + FIELDS[4:] + ("lang",)


def content_refs():
    """Every verse id named by a record in content/."""
    out = set()
    for path in sorted((ROOT / "content").rglob("*.json")):
        for record in json.loads(path.read_text(encoding="utf-8"))["records"]:
            out.update(record["refs"])
    return out


def extracts():
    """Return {relative path: file text} for every chapter in content/."""
    chapters = {(refs.parse(vid).book, refs.parse(vid).chapter) for vid in content_refs()}
    files = {}
    for book, chapter in chapters:
        hebrew = book in refs.OT_CODES
        source, fields = (macula_hebrew, HEBREW_FIELDS) if hebrew else (macula_greek, FIELDS)
        verses = {}
        for t in source.load_tokens(refs.Ref(book, chapter, 1), refs.Ref(book, chapter, 999)):
            verses.setdefault(str(t.ref), []).append({f: getattr(t, f) for f in fields})
        if hebrew:
            data = {"text_id": macula_hebrew.TEXT_ID, "source": "MACULA Hebrew (CC BY 4.0)",
                    "verses": verses}
        else:
            data = {"text_id": sblgnt.TEXT_ID, "source": "MACULA Greek (CC BY 4.0)",
                    "verses": verses}
        folder = "hbo" if hebrew else "grc"
        files[f"data/{folder}/{book}.{chapter}.json"] = (
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
