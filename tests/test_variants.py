"""Text variants: scripts/variants.py (the footnote policy, docs/text-variants.md)
and the site's /variants/ page."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
import variants  # noqa: E402
from tests.site_build import built_site  # noqa: E402

HEBREW = {"source": {"language": "hbo"}}
GREEK = {"source": {"language": "grc"}}


def decision(reason, choice="x"):
    return {"category": "text_variant", "choice": choice, "reason": reason, "footnote": False}


class CategoryTest(unittest.TestCase):
    def cat(self, reason, record=HEBREW):
        return variants.category(decision(reason), record)

    def test_policy_categories(self):
        self.assertEqual(self.cat("A few manuscripts lack this verse."), "verses")
        self.assertEqual(self.cat("Many later manuscripts add it, as the King James Version does."),
                         "english_bible")
        self.assertEqual(self.cat("The written consonants spell it in a shorter form; both mean the same."),
                         "same_sense")
        self.assertEqual(self.cat("The scribes marked the word to be read as a plural."), "spelling")
        self.assertEqual(self.cat("The Greek translation reads 'he set', with God as the one acting."),
                         "versions")
        self.assertEqual(self.cat("Some manuscripts read 'thieves', which would picture the day as dawn.",
                                  GREEK), "sense")
        self.assertEqual(self.cat("Many later manuscripts add 'of Christ'.", GREEK), "manuscripts")
        self.assertEqual(self.cat("As in verse 4."), "covered")
        self.assertEqual(self.cat("The sense is nearly the same, so no footnote.", GREEK), "stated")

    def test_a_reading_that_changes_the_sense_wins_over_spelling(self):
        reason = "The written letters spell 'his son', which would make the words part of the narration."
        self.assertEqual(self.cat(reason), "sense")
        self.assertTrue(variants.expected_footnote(decision(reason), HEBREW))

    def test_psalm_105_verses_22_and_27_are_treated_alike(self):
        found = {(r["id"], d["id"]): d for _, r, d in variants.variants({"PSA"})}
        v22 = found[("PSA.105.22.s1", "m1")]
        v27 = found[("PSA.105.27.s1", "m2")]
        records = {r["id"]: r for _, r, _ in variants.variants({"PSA"})}
        self.assertTrue(variants.expected_footnote(v22, records["PSA.105.22.s1"]))
        self.assertTrue(variants.expected_footnote(v27, records["PSA.105.27.s1"]))

    def test_content_outside_the_psalms_follows_the_policy(self):
        books = {p.name for p in variants.CONTENT.iterdir() if p.is_dir()} - {"PSA"}
        self.assertEqual([(r["id"], d["id"]) for _, r, d, _ in variants.inconsistent(books)], [])


class PageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def read(self, rel):
        return (self.out / rel / "index.html").read_text(encoding="utf-8")

    def test_page_lists_every_footnoted_variant_with_a_link(self):
        page = self.read("variants")
        found = build_site.footnoted_variants()
        self.assertEqual(page.count('<li class="variant">'), sum(len(v) for _, v in found))
        self.assertIn('<a href="/psa/105/#v22">', page)
        self.assertIn('id="gen"', page)
        self.assertIn(build_site.t("en", "variants.heading"), page)

    def test_every_language_has_the_page(self):
        for lang in build_site.LANGUAGES:
            if lang == "en":
                continue
            page = self.read(f"{lang}/variants")
            self.assertIn(build_site.t(lang, "variants.heading"), page)
            self.assertIn(f'href="/{lang}/psa/105/#v22"', page)
        about = self.read("about")
        self.assertIn('href="/variants/"', about)
        self.assertIn("/variants/", (self.out / "sitemap.xml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
