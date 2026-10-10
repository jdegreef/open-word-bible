import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_skeleton import skeleton  # noqa: E402
from owb import validate  # noqa: E402


def boundaries(records):
    return [(r["id"], r["source"]["tokens"][-1]) for r in records]


def content(path):
    return json.loads((ROOT / "content" / path).read_text(encoding="utf-8"))["records"]


class SkeletonTest(unittest.TestCase):
    def test_john_prologue_sentences(self):
        records = skeleton("JHN.1.1", "JHN.1.18")["records"]
        made, ours = boundaries(records), boundaries(content("JHN/JHN.1.1-18.json"))
        # Our records follow the SBLGNT's sentences except at John 1:3, where
        # a punctuation decision keeps the last two words with verse 3.
        differ = [b for b in made if b not in ours]
        self.assertEqual(differ, [("JHN.1.3.s1", "n43001003010"),
                                  ("JHN.1.3.s2", "n43001004012")])

    def test_philippians_sentences(self):
        made = boundaries(skeleton("PHP.4.1", "PHP.4.9")["records"])
        ours = boundaries(content("PHP/PHP.4.1-9.json"))
        # Verses 6-7 were joined by hand: verse 7's "and" continues verse 6.
        self.assertEqual([b for b in made if b not in ours], [("PHP.4.6.s1", "n50004006019"),
                                                              ("PHP.4.7.s1", "n50004007020")])
        self.assertEqual([b for b in ours if b not in made], [("PHP.4.6.s1", "n50004007020")])

    def test_sentence_across_verses_gets_markers(self):
        record = next(r for r in skeleton("JHN.1.12", "JHN.1.13")["records"])
        self.assertEqual(record["refs"], ["JHN.1.12", "JHN.1.13"])
        self.assertEqual(record["renderings"]["en"]["B"], "\\v 13 ")
        self.assertFalse([e for e in validate.validate_record(record)
                          if "verse markers" in e or "source" in e])


if __name__ == "__main__":
    unittest.main()
