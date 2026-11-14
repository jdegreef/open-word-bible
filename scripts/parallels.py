"""Parallel passages: where the source repeats itself, does the translation?

Some passages are told twice: David's song in 2 Samuel 22 and Psalm 18, the
reigns of Samuel-Kings again in Chronicles, Isaiah 36-39 and 2 Kings 18-20,
the list of returning exiles in Ezra 2 and Nehemiah 7, the same scene in two
or three Gospels. PARALLELS below lists the pairs. For each pair this script
lines up the verses by their source words (lemma sequences from data/hbo/
and data/grc/), then, for every language, reports

  1. layout: one side of a verse pair is set in poetic lines and the other is
     prose (a record is lined in a language when any of its levels has \\q);
  2. wording: the source of the two verses is the same word for word (the
     same lemmas in the same order) but a rendering differs, after settings,
     line and verse markers, brackets, case and punctuation are set aside.

Differences where the source differs are left alone: the report never asks
for two different texts to be made to read alike. A wording difference with
identical source is a question for a reviewer, not an error: context can
justify it, and the earlier draft may be the better one.

    python3 scripts/parallels.py                    print the summary
    python3 scripts/parallels.py --write            write docs/review-notes/parallels.md
    python3 scripts/parallels.py --pair "PSA 14"    one pair (matched on its name)

Original-language text is only ever read from the data, never typed here.
"""
import argparse
import difflib
import functools
import json
import re
import unicodedata
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import markup, refs  # noqa: E402

REPORT = ROOT / "docs" / "review-notes" / "parallels.md"
LANGS = ("en", "es", "fr", "sw", "vi", "ko", "pt", "am", "hi", "ru", "uk", "ja")
LEVELS = ("L", "B", "R")
# Verses below this lemma similarity are not paired. The Gospels retell a
# scene in their own words, so their verses pair at a lower bar.
SIMILAR = {"hbo": 0.5, "grc": 0.3}
CLOSE = 0.75          # a pair this similar but not identical is listed as close

# (name, passage, passage): a passage is "BOOK c:v-c:v" or "BOOK c:v-v".
PARALLELS = [
    # Psalms told twice, and the songs of the history books
    ("David's song", "2SA 22:1-51", "PSA 18:1-51"),
    ("The fool says there is no God", "PSA 14:1-7", "PSA 53:1-7"),
    ("Hurry to help me", "PSA 40:14-18", "PSA 70:1-6"),
    ("My heart is steadfast", "PSA 57:8-12", "PSA 108:1-6"),
    ("With God we will do valiantly", "PSA 60:7-14", "PSA 108:7-14"),
    ("David's thanksgiving: Psalm 105", "1CH 16:8-22", "PSA 105:1-15"),
    ("David's thanksgiving: Psalm 96", "1CH 16:23-33", "PSA 96:1-13"),
    ("David's thanksgiving: Psalm 106", "1CH 16:34-36", "PSA 106:1-48"),
    # Prophets and history
    ("Hezekiah, Sennacherib and Isaiah", "ISA 36:1-39:8", "2KI 18:13-20:19"),
    ("The fall of Jerusalem", "2KI 24:18-25:30", "JER 52:1-34"),
    ("The returning exiles", "EZR 2:1-70", "NEH 7:6-73"),
    # Samuel-Kings and Chronicles
    ("Saul's death", "1SA 31:1-13", "1CH 10:1-12"),
    ("David king over Israel; Jerusalem taken", "2SA 5:1-10", "1CH 11:1-9"),
    ("David's mighty men", "2SA 23:8-39", "1CH 11:10-41"),
    ("Hiram; David's sons; the Philistines defeated", "2SA 5:11-25", "1CH 14:1-17"),
    ("The ark and Uzzah", "2SA 6:1-11", "1CH 13:5-14"),
    ("God's covenant with David", "2SA 7:1-29", "1CH 17:1-27"),
    ("David's victories", "2SA 8:1-18", "1CH 18:1-17"),
    ("The Ammonite war", "2SA 10:1-19", "1CH 19:1-19"),
    ("The census and the threshing floor", "2SA 24:1-25", "1CH 21:1-27"),
    ("Solomon's prayer at the dedication", "1KI 8:12-53", "2CH 6:1-42"),
    ("The LORD appears to Solomon again", "1KI 9:1-9", "2CH 7:11-22"),
    ("The queen of Sheba; Solomon's wealth", "1KI 10:1-29", "2CH 9:1-28"),
    ("Micaiah and the two kings", "1KI 22:1-35", "2CH 18:1-34"),
    ("Josiah and the book of the law", "2KI 22:1-23:3", "2CH 34:1-32"),
    # The Gospels: the triple tradition (a curated set) and two double ones
    ("Feeding of the 5,000 (Matthew, Mark)", "MAT 14:13-21", "MRK 6:32-44"),
    ("Feeding of the 5,000 (Matthew, Luke)", "MAT 14:13-21", "LUK 9:10-17"),
    ("Feeding of the 5,000 (Mark, Luke)", "MRK 6:32-44", "LUK 9:10-17"),
    ("Peter's confession (Matthew, Mark)", "MAT 16:13-20", "MRK 8:27-30"),
    ("Peter's confession (Matthew, Luke)", "MAT 16:13-20", "LUK 9:18-21"),
    ("Peter's confession (Mark, Luke)", "MRK 8:27-30", "LUK 9:18-21"),
    ("First passion prediction (Matthew, Mark)", "MAT 16:21-23", "MRK 8:31-33"),
    ("First passion prediction (Matthew, Luke)", "MAT 16:21-23", "LUK 9:22-22"),
    ("Transfiguration (Matthew, Mark)", "MAT 17:1-8", "MRK 9:2-8"),
    ("Transfiguration (Matthew, Luke)", "MAT 17:1-8", "LUK 9:28-36"),
    ("Transfiguration (Mark, Luke)", "MRK 9:2-8", "LUK 9:28-36"),
    ("Second passion prediction (Matthew, Mark)", "MAT 17:22-23", "MRK 9:30-32"),
    ("Second passion prediction (Mark, Luke)", "MRK 9:30-32", "LUK 9:43-45"),
    ("Third passion prediction (Matthew, Mark)", "MAT 20:17-19", "MRK 10:32-34"),
    ("Third passion prediction (Mark, Luke)", "MRK 10:32-34", "LUK 18:31-34"),
    ("The Lord's prayer", "MAT 6:9-13", "LUK 11:2-4"),
    ("The beatitudes", "MAT 5:3-12", "LUK 6:20-23"),
]


