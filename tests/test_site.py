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
        # English for every sentence; Spanish for 1:1-18 so far, French and
        # Swahili for the whole chapter.
        self.assertEqual(data["languages"], ["en", "es", "fr", "sw"])
        self.assertTrue(all("fr" in r["renderings"] for r in data["records"]))
        self.assertTrue(all("sw" in r["renderings"] for r in data["records"]))
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
        self.assertIn("Tap a small letter to read its footnote", page)
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

    def test_a_sentence_across_a_chapter_break_is_on_both_pages(self):
        # John 7:53-8:1 is one sentence. It opens the bracketed, disputed
        # passage 7:53-8:11 with "[" and the note on the manuscripts, so John
        # 8 needs it as much as John 7 does.
        seven, eight = self.chapter_data("jhn/7"), self.chapter_data("jhn/8")
        self.assertEqual(seven["records"][-1]["id"], "JHN.7.53.s1")
        first = eight["records"][0]
        self.assertEqual(first["id"], "JHN.7.53.s1")
        self.assertTrue(first["renderings"]["en"]["B"].startswith("["))
        self.assertTrue(any(d["category"] == "text_variant" and d["footnote"] for d in first["decisions"]))
        self.assertEqual(eight["title"], "John 8")
        names = {p.chapter: (p.name, p.complete) for p in build_site.passages() if p.book == "JHN"}
        self.assertEqual(names[7], ("John 7", True))
        self.assertEqual(names[8], ("John 8", True))
        # Counted once on the home page.
        ids = [r["id"] for r in build_site.all_records()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_cards_quote_the_first_verse_outside_a_disputed_passage(self):
        records = build_site.load_chapter("JHN", 8)[0]
        self.assertEqual(build_site.opening(records, 8)[1], "JHN.8.12")
        self.assertIn("I am the light of the world", build_site.opening_verse(records, 8))
        records = build_site.load_chapter("JHN", 7)[0]
        self.assertEqual(build_site.opening(records, 7)[1], "JHN.7.1")

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

    def test_measures_control_only_where_a_passage_has_units(self):
        gen6 = (self.out / "gen" / "6" / "index.html").read_text(encoding="utf-8")
        gen1 = (self.out / "gen" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-setting="units"', gen6)
        self.assertNotIn('data-setting="units"', gen1)
        self.assertIn("{{units:450 feet|300 cubits}}", json.dumps(self.chapter_data("gen/6")["records"]))

    def test_old_testament_pages_offer_the_divine_name(self):
        # The divine name (the LORD or Yahweh) on Old Testament pages, the
        # title Christ (Christ or Messiah) on New Testament ones.
        gen = (self.out / "gen" / "2" / "index.html").read_text(encoding="utf-8")
        jhn = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-setting="divine_name"', gen)
        self.assertIn('id="hint-divine_name"', gen)
        self.assertNotIn('data-setting="christos"', gen)
        self.assertIn('data-setting="christos"', jhn)
        self.assertNotIn('data-setting="divine_name"', jhn)
        text = json.dumps(self.chapter_data("gen/2")["records"])
        self.assertIn("{{divine_name:the LORD|Yahweh}}", text)

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

    def test_home_page_progress_is_for_its_language(self):
        for lang in build_site.LANGUAGES:
            home = (self.out / build_site.url(lang, "/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            progress = home[home.index('class="progress"'):home.index('class="latest"')]
            records = [r for r in build_site.all_records() if lang in r["renderings"]]
            decisions = sum(d["language"] in (None, lang) for r in records for d in r["decisions"])
            self.assertIn(f"<b>{len(records)}</b>", progress)
            self.assertIn(f"<b>{decisions}</b>", progress)
            shown = {(r.book, r.chapter) for r in map(build_site.refs.parse, (r["refs"][0] for r in records))}
            for p in build_site.passages():
                link = f'href="{build_site.url(lang, p.url)}"'
                self.assertEqual(link in progress, (p.book, p.chapter) in shown, (lang, p.url))

    def test_header_footer_and_read_page_list_only_the_page_language(self):
        for lang in build_site.LANGUAGES:
            shown = {(p.book, p.chapter) for p in build_site.passages_in(lang)}
            books = {b for b, _ in shown}
            read = (self.out / build_site.url(lang, "/read/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            header = re.search(r"<header.*?</header>", read, re.S)[0]
            footer = re.search(r"<footer.*?</footer>", read, re.S)[0]
            for p in build_site.passages():
                link = f'href="{build_site.url(lang, p.url)}"'
                self.assertEqual(link in header, (p.book, p.chapter) in shown, (lang, p.url))
                self.assertEqual(f'id="{p.book.lower()}"' in read, p.book in books, (lang, p.book))
                book_link = f'href="{build_site.url(lang, f"/read/#{p.book.lower()}")}"'
                self.assertEqual(book_link in footer, p.book in books, (lang, p.book))

    def test_reader_navigation_lists_only_the_page_language(self):
        for lang in build_site.LANGUAGES:
            shown = {(p.book, p.chapter) for p in build_site.passages_in(lang)}
            for p in build_site.passages():
                page = (self.out / build_site.url(lang, p.url).lstrip("/") / "index.html").read_text(encoding="utf-8")
                strip = re.search(r'<nav class="chapstrip".*?</nav>', page, re.S)[0]
                turns = re.search(r'<nav class="turns".*?</nav>', page, re.S)[0]
                linked = {(q.book, q.chapter) for q in build_site.passages()
                          if f'href="{build_site.url(lang, q.url)}"' in strip + turns}
                if (p.book, p.chapter) in shown:
                    self.assertLessEqual(linked, shown, (lang, p.url))
                else:  # a page not yet in lang is in English, and links like one
                    self.assertIn((p.book, p.chapter), linked, (lang, p.url))

    def test_read_page_cards_count_the_page_language(self):
        for lang in build_site.LANGUAGES:
            for p in build_site.passages_in(lang):
                card = build_site.passage_card(p.book, p.chapter, lang)
                shown = [d for r in p.records for d in r["decisions"] if d["language"] in (None, lang)]
                self.assertIn(build_site.t(lang, "card.meta", verses=p.verses, sentences=len(p.records),
                                           decisions=len(shown),
                                           uncertain=sum(d["uncertain"] for d in shown)), card)

    def test_paragraphs_follow_the_greek(self):
        # SBLGNT capitalises a paragraph's first word; John 2 has four.
        self.assertEqual(self.chapter_data("jhn/2")["paragraphs"],
                         ["JHN.2.1.s1", "JHN.2.12.s1", "JHN.2.13.s1", "JHN.2.23.s1"])
        # A capitalised quotation after a raised dot does not open one.
        self.assertNotIn("JHN.4.29.s1", self.chapter_data("jhn/4")["paragraphs"])
        # The Hebrew codex marks paragraphs with pe or samekh: Genesis 1's days.
        self.assertEqual(self.chapter_data("gen/1")["paragraphs"],
                         ["GEN.1.1.s1", "GEN.1.6.s1", "GEN.1.9.s1", "GEN.1.14.s1", "GEN.1.20.s1", "GEN.1.24.s1"])

    def test_headings_stand_above_paragraphs(self):
        ids = {r["id"] for b, c in build_site.chapters() for r in build_site.load_chapter(b, c)[0]}
        for rid, heading in build_site.headings().items():
            self.assertIn(rid, ids, rid)
            self.assertIn("en", heading, rid)
            book, chapter = rid.split(".")[:2]
            data = self.chapter_data(f"{book.lower()}/{chapter}")
            self.assertIn(rid, data["paragraphs"], rid)
            self.assertEqual(data["headings"][rid], heading)

    def test_chapter_strip_shows_the_whole_book(self):
        page = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
        done = {p.chapter for p in build_site.passages() if p.book == "JHN"}
        pills = re.findall(r'class="chap[^"]*"[^>]*>(\d+)<', strip)
        self.assertEqual([int(n) for n in pills], list(range(1, build_site.BOOK_CHAPTERS["JHN"] + 1)))
        self.assertEqual(len(re.findall(r'class="chap none"', strip)), 21 - len(done))

    def test_aligned_records_carry_their_ranges(self):
        records = self.chapter_data("jhn/2")["records"]
        linked = [r for r in records if r["links"]]
        self.assertTrue(linked)
        for r in linked:
            text = r["renderings"]["en"]["B"]
            for (start, end, tokens), al in zip(r["links"]["en"]["B"], r["alignments"]):
                self.assertEqual(al["tokens"], tokens)
                # Curly quotes on the page keep every range in place.
                self.assertEqual(build_site.smart_quotes(al["target_span"]), text[start:end])

    def test_word_uses_index(self):
        text = (self.out / "word-uses.json").read_text(encoding="utf-8")
        index = json.loads(text)
        data = self.chapter_data("jhn/2")
        # Each page points at this build's copy of the index.
        self.assertEqual(data["uses"], build_site.word_uses()[1])
        self.assertIn(hashlib.sha256(text.encode()).hexdigest()[:10], data["uses"])
        # Every word of a translated sentence is listed at its verse, once.
        record = data["records"][0]
        for word in data["words"]["JHN.2.1"]:
            if word["id"] in record["source"]["tokens"]:
                self.assertIn("JHN.2.1", index[word["lemma"]])
        for places in index.values():
            self.assertEqual(len(places), len(set(places)))

    def test_reader_has_a_reading_view(self):
        page = (self.out / "jhn" / "2" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<span class="seg" data-setting="view">', page)
        self.assertIn('id="hint-view"', page)
        reader = (self.out / "reader.js").read_text(encoding="utf-8")
        # Copying from the passage adds its reference and level.
        self.assertIn('addEventListener("copy"', reader)
        self.assertIn('" (Open Word Bible, "', reader)

    def test_reader_can_go_to_a_reference(self):
        page = (self.out / "jhn" / "2" / "index.html").read_text(encoding="utf-8")
        strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
        self.assertIn('class="chap-goto" data-open-search', strip)
        search = (self.out / "search.js").read_text(encoding="utf-8")
        # A reference is the palette's first row, so Enter goes straight to it.
        self.assertLess(search.index('fill(ui("go_to")'), search.index('fill(ui("show_all")'))

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
