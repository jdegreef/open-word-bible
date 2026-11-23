"""Only our sites may use the API (accounts.cors.ApiOriginGate), and its
open reads are rate-limited by the address Render saw (config/throttles.py)."""
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from api import views
from config.throttles import ApiThrottle, ReadThrottle
from logia import views as logia

SITE = "https://openwordbible.org"
LOGIA = "https://logia.faith"
API = "https://api.openwordbible.org"


@override_settings(API_ORIGIN_GATE=True, CORS_ALLOWED_ORIGINS=[SITE, LOGIA], OWB_API_URL=API,
                   API_KEYS=["k-ours"])
class ApiGateTest(TestCase):
    def setUp(self):
        cache.clear()

    def get(self, path, **headers):
        return APIClient().get(path, **headers)

    def test_our_sites_are_let_in(self):
        for origin in (SITE, LOGIA):
            r = self.get("/api/logia/likes?chapter=JHN.1", HTTP_ORIGIN=origin)
            self.assertEqual(r.status_code, 200, origin)
            self.assertEqual(r["Access-Control-Allow-Origin"], origin)

    def test_another_site_is_refused(self):
        r = self.get("/api/logia/likes?chapter=JHN.1", HTTP_ORIGIN="https://example.com")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.json()["code"], "forbidden_origin")
        self.assertNotIn("Access-Control-Allow-Origin", r)

    def test_another_site_cannot_post(self):
        # A form or text/plain POST needs no preflight; the gate stops it
        # before the view, so no email is sent.
        r = APIClient().post("/api/auth/link", "email=a@example.org", content_type="text/plain",
                             HTTP_ORIGIN="https://example.com")
        self.assertEqual(r.status_code, 403)

    def test_another_sites_preflight_is_refused(self):
        r = APIClient().options("/api/me", HTTP_ORIGIN="https://example.com",
                                HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET")
        self.assertEqual(r.status_code, 403)

    def test_our_preflight_is_answered(self):
        r = APIClient().options("/api/me", HTTP_ORIGIN=LOGIA, HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET")
        self.assertEqual(r.status_code, 204)

    def test_a_program_without_origin_is_refused(self):
        self.assertEqual(self.get("/api/logia/likes?chapter=JHN.1").status_code, 403)
        self.assertEqual(self.get("/api/editions/").status_code, 403)

    def test_our_key_lets_a_program_in(self):
        r = self.get("/api/logia/likes?chapter=JHN.1", HTTP_X_API_KEY="k-ours")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.get("/api/logia/likes?chapter=JHN.1", HTTP_X_API_KEY="k-other").status_code, 403)

    @override_settings(API_KEYS=[])
    def test_an_empty_key_is_no_key(self):
        self.assertEqual(self.get("/api/logia/likes?chapter=JHN.1", HTTP_X_API_KEY="").status_code, 403)

    def test_the_apis_own_pages_are_let_in(self):
        r = APIClient().post("/api/email/unsubscribe?t=bad", HTTP_ORIGIN=API)
        self.assertNotEqual(r.status_code, 403)

    def test_links_and_redirects_stay_open(self):
        # An email's unsubscribe link, a mail app's one-click POST, and
        # Google sending the reader back come with no Origin.
        for r in (self.get("/api/email/unsubscribe?t=bad"),
                  APIClient().post("/api/email/unsubscribe?t=bad"),
                  self.get("/api/auth/google/start?lang=en"),
                  self.get("/api/auth/google/callback?state=x&code=y")):
            self.assertNotEqual(r.status_code, 403, r.content)

    def test_outside_the_api_is_untouched(self):
        self.assertEqual(self.get("/healthz").status_code, 200)

    @override_settings(API_ORIGIN_GATE=False)
    def test_off_lets_everyone_in(self):
        self.assertEqual(self.get("/api/logia/likes?chapter=JHN.1").status_code, 200)


class ThrottleTest(TestCase):
    def test_open_reads_are_throttled(self):
        for view in (views.editions, views.chapter_text, views.passages, logia.like_counts):
            self.assertIn(ReadThrottle, view.cls.throttle_classes, view)
        self.assertTrue(issubclass(views.SearchThrottle, ApiThrottle))

    def test_counted_by_the_address_render_saw(self):
        request = APIClient().get("/").wsgi_request
        request.META["HTTP_X_FORWARDED_FOR"] = "1.2.3.4, 9.9.9.9"
        self.assertEqual(ReadThrottle().get_ident(request), "9.9.9.9")

    def test_too_many_reads_are_refused(self):
        cache.clear()
        with mock.patch.object(ReadThrottle, "THROTTLE_RATES", {"read": "2/min"}):
            codes = [APIClient().get("/api/logia/likes?chapter=JHN.1").status_code for _ in range(3)]
        cache.clear()
        self.assertEqual(codes, [200, 200, 429])
