"""scripts/compare_search.py: its port of web/search.js's matching, which
the comparison with the API relies on. (The comparison itself needs the
live site and API, so it runs by hand.)"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compare_search as cs  # noqa: E402

VERSE = {"k": "v", "bk": "JHN", "c": 3, "v": 16, "vv": [16],
         "x": {"L": "\\v 16 For God loved the world", "B": "God’s love for the {{christos:Christ|Messiah}}",
               "R": "Señor"}}
NOTE = {"k": "n", "bk": "JHN", "c": 3, "v": 3, "t": "born from above", "al": ["born again"],
        "s": "The word means both."}


def matches(q, doc):
    return bool(cs.browser_results({"docs": [doc]}, q)[doc["k"]])


class BrowserMatchingTest(unittest.TestCase):
    def test_words_match_at_the_start_of_a_word(self):
        self.assertTrue(matches("lov", VERSE))
        self.assertTrue(matches("loved world", VERSE))
        self.assertFalse(matches("ove", VERSE))
        self.assertFalse(matches("love planet", VERSE))

    def test_folding_and_apostrophes(self):
        self.assertTrue(matches("senor", VERSE))
        self.assertTrue(matches("God's love", VERSE))   # curly apostrophe in the text
        self.assertFalse(matches("Gods", VERSE))

    def test_every_option_of_a_setting_and_no_verse_markers(self):
        self.assertTrue(matches("Messiah", VERSE))
        self.assertTrue(matches("Christ", VERSE))
        self.assertFalse(matches("v 16", VERSE))

    def test_phrases_and_note_fields(self):
        self.assertTrue(matches('"born from above"', NOTE))
        self.assertFalse(matches('"above from born"', NOTE))
        self.assertTrue(matches("again", NOTE))
        self.assertTrue(matches("means", NOTE))

    def test_document_keys_ignore_the_apis_highlight(self):
        self.assertEqual(cs.key(NOTE), cs.key({**NOTE, "hl": "⟦born⟧"}))


if __name__ == "__main__":
    unittest.main()
