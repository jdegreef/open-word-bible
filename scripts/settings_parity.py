"""Check that reader settings are used alike across languages and levels.

    python3 scripts/settings_parity.py              span counts and parity per language
    python3 scripts/settings_parity.py --levels     also the cross-level check
    python3 scripts/settings_parity.py --levels --list en deity_pronoun
                                                    list that language's cross-level candidates
    python3 scripts/settings_parity.py --strict     exit 1 on an undocumented outlier

Parity across languages. A setting span marks one choice of wording (a
default and its alternatives), so where the English has a span, a language
that can make the same choice should normally have one too. For each
language and setting the script counts the spans, and the share of the
records the English spans (at any level) where that language spans the same
setting (at any level). A share far below the other languages' median, or
zero, is an outlier. Some outliers are by design, and the language's style
brief says why: those are listed in DOCUMENTED with the brief that explains
them and are reported as documented, not as outliers. Settings only some
languages have (plural_you, Spanish) are counted but not compared.

Parity across levels. A record's levels say the same thing, so a pronoun for
God that Balanced spans should be spanned at Readable too, where Readable
uses the same word. For deity_pronoun, christos and divine_name the script
looks at every record, language and pair of levels where one level spans the
setting and the other has no span of it, and asks whether the other level
holds the first level's default wording unwrapped (the signal). Without the
signal the levels just word it differently (Readable says "God" or "Jesus",
or starts the sentence with "He", which needs no span): fine. With it the
record is a candidate, and a "likely gap" when the other level has more
unwrapped copies of that wording than the spanned level has: the extra copy
is probably the pronoun or title that lost its span. Candidates still need a
reader: the same "he" can be someone else.
"""
import argparse
import collections
import glob
import json
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from owb import markup  # noqa: E402

LEVELS = ("L", "B", "R")
# Settings whose spans the cross-level check follows.
LEVEL_SETTINGS = ("deity_pronoun", "christos", "divine_name")
# Languages whose words are not separated by spaces, or take particles and
# suffixes on the same word: their wording is matched as a substring, not as
# a whole word.
NO_WORD_BOUNDARY = {"ja", "ko", "am", "hi"}
# A language whose share is below this fraction of the median is an outlier.
OUTLIER_RATIO = 0.5

# Outliers by design: (language, setting) -> where the brief explains it.
DOCUMENTED = {
    ("hi", "christos"): "docs/hindi-style.md section 7: मसीह is both the name and the word Messiah",
    ("hi", "deity_pronoun"): "docs/hindi-style.md section 7: Devanagari has no capitals",
    ("am", "deity_pronoun"): "docs/amharic-style.md: the Ethiopic script has no capitals",
    ("ko", "deity_pronoun"): "docs/korean-style.md: Korean has no capitals",
    ("ja", "deity_pronoun"): "docs/japanese-style.md: Japanese has no capitals",
    ("sw", "gender"): "docs/swahili-style.md section 7: Swahili nouns for people are already inclusive",
    ("sw", "deity_pronoun"): "docs/swahili-style.md section 7: most pronouns are inside the verb",
    ("vi", "gender"): "docs/vietnamese-style.md: Vietnamese nouns for people are already inclusive",
    ("ko", "gender"): "docs/korean-style.md: Korean nouns for people are already inclusive",
    ("am", "gender"): "docs/amharic-style.md: Amharic nouns for people are often already inclusive",
    ("ja", "gender"): "docs/japanese-style.md: Japanese words for people are already inclusive",
    ("hi", "gender"): "docs/hindi-style.md section 7: Hindi nouns for people are often already inclusive",
}


def load_records(paths=None):
    """Every record in content/, or in the given files."""
    paths = paths or sorted(glob.glob(os.path.join(ROOT, "content", "*", "*.json")))
    for path in paths:
        with open(path, encoding="utf-8") as f:
            yield from json.load(f)["records"]


def setting_spans(text, setting):
    return [s for s in markup.spans(text) if s.setting == setting]


def counts(records):
    """({lang: Counter(setting -> spans)}, {lang: records rendered})."""
    spans_by_lang = collections.defaultdict(collections.Counter)
    rendered = collections.Counter()
    for record in records:
        for lang, levels in record["renderings"].items():
            rendered[lang] += 1
            for text in levels.values():
                for span in markup.spans(text):
                    spans_by_lang[lang][span.setting] += 1
    return spans_by_lang, rendered


def parity(records, pivot="en"):
    """{(lang, setting): (records the pivot spans, of which lang spans it too)}."""
    found = collections.defaultdict(lambda: [0, 0])
    for record in records:
        renderings = record["renderings"]
        pivot_settings = {s.setting for text in renderings.get(pivot, {}).values()
                          for s in markup.spans(text)}
        for lang, levels in renderings.items():
            if lang == pivot:
                continue
            own = {s.setting for text in levels.values() for s in markup.spans(text)}
            for setting in pivot_settings:
                found[(lang, setting)][0] += 1
                found[(lang, setting)][1] += setting in own
    return {key: tuple(value) for key, value in found.items()}


def outliers(shares, documented=DOCUMENTED, ratio=OUTLIER_RATIO):
    """[(lang, setting, share, median, note)] for shares far below the median.

    shares maps (lang, setting) to a share between 0 and 1. note is the
    documented reason, or None for an outlier nobody has explained."""
    by_setting = collections.defaultdict(dict)
    for (lang, setting), share in shares.items():
        by_setting[setting][lang] = share
    found = []
    for setting, per_lang in sorted(by_setting.items()):
        median = statistics.median(per_lang.values())
        for lang, share in sorted(per_lang.items()):
            if share == 0 or share < ratio * median:
                found.append((lang, setting, share, median, documented.get((lang, setting))))
    return found


