"""Cross-references: for each verse, the other passages most worth reading
beside it, shown in the reader's margin.

They come from OpenBible.info's crowd-voted list (owb/sources/openbible.py,
CC BY), kept in data/crossrefs/<BOOK>.json by scripts/extract_crossrefs.py so
the site never needs the source clone. Like section headings they are an
editorial aid, not translation, and are labelled with their source.

Both ends are in our verse numbering (owb/versification.py): OpenBible
numbers the Old Testament as English Bibles do, so Psalm 23:1 there is our
PSA.23.2. A verse keeps at most PER_VERSE references, each with at least
MIN_VOTES votes, most voted first, so the reader can show the best few. A
reference is written

    "ISA.40.11"           one verse
    "EZK.34.11-12"        verses of one chapter
    "GEN.1.31-2.3"        a passage that runs into the next chapter

A file holds {"about": ..., "source": ..., "refs": {"PSA.23.2": [...], ...}},
one verse to a line, so an update to the source reads as a small diff.
"""
import functools
import json
import re
from collections import defaultdict
from pathlib import Path

from owb import refs, versification

DATA = Path(__file__).resolve().parents[1] / "data" / "crossrefs"
MIN_VOTES = 3
PER_VERSE = 5
TARGET = re.compile(r"([1-3]?[A-Z]{2,3})\.(\d+)\.(\d+)(?:-(?:(\d+)\.)?(\d+))?")


def format_target(first, last):
    if first == last:
        return str(first)
    if first.chapter == last.chapter:
        return f"{first}-{last.verse}"
    return f"{first}-{last.chapter}.{last.verse}"


def parse_target(text):
    """'GEN.1.31-2.3' -> (Ref GEN.1.31, Ref GEN.2.3)."""
    m = TARGET.fullmatch(text)
    if not m:
        raise ValueError(f"bad cross-reference: {text!r}")
    first = refs.parse(f"{m[1]}.{m[2]}.{m[3]}")
    if m[5] is None:
        return first, first
    return first, refs.Ref(first.book, int(m[4] or first.chapter), int(m[5]))


def select(rows, verses):
    """{our Ref: [target text, ...]} from OpenBible rows (owb.sources.openbible)
    and the set of verse Refs our sources have.

    A row's verses are moved to our numbering; one whose ends we do not have
    (a verse SBLGNT leaves out, such as Matt 17:21) is dropped, as is one that
    points at the verse itself. Where two English verses make one of ours,
    their references are merged, each keeping its highest vote."""
    best = defaultdict(dict)
    for row in rows:
        first, last = versification.to_source(row.first), versification.to_source(row.last)
        if not first or not last:
            continue
        first, last = first[0], last[-1]
        if first not in verses or last not in verses:
            continue
        if last.sort_key() < first.sort_key():
            last = first
        for source in versification.to_source(row.source):
            if source not in verses or refs.in_range(source, first, last):
                continue
            votes = best[source]
            votes[first, last] = max(row.votes, votes.get((first, last), row.votes))
    out = {}
    for source, votes in best.items():
        ranked = sorted((v for v in votes.items() if v[1] >= MIN_VOTES),
                        key=lambda v: (-v[1], v[0][0].sort_key(), v[0][1].sort_key()))
        if ranked:
            out[source] = [format_target(*span) for span, _ in ranked[:PER_VERSE]]
    return out


def dumps(book, table, source):
    """The text of data/crossrefs/<book>.json for a select() table."""
    lines = [f"    {json.dumps(str(r))}: {json.dumps(table[r])}"
             for r in sorted((r for r in table if r.book == book), key=refs.Ref.sort_key)]
    head = {"about": "Cross-references for each verse, most voted first, in Open Word Bible "
                     "verse numbering; see owb/crossrefs.py.",
            "source": source}
    return ("{\n" + "".join(f"  {json.dumps(k)}: {json.dumps(v)},\n" for k, v in head.items())
            + '  "refs": {\n' + ",\n".join(lines) + "\n  }\n}\n")


@functools.lru_cache(maxsize=None)
def load(book):
    """{verse id: [target text, ...]} for one book, or {} if it has none."""
    path = DATA / f"{book}.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))["refs"]
