"""Plain-language descriptions of MACULA Greek and Hebrew morphology codes.

The word extracts (data/grc/) carry Robinson-style codes such as N-DSF or
V-2AAI-3S. describe() turns one into words a reader can follow, in English
or Spanish: "Noun · dative singular feminine", "Verb · second aorist active
indicative · 3rd person singular". An unknown code raises ValueError, so a
new code in the data fails the tests rather than showing a reader nothing.
"""
import re

WORDS = {
    "en": {
        "pos": {"N": "Noun", "V": "Verb", "A": "Adjective", "T": "Article",
                "P": "Personal pronoun", "R": "Relative pronoun", "D": "Demonstrative pronoun",
                "K": "Correlative pronoun", "X": "Indefinite pronoun", "I": "Interrogative pronoun",
                "F": "Reflexive pronoun", "C": "Reciprocal pronoun", "S": "Possessive pronoun",
                "Q": "Correlative or interrogative pronoun",
                "ADV": "Adverb", "CONJ": "Conjunction", "PREP": "Preposition", "PRT": "Particle",
                "COND": "Conditional conjunction", "INJ": "Interjection",
                "HEB": "Hebrew word", "ARAM": "Aramaic word"},
        "indeclinable": {"PRI": "proper name, indeclinable", "LI": "letter, indeclinable",
                         "OI": "indeclinable", "NUI": "number, indeclinable"},
        "case": {"N": "nominative", "G": "genitive", "D": "dative", "A": "accusative", "V": "vocative"},
        "number": {"S": "singular", "P": "plural"},
        "gender": {"M": "masculine", "F": "feminine", "N": "neuter"},
        "tense": {"P": "present", "I": "imperfect", "F": "future", "A": "aorist",
                  "R": "perfect", "L": "pluperfect"},
        "second": "second {}",
        "verb": "{tense} {voice} {mood}", "voiced": "{}",
        "voice": {"A": "active", "M": "middle", "P": "passive", "E": "middle or passive",
                  "D": "middle (deponent)", "O": "passive (deponent)",
                  "N": "middle or passive (deponent)", "Q": "impersonal active", "X": ""},
        "mood": {"I": "indicative", "S": "subjunctive", "O": "optative", "M": "imperative",
                 "N": "infinitive", "P": "participle", "R": "participle (as a command)"},
        "person": {"1": "1st person", "2": "2nd person", "3": "3rd person"},
        "suffix": {"N": "negative", "I": "interrogative", "S": "superlative", "C": "comparative",
                   "ATT": "Attic form", "K": "crasis (two words run together)",
                   "P": "with particle attached", "ABB": "abbreviated form"},
    },
    "es": {
        "pos": {"N": "Sustantivo", "V": "Verbo", "A": "Adjetivo", "T": "Artículo",
                "P": "Pronombre personal", "R": "Pronombre relativo", "D": "Pronombre demostrativo",
                "K": "Pronombre correlativo", "X": "Pronombre indefinido", "I": "Pronombre interrogativo",
                "F": "Pronombre reflexivo", "C": "Pronombre recíproco", "S": "Pronombre posesivo",
                "Q": "Pronombre correlativo o interrogativo",
                "ADV": "Adverbio", "CONJ": "Conjunción", "PREP": "Preposición", "PRT": "Partícula",
                "COND": "Conjunción condicional", "INJ": "Interjección",
                "HEB": "Palabra hebrea", "ARAM": "Palabra aramea"},
        "indeclinable": {"PRI": "nombre propio, indeclinable", "LI": "letra, indeclinable",
                         "OI": "indeclinable", "NUI": "número, indeclinable"},
        "case": {"N": "nominativo", "G": "genitivo", "D": "dativo", "A": "acusativo", "V": "vocativo"},
        "number": {"S": "singular", "P": "plural"},
        "gender": {"M": "masculino", "F": "femenino", "N": "neutro"},
        "tense": {"P": "presente", "I": "imperfecto", "F": "futuro", "A": "aoristo",
                  "R": "perfecto", "L": "pluscuamperfecto"},
        "second": "{} segundo",
        "verb": "{mood} {tense}, {voice}", "voiced": "voz {}",
        "voice": {"A": "activa", "M": "media", "P": "pasiva", "E": "media o pasiva",
                  "D": "media (deponente)", "O": "pasiva (deponente)",
                  "N": "media o pasiva (deponente)", "Q": "activa impersonal", "X": ""},
        "mood": {"I": "indicativo", "S": "subjuntivo", "O": "optativo", "M": "imperativo",
                 "N": "infinitivo", "P": "participio", "R": "participio (como mandato)"},
        "person": {"1": "1.ª persona", "2": "2.ª persona", "3": "3.ª persona"},
        "suffix": {"N": "negaci\u00f3n", "I": "interrogativo", "S": "superlativo", "C": "comparativo",
                   "ATT": "forma ática", "K": "crasis (dos palabras unidas)",
                   "P": "con partícula unida", "ABB": "forma abreviada"},
    },
}

