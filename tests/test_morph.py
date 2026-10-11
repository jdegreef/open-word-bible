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
            # As MACULA codes one word at John 8:10, with no person and a stray hyphen.
            "P-GS-": "Personal pronoun · genitive singular",
        }
        for code, words in cases.items():
            self.assertEqual(morph.describe(code), words, code)
        self.assertEqual(morph.describe("V-IAI-3S", "es"),
                         "Verbo · indicativo imperfecto, voz activa · 3.ª persona singular")
        self.assertEqual(morph.describe("V-IAI-3S", "fr"),
                         "Verbe · indicatif imparfait, voix active · 3e personne du singulier")
        self.assertEqual(morph.describe("V-2AAI-3S", "fr"),
                         "Verbe · indicatif aoriste second, voix active · 3e personne du singulier")

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
                for lang in ("es", "fr"):
                    self.assertEqual(data["grammar"][w["morph"]][lang], morph.describe(w["morph"], lang))


if __name__ == "__main__":
    unittest.main()
