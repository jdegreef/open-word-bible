"""New Testament textual evidence, for checking what notes say about it.

Two pinned sources:

- The SBLGNT apparatus (`sblgnt`, data/sblgntapp/text, CC BY 4.0). Every
  place where the SBLGNT differs from Westcott and Hort (WH), Tregelles
  (Treg), the Greek text behind the NIV (NIV), the Robinson-Pierpont
  Byzantine text (RP) or NA28, with the reading of each. The SBLGNT text
  marks each such place (⸀, ⸁, ⸂…⸃, ⸄…⸅), in the order of the notes.
- The CNTR transcriptions (`cntr-transcriptions`, CC BY-SA 4.0): the early
  manuscripts of its "class 1" (the papyri and the great codices up to about
  the fifth century: Sinaiticus 01, Alexandrinus 02, Vaticanus 03, Ephraemi
  04, Bezae 05, Washingtonianus 032, ...) and the Greek text behind the King
  James Version (KJTR). They are read only to check notes; nothing derived
  from them is written to content/ or data/.

`compare(verse, positions, witness)` says whether a witness has the SBLGNT
words at the given word positions of a verse, and `check_note` reads the
claims a note makes about witnesses ("many later manuscripts add ...", "Codex
Vaticanus lacks ...", "the King James Version follows ...") and compares
each with the data.
"""
import difflib
import re
import unicodedata
from functools import lru_cache
from typing import NamedTuple

from owb import refs
from owb.sources import read_text, source_dir
from owb.sources import sblgnt

APP_DIR = "data/sblgntapp/text"
CNTR = "cntr-transcriptions"
EDITIONS = ("WH", "Treg", "NIV", "RP", "NA28")
EDITION_NAMES = {
    "WH": "Westcott and Hort", "Treg": "Tregelles", "NIV": "the NIV's Greek text",
    "RP": "the Robinson-Pierpont Byzantine text", "NA28": "NA28",
    "KJTR": "the Greek text behind the King James Version",
}
# Early manuscripts named in notes: siglum -> (file in "class 1", English name).
MANUSCRIPTS = {
    "01": "Codex Sinaiticus", "02": "Codex Alexandrinus", "03": "Codex Vaticanus",
    "04": "Codex Ephraemi", "05": "Codex Bezae", "032": "Codex Washingtonianus",
}
_NAME_TO_CODE = {name: code for code, _, name in refs.BOOKS}
_NT_NUMBER = {code: 40 + i for i, (code, _) in enumerate(refs.NT_BOOKS)}
_NUMBER_NT = {n: c for c, n in _NT_NUMBER.items()}


# --- Greek word keys -----------------------------------------------------

_DOUBLE = re.compile(r"([λνσρτκμπ])\1")


def key(word):
    """A comparison key for a Greek word: no accents, breathings, case or
    punctuation, final sigma as σ, and the commonest spelling variations of
    the manuscripts folded (ει/ι, αι/ε, doubled consonants, movable ν).
    η, υ, ω and οι are kept, so ἡμῶν/ὑμῶν and ἔχωμεν/ἔχομεν stay apart."""
    w = unicodedata.normalize("NFD", word.lower())
    w = "".join(ch for ch in w if not unicodedata.combining(ch))
    w = w.replace("ς", "σ").replace("ϗ", "και")
    w = "".join(ch for ch in w if "α" <= ch <= "ω")
    w = w.replace("ει", "ι").replace("αι", "ε")
    w = _DOUBLE.sub(r"\1", w)
    if len(w) > 3 and w.endswith(("σιν", "εν", "ιν")):
        w = w[:-1]
    return _ELIDED.get(w, w)


# Words written in full or elided (ἀλλά, ἀλλʼ; κατά, κατʼ, καθʼ), as folded.
_ELIDED = {"αλα": "αλ", "δια": "δι", "κατα": "κατ", "καθ": "κατ", "μετα": "μετ", "μεθ": "μετ",
           "παρα": "παρ", "απο": "απ", "αφ": "απ", "επι": "επ", "εφ": "επ", "υπο": "υπ", "υφ": "υπ",
           "αντι": "αντ", "ανθ": "αντ", "ουδε": "ουδ", "μηδε": "μηδ", "δε": "δ", "τε": "τ"}


def greek_words(text):
    """The Greek words of a reading, without punctuation or sigla."""
    return [w for w in (key(t) for t in text.split()) if w]


# --- The SBLGNT apparatus ----------------------------------------------

class Reading(NamedTuple):
    text: str          # as the apparatus prints it ("+ καὶ", "–", ...)
    words: tuple       # keys of the full reading (with the lemma for "+")
    witnesses: tuple   # edition sigla
    kind: str          # "replace", "add", "omit" or "note" (not plain text)


class Unit(NamedTuple):
    ref: refs.Ref
    start: int         # first SBLGNT word position (1-based) of the lemma
    end: int           # last position (== start - 1 for none)
    lemma: Reading     # the SBLGNT reading and the editions that agree
    others: tuple      # [Reading]

    def editions_with_sblgnt(self):
        """Editions that read as the SBLGNT here (all those not listed with
        another reading)."""
        listed = {w for r in self.others for w in r.witnesses}
        return tuple(e for e in EDITIONS if e not in listed)

    def reading_of(self, edition):
        for r in self.others:
            if edition in r.witnesses:
                return r
        return self.lemma


_SIGLUM = re.compile(r"^[A-Z][A-Za-z0-9]*\.?$")
_HEADING = re.compile(r"^(.+) (\d+):(\d+)$")


def _split_reading(text):
    """'Ἰησοῦ Χριστοῦ WH RP' -> ('Ἰησοῦ Χριστοῦ', ('WH', 'RP'))."""
    parts = text.split()
    sigla = []
    while parts and _SIGLUM.match(parts[-1]):
        sigla.insert(0, parts.pop().rstrip("."))
    return " ".join(parts), tuple(sigla)


def _reading(text, lemma_words):
    body, sigla = _split_reading(text.strip())
    if body in ("–", "-", "—"):
        return Reading(body, (), sigla, "omit")
    if re.search(r"[A-Za-z0-9]", body):
        return Reading(body, (), sigla, "note")
    if "…" in body:     # "σταυρῶσαί σε … ἔχω ἀπολῦσαί": the words around a gap
        return Reading(body, tuple(greek_words(body.replace("…", " "))), sigla, "partial")
    if body.startswith("+"):
        return Reading(body, tuple(lemma_words) + tuple(greek_words(body[1:])), sigla, "add")
    return Reading(body, tuple(greek_words(body)), sigla, "replace")


