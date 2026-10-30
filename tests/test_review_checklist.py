"""scripts/review_checklist.py: every uncertain rendering decision of a language,
listed for reviewers."""
import glob
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import review_checklist  # noqa: E402

ITEM = re.compile(r"^- \[ \] \[([1-3A-Z]{3}) (\d+):(\d+)\]"
                  r"\(https://openwordbible\.org/fr/([1-3a-z]{3})/(\d+)/#v(\d+)\) ")


class ReviewChecklistTest(unittest.TestCase):
    def test_lists_every_uncertain_decision_once(self):
        expected = sum(
            1
            for path in glob.glob(str(ROOT / "content" / "*" / "*.json"))
            for record in json.load(open(path, encoding="utf-8"))["records"]
            for d in record["decisions"]
            if d.get("language") == "fr" and d.get("uncertain"))
        lines = [line for line in review_checklist.render("fr").splitlines() if line.startswith("- [ ]")]
        self.assertEqual(len(lines), expected)

    def test_items_link_to_their_verse_in_order(self):
        last = None
        for line in review_checklist.render("fr").splitlines():
            if line.startswith("## "):
                last = None
            if not line.startswith("- [ ]"):
                continue
            m = ITEM.match(line)
            self.assertIsNotNone(m, line)
            book, chapter, verse, link_book, link_chapter, link_verse = m.groups()
            self.assertEqual((book.lower(), chapter, verse), (link_book, link_chapter, link_verse))
            here = (int(chapter), int(verse))
            if last:
                self.assertLessEqual(last, here, line)
            last = here

    def test_long_reasons_are_cut_at_a_word(self):
        self.assertEqual(review_checklist.short("one two three", limit=8), "one two …")
        self.assertEqual(review_checklist.short("short"), "short")


if __name__ == "__main__":
    unittest.main()
