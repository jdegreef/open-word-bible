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

    def test_japanese_corner_brackets(self):
        self.assertEqual(quoted("イエスは答えられた。「はっきり言っておく。」"), ["はっきり言っておく。"])
        self.assertEqual(quoted("「行け」と言い、また「来い」と言った。"), ["行け", "来い"])
        # 『』 inside 「」 belongs to it, and 「」 again inside that.
        text = "彼は言った。「わたしは『主よ、「来てください」と言え』と言った。」"
        self.assertEqual(quoted(text), [text[text.index("「") + 1:-1]])
        self.assertEqual([text[s:e] for s, e in markup.quotations(text, inner=True)],
                         ["主よ、「来てください」と言え"])
        # A sentence that begins inside a speech an earlier one opened.
        self.assertEqual(quoted("世を救うためである。」 そして去った。", inside=True), ["世を救うためである。"])
        self.assertEqual(quoted("霊から生まれる者は霊である。", inside=True), ["霊から生まれる者は霊である。"])

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
        # Two deep: the son's words inside the father's, inside the parable,
        # where the son quotes in turn (Luke 15:18).
        text = 'I will tell him, "Father, I have sinned."'
        self.assertEqual(quoted(text, inside=True), [text])
        self.assertEqual(quoted(text), ["Father, I have sinned."])
        self.assertEqual(quoted("Il dit : « Ils ont dit “Va”. »"), ["Ils ont dit “Va”."])

    def test_quotations_inside_someone_elses(self):
        # Paul retelling the Damascus road: Jesus's words are inside his.
        text = "I heard a voice say to me, 'Saul, Saul, why do you persecute me?'"
        self.assertEqual([text[s:e] for s, e in markup.quotations(text, inner=True)],
                         ["Saul, Saul, why do you persecute me?"])
        text = "But rise, stand up on your feet.'"
        self.assertEqual([text[s:e] for s, e in markup.quotations(text, inside=True, inner=True)],
                         ["But rise, stand up on your feet."])
        text = "Pablo dijo: «Él dijo: “Ve”»."
        self.assertEqual([text[s:e] for s, e in markup.quotations(text, inner=True)], ["Ve"])

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
            "JHN.3.3.s1: 'red' is not \"all\", \"quoted\", a list of quotation numbers "
            "or {\"inner\": \"all\" or \"quoted\"}"])
        self.assertEqual(words_of_jesus.errors(record, [0]), [])
        self.assertEqual(words_of_jesus.errors(record, [2]),
                         ["JHN.3.3.s1 en.B: has 2 quotations, not quotation 2"])
        text = record["renderings"]["en"]["B"]
        self.assertEqual([text[s:e] for s, e in words_of_jesus.ranges(text, [0])], ["Truly, I tell you."])
        self.assertEqual(len(words_of_jesus.ranges(text, "quoted")), 2)
        record["renderings"]["en"]["B"] = "Jesus told them to go."
        self.assertEqual(words_of_jesus.errors(record, "quoted"),
                         ['JHN.3.3.s1 en.B: marked "quoted" but has no quotation'])


class ParityTest(unittest.TestCase):
    """Every language marks the same words (scripts/check_words_of_jesus.py)."""

    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import check_words_of_jesus
        cls.check = check_words_of_jesus

    def test_languages_mark_the_same_words(self):
        pending = self.check.pending()
        new = [m for m in self.check.mismatches() if (m[1], m[3], m[2]) not in pending]
        self.assertEqual(new, [], "fix the quotation marks or list the fix in "
                                  "docs/review-notes/pending-quote-fixes.jsonl")

    def test_pending_fixes_are_current_and_would_fix(self):
        # A pending fix names today's text; once it is made, its entry goes.
        lines = self.check.PENDING.read_text(encoding="utf-8").splitlines()
        marked = words_of_jesus.marked()
        for line in filter(None, lines):
            e = json.loads(line)
            for key in ("record", "language", "level", "old", "new", "reason"):
                self.assertTrue(e.get(key), (line[:60], key))
            records = self.check.records(e["record"].split(".")[0])
            self.assertEqual(records[e["record"]]["renderings"][e["language"]][e["level"]], e["old"],
                             f"{e['record']} {e['language']}.{e['level']} has changed: remove or update its entry")
            value = marked[e["record"]]
            self.assertLess(sum(b - a for a, b in words_of_jesus.ranges(e["new"], value)),
                            sum(b - a for a, b in words_of_jesus.ranges(e["old"], value)), e["record"])

    def test_a_language_with_a_stray_quotation_is_found(self):
        en = 'Then he told him, "Go and wash in the pool of Siloam" (the name means Sent).'
        odd = "Then he told him, \"Go and wash in the pool of Siloam.\" (Siloam means 'Sent'.)"
        record = {"id": "JHN.9.6.s1", "renderings": {"en": {"B": en}, "es": {"B": en}, "fr": {"B": en},
                                                      "ko": {"B": odd}}}
        ranges = {lang: words_of_jesus.ranges(r["B"], "quoted") for lang, r in record["renderings"].items()}
        self.assertEqual(len(ranges["ko"]), 2)
        self.assertEqual(len(ranges["en"]), 1)
        self.assertEqual(len(words_of_jesus.ranges(odd, [0])), 1)


if __name__ == "__main__":
    unittest.main()
