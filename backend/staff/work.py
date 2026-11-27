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
With no copy kept, a page waits at most WAIT seconds for GitHub and then
says the work is still being read, rather than waiting the 12-16 seconds
the twenty-odd requests take.
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

from . import github
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
    requests. Raises github.GitHubError when GitHub can't be reached."""
    since = (timezone.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    issues = github.call(f"issues?state=all&since={since}&per_page=100")
    # Newest updated first: the pages stop at the first that reaches back
    # past `since`, since a job's pull request has been updated since then.
    pulls = github.call("pulls?state=all&sort=updated&direction=desc&per_page=100",
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
# and pull requests (12-16 s when measured). A copy younger than FRESH is
# used as it is; an older one (kept up to KEEP) is used at once while a
# thread asks GitHub again. With none kept (the first page after the cache
# is emptied) a thread asks, and the page waits for it at most WAIT seconds.
FRESH = 120
KEEP = 86400
KEY = "staff.work.v2"
WAIT = 2.0
# How long one thread's asking holds off another: longer than a refresh
# takes, short enough that one cut off (a worker restarted) is soon retried.
ASKING = 60


def cached_work():
    """fetch_work without the bodies. Raises github.GitHubError when GitHub
    can't be reached and no copy is kept."""
    return _kept()["items"]


def kept_items():
    """The work list kept, without asking GitHub; [] when none is kept."""
    kept = cache.get(KEY)
    return kept["items"] if kept else []


def refresh():
    """The work list read from GitHub now, and kept. Raises
    github.GitHubError when GitHub can't be reached."""
    return _refresh()["items"]


def fetched_at():
    """When the copy cached_work gives was read from GitHub (epoch seconds)."""
    kept = cache.get(KEY)
    return kept["at"] if kept else None


class Pending(github.GitHubError):
    """No copy is kept and GitHub hasn't answered within WAIT seconds: a
    thread is still asking, and keeps what it reads."""


def _kept():
    kept = cache.get(KEY)
    if kept is not None:
        if time.time() - kept["at"] > FRESH and cache.add(KEY + ".refreshing", 1, ASKING):
            threading.Thread(target=_refresh_quietly, daemon=True).start()
        return kept
    if not cache.add(KEY + ".refreshing", 1, ASKING):
        raise Pending   # another request's thread is asking
    # A thread asks GitHub. If it answers within WAIT, this request keeps
    # the answer; if not, the thread keeps it when it comes.
    box = {"lock": threading.Lock(), "waiting": True}
    thread = threading.Thread(target=_ask, args=(box,), daemon=True)
    thread.start()
    thread.join(WAIT)
    with box["lock"]:
        box["waiting"] = False
        if "answer" not in box:
            raise Pending
    cache.delete(KEY + ".refreshing")
    answer = box["answer"]
    if isinstance(answer, Exception):
        raise answer
    cache.set(KEY, answer, KEEP)
    return answer


def _read():
    """fetch_work as kept: when it was read, and the items without bodies."""
    return {"at": time.time(), "items": [{k: v for k, v in item.items() if k != "body"} for item in fetch_work()]}


def _refresh():
    kept = _read()
    cache.set(KEY, kept, KEEP)
    return kept


def _ask(box):
    """_read in a thread, for a request waiting on it at most WAIT seconds:
    the answer (or GitHub's error) goes in box while it waits, and is kept
    here once it has stopped."""
    try:
        answer = _read()
    except github.GitHubError as e:
        answer = e
    with box["lock"]:
        if box["waiting"]:
            box["answer"] = answer
            return
    try:
        if not isinstance(answer, Exception):
            cache.set(KEY, answer, KEEP)
    finally:
        cache.delete(KEY + ".refreshing")
        connections.close_all()   # this thread's own database connection


def _refresh_quietly():
    try:
        _refresh()
    except github.GitHubError:
        pass   # the kept copy stays; the next page asks again
    finally:
        cache.delete(KEY + ".refreshing")
        connections.close_all()   # this thread's own database connection


@admin_view("overview")
def work(request):
    try:
        cached = cached_work()
    except Pending:
        return Response({"items": [], "pending": True,
                         "error": "GitHub is still being asked for the work; open the page again in a moment.",
                         "days": DAYS, "stale_hours": STALE_HOURS})
    except github.GitHubError:
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
