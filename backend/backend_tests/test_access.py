"""Who may use the API (config/access.py): our sites' pages by Origin, our
own servers by key, nobody else."""
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings

from api.views import SearchThrottle

SITE = "https://openwordbible.org"


@override_settings(CORS_ALLOWED_ORIGINS=[SITE, "https://logia.faith"], OWB_API_KEYS=["k1", "k2"],
                   OWB_API_REQUIRE_ORIGIN=True)
class ApiAccessTest(TestCase):
    def test_our_sites_pages_may_call_the_api(self):
        for origin in (SITE, "https://logia.faith"):
            r = self.client.get("/api/auth/methods", HTTP_ORIGIN=origin)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r["Access-Control-Allow-Origin"], origin)

    def test_other_websites_and_bare_scripts_are_refused(self):
        r = self.client.get("/api/auth/methods", HTTP_ORIGIN="https://evil.example")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.json()["code"], "origin_not_allowed")
        self.assertNotIn("Access-Control-Allow-Origin", r)
        self.assertEqual(self.client.get("/api/auth/methods").status_code, 403)
        self.assertEqual(self.client.get("/api/search/", {"q": "light"}).status_code, 403)
        self.assertEqual(self.client.post("/api/messages", {}, content_type="application/json").status_code, 403)

    def test_the_site_can_read_a_refusal(self):
        r = self.client.get("/api/editions/", HTTP_ORIGIN=SITE)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r["Access-Control-Allow-Origin"], SITE)

    def test_preflights_are_still_answered(self):
        r = self.client.options("/api/messages", HTTP_ORIGIN=SITE, HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST")
        self.assertEqual(r.status_code, 204)

    def test_records_and_texts_need_a_key_even_from_the_site(self):
        for path in ("/api/editions/", "/api/text/JHN/1/", "/api/passages/JHN/1/"):
            for headers in ({}, {"HTTP_ORIGIN": SITE}, {"HTTP_X_OWB_KEY": "wrong"}, {"HTTP_X_OWB_KEY": ""}):
                r = self.client.get(path, **headers)
                self.assertEqual(r.status_code, 403, (path, headers))
                self.assertEqual(r.json()["code"], "key_required")
        self.assertEqual(self.client.get("/api/editions/", HTTP_X_OWB_KEY="k2").status_code, 200)

    def test_a_key_works_without_an_origin(self):
        self.assertEqual(self.client.get("/api/auth/methods", HTTP_X_OWB_KEY="k1").status_code, 200)

    @override_settings(OWB_API_KEYS=[])
    def test_no_keys_set_means_no_way_in(self):
        self.assertEqual(self.client.get("/api/editions/", HTTP_X_OWB_KEY="").status_code, 403)

    def test_addresses_a_browser_opens_itself_stay_open(self):
        # No Origin on these: a link in an email, a redirect to Google and back.
        self.assertNotEqual(self.client.get("/api/email/unsubscribe", {"t": "x"}).status_code, 403)
        self.assertNotEqual(self.client.get("/api/auth/google/callback").status_code, 403)
        self.assertNotEqual(self.client.get("/api/auth/google/start").status_code, 403)

    def test_the_rest_of_the_service_is_untouched(self):
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertNotEqual(self.client.get("/admin/login/").status_code, 403)

    @override_settings(OWB_API_REQUIRE_ORIGIN=False)
    def test_the_origin_rule_can_be_turned_off_but_not_the_key_rule(self):
        self.assertEqual(self.client.get("/api/auth/methods").status_code, 200)
        self.assertEqual(self.client.get("/api/editions/").status_code, 403)


@override_settings(CORS_ALLOWED_ORIGINS=[SITE])
class SearchThrottleTest(TestCase):
    def setUp(self):
        cache.clear()

    @mock.patch.object(SearchThrottle, "rate", "2/min", create=True)
    def test_a_made_up_forwarded_for_does_not_reset_the_limit(self):
        # Clients can put anything first in X-Forwarded-For; Render appends
        # the real address last, and that is what is counted.
        codes = [self.client.get("/api/search/", {"q": "light"}, HTTP_ORIGIN=SITE,
                                 HTTP_X_FORWARDED_FOR=f"10.0.0.{i}, 203.0.113.9").status_code
                 for i in range(3)]
        self.assertNotIn(429, codes[:2])
        self.assertEqual(codes[2], 429)