def parse_passage(text):
    """"ISA 36:1-39:8" -> ("ISA", (36, 1), (39, 8))."""
    book, rng = text.split()
    a, _, b = rng.partition("-")
    c1, v1 = map(int, a.split(":"))
    if not b:
        c2, v2 = c1, v1
    elif ":" in b:
        c2, v2 = map(int, b.split(":"))
    else:
        c2, v2 = c1, int(b)
    return book, (c1, v1), (c2, v2)


@functools.cache
def source_chapter(book, chapter):
    """{verse id: [word rows]} from data/hbo or data/grc, or {}."""
    for lang in ("hbo", "grc"):
        path = ROOT / "data" / lang / f"{book}.{chapter}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))["verses"]
    return {}


@functools.cache
def book_records(book):
    """{verse id: [records holding it]} for a book's content."""
    out = {}
    for path in sorted((ROOT / "content" / book).glob("*.json")):
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
            for vid in r["refs"]:
                out.setdefault(vid, []).append(r)
    return out


def passage_verses(text):
    """The verse ids of a passage that have source data, in order."""
    book, start, end = parse_passage(text)
    out = []
    for chapter in range(start[0], end[0] + 1):
        verses = source_chapter(book, chapter)
        for vid in sorted(verses, key=lambda v: refs.parse(v).verse):
            key = (chapter, refs.parse(vid).verse)
            if start <= key <= end:
                out.append(vid)
    return out


def lemmas(vid):
    """A verse's lemma sequence, one per word row (a prefix is a row of its own)."""
    p = refs.parse(vid)
    return tuple(w.get("lemma") or w["text"] for w in source_chapter(p.book, p.chapter).get(vid, []))


def bare(word):
    """A word's letters without vowel points, accents or breathings, lower case."""
    return "".join(c for c in unicodedata.normalize("NFD", word)
                   if unicodedata.category(c)[0] == "L").lower()


def surface(vid):
    """A verse's words as written, letters only: two verses with the same
    lemmas can still differ in person or number (Isaiah 36:5, 2 Kings 18:20)."""
    p = refs.parse(vid)
    return tuple(b for b in (bare(w["text"]) for w in source_chapter(p.book, p.chapter).get(vid, [])) if b)


