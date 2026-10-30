"""Reading groups (groups/views.py)."""
from rest_framework.test import APIClient

from accounts.models import ReaderState
from django.test import TestCase
from groups.models import GroupPost, Membership, ReadingGroup

from .test_reading import signed_in


def reader(email, name="Reader"):
    user, client = signed_in(email)
    user.first_name = name
    user.save()
    return user, client


class GroupsTest(TestCase):
    def setUp(self):
        self.ann, self.a = reader("ann@example.org", "Ann")
        self.ben, self.b = reader("ben@example.org", "Ben")

    def start(self, client=None, **body):
        body = {"name": "Tuesday group", "plan_id": "mark", **body}
        r = (client or self.a).post("/api/groups", body, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        return r.json()

    def test_start_invite_join_and_see_progress(self):
        g = self.start()
        self.assertTrue(g["leader"])
        self.assertEqual(g["days"], 16)
        preview = self.b.get(f"/api/groups/invite/{g['invite']}").json()
        self.assertEqual((preview["name"], preview["members"], preview["member"]), ("Tuesday group", 1, None))
        ReaderState.objects.create(user=self.ben, plans={"active": "mark", "at": 1,
                                                         "plans": {"mark": {"start": "2026-10-01", "done": [1, 2]}}})
        joined = self.b.post("/api/groups/join", {"code": g["invite"]}, format="json").json()
        self.assertFalse(joined["leader"])
        seen = {m["name"]: m for m in self.a.get(f"/api/groups/{g['id']}").json()["member_list"]}
        self.assertEqual(seen["Ben"]["progress"]["done"], [1, 2])
        self.assertTrue(seen["Ann"]["leader"])
        # Addresses are never shown.
        self.assertNotIn("ben@example.org", str(self.a.get(f"/api/groups/{g['id']}").content))
        # Joining again changes nothing.
        self.b.post("/api/groups/join", {"code": g["invite"]}, format="json")
        self.assertEqual(Membership.objects.count(), 2)

    def test_progress_is_shared_only_if_the_member_wants(self):
        g = self.start()
        self.b.post("/api/groups/join", {"code": g["invite"]}, format="json")
        ReaderState.objects.create(user=self.ben, plans={"plans": {"mark": {"start": "2026-10-01", "done": [1]}}})
        self.b.patch(f"/api/groups/{g['id']}", {"share_progress": False}, format="json")
        seen = {m["name"]: m for m in self.a.get(f"/api/groups/{g['id']}").json()["member_list"]}
        self.assertIsNone(seen["Ben"]["progress"])
        mine = {m["name"]: m for m in self.b.get(f"/api/groups/{g['id']}").json()["member_list"]}
        self.assertEqual(mine["Ben"]["progress"]["done"], [1])

    def test_a_display_name_is_needed(self):
        _, nameless = reader("cal@example.org", "")
        self.assertEqual(nameless.post("/api/groups", {"name": "x", "plan_id": "mark"}, format="json")
                         .json()["code"], "need_name")
        g = self.start()
        self.assertEqual(nameless.post("/api/groups/join", {"code": g["invite"]}, format="json").json()["code"],
                         "need_name")

    def test_only_members_see_a_group(self):
        g = self.start()
        self.assertEqual(self.b.get(f"/api/groups/{g['id']}").status_code, 404)
        self.assertEqual(APIClient().get("/api/groups").status_code, 401)
        self.assertEqual(self.b.get("/api/groups").json(), [])

    def test_posts_by_day_and_who_may_delete_them(self):
        g = self.start()
        self.b.post("/api/groups/join", {"code": g["invite"]}, format="json")
        out = self.b.post(f"/api/groups/{g['id']}/posts", {"day": 3, "text": "Mark 3 surprised me."},
                          format="json").json()
        post = out["posts"][0]
        self.assertEqual((post["day"], post["name"], post["mine"]), (3, "Ben", True))
        self.assertEqual(self.b.post(f"/api/groups/{g['id']}/posts", {"day": 17, "text": "x"}, format="json")
                         .status_code, 400)
        self.assertEqual(self.b.post(f"/api/groups/{g['id']}/posts", {"day": 1, "text": " "}, format="json")
                         .status_code, 400)
        # The leader can delete any post; a member only their own.
        mine = self.a.post(f"/api/groups/{g['id']}/posts", {"day": 3, "text": "Me too."}, format="json").json()
        ann_post = [p for p in mine["posts"] if p["name"] == "Ann"][0]["id"]
        self.assertEqual(self.b.delete(f"/api/groups/{g['id']}/posts/{ann_post}").status_code, 403)
        self.assertEqual(self.a.delete(f"/api/groups/{g['id']}/posts/{post['id']}").status_code, 204)
        self.assertEqual(GroupPost.objects.count(), 1)

    def test_the_leader_runs_the_group(self):
        g = self.start()
        self.b.post("/api/groups/join", {"code": g["invite"]}, format="json")
        self.assertEqual(self.b.patch(f"/api/groups/{g['id']}", {"name": "Mine now"}, format="json").status_code, 403)
        self.assertEqual(self.b.post(f"/api/groups/{g['id']}/invite").status_code, 403)
        fresh = self.a.post(f"/api/groups/{g['id']}/invite").json()["invite"]
        self.assertNotEqual(fresh, g["invite"])
        _, cal = reader("cal@example.org", "Cal")
        self.assertEqual(cal.post("/api/groups/join", {"code": g["invite"]}, format="json").status_code, 404)
        ben = [m for m in self.a.get(f"/api/groups/{g['id']}").json()["member_list"] if m["name"] == "Ben"][0]
        self.assertEqual(self.a.delete(f"/api/groups/{g['id']}/members/{ben['id']}").status_code, 204)
        self.assertEqual(self.b.get(f"/api/groups/{g['id']}").status_code, 404)

    def test_leaving_passes_on_the_lead_and_the_last_one_out_closes_it(self):
        g = self.start()
        self.b.post("/api/groups/join", {"code": g["invite"]}, format="json")
        self.assertEqual(self.a.post(f"/api/groups/{g['id']}/leave").status_code, 204)
        self.assertTrue(self.b.get(f"/api/groups/{g['id']}").json()["leader"])
        self.b.post(f"/api/groups/{g['id']}/leave")
        self.assertFalse(ReadingGroup.objects.exists())

    def test_a_readers_own_plan(self):
        g = self.start(plan_id="my-abcd", plan={"name": "Advent", "days": [["LUK.1"], ["LUK.2"]]})
        self.assertEqual((g["plan_name"], g["days"], g["plan"]["days"]), ("Advent", 2, [["LUK.1"], ["LUK.2"]]))
        r = self.a.post("/api/groups", {"name": "x", "plan_id": "my-abcd", "plan": {"name": "x", "days": [["Luke"]]}},
                        format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.a.post("/api/groups", {"name": "x", "plan_id": "nope"}, format="json").status_code, 400)

    def test_deleting_an_account_leaves_its_groups(self):
        g = self.start()
        self.b.post("/api/groups/join", {"code": g["invite"]}, format="json")
        self.b.post(f"/api/groups/{g['id']}/posts", {"day": 1, "text": "Hello"}, format="json")
        self.assertEqual(self.b.delete("/api/me").status_code, 204)
        self.assertEqual(Membership.objects.count(), 1)
        self.assertFalse(GroupPost.objects.exists())
