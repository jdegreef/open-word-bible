"""scripts/name_spellings.py: one name, one spelling per language."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import name_spellings as ns  # noqa: E402


def record(rid, tokens, **renderings):
    return {"id": rid, "source": {"tokens": tokens},
            "renderings": {lang: {"L": text, "B": text, "R": text} for lang, text in renderings.items()}}


NAMES = {"H5816": {"strong": "H5816", "lemma": "U", "lemmas": {"U"},
                   "senses": [{"name": "Uzziel", "kind": "person", "note": ""}]}}
STRONGS = {"t1": ("H5816", "U"), "t2": ("H5816", "U"), "t3": ("H5816", "U"), "t4": ("H5816", "U"),
           "x": ("H1", "other")}


class HelpersTest(unittest.TestCase):
    def test_strong_numbers_lose_leading_zeros(self):
        self.assertEqual(ns.norm_strong("H", "0871a"), "H871a")
        self.assertEqual(ns.norm_strong("G", "3972"), "G3972")
        self.assertIsNone(ns.norm_strong("G", ""))

    def test_endings_are_the_same_name(self):
        self.assertTrue(ns.same_stem(ns.stem("Петра", "ru"), ns.stem("Пётр", "ru"), "ru"))
        self.assertTrue(ns.same_stem(ns.stem("Якова", "uk"), ns.stem("Яків", "uk"), "uk"))
        self.assertTrue(ns.same_stem("다윗이", "다윗", "ko"))
        self.assertTrue(ns.same_stem(ns.stem("የሮቤል", "am"), ns.stem("ሮቤል", "am"), "am"))
        self.assertFalse(ns.same_stem(ns.stem("Озиила", "ru"), ns.stem("Узиил", "ru"), "ru"))

    def test_japanese_words_are_katakana_runs(self):
        self.assertEqual(ns.words("イエス・キリストが来られた", "ja"), ["イエス・キリスト"])


class FormsTest(unittest.TestCase):
    def test_finds_the_usual_form_and_a_variant(self):
        records = [
            record("EXO.6.18.s1", ["t1"], ru="и Узиил был сыном", en="and Uzziel was"),
            record("EXO.6.22.s1", ["t2"], ru="сыновья Узиила", en="the sons of Uzziel"),
            record("NUM.3.19.s1", ["t3"], ru="Хеврон и Узиил", en="Hebron and Uzziel"),
            record("LEV.10.4.s1", ["t4"], ru="сыновей Озиила", en="the sons of Uzziel"),
            record("GEN.1.1.s1", ["x"], ru="В начале Бог", en="In the beginning God"),
        ]
        found = ns.name_forms(records, STRONGS, NAMES)
        form, missing, variants = found[("ru", "H5816")]
        self.assertEqual(form, "Узиил")
        self.assertEqual(missing, ["LEV.10.4.s1"])
        self.assertEqual([w for uses in variants.values() for _rid, w in uses], ["Озиила"])
        self.assertEqual(found[("en", "H5816")][1], [])
        rows = ns.variant_rows(found, NAMES)
        self.assertEqual([(r[0], r[3], r[4], r[5]) for r in rows],
                         [("ru", "Узиил", "Озиила", ["LEV.10.4.s1"])])

    def test_lemma_must_match(self):
        strongs = dict(STRONGS, t4=("H5816", "something else"))
        records = [record(f"X.1.{i}.s1", [f"t{i}"], en="Uzziel came") for i in range(1, 5)]
        found = ns.name_forms(records, strongs, NAMES)
        self.assertEqual(len(found[("en", "H5816")][1]), 0)

    def test_report_renders(self):
        records = [record(f"X.1.{i}.s1", [f"t{i}"], en="Uzziel came") for i in range(1, 5)]
        found = ns.name_forms(records, STRONGS, NAMES)
        text = ns.render_report(ns.variant_rows(found, NAMES), found)
        self.assertIn("| en | 1 | 0 | 0 |", text)


if __name__ == "__main__":
    unittest.main()
