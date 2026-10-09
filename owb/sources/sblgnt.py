"""SBLGNT verse text.

Lines look like "John 1:1<TAB><greek>". SBLGNT marks textual variants inline
with the signs below; we strip them from the text and keep them separately as
(offset, mark) pairs, where offset is the index in the stripped text that the
mark stood before.
"""
from functools import lru_cache
from typing import NamedTuple

from owb import refs
from owb.sources import read_text

VARIANT_MARKS = "⸀⸁⸂⸃⸄⸅"
TEXT_ID = "SBLGNT@v1.2"


class Verse(NamedTuple):
    ref: refs.Ref
    text: str
    marks: tuple  # ((offset, mark), ...)


def strip_marks(raw):
    text, marks = [], []
    for ch in raw:
        if ch in VARIANT_MARKS:
            marks.append((len(text), ch))
        else:
            text.append(ch)
    return "".join(text), tuple(marks)


@lru_cache(maxsize=None)
def load_book(code):
    """Return {Ref: Verse} for one book."""
    name = refs.CODE_TO_SBLGNT[code]
    verses = {}
    for line in read_text("sblgnt", f"data/sblgnt/text/{name}.txt").splitlines():
        if "\t" not in line:
            continue  # book title line
        label, raw = line.split("\t", 1)
        ref = refs.from_sblgnt(label)
        text, marks = strip_marks(raw.strip())
        verses[ref] = Verse(ref, text, marks)
    return verses


def load_verses(start, end=None):
    """Return [Verse] from start to end (inclusive), within one book."""
    start = refs.parse(start) if isinstance(start, str) else start
    end = start if end is None else (refs.parse(end) if isinstance(end, str) else end)
    book = load_book(start.book)
    return [v for r, v in book.items() if refs.in_range(r, start, end)]


def marked_spans(verse):
    """Pair variant marks into readable spans of the stripped text.

    ⸀ and ⸁ mark the single word that follows; ⸂…⸃ and ⸄…⸅ enclose a
    span. Returns [(mark, start, end, text)].
    """
    spans, open_at = [], {}
    for offset, mark in verse.marks:
        if mark in "⸀⸁":
            rest = verse.text[offset:]
            word = rest.split(" ", 1)[0].rstrip(",.·;")
            spans.append((mark, offset, offset + len(word), word))
        elif mark in "⸂⸄":
            open_at.setdefault(mark, []).append(offset)
        else:
            opener = {"⸃": "⸂", "⸅": "⸄"}[mark]
            begin = open_at[opener].pop()
            spans.append((opener + mark, begin, offset, verse.text[begin:offset]))
    return spans
