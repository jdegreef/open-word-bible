"""Validate sentence records (stdlib only).

Checks the rules in schema/sentence-record.schema.json that matter most, plus
what a schema cannot: every token id exists in the MACULA data for the
record's verses, generated source text matches the data, every Greek or
Hebrew word anywhere else in the record is a form or lemma copied from the
source data, a Greek record holds one whole source sentence, and every {{setting:...}} span names a known setting.

Usage: python3 -m owb.validate content/en/JHN/JHN.1.1-2.json [...]
"""
import json
import re
import sys
from pathlib import Path

from owb import markup, refs
from owb.sources import macula_greek, macula_hebrew

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "schema" /
                     "sentence-record.schema.json").read_text(encoding="utf-8"))
_DEFS = SCHEMA["$defs"]
_PROPS = SCHEMA["properties"]
STATUSES = _PROPS["status"]["enum"]
TEXT_IDS = _PROPS["source"]["properties"]["text_id"]["enum"]
SOURCE_LANGUAGES = _PROPS["source"]["properties"]["language"]["enum"]
LEVELS = _DEFS["level"]["enum"]
LAYERS = _DEFS["decision"]["properties"]["layer"]["enum"]
CATEGORIES = _DEFS["decision"]["properties"]["category"]["enum"]
RECORD_ID = re.compile(_PROPS["id"]["pattern"])
LANGUAGE = re.compile(_DEFS["language"]["pattern"])

# Runs of Greek or Hebrew letters and their marks. Punctuation (ano teleia,
# maqaf, sof pasuq, elision marks) ends a word.
_SCRIPTS = {
    "Greek": (re.compile("[\u0300-\u036f\u0370-\u0373\u0376-\u037d"
                         "\u0386\u0388-\u03ff\u1f00-\u1fff]+"),
              macula_greek.forms),
    "Hebrew": (re.compile("[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5"
                          "\u05c7\u05d0-\u05f2\ufb1d-\ufb4f]+"),
               macula_hebrew.forms),
}


def _fields(obj, schema_obj, where, errors):
    """Check required and unknown keys of obj against a schema object."""
    if not isinstance(obj, dict):
        errors.append(f"{where}: must be an object")
        return False
    for key in schema_obj["required"]:
        if key not in obj:
            errors.append(f"{where}: missing {key!r}")
    for key in obj:
        if key not in schema_obj["properties"]:
            errors.append(f"{where}: unknown field {key!r}")
    return True


def _check_markup(text, where, errors):
    if not isinstance(text, str):
        errors.append(f"{where}: must be a string")
        return
    if markup.stray_braces(text):
        errors.append(f"{where}: malformed {{{{...}}}} span")
    for span in markup.spans(text):
        if span.setting not in markup.SETTINGS:
            errors.append(f"{where}: unknown setting {span.setting!r}")


def _strings(obj, where):
    """Yield (where, string) for every string inside obj."""
    if isinstance(obj, str):
        yield where, obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            yield from _strings(value, f"{where}.{key}" if where else key)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from _strings(value, f"{where}[{i}]")


def check_original_language(record, errors):
    """Every Greek or Hebrew word outside source must be copied from the
    source data: it must equal, code point for code point, a word form or
    lemma in MACULA. A word typed by hand usually differs in an accent,
    breathing or vowel point, or is not a real form at all."""
    for where, text in _strings({k: v for k, v in record.items() if k != "source"}, ""):
        for script, (pattern, forms) in _SCRIPTS.items():
            for word in pattern.findall(text):
                if word not in forms():
                    errors.append(f"{where}: {script} {word!r} is not a form or lemma "
                                  "in the source data; copy it from MACULA")