def _span_positions(verse):
    """[(start, end)] word positions (1-based, inclusive) of each marked
    place of a SBLGNT verse, in text order."""
    starts = [0]
    for i, ch in enumerate(verse.text):
        if ch == " ":
            starts.append(i + 1)

    def position(offset):     # the word that begins at or contains offset
        n = 0
        for i, s in enumerate(starts):
            if s <= offset:
                n = i
        return n + 1

    spans = []
    for mark, begin, end, _text in sblgnt.marked_spans(verse):
        first = position(begin)
        last = position(max(begin, end - 1)) if len(mark) == 2 else first
        spans.append((first, last))
    return sorted(spans)


@lru_cache(maxsize=None)
def units(book):
    """{Ref: [Unit]} for one New Testament book."""
    name = refs.CODE_TO_SBLGNT[book]
    raw = read_text("sblgnt", f"{APP_DIR}/{name}.txt")
    verses = sblgnt.load_book(book)
    notes, ref = {}, None
    for line in raw.splitlines():
        line = line.strip()
        m = _HEADING.match(line)
        if m and m[1] in _NAME_TO_CODE:
            ref = refs.Ref(_NAME_TO_CODE[m[1]], int(m[2]), int(m[3]))
            continue
        if ref is None or "]" not in line:
            continue
        line = re.sub(r"^(?:•|\d+:\d+|\d+)\s+", "", line)
        notes.setdefault(ref, []).append(line)
    out = {}
    for ref, lines in notes.items():
        verse = verses.get(ref)
        spans = _span_positions(verse) if verse else []
        words = verse.text.split() if verse else []
        found = []
        for i, line in enumerate(lines):
            left, right = line.split("]", 1)
            start, end = spans[i] if i < len(spans) else (0, -1)
            lemma_text, lemma_sigla = _split_reading(left.strip())
            lemma_words = [key(w) for w in words[start - 1:end]] if start else greek_words(lemma_text)
            lemma = Reading(lemma_text, tuple(w for w in lemma_words if w), lemma_sigla, "replace")
            others = tuple(_reading(part, lemma.words) for part in right.split(";"))
            found.append(Unit(ref, start, end, lemma, others))
        out[ref] = found
    return out


def units_at(ref, positions):
    """The apparatus units of a verse whose lemma touches the positions
    (an addition after the last word counts)."""
    if not positions:
        return []
    lo, hi = min(positions), max(positions)
    found = []
    for u in units(ref.book).get(ref, []):
        if not u.start:
            continue
        # An addition is printed on the word before the gap it fills.
        end = u.end + 1 if any(r.kind == "add" for r in u.others) else u.end
        if u.start <= hi and end >= lo:
            found.append(u)
    return found


# --- CNTR transcriptions -------------------------------------------------

class WitnessVerse(NamedTuple):
    first: tuple       # (key, certain) for each word, as first written
    corrected: tuple   # (key, certain), after the last correction
    absent: bool       # the verse is marked as not in the manuscript
    gaps: bool         # part of the verse is lost (lacuna)


_GROUP = re.compile(r"([xab]?)\{([^{}]*)\}")


def _hands(body):
    """Split a transcription line into the text as first written and as
    finally corrected. A run of brace groups is one place: x{...} (or the
    first unprefixed {...}) is the first hand, the last group the final."""
    first, final, pos = [], [], 0
    pattern = re.compile(r"(?:[xab]?\{[^{}]*\}\s*)+")
    for m in pattern.finditer(body):
        first.append(body[pos:m.start()])
        final.append(body[pos:m.start()])
        groups = _GROUP.findall(m.group(0))
        orig = next((g for p, g in groups if p == "x"), None)
        if orig is None:
            orig = next((g for p, g in groups if p == ""), groups[0][1])
        first.append(" " + orig + " ")
        final.append(" " + groups[-1][1] + " ")
        pos = m.end()
    first.append(body[pos:])
    final.append(body[pos:])
    return "".join(first), "".join(final)


def _words(text):
    text = re.sub(r"\\\d*", " ", text)            # page breaks
    text = text.replace("/", "").replace("|", "").replace("_", " ")
    out = []
    for tok in text.split():
        certain = "~" not in tok and "^" not in tok and "*" not in tok and "&" not in tok
        nomen = "=" in tok
        letters = tok.replace("¯", "ν")
        k = key(letters)
        if not k:
            continue
        out.append((("=" + k) if nomen else k, certain))
    return tuple(out)


@lru_cache(maxsize=None)
def witness(siglum):
    """{Ref: WitnessVerse} for an early manuscript ("01", "P46", ...) or for
    "KJTR", the Greek text behind the King James Version."""
    if siglum in ("KJTR", "RP"):
        path = f"critical texts/{siglum}.txt"
    else:
        path = f"class 1/{siglum}.txt"
    out = {}
    for line in read_text(CNTR, path).splitlines():
        if len(line) < 9 or not line[:8].isdigit():
            continue
        number, body = int(line[:2]), line[9:].strip()
        if number not in _NUMBER_NT:
            continue
        ref = refs.Ref(_NUMBER_NT[number], int(line[2:5]), int(line[5:8]))
        if body in ("-", "-~"):
            out[ref] = WitnessVerse((), (), True, body == "-~")
            continue
        first, final = _hands(body)
        gaps = any(ch in body for ch in "*&~^")
        out[ref] = WitnessVerse(_words(first), _words(final), False, gaps)
    return out


@lru_cache(maxsize=None)
def early_sigla():
    """Sigla of the pinned early manuscripts, papyri included."""
    folder = source_dir(CNTR) / "class 1"
    if folder.is_dir():
        names = sorted(p.stem for p in folder.glob("*.txt"))
    else:
        names = list(MANUSCRIPTS)
    return tuple(n for n in names if n != "README")


# --- Comparing a witness with the SBLGNT ----------------------------------

class Comparison(NamedTuple):
    status: str        # "agree", "differ", "lacuna" or "absent"
    detail: str = ""   # for "differ": "adds", "lacks" or "has other words"


def sblgnt_words(ref):
    verse = sblgnt.load_book(ref.book).get(ref)
    return [key(w) for w in verse.text.split()] if verse else []


