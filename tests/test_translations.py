"""scripts/check_translations.py: which article translations are missing or
behind their English article."""
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_translations  # noqa: E402

ENGLISH = """---
title: The Septuagint
summary: The Greek Old Testament.
date: 2026-10-11
order: 29
section: history
part: ot
---
The Septuagint is the Greek translation of the Hebrew Bible.

## Sources
"""


def article(title="La Septante", date="2026-10-11", order="29", source=None, body="La Septante est..."):
    lines = [f"title: {title}", "summary: L'Ancien Testament grec.", f"date: {date}",
             f"order: {order}", "section: history", "part: ot"]
    if source:
        lines.append(f"source: {source}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body + "\n"


class DigestTest(unittest.TestCase):
    def test_only_the_translated_words_count(self):
        d = check_translations.digest(ENGLISH)
        self.assertRegex(d, r"^[0-9a-f]{12}$")
        # Dates, order and trailing whitespace don't make a translation stale...
        self.assertEqual(d, check_translations.digest(ENGLISH.replace("2026-10-11", "2026-11-01")))
        self.assertEqual(d, check_translations.digest(ENGLISH.replace("order: 29", "order: 30")))
        self.assertEqual(d, check_translations.digest(ENGLISH.replace("Bible.", "Bible.   ")))
        # ...a change to the words does.
        self.assertNotEqual(d, check_translations.digest(ENGLISH.replace("Greek translation", "Greek version")))
        self.assertNotEqual(d, check_translations.digest(ENGLISH.replace("The Greek Old", "A Greek Old")))
        self.assertNotEqual(d, check_translations.digest(ENGLISH.replace("part: ot", "part: ot\nnav_title: LXX")))


class TreeTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.write("the-septuagint.md", ENGLISH)
        self.write("the-masoretes.md", ENGLISH.replace("Septuagint", "Masoretes").replace("order: 29", "order: 24"))

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_stamp_adds_and_replaces_the_source_line(self):
        path = self.write("fr/the-septuagint.md", article())
        check_translations.stamp(path, ENGLISH)
        text = path.read_text(encoding="utf-8")
        self.assertIn(f"source: {check_translations.digest(ENGLISH)}\n---\nLa Septante est...", text)
        self.assertTrue(text.startswith("---\ntitle: La Septante\n"))
        check_translations.stamp(path, ENGLISH.replace("Hebrew Bible", "Hebrew Scriptures"))
        self.assertEqual(path.read_text(encoding="utf-8").count("source: "), 1)

    def test_report_finds_each_kind_of_problem(self):
        current = check_translations.digest(ENGLISH)
        self.write("fr/the-septuagint.md", article(source=current))
        self.write("es/the-septuagint.md", article(source="000000000000"))
        self.write("es/the-masoretes.md", article(order="99", source="x"))
        self.write("es/gone.md", article(source=current))
        self.write("sw/the-septuagint.md", article())
        r = check_translations.report(self.root, ["fr", "es", "sw", "ko"])
        self.assertEqual(r["fr"]["missing"], ["the-masoretes"])
        self.assertEqual(r["fr"]["out_of_date"], [])
        self.assertEqual(r["fr"]["front_matter"], [])
        self.assertEqual(r["es"]["missing"], [])
        self.assertEqual(r["es"]["out_of_date"], ["the-masoretes", "the-septuagint"])
        # The Masoretes translation copied the Septuagint's order by mistake.
        self.assertEqual(r["es"]["front_matter"], [("the-masoretes", "order")])
        self.assertEqual(r["es"]["orphaned"], ["gone"])
        self.assertEqual(r["sw"]["not_stamped"], ["the-septuagint"])
        self.assertEqual(r["ko"]["missing"], ["the-masoretes", "the-septuagint"])

        out = io.StringIO()
        count = check_translations.print_report(r, out)
        text = out.getvalue()
        # One missing (fr) + two out of date, one front matter, one orphan (es)
        # + one missing, one not stamped (sw); Korean, with none, isn't counted.
        self.assertEqual(count, 7)
        self.assertIn("fr: 1 of 2 translated\n  missing (1): the-masoretes", text)
        self.assertIn("front matter differs from the English (1): the-masoretes (order)", text)
        self.assertIn("ko: no articles yet (2 to translate)", text)

    def test_a_current_language_says_so(self):
        for slug in ("the-septuagint", "the-masoretes"):
            english = (self.root / f"{slug}.md").read_text(encoding="utf-8")
            order = "29" if slug == "the-septuagint" else "24"
            self.write(f"fr/{slug}.md", article(order=order, source=check_translations.digest(english)))
        out = io.StringIO()
        self.assertEqual(check_translations.print_report(check_translations.report(self.root, ["fr"]), out), 0)
        self.assertEqual(out.getvalue(), "fr: 2 of 2 translated, all current\n")


class RepositoryTest(unittest.TestCase):
    def test_the_report_runs_on_the_articles(self):
        results = check_translations.report()
        self.assertNotIn("en", results)
        for lang, r in results.items():
            # A translation copies its English article's date, order, section and part.
            self.assertEqual(r["front_matter"], [], lang)
            self.assertEqual(r["orphaned"], [], lang)


if __name__ == "__main__":
    unittest.main()
