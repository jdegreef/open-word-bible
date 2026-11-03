"""Logia: handing a signed-in reader to logia.faith, and saves and likes."""
from datetime import timedelta
from urllib.parse import unquote

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.auth import issue_token
from accounts.models import ApiToken
from logia.models import Handoff, Like, Saved

SITE = "https://openwordbible.org"
LOGIA = "https://logia.faith"


@override_settings(OWB_SITE_URL=SITE, CORS_ALLOWED_ORIGINS=[SITE, LOGIA], PARTNER_SITES={"logia": LOGIA})
class LogiaTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="reader@example.org", email="reader@example.org")
        _, self.owb_token = issue_token(self.user, "OWB browser")
        self.client = APIClient()

    def owb(self):
        c = APIClient(HTTP_ORIGIN=SITE)
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {self.owb_token}")
        return c

    def handoff(self, redirect="/jhn/1/#v14"):
        r = self.owb().post("/api/auth/handoff", {"site": "logia", "redirect": redirect}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        url = r.json()["url"]
        self.assertTrue(url.startswith(f"{LOGIA}/signed-in/#code="), url)
        fragment = url.split("#", 1)[1]
        parts = dict(p.split("=", 1) for p in fragment.split("&"))
        return parts["code"], unquote(parts["to"])

    def redeem(self, code, origin=LOGIA):
        return APIClient(HTTP_ORIGIN=origin).post("/api/auth/handoff/redeem", {"code": code}, format="json")

    def logia(self):
        code, _ = self.handoff()
        token = self.redeem(code).json()["token"]
        c = APIClient(HTTP_ORIGIN=LOGIA)
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return c

    # --- The hand-off ---

    def test_a_handoff_gives_logia_its_own_token_once(self):
        code, to = self.handoff("/jhn/1/")
        self.assertEqual(to, "/jhn/1/")
        self.assertFalse(Handoff.objects.filter(code_hash=code).exists())   # only the hash is kept
        r = self.redeem(code)
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()["user"]["email"], "reader@example.org")
        self.assertNotEqual(r.json()["token"], self.owb_token)
        self.assertTrue(ApiToken.objects.filter(user=self.user, label__startswith="Logia").exists())
        self.assertEqual(self.redeem(code).status_code, 400)                 # it works once

    def test_a_code_expires(self):
        code, _ = self.handoff()
        Handoff.objects.update(created_at=timezone.now() - timedelta(minutes=6))
        self.assertEqual(self.redeem(code).status_code, 400)

    def test_only_logia_may_redeem_a_logia_code(self):
        code, _ = self.handoff()
        self.assertEqual(self.redeem(code, origin="https://evil.example").status_code, 403)
        self.assertEqual(self.redeem(code, origin=SITE).status_code, 403)
        self.assertEqual(self.redeem(code).status_code, 200)

    def test_a_handoff_needs_a_signed_in_reader_on_open_word_bible(self):
        r = APIClient(HTTP_ORIGIN=SITE).post("/api/auth/handoff", {"site": "logia"}, format="json")
        self.assertEqual(r.status_code, 401)
        # Logia itself cannot make one, even with a token.
        c = self.logia()
        self.assertEqual(c.post("/api/auth/handoff", {"site": "logia"}, format="json").status_code, 403)

    def test_only_known_sites_and_paths(self):
        r = self.owb().post("/api/auth/handoff", {"site": "elsewhere"}, format="json")
        self.assertEqual(r.status_code, 400)
        _, to = self.handoff("//evil.example/")
        self.assertEqual(to, "/")
        _, to = self.handoff("https://evil.example/")
        self.assertEqual(to, "/")

    def test_logia_cannot_sign_in_with_a_password(self):
        r = APIClient(HTTP_ORIGIN=LOGIA).post("/api/auth/sign-in",
                                               {"email": "reader@example.org", "password": "x"}, format="json")
        self.assertEqual(r.status_code, 403)
        r = APIClient(HTTP_ORIGIN=LOGIA).post("/api/auth/link", {"email": "reader@example.org"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_logia_may_call_the_api(self):
        r = APIClient(HTTP_ORIGIN=LOGIA).get("/api/logia/likes?chapter=JHN.1")
        self.assertEqual(r["Access-Control-Allow-Origin"], LOGIA)

    # --- Saves and likes ---

    def test_save_and_unsave(self):
        c = self.logia()
        r = c.put("/api/logia/saved/calvin.JHN.1.14")
        self.assertEqual(r.status_code, 200, r.content)
        c.put("/api/logia/saved/calvin.JHN.1.14")                          # twice is still once
        self.assertEqual(Saved.objects.get(user=self.user).chapter, "JHN.1")
        me = c.get("/api/logia/me").json()
        self.assertEqual([s["key"] for s in me["saved"]], ["calvin.JHN.1.14"])
        self.assertEqual(c.delete("/api/logia/saved/calvin.JHN.1.14").status_code, 204)
        self.assertEqual(c.get("/api/logia/me").json()["saved"], [])

    def test_likes_are_counted_publicly(self):
        self.logia().put("/api/logia/likes/henry.JHN.1.1")
        other = get_user_model().objects.create(username="b@example.org")
        Like.objects.create(user=other, key="henry.JHN.1.1", chapter="JHN.1")
        Like.objects.create(user=other, key="ryle.JHN.2.1", chapter="JHN.2")
        r = APIClient().get("/api/logia/likes?chapter=JHN.1")
        self.assertEqual(r.json(), {"counts": {"henry.JHN.1.1": 2}})
        self.assertEqual(APIClient().get("/api/logia/likes?chapter=nope").status_code, 400)

    def test_marks_need_an_account_and_a_real_key(self):
        self.assertEqual(APIClient().put("/api/logia/likes/henry.JHN.1.1").status_code, 401)
        c = self.logia()
        for bad in ("henry", "henry.JHN.1", "Henry.JHN.1.1", "henry.jhn.1.1", "x" * 41 + ".JHN.1.1"):
            self.assertEqual(c.put(f"/api/logia/likes/{bad}").status_code, 400, bad)

    def test_deleting_the_account_deletes_its_marks(self):
        c = self.logia()
        c.put("/api/logia/saved/calvin.JHN.1.14")
        c.put("/api/logia/likes/calvin.JHN.1.14")
        self.user.delete()
        self.assertFalse(Saved.objects.exists() or Like.objects.exists() or Handoff.objects.exists())
