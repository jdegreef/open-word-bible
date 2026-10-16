"""Which article translations are missing or behind their English article.

    python3 scripts/check_translations.py              report every language
    python3 scripts/check_translations.py --lang fr    one language
    python3 scripts/check_translations.py --strict     exit 1 when anything is reported
    python3 scripts/check_translations.py --stamp articles/fr/the-niv.md ...

An English article is articles/<slug>.md and its translation
articles/<lang>/<slug>.md. Each translation records, as `source:` in its
front matter, a digest of the English text it was translated from (title,
summary, nav_title and body). When the English changes, the digests differ
and the translation is reported as out of date. After translating an
article, or after bringing a translation up to date with its English, stamp
it with --stamp, which writes the current English digest.

The report lists, for each reading language (data/languages.json):
- missing: English articles with no translation (a language with no
  articles at all is summed up in one line);
- out of date: the English has changed since the translation was stamped;
- not stamped: a translation with no `source:` line;
- front matter: date, order, section or part differ from the English;
- orphaned: a translation whose English article no longer exists.

It is a report, not a test: English runs ahead of the other languages, so
missing and out-of-date translations are expected. scripts/check.sh prints
it; --strict turns it into a failing check.
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import languages  # noqa: E402

ARTICLES = ROOT / "articles"
FRONT = re.compile(r"---\n(.*?)\n---\n(.*)", re.S)
# Front matter a translation copies from its English article unchanged.
COPIED = ("date", "order", "section", "part")
# Front matter that is translated, so a change to it makes a translation stale.
TRANSLATED = ("title", "summary", "nav_title")


def split(text):
    """(front matter as {key: raw value}, body) of an article's text."""
    m = FRONT.match(text)
    if not m:
        raise SystemExit("missing the --- front matter block")
    meta = {}
    for line in m[1].splitlines():
        if line.strip():
            key, value = line.split(": ", 1)
            meta[key] = value
    return meta, m[2]


def digest(english_text):
    """The digest of what a translation translates: the English title,
    summary, nav_title and body. Dates, order and the like are left out, and
    so is trailing whitespace, so only a change to the words counts."""
    meta, body = split(english_text)
    parts = [f"{key}: {meta.get(key, '')}" for key in TRANSLATED]
    parts += [line.rstrip() for line in body.strip().splitlines()]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]


def stamp(path, english_text):
    """Write the English digest into a translation's front matter as
    `source:`, replacing an earlier one."""
    text = path.read_text(encoding="utf-8")
    m = FRONT.match(text)
    if not m:
        raise SystemExit(f"{path}: missing the --- front matter block")
    lines = [line for line in m[1].splitlines() if not line.startswith("source: ")]
    lines.append(f"source: {digest(english_text)}")
    path.write_text("---\n" + "\n".join(lines) + "\n---\n" + m[2], encoding="utf-8")


def report(root=ARTICLES, langs=None):
    """{lang: {"missing": [...], "out_of_date": [...], "not_stamped": [...],
    "front_matter": [(slug, key), ...], "orphaned": [...]}} for each
    language other than English, plus "total" (the English count)."""
    english = {p.stem: p.read_text(encoding="utf-8") for p in sorted(root.glob("*.md"))}
    out = {}
    for lang in langs or [c for c in languages.CODES if c != "en"]:
        folder = root / lang
        found = {p.stem: p.read_text(encoding="utf-8") for p in sorted(folder.glob("*.md"))} if folder.is_dir() else {}
        r = {"missing": sorted(set(english) - set(found)), "out_of_date": [], "not_stamped": [],
             "front_matter": [], "orphaned": sorted(set(found) - set(english)), "total": len(english)}
        for slug in sorted(set(found) & set(english)):
            meta, _ = split(found[slug])
            en_meta, _ = split(english[slug])
            if "source" not in meta:
                r["not_stamped"].append(slug)
            elif meta["source"] != digest(english[slug]):
                r["out_of_date"].append(slug)
            r["front_matter"] += [(slug, key) for key in COPIED if meta.get(key) != en_meta.get(key)]
        out[lang] = r
    return out


def print_report(results, out=sys.stdout):
    """The report as text; returns how many problems it lists, not counting
    a language with no articles yet."""
    count = 0
    labels = (("missing", "missing"), ("out_of_date", "out of date with the English"),
              ("not_stamped", "not stamped (run --stamp after checking it against the English)"),
              ("orphaned", "orphaned (no English article)"))
    for lang, r in results.items():
        if len(r["missing"]) == r["total"]:
            print(f"{lang}: no articles yet ({r['total']} to translate)", file=out)
            continue
        problems = sum(len(r[key]) for key, _ in labels) + len(r["front_matter"])
        count += problems
        print(f"{lang}: {r['total'] - len(r['missing'])} of {r['total']} translated"
              + ("" if problems else ", all current"), file=out)
        for key, label in labels:
            if r[key]:
                print(f"  {label} ({len(r[key])}): {', '.join(r[key])}", file=out)
        if r["front_matter"]:
            pairs = ", ".join(f"{slug} ({key})" for slug, key in r["front_matter"])
            print(f"  front matter differs from the English ({len(r['front_matter'])}): {pairs}", file=out)
    return count


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--lang", action="append", help="only this language (repeatable)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when anything is reported")
    ap.add_argument("--stamp", nargs="+", metavar="PATH",
                    help="record the current English digest in these translations")
    args = ap.parse_args()
    if args.stamp:
        for name in args.stamp:
            path = Path(name).resolve()
            english = ARTICLES / path.name
            if path.parent.parent != ARTICLES or not english.is_file():
                raise SystemExit(f"{name}: not a translation of an article in {ARTICLES}")
            stamp(path, english.read_text(encoding="utf-8"))
            print(f"stamped {path.relative_to(ROOT)}")
        return
    problems = print_report(report(langs=args.lang))
    if args.strict and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
