"""Transliteration of the source words into Latin letters, for readers who
don't read Greek or Hebrew (the word panel's Transliteration setting).

Greek follows the SBL Handbook's academic style (logos, archē, houtos,
Iēsous): eta and omega keep their macrons, rough breathing is h, gamma
before a velar is n, and upsilon is u inside a diphthong.

Hebrew follows the SBL Handbook's general-purpose style (bereshit, elohim,
ha shamayim, ruah, torah): no marks for alef, ayin or vowel length,
bet/kaf/pe without dagesh as v/kh/f, shin as sh and tsade as ts, vocal
shewa as e, and a consonant doubled by dagesh forte written twice. The
codex does not mark qamets qatan, so it is inferred from the syllable.
Each morpheme is written on its own, as the word panel shows them.

Letters are named by their Unicode names, never typed: original-language
text in this project only ever comes from the source data.
"""
import unicodedata

# --- Greek -----------------------------------------------------------------

_GREEK = {
    "ALPHA": "a", "BETA": "b", "GAMMA": "g", "DELTA": "d", "EPSILON": "e", "ZETA": "z",
    "ETA": "\u0113", "THETA": "th", "IOTA": "i", "KAPPA": "k", "LAMDA": "l", "MU": "m",
    "NU": "n", "XI": "x", "OMICRON": "o", "PI": "p", "RHO": "r", "SIGMA": "s",
    "FINAL SIGMA": "s", "TAU": "t", "UPSILON": "y", "PHI": "ph", "CHI": "ch", "PSI": "ps",
    "OMEGA": "\u014d",
}
_GREEK_VOWELS = {"ALPHA", "EPSILON", "ETA", "IOTA", "OMICRON", "UPSILON", "OMEGA"}
_ROUGH = "\u0314"        # combining reversed comma above (dasia)
_DIAERESIS = "\u0308"
_VELARS = {"GAMMA", "KAPPA", "XI", "CHI"}


def _greek_letters(text):
    """The text's letters as [name, capital, marks], other characters as
    [None, False, char]."""
    out = []
    for ch in unicodedata.normalize("NFD", text):
        if unicodedata.combining(ch):
            if out and out[-1][0]:
                out[-1][2] += ch
            continue
        name = unicodedata.name(ch, "")
        for prefix, capital in (("GREEK SMALL LETTER ", False), ("GREEK CAPITAL LETTER ", True)):
            if name.startswith(prefix) and name[len(prefix):] in _GREEK:
                out.append([name[len(prefix):], capital, ""])
                break
        else:
            out.append([None, False, ch])
    return out


def greek(text):
    """A Greek word (or phrase) in Latin letters."""
    letters = _greek_letters(text)
    out = []
    word_start = True
    for i, (name, capital, marks) in enumerate(letters):
        if name is None:
            # Elision marks and punctuation pass through; a space starts a word.
            out.append(marks)
            word_start = marks.isspace()
            continue
        nxt = letters[i + 1] if i + 1 < len(letters) else [None, False, ""]
        prev = letters[i - 1] if i > 0 else [None, False, ""]
        latin = _GREEK[name]
        if name == "GAMMA" and nxt[0] in _VELARS:
            latin = "n"
        if name == "UPSILON" and _DIAERESIS not in marks and (
                prev[0] in ("ALPHA", "EPSILON", "ETA", "OMICRON") or
                (nxt[0] == "IOTA" and _DIAERESIS not in nxt[2])):
            latin = "u"
        if name == "RHO" and _ROUGH in marks:
            latin = "rh"
        if name in _GREEK_VOWELS and word_start:
            # The breathing of a word's first vowel sound sits on its second
            # letter when that sound is a diphthong (houtos, hui-).
            cluster = [letters[i]]
            if nxt[0] in _GREEK_VOWELS:
                cluster.append(nxt)
            if any(_ROUGH in m for _, _, m in cluster):
                latin = "h" + latin
        if capital:
            latin = latin[0].upper() + latin[1:]
        out.append(latin)
        word_start = False
    return "".join(out)


# --- Hebrew ----------------------------------------------------------------

