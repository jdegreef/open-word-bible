"""Alerts (staff/alerts.py): the super admins are emailed once for each
problem, again when it changes, and when an import or CI problem clears."""
import io
from datetime import timedelta
from unittest import mock

from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from backend_tests.test_admin import SITE, AdminTestCase, account
from feedback.models import ReaderMessage
from staff import jobs
from staff.models import AdminAction
from translation.models import ImportRun

GREEN = {"sha": "aaaaaaa", "url": "https://github.com/x/y/commit/a", "message": "Fine", "date": "2026-10-17T00:00:00Z",
         "checks": [{"name": "Backend", "status": "completed", "conclusion": "success", "url": "u"}]}


def ci(sha="bbbbbbb", conclusion="failure"):
    return {**GREEN, "sha": sha, "checks": [
        {"name": "Backend", "status": "completed", "conclusion": conclusion, "url": "u"},
        {"name": "Site", "status": "in_progress", "conclusion": None, "url": "u"}]}


def issue(number, hours, kind="drafting-job"):
    created = (timezone.now() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"number": number, "title": f"Job {number}", "html_url": f"https://github.com/x/y/issues/{number}",
            "state": "open", "created_at": created, "labels": [{"name": kind}], "assignees": []}


def github(issues):
    def fake(path, method="GET", body=None):
        return [] if path.startswith("pulls") else issues
    return fake


