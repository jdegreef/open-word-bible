"""Users in the admin (staff/users.py): system accounts kept apart from
people, display names with a fallback from the address, and the reader
inbox's search across every message (staff/inbox.py q=)."""
import importlib
from datetime import timedelta

from django.apps import apps
from django.utils import timezone

from accounts.models import SystemAccount
from accounts.system import fits_rule, name_from_email
from feedback.models import ReaderMessage
from staff.models import AdminAction

from .test_admin import K, AdminTestCase, User, account, client_for


class SystemAccountsTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.reader = account("jane.doe+bible@example.org")
        self.render = User.objects.create(username="render")

    def test_the_migration_rule(self):
        signed_in = User.objects.create(username="cron", last_login=timezone.now())
        with_role = account("deploy", (K.EDITOR,))
        self.assertTrue(fits_rule(self.render, has_roles=False))
        self.assertFalse(fits_rule(self.reader, has_roles=False))
        self.assertFalse(fits_rule(signed_in, has_roles=False))
        migration = importlib.import_module("accounts.migrations.0024_system_accounts")
        migration.mark(apps, None)
        migration.mark(apps, None)   # twice changes nothing
        self.assertEqual(list(SystemAccount.objects.values_list("user__username", flat=True)), ["render"])
        self.assertIn("never signed in", SystemAccount.objects.get().reason)
        # Nobody is deleted.
        for user in (self.reader, signed_in, with_role, self.render):
            self.assertTrue(User.objects.filter(id=user.id).exists())

    def test_hidden_from_users_and_counts_unless_asked(self):
        SystemAccount.objects.create(user=self.render)
        data = self.admin.get("/api/admin/users/").json()
        self.assertNotIn("render", [u["email"] for u in data["users"]])
        self.assertEqual(data["system_hidden"], 1)
        self.assertEqual(data["total"], 2)   # boss and the reader
        shown = self.admin.get("/api/admin/users/?system=1").json()
        row = next(u for u in shown["users"] if u["email"] == "render")
        self.assertTrue(row["system"])
        self.assertEqual(shown["system_hidden"], 0)
        only = self.admin.get("/api/admin/users/?system=only").json()
        self.assertEqual([u["email"] for u in only["users"]], ["render"])
        engagement = self.admin.get("/api/admin/engagement/").json()
        self.assertEqual(engagement["accounts"], 2)

    def test_mark_and_unmark(self):
        url = f"/api/admin/users/{self.render.id}/"
        r = self.admin.patch(url, {"system": True}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertTrue(r.json()["system"])
        self.assertIn("boss@example.org", r.json()["system_reason"])
        self.assertTrue(self.admin.get(url).json()["system"])
        r = self.admin.patch(url, {"system": False}, format="json")
        self.assertFalse(r.json()["system"])
        self.assertFalse(SystemAccount.objects.exists())
        self.assertEqual(list(AdminAction.objects.order_by("created_at").values_list("action", flat=True)),
                         ["user.system", "user.person"])
        # Not yourself, not an account with a role, and only true or false.
        self.assertEqual(self.admin.patch(f"/api/admin/users/{self.boss.id}/", {"system": True},
                                          format="json").status_code, 400)
        editor = account("ed@example.org", (K.EDITOR,))
        self.assertEqual(self.admin.patch(f"/api/admin/users/{editor.id}/", {"system": True},
                                          format="json").status_code, 400)
        self.assertEqual(self.admin.patch(url, {"system": "yes"}, format="json").status_code, 400)

    def test_users_area_only(self):
        editor = client_for(account("ed@example.org", (K.EDITOR,)))
        r = editor.patch(f"/api/admin/users/{self.render.id}/", {"system": True}, format="json")
        self.assertEqual(r.status_code, 403)


class NamesTest(AdminTestCase):
    def test_fallback_from_the_address(self):
        self.assertEqual(name_from_email("jane.doe+bible@example.org"), "Jane Doe")
        self.assertEqual(name_from_email("j_smith-jr@example.org"), "J Smith Jr")
        self.assertEqual(name_from_email("render"), "Render")
        account("jane.doe@example.org")
        named = account("ruth@example.org")
        named.first_name = "Ruth Moabite"
        named.save()
        rows = {u["email"]: u for u in self.admin.get("/api/admin/users/").json()["users"]}
        self.assertEqual(rows["jane.doe@example.org"]["name"], "")   # unchanged: the name set, if any
        self.assertEqual(rows["jane.doe@example.org"]["display_name"], "Jane Doe")
        self.assertTrue(rows["jane.doe@example.org"]["display_name_is_fallback"])
        self.assertEqual(rows["ruth@example.org"]["display_name"], "Ruth Moabite")
        self.assertFalse(rows["ruth@example.org"]["display_name_is_fallback"])

    def test_admin_sets_a_name(self):
        reader = account("reader@example.org")
        r = self.admin.patch(f"/api/admin/users/{reader.id}/", {"name": "  Lydia   of Thyatira "}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()["name"], "Lydia of Thyatira")
        reader.refresh_from_db()
        self.assertEqual(reader.first_name, "Lydia of Thyatira")
        self.assertEqual(AdminAction.objects.get().action, "user.name")
        # The reader sees it on their account page.
        self.assertEqual(client_for(reader).get("/api/me").json()["display_name"], "Lydia of Thyatira")
        self.assertEqual(self.admin.patch(f"/api/admin/users/{reader.id}/", {"name": "x" * 81},
                                          format="json").status_code, 400)

    def test_account_page_patch_keeps_a_name_it_was_not_sent(self):
        reader = account("reader@example.org")
        me = client_for(reader)
        me.patch("/api/me", {"display_name": "Lydia"}, format="json")
        me.patch("/api/me", {}, format="json")
        reader.refresh_from_db()
        self.assertEqual(reader.first_name, "Lydia")


class InboxSearchTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.ann = account("ann@example.org")
        self.ann.first_name = "Ann Moore"
        self.ann.save()
        self.bob = account("bob@example.org")
        self.grace = self.message(self.ann, "JHN.3.16", "Why GRACE here and not favour?", days=4)
        self.light = self.message(self.bob, "JHN.1.5", "The light shines in darkness.", days=2)
        self.done = self.message(self.bob, "ROM.5.8", "Grace again: lovely.", status="done")

    def message(self, user, verse, text, days=0, **fields):
        m = ReaderMessage.objects.create(user=user, kind="suggestion", verse=verse, language="en", text=text, **fields)
        ReaderMessage.objects.filter(id=m.id).update(created_at=timezone.now() - timedelta(days=days))
        return m

    def found(self, query):
        return [m["id"] for m in self.admin.get("/api/admin/inbox/" + query).json()["messages"]]

    def test_words_any_case_across_fields(self):
        self.assertEqual(self.found("?q=grace"), [self.grace.id])            # new, the default status
        self.assertEqual(self.found("?status=done&q=grace"), [self.done.id])
        self.assertEqual(self.found("?status=all&q=grace"), [self.done.id, self.grace.id])
        self.assertEqual(self.found("?q=moore"), [self.grace.id])            # the sender's name
        self.assertEqual(self.found("?q=bob%40example"), [self.light.id])    # the sender's address
        self.assertEqual(self.found("?q=jhn.1"), [self.light.id])            # the verse id
        self.assertEqual(self.found("?q=grace+favour"), [self.grace.id])     # every word
        self.assertEqual(self.found("?q=grace+darkness"), [])

    def test_a_reference_finds_its_verse(self):
        self.assertEqual(self.found("?q=JHN.3.16"), [self.grace.id])
        self.assertEqual(self.found("?q=John+3:16"), [self.grace.id])

    def test_keeps_the_other_filters_and_counts_what_it_finds(self):
        ReaderMessage.objects.filter(id=self.grace.id).update(assigned_to=self.boss)
        self.assertEqual(self.found("?q=grace&assigned=me"), [self.grace.id])
        self.assertEqual(self.found("?q=grace&assigned=none"), [])
        self.assertEqual(self.found("?q=grace&kind=question"), [])
        data = self.admin.get("/api/admin/inbox/?q=grace").json()
        self.assertEqual(data["counts"], {"new": 1, "answered": 0, "done": 1, "declined": 0})
        self.assertEqual(data["total"], 1)
        # Without q, the counts are of every message, as before.
        self.assertEqual(self.admin.get("/api/admin/inbox/").json()["counts"]["new"], 2)
