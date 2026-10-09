"""Emit skeleton sentence records with real token ids and source text.

Usage: python3 scripts/build_skeleton.py JHN.1.1 [JHN.1.2] [--lang en] [-o FILE]

Writes one record per verse (split or merge them by hand when a sentence
does not match a verse). Token ids and source text come from MACULA Greek;
translators fill in literal_gloss, renderings and decisions.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from owb import refs  # noqa: E402
from owb.sources import macula_greek, sblgnt  # noqa: E402
from owb.validate import source_text  # noqa: E402


def skeleton(start, end=None, lang="en"):
    by_verse = {}
    for tok in macula_greek.load_tokens(start, end):
        by_verse.setdefault(tok.ref, []).append(tok)
    if not by_verse:
        raise SystemExit(f"no tokens for {start}..{end or start}")
    records = []
    for ref, toks in by_verse.items():
        records.append({
            "id": f"{ref}.s1",
            "refs": [str(ref)],
            "source": {
                "language": "grc",
                "text_id": sblgnt.TEXT_ID,
                "tokens": [t.id for t in toks],
                "text": source_text(toks),
            },
            "literal_gloss": "",
            "renderings": {lang: {"L": "", "B": "", "R": ""}},
            "decisions": [],
            "status": "ai_draft",
        })
    return {"records": records}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("start")
    ap.add_argument("end", nargs="?")
    ap.add_argument("--lang", default="en")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    refs.parse(args.start)
    out = json.dumps(skeleton(args.start, args.end, args.lang), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
