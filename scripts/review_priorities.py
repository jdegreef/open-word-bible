"""Where a native reviewer of one language starts: a priorities list built from the data.

    python3 scripts/review_priorities.py am            print the list
    python3 scripts/review_priorities.py am --write    write docs/review-notes/am-review-priorities.md

Four sections, each generated from content/ so it can be regenerated after
review work:

1. every rendering decision in the language marked uncertain, by book, with
   its levels, choice, alternatives and a one-line question for the reviewer;
2. about forty passages to read first: the best-known passages, and those the
   drafting found hardest (PASSAGES below, the one hand-kept list), each with
   its counts of decisions and uncertain decisions;
3. name forms the drafters say they coined (a "new" form, one not used in an
   earlier book), with how often each is used and any other spelling of it,
   letters that sound alike counted as the same (ሀ ሐ ኀ ሃ, ሰ ሠ, አ ዐ ኣ, ጸ ፀ);
4. decisions that mention an older Bible in the language, familiar wording
   or rewording, so a reviewer can compare the passage with that Bible.

Only Amharic so far: the questions and the patterns for older Bibles and
name forms are written for its decisions. Records stay ai_draft until a named reviewer approves them in the admin;
nothing here changes a record.
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from owb import refs, versification  # noqa: E402

SITE = "https://openwordbible.org"
REASON_MAX = 260

# (first verse, last verse, why) in our (Hebrew) numbering; the label gives the
# English numbering where it differs. Best-known passages first, then the
# passages the drafting reports found hardest.
PASSAGES = [
    ("known", "GEN.1.1", "GEN.2.3", "Creation: the opening every reader knows"),
    ("known", "GEN.2.4", "GEN.2.25", "The garden, the man and the woman"),
    ("known", "GEN.3.1", "GEN.3.24", "The serpent and the fall"),
    ("known", "GEN.12.1", "GEN.12.9", "The call of Abram"),
    ("known", "GEN.22.1", "GEN.22.19", "The binding of Isaac"),
    ("known", "EXO.3.1", "EXO.3.15", "The burning bush and the name (the divine name setting)"),
    ("known", "EXO.20.1", "EXO.20.17", "The Ten Commandments"),
    ("known", "EXO.34.6", "EXO.34.7", "The LORD's self-description, quoted through the Old Testament"),
    ("known", "NUM.6.22", "NUM.6.27", "The priestly blessing"),
    ("known", "DEU.6.4", "DEU.6.9", "The Shema"),
    ("known", "RUT.1.16", "RUT.1.17", "Ruth's vow"),
    ("known", "PSA.1.1", "PSA.1.6", "Psalm 1"),
    ("known", "PSA.22.1", "PSA.22.32", "Psalm 22, quoted at the cross"),
    ("known", "PSA.23.1", "PSA.23.6", "Psalm 23"),
    ("known", "PSA.51.1", "PSA.51.21", "Psalm 51"),
    ("known", "ISA.6.1", "ISA.6.13", "Isaiah's vision"),
    ("known", "ISA.9.1", "ISA.9.6", "\"To us a child is born\""),
    ("known", "ISA.40.1", "ISA.40.11", "\"Comfort, comfort my people\""),
    ("known", "ISA.52.13", "ISA.53.12", "The suffering servant"),
    ("known", "JER.31.31", "JER.31.34", "The new covenant"),
    ("known", "EZK.37.1", "EZK.37.14", "The valley of dry bones"),
    ("known", "MAT.5.1", "MAT.5.48", "The Sermon on the Mount: the Beatitudes and the Law"),
    ("known", "MAT.6.1", "MAT.6.34", "The Sermon on the Mount: the Lord's Prayer"),
    ("known", "MAT.7.1", "MAT.7.29", "The Sermon on the Mount: the end"),
    ("known", "LUK.2.1", "LUK.2.20", "The birth of Jesus"),
    ("known", "JHN.1.1", "JHN.1.18", "The Word"),
    ("known", "JHN.3.1", "JHN.3.21", "Nicodemus; John 3:16"),
    ("known", "ROM.3.9", "ROM.3.31", "All have sinned; righteousness through faith"),
    ("known", "ROM.5.1", "ROM.5.21", "Peace with God; Adam and Christ"),
    ("known", "ROM.6.1", "ROM.7.25", "Dead to sin; the Law and the divided self"),
    ("known", "ROM.8.1", "ROM.8.39", "Life in the Spirit"),
    ("known", "1CO.13.1", "1CO.13.13", "Love"),
    ("hard", "EZK.16.1", "EZK.16.63", "Register: Jerusalem as an unfaithful wife, frank at Literal"),
    ("hard", "EZK.23.1", "EZK.23.49", "Register: Oholah and Oholibah, frank at Literal"),
    ("hard", "SNG.1.1", "SNG.8.14", "Register and imagery: love poetry at three levels"),
    ("hard", "DAN.9.24", "DAN.9.27", "The seventy weeks: a disputed text"),
    ("hard", "HOS.6.1", "HOS.6.6", "\"Steadfast love, not sacrifice\", quoted by Jesus"),
    ("hard", "AMO.9.7", "AMO.9.7", "Israel and the Cushites: the name Cush in Amharic"),
    ("hard", "MIC.1.10", "MIC.1.15", "Wordplay on town names that Amharic cannot keep"),
    ("hard", "MIC.5.1", "MIC.5.1", "Bethlehem, quoted in Matthew 2:6"),
    ("hard", "HAB.2.4", "HAB.2.4", "\"The righteous shall live by faith\", quoted by Paul"),
    ("hard", "ZEC.9.9", "ZEC.9.9", "The king on a donkey, quoted in the Gospels"),
    ("hard", "MAL.3.1", "MAL.3.1", "\"My messenger\", quoted of John the Baptist"),
]

NEW_NAME = re.compile(
    r"(?<!the )(?<!his )(?<!'s )(?<!in a )\bnew names?\b|\bnew (?:form|spelling)s?\b|\((?:a )?new(?:\)|,)"
    r"|\b(?:is|are) new\b|\bnew here\b|\bnew:|\bnot yet on main\b"
    r"|\bno (?:established|traditional) (?:Amharic )?(?:form|name|spelling)"
    r"|\"[\u1200-\u137f ]+\"(?: \([^)]*\))? new\b", re.I)
NAMEISH = re.compile(r"\bnames?\b|spell|transcri|\bforms?\b", re.I)
GENERIC_NEW = re.compile(r"\bnew names?\b", re.I)
UNSURE_NAME = re.compile(r"spelling (?:is not certain|should be checked)|as best recalled", re.I)
AS_BEFORE = re.compile(r"\bas (?:on main|in |the |for |[1-3]?\s?[A-Z][a-z]+ \d)|\bkept\b")
NOT_THIS = re.compile(r"(?:rather than|instead of|\bnot)\s*$")
QUOTED = re.compile(r"\"([\u1200-\u137f][\u1200-\u137f ]*)\"")
BARE = re.compile(r"[\u1200-\u135a]+")
# An English name beside its Amharic form: "ፋቁድ" (Pekod), "ይዱቱን" for Jeduthun, Pekod "ፋቁድ".
PAIRS = (re.compile(r"\"([\u1200-\u137f][\u1200-\u137f ]*)\" (?:\(|for )([A-Z][\w-]+)"),
         re.compile(r"([A-Z][\w-]+) (?:is )?\"([\u1200-\u137f][\u1200-\u137f ]*)\""))
OLDER = re.compile(
    r"1962|1954|1980|\breword\w*|familiar (?:wording|phrase|rendering|verse|line)s?"
    r"|well-known (?:wording|version|translation|rendering)s?"
    r"|(?:older|earlier|existing|traditional|other|copyrighted) (?:Amharic )?(?:Bible|translation|version)s?"
    r"|Bible Society|Standard Version|Living Bible|Easy-to-Read", re.I)
WORD_SPLIT = re.compile(r"[\s።፣፤፥፦፧፨«»“”‘’\"?!.,;:()\[\]{}|\\]+")

# Letters that sound alike: each family's first letter, mapped to the one
# that stands for all of them (each family holds seven or eight vowel orders).
SAME_SOUND = {0x1210: 0x1200, 0x1280: 0x1200, 0x1220: 0x1230, 0x12d0: 0x12a0, 0x1340: 0x1338}
PREFIXES = ("እንደ", "ወደ", "ስለ", "ከ", "የ", "በ", "ለ")
SUFFIXES = ("ንም", "ን", "ም", "ና", "ስ")


def ref_key(verse_id):
    return refs.parse(verse_id).sort_key()


def short(text, limit=REASON_MAX):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + " …"


def same_sound(word):
    """word with each letter that sounds like another written as one form."""
    out = []
    for ch in word:
        cp = ord(ch)
        base = SAME_SOUND.get(cp - cp % 8 if 0x1200 <= cp < 0x1380 else None)
        out.append(chr(base + cp % 8) if base is not None else ch)
    # ሀ and ሃ, አ and ኣ are said alike too.
    return "".join(out).translate({0x1203: 0x1200, 0x12a3: 0x12a0})


def cores(token):
    """The forms a token may be a name in: as written, without a case prefix,
    without a suffix, and without both."""
    found = {token}
    for p in PREFIXES:
        if token.startswith(p) and len(token) > len(p) + 1:
            found.add(token[len(p):])
    for t in list(found):
        for s in SUFFIXES:
            if t.endswith(s) and len(t) > len(s) + 1:
                found.add(t[:-len(s)])
    return found


def load(lang):
    """[(book, record)] in canonical order of book and first verse."""
    out = []
    for path in glob.glob(os.path.join(ROOT, "content", "*", "*.json")):
        book = os.path.basename(os.path.dirname(path))
        for record in json.load(open(path, encoding="utf-8"))["records"]:
            if lang in record["renderings"]:
                out.append((book, record))
    out.sort(key=lambda item: ref_key(item[1]["refs"][0]))
    return out


def link(lang, verse_id):
    book, chapter, verse = verse_id.split(".")
    return f"{SITE}/{lang}/{book.lower()}/{chapter}/#v{verse}"


def label(verse_id, books, end=None):
    """ "Genesis 1:1" or "Genesis 1:1–2:3", with the English numbering after it
    where it differs."""
    def cv(ref):
        return f"{ref.chapter}:{ref.verse}"

    def english(ref, last):
        eng = versification.to_english(ref)
        if not eng:
            return None
        return eng[-1] if last else eng[0]

    start = refs.parse(verse_id)
    stop = refs.parse(end) if end else start
    name = books[start.book]["en"]
    text = cv(start) if stop == start else (
        f"{cv(start)}–{stop.verse}" if stop.chapter == start.chapter else f"{cv(start)}–{cv(stop)}")
    e1, e2 = english(start, False), english(stop, True)
    if e1 and e2 and (e1, e2) != (start, stop):
        alt = cv(e1) if e1 == e2 else (f"{cv(e1)}–{e2.verse}" if e1.chapter == e2.chapter else f"{cv(e1)}–{cv(e2)}")
        if alt != text:
            text += f" (English {alt})"
    return f"{name} {text}"


def question(d):
    """A one-line question for the reviewer about decision d."""
    text = f"{d['choice']} {d['reason']}"
    alts = d.get("alternatives") or []
    chosen = QUOTED.findall(d["choice"])
    other = next((m for a in alts for m in QUOTED.findall(a)), None)
    if d["category"] == "register":
        return ("Is the register right for each level (close at Literal, fit for public reading at "
                "Balanced, plain at Readable), and can it be read aloud in church?")
    if d["category"] == "setting_alternative":
        return "Do both options of the setting read naturally here, and is the default the right one?"
    if d["category"] == "supplied_words":
        return "Are the supplied words needed, and are they natural Amharic?"
    if d["category"] == "word_order":
        return "Does this order read naturally while each verse keeps its own content after its number?"
    if re.search(r"\b(?:bird|tree|plant|animal|insect|stone|gem|jewel|identif|fabric|instrument)", text, re.I):
        return "Which Amharic word, if any, do readers know for this, and is the drafted one clear?"
    if re.search(r"\b(?:spell|name|transcri)", text, re.I) and chosen:
        if "፣" in chosen[0] or len(chosen) > 2:
            return "Are these the spellings Amharic readers know, or the right forms for new names?"
        return f"Is «{chosen[0]}» the spelling Amharic readers know, or the right form for a new name?"
    if chosen and other:
        return f"Is «{chosen[0]}» right here, or is «{other}» better?"
    if chosen:
        return f"Is «{chosen[0]}» accurate and natural here, or is there a better Amharic word?"
    return "Is this wording accurate and natural Amharic, or should it change?"


def uncertain(data, lang):
    """{book: [(verse id, decision)]} for the uncertain rendering decisions."""
    groups = defaultdict(list)
    for book, record in data:
        for d in record["decisions"]:
            if d.get("language") == lang and d.get("uncertain"):
                groups[book].append((record["refs"][0], d))
    return groups


def _quoted_new(clause):
    """Quoted Amharic forms in clause, leaving out parts kept from an earlier
    book ("as on main", "as Judges 9") and forms set aside ("rather than ...")."""
    forms = []
    parts = clause.split(",") if AS_BEFORE.search(clause) else [clause]
    for part in parts:
        if AS_BEFORE.search(part) and not NEW_NAME.search(part):
            continue
        for m in QUOTED.finditer(part):
            if not NOT_THIS.search(part[:m.start()]):
                forms.append(m.group(1))
    return forms


def _paired(choice):
    """{English name: Amharic form} for the names the choice gives in both."""
    pairs = {}
    for m in PAIRS[0].finditer(choice):
        pairs.setdefault(m.group(2), m.group(1))
    for m in PAIRS[1].finditer(choice):
        pairs.setdefault(m.group(1), m.group(2))
    return pairs


def new_forms(d):
    """The name forms decision d says are new, and whether it says so at all:
    (forms, flagged, unsure). A form the decision keeps from an earlier book
    does not count; forms it calls new only in its reason are found there,
    unquoted or by their English names."""
    choice, reason = d["choice"], d["reason"]
    flagged = bool((NEW_NAME.search(choice) or NEW_NAME.search(reason)) and NAMEISH.search(choice + reason))
    unsure = bool(UNSURE_NAME.search(reason))
    if not (flagged or unsure):
        return [], False, False
    forms = [f for clause in choice.split(";") if NEW_NAME.search(clause) for f in _quoted_new(clause)]
    if not forms and flagged:
        pairs = _paired(choice)
        for sentence in re.split(r"(?<=\.)\s+", reason):
            if not NEW_NAME.search(sentence):
                continue
            found = _quoted_new(sentence) or BARE.findall(QUOTED.sub("", sentence))
            if not found:
                for scope in [f for f in sentence.split(";") if NEW_NAME.search(f)], [sentence]:
                    found = [pairs[w] for f in scope for w in re.findall(r"[A-Z][\w-]+", f) if w in pairs]
                    if found:
                        break
            if not found and GENERIC_NEW.search(sentence):
                named = set(pairs.values())
                found = [f for clause in choice.split(";") for f in _quoted_new(clause) if f in named]
            forms += found
    if not forms and unsure:
        forms = QUOTED.findall(choice)
    unique = []
    for f in forms:
        if len(f.replace(" ", "")) > 1 and len(f.split()) <= 3 and f not in unique:
            unique.append(f)
    return unique, flagged, unsure


def name_index(data, lang):
    """({core form: set of verse ids}, {same-sound form: Counter of spellings})."""
    verses, spellings = defaultdict(set), defaultdict(Counter)
    for _, record in data:
        text = " ".join(record["renderings"][lang].values())
        text = re.sub(r"\{\{\w+:", " ", text).replace("}}", " ")
        text = re.sub(r"\\[a-z]+\d?", " ", text)
        for token in WORD_SPLIT.split(text):
            if not token:
                continue
            for core in cores(token):
                verses[core].add(record["refs"][0])
                spellings[same_sound(core)][core] += 1
    return verses, spellings


def older(d):
    """The sentences of decision d's text that mention an older Bible or familiar wording."""
    found = []
    for field in ("choice", "reason"):
        for sentence in re.split(r"(?<=[.;])\s+", d[field]):
            if OLDER.search(sentence):
                found.append(sentence)
    for alt in d.get("alternatives") or []:
        if OLDER.search(alt):
            found.append(f"Alternative: {alt}")
    return found


