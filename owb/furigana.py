"""Furigana: the reading of each run of kanji in a Japanese rendering, so
the reader can set it over the kanji (ruby) for readers still learning
them. A reading aid, like the transliterations: it changes no wording and
no meaning, and is drafted and reviewed like any other text.

data/furigana/<BOOK>.json holds, by record id, language and level, the
runs in the order they appear, each with its reading in hiragana:

    {"JHN.1.5.s1": {"ja": {"B": [["光", "ひかり"], ["闇", "やみ"], ["中", "なか"], ...]}}}

A run is a whole run of kanji (the characters between kana or punctuation),
found after the end of the one before, as alignments are. scripts/furigana.py
shows the runs of a passage and writes a spec into this file.
"""
import functools
import json
import re
from pathlib import Path

from owb import markup

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "data" / "furigana"

KANJI = r"々㐀-䶿一-鿿豈-﫿"
RUN = re.compile(f"[{KANJI}]+")
KANA = re.compile(r"^[ぁ-ゟー]+$")


def runs(text):
    """The kanji runs of a rendering, outside setting spans: [(start, end, run)]."""
    inside = [(s.start, s.end) for s in markup.spans(text)]
    return [(m.start(), m.end(), m.group()) for m in RUN.finditer(text)
            if not any(a <= m.start() < b for a, b in inside)]


def ranges(text, items):
    """[[start, end, reading], ...] for items [[run, reading], ...] in text,
    each a whole kanji run found after the one before. Raises ValueError
    naming the first item that breaks a rule."""
    found = runs(text)
    out, at = [], 0
    for i, item in enumerate(items):
        if not (isinstance(item, list) and len(item) == 2 and all(isinstance(x, str) for x in item)):
            raise ValueError(f"{i}: should be [kanji, reading]")
        run, reading = item
        if not KANA.match(reading):
            raise ValueError(f"{i}: reading {reading!r} for {run!r} is not hiragana")
        hit = next((r for r in found if r[2] == run and r[0] >= at), None)
        if hit is None:
            raise ValueError(f"{i}: {run!r} is not a run of kanji after the previous one")
        out.append([hit[0], hit[1], reading])
        at = hit[1]
    return out


@functools.cache
def book(code):
    path = DIR / f"{code}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def record_ranges(record):
    """{lang: {level: ranges}} for a record, leaving out any level whose
    readings no longer fit its rendering (scripts/check.sh reports those)."""
    mine = book(record["id"].split(".")[0]).get(record["id"], {})
    out = {}
    for lang, levels in mine.items():
        for level, items in levels.items():
            text = record["renderings"].get(lang, {}).get(level)
            if text is None:
                continue
            try:
                out.setdefault(lang, {})[level] = ranges(text, items)
            except ValueError:
                continue
    return out


def errors(records_by_id):
    """Problems in data/furigana/ against the records: readings for a
    record, language or level that does not exist, or that no longer fit
    the rendering."""
    out = []
    for path in sorted(DIR.glob("*.json")):
        for rid, langs in json.loads(path.read_text(encoding="utf-8")).items():
            r = records_by_id.get(rid)
            if r is None:
                out.append(f"{path.name}: {rid}: no such record")
                continue
            for lang, levels in langs.items():
                for level, items in levels.items():
                    text = r["renderings"].get(lang, {}).get(level)
                    if text is None:
                        out.append(f"{path.name}: {rid}: no {lang}/{level} rendering")
                        continue
                    try:
                        ranges(text, items)
                    except ValueError as e:
                        out.append(f"{path.name}: {rid} {lang}/{level}: {e}")
    return out
