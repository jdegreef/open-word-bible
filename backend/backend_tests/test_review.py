"""Review in the admin (staff/review.py) and what each import changed
(staff/changes.py, SentenceChange)."""
import importlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

from django.apps import apps
from django.conf import settings
from django.db import connection
from django.test import SimpleTestCase
from django.test.utils import CaptureQueriesContext

from backend_tests.test_admin import K, AdminTestCase, account, client_for, sentence
from backend_tests.test_backend import CONTENT, import_content, load_extract_words
from staff import review
from texts.models import Edition
from translation.models import ImportRun, Rendering, ReviewEvent, ReviewState, Sentence, SentenceChange


def hebrew(record_id):
    wlc = Edition.objects.get_or_create(
        code="wlc", defaults=dict(name="WLC", language="hbo", kind="original", licence="Public domain",
                                  source="macula-hebrew", source_commit="0" * 40))[0]
    return sentence(record_id, ("en",), edition=wlc)


class ReviewTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        sentence("JHN.1.1.s1", ("en", "fr"))
        sentence("JHN.1.2.s1", ("en",))
        hebrew("GEN.1.1.s1")
        self.scholar = client_for(account("grc@example.org", (K.SCHOLAR_REVIEWER, "grc")))
        self.french = client_for(account("fr@example.org", (K.LANGUAGE_REVIEWER, "fr")))
        self.editor = client_for(account("ed@example.org", (K.EDITOR,)))

    def act(self, client, record, layer, action="approve", note=""):
        return client.post(f"/api/admin/review/{record}/", {"layer": layer, "action": action, "note": note},
                           format="json")

    def test_reviewers_open_review_and_editors_do_not(self):
        self.assertEqual(self.french.get("/api/me").json()["admin"], ["overview", "export", "review"])
        self.assertEqual(self.editor.get("/api/admin/review/").status_code, 403)

    def test_each_reviewer_has_their_own_layer(self):
        data = self.scholar.get("/api/admin/review/").json()
        self.assertEqual([lay["code"] for lay in data["layers"]], ["grc"])
        self.assertEqual([s["record"] for s in data["sentences"]], ["JHN.1.1.s1", "JHN.1.2.s1"])
        self.assertEqual(self.scholar.get("/api/admin/review/?layer=fr").status_code, 403)
        data = self.french.get("/api/admin/review/").json()
        self.assertEqual(data["layer"]["code"], "fr")
        self.assertEqual([s["record"] for s in data["sentences"]], ["JHN.1.1.s1"])
        self.assertEqual(self.act(self.scholar, "JHN.1.1.s1", "fr").status_code, 403)
        self.assertEqual(self.act(self.scholar, "GEN.1.1.s1", "hbo").status_code, 403)
        self.assertEqual(self.act(self.scholar, "GEN.1.1.s1", "grc").status_code, 400)   # not in the NT layer
        self.assertEqual(self.act(self.french, "JHN.1.2.s1", "fr").status_code, 400)     # not drafted in French
        # A super admin may review any layer, Hebrew meaning included.
        self.assertEqual(self.act(self.admin, "GEN.1.1.s1", "hbo").status_code, 201)
        self.assertFalse(ReviewEvent.objects.exclude(user__username="boss@example.org").exists())

    def test_approving_the_meaning(self):
        before = Sentence.objects.get(record_id="JHN.1.1.s1").updated_at
        r = self.act(self.scholar, "JHN.1.1.s1", "grc")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["next"], "JHN.1.2.s1")
        s = Sentence.objects.get(record_id="JHN.1.1.s1")
        self.assertEqual((s.status, s.updated_at), ("meaning_reviewed", before))
        event = ReviewEvent.objects.get()
        self.assertEqual((event.action, event.language, event.user.username),
                         ("meaning_reviewed", "", "grc@example.org"))
        counts = self.scholar.get("/api/admin/review/").json()["counts"]
        self.assertEqual((counts["approved"], counts["not_reviewed"]), (1, 1))
        # The dashboard's status counts see it at once.
        statuses = self.admin.get("/api/admin/overview/").json()["totals"]["statuses"]
        self.assertEqual(statuses["meaning_reviewed"], 1)
        todo = self.scholar.get("/api/admin/review/?state=todo").json()["sentences"]
        self.assertEqual([s["record"] for s in todo], ["JHN.1.2.s1"])

    def test_wording_approval_is_per_language_and_goes_stale(self):
        self.assertEqual(self.act(self.french, "JHN.1.1.s1", "fr").status_code, 201)
        self.assertEqual(self.act(self.admin, "JHN.1.1.s1", "en").status_code, 201)
        self.assertEqual(Sentence.objects.get(record_id="JHN.1.1.s1").status, "ai_draft")

        def state(client, layer):
            return client.get(f"/api/admin/review/JHN.1.1.s1/?layer={layer}").json()["state"]
        self.assertEqual(state(self.french, "fr"), "approved")
        # An import rewrites the French (and saves the sentence, as it does).
        s = Sentence.objects.get(record_id="JHN.1.1.s1")
        s.renderings.filter(language="fr", level="B").update(text="nouveau")
        s.save()
        self.assertEqual(state(self.french, "fr"), "changed")
        self.assertEqual(state(self.admin, "en"), "approved")
        trail = self.french.get("/api/admin/review/JHN.1.1.s1/?layer=fr").json()["trail"]
        self.assertEqual([(e["language"], e["changed"]) for e in trail], [("en", False), ("fr", True)])
        self.assertEqual(self.french.get("/api/admin/review/?state=changed").json()["counts"]["changed"], 1)

    def test_flags_reach_editors_until_approved_again(self):
        self.assertEqual(self.act(self.french, "JHN.1.1.s1", "fr", "flag").status_code, 400)   # needs a note
        self.assertEqual(self.act(self.french, "JHN.1.1.s1", "fr", "flag", "« Verbe » is dated").status_code, 201)
        flags = self.editor.get("/api/admin/review/flags/").json()["flags"]
        self.assertEqual([(f["record"], f["layer"]["code"], f["note"]) for f in flags],
                         [("JHN.1.1.s1", "fr", "« Verbe » is dated")])
        chips = {a["key"]: a["count"] for a in self.editor.get("/api/admin/overview/").json()["attention"]}
        self.assertEqual(chips["flags"], 1)
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        self.assertNotIn("flags", {a["key"] for a in reporter.get("/api/admin/overview/").json()["attention"]})
        self.assertEqual(self.french.get("/api/admin/review/").json()["counts"]["flagged"], 1)
        self.act(self.french, "JHN.1.1.s1", "fr", "comment", "Asked the editors")
        self.assertEqual(len(self.editor.get("/api/admin/review/flags/").json()["flags"]), 1)
        self.act(self.french, "JHN.1.1.s1", "fr")
        self.assertEqual(self.editor.get("/api/admin/review/flags/").json()["flags"], [])


