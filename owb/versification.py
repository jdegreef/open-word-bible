"""Source and English verse numbering: the Old Testament, and five New
Testament verses.

Open Word Bible numbers verses as its source text does. In the Old Testament
that is the Westminster Leningrad Codex, where, for example, a psalm's title
is verse 1, so PSA.3.2 is Psalm 3:1 in English Bibles. The reference Bibles
(owb/sources/open_bibles.py) and most other Bibles use English (KJV)
numbering. Wherever our verse ids meet theirs, convert with to_english() and
to_source().

data/versification.json lists, under "english", every WLC verse whose
English counterpart is not the verse with the same id: {"PSA.3.1": [],
"PSA.3.2": ["PSA.3.1"], ...}. An empty list is a verse with no English
counterpart (a psalm title, which English Bibles print unnumbered above
verse 1). Under "not_in_hebrew" are the English verse ids the WLC has no verse
for (GEN.31.55 is Hebrew GEN.32.1). Any other verse is numbered the same in
both, except the few New Testament verses in NEW_TESTAMENT below and the
three Hebrew half-verses in OLD_TESTAMENT_HALVES, which the verse map leaves
out.

The site shows readers the NIV's numbering (to_niv(), from_niv()), which is
the English numbering but for 3 John 15.

The file is derived by scripts/build_versification.py from the Open
Scriptures Hebrew Bible's wlc/VerseMap.xml (CC BY 4.0), keeping only verses
that exist in MACULA Hebrew. The English numbering is the King James
Version's; the BSB, WEB, ASV and KJV follow it in every Old Testament verse
(tests/test_versification.py). The Reina-Valera 1909 follows it in Psalms
but not everywhere (e.g. parts of Numbers and Job).
"""
import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from owb import refs

DATA = Path(__file__).resolve().parents[1] / "data" / "versification.json"
VERSE_MAP = "wlc/VerseMap.xml"   # in the morphhb source

# The New Testament verses the SBLGNT numbers otherwise than English (KJV)
# Bibles, written by hand: there are only these, against the KJV's text
# (tests/test_versification.py). Each SBLGNT verse -> the English verses that
# hold its text. The verses the SBLGNT leaves out altogether (Matthew 17:21)
# are not here: they are missing, not renumbered.
NEW_TESTAMENT = {
    "ACT.19.40": ("ACT.19.40", "ACT.19.41"),  # its last clause is English 19:41
    "2CO.13.12": ("2CO.13.12", "2CO.13.13"),  # its second sentence is English 13
    "2CO.13.13": ("2CO.13.14",),              # the grace
    "3JN.1.15": ("3JN.1.14",),                # the end of English verse 14
    "REV.12.18": ("REV.13.1",),               # the start of English 13:1
}
# English verse ids those leave with no SBLGNT verse of their own number.
NEW_TESTAMENT_ABSENT = ("ACT.19.41", "2CO.13.14")

# Three Hebrew verses that are the first half of an English verse whose second
# half is the next Hebrew verse. VerseMap.xml pairs only the second half
# (1Sam.21.1 -> 1Sam.20.42), which leaves the first looking like a psalm
# title with no English verse; written by hand, against the KJV's text.
OLD_TESTAMENT_HALVES = {
    "NUM.26.1": ("NUM.26.1",),    # Hebrew 25:19 "after the plague" + 26:1 = English 26:1
    "1SA.20.42": ("1SA.20.42",),  # Hebrew 20:42 + 21:1 = English 20:42
    "1CH.12.4": ("1CH.12.4",),    # Hebrew 12:4 + 12:5 = English 12:4
}

# Reader numbering: what the site shows readers, the NIV's. It is the
# English (KJV) numbering above except in 3 John, where the NIV, like the
# SBLGNT, has a verse 15 ("Peace to you ..."), so our verses keep their own
# numbers there.
NIV_AS_SOURCE = ("3JN.1.15",)

