"""Links to Logia's commentary (data/logia_coverage.json, scripts/fetch_logia.py)."""
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402

COVERAGE = {"JHN.3": {"voices": 12, "verses": {"16": 12, "5": 9, "3": 10}}}


class LogiaLinkTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(build_site, "logia_coverage", return_value=COVERAGE)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_chapter_with_commentary_links_it_and_its_most_discussed_verses(self):
        text = build_site.logia_chapter_html("JHN", 3)
        self.assertIn('href="https://logia.faith/jhn/3/"', text)
        self.assertIn("12 commentators on John 3", text)
        # In verse order.
        self.assertLess(text.index("/jhn/3/3/"), text.index("/jhn/3/16/"))
        self.assertNotIn("hreflang", text)
        self.assertIn('hreflang="en"', build_site.logia_chapter_html("JHN", 3, "es"))

    def test_a_chapter_or_verse_without_commentary_has_no_link(self):
        self.assertEqual(build_site.logia_chapter_html("ACT", 1), "")
        self.assertEqual(build_site.logia_verse_html("JHN.3.17"), "")

    def test_a_verse_page_links_its_verse(self):
        text = build_site.logia_verse_html("JHN.3.16")
        self.assertIn('href="https://logia.faith/jhn/3/16/"', text)
        self.assertIn("What 12 commentators said about John 3:16", text)


class SnapshotTest(unittest.TestCase):
    def test_the_snapshot_is_well_formed(self):
        if not build_site.LOGIA_COVERAGE.exists():
            self.skipTest("no snapshot")
        data = json.loads(build_site.LOGIA_COVERAGE.read_text(encoding="utf-8"))["chapters"]
        for key, ch in data.items():
            book, chapter = key.split(".")
            self.assertIn(book, build_site.BOOK_CHAPTERS, key)
            self.assertTrue(chapter.isdigit() and ch["voices"] >= 1, key)
            for verse, n in ch["verses"].items():
                self.assertTrue(verse.isdigit() and 1 <= n <= ch["voices"], (key, verse))


if __name__ == "__main__":
    unittest.main()
