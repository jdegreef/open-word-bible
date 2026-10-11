"""Accounts: passwords, email links, Google, API tokens, roles and CORS."""
import io
import json
import re
from datetime import timedelta
from unittest import mock
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import CommandError, call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.auth import sync_super_admin
from accounts import google
from accounts.models import ApiToken, FailedSignIn, Role, SignInLink
from translation.models import ReviewEvent

SITE = "https://openwordbible.org"


@override_settings(OWB_SITE_URL=SITE, CORS_ALLOWED_ORIGINS=[SITE],
                   OWB_SUPER_ADMIN_EMAILS=["boss@example.org"])
class SignInTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def ask(self, email="reader@example.org", **extra):
        return self.client.post("/api/auth/link", {"email": email}, format="json", **extra)

    def link_secret(self, page="login"):
        body = mail.outbox[-1].body
        return re.search(re.escape(SITE) + rf"(?:/[a-z]{{2}})?/{page}/(?:\?redirect=[^#\s]+)?#token=([\w-]+)", body)[1]

    def sign_in(self, email="reader@example.org"):
        self.assertEqual(self.ask(email).status_code, 202)
        response = self.client.post("/api/auth/verify", {"token": self.link_secret()}, format="json")
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_a_link_signs_in_once_and_creates_the_account(self):
        data = self.sign_in("Reader@Example.org ")
        self.assertEqual(data["user"]["email"], "reader@example.org")
        self.assertEqual(data["user"]["roles"], [])
        self.assertTrue(get_user_model().objects.filter(username="reader@example.org").exists())
        # The secret is stored only as a hash, and works once.
        secret = self.link_secret()
        self.assertFalse(SignInLink.objects.filter(token_hash=secret).exists())
        again = self.client.post("/api/auth/verify", {"token": secret}, format="json")
        self.assertEqual(again.status_code, 400)

    def test_an_expired_link_does_not_sign_in(self):
        self.ask()
        SignInLink.objects.update(created_at=timezone.now() - timedelta(minutes=21))
        response = self.client.post("/api/auth/verify", {"token": self.link_secret()}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_bad_email_is_rejected_and_requests_are_rate_limited(self):
        self.assertEqual(self.ask("not an email").status_code, 400)
        for _ in range(5):
            self.assertEqual(self.ask().status_code, 202)
        self.assertEqual(self.ask().status_code, 429)
        self.assertEqual(len(mail.outbox), 5)

    def test_token_reads_and_updates_the_account_and_signs_out(self):
        token = self.sign_in()["token"]
        self.assertFalse(ApiToken.objects.filter(key_hash=token).exists())
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(self.client.get("/api/me").json()["email"], "reader@example.org")
        r = self.client.patch("/api/me", {"display_name": "Lydia"}, format="json")
        self.assertEqual(r.json()["display_name"], "Lydia")
        self.assertEqual(self.client.post("/api/auth/sign-out").status_code, 204)
        self.assertEqual(self.client.get("/api/me").status_code, 401)

    def test_a_wrong_token_reads_as_anonymous_but_cannot_see_an_account(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer nonsense")
        self.assertEqual(self.client.get("/api/editions/").status_code, 200)
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        # ...and does not get in the way of signing in again.
        self.assertEqual(self.ask().status_code, 202)
        r = self.client.post("/api/auth/verify", {"token": self.link_secret()}, format="json")
        self.assertEqual(r.status_code, 200)

    def test_an_idle_token_signs_out(self):
        token = self.sign_in()["token"]
        ApiToken.objects.update(created_at=timezone.now() - timedelta(days=200), last_used_at=None)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        self.assertFalse(ApiToken.objects.exists())

    def test_redeeming_one_link_retires_the_others(self):
        self.ask()
        first = self.link_secret()
        self.sign_in()
        r = self.client.post("/api/auth/verify", {"token": first}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_only_json_from_the_site_can_ask_for_a_link(self):
        form = self.client.post("/api/auth/link", {"email": "victim@example.org"})
        self.assertEqual(form.status_code, 415)
        self.assertEqual(self.ask(HTTP_ORIGIN="https://evil.example").status_code, 403)
        self.assertEqual(self.ask(HTTP_ORIGIN=SITE).status_code, 202)

    def test_the_network_limit_uses_the_address_render_saw(self):
        # Clients can put anything first in X-Forwarded-For; Render appends
        # the real address last.
        for i in range(20):
            r = self.ask(f"r{i}@example.org", HTTP_X_FORWARDED_FOR=f"10.0.0.{i}, 203.0.113.9")
            self.assertEqual(r.status_code, 202)
        r = self.ask("r99@example.org", HTTP_X_FORWARDED_FOR="10.9.9.9, 203.0.113.9")
        self.assertEqual(r.status_code, 429)
        # Junk in the header is ignored, not a 500.
        self.assertEqual(self.ask("junk@example.org", HTTP_X_FORWARDED_FOR="not an ip").status_code, 202)

    def test_long_and_international_addresses(self):
        self.assertEqual(self.ask("a" * 140 + "@example.org").status_code, 400)
        self.assertEqual(self.ask("Ana@Bücher.example").status_code, 202)
        self.assertEqual(SignInLink.objects.latest("created_at").email, "ana@xn--bcher-kva.example")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend", DEBUG=False)
    def test_no_links_in_the_log_when_email_is_not_set_up(self):
        self.assertEqual(self.ask().status_code, 503)
        self.assertFalse(SignInLink.objects.exists())

    def test_listed_emails_become_super_admins(self):
        user = self.sign_in("boss@example.org")["user"]
        self.assertTrue(user["is_super_admin"])
        account = get_user_model().objects.get(username="boss@example.org")
        self.assertTrue(account.is_staff and account.is_superuser)
        self.assertFalse(self.sign_in("someone@example.org")["user"]["is_super_admin"])

    def test_super_admin_follows_the_sign_in_address_not_the_email_field(self):
        user = get_user_model().objects.create(username="other@example.org", email="boss@example.org")
        sync_super_admin(user)
        self.assertFalse(user.roles.exists())
        self.assertFalse(user.is_superuser)

    def test_cors_only_for_the_site_and_only_on_the_api(self):
        r = self.client.options("/api/auth/link", HTTP_ORIGIN=SITE,
                                HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST")
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r["Access-Control-Allow-Origin"], SITE)
        self.assertIn("Authorization", r["Access-Control-Allow-Headers"])
        other = self.client.get("/api/editions/", HTTP_ORIGIN="https://evil.example")
        self.assertNotIn("Access-Control-Allow-Origin", other)
        admin = self.client.get("/healthz", HTTP_ORIGIN=SITE)
        self.assertNotIn("Access-Control-Allow-Origin", admin)


GOOD = "a long enough password"


@override_settings(OWB_SITE_URL=SITE, CORS_ALLOWED_ORIGINS=[SITE], OWB_SUPER_ADMIN_EMAILS=[])
class PasswordTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def post(self, path, data, **extra):
        return self.client.post(path, data, format="json", **extra)

    def link(self, page="login"):
        return re.search(re.escape(SITE) + rf"(?:/[a-z]{{2}})?/{page}/(?:\?redirect=([^#\s]+))?#token=([\w-]+)",
                         mail.outbox[-1].body)

    def sign_up(self, email="new@example.org", password=GOOD, **data):
        r = self.post("/api/auth/sign-up", {"email": email, "password": password, **data})
        self.assertEqual(r.status_code, 202, r.content)
        r = self.post("/api/auth/verify", {"token": self.link()[2]})
        self.assertEqual(r.status_code, 200, r.content)
        return r.json()

    def sign_in(self, email="new@example.org", password=GOOD):
        return self.post("/api/auth/sign-in", {"email": email, "password": password})

    def test_sign_up_confirms_the_address_before_any_account_exists(self):
        r = self.post("/api/auth/sign-up", {"email": "New@Example.org", "password": GOOD,
                                            "lang": "es", "redirect": "/es/jhn/3/"})
        self.assertEqual(r.status_code, 202)
        self.assertFalse(get_user_model().objects.exists())
        self.assertEqual(self.sign_in().status_code, 400)
        # The link goes back to the page in the reader's language.
        self.assertIn(f"{SITE}/es/login/?redirect=/es/jhn/3/#token=", mail.outbox[-1].body)
        self.assertNotIn(GOOD, mail.outbox[-1].body)
        user = self.post("/api/auth/verify", {"token": self.link()[2]}).json()["user"]
        self.assertTrue(user["has_password"])
        r = self.sign_in()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["user"]["email"], "new@example.org")

    def test_weak_passwords_are_refused_with_a_code(self):
        for password in ("short", "12345678901", "password123", "new@example.org"):
            r = self.post("/api/auth/sign-up", {"email": "new@example.org", "password": password})
            self.assertEqual(r.status_code, 400, password)
            self.assertEqual(r.json()["code"], "weak_password")
        self.assertEqual(mail.outbox, [])

    def test_sign_up_for_an_existing_account_looks_the_same_and_sets_the_password_once_confirmed(self):
        get_user_model().objects.create(username="new@example.org", email="new@example.org")
        r = self.post("/api/auth/sign-up", {"email": "new@example.org", "password": GOOD})
        self.assertEqual(r.status_code, 202)
        self.assertEqual(self.sign_in().status_code, 400)
        self.post("/api/auth/verify", {"token": self.link()[2]})
        self.assertEqual(self.sign_in().status_code, 200)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_wrong_passwords_say_the_same_thing_and_are_limited(self):
        self.sign_up()
        unknown = self.sign_in("nobody@example.org")
        wrong = self.sign_in(password="not the password")
        self.assertEqual(unknown.json(), wrong.json())
        self.assertEqual(wrong.json()["code"], "invalid_credentials")
        for _ in range(9):
            self.sign_in(password="not the password")
        r = self.sign_in()
        self.assertEqual(r.status_code, 429)
        self.assertEqual(r.json()["code"], "rate_limited")
        FailedSignIn.objects.update(created_at=timezone.now() - timedelta(minutes=16))
        self.assertEqual(self.sign_in().status_code, 200)

    def test_an_account_from_a_link_has_no_password_to_guess(self):
        self.post("/api/auth/link", {"email": "new@example.org"})
        user = self.post("/api/auth/verify", {"token": self.link()[2]}).json()["user"]
        self.assertFalse(user["has_password"])
        self.assertEqual(self.sign_in(password="").status_code, 400)

    def test_reset_sets_a_new_password_and_signs_out_other_devices(self):
        old = self.sign_up()["token"]
        r = self.post("/api/auth/reset", {"email": "new@example.org", "lang": "fr"})
        self.assertEqual(r.status_code, 202)
        self.assertIn(f"{SITE}/fr/reset-password/#token=", mail.outbox[-1].body)
        secret = self.link("reset-password")[2]
        # A reset link does not sign in by itself, and a sign-in link cannot reset.
        self.assertEqual(self.post("/api/auth/verify", {"token": secret}).status_code, 400)
        r = self.post("/api/auth/reset/confirm", {"token": secret, "password": "short"})
        self.assertEqual(r.status_code, 400)
        r = self.post("/api/auth/reset/confirm", {"token": secret, "password": "another fine password"})
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self.sign_in().status_code, 400)
        self.assertEqual(self.sign_in(password="another fine password").status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {old}")
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        self.client.credentials()
        again = self.post("/api/auth/reset/confirm", {"token": secret, "password": "a third fine password"})
        self.assertEqual(again.json()["code"], "link_expired")

    def test_reset_for_an_unknown_address_looks_the_same_but_sends_nothing(self):
        r = self.post("/api/auth/reset", {"email": "nobody@example.org"})
        self.assertEqual(r.status_code, 202)
        self.assertEqual(mail.outbox, [])
        self.assertFalse(get_user_model().objects.exists())

    def test_redirects_stay_on_the_site(self):
        for bad in ("https://evil.example/", "//evil.example/", "/\\evil.example", "/a\nb", "jhn/3/"):
            self.post("/api/auth/link", {"email": "new@example.org", "redirect": bad})
            self.assertIsNone(self.link()[1], bad)
            mail.outbox.clear()
            SignInLink.objects.all().delete()

    def test_deleting_an_account(self):
        token = self.sign_up()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(self.client.delete("/api/me").status_code, 204)
        self.assertFalse(get_user_model().objects.exists())
        self.assertFalse(ApiToken.objects.exists())
        self.assertEqual(self.client.get("/api/me").status_code, 401)

    def test_an_account_with_review_history_is_kept(self):
        token = self.sign_up()["token"]
        user = get_user_model().objects.get()
        with mock.patch.object(ReviewEvent.objects, "filter") as events:
            events.return_value.exists.return_value = True
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
            r = self.client.delete("/api/me")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json()["code"], "has_reviews")
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())

    def test_methods(self):
        self.assertEqual(self.client.get("/api/auth/methods").json(),
                         {"password": True, "link": True, "google": False})


