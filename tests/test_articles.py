"""Articles (articles/*.md) and the colour-mode menu, as built into the site."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from tests.site_build import built_site  # noqa: E402
from owb import validate  # noqa: E402


class ArticlesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()
        cls.articles = build_site.load_articles()

    def test_ten_articles_with_front_matter(self):
        self.assertGreaterEqual(len(self.articles), 10)
        for a in self.articles:
            for key in ("title", "summary", "date"):
                self.assertTrue(a[key].strip(), (a["slug"], key))
            self.assertTrue((self.out / "articles" / a["slug"] / "index.html").is_file())

    def test_no_greek_or_hebrew_typed_in_articles(self):
        # Original-language words come only through {{GREEK:..}} and
        # {{LEMMA:..}} placeholders, filled from data/grc/ at build time.
        # Translations (articles/<lang>/) included.
        for path in sorted((ROOT / "articles").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for script, (pattern, _) in validate._SCRIPTS.items():
                self.assertEqual(pattern.findall(text), [], f"{path.name}: {script} typed by hand")

    def test_placeholders_are_filled_from_the_data(self):
        page = (self.out / "articles" / "the-word-was-god" / "index.html").read_text(encoding="utf-8")
        words = build_site._verse_words("JHN", 1, 1)
        expected = " ".join(w["text"] + (w["after"].rstrip() if w["position"] < 17 else "")
                            for w in words if 14 <= w["position"] <= 17)
        self.assertIn(f'<span class="greek" lang="grc">{expected}</span>', page)
        self.assertIn(build_site.plain(build_site.load_chapter("JHN", 1)[0][0]["renderings"]["en"]["B"]), page)
        for path in (self.out / "articles").rglob("index.html"):
            self.assertNotIn("{{", path.read_text(encoding="utf-8"), path)

    def test_hebrew_placeholders_are_filled_from_the_data(self):
        # Genesis 1:1 word 1 is two parts (a prefix and the noun) sharing a
        # position; the quote keeps the joins but not the closing sof pasuq.
        words = build_site._verse_words("GEN", 1, 1)
        last = max(w["position"] for w in words)
        parts = [w for w in words if w["position"] >= last - 1]
        expected = "".join(w["text"] + w["after"] for w in parts[:-1]) + parts[-1]["text"]
        page = build_site.article_html(f"> {{{{HEBREW:GEN.1.1:{last - 1}-{last}}}}}")
        self.assertIn(f'<span class="hebrew" lang="hbo" dir="rtl">{expected}</span>', page)
        self.assertIn('class="quote hebrew-quote"', page)
        self.assertIn(f"Genesis 1:1 &middot; {build_site.t('en', 'article.hebrew_source')}", page)
        self.assertEqual(build_site.article_passages("{{HEBREW:GEN.1.1:1}}"), [("GEN", 1, [1])])
        first = [w for w in words if w["position"] == 1]
        self.assertGreater(len(first), 1)
        self.assertIn(first[1]["lemma"], build_site.article_html("{{LEMMA:GEN.1.1:1.2}}"))
        for wrong in ("{{LEMMA:GEN.1.1:1}}", "{{GREEK:GEN.1.1:1}}", "{{HEBREW:JHN.1.1:1}}"):
            with self.assertRaises(SystemExit, msg=wrong):
                build_site.article_html(wrong)

    def test_internal_links_resolve(self):
        for path in (self.out / "articles").rglob("index.html"):
            for href in re.findall(r'href="(/[^"#?]*)', path.read_text(encoding="utf-8")):
                target = self.out / href.lstrip("/")
                self.assertTrue(target.is_file() or (target / "index.html").is_file(), (path, href))

    def test_articles_are_in_the_nav_sitemap_and_home_page(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        for a in self.articles:
            self.assertIn(f"{build_site.SITE_URL}/articles/{a['slug']}/", sitemap)
        home = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/articles/"', home)
        first = min(self.articles, key=lambda a: a["order"])
        self.assertIn(build_site.article_url(first), home)

    def test_menu_titles_are_shorter_than_titles(self):
        # nav_title is a short title for the header menu, in every language.
        for lang in build_site.LANGUAGES:
            for a in build_site.load_articles(lang):
                if "nav_title" in a:
                    self.assertLess(len(a["nav_title"]), len(a["title"]), (lang, a["slug"]))

    def test_every_article_has_a_known_section(self):
        for a in self.articles:
            self.assertIn(a["section"], build_site.SECTIONS, a["slug"])
        index = (self.out / "articles" / "index.html").read_text(encoding="utf-8")
        for key in build_site.SECTIONS:
            self.assertIn(f'id="{key}"', index)
            # A link to each section from the top, with its count (the
            # first article opens the page, above the sections)...
            first = min(self.articles, key=lambda a: a["order"])
            count = sum(a["section"] == key for a in self.articles if a is not first)
            self.assertIn(f'<a href="#{key}" data-filter="{key}">{build_site.SECTIONS[key]} <span>{count}</span></a>',
                          index)
        # ...and a section's rows don't repeat its name.
        groups = index[index.index('<section class="a-group"'):]
        self.assertNotIn('class="a-section"', groups)

    def test_articles_page_starts_here_numbers_series_and_links_verses(self):
        index = (self.out / "articles" / "index.html").read_text(encoding="utf-8")
        # The first article, with the next ones in its section to read after it.
        self.assertIn('<div class="a-start" id="a-start">', index)
        self.assertIn('<nav class="a-path"', index)
        # Series are numbered; other sections are not.
        history = index[index.index('id="history"'):]
        self.assertIn('<span class="a-num" aria-hidden="true">20</span>', history)
        method = index[index.index('id="method"'):index.index('id="passage"')]
        self.assertNotIn('a-num', method)
        # Verses an article reads link to the reader.
        self.assertIn('<a class="a-ref" href="/jhn/1/#v1">John 1:1</a>', index)

    def test_history_series_is_in_parts_in_every_language(self):
        english = {a["slug"]: a for a in self.articles}
        for a in self.articles:
            if a["section"] == "history":
                self.assertIn(a.get("part"), build_site.PARTS, a["slug"])
        for lang in build_site.LANGUAGES:
            for a in build_site.load_articles(lang):
                self.assertEqual(a.get("part"), english[a["slug"]].get("part"), f"{lang} {a['slug']}")
        index = (self.out / "articles" / "index.html").read_text(encoding="utf-8")
        history = index[index.index('id="history"'):index.index('id="translation"')]
        self.assertIn('<h3>The Old Testament <span>1\u201310</span></h3>', history)
        self.assertIn('<ol class="a-rows series" start="11">', history)

    def test_articles_page_filters_searches_and_has_a_feed(self):
        index = (self.out / "articles" / "index.html").read_text(encoding="utf-8")
        # The search box waits for web/site.js, which filters the list.
        self.assertIn('<label class="a-search" hidden>', index)
        self.assertIn('id="a-search"', index)
        self.assertIn('getElementById("a-index")', (self.out / "site.js").read_text(encoding="utf-8"))
        self.assertIn('type="application/atom+xml"', index)
        feed = (self.out / "articles" / "feed.xml").read_text(encoding="utf-8")
        self.assertEqual(feed.count("<entry>"), len(self.articles))
        newest = max(self.articles, key=lambda a: a["date"])
        self.assertIn(f"<updated>{newest['date']}T00:00:00Z</updated>", feed)
        es = self.out / "es" / "articles" / "feed.xml"
        self.assertEqual(es.read_text(encoding="utf-8").count("<entry>"), len(build_site.load_articles("es")))

    def test_series_parts_are_numbered_with_turns(self):
        for key in build_site.SERIES:
            parts = sorted((a for a in self.articles if a["section"] == key), key=lambda a: a["order"])
            total = len(parts)
            first = (self.out / "articles" / parts[0]["slug"] / "index.html").read_text(encoding="utf-8")
            self.assertIn(f"Part 1 of {total}", first)
            self.assertIn(f'href="/articles/{parts[1]["slug"]}/"', first.split('class="series"')[1])
            self.assertNotIn('s-turn prev', first)
            last = (self.out / "articles" / parts[-1]["slug"] / "index.html").read_text(encoding="utf-8")
            self.assertIn(f"Part {total} of {total}", last)
            self.assertNotIn('s-turn next', last)
        # A part keeps its English number in a language with fewer parts.
        for lang in build_site.LANGUAGES:
            for a in build_site.load_articles(lang):
                if a["section"] in build_site.SERIES:
                    n, total = build_site.series_numbers()[a["slug"]]
                    page = self.out / build_site.url(lang, build_site.article_url(a)).lstrip("/") / "index.html"
                    self.assertIn(build_site.t(lang, "article.part", n=n, total=total),
                                  page.read_text(encoding="utf-8"))

    def test_chapters_link_the_articles_that_read_them(self):
        page = (self.out / "jhn" / "3" / "index.html").read_text(encoding="utf-8")
        aside = re.search(r'<aside class="chapter-articles".*?</aside>', page, re.S)[0]
        for a in self.articles:
            if any(b == "JHN" and c == 3 for b, c, _ in a["passages"]):
                self.assertIn(build_site.article_url(a), aside)
        # A chapter no article reads has no aside.
        read = {(b, c) for a in self.articles for b, c, _ in a["passages"]}
        book, chapter = next((b, c) for b, c in (("OBA", 1), ("HAG", 1), ("JUD", 1), ("PHM", 1), ("3JN", 1))
                             if (b, c) not in read)
        unread = (self.out / book.lower() / str(chapter) / "index.html").read_text(encoding="utf-8")
        self.assertNotIn('class="chapter-articles"', unread)

    def test_scripture_quotes_are_captioned_and_link_to_the_reader(self):
        page = (self.out / "articles" / "the-word-was-god" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<figure class="quote greek-quote">', page)
        self.assertIn('<figure class="quote owb-quote">', page)
        self.assertIn('href="/jhn/1/#v1">Read it with the reasoning', page)
        self.assertIn('<nav class="toc"', page)
        for slug in re.findall(r'<li><a href="#([^"]+)"', page):
            self.assertIn(f'<h2 id="{slug}">', page)

    def test_passage_labels_join_consecutive_verses(self):
        self.assertEqual(build_site.passage_label("PHP", 4, [6, 7]), "Philippians 4:6–7")
        self.assertEqual(build_site.passage_label("JHN", 1, [1, 14, 16, 17, 18]), "John 1:1, 14, 16–18")


class SiteChromeTest(unittest.TestCase):
    def test_every_page_has_the_header_menu_skip_link_and_footer(self):
        out = built_site()
        for path in out.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            self.assertIn('<a class="skip" href="#main">', text, path)
            self.assertIn('id="main"', text, path)
            self.assertIn('class="tool-btn menu-btn"', text, path)
            self.assertIn('aria-controls="site-nav"', text, path)
            self.assertIn('<footer class="site">', text, path)
            # Links stay in the page's language: /es/ pages link to /es/.
            lang = re.search(r'<html lang="([a-z]+)">', text)[1]
            self.assertIn(f'href="{build_site.url(lang, "/read/#jhn")}"', text, path)
        about = (out / "about" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<h2 id="credits">', about)
        self.assertIn('id="help"', (out / "index.html").read_text(encoding="utf-8"))


class ColourModesTest(unittest.TestCase):
    MODES = [v for v, *_ in build_site.COLOUR_MODES]

    def test_five_colour_modes_plus_automatic(self):
        self.assertEqual(self.MODES, ["auto", "light", "sepia", "dark", "night", "contrast"])

    def test_paper_is_the_default(self):
        css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        self.assertIn('data-pref="theme" data-default="light"', build_site.colour_menu("en"))
        # With no choice saved, nothing follows the device's dark setting.
        self.assertNotIn(":root:not([data-theme])", css)

    def test_every_mode_is_styled_and_known_to_the_scripts(self):
        css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        site_js = (ROOT / "web" / "site.js").read_text(encoding="utf-8")
        js_modes = re.search(r"var MODES = \[([^\]]*)\]", site_js)[1]
        boot_modes = re.search(r"\[([^\]]*)\]\.indexOf", build_site.BOOT_SCRIPT)[1]
        for mode in self.MODES:
            self.assertIn(f':root[data-theme="{mode}"]', css)
            self.assertIn(f'"{mode}"', js_modes)
            self.assertIn(f"'{mode}'", boot_modes)

    def test_display_settings_are_styled_and_applied_before_paint(self):
        css = (ROOT / "web" / "style.css").read_text(encoding="utf-8")
        menu = build_site.colour_menu("en")
        for name, default, values in build_site.DISPLAY_PREFS:
            others = [v for v in values if v != default]
            self.assertIn(default, values)
            self.assertIn(f'data-pref="{name}" data-default="{default}"', menu)
            self.assertIn(f"{name}:{others!r}", build_site.BOOT_SCRIPT)
            for value in values:
                self.assertIn(f'data-value="{value}"', menu)
            for value in others:
                self.assertIn(f':root[data-{name}="{value}"]', css)
        # The reading text takes them; the interface keeps its own sizes.
        for rule in (".text {", ".article-body {"):
            line = next(l for l in css.splitlines() if l.startswith(rule))
            for var in ("--read-font", "--read-scale", "--read-leading"):
                self.assertIn(var, line)

    def test_gear_menu_links_this_page_in_every_language(self):
        menu = build_site.colour_menu("es", "/jhn/3/")
        self.assertIn('<span lang="es" aria-current="true">Español', menu)
        for code in build_site.LANGUAGES:
            if code != "es":
                self.assertIn(f'href="{build_site.url(code, "/jhn/3/")}" lang="{code}" hreflang="{code}" '
                              f'data-lang="{code}"', menu)
        # Without a path (the 404 page), each language's home page.
        self.assertIn('href="/fr/" lang="fr"', build_site.colour_menu("en"))
        # From an article not in a language, that language's articles page.
        menu = build_site.colour_menu("en", "/articles/x/", ("en", "es"))
        self.assertIn('href="/es/articles/x/" lang="es"', menu)
        self.assertIn('href="/fr/articles/" lang="fr"', menu)

    def test_every_page_has_the_gear_menu(self):
        out = built_site()
        for path in out.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            self.assertIn('class="tool-btn prefs-btn"', text, path)
            self.assertIn("localStorage.getItem('owb-theme')", text, path)
        self.assertTrue((out / "site.js").is_file())


if __name__ == "__main__":
    unittest.main()
