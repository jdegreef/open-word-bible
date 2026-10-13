import copy
import json
import re
import unittest
from pathlib import Path

from owb import validate

EXAMPLE = Path(__file__).resolve().parents[1] / "content" / "JHN" / "JHN.1.1-18.json"


def example_records():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))["records"]


class ValidateTest(unittest.TestCase):
    def test_example_file_validates(self):
        self.assertEqual(validate.validate_file(EXAMPLE), [])

    def test_made_up_token_fails(self):
        record = example_records()[0]
        record["decisions"][0]["tokens"] = ["n43001001099"]
        errors = validate.validate_record(record)
        self.assertTrue(any("unknown token 'n43001001099'" in e for e in errors), errors)

    def test_made_up_source_token_fails(self):
        record = example_records()[0]
        record["source"]["tokens"].append("n43001001018")
        self.assertTrue(validate.validate_record(record))

    def test_token_from_another_verse_fails(self):
        record = example_records()[1]  # John 1:2
        record["decisions"][0]["tokens"] = ["n43001001001"]  # John 1:1
        self.assertTrue(validate.validate_record(record))

    def test_edited_source_text_fails(self):
        record = example_records()[0]
        record["source"]["text"] += " "
        self.assertTrue(any("source.text" in e for e in validate.validate_record(record)))

    def test_unknown_setting_fails(self):
        record = example_records()[0]
        record["renderings"]["en"]["B"] = "In the {{colour:beginning|start}}"
        self.assertTrue(any("unknown setting 'colour'" in e for e in validate.validate_record(record)))

    def test_known_setting_passes(self):
        record = example_records()[0]
        record["renderings"]["en"]["B"] = "the light of {{gender:all people|men}}"
        record.pop("alignments", None)   # they belong to the real rendering
        self.assertEqual(validate.validate_record(record), [])

    def test_line_markers_between_words_pass(self):
        record = next(r for r in example_records() if r["id"] == "JHN.1.12.s1")
        en = record["renderings"]["en"]
        en["B"] = en["B"].replace(", ", ", \\q ", 1)
        self.assertIn("\\q", en["B"])
        self.assertEqual(validate.validate_record(record), [])

    def test_misplaced_line_markers_fail(self):
        for bad, reason in (("\\q In the beginning", "starts with a line marker"),
                            ("In the beginning \\q", "ends with a line marker"),
                            ("In the \\q \\q beginning", "doubled line marker"),
                            ("In the\\q beginning", "stand alone"),
                            ("In the {{gender:all \\q people|men}}", "inside a setting span"),
                            ("In the \\x beginning", "unknown backslash marker")):
            record = example_records()[0]
            record["renderings"]["en"]["L"] = bad
            errors = validate.validate_record(record)
            self.assertTrue(any(reason in e for e in errors), (bad, errors))

    def test_line_marker_next_to_a_verse_marker_fails(self):
        record = next(r for r in example_records() if r["id"] == "JHN.1.12.s1")
        record["renderings"]["en"]["B"] = record["renderings"]["en"]["B"].replace("\\v 13 ", "\\q \\v 13 ")
        self.assertTrue(any("next to a verse marker" in e for e in validate.validate_record(record)))

    def test_line_marker_in_the_gloss_fails(self):
        record = example_records()[0]
        record["literal_gloss"] = record["literal_gloss"].replace(" ", " \\q ", 1)
        self.assertTrue(any("renderings only" in e for e in validate.validate_record(record)))

    def test_placeholder_left_in_the_text_fails(self):
        record = example_records()[0]
        record["renderings"]["en"]["R"] = "In the beginning @He@ was there."
        self.assertTrue(any("placeholder '@He@'" in e for e in validate.validate_record(record)))

    def test_layer_language_rules(self):
        base = example_records()[0]
        meaning = copy.deepcopy(base)
        meaning["decisions"][0]["language"] = "en"
        self.assertTrue(any("language null" in e for e in validate.validate_record(meaning)))
        rendering = copy.deepcopy(base)
        rendering["decisions"][4]["language"] = None
        self.assertTrue(validate.validate_record(rendering))

    def test_bad_enums_fail(self):
        record = example_records()[0]
        record["status"] = "approved"
        record["decisions"][0]["category"] = "vibes"
        errors = validate.validate_record(record)
        self.assertTrue(any("status" in e for e in errors))
        self.assertTrue(any("category" in e for e in errors))

    def test_enums_come_from_schema(self):
        self.assertEqual(validate.STATUSES, ["ai_draft", "meaning_reviewed", "reviewed", "revised"])
        self.assertIn("setting_alternative", validate.CATEGORIES)

    def test_sentence_across_verses_needs_its_marker(self):
        record = next(r for r in example_records() if r["id"] == "JHN.1.12.s1")
        self.assertEqual(record["refs"], ["JHN.1.12", "JHN.1.13"])
        self.assertEqual(validate.validate_record(record), [])
        record["renderings"]["en"]["B"] = record["renderings"]["en"]["B"].replace("\\v 13 ", "")
        self.assertTrue(any("verse markers" in e for e in validate.validate_record(record)))

    def _reason_errors(self, word):
        record = example_records()[0]
        record["decisions"][0]["reason"] += f" Compare {word}."
        return [e for e in validate.validate_record(record) if "source data" in e]

    def test_greek_copied_from_the_data_passes(self):
        from owb.sources import macula_greek
        tok = macula_greek.load_tokens("JHN.1.1")[4]
        for word in (tok.text, tok.lemma, tok.normalized):
            self.assertEqual(self._reason_errors(word), [], word)

    def test_greek_typed_by_hand_fails(self):
        import unicodedata
        from owb.sources import macula_greek
        word = macula_greek.load_tokens("JHN.1.1")[4].text
        # The same word with oxia for tonos, decomposed, or misspelled.
        lookalike = word.translate({0x03cc: 0x1f79})
        self.assertNotEqual(lookalike, word)
        for bad in (lookalike, unicodedata.normalize("NFD", word), word + word[-1]):
            errors = self._reason_errors(bad)
            self.assertTrue(errors and "decisions[0].reason: Greek" in errors[0], bad)

    def test_greek_in_renderings_is_checked_too(self):
        from owb.sources import macula_greek
        word = macula_greek.load_tokens("JHN.1.1")[4].text
        record = example_records()[0]
        record["renderings"]["en"]["L"] += " " + word[::-1]
        self.assertTrue(any("renderings.en.L: Greek" in e
                            for e in validate.validate_record(record)))

    def test_hebrew_copied_from_the_data_passes(self):
        from owb import refs
        from owb.sources import macula_hebrew
        prefix, noun = macula_hebrew._all()[refs.parse("GEN.1.1")][:2]
        whole = prefix.text + noun.text
        for word in (noun.text, noun.lemma, whole, macula_hebrew._ACCENTS.sub("", whole)):
            self.assertEqual(self._reason_errors(word), [], word)

    def test_hebrew_typed_by_hand_fails(self):
        from owb import refs
        from owb.sources import macula_hebrew
        noun = macula_hebrew._all()[refs.parse("GEN.1.1")][1]
        errors = self._reason_errors(noun.lemma[::-1])
        self.assertTrue(errors and "Hebrew" in errors[0], errors)

    def test_genesis_validates(self):
        for path in sorted((EXAMPLE.parents[1] / "GEN").glob("*.json")):
            self.assertEqual(validate.validate_file(path), [], path)

    def _genesis(self, rid):
        path = EXAMPLE.parents[1] / "GEN" / "GEN.1.1-13.json"
        return next(r for r in json.loads(path.read_text(encoding="utf-8"))["records"]
                    if r["id"] == rid)

    def test_hebrew_record_must_hold_whole_verses(self):
        record = self._genesis("GEN.1.3.s1")
        record["source"]["tokens"] = record["source"]["tokens"][:-2]
        del record["source"]["text"]
        record["decisions"] = []
        errors = validate.validate_record(record)
        self.assertTrue(any("every word of its verses" in e for e in errors), errors)

    def test_hebrew_source_text_is_rebuilt_from_morphemes(self):
        record = self._genesis("GEN.1.1.s1")
        # A prefix is written joined to its word: 11 morphemes, 7 words.
        self.assertEqual(len(record["source"]["tokens"]), 11)
        self.assertEqual(len(record["source"]["text"].split()), 7)
        record["source"]["text"] = record["source"]["text"].replace(" ", "", 1)
        self.assertTrue(any("source.text" in e for e in validate.validate_record(record)))

    def test_source_text_id_must_match_its_language(self):
        record = self._genesis("GEN.1.1.s1")
        record["source"]["text_id"] = "SBLGNT@v1.2"
        errors = validate.validate_record(record)
        self.assertTrue(any("is not the text for 'hbo'" in e for e in errors), errors)

    def test_record_cut_mid_sentence_fails(self):
        record = example_records()[0]
        record["source"]["tokens"] = record["source"]["tokens"][:5]
        del record["source"]["text"]
        record["decisions"] = [d for d in record["decisions"]
                               if set(d["tokens"]) <= set(record["source"]["tokens"])]
        self.assertTrue(any("ends mid-sentence at n43001001005" in e
                            for e in validate.validate_record(record)))

    def test_two_sentences_in_one_record_fail(self):
        first, second = example_records()[:2]
        first["refs"] += second["refs"]
        first["source"]["tokens"] += second["source"]["tokens"]
        del first["source"]["text"]
        for level in "LBR":
            for lang in first["renderings"]:
                first["renderings"][lang][level] += " \\v 2 x"
        first["literal_gloss"] += " \\v 2 x"
        errors = validate.validate_record(first)
        self.assertTrue(any("a sentence ends at n43001001017" in e for e in errors), errors)

    def test_punctuation_decision_allows_a_different_boundary(self):
        record = next(r for r in example_records() if r["id"] == "JHN.1.3.s1")
        self.assertEqual(validate.validate_record(record), [])
        record["decisions"] = [d for d in record["decisions"] if d["category"] != "punctuation"]
        errors = validate.validate_record(record)
        self.assertTrue(any("a sentence ends at n43001003010" in e for e in errors), errors)
        self.assertTrue(any("ends mid-sentence at n43001003012" in e for e in errors), errors)

    def test_meaning_decision_with_a_wording_category_fails(self):
        record = example_records()[0]
        record["decisions"][0]["category"] = "word_choice"
        self.assertTrue(any("about wording" in e for e in validate.validate_record(record)))

    def test_meaning_categories_come_from_schema(self):
        self.assertIn("word_sense", validate.MEANING_CATEGORIES)
        self.assertNotIn("setting_alternative", validate.MEANING_CATEGORIES)

    def test_meaning_decision_naming_a_language_fails(self):
        for text in ("English needs the article here.", "En espa\u00f1ol se dice así."):
            record = example_records()[0]
            record["decisions"][0]["reason"] = text
            errors = validate.validate_record(record)
            self.assertTrue(any("decisions[0].reason: names" in e for e in errors), (text, errors))

    def test_meaning_decision_with_a_setting_fails(self):
        record = example_records()[0]
        record["decisions"][0]["choice"] = "{{gender:all people|men}}"
        self.assertTrue(any("decisions[0].choice: a reader setting is wording" in e
                            for e in validate.validate_record(record)))

    def test_rendering_decision_may_name_its_language(self):
        record = next(r for r in example_records() if r["id"] == "JHN.1.3.s1")
        rendering = next(d for d in record["decisions"] if d["layer"] == "rendering")
        rendering["reason"] = "Plain English for Readable."
        self.assertEqual(validate.validate_record(record), [])

    def test_badly_formed_setting_spans_fail(self):
        for span, message in (("{{gender:people}}", "at least one"),
                              ("{{gender:people|}}", "at least one"),
                              ("{{gender:people|people}}", "repeats"),
                              ("{{gender:people| men}}", "spaces"),
                              ("{{deity_pronoun:him|He}}", "capitalised")):
            record = example_records()[0]
            record["renderings"]["en"]["B"] = f"the light of {span}"
            errors = validate.validate_record(record)
            self.assertTrue(any(message in e for e in errors), (span, errors))

    def test_alignments_must_follow_the_rendering_in_order(self):
        record = example_records()[0]  # John 1:1
        toks = record["source"]["tokens"]
        text = record["renderings"]["en"]["B"]
        word = text.split()[0]
        record["alignments"] = [{"tokens": toks[:1], "language": "en", "level": "B", "target_span": word}]
        self.assertEqual(validate.validate_record(record), [])
        record["alignments"].append({"tokens": toks[:1], "language": "en", "level": "B", "target_span": word})
        errors = validate.validate_record(record)
        self.assertTrue(any("alignments[1]" in e and "after the previous" in e for e in errors), errors)

    def _record(self, rid):
        path = EXAMPLE.parents[1] / "PHP" / "PHP.4.1-9.json"
        for r in example_records() + json.loads(path.read_text(encoding="utf-8"))["records"]:
            if r["id"] == rid:
                return r

    def test_key_term_must_keep_its_english_word(self):
        record = self._record("JHN.1.17.s1")
        self.assertEqual(validate.validate_record(record), [])
        record["renderings"]["en"]["R"] = record["renderings"]["en"]["R"].replace("Grace", "Kindness")
        errors = validate.validate_record(record)
        self.assertTrue(any("renderings.en.R: key term 'grace'" in e for e in errors), errors)

    def test_a_decision_on_the_word_explains_an_exception(self):
        record = self._record("JHN.1.17.s1")
        record["renderings"]["en"]["R"] = record["renderings"]["en"]["R"].replace("Grace", "Kindness")
        grace = next(t for t in validate.macula_greek.load_tokens("JHN.1.17")
                     if t.strong == "5485")
        record["decisions"].append({
            "id": "r-en-9", "layer": "rendering", "language": "en", "levels": ["R"],
            "category": "word_choice", "tokens": [grace.id], "choice": "kindness",
            "alternatives": ["grace"], "reason": "Test.", "uncertain": False, "footnote": False})
        self.assertEqual(validate.validate_record(record), [])

    def test_gospel_is_good_news_at_readable_only(self):
        record = self._record("PHP.4.3.s1")
        self.assertEqual(validate.validate_record(record), [])
        record["renderings"]["en"]["B"] = record["renderings"]["en"]["B"].replace("gospel", "good news")
        self.assertTrue(any("renderings.en.B: key term 'gospel'" in e
                            for e in validate.validate_record(record)))

    def test_key_term_lemmas_are_copied_from_the_data(self):
        from owb.sources import macula_hebrew
        sources = {"grc": (validate.macula_greek.forms(), validate.macula_greek._all_tokens()),
                   "hbo": (macula_hebrew.forms(), macula_hebrew._all())}
        for (language, strong), term in validate.KEY_TERMS.items():
            forms, words = sources[language]
            self.assertIn(term["lemma"], forms, strong)
            lemmas = {t.lemma for v in words.values() for t in v if t.strong == strong}
            self.assertIn(term["lemma"], lemmas, strong)

    def test_key_terms_are_matched_by_language(self):
        # Hebrew Strong's 4100 ("what", Genesis 2:19) is not Greek 4100 ("believe").
        path = EXAMPLE.parents[1] / "GEN" / "GEN.2.4-25.json"
        self.assertEqual(validate.validate_file(path), [])
        record = next(r for r in json.loads(path.read_text(encoding="utf-8"))["records"]
                      if r["id"] == "GEN.2.5.s1")
        record["renderings"]["en"]["R"] = re.sub(r"\{\{divine_name:[^}]*\}\}", "God",
                                                 record["renderings"]["en"]["R"])
        self.assertTrue(any("key term 'the divine name (YHWH)'" in e
                            for e in validate.validate_record(record)))

    def test_plural_you_is_spanish_only(self):
        path = EXAMPLE.parents[1] / "PHP" / "PHP.4.1-9.json"
        for record in json.loads(path.read_text(encoding="utf-8"))["records"]:
            self.assertNotIn("plural_you", json.dumps(record["renderings"]["en"]))
        self.assertEqual(validate.validate_file(path), [])

    def test_plural_you_outside_spanish_fails(self):
        record = example_records()[0]
        record["renderings"]["en"]["R"] += " {{plural_you:you all|you}}"
        self.assertIn("renderings.en.R: plural_you is not a setting in this language",
                      validate.validate_record(record))

    def test_rendering_in_a_language_not_in_the_registry_fails(self):
        record = example_records()[0]
        record["renderings"]["pt"] = copy.deepcopy(record["renderings"]["en"])
        self.assertIn("renderings: 'pt' is not a language in data/languages.json",
                      validate.validate_record(record))


if __name__ == "__main__":
    unittest.main()
