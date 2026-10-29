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
both, except the few New Testament verses in NEW_TESTAMENT below.

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


@lru_cache(maxsize=None)
def _tables():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    english = {refs.parse(h): tuple(refs.parse(e) for e in es)
               for h, es in (data["english"] | NEW_TESTAMENT).items()}
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