class QueueOrderTest(AdminTestCase):
    """The queue is put in Bible order, filtered and paged in the database;
    "next" is one query; ReviewState follows the trail without rebuilding a
    layer."""

    def setUp(self):
        super().setUp()
        # Made out of order: Acts sorts before John alphabetically, chapter 10
        # before chapter 2 as text.
        for rid in ("REV.1.1.s1", "ACT.1.1.s1", "JHN.10.1.s1", "JHN.2.1.s1", "JHN.2.1.s2", "MAT.1.1.s1"):
            sentence(rid, ("en",))
        self.reviewer = client_for(account("en@example.org", (K.LANGUAGE_REVIEWER, "en")))
        self.order = ["MAT.1.1.s1", "JHN.2.1.s1", "JHN.2.1.s2", "JHN.10.1.s1", "ACT.1.1.s1", "REV.1.1.s1"]

    def records(self, query=""):
        return [s["record"] for s in self.reviewer.get(f"/api/admin/review/?layer=en{query}").json()["sentences"]]

    def act(self, record, action="approve", note=""):
        r = self.reviewer.post(f"/api/admin/review/{record}/", {"layer": "en", "action": action, "note": note},
                               format="json")
        self.assertEqual(r.status_code, 201)
        return r.json()

    def test_bible_order_and_books(self):
        self.assertEqual(self.records(), self.order)
        data = self.reviewer.get("/api/admin/review/?layer=en").json()
        self.assertEqual([b["code"] for b in data["books"]], ["MAT", "JHN", "ACT", "REV"])
        self.assertEqual(self.records("&book=jhn"), self.order[1:4])
        self.assertEqual(self.records("&book=JHN&chapter=2"), self.order[1:3])
        self.assertEqual(list(Sentence.objects.order_by("book_order").values_list("book", flat=True).distinct()),
                         ["MAT", "JHN", "ACT", "REV"])

    def test_paging_and_state_filters(self):
        self.act("JHN.2.1.s1")
        self.act("ACT.1.1.s1", "flag", "Wrong word")
        with mock.patch("staff.review.PAGE", 2):
            first = self.reviewer.get("/api/admin/review/?layer=en").json()
            self.assertEqual([s["record"] for s in first["sentences"]], self.order[:2])
            self.assertEqual((first["more"], first["matching"], first["offset"]), (True, 6, 0))
            last = self.reviewer.get("/api/admin/review/?layer=en&offset=4").json()
            self.assertEqual([s["record"] for s in last["sentences"]], self.order[4:])
            self.assertFalse(last["more"])
            todo = self.reviewer.get("/api/admin/review/?layer=en&state=todo&offset=2").json()
            self.assertEqual([s["record"] for s in todo["sentences"]], ["JHN.10.1.s1", "ACT.1.1.s1"])
            self.assertEqual((todo["matching"], todo["more"]), (5, True))
        self.assertEqual(self.records("&state=approved"), ["JHN.2.1.s1"])
        self.assertEqual(self.records("&state=flagged"), ["ACT.1.1.s1"])
        self.assertEqual(self.records("&state=not_reviewed"), [r for r in self.order if r not in
                                                               ("JHN.2.1.s1", "ACT.1.1.s1")])
        data = self.reviewer.get("/api/admin/review/?layer=en").json()
        self.assertEqual(data["counts"], {"not_reviewed": 4, "approved": 1, "changed": 0, "flagged": 1, "total": 6})
        rows = {s["record"]: s for s in data["sentences"]}
        self.assertEqual((rows["ACT.1.1.s1"]["state"], rows["ACT.1.1.s1"]["last"]["note"]), ("flagged", "Wrong word"))
        self.assertEqual(rows["JHN.2.1.s1"]["last"]["action"], "reviewed")
        self.assertIsNone(rows["MAT.1.1.s1"]["last"])
        self.assertEqual(self.reviewer.get("/api/admin/review/?layer=en&state=nope").status_code, 400)

    def test_queries_do_not_grow_with_the_layer(self):
        self.act("MAT.1.1.s1")
        self.records()

        def count():
            with CaptureQueriesContext(connection) as ctx:
                self.records()
            return len(ctx.captured_queries)
        few = count()
        for v in range(1, 40):
            sentence(f"LUK.1.{v}.s1", ("en",))
        self.act("LUK.1.3.s1")
        self.records()
        self.assertEqual(count(), few)

    def test_next_skips_approved_and_crosses_books(self):
        self.act("JHN.10.1.s1")
        self.assertEqual(self.act("MAT.1.1.s1")["next"], "JHN.2.1.s1")
        self.assertEqual(self.act("JHN.2.1.s1")["next"], "JHN.2.1.s2")
        self.assertEqual(self.act("JHN.2.1.s2")["next"], "ACT.1.1.s1")   # past the approved JHN 10
        self.assertEqual(self.act("ACT.1.1.s1", "flag", "Check")["next"], "REV.1.1.s1")
        self.assertIsNone(self.act("REV.1.1.s1")["next"])
        # From the sentence page too, in one query.
        s = Sentence.objects.get(record_id="JHN.2.1.s1")
        with CaptureQueriesContext(connection) as ctx:
            self.assertEqual(review._next("en", s), "ACT.1.1.s1")
        self.assertEqual(len(ctx.captured_queries), 1)
        self.assertEqual(self.reviewer.get("/api/admin/review/MAT.1.1.s1/?layer=en").json()["next"], "ACT.1.1.s1")

    def test_states_follow_the_trail(self):
        def state(record="JHN.2.1.s1"):
            return self.reviewer.get(f"/api/admin/review/{record}/?layer=en").json()["state"]
        self.assertEqual(state(), "not_reviewed")
        self.assertEqual(self.act("JHN.2.1.s1")["state"], "approved")
        self.assertEqual(self.act("JHN.2.1.s1", "comment", "Fine")["state"], "approved")
        self.assertEqual(self.act("JHN.2.1.s1", "flag", "Not fine")["state"], "flagged")
        self.assertEqual(self.act("JHN.2.1.s1", "comment", "Asked")["state"], "flagged")
        self.assertEqual(self.act("JHN.2.1.s1")["state"], "approved")
        # Deleting the latest approval (Django's admin may) goes back to the flag.
        ReviewEvent.objects.filter(action="reviewed").order_by("-id").first().delete()
        self.assertEqual(state(), "flagged")
        ReviewEvent.objects.all().delete()
        self.assertEqual(state(), "not_reviewed")
        self.assertFalse(ReviewState.objects.exists())

    def test_a_review_compares_nothing_again(self):
        self.act("JHN.2.1.s1")
        self.act("MAT.1.1.s1")
        self.records()
        with mock.patch("staff.review.digest", side_effect=review.digest) as digest:
            self.act("ACT.1.1.s1")      # the approval's own digest only
            self.records()
            self.assertEqual(digest.call_count, 1)
            # A sentence saved again, as an import saves the ones it changes,
            # is compared again; the others are not.
            s = Sentence.objects.get(record_id="JHN.2.1.s1")
            s.renderings.filter(level="B").update(text="changed")
            s.save()
            data = self.reviewer.get("/api/admin/review/?layer=en").json()
            self.assertEqual(digest.call_count, 2)
        self.assertEqual(data["counts"]["changed"], 1)
        self.assertEqual(self.records("&state=changed"), ["JHN.2.1.s1"])
        self.assertEqual(self.records("&state=todo"), [r for r in self.order if r not in
                                                       ("MAT.1.1.s1", "ACT.1.1.s1")])
        # Putting the text back makes it match its approval again.
        s.renderings.filter(level="B").update(text="x")
        s.save()
        self.assertEqual(self.records("&state=approved"), ["MAT.1.1.s1", "JHN.2.1.s1", "ACT.1.1.s1"])

    def test_dashboard_keeps_its_rendering_counts_after_a_review(self):
        self.admin.get("/api/admin/overview/")
        with mock.patch("staff.progress._count_by_book", side_effect=AssertionError("counted again")):
            self.act("JHN.2.1.s1", "flag", "Look")
            chips = {a["key"]: a["count"] for a in self.admin.get("/api/admin/overview/").json()["attention"]}
            self.assertEqual(chips["flags"], 1)
        self.assertEqual(review.open_flag_count(), 1)

    def test_migration_fills_states_from_the_trail(self):
        self.act("JHN.2.1.s1")
        self.act("ACT.1.1.s1")
        self.act("ACT.1.1.s1", "flag", "Look")
        self.act("MAT.1.1.s1", "comment", "Hm")
        greek = Sentence.objects.get(record_id="REV.1.1.s1")
        ReviewEvent.objects.create(sentence=greek, user=self.boss, action="meaning_reviewed", digest="old")
        ReviewState.objects.all().delete()
        migration = importlib.import_module("translation.migrations.0015_review_state_and_bible_order")
        migration.fill_review_states(apps, None)
        self.assertEqual(sorted(ReviewState.objects.values_list("sentence__record_id", "layer", "state")),
                         [("ACT.1.1.s1", "en", "flagged"), ("JHN.2.1.s1", "en", "approved"),
                          ("REV.1.1.s1", "grc", "approved")])
        # Unchecked until opened, when the Greek's old digest no longer matches.
        self.assertEqual(self.admin.get("/api/admin/review/REV.1.1.s1/?layer=grc").json()["state"], "changed")
        self.assertEqual(self.records("&state=approved"), ["JHN.2.1.s1"])


