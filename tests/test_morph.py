"""Plain-language grammar for the Greek morphology codes (owb/morph.py)."""
import json
import re
import sys
import unittest
from pathlib import Path

from owb import morph

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


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
            # Codes not in today's passages, so the next ones do not break the build.
            "N-PRI": "Noun · proper name, indeclinable",
            "A-NUI": "Adjective · number, indeclinable",
            "HEB": "Hebrew word",
            "S-1SNSM": "Possessive pronoun · 1st person singular · nominative singular masculine",
            "P-1NS-K": "Personal pronoun · 1st person nominative singular · crasis (two words run together)",
        }
        for code, words in cases.items():
            self.assertEqual(morph.describe(code), words, code)
        self.assertEqual(morph.describe("V-IAI-3S", "es"),
                         "Verbo · indicativo imperfecto, voz activa · 3.ª persona singular")

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
        # Aramaic stems share letters with Hebrew ones but not names.
        self.assertEqual(morph.describe_hebrew("Vai3ms", "en", "A"),
                         "Verb · Aphel · imperfect (yiqtol) · 3rd person masculine singular")
        for code in ("Xq", "Vxw3ms", "Vqz3ms", "Nq", "Rz", "Vqc3ms"):
            with self.assertRaises(ValueError, msg=code):
                morph.describe_hebrew(code)

    def test_hebrew_reader_data_carries_the_grammar(self):
        page = build_site.chapter_page("GEN", 1)
        data = json.loads(re.search(r'id="owb-data">(.*?)</script>', page, re.S)[1])
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
        page = build_site.chapter_page("JHN", 1)
        data = json.loads(re.search(r'id="owb-data">(.*?)</script>', page, re.S)[1])
        for words in data["words"].values():
            for w in words:
                self.assertEqual(data["grammar"][w["morph"]]["en"], morph.describe(w["morph"]))
                self.assertEqual(data["grammar"][w["morph"]]["es"], morph.describe(w["morph"], "es"))


if __name__ == "__main__":
    unittest.main()
