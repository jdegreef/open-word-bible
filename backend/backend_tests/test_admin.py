"""The admin (staff/) and reader messages (feedback/): who may open what,
the progress numbers, the team, accounts, the inbox, jobs and team email."""
import io
import json
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django.urls import get_resolver
from rest_framework.test import APIClient

from accounts.models import ApiToken, Mark, Role, new_secret
from feedback.models import ReaderMessage
from staff import jobs as staff_jobs
from staff.models import AdminAction, Broadcast
from staff.permissions import AREAS
from staff.verses import covers
from texts.models import Edition
from translation.models import ContentFile, Decision, ImportRun, Rendering, Sentence

SITE = "https://openwordbible.org"
User = get_user_model()
K = Role.Kind


def admin_routes():
    """(path pattern, view) for every /api/admin/ endpoint."""
    staff = next(p for p in get_resolver().url_patterns if str(p.pattern) == "api/admin/")
    return [(str(p.pattern), p.callback) for p in staff.url_patterns]


def account(email, *roles):
    user = User.objects.create(username=email, email=email)
    for kind, *language in roles:
        Role.objects.create(user=user, kind=kind, language=language[0] if language else "")
    return user


def client_for(user):
    secret, key_hash = new_secret()
    ApiToken.objects.create(user=user, key_hash=key_hash)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {secret}")
    return client


def sentence(record_id, langs=("en",), status="ai_draft", edition=None):
    edition = edition or Edition.objects.get_or_create(
        code="sblgnt", defaults=dict(name="SBLGNT", language="grc", kind="original", licence="CC BY 4.0",
                                     source="sblgnt", source_commit="0" * 40))[0]
    book, chapter, verse, _ = record_id.split(".")
    s = Sentence.objects.create(record_id=record_id, book=book, chapter=int(chapter), verse=int(verse),
                                number=1, refs=[record_id.rsplit(".", 1)[0]], source_edition=edition,
                                source_text_id="SBLGNT@v1.2", tokens=[], literal_gloss="x", status=status)
    for lang in langs:
        for level in "LBR":
            Rendering.objects.create(sentence=s, language=lang, level=level, text="x")
    return s


