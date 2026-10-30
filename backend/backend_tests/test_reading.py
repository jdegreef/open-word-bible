"""Syncing a reader's bookmarks, highlights, reading place, reading-plan
progress and settings (accounts/reading.py)."""
import json
import time
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import ApiToken, Mark, PassageNote, ReaderState, ReadingPlace, SavedWord, new_secret


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
                    "place": {"book": "JHN", "chapter": 3, "verse": "16", "at": 100},
                    "plans": None, "settings": None, "notes": {}, "words": {}, "myplans": {}}
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

    def test_a_note_is_kept_synced_and_cleared_like_a_mark(self):
        out = self.sync(marks={"JHN.3.16": {"n": "Read this at the funeral.", "text": "For God", "lang": "en",
                                            "at": 100}})
        self.assertEqual(out["marks"]["JHN.3.16"],
                         {"n": "Read this at the funeral.", "text": "For God", "lang": "en", "at": 100})
        # A newer edit on another device wins; clearing it reaches every device.
        phone = device(self.user)
        self.assertEqual(self.sync(phone, marks={"JHN.3.16": {"n": "Edited", "at": 200}})["marks"]["JHN.3.16"]["n"],
                         "Edited")
        self.assertEqual(self.sync(marks={"JHN.3.16": {"at": 300}})["marks"]["JHN.3.16"], {"at": 300})
        self.assertEqual(Mark.objects.get().note, "")

    def test_a_note_is_text_and_overlong_ones_are_cut(self):
        r = self.client.post("/api/reading", {"marks": {"JHN.3.16": {"n": ["x"], "at": 1}}}, format="json")
        self.assertEqual(r.status_code, 400)
        out = self.sync(marks={"JHN.3.16": {"n": "x" * 9000, "at": 1}})
        self.assertEqual(len(out["marks"]["JHN.3.16"]["n"]), 5000)

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
                     {"marks": {"JHN.3.16": {"b": True, "at": 1}},
                      "place": {"book": "JHN", "chapter": 0, "verse": "1"}},
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
        self.assertEqual(other.get("/api/reading").json(),
                         {"marks": {}, "place": None, "plans": None, "settings": None,
                          "notes": {}, "words": {}, "myplans": {}})


def plans(active=None, at=0, **each):
    return {"active": active, "at": at, "plans": each}


