"""Cross-references from OpenBible.info (CC BY), as kept verbatim in
scrollmapper/bible_databases (pinned in sources.lock.json).

The file is tab-separated: "From Verse", "To Verse", "Votes". A verse is an
OSIS id ("Gen.1.1"), a target may be a range ("Prov.8.22-Prov.8.30"), and
votes are how many readers found the reference helpful (some are negative).
Verses are numbered as in English Bibles (the KJV), not as in the WLC.
"""
from typing import NamedTuple

from owb import refs
from owb.sources import read_text

NAME = "openbible-crossrefs"
PATH = "sources/extras/cross_references.txt"


class Row(NamedTuple):
    source: refs.Ref
    first: refs.Ref
    last: refs.Ref
    votes: int


def parse_osis(osis_id):
    """'Gen.1.1' -> Ref("GEN", 1, 1)."""
    book, chapter, verse = osis_id.split(".")
    return refs.Ref(refs.OSIS_TO_CODE[book], int(chapter), int(verse))


def parse(text):
    """Every row of the file's text, as Rows. A target that runs into
    another book (Lev.27.34-Num.1.1) is cut to its first verse."""
    out = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("From Verse"):
            continue
        source, target, votes = line.split("\t")
        first, _, last = target.partition("-")
        first = parse_osis(first)
        last = parse_osis(last) if last else first
        if last.book != first.book:
            last = first
        out.append(Row(parse_osis(source), first, last, int(votes)))
    return out


def load():
    return parse(read_text(NAME, PATH))