_VERB = re.compile(r"(2?)([PIFARL])([AMPEDONQX])([ISOMNPR])(?:-(.+))?")
_CNG = re.compile(r"([1-3]?)([NGDAV])([SP])([MFN]?)")
_PN = re.compile(r"([1-3])([SP])")
# Possessive pronouns: the owner's person and number, then the noun's case,
# number and gender (S-1SNSM: "my", nominative singular masculine).
_POSS = re.compile(r"([1-3])([SP])([NGDAV])([SP])([MFN])")


def describe(code, lang="en"):
    w = WORDS[lang]
    parts = code.split("-")
    pos, rest = parts[0], parts[1:]
    if pos not in w["pos"]:
        raise ValueError(f"unknown part of speech in {code!r}")
    out = [w["pos"][pos]]
    if pos == "V":
        m = _VERB.fullmatch("-".join(rest))
        if not m:
            raise ValueError(f"unknown verb code {code!r}")
        second, tense, voice, mood, tail = m.groups()
        t = w["tense"][tense]
        if second:
            t = w["second"].format(t)
        v = w["voice"][voice]
        phrase = w["verb"].format(tense=t, voice=w["voiced"].format(v) if v else "", mood=w["mood"][mood])
        out.append(re.sub(r"[ ,]+$", "", re.sub(r"\s+", " ", phrase)).strip())
        tail = tail.split("-") if tail else []
        if tail:
            form = tail.pop(0)
            pn, cng = _PN.fullmatch(form), _CNG.fullmatch(form)
            if mood in "PR" and cng:
                out.append(_cng(cng, w))
            elif pn:
                out.append(f"{w['person'][pn[1]]} {w['number'][pn[2]]}")
            else:
                raise ValueError(f"unknown verb ending in {code!r}")
        rest = tail
    elif rest and rest[0] in w["indeclinable"]:
        out.append(w["indeclinable"][rest[0]])
        rest = rest[1:]
    elif pos == "S" and rest and _POSS.fullmatch(rest[0]):
        m = _POSS.fullmatch(rest[0])
        out.append(f"{w['person'][m[1]]} {w['number'][m[2]]} \u00b7 "
                   f"{w['case'][m[3]]} {w['number'][m[4]]} {w['gender'][m[5]]}")
        rest = rest[1:]
    elif rest and _CNG.fullmatch(rest[0]):
        out.append(_cng(_CNG.fullmatch(rest[0]), w))
        rest = rest[1:]
    for suffix in rest:
        if suffix not in w["suffix"]:
            raise ValueError(f"unknown suffix in {code!r}")
        out.append(w["suffix"][suffix])
    return " · ".join(out)


def _cng(m, w):
    person, case, number, gender = m.groups()
    words = [w["person"][person]] if person else []
    words += [w["case"][case], w["number"][number]]
    if gender:
        words.append(w["gender"][gender])
    return " ".join(words)


