"""Deploy and operations: loading missing texts, the statement timeout and
the Sentry scrubber. Nothing here fetches sources or talks to Sentry."""
import contextlib
import io
import subprocess
import wsgiref.util
from unittest import mock

import psycopg

from django.conf import settings
from django.core.management import CommandError, call_command
from django.core.handlers.wsgi import WSGIHandler
from django.db import connection
from django.test import SimpleTestCase, TestCase

from config import sentry
from config.settings import database_options, statement_timeout_ms
from owb.sources import LOCK
from texts.management.commands.import_texts import Command as ImportTexts
from texts.models import Edition, Verse

ALL = ["sblgnt", "wlc", "bsb", "web", "asv", "kjv", "ylt", "rv1909"]


def edition(code, source, commit=None, verses=True):
    e = Edition.objects.create(code=code, name=code, language="eng", kind="reference",
                               licence="Public domain", source=source,
                               source_commit=commit or LOCK[source]["commit"])
    if verses:
        Verse.objects.create(edition=e, book="GEN", chapter=1, verse=1, text="In the beginning")
    return e


class MissingTextsTests(TestCase):
    def test_all_codes(self):
        self.assertEqual(ImportTexts.all_codes(), ALL)

    def test_nothing_loaded(self):
        self.assertEqual(ImportTexts.missing_codes(), ALL)

    def test_loaded_at_pinned_commit(self):
        edition("sblgnt", "sblgnt")
        edition("bsb", "open-bibles")
        self.assertEqual(ImportTexts.missing_codes(), ["wlc", "web", "asv", "kjv", "ylt", "rv1909"])

    def test_empty_or_out_of_date_editions_are_missing(self):
        edition("sblgnt", "sblgnt", commit="0" * 40)
        edition("wlc", "macula-hebrew", verses=False)
        self.assertEqual(ImportTexts.missing_codes(), ALL)

    def run_missing(self, results=None):
        out = io.StringIO()
        calls = []

        def run(cmd, *args, **kwargs):
            calls.append(cmd[1:])
            code = (results or {}).get(cmd[-1], 0)
            return subprocess.CompletedProcess(cmd, code)

        with mock.patch("subprocess.run", side_effect=run), self.assertLogs(
                "texts.management.commands.import_texts", "ERROR") if results else contextlib.nullcontext():
            call_command("import_texts", "--missing", stdout=out)
        return calls, out.getvalue()

    def test_nothing_to_do_fetches_nothing(self):
        for code in ALL:
            edition(code, ImportTexts.sources(code)[0])
        calls, out = self.run_missing()
        self.assertEqual(calls, [])
        self.assertIn("Every edition is loaded", out)

    def test_fetches_needed_sources_then_one_process_per_edition(self):
        edition("sblgnt", "sblgnt")
        for code in ["web", "asv", "kjv", "ylt", "rv1909"]:
            edition(code, "open-bibles")
        calls, _ = self.run_missing()
        fetch = str(settings.REPO_ROOT / "scripts" / "fetch_sources.py")
        manage = str(settings.BASE_DIR / "manage.py")
        self.assertEqual(calls, [
            [fetch, "macula-hebrew", "open-bibles"],
            [manage, "import_texts", "wlc"],
            [manage, "import_texts", "bsb"],
        ])

    def test_failures_are_logged_not_raised(self):
        for code in ALL[1:]:
            edition(code, ImportTexts.sources(code)[0])
        calls, _ = self.run_missing({"sblgnt": 1})
        self.assertEqual([c[-1] for c in calls], ["macula-greek", "sblgnt"])

    def test_failed_fetch_imports_nothing(self):
        edition("sblgnt", "sblgnt")
        calls, _ = self.run_missing({"open-bibles": 1})
        self.assertEqual(len(calls), 1)

    def test_missing_with_editions_is_an_error(self):
        with self.assertRaisesMessage(CommandError, "not both"):
            call_command("import_texts", "wlc", "--missing")


