"""History in the admin (staff/history.py): word diffs since an approval,
and release notes from what import_content records (RecordChange)."""
import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase
from django.utils import timezone

from backend_tests.test_admin import K, AdminTestCase, account, client_for, sentence
from backend_tests.test_backend import CONTENT, import_content, load_extract_words
from staff.history import release_notes, word_diff
from translation.models import ImportRun, RecordChange, ReviewEvent, Sentence, SentenceChange


class WordDiffTest(SimpleTestCase):
    def test_words_inserted_and_deleted(self):
        self.assertEqual(word_diff("In the beginning was the Word", "In the beginning the Word existed"), [
            {"op": "same", "text": "In the beginning "}, {"op": "del", "text": "was "},
            {"op": "same", "text": "the Word"}, {"op": "ins", "text": " existed"}])
        self.assertEqual(word_diff("same", "same"), [{"op": "same", "text": "same"}])
        self.assertEqual(word_diff("", "new words"), [{"op": "ins", "text": "new words"}])

    def test_a_setting_span_and_a_verse_marker_are_one_word(self):
        before = "\\v 2 my {{gender:brothers|brothers and sisters}}, listen"
        after = "\\v 2 my {{gender:siblings|brothers and sisters}}, listen"
        self.assertEqual(word_diff(before, after), [
            {"op": "same", "text": "\\v 2 my "}, {"op": "del", "text": "{{gender:brothers|brothers and sisters}}"},
            {"op": "ins", "text": "{{gender:siblings|brothers and sisters}}"}, {"op": "same", "text": ", listen"}])


class SinceApprovalTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        s = sentence("JHN.1.1.s1", ("en", "fr"))
        s.renderings.filter(language="en", level="B").update(text="In the beginning was the Word")
        self.english = client_for(account("en@example.org", (K.LANGUAGE_REVIEWER, "en")))

    def approve(self, client, layer):
        r = client.post("/api/admin/review/JHN.1.1.s1/", {"layer": layer, "action": "approve"}, format="json")
        self.assertEqual(r.status_code, 201)
        return ReviewEvent.objects.order_by("-id").first()

    def test_an_approval_keeps_what_was_approved(self):
        event = self.approve(self.english, "en")
        self.assertEqual(event.snapshot["renderings"], {"L": "x", "B": "In the beginning was the Word", "R": "x"})
        self.assertEqual(event.snapshot["decisions"], {})
        meaning = self.approve(self.admin, "grc")
        self.assertEqual(meaning.snapshot, {"literal_gloss": "x", "decisions": {}})
        # Nothing has changed since.
        d = self.admin.get("/api/admin/history/verse/JHN.1.1/").json()
        approvals = d["sentences"][0]["approvals"]
        self.assertEqual([(a["layer"]["code"], a["changed"], a["known"]) for a in approvals],
                         [("grc", False, "unchanged"), ("en", False, "unchanged")])
        self.assertEqual(Sentence.objects.get().status, "meaning_reviewed")   # review.py's doing, not history's

    def test_the_verse_inspector_shows_the_words_changed_since(self):
        self.approve(self.english, "en")
        s = Sentence.objects.get()
        s.renderings.filter(language="en", level="B").update(text="In the beginning the Word existed")
        s.save()
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        d = reporter.get("/api/admin/history/verse/JHN.1.1/").json()
        a = d["sentences"][0]["approvals"][0]
        self.assertEqual((a["layer"]["code"], a["changed"], a["known"], a["by"]),
                         ("en", True, "snapshot", "en@example.org"))
        balanced = next(t for t in a["texts"] if t["level"] == "B")
        self.assertTrue(balanced["changed"])
        self.assertIn({"op": "del", "text": "was "}, balanced["segments"])
        self.assertIn({"op": "ins", "text": " existed"}, balanced["segments"])
        self.assertFalse(next(t for t in a["texts"] if t["level"] == "L")["changed"])
        self.assertEqual(a["decisions"], {"added": [], "changed": [], "removed": []})
        self.assertEqual(Sentence.objects.get().status, "ai_draft")

    def test_an_old_approval_is_worked_out_from_the_imports_since(self):
        s = Sentence.objects.get()
        event = ReviewEvent.objects.create(sentence=s, user=self.boss, action="reviewed", language="en",
                                           digest="before-snapshots")
        run = ImportRun.objects.create()
        SentenceChange.objects.create(run=run, record_id=s.record_id, verse="JHN.1.1", book="JHN", chapter=1,
                                      language="en", level="B", kind="changed",
                                      before="In the beginning was the Word", after="In the beginning the Word was")
        SentenceChange.objects.create(run=run, record_id=s.record_id, verse="JHN.1.1", book="JHN", chapter=1,
                                      language="en", level="B", kind="changed",
                                      before="In the beginning the Word was", after="In the beginning the Word existed")
        s.renderings.filter(language="en", level="B").update(text="In the beginning the Word existed")
        self.assertLess(event.created_at, run.started_at)
        a = self.admin.get("/api/admin/history/approvals/").json()["approvals"][0]
        self.assertEqual((a["record"], a["known"], a["decisions"]), ("JHN.1.1.s1", "reconstructed", None))
        balanced = next(t for t in a["texts"] if t["level"] == "B")
        self.assertEqual((balanced["before"], balanced["after"]),
                         ("In the beginning was the Word", "In the beginning the Word existed"))

    def test_the_approvals_log_is_for_the_team_area(self):
        self.approve(self.english, "en")
        self.assertEqual(self.english.get("/api/admin/history/approvals/").status_code, 403)
        d = self.admin.get("/api/admin/history/approvals/").json()
        self.assertEqual([(a["record"], a["layer"]["code"]) for a in d["approvals"]], [("JHN.1.1.s1", "en")])
        self.assertFalse(d["more"])


