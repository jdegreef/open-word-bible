import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import parallels  # noqa: E402


class ParallelsTest(unittest.TestCase):
    def test_parse_passage(self):
        self.assertEqual(parallels.parse_passage("ISA 36:1-39:8"), ("ISA", (36, 1), (39, 8)))
        self.assertEqual(parallels.parse_passage("PSA 14:1-7"), ("PSA", (14, 1), (14, 7)))
        self.assertEqual(parallels.parse_passage("LUK 9:22"), ("LUK", (9, 22), (9, 22)))

    def test_align_is_monotonic_and_skips_unmatched(self):
        left, right = ["a", "b", "c", "d"], ["x", "b", "c", "d"]
        pairs = parallels.align(left, right, lambda p, q: 1.0 if p == q else 0.0)
        self.assertEqual(pairs, [(1, 1), (2, 2), (3, 3)])
        # A verse added on one side shifts the pairing; nothing crosses.
        pairs = parallels.align(["a", "b", "c"], ["a", "new", "b", "c"], lambda p, q: 1.0 if p == q else 0.0)
        self.assertEqual(pairs, [(0, 0), (1, 2), (2, 3)])

    def test_plain_sets_aside_settings_markers_and_punctuation(self):
        self.assertEqual(parallels.plain("[The] {{divine_name:LORD|Yahweh}} is my shepherd; \\q I lack."),
                         "the lord is my shepherd i lack")
        self.assertEqual(parallels.plain("a, \\v 3 b"), "a b")

    def test_every_passage_has_source_verses(self):
        for name, a, b in parallels.PARALLELS:
            self.assertTrue(parallels.passage_verses(a), (name, a))
            self.assertTrue(parallels.passage_verses(b), (name, b))

    def test_same_source_reads_the_words_not_only_the_lemmas(self):
        # The same lemmas, but "I say" in Isaiah and "you said" in 2 Kings.
        self.assertEqual(parallels.lemmas("ISA.36.5"), parallels.lemmas("2KI.18.20"))
        self.assertFalse(parallels.same_source("ISA.36.5", "2KI.18.20"))
        self.assertTrue(parallels.same_source("ISA.37.1", "2KI.19.1"))

    def test_pairs_follow_the_shifted_numbering(self):
        # Psalm 108:2-6 repeats Psalm 57:8-12 (108:1 is the title).
        found = parallels.compare("t", "PSA 57:8-12", "PSA 108:1-6", langs=("en",))
        self.assertEqual(found["pairs"][0], ("PSA.57.8", "PSA.108.2"))
        self.assertEqual(len(found["pairs"]), 5)

    def test_harmonised_twins_read_alike(self):
        # Jeremiah 52:2 follows 2 Kings 24:19 at Balanced (a rendering
        # decision in each record says so).
        found = parallels.compare("t", "2KI 24:19", "JER 52:2", langs=("en",))
        self.assertEqual(found["identical"], [("2KI.24.19", "JER.52.2")])
        self.assertEqual(found["wording"], [])

    def test_report(self):
        results = [parallels.compare("Hurry to help me", "PSA 40:14-18", "PSA 70:1-6", langs=("en",))]
        text = parallels.report(results)
        self.assertTrue(text.startswith("# Parallel passages\n"))
        self.assertIn("| Hurry to help me | PSA 40:14-18 ↔ PSA 70:1-6 | 5 |", text)


if __name__ == "__main__":
    unittest.main()
