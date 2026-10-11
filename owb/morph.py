"""Plain-language descriptions of MACULA Greek morphology codes.

The word extracts (data/grc/) carry Robinson-style codes such as N-DSF or
V-2AAI-3S. describe() turns one into words a reader can follow, in English,
Spanish, French or Swahili: "Noun · dative singular feminine", "Verb ·
second aorist active indicative · 3rd person singular". An unknown code raises ValueError, so a
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
    "fr": {
        "pos": {"N": "Nom", "V": "Verbe", "A": "Adjectif", "T": "Article",
                "P": "Pronom personnel", "R": "Pronom relatif", "D": "Pronom démonstratif",
                "K": "Pronom corrélatif", "X": "Pronom indéfini", "I": "Pronom interrogatif",
                "F": "Pronom réfléchi", "C": "Pronom réciproque", "S": "Pronom possessif",
                "Q": "Pronom corrélatif ou interrogatif",
                "ADV": "Adverbe", "CONJ": "Conjonction", "PREP": "Préposition", "PRT": "Particule",
                "COND": "Conjonction conditionnelle", "INJ": "Interjection",
                "HEB": "Mot hébreu", "ARAM": "Mot araméen"},
        "indeclinable": {"PRI": "nom propre, indéclinable", "LI": "lettre, indéclinable",
                         "OI": "indéclinable", "NUI": "nombre, indéclinable"},
        "case": {"N": "nominatif", "G": "génitif", "D": "datif", "A": "accusatif", "V": "vocatif"},
        "number": {"S": "singulier", "P": "pluriel"},
        "gender": {"M": "masculin", "F": "féminin", "N": "neutre"},
        "tense": {"P": "présent", "I": "imparfait", "F": "futur", "A": "aoriste",
                  "R": "parfait", "L": "plus-que-parfait"},
        "second": "{} second",
        "verb": "{mood} {tense}, {voice}", "voiced": "voix {}",
        "voice": {"A": "active", "M": "moyenne", "P": "passive", "E": "moyenne ou passive",
                  "D": "moyenne (déponent)", "O": "passive (déponent)",
                  "N": "moyenne ou passive (déponent)", "Q": "active impersonnelle", "X": ""},
        "mood": {"I": "indicatif", "S": "subjonctif", "O": "optatif", "M": "impératif",
                 "N": "infinitif", "P": "participe", "R": "participe (valeur d’impératif)"},
        "person": {"1": "1re personne", "2": "2e personne", "3": "3e personne"},
        "person_number": "{person} du {number}",
        "suffix": {"N": "négation", "I": "interrogatif", "S": "superlatif", "C": "comparatif",
                   "ATT": "forme attique", "K": "crase (deux mots fondus en un)",
                   "P": "avec particule attachée", "ABB": "forme abrégée"},
    },
    "sw": {
        "pos": {"N": "Nomino", "V": "Kitenzi", "A": "Kivumishi", "T": "Kibainishi",
                "P": "Kiwakilishi cha nafsi", "R": "Kiwakilishi rejeshi", "D": "Kiwakilishi kioneshi",
                "K": "Kiwakilishi kiambatani", "X": "Kiwakilishi kisichodhahiri", "I": "Kiwakilishi kiulizi",
                "F": "Kiwakilishi cha kujirejea", "C": "Kiwakilishi cha kutendana", "S": "Kiwakilishi kimilikishi",
                "Q": "Kiwakilishi kiambatani au kiulizi",
                "ADV": "Kielezi", "CONJ": "Kiunganishi", "PREP": "Kihusishi", "PRT": "Kijineno",
                "COND": "Kiunganishi cha sharti", "INJ": "Kiingizi",
                "HEB": "Neno la Kiebrania", "ARAM": "Neno la Kiaramu"},
        "indeclinable": {"PRI": "jina la pekee, halibadiliki", "LI": "herufi, haibadiliki",
                         "OI": "halibadiliki", "NUI": "namba, haibadiliki"},
        "case": {"N": "kiima (nominativi)", "G": "milikishi (jenitivi)", "D": "kipokezi (dativi)",
                 "A": "yambwa (akusativi)", "V": "mwito (vokativi)"},
        "number": {"S": "umoja", "P": "wingi"},
        "gender": {"M": "kiume", "F": "kike", "N": "si kiume wala kike"},
        "tense": {"P": "wakati uliopo", "I": "wakati uliopita endelevu", "F": "wakati ujao",
                  "A": "aoristi", "R": "timilifu", "L": "timilifu ya zamani"},
        "second": "{} ya pili",
        "verb": "{tense}, {mood}, {voice}", "voiced": "kauli {}",
        "voice": {"A": "tendaji", "M": "ya kati", "P": "tendwa", "E": "ya kati au tendwa",
                  "D": "ya kati (maana tendaji)", "O": "tendwa (maana tendaji)",
                  "N": "ya kati au tendwa (maana tendaji)", "Q": "tendaji isiyo na mtenda", "X": ""},
        "mood": {"I": "hali elekezi", "S": "hali tegemezi", "O": "hali ya matamanio", "M": "hali ya amri",
                 "N": "kitenzi-jina", "P": "kitenzi-kivumishi",
                 "R": "kitenzi-kivumishi (kama amri)"},
        "person": {"1": "nafsi ya kwanza", "2": "nafsi ya pili", "3": "nafsi ya tatu"},
        "person_number": "{person}, {number}",
        "join": ", ",
        "suffix": {"N": "kanushi", "I": "kiulizi", "S": "kupita yote", "C": "kulinganisha",
                   "ATT": "umbo la Kiatiki", "K": "maneno mawili yaliyounganishwa",
                   "P": "pamoja na kijineno kilichoambatishwa", "ABB": "umbo lililofupishwa"},
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
    # MACULA's text of John 7:53-8:11 has one stray trailing hyphen ("P-GS-"
    # at 8:10); an empty last part says nothing, so drop it.
    parts = code.removesuffix("-").split("-")
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
                out.append(w.get("person_number", "{person} {number}").format(
                    person=w["person"][pn[1]], number=w["number"][pn[2]]))
            else:
                raise ValueError(f"unknown verb ending in {code!r}")
        rest = tail
    elif rest and rest[0] in w["indeclinable"]:
        out.append(w["indeclinable"][rest[0]])
        rest = rest[1:]
    elif pos == "S" and rest and _POSS.fullmatch(rest[0]):
        m = _POSS.fullmatch(rest[0])
        join = w.get("join", " ")
        out.append(join.join([w["person"][m[1]], w["number"][m[2]]]) + " \u00b7 "
                   + join.join([w["case"][m[3]], w["number"][m[4]], w["gender"][m[5]]]))
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
    return w.get("join", " ").join(words)
