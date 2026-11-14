"""scripts/quotations.py: Old Testament quotations in the New."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import quotations  # noqa: E402
from owb import refs  # noqa: E402


class DataTest(unittest.TestCase):
    def test_entries_are_well_formed(self):
        qs = quotations.load()
        self.assertGreaterEqual(len(qs), 150)
        for q in qs:
            self.assertIn(q["kind"], ("hebrew", "septuagint", "loose"))
            nt = quotations.verse_range(q["nt"])
            self.assertIn(nt[0].book, quotations.NT_BOOKS, q)
            self.assertTrue(quotations.old_testament_verses(q["ot"]), q)

    def test_english_numbering_is_mapped_to_ours(self):
        # Psalm 22:1 in English Bibles is our (Hebrew) Psalm 22:2.
        self.assertEqual([str(r) for r in quotations.old_testament_verses("PSA.22.1")], ["PSA.22.2"])
        self.assertEqual([str(r) for r in quotations.verse_range("MAT.4.15-16")], ["MAT.4.15", "MAT.4.16"])


class EchoTest(unittest.TestCase):
    def test_longest_run(self):
        self.assertEqual(quotations.longest_run("a b c d".split(), "x b c d y".split()), 3)
        self.assertEqual(quotations.longest_run(["a"], ["b"]), 0)

    def test_echo_of_a_quotation_that_matches(self):
        nt = [{"renderings": {"en": {"B": "Love your neighbor as yourself."}}}]
        ot = [{"renderings": {"en": {
            "B": "Instead, love your neighbor as yourself. I am {{divine_name:the LORD|Yahweh}}."}}}]
        share, run = quotations.echo(nt, ot, "en", "B")
        self.assertEqual(share, 1.0)
        self.assertEqual(run, 5)
        self.assertIsNone(quotations.echo(nt, [{"renderings": {}}], "en", "B"))

    def test_classes(self):
        self.assertEqual(quotations.classify({"kind": "hebrew"}), "a")
        self.assertEqual(quotations.classify({"kind": "septuagint"}), "b")
        self.assertEqual(quotations.classify({"kind": "loose"}), "c")


class FormulaTest(unittest.TestCase):
    def test_formulas_are_found_by_strongs_number(self):
        words = json.loads((ROOT / "data" / "grc" / "MAT.4.json").read_text(encoding="utf-8"))["verses"]
        self.assertEqual(quotations.formula(words["MAT.4.4"]), "written")
        self.assertIsNone(quotations.formula(words["MAT.4.2"]))
        words = json.loads((ROOT / "data" / "grc" / "MAT.1.json").read_text(encoding="utf-8"))["verses"]
        self.assertEqual(quotations.formula(words["MAT.1.22"]), "fulfilled")

    def test_formula_sites_are_new_testament_and_in_order(self):
        sites = quotations.formula_sites()
        keys = [refs.parse(v).sort_key() for v, _ in sites]
        self.assertEqual(keys, sorted(keys))
        self.assertTrue(all(refs.parse(v).book in quotations.NT_BOOKS for v, _ in sites))
        self.assertIn(("MAT.4.4", "written"), sites)
        self.assertTrue(quotations.covered("MAT.4.4", quotations.load()))


class SurveyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {r["nt"]: r for r in quotations.survey()}

    def test_every_septuagint_quotation_has_a_footnoted_note(self):
        for r in self.rows.values():
            if r["class"] == "b" and r["nt_records"]:
                self.assertTrue(any("(footnote)" in n for n in r["septuagint_notes"]), r["nt"])

    def test_no_unreviewed_difference_is_left(self):
        self.assertEqual([r["nt"] for r in self.rows.values() if r["flag"] == "differs"], [])

    def test_report_lists_every_quotation(self):
        text = quotations.report()
        for nt in self.rows:
            self.assertIn(f"| {nt} |", text)


if __name__ == "__main__":
    unittest.main()
