"""Two content checks that report and never fail: footnotes whose verse says
something else, and verses or glossary rows that break a language's terms
glossary.

Note/verse mismatches (note_mismatches). A footnoted meaning decision states
a choice and its alternatives, and data/notes/<lang>/<BOOK>.json restates
them in each language. The reader sees the footnote beside the verse, so a
verse that words the alternative, or words neither, contradicts it. Only
decisions about what a word or phrase means are looked at (CATEGORIES: not
text variants, grammar, punctuation or allusions, whose alternatives are
about form), and only notes that are current (a stale or missing note shows
the English, which is checked under "en"). Two signals, kept narrow:

- "alternative": at some level the verse has every word that sets one
  alternative apart from the choice and none of the words that set the
  choice apart from it, while the English at that level words the choice
  ("contrast": "english") or another level of this language does ("level").
  The choice is compared by its key phrase, the part before the first colon
  ("crocus: a wild flower ..." -> "crocus"); an alternative by its quoted
  words when it quotes, without asides; both short (ALT_WORDS content
  words). "english_too" says the English at that level words the
  alternative as well, so the mismatch began there.
- "choice_missing": a word_sense or culture decision with a short key phrase
  that the English has at two levels or more, where this language has
  none of the translated key phrase's words at those levels, or not its
  rarest word when that word is rare in the language (ISA 35:1, "bunga
  kunyit" against "bunga bakung"). Not for Hangul, Japanese or Ethiopic,
  whose inflected last syllables the loose match can't follow.

Words are compared loosely, so endings and affixes still match (Indonesian
membalaskan / membalaskannya, Kubalaskan / dibalaskan): a word matches when
the verse holds three quarters of it in one piece (_matches). A language's most frequent
words in its own verses are left out as function words.

Glossary conflicts (glossary_rows, glossary_conflicts, glossary_hits). The
terms glossaries (docs/<language>-terms.md, e.g. docs/indonesian-terms.md)
are Markdown tables: an English source term, the language's form (italic
words, marked (L), (B) or (R) when for one level) and notes; the "Added
while drafting" table adds a Book column. The checks read what that format
says:

- "avoided": a verse uses a form a row rules out ("Not *jemaah*", "never
  *kusta*", "(not *riba*)") where the English verse at that level has the
  row's English term. A row of "Added while drafting" counts in its book
  only, since it often tells two books' uses apart.
- "alternative": the same for a form a row names as an alternative
  ("alternative *perunggu*", "a footnote gives *Penolong*"), when the verse
  has none of the row's own forms.
- glossary_conflicts: two rows for the same English term (articles,
  plurals and asides ignored) whose forms share no word, or one row using
  a form another row for that term rules out. Rows naming different source
  words in their asides (*pechah*, *hegemon*) are kept apart.

scripts/content_checks.py prints both lists; the admin shows them
(backend/staff/checks.py).
"""
import functools
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

from owb import markup, notes, refs

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEVELS = ("L", "B", "R")

FUNCTION_WORDS = 150   # a language's most frequent verse words, left out
CHOICE_WORDS = 2       # content words a key phrase may have for choice_missing
ALT_WORDS = 4          # content words a choice or alternative may have to be compared
# Meaning decisions about what a word or phrase means. Text variants,
# grammar, punctuation and allusions are about form, which word overlap
# cannot tell apart.
CATEGORIES = frozenset({"word_sense", "idiom", "theology", "culture"})
# choice_missing only looks at decisions about what a thing or word is.
TERM_CATEGORIES = frozenset({"word_sense", "culture"})
SHARE = 0.75           # of a word that must appear in the verse to match
RARE = 25              # verse texts a word may be in and still be rare
LOOSE = 0.6            # the same, for choice_missing (a missing word must be clearly missing)

