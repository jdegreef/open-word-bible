"""Report which languages a book's records have, on a git ref.

usage: python3 .claude/skills/check-book-before-translating/coverage.py BOOK [LANG ...] [--ref REF]

BOOK is the content folder name (MRK, 1CO, ...). REF defaults to origin/main;
run `git fetch origin main` first. Prints, per file, how many records have
each requested language (all languages when none are named).
"""
import json
import subprocess
import sys


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def main(argv):
    ref = "origin/main"
    if "--ref" in argv:
        i = argv.index("--ref")
        ref = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    book, langs = argv[0], argv[1:]
    paths = [p for p in git("ls-tree", "--name-only", f"{ref}:content/{book}").split() if p.endswith(".json")]
    if not paths:
        print(f"{ref}: no content/{book}/ files")
        return
    totals = {}
    count = 0
    for p in paths:
        records = json.loads(git("show", f"{ref}:content/{book}/{p}"))["records"]
        count += len(records)
        have = {}
        for r in records:
            for lang in r["renderings"]:
                have[lang] = have.get(lang, 0) + 1
        for lang, n in have.items():
            totals[lang] = totals.get(lang, 0) + n
        shown = langs or sorted(have)
        print(f"{p}: {len(records)} records; " + ", ".join(f"{lang} {have.get(lang, 0)}" for lang in shown))
    shown = langs or sorted(totals)
    print(f"TOTAL {book} on {ref}: {count} records; " + ", ".join(f"{lang} {totals.get(lang, 0)}" for lang in shown))


if __name__ == "__main__":
    main(sys.argv[1:])
