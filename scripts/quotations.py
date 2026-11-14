"""Old Testament quotations in the New: does our New Testament echo our Old?

Pairs each explicit quotation in data/quotations.json (New Testament verses,
Old Testament verses, and whether the Greek follows the Hebrew, the
Septuagint, or neither closely) with the sentence records on both sides, and
compares their wording in each language and level. It also finds the
quotation formulas in the Greek ("it is written", "that it might be
fulfilled", "the scripture says"), matched by Strong's number and parsing in
data/grc/, so that a formula with no curated quotation shows up.

Each quotation is classed:

  a  the Greek follows the Hebrew: our New Testament should echo our Old
     Testament wording where it reads naturally; a low overlap is flagged;
  b  the New Testament follows the Septuagint where it differs from the
     Hebrew: the difference stays, and a meaning decision with a footnote
     should explain it (flagged when none does);
  c  a loose quotation, a composite or an allusion: left alone.

Usage:
    python3 scripts/quotations.py                 # summary
    python3 scripts/quotations.py --write docs/review-notes/nt-quotations.md
    python3 scripts/quotations.py --language es --level B
"""
import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import languages, markup, refs, versification  # noqa: E402

DATA = ROOT / "data" / "quotations.json"
LEVELS = ("L", "B", "R")

# Quotation formulas, by Strong's number and parsing (no Greek typed).
WRITE, FULFIL, SCRIPTURE = "1125", "4137", "1124"
SAY = {"3004", "2036", "2046", "3004a"}
# A quotation that follows the Hebrew is flagged when its sentences share
# less than this part of their content words with the Old Testament
# sentences and no run of ECHO_RUN words.
ECHO_THRESHOLD = 0.5
ECHO_RUN = 5
CHANGES = "## Changes"

STOP = set("""a an the and or but of to in on at by for from with as is are was were be been
being it its it's this that these those he him his she her they them their we us our you your
i me my not no so then than there what which who whom whose will shall would should may might
can could do does did have has had into out up over under upon all also if when one ones
said says say says let let's because like just very""".split())
_WORD = re.compile(r"[^\W_]+(?:'[^\W_]+)*")
# Explaining the Septuagint, in a meaning decision's choice or reason.
SEPTUAGINT = re.compile(r"Septuagint|Greek Old Testament|Greek translation of|"
                        r"\(\d+:\d+(?:-\d+)? Greek\)|\(Greek\)|in Greek", re.IGNORECASE)


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))["quotations"]


def verse_range(text):
    """'MAT.4.15-16' -> [Ref MAT.4.15, Ref MAT.4.16]; 'GEN.1.1' -> [Ref]."""
    m = re.fullmatch(r"([1-3]?[A-Z]{2,3})\.(\d+)\.(\d+)(?:-(\d+))?", text)
    if not m:
        raise ValueError(f"bad reference: {text!r}")
    book, chapter, first = m[1], int(m[2]), int(m[3])
    last = int(m[4] or first)
    return [refs.Ref(book, chapter, v) for v in range(first, last + 1)]


def old_testament_verses(text):
    """Our verses (Hebrew numbering) for an English-numbered reference."""
    out = []
    for ref in verse_range(text):
        for own in versification.to_source(ref):
            if own not in out:
                out.append(own)
    return out


@lru_cache(maxsize=None)
def book_records(book):
    """{verse id: [record, ...]} for a book, records in file order."""
    out = {}
    folder = ROOT / "content" / book
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        for record in json.loads(path.read_text(encoding="utf-8"))["records"]:
            for vid in record["refs"]:
                out.setdefault(vid, []).append(record)
    return out


def records_for(verses):
    """The records holding any of these verses, each once, in order."""
    out, seen = [], set()
    for ref in verses:
        for record in book_records(ref.book).get(str(ref), []):
            if record["id"] not in seen:
                seen.add(record["id"])
                out.append(record)
    return out


def plain(rendering):
    text = markup.flat(markup.VERSE.sub(" ", markup.render(rendering)))
    return text.replace("[", "").replace("]", "")


