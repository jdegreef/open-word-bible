"""scripts/settings_parity.py: reader settings used alike across languages and levels."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import settings_parity as sp  # noqa: E402


def record(rid, **renderings):
    return {"id": rid, "renderings": renderings}


class CountsTest(unittest.TestCase):
    def test_counts_spans_per_language_and_setting(self):
        records = [record("JHN.1.1.s1",
                          en={"B": "{{christos:Christ|the Messiah}} and {{deity_pronoun:he|He}}"},
                          hi={"B": "मसीह"})]
        spans, rendered = sp.counts(records)
        self.assertEqual(spans["en"]["christos"], 1)
        self.assertEqual(spans["en"]["deity_pronoun"], 1)
        self.assertEqual(spans["hi"]["christos"], 0)
        self.assertEqual(rendered, {"en": 1, "hi": 1})

    def test_parity_counts_records_the_english_spans(self):
        records = [
            record("A.1.1.s1", en={"B": "{{christos:Christ|Messiah}}"},
                   fr={"B": "{{christos:Christ|Messie}}"}, hi={"B": "मसीह"}),
            record("A.1.2.s1", en={"B": "{{christos:Christ|Messiah}}"},
                   fr={"B": "{{christos:Christ|Messie}}"}, hi={"B": "मसीह"}),
            record("A.1.3.s1", en={"B": "plain"}, fr={"B": "{{christos:Christ|Messie}}"}),
        ]
        pairs = sp.parity(records)
        self.assertEqual(pairs[("fr", "christos")], (2, 2))
        self.assertEqual(pairs[("hi", "christos")], (2, 0))


class OutliersTest(unittest.TestCase):
    def test_flags_zero_and_far_below_median(self):
        shares = {("es", "gender"): 0.3, ("fr", "gender"): 0.7, ("pt", "gender"): 0.4,
                  ("sw", "gender"): 0.0, ("vi", "gender"): 0.1}
        found = {(lang, setting): note for lang, setting, _s, _m, note
                 in sp.outliers(shares, documented={("sw", "gender"): "brief"})}
        self.assertEqual(found, {("sw", "gender"): "brief", ("vi", "gender"): None})

    def test_documented_outliers_point_at_existing_briefs(self):
        for note in sp.DOCUMENTED.values():
            path = note.split(" ")[0].rstrip(":")
            self.assertTrue((ROOT / path).is_file(), path)

    def test_the_content_has_no_undocumented_outlier(self):
        _text, undocumented = sp.report(sp.load_records())
        self.assertEqual(undocumented, [])


class LevelsTest(unittest.TestCase):
    def kinds(self, records, lang="en", setting="deity_pronoun"):
        return {(rid, a, b): kind for rid, l, s, a, b, kind, _h
                in sp.level_candidates(records, settings=(setting,), langs={lang})}

    def test_other_wording_is_fine(self):
        records = [record("X.1.1.s1", en={"B": "and {{deity_pronoun:he|He}} spoke", "R": "and God spoke"})]
        self.assertEqual(self.kinds(records), {("X.1.1.s1", "B", "R"): "fine"})

    def test_sentence_start_capital_is_not_the_lowercase_pronoun(self):
        records = [record("X.1.1.s1", en={"B": "and {{deity_pronoun:he|He}} spoke", "R": "He spoke."})]
        self.assertEqual(self.kinds(records)[("X.1.1.s1", "B", "R")], "fine")

    def test_unwrapped_pronoun_is_a_candidate(self):
        records = [record("X.1.1.s1", en={"B": "and {{deity_pronoun:he|He}} spoke", "R": "then he spoke"})]
        self.assertEqual(self.kinds(records)[("X.1.1.s1", "B", "R")], "candidate")

    def test_corroborated_by_other_languages_is_a_likely_gap(self):
        records = [record(
            "X.1.1.s1",
            en={"B": "and {{deity_pronoun:he|He}} spoke", "R": "then he spoke"},
            fr={"R": "puis {{deity_pronoun:il|Il}} parla"},
            pt={"R": "então {{deity_pronoun:ele|Ele}} falou"})]
        self.assertEqual(self.kinds(records)[("X.1.1.s1", "B", "R")], "likely_gap")

    def test_word_boundaries_and_scripts_without_spaces(self):
        self.assertEqual(sp.occurrences("the shepherd he", "he", "en"), 1)
        self.assertEqual(sp.occurrences("{{deity_pronoun:he|He}} and he", "he", "en"), 1)
        self.assertEqual(sp.occurrences("イエス・キリストが", "キリスト", "ja"), 1)

    def test_level_summary_counts_each_record_once(self):
        records = [record("X.1.1.s1", en={"L": "{{deity_pronoun:he|He}}", "B": "{{deity_pronoun:he|He}}",
                                          "R": "so he did"})]
        summary = sp.level_summary(records, settings=("deity_pronoun",))
        self.assertEqual(summary[("en", "deity_pronoun")]["candidate"], 1)


if __name__ == "__main__":
    unittest.main()