_NOMINA = [key(w) for w in (
    "θεός θεοῦ θεῷ θεόν θεέ κύριος κυρίου κυρίῳ κύριον κύριε Ἰησοῦς Ἰησοῦ Ἰησοῦν "
    "Χριστός Χριστοῦ Χριστῷ Χριστόν πνεῦμα πνεύματος πνεύματι πνεύματα πνευμάτων "
    "πατήρ πατρός πατρί πατέρα πάτερ υἱός υἱοῦ υἱῷ υἱόν υἱέ ἄνθρωπος ἀνθρώπου ἀνθρώπῳ "
    "ἄνθρωπον ἄνθρωποι ἀνθρώπων ἀνθρώποις ἀνθρώπους οὐρανός οὐρανοῦ οὐρανῷ οὐρανόν "
    "οὐρανοί οὐρανῶν οὐρανοῖς οὐρανούς σταυρός σταυροῦ σταυρῷ σταυρόν σταυρώσατε "
    "Ἰσραήλ Ἰερουσαλήμ Δαυίδ μήτηρ μητρός μητρί μητέρα σωτήρ σωτῆρος σωτῆρι").split()]


def _is_nomen(short, full):
    """Could the contraction stand for the word: same first and last
    letter, and its letters in order?"""
    if not short or not full or short[0] != full[0] or short[-1] != full[-1]:
        return False
    it = iter(full)
    return all(ch in it for ch in short)


def _resolve(sbl, wit, extra=()):
    """Expand nomina sacra (=κυ) to the word they stand for: a word of the
    SBLGNT verse or of the readings compared, else a common sacred name."""
    out = []
    for k, certain in wit:
        if k.startswith("="):
            k = k[1:]
            k = next((w for w in list(sbl) + list(extra) + _NOMINA if _is_nomen(k, w)), k)
        out.append((k, certain))
    return out


def compare(ref, positions, siglum, hand="first", extra=()):
    """Does the witness have the SBLGNT words at these word positions
    (1-based) of the verse? An addition just after the last position or just
    before the first counts as a difference."""
    verse = witness(siglum).get(ref)
    if verse is None:
        return Comparison("lacuna")
    if verse.absent:
        return Comparison("lacuna" if verse.gaps else "absent")
    sbl = sblgnt_words(ref)
    if not sbl or not positions:
        return Comparison("lacuna")
    wit = _resolve(sbl, verse.first if hand == "first" else verse.corrected, extra)
    keys = [k for k, _ in wit]
    lo, hi = min(positions) - 1, max(positions)      # 0-based [lo, hi)
    matcher = difflib.SequenceMatcher(None, sbl, keys, autojunk=False)
    touched = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            if lo <= i1 <= hi:
                touched.append((tag, i1, i2, j1, j2))
        elif i1 < hi and i2 > lo:
            touched.append((tag, i1, i2, j1, j2))
    # Is the window (and what is around it) legible in the witness?
    blocks = [b for b in matcher.get_matching_blocks() if b.size]
    covered = any(b.a < hi and b.a + b.size > lo for b in blocks)
    if not touched:
        if covered:
            region = [wit[b.b + (i - b.a)][1] for b in blocks
                      for i in range(max(lo, b.a), min(hi, b.a + b.size))]
            return Comparison("agree" if all(region) or not verse.gaps else "lacuna")
        return Comparison("lacuna")
    if verse.gaps:
        # A difference next to lost or supplied text proves nothing.
        uncertain = any(not wit[j][1] for _, _, _, j1, j2 in touched
                        for j in range(max(0, j1 - 1), min(len(wit), j2 + 1)))
        lost_ends = not blocks or blocks[0].a > lo or blocks[-1].a + blocks[-1].size < hi
        if uncertain or lost_ends or any(t == "delete" for t, *_ in touched):
            return Comparison("lacuna")
    if hi - lo >= 6:
        # A passage: words added at either end, or is it there at all?
        if any(t == "insert" and i1 == hi and j2 - j1 >= 3 for t, i1, _, j1, j2 in touched):
            return Comparison("differ", "adds")
        matched = sum(max(0, min(hi, b.a + b.size) - max(lo, b.a)) for b in blocks)
        if matched / (hi - lo) >= 0.7:
            return Comparison("agree", "with small differences")
        if matched / (hi - lo) <= 0.25:
            return Comparison("differ", "lacks")
    mine = sorted(sbl[i] for _, i1, i2, _, _ in touched for i in range(i1, i2))
    theirs = sorted(keys[j] for _, _, _, j1, j2 in touched for j in range(j1, j2))
    if mine and mine == theirs:
        return Comparison("differ", "order")
    tags = {t for t, *_ in touched}
    if tags == {"insert"}:
        return Comparison("differ", "adds")
    if tags == {"delete"}:
        return Comparison("differ", "lacks")
    return Comparison("differ", "has other words")


def compare_gap(ref, unit, adds, siglum, hand="first"):
    """For an addition after the unit's lemma: has the witness the added
    words just before the SBLGNT word that follows the gap (or just after
    the lemma at the end of a verse)? The lemma word itself may differ."""
    verse = witness(siglum).get(ref)
    if verse is None or verse.absent:
        return Comparison("lacuna" if verse is None or verse.gaps else "absent")
    sbl = sblgnt_words(ref)
    extra = [w for r in adds for w in r.words]
    wit = _resolve(sbl, verse.first if hand == "first" else verse.corrected, extra)
    keys = [k for k, _ in wit]
    added = [tuple(r.words[len(unit.lemma.words):]) for r in adds]
    added = [a for a in added if a]
    if not added:
        return Comparison("lacuna")
    after = sbl[unit.end:unit.end + 2]          # the words after the gap
    before = sbl[max(0, unit.end - 2):unit.end]  # the lemma's last words
    spots = []
    if after:
        n = len(after)
        spots = [("before", j) for j in range(len(keys) - n + 1) if keys[j:j + n] == after]
        if not spots and len(after) == 2:
            spots = [("before", j) for j in range(len(keys)) if keys[j] == after[0]]
    if not spots and before:
        n = len(before)
        spots = [("after", j + n) for j in range(len(keys) - n + 1) if keys[j:j + n] == before]
    if not spots:
        return Comparison("lacuna")
    for where, j in spots:
        for a in added:
            if where == "before" and tuple(keys[max(0, j - len(a)):j]) == a:
                return Comparison("differ", "adds")
            if where == "after" and tuple(keys[j:j + len(a)]) == a:
                return Comparison("differ", "adds")
    # The gap is legible and holds none of the added words.
    where, j = spots[0]
    lo, hi = (max(0, j - 3), j) if where == "before" else (j, j + 3)
    if verse.gaps and not all(c for _, c in wit[lo:hi]):
        return Comparison("lacuna")
    return Comparison("agree")