def same_source(x, y):
    """True when two verses have the same words in the same order."""
    return lemmas(x) == lemmas(y) and surface(x) == surface(y)


def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0.0


def align(left, right, score):
    """Monotonic one-to-one alignment of two lists maximising the summed score
    of matched pairs (Needleman-Wunsch with free gaps). Returns [(i, j)]."""
    n, m = len(left), len(right)
    best = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            best[i][j] = max(best[i + 1][j], best[i][j + 1], score(left[i], right[j]) + best[i + 1][j + 1])
    out, i, j = [], 0, 0
    while i < n and j < m:
        s = score(left[i], right[j])
        if s > 0 and best[i][j] == s + best[i + 1][j + 1]:
            out.append((i, j))
            i, j = i + 1, j + 1
        elif best[i][j] == best[i + 1][j]:
            i += 1
        else:
            j += 1
    return out


def verse_text(vid, lang, level):
    """A verse's part of each record holding it, joined; None if untranslated."""
    p = refs.parse(vid)
    parts = []
    for r in book_records(p.book).get(vid, []):
        text = r["renderings"].get(lang, {}).get(level)
        if text is None:
            return None
        verses, verse, pos = {}, refs.parse(r["refs"][0]).verse, 0
        for m in markup.VERSE.finditer(text):
            verses[verse] = text[pos:m.start()]
            verse, pos = int(m[1]), m.end()
        verses[verse] = text[pos:]
        parts.append(verses.get(p.verse, ""))
    return " ".join(x.strip() for x in parts) if parts else None


def lined(vid, lang):
    """True if a record holding the verse is set in lines in lang; None if untranslated."""
    rs = book_records(refs.parse(vid).book).get(vid, [])
    if not rs or any(lang not in r["renderings"] for r in rs):
        return None
    return any(markup.is_poetry(t) for r in rs for t in r["renderings"][lang].values())


def plain(text):
    """Rendered text reduced for comparison: default settings, no markers,
    no brackets or punctuation, lower case, single spaces."""
    text = markup.SPAN.sub(lambda m: m[2].split("|")[0], text)
    text = markup.flat(markup.VERSE.sub(" ", text))
    text = re.sub(r"[\[\]]", "", text)
    text = re.sub(r"[^\w\s'’-]", " ", text)
    return " ".join(text.lower().split())


def compare(name, a, b, langs=LANGS):
    """The findings for one pair: {"pairs", "identical", "layout", "wording"}."""
    left, right = passage_verses(a), passage_verses(b)
    lem = {v: lemmas(v) for v in left + right}
    bar = SIMILAR["grc" if (ROOT / "data" / "grc" / f"{parse_passage(a)[0]}.{parse_passage(a)[1][0]}.json").exists()
                  else "hbo"]
    sims = {}

    def score(x, y):
        if (x, y) not in sims:
            s = similarity(lem[x], lem[y])
            sims[x, y] = s if s >= bar else 0.0
        return sims[x, y]

    pairs = [(left[i], right[j]) for i, j in align(left, right, score)]
    identical = [(x, y) for x, y in pairs if same_source(x, y)]
    close = [(x, y, sims[x, y]) for x, y in pairs if not same_source(x, y) and sims[x, y] >= CLOSE]
    layout, wording = [], []
    for x, y in pairs:
        for lang in langs:
            lx, ly = lined(x, lang), lined(y, lang)
            if lx is not None and ly is not None and lx != ly:
                layout.append((x, y, lang, "lined" if lx else "prose", "lined" if ly else "prose"))
    for x, y in identical:
        for lang in langs:
            for level in LEVELS:
                tx, ty = verse_text(x, lang, level), verse_text(y, lang, level)
                if tx is None or ty is None or not tx.strip() or not ty.strip():
                    continue
                if plain(tx) != plain(ty):
                    wording.append((x, y, lang, level, tx, ty))
    return {"name": name, "a": a, "b": b, "pairs": pairs, "identical": identical, "close": close,
            "layout": layout, "wording": wording}


def show_ref(vid):
    p = refs.parse(vid)
    return f"{p.book} {p.chapter}:{p.verse}"


