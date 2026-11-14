"""Check that the three levels keep their promises.

    python3 scripts/level_checks.py                  print the report
    python3 scripts/level_checks.py --write          write docs/review-notes/level-checks.md
    python3 scripts/level_checks.py --list fr        list one language's supplied-word mismatches

Literal: supplied words are in [brackets]. Every supplied_words decision that
covers Literal names the words English (or another language) adds; the
script looks for them in that language's Literal rendering and asks whether
they stand inside brackets. A decision's choice is free text, so the words
are read out of it: the parts marked for Literal ("cast [it] (L); threw it
out (B)"), quoted wording, and bracketed words in the choice itself. Each
decision comes out as
  bracketed      the words are found in Literal, inside brackets (or the
                 brackets the choice names are there),
  not bracketed  the words are found in Literal, outside brackets: a
                 mismatch for a reader to look at,
  not found      the choice does not quote the Literal wording, so the
                 script cannot tell.
Brackets are also checked as text: in a Literal rendering they must pair up
and not nest, and Balanced and Readable have none ("No brackets",
docs/english-style.md section 4, and every language's brief). The one
exception is the brackets around a passage the oldest manuscripts lack
(John 7:53-8:11, the shorter ending of Mark): they open in one record and
close in a later one, at every level alike, so a record whose levels all
open (or all close) the same unpaired bracket is not flagged.

Readable: plain language. For each book and language the script measures,
at each level, the average sentence length (words; characters for
Japanese, which has no spaces) and the rare-word rate: the share of words
that occur fewer than RARE_BELOW times in that language's whole Readable
text. Readable should be clearly plainer than Balanced: a book is flagged
when its Readable sentences are not at least 5% shorter than its Balanced
ones, or its rare-word rate is not lower.
"""
import argparse
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from owb import markup  # noqa: E402

OUT = os.path.join(ROOT, "docs", "review-notes", "level-checks.md")
LEVELS = ("L", "B", "R")
LEVEL_WORDS = {"l": "L", "literal": "L", "b": "B", "balanced": "B", "r": "R", "readable": "R"}
BRACKET = re.compile(r"\[([^\[\]]*)\]")
QUOTED = re.compile(r'"([^"]+)"|“([^”]+)”|«\s*([^»]+?)\s*»|「([^」]+)」|(?<!\w)\'([^\']+)\'(?!\w)')
ANNOTATION = re.compile(r"\(([^()]*)\)")
SENTENCE_END = re.compile(r"(?<=[.!?。！？።।])")
CHARACTER_LANGS = {"ja"}
RARE_BELOW = 5
MIN_RECORDS = 20  # books with fewer records in a language are left out of part (b)
SHORTER = 0.95  # Readable sentences should be at most this share of Balanced's


# ---------------------------------------------------------------- loading

def book_order():
    with open(os.path.join(ROOT, "data", "books.json"), encoding="utf-8") as f:
        return list(json.load(f)["books"])


def load_records():
    """Records in canonical book order, then file and record order."""
    for book in book_order():
        for path in sorted(glob.glob(os.path.join(ROOT, "content", book, "*.json"))):
            with open(path, encoding="utf-8") as f:
                yield from json.load(f)["records"]


def plain(text):
    """Text as a reader sees it with default settings, on one line, without
    verse markers."""
    text = markup.flat(markup.render(text))
    text = markup.VERSE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------- (a) brackets

def literal_phrases(choice):
    """The Literal wording a supplied_words choice names, as a list of
    phrases (each possibly holding [brackets])."""
    pieces = []
    for piece in re.split(r";\s*", choice):
        notes = ANNOTATION.findall(piece)
        levels = set()
        for note in notes:
            for word in re.findall(r"[A-Za-z]+", note):
                if word.lower() in LEVEL_WORDS:
                    levels.add(LEVEL_WORDS[word.lower()])
        if levels and "L" not in levels:
            continue
        quoted = ["".join(groups) for groups in QUOTED.findall(piece)]
        if quoted:
            pieces.extend(quoted)
            continue
        text = ANNOTATION.sub("", piece)
        text = re.split(r":\s|\s+(?:for|with|as|where|instead of)\s", text)[0]
        pieces.append(text)
    phrases = []
    for piece in pieces:
        for part in re.split(r"\s*(?:\.\.\.|…)\s*", piece):
            part = part.strip(" ,.;:!?\"'“”")
            if part:
                phrases.append(part)
    return phrases


