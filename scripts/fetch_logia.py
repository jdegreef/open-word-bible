"""Refresh data/logia_coverage.json: which chapters and verses have
commentary on Logia (logia.faith), so the chapter and verse pages can link
to what the church has said about them.

    python3 scripts/fetch_logia.py                 from logia.faith
    python3 scripts/fetch_logia.py PATH            from a Logia build's site/api/v1/coverage.json

Logia is a separate site (github.com/jdegreef/logia) whose Bible text is
this translation, numbered as this translation numbers it. The snapshot is
committed so the build never depends on Logia being up; run this again when
Logia adds a book.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "logia_coverage.json"
SOURCE = "https://logia.faith/api/v1/coverage.json"


def main(argv):
    if argv:
        data = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    else:
        with urllib.request.urlopen(SOURCE, timeout=60) as r:
            data = json.load(r)
    # Only the counts: Logia's addresses follow this site's (/jhn/3/, /jhn/3/16/).
    chapters = {k: {"voices": v["voices"], "verses": {n: x["voices"] for n, x in v["verses"].items()}}
                for k, v in sorted(data.items())}
    about = ("What Logia (logia.faith) holds on each chapter: written by scripts/fetch_logia.py"
             f" from {SOURCE}; don't edit by hand.")
    text = json.dumps({"about": about, "chapters": chapters}, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(text + "\n", encoding="utf-8")
    verses = sum(len(v["verses"]) for v in chapters.values())
    print(f"{OUT.relative_to(ROOT)}: {len(chapters)} chapters, {verses} verses")


if __name__ == "__main__":
    main(sys.argv[1:])
