#!/usr/bin/env python3
"""Translate decision notes and the reader's cards into a reading language.

    python3 scripts/notes.py export es [--books JHN ROM] [--chapters 1-3] [--footnotes-only]
                                       [--rendering] [-o FILE]
    python3 scripts/notes.py export-cards es [--kinds glossary key_terms names] [-o FILE]
    python3 scripts/notes.py import es FILE.jsonl [--dry-run]
    python3 scripts/notes.py report [--lang es]
    python3 scripts/notes.py check

export writes a worklist, one JSON object per line, of the decisions whose
note in that language is missing or stale (its English changed after it was
translated): the English choice, alternatives and reason, the record's
renderings in the language and in English for context, and an empty
"translation" to fill in. export-cards does the same for the glossary, name
and key-term cards. Greek and Hebrew in the English are shown as slots
(⟦1⟧, ⟦2⟧, ...; the words themselves are under "original"): keep a slot
where its word belongs and import copies the word back from the English, so
no Greek or Hebrew is ever typed.

import reads a filled worklist (notes and cards alike), checks every line
(owb/notes.py: no reader settings, Greek or Hebrew only from the source data,
as many alternatives as the English) and writes the good ones to
data/notes/<lang>/<BOOK>.json or data/cards/<lang>/<kind>.json with the
English digest. A line whose English changed since it was exported is
refused: export again. Lines left untranslated are skipped.

report prints, for each language, how many footnoted meaning decisions,
meaning decisions and cards are translated and current, and how many are
stale. check validates every note and card file (as CI does).
docs/notes-translation.md is the workflow.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import languages, notes  # noqa: E402


def other_languages():
    return [c for c in languages.CODES if c != "en"]


def _lang(code):
    if code not in languages.READING or code == "en":
        raise SystemExit(f"{code!r} is not a reading language other than English "
                         f"({', '.join(other_languages())})")
    return code


def _slots(texts, words):
    return [notes.to_slots(t, words) for t in texts]


# --------------------------------------------------------------- export


def note_items(lang, books=None, footnotes_only=False, rendering=False, chapters=None):
    """Yield (book, record, decision, entry or None) for every decision a
    note in lang may translate; chapters, a (first, last) pair, keeps the
    records that start in them."""
    for book in books or notes.books():
        have = notes.load_notes(lang, book)
        for r in notes.book_records(book):
            if chapters and not chapters[0] <= int(r["refs"][0].split(".")[1]) <= chapters[1]:
                continue
            for d in r["decisions"]:
                if d["layer"] != "meaning" and not (rendering and d.get("language") == lang):
                    continue
                if footnotes_only and not d.get("footnote"):
                    continue
                yield book, r, d, have.get(r["id"], {}).get(d["id"])


def note_line(lang, book, r, d, entry):
    """One worklist line for decision d of record r."""
    texts = notes.decision_texts(d)
    words = notes.slot_words(texts)
    choice, *alts, reason = _slots(texts, words)
    line = {"kind": "note", "lang": lang, "book": book, "record": r["id"], "decision": d["id"],
            "refs": r["refs"], "layer": d["layer"], "category": d["category"],
            "uncertain": d["uncertain"], "footnote": d.get("footnote", False),
            "status": "stale" if entry else "new", "source": notes.decision_digest(d),
            "english": {"choice": choice, "alternatives": alts, "reason": reason}}
    if words:
        line["original"] = {str(i + 1): w for i, w in enumerate(words)}
    line["rendering"] = r["renderings"].get(lang)
    line["rendering_en"] = r["renderings"].get("en", {}).get("B")
    if entry:
        line["previous"] = {k: entry.get(k) for k in notes.NOTE_FIELDS}
    line["translation"] = {"choice": "", "alternatives": [""] * len(alts), "reason": ""}
    return line


def export(lang, books=None, footnotes_only=False, rendering=False, chapters=None):
    """The worklist lines of every note in lang that is missing or stale."""
    out = []
    for book, r, d, entry in note_items(lang, books, footnotes_only, rendering, chapters):
        if entry and entry.get("source") == notes.decision_digest(d):
            continue
        out.append(note_line(lang, book, r, d, entry))
    return out


def export_cards(lang, kinds=None):
    """The worklist lines of every card in lang that is missing or stale."""
    out = []
    for kind in kinds or list(notes.CARD_KINDS):
        have = notes.load_cards(lang, kind)
        for key, english in notes.english_cards(kind).items():
            entry = have.get(key)
            source = notes.card_digest(kind, english)
            if entry and entry.get("source") == source:
                continue
            texts = notes.card_texts(kind, english)
            words = notes.slot_words(texts)
            line = {"kind": kind, "lang": lang, "key": key, "lemma": english["lemma"],
                    "status": "stale" if entry else "new", "source": source}
            if kind == "key_terms":
                sense, note = _slots(texts, words)
                line["english"] = {"sense": sense, "note": note}
                line["english_words"] = english["english"]
                line["translation"] = {"sense": "", "note": ""} if english.get("note") else {"sense": ""}
            else:
                flat = _slots(texts, words)
                line["english"] = {"senses": [
                    {"name": flat[2 * i], "kind": s["kind"], "note": flat[2 * i + 1]}
                    for i, s in enumerate(english["senses"])]}
                line["translation"] = {"senses": [{"name": "", "note": ""} for _ in english["senses"]]}
            if words:
                line["original"] = {str(i + 1): w for i, w in enumerate(words)}
            if entry:
                line["previous"] = {k: v for k, v in entry.items() if k != "source"}
            out.append(line)
    return out


# --------------------------------------------------------------- import


def _filled(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_filled(v) for v in value)
    if isinstance(value, dict):
        return any(_filled(v) for v in value.values())
    return False


def _expand(value, words):
    if isinstance(value, str):
        return notes.expand(value, words)
    if isinstance(value, list):
        return [_expand(v, words) for v in value]
    if isinstance(value, dict):
        return {k: _expand(v, words) for k, v in value.items()}
    return value


def import_note(lang, line, where, errors, pending):
    book, rid, did = line.get("book"), line.get("record"), line.get("decision")
    d = notes.book_decisions(book).get(rid, {}).get(did) if book in notes.books() else None
    if d is None:
        errors.append(f"{where}: no decision {rid}.{did} in content/{book}")
        return
    if not notes.translatable(d, lang):
        errors.append(f"{where}: {rid}.{did} is another language's rendering decision")
        return
    source = notes.decision_digest(d)
    if line.get("source") != source:
        errors.append(f"{where}: the English of {rid}.{did} changed after this line was exported; "
                      "export it again")
        return
    tr = line.get("translation") or {}
    try:
        entry = {"source": source, **{k: _expand(tr.get(k), notes.slot_words(notes.decision_texts(d)))
                                      for k in notes.NOTE_FIELDS}}
    except KeyError as e:
        errors.append(f"{where}: slot {e.args[0]} has no word in the English")
        return
    if isinstance(entry["alternatives"], list):
        entry["alternatives"] = [a.strip() if isinstance(a, str) else a for a in entry["alternatives"]]
    for k in ("choice", "reason"):
        if isinstance(entry[k], str):
            entry[k] = entry[k].strip()
    found = []
    notes.check_note(entry, d, f"{where} ({rid}.{did})", found, lang)
    if found:
        errors += found
        return
    pending.setdefault(("notes", book), {}).setdefault(rid, {})[did] = entry


def import_card(lang, line, where, errors, pending):
    kind, key = line.get("kind"), line.get("key")
    english = notes.english_cards(kind).get(key) if kind in notes.CARD_KINDS else None
    if english is None:
        errors.append(f"{where}: no {kind} entry {key!r}")
        return
    source = notes.card_digest(kind, english)
    if line.get("source") != source:
        errors.append(f"{where}: the English of {kind} {key} changed after this line was exported; "
                      "export it again")
        return
    try:
        tr = _expand(line.get("translation") or {}, notes.slot_words(notes.card_texts(kind, english)))
    except KeyError as e:
        errors.append(f"{where}: slot {e.args[0]} has no word in the English")
        return
    if kind == "key_terms":
        entry = {"source": source, "sense": (tr.get("sense") or "").strip()}
        if english.get("note"):
            entry["note"] = (tr.get("note") or "").strip()
    else:
        entry = {"source": source, "senses": [{"name": (s.get("name") or "").strip(),
                                               "note": (s.get("note") or "").strip()}
                                              for s in tr.get("senses") or []]}
    found = []
    notes.check_card(kind, entry, english, f"{where} ({kind} {key})", found)
    if found:
        errors += found
        return
    pending.setdefault(("cards", kind), {})[key] = entry


def import_file(lang, path, dry_run=False):
    """Import a filled worklist; returns (written count, errors, skipped)."""
    errors, pending, skipped = [], {}, 0
    for n, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        where = f"{path}:{n}"
        try:
            line = json.loads(raw)
        except json.JSONDecodeError as e:
            errors.append(f"{where}: not JSON ({e})")
            continue
        if line.get("lang", lang) != lang:
            errors.append(f"{where}: a line for {line.get('lang')!r}, not {lang!r}")
            continue
        if not _filled(line.get("translation")):
            skipped += 1
            continue
        if line.get("kind", "note") == "note":
            import_note(lang, line, where, errors, pending)
        else:
            import_card(lang, line, where, errors, pending)
    written = 0
    for (what, name), entries in pending.items():
        written += sum(len(v) for v in entries.values()) if what == "notes" else len(entries)
        if dry_run:
            continue
        if what == "notes":
            path_ = notes.notes_path(lang, name)
            data = json.loads(path_.read_text(encoding="utf-8")) if path_.is_file() else notes.note_template(lang)
            merged = data["notes"]
            for rid, ds in entries.items():
                merged.setdefault(rid, {}).update(ds)
            data["notes"] = notes.ordered_notes(name, merged)
        else:
            path_ = notes.cards_path(lang, name)
            data = json.loads(path_.read_text(encoding="utf-8")) if path_.is_file() else notes.card_template(lang, name)
            data[name].update(entries)
            order = list(notes.english_cards(name))
            data[name] = dict(sorted(data[name].items(),
                                     key=lambda kv: order.index(kv[0]) if kv[0] in order else len(order)))
        notes.write_json(path_, data)
    notes.load_notes.cache_clear()
    notes.load_cards.cache_clear()
    return written, errors, skipped


# --------------------------------------------------------------- report


def report(langs=None):
    """{lang: counts} of what is translated and current, and stale."""
    out = {}
    all_meaning = [(b, r, d) for b in notes.books() for r in notes.book_records(b)
                   for d in r["decisions"] if d["layer"] == "meaning"]
    for lang in langs or other_languages():
        c = {"footnotes": 0, "footnotes_done": 0, "meaning": 0, "meaning_done": 0, "stale": 0,
             "rendering_done": 0, "orphaned": 0, "cards": {}}
        for b, r, d in all_meaning:
            entry = notes.load_notes(lang, b).get(r["id"], {}).get(d["id"])
            current = bool(entry) and entry.get("source") == notes.decision_digest(d)
            c["meaning"] += 1
            c["meaning_done"] += current
            if d.get("footnote"):
                c["footnotes"] += 1
                c["footnotes_done"] += current
            c["stale"] += bool(entry) and not current
        for b in notes.books():
            english = notes.book_decisions(b)
            for rid, ds in notes.load_notes(lang, b).items():
                for did, entry in ds.items():
                    d = english.get(rid, {}).get(did)
                    if d is None:
                        c["orphaned"] += 1
                    elif d["layer"] != "meaning":
                        if entry.get("source") == notes.decision_digest(d):
                            c["rendering_done"] += 1
                        else:
                            c["stale"] += 1
        for kind in notes.CARD_KINDS:
            english, have = notes.english_cards(kind), notes.load_cards(lang, kind)
            fresh = {k: have.get(k, {}).get("source") == notes.card_digest(kind, e) for k, e in english.items()}
            done = sum(fresh.values())
            stale = sum(1 for k in english if k in have and not fresh[k])
            c["cards"][kind] = {"total": len(english), "done": done, "stale": stale,
                                "orphaned": len(set(have) - set(english))}
        out[lang] = c
    return out


def print_report(results, out=sys.stdout):
    for lang, c in results.items():
        cards = ", ".join(f"{kind} {v['done']}/{v['total']}" + (f" ({v['stale']} stale)" if v["stale"] else "")
                          for kind, v in c["cards"].items())
        print(f"{lang}: footnotes {c['footnotes_done']}/{c['footnotes']}, "
              f"meaning notes {c['meaning_done']}/{c['meaning']}"
              + (f", own rendering notes {c['rendering_done']}" if c["rendering_done"] else "")
              + (f", {c['stale']} stale" if c["stale"] else "")
              + (f", {c['orphaned']} orphaned" if c["orphaned"] else "")
              + f"; cards: {cards}", file=out)


def check():
    errors = [e for p in notes.all_files() for e in notes.check_file(p)]
    for e in errors:
        print(e)
    print(f"{len(notes.all_files())} file(s), {len(errors)} error(s)")
    return 1 if errors else 0


# ----------------------------------------------------------------- main


def _write_lines(lines, out):
    text = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lines)
    if out:
        Path(out).write_text(text, encoding="utf-8")
        print(f"{len(lines)} line(s) written to {out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export", help="worklist of missing or stale notes")
    e.add_argument("lang")
    e.add_argument("--books", nargs="+", metavar="BOOK")
    e.add_argument("--chapters", metavar="N[-M]", help="only records starting in these chapters (with one book)")
    e.add_argument("--footnotes-only", action="store_true", help="only decisions with a footnote")
    e.add_argument("--rendering", action="store_true", help="also the language's own rendering decisions")
    e.add_argument("-o", "--out", help="file to write (default: standard output)")
    c = sub.add_parser("export-cards", help="worklist of missing or stale cards")
    c.add_argument("lang")
    c.add_argument("--kinds", nargs="+", choices=list(notes.CARD_KINDS))
    c.add_argument("-o", "--out")
    i = sub.add_parser("import", help="write a filled worklist into data/notes and data/cards")
    i.add_argument("lang")
    i.add_argument("file")
    i.add_argument("--dry-run", action="store_true", help="check only; write nothing")
    r = sub.add_parser("report", help="coverage per language")
    r.add_argument("--lang", action="append")
    sub.add_parser("check", help="validate every note and card file")
    args = ap.parse_args(argv)

    if args.command == "export":
        books = [b.upper() for b in args.books] if args.books else None
        unknown = set(books or []) - set(notes.books())
        if unknown:
            raise SystemExit(f"no content for {', '.join(sorted(unknown))}")
        chapters = None
        if args.chapters:
            first, _, last = args.chapters.partition("-")
            chapters = (int(first), int(last or first))
        _write_lines(export(_lang(args.lang), books, args.footnotes_only, args.rendering, chapters), args.out)
    elif args.command == "export-cards":
        _write_lines(export_cards(_lang(args.lang), args.kinds), args.out)
    elif args.command == "import":
        written, errors, skipped = import_file(_lang(args.lang), args.file, args.dry_run)
        for err in errors:
            print(err, file=sys.stderr)
        print(f"{'checked' if args.dry_run else 'imported'} {written}, skipped {skipped} untranslated, "
              f"{len(errors)} error(s)", file=sys.stderr)
        return 1 if errors else 0
    elif args.command == "report":
        print_report(report([_lang(x) for x in args.lang] if args.lang else None))
    elif args.command == "check":
        return check()
    return 0


if __name__ == "__main__":
    sys.exit(main())
