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

    def chapter_data(self, path="jhn/1"):
        page = (self.out / path / "index.html").read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="owb-data">(.*?)</script>', page, re.S)
        return json.loads(m[1])

    def test_pages_exist(self):
        for rel in ("index.html", "read/index.html", "jhn/1/index.html", "php/4/index.html",
                    "about/index.html", "404.html", "style.css", "reader.js",
                    "sitemap.xml", "robots.txt", "favicon.svg"):
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

    def test_read_page_lists_every_passage(self):
        read = (self.out / "read" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/jhn/1/"', read)
        self.assertIn('href="/php/4/"', read)

    def test_sentence_records_split_a_verse(self):
        data = self.chapter_data("php/4")
        five = [r for r in data["records"] if r["refs"] == ["PHP.4.5"]]
        self.assertEqual([r["id"] for r in five], ["PHP.4.5.s1", "PHP.4.5.s2"])
        self.assertFalse(set(five[0]["source"]["tokens"]) & set(five[1]["source"]["tokens"]))

    def test_pages_have_canonical_urls_and_a_sitemap(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        for path in ("", "read/", "about/", "jhn/1/", "php/4/"):
            url = f"{build_site.SITE_URL}/{path}"
            self.assertIn(f"<loc>{url}</loc>", sitemap)
            page = (self.out / path / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'<link rel="canonical" href="{url}">', page)
        self.assertNotIn("canonical", (self.out / "404.html").read_text(encoding="utf-8"))
        robots = (self.out / "robots.txt").read_text(encoding="utf-8")
        self.assertIn(f"Sitemap: {build_site.SITE_URL}/sitemap.xml", robots)
        self.assertTrue((self.out / "favicon.svg").is_file())

    def test_home_page_example_comes_from_the_content(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        book, chapter, record_id, decision_id = build_site.EXAMPLE
        records, words = build_site.load_chapter(book, chapter)
        record = next(r for r in records if r["id"] == record_id)
        decision = next(d for d in record["decisions"] if d["id"] == decision_id)
        for level in "LBR":
            self.assertIn(build_site.plain(record["renderings"]["en"][level]), home)
        marked = [w["text"] for v in record["refs"] for w in words[v] if w["id"] in decision["tokens"]]
        self.assertTrue(marked)
        for word in marked:
            self.assertIn(f"<mark>{word}</mark>", home)
        self.assertIn(f"<b>{len(build_site.all_records())}</b>", home)
        self.assertIn('href="/jhn/1/"', home)

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