class PlanAndSettingsSyncTest(TestCase):
    def setUp(self):
        self.user, self.client = signed_in()

    def sync(self, client=None, **body):
        r = (client or self.client).post("/api/reading", body, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        return r.json()

    def test_plan_progress_is_kept_and_read_back(self):
        sent = plans("mark", 100, mark={"start": "2026-10-12", "done": [3, 1, 2, 2], "at": 100})
        out = self.sync(plans=sent)
        self.assertEqual(out["plans"], plans("mark", 100, mark={"start": "2026-10-12", "done": [1, 2, 3], "at": 100}))
        self.assertEqual(self.client.get("/api/reading").json()["plans"], out["plans"])

    def test_the_latest_change_to_each_plan_wins(self):
        self.sync(plans=plans("mark", 100, mark={"start": "2026-10-12", "done": [1, 2], "at": 200},
                              john={"start": "2026-09-01", "done": [1], "at": 100}))
        phone = device(self.user)
        out = self.sync(phone, plans=plans("john", 300, mark={"start": "2026-10-12", "done": [1], "at": 150},
                                           john={"start": "2026-09-01", "done": [1, 2], "at": 250},
                                           acts={"start": "2026-10-01", "done": [], "at": 50}))
        self.assertEqual(out["plans"]["plans"]["mark"]["done"], [1, 2])
        self.assertEqual(out["plans"]["plans"]["john"]["done"], [1, 2])
        self.assertIn("acts", out["plans"]["plans"])
        self.assertEqual(out["plans"]["active"], "john")
        # An older choice of plan loses; a newer one, even to stop reading, wins.
        self.assertEqual(self.sync(plans=plans("mark", 200))["plans"]["active"], "john")
        self.assertIsNone(self.sync(plans=plans(None, 400))["plans"]["active"])

    def test_a_device_that_never_stamped_its_plans_loses(self):
        self.sync(plans=plans("mark", 100, mark={"start": "2026-10-12", "done": [1, 2], "at": 100}))
        unstamped = {"active": "mark", "plans": {"mark": {"start": "2026-10-01", "done": []}}}
        out = self.sync(device(self.user), plans=unstamped)
        self.assertEqual(out["plans"]["plans"]["mark"]["done"], [1, 2])

    def test_the_latest_settings_win_whole(self):
        self.sync(settings={"v": {"level": "L", "gender": 1, "partner": "BSB", "lang": "es"}, "at": 200})
        out = self.sync(device(self.user), settings={"v": {"level": "R"}, "at": 100})
        # The page's language is not a setting.
        self.assertEqual(out["settings"], {"v": {"level": "L", "gender": 1, "partner": "BSB"}, "at": 200})
        out = self.sync(settings={"v": {"level": "R"}, "at": 300})
        self.assertEqual(out["settings"], {"v": {"level": "R"}, "at": 300})

    def test_bad_copies_are_refused_and_nothing_is_saved(self):
        for body in ({"plans": ["mark"]},
                     {"plans": {"plans": ["mark"]}},
                     {"plans": plans(mark={"start": "2026-10-12", "done": [], "at": -1})},
                     {"settings": {"v": {"level": "L"}}},
                     {"settings": {"v": ["level"], "at": 1}},
                     {"marks": {"JHN.3.16": {"b": True, "at": 1}}, "settings": {"v": [], "at": 1}}):
            r = self.client.post("/api/reading", body, format="json")
            self.assertEqual(r.status_code, 400, body)
        self.assertFalse(ReaderState.objects.exists())
        self.assertFalse(Mark.objects.exists())

    def test_a_stray_plan_or_setting_is_left_out_and_the_rest_kept(self):
        good = {"start": "2026-10-12", "done": [1], "at": 1}
        out = self.sync(plans=plans("bad", 1, mark=good,
                                    bad={"start": "soon", "done": [], "at": 1},
                                    zero={"start": "2026-10-12", "done": [0], "at": 1},
                                    text={"start": "2026-10-12", "done": ["1"], "at": 1},
                                    **{"../x": good}),
                        settings={"v": {"level": "L", "partner": "<b>", "view": {"x": 1}, "Units": 1, "gender": True},
                                  "at": 1})
        self.assertEqual(out["plans"], plans(None, 1, mark=good))
        self.assertEqual(out["settings"], {"v": {"level": "L"}, "at": 1})

    def test_deleting_the_account_removes_them(self):
        self.sync(plans=plans("mark", 1, mark={"start": "2026-10-12", "done": [1], "at": 1}),
                  settings={"v": {"level": "L"}, "at": 1})
        self.assertEqual(self.client.delete("/api/me").status_code, 204)
        self.assertFalse(ReaderState.objects.exists())


def source_lemmas():
    """Two dictionary forms from the source data (never typed here):
    the first Greek one in John 3, and the first Hebrew one in Genesis 1."""
    data = Path(__file__).resolve().parents[2] / "data"
    greek = json.loads((data / "grc" / "JHN.3.json").read_text(encoding="utf-8"))["verses"]["JHN.3.1"][0]
    hebrew = json.loads((data / "hbo" / "GEN.1.json").read_text(encoding="utf-8"))["verses"]["GEN.1.1"][0]
    return greek["lemma"], hebrew["lemma"]


class StudySyncTest(TestCase):
    """Collections, passage notes, the word list and the reader's own plans."""
    def setUp(self):
        self.user, self.client = signed_in()

    def sync(self, client=None, **body):
        r = (client or self.client).post("/api/reading", body, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        return r.json()

    def test_collections_are_kept_on_a_mark_and_alone_keep_it(self):
        out = self.sync(marks={"JHN.3.16": {"t": ["Prayer", " prayer ", "Sunday's  sermon", ""], "text": "For God",
                                            "lang": "en", "at": 100}})
        self.assertEqual(out["marks"]["JHN.3.16"],
                         {"t": ["Prayer", "Sunday's sermon"], "text": "For God", "lang": "en", "at": 100})
        self.assertEqual(self.sync(marks={"JHN.3.16": {"at": 200}})["marks"]["JHN.3.16"], {"at": 200})
        self.assertEqual(Mark.objects.get().tags, [])

    def test_bad_collections_are_refused(self):
        for tags in ("Prayer", [1], ["x"] * 21):
            r = self.client.post("/api/reading", {"marks": {"JHN.3.16": {"t": tags, "at": 1}}}, format="json")
            self.assertEqual(r.status_code, 400, tags)
        self.assertFalse(Mark.objects.exists())

    def test_a_passage_note_syncs_and_clears(self):
        note = {"n": "The new birth", "text": "Jesus answered", "lang": "en", "t": ["Study"], "at": 100}
        out = self.sync(notes={"JHN.3.3-8": note})
        self.assertEqual(out["notes"], {"JHN.3.3-8": note})
        phone = device(self.user)
        self.assertEqual(self.sync(phone, notes={"JHN.3.3-8": {"n": "Older", "at": 50}})["notes"]["JHN.3.3-8"]["n"],
                         "The new birth")
        self.assertEqual(self.sync(phone, notes={"JHN.3.3-8": {"at": 300}})["notes"], {"JHN.3.3-8": {"at": 300}})
        self.assertEqual(PassageNote.objects.get().note, "")

    def test_a_passage_is_verses_of_one_chapter_in_order(self):
        for passage in ("JHN.3.8-3", "JHN.3.3-3", "JHN.3.16", "JHN.3-4", "jhn.3.1-2"):
            r = self.client.post("/api/reading", {"notes": {passage: {"n": "x", "at": 1}}}, format="json")
            self.assertEqual(r.status_code, 400, passage)

    def test_the_word_list_keeps_saved_words_and_notes(self):
        greek, hebrew = source_lemmas()
        out = self.sync(words={greek: {"s": True, "g": "was", "l": "grc", "at": 100},
                               hebrew: {"n": "A preposition", "g": "in", "l": "hbo", "at": 120}})
        self.assertEqual(out["words"][greek], {"s": True, "g": "was", "l": "grc", "at": 100})
        self.assertEqual(out["words"][hebrew], {"n": "A preposition", "g": "in", "l": "hbo", "at": 120})
        # Taking a word off the list reaches the other devices.
        out = self.sync(device(self.user), words={hebrew: {"at": 200}})
        self.assertEqual(out["words"][hebrew], {"at": 200})
        self.assertEqual(SavedWord.objects.get(lemma=hebrew).note, "")

    def test_a_word_is_greek_or_hebrew(self):
        for lemma in ("love", " ", "x" * 65, "<script>"):
            r = self.client.post("/api/reading", {"words": {lemma: {"s": True, "at": 1}}}, format="json")
            self.assertEqual(r.status_code, 400, lemma)
        self.assertFalse(SavedWord.objects.exists())

    def test_own_plans_sync_and_delete(self):
        plan = {"name": "  Advent   readings ", "days": [["LUK.1", "LUK.2"], ["MAT.1"]], "at": 100}
        out = self.sync(myplans={"my-adv1": plan})
        self.assertEqual(out["myplans"], {"my-adv1": {"name": "Advent readings",
                                                      "days": [["LUK.1", "LUK.2"], ["MAT.1"]], "at": 100}})
        phone = device(self.user)
        self.assertEqual(self.sync(phone, myplans={"my-adv1": {"at": 50}})["myplans"]["my-adv1"]["at"], 100)
        self.assertEqual(self.sync(phone, myplans={"my-adv1": {"at": 200}})["myplans"], {"my-adv1": {"at": 200}})

    def test_bad_own_plans_are_refused(self):
        for plans_ in ({"mark": {"name": "x", "days": [["MRK.1"]], "at": 1}},
                       {"my-abcd": {"name": "", "days": [["MRK.1"]], "at": 1}},
                       {"my-abcd": {"name": "x", "days": [], "at": 1}},
                       {"my-abcd": {"name": "x", "days": [["Mark 1"]], "at": 1}},
                       {"my-abcd": {"name": "x", "days": [["MRK.1"] * 31], "at": 1}}):
            r = self.client.post("/api/reading", {"myplans": plans_}, format="json")
            self.assertEqual(r.status_code, 400, plans_)
        self.assertFalse(ReaderState.objects.exists())
