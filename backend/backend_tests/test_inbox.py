"""Reader-inbox triage (staff/inbox.py): assigning messages, the filters
and order, saved replies, and the dashboard's inbox chips."""
from datetime import timedelta

from django.utils import timezone

from feedback.models import ReaderMessage
from staff.models import AdminAction

from .test_admin import K, AdminTestCase, account, client_for


class InboxTriageTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.reader = account("reader@example.org")
        self.reader.first_name = "Ann"
        self.reader.save()
        self.editor = account("ed@example.org", (K.EDITOR,))
        self.old = self.message("JHN.3.16", days=5)
        self.recent = self.message("JHN.3.17", days=1)

    def message(self, verse, days=0, **fields):
        m = ReaderMessage.objects.create(user=self.reader, kind="suggestion", verse=verse, language="en",
                                         text="A thought.", **fields)
        ReaderMessage.objects.filter(id=m.id).update(created_at=timezone.now() - timedelta(days=days))
        m.refresh_from_db()
        return m

    def patch(self, client, m, body):
        return client.patch(f"/api/admin/inbox/{m.id}/", body, format="json")

    def test_assign_and_unassign(self):
        r = self.patch(self.admin, self.old, {"assigned_to": "me"})
        self.assertEqual(r.json()["assigned_to"]["email"], "boss@example.org")
        r = self.patch(self.admin, self.old, {"assigned_to": "ED@example.org"})
        self.assertEqual(r.json()["assigned_to"]["id"], self.editor.id)
        self.assertTrue(r.json()["assigned_at"])
        r = self.patch(self.admin, self.old, {"assigned_to": None})
        self.assertIsNone(r.json()["assigned_to"])
        self.assertIsNone(r.json()["assigned_at"])
        actions = list(AdminAction.objects.order_by("created_at").values_list("action", flat=True))
        self.assertEqual(actions, ["message.assign", "message.assign", "message.unassign"])

    def test_only_inbox_members_can_be_assigned(self):
        reporter = account("rep@example.org", (K.REPORTING,))
        for who in (reporter.id, "reader@example.org", 99999):
            r = self.patch(self.admin, self.old, {"assigned_to": who})
            self.assertEqual(r.status_code, 400, who)
        self.old.refresh_from_db()
        self.assertIsNone(self.old.assigned_to)
        team = {u["email"] for u in self.admin.get("/api/admin/inbox/").json()["team"]}
        self.assertEqual(team, {"boss@example.org", "ed@example.org"})

    def test_filters_and_order(self):
        ReaderMessage.objects.filter(id=self.recent.id).update(assigned_to=self.editor)
        new = self.admin.get("/api/admin/inbox/").json()["messages"]
        self.assertEqual([m["verse"] for m in new], ["JHN.3.16", "JHN.3.17"])   # oldest waiting first
        self.assertEqual([m["waiting"] for m in new], [True, False])
        self.assertEqual(new[0]["age_days"], 5)
        mine = client_for(self.editor).get("/api/admin/inbox/?assigned=me").json()["messages"]
        self.assertEqual([m["verse"] for m in mine], ["JHN.3.17"])
        none = self.admin.get("/api/admin/inbox/?assigned=none").json()["messages"]
        self.assertEqual([m["verse"] for m in none], ["JHN.3.16"])
        theirs = self.admin.get(f"/api/admin/inbox/?assigned={self.editor.id}").json()["messages"]
        self.assertEqual([m["verse"] for m in theirs], ["JHN.3.17"])
        ReaderMessage.objects.update(status="done")
        done = self.admin.get("/api/admin/inbox/?status=done").json()["messages"]
        self.assertEqual([m["verse"] for m in done], ["JHN.3.17", "JHN.3.16"])   # the rest newest first

    def test_saved_replies_are_filled(self):
        m = self.admin.get("/api/admin/inbox/").json()["messages"][0]
        replies = {r["key"]: r["text"] for r in m["replies"]}
        self.assertIn("Hello Ann,", replies["thanks"])
        self.assertIn("John 3:16", replies["thanks"])
        self.assertIn("/jhn/3/#v16", replies["fixed"])
        self.assertNotIn("{", "".join(replies.values()))
        answered = self.message("JHN.3.18", status="answered", reply="Thanks.")
        r = self.patch(self.admin, answered, {"note": "x"})
        self.assertEqual(r.json()["replies"], [])
        # A reply is still sent once.
        r = self.patch(self.admin, answered, {"reply": "Again"})
        self.assertEqual(r.status_code, 400)

    def test_dashboard_chips(self):
        ReaderMessage.objects.filter(id=self.recent.id).update(assigned_to=self.boss)
        keys = {a["key"]: a for a in self.admin.get("/api/admin/overview/").json()["attention"]}
        self.assertEqual(keys["inbox_late"]["count"], 1)
        self.assertEqual(keys["inbox_late"]["tone"], "hot")
        self.assertEqual(keys["inbox"]["count"], 2)
        self.assertEqual(keys["inbox_mine"]["count"], 1)
        self.assertEqual(keys["inbox_mine"]["href"], "#inbox/mine")
        keys = {a["key"] for a in client_for(self.editor).get("/api/admin/overview/").json()["attention"]}
        self.assertNotIn("inbox_mine", keys)
