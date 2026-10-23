"""Review in the admin (staff/review.py) and what each import changed
(staff/changes.py, SentenceChange)."""
import json
import tempfile
from pathlib import Path

from backend_tests.test_admin import K, AdminTestCase, account, client_for, sentence
from backend_tests.test_backend import CONTENT, import_content, load_extract_words
from texts.models import Edition
from translation.models import ImportRun, Rendering, ReviewEvent, Sentence, SentenceChange


def hebrew(record_id):
    wlc = Edition.objects.get_or_create(
        code="wlc", defaults=dict(name="WLC", language="hbo", kind="original", licence="Public domain",
                                  source="macula-hebrew", source_commit="0" * 40))[0]
    return sentence(record_id, ("en",), edition=wlc)


class ReviewTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        sentence("JHN.1.1.s1", ("en", "fr"))
        sentence("JHN.1.2.s1", ("en",))
        hebrew("GEN.1.1.s1")
        self.scholar = client_for(account("grc@example.org", (K.SCHOLAR_REVIEWER, "grc")))
        self.french = client_for(account("fr@example.org", (K.LANGUAGE_REVIEWER, "fr")))
        self.editor = client_for(account("ed@example.org", (K.EDITOR,)))

    def act(self, client, record, layer, action="approve", note=""):
        return client.post(f"/api/admin/review/{record}/", {"layer": layer, "action": action, "note": note},
                           format="json")

    def test_reviewers_open_review_and_editors_do_not(self):
        self.assertEqual(self.french.get("/api/me").json()["admin"], ["overview", "export", "review"])
        self.assertEqual(self.editor.get("/api/admin/review/").status_code, 403)

    def test_each_reviewer_has_their_own_layer(self):
        data = self.scholar.get("/api/admin/review/").json()
        self.assertEqual([lay["code"] for lay in data["layers"]], ["grc"])
        self.assertEqual([s["record"] for s in data["sentences"]], ["JHN.1.1.s1", "JHN.1.2.s1"])
        self.assertEqual(self.scholar.get("/api/admin/review/?layer=fr").status_code, 403)
        data = self.french.get("/api/admin/review/").json()
        self.assertEqual(data["layer"]["code"], "fr")
        self.assertEqual([s["record"] for s in data["sentences"]], ["JHN.1.1.s1"])
        self.assertEqual(self.act(self.scholar, "JHN.1.1.s1", "fr").status_code, 403)
        self.assertEqual(self.act(self.scholar, "GEN.1.1.s1", "hbo").status_code, 403)
        self.assertEqual(self.act(self.scholar, "GEN.1.1.s1", "grc").status_code, 400)   # not in the NT layer
        self.assertEqual(self.act(self.french, "JHN.1.2.s1", "fr").status_code, 400)     # not drafted in French
        # A super admin may review any layer, Hebrew meaning included.
        self.assertEqual(self.act(self.admin, "GEN.1.1.s1", "hbo").status_code, 201)
        self.assertFalse(ReviewEvent.objects.exclude(user__username="boss@example.org").exists())

    def test_approving_the_meaning(self):
        before = Sentence.objects.get(record_id="JHN.1.1.s1").updated_at
        r = self.act(self.scholar, "JHN.1.1.s1", "grc")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["next"], "JHN.1.2.s1")
        s = Sentence.objects.get(record_id="JHN.1.1.s1")
        self.assertEqual((s.status, s.updated_at), ("meaning_reviewed", before))
        event = ReviewEvent.objects.get()
        self.assertEqual((event.action, event.language, event.user.username),
                         ("meaning_reviewed", "", "grc@example.org"))
        counts = self.scholar.get("/api/admin/review/").json()["counts"]
        self.assertEqual((counts["approved"], counts["not_reviewed"]), (1, 1))
        # The dashboard's status counts see it at once.
        statuses = self.admin.get("/api/admin/overview/").json()["totals"]["statuses"]
        self.assertEqual(statuses["meaning_reviewed"], 1)
        todo = self.scholar.get("/api/admin/review/?state=todo").json()["sentences"]
        self.assertEqual([s["record"] for s in todo], ["JHN.1.2.s1"])

    def test_wording_approval_is_per_language_and_goes_stale(self):
        self.assertEqual(self.act(self.french, "JHN.1.1.s1", "fr").status_code, 201)
        self.assertEqual(self.act(self.admin, "JHN.1.1.s1", "en").status_code, 201)
        self.assertEqual(Sentence.objects.get(record_id="JHN.1.1.s1").status, "ai_draft")

        def state(client, layer):
            return client.get(f"/api/admin/review/JHN.1.1.s1/?layer={layer}").json()["state"]
        self.assertEqual(state(self.french, "fr"), "approved")
        # An import rewrites the French (and saves the sentence, as it does).
        s = Sentence.objects.get(record_id="JHN.1.1.s1")
        s.renderings.filter(language="fr", level="B").update(text="nouveau")
        s.save()
        self.assertEqual(state(self.french, "fr"), "changed")
        self.assertEqual(state(self.admin, "en"), "approved")
        trail = self.french.get("/api/admin/review/JHN.1.1.s1/?layer=fr").json()["trail"]
        self.assertEqual([(e["language"], e["changed"]) for e in trail], [("en", False), ("fr", True)])
        self.assertEqual(self.french.get("/api/admin/review/?state=changed").json()["counts"]["changed"], 1)

    def test_flags_reach_editors_until_approved_again(self):
        self.assertEqual(self.act(self.french, "JHN.1.1.s1", "fr", "flag").status_code, 400)   # needs a note
        self.assertEqual(self.act(self.french, "JHN.1.1.s1", "fr", "flag", "« Verbe » is dated").status_code, 201)
        flags = self.editor.get("/api/admin/review/flags/").json()["flags"]
        self.assertEqual([(f["record"], f["layer"]["code"], f["note"]) for f in flags],
                         [("JHN.1.1.s1", "fr", "« Verbe » is dated")])
        chips = {a["key"]: a["count"] for a in self.editor.get("/api/admin/overview/").json()["attention"]}
        self.assertEqual(chips["flags"], 1)
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        self.assertNotIn("flags", {a["key"] for a in reporter.get("/api/admin/overview/").json()["attention"]})
        self.assertEqual(self.french.get("/api/admin/review/").json()["counts"]["flagged"], 1)
        self.act(self.french, "JHN.1.1.s1", "fr", "comment", "Asked the editors")
        self.assertEqual(len(self.editor.get("/api/admin/review/flags/").json()["flags"]), 1)
        self.act(self.french, "JHN.1.1.s1", "fr")
        self.assertEqual(self.editor.get("/api/admin/review/flags/").json()["flags"], [])


