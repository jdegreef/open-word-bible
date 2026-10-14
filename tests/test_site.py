import hashlib
import html
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from tests.site_build import built_site  # noqa: E402


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def chapter_data(self, path="jhn/1"):
        page = (self.out / path / "index.html").read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="owb-data">(.*?)</script>', page, re.S)
        return json.loads(m[1])

    def test_pages_exist(self):
        for rel in ("index.html", "read/index.html", "jhn/1/index.html", "php/4/index.html",
                    "about/index.html", "404.html", "style.css", "reader.js",
                    "sitemap.xml", "robots.txt", "favicon.svg"):
            self.assertTrue((self.out / rel).is_file(), rel)

    def test_poetry_keeps_its_lines_for_the_reader_only(self):
        # The reader gets the line markers to set Psalm 23 as poetry; every
        # text the build writes on one line reads them as spaces.
        data = self.chapter_data("psa/23")
        self.assertTrue(any("\\q " in r["renderings"]["en"]["B"] for r in data["records"]))
        self.assertEqual(build_site.plain("my shepherd; \\q I will never be in need."),
                         "my shepherd; I will never be in need.")
        records = build_site.load_chapter("PSA", 23)[0]
        self.assertNotIn("\\q", build_site.opening_verse(records, 23))
        page = (self.out / "psa" / "23" / "index.html").read_text(encoding="utf-8")
        head = page.split("<body", 1)[0]
        self.assertNotIn("\\q", head)

    def test_account_pages_are_built_but_not_indexed(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        for name, marker in (("account", 'id="name-form"'), ("login", 'id="login-form"'),
                             ("reset-password", 'id="reset-form"')):
            page = (self.out / name / "index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex">', page)
            self.assertIn(marker, page)
            self.assertNotIn(f"/{name}/", sitemap)
        self.assertTrue((self.out / "account.js").is_file())
        login = (self.out / "login" / "index.html").read_text(encoding="utf-8")
        # Sign in, create an account, reset: one page, sign in showing first.
        self.assertIn('<span data-for="sign-in">Welcome back</span>', login)
        self.assertIn('<span data-for="sign-up" hidden>Create your account</span>', login)
        self.assertIn('id="google"', login)
        # Every page knows the API and has the header's account menu.
        for path in self.out.rglob("index.html"):
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'<meta name="owb-api" content="{build_site.API_URL}">', text, path)
            lang = re.search(r'<html lang="([a-z]+)">', text)[1]
            self.assertIn(f'<a class="sign-in-btn" href="{build_site.url(lang, "/login/")}" data-login>', text, path)
            self.assertIn(f'<a class="pop-item" href="{build_site.url(lang, "/account/")}">', text, path)

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

    def chapter_text(self, path):
        page = (self.out / path / "index.html").read_text(encoding="utf-8")
        return page, re.search(r'<div class="text" id="text">(.*?)</div>\s*<section class="notes"', page, re.S)[1]

    def test_chapter_text_is_in_the_page(self):
        # Without JavaScript the page still has the Balanced text at the
        # default settings, a span per verse as the reader draws it.
        for path in ("1ti/5", "jhn/1", "gen/1"):
            page, text = self.chapter_text(path)
            data = self.chapter_data(path)
            verses = [str(build_site.refs.parse(v).verse) for v in
                      dict.fromkeys(v for r in data["records"] for v in r["refs"])]
            self.assertEqual(list(dict.fromkeys(re.findall(r'data-v="([^"]+)"', text))), verses, path)
            self.assertEqual(re.findall(r"<sup>([^<]+)</sup>", text), verses, path)
            self.assertNotIn("{{", text)
            self.assertNotIn("\\v ", text)
            for r in data["records"]:
                default = build_site.markup.render(r["renderings"]["en"]["B"])
                first = build_site.markup.VERSE.split(default)[0].strip()
                self.assertIn(html.escape(first, quote=False), text, r["id"])
                self.assertIn(f'data-record="{r["id"]}"', text)
            for heading in data["headings"].values():
                shown = html.escape(build_site.markup.render(heading["en"]), quote=False)
                self.assertIn(f'<h2 class="section-head">{shown}</h2>', text)
            self.assertIn("<noscript>", page)
            self.assertIn(build_site.t("en", "reader.noscript", level="Balanced"), page)
        self.assertIn('<sup class="fn" aria-hidden="true"><span class="fn-mark">a</span></sup>',
                      self.chapter_text("1ti/5")[1])

    def test_chapter_text_falls_back_to_english(self):
        # A sentence not yet in the page's language is shown in English, in
        # grey, under the notice that says so.
        for lang in build_site.LANGUAGES:
            for p in build_site.passages():
                missing = [r for r in p.records if lang not in r["renderings"]]
                if not missing:
                    continue
                page, text = self.chapter_text(build_site.url(lang, p.url).strip("/"))
                self.assertIn('class="verse fallback" lang="en" data-v=', text)
                self.assertIn(f'data-record="{missing[0]["id"]}"', text)
                self.assertNotIn('id="partial" hidden', page)
                return
        self.skipTest("every chapter is in every language")

    def test_disputed_passage_is_set_apart_in_the_text(self):
        _, text = self.chapter_text("jhn/8")
        block = re.search(r'<div class="disputed-block"><div class="disputed-note">.*?</div>(.*?)</div>', text, re.S)
        self.assertIsNotNone(block)
        self.assertIn('data-v="7:53"', block[1])
        self.assertIn('data-v="11"', block[1])
        self.assertNotIn('data-v="12"', block[1])

    def test_chapter_pages_carry_linked_data(self):
        for path, source in (("1ti/5", "SBLGNT"), ("gen/1", "Open Scriptures Hebrew Bible"),
                             ("es/jhn/1", "SBLGNT")):
            page = (self.out / path / "index.html").read_text(encoding="utf-8")
            raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)[1]
            data = json.loads(raw)
            self.assertEqual(data["@type"], "Chapter")
            self.assertEqual(data["url"], build_site.SITE_URL + "/" + path + "/")
            self.assertEqual(data["inLanguage"], "es" if path.startswith("es/") else "en")
            self.assertEqual(data["isPartOf"]["name"], "Open Word Bible")
            self.assertEqual(data["license"], "https://creativecommons.org/publicdomain/zero/1.0/")
            # Nothing is reviewed yet.
            self.assertEqual(data["creativeWorkStatus"], "Draft")
            self.assertIn(source, data["isBasedOn"]["name"])
            self.assertEqual(data["translationOfWork"], data["isBasedOn"])
        # Nothing in it can close its script element.
        records = build_site.load_chapter("1TI", 5)[0]
        title = "</script><script>alert(1)</script>"
        script = build_site.chapter_ld(records, "1TI", 5, title)
        self.assertEqual(script.count("</"), 1)
        self.assertEqual(json.loads(script[script.index(">") + 1:-len("</script>")])["name"], title)

    def test_footer_counts_the_books_not_started(self):
        page = (self.out / "1ti" / "5" / "index.html").read_text(encoding="utf-8")
        index = re.search(r'<nav class="foot-books".*?</nav>', page, re.S)[0]
        ot = build_site.refs.OT_CODES
        have = {b for b, _ in build_site.books("en")}
        missing = [code for code in ot if code not in have]
        for code in ot:
            self.assertEqual(f'>{build_site.BOOK_NAMES[code]["en"]}<' in index,
                             code in have or len(missing) == 1, code)
        if len(missing) > 1:
            self.assertIn(f'href="/read/">{build_site.t("en", "footer.not_started", n=len(missing))}</a>', index)

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
        example = home[home.index('class="example"'):home.index('class="points-wrap"')]
        # The text as read, without the tags that mark aligned words and settings.
        text = re.sub(r"<[^>]+>", "", example)
        self.assertEqual(len(build_site.EXAMPLES), 2)
        for book, chapter, record_id, decision_id in build_site.EXAMPLES:
            records, words = build_site.load_chapter(book, chapter)
            record = next(r for r in records if r["id"] == record_id)
            decision = next(d for d in record["decisions"] if d["id"] == decision_id)
            for level in "LBR":
                self.assertIn(html.escape(build_site.plain(record["renderings"]["en"][level]), quote=False), text)
            marked = [w["text"] for v in record["refs"] for w in words[v] if w["id"] in decision["tokens"]]
            self.assertTrue(marked)
            for word in marked:
                self.assertIn(f"<mark>{word}</mark>", example)
            for tid in record["source"]["tokens"]:
                if any(w["id"] == tid for v in record["refs"] for w in words[v]):
                    self.assertIn(f'data-t="{tid}"', example)
            self.assertIn(f'href="/{book.lower()}/{chapter}/"', example)
        # Aligned words light up their English; the divine name can switch.
        self.assertIn('class="al" data-t="n43001001002"', example)
        self.assertIn('data-switch="divine_name"', example)
        self.assertIn(f"<b>{len(build_site.all_records())}</b>", home)

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

    def test_beliefs_page_sets_out_the_creed_vision_and_values(self):
        page = (self.out / "about" / "beliefs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("I believe in God, the Father almighty", page)
        self.assertIn("Apostles' Creed", page)
        for heading in ("Our vision", "Our mission", "What guides the work"):
            self.assertIn(f"<h2>{heading}</h2>", page)
        self.assertEqual(page.count("<li><strong>"), 5)
        # The About menu and the footer both link to it.
        self.assertGreaterEqual(page.count('href="/about/beliefs/"'), 2)

    def test_about_page_renders_markdown_links(self):
        about = (self.out / "about" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<a href="https://github.com/seven1m/open-bibles">seven1m/open-bibles</a>', about)
        self.assertNotIn("](", about)

    def test_home_page_example_has_curly_quotes(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        why = re.search(r'<p class="why">(.*?)</p>', home, re.S)[1]
        self.assertNotIn('"', why)
        self.assertNotIn("&quot;", why)

    def test_home_page_searches_in_its_language(self):
        for lang in build_site.LANGUAGES:
            home = (self.out / build_site.url(lang, "/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            form = re.search(r'<form class="hero-search" action="([^"]+)"', home)
            self.assertEqual(form[1], build_site.url(lang, "/search/"))
            for q in build_site.catalog(lang)["search.examples"]:
                self.assertIn(f'?q={html.escape(q.replace(" ", "+"))}"', home)

    def test_verses_of_the_day_are_drafted_whole_sentences(self):
        self.assertEqual(len(build_site.VERSES_OF_THE_DAY), len(set(build_site.VERSES_OF_THE_DAY)))
        for lang in build_site.LANGUAGES:
            verses = build_site.verses_of_the_day(lang)
            self.assertEqual(len(verses), len(build_site.VERSES_OF_THE_DAY))
            for vid, v in zip(build_site.VERSES_OF_THE_DAY, verses):
                # The verse ends a sentence, so it reads on its own.
                self.assertRegex(v["t"], r"[.?!][”’]?$", vid)
        home = (self.out / "index.html").read_text(encoding="utf-8")
        data = re.search(r'<script type="application/json" class="votd-data">(.*?)</script>', home, re.S)[1]
        self.assertEqual(json.loads(data), build_site.verses_of_the_day("en"))

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
        for name, page in (("style.css", home), ("site.js", home), ("markup.js", chapter),
                           ("reader.js", chapter)):
            m = re.search(r'"/%s\?v=([0-9a-f]{10})"' % re.escape(name), page)
            self.assertTrue(m, name)
            digest = hashlib.sha256((self.out / name).read_bytes()).hexdigest()[:10]
            self.assertEqual(m[1], digest, name)

    def test_header_dropdowns_list_passages_and_articles(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        header = re.search(r'<header class="site">(.*?)</header>', home, re.S)[1]
        for key in ("read", "articles", "about"):
            self.assertIn(f'aria-controls="dd-{key}"', header)
            self.assertIn('<div class="dropdown', header)
        # A line per book, linking to its chapters on the Read page.
        self.assertIn('href="/read/#jhn"', header)
        self.assertIn('href="/read/#php"', header)
        self.assertNotIn('class="chap', header)
        # Continue reading heads the Read menu, hidden until web/site.js
        # finds a place; GitHub is under About, not a header button.
        read_panel = header[header.index('id="dd-read"'):header.index('id="dd-articles"')]
        self.assertIn('<a class="dd-resume" data-resume hidden', read_panel)
        self.assertNotIn(f'class="tool-btn" href="{build_site.GITHUB_URL}"', header)
        about_panel = header[header.index('id="dd-about"'):]
        self.assertIn(f'href="{build_site.GITHUB_URL}"', about_panel)
        # ...grouped by testament, Old before New.
        read = header[header.index('id="dd-read"'):header.index('id="dd-articles"')]
        self.assertLess(read.index(">Old Testament<"), read.index('href="/read/#gen"'))
        self.assertLess(read.index('href="/read/#gen"'), read.index(">New Testament<"))
        self.assertLess(read.index(">New Testament<"), read.index('href="/read/#jhn"'))
        # The first few articles of each section, and a link to the rest.
        articles_ = sorted(build_site.load_articles(), key=lambda a: a["order"])
        for key in build_site.SECTIONS:
            section = [a for a in articles_ if a["section"] == key]
            for i, a in enumerate(section):
                linked = f'href="{build_site.article_url(a)}"' in header
                self.assertEqual(linked, i < build_site.MENU_ARTICLES, a["slug"])
            if len(section) > build_site.MENU_ARTICLES:
                self.assertIn(f'href="/articles/#{key}"', header)
        self.assertNotIn("min read", header)
        # The current section's trigger is marked on its pages.
        articles = (self.out / "articles" / "index.html").read_text(encoding="utf-8")
        self.assertRegex(articles, r'class="nav-link nav-trigger active"[^>]*aria-controls="dd-articles"')
        # ...and the dropdown link to the page itself tells a screen reader.
        chapter = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        chapter_header = re.search(r'<header class="site">(.*?)</header>', chapter, re.S)[1]
        self.assertIn('data-book="jhn" aria-current="true"', chapter_header)
        self.assertNotIn('data-book="php" aria-current', chapter_header)

    def test_interface_fonts_are_self_hosted_with_their_licences(self):
        css = (self.out / "style.css").read_text(encoding="utf-8")
        files = re.findall(r"url\(/fonts/([^)]+)\)", css)
        self.assertTrue(files)
        for name in files:
            self.assertTrue((self.out / "fonts" / name).is_file(), name)
        self.assertIn("atkinson-hyperlegible-latin-400-normal.woff2", files)
        for licence in ("OFL-Fraunces.txt", "OFL-HankenGrotesk.txt", "OFL-AtkinsonHyperlegible.txt"):
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
            progress = home[home.index('class="progress"'):home.index('class="involve"')]
            records = [r for r in build_site.all_records() if lang in r["renderings"]]
            decisions = sum(d["language"] in (None, lang) for r in records for d in r["decisions"])
            self.assertIn(f"<b>{len(records)}</b>", progress)
            self.assertIn(f"<b>{decisions}</b>", progress)
            # The map has a tile for every book, linked once it has a
            # sentence in lang, and no chapter links.
            shown = {build_site.refs.parse(r["refs"][0]).book for r in records}
            self.assertEqual(progress.count('<li><a class="map-book') + progress.count('<li><span class="map-book'),
                             len(build_site.refs.BOOK_CODES))
            for book in build_site.refs.BOOK_CODES:
                link = f'href="{build_site.url(lang, f"/read/#{book.lower()}")}"'
                self.assertEqual(link in progress, book in shown, (lang, book))
            for p in build_site.passages():
                self.assertNotIn(f'href="{build_site.url(lang, p.url)}"', progress, (lang, p.url))

    def test_header_footer_and_read_page_list_only_the_page_language(self):
        for lang in build_site.LANGUAGES:
            shown = {(p.book, p.chapter) for p in build_site.passages_in(lang)}
            books = {b for b, _ in shown}
            read = (self.out / build_site.url(lang, "/read/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            header = re.search(r"<header.*?</header>", read, re.S)[0]
            footer = re.search(r"<footer.*?</footer>", read, re.S)[0]
            for p in build_site.passages():
                self.assertEqual(f'id="{p.book.lower()}"' in read, p.book in books, (lang, p.book))
                book_link = f'href="{build_site.url(lang, f"/read/#{p.book.lower()}")}"'
                self.assertEqual(book_link in header, p.book in books, (lang, p.book))
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

    def test_summary_stands_under_the_title(self):
        page = (self.out / "1ti" / "5" / "index.html").read_text(encoding="utf-8")
        summary = html.escape(build_site.summaries()[("1TI", 5)]["en"])
        self.assertRegex(page, r'<h1 id="title">[^<]*</h1>\s*<p class="chapter-summary">' + re.escape(summary))
        # A page in another language shows the English summary only where the
        # chapter itself reads in English, and marks it so.
        records = build_site.load_chapter("1TI", 5)[0]
        if not any("es" in r["renderings"] for r in records) and "es" not in build_site.summaries()[("1TI", 5)]:
            page = (self.out / "es" / "1ti" / "5" / "index.html").read_text(encoding="utf-8")
            self.assertIn('<p class="chapter-summary" lang="en">', page)
        with_es = [{"renderings": {"en": {}, "es": {}}}]
        self.assertEqual(build_site.chapter_summary("1TI", 5, with_es, "es"), "")
        self.assertEqual(build_site.chapter_summary("JHN", 999, records, "en"), "")

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

    def test_name_cards_match_the_word_data(self):
        import glob
        words = {}
        for path in glob.glob(str(build_site.ROOT / "data" / "*" / "*.json")):
            if "/grc/" in path or "/hbo/" in path:
                for vid, ws in json.loads(Path(path).read_text(encoding="utf-8"))["verses"].items():
                    for w in ws:
                        words.setdefault((build_site.word_strong(w), w["lemma"]), set()).add(vid)
        for (strong, lemma), senses in build_site.name_cards().items():
            # Every lemma is copied from the source data, never typed.
            self.assertIn((strong, lemma), words, (strong, lemma))
            listed = [v for s in senses for v in s.get("verses", [])]
            self.assertEqual(len(listed), len(set(listed)), strong)
            self.assertLessEqual(sum("verses" not in s for s in senses), 1, strong)
            self.assertTrue(set(listed) <= words[(strong, lemma)], strong)
        # A page's cards resolve a shared name by verse: two Lamechs.
        gen4 = self.chapter_data("gen/4")["cards"]["list"]
        gen5 = self.chapter_data("gen/5")["cards"]["list"]
        self.assertIn("Lamech, descendant of Cain", [c["title"] for c in gen4])
        self.assertIn("Lamech, father of Noah", [c["title"] for c in gen5])

    def test_site_can_be_installed_and_read_offline(self):
        manifest = json.loads((self.out / "manifest.webmanifest").read_text(encoding="utf-8"))
        for icon in manifest["icons"]:
            self.assertTrue((self.out / icon["src"].lstrip("/")).is_file(), icon["src"])
        sw = (self.out / "sw.js").read_text(encoding="utf-8")
        self.assertNotIn("__PRECACHE__", sw)
        self.assertNotIn("__VERSION__", sw)
        precache = json.loads(re.search(r"var PRECACHE = (\[.*?\]);", sw)[1])
        for u in precache:
            path = u.split("?")[0].lstrip("/")
            self.assertTrue((self.out / path).is_file() or (self.out / path / "index.html").is_file(), u)
        for lang in build_site.LANGUAGES:
            self.assertIn(build_site.url(lang, "/offline/"), precache)
        page = (self.out / "jhn" / "2" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="manifest" href="/manifest.webmanifest">', page)
        self.assertNotIn("/offline/", (self.out / "sitemap.xml").read_text(encoding="utf-8"))

    def test_reader_can_read_aloud(self):
        for code in build_site.LANGUAGES:
            page = (self.out / build_site.url(code, "/jhn/2/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
            # Hidden until reader.js finds the browser can speak.
            self.assertIn('id="listen-start" hidden', strip)
            ui = self.chapter_data(build_site.url(code, "/jhn/2").lstrip("/"))["ui"]
            for key in ("listen_bar", "listen_play", "listen_pause", "listen_prev", "listen_next",
                        "listen_speed", "listen_voice", "listen_stop", "listen_no_voice"):
                self.assertTrue(ui.get(key), (code, key))

    def test_saved_verses_page(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("/saved/", sitemap)
        for code in build_site.LANGUAGES:
            rel = build_site.url(code, "/saved/").lstrip("/")
            page = (self.out / rel / "index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex">', page)
            data = json.loads(html.unescape(re.search(r'data-saved="([^"]*)"', page)[1]))
            self.assertEqual(data["order"], [b for b, _ in build_site.books()])
            # Each book's chapter address is the reader's, in the page language.
            self.assertEqual(data["chapters"]["JHN"].replace("{c}", "3"), build_site.url(code, "/jhn/3/"))
            self.assertTrue((self.out / build_site.url(code, "/jhn/3/").lstrip("/") / "index.html").is_file())
            chapter = self.chapter_data(build_site.url(code, "/jhn/2").lstrip("/"))
            self.assertEqual(chapter["saved"], build_site.url(code, "/saved/"))
            for key in ("bookmark", "bookmarked", "highlight", "hl_yellow", "hl_green", "hl_blue",
                        "hl_pink", "saved_all"):
                self.assertTrue(chapter["ui"].get(key), (code, key))

    def test_read_page_groups_chapters_by_book(self):
        read = (self.out / "read" / "index.html").read_text(encoding="utf-8")
        for book, chaps in build_site.books():
            section = re.search(rf'<section class="book-group" id="{book.lower()}"(.*?)</section>', read, re.S)[1]
            for p in chaps:
                self.assertIn(f'href="{p.url}"', section)
        self.assertIn("4 of 4 chapters, complete", read)
        self.assertIn("1 chapter, complete", read)
        self.assertNotIn("1 of 1 chapters", read)
        # An index of the books first, each linked to its section.
        index = re.search(r'<nav class="book-index".*?</nav>', read, re.S)[0]
        for book, _ in build_site.books():
            self.assertIn(f'href="#{book.lower()}"', index)

    def test_card_quotes_alternate_and_keep_apostrophes(self):
        # Speech inside the verse's speech turns to double quotes.
        self.assertEqual(build_site.inner_quotes("He said, \u201cThey will say, \u2018No.\u2019\u201d"),
                         "He said, \u2018They will say, \u201cNo.\u201d\u2019")
        # An apostrophe is not a closing quote.
        self.assertEqual(build_site.inner_quotes("Moses\u2019 father-in-law and Aaron\u2019s sons"),
                         "Moses\u2019 father-in-law and Aaron\u2019s sons")
        # Speech that runs on into the next verse is closed, inner first.
        self.assertEqual(build_site.inner_quotes("He said, \u201cTell him, \u2018Go"),
                         "He said, \u2018Tell him, \u201cGo\u201d\u2019")

    def built(self, path):
        """The built file a site path names ("/es/offline/", "/style.css?v=...")."""
        rel = path.split("?")[0].lstrip("/")
        return self.out / (rel + "index.html" if rel.endswith("/") or not rel else rel)

    def test_offline_worker_keeps_files_that_exist(self):
        sw = (self.out / "sw.js").read_text(encoding="utf-8")
        self.assertNotIn("__", sw.split('"use strict";')[1])
        precache = json.loads(re.search(r"var PRECACHE = (.*);", sw)[1])
        offline = json.loads(re.search(r"var OFFLINE = (.*);", sw)[1])
        for path in precache + list(offline.values()):
            self.assertTrue(self.built(path).is_file(), path)
        self.assertIn(build_site.asset("reader.js"), precache)
        self.assertIn(build_site.asset("markup.js"), precache)
        self.assertEqual(set(offline), {"" if code == "en" else code for code in build_site.LANGUAGES})
        manifest = json.loads((self.out / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["start_url"], "/")
        self.assertIn('<link rel="manifest" href="/manifest.webmanifest">',
                      (self.out / "index.html").read_text(encoding="utf-8"))

    def test_offline_pages_are_built_but_not_indexed(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("/offline/", sitemap)
        for code in build_site.LANGUAGES:
            page = self.built(build_site.url(code, "/offline/")).read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex">', page)
            self.assertIn('id="saved-books"', page)

    def test_read_page_can_save_each_book(self):
        for code in build_site.LANGUAGES:
            read = self.built(build_site.url(code, "/read/")).read_text(encoding="utf-8")
            files = json.loads(html.unescape(re.search(r'data-offline-files="([^"]*)"', read)[1]))
            for path in files:
                self.assertTrue(self.built(path).is_file(), path)
            buttons = re.findall(r'class="save-book" hidden data-book="([A-Z0-9]+)"[^>]*data-pages="([^"]*)"', read)
            self.assertEqual([b for b, _ in buttons], [b for b, _ in build_site.books(code)])
            for _, pages in buttons:
                for path in json.loads(html.unescape(pages)):
                    self.assertTrue(path.startswith(build_site.url(code, "/")), path)
                    self.assertTrue(self.built(path).is_file(), path)


class ExtractTest(unittest.TestCase):
    def test_extracts_are_up_to_date(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_tokens.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_comparison_extracts_are_up_to_date(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "extract_comparison.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


def note(reason, alternatives=()):
    return {"decisions": [{"choice": "x", "alternatives": list(alternatives), "reason": reason}]}


class ComparisonTest(unittest.TestCase):
    """A note's reference to a chapter not translated yet carries that
    verse from a public-domain Bible, for comparison: only the verses the
    page's notes name, so the page stays small."""

    def test_notes_bring_only_untranslated_verses(self):
        records, _ = build_site.load_chapter("1TI", 5)
        compare = build_site.comparison_verses(records, "en")
        self.assertEqual((compare["name"], compare["lang"]), ("World English Bible", "en"))
        # 1 Timothy 5:18 quotes Deuteronomy 25:4.
        self.assertEqual(compare["verses"]["DEU.25.4"], build_site.comparison_text("web")["DEU.25.4"])
        have = build_site.book_refs("en")["chapters"]
        for vid in compare["verses"]:
            book, chapter, _ = vid.split(".")
            self.assertNotIn(int(chapter), have.get(book, []), vid)

    def test_spanish_pages_compare_with_the_reina_valera(self):
        records, _ = build_site.load_chapter("1TI", 5)
        compare = build_site.comparison_verses(records, "es")
        self.assertEqual((compare["name"], compare["lang"]), ("Reina-Valera 1909", "es"))
        self.assertEqual(compare["verses"]["DEU.25.4"], build_site.comparison_text("rv1909")["DEU.25.4"])

    def test_ranges_are_capped_and_translated_chapters_skipped(self):
        have = build_site.book_refs("en")["chapters"]
        self.assertIn(10, have["LUK"])
        self.assertNotIn(9, have.get("DEU", []))
        self.assertNotIn(32, have.get("DEU", []))
        compare = build_site.comparison_verses(
            [note("As in Deuteronomy 9:9-20, and Luke 10:7.", alternatives=["Deuteronomy 32:4"])], "en")
        self.assertEqual(set(compare["verses"]),
                         {"DEU.32.4"} | {f"DEU.9.{v}" for v in range(9, 9 + build_site.COMPARE_MAX_VERSES)})
        self.assertIsNone(build_site.comparison_verses([note("Luke 10:7 only.")], "en"))
        self.assertIsNone(build_site.comparison_verses([note("No references here.")], "en"))

    def test_chapter_pages_embed_the_comparison(self):
        page = (built_site() / "1ti" / "5" / "index.html").read_text(encoding="utf-8")
        data = json.loads(re.search(r'<script type="application/json" id="owb-data">(.*?)</script>', page, re.S)[1])
        self.assertIn("DEU.25.4", data["compare"]["verses"])
        # A page's comparison verses are a few kilobytes at most.
        self.assertLess(len(json.dumps(data["compare"], ensure_ascii=False)), 25000)


class SharedDataTest(unittest.TestCase):
    """Book data that pull requests adding chapters would otherwise all edit."""

    def test_every_book_is_named_in_every_language(self):
        from owb import refs
        self.assertEqual(list(build_site.BOOK_NAMES), refs.BOOK_CODES)
        for code, names in build_site.BOOK_NAMES.items():
            self.assertEqual(set(names), set(build_site.LANGUAGES), code)
            self.assertEqual(names["en"], refs.BOOK_NAMES[code])
            self.assertGreater(build_site.BOOK_CHAPTERS[code], 0, code)

    def test_headings_are_filed_by_book(self):
        for path in (ROOT / "data" / "headings").glob("*.json"):
            for rid in json.loads(path.read_text(encoding="utf-8"))["headings"]:
                self.assertEqual(rid.split(".")[0], path.stem, path.name)

    def test_summaries_are_well_formed(self):
        done = set(build_site.chapters())
        for path in (ROOT / "data" / "summaries").glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "ai_draft", path.name)
            self.assertTrue(data["description"], path.name)
            for chapter, summary in data["summaries"].items():
                where = f"{path.name} {chapter}"
                self.assertRegex(chapter, r"^[1-9][0-9]*$", where)
                self.assertIn((path.stem, int(chapter)), done, where)
                self.assertIn("en", summary, where)
                for lang, text in summary.items():
                    self.assertIn(lang, build_site.LANGUAGES, where)
                    self.assertTrue(text.strip(), where)
                    # Shown as plain text under the title: no reader settings.
                    self.assertNotIn("{{", text, where)


if __name__ == "__main__":
    unittest.main()