def evidence(ref, positions, whole=False):
    """Everything the data says about these word positions of a verse:
    {"units": [Unit], "editions": {siglum: "agree"|"order"|"differ"},
     "witnesses": {siglum: Comparison}}. KJTR and the early manuscripts are
    compared word by word; the editions come from the apparatus (an edition
    the apparatus does not list here reads as the SBLGNT).

    whole: the question is whether a passage is there at all, so smaller
    differences inside it are left aside."""
    found = units_at(ref, positions)
    if whole:
        span = len(set(positions))
        found = [u for u in found if any(r.kind == "note" for r in u.others)
                 or (any(r.kind == "omit" for r in u.others) and u.end - u.start + 1 >= span / 2)]
    editions = {}
    for e in EDITIONS:
        editions[e] = "agree"
        for u in found:
            r = u.reading_of(e)
            if r is u.lemma:
                continue
            if r.words and sorted(r.words) == sorted(u.lemma.words) and editions[e] == "agree":
                editions[e] = "order"
            else:
                editions[e] = "differ"
    # Where the apparatus marks the place, compare there; otherwise at the
    # words the decision is about.
    places = [positions] if whole else ([u for u in found] or [positions])
    extra = [w for u in found for r in u.others for w in r.words]

    def at_places(siglum, hand="first"):
        results = []
        for p in places:
            if isinstance(p, Unit):
                adds = [r for r in p.others if r.kind == "add"]
                if adds and all(r.kind in ("add", "note") for r in p.others):
                    results.append(compare_gap(ref, p, adds, siglum, hand))
                    continue
                span = list(range(p.start, p.end + 1))
                # A long unit (a change of case all through a sentence) and a
                # decision about one word of it: compare that word.
                inside = sorted(set(span) & set(positions))
                p = inside if inside and len(inside) < len(span) else span
            results.append(compare(ref, p, siglum, hand, extra))
        for status in ("differ", "agree", "absent"):
            for c in results:
                if c.status == status:
                    return c
        return Comparison("lacuna")

    wits = {"KJTR": at_places("KJTR")}
    for s in early_sigla():
        c = at_places(s)
        if c.status != "lacuna":
            wits[s] = c
            corrected = at_places(s, hand="corrected")
            if corrected != c:
                wits[s + "c"] = corrected
    return {"units": found, "editions": editions, "witnesses": wits}


def decision_positions(decision):
    """{Ref: [word position]} of a decision's SBLGNT tokens."""
    out = {}
    for tok in decision.get("tokens") or []:
        m = re.fullmatch(r"n(\d\d)(\d\d\d)(\d\d\d)(\d\d\d)", tok)
        if not m or int(m[1]) not in _NUMBER_NT:
            continue
        ref = refs.Ref(_NUMBER_NT[int(m[1])], int(m[2]), int(m[3]))
        out.setdefault(ref, []).append(int(m[4]))
    return out


def missing_verses(book):
    """Verses the SBLGNT does not print but the Byzantine text or the King
    James Version's Greek has (Matthew 17:21, Luke 17:36, ...)."""
    have = set(sblgnt.load_book(book))
    out = set()
    for siglum in ("RP", "KJTR"):
        out |= {r for r, v in witness(siglum).items() if r.book == book and not v.absent and r not in have}
    return out


def verse_evidence(ref):
    """evidence() for a whole verse the SBLGNT leaves out: a witness that
    has it differs (adds), one marked as not having it agrees."""
    editions = {e: "agree" for e in EDITIONS}
    rp = witness("RP").get(ref)
    if rp is not None and not rp.absent:
        editions["RP"] = "differ"
    wits = {}
    for s in ("KJTR",) + early_sigla():
        v = witness(s).get(ref)
        if v is None:
            continue
        if v.absent:
            if not v.gaps:
                wits[s] = Comparison("agree")
        elif not v.gaps or len(v.first) > 3:
            wits[s] = Comparison("differ", "adds")
    return {"units": [], "editions": editions, "witnesses": wits}


def _named_missing(decision, positions):
    """Missing verses next to the decision's verses that its note names
    ("no verse 36", "verse 21", "17:21")."""
    text = " ".join([decision.get("choice", ""), decision.get("reason", "")])
    out = []
    for ref in positions:
        for r in sorted(missing_verses(ref.book), key=lambda r: r.sort_key()):
            if r.chapter == ref.chapter and abs(r.verse - ref.verse) <= 2 and re.search(
                    rf"\b(?:verses? |{r.chapter}:){r.verse}\b", text):
                out.append(r)
    return out


def decision_evidence(decision):
    """evidence() over all the verses a decision's tokens touch. A witness
    differs if it differs in any verse, agrees if it agrees in all of them;
    a verse the manuscript does not have counts as lacking the words. A
    whole verse the SBLGNT leaves out and the note names is used instead of
    the words around it."""
    positions = decision_positions(decision)
    missing = _named_missing(decision, positions)
    whole = readings_of(decision).included and sum(len(p) for p in positions.values()) >= 6
    if missing:
        per_verse = [verse_evidence(r) for r in missing]
    else:
        per_verse = [evidence(ref, pos, whole) for ref, pos in positions.items()]
    out = {"units": [u for e in per_verse for u in e["units"]],
           "editions": {e: "agree" for e in EDITIONS}, "witnesses": {}}
    for e in per_verse:
        for k, v in e["editions"].items():
            if v == "differ" or (v == "order" and out["editions"][k] == "agree"):
                out["editions"][k] = v
        for k, c in e["witnesses"].items():
            if c.status == "absent":
                c = Comparison("differ", "lacks")
            old = out["witnesses"].get(k)
            if old is None or c.status == "differ":
                out["witnesses"][k] = c
    return out


# --- Claims in a note ------------------------------------------------------

class Claim(NamedTuple):
    group: str         # "later", "early", "some", "western", "KJTR", "WH", "03", ...
    strength: str      # "strong" (the earliest, most) or "weak" (some, many)
    side: str          # "sblgnt", "other" or "unclear"
    hand: str          # "first" or "corrected" (for a named manuscript)
    clause: str        # the words of the note it was read from
    verdict: str = ""  # "confirmed", "contradicted", "unsupported", "mixed",
                       # "unclear" or "not covered"
    why: str = ""


