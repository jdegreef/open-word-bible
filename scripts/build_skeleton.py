"""Emit skeleton sentence records with real token ids and source text.

Usage: python3 scripts/build_skeleton.py JHN.1.1 [JHN.1.2] [--lang en] [-o FILE]

Writes one record per source sentence (see macula_greek.sentences), so a
sentence may cover part of a verse or run across several; later verses are
marked with \\v N in the gloss and renderings. Old Testament passages get one
record per verse (see macula_hebrew.sentences). Token ids and source text come
from MACULA Greek or Hebrew; translators fill in literal_gloss, renderings and
decisions.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from owb import refs  # noqa: E402
from owb.sources import macula_greek, macula_hebrew, sblgnt  # noqa: E402
from owb.validate import source_text  # noqa: E402


def skeleton(start, end=None, lang="en"):
    hebrew = refs.parse(start).book in refs.OT_CODES
    source = macula_hebrew if hebrew else macula_greek
    tokens = source.load_tokens(start, end)
    if not tokens:
        raise SystemExit(f"no tokens for {start}..{end or start}")
    records, per_verse = [], {}
    for toks in source.sentences(tokens):
        verses = list(dict.fromkeys(t.ref for t in toks))
        per_verse[verses[0]] = per_verse.get(verses[0], 0) + 1
        markers = "".join(f"\\v {v.verse} " for v in verses[1:])
        records.append({
            "id": f"{verses[0]}.s{per_verse[verses[0]]}",
            "refs": [str(v) for v in verses],
            "source": {
                "language": macula_hebrew.source_language(toks) if hebrew else "grc",
                "text_id": macula_hebrew.TEXT_ID if hebrew else sblgnt.TEXT_ID,
                "tokens": [t.id for t in toks],
                "text": source_text(toks),
            },
            "literal_gloss": markers,
            "renderings": {lang: {"L": markers, "B": markers, "R": markers}},
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
