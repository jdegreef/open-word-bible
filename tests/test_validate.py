import copy
import json
import unittest
from pathlib import Path

from owb import validate

EXAMPLE = Path(__file__).resolve().parents[1] / "content" / "en" / "JHN" / "JHN.1.1-2.json"


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


if __name__ == "__main__":
    unittest.main()
