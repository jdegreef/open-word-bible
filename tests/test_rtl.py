"""Right to left: a language's direction in data/languages.json
(owb/languages.py), <html dir="rtl"> for a page in such a language, and a dir
on text whose language reads the other way from what surrounds it
(build_site.isolate_directions; web/site.js does the same for text the
scripts add, tests/js/bidi.test.mjs). Arabic is the first reading language
written right to left; these tests also flag one for a while (Spanish, for
the length of a test), and take Arabic's flag away to check that with none,
pages are as they were before."""
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from owb import languages  # noqa: E402


def flagged_rtl(code):
    """A patch making code a reading language written right to left."""
    rtl = languages.RTL | {code}
    reading = tuple(c for c in languages.CODES if c in rtl)
    return mock.patch.multiple(languages, RTL=rtl, RTL_READING=reading)


def no_rtl_reading():
    """A patch leaving no reading language written right to left."""
    return mock.patch.multiple(languages, RTL=languages.RTL - set(languages.RTL_READING), RTL_READING=())


def tags_with_dir(text):
    """Every start tag in text that has a dir attribute."""
    return re.findall(r"<[a-zA-Z][^<>]*\sdir=\"[^\"]*\"[^<>]*>", text)


class DirectionTest(unittest.TestCase):
    def test_hebrew_and_its_aliases_read_right_to_left(self):
        for code in ("hbo", "arc", "he"):
            self.assertEqual(languages.direction(code), "rtl", code)
        self.assertEqual(languages.direction("grc"), "ltr")

    def test_arabic_is_the_one_reading_language_read_right_to_left(self):
        self.assertEqual(languages.RTL_READING, ("ar",))
        for code in languages.CODES:
            self.assertEqual(languages.direction(code), "rtl" if code == "ar" else "ltr", code)

    def test_a_tag_with_a_region_counts_as_its_language(self):
        with flagged_rtl("es"):
            self.assertEqual(languages.direction("es-419"), "rtl")
            self.assertEqual(languages.direction("es"), "rtl")
        self.assertEqual(languages.direction("es"), "ltr")

    def test_dir_is_ltr_or_rtl_where_given(self):
        data = json.loads((ROOT / "data" / "languages.json").read_text(encoding="utf-8"))
        for lang in (*data["reading"], *data["original"]):
            self.assertIn(lang.get("dir", "ltr"), languages.DIRECTIONS, lang["code"])


class IsolateTest(unittest.TestCase):
    """isolate_directions, with Arabic and Hebrew right to left."""

    @staticmethod
    def isolate(text, base):
        return build_site.isolate_directions(text, base, lambda c: "rtl" if c in ("ar", "hbo") else "ltr")

    def test_text_in_the_other_direction_gets_a_dir(self):
        self.assertEqual(self.isolate('<p lang="ar">x</p><p>y</p>', "ltr"),
                         '<p lang="ar" dir="rtl">x</p><p>y</p>')
        self.assertEqual(self.isolate('<p lang="en">x</p><p lang="ar">y</p>', "rtl"),
                         '<p lang="en" dir="ltr">x</p><p lang="ar">y</p>')

    def test_direction_is_relative_to_the_nearest_dir(self):
        # English inside Arabic inside an English page; Arabic inside that.
        text = '<div lang="ar">a <span lang="en">b <i lang="ar">c</i></span> d</div> <b lang="en">e</b>'
        self.assertEqual(
            self.isolate(text, "ltr"),
            '<div lang="ar" dir="rtl">a <span lang="en" dir="ltr">b <i lang="ar" dir="rtl">c</i></span> d</div> '
            '<b lang="en">e</b>')

    def test_a_dir_of_its_own_stays(self):
        text = '<p lang="hbo" dir="rtl">x</p><a lang="ar" dir="ltr"><span lang="ar">y</span></a>'
        self.assertEqual(self.isolate(text, "ltr"), text.replace('<span lang="ar">', '<span lang="ar" dir="rtl">'))

    def test_void_and_self_closing_elements_and_scripts(self):
        text = ('<p lang="ar">a<br><img src="x" alt="">b<svg><use href="#arrow"/></svg>'
                '<script>var s = "<i lang=\\"en\\">";</script><span lang="en">c</span></p>')
        self.assertEqual(self.isolate(text, "ltr"),
                         text.replace('<p lang="ar">', '<p lang="ar" dir="rtl">')
                             .replace('<span lang="en">', '<span lang="en" dir="ltr">'))

    def test_hreflang_and_data_lang_are_not_languages_of_text(self):
        text = '<a href="/ar/" hreflang="ar" data-lang="ar">x</a>'
        self.assertEqual(self.isolate(text, "ltr"), text)


