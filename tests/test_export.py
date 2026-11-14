"""owb/export.py: the translation as USFM or JSON files."""
import io
import json
import unittest
import zipfile

from owb import export


def rec(verse_ids, en, status="ai_draft", **langs):
    renderings = {"en": {"B": en, "L": "literal " + en}}
    for lang, text in langs.items():
        renderings[lang] = {"B": text}
    return {"refs": verse_ids, "renderings": renderings, "status": status}


RECORDS = [
    rec(["JHN.1.12", "JHN.1.13"], "to {{gender:all people|men}} who \\v 13 were born of God",
        sw="kwa wote \\v 13 waliozaliwa"),
    rec(["PHP.4.5"], "Let your gentleness be known."),
    rec(["PHP.4.5"], "The Lord is near.", status="reviewed"),
    rec(["PSA.3.1"], "A psalm of David."),
    rec(["PSA.3.2"], "LORD, how many \\q are my foes!"),
    rec(["PSA.13.6"], "But I trust in your love; I will sing to the LORD."),
    rec(["ISA.63.19"], "Oh, that you would tear open the heavens."),
]


def unzip(body):
    z = zipfile.ZipFile(io.BytesIO(body))
    return {name: z.read(name).decode() for name in z.namelist()}


class VerseTextTest(unittest.TestCase):
    def test_splits_joins_and_flattens(self):
        verses = export.verse_texts(RECORDS, "en", "B", {"gender": 1})
        self.assertEqual(verses["JHN.1.12"], "to men who")
        self.assertEqual(verses["JHN.1.13"], "were born of God")
        self.assertEqual(verses["PHP.4.5"], "Let your gentleness be known. The Lord is near.")
        self.assertEqual(verses["PSA.3.2"], "LORD, how many are my foes!")
        self.assertEqual(list(verses)[0], "PSA.3.1", "Bible order")

    def test_a_language_without_the_level_has_nothing(self):
        self.assertEqual(export.verse_texts(RECORDS, "sw", "L"), {})
        self.assertEqual(list(export.verse_texts(RECORDS, "sw", "B")), ["JHN.1.12", "JHN.1.13"])


class NumberingTest(unittest.TestCase):
    def test_english_numbering(self):
        entries, titles = export.numbered(export.verse_texts(RECORDS, "en", "B"))
        by_id = {f"{e['book']}.{e['chapter']}.{e['verse']}": e for e in entries}
        self.assertEqual(titles, {("PSA", 3): "A psalm of David."})
        self.assertEqual(by_id["PSA.3.1"]["text"], "LORD, how many are my foes!")
        self.assertEqual(by_id["PSA.13.5"]["to"], 6)
        self.assertEqual(by_id["ISA.63.19"]["holds"], ["ISA.63.19", "ISA.64.1"])
        self.assertNotIn("to", by_id["ISA.63.19"])

    def test_source_numbering_keeps_ours(self):
        entries, titles = export.numbered(export.verse_texts(RECORDS, "en", "B"), "source")
        self.assertEqual(titles, {})
        self.assertIn(("PSA", 3, 1, "A psalm of David."),
                      [(e["book"], e["chapter"], e["verse"], e["text"]) for e in entries])
        self.assertFalse(any("to" in e or "holds" in e for e in entries))


