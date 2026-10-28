"""Plain-language descriptions of MACULA Greek and Hebrew morphology codes.

The word extracts (data/grc/) carry Robinson-style codes such as N-DSF or
V-2AAI-3S. describe() turns one into words a reader can follow, in each
reading language (English, Spanish, French, Swahili, Vietnamese, Korean,
Portuguese, Amharic): "Noun · dative singular feminine", "Verb · second aorist
active indicative · 3rd person singular". An unknown code raises ValueError, so a new code in the
data fails the tests rather than showing a reader nothing.
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
    "vi": {
        "pos": {"N": "Danh từ", "V": "Động từ", "A": "Tính từ", "T": "Mạo từ",
                "P": "Đại từ nhân xưng", "R": "Đại từ quan hệ", "D": "Đại từ chỉ định",
                "K": "Đại từ tương liên", "X": "Đại từ bất định", "I": "Đại từ nghi vấn",
                "F": "Đại từ phản thân", "C": "Đại từ hỗ tương", "S": "Đại từ sở hữu",
                "Q": "Đại từ tương liên hoặc nghi vấn",
                "ADV": "Trạng từ", "CONJ": "Liên từ", "PREP": "Giới từ", "PRT": "Tiểu từ",
                "COND": "Liên từ điều kiện", "INJ": "Thán từ",
                "HEB": "Từ Hê-bơ-rơ", "ARAM": "Từ A-ram"},
        "indeclinable": {"PRI": "tên riêng, không biến cách", "LI": "chữ cái, không biến cách",
                         "OI": "không biến cách", "NUI": "số, không biến cách"},
        "case": {"N": "chủ cách", "G": "sở hữu cách", "D": "tặng cách", "A": "đối cách", "V": "hô cách"},
        "number": {"S": "số ít", "P": "số nhiều"},
        "gender": {"M": "giống đực", "F": "giống cái", "N": "giống trung"},
        "tense": {"P": "thì hiện tại", "I": "thì quá khứ chưa hoàn thành", "F": "thì tương lai",
                  "A": "thì bất định (aorist)", "R": "thì hoàn thành", "L": "thì quá khứ hoàn thành"},
        "second": "{} thứ hai",
        "verb": "{tense}, {mood}, {voice}", "voiced": "thể {}",
        "voice": {"A": "chủ động", "M": "trung", "P": "bị động", "E": "trung hoặc bị động",
                  "D": "trung (nghĩa chủ động)", "O": "bị động (nghĩa chủ động)",
                  "N": "trung hoặc bị động (nghĩa chủ động)", "Q": "chủ động vô nhân xưng", "X": ""},
        "mood": {"I": "lối trình bày", "S": "lối giả định", "O": "lối ao ước", "M": "lối mệnh lệnh",
                 "N": "nguyên mẫu", "P": "phân từ", "R": "phân từ (mang nghĩa mệnh lệnh)"},
        "person": {"1": "ngôi thứ nhất", "2": "ngôi thứ hai", "3": "ngôi thứ ba"},
        "person_number": "{person}, {number}",
        "join": ", ",
        "suffix": {"N": "phủ định", "I": "nghi vấn", "S": "so sánh nhất", "C": "so sánh hơn",
                   "ATT": "dạng Attic", "K": "hai từ ghép làm một",
                   "P": "có tiểu từ gắn liền", "ABB": "dạng viết tắt"},
    },
    "ko": {
        "pos": {"N": "명사", "V": "동사", "A": "형용사", "T": "관사",
                "P": "인칭대명사", "R": "관계대명사", "D": "지시대명사",
                "K": "상관대명사", "X": "부정대명사", "I": "의문대명사",
                "F": "재귀대명사", "C": "상호대명사", "S": "소유대명사",
                "Q": "상관대명사 또는 의문대명사",
                "ADV": "부사", "CONJ": "접속사", "PREP": "전치사", "PRT": "불변화사",
                "COND": "조건 접속사", "INJ": "감탄사",
                "HEB": "히브리어 단어", "ARAM": "아람어 단어"},
        "indeclinable": {"PRI": "고유명사, 격변화 없음", "LI": "글자, 격변화 없음",
                         "OI": "격변화 없음", "NUI": "수사, 격변화 없음"},
        "case": {"N": "주격", "G": "속격", "D": "여격", "A": "대격", "V": "호격"},
        "number": {"S": "단수", "P": "복수"},
        "gender": {"M": "남성", "F": "여성", "N": "중성"},
        "tense": {"P": "현재", "I": "미완료", "F": "미래", "A": "부정과거",
                  "R": "완료", "L": "과거완료"},
        "second": "제2{}",
        "verb": "{tense} {voice} {mood}", "voiced": "{}",
        "voice": {"A": "능동태", "M": "중간태", "P": "수동태", "E": "중간태 또는 수동태",
                  "D": "중간태(능동의 뜻)", "O": "수동태(능동의 뜻)",
                  "N": "중간태 또는 수동태(능동의 뜻)", "Q": "비인칭 능동태", "X": ""},
        "mood": {"I": "직설법", "S": "가정법", "O": "희구법", "M": "명령법",
                 "N": "부정사", "P": "분사", "R": "분사(명령의 뜻)"},
        "person": {"1": "1인칭", "2": "2인칭", "3": "3인칭"},
        "suffix": {"N": "부정", "I": "의문", "S": "최상급", "C": "비교급",
                   "ATT": "앗티카 형태", "K": "두 단어가 한 단어로 합쳐진 형태",
                   "P": "불변화사가 붙은 형태", "ABB": "줄임 형태"},
    },
    "pt": {
        "pos": {"N": "Substantivo", "V": "Verbo", "A": "Adjetivo", "T": "Artigo",
                "P": "Pronome pessoal", "R": "Pronome relativo", "D": "Pronome demonstrativo",
                "K": "Pronome correlativo", "X": "Pronome indefinido", "I": "Pronome interrogativo",
                "F": "Pronome reflexivo", "C": "Pronome recíproco", "S": "Pronome possessivo",
                "Q": "Pronome correlativo ou interrogativo",
                "ADV": "Advérbio", "CONJ": "Conjunção", "PREP": "Preposição", "PRT": "Partícula",
                "COND": "Conjunção condicional", "INJ": "Interjeição",
                "HEB": "Palavra hebraica", "ARAM": "Palavra aramaica"},
        "indeclinable": {"PRI": "nome próprio, indeclinável", "LI": "letra, indeclinável",
                         "OI": "indeclinável", "NUI": "número, indeclinável"},
        "case": {"N": "nominativo", "G": "genitivo", "D": "dativo", "A": "acusativo", "V": "vocativo"},
        "number": {"S": "singular", "P": "plural"},
        "gender": {"M": "masculino", "F": "feminino", "N": "neutro"},
        "tense": {"P": "presente", "I": "imperfeito", "F": "futuro", "A": "aoristo",
                  "R": "perfeito", "L": "mais-que-perfeito"},
        "second": "{} segundo",
        "verb": "{mood} {tense}, {voice}", "voiced": "voz {}",
        "voice": {"A": "ativa", "M": "média", "P": "passiva", "E": "média ou passiva",
                  "D": "média (depoente)", "O": "passiva (depoente)",
                  "N": "média ou passiva (depoente)", "Q": "ativa impessoal", "X": ""},
        "mood": {"I": "indicativo", "S": "subjuntivo", "O": "optativo", "M": "imperativo",
                 "N": "infinitivo", "P": "particípio", "R": "particípio (como ordem)"},
        "person": {"1": "1.ª pessoa", "2": "2.ª pessoa", "3": "3.ª pessoa"},
        "suffix": {"N": "negação", "I": "interrogativo", "S": "superlativo", "C": "comparativo",
                   "ATT": "forma ática", "K": "crase (duas palavras unidas)",
                   "P": "com partícula unida", "ABB": "forma abreviada"},
    },
    "am": {
        "pos": {"N": "ስም", "V": "ግስ", "A": "ቅጽል", "T": "መወሰኛ",
                "P": "ግላዊ ተውላጠ ስም", "R": "አያያዥ ተውላጠ ስም", "D": "አመልካች ተውላጠ ስም",
                "K": "ተዛማጅ ተውላጠ ስም", "X": "ያልተወሰነ ተውላጠ ስም", "I": "ጠያቂ ተውላጠ ስም",
                "F": "ተመላሽ ተውላጠ ስም", "C": "የእርስ በርስ ተውላጠ ስም", "S": "የባለቤትነት ተውላጠ ስም",
                "Q": "ተዛማጅ ወይም ጠያቂ ተውላጠ ስም",
                "ADV": "ተውሳከ ግስ", "CONJ": "መስተጻምር", "PREP": "መስተዋድድ", "PRT": "ቅንጣት",
                "COND": "የሁኔታ መስተጻምር", "INJ": "ቃለ አጋኖ",
                "HEB": "የዕብራይስጥ ቃል", "ARAM": "የአራማይስጥ ቃል"},
        "indeclinable": {"PRI": "የተጸውዖ ስም፣ የማይለወጥ", "LI": "ፊደል፣ የማይለወጥ",
                         "OI": "የማይለወጥ", "NUI": "ቁጥር፣ የማይለወጥ"},
        "case": {"N": "ባለቤት", "G": "የባለቤትነት", "D": "ተቀባይ", "A": "ተሳቢ", "V": "ጥሪ"},
        "number": {"S": "ነጠላ", "P": "ብዙ"},
        "gender": {"M": "ወንድ", "F": "ሴት", "N": "ገለልተኛ"},
        "tense": {"P": "የአሁን ጊዜ", "I": "ያልተጠናቀቀ ኃላፊ ጊዜ", "F": "የወደፊት ጊዜ",
                  "A": "ቀላል ኃላፊ ጊዜ", "R": "ፍጹም ጊዜ", "L": "ኃላፊ ፍጹም ጊዜ"},
        "second": "ሁለተኛ {}",
        # The voice comes last and may be empty (X), so its separator travels
        # with it: an Ethiopic comma is not stripped like a trailing ", ".
        "verb": "{tense}፣ {mood}{voice}", "voiced": "፣ {}",
        "voice": {"A": "ገቢር", "M": "መካከለኛ", "P": "ተገብሮ", "E": "መካከለኛ ወይም ተገብሮ",
                  "D": "መካከለኛ (የገቢር ትርጉም)", "O": "ተገብሮ (የገቢር ትርጉም)",
                  "N": "መካከለኛ ወይም ተገብሮ (የገቢር ትርጉም)", "Q": "ባለቤት የሌለው ገቢር", "X": ""},
        "mood": {"I": "አመልካች ዘይቤ", "S": "ሁኔታዊ ዘይቤ", "O": "የምኞት ዘይቤ", "M": "የትእዛዝ ዘይቤ",
                 "N": "የግስ ስም", "P": "ቅጽላዊ ግስ", "R": "ቅጽላዊ ግስ (በትእዛዝ ትርጉም)"},
        "person": {"1": "አንደኛ መደብ", "2": "ሁለተኛ መደብ", "3": "ሦስተኛ መደብ"},
        "person_number": "{person}፣ {number}",
        "join": "፣ ",
        "suffix": {"N": "አሉታ", "I": "ጠያቂ", "S": "ከሁሉ የበለጠ", "C": "የንጽጽር",
                   "ATT": "የአቲካ ቅርጽ", "K": "ሁለት ቃላት ተዋሕደው አንድ የሆኑበት",
                   "P": "ቅንጣት የተያያዘበት", "ABB": "ያጠረ ቅርጽ"},
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
        # An infinitive has no person or case, so its tail may be only a
        # suffix: V-RAN-ATT (Luke 24:46), an Attic perfect infinitive.
        if tail and tail[0] not in w["suffix"]:
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
    "vi": {
        "pos": {"A": "Tính từ", "C": "Liên từ", "D": "Trạng từ", "N": "Danh từ",
                "P": "Đại từ", "R": "Giới từ", "S": "Hậu tố", "T": "Tiểu từ", "V": "Động từ"},
        "noun": {"c": "chung", "g": "chỉ dân tộc hoặc nơi chốn", "p": "tên riêng", "x": ""},
        "adjective": {"a": "", "c": "số đếm", "g": "chỉ dân tộc", "o": "số thứ tự"},
        "pronoun": {"d": "chỉ định", "f": "bất định", "i": "nghi vấn",
                    "p": "nhân xưng", "r": "quan hệ"},
        "particle": {"a": "khẳng định", "d": "mạo từ xác định", "e": "khích lệ",
                     "i": "nghi vấn", "j": "thán từ", "m": "chỉ định",
                     "n": "phủ định", "o": "dấu tân ngữ trực tiếp", "r": "quan hệ"},
        "suffix": {"d": "đuôi chỉ hướng (về phía)", "h": "he thêm vào",
                   "n": "nun thêm vào", "p": "đại từ"},
        "with_article": "có mạo từ",
        "stem": None,  # the stems are names, the same in every language
        "conjugation": {"p": "hoàn thành (qatal)", "q": "hoàn thành với \u201cvà\u201d (weqatal)",
                        "i": "chưa hoàn thành (yiqtol)", "w": "tường thuật quá khứ (wayyiqtol)",
                        "h": "khích lệ", "j": "mệnh lệnh gián tiếp", "v": "mệnh lệnh",
                        "r": "phân từ", "s": "phân từ bị động",
                        "a": "nguyên mẫu tuyệt đối", "c": "nguyên mẫu kết cấu"},
        "person": {"1": "ngôi thứ nhất", "2": "ngôi thứ hai", "3": "ngôi thứ ba"},
        "gender": {"m": "giống đực", "f": "giống cái", "b": "giống đực hoặc giống cái",
                   "c": "giống chung"},
        "number": {"s": "số ít", "p": "số nhiều", "d": "số đôi"},
        "state": {"a": "tuyệt đối", "c": "kết cấu (của ...)", "d": "xác định"},
    },
    "ko": {
        "pos": {"A": "형용사", "C": "접속사", "D": "부사", "N": "명사",
                "P": "대명사", "R": "전치사", "S": "접미사", "T": "불변화사", "V": "동사"},
        "noun": {"c": "보통명사", "g": "민족이나 지역을 나타내는 말", "p": "고유명사", "x": ""},
        "adjective": {"a": "", "c": "기수", "g": "민족을 나타내는 말", "o": "서수"},
        "pronoun": {"d": "지시", "f": "부정", "i": "의문", "p": "인칭", "r": "관계"},
        "particle": {"a": "긍정", "d": "정관사", "e": "권유",
                     "i": "의문", "j": "감탄", "m": "지시",
                     "n": "부정", "o": "직접 목적어 표지", "r": "관계"},
        "suffix": {"d": "방향 어미(~쪽으로)", "h": "덧붙은 헤", "n": "덧붙은 눈", "p": "대명사"},
        "with_article": "관사가 붙음",
        "stem": None,  # the stems are names, the same in every language
        "conjugation": {"p": "완료형 (카탈)", "q": "\u201c그리고\u201d가 붙은 완료형 (워카탈)",
                        "i": "미완료형 (이크톨)", "w": "과거 서술형 (와이이크톨)",
                        "h": "권유형", "j": "지시형", "v": "명령형",
                        "r": "분사", "s": "수동 분사",
                        "a": "독립 부정사", "c": "연계 부정사"},
        "person": {"1": "1인칭", "2": "2인칭", "3": "3인칭"},
        "gender": {"m": "남성", "f": "여성", "b": "남성 또는 여성", "c": "통성"},
        "number": {"s": "단수", "p": "복수", "d": "쌍수"},
        "state": {"a": "절대형", "c": "연계형 (~의)", "d": "한정형"},
    },
    "pt": {
        "pos": {"A": "Adjetivo", "C": "Conjunção", "D": "Advérbio", "N": "Substantivo",
                "P": "Pronome", "R": "Preposição", "S": "Sufixo", "T": "Partícula", "V": "Verbo"},
        "noun": {"c": "comum", "g": "gentílico (povo ou lugar)", "p": "nome próprio", "x": ""},
        "adjective": {"a": "", "c": "número cardinal", "g": "gentílico", "o": "número ordinal"},
        "pronoun": {"d": "demonstrativo", "f": "indefinido", "i": "interrogativo",
                    "p": "pessoal", "r": "relativo"},
        "particle": {"a": "afirmação", "d": "artigo definido", "e": "exortação",
                     "i": "interrogativa", "j": "interjeição", "m": "demonstrativa",
                     "n": "negação", "o": "marca de objeto direto", "r": "relativa"},
        "suffix": {"d": "terminação direcional (para)", "h": "he paragógico",
                   "n": "nun paragógico", "p": "pronominal"},
        "with_article": "com artigo",
        "stem": None,  # the stems are names, the same in every language
        "conjugation": {"p": "perfeito (qatal)", "q": "perfeito com \u201ce\u201d (weqatal)",
                        "i": "imperfeito (yiqtol)", "w": "narrativo passado (wayyiqtol)",
                        "h": "coortativo", "j": "jussivo", "v": "imperativo",
                        "r": "particípio", "s": "particípio passivo",
                        "a": "infinitivo absoluto", "c": "infinitivo construto"},
        "person": {"1": "1.ª pessoa", "2": "2.ª pessoa", "3": "3.ª pessoa"},
        "gender": {"m": "masculino", "f": "feminino", "b": "masculino ou feminino",
                   "c": "comum"},
        "number": {"s": "singular", "p": "plural", "d": "dual"},
        "state": {"a": "absoluto", "c": "construto (de ...)", "d": "determinado"},
    },
    "am": {
        "pos": {"A": "ቅጽል", "C": "መስተጻምር", "D": "ተውሳከ ግስ", "N": "ስም",
                "P": "ተውላጠ ስም", "R": "መስተዋድድ", "S": "ቅጥያ", "T": "ቅንጣት", "V": "ግስ"},
        "noun": {"c": "የወል ስም", "g": "የሕዝብ ወይም የቦታ መጠሪያ", "p": "የተጸውዖ ስም", "x": ""},
        "adjective": {"a": "", "c": "መደበኛ ቁጥር", "g": "የሕዝብ መጠሪያ", "o": "ተራ ቁጥር"},
        "pronoun": {"d": "አመልካች", "f": "ያልተወሰነ", "i": "ጠያቂ", "p": "ግላዊ", "r": "አያያዥ"},
        "particle": {"a": "ማረጋገጫ", "d": "መወሰኛ", "e": "ማበረታቻ",
                     "i": "ጠያቂ", "j": "ቃለ አጋኖ", "m": "አመልካች",
                     "n": "አሉታ", "o": "የቀጥታ ተሳቢ ምልክት", "r": "አያያዥ"},
        "suffix": {"d": "አቅጣጫ አመልካች መድረሻ (ወደ)", "h": "ተጨማሪ ሄ", "n": "ተጨማሪ ኑን", "p": "ተውላጠ ስም"},
        "with_article": "ከመወሰኛ ጋር",
        "stem": None,  # the stems are names, the same in every language
        "conjugation": {"p": "ፍጹም (ቃጣል)", "q": "«እና» የተጨመረበት ፍጹም (ወቃጣል)",
                        "i": "ያልተጠናቀቀ (ይቅጦል)", "w": "የኃላፊ ትረካ (ወይይቅጦል)",
                        "h": "የራስ ምኞት", "j": "የሦስተኛ መደብ ትእዛዝ", "v": "ትእዛዝ",
                        "r": "ቅጽላዊ ግስ", "s": "ተገብሮ ቅጽላዊ ግስ",
                        "a": "ፍጹም የግስ ስም", "c": "ጥገኛ የግስ ስም"},
        "person": {"1": "አንደኛ መደብ", "2": "ሁለተኛ መደብ", "3": "ሦስተኛ መደብ"},
        "gender": {"m": "ወንድ", "f": "ሴት", "b": "ወንድ ወይም ሴት", "c": "የጋራ"},
        "number": {"s": "ነጠላ", "p": "ብዙ", "d": "ጥንድ"},
        "state": {"a": "ነጻ", "c": "ጥገኛ (የ...)", "d": "የተወሰነ"},
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
