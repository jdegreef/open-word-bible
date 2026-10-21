import json
import unittest
from pathlib import Path

from owb import markup, words_of_jesus

ROOT = Path(__file__).resolve().parents[1]


def quoted(text, inside=False):
    return [text[s:e] for s, e in markup.quotations(text, inside)]


class QuotationsTest(unittest.TestCase):
    def test_narration_and_quotation(self):
        self.assertEqual(quoted('Jesus answered him, "Truly, I tell you."'), ["Truly, I tell you."])
        self.assertEqual(quoted('He said, "Go," and then, "Come."'), ["Go,", "Come."])

    def test_guillemets_without_their_spaces(self):
        self.assertEqual(quoted("Jésus lui répondit : « En vérité. »"), ["En vérité."])
        self.assertEqual(quoted("Jesús le respondió: «En verdad te digo»."), ["En verdad te digo"])

    def test_a_sentence_can_begin_or_end_inside_a_quotation(self):
        self.assertEqual(quoted('of the Spirit." Then he left.'), ["of the Spirit."])
        self.assertEqual(quoted('Jesus replied, "Truly, truly.'), ["Truly, truly."])
        self.assertEqual(quoted("Whatever is born of the flesh is flesh."), [])
        self.assertEqual(quoted("Whatever is born of the flesh is flesh.", inside=True),
                         ["Whatever is born of the flesh is flesh."])

    def test_a_quotation_inside_another_belongs_to_it(self):
        text = "Do not be surprised that I told you, 'All of you must be born from above.'"
        self.assertEqual(quoted(text, inside=True), [text])
        self.assertEqual(quoted('He said, "I told you, \'Go.\'"'), ["I told you, 'Go.'"])
        # Three deep, beginning two deep: all of it before the last mark.
        text = 'your body will not be buried in the tomb of your ancestors, "he said," as I was told.\'"'
        self.assertEqual(quoted(text), [text[:-1]])
        # A quotation inside the speech, closing in a later sentence than
        # the one that opened it, leaves the speech open (Matthew 6:13).
        text = "And do not lead us into testing, but rescue us from the evil one.'"
        self.assertEqual(quoted(text, inside=True), [text])
        text = "rescue us from the evil one.' For if you forgive others,\" he said."
        self.assertEqual(quoted(text, inside=True), [text[:text.index('"')]])
        self.assertEqual(quoted("Il dit : « Ils ont dit “Va”. »"), ["Ils ont dit “Va”."])

    def test_apostrophes_are_not_quotation_marks(self):
        self.assertEqual(quoted('Jesus said, "Don\'t fear the disciples\' doubts."'),
                         ["Don't fear the disciples' doubts."])
        self.assertEqual(quoted("C’est pour cela qu’{{deity_pronoun:il|Il}} a dit : « Vous n’êtes pas tous propres. »"),
                         ["Vous n’êtes pas tous propres."])
        # Korean sets a particle right after a closing quote.
        self.assertEqual(quoted("그는 '왕좌 회랑'을 만들었다. 그곳은 '재판 회랑'이라고도 불렸다."),
                         ["왕좌 회랑", "재판 회랑"])

    def test_a_closing_quote_after_a_dash(self):
        self.assertEqual(quoted('God said, "and now, lest he live forever —"'), ["and now, lest he live forever —"])

    def test_marks_that_do_not_pair(self):
        with self.assertRaises(ValueError):
            markup.quotations('He said, "Go, "come" now.')
        with self.assertRaises(ValueError):
            markup.quotations('the {{gender:"a"|b}} one')

    def test_every_rendering_parses(self):
        # Quotation marks are in every language; they must pair everywhere,
        # so any sentence can be marked.
        for path in sorted((ROOT / "content").glob("*/*.json")):
            for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
                for lang, levels in r["renderings"].items():
                    for level, text in levels.items():
                        for inside in (False, True):
                            try:
                                markup.quotations(text, inside)
                            except ValueError as e:
                                self.fail(f"{r['id']} {lang}.{level}: {e}")


class DataTest(unittest.TestCase):
    def test_marked_records_exist_and_fit_their_renderings(self):
        paths = sorted((ROOT / "data" / "words_of_jesus").glob("*.json"))
        self.assertTrue(paths)
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "ai_draft", path.name)
            self.assertTrue(data["description"], path.name)
            records = {r["id"]: r for p in (ROOT / "content" / path.stem).glob("*.json")
                       for r in json.loads(p.read_text(encoding="utf-8"))["records"]}
            for rid, value in data["records"].items():
                self.assertEqual(rid.split(".")[0], path.stem, rid)
                self.assertIn(rid, records, rid)
                self.assertEqual(words_of_jesus.errors(records[rid], value), [], rid)

    def test_values(self):
        record = {"id": "JHN.3.3.s1", "renderings": {"en": {
            "B": 'Jesus answered him, "Truly, I tell you." They said, "How?"'}}}
        self.assertEqual(words_of_jesus.errors(record, "red"), [
            "JHN.3.3.s1: 'red' is not \"all\", \"quoted\" or a list of quotation numbers"])
        self.assertEqual(words_of_jesus.errors(record, [0]), [])
        self.assertEqual(words_of_jesus.errors(record, [2]),
                         ["JHN.3.3.s1 en.B: has 2 quotations, not quotation 2"])
        text = record["renderings"]["en"]["B"]
        self.assertEqual([text[s:e] for s, e in words_of_jesus.ranges(text, [0])], ["Truly, I tell you."])
        self.assertEqual(len(words_of_jesus.ranges(text, "quoted")), 2)
        record["renderings"]["en"]["B"] = "Jesus told them to go."
        self.assertEqual(words_of_jesus.errors(record, "quoted"),
                         ['JHN.3.3.s1 en.B: marked "quoted" but has no quotation'])


if __name__ == "__main__":
    unittest.main()