class BuildTest(unittest.TestCase):
    def test_usfm_zip(self):
        name, content_type, body, manifest = export.build(RECORDS, "en", "B", settings={"deity_pronoun": 1})
        self.assertEqual((name, content_type), ("owb-en-b-usfm.zip", "application/zip"))
        files = unzip(body)
        self.assertEqual(sorted(files), ["19-PSA.usfm", "23-ISA.usfm", "43-JHN.usfm", "50-PHP.usfm", "manifest.json"])
        psalms = files["19-PSA.usfm"]
        self.assertTrue(psalms.startswith("\\id PSA Open Word Bible, English, Balanced (OWB-B)\n"))
        self.assertIn("\\c 3\n\\d A psalm of David.\n\\p\n\\v 1 LORD, how many are my foes!\n", psalms)
        self.assertIn("\\v 5-6 But I trust", psalms)
        self.assertEqual(json.loads(files["manifest.json"]), manifest)
        self.assertEqual(manifest["settings"]["deity_pronoun"], "He")
        self.assertEqual(manifest["status"], {"ai_draft": 6, "reviewed": 1})
        self.assertEqual(manifest["licence_url"], "https://creativecommons.org/publicdomain/zero/1.0/")
        self.assertNotIn("missing", manifest)

    def test_paragraphs(self):
        records = [rec(["JHN.3.1"], "There was a man."), rec(["JHN.3.2"], "He came by night."),
                   rec(["JHN.3.3"], "Jesus answered."), rec(["PSA.3.2"], "LORD, how many \\q are my foes!")]
        opens = frozenset({"JHN.3.1", "JHN.3.3", "PSA.3.2"})
        john = unzip(export.build(records, "en", "B", paragraphs=opens)[2])["43-JHN.usfm"]
        # A chapter opens a paragraph anyway; a start later in it is a \p before its verse.
        self.assertIn("\\c 3\n\\p\n\\v 1 There was a man.\n\\v 2 He came by night.\n\\p\n\\v 3 Jesus", john)
        books = json.loads(export.build(records, "en", "B", "json", paragraphs=opens)[2])["books"]
        verses = books[1]["chapters"][0]["verses"]
        self.assertEqual([v.get("paragraph", False) for v in verses], [True, False, True])
        # Numbered as English, the start moves with its verse (our PSA.3.2 is Psalm 3:1).
        psalm = json.loads(export.build(records, "en", "B", "json", paragraphs=opens)[2])["books"][0]
        self.assertEqual(psalm["chapters"][0]["verses"][0],
                         {"verse": 1, "paragraph": True, "text": "LORD, how many are my foes!"})
        # Without paragraphs nothing changes.
        self.assertNotIn("\\p\n\\v 3", unzip(export.build(records, "en", "B")[2])["43-JHN.usfm"])

    def test_words_of_jesus(self):
        records = [
            {"id": "JHN.11.43.s1", "refs": ["JHN.11.43"], "status": "ai_draft",
             "renderings": {"en": {"B": 'He cried out, "Lazarus, come out!"'}}},
            # A speech that runs on into the next verse is closed and reopened there.
            {"id": "JHN.3.15.s1", "refs": ["JHN.3.15", "JHN.3.16"], "status": "ai_draft",
             "renderings": {"en": {"B": "so that all may live. \\v 16 "
                                        "For God {{gender:loved all people|loved men}}."}}},
            {"id": "JHN.11.35.s1", "refs": ["JHN.11.35"], "status": "ai_draft",
             "renderings": {"en": {"B": "Jesus wept."}}},
        ]
        wj = {"JHN.11.43.s1": "quoted", "JHN.3.15.s1": "all"}
        john = unzip(export.build(records, "en", "B", words_of_jesus=wj)[2])["43-JHN.usfm"]
        self.assertIn('\\v 43 He cried out, "\\wj Lazarus, come out!\\wj*"', john)
        self.assertIn("\\v 15 \\wj so that all may live.\\wj*\n\\v 16 \\wj For God loved all people.\\wj*", john)
        self.assertIn("\\v 35 Jesus wept.\n", john)
        verses = json.loads(export.build(records, "en", "B", "json", words_of_jesus=wj)[2])["books"][0]["chapters"]
        lazarus = verses[1]["verses"][1]
        self.assertEqual(lazarus["text"][slice(*lazarus["wj"][0])], "Lazarus, come out!")
        self.assertNotIn("wj", verses[1]["verses"][0])
        # Without the markings, the text is the same and nothing is marked.
        self.assertNotIn("\\wj", unzip(export.build(records, "en", "B")[2])["43-JHN.usfm"])
        # The site's loader finds the ranges before it curls the quotes, and the
        # record carries them: those are used, not found again in curled text.
        curled = {"id": "JHN.11.43.s1", "refs": ["JHN.11.43"], "status": "ai_draft",
                  "renderings": {"en": {"B": "He cried out, \u201cLazarus, come out!\u201d"}},
                  "wj": {"en": {"B": [[15, 33]]}}}
        john = unzip(export.build([curled], "en", "B", words_of_jesus=wj)[2])["43-JHN.usfm"]
        self.assertIn("\\v 43 He cried out, \u201c\\wj Lazarus, come out!\\wj*\u201d", john)

    def test_same_text_same_bytes(self):
        self.assertEqual(export.build(RECORDS, "en", "B")[2], export.build(RECORDS, "en", "B")[2])

    def test_json(self):
        name, content_type, body, manifest = export.build(RECORDS, "en", "B", "json", books=["PSA"],
                                                          expected=["PSA.3.1", "PSA.3.2", "PSA.3.3", "JHN.1.1"])
        self.assertEqual(name, "owb-en-b.json")
        data = json.loads(body)
        self.assertEqual([b["code"] for b in data["books"]], ["PSA"])
        psalm3 = data["books"][0]["chapters"][0]
        self.assertEqual(psalm3["title"], "A psalm of David.")
        self.assertEqual(psalm3["verses"][0], {"verse": 1, "text": "LORD, how many are my foes!"})
        self.assertEqual(data["books"][0]["chapters"][1]["verses"][0]["to"], 6)
        self.assertEqual(manifest["missing"], {"count": 1, "by_book": {"PSA": 1}, "verses": ["PSA.3.3"]})

    def test_language_and_book_names(self):
        files = unzip(export.build(RECORDS, "sw", "B", numbering="source")[2])
        self.assertEqual(list(files), ["manifest.json", "43-JHN.usfm"])
        self.assertIn("\\h Yohana\n", files["43-JHN.usfm"])
        self.assertIn("\\v 13 waliozaliwa\n", files["43-JHN.usfm"])

    def test_bad_choices(self):
        for args in (("xx", "B"), ("en", "X"), ("en", "B", "pdf"), ("en", "B", "usfm", "kjv")):
            with self.assertRaises(ValueError):
                export.build(RECORDS, *args)


if __name__ == "__main__":
    unittest.main()