# Sentences of one SBLGNT verse that the NIV numbers as two verses, each
# sentence wholly in one of them: record id -> its verses in reader numbering.
READER_RECORDS = {
    "ACT.19.40.s1": ("ACT.19.40",),
    "ACT.19.40.s2": ("ACT.19.41",),   # "With these words he sent the assembly away."
    "2CO.13.12.s1": ("2CO.13.12",),
    "2CO.13.12.s2": ("2CO.13.13",),   # "All God's holy people send you greetings."
}


@lru_cache(maxsize=None)
def _tables():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    english = {refs.parse(h): tuple(refs.parse(e) for e in es)
               for h, es in (data["english"] | OLD_TESTAMENT_HALVES | NEW_TESTAMENT).items()}
    absent = {refs.parse(e) for e in (*data["not_in_hebrew"], *NEW_TESTAMENT_ABSENT)}
    source, chapters = defaultdict(list), defaultdict(set)
    for h, es in english.items():
        for e in es:
            source[e].append(h)
            chapters[h.book, h.chapter].add(e.chapter)
    return english, {e: tuple(hs) for e, hs in source.items()}, absent, dict(chapters)


def to_english(ref):
    """The English-numbered verses that hold the text of one of our verses
    (a Ref), in order: usually one, none for a psalm title, two where the
    Hebrew verse spans two English ones (PSA.13.6 is Psalm 13:5-6)."""
    return _tables()[0].get(ref, (ref,))


def to_source(ref):
    """Our verses that hold the text of one English-numbered verse."""
    english, source, absent, _ = _tables()
    own = () if ref in english or ref in absent else (ref,)
    return tuple(sorted(source.get(ref, ()) + own, key=refs.Ref.sort_key))


def english_ids(verse_ids):
    """The English verse ids for a list of our verse ids, in order, each once."""
    out = []
    for verse_id in verse_ids:
        for ref in to_english(refs.parse(verse_id)):
            if str(ref) not in out:
                out.append(str(ref))
    return out


def to_niv(ref):
    """The verses in reader (NIV) numbering that hold one of our verses:
    to_english() except where the NIV numbers as the SBLGNT does."""
    return (ref,) if str(ref) in NIV_AS_SOURCE else to_english(ref)


def from_niv(ref):
    """Our verses that hold one verse in reader (NIV) numbering."""
    if str(ref) in NIV_AS_SOURCE:
        return (ref,)
    return tuple(r for r in to_source(ref) if str(r) not in NIV_AS_SOURCE)


def niv_ids(verse_ids):
    """The reader (NIV) verse ids for a list of our verse ids, in order, each once."""
    out = []
    for verse_id in verse_ids:
        for ref in to_niv(refs.parse(verse_id)):
            if str(ref) not in out:
                out.append(str(ref))
    return out


def reader_ids(verse_id):
    """The verse ids the site shows readers for one of our verse ids (reader,
    NIV, numbering), as strings: usually one, two where one of our verses
    is two in the NIV (PSA.13.6 is Psalm 13:5-6). A psalm's title, which the
    NIV prints unnumbered above verse 1, is verse 0 of its psalm (PSA.3.1 ->
    PSA.3.0), so it still has a place in its chapter."""
    ref = refs.parse(verse_id)
    niv = to_niv(ref)
    if not niv:
        return (f"{ref.book}.{ref.chapter}.0",)
    return tuple(str(r) for r in niv)


def reader_ids_of(verse_ids):
    """reader_ids() of a list of our verse ids, in order, each once."""
    out = []
    for verse_id in verse_ids:
        for r in reader_ids(verse_id):
            if r not in out:
                out.append(r)
    return out


def record_reader_ids(record_id, verse_ids, segments):
    """A record's verses in reader numbering: READER_RECORDS's for the
    sentences named there, otherwise reader_ids_of(verse_ids), keeping no
    more verses than the text has segments (its verse markers plus one). So
    a verse of ours that is two NIV verses keeps only the first until its
    text marks where the second starts."""
    if record_id in READER_RECORDS:
        return list(READER_RECORDS[record_id])
    return reader_ids_of(verse_ids)[:max(segments, len(verse_ids))]


def from_reader(verse_id):
    """Our verse ids that hold one reader (NIV) verse id (PSA.3.0 -> the
    psalm's title verses)."""
    ref = refs.parse(verse_id)
    if ref.verse == 0:
        return tuple(str(h) for h in _titles().get((ref.book, ref.chapter), ()))
    return tuple(str(r) for r in from_niv(ref))


