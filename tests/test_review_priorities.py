"""scripts/review_priorities.py: where a native reviewer of a language starts."""
import glob
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import review_priorities as rp  # noqa: E402

from owb import refs  # noqa: E402


def decision(choice, reason="", category="word_choice", alternatives=()):
    return {"choice": choice, "reason": reason, "category": category, "alternatives": list(alternatives)}


class PrioritiesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = rp.render("am")
        cls.sections = re.split(r"^## ", cls.text, flags=re.M)

    def section(self, n):
        return next(s for s in self.sections if s.startswith(f"{n}. "))

    def test_lists_every_uncertain_decision_once(self):
        expected = sum(
            1
            for path in glob.glob(str(ROOT / "content" / "*" / "*.json"))
            for record in json.load(open(path, encoding="utf-8"))["records"]
            for d in record["decisions"]
            if d.get("language") == "am" and d.get("uncertain"))
        items = [line for line in self.section(1).splitlines() if line.startswith("- [ ]")]
        self.assertEqual(len(items), expected)
        self.assertEqual(self.section(1).count("**Question:**"), expected)
        self.assertIn(f"| **Total** | **{expected}** |", self.section(1))

    def test_passages_parse_in_order_and_are_drafted(self):
        for _, first, last, why in rp.PASSAGES:
            self.assertLessEqual(refs.parse(first).sort_key(), refs.parse(last).sort_key(), first)
            self.assertTrue(why)
        rows = [line for line in self.section(2).splitlines() if re.match(r"\| \d+ \|", line)]
        self.assertEqual(len(rows), len(rp.PASSAGES))
        for row in rows:
            records = int(row.split("|")[4])
            self.assertGreater(records, 0, row)

    def test_english_numbering_is_shown_where_it_differs(self):
        books = json.load(open(ROOT / "data" / "books.json", encoding="utf-8"))["books"]
        self.assertEqual(rp.label("MIC.5.1", books), "Micah 5:1 (English 5:2)")
        self.assertEqual(rp.label("JHN.3.16", books), "John 3:16")
        self.assertEqual(rp.label("GEN.1.1", books, "GEN.2.3"), "Genesis 1:1–2:3")

    def test_new_forms_leave_out_forms_kept_from_earlier_books(self):
        forms, flagged, _ = rp.new_forms(decision(
            "Heman \"ሄማን\" as 1 Kings 5:11; Asaph \"አሳፍ\" as 2 Kings 18:18; "
            "Berechiah \"በራክያ\", Kushaiah \"ቁሻያ\" new", "Names keep their forms."))
        self.assertTrue(flagged)
        self.assertEqual(forms, ["በራክያ", "ቁሻያ"])

    def test_new_forms_named_only_in_the_reason(self):
        forms, flagged, _ = rp.new_forms(decision(
            "Zoan \"ጾዓን\" (as Numbers 13:22 on main) and Hanes \"ሐኔስ\"",
            "Hanes appears only here; the form follows the Hebrew and is new in this draft."))
        self.assertTrue(flagged)
        self.assertEqual(forms, ["ሐኔስ"])

    def test_a_new_name_in_the_story_is_not_a_coinage(self):
        _, flagged, _ = rp.new_forms(decision("\"አብርሃም\" from here on", "The new name begins where God gives it."))
        self.assertFalse(flagged)

    def test_letters_that_sound_alike_are_one_form(self):
        self.assertEqual(rp.same_sound("ሐና"), rp.same_sound("ሀና"))
        self.assertEqual(rp.same_sound("ኤልዓሣ"), rp.same_sound("ኤልአሳ"))
        self.assertNotEqual(rp.same_sound("ሐና"), rp.same_sound("ሐኖ"))

    def test_questions_are_one_line(self):
        for d in (decision("\"መልክ\" for the image", alternatives=["\"አምሳል\""]),
                  decision("frank at Literal", category="register"),
                  decision("\"ሐኔስ\"", "a new name spelled from the Hebrew")):
            q = rp.question(d)
            self.assertNotIn("\n", q)
            self.assertTrue(q.endswith("?"), q)
        self.assertIn("«አምሳል»", rp.question(decision("\"መልክ\" for the image", alternatives=["\"አምሳል\""])))

    def test_older_bible_mentions_are_collected(self):
        found = rp.older(decision("own wording", "The 1962 Bible's familiar form was not followed. Other text.",
                                  alternatives=["\"ኤዶታም\" (the 1962 form)"]))
        self.assertEqual(found, ["The 1962 Bible's familiar form was not followed.",
                                 "Alternative: \"ኤዶታም\" (the 1962 form)"])


if __name__ == "__main__":
    unittest.main()
