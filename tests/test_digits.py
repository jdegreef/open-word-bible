"""Digits: a language's own digits in data/languages.json (owb/languages.py
DIGITS), shown in place of ASCII digits in text in that language
(build_site.localize_digits; web/site.js OWBDigits does the same for text
the scripts add, tests/js/digits.test.mjs). Persian is the language with
digits of its own; the records keep ASCII digits."""
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from owb import languages  # noqa: E402

FA = "۰۱۲۳۴۵۶۷۸۹"


class LanguagesTest(unittest.TestCase):
    def test_persian_has_its_digits(self):
        self.assertEqual(languages.digits("fa"), FA)
        self.assertEqual(languages.digits("fa-AF"), FA)
        self.assertIsNone(languages.digits("en"))
        self.assertIsNone(languages.digits("ar"))
        self.assertIsNone(languages.digits(""))


class LocalizeTest(unittest.TestCase):
    def localize(self, text, base="fa"):
        return build_site.localize_digits(text, base)

    def test_numbers_in_persian_text(self):
        self.assertEqual(self.localize("<p>اعمال 3:16 <sup>12</sup></p>"), "<p>اعمال ۳:۱۶ <sup>۱۲</sup></p>")

    def test_markup_and_addresses_keep_ascii(self):
        text = '<a href="/fa/act/3/#v16" data-v="16" id="v16">x</a>'
        self.assertEqual(self.localize(text), text)

    def test_other_languages_keep_their_digits(self):
        self.assertEqual(self.localize('<p>1 <span lang="en">2 <i>3</i></span> 4</p>'),
                         '<p>۱ <span lang="en">2 <i>3</i></span> ۴</p>')
        self.assertEqual(self.localize('<p>1 <span lang="fa">2</span><br>3</p>', "en"),
                         '<p>1 <span lang="fa">۲</span><br>3</p>')

    def test_script_style_code_and_references_keep_ascii(self):
        text = "<script>var a = 1;</script><style>p{margin:0 1px}</style><code>v1</code>&#8212;&#x2014;"
        self.assertEqual(self.localize(text), text)

    def test_digits_joined_to_latin_letters_keep_ascii(self):
        self.assertEqual(self.localize("<p>G2316 H430 CC0 7</p>"), "<p>G2316 H430 CC0 ۷</p>")


class PageTest(unittest.TestCase):
    def test_a_persian_page(self):
        text = build_site.page("fa", "Title", "<p>فصل 3</p>", path="/about/")
        self.assertIn("<p>فصل ۳</p>", text)
        self.assertIn(f'<meta name="owb-digits" content="fa:{FA}">', text)

    def test_other_pages_keep_ascii(self):
        text = build_site.page("en", "Title", "<p>Chapter 3</p>", path="/about/")
        self.assertIn("<p>Chapter 3</p>", text)

    def test_without_digits_nothing_changes(self):
        with mock.patch.multiple(languages, DIGITS={}), \
                mock.patch.object(build_site, "localize_digits", side_effect=AssertionError("called")):
            text = build_site.page("fa", "Title", "<p>فصل 3</p>", path="/about/")
        self.assertIn("<p>فصل 3</p>", text)
        self.assertNotIn("owb-digits", text)


if __name__ == "__main__":
    unittest.main()
