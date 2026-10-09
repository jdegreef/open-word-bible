import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "site"
        build_site.build(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def chapter_data(self):
        page = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="owb-data">(.*?)</script>', page, re.S)
        return json.loads(m[1])

    def test_pages_exist(self):
        for rel in ("index.html", "jhn/1/index.html", "about/index.html", "404.html",
                    "style.css", "reader.js"):
            self.assertTrue((self.out / rel).is_file(), rel)

    def test_chapter_has_every_verse_in_both_languages(self):
        data = self.chapter_data()
        self.assertEqual([v for r in data["records"] for v in r["refs"]],
                         [f"JHN.1.{v}" for v in range(1, 19)])
        self.assertEqual(data["languages"], ["en", "es"])

    def test_words_match_each_verse_source_tokens(self):
        data = self.chapter_data()
        for r in data["records"]:
            words = {t["id"] for v in r["refs"] for t in data["words"][v]}
            self.assertEqual(set(r["source"]["tokens"]), words, r["id"])

    def test_about_page_credits_sources(self):
        about = (self.out / "about" / "index.html").read_text(encoding="utf-8")
        for name in ("SBL Greek New Testament", "MACULA Greek", "Open Scriptures Hebrew Bible"):
            self.assertIn(name, about)


class ExtractTest(unittest.TestCase):
    def test_extracts_are_up_to_date(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_tokens.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
