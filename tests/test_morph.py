"""Plain-language grammar for the Greek morphology codes (owb/morph.py)."""
import json
import sys
import unittest
from pathlib import Path

from owb import morph

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from tests.site_build import page_data  # noqa: E402


class MorphTest(unittest.TestCase):
    def test_every_code_in_the_extracts_is_described_in_every_language(self):
        codes = {w["morph"] for path in (ROOT / "data" / "grc").glob("*.json")
                 for words in json.loads(path.read_text(encoding="utf-8"))["verses"].values()
                 for w in words}
        self.assertTrue(codes)
        for code in sorted(codes):
            for lang in morph.WORDS:
                self.assertTrue(morph.describe(code, lang), (code, lang))

    def test_descriptions(self):
        cases = {
            "N-DSF": "Noun · dative singular feminine",
            "V-IAI-3S": "Verb · imperfect active indicative · 3rd person singular",
            "V-2AAI-3S": "Verb · second aorist active indicative · 3rd person singular",
            "V-PAP-NSM": "Verb · present active participle · nominative singular masculine",
            "V-2ADN": "Verb · second aorist middle (deponent) infinitive",
            "P-1DS": "Personal pronoun · 1st person dative singular",
            "PRT-N": "Particle · negative",
            "V-RAI-3S-ATT": "Verb · perfect active indicative · 3rd person singular · Attic form",
            "V-RAN-ATT": "Verb · perfect active infinitive · Attic form",
            # Codes not in today's passages, so the next ones do not break the build.
            "N-PRI": "Noun · proper name, indeclinable",
            "A-NUI": "Adjective · number, indeclinable",
            "HEB": "Hebrew word",
            "S-1SNSM": "Possessive pronoun · 1st person singular · nominative singular masculine",
            "P-1NS-K": "Personal pronoun · 1st person nominative singular · crasis (two words run together)",
            # As MACULA codes one word at John 8:10, with no person and a stray hyphen.
            "P-GS-": "Personal pronoun · genitive singular",
            "P-GP-": "Personal pronoun · genitive plural",
        }
        for code, words in cases.items():
            self.assertEqual(morph.describe(code), words, code)
        self.assertEqual(morph.describe("V-IAI-3S", "es"),
                         "Verbo · indicativo imperfecto, voz activa · 3.ª persona singular")
        self.assertEqual(morph.describe("V-IAI-3S", "fr"),
                         "Verbe · indicatif imparfait, voix active · 3e personne du singulier")
        self.assertEqual(morph.describe("V-2AAI-3S", "fr"),
                         "Verbe · indicatif aoriste second, voix active · 3e personne du singulier")
        self.assertEqual(morph.describe("V-IAI-3S", "sw"),
                         "Kitenzi · wakati uliopita endelevu, hali elekezi, kauli tendaji · nafsi ya tatu, umoja")
        self.assertEqual(morph.describe("N-DSF", "sw"), "Nomino · kipokezi (dativi), umoja, kike")
        self.assertEqual(morph.describe("V-IAI-3S", "vi"),
                         "Động từ · thì quá khứ chưa hoàn thành, lối trình bày, thể chủ động · ngôi thứ ba, số ít")
        self.assertEqual(morph.describe("N-DSF", "vi"), "Danh từ · tặng cách, số ít, giống cái")
        self.assertEqual(morph.describe("V-2AAI-3S", "ko"), "동사 · 제2부정과거 능동태 직설법 · 3인칭 단수")
        self.assertEqual(morph.describe("N-DSF", "ko"), "명사 · 여격 단수 여성")
        self.assertEqual(morph.describe("V-2AAI-3S", "pt"),
                         "Verbo · indicativo aoristo segundo, voz ativa · 3.ª pessoa singular")
        self.assertEqual(morph.describe("N-DSF", "pt"), "Substantivo · dativo singular feminino")
        self.assertEqual(morph.describe("V-IAI-3S", "am"),
                         "ግስ · ያልተጠናቀቀ ኃላፊ ጊዜ፣ አመልካች ዘይቤ፣ ገቢር · ሦስተኛ መደብ፣ ነጠላ")
        self.assertEqual(morph.describe("V-2AAI-3S", "am"),
                         "ግስ · ሁለተኛ ቀላል ኃላፊ ጊዜ፣ አመልካች ዘይቤ፣ ገቢር · ሦስተኛ መደብ፣ ነጠላ")
        self.assertEqual(morph.describe("N-DSF", "am"), "ስም · ተቀባይ፣ ነጠላ፣ ሴት")
        # A verb with no voice (X) leaves no stray Ethiopic comma.
        self.assertFalse(morph.describe("V-PXI-3S", "am").split(" · ")[1].endswith("፣"))
        self.assertEqual(morph.describe("V-2AAI-3S", "hi"),
                         "क्रिया · द्वितीय एओरिस्ट (सामान्य भूत), निश्चयार्थ, कर्तृवाच्य · अन्य पुरुष, एकवचन")
        self.assertEqual(morph.describe("N-DSF", "hi"), "संज्ञा · संप्रदान कारक, एकवचन, स्त्रीलिंग")
        self.assertEqual(morph.describe("V-PXI-3S", "hi"), "क्रिया · वर्तमान, निश्चयार्थ · अन्य पुरुष, एकवचन")
        self.assertEqual(morph.describe("V-2AAI-3S", "ru"),
                         "Глагол · второй аорист, изъявительное наклонение, действительный залог"
                         " · 3-е лицо, единственное число")
        self.assertEqual(morph.describe("N-DSF", "ru"),
                         "Существительное · дательный, единственное число, женский род")
        self.assertEqual(morph.describe("V-2AAI-3S", "uk"),
                         "Дієслово · другий аорист, дійсний спосіб, активний стан · 3-тя особа, однина")
        self.assertEqual(morph.describe("N-DSF", "uk"), "Іменник · давальний, однина, жіночий рід")
        self.assertEqual(morph.describe("V-2AAI-3S", "ja"), "動詞 · 第二アオリスト、直説法、能動態 · 三人称単数")
        self.assertEqual(morph.describe("N-DSF", "ja"), "名詞 · 与格、単数、女性")

    def test_every_hebrew_code_in_the_extracts_is_described(self):
        words = [w for path in (ROOT / "data" / "hbo").glob("*.json")
                 for ws in json.loads(path.read_text(encoding="utf-8"))["verses"].values()
                 for w in ws]
        self.assertTrue(words)
        for w in words:
            for lang in morph.HEBREW_WORDS:
                self.assertTrue(morph.describe_hebrew(w["morph"], lang, w["lang"]), w["morph"])

    def test_hebrew_descriptions(self):
        cases = {
            "Vqw3ms": "Verb · Qal · past narrative (wayyiqtol) · 3rd person masculine singular",
            "Vqp3ms": "Verb · Qal · perfect (qatal) · 3rd person masculine singular",
            "VNrmsa": "Verb · Niphal · participle · masculine singular absolute",
            "Vqc": "Verb · Qal · infinitive construct",
            "Ncfsa": "Noun · common · feminine singular absolute",
            "Np": "Noun · proper name",
            "Aomsa": "Adjective · ordinal number · masculine singular absolute",
            "Rd": "Preposition · with the article",
            "Sp3ms": "Suffix · pronoun · 3rd person masculine singular",
            "To": "Particle · direct object marker",
            "Pdxms": "Pronoun · demonstrative · masculine singular",
            "C": "Conjunction",
        }
        for code, words in cases.items():
            self.assertEqual(morph.describe_hebrew(code), words, code)
        self.assertEqual(morph.describe_hebrew("Vqw3ms", "es"),
                         "Verbo · Qal · narrativo pasado (wayyiqtol) · 3.ª persona masculino singular")
        self.assertEqual(morph.describe_hebrew("Vqw3ms", "am"),
                         "ግስ · Qal · የኃላፊ ትረካ (ወይይቅጦል) · ሦስተኛ መደብ ወንድ ነጠላ")
        self.assertEqual(morph.describe_hebrew("Vqw3ms", "hi"),
                         "क्रिया · Qal · भूतकाल का वर्णन (वय्यिक़्तोल) · अन्य पुरुष पुल्लिंग एकवचन")
        self.assertEqual(morph.describe_hebrew("Vqw3ms", "ru"),
                         "Глагол · Qal · повествовательное прошедшее (ваййиктол)"
                         " · 3-е лицо мужской род единственное число")
        self.assertEqual(morph.describe_hebrew("Vqw3ms", "uk"),
                         "Дієслово · Qal · розповідний минулий (ваййіктол)"
                         " · 3-тя особа чоловічий рід однина")
        self.assertEqual(morph.describe_hebrew("Vqw3ms", "ja"),
                         "動詞 · Qal · 物語の過去（ワイイクトル） · 三人称 男性 単数")
        # Aramaic stems share letters with Hebrew ones but not names.
        self.assertEqual(morph.describe_hebrew("Vai3ms", "en", "A"),
                         "Verb · Aphel · imperfect (yiqtol) · 3rd person masculine singular")
        for code in ("Xq", "Vxw3ms", "Vqz3ms", "Nq", "Rz", "Vqc3ms"):
            with self.assertRaises(ValueError, msg=code):
                morph.describe_hebrew(code)

    def test_hebrew_reader_data_carries_the_grammar(self):
        data = page_data(build_site.chapter_page("GEN", 1))
        self.assertEqual(data["source"], "hbo")
        for words in data["words"].values():
            for w in words:
                self.assertEqual(data["grammar"][w["morph"]]["en"],
                                 morph.describe_hebrew(w["morph"], "en", w["lang"]))

    def test_unknown_codes_fail_loudly(self):
        for code in ("Z-NSM", "V-ZAI-3S", "N-QSM", "PREP-Z"):
            with self.assertRaises(ValueError, msg=code):
                morph.describe(code)

    def test_reader_data_carries_the_grammar(self):
        # Each page carries the grammar in its own language only.
        for lang in build_site.LANGUAGES:
            data = page_data(build_site.chapter_page("JHN", 1, lang))
            for words in data["words"].values():
                for w in words:
                    self.assertEqual(data["grammar"][w["morph"]], {lang: morph.describe(w["morph"], lang)})


if __name__ == "__main__":
    unittest.main()
