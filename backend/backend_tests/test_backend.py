"""Backend tests. They need a Postgres database (DATABASE_URL) but not the
large source clones: source words come from the committed extracts in
data/grc/ and data/hbo/."""
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


def load_extract_words(languages=("grc", "hbo")):
    """Create the SBLGNT and WLC editions and the words for every chapter in
    content/ (or only the editions for languages). Returns the SBLGNT
    edition."""
    editions = {
        "grc": Edition.objects.create(code="sblgnt", name="SBL Greek New Testament", language="grc",
                                      kind="original", licence="CC BY 4.0", source="sblgnt",
                                      source_commit="test"),
        "hbo": Edition.objects.create(code="wlc", name="Westminster Leningrad Codex", language="hbo",
                                      kind="original", licence="Public domain", source="macula-hebrew",
                                      source_commit="test"),
    }
    seq = 0
    for folder, edition in editions.items():
        if folder not in languages:
            continue
        for path in sorted((settings.REPO_ROOT / "data" / folder).glob("*.json")):
            for vid, words in json.loads(path.read_text(encoding="utf-8"))["verses"].items():
                book, chapter, verse = vid.split(".")
                for w in words:
                    # Hebrew extracts carry each morpheme's language (H or A).
                    Word.objects.create(edition=edition, book=book, chapter=int(chapter),
                                        verse=int(verse), seq=seq, **{"lang": folder, **w})
                    seq += 1
    return editions["grc"]


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
        # One rendering per language and level the record has.
        record = next(r for r in json.loads((CONTENT / "JHN" / "JHN.1.1-18.json").read_text())["records"]
                      if r["id"] == "JHN.1.12.s1")
        self.assertEqual(s.renderings.count(), sum(len(levels) for levels in record["renderings"].values()))
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