def bracket_regions(text):
    return [(m.start(), m.end()) for m in BRACKET.finditer(text)]


def supplied_status(phrases, literal):
    """bracketed, not_bracketed or not_found, for a decision's phrases
    against its Literal rendering."""
    text = plain(literal)
    folded = text.casefold()
    regions = bracket_regions(text)
    found_any = False
    for phrase in phrases:
        inner = BRACKET.findall(phrase)
        if inner:
            # The choice brackets the supplied words itself: those exact
            # brackets should be in Literal.
            if all(f"[{w.strip()}]".casefold() in folded for w in inner if w.strip()):
                return "bracketed"
            bare = BRACKET.sub(lambda m: m[1], phrase)
            if bare.strip().casefold() in BRACKET.sub(lambda m: m[1], text).casefold():
                found_any = True
            continue
        target = phrase.casefold()
        if not target:
            continue
        for m in re.finditer(re.escape(target), folded):
            found_any = True
            if any(s < m.end() and m.start() < e for s, e in regions):
                return "bracketed"
    return "not_bracketed" if found_any else "not_found"


def supplied_checks(records):
    """Yield (record id, lang, status, choice) for each supplied_words
    decision that covers Literal."""
    for record in records:
        for d in record["decisions"]:
            if d["category"] != "supplied_words":
                continue
            levels = d.get("levels") or LEVELS
            if "L" not in levels:
                continue
            langs = [d["language"]] if d.get("language") else ["en"]
            for lang in langs:
                literal = record["renderings"].get(lang, {}).get("L")
                if literal is None:
                    continue
                status = supplied_status(literal_phrases(d["choice"]), literal)
                yield record["id"], lang, status, d["choice"]


def bracket_problems(text):
    """What is wrong with the brackets of one rendering, ignoring an
    unpaired bracket (the caller decides whether that is a passage
    bracket)."""
    found, depth = [], 0
    for ch in text:
        if ch == "[":
            depth += 1
            if depth > 1:
                found.append("nested brackets")
        elif ch == "]":
            depth -= 1
            if depth < 0:
                depth = 0
    if "[]" in text:
        found.append("empty brackets")
    return sorted(set(found))


def unpaired(text):
    """(opening brackets with no close, closing brackets with no open)."""
    opened = closed = 0
    for ch in text:
        if ch == "[":
            opened += 1
        elif ch == "]":
            if opened:
                opened -= 1
            else:
                closed += 1
    return opened, closed


def without_unpaired(text):
    """text with its unpaired brackets taken out (the passage brackets)."""
    keep, stack = list(text), []
    for i, ch in enumerate(text):
        if ch == "[":
            stack.append(i)
        elif ch == "]":
            if stack:
                stack.pop()
            else:
                keep[i] = ""
    for i in stack:
        keep[i] = ""
    return "".join(keep)


def bracket_checks(records):
    """Yield (record id, lang, level, problem) for brackets out of place."""
    for record in records:
        for lang, levels in record["renderings"].items():
            shapes = {lv: unpaired(levels[lv]) for lv in LEVELS if lv in levels}
            passage = (len(shapes) == 3 and len(set(shapes.values())) == 1
                       and shapes["L"] != (0, 0))
            for level, text in levels.items():
                # A passage bracket may hold supplied words in brackets: only
                # the brackets that pair up inside the record are checked.
                paired = without_unpaired(text) if passage else text
                for problem in bracket_problems(paired):
                    yield record["id"], lang, level, problem
                if shapes[level] != (0, 0) and not passage:
                    yield record["id"], lang, level, "unbalanced brackets"
                if level != "L" and ("[" in paired or "]" in paired):
                    yield record["id"], lang, level, f"brackets at {level}"


# ------------------------------------------------------- (b) readability

