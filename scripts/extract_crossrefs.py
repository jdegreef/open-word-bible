"""Write data/crossrefs/<BOOK>.json, the cross-references shown in the
reader's margin (owb/crossrefs.py), from OpenBible.info's list as pinned in
sources.lock.json, moved to our verse numbering.

The files are checked in so a deploy never needs the source clones.

Usage: OWB_VENDOR=<sources dir> python3 scripts/extract_crossrefs.py [--check]

--check exits non-zero if a file is missing or out of date.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import crossrefs, refs  # noqa: E402
from owb.sources import LOCK, macula_hebrew, openbible, sblgnt  # noqa: E402


def our_verses():
    """Every verse our sources have: the WLC's (MACULA Hebrew) and SBLGNT's."""
    out = set(macula_hebrew.verses())
    for code, _ in refs.NT_BOOKS:
        out |= set(sblgnt.load_book(code))
    return out


def build():
    """{path: text} for every book."""
    table = crossrefs.select(openbible.load(), our_verses())
    lock = LOCK[openbible.NAME]
    source = (f"OpenBible.info cross references (CC BY), {openbible.PATH} in "
              f"{lock['repo'].removeprefix('https://github.com/')} at {lock['commit']}")
    return {crossrefs.DATA / f"{code}.json": crossrefs.dumps(code, table, source)
            for code in refs.BOOK_CODES}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit non-zero if a file is out of date")
    args = ap.parse_args(argv)
    stale = []
    for path, text in build().items():
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            continue
        if args.check:
            stale.append(path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    for path in stale:
        print(f"out of date: {path.relative_to(ROOT)} (run scripts/extract_crossrefs.py)", file=sys.stderr)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