# Consonants: (plain, with dagesh). Alef and ayin are not written.
_CONSONANTS = {
    "ALEF": ("", ""), "BET": ("v", "b"), "GIMEL": ("g", "g"), "DALET": ("d", "d"),
    "HE": ("h", "h"), "VAV": ("v", "v"), "ZAYIN": ("z", "z"), "HET": ("h", "h"),
    "TET": ("t", "t"), "YOD": ("y", "y"), "KAF": ("kh", "k"), "FINAL KAF": ("kh", "k"),
    "LAMED": ("l", "l"), "MEM": ("m", "m"), "FINAL MEM": ("m", "m"), "NUN": ("n", "n"),
    "FINAL NUN": ("n", "n"), "SAMEKH": ("s", "s"), "AYIN": ("", ""), "PE": ("f", "p"),
    "FINAL PE": ("f", "p"), "TSADI": ("ts", "ts"), "FINAL TSADI": ("ts", "ts"),
    "QOF": ("q", "q"), "RESH": ("r", "r"), "SHIN": ("sh", "sh"), "TAV": ("t", "t"),
}
_VOWELS = {
    "PATAH": "a", "QAMATS": "a", "HATAF PATAH": "a", "SEGOL": "e", "TSERE": "e",
    "HATAF SEGOL": "e", "HIRIQ": "i", "HOLAM": "o", "HOLAM HASER FOR VAV": "o",
    "HATAF QAMATS": "o", "QUBUTS": "u",
}
_LONG = {"QAMATS", "TSERE", "HOLAM", "HOLAM HASER FOR VAV"}
_HATAF = {"HATAF PATAH", "HATAF SEGOL", "HATAF QAMATS"}
_MAQAF = "\u05be"


def _hebrew_letters(text):
    """The text's consonants with their points: dicts of name, vowel,
    shewa, dagesh, sin, meteg. Accents and other marks are dropped."""
    out = []
    for ch in text:
        name = unicodedata.name(ch, "")
        if name.startswith("HEBREW LETTER "):
            out.append({"name": name[14:], "vowel": None, "shewa": False, "dagesh": False, "sin": False,
                        "meteg": False, "vowel2": None})
        elif not out:
            continue
        elif name.startswith("HEBREW POINT "):
            point = name[13:]
            last = out[-1]
            if point in _VOWELS:
                if last["vowel"]:
                    last["vowel2"] = point
                else:
                    last["vowel"] = point
            elif point == "SHEVA":
                last["shewa"] = True
            elif point == "DAGESH OR MAPIQ":
                last["dagesh"] = True
            elif point == "SIN DOT":
                last["sin"] = True
            elif point == "METEG":
                last["meteg"] = True
    return out