def words(text, lang):
    """The words (characters, for Japanese) of a plain text."""
    text = BRACKET.sub(lambda m: m[1], text)
    if lang in CHARACTER_LANGS:
        return [ch for ch in text if ch.isalnum()]
    found = []
    for token in text.split():
        token = token.strip("\"'“”‘’«»「」『』()[].,;:!?¿¡—–-·።፣፤፥፦।॥…").casefold()
        if any(ch.isalnum() for ch in token):
            found.append(token)
    return found


def sentences(text):
    return [s for s in SENTENCE_END.split(text) if s.strip()]


def readability(records):
    """{(book, lang, level): {"records", "sentences", "words", "tokens"}}, and
    {lang: Counter of Readable words}."""
    stats = collections.defaultdict(lambda: {"records": 0, "sentences": 0, "words": 0, "tokens": []})
    vocab = collections.defaultdict(collections.Counter)
    for record in records:
        book = record["id"].split(".")[0]
        for lang, levels in record["renderings"].items():
            for level, text in levels.items():
                text = plain(text)
                ws = words(text, lang)
                s = stats[(book, lang, level)]
                s["records"] += 1
                s["sentences"] += max(1, sum(1 for sent in sentences(text) if words(sent, lang)))
                s["words"] += len(ws)
                s["tokens"].extend(ws)
                if level == "R":
                    vocab[lang].update(ws)
    return stats, vocab


def readability_table(stats, vocab):
    """Rows (book, lang, {level: (avg sentence length, rare rate)}, flags)."""
    rows = []
    books = book_order()
    keys = sorted({(b, lang) for b, lang, _lv in stats},
                  key=lambda k: (books.index(k[0]) if k[0] in books else 99, k[1]))
    for book, lang in keys:
        per = {}
        for level in LEVELS:
            s = stats.get((book, lang, level))
            if not s or not s["words"]:
                continue
            rare = sum(1 for w in s["tokens"] if vocab[lang][w] < RARE_BELOW)
            per[level] = (s["words"] / s["sentences"], rare / s["words"], s["records"])
        if len(per) < 3 or per["R"][2] < MIN_RECORDS:
            continue
        flags = []
        if per["R"][0] > SHORTER * per["B"][0]:
            flags.append("sentences")
        if per["R"][1] >= per["B"][1]:
            flags.append("rare words")
        rows.append((book, lang, per, flags))
    return rows


# ------------------------------------------------------- report

def language_order():
    with open(os.path.join(ROOT, "data", "languages.json"), encoding="utf-8") as f:
        return [lang["code"] for lang in json.load(f)["reading"]]