# Hebrew and Aramaic: the Open Scriptures Hebrew Bible codes MACULA Hebrew
# uses, one per morpheme and without the leading language letter: Ncfsa
# (common noun, feminine singular absolute), Vqw3ms (Qal wayyiqtol, 3rd
# masculine singular), R (preposition), Sp3ms (suffix "his"). The verb stems
# differ between Hebrew and Aramaic, so describe_hebrew takes the word's
# language (H or A, as in the extracts).
HEBREW_WORDS = {
    "en": {
        "pos": {"A": "Adjective", "C": "Conjunction", "D": "Adverb", "N": "Noun",
                "P": "Pronoun", "R": "Preposition", "S": "Suffix", "T": "Particle", "V": "Verb"},
        "noun": {"c": "common", "g": "gentilic (people or place)", "p": "proper name", "x": ""},
        "adjective": {"a": "", "c": "cardinal number", "g": "gentilic", "o": "ordinal number"},
        "pronoun": {"d": "demonstrative", "f": "indefinite", "i": "interrogative",
                    "p": "personal", "r": "relative"},
        "particle": {"a": "affirmation", "d": "definite article", "e": "exhortation",
                     "i": "interrogative", "j": "interjection", "m": "demonstrative",
                     "n": "negative", "o": "direct object marker", "r": "relative"},
        "suffix": {"d": "directional ending (toward)", "h": "paragogic he",
                   "n": "paragogic nun", "p": "pronoun"},
        "with_article": "with the article",
        "stem": {
            "H": {"q": "Qal", "N": "Niphal", "p": "Piel", "P": "Pual", "h": "Hiphil",
                  "H": "Hophal", "t": "Hithpael", "o": "Polel", "O": "Polal",
                  "r": "Hithpolel", "m": "Poel", "M": "Poal", "k": "Palel", "K": "Pulal",
                  "Q": "Qal passive", "l": "Pilpel", "L": "Polpal", "f": "Hithpalpel",
                  "D": "Nithpael", "j": "Pealal", "i": "Pilel", "u": "Hothpaal",
                  "c": "Tiphil", "v": "Hishtaphel", "w": "Nithpalel", "y": "Nithpoel",
                  "z": "Hithpoel"},
            "A": {"q": "Peal", "Q": "Peil", "u": "Hithpeel", "p": "Pael", "P": "Ithpaal",
                  "M": "Hithpaal", "a": "Aphel", "h": "Haphel", "s": "Saphel", "e": "Shaphel",
                  "H": "Hophal", "i": "Ithpeel", "t": "Hishtaphel", "v": "Ishtaphel",
                  "w": "Hithaphel", "o": "Polel", "z": "Ithpoel", "r": "Hithpolel",
                  "f": "Hithpalpel", "b": "Hephal", "c": "Tiphel", "m": "Poel",
                  "l": "Palpel", "L": "Ithpalpel", "O": "Ithpolel", "G": "Ittaphal"},
        },
        "conjugation": {"p": "perfect (qatal)", "q": "perfect with and (weqatal)",
                        "i": "imperfect (yiqtol)", "w": "past narrative (wayyiqtol)",
                        "h": "cohortative", "j": "jussive", "v": "imperative",
                        "r": "participle", "s": "passive participle",
                        "a": "infinitive absolute", "c": "infinitive construct"},
        "person": {"1": "1st person", "2": "2nd person", "3": "3rd person"},
        "gender": {"m": "masculine", "f": "feminine", "b": "masculine or feminine",
                   "c": "common"},
        "number": {"s": "singular", "p": "plural", "d": "dual"},
        "state": {"a": "absolute", "c": "construct (of ...)", "d": "determined"},
    },
    "es": {
        "pos": {"A": "Adjetivo", "C": "Conjunción", "D": "Adverbio", "N": "Sustantivo",
                "P": "Pronombre", "R": "Preposición", "S": "Sufijo", "T": "Partícula", "V": "Verbo"},
        "noun": {"c": "común", "g": "gentilicio (pueblo o lugar)", "p": "nombre propio", "x": ""},
        "adjective": {"a": "", "c": "número cardinal", "g": "gentilicio", "o": "número ordinal"},
        "pronoun": {"d": "demostrativo", "f": "indefinido", "i": "interrogativo",
                    "p": "personal", "r": "relativo"},
        "particle": {"a": "afirmación", "d": "artículo definido", "e": "exhortación",
                     "i": "interrogativa", "j": "interjección", "m": "demostrativa",
                     "n": "negación", "o": "marca de complemento directo", "r": "relativa"},
        "suffix": {"d": "terminación direccional (hacia)", "h": "he paragógica",
                   "n": "nun paragógica", "p": "pronominal"},
        "with_article": "con artículo",
        "stem": None,  # the stems are names, the same in every language
        "conjugation": {"p": "perfecto (qatal)", "q": "perfecto con «y» (weqatal)",
                        "i": "imperfecto (yiqtol)", "w": "narrativo pasado (wayyiqtol)",
                        "h": "cohortativo", "j": "yusivo", "v": "imperativo",
                        "r": "participio", "s": "participio pasivo",
                        "a": "infinitivo absoluto", "c": "infinitivo constructo"},
        "person": {"1": "1.ª persona", "2": "2.ª persona", "3": "3.ª persona"},
        "gender": {"m": "masculino", "f": "femenino", "b": "masculino o femenino",
                   "c": "común"},
        "number": {"s": "singular", "p": "plural", "d": "dual"},
        "state": {"a": "absoluto", "c": "constructo (de ...)", "d": "determinado"},
    },
}