class FakeGoogle:
    """Google's token endpoint, answering with claims."""
    def __init__(self, claims):
        payload = json.dumps(claims).encode()
        import base64
        self.body = json.dumps({"id_token": "h." + base64.urlsafe_b64encode(payload).decode().rstrip("=") + ".s"})
        self.requests = []

    def __call__(self, request, timeout=None):
        self.requests.append(parse_qs(request.data.decode()))
        return io.BytesIO(self.body.encode())


@override_settings(OWB_SITE_URL=SITE, CORS_ALLOWED_ORIGINS=[SITE], OWB_SUPER_ADMIN_EMAILS=[],
                   GOOGLE_CLIENT_ID="client-id", GOOGLE_CLIENT_SECRET="client-secret")
class GoogleTest(TestCase):
    def claims(self, **extra):
        return {"aud": "client-id", "iss": "https://accounts.google.com", "exp": 9999999999,
                "email": "Lydia@Example.org", "email_verified": True, **extra}

    def round_trip(self, claims, state=None, redirect="/jhn/3/", lang="sw"):
        start = self.client.get("/api/auth/google/start", {"lang": lang, "redirect": redirect})
        self.assertEqual(start.status_code, 302)
        query = parse_qs(urlsplit(start["Location"]).query)
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertEqual(query["redirect_uri"], ["http://testserver/api/auth/google/callback"])
        fake = FakeGoogle(claims)
        with mock.patch("urllib.request.urlopen", fake):
            back = self.client.get("/api/auth/google/callback",
                                   {"code": "abc", "state": state or query["state"][0]})
        self.assertEqual(back.status_code, 302)
        return back["Location"], fake

    def test_google_signs_in_through_a_single_use_link(self):
        location, fake = self.round_trip(self.claims())
        self.assertTrue(location.startswith(f"{SITE}/sw/login/?redirect=/jhn/3/#google="), location)
        self.assertEqual(fake.requests[0]["client_secret"], ["client-secret"])
        self.assertIn("code_verifier", fake.requests[0])
        secret = location.split("#google=")[1]
        r = self.client.post("/api/auth/verify", {"token": secret}, content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["user"]["email"], "lydia@example.org")
        self.assertFalse(r.json()["user"]["has_password"])

    def test_a_forged_state_or_unverified_email_or_other_audience_is_refused(self):
        for claims, state in ((self.claims(), "forged"),
                              (self.claims(email_verified=False), None),
                              (self.claims(aud="someone-else"), None),
                              (self.claims(exp=1), None)):
            location, _ = self.round_trip(claims, state)
            self.assertTrue(location.endswith("#error=google_failed"), (claims, state, location))
        self.assertFalse(SignInLink.objects.exists())

    def test_a_bad_redirect_is_dropped(self):
        location, _ = self.round_trip(self.claims(), redirect="//evil.example/", lang="xx")
        self.assertTrue(location.startswith(f"{SITE}/login/#google="), location)

    @override_settings(GOOGLE_CLIENT_ID="")
    def test_without_keys_the_site_is_told(self):
        r = self.client.get("/api/auth/google/start")
        self.assertEqual(r["Location"], f"{SITE}/login/#error=google_unavailable")
        self.assertFalse(google.enabled())


class RoleTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="r@example.org", email="r@example.org")

    def test_each_role_takes_the_right_kind_of_language(self):
        Role.objects.create(user=self.user, kind="scholar_reviewer", language="grc")
        Role.objects.create(user=self.user, kind="language_reviewer", language="es")
        Role.objects.create(user=self.user, kind="language_reviewer", language="fr")
        Role.objects.create(user=self.user, kind="language_reviewer", language="sw")
        Role.objects.create(user=self.user, kind="editor")
        for kind, language in [("scholar_reviewer", "es"), ("language_reviewer", "grc"),
                               ("language_reviewer", "de"),
                               ("editor", "en"), ("scholar_reviewer", "")]:
            with self.assertRaises(IntegrityError, msg=(kind, language)), transaction.atomic():
                Role.objects.create(user=self.user, kind=kind, language=language)

    def test_grant_role_command(self):
        out = io.StringIO()
        call_command("grant_role", "New@Example.org", "language_reviewer", "es", stdout=out)
        user = get_user_model().objects.get(username="new@example.org")
        self.assertEqual([str(r) for r in user.roles.all()], ["Language reviewer (es)"])
        with self.assertRaises(CommandError):
            call_command("grant_role", "new@example.org", "scholar_reviewer", stdout=out)
        call_command("grant_role", "new@example.org", "language_reviewer", "es", "--remove", stdout=out)
        self.assertFalse(user.roles.exists())

    def test_grant_role_leaves_no_account_behind_on_a_mistake(self):
        out = io.StringIO()
        call_command("grant_role", "typo@example.org", "editor", "--remove", stdout=out)
        with self.assertRaises(CommandError):
            call_command("grant_role", "typo@example.org", "scholar_reviewer", "es", stdout=out)
        with self.assertRaises(CommandError):
            call_command("grant_role", "not-an-email", "editor", stdout=out)
        self.assertFalse(get_user_model().objects.filter(username__in=["typo@example.org", "not-an-email"]).exists())
