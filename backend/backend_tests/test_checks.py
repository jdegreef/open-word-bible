"""The admin's content checks (staff/checks.py): footnotes whose verse words
the alternative, and verses and glossary rows at odds with a language's
terms glossary."""
from unittest import mock

from accounts.models import Role
from owb import content_checks as cc
from owb import notes
from translation.models import Decision, Rendering, Sentence

from .test_admin import AdminTestCase, account, client_for, sentence

K = Role.Kind

GLOSSARY = """# Indonesian terms

## Worship

| Source (English) | Indonesian | Notes |
|---|---|---|
| assembly (*qahal*) | *perhimpunan* | Not *jemaah*. |
| governor | *gubernur* | |

## Added while drafting

| Book | Source (English) | Indonesian | First verse |
|---|---|---|---|
| Haggai | governor | *bupati* | 1:1 |
"""

CHOICE = "I will hold innocent their blood: I will vindicate it"
ALTERNATIVES = ["the Greek translation: \"I will avenge their blood\""]


class ChecksTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        s = sentence("JOL.4.21.s1", ("en", "id"))
        texts = {
            ("en", "L"): "And I will hold innocent their blood", ("en", "B"): "I will avenge their blood.",
            ("en", "R"): "I will punish them.",
            ("id", "L"): "Dan Aku akan menyatakan tidak bersalah darah mereka",
            ("id", "B"): "Aku akan membalaskan darah mereka.", ("id", "R"): "Aku akan menghukum mereka.",
        }
        for (lang, level), text in texts.items():
            Rendering.objects.filter(sentence=s, language=lang, level=level).update(text=text)
        Decision.objects.create(sentence=s, key="m1", order=0, layer="meaning", category="word_sense",
                                choice=CHOICE, alternatives=ALTERNATIVES, reason="why", footnote=True)
        other = sentence("NUM.10.7.s1", ("en", "id"))
        Rendering.objects.filter(sentence=other, language="en").update(text="gather the assembly")
        Rendering.objects.filter(sentence=other, language="id").update(text="kumpulkanlah jemaah itu")
        self.sentence = s
        digest = notes.decision_digest({"choice": CHOICE, "alternatives": ALTERNATIVES, "reason": "why"})
        self.notes = {"JOL.4.21.s1": {"m1": {
            "source": digest, "choice": "Aku akan menyatakan darah mereka tidak bersalah: Aku membelanya",
            "alternatives": ["terjemahan Yunani: \"Aku akan membalaskan darah mereka\""], "reason": "x"}}}
        patches = [mock.patch("staff.checks._notes", return_value=self.notes),
                   mock.patch("staff.checks._glossary",
                              return_value=cc.glossary_rows(GLOSSARY, "Indonesian"))]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def get(self, query):
        response = self.admin.get("/api/admin/checks/" + query)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_note_mismatches(self):
        d = self.get("?lang=id")
        self.assertEqual(d["language"], "id")
        self.assertEqual(d["notes"]["total"], 1)
        self.assertEqual(d["notes"]["kinds"], {"alternative": 1})
        hit = d["notes"]["hits"][0]
        self.assertEqual((hit["record"], hit["verse"], hit["label"], hit["level"], hit["decision"]),
                         ("JOL.4.21.s1", "JOL.4.21", "Joel 4:21", "B", "m1"))
        self.assertTrue(hit["english_too"])
        # English is checked against its own decisions.
        en = self.get("?lang=en")
        self.assertEqual([(h["record"], h["level"]) for h in en["notes"]["hits"]], [("JOL.4.21.s1", "B")])
        self.assertIsNone(en["glossary"]["file"])

    def test_glossary(self):
        g = self.get("?lang=id")["glossary"]
        self.assertEqual(g["file"], "docs/indonesian-terms.md")
        self.assertEqual([(h["record"], h["kind"], h["form"], h["label"]) for h in g["verses"]["hits"]],
                         [("NUM.10.7.s1", "avoided", "jemaah", "Numbers 10:7")])
        # One hit for the verse, naming each level that uses the form.
        self.assertEqual(g["verses"]["hits"][0]["levels"], ["L", "B", "R"])
        self.assertEqual([(c["term"], c["kind"]) for c in g["rows"]], [("governor", "different_forms")])

    def test_languages_and_validation(self):
        d = self.get("?lang=id")
        langs = {entry["code"]: entry for entry in d["languages"]}
        self.assertTrue(langs["id"]["glossary"])
        self.assertFalse(langs["en"]["glossary"])
        self.assertEqual(self.admin.get("/api/admin/checks/?lang=xx").status_code, 400)

    def test_any_team_member_may_look(self):
        editor = client_for(account("editor@example.org", (K.EDITOR,)))
        self.assertEqual(editor.get("/api/admin/checks/?lang=id").status_code, 200)

    def test_cached_until_a_sentence_changes(self):
        self.get("?lang=id")
        with mock.patch("staff.checks.measure", side_effect=AssertionError("measured again")):
            self.get("?lang=id")
        Sentence.objects.get(id=self.sentence.id).save()
        empty = {"notes": {"total": 0, "kinds": {}, "hits": []},
                 "glossary": {"file": None, "verses": {"total": 0, "kinds": {}, "hits": []}, "rows": []}}
        with mock.patch("staff.checks.measure", return_value=empty) as measure:
            self.assertEqual(self.get("?lang=id")["notes"]["total"], 0)
        measure.assert_called_once_with("id")
