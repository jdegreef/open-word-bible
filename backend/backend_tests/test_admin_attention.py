"""The rail's counts (staff/attention.py): what is waiting for an account,
only in the sections its roles open, and cheap to ask for again."""
from unittest import mock

from django.core.cache import cache
from django.test import override_settings

from accounts.models import Role
from feedback.models import ReaderMessage
from staff import jobs as staff_jobs

from .test_admin import AdminTestCase, account, client_for, sentence

K = Role.Kind


class AttentionTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        self.reader = account("ruth@example.org")
        self.editor_user = account("ed@example.org", (K.EDITOR,))
        self.editor = client_for(self.editor_user)

    def sections(self, client):
        r = client.get("/api/admin/attention/")
        self.assertEqual(r.status_code, 200)
        return r.json()["sections"]

    def test_signed_out_is_refused(self):
        from rest_framework.test import APIClient
        self.assertEqual(APIClient().get("/api/admin/attention/").status_code, 401)

    def test_nothing_waiting(self):
        self.assertEqual(self.sections(self.admin), {})

    def test_inbox_new_and_assigned_to_the_account(self):
        for text in ("one", "two", "three"):
            ReaderMessage.objects.create(user=self.reader, kind="question", verse="JHN.3.16", language="en", text=text)
        ReaderMessage.objects.filter(text="one").update(assigned_to=self.editor_user)
        ReaderMessage.objects.filter(text="three").update(status=ReaderMessage.Status.DONE)
        inbox = self.sections(self.editor)["inbox"]
        self.assertEqual(inbox["count"], 2)
        self.assertEqual(inbox["title"], "2 new messages, 1 assigned to you")
        self.assertEqual(self.sections(self.admin)["inbox"]["title"], "2 new messages")
        # A reviewer's roles don't open the inbox.
        reviewer = client_for(account("rev@example.org", (K.LANGUAGE_REVIEWER, "en")))
        self.assertNotIn("inbox", self.sections(reviewer))

    def test_review_counts_the_account_layers_not_approved(self):
        for n in (1, 2, 3):
            sentence(f"PHM.1.{n}.s1", langs=("en", "fr"))
        reviewer_user = account("rev@example.org", (K.LANGUAGE_REVIEWER, "en"))
        reviewer = client_for(reviewer_user)
        self.assertEqual(self.sections(reviewer)["review"]["count"], 3)
        r = reviewer.post("/api/admin/review/PHM.1.1.s1/", {"layer": "en", "action": "approve"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        review = self.sections(reviewer)["review"]
        self.assertEqual(review["count"], 2)
        self.assertEqual(review["title"], "To review: 2 in en")
        # A super admin may review every layer, but no reviewer role names one.
        self.assertNotIn("review", self.sections(self.admin))
        # An editor doesn't review.
        self.assertNotIn("review", self.sections(self.editor))

    def test_layer_sizes_are_cached_until_the_content_changes(self):
        sentence("PHM.1.1.s1")
        reviewer = client_for(account("rev@example.org", (K.LANGUAGE_REVIEWER, "en")))
        self.sections(reviewer)
        with mock.patch("staff.review._scope", side_effect=AssertionError("counted again")):
            self.assertEqual(self.sections(reviewer)["review"]["count"], 1)
        sentence("PHM.1.2.s1")
        self.assertEqual(self.sections(reviewer)["review"]["count"], 2)

    @override_settings(OWB_GITHUB_TOKEN="token")
    def test_fixes_and_jobs_from_github_cached(self):
        calls = []

        def issue(number, title, **more):
            return {"number": number, "title": title, "html_url": "u", "created_at": "2026-11-01T00:00:00Z", "body": "",
                    **more}

        def github(path, method="GET", body=None):
            calls.append(path)
            if "fix-request" in path:
                return [issue(5, "Fix"), issue(6, "PR", pull_request={})]
            return [issue(7, "Draft")]

        with mock.patch.object(staff_jobs, "_github", side_effect=github):
            found = self.sections(self.admin)
            self.assertEqual(found["fixes"], {"count": 1, "title": "1 open fix request"})
            self.assertEqual(found["jobs"], {"count": 1, "title": "1 open drafting job"})
            self.sections(self.admin)
            self.assertEqual(len(calls), 2)
            # An editor sees fix requests but not drafting jobs.
            found = self.sections(self.editor)
            self.assertIn("fixes", found)
            self.assertNotIn("jobs", found)

    @override_settings(OWB_GITHUB_TOKEN="token")
    def test_github_down_leaves_its_numbers_out(self):
        with mock.patch.object(staff_jobs, "_github", side_effect=staff_jobs.GitHubError):
            ReaderMessage.objects.create(user=self.reader, kind="question", verse="JHN.3.16", language="en", text="x")
            found = self.sections(self.admin)
        self.assertNotIn("fixes", found)
        self.assertEqual(found["inbox"]["count"], 1)

    def test_no_token_asks_nothing_of_github(self):
        with mock.patch.object(staff_jobs, "_github", side_effect=AssertionError("asked GitHub")):
            self.assertEqual(self.sections(self.admin), {})
