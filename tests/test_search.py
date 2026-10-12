"""Search: the index the build writes for each interface language, the
/search/ page, and the header's search button (web/search.js runs them)."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


class SearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "site"
        build_site.build(cls.out)
        cls.records = build_site.all_records()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def index(self, lang):
        return json.loads((self.out / f"search-{lang}.json").read_text(encoding="utf-8"))

    def page_exists(self, href):
        path = href.split("#")[0].split("?")[0].strip("/")
        return (self.out / path / "index.html").is_file()

    def test_every_page_points_at_its_languages_index(self):
        for page in self.out.rglob("index.html"):
            text = page.read_text(encoding="utf-8")
            lang = re.search(r'<html lang="(\w+)">', text)[1]
            m = re.search(r'<meta name="owb-search" content="/search-(\w+)\.json\?v=(\w+)">', text)
            self.assertIsNotNone(m, page)
            self.assertEqual(m[1], lang, page)
            body = (self.out / f"search-{lang}.json").read_bytes()
            self.assertEqual(m[2], hashlib.sha256(body).hexdigest()[:10], page)
            self.assertIn('id="palette"', text, page)
            self.assertIn(f'class="tool-btn search-btn" href="{build_site.url(lang, "/search/")}"', text, page)

    def test_search_page_in_each_language_and_in_the_sitemap(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        for lang in build_site.LANGUAGES:
            path = build_site.url(lang, "/search/")
            page = (self.out / path.strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="search-q"', page)
            self.assertIn(f'action="{path}"', page)
            self.assertIn(f"<loc>{build_site.SITE_URL}{path}</loc>", sitemap)

    def test_every_sentence_is_in_every_index_once(self):
        for lang in build_site.LANGUAGES:
            verses = [d for d in self.index(lang)["docs"] if d["k"] == "v"]
            self.assertEqual(len(verses), len(self.records), lang)
            for doc, record in zip(verses, self.records):
                shown = build_site.text_lang(record, lang)
                self.assertEqual(doc["x"], record["renderings"][shown])
                # A sentence not yet in lang is shown, and found, in English.
                self.assertEqual(doc.get("l"), None if shown == lang else shown)
                self.assertEqual(doc["vv"], [int(r.split(".")[2]) for r in record["refs"]])

    def test_notes_are_meaning_and_the_shown_languages_wording(self):
        for lang in build_site.LANGUAGES:
            notes = [d for d in self.index(lang)["docs"] if d["k"] == "n"]
            expected = sum(1 for r in self.records for d in r["decisions"]
                           if d["layer"] == "meaning" or d["language"] == build_site.text_lang(r, lang))
            self.assertEqual(len(notes), expected, lang)
            self.assertTrue(all(n["y"] in ("meaning", "rendering") for n in notes))

    def test_every_link_in_the_index_is_a_built_page(self):
        for lang in build_site.LANGUAGES:
            data = self.index(lang)
            for doc in data["docs"]:
                self.assertTrue(self.page_exists(doc["u"]), doc["u"])
                if doc["k"] != "a":
                    self.assertTrue(doc["u"].startswith(build_site.url(lang, "/")), doc["u"])
            for _, href in data["pages"]:
                self.assertTrue(self.page_exists(href), href)
            for book in data["books"]:
                for chapter in book.get("chapters", {}).values():
                    self.assertTrue(self.page_exists(chapter["url"]), chapter["url"])

    def test_articles_and_passages_are_indexed(self):
        for lang in build_site.LANGUAGES:
            docs = self.index(lang)["docs"]
            self.assertEqual(sum(d["k"] == "a" for d in docs), len(build_site.load_articles(lang)))
            self.assertEqual(sum(d["k"] == "c" for d in docs), len(build_site.passages()))
            for article in (d for d in docs if d["k"] == "a"):
                self.assertNotIn("{{", article["x"])
                self.assertNotIn("l", article)

    def test_book_names_and_abbreviations(self):
        books = {b["code"]: b for b in self.index("es")["books"]}
        self.assertEqual(books["JHN"]["name"], "Juan")
        for alias in ("john", "juan", "jhn", "jn"):
            self.assertIn(alias, books["JHN"]["aliases"])
        self.assertIn("filipenses", books["PHP"]["aliases"])
        self.assertIn("phil", books["PHP"]["aliases"])
        # Books without passages yet are known, for "not translated yet".
        self.assertIn("NAM", books)
        self.assertNotIn("chapters", books["NAM"])

    def test_fold(self):
        self.assertEqual(build_site.fold("Señor Corazón"), "senor corazon")

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_script_parses(self):
        subprocess.run(["node", "--check", str(ROOT / "web" / "search.js")], check=True)


if __name__ == "__main__":
    unittest.main()
