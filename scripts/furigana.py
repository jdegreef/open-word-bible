"""Draft furigana (owb/furigana.py): the reading of each run of kanji in a
language's rendering, kept in data/furigana/<BOOK>.json.

    python3 scripts/furigana.py show content/JHN/JHN.1.1-18.json
    python3 scripts/furigana.py apply content/JHN/JHN.1.1-18.json spec.txt

show prints each record's rendering and its kanji runs in order. apply
reads a spec, one record per line, a reading for every run in order:

    JHN.1.5.s1: 光=ひかり | 闇=やみ | 中=なか | 輝=かがや | 闇=やみ | 光=ひかり | 打=う | 勝=か

Readings are hiragana for the kanji alone (輝いている: 輝=かがや). Every run
must have one, so a record is all or nothing. Records not in the spec are
left alone. --check only checks the spec and writes nothing.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import furigana  # noqa: E402


def show(path, lang, level):
    for r in json.loads(Path(path).read_text(encoding="utf-8"))["records"]:
        text = r["renderings"].get(lang, {}).get(level)
        if text is None:
            continue
        have = furigana.book(r["id"].split(".")[0]).get(r["id"], {}).get(lang, {}).get(level)
        print(f"== {r['id']}\n{text}\nruns: {' | '.join(x[2] for x in furigana.runs(text))}")
        if have:
            print("now:  " + " | ".join(f"{a}={b}" for a, b in have))
        print()


def apply(path, spec, lang, level, check=False):
    records = {r["id"]: r for r in json.loads(Path(path).read_text(encoding="utf-8"))["records"]}
    errors, new = [], {}
    for n, line in enumerate(Path(spec).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rid, _, rest = line.partition(":")
        rid = rid.strip()
        r = records.get(rid)
        if r is None or lang not in r["renderings"]:
            errors.append(f"{spec}:{n}: no {lang} record {rid} in {path}")
            continue
        items = []
        for part in rest.split("|"):
            run, eq, reading = part.strip().partition("=")
            if part.strip():
                items.append([run.strip(), reading.strip()])
        text = r["renderings"][lang][level]
        try:
            furigana.ranges(text, items)
        except ValueError as e:
            i, _, reason = str(e).partition(": ")
            errors.append(f"{rid}: item {int(i) + 1}: {reason}")
            continue
        if len(items) != len(furigana.runs(text)):
            errors.append(f"{rid}: {len(items)} readings for {len(furigana.runs(text))} runs of kanji")
            continue
        new[rid] = items
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(f"{len(errors)} problem(s); nothing written")
    if check:
        print(f"{len(new)} record(s) fit")
        return
    by_book = {}
    for rid, items in new.items():
        by_book.setdefault(rid.split(".")[0], {})[rid] = items
    for code, entries in by_book.items():
        out = furigana.DIR / f"{code}.json"
        data = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
        for rid, items in entries.items():
            data.setdefault(rid, {}).setdefault(lang, {})[level] = items
        order = {}
        for name in sorted(data, key=_order):
            order[name] = data[name]
        furigana.DIR.mkdir(parents=True, exist_ok=True)
        out.write_text(_dump(order), encoding="utf-8")
    furigana.book.cache_clear()
    print(f"{len(new)} record(s) written")


def _order(rid):
    book, chapter, verse, sentence = rid.split(".")
    return int(chapter), int(verse), sentence


def _dump(data):
    """One record per line, so a diff shows which changed."""
    lines = [f"  {json.dumps(rid)}: {json.dumps(v, ensure_ascii=False, separators=(', ', ': '))}"
             for rid, v in data.items()]
    return "{\n" + ",\n".join(lines) + "\n}\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["show", "apply"])
    ap.add_argument("file")
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--lang", default="ja")
    ap.add_argument("--level", default="B", choices=["L", "B", "R"])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.command == "show":
        show(a.file, a.lang, a.level)
    elif not a.spec:
        ap.error("apply needs a spec file")
    else:
        apply(a.file, a.spec, a.lang, a.level, a.check)


if __name__ == "__main__":
    main()
