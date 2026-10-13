"""The site in each interface language: English at the root, Spanish under
/es/, French under /fr/ and Swahili under /sw/, the footer's language switch,
and the message catalogs in i18n/."""
import json
import re
import string
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from owb import languages, markup, morph  # noqa: E402
from tests.site_build import built_site  # noqa: E402

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


class RegistryTest(unittest.TestCase):
    """data/languages.json: each language listed there has the data the site
    needs, and nothing is translated into a language it does not list."""

    def test_every_language_has_a_catalog_and_every_catalog_a_language(self):
        catalogs = {path.stem for path in (ROOT / "i18n").glob("*.json")}
        self.assertEqual(set(languages.CODES), catalogs)

    def test_english_comes_first(self):
        self.assertEqual(languages.CODES[0], "en")

    def test_every_language_has_its_names_and_grammar_words(self):
        for code, lang in languages.READING.items():
            self.assertTrue(lang["name"] and lang["native"] and "{}" in lang["quotes"], code)
            self.assertIn(code, morph.WORDS)
            self.assertIn(code, build_site.CHAPTER_NAMES["PSA"])

    def test_language_settings_are_reader_settings(self):
        for code, lang in languages.READING.items():
            for name, labels in lang.get("settings", {}).items():
                self.assertIn(name, markup.SETTINGS, code)
                self.assertGreaterEqual(len(labels), 2, code)


class LanguagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def read(self, rel):
        return (self.out / rel).read_text(encoding="utf-8")

    def english_pages(self):
        """Every English page but the articles and the reading plans, which
        a language has only once they are translated."""
        langs = set(OTHERS)
        rels = (p.relative_to(self.out) for p in self.out.rglob("index.html"))
        return [rel for rel in rels if rel.parts[0] not in langs
                and (rel.parts[0] not in ("articles", "plans") or len(rel.parts) == 2)]

    def test_every_page_is_built_in_every_language(self):
        pages = self.english_pages()
        self.assertIn(Path("jhn/1/index.html"), pages)
        for lang in OTHERS:
            for rel in pages:
                self.assertTrue((self.out / lang / rel).is_file(), (lang, rel))
                text = self.read(Path(lang) / rel)
                self.assertIn(f'<html lang="{lang}">', text, rel)
                self.assertIn(build_site.langs_meta(build_site.LANGUAGES), text, rel)
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
        for path in ("es/", "es/read/", "es/jhn/1/"):
            self.assertIn(f"<loc>{build_site.SITE_URL}/{path}</loc>", sitemap)
        # A language's articles page is listed once it has articles.
        listed = f"<loc>{build_site.SITE_URL}/es/articles/</loc>" in sitemap
        self.assertEqual(listed, bool(build_site.load_articles("es")))

    def test_footer_switches_to_the_same_page_in_each_language(self):
        en = self.read("jhn/1/index.html")
        es = self.read("es/jhn/1/index.html")
        self.assertIn('<span lang="en" aria-current="true">English</span>', en)
        self.assertIn('<a href="/es/jhn/1/" lang="es" hreflang="es" data-lang="es">Español</a>', en)
        self.assertIn('<a href="/fr/jhn/1/" lang="fr" hreflang="fr" data-lang="fr">Français</a>', en + es)
        self.assertIn('<span lang="fr" aria-current="true">Français</span>', self.read("fr/jhn/1/index.html"))
        self.assertIn('<a href="/sw/jhn/1/" lang="sw" hreflang="sw" data-lang="sw">Kiswahili</a>', en + es)
        self.assertIn('<span lang="sw" aria-current="true">Kiswahili</span>', self.read("sw/jhn/1/index.html"))
        self.assertIn('<span lang="es" aria-current="true">Español</span>', es)
        self.assertIn('<a href="/jhn/1/" lang="en" hreflang="en" data-lang="en">English</a>', es)
        self.assertIn('<h2 id="foot-langs">Idiomas</h2>', es)
        # The 404 page, which has no path, offers each language's home page.
        self.assertIn('href="/es/" lang="es"', self.read("404.html"))
        self.assertNotIn('name="owb-langs"', self.read("404.html"))

    def test_other_language_pages_have_their_own_interface_text(self):
        en = build_site.catalog("en")
        for lang in OTHERS:
            keys = ("skip", "nav.home", "nav.all_books", "footer.tagline",
                    "footer.review", "footer.report", "tools.theme", "theme.night")
            if build_site.load_articles(lang):
                keys += ("nav.all_articles",)
            cat = build_site.catalog(lang)
            for rel in self.english_pages():
                # The passage data and the text written into the page may
                # hold the same words as Bible text (Genesis 1:5 names the
                # darkness "Night"), in English where a sentence has no
                # translation yet; only the interface counts.
                page = re.sub(r'<script type="application/json" id="owb-data">.*?</script>'
                              r'|<div class="text" id="text">.*?</div>\s*<section class="notes"', "",
                              self.read(Path(lang) / rel), flags=re.S)
                for key in keys:
                    self.assertNotIn(en[key], page, (lang, rel, key))
                    self.assertIn(cat[key], page, (lang, rel, key))
            home = self.read(f"{lang}/index.html")
            self.assertIn(cat["home.heading"], home)
            self.assertIn(f'href="/{lang}/read/"', home)
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
        fr = self.read("fr/jhn/1/index.html")
        self.assertNotIn('data-setting="plural_you"', fr)
        self.assertIn(">Équilibrée</button>", fr)
        sw = self.read("sw/jhn/1/index.html")
        self.assertNotIn('data-setting="plural_you"', sw)
        self.assertIn(">Linganifu</button>", sw)

    def test_a_language_shows_only_its_own_articles(self):
        for lang in OTHERS:
            own = {a["slug"] for a in build_site.load_articles(lang)}
            for article in build_site.load_articles("en"):
                rel = Path(lang) / build_site.article_url(article).strip("/") / "index.html"
                self.assertEqual((self.out / rel).is_file(), article["slug"] in own, rel)
            listing = self.read(f"{lang}/articles/index.html")
            home = self.read(f"{lang}/index.html")
            if not own:
                self.assertIn(build_site.catalog(lang)["articles.none"], listing)
                self.assertNotIn('class="a-card', listing + home)
                self.assertNotIn('id="dd-articles"', home)

    def test_an_english_article_switches_languages_to_their_articles_page(self):
        article = build_site.load_articles("en")[0]
        page = self.read(build_site.article_url(article).strip("/") + "/index.html")
        for lang in OTHERS:
            if lang not in build_site.article_languages(article):
                self.assertIn(f'<a href="/{lang}/articles/" lang="{lang}"', page)
                self.assertNotIn(f'hreflang="{lang}" href=', page)

    def test_links_inside_other_language_pages_resolve(self):
        for path in (p for lang in OTHERS for p in (self.out / lang).rglob("index.html")):
            for href in re.findall(r'href="(/[^"#?]*)', path.read_text(encoding="utf-8")):
                target = self.out / href.lstrip("/")
                self.assertTrue(target.is_file() or (target / "index.html").is_file(), (path, href))

    def test_account_page_speaks_the_page_language(self):
        page = self.read("es/account/index.html")
        m = re.search(r'id="account-text">(.*?)</script>', page, re.S)
        self.assertEqual(json.loads(m[1]), build_site.catalog("es")["account.ui"])
        login = self.read("es/login/index.html")
        m = re.search(r'id="login-text">(.*?)</script>', login, re.S)
        self.assertEqual(json.loads(m[1]), build_site.catalog("es")["login.ui"])
        self.assertIn("Bienvenido de nuevo", login)
        self.assertIn('<meta name="robots" content="noindex">', page)
        self.assertNotIn('rel="canonical"', page)
        # Unlisted, but the switch and the remembered choice still lead to it.
        self.assertIn('<a href="/account/" lang="en"', page)
        self.assertIn(build_site.langs_meta(build_site.LANGUAGES), page)
        self.assertNotIn("/account/", self.read("sitemap.xml"))

    def test_chapter_strip_and_turns_stay_in_the_language(self):
        page = self.read("es/php/2/index.html")
        strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
        self.assertIn('href="/es/php/2/" aria-current=page', strip)
        self.assertIn("Filipenses", strip)
        turns = re.search(r'<nav class="turns"(.*?)</nav>', page, re.S)[1]
        self.assertIn('href="/es/php/1/" rel="prev"', turns)
        self.assertIn("Anterior", turns)

    def test_dates_are_written_in_each_language(self):
        self.assertEqual(build_site._date("2026-10-10", "en"), "10 October 2026")
        self.assertEqual(build_site._date("2026-10-10", "es"), "10 de octubre de 2026")
        self.assertEqual(build_site._date("2026-10-10", "fr"), "10 octobre 2026")
        self.assertEqual(build_site._date("2026-10-10", "sw"), "10 Oktoba 2026")

    def test_french_typography_has_no_breaking_space_before_its_marks(self):
        # French sets « » : ; ! ? off with no-break spaces, so a line never
        # starts with one. A plain space before them is a typo.
        text = (ROOT / "i18n" / "fr.json").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"(?: [;:!?»]|« )", text), [])


if __name__ == "__main__":
    unittest.main()