_MS_NAMES = [
    (r"(?:Codex )?Sinaiticus", "01"), (r"(?:Codex )?Alexandrinus", "02"),
    (r"(?:Codex )?Vaticanus", "03"), (r"(?:Codex )?Ephraemi(?: Rescriptus)?", "04"),
    (r"(?:Codex )?Bezae|Codex D\b", "05"),
    (r"(?:Codex )?Washingtonianus|Codex W\b|the Freer (?:Gospels|codex|manuscript)", "032"),
]
_PAPYRUS = re.compile(r"\b(?:P|𝔓|papyrus |Papyrus )(\d{1,3})\b")
_EDITION_NAMES = [
    (r"Westcott(?: and |-|–| & )Hort|\bWH\b", "WH"), (r"Tregelles", "Treg"),
    (r"\bNA2[78]\b|Nestle(?:-|–| )Aland|\bthe Nestle text", "NA28"),
    (r"Robinson(?:-|–| and )Pierpont|Byzantine text|Majority Text", "RP"),
    (r"King James|\bKJV\b|Textus Receptus|traditional (?:printed )?(?:Greek )?text"
     r"|(?:older|later|early|traditional|first) printed (?:Greek )?(?:editions?|texts?)|Received Text"
     r"|printed editions", "KJTR"),
]
_QUANT = (r"(?:(?:the |a )?(?:great |vast )?(?:most|majority of(?: the)?|many|some|several|a few|few|other|"
          r"nearly all|almost all|all|one|two|numerous)\s+(?:of the\s+)?)?")
_GROUPS = [
    (rf"{_QUANT}(?:the )?(?:earliest|oldest|early|earlier|older|ancient)"
     r"(?:(?:,)? (?:and|or) (?:best|important|reliable|weighty))?(?: Greek)?\s+"
     r"(?:manuscripts?|copies|witnesses|papyri|papyrus|codices)", "early"),
    (rf"{_QUANT}(?:the )?(?:later|late|medieval|Byzantine)(?: Greek)?\s+(?:manuscripts?|copies|witnesses)", "later"),
    (r"(?:the |a )?(?:great |vast )?(?:majority of(?: the)? |most |nearly all |almost all )"
     r"(?:Greek )?(?:manuscripts?|copies|witnesses)", "later"),
    (rf"{_QUANT}(?:Greek )?(?:manuscripts?|copies|witnesses)", "some"),
    (r"(?:the )?Western (?:text|manuscripts?|witnesses|tradition|reading)", "western"),
]
_NOT_COVERED = re.compile(
    r"\b(?:Latin|Syriac|Coptic|Armenian|Georgian|Ethiopic|Gothic|Vulgate|versions|"
    r"ancient translations|early translations|translations|church fathers|fathers|"
    r"Origen|Tertullian|Irenaeus|Marcion|Jerome|Augustine|Chrysostom|Eusebius|Cyprian|"
    r"Clement|Ambrose|Epiphanius|Justin|Tatian|Diatessaron|Hilary|lectionar\w+|"
    r"minuscules?|family 1|family 13|f1|f13|1739|Dead Sea)\b")
_STRONG = re.compile(r"^(?:the (?:great |vast )?majority|most|nearly all|almost all|all|the "
                     r"(?:earliest|oldest|early|earlier|older|later|late|Byzantine))\b", re.I)
_SBL_SIDE = re.compile(
    r"\b(?:as|like|with|followed by|follow(?:s|ed)? by) (?:in )?the SBLGNT\b|"
    r"\bthe SBLGNT (?:follows|has followed|keeps|agrees with|goes with|sides with|prints what)\b|"
    r"\b(?:which|that) the SBLGNT (?:follows|prints|keeps|has)\b|"
    r"\bthe reading (?:followed|printed|kept) here\b|\bthe text followed here\b|\bas here\b|"
    r"\bsupport(?:s|ed)? (?:the SBLGNT|this reading|the reading followed)\b|"
    r"\bthe (?:harder|more difficult) (?:reading|wording|text|form)\b|"
    r"\b(?:this|that) is the reading of\b|\b(?:given|printed|followed|kept) here\b|"
    r"\b(?:have|has|read|support) (?:this|the same) (?:wording|reading|text|form)\b|"
    r"\bthe SBLGNT,? (?:supported|attested) by\b|\bthe reading of the SBLGNT\b", re.I)
_DIVIDED = re.compile(r"\b(?:divide|divided|differ|vary|varies|disagree|are split|split between)\b", re.I)
_LONGER = re.compile(r"\b(?:add|adds|added|adding|insert|inserts|inserted|include|includes|included|repeat|repeats|"
                     r"expand|expands|fill(?:s)? out|longer|continue|continues|go on|goes on|have more|"
                     r"(?:have|has|keep|keeps|contain|contains|give|gives|print|prints) "
                     r"(?:the |these |this |those |a |an )?(?:\w+ ){0,2}"
                     r"(?:words?|phrase|clause|verse|sentence|passage|request|addition|it|them)|"
                     r"(?:is|are) (?:found )?in)\b", re.I)
_NEGATED = re.compile(r"\b(?:lack|lacks|lacking|omit|omits|omitted|omitting|leave(?:s)? out|left out|"
                      r"leave(?:s)? (?:it|them|this|these words) out|"
                      r"do(?:es)? not (?:have|include|contain|read)|"
                      r"do(?:es)? not\b(?! (?:say|change|mean|affect|alter))|"
                      r"have no|has no|have none|has none|without|missing (?:from|in)|absent (?:from|in)|"
                      r"not (?:in|found in)|drop(?:s|ped)?|cut(?:s)?)\b", re.I)
_SHORT = re.compile(r"\b(?:shorter|short|only|alone|end(?:s)? (?:the \w+ )?(?:here|with|at)|end the verse|"
                    r"go(?:es)? straight (?:on|from)|"
                    r"stop(?:s)? (?:here|at))\b", re.I)
_ELSEWHERE = re.compile(r"(?<!as )(?<!from )(?<!like )\b(?:in|at) (?:verses? )?(?:[1-3] )?(?:[A-Z][a-z]+ )?\d+:\d+")
_QUOTE = re.compile(r"[\"“]([^\"”]+)[\"”]")
_HEDGE = re.compile(r"apparatus|[Rr]eviewers? (?:should|must)|to be checked|general knowledge|from memory")
_STOP = {"the", "a", "an"}
# Words that describe witnesses or variants, not a reading.
_GENERIC = {"manuscript", "manuscripts", "reading", "readings", "read", "reads", "text", "early", "earlier",
            "later", "earliest", "oldest", "older", "many", "some", "most", "add", "adds", "added", "omit",
            "omits", "sblgnt", "codex", "have", "has", "verse", "words", "word", "form",
            "is", "it", "here", "as", "others", "other", "few", "several", "copies",
            "bezae", "sinaiticus", "vaticanus", "alexandrinus", "ephraemi", "washingtonianus",
            "papyrus", "papyri", "latin", "syriac", "coptic", "old", "western", "byzantine", "king", "james",
            "version", "kjv", "witnesses", "hand", "first", "corrector", "followed", "follows", "by", "found",
            "printed", "editions", "greek", "lack", "lacks", "include", "includes", "included", "left",
            # function words, and words that describe a reading rather than quote it
            "verses", "sentence", "passage", "part", "place", "are", "were", "was", "be", "or",
            "among", "had", "do", "does", "did", "this", "these",
            "those", "there", "which", "what", "but", "if", "then", "also", "only", "both", "either",
            "omitted", "addition", "shorter", "longer", "end", "ends", "phrase", "clause", "line",
            "lines", "saying", "prayer", "story", "doubtful", "brackets", "bracketed"}
