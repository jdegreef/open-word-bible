"""Syncing a reader's bookmarks, highlights and reading place (accounts/reading.py)."""
import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import ApiToken, Mark, ReadingPlace, new_secret


def device(user):
    """A browser signed in to user's account: a token of its own."""
    secret, key_hash = new_secret()
    ApiToken.objects.create(user=user, key_hash=key_hash)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {secret}")
    return client


def signed_in(email="reader@example.org"):
    user = get_user_model().objects.create_user(username=email, email=email)
    return user, device(user)


class ReadingSyncTest(TestCase):
    def setUp(self):
        self.user, self.client = signed_in()

    def sync(self, client=None, **body):
        r = (client or self.client).post("/api/reading", body, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        return r.json()

    def test_needs_an_account(self):
        self.assertEqual(APIClient().get("/api/reading").status_code, 401)
        self.assertEqual(APIClient().post("/api/reading", {}, format="json").status_code, 401)

    def test_a_device_copy_is_kept_and_read_back(self):
        out = self.sync(marks={"JHN.3.16": {"b": True, "h": "yellow", "text": "For God", "lang": "en", "at": 100}},
                        place={"book": "JHN", "chapter": 3, "verse": "16", "at": 100})
        expected = {"marks": {"JHN.3.16": {"b": True, "h": "yellow", "text": "For God", "lang": "en", "at": 100}},
                    "place": {"book": "JHN", "chapter": 3, "verse": "16", "at": 100}}
        self.assertEqual(out, expected)
        self.assertEqual(self.client.get("/api/reading").json(), expected)

    def test_the_latest_change_to_a_verse_wins(self):
        self.sync(marks={"JHN.3.16": {"h": "yellow", "at": 200}, "JHN.3.17": {"b": True, "at": 200}})
        # Another device: an older change to 3:16 loses, a newer one to 3:17 wins.
        phone = device(self.user)
        out = self.sync(phone, marks={"JHN.3.16": {"h": "blue", "at": 150}, "JHN.3.17": {"h": "green", "at": 300},
                                      "ROM.8.28": {"b": True, "at": 250}})
        self.assertEqual(out["marks"]["JHN.3.16"]["h"], "yellow")
        self.assertEqual(out["marks"]["JHN.3.17"], {"h": "green", "text": "", "lang": "", "at": 300})
        self.assertIn("ROM.8.28", out["marks"])
        # Sending the same copy again changes nothing.
        self.assertEqual(self.sync(phone, marks={"JHN.3.16": {"h": "blue", "at": 150}})["marks"], out["marks"])

    def test_a_cleared_mark_reaches_other_devices(self):
        self.sync(marks={"JHN.3.16": {"b": True, "h": "pink", "text": "x", "lang": "en", "at": 100}})
        out = self.sync(marks={"JHN.3.16": {"at": 200}})
        self.assertEqual(out["marks"]["JHN.3.16"], {"at": 200})
        self.assertEqual(Mark.objects.get().highlight, "")

    def test_the_latest_place_wins(self):
        self.sync(place={"book": "JHN", "chapter": 3, "verse": "16", "at": 200})
        self.sync(place={"book": "ROM", "chapter": 1, "verse": "1", "at": 100})
        self.assertEqual(self.sync()["place"]["book"], "JHN")
        self.sync(place={"book": "JHN", "chapter": 8, "verse": "7:53", "at": 300})
        self.assertEqual(ReadingPlace.objects.get().verse, "7:53")

    def test_a_clock_in_the_future_counts_as_now(self):
        future = int(time.time() * 1000) + 10 * 86_400_000
        out = self.sync(marks={"JHN.3.16": {"h": "yellow", "at": future}})
        self.assertLessEqual(out["marks"]["JHN.3.16"]["at"], int(time.time() * 1000) + 1000)
        # So a real later change still wins.
        out = self.sync(marks={"JHN.3.16": {"h": "blue", "at": int(time.time() * 1000) + 5000}})
        self.assertEqual(out["marks"]["JHN.3.16"]["h"], "blue")

    def test_bad_copies_are_refused_and_nothing_is_saved(self):
        for body in ({"marks": {"JHN.3.16": {"h": "purple", "at": 1}}},
                     {"marks": {"not a verse": {"b": True, "at": 1}}},
                     {"marks": {"JHN.3.16": {"b": True}}},
                     {"marks": {"JHN.3.16": {"b": True, "at": 1}}, "place": {"book": "JHN", "chapter": 0, "verse": "1"}},
                     {"marks": ["JHN.3.16"]}):
            r = self.client.post("/api/reading", body, format="json")
            self.assertEqual(r.status_code, 400, body)
        self.assertFalse(Mark.objects.exists())
        # Overlong words are cut, and an unknown language is dropped.
        out = self.sync(marks={"JHN.3.16": {"b": True, "text": "x" * 5000, "lang": "de", "at": 1}})
        self.assertEqual(len(out["marks"]["JHN.3.16"]["text"]), 2000)
        self.assertEqual(out["marks"]["JHN.3.16"]["lang"], "")

    def test_readers_see_only_their_own(self):
        self.sync(marks={"JHN.3.16": {"b": True, "at": 1}}, place={"book": "JHN", "chapter": 3, "verse": "16", "at": 1})
        _, other = signed_in("other@example.org")
        self.assertEqual(other.get("/api/reading").json(), {"marks": {}, "place": None})
