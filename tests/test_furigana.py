"""Furigana (owb/furigana.py, data/furigana/): readings over kanji runs."""
import json
import unittest
from pathlib import Path

from owb import furigana

ROOT = Path(__file__).resolve().parents[1]


class FuriganaTest(unittest.TestCase):
    def test_ranges_follow_the_kanji_runs_in_order(self):
        text = "光は闇の中で輝いている。闇はこの光に打ち勝った。"
        got = furigana.ranges(text, [["光", "ひかり"], ["闇", "やみ"], ["中", "なか"], ["輝", "かがや"],
                                     ["闇", "やみ"], ["光", "ひかり"], ["打", "う"], ["勝", "か"]])
        self.assertEqual([text[s:e] for s, e, _ in got], ["光", "闇", "中", "輝", "闇", "光", "打", "勝"])
        self.assertEqual(got[1][2], "やみ")
        for bad, reason in (([["中", "なか"], ["光", "ひかり"], ["闇", "やみ"]], "after the previous"),
                            ([["光", "ヒカリ"]], "not hiragana"),
                            ([["打ち", "う"]], "not a run"),
                            ([["光は", "ひかり"]], "not hiragana|not a run")):
            with self.assertRaisesRegex(ValueError, reason):
                furigana.ranges(text, bad)

    def test_runs_leave_setting_spans_alone(self):
        text = "{{units:約3キロ|十五スタディオン}}の所に神がいた。"
        self.assertEqual([r[2] for r in furigana.runs(text)], ["所", "神"])

    def test_every_reading_fits_its_rendering(self):
        records = {}
        for path in (ROOT / "content").glob("*/*.json"):
            for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
                records[r["id"]] = r
        self.assertEqual(furigana.errors(records), [])


if __name__ == "__main__":
    unittest.main()