@override_settings(EMAIL_HOST="smtp.example.org", OWB_GITHUB_TOKEN="t")
class AlertsTest(AdminTestCase):
    def run_alerts(self, ci_status=GREEN, issues=()):
        out = io.StringIO()
        with mock.patch("staff.progress._ci_status", return_value=ci_status), \
                mock.patch("staff.jobs._github", side_effect=github(list(issues))):
            call_command("send_alerts", stdout=out, stderr=out)
        return out.getvalue()

    def sent(self):
        subjects = [m.subject for m in mail.outbox]
        mail.outbox.clear()
        return subjects

    def test_nothing_broken_sends_nothing(self):
        ImportRun.objects.create().finish()
        self.assertIn("0 alert(s) sent", self.run_alerts())
        self.assertEqual(self.sent(), [])

    def test_failed_import_once_then_resolved(self):
        ImportRun.objects.create().finish(error="CommandError: content/JHN/JHN.1.json: 2 error(s)")
        self.run_alerts()
        self.assertIn("2 error(s)", mail.outbox[0].body)
        self.assertIn(f"{SITE}/admin/#health", mail.outbox[0].body)
        self.assertEqual(self.sent(), ["Open Word Bible: The last content import failed"])
        self.run_alerts()   # the same run: nothing new
        self.assertEqual(self.sent(), [])
        ImportRun.objects.create().finish(error="CommandError: another")   # a new failing run: again
        self.run_alerts()
        self.assertEqual(len(self.sent()), 1)
        ImportRun.objects.create().finish()
        self.run_alerts()
        self.assertEqual(self.sent(), ["Open Word Bible: resolved: The last content import failed"])
        self.run_alerts()
        self.assertEqual(self.sent(), [])

    def test_skipped_files_and_a_running_import(self):
        run = ImportRun.objects.create(skipped=["content/GEN/GEN.1.json: the wlc text is not in the database"])
        self.run_alerts()   # still running: not known yet
        self.assertEqual(self.sent(), [])
        run.finish()
        self.run_alerts()
        self.assertEqual(self.sent(), ["Open Word Bible: The last content import left files for later"])

    def test_ci_failing_on_main(self):
        self.run_alerts(ci_status=ci())
        [m] = mail.outbox
        self.assertEqual(m.subject, "Open Word Bible: CI is failing on main")
        self.assertIn("Backend failed", m.body)
        self.assertNotIn("Site", m.body)   # still running
        self.assertIn(f"{SITE}/admin/#health", m.body)
        self.assertEqual(sorted(x.to[0] for x in mail.outbox), ["boss@example.org"])
        self.sent()
        self.run_alerts(ci_status=ci())
        self.assertEqual(self.sent(), [])
        self.run_alerts(ci_status=ci(sha="ccccccc", conclusion="timed_out"))   # a new failing commit
        self.assertEqual(len(self.sent()), 1)
        self.run_alerts(ci_status=GREEN)
        self.assertEqual(self.sent(), ["Open Word Bible: resolved: CI is failing on main"])

    def test_github_out_of_reach_is_neither_a_problem_nor_resolved(self):
        self.run_alerts(ci_status=ci())
        self.sent()
        out = io.StringIO()
        with mock.patch("staff.progress._ci_status", return_value=None), \
                mock.patch("staff.jobs._github", side_effect=jobs.GitHubError("down")):
            call_command("send_alerts", stdout=out)
        self.assertEqual(self.sent(), [])
        self.assertIn("0 alert(s) sent", out.getvalue())

    def test_stalled_jobs_alerted_when_one_is_new(self):
        self.run_alerts(issues=[issue(7, 30), issue(8, 2)])
        [m] = mail.outbox
        self.assertEqual(m.subject, "Open Word Bible: 1 job has stalled")
        self.assertIn("Drafting job #7", m.body)
        self.assertNotIn("#8", m.body)
        self.assertIn(f"{SITE}/admin/#work", m.body)
        self.sent()
        self.run_alerts(issues=[issue(7, 31)])
        self.assertEqual(self.sent(), [])
        self.run_alerts(issues=[issue(7, 32), issue(9, 40, "fix-request")])
        self.assertEqual(self.sent(), ["Open Word Bible: 2 jobs have stalled"])

    def test_reader_messages_waiting(self):
        reader = account("reader@example.org")
        old = ReaderMessage.objects.create(user=reader, kind="question", verse="JHN.1.1", language="en", text="?")
        ReaderMessage.objects.filter(id=old.id).update(created_at=timezone.now() - timedelta(days=4))
        ReaderMessage.objects.create(user=reader, kind="question", verse="JHN.1.2", language="en", text="?")
        self.run_alerts()
        self.assertEqual(self.sent(), ["Open Word Bible: 1 reader message has waited more than 3 days"])
        self.run_alerts()
        self.assertEqual(self.sent(), [])

    def test_super_admins_from_the_environment_too(self):
        account("ed@example.org", ("editor",))
        ImportRun.objects.create().finish(error="boom")
        with self.settings(OWB_SUPER_ADMIN_EMAILS=["owner@example.org"]):
            self.run_alerts()
        self.assertEqual(sorted(m.to[0] for m in mail.outbox), ["boss@example.org", "owner@example.org"])
        action = AdminAction.objects.get(action="alert.sent")
        self.assertEqual((action.detail["kind"], action.detail["recipients"]), ("import", 2))

    @override_settings(EMAIL_HOST="")
    def test_no_email_server_sends_and_logs_nothing(self):
        ImportRun.objects.create().finish(error="boom")
        out = self.run_alerts()
        self.assertIn("No EMAIL_HOST; not sent: Open Word Bible: The last content import failed", out)
        self.assertEqual(mail.outbox, [])
        self.assertFalse(AdminAction.objects.filter(action="alert.sent").exists())

    def test_never_fails(self):
        out = io.StringIO()
        with mock.patch("staff.alerts.send", side_effect=RuntimeError("database gone")):
            call_command("send_alerts", stdout=out, stderr=out)
        self.assertIn("send_alerts failed: RuntimeError: database gone", out.getvalue())

    def test_dry_run(self):
        ImportRun.objects.create().finish(error="boom")
        with mock.patch("staff.progress._ci_status", return_value=GREEN):
            out = io.StringIO()
            call_command("send_alerts", "--dry-run", stdout=out)
        self.assertIn("Would send: Open Word Bible: The last content import failed", out.getvalue())
        self.assertEqual(mail.outbox, [])

    def test_health_lists_the_alerts(self):
        ImportRun.objects.create().finish(error="boom")
        with mock.patch("staff.progress._ci_status", return_value=ci()):
            before = {a["kind"]: a for a in self.admin.get("/api/admin/health/").json()["alerts"]}
            self.assertIsNone(before["import"]["emailed_at"])
            self.assertEqual(before["ci"]["href"], "#health")
        self.run_alerts(ci_status=ci())
        with mock.patch("staff.progress._ci_status", return_value=ci()):
            after = {a["kind"]: a for a in self.admin.get("/api/admin/health/").json()["alerts"]}
        self.assertTrue(after["import"]["emailed_at"])
        self.assertTrue(after["ci"]["emailed_at"])
