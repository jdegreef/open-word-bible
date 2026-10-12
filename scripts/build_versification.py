"""Write data/versification.json, the Hebrew <-> English verse numbering
table (see owb/versification.py), from the Open Scriptures Hebrew Bible's
wlc/VerseMap.xml and the verses of MACULA Hebrew.

The table is checked in so the API and the site never need the source
clones. tests/test_versification.py checks it is up to date.

Usage: OWB_VENDOR=<sources dir> python3 scripts/build_versification.py [--check]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import versification  # noqa: E402
from owb.sources import LOCK, macula_hebrew, read_text  # noqa: E402


def build():
    """The text data/versification.json should have."""
    table, absent = versification.derive(read_text("morphhb", versification.VERSE_MAP),
                                         set(macula_hebrew.verses()))
    return versification.dumps(table, absent, LOCK["morphhb"]["commit"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit non-zero if the file is out of date")
    args = ap.parse_args(argv)
    text = build()
    path = versification.DATA
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == text:
        return 0
    if args.check:
        print(f"out of date: {path.relative_to(ROOT)} (run scripts/build_versification.py)")
        return 1
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
