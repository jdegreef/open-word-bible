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


if __name__ == "__main__":
    unittest.main()
