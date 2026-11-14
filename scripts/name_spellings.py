"""Find names spelled more than one way in one language.

    python3 scripts/name_spellings.py                 print the report
    python3 scripts/name_spellings.py --write         write docs/review-notes/name-spellings.md
    python3 scripts/name_spellings.py --lang hi       one language, every variant

data/names.json lists the people, places and peoples of the text by Strong's
number, with their English names. Which records hold each name comes from
the word extracts (data/grc/, data/hbo/): a record holds a name when one of
its source tokens carries that Strong's number. Renderings have no
alignments outside a pilot, so a name's spelling in each language is found
from the text:

1. For a name and a language, take the records that hold the name and are
   rendered in the language, and every word (for Japanese, every katakana
   run) of their renderings at all levels.
2. The name's form is the word that occurs in the most of those records
   while being rare elsewhere (document frequency within the name's records,
   weighted by inverse frequency across the language). It must be in at
   least half of them, and in a cased script it must start with a capital.
3. A record whose renderings hold no word of that form (allowing for case
   endings: same stem) is a candidate. Its words that look like the form
   (similar letters, capitalised, not the same stem) are variant spellings.

Variants that recur are reported per language: the name, its usual form,
the variant and the records that use it. Some are deliberate: different
people who share a Strong's number (data/names.json has a sense for each),
a Hebrew and a Greek form of one name (Elijah, Elias), or a form a style
brief chooses. The report is a list for a reader, not a verdict.
"""
import argparse
import collections
import difflib
import glob
import json
import math
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from owb import markup  # noqa: E402

OUT = os.path.join(ROOT, "docs", "review-notes", "name-spellings.md")
CASED = {"en", "es", "fr", "sw", "vi", "pt", "ru", "uk"}
KATAKANA = re.compile(r"[ァ-ヴー・]{2,}")
MIN_RECORDS = 3
MIN_SHARE = 0.5
SIMILAR = 0.67
STRIP = "\"'“”‘’«»「」『』()[].,;:!?¿¡—–-·።፣፤፥፦।॥…"


def norm_strong(prefix, strong):
    """("H", "0871a") -> "H871a"."""
    m = re.fullmatch(r"0*(\d+)([a-z]?)", strong or "")
    return f"{prefix}{m[1]}{m[2]}" if m else None


def token_strongs():
    """{token id: (Strong's key, lemma)} for every word in data/grc and data/hbo."""
    found = {}
    for folder, prefix in (("grc", "G"), ("hbo", "H")):
        for path in glob.glob(os.path.join(ROOT, "data", folder, "*.json")):
            with open(path, encoding="utf-8") as f:
                for words in json.load(f)["verses"].values():
                    for word in words:
                        key = norm_strong(prefix, word.get("strong"))
                        if key:
                            found[word["id"]] = (key, unicodedata.normalize("NFC", word.get("lemma") or ""))
    return found


def load_names():
    """{Strong's key: entry}, merging entries that share a key."""
    with open(os.path.join(ROOT, "data", "names.json"), encoding="utf-8") as f:
        names = {}
        for entry in json.load(f)["names"]:
            key = norm_strong(entry["strong"][0], entry["strong"][1:])
            if not key:
                continue
            lemma = unicodedata.normalize("NFC", entry["lemma"])
            if key in names:
                names[key]["senses"] = names[key]["senses"] + entry["senses"]
                names[key]["lemmas"].add(lemma)
            else:
                names[key] = dict(entry, lemmas={lemma})
    return names


def load_records():
    for path in sorted(glob.glob(os.path.join(ROOT, "content", "*", "*.json"))):
        with open(path, encoding="utf-8") as f:
            yield from json.load(f)["records"]


def words(text, lang):
    """The words of a rendering as a reader sees it (default settings)."""
    text = markup.VERSE.sub(" ", markup.flat(markup.render(text)))
    if lang == "ja":
        return [w.strip("・") for w in KATAKANA.findall(text) if w.strip("・")]
    found = []
    for token in text.replace("—", " ").split():
        token = token.strip(STRIP)
        if any(ch.isalpha() for ch in token):
            found.append(token)
    return found


