"""owb/content_checks.py: footnotes whose verse words the alternative, and
verses and glossary rows at odds with a terms glossary."""
import unittest

from owb import content_checks as cc
from owb import notes

STOP = frozenset({"i", "will", "their", "the", "and", "aku", "akan", "mereka", "dan", "di"})


def record(rid, renderings, decisions):
    return {"id": rid, "refs": [rid.rsplit(".", 1)[0]], "renderings": renderings, "decisions": decisions}


def decision(choice, alternatives, category="word_sense", did="m1"):
    return {"id": did, "layer": "meaning", "category": category, "footnote": True, "choice": choice,
            "alternatives": alternatives, "reason": "why"}


def note(d, choice, alternatives):
    return {"source": notes.decision_digest(d), "choice": choice, "alternatives": alternatives, "reason": "x"}


JOEL = decision("I will hold innocent their blood: I will vindicate it",
                ["the Greek translation: \"I will avenge their blood\""])
JOEL_ID = note(JOEL, "Aku akan menyatakan darah mereka tidak bersalah: Aku akan membelanya",
               ["terjemahan Yunani: \"Aku akan membalaskan darah mereka\""])
CROCUS = decision("crocus: a wild flower", ["rose", "narcissus"])
CROCUS_ID = note(CROCUS, "bunga kunyit: bunga liar", ["mawar", "narsis"])


def joel(id_b="Aku akan membalaskan darah mereka, yang belum Kubalaskan.",
         en_b="I will avenge their blood, which I had left unavenged."):
    return record("JOL.4.21.s1", {
        "en": {"L": "And I will hold innocent their blood", "B": en_b, "R": "I will punish them"},
        "id": {"L": "Dan {{deity_pronoun:aku|Aku}} akan menyatakan tidak bersalah darah mereka",
               "B": id_b, "R": "Aku akan menghukum mereka"},
    }, [JOEL])


def crocus(id_text="Padang gurun akan berbunga seperti bunga bakung."):
    return record("ISA.35.1.s1", {
        "en": {lv: "The desert will blossom like the crocus." for lv in "LBR"},
        "id": {lv: id_text for lv in "LBR"},
    }, [CROCUS])


class NoteMismatchTest(unittest.TestCase):
    def run_id(self, records, translated):
        return cc.note_mismatches(records, "id", translated, stop=STOP, en_stop=STOP)

    def test_a_verse_wording_the_alternative(self):
        hits = self.run_id([joel()], {"JOL.4.21.s1": {"m1": JOEL_ID}})
        self.assertEqual([(h["level"], h["kind"], h["words"]) for h in hits], [("B", "alternative", ["membalaskan"])])
        hit = hits[0]
        self.assertEqual((hit["verse"], hit["decision"], hit["alternative"]),
                         ("JOL.4.21", "m1", JOEL_ID["alternatives"][0]))
        # The English Balanced says "avenge" too: the mismatch began there,
        # and the contrast is the Literal, which words the choice.
        self.assertTrue(hit["english_too"])
        self.assertEqual(hit["contrast"], "level")

    def test_english_has_its_own_list(self):
        hits = cc.note_mismatches([joel()], "en", stop=STOP)
        self.assertEqual([(h["level"], h["kind"]) for h in hits], [("B", "alternative")])

    def test_a_verse_wording_the_choice_is_fine(self):
        good = joel(id_b="Aku akan menyatakan darah mereka tidak bersalah.",
                    en_b="I will hold innocent their blood.")
        self.assertEqual(self.run_id([good], {"JOL.4.21.s1": {"m1": JOEL_ID}}), [])

    def test_stale_missing_and_form_decisions_are_skipped(self):
        stale = dict(JOEL_ID, source="000000000000")
        self.assertEqual(self.run_id([joel()], {"JOL.4.21.s1": {"m1": stale}}), [])
        self.assertEqual(self.run_id([joel()], {}), [])
        variant = joel()
        variant["decisions"] = [dict(JOEL, category="text_variant")]
        self.assertEqual(self.run_id([variant], {"JOL.4.21.s1": {"m1": JOEL_ID}}), [])

    def test_a_choice_the_verse_does_not_word(self):
        hits = self.run_id([crocus()], {"ISA.35.1.s1": {"m1": CROCUS_ID}})
        # "bunga" is in the verse, but the rarer "kunyit" is not, at any
        # level where the English says "crocus".
        self.assertEqual([(h["kind"], h["levels"], h["words"]) for h in hits],
                         [("choice_missing", ["L", "B", "R"], ["kunyit"])])
        fine = crocus("Padang gurun akan berbunga seperti bunga kunyit.")
        self.assertEqual(self.run_id([fine], {"ISA.35.1.s1": {"m1": CROCUS_ID}}), [])

    def test_key_phrases(self):
        self.assertEqual(cc.key_phrase("crocus (a flower): a wild flower"), "crocus")
        self.assertEqual(cc.key_phrase("殺す：人を不法に殺すこと"), "殺す")
        self.assertEqual(cc.alt_phrase("the Greek translation: \"I will avenge\""), "i will avenge")
        self.assertEqual(cc.alt_phrase("shields (the ancient Greek translation)"), "shields")

    def test_words(self):
        self.assertEqual(cc.words("बिना कुछ संदेह किए"), ["बिना", "कुछ", "संदेह", "किए"])
        self.assertEqual(cc.words("わたしは罪なしとする"), ["罪"])
        # Accents stay: they tell Vietnamese words apart.
        self.assertNotEqual(cc.flatten("lạ lùng"), cc.flatten("la lung"))
        self.assertEqual(cc.flatten("{{divine_name:TUHAN|Yahweh}} \\q diam"), "tuhan diam")
        self.assertTrue(cc._matches("membalaskan", "akan membalaskannya"))
        self.assertTrue(cc._matches("kubalaskan", "telah dibalaskan"))
        self.assertFalse(cc._matches("membalaskan", "yang belum kulakukan"))