class PageTest(unittest.TestCase):
    """build_site.page, with no reading language right to left, in Arabic,
    and with Spanish flagged as one too."""

    def page(self, lang):
        return build_site.page(lang, "Title", '<p>Body <span lang="hbo" dir="rtl">x</span></p>', path="/about/")

    def test_left_to_right_pages_are_as_before(self):
        with no_rtl_reading(), \
                mock.patch.object(build_site, "isolate_directions", side_effect=AssertionError("called")):
            for lang in ("en", "es"):
                text = self.page(lang)
                self.assertIn(f'<!doctype html>\n<html lang="{lang}">\n<head>', text)
                self.assertNotIn("owb-rtl", text)
                # Only the Hebrew in the body has a dir.
                self.assertEqual(tags_with_dir(text), ['<span lang="hbo" dir="rtl">'], lang)
        self.assertEqual(build_site.forward("en"), "&rarr;")
        self.assertEqual(build_site.html_dir("en"), "")

    def test_a_right_to_left_page(self):
        with flagged_rtl("es"):
            text = self.page("es")
            self.assertEqual(build_site.forward("es"), "&larr;")
        self.assertIn('<html lang="es" dir="rtl">', text)
        self.assertIn('<meta name="owb-rtl" content="ar arc es hbo he">', text)
        # The footer's languages in their own names: each left-to-right one
        # is isolated, its gloss in the page's language is not.
        self.assertIn('<a href="/about/" lang="en" dir="ltr" hreflang="en" data-lang="en">English '
                      '<span class="lang-gloss" lang="es" dir="rtl">(inglés)</span></a>', text)
        self.assertIn('<span lang="es" aria-current="true">Español', text)
        self.assertIn('<span lang="hbo" dir="rtl">x</span>', text)
        # Nothing in the page's own direction is given a dir.
        self.assertNotIn('lang="es" dir="rtl" aria-current', text)

    def test_a_left_to_right_page_beside_a_right_to_left_language(self):
        with flagged_rtl("es"):
            text = self.page("en")
        self.assertIn('<html lang="en">', text)
        self.assertIn('<meta name="owb-rtl" content="ar arc es hbo he">', text)
        self.assertIn('<a href="/es/about/" lang="es" dir="rtl" hreflang="es" data-lang="es">Español '
                      '<span class="lang-gloss" lang="en" dir="ltr">(Spanish)</span></a>', text)
        self.assertNotIn('lang="fr" dir=', text)


    def test_an_arabic_page(self):
        text = self.page("ar")
        self.assertEqual(build_site.forward("ar"), "&larr;")
        self.assertIn('<html lang="ar" dir="rtl">', text)
        self.assertIn('<meta name="owb-rtl" content="ar arc hbo he">', text)
        self.assertRegex(text, r'<a href="/about/" lang="en" dir="ltr" hreflang="en" data-lang="en">English '
                               r'<span class="lang-gloss" lang="ar" dir="rtl">\(')
        self.assertIn('<span lang="ar" aria-current="true">العربية', text)
        # An English page names Arabic in its footer, isolated.
        self.assertIn('<a href="/ar/about/" lang="ar" dir="rtl" hreflang="ar" data-lang="ar">العربية', self.page("en"))


class StyleTest(unittest.TestCase):
    """web/style.css and web/admin.css give margins, padding, borders and
    alignment by the start and end of a line, which follow the page's
    direction, not by left and right. Positions keep left and right only
    to centre (left: 50%) or stretch across (left and right alike), and a
    float on the left is floated right on a right-to-left page."""

    def test_margins_padding_and_borders_are_logical(self):
        css = re.sub(r"/\*.*?\*/", "", (ROOT / "web" / "style.css").read_text(encoding="utf-8"), flags=re.S)
        css += re.sub(r"/\*.*?\*/", "", (ROOT / "web" / "admin.css").read_text(encoding="utf-8"), flags=re.S)
        self.assertEqual(re.findall(r"(?:margin|padding|border)-(?:left|right)\b[^;}]*", css), [])
        self.assertEqual(re.findall(r"text-align:\s*(?:left|right)", css), [])
        floats = re.findall(r"([^{}]*)\{[^}]*float:\s*(left|right)", css)
        self.assertEqual(sorted(side for _, side in floats), ["left", "left", "right"])
        self.assertTrue(all("[dir=\"rtl\"]" in rule for rule, side in floats if side == "right"))
