"""Bulk drafting jobs and the queue board (staff/jobs.py)."""
import json
from unittest import mock

from django.core.cache import cache
from django.test import override_settings

from staff import jobs as staff_jobs
from staff.models import AdminAction

from .test_admin import K, AdminTestCase, account, client_for, sentence

OPEN_JOB = {"number": 5, "title": "Draft Ezekiel", "html_url": "https://github.com/x/y/issues/5",
            "created_at": "2026-10-15T00:00:00Z", "state": "open", "labels": [{"name": "drafting-job"}],
            "body": 'x\n<!-- drafting-job {"book": "EZK", "languages": ["es"]} -->'}
PULL = {"number": 9, "title": "Draft Ezekiel in Spanish", "body": "Part of #5", "state": "open",
        "html_url": "https://github.com/x/y/pull/9", "draft": False, "merged_at": None,
        "updated_at": "2026-10-16T00:00:00Z"}


class GitHub:
    """A stand-in for jobs._github: the open job above, and new issues
    numbered from 100, refusing from the fail_after'th on."""

    def __init__(self, fail_after=None):
        self.filed, self.fail_after = [], fail_after

    def __call__(self, path, method="GET", body=None):
        if method == "POST":
            if self.fail_after is not None and len(self.filed) >= self.fail_after:
                raise staff_jobs.GitHubError
            self.filed.append(body)
            n = 99 + len(self.filed)
            return {"number": n, "html_url": f"https://github.com/x/y/issues/{n}"}
        if path.startswith("pulls"):
            return [PULL]
        return [OPEN_JOB]


@override_settings(OWB_GITHUB_TOKEN="t")
class BulkJobsTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        # Genesis, Exodus and Ezekiel have one chapter of one sentence here:
        # English has all three; French has Genesis too.
        chapters = mock.patch.dict(staff_jobs.CHAPTERS, {"GEN": 1, "EXO": 1, "EZK": 1})
        chapters.start()
        self.addCleanup(chapters.stop)
        sentence("GEN.1.1.s1", ("en", "fr"))
        sentence("EXO.1.1.s1", ("en",))
        sentence("EZK.1.1.s1", ("en",))
        self.github = GitHub()
        patcher = mock.patch.object(staff_jobs, "_github", side_effect=self.github)
        patcher.start()
        self.addCleanup(patcher.stop)

    def post(self, **body):
        return self.admin.post("/api/admin/jobs/bulk/", body, format="json")

    def test_dry_run_plans_without_filing(self):
        r = self.post(languages=["es", "fr"], books=["EZK", "GEN", "LEV", "exo"], dry_run=True)
        self.assertEqual(r.status_code, 200, r.content)
        data = r.json()
        # Bible order; Ezekiel's Spanish is already asked for, so only French;
        # Leviticus isn't drafted in English yet.
        self.assertEqual(data["plan"], [{"book": "GEN", "languages": ["es"]},
                                        {"book": "EXO", "languages": ["es", "fr"]},
                                        {"book": "EZK", "languages": ["fr"]}])
        self.assertEqual(data["skipped"], [{"book": "LEV", "reason": "not drafted in English yet"}])
        self.assertEqual(self.github.filed, [])
        self.assertFalse(AdminAction.objects.exists())

    def test_files_and_logs_each_job(self):
        r = self.post(languages=["es"], books=["GEN", "EXO", "EZK"], note="Pentateuch first")
        self.assertEqual(r.status_code, 201, r.content)
        data = r.json()
        self.assertEqual([(j["book"], j["number"]) for j in data["filed"]], [("GEN", 100), ("EXO", 101)])
        self.assertEqual(data["skipped"], [{"book": "EZK", "reason": "already asked for in #5"}])
        self.assertEqual(self.github.filed[0]["title"], "Draft Genesis in Spanish")
        self.assertIn("Pentateuch first", self.github.filed[0]["body"])
        self.assertIn('<!-- drafting-job {"book": "EXO", "languages": ["es"]} -->', self.github.filed[1]["body"])
        actions = AdminAction.objects.filter(action="job.file").order_by("id")
        self.assertEqual([a.target for a in actions], ["#100 GEN", "#101 EXO"])
        self.assertTrue(actions[0].detail["bulk"])

    def test_skips_what_is_drafted(self):
        data = self.post(languages=["fr"], books=["GEN"], dry_run=True).json()
        self.assertEqual((data["plan"], data["skipped"]), ([], [{"book": "GEN", "reason": "already drafted"}]))

    def test_caps_one_request(self):
        with mock.patch.object(staff_jobs, "BULK_LIMIT", 2):
            data = self.post(languages=["en"], testament="ot").json()
        self.assertEqual([j["book"] for j in data["filed"]], ["LEV", "NUM"])
        self.assertEqual(data["remaining"], 39 - 3 - 2)   # Genesis, Exodus and Ezekiel are drafted

    def test_github_failing_midway_says_what_was_filed(self):
        self.github.fail_after = 1
        r = self.post(languages=["es"], books=["GEN", "EXO"])
        data = r.json()
        self.assertEqual(r.status_code, 201)
        self.assertEqual([j["book"] for j in data["filed"]], ["GEN"])
        self.assertEqual(data["not_filed"], [{"book": "EXO", "languages": ["es"]}])
        self.assertIn("1 filed, 1 not", data["error"])
        self.github.fail_after = 0
        r = self.post(languages=["fr"], books=["EXO"])
        self.assertEqual((r.status_code, r.json()["code"]), (503, "github"))

    def test_checks_the_request(self):
        self.assertEqual(self.post(languages=[], testament="ot").status_code, 400)
        self.assertEqual(self.post(languages=["es"]).json()["code"], "invalid_testament")
        self.assertEqual(self.post(languages=["es"], books=["XYZ"]).json()["code"], "invalid_book")
        with override_settings(OWB_GITHUB_TOKEN=""):
            self.assertEqual(self.post(languages=["es"], testament="ot").status_code, 503)
            self.assertEqual(self.post(languages=["es"], testament="ot", dry_run=True).status_code, 200)

    def test_only_the_jobs_area(self):
        editor = client_for(account("ed@example.org", (K.EDITOR,)))
        r = editor.post("/api/admin/jobs/bulk/", {"languages": ["es"], "testament": "ot"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_board(self):
        board = self.admin.get("/api/admin/jobs/").json()["board"]
        self.assertEqual(board["GEN"]["fr"]["state"], "drafted")
        self.assertEqual(board["EZK"]["es"], {"state": "pr", "url": PULL["html_url"], "number": 9})
        self.assertNotIn("LEV", board)
        json.dumps(board)