def check_sentence(tokens, decisions, errors):
    """A Greek record holds one source sentence: it ends where the SBLGNT
    ends a sentence (full stop, question mark or raised dot) and has no full
    stop or question mark inside. A meaning decision in the punctuation
    category exempts the record, since it reads the text's punctuation
    differently (as John 1:3 does with the last two words)."""
    if any(isinstance(d, dict) and d.get("layer") == "meaning"
           and d.get("category") == "punctuation" for d in decisions):
        return
    ends = macula_greek.FULL_STOPS + macula_greek.RAISED_DOT
    if not any(c in tokens[-1].after for c in ends):
        errors.append(f"source.tokens: the record ends mid-sentence at {tokens[-1].id}; "
                      "extend it to the end of the sentence, or add a punctuation "
                      "meaning decision")
    for tok in tokens[:-1]:
        if any(c in tok.after for c in macula_greek.FULL_STOPS):
            errors.append(f"source.tokens: a sentence ends at {tok.id}; split the record "
                          "there, or add a punctuation meaning decision")


def source_text(tokens):
    """The source text of a token list, rebuilt from the MACULA data."""
    return " ".join(t.text + t.after.rstrip() for t in tokens)


def validate_record(record, known_tokens=None, original_language=True):
    """Return a list of error strings (empty if the record is valid).

    known_tokens maps token id -> Token; by default it is loaded from MACULA
    for the record's refs. original_language=False skips the check of Greek
    and Hebrew quoted outside source, which needs the whole MACULA data.
    """
    errors = []
    if not _fields(record, SCHEMA, "record", errors):
        return errors
    rid = record.get("id", "?")
    if not (isinstance(rid, str) and RECORD_ID.fullmatch(rid)):
        errors.append(f"id: bad record id {rid!r}")

    verse_ids = record.get("refs") or []
    for vid in verse_ids:
        try:
            refs.parse(vid)
        except (ValueError, TypeError):
            errors.append(f"refs: bad verse id {vid!r}")
    if errors:
        return errors
    if known_tokens is None:
        known_tokens = macula_greek.tokens_for_refs(verse_ids)

    source = record["source"]
    source_tokens = []
    if _fields(source, _PROPS["source"], "source", errors):
        if source.get("language") not in SOURCE_LANGUAGES:
            errors.append(f"source.language: {source.get('language')!r} not allowed")
        if source.get("text_id") not in TEXT_IDS:
            errors.append(f"source.text_id: {source.get('text_id')!r} not allowed")
        source_tokens = source.get("tokens") or []
        if not source_tokens:
            errors.append("source.tokens: must not be empty")
        for tid in source_tokens:
            if tid not in known_tokens:
                errors.append(f"source.tokens: unknown token {tid!r} for {verse_ids}")
        if "text" in source and all(t in known_tokens for t in source_tokens):
            expected = source_text([known_tokens[t] for t in source_tokens])
            if source["text"] != expected:
                errors.append("source.text: does not match the source data "
                              "(regenerate it with scripts/build_skeleton.py)")
        if (source.get("language") == "grc" and source_tokens
                and all(t in known_tokens for t in source_tokens)):
            check_sentence([known_tokens[t] for t in source_tokens],
                           record.get("decisions") or [], errors)
    in_source = set(source_tokens)

    def check_tokens(ids, where):
        if not isinstance(ids, list):
            errors.append(f"{where}: must be a list")
            return
        for tid in ids:
            if tid not in known_tokens:
                errors.append(f"{where}: unknown token {tid!r}")
            elif tid not in in_source:
                errors.append(f"{where}: token {tid!r} is not in source.tokens")

    # Every verse after the first is marked where it starts, in order.
    later_verses = [refs.parse(v).verse for v in verse_ids[1:]]

    def check_verses(text, where):
        if isinstance(text, str) and markup.verse_markers(text) != later_verses:
            errors.append(f"{where}: verse markers {markup.verse_markers(text)} "
                          f"should be {later_verses}")

    _check_markup(record.get("literal_gloss"), "literal_gloss", errors)
    check_verses(record.get("literal_gloss"), "literal_gloss")

    renderings = record.get("renderings")
    if not isinstance(renderings, dict) or not renderings:
        errors.append("renderings: must be a non-empty object")
        renderings = {}
    for lang, levels in renderings.items():
        if not LANGUAGE.fullmatch(lang):
            errors.append(f"renderings: bad language code {lang!r}")
        if not isinstance(levels, dict) or set(levels) != set(LEVELS):
            errors.append(f"renderings.{lang}: must have exactly {LEVELS}")
            continue
        for level, text in levels.items():
            _check_markup(text, f"renderings.{lang}.{level}", errors)
            check_verses(text, f"renderings.{lang}.{level}")

    for i, al in enumerate(record.get("alignments", [])):
        where = f"alignments[{i}]"
        if not _fields(al, _PROPS["alignments"]["items"], where, errors):
            continue
        check_tokens(al.get("tokens"), f"{where}.tokens")
        target = renderings.get(al.get("language"), {}).get(al.get("level"))
        if target is None:
            errors.append(f"{where}: no rendering for {al.get('language')}/{al.get('level')}")
        elif al.get("target_span") not in target:
            errors.append(f"{where}: target_span not found in rendering")

    seen = set()
    for i, d in enumerate(record.get("decisions") or []):
        where = f"decisions[{i}]"
        if not _fields(d, _DEFS["decision"], where, errors):
            continue
        if d.get("id") in seen:
            errors.append(f"{where}: duplicate id {d.get('id')!r}")
        seen.add(d.get("id"))
        layer = d.get("layer")
        if layer not in LAYERS:
            errors.append(f"{where}.layer: {layer!r} not allowed")
        elif layer == "meaning":
            if d.get("language") is not None:
                errors.append(f"{where}: meaning decisions must have language null")
            if "levels" in d:
                errors.append(f"{where}: meaning decisions apply to every level; drop 'levels'")
        else:
            if d.get("language") not in renderings:
                errors.append(f"{where}: rendering decisions need a language "
                              "that has renderings")
            levels = d.get("levels")
            if not levels or not isinstance(levels, list) or not set(levels) <= set(LEVELS):
                errors.append(f"{where}.levels: must be a non-empty subset of {LEVELS}")
        if d.get("category") not in CATEGORIES:
            errors.append(f"{where}.category: {d.get('category')!r} not allowed")
        check_tokens(d.get("tokens"), f"{where}.tokens")
        _check_markup(d.get("choice"), f"{where}.choice", errors)
        alternatives = d.get("alternatives")
        if not isinstance(alternatives, list):
            errors.append(f"{where}.alternatives: must be a list")
        else:
            for alt in alternatives:
                _check_markup(alt, f"{where}.alternatives", errors)
        if not (isinstance(d.get("reason"), str) and d.get("reason").strip()):
            errors.append(f"{where}.reason: must be a non-empty string")
        for flag in ("uncertain", "footnote"):
            if not isinstance(d.get(flag), bool):
                errors.append(f"{where}.{flag}: must be true or false")

    if original_language:
        check_original_language(record, errors)

    if record.get("status") not in STATUSES:
        errors.append(f"status: {record.get('status')!r} not allowed")
    return errors


def validate_file(path):
    """Validate a content file {"records": [...]}; return error strings."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    records = data.get("records") if isinstance(data, dict) else None
    if not isinstance(records, list) or not records:
        return [f"{path}: expected {{\"records\": [...]}} with at least one record"]
    errors, ids = [], set()
    for record in records:
        rid = record.get("id", "?") if isinstance(record, dict) else "?"
        if rid in ids:
            errors.append(f"{path}: duplicate record id {rid!r}")
        ids.add(rid)
        errors += [f"{path}: {rid}: {e}" for e in validate_record(record)]
    return errors


def main(paths):
    errors = [e for p in paths for e in validate_file(p)]
    for e in errors:
        print(e)
    print(f"{len(paths)} file(s), {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