AMHARIC_PREFIX = ("እንደ", "ወደ", "በ", "የ", "ከ", "ለ")
AMHARIC_SUFFIX = ("ንም", "ም", "ን", "ና", "ስ")
KOREAN_PARTICLE = ("에게서", "으로부터", "께서는", "께서", "에게", "에서", "으로", "이여", "이요", "이며",
                   "이다", "와", "과", "의", "은", "는", "이", "가", "을", "를", "에", "도", "로", "께", "아", "야")


def stem(word, lang):
    """A word without the case ending, prefix or particle a name takes."""
    w = unicodedata.normalize("NFC", word).casefold()
    if lang in {"ru", "uk"} and len(w) > 4:
        return re.sub(r"(ом|ем|ой|ою|ею|ам|ям|ах|ях|ами|ові|еві|у|ю|а|я|е|і|и|ы|ь)$", "", w)
    if lang == "am":
        for prefix in AMHARIC_PREFIX:
            if w.startswith(prefix) and len(w) - len(prefix) >= 2:
                w = w[len(prefix):]
                break
        for suffix in AMHARIC_SUFFIX:
            if w.endswith(suffix) and len(w) - len(suffix) >= 2:
                w = w[:-len(suffix)]
                break
    if lang == "ko":
        for particle in KOREAN_PARTICLE:
            if w.endswith(particle) and len(w) - len(particle) >= 2:
                return w[:-len(particle)]
    if lang in {"en", "es", "fr", "pt", "sw", "vi"}:
        w = re.sub(r"[’']s$", "", w)
    return w


def same_stem(a, b, lang):
    """True if two stems are one name, allowing a short ending (Hindi
    यहूदियों beside यहूदी, English Israelites beside Israelite)."""
    if a == b:
        return True
    short, long_ = sorted((a, b), key=len)
    if lang in {"ko", "am"}:
        # particles and prefixes attach to the name: 다윗이, የሮቤል
        return len(short) >= 2 and short in long_
    if lang in {"ru", "uk"}:
        # declension changes the ending and sometimes the last vowel of
        # the stem (Пётр, Петра; Павел, Павла; Яків, Якова)
        a, b = a.replace("ё", "е"), b.replace("ё", "е")
        prefix = len(os.path.commonprefix([a, b]))
        return min(len(a), len(b)) >= 3 and prefix >= max(2, min(len(a), len(b)) - 2)
    if lang == "hi":
        short = short[:-1]
    return len(short) >= 3 and len(long_) - len(short) <= 3 and long_.startswith(short)


def looks_like_name(word, lang):
    return word[:1].isupper() if lang in CASED else True


def name_forms(records, strongs, names, langs=None):
    """{(lang, key): (form, [record ids], {variant stem: [(record id, word)]})}."""
    holding = collections.defaultdict(list)  # key -> records
    for record in records:
        # The token must carry the name's lemma too: names.json lists
        # Neapolis under the Strong's number of polis, "city".
        keys = {key for key, lemma in (strongs.get(t, (None, None)) for t in record["source"]["tokens"])
                if key in names and lemma in names[key]["lemmas"]}
        for key in keys:
            holding[key].append(record)
    doc_freq = collections.defaultdict(collections.Counter)
    totals = collections.Counter()
    record_words = {}  # record id -> {lang: {stem: word}}
    for recs in holding.values():
        for record in recs:
            if record["id"] in record_words:
                continue
            per = {}
            for lang, levels in record["renderings"].items():
                if langs and lang not in langs:
                    continue
                per[lang] = {stem(w, lang): w for text in levels.values()
                             for w in words(text, lang) if looks_like_name(w, lang)}
            record_words[record["id"]] = per
    for per in record_words.values():
        for lang, ws in per.items():
            totals[lang] += 1
            doc_freq[lang].update(ws.keys())
    found = {}
    for key, recs in holding.items():
        by_lang = collections.defaultdict(list)
        for record in recs:
            for lang, ws in record_words[record["id"]].items():
                by_lang[lang].append((record["id"], ws))
        for lang, items in by_lang.items():
            if len(items) < MIN_RECORDS:
                continue
            counts = collections.Counter(st for _rid, ws in items for st in ws)
            best, best_score = None, 0
            for st, n in counts.items():
                share = n / len(items)
                if share < MIN_SHARE or len(st) < 2:
                    continue
                score = share * math.log(1 + totals[lang] / doc_freq[lang][st])
                if score > best_score:
                    best, best_score = st, score
            if not best:
                continue
            spelled = collections.Counter(ws[best] for _rid, ws in items if best in ws).most_common(1)[0][0]
            missing, variants = [], collections.defaultdict(list)
            for rid, ws in items:
                if any(same_stem(st, best, lang) or same_stem(w.casefold(), spelled.casefold(), lang)
                   for st, w in ws.items()):
                    continue
                missing.append(rid)
                for st, w in sorted(ws.items()):
                    if (difflib.SequenceMatcher(None, st, best).ratio() >= SIMILAR
                            and not any(same_stem(st, v, lang) for v in variants if v != st)):
                        variants[st].append((rid, w))
            found[(lang, key)] = (spelled, missing, dict(variants))
    # A Strong's number whose English form is not capitalised is a common
    # noun that names.json lists for a name built on it (polis in Neapolis).
    for key in {k for _l, k in found}:
        english = found.get(("en", key))
        if english and not english[0][:1].isupper():
            for lang in [lang for lang, k in found if k == key]:
                del found[(lang, key)]
    return found


