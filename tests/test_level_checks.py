"""scripts/level_checks.py: supplied words in brackets, and Readable plainer than Balanced."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import level_checks as lc  # noqa: E402


def decision(choice, levels=("L",), lang="en"):
    return {"category": "supplied_words", "layer": "rendering", "language": lang,
            "levels": list(levels), "choice": choice}


def record(rid, renderings, decisions=()):
    return {"id": rid, "renderings": renderings, "decisions": list(decisions)}


class PhrasesTest(unittest.TestCase):
    def test_keeps_the_literal_parts(self):
        self.assertEqual(lc.literal_phrases("cast [it] (L); threw it out (B); So they did (R)"),
                         ["cast [it]"])
        self.assertEqual(lc.literal_phrases("I broke (L in brackets); loaves (B, R)"), ["I broke"])

    def test_quoted_wording_and_ellipsis(self):
        self.assertEqual(lc.literal_phrases('"[ይኸውም] ... [ነው]" (that is, ... so) supplied'),
                         ["[ይኸውም]", "[ነው]"])
        self.assertEqual(lc.literal_phrases("nawaambia, mtaona: the plural is in the verb"),
                         ["nawaambia, mtaona"])


class SuppliedStatusTest(unittest.TestCase):
    def test_bracketed(self):
        self.assertEqual(lc.supplied_status(["cast [it]"], "So they cast [it], and"), "bracketed")
        self.assertEqual(lc.supplied_status(["your name"],
                                            "lift [{{deity_pronoun:your|Your}} name] up"), "bracketed")

    def test_not_bracketed_and_not_found(self):
        self.assertEqual(lc.supplied_status(["kumtumikia"], "Wakisikia na kumtumikia,"), "not_bracketed")
        self.assertEqual(lc.supplied_status(["a closing square bracket"], "Amen.]"), "not_found")

    def test_only_decisions_covering_literal(self):
        records = [record("X.1.1.s1", {"en": {"L": "free [woman]", "B": "free woman", "R": "free woman"}},
                          [decision("free [woman] (L); free woman (B, R)", ("L", "B", "R")),
                           decision("also", ("B", "R"))])]
        self.assertEqual([s for _r, _l, s, _c in lc.supplied_checks(records)], ["bracketed"])


class BracketChecksTest(unittest.TestCase):
    def problems(self, renderings):
        return [(lv, p) for _r, _l, lv, p in lc.bracket_checks([record("X.1.1.s1", {"en": renderings})])]

    def test_brackets_at_balanced_are_flagged(self):
        self.assertEqual(self.problems({"L": "sent [men]", "B": "sent [men]", "R": "sent men"}),
                         [("B", "brackets at B")])

    def test_unbalanced_literal(self):
        self.assertEqual(self.problems({"L": "sent [men", "B": "sent men", "R": "sent men"}),
                         [("L", "unbalanced brackets")])

    def test_passage_brackets_are_fine_even_with_supplied_words_inside(self):
        self.assertEqual(self.problems({"L": "[Now on [the] first [day] he rose.",
                                        "B": "[Early on the first day he rose.",
                                        "R": "[Jesus rose on Sunday."}), [])
        self.assertEqual(self.problems({"L": "Amen.]", "B": "Amen.]", "R": "Amen.]"}), [])

    def test_nested_brackets(self):
        self.assertEqual(self.problems({"L": "a [b [c]] d", "B": "a b c d", "R": "a b c d"}),
                         [("L", "nested brackets")])


class ReadabilityTest(unittest.TestCase):
    def test_words_and_sentences(self):
        self.assertEqual(lc.words("Then he said, “Go.”", "en"), ["then", "he", "said", "go"])
        self.assertEqual(len(lc.words("初めに、言はおられた。", "ja")), 9)
        self.assertEqual(len(lc.sentences("One. Two! Three?")), 3)

    def test_flags_a_readable_that_is_not_plainer(self):
        long_b = "The very long sentence goes on and on here."
        records = [record(f"GEN.1.{i}.s1", {"en": {"L": long_b, "B": long_b,
                                                   "R": "The very long sentence goes on and on here too."}})
                   for i in range(1, lc.MIN_RECORDS + 1)]
        stats, vocab = lc.readability(records)
        rows = lc.readability_table(stats, vocab)
        self.assertEqual(len(rows), 1)
        self.assertIn("sentences", rows[0][3])

    def test_plainer_readable_is_not_flagged(self):
        records = [record(f"GEN.1.{i}.s1", {"en": {
            "L": "Moreover the extraordinarily magnificent luminaries illuminated everything.",
            "B": "Moreover the magnificent luminaries illuminated everything there.",
            "R": "The lights shone. All was bright."}}) for i in range(1, lc.MIN_RECORDS + 1)]
        stats, vocab = lc.readability(records)
        self.assertEqual(lc.readability_table(stats, vocab)[0][3], [])


if __name__ == "__main__":
    unittest.main()
