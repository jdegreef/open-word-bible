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
# All 66 books in Protestant canonical order: (USFM code, OSIS id, English name).
# The book number used by Zefania XML is the position in this list, from 1.
BOOKS = [
    ("GEN", "Gen", "Genesis"), ("EXO", "Exod", "Exodus"), ("LEV", "Lev", "Leviticus"),
    ("NUM", "Num", "Numbers"), ("DEU", "Deut", "Deuteronomy"), ("JOS", "Josh", "Joshua"),
    ("JDG", "Judg", "Judges"), ("RUT", "Ruth", "Ruth"), ("1SA", "1Sam", "1 Samuel"),
    ("2SA", "2Sam", "2 Samuel"), ("1KI", "1Kgs", "1 Kings"), ("2KI", "2Kgs", "2 Kings"),
    ("1CH", "1Chr", "1 Chronicles"), ("2CH", "2Chr", "2 Chronicles"), ("EZR", "Ezra", "Ezra"),
    ("NEH", "Neh", "Nehemiah"), ("EST", "Esth", "Esther"), ("JOB", "Job", "Job"),
    ("PSA", "Ps", "Psalms"), ("PRO", "Prov", "Proverbs"), ("ECC", "Eccl", "Ecclesiastes"),
    ("SNG", "Song", "Song of Songs"), ("ISA", "Isa", "Isaiah"), ("JER", "Jer", "Jeremiah"),
    ("LAM", "Lam", "Lamentations"), ("EZK", "Ezek", "Ezekiel"), ("DAN", "Dan", "Daniel"),
    ("HOS", "Hos", "Hosea"), ("JOL", "Joel", "Joel"), ("AMO", "Amos", "Amos"),
    ("OBA", "Obad", "Obadiah"), ("JON", "Jonah", "Jonah"), ("MIC", "Mic", "Micah"),
    ("NAM", "Nah", "Nahum"), ("HAB", "Hab", "Habakkuk"), ("ZEP", "Zeph", "Zephaniah"),
    ("HAG", "Hag", "Haggai"), ("ZEC", "Zech", "Zechariah"), ("MAL", "Mal", "Malachi"),
    ("MAT", "Matt", "Matthew"), ("MRK", "Mark", "Mark"), ("LUK", "Luke", "Luke"),
    ("JHN", "John", "John"), ("ACT", "Acts", "Acts"), ("ROM", "Rom", "Romans"),
    ("1CO", "1Cor", "1 Corinthians"), ("2CO", "2Cor", "2 Corinthians"), ("GAL", "Gal", "Galatians"),
    ("EPH", "Eph", "Ephesians"), ("PHP", "Phil", "Philippians"), ("COL", "Col", "Colossians"),
    ("1TH", "1Thess", "1 Thessalonians"), ("2TH", "2Thess", "2 Thessalonians"),
    ("1TI", "1Tim", "1 Timothy"), ("2TI", "2Tim", "2 Timothy"), ("TIT", "Titus", "Titus"),
    ("PHM", "Phlm", "Philemon"), ("HEB", "Heb", "Hebrews"), ("JAS", "Jas", "James"),
    ("1PE", "1Pet", "1 Peter"), ("2PE", "2Pet", "2 Peter"), ("1JN", "1John", "1 John"),
    ("2JN", "2John", "2 John"), ("3JN", "3John", "3 John"), ("JUD", "Jude", "Jude"),
    ("REV", "Rev", "Revelation"),
]
BOOK_CODES = [code for code, _, _ in BOOKS]
OSIS_TO_CODE = {osis: code for code, osis, _ in BOOKS}
BOOK_NAMES = {code: name for code, _, name in BOOKS}
OT_CODES = BOOK_CODES[:39]
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
