import json
import unittest
from pathlib import Path

from owb import markup

# Shared with tests/js/markup.test.mjs, which runs the same cases against
# web/markup.js (the reader's copy of these rules).
VECTORS = json.loads((Path(__file__).parent / "markup_vectors.json").read_text(encoding="utf-8"))

TEXT = "the light of {{gender:all people|men}}, the {{christos:Messiah|Christ}}"


class MarkupTest(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(markup.render(TEXT), "the light of all people, the Messiah")

    def test_alternates(self):
        self.assertEqual(markup.render(TEXT, {"gender": 1, "christos": 1}),
                         "the light of men, the Christ")

    def test_out_of_range_and_unknown(self):
        self.assertEqual(markup.render(TEXT, {"gender": 7}), "the light of all people, the Messiah")
        self.assertEqual(markup.render("{{colour:red|blue}}", {"colour": 1}), "red")

    def test_plain_text_unchanged(self):
        self.assertEqual(markup.render("In the beginning"), "In the beginning")

    def test_spans(self):
        found = markup.spans(TEXT)
        self.assertEqual([(s.setting, s.options) for s in found],
                         [("gender", ("all people", "men")), ("christos", ("Messiah", "Christ"))])
        self.assertEqual(TEXT[found[0].start:found[0].end], "{{gender:all people|men}}")

    def test_stray_braces(self):
        self.assertFalse(markup.stray_braces(TEXT))
        self.assertTrue(markup.stray_braces("the {{gender:all people"))

    def test_verse_markers(self):
        text = "children of God \\v 13 children born of God."
        self.assertEqual(markup.verse_markers(text), [13])
        self.assertEqual(markup.split_verses(text),
                         [(None, "children of God"), (13, "children born of God.")])
        self.assertEqual(markup.split_verses("In the beginning"), [(None, "In the beginning")])


    def test_alignment_ranges_follow_the_rendering_in_order(self):
        text = "the light of {{gender:all people|men}} \\v 5 and the light shines"
        # The second "the" is found after "of", not at the start again.
        ranges = markup.alignment_ranges(text, ["the light", "{{gender:all people|men}}", "the light"])
        self.assertEqual([text[s:e] for s, e in ranges],
                         ["the light", "{{gender:all people|men}}", "the light"])
        self.assertEqual(ranges[2][0], text.rindex("the light"))
        for bad, reason in ((["shines", "light"], "after the previous"),
                            (["darkness"], "not found in rendering"),
                            (["of {{gender:all"], "cuts a setting span"),
                            (["men}} \\v 5 and"], "verse marker"),
                            ([" "], "empty")):
            with self.assertRaisesRegex(ValueError, reason):
                markup.alignment_ranges(text, bad)


class VectorsTest(unittest.TestCase):
    def test_settings_match_the_reader(self):
        self.assertEqual(list(markup.SETTINGS), VECTORS["settings"])

    def test_cases(self):
        for case in VECTORS["cases"]:
            with self.subTest(case["name"]):
                rendered = markup.render(case["text"], case["settings"])
                self.assertEqual(rendered, case["rendered"])
                if "verses" in case:
                    self.assertEqual([list(p) for p in markup.split_verses(rendered)], case["verses"])

    def test_known_differences(self):
        for case in VECTORS["differences"]:
            with self.subTest(case["name"]):
                if case["kind"] == "render":
                    self.assertEqual(markup.render(case["text"], case["settings"]), case["python"])
                else:
                    self.assertEqual([list(p) for p in markup.split_verses(case["text"])], case["python"])


if __name__ == "__main__":
    unittest.main()
