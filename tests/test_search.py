"""Search: the documents the API searches (search_documents, one set per
interface language), the /search/ page, and the header's search button
(web/search.js runs them)."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from owb import markup  # noqa: E402
from tests.site_build import built_site, sitemap_text  # noqa: E402


class SearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()
        cls.records = build_site.all_records()

    def index(self, lang):
        return build_site.search_documents(lang)

    def page_exists(self, href):
        path = href.split("#")[0].split("?")[0].strip("/")
        return (self.out / path / "index.html").is_file()

    def test_every_page_points_at_the_api_and_its_languages_text(self):
        source = re.escape(build_site.search_source("en"))
        digests = {lang: hashlib.sha256((self.out / f"search-ui-{lang}.json").read_bytes()).hexdigest()[:10]
                   for lang in build_site.LANGUAGES}
        for page in self.out.rglob("index.html"):
            text = page.read_text(encoding="utf-8")
            lang = re.search(r'<html lang="(\w+)"[ >]', text)[1]
            m = re.search(rf'<meta name="owb-search" content="{source}" '
                          r'data-ui="/search-ui-(\w+)\.json\?v=(\w+)">', text)
            self.assertIsNotNone(m, page)
            self.assertEqual(m[1], lang, page)
            self.assertEqual(m[2], digests[lang], page)
            self.assertIn('id="palette"', text, page)
            self.assertIn(f'class="tool-btn search-btn" href="{build_site.url(lang, "/search/")}"', text, page)

    def test_search_asks_the_api(self):
        self.assertEqual(build_site.search_source("es"), f"{build_site.API_URL}/api/search/")
        for lang in build_site.LANGUAGES:
            data = json.loads((self.out / f"search-ui-{lang}.json").read_text(encoding="utf-8"))
            index = self.index(lang)
            self.assertEqual((data["ui"], data["pages"]), (index["ui"], index["pages"]))
            self.assertEqual(data["names"]["JHN"], next(b["name"] for b in index["books"] if b["code"] == "JHN"))
            self.assertTrue(data["ui"]["offline"], lang)
            # Small: the whole index was megabytes.
            self.assertLess(len(json.dumps(data)), 20_000)
            page = (self.out / build_site.url(lang, "/search/").strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn('data-offline="', page)
        # The static indexes are no longer built; the service worker neither
        # keeps them nor offers them to saved books, and drops copies kept
        # before.
        self.assertFalse([p.name for p in self.out.glob("search-*.json") if not p.name.startswith("search-ui-")])
        sw = (self.out / "sw.js").read_text(encoding="utf-8")
        current = json.loads(re.search(r"var CURRENT = (.*);", sw)[1])
        dropped = json.loads(re.search(r"var DROPPED = (.*);", sw)[1])
        self.assertEqual(sorted(dropped), sorted(f"/search-{lang}.json" for lang in build_site.LANGUAGES))
        self.assertFalse([u for u in current if u.split("?")[0] in dropped])
        self.assertIn(build_site.search_ui_url("en"), current)
        self.assertNotIn("/search-en.json", json.dumps(build_site.offline_files("en")))
        self.assertIn('url.pathname.indexOf("/api/") === 0', sw)

    def test_search_page_in_each_language_and_not_listed(self):
        sitemap = sitemap_text(self.out)
        for lang in build_site.LANGUAGES:
            path = build_site.url(lang, "/search/")
            page = (self.out / path.strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="search-q"', page)
            self.assertIn(f'action="{path}"', page)
            # Search results are not worth listing in a search engine.
            self.assertRegex(page, r'<meta name="robots" content="noindex[^"]*">')
            self.assertNotIn(f"<loc>{build_site.SITE_URL}{path}</loc>", sitemap)

    def test_every_sentence_is_in_every_index_once(self):
        for lang in build_site.LANGUAGES:
            verses = [d for d in self.index(lang)["docs"] if d["k"] == "v"]
            self.assertEqual(len(verses), len(self.records), lang)
            for doc, record in zip(verses, self.records):
                shown = build_site.text_lang(record, lang)
                # Poetic line markers (\q) read as spaces in search.
                self.assertEqual(doc["x"], {level: markup.flat(text)
                                            for level, text in record["renderings"][shown].items()})
                self.assertFalse(any("\\q" in text for text in doc["x"].values()), doc)
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
        # Every book is known; each now has passages to link to.
        self.assertEqual(len(books), 66)
        self.assertIn("chapters", books["ECC"])

    def test_fold(self):
        self.assertEqual(build_site.fold("Señor Corazón"), "senor corazon")
        # The kana voicing marks are not accents (ガ is not カ), and full-width
        # digits are digits, so Japanese book names match as they are typed.
        self.assertEqual(build_site.fold("ガラテヤ３"), "ガラテヤ3")
        self.assertIn("ガラテヤの信徒への手紙", {b["code"]: b for b in self.index("ja")["books"]}["GAL"]["aliases"])

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_script_parses(self):
        subprocess.run(["node", "--check", str(ROOT / "web" / "search.js")], check=True)


class ArabicFoldTest(unittest.TestCase):
    """Arabic and Persian are typed with and without the short vowels, with
    hamza or without, and with either form of yeh and kaf: each way finds
    the others. The site's search.js folds as build_site.fold (and the API's
    search.fold) do."""
    CASES = {
        "\u0627\u0644\u0652\u0643\u064e\u0644\u0650\u0645\u064e\u0629\u064f":  # الْكَلِمَةُ: الكلمة
            "\u0627\u0644\u0643\u0644\u0645\u0629",
        "\u0623\u0628\u0631\u0627\u0647\u064a\u0645": "\u0627\u0628\u0631\u0627\u0647\u064a\u0645",  # أبراهيم: ابراهيم
        "\u0625\u0644\u0647 \u0622\u062f\u0645 \u0671\u0644": "\u0627\u0644\u0647 \u0627\u062f\u0645 \u0627\u0644",
        "\u0645\u0648\u0633\u0649": "\u0645\u0648\u0633\u064a",  # موسى: alef maqsura as yeh
        "\u06a9\u062a\u0627\u0628 \u0639\u06cc\u0633\u06cc":  # Persian ک and ی
            "\u0643\u062a\u0627\u0628 \u0639\u064a\u0633\u064a",
        "\u0627\u0644\u0644\u0640\u0640\u0647": "\u0627\u0644\u0644\u0647",  # tatweel
        "\u064a\u0648\u062d\u0646\u0627 \u0663:\u0661\u0666 \u06f3:\u06f1\u06f6":
            "\u064a\u0648\u062d\u0646\u0627 3:16 3:16",
    }

    def test_fold(self):
        for text, folded in self.CASES.items():
            self.assertEqual(build_site.fold(text), folded, text)

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_search_js_folds_the_same(self):
        source = (ROOT / "web" / "search.js").read_text()
        body = re.search(r"\n  function fold\(s\) \{\n.*?\n  \}\n", source, re.S)[0]
        script = body + "process.stdout.write(JSON.stringify(JSON.parse(process.argv[1]).map(fold)));"
        texts = list(self.CASES)
        out = subprocess.run(["node", "-e", script, json.dumps(texts)], check=True,
                             capture_output=True, text=True).stdout
        self.assertEqual(json.loads(out), [build_site.fold(t) for t in texts])


if __name__ == "__main__":
    unittest.main()
