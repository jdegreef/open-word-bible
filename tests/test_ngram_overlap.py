import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ngram_overlap  # noqa: E402

RECORD = {
    "id": "COL.1.27.s1",
    "refs": ["COL.1.27"],
    "renderings": {"en": {
        "B": "God chose to make known how rich this is. \\v 27 The mystery is this: "
             "{{christos:Christ|the Messiah}} in you, the hope of glory.",
    }},
}


class NgramOverlapTest(unittest.TestCase):
    def test_plain_uses_defaults_and_drops_markers_and_brackets(self):
        self.assertEqual(ngram_overlap.plain("[the] Son \\v 2 of {{christos:Christ|Messiah}}"),
                         "the Son  of Christ")

    def test_words_keep_apostrophes(self):
        self.assertEqual(ngram_overlap.words("Christ’s body, God's people."),
                         ["Christ's", "body", "God's", "people"])

    def test_runs_merge_overlapping_ngrams(self):
        ours = "a b c d e x f g h".split()
        theirs = "q a b c d e r f g h".split()
        self.assertEqual(ngram_overlap.runs(ours, theirs, 3), [(0, 5), (6, 9)])
        self.assertEqual(ngram_overlap.runs(ours, theirs, 4), [(0, 5)])

    def test_compare_and_distinctive(self):
        editions = {
            "pd": {"COL.1.27": "To them God willed to make known ... Christ in you, the hope of glory"},
            "other": {"COL.1.27": "God chose to make known how rich ... Christ in you, the hope of glory."},
        }
        [result] = ngram_overlap.compare([RECORD], "en", ["L", "B"], editions, 5)
        self.assertEqual(result["level"], "B")
        text = {name: [" ".join(result["words"][s:e]) for s, e in spans]
                for name, spans in result["runs"].items()}
        self.assertEqual(text, {
            "pd": ["Christ in you the hope of glory"],
            "other": ["God chose to make known how rich", "Christ in you the hope of glory"],
        })
        found = ngram_overlap.distinctive(result, ["other"], ["pd"])
        self.assertEqual([" ".join(result["words"][s:e]) for s, e in found["other"]],
                         ["God chose to make known how rich"])

    def test_main_with_extra_file_only(self):
        with tempfile.TemporaryDirectory() as d:
            content = Path(d) / "COL.1.json"
            content.write_text(json.dumps({"records": [RECORD]}), encoding="utf-8")
            extra = Path(d) / "other.tsv"
            extra.write_text("# comment\nCOL.1.27\tGod chose to make known how rich it is\n",
                             encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                ngram_overlap.main([str(content), "--no-open-bibles", "--extra", f"other={extra}"])
        self.assertIn("other     7 words  God chose to make known how rich", out.getvalue())
        self.assertIn("(extra)", out.getvalue())


if __name__ == "__main__":
    unittest.main()
