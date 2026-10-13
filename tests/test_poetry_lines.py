import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import poetry_lines  # noqa: E402
from owb import markup  # noqa: E402


def verse(vid):
    book, chapter, _ = vid.split(".")
    path = ROOT / "data" / "hbo" / f"{book}.{chapter}.json"
    return json.loads(path.read_text(encoding="utf-8"))["verses"][vid]


class PoetryLinesTest(unittest.TestCase):
    def test_cola_follow_the_main_accents(self):
        # Psalm 23:2 has one atnach: two cola. Psalm 1:1 has olev-weyored
        # and atnach: three.
        parts, names = poetry_lines.cola("PSA", verse("PSA.23.2"))
        self.assertEqual((len(parts), names), (2, ["atnach"]))
        parts, names = poetry_lines.cola("PSA", verse("PSA.1.1"))
        self.assertEqual((len(parts), names), (3, ["olev-weyored", "atnach"]))
        # Every word is in exactly one colon.
        self.assertEqual(sum(len(seg.split()) for colon in parts for seg in colon),
                         sum(len(g.split()) for _, g in poetry_lines.words(verse("PSA.1.1")) if g))

    def test_fill_breaks_after_the_only_semicolon_or_colon(self):
        self.assertEqual(poetry_lines.fill("Tremble, and do not sin; speak in your heart."),
                         "Tremble, and do not sin; \\q speak in your heart.")
        for text in ("One; two; three.", "No mark at all.", "Already \\q marked; here.",
                     "{{gender:a;b|c}} and so"):
            self.assertIsNone(poetry_lines.fill(text), text)
        self.assertEqual(markup.line_errors(poetry_lines.fill("a; b")), [])


if __name__ == "__main__":
    unittest.main()
