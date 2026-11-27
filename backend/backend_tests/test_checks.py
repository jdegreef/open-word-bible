"""The admin's content checks (staff/checks.py): footnotes whose verse words
the alternative, and verses and glossary rows at odds with a language's
terms glossary."""
import io
import os
import tempfile
import time
from pathlib import Path
from unittest import mock

from django.core.cache import cache
from django.core.management import CommandError, call_command

from accounts.models import Role
from owb import content_checks as cc
from owb import notes
from staff import checks
from staff.models import ChecksAnswer
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


class ChecksBase(AdminTestCase):
    """Two sentences in English and Indonesian, a footnoted decision, its
    translated note and an Indonesian glossary."""

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


class ChecksTest(ChecksBase):
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

    def test_a_hit_found_fine_stays_away_until_its_text_changes(self):
        hit = self.get("?lang=id")["notes"]["hits"][0]
        r = self.admin.post("/api/admin/checks/dismiss/", {"lang": "id", "signature": hit["signature"]}, format="json")
        self.assertEqual(r.status_code, 201)
        d = self.get("?lang=id")
        self.assertEqual((d["notes"]["total"], d["dismissed"]), (0, 1))
        # The verse changes: the hit (if still found) has a new signature and shows again.
        from staff.checks import signature
        self.assertNotEqual(signature({**hit, "text": hit["text"] + " baru"}), hit["signature"])
        bad = self.admin.post("/api/admin/checks/dismiss/", {"lang": "id", "signature": "0" * 64}, format="json")
        self.assertEqual(bad.json()["code"], "not_found")

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

    def test_files_stamp_follows_content_not_file_times(self):
        # The import job keeps the answer under the key its own checkout
        # gives; the API's checkout has other file times but the same files.
        with tempfile.TemporaryDirectory() as tmp, mock.patch("owb.notes.NOTES", Path(tmp)):
            folder = Path(tmp) / "id"
            folder.mkdir()
            path = folder / "JOL.json"
            path.write_text('{"a": 1}')
            before = checks._files_stamp("id")
            os.utime(path, ns=(1, 1))
            self.assertEqual(checks._files_stamp("id"), before)
            path.write_text('{"a": 22}')
            os.utime(path, ns=(1, 1))
            self.assertNotEqual(checks._files_stamp("id"), before)


EMPTY = {"notes": {"total": 0, "kinds": {}, "hits": []},
         "glossary": {"file": None, "verses": {"total": 0, "kinds": {}, "hits": []}, "rows": []}}


class KeptAnswerTest(ChecksBase):
    """The answer kept in the database (precompute_checks, or a request that
    measured), which outlives the cache being emptied."""

    def test_a_request_keeps_its_answer_in_the_database(self):
        cache.clear()
        d = self.get("?lang=id")
        row = ChecksAnswer.objects.get(language="id")
        self.assertEqual(row.stamp, checks.content_stamp("id"))
        self.assertEqual(row.answer["notes"]["total"], d["notes"]["total"])

    def test_reads_the_kept_answer_when_the_cache_is_empty(self):
        checks.precompute("id")
        cache.clear()
        with mock.patch("staff.checks.measure", side_effect=AssertionError("measured again")):
            d = self.get("?lang=id")
        self.assertEqual(d["notes"]["total"], 1)
        self.assertEqual(d["language"], "id")
        # And puts it back in the cache.
        self.assertIsNotNone(cache.get(f"staff.checks.id.{checks.content_stamp('id')}"))

    def test_measures_again_once_the_content_has_changed(self):
        checks.precompute("id")
        cache.clear()
        Sentence.objects.get(id=self.sentence.id).save()
        with mock.patch("staff.checks.measure", return_value=EMPTY) as measure:
            self.assertEqual(self.get("?lang=id")["notes"]["total"], 0)
        measure.assert_called_once_with("id")
        row = ChecksAnswer.objects.get(language="id")
        self.assertEqual((row.stamp, row.answer), (checks.content_stamp("id"), EMPTY))
        self.assertEqual(ChecksAnswer.objects.filter(language="id").count(), 1)


class PrecomputeChecksTest(ChecksBase):
    def run_command(self, *args, **options):
        out = io.StringIO()
        call_command("precompute_checks", *args, stdout=out, **options)
        return out.getvalue()

    def test_measures_every_reading_language_then_only_what_changed(self):
        out = self.run_command()
        n = len(checks.languages.READING)
        self.assertIn(f"Content checks: {n} measured, 0 already current", out)
        self.assertEqual(set(ChecksAnswer.objects.values_list("language", flat=True)),
                         set(checks.languages.READING))
        self.assertEqual(ChecksAnswer.objects.get(language="id").answer["notes"]["total"], 1)
        with mock.patch("staff.checks.measure", side_effect=AssertionError("measured again")):
            self.assertIn(f"0 measured, {n} already current", self.run_command())
        # A sentence changed: every language is measured again.
        Sentence.objects.get(id=self.sentence.id).save()
        with mock.patch("staff.checks.measure", return_value=EMPTY) as measure:
            self.assertIn(f"{n} measured, 0 already current", self.run_command())
        self.assertEqual(measure.call_count, n)
        self.assertEqual(ChecksAnswer.objects.count(), n)

    def test_languages_force_and_the_deadline(self):
        self.run_command(lang=["id", "en"])
        self.assertEqual(set(ChecksAnswer.objects.values_list("language", flat=True)), {"id", "en"})
        with mock.patch("staff.checks.measure", return_value=EMPTY) as measure:
            self.assertIn("1 measured", self.run_command(lang=["id"], force=True))
        measure.assert_called_once_with("id")
        out = self.run_command(deadline=time.time() - 1)
        self.assertIn("Stopped at the deadline before en", out)
        with self.assertRaises(CommandError):
            self.run_command(lang=["xx"])

    def test_a_failing_language_does_not_stop_the_rest(self):
        def measure(lang):
            if lang == "es":
                raise RuntimeError("broken")
            return EMPTY
        with mock.patch("staff.checks.measure", side_effect=measure):
            out = self.run_command(lang=["es", "id"])
        self.assertIn("FAIL es: RuntimeError: broken", out)
        self.assertIn("1 measured, 0 already current, 1 failed", out)
        self.assertEqual(list(ChecksAnswer.objects.values_list("language", flat=True)), ["id"])
