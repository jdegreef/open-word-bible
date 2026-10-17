"""The API's speed: editions' stored verse counts, compressed answers and
Server-Timing."""
import gzip
import importlib
import json
from unittest import mock

from django.apps import apps
from django.http import JsonResponse
from django.test import RequestFactory, SimpleTestCase

from config.middleware import ApiGzipMiddleware
from texts.management.commands.import_texts import Command as ImportTexts
from texts.models import Edition, Verse

from .test_admin import SITE, AdminTestCase


class VerseCountTest(AdminTestCase):
    def test_import_texts_keeps_the_count_and_health_reads_it(self):
        ImportTexts().save("sblgnt", [("JHN", 1, 1, "a"), ("JHN", 1, 2, "b")], [])
        self.assertEqual(Edition.objects.get(code="sblgnt").verse_count, 2)
        ImportTexts().save("sblgnt", [("JHN", 1, 1, "a")], [])
        self.assertEqual(Edition.objects.get(code="sblgnt").verse_count, 1)
        with mock.patch("staff.progress._ci_status", return_value=None):
            editions = self.admin.get("/api/admin/health/").json()["editions"]
        self.assertEqual(editions[0]["verses"], 1)

    def test_migration_counts_verses_already_loaded(self):
        ImportTexts().save("sblgnt", [("JHN", 1, 1, "a"), ("JHN", 1, 2, "b")], [])
        Edition.objects.update(verse_count=0)
        migration = importlib.import_module("texts.migrations.0002_edition_verse_count")
        migration.count_verses(apps, None)
        self.assertEqual(Edition.objects.get(code="sblgnt").verse_count, Verse.objects.count())


class CompressionTest(AdminTestCase):
    def test_large_reads_are_gzipped_with_vary(self):
        r = self.admin.get("/api/admin/coverage/", HTTP_ACCEPT_ENCODING="gzip", HTTP_ORIGIN=SITE)
        self.assertEqual(r["Content-Encoding"], "gzip")
        self.assertIn("Accept-Encoding", r["Vary"])
        self.assertIn("Origin", r["Vary"])
        self.assertEqual(len(json.loads(gzip.decompress(r.content))["books"]), 66)

    def test_not_without_accept_encoding(self):
        r = self.admin.get("/api/admin/coverage/")
        self.assertFalse(r.has_header("Content-Encoding"))

    def test_server_timing(self):
        r = self.admin.get("/api/admin/coverage/", HTTP_ORIGIN=SITE)
        self.assertRegex(r["Server-Timing"], r'^db;dur=[\d.]+;desc="\d+ queries", app;dur=[\d.]+$')
        self.assertEqual(r["Timing-Allow-Origin"], SITE)
        self.assertFalse(self.client.get("/healthz").has_header("Server-Timing"))


class GzipScopeTest(SimpleTestCase):
    """Answers that may carry a token (POSTs, as sign-in is) are never
    compressed, nor small ones or anything outside /api/."""

    def response(self, method, path, size=4000):
        request = getattr(RequestFactory(), method)(path, HTTP_ACCEPT_ENCODING="gzip")
        return ApiGzipMiddleware(lambda r: JsonResponse({"token": "t", "pad": "x" * size}))(request)

    def test_scope(self):
        self.assertEqual(self.response("get", "/api/admin/coverage/")["Content-Encoding"], "gzip")
        self.assertFalse(self.response("post", "/api/auth/sign-in").has_header("Content-Encoding"))
        self.assertFalse(self.response("get", "/api/me", size=10).has_header("Content-Encoding"))
        self.assertFalse(self.response("get", "/admin/").has_header("Content-Encoding"))
