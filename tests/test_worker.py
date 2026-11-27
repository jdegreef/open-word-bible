"""cloudflare/worker.js against the built site (build_site.py WORKER_PAGES):
its verse pages are the pages verse_page builds, byte for byte, in every
language; its level pages are a chapter's Literal and Readable text; and
everything else goes on to the 404 page. The site is built with
OWB_WORKER_PAGES=1 in CI; without it these are skipped."""
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import build_site  # noqa: E402
from tests.site_build import built_site  # noqa: E402


def worker(site, *paths):
    """{path: {status, location, type, body}} as the Worker answers them."""
    out = subprocess.run(["node", str(ROOT / "tests" / "worker_harness.mjs"), str(site), *paths],
                         capture_output=True, text=True, check=True, cwd=ROOT)
    return json.loads(out.stdout)


@unittest.skipUnless(build_site.WORKER_PAGES, "the site is built without OWB_WORKER_PAGES=1")
@unittest.skipUnless(shutil.which("node"), "needs Node")
class WorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def test_verse_pages_are_the_pages_the_build_writes(self):
        # A Gospel, a psalm (poetry, numbered otherwise in Hebrew Bibles),
        # Malachi 4 (Hebrew Bibles' Malachi 3) and Romans 8, in each
        # language they are in, among them Persian (right to left, its own
        # digits), Korean, Japanese and Chinese (wide characters).
        cases = []
        for book, chapter in (("JHN", 3), ("PSA", 23), ("MAL", 4), ("ROM", 8)):
            for lang in build_site.LANGUAGES:
                vids = build_site.chapter_verse_pages(book, chapter, lang)
                cases += [(vid, lang) for vid in vids[:6] + vids[-2:]]
        self.assertGreater(len({lang for _, lang in cases}), 10)
        # A verse page the build writes is a file, which is served before
        # the Worker is asked.
        paths = {path: (vid, lang) for vid, lang in cases
                 if not (self.out / (path := build_site.url(lang, build_site.verse_page_url(vid))).lstrip("/")
                         / "index.html").exists()}
        self.assertGreater(len(paths), 100)
        got = worker(self.out, *paths)
        # Among them, pages with the verse in the comparison Bibles.
        self.assertTrue(any("verse-others" in got[p]["body"] for p in paths if paths[p][1] == "es"))
        for path, (vid, lang) in paths.items():
            with self.subTest(path=path):
                self.assertEqual(got[path]["status"], 200)
                self.assertEqual(got[path]["type"], "text/html; charset=utf-8")
                self.assertEqual(got[path]["body"], build_site.verse_page(vid, lang))

    def test_a_verse_not_in_a_language_and_a_verse_that_is_not_are_not_found(self):
        missing = next(vid for vid, langs in build_site.chapter_verse_languages("GEN", 30).items() if "ar" not in langs)
        got = worker(self.out, "/jhn/3/99/", "/jhn/99/1/", "/xyz/3/1/", "/xx/jhn/3/1/", "/en/jhn/3/1/",
                     build_site.url("ar", build_site.verse_page_url(missing)))
        for path, answer in got.items():
            with self.subTest(path=path):
                self.assertEqual(answer["status"], 404)

    def test_an_address_without_its_slash_is_sent_to_it(self):
        got = worker(self.out, "/jhn/3/16", "/es/jhn/3/readable")
        self.assertEqual(got["/jhn/3/16"]["status"], 301)
        self.assertEqual(got["/jhn/3/16"]["location"], "https://openwordbible.org/jhn/3/16/")
        self.assertEqual(got["/es/jhn/3/readable"]["location"], "https://openwordbible.org/es/jhn/3/readable/")

    def test_a_chapter_at_each_level_has_a_page_of_its_own(self):
        got = worker(self.out, "/jhn/3/readable/", "/jhn/3/literal/", "/es/psa/23/readable/")
        page = got["/jhn/3/readable/"]["body"]
        self.assertIn("<title>John 3 in easy-to-read English · Open Word Bible</title>", page)
        self.assertIn('<link rel="canonical" href="https://openwordbible.org/jhn/3/readable/">', page)
        self.assertIn('<link rel="alternate" hreflang="es" href="https://openwordbible.org/es/jhn/3/readable/">', page)
        # The Readable text, verse by verse, each number a link to its page.
        readable = build_site.verse_levels("JHN.3.16", "en")["R"]
        self.assertIn(build_site.html.escape(readable, quote=False), page)
        self.assertIn('<sup><a class="vn-link" href="/jhn/3/16/">16</a></sup>', page)
        self.assertIn('<a href="/jhn/3/literal/">Literal</a>', page)
        self.assertIn('href="/jhn/3/?level=R"', page)
        literal = got["/jhn/3/literal/"]["body"]
        self.assertIn("<title>John 3: literal, word-for-word translation · Open Word Bible</title>", literal)
        self.assertIn(build_site.html.escape(build_site.verse_levels("JHN.3.16", "en")["L"], quote=False), literal)
        # A psalm is set in lines.
        self.assertIn('<span class="ed-line">', got["/es/psa/23/readable/"]["body"])

    def test_a_chapter_links_every_verse_and_its_other_levels(self):
        page = (self.out / "es" / "jhn" / "3" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<a class="vn-link" href="/es/jhn/3/5/">5</a>', page)
        self.assertIn('<a href="/es/jhn/3/readable/">Sencilla</a>', page)

    def test_the_sitemaps_list_every_verse_and_level_page(self):
        verses = (self.out / "sitemap-es-verses.xml").read_text(encoding="utf-8")
        self.assertIn("<loc>https://openwordbible.org/es/jhn/3/5/</loc>", verses)
        chapters = (self.out / "sitemap-es-chapters.xml").read_text(encoding="utf-8")
        self.assertIn("<loc>https://openwordbible.org/es/jhn/3/literal/</loc>", chapters)
        total = sum(len(langs) for book, chapter in build_site.chapters()
                    for langs in build_site.chapter_verse_languages(book, chapter).values())
        listed = sum((self.out / f"sitemap-{lang}-verses.xml").read_text(encoding="utf-8").count("<url>")
                     for lang in build_site.LANGUAGES if (self.out / f"sitemap-{lang}-verses.xml").exists())
        self.assertEqual(listed, total)

    def test_the_worker_data_is_not_for_search_engines(self):
        self.assertIn("Disallow: /_worker/", (self.out / "robots.txt").read_text(encoding="utf-8"))
        meta = json.loads((self.out / "_worker" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["hebrewNumbers"]["MAL.4.1"], "MAL.3.19")
        self.assertIn("jhn-3", meta["cards"])


if __name__ == "__main__":
    unittest.main()
