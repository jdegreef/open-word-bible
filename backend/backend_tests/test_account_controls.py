"""The account page's controls (accounts/controls.py), reading-plan emails
(accounts/reminders.py) and passkeys (accounts/passkeys.py)."""
import base64
import hashlib
import io
import json
import os
import re
from datetime import datetime, timezone as dt_timezone
from unittest import mock

import cbor2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from accounts import reminders
from accounts.controls import describe_agent, unsubscribe_url
from accounts.models import ApiToken, EmailPrefs, Passkey, PasskeyChallenge, ReaderState, SignInLink
from feedback.models import ReaderMessage

from .test_reading import device, signed_in

SITE = "https://openwordbible.org"


class DevicesTest(TestCase):
    def setUp(self):
        self.user, self.client = signed_in()
        ApiToken.objects.filter(user=self.user).update(
            label="Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/130.0 Safari/537.36 Edg/130.0")
        self.phone = device(self.user)

    def test_devices_are_listed_with_this_one_marked(self):
        out = self.client.get("/api/me/devices").json()
        self.assertEqual(len(out), 2)
        self.assertEqual([d["current"] for d in out].count(True), 1)
        self.assertIn("Edge on Windows", [d["label"] for d in out])

    def test_a_device_is_signed_out(self):
        other = [d for d in self.client.get("/api/me/devices").json() if not d["current"]][0]
        self.assertEqual(self.client.delete(f"/api/me/devices/{other['id']}").status_code, 204)
        self.assertEqual(self.phone.get("/api/me").status_code, 401)
        self.assertEqual(self.client.get("/api/me").status_code, 200)

    def test_sign_out_everywhere_else(self):
        self.assertEqual(self.client.post("/api/me/devices/sign-out-others").json(), {"signed_out": 1})
        self.assertEqual(self.phone.get("/api/me").status_code, 401)
        self.assertEqual(self.client.get("/api/me").status_code, 200)

    def test_another_readers_device_is_not_found(self):
        _, stranger = signed_in("other@example.org")
        theirs = stranger.get("/api/me/devices").json()[0]["id"]
        self.assertEqual(self.client.delete(f"/api/me/devices/{theirs}").status_code, 404)
        self.assertEqual(stranger.get("/api/me").status_code, 200)

    def test_browser_names(self):
        self.assertEqual(describe_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit Version/17.0 "
                                        "Mobile/15E148 Safari/604.1"), "Safari on iPhone")
        self.assertEqual(describe_agent("Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"),
                         "Firefox on Linux")
        self.assertEqual(describe_agent("curl/8.0"), "")


@override_settings(OWB_SITE_URL=SITE, DEBUG=True)
class ChangeEmailTest(TestCase):
    def setUp(self):
        self.user, self.client = signed_in("old@example.org")

    def secret(self):
        return re.search(r"/account/#email=([\w-]+)", mail.outbox[-1].body)[1]

    def test_the_new_address_confirms_the_change(self):
        r = self.client.post("/api/me/email", {"email": "New@Example.org"}, format="json")
        self.assertEqual(r.status_code, 202, r.content)
        self.assertEqual(mail.outbox[-1].to, ["new@example.org"])
        # Not changed until the link is used.
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "old@example.org")
        secret = self.secret()
        r = APIClient().post("/api/me/email/confirm", {"token": secret}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()["email"], "new@example.org")
        self.user.refresh_from_db()
        self.assertEqual((self.user.username, self.user.email), ("new@example.org", "new@example.org"))
        # The old address is told.
        self.assertEqual(mail.outbox[-1].to, ["old@example.org"])
        # The link works once.
        self.assertEqual(APIClient().post("/api/me/email/confirm", {"token": secret}, format="json").status_code, 400)

    def test_an_address_with_an_account_is_refused_when_the_link_is_used(self):
        get_user_model().objects.create_user(username="taken@example.org", email="taken@example.org")
        self.assertEqual(self.client.post("/api/me/email", {"email": "taken@example.org"}, format="json")
                         .status_code, 202)
        r = APIClient().post("/api/me/email/confirm", {"token": self.secret()}, format="json")
        self.assertEqual(r.json()["code"], "email_taken")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "old@example.org")

    def test_a_change_link_does_not_sign_in(self):
        self.client.post("/api/me/email", {"email": "new@example.org"}, format="json")
        self.assertEqual(APIClient().post("/api/auth/verify", {"token": self.secret()}, format="json").status_code, 400)

    def test_bad_requests(self):
        self.assertEqual(self.client.post("/api/me/email", {"email": "old@example.org"}, format="json")
                         .json()["code"], "same_email")
        self.assertEqual(self.client.post("/api/me/email", {"email": "nope"}, format="json").status_code, 400)
        self.assertEqual(APIClient().post("/api/me/email", {"email": "a@example.org"}, format="json").status_code, 401)
        self.assertFalse(SignInLink.objects.filter(purpose="change_email").exists())


