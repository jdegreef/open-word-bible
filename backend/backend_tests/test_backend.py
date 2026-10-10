"""Backend tests. They need a Postgres database (DATABASE_URL) but not the
large source clones: source words come from the committed extracts in
data/grc/."""
import io
import json
import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import TestCase

from texts.models import Edition, Verse, Word
from translation.models import ReviewEvent, Sentence

CONTENT = settings.REPO_ROOT / "content"


def load_extract_words():
    """Create the SBLGNT edition and the words for every chapter in content/."""
    edition = Edition.objects.create(code="sblgnt", name="SBL Greek New Testament", language="grc",
                                     kind="original", licence="CC BY 4.0", source="sblgnt",
                                     source_commit="test")
    seq = 0
    for path in sorted((settings.REPO_ROOT / "data" / "grc").glob("*.json")):
        for vid, words in json.loads(path.read_text(encoding="utf-8"))["verses"].items():
            book, chapter, verse = vid.split(".")
            for w in words:
                Word.objects.create(edition=edition, book=book, chapter=int(chapter), verse=int(verse),
                                    seq=seq, lang="grc", **w)
                seq += 1
    return edition


def import_content(*paths):
    call_command("import_content", *paths, stdout=io.StringIO(), stderr=io.StringIO())


class ImportContentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_extract_words()

    def test_imports_every_record(self):
        import_content()
        files = sorted(CONTENT.glob("*/*.json"))
        expected = sum(len(json.loads(p.read_text())["records"]) for p in files)
        self.assertEqual(Sentence.objects.count(), expected)
        s = Sentence.objects.get(record_id="JHN.1.12.s1")
        self.assertEqual(s.refs, ["JHN.1.12", "JHN.1.13"])
        self.assertEqual(s.renderings.count(), 6)
        self.assertTrue(s.decisions.filter(layer="meaning").exists())

    def test_reimport_never_resets_review_status(self):
        import_content()
        s = Sentence.objects.get(record_id="JHN.1.1.s1")
        s.status = "reviewed"
        s.save()
        import_content()
        s.refresh_from_db()
        self.assertEqual(s.status, "reviewed")

    def test_file_with_an_unknown_word_is_not_imported(self):
        data = json.loads((CONTENT / "JHN" / "JHN.1.1-18.json").read_text())
        data["records"][0]["decisions"][0]["tokens"] = ["n43001001099"]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(data, f)
        with self.assertRaises(CommandError):
            import_content(f.name)
        Path(f.name).unlink()
        self.assertEqual(Sentence.objects.count(), 0)


class ApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        edition = load_extract_words()
        import_content()
        bsb = Edition.objects.create(code="bsb", name="Berean Standard Bible", language="eng",
                                     kind="reference", licence="Public domain", source="open-bibles",
                                     source_commit="test")
        Verse.objects.create(edition=bsb, book="JHN", chapter=1, verse=1,
                             text="In the beginning was the Word")
        Verse.objects.create(edition=edition, book="JHN", chapter=1, verse=1, text="Ἐν ἀρχῇ")

    def test_passages_round_trip_the_content_files(self):
        response = self.client.get("/api/passages/jhn/1/")
        self.assertEqual(response.status_code, 200)
        from_file = json.loads((CONTENT / "JHN" / "JHN.1.1-18.json").read_text())["records"]
        self.assertEqual(response.json()["records"], from_file)
        self.assertIn("JHN.1.1", response.json()["words"])

    def test_chapter_text_by_edition(self):
        response = self.client.get("/api/text/JHN/1/?editions=bsb,sblgnt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["verses"][0]["text"],
                         {"bsb": "In the beginning was the Word", "sblgnt": "Ἐν ἀρχῇ"})

    def test_unknown_book_and_edition(self):
        self.assertEqual(self.client.get("/api/passages/XYZ/1/").status_code, 404)
        self.assertEqual(self.client.get("/api/text/JHN/1/?editions=nope").status_code, 400)

    def test_editions_and_health(self):
        self.assertEqual({e["code"] for e in self.client.get("/api/editions/").json()}, {"sblgnt", "bsb"})
        self.assertEqual(self.client.get("/healthz").json(), {"ok": True})


class AdminTest(TestCase):
    def test_review_event_records_the_reviewer(self):
        load_extract_words()
        import_content()
        user = get_user_model().objects.create_superuser("reviewer", "r@example.com", "pw-not-used-elsewhere")
        self.client.force_login(user)
        s = Sentence.objects.get(record_id="PHP.4.5.s2")
        page = self.client.get(f"/admin/translation/sentence/{s.pk}/change/")
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "PHP.4.5.s2")
        ReviewEvent.objects.create(sentence=s, user=user, action="comment", note="test")
        self.assertEqual(s.review_events.get().user, user)
