"""Source loading. Sources are found via OWB_VENDOR, defaulting to vendor/."""
import unittest

from owb import refs
from owb.sources import macula_greek, sblgnt


class RefsTest(unittest.TestCase):
    def test_round_trip(self):
        self.assertEqual(str(refs.parse("JHN.1.1")), "JHN.1.1")
        self.assertEqual(refs.from_sblgnt("1Cor 13:4"), refs.Ref("1CO", 13, 4))

    def test_all_27_books(self):
        self.assertEqual(len(refs.NT_BOOKS), 27)

    def test_bad_id(self):
        with self.assertRaises(ValueError):
            refs.parse("XYZ.1.1")


class SblgntTest(unittest.TestCase):
    def test_john_1_1(self):
        [verse] = sblgnt.load_verses("JHN.1.1")
        self.assertEqual(
            verse.text,
            "Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ θεὸς ἦν ὁ λόγος.")
        self.assertEqual(verse.marks, ())

    def test_john_1_18_variant_marks(self):
        [verse] = sblgnt.load_verses("JHN.1.18")
        for mark in sblgnt.VARIANT_MARKS:
            self.assertNotIn(mark, verse.text)
        self.assertEqual([m for _, m in verse.marks], ["⸂", "⸃"])
        [(mark, start, end, text)] = sblgnt.marked_spans(verse)
        self.assertEqual(mark, "⸂⸃")
        self.assertEqual(verse.text[start:end], text)
        words = [t.text for t in macula_greek.load_tokens("JHN.1.18")]
        self.assertEqual(text, " ".join(words[4:6]))  # μονογενὴς θεὸς, from the data
        self.assertEqual(text.split(), ["μονογενὴς", "θεὸς"])

    def test_range(self):
        self.assertEqual(len(sblgnt.load_verses("JHN.1.1", "JHN.1.5")), 5)


class MaculaGreekTest(unittest.TestCase):
    def test_john_1_1_token_count(self):
        tokens = macula_greek.load_tokens("JHN.1.1")
        self.assertEqual(len(tokens), 17)
        self.assertEqual(tokens[0].id, "n43001001001")
        self.assertEqual([t.position for t in tokens], list(range(1, 18)))

    def test_words_match_sblgnt(self):
        [verse] = sblgnt.load_verses("JHN.1.1")
        words = [t.text + t.after.rstrip() for t in macula_greek.load_tokens("JHN.1.1")]
        self.assertEqual(" ".join(words), verse.text)

    def test_token_fields(self):
        tok = macula_greek.load_tokens("JHN.1.1")[4]
        self.assertEqual((tok.lemma, tok.morph, tok.strong, tok.gloss), ("λόγος", "N-NSM", "3056", "Word"))


if __name__ == "__main__":
    unittest.main()