class PrefsTest(TestCase):
    def setUp(self):
        self.user, self.client = signed_in()

    def test_defaults_then_changes(self):
        self.assertEqual(self.client.get("/api/me/prefs").json(),
                         {"replies": True, "plan_reminders": False, "reminder_hour": 7, "timezone": "UTC",
                          "language": "en"})
        out = self.client.patch("/api/me/prefs", {"plan_reminders": True, "reminder_hour": 21,
                                                  "timezone": "Africa/Nairobi", "language": "sw"}, format="json").json()
        self.assertEqual(out, {"replies": True, "plan_reminders": True, "reminder_hour": 21,
                               "timezone": "Africa/Nairobi", "language": "sw"})

    def test_bad_values_are_refused(self):
        for body in ({"replies": "yes"}, {"reminder_hour": 24}, {"timezone": "Mars/Olympus"}, {"language": "xx"}):
            self.assertEqual(self.client.patch("/api/me/prefs", body, format="json").status_code, 400, body)
        self.assertFalse(EmailPrefs.objects.exists())

    def test_replies_off_means_no_reply_email_but_the_reply_is_kept(self):
        from accounts.models import Role
        self.client.patch("/api/me/prefs", {"replies": False}, format="json")
        m = ReaderMessage.objects.create(user=self.user, kind="question", verse="JHN.3.16", language="en", text="Why?")
        editor, staff = signed_in("editor@example.org")
        Role.objects.create(user=editor, kind=Role.Kind.EDITOR)
        r = staff.patch(f"/api/admin/inbox/{m.id}/", {"reply": "Because."}, format="json")
        self.assertIn(r.status_code, (200, 201), r.content)
        m.refresh_from_db()
        self.assertEqual(m.reply, "Because.")
        self.assertEqual(mail.outbox, [])


def plans(active, **each):
    return {"active": active, "at": 1, "plans": each}


@override_settings(OWB_SITE_URL=SITE, OWB_API_URL="https://api.openwordbible.org")
class RemindersTest(TestCase):
    def setUp(self):
        self.user, self.client = signed_in()
        self.client.patch("/api/me/prefs", {"plan_reminders": True, "reminder_hour": 7,
                                            "timezone": "America/New_York"}, format="json")

    def at(self, iso):
        return datetime.fromisoformat(iso).replace(tzinfo=dt_timezone.utc)

    def run_at(self, iso):
        with mock.patch("django.utils.timezone.now", return_value=self.at(iso)):
            call_command("send_plan_reminders", stdout=io.StringIO())

    def test_the_first_day_not_done_is_sent_once_a_day_at_the_hour(self):
        ReaderState.objects.create(user=self.user, plans=plans("mark", mark={"start": "2026-10-01", "done": [1, 2]}))
        self.run_at("2026-10-30T10:00:00")   # 6:00 in New York: too early
        self.assertEqual(mail.outbox, [])
        self.run_at("2026-10-30T11:30:00")
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.subject, "Today’s reading: Mark 3")
        self.assertIn("https://openwordbible.org/mrk/3/", sent.body)
        self.assertIn("List-Unsubscribe", sent.extra_headers)
        self.run_at("2026-10-30T20:00:00")   # the same day: nothing more
        self.assertEqual(len(mail.outbox), 1)
        self.run_at("2026-10-31T12:00:00")   # the next day, nothing read: offered again
        self.assertEqual(mail.outbox[-1].subject, "Today’s reading: Mark 3")

    def test_the_readers_own_plan_and_language(self):
        EmailPrefs.objects.filter(user=self.user).update(language="es")
        progress = {"my-abcd": {"start": "2026-10-01", "done": []}}
        ReaderState.objects.create(user=self.user, plans=plans("my-abcd", **progress),
                                   custom_plans={"my-abcd": {"name": "Advent", "days": [["LUK.1", "LUK.2"]], "at": 1}})
        self.run_at("2026-10-30T12:00:00")
        self.assertIn("Advent", mail.outbox[0].body)
        self.assertIn("https://openwordbible.org/es/luk/2/", mail.outbox[0].body)

    def test_nothing_without_a_plan_under_way(self):
        ReaderState.objects.create(user=self.user, plans=plans("mark", mark={"start": "2026-10-01",
                                                                             "done": list(range(1, 17))}))
        self.run_at("2026-10-30T12:00:00")
        EmailPrefs.objects.update(plan_reminders=False, last_reminder=None)
        ReaderState.objects.update(plans=plans("mark", mark={"start": "2026-10-01", "done": []}))
        self.run_at("2026-10-30T13:00:00")
        self.assertEqual(mail.outbox, [])

    def test_unsubscribing_takes_a_post(self):
        url = unsubscribe_url(self.user).replace("https://api.openwordbible.org", "")
        r = APIClient().get(url)
        self.assertContains(r, "Stop these emails")
        self.assertTrue(EmailPrefs.objects.get().plan_reminders)
        self.assertEqual(APIClient().post(url).status_code, 200)
        self.assertFalse(EmailPrefs.objects.get().plan_reminders)
        self.assertEqual(APIClient().post("/api/email/unsubscribe?t=forged").status_code, 400)

    def test_todays_reading(self):
        state = ReaderState(plans=plans("john", john={"start": "2026-10-01", "done": [1, 3]}))
        name, day, total, refs = reminders.todays_reading(state)
        self.assertEqual((day, refs), (2, ["JHN.2"]))