def sense_for(entry, rid):
    """The English name of the sense that covers record id rid."""
    verse = ".".join(rid.split(".")[:3])
    default = None
    for sense in entry["senses"]:
        if verse in sense.get("verses", ()):
            return sense["name"]
        if not sense.get("verses") and default is None:
            default = sense["name"]
    return default or entry["senses"][0]["name"]


def language_order():
    with open(os.path.join(ROOT, "data", "languages.json"), encoding="utf-8") as f:
        return [lang["code"] for lang in json.load(f)["reading"]]


def variant_rows(found, names, min_count=1):
    """[(lang, key, English name, form, variant, [record ids], senses differ)]."""
    rows = []
    for (lang, key), (form, _missing, variants) in found.items():
        for _stem, uses in variants.items():
            rids = sorted({rid for rid, _w in uses})
            if len(rids) < min_count:
                continue
            spelled = collections.Counter(w for _rid, w in uses).most_common(1)[0][0]
            entry = names[key]
            senses = {sense_for(entry, rid) for rid in rids}
            rows.append((lang, key, entry["senses"][0]["name"], form, spelled, rids,
                         len(entry["senses"]) > 1, sorted(senses)))
    order = language_order()
    rows.sort(key=lambda r: (order.index(r[0]) if r[0] in order else 99, -len(r[5]), r[2]))
    return rows


# What a reader has already made of the list (kept in the report when it is
# regenerated; update it with each review pass).
REVIEWED = """## Reviewed (November 2026)

Fixed, the same person or place spelled two ways with no reason in a brief:

- ru: Uzziel, Leviticus 10:4 Озиил to Узиил, as Exodus 6:18-22.
- uk: Beelzebul, Mark 3:22 Вельзевул to Веельзевул, as Matthew and Luke
  (the Matthew 12 decision chooses Веельзевул, the form close to the Greek).
- hi: Uzziel, Numbers 3:19, 3:27, 3:30 उज्जीएल to उज़्ज़ीएल (the Leviticus 10:4
  decision chooses the nukta form, "one form through the book"); Euphrates,
  Deuteronomy 11:24 and Numbers 22:5 फरात to फ़रात, as the other 30 places;
  Aram-naharaim, Judges 3:8 अरम-नहरैम to अराम-नहरैम, as Genesis 24:10 and
  Deuteronomy 23:5.
- am: Uzziel, Leviticus 10:4 ዑዚኤል to ዑዝኤል, as the other 52 places; Izhar,
  Numbers 16:1 ይስሐር to ይስዓር, as the other 30.
- es: Capernaum, John and Mark Capernaúm to Cafarnaúm, the form
  docs/nt-spanish-swahili-terms.md sets and Matthew and Luke use (28 places).
- uk (after the Ukrainian Old Testament was merged; docs/ukrainian-ot-terms.md
  asks for "one form per name through every book"): Lebanon Ліван to Ливан
  (Kings, Chronicles, Ezra, Jeremiah, Ezekiel; Psalms in the patch file), as
  Deuteronomy, Joshua, Isaiah and the Song; Shiloh Шило to Шіло (1 Samuel,
  2 Chronicles, Jeremiah), as Joshua, Judges and Psalm 78 decide; Migdol
  Мігдол to Мигдол (Numbers, Ezekiel), as Exodus; Aram-naharaim Нахараїм to
  Нагараїм (Judges 3:8), as Genesis and Deuteronomy, with г for h; Ishvi
  Ішві to Їшві (1 Samuel 14:49), as Genesis and Numbers; Benjamin Веніамин to
  Веніямин (Romans 11:1), the terms note's form; Bethlehem Віфлеєм to
  Вифлеєм (Jeremiah 41:17), the style brief's form.

Deliberate, left as they are:

- Nebuchadnezzar and Nebuchadrezzar follow each verse's Hebrew in every
  language (ko 느부갓네살 / 느부갓레살; the Jeremiah and Ezekiel term notes).
- Different people who share a name and a Strong's number keep the form
  their tradition gives each: Korean 아미나답 (Judah) and 암미나답 (the Levite,
  1 Chronicles 15:10-11); Amharic ኢዩኤል for Joel the prophet (the book's name)
  beside ኢዮኤል for other Joels; Amharic ማቲትያ (the musician, 1 Chronicles
  15-16, 25) and መቲትያ (others); English, Portuguese, Swahili Saul / Shaul,
  Enoch / Hanoch, Isaiah / Jeshaiah.
- Endings and derived words the matching cannot tell from a variant:
  Egypt / Egyptians, Levites / a Levite, Swahili Wayahudi / Myahudi,
  Hamath / Lebo-hamath, Dibon / Dibon-gad.

Left for a reviewer: Hindi ज़कर्याह / जकर्याह (Zechariah, several people) and
Ukrainian Натанаїл / Нетанеїл (Nethanel, several people), where the
nukta or the Greek-shaped form may be chosen per person; Ukrainian Гад /
Ґад (the tribe and the prophet Gad). Not yet read: the remaining English, Spanish, French, Swahili, Vietnamese and
Portuguese variants below (for example Spanish Libna / Libná, Jaír / Jair,
Seír / Seir; French Bashân / Basan, Yazer / Jazer; Vietnamese Mích-ba /
Mích-pa, Cô-ra / Cô-rê). Most look like book-by-book drafting differences
for that language's reviewer to settle against its brief."""


