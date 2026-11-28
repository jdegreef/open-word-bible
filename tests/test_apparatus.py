"""New Testament textual evidence (owb/apparatus.py) against the pinned SBLGNT
apparatus and CNTR transcriptions. No Greek is typed here: words are read
from the data and the claims are English, as in the notes."""
import sys
import unittest
from pathlib import Path

from owb import apparatus, refs
from owb.sources import sblgnt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import apparatus_check  # noqa: E402

LUK_13_35 = refs.Ref("LUK", 13, 35)
ROM_5_1 = refs.Ref("ROM", 5, 1)


def token(ref, position):
    return f"n{apparatus._NT_NUMBER[ref.book]:02d}{ref.chapter:03d}{ref.verse:03d}{position:03d}"


def decision(ref, positions, reason, choice, alternatives=()):
    return {"layer": "meaning", "category": "text_variant", "tokens": [token(ref, p) for p in positions],
            "reason": reason, "choice": choice, "alternatives": list(alternatives)}


def verdicts(result):
    return {(c.group, c.verdict) for c in result["claims"]}


class ApparatusTest(unittest.TestCase):
    def test_every_note_has_a_marked_place(self):
        total = matched = 0
        for code, _ in refs.NT_BOOKS:
            for ref, units in apparatus.units(code).items():
                words = sblgnt.load_book(code)[ref].text.split()
                for u in units:
                    total += 1
                    if u.start and apparatus.key(words[u.start - 1]) == (u.lemma.words or ("",))[0]:
                        matched += 1
        self.assertGreater(total, 6900)
        self.assertGreater(matched / total, 0.99)

    def test_addition_and_editions(self):
        # Luke 13:35: RP and the NIV's text add a word after the sixth.
        [unit] = [u for u in apparatus.units_at(LUK_13_35, [6]) if u.start == 6]
        self.assertEqual(unit.others[0].kind, "add")
        self.assertEqual(set(unit.others[0].witnesses), {"NIV", "RP"})
        self.assertEqual(set(unit.editions_with_sblgnt()), {"WH", "Treg", "NA28"})

    def test_witnesses_at_an_addition(self):
        ev = apparatus.evidence(LUK_13_35, [6])
        self.assertEqual(ev["editions"]["RP"], "differ")
        self.assertEqual(ev["witnesses"]["03"].status, "agree")      # Vaticanus
        self.assertEqual(ev["witnesses"]["05"], apparatus.Comparison("differ", "adds"))  # Bezae
        self.assertEqual(ev["witnesses"]["KJTR"].status, "differ")

    def test_first_hand_and_correction(self):
        # Romans 5:1, "we have" / "let us have": Sinaiticus was corrected.
        self.assertEqual(apparatus.compare(ROM_5_1, [6], "01").status, "differ")
        self.assertEqual(apparatus.compare(ROM_5_1, [6], "01", hand="corrected").status, "agree")

    def test_nomina_sacra(self):
        # The contraction for "Lord" in the manuscripts matches the full word.
        lord = apparatus.key(sblgnt.load_book("LUK")[refs.Ref("LUK", 13, 35)].text.split()[-1])
        self.assertTrue(apparatus._is_nomen(lord[0] + lord[-1], lord))

    def test_missing_verse(self):
        missing = apparatus.missing_verses("MAT")
        self.assertIn(refs.Ref("MAT", 17, 21), missing)
        ev = apparatus.verse_evidence(refs.Ref("MAT", 17, 21))
        self.assertEqual(ev["witnesses"]["01"].status, "agree")      # Sinaiticus lacks it, as the SBLGNT
        self.assertEqual(ev["witnesses"]["05"].status, "differ")     # Bezae has it
        self.assertEqual(ev["editions"]["RP"], "differ")


class ClaimTest(unittest.TestCase):
    def check(self, reason, ref=LUK_13_35, positions=(6,), choice="your house is left to you",
              alternatives=("your house is left to you desolate",)):
        return apparatus.check_note(decision(ref, positions, reason, choice, alternatives))

    def test_confirmed(self):
        result = self.check('Many later manuscripts add "desolate". The earliest manuscripts lack it. '
                            "Reviewers should check the evidence against the apparatus.")
        self.assertEqual(verdicts(result), {("later", "confirmed"), ("earliest", "confirmed")})
        self.assertEqual(result["status"], "confirmed")

    def test_contradicted(self):
        result = self.check('Codex Vaticanus adds "desolate", and Codex Bezae lacks it.')
        self.assertEqual(verdicts(result), {("03", "contradicted"), ("05", "contradicted")})
        self.assertEqual(result["status"], "contradicted")

    def test_king_james(self):
        result = self.check('The King James Version has "desolate".')
        self.assertEqual(verdicts(result), {("KJTR", "confirmed")})

    def test_not_covered(self):
        result = self.check('Many later manuscripts and the Latin translation add "desolate".')
        self.assertEqual(result["status"], "partly")
        self.assertIn(("versions", "not covered"), verdicts(result))

    def test_first_hand(self):
        result = self.check('Codex Sinaiticus as first written and Codex Vaticanus read "let us have peace". '
                            'A corrector of Codex Sinaiticus wrote "we have".',
                            ref=ROM_5_1, positions=(6,), choice='"we have"', alternatives=('"let us have"',))
        self.assertEqual(verdicts(result), {("01", "confirmed"), ("03", "confirmed")})

    def test_instead_of(self):
        result = self.check('Codex Vaticanus reads "let us have" instead of "we have".',
                            ref=ROM_5_1, positions=(6,), choice='"we have"', alternatives=('"let us have"',))
        self.assertEqual(verdicts(result), {("03", "confirmed")})

    def test_divided(self):
        result = self.check("Manuscripts differ here.")
        self.assertEqual(verdicts(result), {("some", "confirmed")})

    def test_cross_reference_is_skipped(self):
        self.assertEqual(apparatus.read_claims("Nearly all manuscripts have it in Mark 13:32."), [])

    def test_general_knowledge_prefix(self):
        self.assertEqual(apparatus.without_knowledge("From general knowledge, many later manuscripts add it."),
                         "Many later manuscripts add it.")
        claims = apparatus.read_claims('From general knowledge: many later manuscripts add "desolate".')
        self.assertEqual([c.group for c in claims], ["later"])

    def test_whole_verse(self):
        d = decision(refs.Ref("MAT", 17, 20), [len(sblgnt.load_book("MAT")[refs.Ref("MAT", 17, 20)].text.split())],
                     "Codex Sinaiticus and Codex Vaticanus do not have verse 21; Codex Bezae and the "
                     "King James Version have it.", "no verse 21")
        result = apparatus.check_note(d)
        self.assertEqual(verdicts(result), {("01", "confirmed"), ("03", "confirmed"), ("05", "confirmed"),
                                            ("KJTR", "confirmed")})


class ScriptTest(unittest.TestCase):
    def test_romans(self):
        self.assertEqual(apparatus_check.main(["--book", "PHM"]), 0)


if __name__ == "__main__":
    unittest.main()