def words(text, language):
    found = [w.lower() for w in _WORD.findall(plain(text).replace("’", "'"))]
    if language == "en":
        return [w for w in found if w not in STOP]
    return [w for w in found if len(w) > 3]


def text_of(records, language, level):
    return " ".join(r["renderings"].get(language, {}).get(level, "") for r in records)


def echo(nt_records, ot_records, language, level):
    """(share, run): the share of the Old Testament wording's content words
    that the New Testament sentences use, and the longest run of words (all
    words, in order) the two share. None where either side has no text."""
    nt_text, ot_text = text_of(nt_records, language, level), text_of(ot_records, language, level)
    if not nt_text.strip() or not ot_text.strip():
        return None
    nt, ot = set(words(nt_text, language)), set(words(ot_text, language))
    if not ot or not nt:
        return None
    # A quotation is often part of its verse, and its sentence holds more
    # than the quotation, so the shared words are measured against the
    # smaller side.
    share = len(nt & ot) / min(len(nt), len(ot))
    a = [w.lower() for w in _WORD.findall(plain(nt_text))]
    b = [w.lower() for w in _WORD.findall(plain(ot_text))]
    return round(share, 2), longest_run(a, b)


def longest_run(a, b):
    best, prev = 0, {}
    for x in a:
        cur = {}
        for j, y in enumerate(b):
            if x == y:
                cur[j] = prev.get(j - 1, 0) + 1
                best = max(best, cur[j])
        prev = cur
    return best


def septuagint_note(records):
    """The meaning decisions that explain a Greek Old Testament reading."""
    return [(r["id"], d) for r in records for d in r.get("decisions") or []
            if d.get("layer") == "meaning" and SEPTUAGINT.search(d.get("choice", "") + " " + d.get("reason", ""))]


def classify(quotation):
    return {"hebrew": "a", "septuagint": "b"}.get(quotation["kind"], "c")


def pair(quotation):
    nt = records_for(verse_range(quotation["nt"]))
    ot = records_for(old_testament_verses(quotation["ot"]))
    return nt, ot


def survey(language="en", level="B"):
    """One row per quotation."""
    rows = []
    for q in load():
        nt, ot = pair(q)
        cls = classify(q)
        row = {"nt": q["nt"], "ot": q["ot"], "kind": q["kind"], "class": cls,
               "nt_records": [r["id"] for r in nt], "ot_records": [r["id"] for r in ot],
               "echo": {}, "flag": "", "note": q.get("note", "")}
        for lang in languages.READING:
            e = echo(nt, ot, lang, level)
            if e:
                row["echo"][lang] = e
        main = row["echo"].get(language)
        if not nt or not ot:
            row["flag"] = "not drafted"
        elif cls == "a" and main and main[0] < ECHO_THRESHOLD and main[1] < ECHO_RUN:
            # A reviewed difference ("note" in the data) is kept, not flagged.
            row["flag"] = "kept" if q.get("note") else "differs"
        elif cls == "b":
            notes = septuagint_note(nt)
            row["septuagint_notes"] = [f"{rid} {d['id']}" + (" (footnote)" if d.get("footnote") else "")
                                       for rid, d in notes]
            if not any(d.get("footnote") for _, d in notes):
                row["flag"] = "no footnote" if notes else "no note"
        rows.append(row)
    return rows


@lru_cache(maxsize=None)
def _words_of(book, chapter):
    path = ROOT / "data" / "grc" / f"{book}.{chapter}.json"
    return json.loads(path.read_text(encoding="utf-8"))["verses"] if path.exists() else {}


def formula(words_of_verse):
    """The quotation formula in one verse's Greek words, or None: "written"
    (perfect passive of the verb write), "fulfilled" (aorist passive
    subjunctive of fulfil, as in "that it might be fulfilled"), or
    "scripture" (the noun scripture beside a verb of saying)."""
    strongs = {w.get("strong") for w in words_of_verse}
    for w in words_of_verse:
        morph = w.get("morph", "")
        if w.get("strong") == WRITE and (morph.startswith("V-RPI") or morph.startswith("V-RPP")
                                         or morph.startswith("V-LPI")):
            return "written"
        if w.get("strong") == FULFIL and morph.startswith("V-APS"):
            return "fulfilled"
    if SCRIPTURE in strongs and strongs & SAY:
        return "scripture"
    return None