def render_report(records, list_limit=15):
    records = list(records)
    langs = language_order()
    out = ["# Level checks", "",
           "Generated by `python3 scripts/level_checks.py --write`; see the script's",
           "docstring for what each check means. Records stay `ai_draft`.", ""]

    supplied = list(supplied_checks(records))
    by_lang = collections.defaultdict(collections.Counter)
    mismatches = collections.defaultdict(list)
    for rid, lang, status, choice in supplied:
        by_lang[lang][status] += 1
        if status == "not_bracketed":
            mismatches[lang].append((rid, choice))
    total_supplied = sum(1 for r in records for d in r["decisions"] if d["category"] == "supplied_words")
    meaning = sum(1 for r in records for d in r["decisions"]
                  if d["category"] == "supplied_words" and d["layer"] == "meaning")
    with_l = len(supplied)
    out += ["## 1. Literal: supplied words in brackets", "",
            f"{total_supplied} supplied_words decisions ({meaning} meaning decisions); "
            f"{with_l} cover Literal. The rest name words that Balanced or Readable add, "
            "which take no brackets.", "",
            "| lang | cover Literal | bracketed | not bracketed | not found |",
            "|---|---|---|---|---|"]
    for lang in langs:
        c = by_lang.get(lang)
        if c:
            out.append(f"| {lang} | {sum(c.values())} | {c['bracketed']} | {c['not_bracketed']} | {c['not_found']} |")
    out += ["",
            "\"Not bracketed\" is a decision whose Literal wording is in the rendering",
            "but outside brackets. Many are not errors: a supplied word inside an",
            "inflected word (Swahili object prefixes, Korean and Japanese particles)",
            "cannot be bracketed, and some decisions name the whole phrase the",
            "bracket sits in. The first few per language, for a reader:", ""]
    for lang in langs:
        if mismatches.get(lang):
            out.append(f"- **{lang}** ({len(mismatches[lang])}): " + "; ".join(
                f"{rid} ({choice[:60]})" for rid, choice in mismatches[lang][:list_limit]))
    problems = list(bracket_checks(records))
    counts = collections.Counter((lang, problem) for _rid, lang, _lv, problem in problems)
    out += ["", "### Brackets as text", ""]
    if problems:
        out += ["| lang | problem | renderings |", "|---|---|---|"]
        for (lang, problem), n in sorted(counts.items()):
            out.append(f"| {lang} | {problem} | {n} |")
        out += [""] + [f"- {rid} {lang} {lv}: {problem}" for rid, lang, lv, problem in problems[:60]]
    else:
        out.append("No unbalanced or nested brackets, and none at Balanced or Readable "
                   "outside the passage brackets of John 7:53-8:11 and Mark 16.")

    stats, vocab = readability(records)
    rows = readability_table(stats, vocab)
    flagged = [row for row in rows if row[3]]
    out += ["", "## 2. Readable: plainer than Balanced", "",
            f"Average sentence length (words; characters for Japanese) and rare-word rate "
            f"(share of words seen fewer than {RARE_BELOW} times in the language's whole "
            f"Readable text) per level. Books with fewer than {MIN_RECORDS} records in a "
            f"language are left out. {len(rows)} book-language pairs, {len(flagged)} flagged.", ""]
    summary = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
    for _book, lang, per, _flags in rows:
        for level, (length, rare, n) in per.items():
            acc = summary[lang][level]
            acc[0] += length * n
            acc[1] += rare * n
            acc[2] += n
    out += ["### By language (weighted by records)", "",
            "| lang | L length | B length | R length | L rare | B rare | R rare |",
            "|---|---|---|---|---|---|---|"]
    for lang in langs:
        if lang in summary:
            s = summary[lang]
            cells = [f"{s[lv][0] / s[lv][2]:.1f}" for lv in LEVELS]
            cells += [f"{s[lv][1] / s[lv][2]:.1%}" for lv in LEVELS]
            out.append(f"| {lang} | " + " | ".join(cells) + " |")
    out += ["", "### Flagged books", "",
            "Readable sentences not at least 5% shorter than Balanced (\"sentences\"), or",
            "Readable's rare-word rate not lower (\"rare words\").", ""]
    if flagged:
        out += ["| book | lang | B length | R length | B rare | R rare | flag |", "|---|---|---|---|---|---|---|"]
        for book, lang, per, flags in flagged:
            out.append(f"| {book} | {lang} | {per['B'][0]:.1f} | {per['R'][0]:.1f} | "
                       f"{per['B'][1]:.1%} | {per['R'][1]:.1%} | {', '.join(flags)} |")
    else:
        out.append("None.")
    out += ["", "### Every book", "",
            "| book | lang | L length | B length | R length | L rare | B rare | R rare |",
            "|---|---|---|---|---|---|---|---|"]
    for book, lang, per, _flags in rows:
        out.append(f"| {book} | {lang} | " + " | ".join(f"{per[lv][0]:.1f}" for lv in LEVELS) + " | "
                   + " | ".join(f"{per[lv][1]:.1%}" for lv in LEVELS) + " |")
    return "\n".join(out) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true", help=f"write {os.path.relpath(OUT, ROOT)}")
    parser.add_argument("--list", metavar="LANG", help="list one language's supplied-word mismatches")
    args = parser.parse_args(argv)
    records = list(load_records())
    if args.list:
        for rid, lang, status, choice in supplied_checks(records):
            if lang == args.list and status == "not_bracketed":
                print(f"{rid}\t{choice}")
        for rid, lang, level, problem in bracket_checks(records):
            if lang == args.list:
                print(f"{rid}\t{level}\t{problem}")
        return 0
    text = render_report(records)
    if args.write:
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
