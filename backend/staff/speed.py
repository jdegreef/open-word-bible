"""How long the admin's pages take on the live database, kept for a day so
Health can show the slowest before one creeps past the web server's 15 s
statement limit and fails. (The nightly check, check_admin_speed, times a
runner's copy of the content, whose database fits in memory.)

config.middleware.ServerTimingMiddleware calls note() for every admin GET.
The times go into one cache entry an hour, per address pattern (a verse or
book in the address is not told apart): requests, total and slowest time,
how many took over SLOW seconds and how many failed (5xx, a timeout among
them). Two requests finishing at the same moment on different workers can
lose one count; these are a gauge, not a ledger.
"""
from datetime import UTC, datetime, timedelta

from django.core.cache import cache

HOURS = 24
SLOW = 5.0     # seconds; the nightly check's limit


def _key(at):
    return "staff.speed." + at.strftime("%Y%m%d%H")


def note(route, seconds, status, now=None):
    """Count one answer to the admin address route ("api/admin/coverage/")."""
    key = _key(now or datetime.now(UTC))
    hour = cache.get(key) or {}
    r = hour.setdefault(route, {"n": 0, "total": 0.0, "max": 0.0, "slow": 0, "errors": 0})
    r["n"] += 1
    r["total"] += seconds
    r["max"] = max(r["max"], seconds)
    r["slow"] += seconds > SLOW
    r["errors"] += status >= 500
    cache.set(key, hour, (HOURS + 1) * 3600)


def slowest(limit=15, now=None):
    """The last HOURS' admin addresses, slowest first: [{"route", "requests",
    "average_ms", "max_ms", "slow", "errors"}]."""
    now = now or datetime.now(UTC)
    hours = cache.get_many([_key(now - timedelta(hours=h)) for h in range(HOURS)])
    merged = {}
    for hour in hours.values():
        for route, r in hour.items():
            m = merged.setdefault(route, {"n": 0, "total": 0.0, "max": 0.0, "slow": 0, "errors": 0})
            m["n"] += r["n"]
            m["total"] += r["total"]
            m["max"] = max(m["max"], r["max"])
            m["slow"] += r["slow"]
            m["errors"] += r["errors"]
    rows = [{"route": "/" + route, "requests": m["n"], "average_ms": round(m["total"] / m["n"] * 1000),
             "max_ms": round(m["max"] * 1000), "slow": m["slow"], "errors": m["errors"]}
            for route, m in merged.items() if m["n"]]
    rows.sort(key=lambda r: (r["errors"], r["max_ms"]), reverse=True)
    return rows[:limit]
