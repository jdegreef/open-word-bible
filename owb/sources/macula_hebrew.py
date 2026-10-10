"""MACULA Hebrew word data for the Westminster Leningrad Codex.

Reads WLC/tsv/macula-hebrew.tsv (a Git LFS file; see scripts/fetch_sources.py).
Each row is one morpheme: a prefix such as the preposition be- is its own row
with an empty `after`, so a verse's text is the rows' text + after, joined.
Columns used: xml:id, ref ("GEN 1:1!1" = word 1 of Genesis 1:1), text, after,
transliteration, lemma, morph, gloss, english, strongnumberx, lang (H Hebrew,
A Aramaic). The word-sense columns (sdbh, lexdomain, coredomain,
contextualdomain) are not used or redistributed.
"""
import csv
import io
import re
from functools import lru_cache
from typing import NamedTuple

from owb import refs
from owb.sources import read_text

TSV_PATH = "WLC/tsv/macula-hebrew.tsv"

# Word-sense columns (SDBH, UBS MARBLE): not used or redistributed; see
# tests/test_licensing.py.
RESTRICTED = ("lexdomain", "contextualdomain", "coredomain", "sdbh")
TEXT_ID = "WLC@macula-hebrew"
_REF = re.compile(r"(\w+) (\d+):(\d+)!(\d+)")


class Morpheme(NamedTuple):
    id: str
    ref: refs.Ref
    position: int     # word number within the verse
    text: str
    after: str
    transliteration: str
    lemma: str
    morph: str
    gloss: str
    english: str
    strong: str
    lang: str


@lru_cache(maxsize=None)
def _all():
    """Return {Ref: [Morpheme]} for the whole Old Testament."""
    reader = csv.DictReader(io.StringIO(read_text("macula-hebrew", TSV_PATH)),
                            delimiter="\t", quoting=csv.QUOTE_NONE)
    by_verse = {}
    for row in reader:
        m = _REF.fullmatch(row["ref"])
        ref = refs.Ref(m[1], int(m[2]), int(m[3]))
        by_verse.setdefault(ref, []).append(Morpheme(
            id=row["xml:id"], ref=ref, position=int(m[4]), text=row["text"],
            after=row["after"], transliteration=row["transliteration"],
            lemma=row["lemma"], morph=row["morph"], gloss=row["gloss"],
            english=row["english"], strong=row["strongnumberx"], lang=row["lang"]))
    return by_verse


def verses():
    """Return {Ref: [Morpheme]} in canonical order."""
    return dict(sorted(_all().items(), key=lambda kv: kv[0].sort_key()))


def verse_text(morphemes):
    return "".join(m.text + m.after for m in morphemes).strip()


_ACCENTS = re.compile("[֑-֯]")


@lru_cache(maxsize=None)
def forms():
    """Every morpheme, lemma and whole word in the Old Testament, each with
    and without cantillation accents. A whole word joins the morphemes that
    share a word number (be- + reshit)."""
    out = set()
    for morphemes in _all().values():
        words = {}
        for m in morphemes:
            out.update((m.text, m.lemma))
            words[m.position] = words.get(m.position, "") + m.text
        out.update(words.values())
    out |= {_ACCENTS.sub("", f) for f in out}
    out.discard("")
    return frozenset(out)
