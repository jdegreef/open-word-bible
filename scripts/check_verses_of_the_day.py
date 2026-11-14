"""Check that verses of the day read on their own.

    python3 scripts/check_verses_of_the_day.py            # data/verse_of_the_day.json
    python3 scripts/check_verses_of_the_day.py JHN.3.16 PSA.23.1 ...
    python3 scripts/check_verses_of_the_day.py --show     # every verse's English

The home page shows a verse of the day as build_site.verses_of_the_day does:
the first record that holds the verse, Balanced, at the default settings, in
the page's language. Two things make a verse unusable, and fail the check:

- it is not drafted, or is numbered otherwise in English Bibles
  (owb/versification.py), so the reference a reader sees would find other
  words in their own Bible;
- in some language it does not end a sentence (tests/test_site.py).

Others make it read less well on its own, and are reported as notes; with
--strict they fail too. In every language its record is drafted in:

- one record holds it, and that record is this verse alone, so the page
  shows the whole verse and no sentence is cut;
- the sentence before it ends, so it does not start mid-sentence;
- it does not start with a word that leans on what came before
  ("Therefore", "For", "And", ...);
- its quotation marks are balanced, so it does not open or close a speech
  that runs on beyond it.

The list's first 71 verses were chosen by hand before this check, and some
keep a well-known verse that leans on the one before (John 3:16, "For God
..."); every verse added since passes --strict.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from owb import refs, versification  # noqa: E402

NBSP = " "
# A sentence's end, as tests/test_site.py checks a verse of the day's.
ENDS = re.compile("[.?!።।。？！](?:[”’»」』]|" + NBSP + "»)?$")
# The sentence before may also close a bracketed passage (John 8:11).
ENDED = re.compile("[.?!።।。？！](?:[”’»」』]|" + NBSP + r"»)?[\])]?$")
# Words that tie a sentence to the one before it, by language (lower case,
# matched at the start after any opening quotation mark).
LEANS = {
    "en": ("for ", "therefore", "so ", "and ", "then ", "now ", "because", "thus", "but ", "yet ",
           "that ", "this is why", "for this reason", "wherefore", "since ", "or ", "nor ", "likewise",
           "also ", "moreover", "furthermore", "in the same way", "after this", "after these"),
    "es": ("porque", "pues", "por tanto", "por eso", "así que", "pero ", "y ", "entonces", "también"),
    "fr": ("car ", "donc", "c’est pourquoi", "ainsi", "mais ", "et ", "alors"),
    "pt": ("porque", "pois ", "portanto", "por isso", "assim", "mas ", "e ", "então", "também"),
    "sw": ("kwa maana", "kwa kuwa", "kwa hiyo", "kwa sababu", "basi", "lakini", "na ", "ndipo"),
    "ru": ("ибо", "потому", "итак", "поэтому", "но ", "и ", "тогда", "также", "так "),
    "uk": ("бо ", "тому", "отже", "але ", "і ", "й ", "тоді", "також", "так "),
    "vi": ("vì ", "vậy", "cho nên", "nhưng", "và ", "rồi ", "bởi vậy", "thế nên"),
}
OPENING = "“‘«„「『\"' "
# Quotation marks that open and close, by language.
QUOTES = {"ru": ("«»",), "uk": ("«»",), "ja": ("「」", "『』")}
DEFAULT_QUOTES = ("“”", "«»")


def balanced(text, lang):
    return all(text.count(a) == text.count(b) for a, b in QUOTES.get(lang, DEFAULT_QUOTES))


def same_number_in_english(vid):
    ref = refs.parse(vid)
    return versification.to_english(ref) == (ref,) and versification.to_source(ref) == (ref,)


def before(book, chapter, record):
    """The record read just before this one: in its chapter, or the last of
    the previous chapter; None at a book's start."""
    rs = build_site.chapter_records(book, chapter)
    i = next(i for i, r in enumerate(rs) if r["id"] == record["id"])
    if i:
        return rs[i - 1]
    if chapter > 1:
        prev = build_site.chapter_records(book, chapter - 1)
        return prev[-1] if prev else None
    return None


def check(vid):
    """(errors, notes) for one verse id."""
    ref = refs.parse(vid)
    if ref.book not in build_site.BOOK_CHAPTERS:
        return [f"no book {ref.book}"], []
    holding = [r for r in build_site.chapter_records(ref.book, ref.chapter) if vid in r["refs"]]
    if not holding:
        return ["not drafted"], []
    errors, notes = [], []
    if not same_number_in_english(vid):
        errors.append("numbered otherwise in English Bibles")
    if len(holding) > 1:
        notes.append(f"{len(holding)} records hold it: only the first is shown")
    r = holding[0]
    if r["refs"] != [vid]:
        notes.append(f"its sentence runs over {r['refs'][0]}–{r['refs'][-1]}")
    prev = before(ref.book, ref.chapter, r)
    for lang in r["renderings"]:
        text = build_site.verse_text(r, vid, lang)
        if not ENDS.search(text):
            errors.append(f"{lang}: does not end a sentence")
        if prev is not None and lang in prev["renderings"]:
            if not ENDED.search(build_site.plain(prev["renderings"][lang]["B"])):
                notes.append(f"{lang}: the sentence before it runs on into it")
        start = text.lstrip(OPENING).lower()
        lean = next((w for w in LEANS.get(lang, ()) if start.startswith(w)), None)
        if lean:
            notes.append(f"{lang}: starts with “{lean.strip()}”")
        if not balanced(text, lang):
            notes.append(f"{lang}: unbalanced quotation marks")
    return errors, notes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("refs", nargs="*", help="verse ids (default: data/verse_of_the_day.json)")
    ap.add_argument("--strict", action="store_true", help="fail on notes too")
    ap.add_argument("--show", action="store_true", help="print each verse's English and verdict")
    args = ap.parse_args(argv)
    vids = args.refs or json.loads((ROOT / "data" / "verse_of_the_day.json").read_text(encoding="utf-8"))["refs"]
    failed = 0
    for vid in vids:
        errors, notes = check(vid)
        bad = bool(errors or (args.strict and notes))
        failed += bad
        found = errors + notes
        if args.show:
            r = next((r for r in build_site.chapter_records(*refs.parse(vid)[:2]) if vid in r["refs"]), None)
            en = build_site.verse_text(r, vid, "en") if r else ""
            verdict = "FAIL" if bad else "note" if found else "ok  "
            print(f"{verdict} {vid}\t{en}" + (f"\t[{'; '.join(found)}]" if found else ""))
        elif found:
            print(f"{'FAIL' if bad else 'note'} {vid}: {'; '.join(found)}")
    if not args.show:
        print(f"{len(vids) - failed} of {len(vids)} verses pass{' strictly' if args.strict else ''}.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
