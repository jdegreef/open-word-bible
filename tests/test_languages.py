"""The site in each interface language: English at the root, Spanish under
/es/, the footer's language switch, and the message catalogs in i18n/."""
import json
import re
import string
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402

OTHERS = [lang for lang in build_site.LANGUAGES if lang != "en"]


def shape(value):
    """A catalog value's structure: keys, list lengths and the {names} each
    string fills, without the words."""
    if isinstance(value, dict):
        return {k: shape(v) for k, v in value.items()}
    if isinstance(value, list):
        return [shape(v) for v in value]
    return sorted({name for _, name, _, _ in string.Formatter().parse(value) if name})


class CatalogTest(unittest.TestCase):
    def test_every_language_has_every_message_with_the_same_placeholders(self):
        english = shape(build_site.catalog("en"))
        for lang in OTHERS:
            self.assertEqual(shape(build_site.catalog(lang)), english, lang)

    def test_catalogs_type_no_greek_or_hebrew(self):
        from owb import validate
        for path in sorted((ROOT / "i18n").glob("*.json")):
            text = path.read_text(encoding="utf-8")
            for script, (pattern, _) in validate._SCRIPTS.items():
                self.assertEqual(pattern.findall(text), [], f"{path.name}: {script}")


class LanguagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "site"
        build_site.build(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def english_pages(self):
        langs = set(OTHERS)
        return [p.relative_to(self.out) for p in self.out.rglob("index.html")
                if p.relative_to(self.out).parts[0] not in langs]

    def test_every_page_is_built_in_every_language(self):
        pages = self.english_pages()
        self.assertIn(Path("jhn/1/index.html"), pages)
        for lang in OTHERS:
            for rel in pages:
                self.assertTrue((self.out / lang / rel).is_file(), (lang, rel))
                text = self.read(Path(lang) / rel)
                self.assertIn(f'<html lang="{lang}">', text, rel)
                self.assertIn(build_site.LANG_SCRIPT, text, rel)
        for rel in pages:
            self.assertIn('<html lang="en">', self.read(rel), rel)

    def test_pages_name_each_other_with_hreflang(self):
        home = self.read("es/index.html")
        for lang in build_site.LANGUAGES:
            href = build_site.SITE_URL + build_site.url(lang, "/")
            self.assertIn(f'<link rel="alternate" hreflang="{lang}" href="{href}">', home)
        self.assertIn(f'hreflang="x-default" href="{build_site.SITE_URL}/"', home)
        self.assertIn(f'<link rel="canonical" href="{build_site.SITE_URL}/es/">', home)
        sitemap = self.read("sitemap.xml")
        for path in ("es/", "es/read/", "es/jhn/1/", "es/articles/"):
            self.assertIn(f"<loc>{build_site.SITE_URL}/{path}</loc>", sitemap)

    def test_footer_switches_to_the_same_page_in_each_language(self):
        en = self.read("jhn/1/index.html")
        es = self.read("es/jhn/1/index.html")
        self.assertIn('<span lang="en" aria-current="true">English</span>', en)
        self.assertIn('<a href="/es/jhn/1/" lang="es" hreflang="es" data-lang="es">Español</a>', en)
        self.assertIn('<span lang="es" aria-current="true">Español</span>', es)
        self.assertIn('<a href="/jhn/1/" lang="en" hreflang="en" data-lang="en">English</a>', es)
        self.assertIn('<h2 id="foot-langs">Idiomas</h2>', es)
        # The 404 page, which has no path, offers each language's home page.
        self.assertIn('href="/es/" lang="es"', self.read("404.html"))
        self.assertNotIn(build_site.LANG_SCRIPT, self.read("404.html"))

    def test_spanish_pages_have_spanish_interface_text(self):
        en, es = build_site.catalog("en"), build_site.catalog("es")
        keys = ("skip", "nav.home", "nav.all_passages", "nav.all_articles", "footer.tagline",
                "footer.review", "footer.report", "tools.theme", "theme.night")
        for rel in self.english_pages():
            page = self.read(Path("es") / rel)
            for key in keys:
                self.assertNotIn(en[key], page, (rel, key))
                self.assertIn(es[key], page, (rel, key))
        home = self.read("es/index.html")
        self.assertIn(es["home.heading"], home)
        self.assertIn('href="/es/read/"', home)
        self.assertNotIn('href="/read/"', home)

    def test_reader_reads_in_the_page_language(self):
        def data(rel):
            m = re.search(r'id="owb-data">(.*?)</script>', self.read(rel), re.S)
            return json.loads(m[1])

        for lang in build_site.LANGUAGES:
            d = data(build_site.url(lang, "/jhn/1/").lstrip("/") + "index.html")
            self.assertEqual(d["lang"], lang)
            self.assertEqual(d["ui"], build_site.catalog(lang)["reader.ui"])
            self.assertTrue(d["title"].startswith(build_site.BOOK_NAMES["JHN"][lang]))
        # The language is the page's: no language control in the settings,
        # and the Spanish-only plural setting only on Spanish pages.
        en, es = self.read("jhn/1/index.html"), self.read("es/jhn/1/index.html")
        self.assertNotIn('data-setting="lang"', en + es)
        self.assertNotIn('data-setting="plural_you"', en)
        self.assertIn('data-setting="plural_you"', es)
        self.assertIn(">Equilibrada</button>", es)

    def test_an_untranslated_article_shows_the_english_and_points_to_it(self):
        for article in build_site.load_articles("es"):
            rel = Path("es") / build_site.article_url(article).strip("/") / "index.html"
            page = self.read(rel)
            english = build_site.SITE_URL + build_site.article_url(article)
            if article["lang"] == "es":
                self.assertIn('hreflang="es"', page)
                continue
            self.assertIn(build_site.catalog("es")["article.not_translated"], page)
            self.assertIn(f'<link rel="canonical" href="{english}">', page)
            self.assertIn('<div class="article-body" lang="en">', page)
            self.assertNotIn(f"{build_site.SITE_URL}/es{build_site.article_url(article)}<",
                             self.read("sitemap.xml"))

    def test_links_inside_spanish_pages_resolve(self):
        for path in (self.out / "es").rglob("index.html"):
            for href in re.findall(r'href="(/[^"#?]*)', path.read_text(encoding="utf-8")):
                target = self.out / href.lstrip("/")
                self.assertTrue(target.is_file() or (target / "index.html").is_file(), (path, href))

    def test_dates_are_written_in_each_language(self):
        self.assertEqual(build_site._date("2026-10-10", "en"), "10 October 2026")
        self.assertEqual(build_site._date("2026-10-10", "es"), "10 de octubre de 2026")


if __name__ == "__main__":
    unittest.main()