def word_diff(x, y):
    """The changed words of two texts, as "a → b" pieces."""
    a, b = plain(x).split(), plain(y).split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != "equal":
            out.append(f"{' '.join(a[i1:i2]) or '∅'} → {' '.join(b[j1:j2]) or '∅'}")
    return "; ".join(out)


def is_psalm(vid):
    return vid.startswith("PSA.")


def report(results):
    """The markdown report."""
    lines = [
        "# Parallel passages",
        "",
        "Generated by `python3 scripts/parallels.py --write`; do not edit by hand.",
        "Verses are paired by their source words (lemmas); see the script's",
        "docstring for the rules. **Layout** lists verse pairs set in lines on one",
        "side and as prose on the other. **Wording** lists verse pairs whose source",
        "is identical word for word but whose rendering differs (settings, markers,",
        "brackets, case and punctuation set aside); the English is shown, other",
        "languages are counted. A difference is a question for a reviewer, not",
        "necessarily an error.",
        "",
        "| Pair | Passages | Verse pairs | Identical source | Layout (en) | Layout (all) "
        "| Wording (en) | Wording (all) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        en_layout = sum(1 for f in r["layout"] if f[2] == "en")
        en_wording = sum(1 for f in r["wording"] if f[2] == "en")
        lines.append(f"| {r['name']} | {r['a']} ↔ {r['b']} | {len(r['pairs'])} | {len(r['identical'])} "
                     f"| {en_layout} | {len(r['layout'])} | {en_wording} | {len(r['wording'])} |")
    psalm_side = sorted({(f[0], f[1]) for r in results for f in r["layout"]
                         if (is_psalm(f[0]) and f[3] == "prose") or (is_psalm(f[1]) and f[4] == "prose")})
    if psalm_side:
        lines += ["", "## Psalm-side layout gaps (for the Psalms work)", ""]
        lines += [f"- {show_ref(x)} ↔ {show_ref(y)}" for x, y in psalm_side]
    for r in results:
        if not r["layout"] and not r["wording"] and not r["close"]:
            continue
        lines += ["", f"## {r['name']}: {r['a']} ↔ {r['b']}", ""]
        if r["layout"]:
            by_pair = {}
            for x, y, lang, sx, sy in r["layout"]:
                by_pair.setdefault((x, y, sx, sy), []).append(lang)
            lines += ["**Layout**", ""]
            for (x, y, sx, sy), langs in by_pair.items():
                lines.append(f"- {show_ref(x)} ({sx}) ↔ {show_ref(y)} ({sy}): {', '.join(langs)}")
            lines.append("")
        if r["wording"]:
            by_pair = {}
            for x, y, lang, level, tx, ty in r["wording"]:
                by_pair.setdefault((x, y), []).append((lang, level, tx, ty))
            lines += ["**Wording, identical source**", ""]
            for (x, y), found in by_pair.items():
                others = sorted({lang for lang, *_ in found if lang != "en"})
                lines.append(f"- {show_ref(x)} ↔ {show_ref(y)}"
                             + (f" (also differs in: {', '.join(others)})" if others else ""))
                for lang, level, tx, ty in found:
                    if lang == "en":
                        lines.append(f"  - en {level}: {word_diff(tx, ty)}")
            lines.append("")
        if r["close"]:
            lines += [f"**Close but not identical source** (lemma similarity ≥ {CLOSE}; for reference)", ""]
            for x, y, s in r["close"]:
                tx, ty = verse_text(x, "en", "L"), verse_text(y, "en", "L")
                diff = word_diff(tx, ty) if tx and ty else "not translated"
                lines.append(f"- {show_ref(x)} ↔ {show_ref(y)} ({s:.2f}): en L {diff or 'same'}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--write", action="store_true", help=f"write {REPORT.relative_to(ROOT)}")
    p.add_argument("--pair", help="only the pairs whose name or passages contain this text")
    args = p.parse_args(argv)
    chosen = [x for x in PARALLELS if not args.pair or any(args.pair in s for s in x)]
    results = [compare(*x) for x in chosen]
    if args.write:
        REPORT.write_text(report(results), encoding="utf-8")
        print(f"wrote {REPORT.relative_to(ROOT)}")
    for r in results:
        print(f"{r['name']}: {len(r['pairs'])} verse pairs, {len(r['identical'])} identical source, "
              f"layout {len(r['layout'])}, wording {len(r['wording'])}")


if __name__ == "__main__":
    main()
