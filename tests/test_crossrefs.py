import subprocess
import sys
import unittest
from pathlib import Path

from owb import crossrefs, refs
from owb.sources import openbible

ROOT = Path(__file__).resolve().parents[1]


def ref(text):
    return refs.parse(text)


def rows(text):
    return openbible.parse("From Verse\tTo Verse\tVotes\t#header\n" + text)


class FormatTest(unittest.TestCase):
    def test_round_trip(self):
        for text in ("ISA.40.11", "EZK.34.11-12", "GEN.1.31-2.3", "1JN.4.9-10"):
            self.assertEqual(crossrefs.format_target(*crossrefs.parse_target(text)), text)

    def test_bad_target(self):
        for text in ("ISA.40", "ISA.40.11-", "XYZ.1.1", "ISA.40.11-12-13"):
            with self.assertRaises(ValueError, msg=text):
                crossrefs.parse_target(text)

    def test_a_range_into_another_book_keeps_its_first_verse(self):
        (row,) = rows("Num.3.1\tLev.27.34-Num.1.1\t2\n")
        self.assertEqual((row.first, row.last), (ref("LEV.27.34"), ref("LEV.27.34")))


class SelectTest(unittest.TestCase):
    VERSES = {ref(v) for v in (
        "JHN.3.15", "JHN.3.16", "ROM.5.8", "ROM.8.32", "1JN.4.9", "1JN.4.10", "JHN.11.25", "JHN.11.26",
        "JHN.6.40", "JHN.3.36", "MAT.17.20", "PSA.3.1", "PSA.3.2", "PSA.17.7", "PSA.52.10",
        "PSA.13.6", "ISA.12.2", "HAB.3.18")}

    def select(self, text):
        return {str(k): v for k, v in crossrefs.select(rows(text), self.VERSES).items()}

    def test_most_voted_first_and_at_most_per_verse(self):
        out = self.select("John.3.16\tRom.5.8\t871\n"
                          "John.3.16\t1John.4.9-1John.4.10\t618\n"
                          "John.3.16\tJohn.3.15\t439\n"
                          "John.3.16\tRom.8.32\t434\n"
                          "John.3.16\tJohn.11.25-John.11.26\t400\n"
                          "John.3.16\tJohn.6.40\t344\n")
        self.assertEqual(len(out["JHN.3.16"]), crossrefs.PER_VERSE)
        self.assertEqual(out["JHN.3.16"][:2], ["ROM.5.8", "1JN.4.9-10"])
        self.assertNotIn("JHN.6.40", out["JHN.3.16"])

    def test_too_few_votes_and_the_verse_itself_are_left_out(self):
        out = self.select(f"John.3.16\tRom.5.8\t{crossrefs.MIN_VOTES - 1}\n"
                          "John.3.16\tJohn.3.15-John.3.16\t50\n"
                          "John.3.16\tJohn.3.36\t-3\n")
        self.assertNotIn("JHN.3.16", out)

    def test_verses_our_text_lacks_are_dropped(self):
        # SBLGNT has no Matthew 17:21.
        out = self.select("John.3.16\tMatt.17.20-Matt.17.21\t40\n"
                          "Matt.17.21\tJohn.3.16\t40\n")
        self.assertEqual(out, {})

    def test_old_testament_moves_to_hebrew_numbering(self):
        # English Psalm 3:1 is our PSA.3.2 (3:1 is the title), English
        # 52:8 our 52:10; English 13:5 and 13:6 are both our 13:6.
        out = self.select("Ps.3.1\tPs.17.7\t12\n"
                          "Ps.17.7\tPs.52.8\t9\n"
                          "Ps.13.5\tIsa.12.2\t20\n"
                          "Ps.13.6\tHab.3.18\t30\n"
                          "Ps.13.6\tIsa.12.2\t5\n")
        self.assertNotIn("PSA.3.1", out)
        self.assertEqual(out["PSA.3.2"], ["PSA.17.7"])
        self.assertEqual(out["PSA.17.7"], ["PSA.52.10"])
        self.assertEqual(out["PSA.13.6"], ["HAB.3.18", "ISA.12.2"])


class DataTest(unittest.TestCase):
    def test_every_book_has_well_formed_references(self):
        for code in refs.BOOK_CODES:
            table = crossrefs.load(code)
            self.assertTrue(table, code)
            for vid, targets in table.items():
                self.assertEqual(refs.parse(vid).book, code, vid)
                self.assertTrue(1 <= len(targets) <= crossrefs.PER_VERSE, vid)
                self.assertEqual(len(set(targets)), len(targets), vid)
                for target in targets:
                    first, last = crossrefs.parse_target(target)
                    self.assertLessEqual(first.sort_key(), last.sort_key(), (vid, target))

    def test_known_verses(self):
        self.assertEqual(crossrefs.load("JHN")["JHN.3.16"][0], "ROM.5.8")
        self.assertIn("ISA.40.11", crossrefs.load("PSA")["PSA.23.1"])
        self.assertNotIn("PSA.3.1", crossrefs.load("PSA"))

    def test_extracts_are_up_to_date(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_crossrefs.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
