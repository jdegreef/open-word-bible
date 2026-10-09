"""Canonical verse references.

A verse id is "<BOOK>.<chapter>.<verse>", e.g. "JHN.1.1", where BOOK is a
USFM-style book code.
"""
import re
from typing import NamedTuple

# (USFM code, SBLGNT file/book name) in canonical order.
NT_BOOKS = [
    ("MAT", "Matt"), ("MRK", "Mark"), ("LUK", "Luke"), ("JHN", "John"),
    ("ACT", "Acts"), ("ROM", "Rom"), ("1CO", "1Cor"), ("2CO", "2Cor"),
    ("GAL", "Gal"), ("EPH", "Eph"), ("PHP", "Phil"), ("COL", "Col"),
    ("1TH", "1Thess"), ("2TH", "2Thess"), ("1TI", "1Tim"), ("2TI", "2Tim"),
    ("TIT", "Titus"), ("PHM", "Phlm"), ("HEB", "Heb"), ("JAS", "Jas"),
    ("1PE", "1Pet"), ("2PE", "2Pet"), ("1JN", "1John"), ("2JN", "2John"),
    ("3JN", "3John"), ("JUD", "Jude"), ("REV", "Rev"),
]
BOOK_CODES = [code for code, _ in NT_BOOKS]
SBLGNT_TO_CODE = {name: code for code, name in NT_BOOKS}
CODE_TO_SBLGNT = {code: name for code, name in NT_BOOKS}
_ORDER = {code: i for i, code in enumerate(BOOK_CODES)}

_VERSE_ID = re.compile(r"([1-3]?[A-Z]{2,3})\.(\d+)\.(\d+)")


class Ref(NamedTuple):
    book: str
    chapter: int
    verse: int

    def __str__(self):
        return f"{self.book}.{self.chapter}.{self.verse}"

    def sort_key(self):
        return (_ORDER[self.book], self.chapter, self.verse)


def parse(verse_id):
    """Parse "JHN.1.1" into a Ref. Raises ValueError if malformed or unknown."""
    m = _VERSE_ID.fullmatch(verse_id)
    if not m or m[1] not in _ORDER:
        raise ValueError(f"bad verse id: {verse_id!r}")
    return Ref(m[1], int(m[2]), int(m[3]))


def format_ref(ref):
    return str(ref)


def from_sblgnt(label):
    """Parse an SBLGNT line label such as "John 1:1" or "1Cor 13:4"."""
    name, cv = label.rsplit(" ", 1)
    chapter, verse = cv.split(":")
    return Ref(SBLGNT_TO_CODE[name], int(chapter), int(verse))


def in_range(ref, start, end):
    """True if start <= ref <= end in canonical order."""
    return start.sort_key() <= ref.sort_key() <= end.sort_key()
