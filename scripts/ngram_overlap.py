"""Find long runs of words that our renderings share with other Bibles.

For each sentence and level, the default rendering is compared with the same
verses in each comparison Bible, and every run of at least --min words that
appears in both is reported. Runs shared with the public-domain Bibles in
vendor/open-bibles are the common heritage of English (or Spanish) Bible
wording. A run shared only with a copyrighted translation is what a reviewer
should look at.

Copyrighted translations are never stored in this repository. A reviewer who
owns one can compare against it with --extra NAME=PATH, where PATH is a local
tab-separated file of "VERSE_ID<TAB>text" lines (e.g. "COL.1.1<TAB>Paul, ...").
Keep that file outside the repository.

Our Old Testament verses are numbered as the Hebrew text is (a psalm's title
is verse 1); the comparison Bibles, --extra files included, are taken to use
English numbering, and each sentence is compared with the English verses that
hold the same text (owb/versification.py).

Usage:
    OWB_VENDOR=<sources dir> python3 scripts/ngram_overlap.py content/COL/COL.1.json
    python3 scripts/ngram_overlap.py --no-open-bibles --extra niv=~/niv-col.tsv content/COL/*.json

Options: --language en, --levels L,B,R, --min 6, --distinctive (only runs
not shared with any public-domain Bible; needs --extra).
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import markup, refs, versification  # noqa: E402

# Our language codes and the open-bibles language codes.
OPEN_BIBLE_LANGUAGE = {"en": "eng", "es": "spa"}

_WORD = re.compile(r"[^\W_]+(?:'[^\W_]+)*")


def words(text):
    """The words of text, apostrophes kept inside words."""
    return _WORD.findall(text.replace("’", "'"))


def plain(rendering):
    """A rendering with default settings, verse markers and [brackets] removed."""
    text = markup.flat(markup.VERSE.sub(" ", markup.render(rendering)))
    return text.replace("[", "").replace("]", "")


def runs(ours, theirs, n):
    """Maximal stretches of ours made of n-word sequences that also occur in
    theirs. Both are lists of lower-case words. Returns [(start, end), ...]
    as slice bounds into ours."""
    grams = {tuple(theirs[i:i + n]) for i in range(len(theirs) - n + 1)}
    out = []
    for i in range(len(ours) - n + 1):
        if tuple(ours[i:i + n]) in grams:
            if out and i <= out[-1][1]:
                out[-1] = (out[-1][0], i + n)
            else:
                out.append((i, i + n))
    return out


def read_tsv(path):
    """{verse id: text} from a "VERSE_ID<TAB>text" file; # starts a comment."""
    out = {}
    for line in Path(path).expanduser().read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        verse_id, text = line.split("\t", 1)
        refs.parse(verse_id.strip())
        out[verse_id.strip()] = text.strip()
    return out


def open_bible_editions(language):
    """{code: {verse id: text}} for the public-domain Bibles in one language."""
    from owb.sources import open_bibles
    wanted = OPEN_BIBLE_LANGUAGE.get(language)
    return {code: {str(refs.Ref(*key)): text for key, text in open_bibles.load(code).items()}
            for code, (_, _, lang, _, _) in open_bibles.EDITIONS.items() if lang == wanted}


def compare(records, language, levels, editions, n):
    """One result per sentence and level that has a rendering:
    {"id", "level", "words", "runs": {edition: [(start, end), ...]}}.
    The editions are keyed by English verse id."""
    results = []
    for record in records:
        english = versification.english_ids(record["refs"])
        renderings = record["renderings"].get(language, {})
        for level in levels:
            if level not in renderings:
                continue
            ours = words(plain(renderings[level]))
            lower = [w.lower() for w in ours]
            found = {}
            for name, verses in editions.items():
                theirs = words(" ".join(verses.get(r, "") for r in english))
                hits = runs(lower, [w.lower() for w in theirs], n)
                if hits:
                    found[name] = hits
            results.append({"id": record["id"], "level": level, "words": ours, "runs": found})
    return results


def distinctive(result, extra, public):
    """The runs found in extra editions that are not wholly covered by a run
    in any public-domain edition."""
    covered = {i for name in public for start, end in result["runs"].get(name, ())
               for i in range(start, end)}
    return {name: [(s, e) for s, e in result["runs"].get(name, ())
                   if not set(range(s, e)) <= covered]
            for name in extra}


def report(results, editions, extra, n, only_distinctive):
    public = [name for name in editions if name not in extra]
    total = sum(len(r["words"]) for r in results)
    covered = {name: 0 for name in editions}
    longest = {name: 0 for name in editions}
    lines = []
    for result in results:
        shown = distinctive(result, extra, public) if only_distinctive else result["runs"]
        rows = []
        for name in editions:
            spans = result["runs"].get(name, ())
            covered[name] += len({i for s, e in spans for i in range(s, e)})
            longest[name] = max([longest[name]] + [e - s for s, e in spans])
            for s, e in shown.get(name, ()):
                rows.append(f"  {name:<8}{e - s:>3} words  {' '.join(result['words'][s:e])}")
        if rows:
            lines.append(f"{result['id']} {result['level']} ({len(result['words'])} words)")
            lines.extend(rows)
    lines.append("")
    lines.append(f"Words in runs of {n}+ shared with each Bible ({total} words compared):")
    for name in editions:
        share = 100 * covered[name] / total if total else 0
        tag = "  (extra)" if name in extra else ""
        lines.append(f"  {name:<8}{share:5.1f}%   longest run {longest[name]} words{tag}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="+", help="content files, e.g. content/COL/COL.1.json")
    parser.add_argument("--language", default="en")
    parser.add_argument("--levels", default="L,B,R")
    parser.add_argument("--min", type=int, default=6, help="shortest run to report (words)")
    parser.add_argument("--extra", action="append", default=[], metavar="NAME=PATH",
                        help="a local VERSE_ID<TAB>text file to compare against")
    parser.add_argument("--no-open-bibles", action="store_true",
                        help="skip the public-domain Bibles in vendor/open-bibles")
    parser.add_argument("--distinctive", action="store_true",
                        help="show only runs from --extra Bibles not shared with a public-domain one")
    args = parser.parse_args(argv)
    if args.min < 2:
        parser.error("--min must be at least 2")

    editions = {} if args.no_open_bibles else open_bible_editions(args.language)
    extra = []
    for item in args.extra:
        name, sep, path = item.partition("=")
        if not sep or not name or not path:
            parser.error(f"--extra needs NAME=PATH, got {item!r}")
        editions[name] = read_tsv(path)
        extra.append(name)
    if not editions:
        parser.error(f"no Bibles to compare against for language {args.language!r}")
    if args.distinctive and not extra:
        parser.error("--distinctive needs at least one --extra Bible")

    records = [record for path in args.paths
               for record in json.loads(Path(path).read_text(encoding="utf-8"))["records"]]
    results = compare(records, args.language, args.levels.split(","), editions, args.min)
    print(report(results, editions, extra, args.min, args.distinctive))


if __name__ == "__main__":
    main()
