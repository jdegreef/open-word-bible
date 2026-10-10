import copy
import json
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
        self.assertEqual(validate.validate_record(record), [])

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

    def test_plural_you_is_spanish_only(self):
        path = EXAMPLE.parents[1] / "PHP" / "PHP.4.1-9.json"
        for record in json.loads(path.read_text(encoding="utf-8"))["records"]:
            self.assertNotIn("plural_you", json.dumps(record["renderings"]["en"]))
        self.assertEqual(validate.validate_file(path), [])


if __name__ == "__main__":
    unittest.main()