NT_BOOKS = ["MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH", "PHP", "COL",
            "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS", "1PE", "2PE", "1JN", "2JN",
            "3JN", "JUD", "REV"]


def formula_sites():
    """[(verse id, formula)] for every New Testament verse with a formula."""
    out = []
    for path in sorted((ROOT / "data" / "grc").glob("*.json")):
        book, chapter = path.stem.split(".")
        if book not in NT_BOOKS:
            continue
        for vid, ws in _words_of(book, int(chapter)).items():
            f = formula(ws)
            if f:
                out.append((vid, f))
    return sorted(out, key=lambda x: refs.parse(x[0]).sort_key())


def covered(vid, quotations):
    """Whether a formula at vid introduces a curated quotation (the same
    verse or the next three)."""
    ref = refs.parse(vid)
    for q in quotations:
        for r in verse_range(q["nt"]):
            if r.book == ref.book and r.chapter == ref.chapter and 0 <= r.verse - ref.verse <= 3:
                return True
    return False


def report(language="en", level="B"):
    rows = survey(language, level)
    qs = load()
    sites = formula_sites()
    loose = [s for s in sites if not covered(s[0], qs)]
    counts = {c: sum(r["class"] == c for r in rows) for c in "abc"}
    flags = {}
    for r in rows:
        if r["flag"]:
            flags[r["flag"]] = flags.get(r["flag"], 0) + 1
    out = ["# Old Testament quotations in the New Testament", "",
           "Written by `python3 scripts/quotations.py --write` from `data/quotations.json` "
           f"({len(rows)} curated quotations) and the content. Level compared: {level}. "
           "`echo` is the share of content words the New Testament and Old Testament sentences "
           "have in common (of the smaller side), then the longest run of words they share; whole "
           "sentences are compared, so a low share is a prompt to look, not a verdict. A quotation "
           "that follows the Hebrew is flagged `differs` below a share of "
           f"{ECHO_THRESHOLD} with no run of {ECHO_RUN} words, or `kept` where the data notes why.", "",
           f"Classes: (a) follows the Hebrew {counts['a']}; (b) follows the Septuagint where it "
           f"differs {counts['b']}; (c) loose, composite or allusive {counts['c']}. "
           "Flags: " + ", ".join(f"{k} {v}" for k, v in sorted(flags.items())) + ".", ""]
    out += ["## Quotations", "",
            f"| New Testament | Old Testament | Class | Echo ({language}) | Flag | Note | Other languages (share) |",
            "|---|---|---|---|---|---|---|"]
    for r in rows:
        e = r["echo"].get(language)
        others = ", ".join(f"{k} {v[0]}" for k, v in r["echo"].items() if k != language)
        out.append(f"| {r['nt']} | {r['ot']} | {r['class']} | "
                   f"{'%s / %s' % e if e else ''} | {r['flag']} | {r['note']} | {others} |")
    out += ["", "## Formulas with no curated quotation", "",
            f"{len(sites)} verses have a quotation formula in the Greek; these {len(loose)} have "
            "no curated quotation within three verses (many point to scripture in general, or "
            "to a saying without a single source):", "",
            ", ".join(f"{vid} ({f})" for vid, f in loose), ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--language", default="en")
    ap.add_argument("--level", default="B", choices=LEVELS)
    ap.add_argument("--write", metavar="PATH", help="write the Markdown report")
    args = ap.parse_args(argv)
    text = report(args.language, args.level)
    if args.write:
        path = Path(args.write)
        # A hand-written section from "## Changes" on is kept.
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        kept = old[old.find(CHANGES):] if CHANGES in old else ""
        path.write_text(text + ("\n" + kept if kept else ""), encoding="utf-8")
    else:
        rows = survey(args.language, args.level)
        for r in rows:
            if r["flag"]:
                print(r["nt"], r["ot"], r["class"], r["flag"], r["echo"].get(args.language))
    return 0


if __name__ == "__main__":
    sys.exit(main())
