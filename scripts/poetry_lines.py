"""Where a chapter's poetic lines fall in the Hebrew, beside our renderings.

Hebrew poetry is built from parallel lines (cola), and the Masoretic accents
mark them: in each verse the main dividing accent (atnach; in Psalms,
Proverbs and Job also olev-weyored, which outranks it) splits the verse into
its halves, and lesser disjunctive accents split those again. This script
reads the accents from the word data in data/hbo/ (the WLC text, through
MACULA Hebrew) and prints, for each verse:

    PSA.1.2  2 cola (atnach)
      1  but rather in law of the LORD delight his
            · and in his law he meditates day and night
      ...

The numbered rows are the cola at the main division, given as MACULA's
English glosses of the Hebrew words in Hebrew order (so read them as a
gloss, not as English). A "·" row inside a colon is a lesser division (in the
poetic books revia, tsinnor or shalshelet; elsewhere zaqef, segolta or
shalshelet): a place where a long colon may be broken again. Under that come
the current renderings, one line per poetic line, each level marked with how
many lines it has.

Line breaks are marked in renderings with "\\q " (owb/markup.py, and
"Poetry: lines" in docs/english-style.md). This script never decides wording
and never places a break by itself except with --fill, a first pass that
puts a break after the ";" or ":" of a verse's text at a level where the
English has exactly one ";" or ":" and the Hebrew has exactly two cola. A
person or agent places the rest, reading the printout.

Usage:
    python3 scripts/poetry_lines.py PSA 1             # one chapter
    python3 scripts/poetry_lines.py PSA 1-3 23        # several
    python3 scripts/poetry_lines.py ISA 40 --lang es  # another language's renderings
    python3 scripts/poetry_lines.py PSA 1 --fill      # first pass: write easy breaks

Accents are named by Unicode code point here; Hebrew text is only ever read
from the data, never typed.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import markup, refs  # noqa: E402

# Books accented with the poetic ("three books") system. Job's prose frame
# (1:1-3:1, 42:7-17) is accented as prose, but its few verses are left to
# the reader of this printout.
POETIC_BOOKS = {"PSA", "PRO", "JOB"}

ATNACH = "֑"
SEGOLTA = "֒"
SHALSHELET = "֓"
ZAQEF_QATAN = "֔"
ZAQEF_GADOL = "֕"
REVIA = "֗"
TSINNOR = "֘"       # zarqa in prose; tsinnor in the poetic books
OLE = "֫"           # with merkha (yored): olev-weyored
MERKHA = "֥"
MAHAPAKH = "֤"

NAMES = {ATNACH: "atnach", OLE: "olev-weyored", SEGOLTA: "segolta", SHALSHELET: "shalshelet",
         ZAQEF_QATAN: "zaqef", ZAQEF_GADOL: "zaqef gadol", REVIA: "revia", TSINNOR: "tsinnor"}

# The main division (level 1) and the lesser one (level 2), per system.
MAJOR = {"poetic": (OLE, ATNACH), "prose": (ATNACH,)}
MINOR = {"poetic": (REVIA, TSINNOR, SHALSHELET),
         "prose": (SEGOLTA, ZAQEF_QATAN, ZAQEF_GADOL, SHALSHELET)}

PUNCT = re.compile(r"[;:]")


def words(verse_rows):
    """A verse's words: [(text of all its morphemes, english gloss)], in order.
    MACULA gives a word with a prefix as two or more rows (same position)."""
    out = []
    for row in verse_rows:
        if out and out[-1][0] == row["position"]:
            out[-1][1] += row["text"]
            out[-1][2].append(row["english"] or "")
        else:
            out.append([row["position"], row["text"], [row["english"] or ""]])
    return [(text, " ".join(e for e in english if e)) for _, text, english in out]


def divisions(book, verse_rows):
    """For each word of a verse, the level of the division after it: 1 (main),
    2 (lesser) or 0. Returns (levels, names of the main dividers found)."""
    system = "poetic" if book in POETIC_BOOKS else "prose"
    ws = words(verse_rows)
    levels, names = [0] * len(ws), []
    for i, (text, _) in enumerate(ws[:-1]):     # the verse's end needs no mark
        accents = set(text)
        if OLE in accents:
            # Olev-weyored divides after the word with yored (merkha); on a
            # short word the ole stands on the word before it.
            at = i if MERKHA in accents else min(i + 1, len(ws) - 2)
            levels[at] = 1
            names.append(NAMES[OLE])
        elif ATNACH in accents:
            levels[i] = 1
            names.append(NAMES[ATNACH])
        elif any(a in accents for a in MINOR[system]):
            # Tsinnorit (a conjunctive form of the same sign) shares a word
            # with merkha or mahapakh; tsinnor stands alone.
            if TSINNOR in accents and (MERKHA in accents or MAHAPAKH in accents) and not (
                    accents & (set(MINOR[system]) - {TSINNOR})):
                continue
            levels[i] = max(levels[i], 2)
    return levels, names


def cola(book, verse_rows):
    """[[segment gloss, ...] per colon]: the cola at the main division, each a
    list of its segments at the lesser one."""
    levels, names = divisions(book, verse_rows)
    out, colon, seg = [], [], []
    for (_, gloss), level in zip(words(verse_rows), levels + [1]):
        if gloss:
            seg.append(gloss)
        if level:
            colon.append(" ".join(seg))
            seg = []
        if level == 1:
            out.append(colon)
            colon = []
    if seg or colon:
        out.append(colon + ([" ".join(seg)] if seg else []))
    return out, names


def verse_parts(record, text):
    """{verse number: (start, end)} of each verse's text in a rendering."""
    first = refs.parse(record["refs"][0]).verse
    spans, verse, pos = {}, first, 0
    for m in markup.VERSE.finditer(text):
        spans[verse] = (pos, m.start())
        verse, pos = int(m[1]), m.end()
    spans[verse] = (pos, len(text))
    return spans


