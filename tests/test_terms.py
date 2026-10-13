"""The key-terms glossary: /terms/ and a page per term (scripts/build_site.py)."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from owb import refs, validate  # noqa: E402
from tests.site_build import built_site  # noqa: E402

GRACE = ("grc", "5485")
YHWH = ("hbo", "3068")


class TermUsesTest(unittest.TestCase):
    def words(self, verse):
        ref = refs.parse(verse)
        data = json.loads(build_site.words_path(ref.book, ref.chapter).read_text(encoding="utf-8"))
        return {w["id"]: w for w in data["verses"][verse]}

    def test_uses_are_found_by_strongs_number_and_language(self):
        uses = build_site.term_uses()
        self.assertEqual(set(uses), set(validate.KEY_TERMS))
        grace = {u.record["id"]: u for u in uses[GRACE]}
        self.assertIn("JHN.1.17.s1", grace)
        for key, found in uses.items():
            for u in found:
                self.assertTrue(all(validate.token_language(tid) == key[0] for tid in u.tokens))
                self.assertLessEqual(len(u.verses), len(u.tokens))
        # Hebrew Strong's 4100 ("what", Genesis 2:19) is not Greek "believe".
        believe = {u.record["id"] for u in uses[("grc", "4100")]}
        self.assertFalse(any(rid.startswith("GEN.") for rid in believe))
        self.assertTrue(any(u.record["id"].startswith("GEN.2.") for u in uses[YHWH]))

    def test_each_use_is_a_word_with_the_terms_number(self):
        use = next(u for u in build_site.term_uses()[GRACE] if u.record["id"] == "JHN.1.17.s1")
        words = self.words("JHN.1.17")
        self.assertEqual(use.verses, ["JHN.1.17"])
        for tid in use.tokens:
            self.assertEqual(words[tid]["strong"], "5485")

    def test_uses_are_in_canonical_order_and_counted_once(self):
        for found in build_site.term_uses().values():
            keys = [refs.parse(u.verses[0]).sort_key() for u in found]
            self.assertEqual(keys, sorted(keys))
            ids = [u.record["id"] for u in found]
            self.assertEqual(len(ids), len(set(ids)))

    def test_an_exception_shows_the_decision_that_explains_it(self):
        # Luke 1:30: "found favor with God" at Balanced and Readable, as an
        # English rendering decision on the word explains.
        use = next(u for u in build_site.term_uses()[GRACE] if u.record["id"] == "LUK.1.30.s1")
        self.assertEqual(use.departs, ["B", "R"])
        explained = validate.explaining_decisions(use.record)
        for d in use.decisions:
            self.assertTrue(any(d in explained.get(tid, []) for tid in use.tokens))
        # A sentence that keeps the word everywhere is no exception, even
        # with a decision on the word.
        for u in build_site.term_uses()[GRACE]:
            if not u.departs:
                self.assertEqual(u.decisions, [])

    def test_emphasise_marks_the_settled_word(self):
        mark = build_site.emphasise
        self.assertEqual(mark("Grace & truth", ["grace"]),
                         '<mark class="term-hit">Grace</mark> &amp; truth')
        # The term's own case wins: "LORD" (the divine name), not "Lord".
        self.assertEqual(mark("the LORD said to my Lord", ["LORD"]),
                         'the <mark class="term-hit">LORD</mark> said to my Lord')
        self.assertEqual(mark("signs and wonders", ["sign"]),
                         '<mark class="term-hit">signs</mark> and wonders')
        # No allowed word: nothing is guessed.
        self.assertEqual(mark("You have found favor", ["grace"]), "You have found favor")

    def test_slugs_are_unique_and_readable(self):
        slugs = build_site.term_slugs()
        self.assertEqual(len(set(slugs.values())), len(slugs))
        self.assertEqual(slugs[GRACE], "grace")
        self.assertEqual(slugs[YHWH], "the-divine-name-yhwh")
        for slug in slugs.values():
            self.assertRegex(slug, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_english_for_every_level(self):
        gospel = validate.KEY_TERMS[("grc", "2098")]
        self.assertEqual(build_site.term_english(gospel), ["gospel", "good news"])
        html_text = build_site.term_english_html(gospel, "en")
        self.assertIn("Readable", html_text)
        self.assertIn("good news", html_text)


class TermPagesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def read(self, rel):
        return (self.out / rel / "index.html").read_text(encoding="utf-8")

    def test_index_lists_every_term_by_source_language(self):
        for lang in build_site.LANGUAGES:
            prefix = "" if lang == "en" else f"{lang}/"
            page = self.read(f"{prefix}terms")
            for key, term in validate.KEY_TERMS.items():
                self.assertIn(f'href="{build_site.url(lang, build_site.term_path(term))}"', page)
                self.assertIn(f'lang="{key[0]}">{term["lemma"]}<', page)
            self.assertLess(page.index('id="grc"'), page.index('id="hbo"'))
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("/terms/grace/", sitemap)
        self.assertIn("/es/terms/grace/", sitemap)

    def test_term_page_links_every_use_to_the_reader(self):
        page = self.read("terms/grace")
        term = validate.KEY_TERMS[GRACE]
        self.assertIn(f'lang="grc">{term["lemma"]}<', page)
        self.assertIn("Strong&rsquo;s G5485", page)
        self.assertIn('<a href="/jhn/1/#v17">John 1:17</a>', page)
        self.assertIn('<mark class="term-hit">', page)
        uses = build_site.term_uses()[GRACE]
        # Every sentence once in its book, and the exceptions again first.
        self.assertEqual(page.count('<li class="term-use'),
                         len(uses) + sum(bool(u.decisions) for u in uses))
        self.assertIn('class="term-use departs"', page)
        self.assertIn("Translated otherwise", page)

    def test_long_lists_fold_away(self):
        many = self.read("terms/the-divine-name-yhwh")
        self.assertIn('<details class="term-book" id="gen">', many)
        self.assertNotIn('class="term-book" id="gen" open', many)
        self.assertIn('href="#gen">Genesis <span>', many)
        few = next(term for key, term in validate.KEY_TERMS.items()
                   if 0 < build_site.term_count(term) <= build_site.TERM_OPEN_USES)
        page = self.read(build_site.term_path(few).strip("/"))
        self.assertRegex(page, r'<details class="term-book" id="[a-z0-9]+" open>')

    def test_term_pages_in_other_languages_keep_the_english(self):
        page = self.read("fr/terms/grace")
        self.assertIn('<a href="/fr/jhn/1/#v17">Jean 1:17</a>', page)
        self.assertIn('<p class="term-text" lang="en">', page)
        self.assertIn(build_site.t("fr", "notes_in_english"), page)

    def test_menu_and_footer_link_the_index(self):
        for lang in build_site.LANGUAGES:
            prefix = "" if lang == "en" else f"{lang}/"
            page = self.read(f"{prefix}about")
            href = build_site.url(lang, "/terms/")
            header = re.search(r'<header class="site">.*?</header>', page, re.S)[0]
            footer = re.search(r'<footer class="site">.*?</footer>', page, re.S)[0]
            self.assertIn(f'href="{href}"', header)
            self.assertIn(f'href="{href}"', footer)

    def test_reader_cards_link_key_terms(self):
        page = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        data = json.loads(re.search(
            r'<script type="application/json" id="owb-data">(.*?)</script>', page, re.S)[1])
        cards = {c["title"]: c for c in data["cards"]["list"]}
        self.assertEqual(cards["grace"]["href"], "/terms/grace/")
        self.assertNotIn("href", next(c for c in cards.values() if c["type"] == "name"))
        es = (self.out / "es" / "gen" / "2" / "index.html").read_text(encoding="utf-8")
        self.assertIn('"href":"/es/terms/the-divine-name-yhwh/"', es.replace(": ", ":"))
        reader = (self.out / "reader.js").read_text(encoding="utf-8")
        self.assertIn('t("card_term_link")', reader)


if __name__ == "__main__":
    unittest.main()
