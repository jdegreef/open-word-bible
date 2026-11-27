"""A planning board for one language: one page for the month's question
"what should happen next?", from what Coverage, Review assignments, Review
pace, Drafting jobs and Reviewer flags each show apart.

GET /api/admin/plan/?lang=fr
        unassigned: books drafted in the language that nobody has an open
            assignment for and aren't fully approved, with how far review
            has got (Assign on each row)
        undrafted: books English has and this language hasn't, or has in
            part (File a drafting job on each row), and the open drafting
            jobs that name the language
        reviewers: the language's reviewers, with their open assignments
            and when they last approved anything (idle: none open)
        overdue: open assignments past their date
        blocked: books with open flags, and how many wait on a fix request

Reads kept counts only (DraftedCount, ReviewState, the kept work list):
nothing here asks GitHub or counts renderings.
"""
from django.contrib.auth import get_user_model
from django.db.models import Count, Max
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.models import Role
from owb import languages, refs
from translation import counts
from translation.models import ReviewEvent, ReviewState

from . import assignments as asg
from . import people
from .models import FlagReply, ReviewAssignment
from .permissions import admin_view
from .review import _scope, refresh
from .work import kept_items

RS = ReviewState.State
K = Role.Kind


@admin_view("overview")
def plan(request):
    lang = request.query_params.get("lang") or "en"
    if lang not in languages.READING:
        raise ValidationError({"lang": "Choose a reading language.", "code": "invalid_language"})
    refresh(lang)
    today = timezone.localdate()
    drafted = counts.by_book()
    approved = dict(ReviewState.objects.filter(layer=lang, state=RS.APPROVED).values("sentence__book")
                    .annotate(n=Count("id")).values_list("sentence__book", "n"))
    listed = asg.listed(ReviewAssignment.objects.filter(layer=lang, closed_at__isnull=True))
    covered = {x["book"] for x in listed}

    def book(code, **extra):
        return {"code": code, "name": refs.BOOK_NAMES.get(code, code), **extra}

    unassigned, undrafted = [], []
    for code in refs.BOOK_CODES:
        here = drafted.get(code, {}).get(lang, 0)
        english = drafted.get(code, {}).get("en", 0)
        if here and code not in covered and approved.get(code, 0) < here:
            unassigned.append(book(code, drafted=here, approved=approved.get(code, 0)))
        if english and here < english:
            undrafted.append(book(code, drafted=here, of=english))
    jobs = [{"number": w["number"], "title": w["title"], "url": w["url"], "state": w["state"],
             "prs": len(w["prs"])} for w in kept_items()
            if w["kind"] == "drafting-job" and w["state"] == "open"
            and (languages.READING[lang]["name"].lower() in w["title"].lower() or f"({lang})" in w["title"])]

    User = get_user_model()
    team = (User.objects.filter(is_active=True, roles__kind=K.LANGUAGE_REVIEWER, roles__language=lang).distinct()
            .order_by("username"))
    last = dict(ReviewEvent.objects.filter(language=lang, action=ReviewEvent.Action.REVIEWED, user__in=team)
                .values("user").annotate(t=Max("created_at")).values_list("user", "t"))
    reviewers = []
    for u in team:
        mine = [x for x in listed if x["assignee"]["id"] == u.id]
        active = [x for x in mine if x["standing"] in ("open", "overdue")]
        reviewers.append({**people.person(u), "assignments": mine, "last_approval": last.get(u.id),
                          "idle": not active})
    overdue = [x for x in listed if x["standing"] == "overdue"]

    flagged = (ReviewState.objects.filter(layer=lang, state=RS.FLAGGED).values("sentence__book", "event_id"))
    fixing = set(FlagReply.objects.filter(kind=FlagReply.Kind.FIX, flag_id__in=[r["event_id"] for r in flagged])
                 .values_list("flag_id", flat=True))
    blocked = {}
    for r in flagged:
        b = blocked.setdefault(r["sentence__book"], book(r["sentence__book"], flags=0, fixing=0))
        b["flags"] += 1
        b["fixing"] += r["event_id"] in fixing
    order = {c: i for i, c in enumerate(refs.BOOK_CODES)}
    return Response({
        "language": {"code": lang, "name": languages.READING[lang]["name"]},
        "unassigned": unassigned, "undrafted": undrafted, "jobs": jobs,
        "reviewers": reviewers, "overdue": overdue,
        "blocked": sorted(blocked.values(), key=lambda b: order.get(b["code"], 99)),
        "today": today,
        "languages": [{"code": c, "name": x["name"]} for c, x in languages.READING.items()],
        "drafted_total": _scope(lang).count(),
    })
