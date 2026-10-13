"""Transliteration of the source words (owb/translit.py), checked against
words picked from the source data by verse and position: Greek and Hebrew
are never typed in this project."""
import json
import sys
import unittest
from pathlib import Path

from owb import translit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_site  # noqa: E402


def verse(source, ref):
    book, chapter, _ = ref.split(".")
    return json.loads((ROOT / "data" / source / f"{book}.{chapter}.json").read_text(encoding="utf-8"))["verses"][ref]


class GreekTest(unittest.TestCase):
    def latin(self, ref):
        return [translit.greek(w["text"]) for w in verse("grc", ref)]

    def test_john_1_1(self):
        self.assertEqual(" ".join(self.latin("JHN.1.1")),
                         "En archē ēn ho logos kai ho logos ēn pros ton theon kai theos ēn ho logos")

    def test_rough_breathing_on_a_diphthong(self):
        self.assertEqual(self.latin("JHN.1.2")[0], "houtos")

    def test_capitals_and_long_vowels(self):
        words = self.latin("JHN.1.6")
        self.assertEqual(words[0], "Egeneto")
        self.assertEqual(words[-1], "Iōannēs")
        self.assertIn("Iēsoun", self.latin("JHN.1.29"))

    def test_upsilon_in_a_diphthong_and_nasal_gamma(self):
        self.assertIn("autou", self.latin("JHN.1.3"))
        # "angelos": gamma before gamma is n (Mark 1:2).
        self.assertIn("angelon", self.latin("MRK.1.2"))


class HebrewTest(unittest.TestCase):
    def latin(self, ref):
        words = verse("hbo", ref)
        out = translit.hebrew_words(words)
        return [out[w["id"]] for w in words]

    def test_genesis_1_1(self):
        self.assertEqual(" ".join(self.latin("GEN.1.1")), "be reshit bara elohim et ha shamayim ve et ha arets")

    def test_furtive_patah_and_spirants(self):
        words = self.latin("GEN.1.2")
        self.assertIn("ruah", words)          # patah said before a final het
        self.assertIn("hoshekh", words)       # kaf without dagesh
        self.assertIn("merahefet", words)     # pe without dagesh

    def test_dagesh_forte_doubles_within_a_morpheme(self):
        # "dry land" (Genesis 1:9); a prefix is written apart, so the letter
        # after it is not doubled ("va yomer", not "vayyomer").
        self.assertIn("yabbashah", self.latin("GEN.1.9"))
        self.assertEqual(self.latin("GEN.1.3")[:2], ["va", "yomer"])

    def test_divine_name_and_suffixes(self):
        # "YHWH roi": the name as its consonants, and the suffix yod of
        # "my shepherd" silent after the hiriq it lengthens.
        self.assertEqual(self.latin("PSA.23.1"), ["mizmor", "le", "david", "YHWH", "roi", "", "lo", "ehsar"])

    def test_every_hebrew_word_has_letters_or_is_a_silent_suffix(self):
        for path in sorted((ROOT / "data" / "hbo").glob("GEN.*.json")):
            for ref, words in json.loads(path.read_text(encoding="utf-8"))["verses"].items():
                out = translit.hebrew_words(words)
                for w in words:
                    self.assertTrue(out[w["id"]].isascii() or "YHWH" in out[w["id"]], (ref, out[w["id"]]))


class PageDataTest(unittest.TestCase):
    def test_the_reader_gets_one_transliteration_per_word(self):
        for source, ref in (("grc", "JHN.1.1"), ("hbo", "GEN.1.1")):
            words = build_site.transliterated(verse(source, ref), source)
            self.assertTrue(all(w["translit"] for w in words), ref)
            # MACULA's own column (Hebrew only, with gaps) is not sent.
            self.assertFalse(any("transliteration" in w for w in words), ref)
        self.assertEqual(build_site.transliterated(verse("grc", "JHN.1.1"), "grc")[4]["translit"], "logos")


if __name__ == "__main__":
    unittest.main()