_WITNESS_WORDS = re.compile(r"\b(?:P\d+|Codex \w+|[A-Z][a-z]+us\b)")
# A statement about a witness in general, not about this place.
_GENERAL = re.compile(r"\b(?:usually|often|tend(?:s)? to|generally|typically|as a rule|known as|"
                      r"combines?|conflat\w+|joins? the two|both readings|mark(?:s|ed)? (?:it|them|the \w+) "
                      r"(?:with|for))\b")
_VERB_SPLIT = (r",?\s+and\s+(?=(?:is|are|was|were|has|have|had|read|reads|add|adds|lack|lacks|omit|omits|"
               r"leave|leaves|missing|absent|it is|they are)\b)")


def _sentences(text):
    """Split at a full stop, question or exclamation mark that is not inside
    quotation marks."""
    out, start, inside = [], 0, False
    for i, ch in enumerate(text):
        if ch in "\"“”":
            inside = not inside if ch == '"' else (ch == "“")
        elif ch in ".!?" and not inside and i + 1 < len(text) and text[i + 1] == " ":
            out.append(text[start:i + 1])
            start = i + 2
    out.append(text[start:])
    return [x for x in out if x.strip()]


def _clauses(reason):
    reason = re.sub(r"\((?:From general knowledge[^)]*)\)", "", reason)
    for sentence in _sentences(reason):
        for clause in re.split(r";\s+|,?\s+(?:but|while|whereas)\s+|:\s+(?=[A-Z])|" + _VERB_SPLIT, sentence):
            if clause and clause.strip():
                yield clause.strip()


def _core(text):
    """The words a choice or alternative quotes, without "(SBLGNT)", "the
    reading of the SBLGNT" and the like."""
    text = re.sub(r"\((?:the )?SBLGNT[^)]*\)", "", text or "")
    text = re.sub(r"^(?:follow(?:ing|s)? )?(?:the )?SBLGNT(?: text| reading)?\s*[:,]\s*", "", text)
    text = re.sub(r"[:,;]?\s*(?:as in |in |follow(?:ing|s)? |with |per )?(?:the reading of )?the SBLGNT\b.*$", "", text)
    text = re.sub(r"[:,;]\s*(?:the )?reading of\b.*$", "", text)
    return text.strip()


def _stem(w):
    for suffix in ("ing", "ed", "es", "s"):
        if len(w) > len(suffix) + 3 and w.endswith(suffix):
            return w[:-len(suffix)]
    return w


def _content(text):
    return {_stem(w) for w in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower()) if w not in _STOP}


_GENERIC_STEMS = _GENERIC | {_stem(w) for w in _GENERIC}


def _reading_words(text):
    """Content words of a reading as a decision gives it, without the names
    of the witnesses that have it."""
    return _content(text) - _GENERIC_STEMS


def _negative(text):
    return bool(re.search(r"^(?:no|not)\b|\b(?:without|omit\w*|lack\w*|leaves? out|left out|"
                          r"short(?:er)? text|no verse)\b", text, re.I))


class Readings(NamedTuple):
    choice: set        # content words of the SBLGNT reading as the decision gives it
    others: list       # [set] for each alternative
    negative: bool     # the choice is an absence ("without ...", "no verse 36")
    included: bool     # the choice is that words are there ("the verse is included")
    full_choice: set = frozenset()   # the same, before descriptive words are dropped
    full_others: list = ()
    short: bool = False              # the choice is called the short or shorter text


_INCLUDED = re.compile(r"\b(?:included|includes|include|belongs?|kept|keeps|present|in the text|is part|are part|"
                       r"with (?:the|its) (?:\w+ )?(?:verse|words|sentence|passage|prayer|clause|phrase)|"
                       r"longer text)\b", re.I)


def readings_of(decision):
    raw = decision.get("choice", "")
    choice = _core(raw)
    alts = [_core(a) for a in decision.get("alternatives") or []]
    others = [_reading_words(a) for a in alts]
    return Readings(_reading_words(choice), [o for o in others if o], _negative(choice),
                    bool(_INCLUDED.search(raw)), _content(choice),
                    [o for o in (_content(a) for a in alts) if o],
                    bool(re.search(r"\bshort(?:er)? (?:text|reading|form|wording)\b", raw, re.I)))


def _vote(fragment, readings):
    """'sblgnt', 'other' or None: which reading a quoted fragment names.
    Tried with all the words first, then without the descriptive ones."""
    full = _content(fragment)
    for words, choice, others in ((full, readings.full_choice, readings.full_others),
                                  (full - _GENERIC_STEMS, readings.choice, readings.others)):
        if words and choice:
            vote = _vote_words(words, Readings(choice, list(others), False, False))
            if vote:
                return vote
    return None


def _vote_words(words, readings):

    def share(reading):
        return len(words & reading) / min(len(words), len(reading)) if reading else 0

    def jaccard(reading):
        return len(words & reading) / len(words | reading) if reading else 0
    c = share(readings.choice)
    a = max((share(o) for o in readings.others), default=0)
    if c >= 0.6 and c > a + 0.15:
        return "sblgnt"
    if a >= 0.6 and a > c + 0.15:
        return "other"
    if c >= 0.6 and c == a:
        # "not" against "not yet": the words that only one reading has decide.
        others = set().union(*readings.others)
        mine, theirs = readings.choice - others, others - readings.choice
        if words & theirs and not words & mine:
            return "other"
        if words & mine and not words & theirs:
            return "sblgnt"
        if not words & (mine | theirs):
            if theirs and not mine:
                return "sblgnt"     # the quote lacks what the other reading adds
            if mine and not theirs:
                return "other"
    if c >= 0.6 and c == a:     # "blessing" against "praising and blessing"
        cj = jaccard(readings.choice)
        aj = max(jaccard(o) for o in readings.others)
        if abs(cj - aj) >= 0.2:
            return "sblgnt" if cj > aj else "other"
    return None