# A letter, or a combining mark (Devanagari vowel signs, accents), which \w
# leaves out.
_LETTER = r"(?:[^\W\d_]|[\u0300-\u036f\u0900-\u097f])"
_WORD = re.compile(rf"{_LETTER}+(?:-{_LETTER}+)*")
_QUOTED = re.compile(r"[\"“”«»„‘’「」『』]([^\"“”«»„「」『』]{2,}?)[\"“”«»„’「」『』]")
_ASIDE = re.compile(r"\([^()]*\)|\[[^\[\]]*\]|（[^（）]*）")
_KANA = re.compile("[぀-ヿ]")
_HAN_RUN = re.compile(r"[\u3400-\u9fff\u30a0-\u30ff\uf900-\ufaff]+")


# ------------------------------------------------------------------ words

def _script(word):
    """The minimum length a word of this script needs to be a content word."""
    ch = word[0]
    if "\u1100" <= ch <= "\u11ff" or "\uac00" <= ch <= "\ud7af":
        return 2      # Hangul: one syllable per character
    if "\u1200" <= ch <= "\u139f":
        return 2      # Ethiopic
    if "\u0900" <= ch <= "\u097f":
        return 3      # Devanagari
    if "\u3040" <= ch <= "\u30ff" or "\u3400" <= ch <= "\u9fff":
        return 1      # Japanese: runs of kanji and katakana
    return 4


def fold(text):
    """Lower case, composed. Accents are kept: they tell Vietnamese words
    apart."""
    text = text.lower()
    return text if text.isascii() else unicodedata.normalize("NFC", text)


@functools.lru_cache(maxsize=1 << 18)
def flatten(text, every_option=False):
    """A rendering as plain lower-case text: settings at their defaults (or
    every option, joined), no markers."""
    if every_option:
        text = markup.SPAN.sub(lambda m: " " + " / ".join(m[2].split("|")) + " ", text)
    else:
        text = markup.render(text)
    text = markup.flat(text)
    text = re.sub(r"\\[a-z]+\d*\*?", " ", text)
    text = fold(text)
    return " ".join(text.split())


def words(text):
    """The words of plain text. Japanese, which has no spaces, gives its runs
    of kanji and katakana (kana inflections and particles left out)."""
    if _KANA.search(text):
        return _HAN_RUN.findall(text)
    return _WORD.findall(text)


def content_words(text, stop):
    seen = []
    for w in words(text):
        if w in stop or len(w) < _script(w) or w in seen:
            continue
        seen.append(w)
    return seen


@functools.lru_cache(maxsize=1 << 16)
def _pieces(word, share=SHARE):
    n = len(word)
    k = max(_script(word), math.ceil(share * n))
    if k >= n:
        return [word]
    return [word[i:i + k] for i in range(n - k + 1)]


def _matches(word, text, share=SHARE):
    """Whether text (plain, lower case) holds the word or a long enough piece
    of it (share of its letters)."""
    return any(p in text for p in _pieces(word, share))


class Vocabulary(frozenset):
    """A language's function words (the set), with .counts: in how many
    verse texts each word appears."""
    counts = Counter()