def occurrences(text, wording, lang):
    """How often wording appears in text outside setting spans."""
    plain = markup.SPAN.sub(" ⁣ ", markup.flat(text))
    if lang in NO_WORD_BOUNDARY:
        return plain.count(wording)
    return len(re.findall(r"(?<![\w’'-])" + re.escape(wording) + r"(?![\w’'])", plain))


def corroborating(record, lang, setting, level):
    """How many other languages span setting at this level of the record."""
    return sum(1 for other, levels in record["renderings"].items()
               if other != lang and setting_spans(levels.get(level, ""), setting))


def level_candidates(records, settings=LEVEL_SETTINGS, langs=None):
    """Cross-level pairs: yield (record id, lang, setting, spanned level,
    other level, kind, wordings), kind being "fine", "candidate" or "likely_gap".

    A candidate is a likely gap when at least two other languages span the
    setting at the other level of the same record: they found a pronoun (or
    title, or name) for God there, so this language probably has one too."""
    for record in records:
        for lang, levels in record["renderings"].items():
            if langs and lang not in langs:
                continue
            for setting in settings:
                spanned = {lv: setting_spans(levels[lv], setting) for lv in LEVELS if lv in levels}
                for a in LEVELS:
                    if not spanned.get(a):
                        continue
                    for b in LEVELS:
                        if b == a or b not in spanned or spanned[b]:
                            continue
                        wordings = sorted({s.options[0] for s in spanned[a]})
                        hits = [w for w in wordings if w.strip() and occurrences(levels[b], w, lang)]
                        if not hits:
                            kind = "fine"
                        elif corroborating(record, lang, setting, b) >= 2:
                            kind = "likely_gap"
                        else:
                            kind = "candidate"
                        yield record["id"], lang, setting, a, b, kind, hits


def level_summary(records, **kw):
    """{(lang, setting): Counter(kind -> records)}, each record counted once
    per kind (its worst pair: likely_gap, then candidate, then fine)."""
    rank = {"fine": 0, "candidate": 1, "likely_gap": 2}
    worst = {}
    for rid, lang, setting, _a, _b, kind, _hits in level_candidates(records, **kw):
        key = (rid, lang, setting)
        if rank[kind] >= rank.get(worst.get(key), -1):
            worst[key] = kind
    summary = collections.defaultdict(collections.Counter)
    for (_rid, lang, setting), kind in worst.items():
        summary[(lang, setting)][kind] += 1
    return summary


def language_order():
    with open(os.path.join(ROOT, "data", "languages.json"), encoding="utf-8") as f:
        return [lang["code"] for lang in json.load(f)["reading"]]


def report(records, show_levels=False):
    """The report as text, and the undocumented outliers."""
    records = list(records)
    order = language_order()
    spans_by_lang, rendered = counts(records)
    langs = [lang for lang in order if lang in rendered]
    out = ["## Spans per language", "",
           "| lang | records | " + " | ".join(markup.SETTINGS) + " |",
           "|---" * (len(markup.SETTINGS) + 2) + "|"]
    for lang in langs:
        out.append(f"| {lang} | {rendered[lang]} | "
                   + " | ".join(str(spans_by_lang[lang][s]) for s in markup.SETTINGS) + " |")
    pairs = parity(records)
    shares = {key: (hit / total) for key, (total, hit) in pairs.items() if total}
    out += ["", "## Parity with English",
            "",
            "Of the records where the English spans a setting, the share where the",
            "language spans it too.", "",
            "| lang | " + " | ".join(s for s in markup.SETTINGS if s != "plural_you") + " |",
            "|---" * len(markup.SETTINGS) + "|"]
    for lang in langs[1:]:
        cells = []
        for setting in markup.SETTINGS:
            if setting == "plural_you":
                continue
            total, hit = pairs.get((lang, setting), (0, 0))
            cells.append(f"{hit}/{total} ({hit / total:.0%})" if total else "-")
        out.append(f"| {lang} | " + " | ".join(cells) + " |")
    found = outliers(shares)
    out += ["", "## Outliers", ""]
    undocumented = []
    for lang, setting, share, median, note in found:
        line = f"- {lang} {setting}: {share:.0%} (median {median:.0%})"
        if note:
            out.append(line + f": documented, {note}")
        else:
            out.append(line + ": **not documented**")
            undocumented.append((lang, setting))
    if not found:
        out.append("None.")
    if show_levels:
        summary = level_summary(records)
        out += ["", "## Across levels", "",
                "Records where one level spans the setting and another has no span of it.",
                "", "| lang | setting | fine | candidate | likely gap |", "|---|---|---|---|---|"]
        for lang in langs:
            for setting in LEVEL_SETTINGS:
                c = summary.get((lang, setting))
                if c:
                    out.append(f"| {lang} | {setting} | {c['fine']} | {c['candidate']} | {c['likely_gap']} |")
    return "\n".join(out), undocumented


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--levels", action="store_true", help="also check across levels")
    parser.add_argument("--list", nargs=2, metavar=("LANG", "SETTING"),
                        help="list the cross-level candidates of one language and setting")
    parser.add_argument("--strict", action="store_true", help="exit 1 on an undocumented outlier")
    parser.add_argument("files", nargs="*", help="record files (default: all of content/)")
    args = parser.parse_args(argv)
    records = list(load_records(args.files or None))
    if args.list:
        lang, setting = args.list
        for rid, _lang, _s, a, b, kind, hits in level_candidates(records, settings=(setting,), langs={lang}):
            if kind != "fine":
                print(f"{rid}\t{a}->{b}\t{kind}\t{' / '.join(hits)}")
        return 0
    text, undocumented = report(records, show_levels=args.levels)
    print(text)
    return 1 if args.strict and undocumented else 0


if __name__ == "__main__":
    sys.exit(main())
