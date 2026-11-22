"""The work the admin has handed to Claude sessions, followed through to its
pull requests: drafting jobs, fix requests and article jobs.

GET /api/admin/work/      every job filed in the last 30 days, open or done,
                          with the pull requests that name it and whether it
                          has stalled

A pull request belongs to a job when its title or body says "Fixes #N",
"Closes #N", "Resolves #N" or "Part of #N" (as the worker skills write
them). A job open for more than STALE_HOURS with no pull request has
stalled. GitHub is asked at most every FRESH seconds: a page in between
uses the copy kept, saying when it was read, while a thread asks again.
"""
import re
import threading
import time
from datetime import UTC, datetime, timedelta

from django.core.cache import cache
from django.db import connections
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.response import Response

from . import jobs
from .permissions import admin_view

KINDS = {"drafting-job": "Drafting job", "fix-request": "Fix request", "article-job": "Article job"}
DAYS = 30
STALE_HOURS = 24
REFERENCE = re.compile(r"\b(?:fix(?:es|ed)?|close[sd]?|resolve[sd]?|part of)\s+#(\d+)", re.IGNORECASE)


def _pr_state(pr):
    if pr.get("merged_at"):
        return "merged"
    return "draft" if pr.get("draft") and pr["state"] == "open" else pr["state"]


def fetch_work(days=DAYS):
    """The jobs filed in the last `days`, newest first, each with its pull
    requests. Raises jobs.GitHubError when GitHub can't be reached."""
    since = (timezone.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    issues = jobs._github(f"issues?state=all&since={since}&per_page=100")
    # Newest updated first: the pages stop at the first that reaches back
    # past `since`, since a job's pull request has been updated since then.
    pulls = jobs._github("pulls?state=all&sort=updated&direction=desc&per_page=100",
                         stop=lambda page: bool(page) and (page[-1].get("updated_at") or "") < since)
    by_issue = {}
    for pr in pulls:
        for number in {int(n) for n in REFERENCE.findall(f"{pr.get('title', '')}\n{pr.get('body') or ''}")}:
            by_issue.setdefault(number, []).append({
                "number": pr["number"], "title": pr["title"], "url": pr["html_url"], "state": _pr_state(pr),
                "merged_at": pr.get("merged_at"), "updated_at": pr.get("updated_at")})
    now = timezone.now()
    out = []
    for issue in issues:
        labels = [label["name"] for label in issue.get("labels", [])]
        kind = next((k for k in KINDS if k in labels), None)
        if not kind or "pull_request" in issue:
            continue
        prs = by_issue.get(issue["number"], [])
        created = parse_datetime(issue["created_at"])
        stale = issue["state"] == "open" and not prs and now - created > timedelta(hours=STALE_HOURS)
        out.append({
            "kind": kind, "kind_label": KINDS[kind], "number": issue["number"], "title": issue["title"],
            "url": issue["html_url"], "state": issue["state"], "state_reason": issue.get("state_reason"),
            "created_at": issue["created_at"], "closed_at": issue.get("closed_at"),
            "assignees": [a["login"] for a in issue.get("assignees", [])],
            "comments": issue.get("comments", 0), "body": issue.get("body") or "",
            "prs": prs, "stale": stale,
        })
    out.sort(key=lambda w: w["created_at"], reverse=True)
    return out


# Work is listed from GitHub, about twenty requests for 30 days of issues
# and pull requests (12 s when measured). A copy younger than FRESH is used
# as it is; an older one (kept up to KEEP) is used at once while a thread
# asks GitHub again, so only the first page after a deploy waits.
FRESH = 120
KEEP = 86400
KEY = "staff.work.v2"


def cached_work():
    """fetch_work without the bodies. Raises jobs.GitHubError when GitHub
    can't be reached and no copy is kept."""
    return _kept()["items"]


def fetched_at():
    """When the copy cached_work gives was read from GitHub (epoch seconds)."""
    kept = cache.get(KEY)
    return kept["at"] if kept else None



def _kept():
    kept = cache.get(KEY)
    if kept is None:
        return _refresh()
    if time.time() - kept["at"] > FRESH and cache.add(KEY + ".refreshing", 1, 300):
        threading.Thread(target=_refresh_quietly, daemon=True).start()
    return kept


def _refresh():
    kept = {"at": time.time(), "items": [{k: v for k, v in item.items() if k != "body"} for item in fetch_work()]}
    cache.set(KEY, kept, KEEP)
    return kept


def _refresh_quietly():
    try:
        _refresh()
    except jobs.GitHubError:
        pass   # the kept copy stays; the next page asks again
    finally:
        cache.delete(KEY + ".refreshing")
        connections.close_all()   # this thread's own database connection


@admin_view("overview")
def work(request):
    try:
        cached = cached_work()
    except jobs.GitHubError:
        return Response({"items": [], "error": "GitHub could not be reached, so the work isn't listed.",
                         "days": DAYS, "stale_hours": STALE_HOURS})
    counts = {"open": sum(1 for w in cached if w["state"] == "open"),
              "stale": sum(1 for w in cached if w["stale"]),
              "in_review": sum(1 for w in cached if w["state"] == "open"
                               and any(p["state"] in ("open", "draft") for p in w["prs"])),
              "done": sum(1 for w in cached if w["state"] == "closed")}
    at = fetched_at()
    return Response({"items": cached, "counts": counts, "days": DAYS, "stale_hours": STALE_HOURS,
                     "fetched_at": datetime.fromtimestamp(at, UTC) if at else None})
