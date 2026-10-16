"""Check that every message catalog in i18n/ has every message English has,
with the same {placeholders}, and nothing English lacks.

    python3 scripts/check_catalogs.py

A message added to i18n/en.json has to be added to every other catalog in
the same pull request: the site build needs it in each language. The unit
test (tests/test_languages.py) checks the same thing; this script runs in
seconds and names each missing key, so CI fails early and says what to add.
"""
import json
import string
import sys
from pathlib import Path

I18N = Path(__file__).resolve().parents[1] / "i18n"


def placeholders(text):
    return sorted({name for _, name, _, _ in string.Formatter().parse(text) if name})


def compare(english, other, path=""):
    """Problems in other against english, as readable lines."""
    if isinstance(english, dict):
        if not isinstance(other, dict):
            return [f"{path or '(root)'}: should be an object"]
        problems = []
        for key in english.keys() | other.keys():
            where = f"{path}.{key}" if path else key
            if key not in other:
                problems.append(f"{where}: missing")
            elif key not in english:
                problems.append(f"{where}: not in English")
            else:
                problems += compare(english[key], other[key], where)
        return sorted(problems)
    if isinstance(english, list):
        if not isinstance(other, list) or len(other) != len(english):
            return [f"{path}: should be a list of {len(english)}"]
        return [p for i, (e, o) in enumerate(zip(english, other))
                for p in compare(e, o, f"{path}[{i}]")]
    if not isinstance(other, str):
        return [f"{path}: should be text"]
    if placeholders(english) != placeholders(other):
        return [f"{path}: placeholders {placeholders(other)}, English has {placeholders(english)}"]
    return []


def main():
    english = json.loads((I18N / "en.json").read_text(encoding="utf-8"))
    failed = False
    for path in sorted(I18N.glob("*.json")):
        if path.stem == "en":
            continue
        problems = compare(english, json.loads(path.read_text(encoding="utf-8")))
        if problems:
            failed = True
            print(f"i18n/{path.name}: {len(problems)} problem(s)")
            for problem in problems:
                print(f"  {problem}")
    if failed:
        print("\nAdd each missing message to every catalog in i18n/ "
              "(after merging main, which may have added languages).")
        return 1
    print(f"{len(list(I18N.glob('*.json')))} catalogs match English")
    return 0


if __name__ == "__main__":
    sys.exit(main())