def fill(text):
    """text (one verse's part) with a break after its only ";" or ":", or None."""
    if markup.is_poetry(text):
        return None
    marks = [m for m in PUNCT.finditer(text)
             if not any(s.start <= m.start() < s.end for s in markup.spans(text))]
    if len(PUNCT.findall(text)) != 1 or len(marks) != 1:
        return None
    at = marks[0].end()
    head, tail = text[:at], text[at:].lstrip()
    if not tail.strip() or tail.startswith("\\v"):
        return None
    return head + " \\q " + tail


def chapters(arg):
    a, _, b = arg.partition("-")
    return range(int(a), int(b or a) + 1)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog="See the module docstring for the output format.")
    p.add_argument("book", help="book code, e.g. PSA")
    p.add_argument("chapters", nargs="+", help="chapter numbers or ranges, e.g. 1 3-5")
    p.add_argument("--lang", default="en", help="renderings to show and fill (default en)")
    p.add_argument("--fill", action="store_true",
                   help="write a break where the Hebrew has two cola and a level's text one ';' or ':'")
    args = p.parse_args(argv)
    book = args.book.upper()
    for arg in args.chapters:
        for chapter in chapters(arg):
            show(book, chapter, args.lang, args.fill)


def show(book, chapter, lang, write):
    path = ROOT / "content" / book / f"{book}.{chapter}.json"
    words_path = ROOT / "data" / "hbo" / f"{book}.{chapter}.json"
    if not path.exists() or not words_path.exists():
        print(f"{book} {chapter}: not drafted (no {path.relative_to(ROOT)} or word data)")
        return
    doc = json.loads(path.read_text(encoding="utf-8"))
    hebrew = json.loads(words_path.read_text(encoding="utf-8"))["verses"]
    filled = []
    print(f"=== {book} {chapter} ({lang})")
    for record in doc["records"]:
        levels = record["renderings"].get(lang)
        mine = set(record["source"]["tokens"])
        for vid in record["refs"]:
            ref = refs.parse(vid)
            rows = [w for w in hebrew.get(vid, []) if w["id"] in mine]
            parts, names = cola(book, rows)
            how = f" ({', '.join(names)})" if names else ""
            print(f"\n{vid}  {len(parts)} {'colon' if len(parts) == 1 else 'cola'}{how}")
            for n, colon in enumerate(parts, 1):
                print(f"  {n}  {colon[0]}")
                for seg in colon[1:]:
                    print(f"        · {seg}")
            if not levels:
                print(f"  (no {lang} rendering yet)")
                continue
            for level in "LBR":
                text = levels[level]
                start, end = verse_parts(record, text)[ref.verse]
                part = text[start:end]
                if write and len(parts) == 2:
                    new = fill(part.strip())
                    if new:
                        lead = part[:len(part) - len(part.lstrip())]
                        trail = part[len(part.rstrip()):]
                        levels[level] = text[:start] + lead + new + trail + text[end:]
                        part = lead + new + trail
                        filled.append(f"{vid} {level}")
                lines = markup.split_lines(part.strip())
                print(f"  {level} [{len(lines)}]  " + "\n         ".join(lines))
    if write:
        if filled:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nfilled {len(filled)}: {', '.join(filled) or 'none'}")


if __name__ == "__main__":
    main()
