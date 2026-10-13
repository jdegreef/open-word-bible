import unittest

from owb import markup

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

    def test_line_markers(self):
        text = "Blessed is the one who does not walk in the counsel of the wicked, \\q nor stand"
        self.assertTrue(markup.is_poetry(text))
        self.assertFalse(markup.is_poetry("In the beginning"))
        self.assertEqual(markup.line_markers(text), 1)
        self.assertEqual(markup.split_lines(text),
                         ["Blessed is the one who does not walk in the counsel of the wicked,", "nor stand"])
        self.assertEqual(markup.split_lines("In the beginning"), ["In the beginning"])
        self.assertEqual(markup.flat(text), text.replace(" \\q ", " "))
        # Verses first, then lines within each verse.
        parts = markup.split_verses("a, \\q b \\v 2 c; \\q d")
        self.assertEqual([markup.split_lines(t) for _, t in parts], [["a,", "b"], ["c;", "d"]])
        self.assertEqual(markup.line_errors(text), [])
        self.assertEqual(markup.line_errors("\\q a"), ["starts with a line marker"])


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
                            (["and the \\q light"], "line marker"),
                            ([" "], "empty")):
            with self.assertRaisesRegex(ValueError, reason):
                markup.alignment_ranges(text, bad)

if __name__ == "__main__":
    unittest.main()
