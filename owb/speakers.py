"""Who speaks in each sentence, for the reader's speaker labels (a pilot;
docs/speakers.md).

data/speakers/<BOOK>.json names, for every record of the book, the voice
that holds most of the sentence ("narrator", "god", "job", ...), and gives
each voice's name in every language:

    {"description": ..., "status": "ai_draft",
     "speakers": {"eliphaz": {"en": "Eliphaz", "es": "Elifaz", ...}, ...},
     "records": {"JOB.4.1.s1": "narrator", "JOB.4.2.s1": "eliphaz", ...}}

Like headings, this is an editorial aid, not translation: it says who
speaks, the same in every language, and uses no reader settings. The
reader shows a voice's name where the speaker changes (labels()).
"""
import functools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "data" / "speakers"


@functools.cache
def load(book):
    """The book's speaker file, or None."""
    path = DIR / f"{book}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def labels(book, record_ids, lang):
    """{record id: speaker's name in lang (English where it has none)} for the
    records of one chapter, in order, where the voice changes: the first
    record, and each whose speaker differs from the one before."""
    data = load(book)
    if not data:
        return {}
    out, before = {}, None
    for rid in record_ids:
        who = data["records"].get(rid)
        if who and who != before:
            names = data["speakers"][who]
            out[rid] = names.get(lang) or names["en"]
        before = who or before
    return out


def errors(book, records, languages):
    """What is wrong with a book's speaker file, against its records."""
    data = load(book)
    found = []
    if data["status"] != "ai_draft":
        found.append(f"{book}: status must be ai_draft until a named reviewer approves it")
    ids = {r["id"] for r in records}
    for rid, who in data["records"].items():
        if rid not in ids:
            found.append(f"{rid}: no such record")
        if who not in data["speakers"]:
            found.append(f"{rid}: {who!r} is not a listed speaker")
    for rid in sorted(ids - set(data["records"])):
        found.append(f"{rid}: no speaker")
    for who, names in data["speakers"].items():
        missing = [lang for lang in languages if not names.get(lang)]
        if missing:
            found.append(f"speaker {who}: no name in {', '.join(missing)}")
        if any("{{" in n for n in names.values()):
            found.append(f"speaker {who}: a name may not hold a reader setting")
    return found