class CacheSettingsTest(SimpleTestCase):
    def cache_backend(self, **env):
        code = "from django.conf import settings; print(settings.CACHES['default']['BACKEND'])"
        env = {k: v for k, v in os.environ.items() if k != "REDIS_URL"} | {"DJANGO_DEBUG": "1"} | env
        out = subprocess.run([sys.executable, "-c", f"import django; django.setup(); {code}"], env=env,
                             cwd=settings.BASE_DIR, capture_output=True, text=True, check=True)
        return out.stdout.strip()

    def test_redis_when_configured(self):
        self.assertEqual(self.cache_backend(DJANGO_SETTINGS_MODULE="config.settings"),
                         "django.core.cache.backends.db.DatabaseCache")
        self.assertEqual(self.cache_backend(DJANGO_SETTINGS_MODULE="config.settings",
                                            REDIS_URL="redis://localhost:6379/0"),
                         "django.core.cache.backends.redis.RedisCache")


class ChangesTest(AdminTestCase):
    @classmethod
    def setUpTestData(cls):
        load_extract_words(("grc",), books=("PHM",))

    def test_import_records_changes_but_only_counts_first_drafts(self):
        path = CONTENT / "PHM" / "PHM.1.json"
        records = json.loads(path.read_text())["records"]
        import_content(str(path))
        run = ImportRun.objects.get()
        self.assertFalse(SentenceChange.objects.exists())
        self.assertEqual(run.drafted["PHM"]["en"], len(records))
        reviewer = client_for(account("en@example.org", (K.LANGUAGE_REVIEWER, "en")))
        reviewer.post("/api/admin/review/PHM.1.1.s1/", {"layer": "en", "action": "approve"}, format="json")

        data = json.loads(path.read_text())
        first = data["records"][0]
        old = first["renderings"]["en"]["B"]
        first["renderings"]["en"]["B"] = old + " Amen."
        first["renderings"]["fr"]["R"] += " Amen."
        with tempfile.TemporaryDirectory() as tmp:
            edited = Path(tmp) / "PHM.1.json"
            edited.write_text(json.dumps(data))
            import_content(str(edited))
        run = ImportRun.objects.first()
        self.assertEqual(run.drafted, {})
        self.assertEqual(sorted(SentenceChange.objects.values_list("record_id", "language", "level", "kind")),
                         [("PHM.1.1.s1", "en", "B", "changed"), ("PHM.1.1.s1", "fr", "R", "changed")])
        d = self.admin.get("/api/admin/changes/").json()
        self.assertEqual([r["changed"] for r in d["runs"]], [2, 0])
        self.assertEqual(d["run"]["id"], run.id)
        en = next(c for c in d["changes"] if c["language"] == "en")
        self.assertEqual((en["verse"], en["before"], en["after"]), ("PHM.1.1", old, old + " Amen."))
        self.assertEqual(len(self.admin.get(f"/api/admin/changes/?run={run.id}&lang=fr").json()["changes"]), 1)
        # The English approval no longer matches what the import brought.
        state = reviewer.get("/api/admin/review/PHM.1.1.s1/?layer=en").json()["state"]
        self.assertEqual(state, "changed")
        self.assertEqual(Rendering.objects.filter(sentence__record_id="PHM.1.1.s1", language="fr").count(), 3)
