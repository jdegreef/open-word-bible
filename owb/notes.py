"""Translations of the English editorial text into the reading languages:
decision notes (data/notes/<lang>/<BOOK>.json) and the reader's cards
(data/cards/<lang>/glossary.json, names.json, key_terms.json).

content/ keeps every decision's choice, alternatives and reason in English,
and data/glossary.json, data/names.json and data/key_terms.json state their
senses in English. A translation sits beside them, one file per language
(and, for notes, per book, like data/headings/ and data/summaries/), so
pull requests for different languages or books touch different files, and
scripts/merge_json.py merges the rest.

Each translated entry carries `source`: a digest of the English it was
translated from (decision_digest, card_digest), as an article translation
does (scripts/check_translations.py). When the English changes the digests
differ, the entry is stale, and the site shows the English again until the
translation is brought up to date. scripts/notes.py exports what is missing
or stale, imports translations, and reports coverage; docs/notes-translation.md
is the workflow.

A translation follows the rules of what it translates: it states the sense
only, has no reader settings ({{setting:...}} spans), copies any Greek or
Hebrew from the source data (owb.validate's check), and keeps the English
number of alternatives. check_notes_file and check_cards_file apply them;
`python3 -m owb.validate` runs them on a note or card file it is given, and
tests/test_notes.py runs them on every file.
"""
import functools
import hashlib
import json
import re
from pathlib import Path

from owb import languages, markup, refs

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "data" / "notes"
CARDS = ROOT / "data" / "cards"
CONTENT = ROOT / "content"

NOTE_FIELDS = ("choice", "alternatives", "reason")
# The card files, and the key their entries are under (in data/ and in a
# translation alike, except key_terms.json, whose English list is "terms").
CARD_KINDS = {"glossary": "glossary", "names": "names", "key_terms": "terms"}
DIGEST = re.compile(r"[0-9a-f]{12}")
# Greek or Hebrew in an exported English text is replaced by ⟦1⟧, ⟦2⟧, ...
# so a translator never retypes it; import puts the words back, copied from
# the English (expand).
SLOT = re.compile("⟦(\\d+)⟧")
STATUSES = ("ai_draft", "meaning_reviewed", "reviewed", "revised")


def _digest(value):
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def decision_digest(d):
    """The digest of what a note translates: the decision's English choice,
    alternatives and reason."""
    return _digest([d["choice"], list(d.get("alternatives") or []), d["reason"]])


def card_digest(kind, entry):
    """The digest of what a card translation translates: each sense's name
    and note (glossary, names), or a key term's sense and note."""
    if kind == "key_terms":
        return _digest([entry["sense"], entry.get("note", "")])
    return _digest([[s["name"], s["note"]] for s in entry["senses"]])


def card_key(kind, entry):
    """A card's key in a translation file: "<strong>|<lemma>" for glossary
    and names entries (H7676|<lemma>), "<language>|<strong>" for a key term
    (grc|5485, hbo|3068), as owb.validate keys key terms."""
    if kind == "key_terms":
        return f"{entry.get('language', 'grc')}|{entry['strong']}"
    return f"{entry['strong']}|{entry['lemma']}"


# ---------------------------------------------------------------- English


@functools.lru_cache(maxsize=None)
def book_records(book):
    """A book's records as content/ stores them (straight quotes, the text
    the digests are taken of), in file order."""
    out = []
    for path in sorted((CONTENT / book).glob("*.json")):
        out += json.loads(path.read_text(encoding="utf-8"))["records"]
    return tuple(out)


@functools.lru_cache(maxsize=None)
def book_decisions(book):
    """{record id: {decision id: decision}} for a book."""
    return {r["id"]: {d["id"]: d for d in r["decisions"]} for r in book_records(book)}


def books():
    """Every book with content, in canonical order."""
    found = {p.name for p in CONTENT.iterdir() if p.is_dir()} if CONTENT.is_dir() else set()
    return [b for b in refs.BOOK_CODES if b in found]


def translatable(d, lang):
    """Whether a note in lang may translate decision d: every meaning
    decision, and lang's own rendering decisions."""
    return d["layer"] == "meaning" or d.get("language") == lang


