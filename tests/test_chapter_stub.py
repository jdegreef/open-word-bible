"""A chapter's page in a language with none of its sentences yet is a short
page leading to the English one (build_site.chapter_stub), not the whole
chapter in English under that language's interface."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


class ChapterStubTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A chapter some site language has none of, and that language.
        cls.book, cls.chapter, cls.lang = next(
            (b, c, lang) for lang in reversed(build_site.LANGUAGES) for b, c in build_site.chapters()
            if not build_site.chapter_has(b, c, lang))

    def test_says_so_and_leads_to_english(self):
        page = build_site.chapter_stub(self.book, self.chapter, self.lang)
        english = build_site.chapter_url(self.book, self.chapter)
        self.assertIn(f'<html lang="{self.lang}"', page)
        self.assertIn(build_site.catalog(self.lang)["reader.ui"]["not_in_language"], page)
        self.assertIn(f'<a class="button" href="{english}" hreflang="en">', page)
        self.assertIn('<meta name="robots" content="noindex', page)
        self.assertNotIn('<div class="reader">', page)
        # The site's header and footer, as on every page.
        self.assertIn('class="tool-btn prefs-btn"', page)
        self.assertLess(len(page.encode()), 60_000)

    def test_a_chapter_with_text_is_not_a_stub(self):
        self.assertTrue(build_site.chapter_has("JHN", 1, "en"))
        self.assertFalse(build_site.chapter_has(self.book, self.chapter, self.lang))


if __name__ == "__main__":
    unittest.main()
