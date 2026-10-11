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
import itertools
import re
from functools import lru_cache
from typing import NamedTuple

from owb import refs
from owb.sources import lfs_path, read_text

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


def _morphemes(lines):
    """Parse the TSV's lines into Morphemes, in the file's order."""
    for row in csv.DictReader(lines, delimiter="\t", quoting=csv.QUOTE_NONE):
        m = _REF.fullmatch(row["ref"])
        ref = refs.Ref(m[1], int(m[2]), int(m[3]))
        yield Morpheme(
            id=row["xml:id"], ref=ref, position=int(m[4]), text=row["text"],
            after=row["after"], transliteration=row["transliteration"],
            lemma=row["lemma"], morph=row["morph"], gloss=row["gloss"],
            english=row["english"], strong=row["strongnumberx"], lang=row["lang"])


@lru_cache(maxsize=None)
def _all():
    """Return {Ref: [Morpheme]} for the whole Old Testament."""
    by_verse = {}
    for m in _morphemes(io.StringIO(read_text("macula-hebrew", TSV_PATH))):
        by_verse.setdefault(m.ref, []).append(m)
    return by_verse


def verses():
    """Return {Ref: [Morpheme]} in canonical order."""
    return dict(sorted(_all().items(), key=lambda kv: kv[0].sort_key()))


def iter_verses():
    """Yield (Ref, [Morpheme]) one verse at a time, reading the file as it
    goes: the same verses in the same order as verses(), without holding the
    Old Testament in memory (about 475,000 rows; the import on a small
    server cannot afford the whole of it at once). The file is already in
    canonical order; a test checks that against verses()."""
    with open(lfs_path("macula-hebrew", TSV_PATH), encoding="utf-8", newline="") as f:
        for ref, group in itertools.groupby(_morphemes(f), key=lambda m: m.ref):
            yield ref, list(group)


def verse_text(morphemes):
    return "".join(m.text + m.after for m in morphemes).strip()


def written(m):
    """False for a morpheme the WLC does not write: the article that a
    preposition swallows (la- "to the") has a row of its own with no text and
    an id ending in a letter. The preposition's code (Rd) already says the
    article is there, so records and extracts leave these rows out."""
    return bool(m.text)


def load_tokens(start, end=None):
    """Return the written [Morpheme] for verses start..end (inclusive), in
    text order."""
    start = refs.parse(start) if isinstance(start, str) else start
    end = start if end is None else (refs.parse(end) if isinstance(end, str) else end)
    return [m for ref, ms in verses().items()
            if refs.in_range(ref, start, end) for m in ms if written(m)]


def tokens_for_refs(verse_ids):
    """Return {morpheme id: Morpheme} for the written morphemes of a list of
    verse ids."""
    out = {}
    for vid in verse_ids:
        for m in _all().get(refs.parse(vid), []):
            if written(m):
                out[m.id] = m
    return out


def source_language(morphemes):
    """hbo for Hebrew, arc for a passage wholly in Aramaic."""
    return "arc" if morphemes and all(m.lang == "A" for m in morphemes) else "hbo"


def text_of(morphemes):
    """The text of a run of morphemes as the WLC writes it: a prefix joins
    its word, maqaf joins two words, and a new verse starts after a space."""
    out = []
    for i, m in enumerate(morphemes):
        out.append(m.text + m.after)
        nxt = morphemes[i + 1] if i + 1 < len(morphemes) else None
        if nxt is not None and verse_of(nxt.id) != verse_of(m.id) and not m.after.endswith(" "):
            out.append(" ")
    return "".join(out).strip()


def verse_of(morpheme_id):
    """The verse part of a MACULA Hebrew id: o + book, chapter, verse
    (2 + 3 + 3 digits), then word and morpheme numbers."""
    return morpheme_id[:9]


def sentences(morphemes):
    """Group morphemes (in text order) into records, one per verse.

    The WLC marks only the end of a verse (sof pasuq, with a paragraph sign
    after it), so verse divisions are the only sentence boundaries the source
    gives. A Hebrew record is one verse, or several whole verses joined by
    hand where one sentence runs across them (see owb.validate)."""
    out = []
    for m in morphemes:
        if out and verse_of(out[-1][-1].id) == verse_of(m.id):
            out[-1].append(m)
        else:
            out.append([m])
    return out


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
