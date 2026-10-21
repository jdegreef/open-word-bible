"""Which sentences hold the words of Jesus, for the reader's red letters.

data/words_of_jesus/<BOOK>.json maps a record id to where Jesus speaks in
it, one file per book (like data/headings/), so marking a book touches no
translation file:

    "all"     the sentence is inside his words from its start (it continues
              a speech an earlier sentence opened); every quotation in it is
              his, and the whole of it when it has no quotation marks
    "quoted"  every quotation in the sentence is his, and the narration
              around them is not ("Jesus answered him, \"Truly ...\"")
    [0, 2]    only these quotations, counted from 0, where someone else
              also speaks in the sentence
    {"inner": "quoted"} or {"inner": "all"}
              the quotations inside someone else's words, where a speaker
              quotes Jesus (Paul retelling the Damascus road, Acts 22:7);
              "all" when the sentence begins inside such a quotation

Who is speaking is a fact about the original, the same in every language,
so it is marked once; the words themselves are found in each rendering from
its own quotation marks (markup.quotations). Where a speech ends is a
meaning decision, made in the record and shown by its quotation marks
(John 3:16-21), so the red letters follow the translation, never the other
way round. Words of Jesus are his direct speech, including where the
narrator quotes what he said ("he had said, \"Follow me\""), but not other
people quoting him.
"""
import functools
import json
from pathlib import Path

from owb import markup

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "data" / "words_of_jesus"


@functools.cache
def marked():
    """Every marked record id, across books, to its value."""
    out = {}
    for path in sorted(DIR.glob("*.json")):
        out.update(json.loads(path.read_text(encoding="utf-8"))["records"])
    return out


def _quotations(text, value):
    if isinstance(value, dict):
        return markup.quotations(text, inside=value["inner"] == "all", inner=True)
    return markup.quotations(text, inside=value == "all")


def ranges(text, value):
    """Where Jesus speaks in one rendering, as [(start, end), ...]."""
    found = _quotations(text, value)
    if isinstance(value, list):
        return [found[i] for i in value if i < len(found)]
    return found


def record_ranges(record, value):
    """ranges() for each of a record's renderings: {lang: {level: [[s, e], ...]}}."""
    return {lang: {level: [list(r) for r in ranges(text, value)] for level, text in levels.items()}
            for lang, levels in record["renderings"].items()}


def errors(record, value):
    """What is wrong with a record's marking, as a list of reasons."""
    if not (value in ("all", "quoted") or (isinstance(value, list) and value
                                         and all(isinstance(i, int) and i >= 0 for i in value))
            or (isinstance(value, dict) and list(value) == ["inner"] and value["inner"] in ("all", "quoted"))):
        return [f"{record['id']}: {value!r} is not \"all\", \"quoted\", a list of quotation numbers "
                "or {\"inner\": \"all\" or \"quoted\"}"]
    found = []
    for lang, levels in record["renderings"].items():
        for level, text in levels.items():
            where = f"{record['id']} {lang}.{level}"
            try:
                quotes = _quotations(text, value)
            except ValueError as e:
                found.append(f"{where}: {e}")
                continue
            if (value == "quoted" or value == {"inner": "quoted"}) and not quotes:
                found.append(f"{where}: marked \"quoted\" but has no quotation")
            if isinstance(value, list) and max(value) >= len(quotes):
                found.append(f"{where}: has {len(quotes)} quotations, not quotation {max(value)}")
    return found
