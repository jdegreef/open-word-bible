"""Emit skeleton sentence records with real token ids and source text.

Usage: python3 scripts/build_skeleton.py JHN.1.1 [JHN.1.2] [--lang en] [-o FILE]

Writes one record per source sentence (see macula_greek.sentences), so a
sentence may cover part of a verse or run across several; later verses are
marked with \\v N in the gloss and renderings. Token ids and source text come
from MACULA Greek; translators fill in literal_gloss, renderings and
decisions.
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
    tokens = macula_greek.load_tokens(start, end)
    if not tokens:
        raise SystemExit(f"no tokens for {start}..{end or start}")
    records, per_verse = [], {}
    for toks in macula_greek.sentences(tokens):
        verses = list(dict.fromkeys(t.ref for t in toks))
        per_verse[verses[0]] = per_verse.get(verses[0], 0) + 1
        markers = "".join(f"\\v {v.verse} " for v in verses[1:])
        records.append({
            "id": f"{verses[0]}.s{per_verse[verses[0]]}",
            "refs": [str(v) for v in verses],
            "source": {
                "language": "grc",
                "text_id": sblgnt.TEXT_ID,
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