def _side(clause, readings, direction):
    """Which reading a clause gives the witnesses it names: "sblgnt",
    "other" or "unclear"."""
    if _SBL_SIDE.search(clause):
        return "sblgnt"
    bare = _QUOTE.sub('""', clause)      # "I do not find" is not a "not"
    negated = bool(_NEGATED.search(bare))
    longer = bool(_LONGER.search(_NEGATED.sub("", bare)))
    short = bool(_SHORT.search(bare))
    if _DIVIDED.search(bare) and not longer and not negated:
        return "exists"     # "manuscripts differ here": that there is a variant
    # 0. The choice is an absence or the shorter text.
    if readings and (readings.negative or readings.short):
        if (negated or short) and not longer:
            return "sblgnt"
        if longer and not negated:
            return "other"
    # 1. The clause quotes one of the readings.
    if readings and not readings.negative:
        votes, attached = set(), False
        for m in _QUOTE.finditer(clause):
            vote = _vote(m.group(1), readings)
            if vote and (_NEGATED.search(clause[max(0, m.start() - 25):m.start()])
                         or re.search(r"\b(?:instead of|in place of|rather than)\s*$", clause[:m.start()])):
                vote, attached = ("other" if vote == "sblgnt" else "sblgnt"), True
            if vote:
                votes.add(vote)
        if not votes:
            # Words only one of the readings has, named outside quotation marks.
            words = _content(_WITNESS_WORDS.sub(" ", bare)) - _GENERIC_STEMS
            others = set().union(*readings.others) if readings.others else set()
            mine = len(words & (readings.choice - others))
            theirs = len(words & (others - readings.choice))
            if mine and not theirs:
                votes = {"sblgnt"}
            elif theirs and not mine:
                votes = {"other"}
            elif readings.choice and readings.choice <= words and not any(o <= words for o in readings.others):
                votes = {"sblgnt"}      # "most manuscripts read sixty" (not "a hundred and sixty")
            if negated:
                votes = set()           # descriptive words of a reading said to be missing: no vote
        if len(votes) == 1:
            vote = votes.pop()
            if negated and not attached:
                vote = "other" if vote == "sblgnt" else "sblgnt"
            return vote
    # 2. Added or left out, and which reading is the longer.
    if direction is None and readings and readings.included and re.search(
            r"\b(?:the|this|these|that|whole|those) (?:verses?|passage|sentence|prayer|words|clause|story|"
            r"section|saying|lines?)\b|\b(?:it|them)\b", bare):
        direction = "sblgnt_longer"
    if direction and (negated or short) != longer:
        shorter_side = "sblgnt" if direction == "sblgnt_shorter" else "other"
        longer_side = "other" if direction == "sblgnt_shorter" else "sblgnt"
        return longer_side if longer else shorter_side
    if re.search(r"\bthe SBLGNT\b", clause, re.I) and not re.search(
            r"\b(?:unlike|against|instead of|than)\b", clause):
        return "sblgnt"
    if (longer and not negated and not short) or re.search(r"\binstead\b(?! of)", bare):
        return "other"      # "many later manuscripts add ...", "Codex B instead reads ..."
    if negated and not longer and readings and not (readings.negative or readings.short) and re.search(
            r"\b(?:lack|lacks|omit|omits|leave out|leaves out|do not have|does not have)\s+"
            r"(?:it|them|this \w+|these \w+|the (?:words?|phrase|clause|sentence|verse|name|title))\b", bare):
        return "other"      # "early manuscripts lack the words": the SBLGNT's words
    return "unclear"


def read_claims(reason, readings=None, direction=None):
    """The claims of a note about witnesses, as [Claim].

    direction is "sblgnt_shorter", "sblgnt_longer" or None: which reading is
    the longer, from the data, so that "add" and "lack" can be put on a side."""
    claims = []
    for clause in _clauses(reason):
        if _HEDGE.search(clause) or _ELSEWHERE.search(clause) or _GENERAL.search(clause):
            continue
        found = []
        for pattern, code in _MS_NAMES:
            for m in re.finditer(pattern, clause):
                after = clause[m.end():m.end() + 40]
                before = clause[max(0, m.start() - 30):m.start()]
                hand = "corrected" if re.match(
                    r"\s*(?:\(|,)?\s*(?:as corrected|after correction|corrected|a corrector|in a correction)",
                    after) or re.search(r"(?:corrector|correction|later hand) (?:of|in|to) (?:the )?$", before) \
                    else "first"
                found.append((m.start(), m.end(), code, "strong", hand))
        for m in _PAPYRUS.finditer(clause):
            found.append((m.start(), m.end(), "P" + m[1], "strong", "first"))
        for pattern, code in _EDITION_NAMES:
            for m in re.finditer(pattern, clause):
                found.append((m.start(), m.end(), code, "strong", "first"))
        for pattern, code in _GROUPS:
            for m in re.finditer(pattern, clause, re.I):
                if any(a < m.end() and m.start() < b for a, b, *_ in found):
                    continue
                phrase = m.group(0)
                if re.match(r"\s*(?:P\d|𝔓|\d|of the|called|known|Codex|\()", clause[m.end():]) \
                        and not re.search(r"(?:manuscripts|papyri|witnesses|copies)$", phrase):
                    continue    # "the early papyrus P75": that papyrus, not a group
                if code == "some" and re.match(r"(?:the |a )?other\b", phrase, re.I):
                    continue    # "other manuscripts": the rest, not a claim
                strength = "strong" if _STRONG.match(phrase) else "weak"
                if code == "early" and re.search(r"\b(?:earliest|oldest|older|earlier)\b", phrase, re.I):
                    code = "earliest"
                found.append((m.start(), m.end(), code, strength, "first"))
        if not found:
            continue
        side = _side(clause, readings, direction)
        for _, _, code, strength, hand in sorted(found):
            claims.append(Claim(code, strength, side, hand, clause))
        if _NOT_COVERED.search(clause):
            claims.append(Claim("versions", "weak", side, "first", clause, "not covered",
                                "ancient translations, church fathers and minuscules are not pinned"))
    return claims


def note_direction(decision):
    """Which reading is the longer, from the note itself: a quoted reading
    that is part of the choice and is said to be missing, or a quoted
    reading not in the choice that is said to be added."""
    reason = decision.get("reason", "")
    choice = _content(_core(decision.get("choice", "")))
    for m in _QUOTE.finditer(reason):
        words = _content(m.group(1))
        before = reason[max(0, m.start() - 30):m.start()]
        if words and words <= choice and _NEGATED.search(before):
            return "sblgnt_longer"
        if words and not words <= choice and re.search(r"\b(?:add|adds|added|insert|inserts)\b", before):
            return "sblgnt_shorter"
    return None