_HEB_PGN = re.compile(r"([123x])([mfbcx])([spdx])")
_HEB_GNS = re.compile(r"([mfbcx])([spdx])([acd])")


def describe_hebrew(code, lang="en", language="H"):
    """Describe one MACULA Hebrew morph code. language is H or A. A
    language without its own table (a new interface language) gets English."""
    w = HEBREW_WORDS.get(lang, HEBREW_WORDS["en"])
    stems = (w["stem"] or HEBREW_WORDS["en"]["stem"])[language]
    if not code or code[0] not in w["pos"]:
        raise ValueError(f"unknown Hebrew part of speech in {code!r}")
    pos, rest = code[0], code[1:]
    out = [w["pos"][pos]]

    def pgn(s):
        m = _HEB_PGN.fullmatch(s)
        if not m:
            raise ValueError(f"unknown Hebrew person, gender or number in {code!r}")
        words = [w["person"].get(m[1], ""), w["gender"].get(m[2], ""), w["number"].get(m[3], "")]
        return " ".join(x for x in words if x)

    def gns(s):
        m = _HEB_GNS.fullmatch(s)
        if not m:
            raise ValueError(f"unknown Hebrew gender, number or state in {code!r}")
        words = [w["gender"].get(m[1], ""), w["number"].get(m[2], ""), w["state"][m[3]]]
        return " ".join(x for x in words if x)

    def table(name, key):
        if key not in w[name]:
            raise ValueError(f"unknown Hebrew {name} in {code!r}")
        return w[name][key]

    if pos == "V":
        if len(rest) < 2 or rest[0] not in stems:
            raise ValueError(f"unknown Hebrew verb stem in {code!r}")
        out.append(stems[rest[0]])
        conj = table("conjugation", rest[1])
        out.append(conj)
        tail = rest[2:]
        if rest[1] in "rs":
            out.append(gns(tail))
        elif rest[1] in "ac":
            if tail:
                raise ValueError(f"unknown Hebrew infinitive in {code!r}")
        else:
            out.append(pgn(tail))
    elif pos == "N":
        if not rest:
            raise ValueError(f"unknown Hebrew noun in {code!r}")
        kind = table("noun", rest[0])
        if kind:
            out.append(kind)
        if rest[1:]:
            out.append(gns(rest[1:]))
    elif pos == "A":
        if not rest:
            raise ValueError(f"unknown Hebrew adjective in {code!r}")
        kind = table("adjective", rest[0])
        if kind:
            out.append(kind)
        out.append(gns(rest[1:]))
    elif pos == "P":
        if rest:
            out.append(table("pronoun", rest[0]))
            if rest[1:]:
                out.append(pgn(rest[1:]))
    elif pos == "T":
        if rest:
            out.append(table("particle", rest))
    elif pos == "S":
        if not rest:
            raise ValueError(f"unknown Hebrew suffix in {code!r}")
        out.append(table("suffix", rest[0]))
        if rest[1:]:
            out.append(pgn(rest[1:]))
    elif pos == "R":
        if rest == "d":
            out.append(w["with_article"])
        elif rest:
            raise ValueError(f"unknown Hebrew preposition in {code!r}")
    elif rest:   # C, D
        raise ValueError(f"unknown Hebrew code {code!r}")
    return " · ".join(x for x in out if x)