def hebrew(text, prefix=False, maqaf=False, verb=False):
    """A Hebrew (or Aramaic) word or morpheme in Latin letters, on its own:
    a prefix (be-, ve-, ha-) is written apart from the word it joins, so the
    letter after the article is not doubled (ha shamayim). prefix: the
    morpheme joins the word that follows, so a shewa at its end is still
    said. maqaf: the word is bound to the next one by maqaf and loses its
    stress, so a qamets in its last, closed syllable is o (kol). verb: the
    morpheme is a verb, where a qamets before a shewa is long and the shewa
    said (amru is ameru); elsewhere that qamets is short and the syllable
    closed (hokhmah)."""
    letters = _hebrew_letters(text)
    out = []
    prev_vowel = None   # None at the start; then short, long, hataf, vocal, silent
    for i, c in enumerate(letters):
        name, vowel = c["name"], c["vowel"]
        nxt = letters[i + 1] if i + 1 < len(letters) else None
        last = nxt is None
        # Vav as a vowel letter: shureq (u), or holam male (o) after a
        # consonant with no vowel of its own.
        if name == "VAV" and not c["shewa"] and (vowel is None or vowel == "HOLAM"):
            bare_before = i == 0 or (letters[i - 1]["vowel"] is None and not letters[i - 1]["shewa"])
            if c["dagesh"] and vowel is None and bare_before:
                out.append("u")
                prev_vowel = "long"
                continue
            if vowel == "HOLAM" and not c["dagesh"] and bare_before and i > 0:
                out.append("o")
                prev_vowel = "long"
                continue
        # Yod as a vowel letter after i or e (hiriq, tsere, segol).
        if (name == "YOD" and vowel is None and not c["shewa"] and not c["dagesh"] and i > 0
                and letters[i - 1]["vowel"] in ("HIRIQ", "TSERE", "SEGOL")):
            prev_vowel = "long"
            continue
        # An alef with no vowel is silent.
        if name == "ALEF" and vowel is None and not c["shewa"]:
            continue
        plain, hard = _CONSONANTS.get(name, ("", ""))
        if name == "SHIN" and c["sin"]:
            plain = hard = "s"
        consonant = plain
        doubled = False
        if c["dagesh"]:
            consonant = hard
            # After a vowel the dagesh doubles the letter (forte); at the
            # start of a word or after a closed syllable it only hardens a
            # begadkefat letter (lene). A final he's dagesh is mapiq.
            doubled = prev_vowel in ("short", "long") and not (name == "HE" and last)
        if doubled and len(consonant) == 1:
            consonant *= 2
        # Furtive patah: the patah of a word's final het, ayin or mapiq he
        # is said before it (ruah).
        if last and not prefix and i > 0 and vowel == "PATAH" and (
                name in ("HET", "AYIN") or (name == "HE" and c["dagesh"])):
            out.append("a" + consonant)
            break
        out.append(consonant)
        if vowel:
            latin = _VOWELS[vowel]
            # Qamets qatan: a qamets in the last, closed syllable of a word
            # bound by maqaf (kol-), or before a silent shewa outside verbs
            # (hokhmah, ozne).
            qatan_before_shewa = (not verb and not c["meteg"] and nxt is not None and nxt["shewa"]
                                  and not nxt["dagesh"] and i + 2 < len(letters))
            if vowel == "QAMATS" and nxt is not None and nxt["vowel"] is None and (qatan_before_shewa or (
                    maqaf and i + 2 == len(letters) and not nxt["shewa"])):
                latin = "o"
            # Two vowels on one letter: the perpetual qere of Jerusalem
            # (Yerushalayim), read with a yod between them.
            if c["vowel2"]:
                latin += "y" + _VOWELS[c["vowel2"]]
            out.append(latin)
            # A long vowel ends an open syllable, so a shewa after it is
            # said. Qamets may be short (qamets qatan) or long; it counts as
            # long when the codex marks it with a meteg.
            long = vowel in _LONG and (vowel != "QAMATS" or c["meteg"] or verb)
            prev_vowel = "hataf" if vowel in _HATAF else "long" if long else "short"
        elif c["shewa"]:
            # Vocal at the start, after a long vowel, under a
            # doubled letter, and as the second of two shewas; silent at the
            # end and after a closed syllable.
            vocal = (prefix or not last) and (prev_vowel in (None, "long") or doubled or prev_vowel == "silent")
            if vocal:
                out.append("e")
                prev_vowel = "vocal"
            else:
                prev_vowel = "silent"
        else:
            prev_vowel = "silent"
    return "".join(out)


def hebrew_words(words):
    """Transliterations for a verse's morphemes (MACULA rows, in order), as
    {id: text}."""
    out = {}
    before = ""   # the previous morpheme of the same word, if any
    for w in words:
        if w.get("strong", "").lstrip("0") in ("3068", "3069") and w.get("morph", "").startswith("Np"):
            text = "YHWH"   # the divine name: its pointing is the reading, not the word
        else:
            text = hebrew(w["text"], prefix=w["after"] == "", maqaf=_MAQAF in w["after"],
                          verb=w.get("morph", "").startswith("V"))
        # A suffix that is only a yod, after an i or e sound, is its vowel
        # letter and silent (ro-i, "my shepherd").
        letters = _hebrew_letters(w["text"])
        if before[-1:] in ("i", "e") and len(letters) == 1 and letters[0]["name"] == "YOD" and not (
                letters[0]["vowel"] or letters[0]["shewa"] or letters[0]["dagesh"]):
            text = ""
        out[w["id"]] = text
        before = text if w["after"] == "" else ""
    return out