class StatementTimeoutTests(TestCase):
    def test_web_server_has_a_limit(self):
        self.assertEqual(statement_timeout_ms(["/opt/render/.venv/bin/gunicorn"], {}), 15000)
        self.assertEqual(statement_timeout_ms(["manage.py", "runserver"], {}), 15000)
        self.assertEqual(statement_timeout_ms(["gunicorn"], {"DB_STATEMENT_TIMEOUT_MS": "5000"}), 5000)

    def test_management_commands_have_none(self):
        for command in ["migrate", "import_texts", "import_content", "shell", "test"]:
            self.assertEqual(statement_timeout_ms(["backend/manage.py", command],
                                                  {"DB_STATEMENT_TIMEOUT_MS": "5000"}), 0)
        with connection.cursor() as cursor:
            cursor.execute("SHOW statement_timeout")
            self.assertEqual(cursor.fetchone()[0], "0")

    def test_postgres_applies_the_option(self):
        """A connection made as the web server makes them is cut off."""
        params = {**connection.get_connection_params(), **database_options(200)}
        with psycopg.connect(**params) as conn:
            self.assertEqual(conn.execute("SHOW statement_timeout").fetchone()[0], "200ms")
            with self.assertRaises(psycopg.errors.QueryCanceled):
                conn.execute("SELECT pg_sleep(2)")


class SentryScrubTests(SimpleTestCase):
    def test_event(self):
        event = {
            "request": {"url": "https://api.openwordbible.org/api/search/?q=light&lang=en",
                        "method": "GET", "query_string": "q=light&lang=en",
                        "cookies": {"sessionid": "x"}, "headers": {"Authorization": "Token x"},
                        "data": {"q": "light"}, "env": {"REMOTE_ADDR": "1.2.3.4"}},
            "extra": {"q": "light", "path": "/api/search/?q=light"},
            "logentry": {"message": "Failed: %s", "params": ["/api/search/?q=light"]},
            "breadcrumbs": {"values": [
                {"category": "query", "message": "SELECT ... WHERE text @@ %s",
                 "data": {"params": ["light"]}},
                {"category": "httplib", "data": {"url": "https://x.org/a?q=light",
                                                 "http.query": "q=light", "q": "light"}},
                {"category": "django", "message": "Not Found: /api/search/?q=light"},
            ]},
        }
        clean = sentry.scrub_event(event)
        self.assertEqual(clean["request"], {"url": "https://api.openwordbible.org/api/search/",
                                            "method": "GET"})
        self.assertEqual(clean["extra"], {"path": "/api/search/"})
        self.assertEqual(clean["logentry"]["params"], ["/api/search/"])
        self.assertEqual(clean["breadcrumbs"]["values"], [
            {"category": "httplib", "data": {"url": "https://x.org/a"}},
            {"category": "django", "message": "Not Found: /api/search/"},
        ])
        self.assertNotIn("light", repr(clean))

    def test_breadcrumb(self):
        self.assertIsNone(sentry.scrub_breadcrumb({"category": "query", "message": "SELECT 1"}))
        self.assertEqual(sentry.scrub_breadcrumb({"message": "GET /api/search/?q=lamb", "data": {"q": "lamb"}}),
                         {"message": "GET /api/search/", "data": {}})

    def test_django_error_end_to_end(self):
        """A failing request reaches Sentry without its query, cookies or
        headers. Through the WSGI handler, as under gunicorn, since that is
        where Sentry reads the request."""
        import sentry_sdk

        sent = []

        class Transport(sentry_sdk.transport.Transport):
            def capture_envelope(self, envelope):
                sent.extend(item.payload.json for item in envelope.items if item.payload.json)

        sentry.init("https://key@sentry.invalid/1", "test", transport=Transport)
        environ = {"PATH_INFO": "/healthz", "QUERY_STRING": "q=light", "HTTP_HOST": "testserver",
                   "HTTP_COOKIE": "sessionid=abc", "HTTP_AUTHORIZATION": "Token secret"}
        wsgiref.util.setup_testing_defaults(environ)
        try:
            with mock.patch("api.views.connection") as conn, self.assertLogs("django.request"):
                conn.cursor.side_effect = RuntimeError("database down")
                WSGIHandler()(environ, lambda *args: None)
            sentry_sdk.flush()
        finally:
            sentry_sdk.init()   # no DSN: switch it off again
        errors = [e for e in sent if "exception" in e]
        self.assertEqual(errors[0]["exception"]["values"][0]["value"], "database down")
        self.assertEqual(errors[0]["request"], {"url": "http://testserver/healthz", "method": "GET"})
        for word in ("light", "abc", "secret"):
            self.assertNotIn(word, repr(sent))
