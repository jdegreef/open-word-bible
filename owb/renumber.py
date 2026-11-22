"""Readers' saved verses, from our verse numbers to the NIV's.

Until the site switched to NIV numbering (live 2026-11-21 13:40 UTC), the
reader keyed a reader's bookmarks, highlights, notes, passage notes, verses
being memorized and reading place by our own verse ids, which in the Old
Testament follow the Hebrew Bible (Psalm 3's title was PSA.3.1, Malachi 4:1
was MAL.3.19). Since then it keys them by the verse ids readers see
(versification.reader_ids). Anything saved before the switch is moved here,
by when it was saved: in the account's database by a migration
(accounts/migrations), in the browser by web/site.js with table(), and in a
copy sent by a browser that has not moved its own yet (accounts/reading.py).

A verse of ours that the NIV splits in two goes to the first of them; two of
ours that the NIV makes one meet there, and merge() keeps both readers'
changes as well as it can (the later wins, notes are joined)."""
from functools import lru_cache

from . import refs, versification

# When the site in NIV numbering went live (Render's deploy of main at
# ade421e succeeded at 2026-11-21T13:40:00Z), in milliseconds: the
# reader's "at" and the database's updated_at are kept so.
SWITCHED_MS = 1795268400000


@lru_cache(maxsize=None)
def table():
    """{our verse id: [first, last] reader verse id} for each verse whose
    number changed; every other verse keeps its id."""
    out = {}
    for ref in versification._tables()[0]:
        ours = str(ref)
        theirs = versification.reader_ids(ours)
        if theirs != (ours,):
            out[ours] = [theirs[0], theirs[-1]]
    return dict(sorted(out.items(), key=lambda kv: refs.Ref.sort_key(refs.parse(kv[0]))))


def verse(verse_id):
    """A verse id in reader numbering (the first, where the NIV has two)."""
    return table().get(verse_id, [verse_id])[0]


def passage(key):
    """A verse or a range of one chapter's verses ("PSA.3.1-8") in reader
    numbering. A range whose verses land in two NIV chapters keeps those in
    the chapter it starts in."""
    if "-" not in key:
        return verse(key)
    first, end = key.rsplit("-", 1)
    try:
        start, end = refs.parse(first), int(end)
    except (ValueError, KeyError):
        return key
    ids = [f"{start.book}.{start.chapter}.{v}" for v in range(start.verse, end + 1)]
    if not any(i in table() for i in ids):
        return key
    a = refs.parse(verse(first))
    moved = [refs.parse(r) for i in ids for r in table().get(i, [i])]
    last = max((r.verse for r in moved if (r.book, r.chapter) == (a.book, a.chapter)), default=a.verse)
    return str(a) if last <= a.verse else f"{a}-{last}"


def old(at):
    """Whether something saved at this time (ms) was keyed by our numbers."""
    return isinstance(at, (int, float)) and 0 <= at < SWITCHED_MS


def merge(a, b):
    """Two saved entries ({..., "at"}) that now share a verse: the later
    one's fields over the earlier one's, the notes joined and the
    collections of both."""
    first, later = sorted((a, b), key=lambda m: m.get("at", 0))
    out = {**first, **later}
    notes = [m.get("n") for m in (first, later) if m.get("n")]
    if notes:
        out["n"] = "\n\n".join(dict.fromkeys(notes))
    tags = list(dict.fromkeys((first.get("t") or []) + (later.get("t") or [])))
    if tags:
        out["t"] = tags[:20]
    return out


def store(entries, key=passage):
    """A browser's {verse or range: entry} with those saved before the
    switch moved to reader numbering."""
    out = {}
    for k, entry in entries.items():
        at = entry.get("at", 0) if isinstance(entry, dict) else 0
        new = key(k) if old(at) else k
        out[new] = merge(out[new], entry) if new in out and isinstance(entry, dict) else entry
    return out


def place(p):
    """A reading place {book, chapter, verse: "16" or "7:53", at}."""
    if not isinstance(p, dict) or not old(p.get("at", 0)):
        return p
    v = str(p.get("verse", ""))
    chapter = p.get("chapter")
    if ":" in v:
        chapter, v = v.split(":", 1)
    try:
        ours = f"{p['book']}.{int(chapter)}.{int(v)}"
    except (ValueError, KeyError, TypeError):
        return p
    if ours not in table():
        return p
    moved = refs.parse(verse(ours))
    out = dict(p)
    out["chapter"] = moved.chapter
    out["verse"] = str(moved.verse)
    return out
