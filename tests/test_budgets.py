import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_budgets  # noqa: E402


class BudgetsTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.site = Path(tmp.name)
        self.write("index.html", b"<!doctype html>home")
        self.write("jhn/1/index.html", b"<p>In the beginning</p>" * 50)
        self.write("es/jhn/1/index.html", os.urandom(3000))   # random: gzip can't shrink it
        self.write("read/index.html", os.urandom(9000))       # not a chapter page
        self.write("reader.js", b"var a = 1;\n" * 100)
        self.write("style.css", os.urandom(2000))

    def write(self, rel, data):
        path = self.site / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def run_check(self, **limits):
        budgets = dict(check_budgets.BUDGETS, **limits)
        out = io.StringIO()
        with mock.patch.dict(check_budgets.BUDGETS, budgets):
            return check_budgets.check(self.site, out), out.getvalue()

    def test_measures_the_largest_of_each(self):
        found = check_budgets.measure(self.site)
        self.assertEqual(found["chapter_page_gz"][1], self.site / "es/jhn/1/index.html")
        self.assertEqual(found["js_css_asset_gz"][1], self.site / "style.css")
        total = sum(p.stat().st_size for p in self.site.rglob("*") if p.is_file())
        self.assertEqual(found["site_total"], (total, None))

    def test_a_chapter_page_counts_its_shared_data_and_reader_data_is_no_asset(self):
        # Every language's page of a chapter loads the chapter's shared data;
        # the reader data scripts are data, not code.
        self.write("chapter-data/jhn/1.js", os.urandom(5000))
        self.write("reader-en.js", os.urandom(8000))
        found = check_budgets.measure(self.site)
        page, data = self.site / "es/jhn/1/index.html", self.site / "chapter-data/jhn/1.js"
        self.assertEqual(found["chapter_page_gz"], (check_budgets.gzipped(page) + check_budgets.gzipped(data), page))
        self.assertEqual(found["js_css_asset_gz"][1], self.site / "style.css")

    def test_within_budget_passes(self):
        failed, report = self.run_check()
        self.assertEqual(failed, [])
        self.assertIn("headroom", report)
        self.assertIn("es/jhn/1/index.html", report)

    def test_over_budget_fails_and_says_by_how_much(self):
        failed, report = self.run_check(chapter_page_gz=1024, site_total=10 * 1024)
        self.assertEqual(failed, ["chapter_page_gz", "site_total"])
        self.assertIn("OVER by", report)

    def test_main_exit_status(self):
        with mock.patch("sys.stdout", io.StringIO()), mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(check_budgets.main([str(self.site)]), 0)
            with mock.patch.dict(check_budgets.BUDGETS, {"js_css_asset_gz": 100}):
                self.assertEqual(check_budgets.main([str(self.site)]), 1)

    def test_a_budget_can_be_dropped(self):
        budgets = {k: v for k, v in check_budgets.BUDGETS.items() if k != "js_css_asset_gz"}
        with mock.patch.object(check_budgets, "BUDGETS", budgets):
            self.assertNotIn("js_css_asset_gz", check_budgets.measure(self.site))


if __name__ == "__main__":
    unittest.main()
