import hashlib
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

    def test_account_page_is_built_but_not_indexed(self):
        page = (self.out / "account" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex">', page)
        self.assertIn('id="link-form"', page)
        self.assertTrue((self.out / "account.js").is_file())
        self.assertNotIn("/account/", (self.out / "sitemap.xml").read_text(encoding="utf-8"))
        # Every page knows the API and has the account button.
        for path in self.out.rglob("index.html"):
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'<meta name="owb-api" content="{build_site.API_URL}">', text, path)
            lang = re.search(r'<html lang="([a-z]+)">', text)[1]
            account = build_site.url(lang, "/account/")
            self.assertIn(f'class="tool-btn account-btn" href="{account}"', text, path)

    def test_chapter_has_every_verse_in_order(self):
        data = self.chapter_data()
        verses = list(dict.fromkeys(v for r in data["records"] for v in r["refs"]))
        self.assertEqual(verses, [f"JHN.1.{v}" for v in range(1, 52)])
        # English for every sentence; Spanish and Swahili for 1:1-18 so far,
        # French for the whole chapter.
        self.assertEqual(data["languages"], ["en", "es", "fr", "sw"])
        self.assertTrue(all("fr" in r["renderings"] for r in data["records"]))
        self.assertTrue(all("en" in r["renderings"] for r in data["records"]))

    def test_each_verse_words_are_covered_once(self):
        # A verse may hold several sentences (1:21 has five) and a sentence
        # may cross verses; together the records cover every word once.
        data = self.chapter_data()
        seen = {}
        for r in data["records"]:
            for tid in r["source"]["tokens"]:
                self.assertNotIn(tid, seen, f"{tid} in {seen.get(tid)} and {r['id']}")
                seen[tid] = r["id"]
        for vid in dict.fromkeys(v for r in data["records"] for v in r["refs"]):
            words = {t["id"] for t in data["words"][vid]}
            self.assertEqual({t for t in seen if t in words}, words, vid)

    def test_chapter_has_a_notes_section(self):
        page = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="notes"', page)
        self.assertIn("Small letters mark footnotes", page)
        reader = (self.out / "reader.js").read_text(encoding="utf-8")
        # Alternatives a decision set aside are never offered as possible.
        self.assertIn('d.uncertain ? "fn_or" : "also"', reader)

    def test_read_page_lists_every_passage(self):
        read = (self.out / "read" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/jhn/1/"', read)
        self.assertIn('href="/php/4/"', read)
        # Each card opens with its passage's first verse, from the content.
        self.assertEqual(read.count('class="a-card p-card"'), len(build_site.chapters()))
        first = build_site.load_chapter("JHN", 1)[0][0]
        self.assertIn(build_site.plain(first["renderings"]["en"]["B"]), read)

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

    def test_fonts_are_self_hosted_with_their_licences(self):
        css = (self.out / "style.css").read_text(encoding="utf-8")
        files = re.findall(r"url\(/fonts/([^)]+)\)", css)
        self.assertTrue(files)
        for name in files:
            self.assertTrue((self.out / "fonts" / name).is_file(), name)
        for script in ("greek", "greek-ext"):
            self.assertIn(f"gentium-book-plus-{script}-400-normal.woff2", files)
        self.assertIn("noto-serif-hebrew-hebrew-400-normal.woff2", files)
        for licence in ("OFL-Gentium.txt", "OFL-NotoSerifHebrew.txt"):
            self.assertIn("SIL Open Font License", (ROOT / "web" / "fonts" / licence).read_text(encoding="utf-8"))
        home = (self.out / "index.html").read_text(encoding="utf-8")
        preload = re.search(r'<link rel="preload" href="/fonts/([^"]+)"', home)[1]
        self.assertIn(preload, files)

    def test_about_page_credits_sources(self):
        about = (self.out / "about" / "index.html").read_text(encoding="utf-8")
        for name in ("SBL Greek New Testament", "MACULA Greek", "Open Scriptures Hebrew Bible"):
            self.assertIn(name, about)

    def test_about_page_renders_markdown_links(self):
        about = (self.out / "about" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<a href="https://github.com/seven1m/open-bibles">seven1m/open-bibles</a>', about)
        self.assertNotIn("](", about)

    def test_home_page_example_has_curly_quotes(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        why = re.search(r'<p class="why">(.*?)</p>', home, re.S)[1]
        self.assertNotIn('"', why)
        self.assertNotIn("&quot;", why)

    def test_chapter_data_has_curly_quotes(self):
        for r in self.chapter_data()["records"]:
            texts = [t for levels in r["renderings"].values() for t in levels.values()]
            texts += [r["literal_gloss"]] + [d["reason"] for d in r["decisions"]]
            for text in texts:
                self.assertNotRegex(text, "[\"']", r["id"])

    def test_chapter_settings_fold_behind_a_toggle(self):
        page = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertIn('aria-controls="settings"', page)
        self.assertIn('<div class="settings" id="settings">', page)

    def test_assets_are_versioned_by_content(self):
        # A deploy must never pair new pages with a stylesheet the browser
        # kept from the last one: each asset URL carries its content hash.
        home = (self.out / "index.html").read_text(encoding="utf-8")
        chapter = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        for name, page in (("style.css", home), ("site.js", home), ("reader.js", chapter)):
            m = re.search(r'"/%s\?v=([0-9a-f]{10})"' % re.escape(name), page)
            self.assertTrue(m, name)
            digest = hashlib.sha256((self.out / name).read_bytes()).hexdigest()[:10]
            self.assertEqual(m[1], digest, name)

    def test_header_dropdowns_list_passages_and_articles(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        header = re.search(r'<header class="site">(.*?)</header>', home, re.S)[1]
        for key in ("read", "articles", "about"):
            self.assertIn(f'aria-controls="dd-{key}"', header)
            self.assertIn(f'<div class="dropdown', header)
        self.assertIn('href="/jhn/1/"', header)
        self.assertIn('href="/php/4/"', header)
        for a in build_site.load_articles():
            self.assertIn(f'href="{build_site.article_url(a)}"', header)
        # The current section's trigger is marked on its pages.
        articles = (self.out / "articles" / "index.html").read_text(encoding="utf-8")
        self.assertRegex(articles, r'class="nav-link nav-trigger active"[^>]*aria-controls="dd-articles"')
        # ...and the dropdown link to the page itself tells a screen reader.
        chapter = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertRegex(chapter, r'class="chap(?: part)?" href="/jhn/1/" aria-current="page"')
        self.assertNotIn('href="/php/4/" aria-current', chapter)

    def test_interface_fonts_are_self_hosted_with_their_licences(self):
        css = (self.out / "style.css").read_text(encoding="utf-8")
        files = re.findall(r"url\(/fonts/([^)]+)\)", css)
        self.assertTrue(files)
        for name in files:
            self.assertTrue((self.out / "fonts" / name).is_file(), name)
        for licence in ("OFL-Fraunces.txt", "OFL-HankenGrotesk.txt"):
            self.assertIn("SIL Open Font License", (ROOT / "web" / "fonts" / licence).read_text(encoding="utf-8"))
        home = (self.out / "index.html").read_text(encoding="utf-8")
        preload = re.search(r'<link rel="preload" href="/fonts/([^"]+)"', home)[1]
        self.assertIn(preload, files)

    def test_whole_chapters_are_named_without_a_verse_range(self):
        names = {(p.book, p.chapter): (p.name, p.complete) for p in build_site.passages()}
        self.assertEqual(names[("PHP", 2)], ("Philippians 2", True))
        page = (self.out / "php" / "2" / "index.html").read_text(encoding="utf-8")
        self.assertIn("<title>Philippians 2 · Open Word Bible</title>", page)
        self.assertNotIn("Sample passage", page)

    def test_reader_links_every_chapter_and_its_neighbours(self):
        ps = build_site.passages()
        for i, p in enumerate(ps):
            page = (self.out / p.url.strip("/") / "index.html").read_text(encoding="utf-8")
            strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
            for q in ps:
                if q.book == p.book:
                    self.assertIn(f'href="{q.url}"', strip)
            self.assertIn(f'href="{p.url}" aria-current=page', strip)
            turns = re.search(r'<nav class="turns"(.*?)</nav>', page, re.S)[1]
            if i > 0:
                self.assertIn(f'href="{ps[i - 1].url}" rel="prev"', turns)
            if i + 1 < len(ps):
                self.assertIn(f'href="{ps[i + 1].url}" rel="next"', turns)

    def test_read_page_groups_chapters_by_book(self):
        read = (self.out / "read" / "index.html").read_text(encoding="utf-8")
        for book, chaps in build_site.books():
            section = re.search(rf'<section class="book-group" id="{book.lower()}"(.*?)</section>', read, re.S)[1]
            for p in chaps:
                self.assertIn(f'href="{p.url}"', section)
        self.assertIn("4 of 4 chapters, complete", read)


class ExtractTest(unittest.TestCase):
    def test_extracts_are_up_to_date(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_tokens.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