@override_settings(OWB_SITE_URL=SITE, CORS_ALLOWED_ORIGINS=[SITE], OWB_SUPER_ADMIN_EMAILS=[],
                   OWB_GITHUB_TOKEN="", EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AdminTestCase(TestCase):
    def setUp(self):
        self.boss = account("boss@example.org", (K.SUPER_ADMIN,))
        self.admin = client_for(self.boss)


class AccessTest(AdminTestCase):
    def test_every_admin_endpoint_names_an_area(self):
        routes = admin_routes()
        self.assertGreater(len(routes), 10)
        for pattern, view in routes:
            self.assertIn(getattr(view, "admin_area", None), AREAS, f"{pattern} has no admin area")

    def test_signed_out_is_401_and_a_reader_is_403_everywhere(self):
        reader = client_for(account("reader@example.org"))
        for pattern, view in admin_routes():
            path = "/api/admin/" + pattern.replace("<str:code>", "JHN").replace("<int:message_id>", "1") \
                .replace("<int:user_id>", "1").replace("<int:role_id>", "1")
            allowed = [m.lower() for m in view.cls().allowed_methods if m not in ("OPTIONS",)]
            method = allowed[0]
            self.assertEqual(getattr(APIClient(), method)(path).status_code, 401, path)
            self.assertEqual(getattr(reader, method)(path).status_code, 403, path)

    def test_roles_open_their_areas(self):
        cases = {
            K.EDITOR: ["overview", "inbox"],
            K.REPORTING: ["overview"],
            K.USERS: ["overview", "users"],
            K.EMAIL: ["overview", "email"],
            K.SUPER_ADMIN: list(AREAS),
        }
        for kind, expected in cases.items():
            user = account(f"{kind}@example.org", (kind,))
            me = client_for(user).get("/api/me").json()
            self.assertEqual(me["admin"], expected, kind)
        reviewer = account("fr@example.org", (K.LANGUAGE_REVIEWER, "fr"))
        self.assertEqual(client_for(reviewer).get("/api/me").json()["admin"], ["overview"])
        self.assertEqual(client_for(account("r@example.org")).get("/api/me").json()["admin"], [])

    def test_an_editor_cannot_open_the_team(self):
        editor = client_for(account("ed@example.org", (K.EDITOR,)))
        self.assertEqual(editor.get("/api/admin/inbox/").status_code, 200)
        self.assertEqual(editor.get("/api/admin/team/").status_code, 403)
        self.assertEqual(editor.get("/api/admin/users/").status_code, 403)


class ProgressTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        for v in range(1, 4):
            sentence(f"PHM.1.{v}.s1", ("en", "fr"))   # Philemon: one chapter, so wholly drafted
        sentence("JHN.1.1.s1", ("en",))
        sentence("JHN.1.2.s1", ("en", "fr"))
        Decision.objects.create(sentence=Sentence.objects.get(record_id="JHN.1.2.s1"), key="r-fr-1", order=0,
                                layer="rendering", language="fr", category="word_choice", choice="x",
                                reason="x", uncertain=True)

    def test_coverage(self):
        books = {b["code"]: b for b in self.admin.get("/api/admin/coverage/").json()["books"]}
        self.assertEqual(len(books), 66)
        self.assertEqual(books["PHM"]["languages"]["en"]["state"], "drafted")
        self.assertEqual(books["PHM"]["languages"]["fr"]["state"], "drafted")
        self.assertEqual(books["PHM"]["languages"]["es"]["state"], "none")
        self.assertEqual(books["JHN"]["languages"]["en"]["state"], "partial")   # 1 of 21 chapters
        self.assertEqual(books["JHN"]["languages"]["fr"], {"sentences": 1, "state": "partial"})
        self.assertEqual(books["JHN"]["statuses"], {"ai_draft": 2})
        self.assertEqual(books["GEN"]["sentences"], 0)

    def test_languages(self):
        data = self.admin.get("/api/admin/languages/").json()
        fr = next(row for row in data["languages"] if row["code"] == "fr")
        self.assertEqual((fr["sentences"], fr["of"], fr["books_drafted"], fr["books_partial"]), (4, 5, 1, 1))
        self.assertEqual(fr["uncertain"], 1)
        self.assertEqual(fr["style_brief"], "docs/french-style.md")

    def test_book(self):
        data = self.admin.get("/api/admin/books/jhn/").json()
        self.assertEqual(len(data["chapters"]), 21)
        self.assertEqual(data["chapters"][0]["sentences"], 2)
        self.assertEqual(data["chapters"][0]["languages"]["fr"], 1)
        self.assertEqual(data["uncertain"], {"fr": 1})
        self.assertEqual(self.admin.get("/api/admin/books/XYZ/").status_code, 404)

    def test_overview(self):
        ReaderMessage.objects.create(user=self.boss, kind="question", verse="JHN.1.1", language="en", text="Why?")
        account("pending@example.org", (K.EDITOR,))
        data = self.admin.get("/api/admin/overview/").json()
        self.assertEqual(data["totals"]["sentences"], 5)
        self.assertEqual(data["totals"]["books_drafted"], 1)
        keys = {a["key"]: a["count"] for a in data["attention"]}
        self.assertEqual(keys["inbox"], 1)
        self.assertEqual(keys["books"], 64)
        self.assertEqual(keys["invites"], 2)   # boss has never signed in either
        # Someone with reporting only sees nothing about the inbox or the team.
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        keys = {a["key"] for a in reporter.get("/api/admin/overview/").json()["attention"]}
        self.assertNotIn("inbox", keys)
        self.assertNotIn("invites", keys)

    def test_health_lists_import_runs(self):
        with self.assertRaises(CommandError):
            call_command("import_content", str(settings.REPO_ROOT / "content" / "PHM" / "PHM.1.json"),
                         stdout=io.StringIO(),
                         stderr=io.StringIO())
        run = ImportRun.objects.get()
        self.assertTrue(run.finished_at)
        self.assertIn("not in the database", run.error)
        with mock.patch("staff.progress._ci_status", return_value=None):
            data = self.admin.get("/api/admin/health/").json()
        self.assertFalse(data["imports"][0]["ok"])
        self.assertEqual(data["sentences"], 5)
        self.assertEqual(data["editions"][0]["code"], "sblgnt")

    def test_engagement_counts_only(self):
        reader = account("reader@example.org")
        Mark.objects.create(user=reader, verse="JHN.3.16", bookmark=True, lang="en", updated_at=1)
        Mark.objects.create(user=reader, verse="JHN.3.17", highlight="yellow", lang="en", updated_at=1)
        data = self.admin.get("/api/admin/engagement/").json()
        self.assertEqual(data["marks"], {"bookmarks": 1, "highlights": 1, "readers": 1})
        self.assertEqual(data["marks_by_book"], [{"code": "JHN", "name": "John", "marks": 2}])
        self.assertNotIn("reader@example.org", json.dumps(data))


class TeamTest(AdminTestCase):
    def test_grant_invites_and_logs(self):
        r = self.admin.post("/api/admin/team/", {"email": "New@Example.org", "kind": "language_reviewer",
                                                 "language": "fr"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertTrue(r.json()["invited"])
        self.assertEqual(mail.outbox[-1].to, ["new@example.org"])
        self.assertIn(f"{SITE}/login/?redirect=/admin/", mail.outbox[-1].body)
        role = Role.objects.get(user__username="new@example.org")
        self.assertEqual((role.kind, role.language, role.granted_by), ("language_reviewer", "fr", self.boss))
        self.assertEqual(AdminAction.objects.filter(action="role.grant").count(), 1)
        again = self.admin.post("/api/admin/team/", {"email": "new@example.org", "kind": "language_reviewer",
                                                     "language": "fr"}, format="json")
        self.assertEqual(again.status_code, 409)

    def test_grant_checks_the_language(self):
        for body in ({"email": "a@example.org", "kind": "editor", "language": "fr"},
                     {"email": "a@example.org", "kind": "scholar_reviewer"},
                     {"email": "a@example.org", "kind": "super_admin"},
                     {"email": "nope", "kind": "editor"}):
            self.assertEqual(self.admin.post("/api/admin/team/", body, format="json").status_code, 400, body)
        self.assertFalse(User.objects.filter(username="a@example.org").exists())

    def test_revoke(self):
        user = account("ed@example.org", (K.EDITOR,))
        role = user.roles.get()
        self.assertEqual(self.admin.delete(f"/api/admin/team/roles/{role.id}/").status_code, 204)
        self.assertFalse(Role.objects.filter(id=role.id).exists())
        boss_role = self.boss.roles.get()
        self.assertEqual(self.admin.delete(f"/api/admin/team/roles/{boss_role.id}/").status_code, 400)
        data = self.admin.get("/api/admin/activity/").json()
        self.assertEqual(data["actions"][0]["action"], "role.revoke")

    def test_team_lists_members_and_grantable_roles(self):
        account("ed@example.org", (K.EDITOR,), (K.LANGUAGE_REVIEWER, "en"))
        data = self.admin.get("/api/admin/team/").json()
        self.assertEqual([m["email"] for m in data["members"]], ["boss@example.org", "ed@example.org"])
        self.assertEqual(len(data["members"][1]["roles"]), 2)
        self.assertNotIn("super_admin", [g["kind"] for g in data["grantable"]])

    def test_resend(self):
        account("ed@example.org", (K.EDITOR,))
        r = self.admin.post("/api/admin/team/invite/", {"email": "ed@example.org"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(mail.outbox[-1].to, ["ed@example.org"])
        r = self.admin.post("/api/admin/team/invite/", {"email": "nobody@example.org"}, format="json")
        self.assertEqual(r.status_code, 404)


class UsersTest(AdminTestCase):
    def test_list_search_and_detail(self):
        reader = account("reader@example.org")
        reader.first_name = "Ruth"
        reader.save()
        Mark.objects.create(user=reader, verse="RUT.1.16", bookmark=True, updated_at=1)
        viewer = client_for(account("helper@example.org", (K.USERS,)))
        data = viewer.get("/api/admin/users/?q=ruth").json()
        self.assertEqual([u["email"] for u in data["users"]], ["reader@example.org"])
        self.assertEqual(data["users"][0]["marks"], 1)
        team = viewer.get("/api/admin/users/?role=any").json()
        self.assertEqual({u["email"] for u in team["users"]}, {"boss@example.org", "helper@example.org"})
        detail = viewer.get(f"/api/admin/users/{reader.id}/").json()
        self.assertEqual(detail["marks"], {"bookmarks": 1, "highlights": 0})
        self.assertFalse(detail["can_delete"])
        # Only a super admin deletes.
        self.assertEqual(viewer.delete(f"/api/admin/users/{reader.id}/").status_code, 403)
        self.assertEqual(self.admin.delete(f"/api/admin/users/{reader.id}/").status_code, 204)
        self.assertFalse(User.objects.filter(username="reader@example.org").exists())
        self.assertEqual(AdminAction.objects.get(action="user.delete").target, "reader@example.org")

    def test_super_admins_and_yourself_are_not_deleted_here(self):
        other = account("boss2@example.org", (K.SUPER_ADMIN,))
        self.assertEqual(self.admin.delete(f"/api/admin/users/{other.id}/").status_code, 400)
        self.assertEqual(self.admin.delete(f"/api/admin/users/{self.boss.id}/").status_code, 400)

    def test_sign_out_everywhere(self):
        reader = account("reader@example.org")
        client_for(reader)
        client_for(reader)
        r = self.admin.post(f"/api/admin/users/{reader.id}/sign-out/")
        self.assertEqual(r.json(), {"signed_out": 2})
        self.assertFalse(ApiToken.objects.filter(user=reader).exists())


class MessagesTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.reader_user = account("reader@example.org")
        self.reader = client_for(self.reader_user)

    def send(self, **body):
        body = {"kind": "suggestion", "verse": "JHN.1.1", "lang": "fr", "level": "B",
                "text": "La Parole ?", **body}
        return self.reader.post("/api/messages", body, format="json")

    def test_a_reader_sends_and_sees_their_messages(self):
        self.assertEqual(APIClient().post("/api/messages", {}, format="json").status_code, 401)
        self.assertEqual(self.send().status_code, 201)
        for bad in ({"verse": "JHN.1"}, {"verse": "XYZ.1.1"}, {"kind": "praise"}, {"text": " "},
                    {"text": "x" * 2001}):
            self.assertEqual(self.send(**bad).status_code, 400, bad)
        mine = self.reader.get("/api/messages").json()
        self.assertEqual([m["verse"] for m in mine], ["JHN.1.1"])

    def test_rate_limit(self):
        for _ in range(10):
            self.assertEqual(self.send().status_code, 201)
        self.assertEqual(self.send().status_code, 429)

    def test_an_editor_answers_by_email_once(self):
        self.send()
        editor_user = account("ed@example.org", (K.EDITOR,))
        editor_user.first_name = "Priscilla"
        editor_user.save()
        editor = client_for(editor_user)
        data = editor.get("/api/admin/inbox/").json()
        self.assertEqual(data["counts"]["new"], 1)
        m = data["messages"][0]
        self.assertEqual((m["verse_label"], m["from"]["email"]), ("John 1:1", "reader@example.org"))
        self.assertEqual(m["url"], f"{SITE}/fr/jhn/1/#v1")
        r = editor.patch(f"/api/admin/inbox/{m['id']}/", {"reply": "Merci ! Bonne question."}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "answered")
        self.assertEqual(mail.outbox[-1].to, ["reader@example.org"])
        self.assertIn("Priscilla replied", mail.outbox[-1].body)
        self.assertIn("> La Parole ?", mail.outbox[-1].body)
        again = editor.patch(f"/api/admin/inbox/{m['id']}/", {"reply": "Again"}, format="json")
        self.assertEqual(again.status_code, 400)
        r = editor.patch(f"/api/admin/inbox/{m['id']}/", {"status": "done"}, format="json")
        self.assertEqual(r.json()["status"], "done")
        self.assertEqual(editor.get("/api/admin/inbox/?status=done").json()["total"], 1)
        self.assertEqual(self.reader.get("/api/messages").json()[0]["reply"], "Merci ! Bonne question.")

    def test_answering_needs_a_reply(self):
        self.send()
        m = ReaderMessage.objects.get()
        r = self.admin.patch(f"/api/admin/inbox/{m.id}/", {"status": "answered"}, format="json")
        self.assertEqual(r.status_code, 400)
        r = self.admin.patch(f"/api/admin/inbox/{m.id}/", {"status": "declined", "note": "duplicate"},
                             format="json")
        self.assertEqual(r.json()["status"], "declined")


class JobsTest(AdminTestCase):
    def test_not_configured(self):
        with mock.patch.object(staff_jobs, "open_jobs", return_value=[]):
            data = self.admin.get("/api/admin/jobs/").json()
        self.assertFalse(data["configured"])
        r = self.admin.post("/api/admin/jobs/", {"book": "EZK", "languages": ["en"]}, format="json")
        self.assertEqual(r.status_code, 503)

    @override_settings(OWB_GITHUB_TOKEN="t")
    def test_file_a_job(self):
        sentence("PHM.1.1.s1", ("en",))
        calls = []

        def github(path, method="GET", body=None):
            calls.append((path, method, body))
            if method == "POST":
                return {"number": 7, "html_url": "https://github.com/x/y/issues/7"}
            return [{"number": 5, "title": "t", "html_url": "u", "created_at": "2026-10-15T00:00:00Z",
                     "body": 'x\n<!-- drafting-job {"book": "EZK", "languages": ["en"]} -->'}]
        with mock.patch.object(staff_jobs, "_github", side_effect=github):
            self.assertEqual(self.admin.get("/api/admin/jobs/").json()["jobs"][0]["book"], "EZK")
            dup = self.admin.post("/api/admin/jobs/", {"book": "EZK", "languages": ["en"]}, format="json")
            self.assertEqual(dup.json()["code"], "duplicate")
            first = self.admin.post("/api/admin/jobs/", {"book": "DAN", "languages": ["fr"]}, format="json")
            self.assertEqual(first.json()["code"], "english_first")
            done = self.admin.post("/api/admin/jobs/", {"book": "PHM", "languages": ["en"]}, format="json")
            self.assertEqual(done.json()["code"], "already_drafted")
            r = self.admin.post("/api/admin/jobs/", {"book": "PHM", "languages": ["fr", "es"], "note": "Soon"},
                                format="json")
        self.assertEqual(r.status_code, 201, r.content)
        path, method, body = calls[-1]
        self.assertEqual((path, method, body["labels"]), ("issues", "POST", ["drafting-job"]))
        self.assertEqual(body["title"], "Draft Philemon in Spanish, French")
        self.assertIn('<!-- drafting-job {"book": "PHM", "languages": ["es", "fr"]} -->', body["body"])
        self.assertEqual(AdminAction.objects.get(action="job.file").target, "#7 PHM")


class EmailTest(AdminTestCase):
    def test_test_then_send_to_a_role(self):
        account("ed1@example.org", (K.EDITOR,))
        account("ed2@example.org", (K.EDITOR,))
        account("reader@example.org")
        sender = client_for(account("mail@example.org", (K.EMAIL,)))
        data = sender.get("/api/admin/emails/").json()
        counts = {a["key"]: a["count"] for a in data["audiences"]}
        self.assertEqual((counts["team"], counts["editor"]), (4, 2))
        body = {"subject": "Hello team", "body": "News.", "audience": "editor"}
        r = sender.post("/api/admin/emails/", {**body, "test": True}, format="json")
        self.assertEqual(r.json(), {"test": True, "sent": 1})
        self.assertEqual((mail.outbox[-1].to, mail.outbox[-1].subject), (["mail@example.org"], "[Test] Hello team"))
        self.assertFalse(Broadcast.objects.exists())
        r = sender.post("/api/admin/emails/", body, format="json")
        self.assertEqual(r.json()["sent"], 2)
        self.assertEqual(sorted(m.to[0] for m in mail.outbox[1:]), ["ed1@example.org", "ed2@example.org"])
        self.assertIn("Open Word Bible team (editors)", mail.outbox[-1].body)
        self.assertEqual(Broadcast.objects.get().recipients, 2)

    def test_validation(self):
        for body in ({"subject": "", "body": "x", "audience": "team"},
                     {"subject": "a\nb", "body": "x", "audience": "team"},
                     {"subject": "s", "body": "", "audience": "team"},
                     {"subject": "s", "body": "x", "audience": "readers"}):
            self.assertEqual(self.admin.post("/api/admin/emails/", body, format="json").status_code, 400, body)


class VerseTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.s1 = sentence("JHN.1.1.s1", ("en", "fr"))
        self.s2 = sentence("JHN.1.2.s1", ("en",))
        Decision.objects.create(sentence=self.s1, key="m1", order=0, layer="meaning", category="allusion",
                                choice="In the beginning", reason="Genesis 1:1", footnote=True)
        ContentFile.objects.create(path="content/JHN/JHN.1.1-18.json", digest="x")
        ContentFile.objects.create(path="content/JHN/JHN.3.json", digest="x")

    def test_covers(self):
        self.assertTrue(covers("content/JHN/JHN.3.json", 3, 16))
        self.assertFalse(covers("content/JHN/JHN.3.json", 4, 1))
        self.assertTrue(covers("content/JHN/JHN.1.1-18.json", 1, 18))
        self.assertFalse(covers("content/JHN/JHN.1.1-18.json", 1, 19))
        self.assertTrue(covers("content/JHN/JHN.7.53-8.11.json", 8, 2))
        self.assertTrue(covers("content/JHN/JHN.7.53-8.11.json", 7, 53))
        self.assertFalse(covers("content/JHN/JHN.7.53-8.11.json", 7, 52))
        self.assertTrue(covers("content/1JN/1JN.1.json", 1, 1))

    def test_a_verse_whole(self):
        ReaderMessage.objects.create(user=self.boss, kind="question", verse="JHN.1.1", language="fr", text="?")
        data = self.admin.get("/api/admin/verses/jhn.1.1/").json()
        self.assertEqual((data["verse"], data["label"]), ("JHN.1.1", "John 1:1"))
        record = data["records"][0]
        self.assertEqual(record["id"], "JHN.1.1.s1")
        self.assertEqual(sorted(record["renderings"]), ["en", "fr"])
        self.assertEqual(record["decisions"][0]["choice"], "In the beginning")
        self.assertEqual(data["files"], {"JHN.1.1.s1": "content/JHN/JHN.1.1-18.json"})
        self.assertEqual(data["neighbours"], [None, "JHN.1.2"])
        self.assertEqual(len(data["messages"]), 1)
        # Reporting sees the text, not who wrote in.
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        self.assertNotIn("messages", reporter.get("/api/admin/verses/JHN.1.1/").json())
        self.assertEqual(self.admin.get("/api/admin/verses/nonsense/").status_code, 404)

    def test_find(self):
        self.assertEqual(self.admin.get("/api/admin/verses/?q=JHN.1.2").json(), {"verse": "JHN.1.2"})
        self.assertEqual(self.admin.get("/api/admin/verses/?q=no such").status_code, 400)


class FixTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.s = sentence("JHN.1.1.s1", ("en", "fr"))
        ContentFile.objects.create(path="content/JHN/JHN.1.1-18.json", digest="x")
        self.body = {"record": "JHN.1.1.s1", "verse": "JHN.1.1", "language": "fr", "levels": ["B", "R"],
                     "change": "Use la Parole", "reason": "Readers hear grammar in le Verbe"}

    def test_not_configured_and_only_for_the_inbox(self):
        self.assertEqual(self.admin.post("/api/admin/fixes/", self.body, format="json").status_code, 503)
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        self.assertEqual(reporter.post("/api/admin/fixes/", self.body, format="json").status_code, 403)

    @override_settings(OWB_GITHUB_TOKEN="t")
    def test_file_a_fix_from_a_reader_message(self):
        reader = account("reader@example.org")
        message = ReaderMessage.objects.create(user=reader, kind="suggestion", verse="JHN.1.1", language="fr",
                                               text="La Parole, s'il vous plaît")
        calls = []

        def github(path, method="GET", body=None):
            calls.append((path, method, body))
            if method == "POST":
                return {"number": 9, "html_url": "https://github.com/x/y/issues/9"}
            return [{"number": 9, "title": "t", "html_url": "u", "created_at": "2026-10-16T00:00:00Z",
                     "body": 'x\n<!-- fix-request {"record": "JHN.1.1.s1", "verse": "JHN.1.1", "language": "fr"} -->'}]
        editor = client_for(account("ed@example.org", (K.EDITOR,)))
        with mock.patch.object(staff_jobs, "_github", side_effect=github):
            bad = editor.post("/api/admin/fixes/", {**self.body, "language": "es"}, format="json")
            self.assertEqual(bad.json()["code"], "not_drafted")
            r = editor.post("/api/admin/fixes/", {**self.body, "message": message.id}, format="json")
            self.assertEqual(r.status_code, 201, r.content)
            listed = editor.get("/api/admin/fixes/").json()
        self.assertEqual(listed["fixes"][0]["record"], "JHN.1.1.s1")
        path, method, body = calls[-2]
        self.assertEqual((path, method, body["labels"]), ("issues", "POST", ["fix-request"]))
        self.assertEqual(body["title"], "Fix John 1:1 (French): Use la Parole")
        self.assertIn("**File:** `content/JHN/JHN.1.1-18.json`", body["body"])
        self.assertIn("- Balanced: x", body["body"])
        self.assertNotIn("- Literal:", body["body"])
        self.assertIn("> La Parole, s'il vous plaît", body["body"])
        self.assertIn(f'"message": {message.id}', body["body"])
        message.refresh_from_db()
        self.assertEqual(message.note, "Fix requested: #9")
        action = AdminAction.objects.get(action="fix.request")
        self.assertEqual((action.target, action.detail["verse"]), ("#9 JHN.1.1.s1", "JHN.1.1"))
        # The inspector lists it.
        fixes = editor.get("/api/admin/verses/JHN.1.1/").json()["fixes"]
        self.assertEqual(fixes[0]["number"], 9)