class FreshDatabaseTest(TestCase):
    def test_deploy_import_skips_until_texts_are_loaded(self):
        out = io.StringIO()
        call_command("import_content", "--if-texts-loaded", stdout=out, stderr=io.StringIO())
        self.assertIn("run import_texts", out.getvalue())
        self.assertEqual(Sentence.objects.count(), 0)
        with self.assertRaises(CommandError):
            import_content()

    def test_deploy_import_runs_once_texts_are_loaded(self):
        load_extract_words()
        call_command("import_content", "--if-texts-loaded", stdout=io.StringIO(), stderr=io.StringIO())
        self.assertTrue(Sentence.objects.exists())

    def test_deploy_import_skips_files_whose_text_is_not_loaded(self):
        # Only the Greek is in: the deploy imports the New Testament and skips
        # Genesis instead of failing (which blocked every deploy once Genesis
        # was added before the Hebrew was imported).
        load_extract_words(languages=("grc",))
        out = io.StringIO()
        call_command("import_content", "--if-texts-loaded", stdout=out, stderr=io.StringIO())
        self.assertIn("run import_texts wlc. Skipped.", out.getvalue())
        self.assertTrue(Sentence.objects.filter(book="JHN").exists())
        self.assertTrue(Sentence.objects.filter(book="ROM").exists())
        self.assertFalse(Sentence.objects.filter(book="GEN").exists())
        # Run by hand, the missing text is an error that says what to do.
        with self.assertRaisesMessage(CommandError, "run import_texts wlc"):
            import_content()


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
        # English numbering: a psalm's title is not a verse, so Psalm 3:1 is
        # our PSA.3.2; Hebrew Psalm 13:6 is English 13:5-6; Hebrew Genesis
        # 32:1 is English 31:55.
        for (book, chapter, verse), text in {
                ("PSA", 3, 1): "O LORD, how many are my foes!", ("PSA", 3, 2): "Many say of me",
                ("PSA", 13, 5): "But I have trusted in Your loving devotion;",
                ("PSA", 13, 6): "I will sing to the LORD,", ("GEN", 31, 55): "Early the next morning",
                ("GEN", 32, 1): "Jacob also went on his way"}.items():
            Verse.objects.create(edition=bsb, book=book, chapter=chapter, verse=verse, text=text)

    def test_passages_round_trip_the_content_files(self):
        response = self.client.get("/api/passages/jhn/1/")
        self.assertEqual(response.status_code, 200)
        # A chapter may be spread over several content files (John 1:1-18,
        # 1:19-51); the API returns all of its records, in file order.
        from_file = [r for path in sorted((CONTENT / "JHN").glob("JHN.1.*.json"))
                     for r in json.loads(path.read_text())["records"]]
        self.assertGreater(len(from_file), 17)   # both files, not just 1:1-18
        self.assertEqual(response.json()["records"], from_file)
        self.assertIn("JHN.1.1", response.json()["words"])

    def test_hebrew_passage_round_trips(self):
        response = self.client.get("/api/passages/gen/1/")
        self.assertEqual(response.status_code, 200)
        from_file = [r for path in sorted((CONTENT / "GEN").glob("GEN.1.*.json"))
                     for r in json.loads(path.read_text())["records"]]
        self.assertEqual(response.json()["records"], from_file)
        extract = json.loads((settings.REPO_ROOT / "data" / "hbo" / "GEN.1.json").read_text())
        self.assertEqual(response.json()["words"]["GEN.1.1"], extract["verses"]["GEN.1.1"])

    def test_chapter_text_by_edition(self):
        response = self.client.get("/api/text/JHN/1/?editions=bsb,sblgnt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["verses"][0]["text"],
                         {"bsb": "In the beginning was the Word", "sblgnt": "Ἐν ἀρχῇ"})

    def test_chapter_text_uses_our_verse_numbers(self):
        data = self.client.get("/api/text/PSA/3/?editions=bsb").json()
        self.assertEqual(data["numbering"], "source")
        self.assertEqual(data["verses"], [
            {"verse": 2, "text": {"bsb": "O LORD, how many are my foes!"}, "refs": {"bsb": ["PSA.3.1"]}},
            {"verse": 3, "text": {"bsb": "Many say of me"}, "refs": {"bsb": ["PSA.3.2"]}}])
        [verse] = self.client.get("/api/text/PSA/13/?editions=bsb").json()["verses"]
        self.assertEqual(verse, {"verse": 6, "refs": {"bsb": ["PSA.13.5", "PSA.13.6"]},
                                 "text": {"bsb": "But I have trusted in Your loving devotion; "
                                                 "I will sing to the LORD,"}})
        # A verse can move to another chapter.
        verses = self.client.get("/api/text/GEN/32/?editions=bsb").json()["verses"]
        self.assertEqual([(v["verse"], v["text"]["bsb"]) for v in verses],
                         [(1, "Early the next morning"), (2, "Jacob also went on his way")])
        self.assertEqual(self.client.get("/api/text/GEN/31/?editions=bsb").status_code, 404)

    def test_chapter_text_in_each_editions_numbering(self):
        data = self.client.get("/api/text/PSA/3/?editions=bsb&numbering=edition").json()
        self.assertEqual(data["verses"][0], {"verse": 1, "text": {"bsb": "O LORD, how many are my foes!"}})
        verses = self.client.get("/api/text/GEN/31/?editions=bsb&numbering=edition").json()["verses"]
        self.assertEqual(verses, [{"verse": 55, "text": {"bsb": "Early the next morning"}}])
        self.assertEqual(self.client.get("/api/text/PSA/3/?numbering=english").status_code, 400)

    def test_unknown_book_and_edition(self):
        self.assertEqual(self.client.get("/api/passages/XYZ/1/").status_code, 404)
        self.assertEqual(self.client.get("/api/text/JHN/1/?editions=nope").status_code, 400)

    def test_no_restricted_macula_fields(self):
        # Louw-Nida and SDBH word senses are used with permission, not openly
        # licensed: the word table and the API never carry them.
        from owb.sources import macula_greek, macula_hebrew
        restricted = set(macula_greek.RESTRICTED + macula_hebrew.RESTRICTED)
        self.assertFalse({f.name for f in Word._meta.get_fields()} & restricted)
        words = self.client.get("/api/passages/jhn/1/").json()["words"]["JHN.1.1"]
        self.assertTrue(words)
        self.assertFalse({k for w in words for k in w} & restricted)

    def test_editions_and_health(self):
        self.assertEqual({e["code"] for e in self.client.get("/api/editions/").json()}, {"sblgnt", "wlc", "bsb"})
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