def render_report(rows, found, limit=40):
    order = language_order()
    per_lang = collections.Counter(r[0] for r in rows)
    checked = collections.Counter(lang for lang, _key in found)
    out = ["# Name spellings", "",
           "Generated by `python3 scripts/name_spellings.py --write`; the method is in the",
           "script's docstring. A variant is a word that looks like a name's usual form in a",
           "record that holds the name but not the usual form. \"Shared\" marks a Strong's",
           "number that names more than one person or place in data/names.json, where a",
           "different spelling may be deliberate.", "", REVIEWED, "",
           "| lang | names checked | variants | in 2+ records |", "|---|---|---|---|"]
    for lang in order:
        if checked[lang]:
            multi = sum(1 for r in rows if r[0] == lang and len(r[5]) > 1)
            out.append(f"| {lang} | {checked[lang]} | {per_lang[lang]} | {multi} |")
    for lang in order:
        lang_rows = [r for r in rows if r[0] == lang]
        if not lang_rows:
            continue
        out += ["", f"## {lang}", "",
                "| name | Strong's | usual | variant | records | where |", "|---|---|---|---|---|---|"]
        for _lang, key, name, form, variant, rids, shared, senses in lang_rows[:limit]:
            where = ", ".join(rids[:4]) + (f" (+{len(rids) - 4})" if len(rids) > 4 else "")
            note = " (shared: " + "; ".join(senses) + ")" if shared else ""
            out.append(f"| {name}{note} | {key} | {form} | {variant} | {len(rids)} | {where} |")
        if len(lang_rows) > limit:
            out.append(f"\n{len(lang_rows) - limit} more: `python3 scripts/name_spellings.py --lang {lang}`.")
    return "\n".join(out) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--lang", help="list every variant of one language")
    args = parser.parse_args(argv)
    names = load_names()
    found = name_forms(list(load_records()), token_strongs(), names,
                       langs={args.lang, "en"} if args.lang else None)
    rows = variant_rows(found, names)
    if args.lang:
        for lang, key, name, form, variant, rids, shared, senses in rows:
            if lang != args.lang:
                continue
            print(f"{key}\t{name}\t{form}\t{variant}\t{len(rids)}\t{' '.join(rids)}"
                  + ("\tshared: " + "; ".join(senses) if shared else ""))
        return 0
    text = render_report(rows, found)
    if args.write:
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
