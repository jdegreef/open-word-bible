#!/usr/bin/env python3
"""Print the content checks of owb/content_checks.py: footnotes whose verse
words an alternative (or not the choice), and verses or glossary rows that
break a language's terms glossary (docs/<language>-terms.md).

    python3 scripts/content_checks.py                  # every language, counts and examples
    python3 scripts/content_checks.py --lang id --check notes --all
    python3 scripts/content_checks.py --lang id --check glossary --json > hits.json
    python3 scripts/content_checks.py --books JOL ISA

It reports and always exits 0: the checks are heuristics for a reviewer to
look at, not rules (see the module's docstring for what each one flags).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import content_checks as cc  # noqa: E402
from owb import languages  # noqa: E402


def run(langs, books, checks):
    records = cc.load_records(books)
    en_stop = cc.language_function_words(records, "en") if "notes" in checks else None
    out = {}
    for lang in langs:
        entry = {}
        if "notes" in checks:
            translated = None if lang == "en" else cc.load_notes(lang, books)
            stop = en_stop if lang == "en" else None
            entry["notes"] = cc.note_mismatches(records, lang, translated, stop=stop, en_stop=en_stop)
        if "glossary" in checks and lang != "en":
            rows = cc.load_glossary(languages.READING[lang]["name"])
            entry["glossary"] = {"verses": cc.glossary_hits(rows, records, lang) if rows else [],
                                 "rows": cc.glossary_conflicts(rows), "has_glossary": bool(rows)}
        out[lang] = entry
    return out


def _print(results, every):
    limit = None if every else 5
    for lang, entry in results.items():
        name = languages.READING[lang]["name"]
        if "notes" in entry:
            hits = entry["notes"]
            kinds = {}
            for h in hits:
                kinds[h["kind"]] = kinds.get(h["kind"], 0) + 1
            print(f"{name} ({lang}): {len(hits)} note/verse mismatches "
                  + ", ".join(f"{k} {n}" for k, n in sorted(kinds.items())))
            for h in hits[:limit]:
                extra = f' -> "{h["alternative"]}"' if h["alternative"] else ""
                print(f'  {h["record"]} {h["level"]} {h["decision"]} {h["kind"]}: "{h["choice"]}"{extra}')
                print(f'      {h["text"]}')
        g = entry.get("glossary")
        if g and g["has_glossary"]:
            print(f'{name} ({lang}): {len(g["verses"])} verses against the glossary, '
                  f'{len(g["rows"])} glossary rows in conflict')
            for h in g["verses"][:limit]:
                print(f'  {h["record"]} {h["level"]} {h["kind"]} "{h["form"]}" for "{h["term"]}" '
                      f'(glossary line {h["row"]["line"]})')
            for c in g["rows"][:limit]:
                rows = " / ".join(f'line {x["line"]} {x["forms"]!r}' for x in c["rows"])
                print(f'  "{c["term"]}" {c["kind"]}: {rows}')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lang", nargs="*", help="language codes (default: every reading language)")
    p.add_argument("--books", nargs="*", help="book codes (default: every book)")
    p.add_argument("--check", choices=("notes", "glossary", "all"), default="all")
    p.add_argument("--json", action="store_true", help="print the full lists as JSON")
    p.add_argument("--all", action="store_true", help="print every hit, not five examples")
    args = p.parse_args(argv)
    langs = args.lang or list(languages.READING)
    unknown = [code for code in langs if code not in languages.READING]
    if unknown:
        p.error("not a reading language: " + ", ".join(unknown))
    checks = {"notes", "glossary"} if args.check == "all" else {args.check}
    results = run(langs, args.books, checks)
    if args.json:
        json.dump(results, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        _print(results, args.all)
    return 0


if __name__ == "__main__":
    sys.exit(main())