GLOSSARY = """# Indonesian terms

## 3. Worship

| Source (English) | Indonesian | Notes |
|---|---|---|
| congregation (*edah*); assembly (*qahal*) | *umat*; *perhimpunan* | Not *jemaah*. |
| bronze | *tembaga* (alternative *perunggu*) | |
| governor | *gubernur* | |
| governor (*hegemon*) | *wali negeri* | |

## 8. People

| English | Indonesian | English | Indonesian |
|---|---|---|---|
| Lot | Lot | the satan (Job 1) | Iblis (L, B); *si Penuduh* (R) |

## 13. Added while drafting

| Book | Source (English) | Indonesian | First verse |
|---|---|---|---|
| Joshua | assembly (*qahal*) | *jemaah* (L, B); *perkumpulan* (R) | 8:35 |
| Haggai | governor (*pechah*) | *bupati* | 1:1 |
| Haggai | governors | *bupati* | 1:1 |
| Numbers | lot | *undian* | 26:55 |
| 1 Chronicles | Satan (no article) | Satan | 21:1 |
"""


class GlossaryTest(unittest.TestCase):
    def setUp(self):
        self.rows = cc.glossary_rows(GLOSSARY, "Indonesian")

    def test_rows(self):
        by = {(r["line"], r["source"]): r for r in self.rows}
        assembly = by[(7, "assembly (*qahal*)")]
        self.assertEqual((assembly["english"], assembly["sources"], assembly["forms"], assembly["avoided"]),
                         (["assembly"], ["qahal"], [("perhimpunan", None)], ["jemaah"]))
        bronze = next(r for r in self.rows if r["english"] == ["bronze"])
        self.assertEqual((bronze["forms"], bronze["alternatives"]), ([("tembaga", None)], ["perunggu"]))
        # The people table has two pairs a line.
        self.assertIn("satan", [t for r in self.rows for t in r["english"]])
        joshua = next(r for r in self.rows if r["book"] == "JOS")
        self.assertEqual(joshua["forms"], [("jemaah", ["L", "B"]), ("perkumpulan", ["R"])])

    def test_conflicts(self):
        found = {c["term"]: c for c in cc.glossary_conflicts(self.rows)}
        self.assertEqual(found["assembly"]["kind"], "ruled_out")
        self.assertEqual(found["assembly"]["forms"], ["jemaah"])
        # gubernur, wali negeri and bupati; the hegemon and pechah rows name
        # different source words, so those two are not compared, but each
        # is against the rows that name none.
        governor = found["governor"]
        self.assertEqual(governor["kind"], "different_forms")
        self.assertEqual([r["forms"] for r in governor["rows"]],
                         ["*gubernur*", "*wali negeri*", "*bupati*", "*bupati*"])
        self.assertIn("satan", found)
        # Lot the man and the lot cast are told apart.
        self.assertNotIn("lot", found)

    def test_verses(self):
        recs = [
            record("NUM.10.7.s1", {"en": {"L": "you shall gather the assembly"},
                                   "id": {"L": "kamu harus mengumpulkan jemaah itu"}}, []),
            record("JOS.8.35.s1", {"en": {"L": "before all the assembly of Israel"},
                                   "id": {"L": "di depan seluruh jemaah Israel"}}, []),
            # No assembly in the English: the word may mean something else.
            record("ACT.2.47.s1", {"en": {"L": "the church"}, "id": {"L": "jemaah"}}, []),
            record("EXO.27.2.s1", {"en": {"B": "overlay it with bronze"},
                                   "id": {"B": "lapisilah dengan perunggu"}}, []),
            record("EXO.27.3.s1", {"en": {"B": "bronze and more bronze"},
                                   "id": {"B": "tembaga, atau perunggu"}}, []),
        ]
        hits = cc.glossary_hits(self.rows, recs, "id")
        got = [(h["record"], h["kind"], h["form"], h["term"], h["allowed_by"]) for h in hits]
        self.assertEqual(got, [("NUM.10.7.s1", "avoided", "jemaah", "assembly", None),
                               ("JOS.8.35.s1", "avoided", "jemaah", "assembly", 22),
                               ("EXO.27.2.s1", "alternative", "perunggu", "bronze", None)])


if __name__ == "__main__":
    unittest.main()
