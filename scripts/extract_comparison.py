"""Write the verse text of two public-domain reference Bibles to
data/comparison/: the World English Bible (web.json) and the Reina-Valera
1909 (rv1909.json), from seven1m/open-bibles (pinned in sources.lock.json).

When a note names a verse Open Word Bible has not translated yet, the reader
shows that verse from one of these, labelled as a comparison text. The site
is built from these files so a deploy never needs the source clones. They
are never the basis for Open Word Bible wording.

Usage: python3 scripts/extract_comparison.py [--check]

--check exits non-zero if a file is missing or out of date.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import refs  # noqa: E402
from owb.sources import open_bibles  # noqa: E402

EDITIONS = ("web", "rv1909")
OUT = ROOT / "data" / "comparison"


def extract(code):
    """One edition as file text: {"GEN.1.1": "...", ...} in canonical order,
    one verse a line so a change shows as a small diff."""
    verses = open_bibles.load(code)
    order = {c: i for i, c in enumerate(refs.BOOK_CODES)}
    keys = sorted(verses, key=lambda k: (order[k[0]], k[1], k[2]))
    lines = [f"{json.dumps(f'{b}.{c}.{v}')}: {json.dumps(verses[(b, c, v)], ensure_ascii=False)}"
             for b, c, v in keys]
    return "{\n" + ",\n".join(lines) + "\n}\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="fail if a file is missing or stale")
    args = parser.parse_args()
    stale = []
    for code in EDITIONS:
        path = OUT / f"{code}.json"
        text = extract(code)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(path)
        else:
            OUT.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    if stale:
        for path in stale:
            print(f"out of date: {path.relative_to(ROOT)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