def function_words(texts, n=FUNCTION_WORDS):
    """The n most frequent words of a language's verses (each in at least
    one text in a hundred), as a Vocabulary."""
    counts, total = Counter(), 0
    for t in texts:
        counts.update(set(words(t)))
        total += 1
    # A function word is in many texts, not only among the commonest of a
    # few (as in a test's handful of sentences).
    least = max(3, total // 100)
    out = Vocabulary(w for w, c in counts.most_common(n) if c >= least)
    out.counts = counts
    return out


def language_function_words(records, lang):
    """function_words of lang's renderings in records, every level."""
    return function_words(flatten(t) for r in records for lv, t in (r.get("renderings", {}).get(lang) or {}).items()
                          if lv in LEVELS)


# ------------------------------------------------------- note mismatches

def key_phrase(choice):
    """The words a choice is compared by: before the first colon, no asides."""
    head = _ASIDE.sub(" ", choice).replace("：", ":").split(":", 1)[0]
    return " ".join(fold(head).split())


def alt_phrase(alt):
    """An alternative's own words: what it quotes, else the text without its
    asides (and without a "Greek: ..." label before a colon)."""
    quoted = _QUOTED.findall(alt)
    if quoted:
        return " ".join(fold(q) for q in quoted)
    text = _ASIDE.sub(" ", alt)
    text = text.replace("：", ":")
    if ":" in text:
        head, tail = text.split(":", 1)
        text = tail if len(head.split()) <= 4 else head
    return " ".join(fold(text).split())


def _distinct(phrase, other, stop):
    return [w for w in content_words(phrase, stop) if not _matches(w, other)]


def _snippet(text, limit=240):
    return text if len(text) <= limit else text[:limit - 1].rstrip() + "…"


def note_mismatches(records, lang, translated=None, stop=None, en_stop=None):
    """[hit] for one language. records: dicts with id, refs, renderings and
    decisions as content/ stores them (renderings need lang, and en when
    lang isn't English). translated: {record id: {decision id: note}} from
    data/notes/<lang>/ (None for English, whose notes are the decisions).
    stop, en_stop: the language's and English's function words, worked out
    from the records when not given."""
    records = list(records)
    if stop is None:
        stop = language_function_words(records, lang)
    if en_stop is None:
        en_stop = stop if lang == "en" else language_function_words(records, "en")
    hits = []
    for r in records:
        mine = r.get("renderings", {}).get(lang) or {}
        if not mine:
            continue
        for d in r.get("decisions", []):
            if d.get("layer") != "meaning" or not d.get("footnote") or d.get("category") not in CATEGORIES:
                continue
            if lang == "en":
                note = d
            else:
                note = (translated or {}).get(r["id"], {}).get(d["id"])
                if not note or note.get("source") != notes.decision_digest(d):
                    continue
            hits += _decision_hits(r, d, note, lang, stop, en_stop)
    return hits


class _Sides:
    """A choice and one alternative as words: those each has that the other
    lacks."""

    def __init__(self, choice, alt, stop):
        self.choice = _distinct(choice, alt, stop)
        self.alt = _distinct(alt, choice, stop)
        self.usable = (bool(self.choice) and bool(self.alt) and len(content_words(alt, stop)) <= ALT_WORDS
                       and len(content_words(choice, stop)) <= ALT_WORDS)

    def words_alt(self, text):
        return all(_matches(w, text) for w in self.alt) and not any(_matches(w, text) for w in self.choice)

    def words_choice(self, text):
        return any(_matches(w, text) for w in self.choice) and not any(_matches(w, text) for w in self.alt)


def _decision_hits(r, d, note, lang, stop, en_stop):
    mine = {lv: flatten(t) for lv, t in (r["renderings"].get(lang) or {}).items() if lv in LEVELS}
    english = {lv: flatten(t) for lv, t in (r["renderings"].get("en") or {}).items() if lv in LEVELS}
    choice, en_choice = key_phrase(note["choice"]), key_phrase(d["choice"])
    alts = [alt_phrase(a) for a in note.get("alternatives") or []]
    en_alts = [alt_phrase(a) for a in d.get("alternatives") or []]
    out = []

    def hit(level, kind, words, alternative="", levels=None):
        return {"record": r["id"], "verse": r["refs"][0], "language": lang, "level": level,
                "levels": levels or [level], "decision": d["id"], "category": d.get("category", ""),
                "kind": kind, "choice": note["choice"], "alternative": alternative, "words": words,
                "text": _snippet(mine[level])}

    for i, alt in enumerate(alts):
        sides = _Sides(choice, alt, stop)
        if not sides.usable:
            continue
        en_sides = _Sides(en_choice, en_alts[i], en_stop) if i < len(en_alts) else None
        for level, text in mine.items():
            if not sides.words_alt(text):
                continue
            # The contrast that makes it a mismatch, not a paraphrase: the
            # English at this level words the choice, or another level of
            # this language does.
            en_ok = en_sides is not None and en_sides.usable
            english_choice = lang != "en" and en_ok and en_sides.words_choice(english.get(level, ""))
            other_level = any(sides.words_choice(t) for lv, t in mine.items() if lv != level)
            if not (english_choice or other_level):
                continue
            # The English at this level words the alternative too: the
            # mismatch began there (and shows under English as well).
            english_too = lang != "en" and en_ok and en_sides.words_alt(english.get(level, ""))
            same = next((h for h in out if h["alternative"] == note["alternatives"][i]), None)
            if same:
                # One hit for the alternative, with every level that words it.
                same["levels"].append(level)
                same["english_too"] = same["english_too"] and english_too
                if english_choice:
                    same["contrast"] = "english"
                continue
            found = hit(level, "alternative", sides.alt, note["alternatives"][i])
            found["english_too"] = english_too
            found["contrast"] = "english" if english_choice else "level"
            out.append(found)
    if out or lang == "en" or d.get("category") not in TERM_CATEGORIES:
        return out
    # choice_missing: a short key phrase the English has at two levels or
    # more, and this language has at none of them: none of its words, or
    # not its rarest word when that is a rare one (crocus, "bunga kunyit").
    key = content_words(choice, stop)
    en_key = content_words(en_choice, en_stop)
    if not key or len(key) > CHOICE_WORDS or not en_key or len(en_key) > CHOICE_WORDS:
        return out
    # Hangul, Japanese and Ethiopic words change their last syllable as they
    # inflect, which the loose match can't follow: alternatives only there.
    if any(_script(w) <= 2 for w in key):
        return out
    shown = [lv for lv in LEVELS if lv in mine and all(_matches(w, english.get(lv, "")) for w in en_key)]
    if len(shown) < 2:
        return out
    parts = key + [p for w in key if "-" in w for p in w.split("-") if len(p) >= _script(p) and p not in stop]
    if not any(_matches(w, mine[lv], LOOSE) for lv in shown for w in parts):
        missing = key
    else:
        counts = getattr(stop, "counts", None) or {}
        rarest = min(key, key=lambda w: (counts.get(w, 0), -len(w)))
        if len(key) < 2 or counts.get(rarest, 0) > RARE or any(_matches(rarest, mine[lv], LOOSE) for lv in shown):
            return out
        missing = [rarest]
    found = hit(shown[0], "choice_missing", missing, levels=shown)
    found["english_too"] = False
    found["contrast"] = "english"
    out.append(found)
    return out


# -------------------------------------------------------------- glossary

def glossary_path(name):
    """docs/<english name>-terms.md for a language name ("Indonesian")."""
    return DOCS / f"{name.lower()}-terms.md"


_BOOK_NAMES = {name.lower(): code for code, name in refs.BOOK_NAMES.items()}
_LEVEL_MARK = re.compile(r"\(([^()]*)\)")
_ITALIC = re.compile(r"\*([^*]+)\*")
_RULED_OUT = re.compile(r"\b(?:not|never)\b[^*|;.]{0,12}((?:\*[^*]+\*(?:\s*(?:,|or|nor|and)\s*)?)+)", re.I)
_ALTERNATIVE = re.compile(r"\b(?:alternatives?|a footnote gives|footnote:)\s*((?:\*[^*]+\*(?:\s*(?:,|or|and)\s*)?)+)",
                          re.I)
_ARTICLE = re.compile(r"^(?:the|a|an)\s+")


def _cells(line):
    line = line.strip()
    if not (line.startswith("|") and line.endswith("|")):
        return None
    # Split on pipes not escaped (\|, used inside {{divine_name:...\|...}}).
    parts = re.split(r"(?<!\\)\|", line[1:-1])
    return [p.strip().replace("\\|", "|") for p in parts]


def _forms_in(text):
    return [" ".join(f.lower().split()) for f in _ITALIC.findall(text)]


def _levels(text):
    """The levels a form is marked for in the text right after it."""
    m = _LEVEL_MARK.match(text.strip())
    if not m:
        return None
    marks = [x.strip() for x in re.split(r"[,;]", m.group(1))]
    lv = [x for x in marks if x in LEVELS]
    return lv or None


def _row_forms(cell):
    """[(form, levels or None)] of a language cell, without the forms it
    rules out or names as alternatives."""
    cell = _RULED_OUT.sub(" ", cell)
    cell = _ALTERNATIVE.sub(" ", cell)
    forms = []
    for m in _ITALIC.finditer(cell):
        form = " ".join(m.group(1).lower().split())
        forms.append((form, _levels(cell[m.end():])))
    if not forms:
        # Names are written without italics: "Ainon"; "Lembah Kidron; sungai Kidron (L)".
        for part in re.split(r"[;,]", cell):
            lv = _levels(part[part.find("("):]) if "(" in part else None
            form = " ".join(_ASIDE.sub(" ", markup.render(part)).lower().split())
            if form:
                forms.append((form, lv))
    return forms


def _english_terms(cell):
    """The English terms of a source cell, lower case, without asides or
    leading articles: "congregation (*edah*); assembly (*qahal*)" ->
    ["congregation", "assembly"]."""
    out = []
    for part in re.split(r"[;,]", _ASIDE.sub(" ", cell)):
        part = _ITALIC.sub(" ", part)
        part = re.sub(r"[\"“”]", " ", part)
        part = _ARTICLE.sub("", " ".join(part.lower().split()))
        if part and re.search(r"[a-z]", part):
            out.append(part)
    return out


def _source_words(cell):
    return sorted({w.lower() for a in re.findall(r"\(([^()]*)\)", cell) for w in _ITALIC.findall(a)})


def _singular(term):
    """A term with its words' plural -s taken off (governors -> governor),
    not from -ss, -us, -is (Silvanus, jealous)."""
    return " ".join(w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")) else w
                    for w in term.split())


def _entry(number, section, book, source, cell, extra):
    return {
        "line": number, "section": section, "book": book, "source": source, "cell": cell,
        "english": _english_terms(source),
        "capital": source.lstrip("*_ ")[:1].isupper(),
        "sources": _source_words(source),
        "forms": _row_forms(cell),
        "avoided": [f for m in _RULED_OUT.finditer(cell + " " + extra) for f in _forms_in(m.group(1))],
        "alternatives": [f for m in _ALTERNATIVE.finditer(cell + " " + extra) for f in _forms_in(m.group(1))],
    }


def _split_parts(cell):
    """A cell's ";"-separated parts, not splitting inside parentheses or
    {{...}} spans."""
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(cell):
        if ch in "({":
            depth += 1
        elif ch in ")}":
            depth = max(0, depth - 1)
        elif ch == ";" and depth == 0:
            parts.append(cell[start:i].strip())
            start = i + 1
    parts.append(cell[start:].strip())
    return [p for p in parts if p]


def glossary_rows(text, name):
    """The entries of a terms glossary: each pair of an English column and a
    column for the language (headed name, e.g. "Indonesian"; the people and
    places tables have two pairs a line), split into its "x; y" parts when
    the English and the language have as many. Each entry: {line, section,
    book (for "Added while drafting"), source, cell, english: [terms],
    sources (transliterated words in the English's asides), forms:
    [(form, levels or None)], avoided, alternatives}."""
    rows, section, header = [], "", None
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            section = line.lstrip("#").strip()
            header = None
            continue
        cells = _cells(line)
        if cells is None:
            header = None
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        targets = [i for i, h in enumerate(header) if h == name.lower()]
        book_col = header.index("book") if "book" in header else None
        notes_col = header.index("notes") if "notes" in header else None
        book = _BOOK_NAMES.get(cells[book_col].lower()) if book_col is not None and book_col < len(cells) else None
        extra = cells[notes_col] if notes_col is not None and notes_col < len(cells) else ""
        for target in targets:
            if target >= len(cells) or not cells[target]:
                continue
            source_col = next((i for i in range(target - 1, -1, -1)
                               if i not in (book_col, notes_col) and i not in targets), None)
            if source_col is None or not cells[source_col]:
                continue
            source, cell = cells[source_col], cells[target]
            src_parts, cell_parts = _split_parts(source), _split_parts(cell)
            if len(src_parts) > 1 and len(src_parts) == len(cell_parts):
                for s, c in zip(src_parts, cell_parts):
                    rows.append(_entry(number, section, book, s, c, extra))
            else:
                rows.append(_entry(number, section, book, source, cell, extra))
    return rows


def _form_words(entry):
    """The words of an entry's forms and of the rest of its cell (names are
    not in italics), four letters or more, hyphenated words in parts too."""
    cell = _ALTERNATIVE.sub(" ", _RULED_OUT.sub(" ", entry["cell"]))
    text = flatten(cell + " " + " ".join(f for f, _ in entry["forms"]), every_option=True)
    out = set()
    for w in words(text):
        out |= {p for p in [w, *w.split("-")] if len(p) >= 4}
    return out


def _row_json(row):
    return {"line": row["line"], "section": row["section"], "book": row["book"],
            "source": row["source"], "forms": row["cell"]}


def _uses_ruled_out(rule, row):
    """The forms rule rules out that row gives as its own."""
    return [f for f in rule["avoided"] if any(_form_in(f, flatten(own)) for own, _ in row["forms"])]


def _form_capital(entry):
    """Whether an entry's language form starts with a capital (a name)."""
    return re.sub(r"[\W\d_]", "", markup.render(entry["cell"]))[:1].isupper()


def glossary_conflicts(rows):
    """[conflict]: pairs of entries for one English term whose forms share
    no word ("different_forms"), or where one uses a form the other rules
    out ("ruled_out"). Entries naming different source words in their
    asides (*pechah*, *hegemon*) are told apart, and so are a name and a
    common noun (Lot the man, lots cast)."""
    by_term = {}
    for row in rows:
        for term in row["english"]:
            by_term.setdefault(_singular(term), []).append(row)
    out = []
    for term, group in sorted(by_term.items()):
        involved, ruled, kinds = [], set(), set()
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                if (a["line"], a["source"]) == (b["line"], b["source"]):
                    continue
                if a["sources"] and b["sources"] and not set(a["sources"]) & set(b["sources"]):
                    continue
                if a["capital"] != b["capital"] and _form_capital(a) != _form_capital(b):
                    continue
                these = _uses_ruled_out(b, a) + _uses_ruled_out(a, b)
                if these:
                    kinds.add("ruled_out")
                    ruled |= set(these)
                elif len(a["english"]) == 1 and len(b["english"]) == 1:
                    wa, wb = _form_words(a), _form_words(b)
                    if not wa or not wb or wa & wb:
                        continue
                    kinds.add("different_forms")
                else:
                    continue
                involved += [x for x in (a, b) if x not in involved]
        if involved:
            involved.sort(key=lambda x: x["line"])
            out.append({"term": term, "kind": "ruled_out" if "ruled_out" in kinds else "different_forms",
                        "forms": sorted(ruled), "rows": [_row_json(x) for x in involved]})
    return out


@functools.lru_cache(maxsize=None)
def _phrase_pattern(term):
    stems = [_singular(w) for w in term.split()]
    pattern = r"(?<![\w-])" + r"\s+".join(re.escape(p) + r"\w{0,3}" for p in stems) + r"(?![\w-])"
    return stems[0], re.compile(pattern)


def _phrase_in(term, text):
    """Whether an English term appears in English text as whole words, a
    plural or -ed/-ing ending allowed."""
    first, pattern = _phrase_pattern(term)
    return first in text and pattern.search(text) is not None


def _form_in(form, text):
    """A glossary form in a verse: as whole words, a short ending allowed
    (Indonesian -nya, -lah, Russian case endings)."""
    form, pattern = _form_pattern(form)
    return bool(form) and form in text and pattern.search(text) is not None


@functools.lru_cache(maxsize=None)
def _form_pattern(form):
    form = flatten(form)
    return form, re.compile(r"(?<![\w-])" + re.escape(form) + r"[\w-]{0,4}(?![\w])")


def glossary_hits(rows, records, lang):
    """[hit]: verses in lang using a form the glossary rules out ("avoided")
    or names only as an alternative ("alternative") where the English verse
    at that level has the row's English term."""
    rules = [row for row in rows if (row["avoided"] or row["alternatives"]) and row["english"]]
    # A book's own "Added while drafting" entry may give the form the
    # general one rules out (Joshua's *jemaah*): the hit says so.
    book_rows = {}
    for row in rows:
        if row["book"]:
            for term in row["english"]:
                book_rows.setdefault((row["book"], _singular(term)), []).append(row)
    hits = []
    for r in records:
        mine = r.get("renderings", {}).get(lang) or {}
        english = r.get("renderings", {}).get("en") or {}
        book = r["id"].split(".")[0]
        mine_hits = {}
        for level, raw in sorted(mine.items(), key=lambda kv: LEVELS.index(kv[0]) if kv[0] in LEVELS else 9):
            if level not in LEVELS:
                continue
            text = None
            en_text = flatten(english.get(level) or " ".join(english.values()), every_option=True)
            for row in rules:
                if row["book"] and row["book"] != book:
                    continue
                term = next((t for t in row["english"] if _phrase_in(t, en_text)), None)
                if term is None:
                    continue
                if text is None:
                    text = flatten(raw, every_option=True)
                bad = [(f, "avoided") for f in row["avoided"] if _form_in(f, text)]
                if not bad and row["alternatives"]:
                    own = [f for f, lv in row["forms"] if not lv or level in lv]
                    if not any(_form_in(f, text) for f in own):
                        bad = [(f, "alternative") for f in row["alternatives"] if _form_in(f, text)]
                for form, kind in bad[:1]:
                    key = (r["id"], row["line"], row["source"], form)
                    if key in mine_hits:
                        mine_hits[key]["levels"].append(level)
                        continue
                    allowed = next((x["line"] for x in book_rows.get((book, _singular(term)), [])
                                    if x is not row and any(_form_in(form, flatten(f)) for f, _ in x["forms"])), None)
                    mine_hits[key] = {"record": r["id"], "verse": r["refs"][0], "language": lang, "level": level,
                                      "levels": [level], "kind": kind, "form": form, "term": term,
                                      "row": _row_json(row), "allowed_by": allowed, "text": _snippet(text)}
        hits += mine_hits.values()
    return hits


# ----------------------------------------------------------------- files

def load_records(books=None, langs=None):
    """Every record of content/ (or of books), slimmed to what the checks
    read: id, refs, the renderings in langs (and English) and the footnoted
    meaning decisions."""
    keep = None if langs is None else set(langs) | {"en"}
    out = []
    for book in books or notes.books():
        for path in sorted((notes.CONTENT / book).glob("*.json")):
            for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
                out.append({
                    "id": r["id"], "refs": r["refs"],
                    "renderings": {k: v for k, v in r.get("renderings", {}).items() if keep is None or k in keep},
                    "decisions": [d for d in r.get("decisions", []) if d.get("layer") == "meaning"
                                  and d.get("footnote")],
                })
    return out


def load_notes(lang, books=None):
    """{record id: {decision id: note}} of data/notes/<lang>/."""
    out = {}
    folder = notes.NOTES / lang
    if not folder.is_dir():
        return out
    for path in sorted(folder.glob("*.json")):
        if books and path.stem not in books:
            continue
        out.update(json.loads(path.read_text(encoding="utf-8")).get("notes", {}))
    return out


def load_glossary(name):
    """The rows of docs/<name>-terms.md, or [] when the language has none."""
    path = glossary_path(name)
    if not path.is_file():
        return []
    return glossary_rows(path.read_text(encoding="utf-8"), name)
