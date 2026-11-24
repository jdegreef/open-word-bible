"""The admin's own times, kept for Health (staff/speed.py)."""
from datetime import UTC, datetime, timedelta
from unittest import mock

from django.core.cache import cache

from staff import speed

from .test_admin import AdminTestCase


class SpeedLogTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_slowest_first_over_the_last_day(self):
        now = datetime(2026, 11, 23, 12, tzinfo=UTC)
        speed.note("api/admin/coverage/", 0.4, 200, now=now)
        speed.note("api/admin/coverage/", 6.0, 200, now=now - timedelta(hours=3))
        speed.note("api/admin/terms/", 1.0, 200, now=now)
        speed.note("api/admin/old/", 9.0, 200, now=now - timedelta(hours=30))   # over a day ago
        rows = speed.slowest(now=now)
        self.assertEqual([r["route"] for r in rows], ["/api/admin/coverage/", "/api/admin/terms/"])
        self.assertEqual(rows[0], {"route": "/api/admin/coverage/", "requests": 2, "average_ms": 3200,
                                   "max_ms": 6000, "slow": 1, "errors": 0})

    def test_failures_come_first(self):
        speed.note("api/admin/a/", 9.0, 200)
        speed.note("api/admin/b/", 0.1, 503)
        self.assertEqual([r["route"] for r in speed.slowest()], ["/api/admin/b/", "/api/admin/a/"])

    def test_admin_reads_are_kept_by_pattern_and_shown_on_health(self):
        self.admin.get("/api/admin/verses/JHN.3.16/")
        self.admin.get("/api/admin/verses/JHN.3.17/")
        self.admin.post("/api/admin/review/x/", {}, format="json")   # not a read: not kept
        rows = {r["route"]: r for r in self.admin.get("/api/admin/health/").json()["speed"]}
        self.assertEqual(rows["/api/admin/verses/<str:vid>/"]["requests"], 2)
        self.assertFalse([r for r in rows if "review" in r])

    def test_a_cache_failure_never_fails_the_page(self):
        with mock.patch("staff.speed.note", side_effect=OSError("cache down")), \
                self.assertLogs("config.middleware", "WARNING"):
            self.assertEqual(self.admin.get("/api/admin/coverage/").status_code, 200)