def direction(ev):
    """Which reading is the longer, from how the witnesses that differ do."""
    details = {c.detail for c in ev["witnesses"].values() if c.status == "differ"}
    kinds = {r.kind for u in ev["units"] for r in u.others} - {"note"}
    if any("⟦" in r.text for u in ev["units"] for r in u.others) and not kinds:
        kinds = {"omit"}
    if kinds == {"add"} or (not kinds and details == {"adds"}):
        return "sblgnt_shorter"
    if kinds == {"omit"} or (not kinds and details == {"lacks"}):
        return "sblgnt_longer"
    return None


def _early(ev, earliest=False):
    """{siglum: "agree"|"differ"} for the early manuscripts extant here; with
    earliest, only the papyri, Codex Sinaiticus and Codex Vaticanus (the
    fourth century and before)."""
    return {k: c.status for k, c in ev["witnesses"].items()
            if k not in ("KJTR", "RP") and not k.endswith("c") and c.status in ("agree", "differ")
            and (not earliest or k in ("01", "03") or k.startswith("P"))}


_ORDER_WORDS = re.compile(r"\b(?:order|move[sd]?|moving|transpos\w*|position|places?|put|puts|after|before)\b")


def _view(ev, about_order):
    """The evidence with differences of word order counted as differences
    only for a claim about the order of the words."""
    def status(v):
        return ("differ" if about_order else "agree") if v == "order" else v
    wits = {}
    for k, c in ev["witnesses"].items():
        if c.status == "differ" and c.detail == "order":
            c = Comparison("differ", "order") if about_order else Comparison("agree", "in another order")
        wits[k] = c
    return {"units": ev["units"], "editions": {k: status(v) for k, v in ev["editions"].items()},
            "witnesses": wits}


def judge(claim, ev):
    """Compare one claim with the evidence; return it with a verdict."""
    if claim.verdict:
        return claim
    ev = _view(ev, bool(_ORDER_WORDS.search(claim.clause)))
    if claim.side == "exists":
        differs = any(v == "differ" for v in ev["editions"].values()) or any(
            c.status == "differ" for c in ev["witnesses"].values())
        return claim._replace(verdict="confirmed" if differs else "unsupported",
                              why="the pinned witnesses differ here" if differs
                              else "no pinned witness differs here")
    want = {"sblgnt": "agree", "other": "differ"}.get(claim.side)
    if want is None:
        return claim._replace(verdict="unclear", why="cannot tell which reading the note gives this witness")
    if claim.group in EDITIONS:
        got = ev["editions"][claim.group]
        name = EDITION_NAMES[claim.group]
        return claim._replace(verdict="confirmed" if got == want else "contradicted",
                              why=f"{name} {'reads as' if got == 'agree' else 'differs from'} the SBLGNT here")
    if claim.group == "KJTR" or claim.group in MANUSCRIPTS or claim.group.startswith("P"):
        name = EDITION_NAMES.get(claim.group) or MANUSCRIPTS.get(claim.group) or claim.group
        c = ev["witnesses"].get(claim.group)
        corrected = ev["witnesses"].get(claim.group + "c")
        if claim.hand == "corrected":
            if not corrected:
                return claim._replace(verdict="unsupported",
                                      why=f"the transcription of {name} records no correction here")
            c = corrected
        if c is None or c.status not in ("agree", "differ"):
            return claim._replace(verdict="unsupported", why=f"{name} is lost or not pinned here")
        if c.status == want:
            return claim._replace(verdict="confirmed", why=f"{name} {_says(c)}")
        if corrected and corrected.status == want:
            return claim._replace(verdict="confirmed", why=f"{name} as corrected {_says(corrected)}")
        return claim._replace(verdict="contradicted", why=f"{name} {_says(c)}")
    if claim.group == "later":
        got = ev["editions"]["RP"]
        if got == want:
            return claim._replace(verdict="confirmed", why="the Byzantine text (RP) agrees")
        return claim._replace(verdict="contradicted" if claim.strength == "strong" else "unsupported",
                              why="the Byzantine text (RP) reads the other way")
    if claim.group in ("early", "earliest"):
        early = _early(ev, earliest=claim.group == "earliest")
        on = sorted(k for k, v in early.items() if v == want)
        if not early:
            return claim._replace(verdict="unsupported", why="no early manuscript is extant here")
        share = len(on) / len(early)
        listing = f"{len(on)} of {len(early)} early manuscripts ({', '.join(on) or 'none'})"
        if claim.strength == "strong":
            if share >= 2 / 3:
                return claim._replace(verdict="confirmed", why=listing)
            if share <= 1 / 3 and len(early) >= 2:
                return claim._replace(verdict="contradicted", why=listing)
            return claim._replace(verdict="mixed", why=listing)
        if on:
            return claim._replace(verdict="confirmed", why=listing)
        return claim._replace(verdict="unsupported", why=listing)
    if claim.group == "western":
        c = ev["witnesses"].get("05")
        if c and c.status == want:
            return claim._replace(verdict="confirmed", why="Codex Bezae agrees")
        return claim._replace(verdict="unsupported", why="Codex Bezae is lost here or reads the other way")
    # "some manuscripts", "many manuscripts"
    sides = [c.status for c in ev["witnesses"].values() if c.status in ("agree", "differ")]
    sides.append(ev["editions"]["RP"])
    if want in sides:
        return claim._replace(verdict="confirmed", why="at least one pinned witness reads so")
    return claim._replace(verdict="unsupported", why="no pinned witness reads so")


def _says(c):
    return "has the SBLGNT words" if c.status == "agree" else f"differs from the SBLGNT ({c.detail})"


def check_note(decision):
    """{"claims": [Claim], "status": ..., "evidence": ...} for a decision.

    status: "confirmed" (every claim agrees with the data), "partly" (none
    is contradicted, but some the data cannot settle), "contradicted",
    "unclear", "no claims" (the note names no witnesses) or "no data" (no
    pinned witness differs from the SBLGNT at the decision's words)."""
    ev = decision_evidence(decision)
    claims = [judge(c, ev) for c in read_claims(decision.get("reason", ""), readings_of(decision),
                                                 direction(ev) or note_direction(decision))]
    differs = any(v in ("differ", "order") for v in ev["editions"].values()) or any(
        c.status == "differ" for c in ev["witnesses"].values())
    verdicts = {c.verdict for c in claims}
    if "contradicted" in verdicts:
        status = "contradicted"
    elif not differs:
        status = "no data"
    elif not claims:
        status = "no claims"
    elif verdicts & {"unclear", "mixed"}:
        status = "unclear"
    elif verdicts == {"confirmed"}:
        status = "confirmed"
    else:
        status = "partly"
    return {"claims": claims, "status": status, "evidence": ev}
