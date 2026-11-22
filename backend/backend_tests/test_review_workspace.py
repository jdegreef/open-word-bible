"""A reviewer's workspace (staff/workspace.py), bulk review
(staff/bulk.py) and review assignments (staff/assignments.py)."""
import datetime
from unittest import mock

from django.utils import timezone

from backend_tests.test_admin import K, AdminTestCase, account, client_for, sentence
from staff import bulk, review
from staff.models import AdminAction, ReviewAssignment
from translation.models import ReviewEvent, ReviewState, Sentence


class BulkTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        for rid in ("JHN.3.1.s1", "JHN.3.2.s1", "JHN.3.3.s1", "JHN.4.1.s1"):
            sentence(rid, ("en", "fr"))
        sentence("JHN.3.4.s1", ("en",))   # not drafted in French
        self.french = client_for(account("fr@example.org", (K.LANGUAGE_REVIEWER, "fr")))
        self.scholar = client_for(account("grc@example.org", (K.SCHOLAR_REVIEWER, "grc")))
        self.editor = client_for(account("ed@example.org", (K.EDITOR,)))

    def post(self, client, **body):
        return client.post("/api/admin/review/bulk/", body, format="json")

    def test_permissions(self):
        body = dict(layer="fr", action="approve", records=["JHN.3.1.s1"])
        self.assertEqual(self.post(self.editor, **body).status_code, 403)          # no review area
        self.assertEqual(self.post(self.scholar, **body).status_code, 403)         # not their layer
        self.assertEqual(self.post(self.french, **{**body, "layer": "en"}).status_code, 403)
        self.assertEqual(self.post(self.french, **body).status_code, 201)
        self.assertFalse(ReviewEvent.objects.exclude(user__username="fr@example.org").exists())

    def test_approves_each_as_a_normal_review_event(self):
        r = self.post(self.french, layer="fr", action="approve", records=["JHN.3.2.s1", "JHN.3.1.s1", "JHN.3.1.s1"])
        self.assertEqual(r.status_code, 201)
        data = r.json()
        self.assertEqual(data["applied"], 2)
        self.assertEqual([(x["record"], x["result"], x["state"]) for x in data["results"]],
                         [("JHN.3.1.s1", "applied", "approved"), ("JHN.3.2.s1", "applied", "approved")])
        events = ReviewEvent.objects.order_by("id")
        self.assertEqual([(e.sentence.record_id, e.action, e.language) for e in events],
                         [("JHN.3.1.s1", "reviewed", "fr"), ("JHN.3.2.s1", "reviewed", "fr")])
        s = Sentence.objects.get(record_id="JHN.3.1.s1")
        self.assertEqual(events[0].digest, review.digest(review._with_texts(Sentence.objects, "fr").get(pk=s.pk), "fr"))
        self.assertEqual(events[0].snapshot["renderings"], {"L": "x", "B": "x", "R": "x"})
        self.assertEqual(ReviewState.objects.filter(layer="fr", state="approved").count(), 2)
        self.assertEqual(s.status, "ai_draft")   # wording approvals don't change the status
        # Again: already approved, so skipped rather than approved twice.
        again = self.post(self.french, layer="fr", action="approve", records=["JHN.3.1.s1"]).json()
        self.assertEqual((again["applied"], again["skipped"]), (0, 1))
        self.assertEqual(ReviewEvent.objects.count(), 2)

    def test_meaning_bulk_moves_status_on(self):
        r = self.post(self.scholar, layer="grc", action="approve", records=["JHN.3.1.s1", "JHN.3.4.s1"])
        self.assertEqual(r.status_code, 201)
        self.assertEqual(set(Sentence.objects.filter(status="meaning_reviewed").values_list("record_id", flat=True)),
                         {"JHN.3.1.s1", "JHN.3.4.s1"})

    def test_flag_needs_a_note_and_opens_flags(self):
        self.assertEqual(self.post(self.french, layer="fr", action="flag", records=["JHN.3.1.s1"]).status_code, 400)
        r = self.post(self.french, layer="fr", action="flag", note="Tutoiement", records=["JHN.3.1.s1", "JHN.3.2.s1"])
        self.assertEqual(r.status_code, 201)
        self.assertEqual(len(self.editor.get("/api/admin/review/flags/").json()["flags"]), 2)

    def test_a_bad_record_saves_nothing(self):
        r = self.post(self.french, layer="fr", action="approve", records=["JHN.3.1.s1", "JHN.3.4.s1", "NOPE.1.1.s1"])
        self.assertEqual(r.status_code, 400)
        self.assertEqual({x["record"]: x["code"] for x in r.json()["results"]},
                         {"JHN.3.4.s1": "not_in_layer", "NOPE.1.1.s1": "not_found"})
        self.assertFalse(ReviewEvent.objects.exists())

    def test_a_failure_partway_rolls_everything_back(self):
        real = review.apply
        calls = []

        def failing(user, s, layer, action, note):
            calls.append(s.record_id)
            if len(calls) == 2:
                raise RuntimeError("boom")
            return real(user, s, layer, action, note)

        with mock.patch.object(review, "apply", failing):
            r = self.post(self.french, layer="fr", action="approve", records=["JHN.3.1.s1", "JHN.3.2.s1", "JHN.3.3.s1"])
        self.assertEqual(r.status_code, 500)
        self.assertEqual(len(calls), 2)
        self.assertFalse(ReviewEvent.objects.exists())
        self.assertFalse(ReviewState.objects.exists())

    def test_batch_size_is_capped(self):
        with mock.patch.object(bulk, "MAX", 2):
            r = self.post(self.french, layer="fr", action="approve", records=["JHN.3.1.s1", "JHN.3.2.s1", "JHN.3.3.s1"])
        self.assertEqual((r.status_code, r.json()["code"]), (400, "too_many"))
        self.assertFalse(ReviewEvent.objects.exists())

    def test_rest_of_chapter_leaves_flags_and_other_chapters(self):
        self.post(self.french, layer="fr", action="flag", note="Check", records=["JHN.3.2.s1"])
        self.post(self.french, layer="fr", action="approve", records=["JHN.3.1.s1"])
        dry = self.post(self.french, layer="fr", action="approve", chapter="JHN.3", dry_run=True).json()
        self.assertEqual([(x["record"], x["result"]) for x in dry["results"]], [("JHN.3.3.s1", "would_apply")])
        self.assertEqual(ReviewEvent.objects.count(), 2)
        done = self.post(self.french, layer="fr", action="approve", chapter="JHN.3").json()
        self.assertEqual([x["record"] for x in done["results"]], ["JHN.3.3.s1"])
        states = dict(ReviewState.objects.filter(layer="fr").values_list("sentence__record_id", "state"))
        self.assertEqual(states, {"JHN.3.1.s1": "approved", "JHN.3.2.s1": "flagged", "JHN.3.3.s1": "approved"})
        self.assertEqual(self.post(self.french, layer="fr", action="flag", note="x", chapter="JHN.3").status_code, 400)
        self.assertEqual(self.post(self.french, layer="fr", action="approve", chapter="JHN").status_code, 400)


class AssignmentTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        sentence("JHN.1.1.s1", ("en", "fr"))
        sentence("JHN.2.1.s1", ("en", "fr"))
        sentence("ROM.1.1.s1", ("en", "fr"))
        self.fr_user = account("fr@example.org", (K.LANGUAGE_REVIEWER, "fr"))
        self.french = client_for(self.fr_user)
        self.ed_user = account("ed@example.org", (K.EDITOR,))
        self.editor = client_for(self.ed_user)
        self.other = account("es@example.org", (K.LANGUAGE_REVIEWER, "es"))

    def assign(self, client, **body):
        body = {"layer": "fr", "book": "JHN", "assignee": self.fr_user.id, **body}
        return client.post("/api/admin/assignments/", body, format="json")

    def test_editors_and_admins_assign_reviewers_do_not(self):
        self.assertEqual(self.assign(self.french).status_code, 403)
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        self.assertEqual(self.assign(reporter).status_code, 403)
        r = self.assign(self.editor, chapter_from=1, chapter_to=1, due="2030-01-01", note="Start here")
        self.assertEqual(r.status_code, 201)
        a = r.json()["assignment"]
        self.assertEqual((a["label"], a["standing"], a["progress"]["total"]), ("John 1", "open", 1))
        self.assertEqual(self.assign(self.admin).status_code, 201)
        self.assertTrue(AdminAction.objects.filter(action="review.assign").exists())
        # Only to someone who reviews the layer, and only a book in it.
        self.assertEqual(self.assign(self.editor, assignee=self.other.id).json()["code"], "not_a_reviewer")
        self.assertEqual(self.assign(self.editor, layer="grc").json()["code"], "not_a_reviewer")
        self.assertEqual(self.assign(self.editor, layer="hbo", assignee=self.boss.id).json()["code"], "not_in_layer")
        self.assertEqual(self.assign(self.editor, chapter_from=3, chapter_to=2).status_code, 400)
        self.assertEqual(self.assign(self.editor, due="tomorrow").status_code, 400)
        # Editors change and close; reviewers can't.
        path = f"/api/admin/assignments/{a['id']}/"
        self.assertEqual(self.french.patch(path, {"closed": True}, format="json").status_code, 403)
        self.assertEqual(self.french.delete(path).status_code, 403)
        closed = self.editor.patch(path, {"closed": True}, format="json").json()["assignment"]
        self.assertEqual(closed["standing"], "closed")
        self.assertEqual(self.editor.delete(path).status_code, 204)

    def test_who_sees_which(self):
        self.assign(self.editor)
        ReviewAssignment.objects.create(layer="es", book="JHN", assignee=self.other)
        self.assertEqual(len(self.french.get("/api/admin/assignments/").json()["assignments"]), 1)
        self.assertNotIn("reviewers", self.french.get("/api/admin/assignments/").json())
        everyone = self.editor.get("/api/admin/assignments/").json()
        self.assertEqual(len(everyone["assignments"]), 2)
        self.assertIn(self.fr_user.id, [p["id"] for p in everyone["reviewers"]])
        self.assertNotIn(self.ed_user.id, [p["id"] for p in everyone["reviewers"]])

    def test_overdue_done_and_closed(self):
        today = timezone.localdate()
        late = self.assign(self.editor, chapter_from=1, chapter_to=1,
                           due=(today - datetime.timedelta(days=1)).isoformat()).json()["assignment"]
        self.assertEqual((late["standing"], late["days_left"]), ("overdue", -1))
        due_today = self.assign(self.editor, chapter_from=2, due=today.isoformat()).json()["assignment"]
        self.assertEqual(due_today["standing"], "open")
        self.assign(self.editor, book="ROM")   # no date: never overdue
        chips = {c["key"]: c["count"] for c in self.french.get("/api/admin/overview/").json()["attention"]}
        self.assertEqual((chips["assigned"], chips["assigned_overdue"]), (3, 1))
        # Every sentence in range approved: done, no longer overdue nor counted.
        self.french.post("/api/admin/review/JHN.1.1.s1/", {"layer": "fr", "action": "approve"}, format="json")
        listed = {a["id"]: a for a in self.french.get("/api/admin/assignments/").json()["assignments"]}
        self.assertEqual(listed[late["id"]]["standing"], "done")
        chips = {c["key"]: c["count"] for c in self.french.get("/api/admin/overview/").json()["attention"]}
        self.assertEqual(chips["assigned"], 2)
        self.assertNotIn("assigned_overdue", chips)
        # A closed one is left out unless asked for.
        self.editor.patch(f"/api/admin/assignments/{due_today['id']}/", {"closed": True}, format="json")
        self.assertEqual(len(self.french.get("/api/admin/assignments/").json()["assignments"]), 2)
        self.assertEqual(len(self.french.get("/api/admin/assignments/?closed=1").json()["assignments"]), 3)
        # Editors don't review, so they get no assignment chips.
        chips = {c["key"] for c in self.editor.get("/api/admin/overview/").json()["attention"]}
        self.assertNotIn("assigned", chips)


class WorkspaceTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        for rid in ("JHN.1.1.s1", "JHN.1.2.s1", "ROM.1.1.s1"):
            sentence(rid, ("en", "fr"))
        self.fr_user = account("fr@example.org", (K.LANGUAGE_REVIEWER, "fr"))
        self.french = client_for(self.fr_user)

    def act(self, record, action="approve", note=""):
        return self.french.post(f"/api/admin/review/{record}/", {"layer": "fr", "action": action, "note": note},
                                format="json")

    def test_only_reviewers_of_the_layer(self):
        self.assertEqual(client_for(account("ed@example.org", (K.EDITOR,))).get(
            "/api/admin/review/workspace/").status_code, 403)
        self.assertEqual(self.french.get("/api/admin/review/workspace/?layer=grc").status_code, 403)

    def test_the_workspace(self):
        self.act("JHN.1.1.s1")
        self.act("JHN.1.2.s1", "flag", "Tense")
        ReviewAssignment.objects.create(layer="fr", book="ROM", assignee=self.fr_user)
        # An import changes the approved sentence.
        s = Sentence.objects.get(record_id="JHN.1.1.s1")
        s.renderings.filter(language="fr", level="B").update(text="nouveau texte")
        s.save()
        d = self.french.get("/api/admin/review/workspace/").json()
        self.assertEqual(d["layer"]["code"], "fr")
        self.assertEqual((d["counts"]["changed"], d["counts"]["flagged"], d["counts"]["not_reviewed"]), (1, 1, 1))
        self.assertEqual([(b["code"], b["counts"]["total"]) for b in d["books"]], [("JHN", 2), ("ROM", 1)])
        self.assertEqual(d["in_progress"], ["JHN", "ROM"])
        self.assertEqual([(f["record"], f["note"]) for f in d["flags"]], [("JHN.1.2.s1", "Tense")])
        self.assertEqual(d["changes"]["total"], 1)
        item = d["changes"]["items"][0]
        self.assertEqual((item["record"], item["changed"]), ("JHN.1.1.s1", True))
        self.assertIn({"op": "ins", "text": "nouveau texte"}, [seg for t in item["texts"] for seg in t["segments"]])
        self.assertEqual([a["label"] for a in d["assignments"]], ["Romans"])
        self.assertEqual(d["checks"], "fr")