class ReleaseNotesTest(AdminTestCase):
    @classmethod
    def setUpTestData(cls):
        load_extract_words(("grc",), books=("PHM",))

    def test_what_changed_in_a_language(self):
        path = CONTENT / "PHM" / "PHM.1.json"
        data = json.loads(path.read_text())
        # The first import drafts English (and every other language) for the first time.
        first = data["records"][0]
        del first["renderings"]["en"]
        first["decisions"] = [d for d in first["decisions"] if d["language"] != "en"]
        with tempfile.TemporaryDirectory() as tmp:
            edited = Path(tmp) / "PHM.1.json"
            edited.write_text(json.dumps(data))
            import_content(str(edited))
        n = len(data["records"])
        self.assertEqual(RecordChange.objects.filter(kind="drafted", language="en").count(), n - 1)
        reviewer = client_for(account("en@example.org", (K.LANGUAGE_REVIEWER, "en")))
        data = json.loads(path.read_text())
        second = data["records"][1]
        rid, vid = second["id"], second["refs"][0]
        reviewer.post(f"/api/admin/review/{rid}/", {"layer": "en", "action": "approve"}, format="json")

        # The next brings PHM.1.1.s1 to English, and changes the second sentence.
        old = second["renderings"]["en"]["B"]
        second["renderings"]["en"]["B"] = old + " Amen."
        meaning = next(d for d in second["decisions"] if d["layer"] == "meaning")
        meaning["footnote"] = True
        meaning["choice"] += " (see the note)"
        second["decisions"].append({"id": "r-en-9", "layer": "rendering", "language": "en", "levels": ["B"],
                                    "category": "word_choice", "tokens": second["decisions"][-1]["tokens"][:1],
                                    "choice": "Amen", "alternatives": [], "reason": "A closing word.",
                                    "uncertain": False, "footnote": True})
        with tempfile.TemporaryDirectory() as tmp:
            edited = Path(tmp) / "PHM.1.json"
            edited.write_text(json.dumps(data))
            import_content(str(edited))
        self.assertEqual(Sentence.objects.get(record_id=rid).status, "ai_draft")
        self.assertEqual(sorted(RecordChange.objects.exclude(kind="drafted").values_list("record_id", "language",
                                                                                         "kind", "key")),
                         [(rid, "", "decision_changed", meaning["id"]),
                          (rid, "en", "decision_added", "r-en-9")])
        self.assertEqual(RecordChange.objects.filter(kind="drafted", language="en", run=ImportRun.objects.first())
                         .get().record_id, "PHM.1.1.s1")

        today = timezone.localdate().isoformat()
        exporter = client_for(account("rep@example.org", (K.REPORTING,)))
        self.assertEqual(exporter.get("/api/admin/history/release-notes/?lang=en").status_code, 400)
        self.assertEqual(exporter.get("/api/admin/history/release-notes/?lang=xx&since=" + today).status_code, 400)
        d = exporter.get("/api/admin/history/release-notes/?lang=en&since=" + today).json()
        self.assertEqual(d["imports"], 2)
        phm = d["books"][0]
        self.assertEqual((phm["code"], phm["drafted"], phm["counts"]["added"]), ("PHM", n, n))
        self.assertEqual(phm["counts"]["renderings"], 0)   # drafted in the same stretch: new, not changed
        # Since the first import only: one sentence drafted, one changed.
        run = ImportRun.objects.first()
        release = release_notes("en", run.started_at, timezone.now())
        later = release["books"][0]
        self.assertEqual([a["record"] for a in later["added"]], ["PHM.1.1.s1"])
        self.assertEqual(later["added_verses"], "1:1")
        self.assertEqual([(r["record"], r["level"], r["kind"]) for r in later["renderings"]], [(rid, "B", "changed")])
        self.assertEqual(later["renderings"][0]["segments"][-1], {"op": "ins", "text": " Amen."})
        self.assertEqual(sorted((x["key"], x["layer"], x["kind"]) for x in later["decisions"]),
                         [(meaning["id"], "meaning", "changed"), ("r-en-9", "rendering", "added")])
        self.assertEqual(sorted(x["key"] for x in later["footnotes"]), [meaning["id"], "r-en-9"])
        self.assertIn("footnote", next(x for x in later["decisions"] if x["key"] == meaning["id"])["fields"])
        # French saw the meaning decision change, but not the English one.
        french = release_notes("fr", run.started_at, timezone.now())["books"][0]
        self.assertEqual([x["key"] for x in french["decisions"]], [meaning["id"]])

        md = exporter.get("/api/admin/history/release-notes/?lang=en&since=" + today + "&file=md")
        self.assertEqual(md["Content-Type"], "text/markdown; charset=utf-8")
        self.assertIn(f'filename="open-word-bible-en-changes-{today}.md"', md["Content-Disposition"])
        text = md.content.decode()
        self.assertTrue(text.startswith("# Open Word Bible: what changed in English"))
        self.assertIn("## Philemon", text)
        self.assertIn("AI-assisted draft", text)

        # The English approval now shows what the import changed, word by word.
        a = self.admin.get(f"/api/admin/history/verse/{vid}/").json()["sentences"][0]["approvals"][0]
        self.assertEqual((a["known"], a["decisions"]["added"]), ("snapshot", ["r-en-9"]))
        balanced = next(t for t in a["texts"] if t["level"] == "B")
        self.assertEqual((balanced["before"], balanced["segments"][-1]), (old, {"op": "ins", "text": " Amen."}))