class ChangesTest(AdminTestCase):
    @classmethod
    def setUpTestData(cls):
        load_extract_words(("grc",), books=("PHM",))

    def test_import_records_changes_but_only_counts_first_drafts(self):
        path = CONTENT / "PHM" / "PHM.1.json"
        records = json.loads(path.read_text())["records"]
        import_content(str(path))
        run = ImportRun.objects.get()
        self.assertFalse(SentenceChange.objects.exists())
        self.assertEqual(run.drafted["PHM"]["en"], len(records))
        reviewer = client_for(account("en@example.org", (K.LANGUAGE_REVIEWER, "en")))
        reviewer.post("/api/admin/review/PHM.1.1.s1/", {"layer": "en", "action": "approve"}, format="json")

        data = json.loads(path.read_text())
        first = data["records"][0]
        old = first["renderings"]["en"]["B"]
        first["renderings"]["en"]["B"] = old + " Amen."
        first["renderings"]["fr"]["R"] += " Amen."
        with tempfile.TemporaryDirectory() as tmp:
            edited = Path(tmp) / "PHM.1.json"
            edited.write_text(json.dumps(data))
            import_content(str(edited))
        run = ImportRun.objects.first()
        self.assertEqual(run.drafted, {})
        self.assertEqual(sorted(SentenceChange.objects.values_list("record_id", "language", "level", "kind")),
                         [("PHM.1.1.s1", "en", "B", "changed"), ("PHM.1.1.s1", "fr", "R", "changed")])
        d = self.admin.get("/api/admin/changes/").json()
        self.assertEqual([r["changed"] for r in d["runs"]], [2, 0])
        self.assertEqual(d["run"]["id"], run.id)
        en = next(c for c in d["changes"] if c["language"] == "en")
        self.assertEqual((en["verse"], en["before"], en["after"]), ("PHM.1.1", old, old + " Amen."))
        self.assertEqual(len(self.admin.get(f"/api/admin/changes/?run={run.id}&lang=fr").json()["changes"]), 1)
        # The English approval no longer matches what the import brought.
        state = reviewer.get("/api/admin/review/PHM.1.1.s1/?layer=en").json()["state"]
        self.assertEqual(state, "changed")
        self.assertEqual(Rendering.objects.filter(sentence__record_id="PHM.1.1.s1", language="fr").count(), 3)
