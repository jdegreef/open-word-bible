"""Draft word alignments for one language of a passage file: links from
source tokens to spans of a rendering, which the reader uses to light a
Greek or Hebrew word and the words it became, and in Parallel to light a
word's partner in the other language (both are aligned to the same tokens).

Tokens are written as their numbers in the record (1 = the record's first
source token), so no Greek or Hebrew is typed.

    python3 scripts/align.py show content/JHN/JHN.1.1-18.json --lang ja
    python3 scripts/align.py apply content/JHN/JHN.1.1-18.json spec.txt --lang ja

show prints, for each record, the rendering, the numbered source words
with their glosses, and the English Balanced alignments as a guide.

apply reads a spec, one record per line, spans in the order they appear:

    JHN.1.1.s1: 初めに=1,2 | 言=4,5 | おられた=3

and replaces the language's alignments at that level in the records it
names, after checking every span is found in order as a whole word (a
span may sit inside a setting span only whole, as {{...}}). A record listed
with nothing after the colon has its alignments for that language removed.
Records not in the spec are left alone. Nothing else in the file changes.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import markup  # noqa: E402


def load_words(records):
    """Source words by token id, from the chapter extracts (data/grc, data/hbo)."""
    words = {}
    for r in records:
        lang = r["source"]["language"]
        folder = ROOT / "data" / ("grc" if lang == "grc" else "hbo")
        for ref in r["refs"]:
            book, chapter, _ = ref.split(".")
            path = folder / f"{book}.{chapter}.json"
            if path in words:
                continue
            verses = json.loads(path.read_text(encoding="utf-8"))["verses"]
            words[path] = {w["id"]: w for ws in verses.values() for w in ws}
    out = {}
    for table in words.values():
        out.update(table)
    return out


def show(path, lang, level, only):
    records = json.loads(Path(path).read_text(encoding="utf-8"))["records"]
    words = load_words(records)
    for r in records:
        if only and r["id"] != only:
            continue
        toks = r["source"]["tokens"]
        num = {t: i + 1 for i, t in enumerate(toks)}
        print(f"== {r['id']}")
        text = r["renderings"].get(lang, {}).get(level)
        print(f"{lang}/{level}: {text if text is not None else '(no rendering)'}")
        print("source:", "  ".join(f"{i}:{words.get(t, {}).get('text', '?')}[{words.get(t, {}).get('gloss', '')}]"
                                    for i, t in enumerate(toks, 1)))
        en = [a for a in r.get("alignments", []) if a["language"] == "en" and a["level"] == "B"]
        if en:
            print("en/B:  ", " | ".join(f"{a['target_span']}={','.join(str(num[t]) for t in a['tokens'])}" for a in en))
        mine = [a for a in r.get("alignments", []) if a["language"] == lang and a["level"] == level]
        if mine and lang != "en":
            print(f"{lang}/{level} now:",
                  " | ".join(f"{a['target_span']}={','.join(str(num[t]) for t in a['tokens'])}" for a in mine))
        print()


def parse(spec):
    out = {}
    for n, line in enumerate(Path(spec).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rid, sep, rest = line.partition(":")
        if not sep:
            raise SystemExit(f"{spec}:{n}: expected 'RECORD_ID: span=1,2 | ...'")
        items = []
        # "|" separates spans, except inside a setting span {{name:a|b}}.
        for part in re.split(r"\|(?![^{]*\}\})", rest):
            part = part.strip()
            if not part:
                continue
            span, eq, nums = part.rpartition("=")
            if not eq or not span:
                raise SystemExit(f"{spec}:{n}: {part!r} is not span=numbers")
            try:
                items.append((span, [int(x) for x in nums.replace(" ", "").split(",") if x]))
            except ValueError:
                raise SystemExit(f"{spec}:{n}: {part!r}: token numbers must be integers")
        out[rid.strip()] = items
    return out


def apply(path, spec, lang, level):
    p = Path(path)
    doc = json.loads(p.read_text(encoding="utf-8"))
    wanted = parse(spec)
    by_id = {r["id"]: r for r in doc["records"]}
    errors = [f"{rid}: no such record in {path}" for rid in wanted if rid not in by_id]
    for rid, items in wanted.items():
        r = by_id.get(rid)
        if r is None:
            continue
        toks = r["source"]["tokens"]
        text = r["renderings"].get(lang, {}).get(level)
        if text is None:
            errors.append(f"{rid}: no {lang}/{level} rendering")
            continue
        new = []
        for span, nums in items:
            bad = [x for x in nums if not 1 <= x <= len(toks)]
            if bad or not nums:
                errors.append(f"{rid}: {span!r}: token numbers {bad or nums} outside 1..{len(toks)}")
                continue
            new.append({"tokens": [toks[x - 1] for x in nums], "language": lang, "level": level, "target_span": span})
        try:
            markup.alignment_ranges(text, [a["target_span"] for a in new])
        except ValueError as e:
            i, _, reason = str(e).partition(": ")
            errors.append(f"{rid}: span {int(i) + 1}: {reason}")
            continue
        kept = [a for a in r.get("alignments", []) if not (a["language"] == lang and a["level"] == level)]
        r["alignments"] = kept + new
        if not r["alignments"]:
            r.pop("alignments")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(f"{len(errors)} problem(s); {path} not written")
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{path}: {len(wanted)} record(s) aligned in {lang}/{level}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["show", "apply"])
    ap.add_argument("file")
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--lang", required=True)
    ap.add_argument("--level", default="B", choices=["L", "B", "R"])
    ap.add_argument("--record")
    a = ap.parse_args()
    if a.command == "show":
        show(a.file, a.lang, a.level, a.record)
    else:
        if not a.spec:
            ap.error("apply needs a spec file")
        apply(a.file, a.spec, a.lang, a.level)


if __name__ == "__main__":
    main()