@lru_cache(maxsize=None)
def _titles():
    out = defaultdict(list)
    for h, es in _tables()[0].items():
        if not es:
            out[h.book, h.chapter].append(h)
    return {k: tuple(sorted(v, key=refs.Ref.sort_key)) for k, v in out.items()}


def english_chapters(book, chapter):
    """The English chapters that hold text of one of our chapters (Hebrew
    Genesis 32:1 is English Genesis 31:55)."""
    return sorted({chapter} | _tables()[3].get((book, chapter), set()))


# Deriving data/versification.json

_ENTRY = re.compile(r'<verse wlc="([^"]+)" kjv="([^"]+)" type="(full|partial)"\s*/>')


def _parse_osis(osis_id):
    """'Ps.13.6!a' -> (Ref, True): the Ref, and whether only part of it is meant."""
    verse, _, part = osis_id.partition("!")
    book, chapter, number = verse.split(".")
    return refs.Ref(refs.OSIS_TO_CODE[book], int(chapter), int(number)), bool(part)


def derive(verse_map_xml, hebrew_refs):
    """From the text of OSHB's VerseMap.xml and the set of the WLC's verse
    Refs, return {WLC Ref: (English Refs)} for every WLC verse not numbered
    the same in both, and the set of renumbered English Refs that are not WLC
    verses.

    Each map entry pairs a WLC verse (or half of one, "!a"/"!b") with a KJV
    verse (or half). A WLC verse overlaps the KJV verses it is paired with,
    and also the KJV verse with its own number unless an entry pairs either
    of them whole with something else. The map pairs the second verse of a
    two-verse psalm title (PSA.51.2) whole with English verse 1 as well as
    the verse that is verse 1 (PSA.51.3), since it "did not distinguish" the
    title from verse 1; where several WLC verses are paired whole with one
    KJV verse, only the last is kept, so the title has no English verse.
    """
    entries = [(*_parse_osis(w), *_parse_osis(k), kind)
               for w, k, kind in _ENTRY.findall(verse_map_xml)]
    if not entries:
        raise ValueError("no entries found in VerseMap.xml")
    whole = defaultdict(list)
    for entry in entries:
        w, _, k, k_part, kind = entry
        if kind == "full" and not k_part:
            whole[k].append(entry)
    titles = {e for es in whole.values()
              for e in sorted(es, key=lambda e: e[0].verse)[:-1]}
    paired = defaultdict(set)
    renumbered = set()
    for entry in entries:
        w, w_part, k, k_part, _ = entry
        if not w_part:
            renumbered.add(w)
        if not k_part:
            renumbered.add(k)
        if entry not in titles:
            paired[w].add(k)
    out, absent = {}, set()
    for ref in set(paired) | renumbered:
        if ref not in hebrew_refs:
            absent.add(ref)
            continue
        english = paired.get(ref, set()) | ({ref} if ref not in renumbered else set())
        english = tuple(sorted(english, key=refs.Ref.sort_key))
        if english != (ref,):
            out[ref] = english
    return out, absent


def dumps(table, absent, commit):
    """The text of data/versification.json for a derive() table: one verse
    to a line, so changes are easy to read in a diff."""
    lines = [f'    "{h}": {json.dumps([str(e) for e in table[h]])}'
             for h in sorted(table, key=refs.Ref.sort_key)]
    missing = [str(e) for e in sorted(absent, key=refs.Ref.sort_key)]
    head = {"about": "WLC verse id -> English (KJV-numbered) verse ids, for verses not "
                     "numbered the same; see owb/versification.py.",
            "source": f"Open Scriptures Hebrew Bible (CC BY 4.0), {VERSE_MAP} at {commit}"}
    return ("{\n" + "".join(f"  {json.dumps(k)}: {json.dumps(v)},\n" for k, v in head.items())
            + '  "english": {\n' + ",\n".join(lines) + "\n  },\n"
            + f'  "not_in_hebrew": {json.dumps(missing)}\n}}\n')