def terms_notes(lang_name):
    """(file, line number, text) of lines in the language's terms docs that
    mention an older Bible or familiar wording."""
    out = []
    pattern = os.path.join(ROOT, "docs", f"*{lang_name.lower()}*.md")
    for path in sorted(glob.glob(pattern)):
        if "review" in os.path.basename(path):
            continue
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            if re.search(r"1962|1954|1980|\breword|familiar wording|well-known version", line):
                out.append((os.path.relpath(path, ROOT), n, line.strip()))
    return out


def render(lang):
    books = json.load(open(os.path.join(ROOT, "data", "books.json"), encoding="utf-8"))["books"]
    lang_name = next(x["name"] for x in json.load(open(os.path.join(ROOT, "data", "languages.json"),
                                                         encoding="utf-8"))["reading"] if x["code"] == lang)
    data = load(lang)
    groups = uncertain(data, lang)
    order = sorted(groups, key=refs.BOOK_CODES.index)
    total = sum(len(v) for v in groups.values())
    ot = sum(len(groups[b]) for b in order if b in refs.OT_CODES)

    def book_name(code):
        own = books[code].get(lang)
        return f"{books[code]['en']} ({own})" if own and own != books[code]["en"] else books[code]["en"]

    out = [f"# {lang_name} review priorities", "",
           f"Generated by `python3 scripts/review_priorities.py {lang} --write`; do not edit by hand. "
           f"Built from the {lang_name} renderings in `content/` ({len(data)} records), for the native "
           f"reviewers who start with [the {lang_name} review guide](../{lang_name.lower()}-review-guide.md). "
           "Every record is `ai_draft`: ticking a box here changes nothing. A reviewer approves or flags "
           "a sentence in the site admin's Review page, and a choice settled differently is changed in its "
           "terms doc and in every passage drafted under it.", "",
           "Links go to the verse on the site. Verse numbers are those of the Hebrew and Greek, as in "
           "`content/`; where English Bibles number a verse differently, the English number follows in "
           "brackets. Levels are L (Literal), B (Balanced), R (Readable).", "",
           "1. [Uncertain decisions](#1-uncertain-decisions)",
           "2. [Passages to read first](#2-passages-to-read-first)",
           "3. [New name forms to confirm](#3-new-name-forms-to-confirm)",
           "4. [Possible closeness to older Amharic Bibles](#4-possible-closeness-to-older-amharic-bibles)"
           if lang == "am" else "4. [Possible closeness to older Bibles](#4-possible-closeness-to-older-bibles)",
           ""]

    # 1. Uncertain decisions.
    out += ["## 1. Uncertain decisions", "",
            f"{total} {lang_name} rendering decisions are marked uncertain: {ot} in the Old Testament and "
            f"{total - ot} in the New, in {len(order)} books. Each gives the verse, the levels, the "
            "category, the choice, the alternatives the drafter weighed and a question to answer. "
            "Answer it in the Review page's note (approve if the drafted wording stands; flag it with the "
            "wording you want if not).", "",
            "| Book | Uncertain |", "|---|---:|"]
    out += [f"| {book_name(b)} | {len(groups[b])} |" for b in order]
    out += [f"| **Total** | **{total}** |", ""]
    for b in order:
        out += [f"### {book_name(b)} ({len(groups[b])})", ""]
        for verse_id, d in groups[b]:
            alts = "; ".join(short(a, 120) for a in d.get("alternatives") or []) or "none given"
            out += [f"- [ ] [{label(verse_id, books)}]({link(lang, verse_id)}) "
                    f"{'/'.join(d.get('levels') or []) or '-'} · {d['category']} · {short(d['choice'], 200)}",
                    f"  - Alternatives: {alts}",
                    f"  - Why: {short(d['reason'])}",
                    f"  - **Question:** {question(d)}"]
        out.append("")

    # 2. Passages.
    keyed = [([ref_key(v) for v in r["refs"]], r) for _, r in data]
    out += ["## 2. Passages to read first", "",
            f"{len(PASSAGES)} passages, in the order to read them: first the passages readers know best, "
            "where the wording matters most and where memory of the older Bibles pulls hardest; then the "
            "passages the drafting found hardest. Read each at all three levels, with the English and the "
            "meaning decisions beside it (the verse inspector, or the reader's Study view). The counts are "
            f"the passage's records, its {lang_name} rendering decisions and the uncertain ones among them.",
            "", "| # | Passage | Why | Records | Decisions | Uncertain |", "|---:|---|---|---:|---:|---:|"]
    for n, (kind, first, last, why) in enumerate(PASSAGES, 1):
        start, stop = ref_key(first), ref_key(last)
        recs = [r for keys, r in keyed if any(start <= k <= stop for k in keys)]
        decs = [d for r in recs for d in r["decisions"] if d.get("language") == lang]
        unc = [d for d in decs if d.get("uncertain")]
        tag = "" if kind == "known" else " *(hard)*"
        out.append(f"| {n} | [{label(first, books, last)}]({link(lang, first)}) | {why}{tag} | "
                   f"{len(recs)} | {len(decs)} | {len(unc)} |")
    out.append("")

    # 3. New name forms.
    verses, spellings = name_index(data, lang)
    single, variant, unquoted, unsure = [], [], [], []
    seen = set()
    for _, record in data:
        for d in record["decisions"]:
            if d.get("language") != lang:
                continue
            forms, flagged, doubt = new_forms(d)
            if not (flagged or doubt):
                continue
            verse_id = record["refs"][0]
            if not forms:
                unquoted.append((verse_id, d))
                continue
            for form in forms:
                if form in seen:
                    continue
                seen.add(form)
                key = form.split()[-1] if " " in form else form
                others = sorted((s for s in spellings.get(same_sound(key), ()) if s != key),
                                key=lambda s: -spellings[same_sound(key)][s])
                item = (verse_id, form, len(verses.get(key, ())), others, d)
                if doubt and not flagged:
                    unsure.append(item)
                elif others:
                    variant.append(item)
                else:
                    single.append(item)

    def name_line(verse_id, form, uses, others, d):
        where = f"used in {uses} verse{'s' if uses != 1 else ''}" if uses else "not found as a word in the text"
        extra = ("; also written " + ", ".join(f"«{o}» ({spellings[same_sound(o)][o]}×)" for o in others[:4])
                 if others else "")
        return (f"- [ ] «{form}» — [{label(verse_id, books)}]({link(lang, verse_id)}), {where}{extra}. "
                f"{short(d['choice'], 140)}")

    out += ["## 3. New name forms to confirm", "",
            "Names the drafters had no earlier book to copy from, so they made a new Amharic form, mostly "
            "from the Hebrew. Confirm the spelling, or give the form Amharic readers know. Counts are the "
            "verses whose text uses the form as a word (with or without a case prefix or suffix); "
            "\"also written\" lists spellings that differ only in letters that sound alike "
            "(ሀ ሐ ኀ ሃ, ሰ ሠ, አ ዐ ኣ ዓ, ጸ ፀ), which may be the same name spelled two ways, "
            "or a different name or an ordinary word.", "",
            f"### Coined forms with one spelling ({len(single)})", ""]
    out += [name_line(*item) for item in single] + [""]
    out += [f"### Coined forms also written another way ({len(variant)})", "",
            "Check whether the other spelling is the same name (it may be an ordinary word, "
            "such as አያት, grandfather); if it is, choose one spelling.", ""]
    out += [name_line(*item) for item in variant] + [""]
    out += [f"### Decisions that call names new without quoting them ({len(unquoted)})", "",
            "Read the verse: the decision says some names in it are new forms but does not list them.", ""]
    out += [f"- [ ] [{label(v, books)}]({link(lang, v)}) {short(d['choice'], 200)}" for v, d in unquoted] + [""]
    out += [f"### Traditional forms the drafters were unsure of ({len(unsure)})", "",
            "Not coined: the drafters meant the form of the Ethiopian Bible tradition but were not sure "
            "they had it right.", ""]
    out += [name_line(*item) for item in unsure] + [""]

    # 4. Older Bibles.
    close = defaultdict(list)
    for book, record in data:
        for d in record["decisions"]:
            if d.get("language") == lang:
                found = older(d)
                if found:
                    close[book].append((record["refs"][0], d, found))
    n_close = sum(len(v) for v in close.values())
    title = "Possible closeness to older Amharic Bibles" if lang == "am" else "Possible closeness to older Bibles"
    out += [f"## 4. {title}", "",
            f"{n_close} decisions mention an older {lang_name} Bible (the 1954 E.C. / 1962 Bible and its "
            "revisions), familiar wording, or wording changed to avoid it. Open the passage beside the "
            "older Bible: the drafts must be their own wording, with nothing longer than a short fixed "
            "phrase in common, and a form the drafters kept because readers know it (a name, a term) "
            "should be one that is free to use. Lines from the terms notes come first.", "",
            "### From the terms notes", ""]
    out += [f"- {path}:{n}: {short(text, 300)}" for path, n, text in terms_notes(lang_name)] + [""]
    for b in sorted(close, key=refs.BOOK_CODES.index):
        out += [f"### {book_name(b)} ({len(close[b])})", ""]
        for verse_id, d, found in close[b]:
            out.append(f"- [ ] [{label(verse_id, books)}]({link(lang, verse_id)}) "
                       f"{'/'.join(d.get('levels') or []) or '-'} · {short(d['choice'], 160)} — "
                       + " ".join(short(s, 220) for s in found[:2]))
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("lang", choices=["am"], help="only Amharic so far: the questions and the "
                        "older-Bible patterns are written for it")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    text = render(args.lang)
    if args.write:
        path = os.path.join(ROOT, "docs", "review-notes", f"{args.lang}-review-priorities.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(path)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
