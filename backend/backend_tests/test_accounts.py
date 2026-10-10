"""Accounts: email sign-in links, API tokens, roles and CORS."""
import io
import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import CommandError, call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import ApiToken, Role, SignInLink

SITE = "https://openwordbible.org"


@override_settings(OWB_SITE_URL=SITE, CORS_ALLOWED_ORIGINS=[SITE],
                   OWB_SUPER_ADMIN_EMAILS=["boss@example.org"])
class SignInTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def ask(self, email="reader@example.org"):
        return self.client.post("/api/auth/link", {"email": email}, format="json")

    def link_secret(self):
        body = mail.outbox[-1].body
        return re.search(re.escape(SITE) + r"/account/#token=([\w-]+)", body)[1]

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

    def test_a_wrong_token_is_401_not_anonymous(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer nonsense")
        self.assertEqual(self.client.get("/api/editions/").status_code, 401)

    def test_listed_emails_become_super_admins(self):
        user = self.sign_in("boss@example.org")["user"]
        self.assertTrue(user["is_super_admin"])
        account = get_user_model().objects.get(username="boss@example.org")
        self.assertTrue(account.is_staff and account.is_superuser)
        self.assertFalse(self.sign_in("someone@example.org")["user"]["is_super_admin"])

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


class RoleTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="r@example.org", email="r@example.org")

    def test_each_role_takes_the_right_kind_of_language(self):
        Role.objects.create(user=self.user, kind="scholar_reviewer", language="grc")
        Role.objects.create(user=self.user, kind="language_reviewer", language="es")
        Role.objects.create(user=self.user, kind="editor")
        for kind, language in [("scholar_reviewer", "es"), ("language_reviewer", "grc"),
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