@functools.lru_cache(maxsize=None)
def english_cards(kind):
    """{key: entry} of data/<kind>.json."""
    path = ROOT / "data" / f"{kind}.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {card_key(kind, e): e for e in data[CARD_KINDS[kind]]}


# ---------------------------------------------------------- translations


def notes_path(lang, book):
    return NOTES / lang / f"{book}.json"


def cards_path(lang, kind):
    return CARDS / lang / f"{kind}.json"


def _read(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


@functools.lru_cache(maxsize=None)
def load_notes(lang, book):
    """{record id: {decision id: entry}} of data/notes/<lang>/<BOOK>.json."""
    data = _read(notes_path(lang, book))
    return data["notes"] if data else {}


@functools.lru_cache(maxsize=None)
def load_cards(lang, kind):
    """{key: entry} of data/cards/<lang>/<kind>.json."""
    data = _read(cards_path(lang, kind))
    return data[kind] if data else {}


def current_notes(lang, book):
    """{record id: {decision id: {"choice", "alternatives", "reason"}}}: the
    notes in lang whose English has not changed since they were translated.
    A stale note is left out, so the English shows instead."""
    english = book_decisions(book)
    out = {}
    for rid, entries in load_notes(lang, book).items():
        for did, entry in entries.items():
            d = english.get(rid, {}).get(did)
            if d and entry.get("source") == decision_digest(d):
                out.setdefault(rid, {})[did] = {k: entry[k] for k in NOTE_FIELDS}
    return out


def current_card(lang, kind, key):
    """A card's translation in lang if its English has not changed since,
    else None."""
    entry = load_cards(lang, kind).get(key)
    english = english_cards(kind).get(key)
    if entry and english and entry.get("source") == card_digest(kind, english):
        return entry
    return None


def note_template(lang):
    return {"description": (
        "Translations of decision notes (choice, alternatives, reason), which content/ keeps "
        "in English, keyed by record id and decision id. \"source\" is a digest of the "
        "English each was translated from (owb/notes.py); when the English changes the note "
        "is stale and the site shows the English until it is translated again. They state "
        "the sense only and use no reader settings. Every note is an AI draft until a named "
        "reviewer approves it. See docs/notes-translation.md."),
        "status": "ai_draft", "language": lang, "notes": {}}


def card_template(lang, kind):
    what = {"glossary": "glossary cards (data/glossary.json)",
            "names": "name cards (data/names.json)",
            "key_terms": "key terms' senses and notes (data/key_terms.json)"}[kind]
    keyed = ("\"<language>|<Strong's number>\", as owb.validate keys key terms"
             if kind == "key_terms" else "\"<Strong's number>|<lemma>\", the lemma copied from the source data")
    return {"description": (
        f"Translations of the {what}, keyed by {keyed}. \"source\" is a digest of the English "
        "each was translated from (owb/notes.py); when the English changes the card is stale "
        "and the site shows the English until it is translated again. They state the sense "
        "only and use no reader settings. Every entry is an AI draft until a named reviewer "
        "approves it. See docs/notes-translation.md."),
        "status": "ai_draft", "language": lang, kind: {}}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ordered_notes(book, notes):
    """notes ({record id: {decision id: entry}}) in the book's record and
    decision order, so a file's diff only shows what changed. Entries for a
    record or decision that is gone come last."""
    out = {}
    for r in book_records(book):
        if r["id"] in notes:
            got = notes[r["id"]]
            ids = [d["id"] for d in r["decisions"] if d["id"] in got]
            out[r["id"]] = {did: got[did] for did in ids + [k for k in got if k not in ids]}
    out.update({rid: v for rid, v in notes.items() if rid not in out})
    return out


# ------------------------------------------------------- Greek and Hebrew


def original_words(text):
    """The Greek and Hebrew words in text, in order, as owb.validate finds
    them."""
    from owb import validate
    found = []
    for m in sorted((m for pattern, _ in validate._SCRIPTS.values() for m in pattern.finditer(text)),
                    key=lambda m: m.start()):
        found.append(m)
    return found


def slot_words(texts):
    """The distinct Greek and Hebrew words in some English texts, in order:
    slot n is words[n - 1]."""
    words = []
    for text in texts:
        for m in original_words(text):
            if m[0] not in words:
                words.append(m[0])
    return words


def decision_texts(d):
    """A decision's English texts, in the order slots are numbered."""
    return [d["choice"], *d.get("alternatives", []), d["reason"]]


def card_texts(kind, entry):
    """A card's English texts, in the order slots are numbered."""
    if kind == "key_terms":
        return [entry["sense"], entry.get("note", "")]
    return [x for s in entry["senses"] for x in (s["name"], s["note"])]


def to_slots(text, words):
    """text with each Greek or Hebrew word replaced by its slot ⟦n⟧."""
    out, last = [], 0
    for m in original_words(text):
        out += [text[last:m.start()], f"⟦{words.index(m[0]) + 1}⟧"]
        last = m.end()
    return "".join(out) + text[last:]


def expand(text, words):
    """text with each slot ⟦n⟧ replaced by its word; raises KeyError for a
    slot the English has no word for."""
    def put(m):
        n = int(m[1])
        if not 1 <= n <= len(words):
            raise KeyError(m[0])
        return words[n - 1]
    return SLOT.sub(put, text)


# ------------------------------------------------------------- checking


def check_text(text, where, errors):
    """The rules every translated string follows: non-empty text, no reader
    setting, no slot or drafting placeholder left, and Greek or Hebrew only
    as copied from the source data."""
    from owb import validate
    if not isinstance(text, str) or not text.strip():
        errors.append(f"{where}: must be a non-empty string")
        return
    if markup.spans(text) or markup.stray_braces(text):
        errors.append(f"{where}: a reader setting is wording; a translated note states the sense only")
    if SLOT.search(text):
        errors.append(f"{where}: slot {SLOT.search(text)[0]} left in the text (scripts/notes.py import fills them)")
    if validate.PLACEHOLDER.search(text):
        errors.append(f"{where}: placeholder {validate.PLACEHOLDER.search(text)[0]!r} left in the text")
    for script, (pattern, forms) in validate._SCRIPTS.items():
        for word in pattern.findall(text):
            if word not in forms():
                errors.append(f"{where}: {script} {word!r} is not a form or lemma in the source "
                              "data; copy it from the English note")


def check_note(entry, d, where, errors, lang=None):
    """A translated note against its English decision d. A note whose
    English has changed (stale) is only checked for its shape: it is not
    shown, and will be translated again."""
    if not isinstance(entry, dict):
        errors.append(f"{where}: must be an object")
        return
    for key in sorted(set(entry) - {"source", *NOTE_FIELDS}):
        errors.append(f"{where}: unknown field {key!r}")
    for key in ("source", *NOTE_FIELDS):
        if key not in entry:
            errors.append(f"{where}: missing {key!r}")
    if not (isinstance(entry.get("source"), str) and DIGEST.fullmatch(entry["source"])):
        errors.append(f"{where}.source: must be the 12-character digest of the English")
    if lang and d is not None and not translatable(d, lang):
        errors.append(f"{where}: {d['id']} is another language's rendering decision")
    check_text(entry.get("choice"), f"{where}.choice", errors)
    check_text(entry.get("reason"), f"{where}.reason", errors)
    alts = entry.get("alternatives")
    if not isinstance(alts, list):
        errors.append(f"{where}.alternatives: must be a list")
        alts = []
    for i, alt in enumerate(alts):
        check_text(alt, f"{where}.alternatives[{i}]", errors)
    if d is not None and entry.get("source") == decision_digest(d) and len(alts) != len(d["alternatives"]):
        errors.append(f"{where}.alternatives: {len(alts)} given, the English has {len(d['alternatives'])}")


def _check_header(data, lang, key, errors, where):
    if not isinstance(data, dict):
        errors.append(f"{where}: must be a JSON object")
        return False
    for k in sorted(set(data) - {"description", "status", "language", key}):
        errors.append(f"{where}: unknown field {k!r}")
    if data.get("status") not in STATUSES:
        errors.append(f"{where}: status {data.get('status')!r} not allowed")
    if data.get("language") != lang:
        errors.append(f"{where}: language {data.get('language')!r} should be {lang!r} (its folder)")
    if not isinstance(data.get(key), dict):
        errors.append(f"{where}: {key!r} must be an object")
        return False
    return True


def _lang_of(path, root):
    lang = path.parent.name
    if path.parent.parent != root or lang not in languages.READING or lang == "en":
        return None
    return lang


def check_notes_file(path):
    """Error strings for data/notes/<lang>/<BOOK>.json (empty when valid)."""
    path = Path(path).resolve()
    where = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    lang, book = _lang_of(path, NOTES), path.stem
    if lang is None:
        return [f"{where}: not data/notes/<language>/<BOOK>.json for a reading language other than English"]
    if book not in refs.BOOK_CODES:
        return [f"{where}: {book!r} is not a book code"]
    errors = []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not _check_header(data, lang, "notes", errors, where):
        return errors
    english = book_decisions(book)
    for rid, entries in data["notes"].items():
        if not isinstance(entries, dict):
            errors.append(f"{where}: {rid}: must be an object of decision id -> note")
            continue
        for did, entry in entries.items():
            # A note whose record or decision is gone (orphaned) is never
            # shown; scripts/notes.py report counts it, and it is checked
            # for its shape only, so editing the English never fails here.
            check_note(entry, english.get(rid, {}).get(did), f"{where}: {rid}.{did}", errors, lang)
    return errors


def check_card(kind, entry, english, where, errors):
    """A translated card against its English entry. A stale one is only
    checked for its shape."""
    fields = {"source", "sense", "note"} if kind == "key_terms" else {"source", "senses"}
    for k in sorted(set(entry) - fields):
        errors.append(f"{where}: unknown field {k!r}")
    if not (isinstance(entry.get("source"), str) and DIGEST.fullmatch(entry["source"])):
        errors.append(f"{where}.source: must be the 12-character digest of the English")
    current = english is not None and entry.get("source") == card_digest(kind, english)
    if kind == "key_terms":
        check_text(entry.get("sense"), f"{where}.sense", errors)
        if (english or {}).get("note") or "note" in entry:
            check_text(entry.get("note"), f"{where}.note", errors)
        return
    senses = entry.get("senses")
    if not isinstance(senses, list):
        errors.append(f"{where}.senses: must be a list")
        return
    if current and len(senses) != len(english["senses"]):
        errors.append(f"{where}.senses: {len(senses)} given, the English has {len(english['senses'])}")
    for i, s in enumerate(senses):
        if not isinstance(s, dict) or set(s) != {"name", "note"}:
            errors.append(f"{where}.senses[{i}]: must be {{\"name\", \"note\"}}")
            continue
        check_text(s["name"], f"{where}.senses[{i}].name", errors)
        check_text(s["note"], f"{where}.senses[{i}].note", errors)


def check_cards_file(path):
    """Error strings for data/cards/<lang>/<kind>.json (empty when valid)."""
    path = Path(path).resolve()
    where = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    lang, kind = _lang_of(path, CARDS), path.stem
    if lang is None or kind not in CARD_KINDS:
        return [f"{where}: not data/cards/<language>/{{{','.join(CARD_KINDS)}}}.json"]
    errors = []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not _check_header(data, lang, kind, errors, where):
        return errors
    english = english_cards(kind)
    for key, entry in data[kind].items():
        at = f"{where}: {key}"
        if not isinstance(entry, dict):
            errors.append(f"{at}: must be an object")
            continue
        # An entry whose English is gone (orphaned) is checked for its shape
        # only; scripts/notes.py report counts it.
        check_card(kind, entry, english.get(key), at, errors)
    return errors


def check_file(path):
    """check_notes_file or check_cards_file, by where the file is."""
    path = Path(path).resolve()
    if path.is_relative_to(CARDS):
        return check_cards_file(path)
    return check_notes_file(path)


def is_translation_file(path):
    path = Path(path).resolve()
    return path.suffix == ".json" and (path.is_relative_to(NOTES) or path.is_relative_to(CARDS))


def all_files():
    """Every note and card translation file."""
    return sorted(NOTES.glob("*/*.json")) + sorted(CARDS.glob("*/*.json"))
