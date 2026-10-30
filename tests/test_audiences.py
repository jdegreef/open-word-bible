"""The "Open Word Bible for" pages (build_site.AUDIENCES): one per audience
at /for/<id>/ in every language, and the home page's way in to each."""
import html
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from tests.site_build import built_site  # noqa: E402


class AudienceDataTest(unittest.TestCase):
    def test_every_audience_has_its_words_in_every_language(self):
        for lang in build_site.LANGUAGES:
            words = build_site.catalog(lang)["audiences"]
            for audience in build_site.AUDIENCES:
                own = words[audience.id]
                self.assertEqual(len(own["steps"]), len(audience.steps), (lang, audience.id))
                for key in ("name", "card", "heading", "dek"):
                    self.assertTrue(own[key], (lang, audience.id, key))

    def test_articles_and_steps_lead_somewhere(self):
        ids = [a.id for a in build_site.AUDIENCES]
        self.assertEqual(len(ids), len(set(ids)))
        for audience in build_site.AUDIENCES:
            self.assertIn(audience.icon, build_site.ICONS)
            for slug in audience.articles:
                self.assertTrue((build_site.ARTICLES / f"{slug}.md").is_file(), slug)
            for ico, path in audience.steps:
                self.assertIn(ico, build_site.ICONS)
                self.assertTrue(path.startswith("/"), path)


class AudiencePageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def read(self, rel):
        return (self.out / rel / "index.html").read_text(encoding="utf-8")

    def links(self, page):
        return set(re.findall(r'href="([^"]+)"', page))

    def test_each_audience_has_a_page_in_every_language(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        for lang in build_site.LANGUAGES:
            prefix = "" if lang == "en" else f"{lang}/"
            for audience in build_site.AUDIENCES:
                page = self.read(f"{prefix}for/{audience.id}")
                own = build_site.catalog(lang)["audiences"][audience.id]
                self.assertIn(f"<h1>{own['heading']}</h1>", page)
                self.assertIn(build_site.SITE_URL + build_site.url(lang, build_site.audience_url(audience)), sitemap)
                links = {html.unescape(h) for h in self.links(page)}
                for _, path in audience.steps:
                    self.assertIn(build_site.url(lang, path), links, (lang, audience.id))
                # The other audiences, never itself.
                for other in build_site.AUDIENCES:
                    href = build_site.url(lang, build_site.audience_url(other))
                    self.assertEqual(href in links, other != audience, (lang, other.id))

    def test_reading_is_the_articles_written_in_the_language(self):
        preachers = build_site.AUDIENCES[0]
        page = self.read("for/preachers")
        for slug in preachers.articles:
            self.assertIn(f'href="/articles/{slug}/"', page)
        # Portuguese has no articles yet: no reading section, nothing in English.
        if not build_site.load_articles("pt"):
            self.assertNotIn("/articles/showing-the-work/", self.read("pt/for/preachers"))
            self.assertNotIn('id="audience-read-h"', self.read("pt/for/preachers"))

    def test_steps_open_the_reader_at_a_level(self):
        page = html.unescape(self.read("for/seekers"))
        self.assertIn('href="/jhn/1/?level=R"', page)
        page = html.unescape(self.read("es/for/preachers"))
        self.assertIn('href="/es/jhn/1/?level=L"', page)

    def test_home_page_leads_to_each_audience(self):
        for lang in ("en", "ko"):
            home = self.read(build_site.url(lang, "/").strip("/"))
            self.assertIn('aria-labelledby="audiences-h"', home)
            for audience in build_site.AUDIENCES:
                self.assertIn(f'href="{build_site.url(lang, build_site.audience_url(audience))}"', home)


if __name__ == "__main__":
    unittest.main()
