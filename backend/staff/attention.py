"""The small numbers on the admin's rail: what is waiting for this account.

GET /api/admin/attention/     {"sections": {section: {"count", "title"}}}
                              for the rail sections with pending work the
                              account's roles open: the reader inbox (new
                              messages, and those assigned to the account),
                              open fix requests, open reviewer flags, the
                              review queue (sentences not approved in the
                              layers the account's reviewer roles name) and
                              open drafting jobs

The admin asks on each move between sections and after each change, and
never waits on the answer to draw a page, so this stays cheap: the inbox and
flags are counts on indexed columns; a review layer's size is cached until
the content changes; the GitHub numbers are cached for a few minutes (and
left out when GitHub can't be asked). For anyone on the team; a section is
left out when the account's roles don't open it, as the rail leaves it out.
"""
from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from rest_framework.response import Response

from accounts.models import Role
from feedback.models import ReaderMessage
from translation.models import ReviewState

from . import jobs
from .permissions import admin_view

# jobs._github forgets it when it files or changes an issue.
GITHUB_KEY = "staff.attention.github"
GITHUB_SECONDS = 300


def _github():
    """{"fixes": n, "jobs": n} open on GitHub, or {} when it can't be asked."""
    if not settings.OWB_GITHUB_TOKEN:
        return {}
    found = cache.get(GITHUB_KEY)
    if found is None:
        from .fixes import open_fixes   # fixes imports this module
        try:
            found = {"fixes": len(open_fixes()), "jobs": len(jobs.open_jobs())}
            cache.set(GITHUB_KEY, found, GITHUB_SECONDS)
        except jobs.GitHubError:
            found = {}
            cache.set(GITHUB_KEY, found, 60)
    return found


def _layer_size(layer, stamp):
    """How many sentences are in a review layer, cached until the content
    changes (stamp)."""
    from .review import _scope   # review is imported by much of staff/
    key = f"staff.attention.layer.{layer}.{stamp}"
    n = cache.get(key)
    if n is None:
        n = _scope(layer).count()
        cache.set(key, n, 7 * 86400)
    return n


def _review(user):
    """(sentences not approved, [(layer, n)]) in the layers the account's
    reviewer roles name. A super admin may review every layer, but only the
    layers a reviewer role names are counted: every language's every
    sentence is not one person's queue."""
    mine = sorted(set(user.roles.filter(kind__in=[Role.Kind.SCHOLAR_REVIEWER, Role.Kind.LANGUAGE_REVIEWER])
                      .exclude(language="").values_list("language", flat=True)))
    if not mine:
        return 0, []
    from .progress import _stamps
    stamp = _stamps()[0]
    approved = dict(ReviewState.objects.filter(layer__in=mine, state=ReviewState.State.APPROVED)
                    .values("layer").annotate(n=Count("id")).values_list("layer", "n"))
    per = [(layer, max(_layer_size(layer, stamp) - approved.get(layer, 0), 0)) for layer in mine]
    return sum(n for _, n in per), per


def _plural(n, one, many=None):
    return f"{n} {one if n == 1 else (many or one + 's')}"


@admin_view("overview")
def attention(request):
    areas = request.admin_areas
    out = {}
    if "inbox" in areas:
        waiting = ReaderMessage.objects.filter(status=ReaderMessage.Status.NEW).aggregate(
            new=Count("id"), mine=Count("id", filter=Q(assigned_to=request.user)))
        if waiting["new"]:
            title = _plural(waiting["new"], "new message")
            if waiting["mine"]:
                title += f", {waiting['mine']} assigned to you"
            out["inbox"] = {"count": waiting["new"], "title": title}
        flags = ReviewState.objects.filter(state=ReviewState.State.FLAGGED).count()
        if flags:
            out["flags"] = {"count": flags, "title": _plural(flags, "open flag")}
    if "review" in areas:
        todo, per = _review(request.user)
        if todo:
            where = ", ".join(f"{n} in {layer}" for layer, n in per if n)
            out["review"] = {"count": todo, "title": f"To review: {where}"}
    github = _github() if ("inbox" in areas or "jobs" in areas) else {}
    if "inbox" in areas and github.get("fixes"):
        out["fixes"] = {"count": github["fixes"], "title": _plural(github["fixes"], "open fix request")}
    if "jobs" in areas and github.get("jobs"):
        out["jobs"] = {"count": github["jobs"], "title": _plural(github["jobs"], "open drafting job")}
    return Response({"sections": out})
