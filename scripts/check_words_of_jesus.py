"""Check that every language marks the words of Jesus alike.

data/words_of_jesus/<BOOK>.json marks a record once for every language
(owb/words_of_jesus.py); each rendering's own quotation marks then say
where his words are. So a missing or extra quotation mark in one language
shows up as red letters there that the others lack: Jesus' saying left in
black, or the narrator's words in red. This compares, for each marked
record and level, how much of each language's rendering is red (the
share of its visible text, settings at their defaults) and flags a
language that differs from the others' median by more than TOLERANCE, or
that has none at all where they have some.

A flagged rendering whose quotation marks need fixing is listed in
docs/review-notes/pending-quote-fixes.jsonl (record id, language, level,
old, new, reason) until the fix is made in content/; such a rendering is
reported as pending, not as a failure. One that only reads differently
(a language that puts "he said" first, so it has one quotation where
English has two) is not flagged: the red share is the same.

    python3 scripts/check_words_of_jesus.py            # exit 1 on new mismatches
    python3 scripts/check_words_of_jesus.py --all      # also list the pending ones
"""
import argparse
import re
import glob
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import markup, words_of_jesus  # noqa: E402

PENDING = ROOT / "docs" / "review-notes" / "pending-quote-fixes.jsonl"
# How far one language's red share may stray from the others' median.
TOLERANCE = 0.3
# Verse and line markers, which a reader does not see.
MARKER = re.compile(r"\\v \d+ ?| ?\\q ?")


def visible(text, ranges):
    """(red characters, all characters) of a rendering as a reader sees it:
    setting spans count by their default's length, markers not at all."""
    hidden = [(s.start, s.end, len(markup.default(s.setting, s.options))) for s in markup.spans(text)]
    marks = [(m.start(), m.end()) for m in MARKER.finditer(text)]

    def length(a, b):
        n = b - a
        for s, e, d in hidden:
            if s >= a and e <= b:
                n -= (e - s) - d
        for s, e in marks:
            if s >= a and e <= b:
                n -= e - s
        return n
    total = length(0, len(text))
    red = sum(length(s, e) for s, e in ranges)
    return red, max(total, 1)


def pending():
    """{(record id, language, level)} listed in the pending fixes."""
    if not PENDING.exists():
        return set()
    out = set()
    for line in PENDING.read_text(encoding="utf-8").splitlines():
        if line.strip():
            e = json.loads(line)
            out.add((e["record"], e["language"], e["level"]))
    return out


def records(book):
    out = {}
    for path in sorted(glob.glob(str(ROOT / "content" / book / "*.json"))):
        for r in json.loads(Path(path).read_text(encoding="utf-8"))["records"]:
            out[r["id"]] = r
    return out


def mismatches():
    """[(book, record id, level, language, its share, median, why)] for every
    rendering whose red share stands apart from the other languages'."""
    found = []
    for path in sorted(words_of_jesus.DIR.glob("*.json")):
        book = path.stem
        marked = json.loads(path.read_text(encoding="utf-8"))["records"]
        recs = records(book)
        for rid, value in marked.items():
            r = recs.get(rid)
            if not r:
                continue
            for level in ("L", "B", "R"):
                share, count = {}, {}
                for lang, levels in r["renderings"].items():
                    if level in levels:
                        ranges = words_of_jesus.ranges(levels[level], value)
                        red, total = visible(levels[level], ranges)
                        share[lang], count[lang] = red / total, len(ranges)
                if len(share) < 3:
                    continue
                med = statistics.median(share.values())
                for lang, s in share.items():
                    others = [n for other, n in count.items() if other != lang]
                    if s == 0 < med:
                        why = "no red letters"
                    elif abs(s - med) > TOLERANCE:
                        why = "more red than the others" if s > med else "less red than the others"
                    elif count[lang] > max(others):
                        # More quotations than any other language: words someone
                        # else says (a gloss in quotation marks), in red.
                        why = "a quotation no other language has"
                    else:
                        continue
                    found.append((book, rid, level, lang, round(s, 2), round(med, 2), why))
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true", help="also list the mismatches already pending a fix")
    args = ap.parse_args(argv)
    known = pending()
    new = 0
    for _book, rid, level, lang, s, med, why in mismatches():
        waiting = (rid, lang, level) in known
        if waiting and not args.all:
            continue
        new += not waiting
        print(f"{'pending ' if waiting else ''}{rid} {lang}.{level}: {why} ({s:.2f} red, others {med:.2f})")
    if new:
        print(f"{new} rendering(s) mark the words of Jesus unlike the other languages; fix the quotation "
              f"marks or list the fix in {PENDING.relative_to(ROOT)}", file=sys.stderr)
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