def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


class FakeAuthenticator:
    """A passkey made and used in the test, as a browser's would be."""
    def __init__(self, rp_id="openwordbible.org", origin=SITE):
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.credential_id = os.urandom(16)
        self.rp_hash = hashlib.sha256(rp_id.encode()).digest()
        self.origin = origin
        self.count = 0

    def client_data(self, kind, challenge):
        return json.dumps({"type": kind, "challenge": challenge, "origin": self.origin,
                           "crossOrigin": False}).encode()

    def create(self, options):
        numbers = self.key.public_key().public_numbers()
        cose = cbor2.dumps({1: 2, 3: -7, -1: 1, -2: numbers.x.to_bytes(32, "big"), -3: numbers.y.to_bytes(32, "big")})
        auth_data = (self.rp_hash + bytes([0x45]) + (0).to_bytes(4, "big") + bytes(16)
                     + len(self.credential_id).to_bytes(2, "big") + self.credential_id + cose)
        attestation = cbor2.dumps({"fmt": "none", "attStmt": {}, "authData": auth_data})
        return {"id": b64(self.credential_id), "rawId": b64(self.credential_id), "type": "public-key",
                "response": {"clientDataJSON": b64(self.client_data("webauthn.create", options["challenge"])),
                             "attestationObject": b64(attestation), "transports": ["internal"]}}

    def get(self, options):
        self.count += 1
        auth_data = self.rp_hash + bytes([0x05]) + self.count.to_bytes(4, "big")
        client = self.client_data("webauthn.get", options["challenge"])
        signature = self.key.sign(auth_data + hashlib.sha256(client).digest(), ec.ECDSA(hashes.SHA256()))
        return {"id": b64(self.credential_id), "rawId": b64(self.credential_id), "type": "public-key",
                "response": {"clientDataJSON": b64(client), "authenticatorData": b64(auth_data),
                             "signature": b64(signature), "userHandle": None}}


@override_settings(PASSKEY_RP_ID="openwordbible.org", PASSKEY_ORIGINS=[SITE], CORS_ALLOWED_ORIGINS=[SITE])
class PasskeyTest(TestCase):
    def setUp(self):
        self.user, self.client = signed_in()
        self.key = FakeAuthenticator()

    def add(self, key=None):
        options = self.client.post("/api/me/passkeys/options").json()
        return self.client.post("/api/me/passkeys", {"credential": (key or self.key).create(options)}, format="json")

    def sign_in(self, key=None):
        anon = APIClient()
        options = anon.post("/api/auth/passkey/options").json()
        return anon.post("/api/auth/passkey", {"credential": (key or self.key).get(options)}, format="json")

    def test_a_passkey_is_added_and_signs_in(self):
        r = self.add()
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(len(self.client.get("/api/me/passkeys").json()), 1)
        r = self.sign_in()
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()["user"]["email"], self.user.username)
        token = APIClient()
        token.credentials(HTTP_AUTHORIZATION="Bearer " + r.json()["token"])
        self.assertEqual(token.get("/api/me").status_code, 200)
        self.assertEqual(Passkey.objects.get().sign_count, 1)

    def test_a_challenge_works_once(self):
        self.add()
        anon = APIClient()
        options = anon.post("/api/auth/passkey/options").json()
        first = self.key.get(options)
        self.assertEqual(anon.post("/api/auth/passkey", {"credential": first}, format="json").status_code, 200)
        self.assertEqual(anon.post("/api/auth/passkey", {"credential": self.key.get(options)}, format="json")
                         .status_code, 400)

    def test_another_origin_or_an_unknown_passkey_is_refused(self):
        self.add()
        self.assertEqual(self.sign_in(FakeAuthenticator(origin="https://evil.example")).status_code, 400)
        stray = FakeAuthenticator()
        self.assertEqual(self.sign_in(stray).status_code, 400)
        self.assertEqual(self.add(FakeAuthenticator(origin="https://evil.example")).status_code, 400)
        self.assertEqual(Passkey.objects.count(), 1)

    def test_a_removed_passkey_no_longer_signs_in(self):
        pid = self.add().json()["id"]
        self.assertEqual(self.client.delete(f"/api/me/passkeys/{pid}").status_code, 204)
        self.assertEqual(self.sign_in().status_code, 400)

    def test_challenges_go_stale(self):
        anon = APIClient()
        options = anon.post("/api/auth/passkey/options").json()
        PasskeyChallenge.objects.update(created_at=datetime(2020, 1, 1, tzinfo=dt_timezone.utc))
        self.add()
        self.assertEqual(anon.post("/api/auth/passkey", {"credential": self.key.get(options)}, format="json")
                         .status_code, 400)

    def test_deleting_the_account_removes_its_passkeys(self):
        self.add()
        self.client.delete("/api/me")
        self.assertFalse(Passkey.objects.exists())
