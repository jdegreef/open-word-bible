"""Review pace: how fast people are approving, for the charter's question of
when the translation will be reviewed.

GET /api/admin/pace/
        for the last WEEKS weeks (Monday to Sunday, UTC): approvals each week
        in each review layer (the meaning in grc and hbo, the wording in each
        reading language), what of the layer is approved now and its size,
        the pace of the last RECENT weeks and, at that pace, about how many
        weeks are left; and each reviewer's approvals in the period

An approval is a ReviewEvent approving the meaning or the wording; one made
again after the sentence changed counts again, as it is work done. Reviewers
are named by their display name (their address only for a super admin).
"""
from datetime import timedelta

from django.db.models import Count, F, Sum, Value
from django.db.models.functions import Coalesce, NullIf, TruncWeek
from django.utils import timezone
from rest_framework.response import Response

from owb import languages
from translation.models import DraftedCount, ReviewEvent, ReviewState, Sentence

from .permissions import admin_view, is_super_admin

WEEKS = 12
RECENT = 4
A = ReviewEvent.Action
APPROVALS = (A.MEANING_REVIEWED, A.REVIEWED)
MEANING = {"grc": "Greek", "hbo": "Hebrew"}


def _layer_name(code):
    if code in MEANING:
        return f"Meaning ({MEANING[code]})"
    return f"{languages.READING[code]['name']} wording" if code in languages.READING else code


@admin_view("overview")
def pace(request):
    today = timezone.now().date()
    monday = today - timedelta(days=today.weekday())
    weeks = [monday - timedelta(weeks=n) for n in range(WEEKS - 1, -1, -1)]
    events = (ReviewEvent.objects.filter(action__in=APPROVALS, created_at__date__gte=weeks[0])
              .annotate(layer=Coalesce(NullIf(F("language"), Value("")), F("sentence__source_edition__language"))))
    per_week = {}
    for row in events.annotate(week=TruncWeek("created_at")).values("layer", "week").annotate(n=Count("id")):
        per_week.setdefault(row["layer"], {})[row["week"].date()] = row["n"]
    sizes = dict(DraftedCount.objects.values("language").annotate(n=Sum("sentences")).values_list("language", "n"))
    for code in MEANING:
        sizes[code] = Sentence.objects.filter(source_edition__language=code).count()
    approved = dict(ReviewState.objects.filter(state=ReviewState.State.APPROVED).values("layer")
                    .annotate(n=Count("sentence", distinct=True)).values_list("layer", "n"))
    layers = []
    for code in [*MEANING, *languages.READING]:
        counts = [per_week.get(code, {}).get(w, 0) for w in weeks]
        size, done = sizes.get(code) or 0, approved.get(code, 0)
        if not size and not done and not any(counts):
            continue
        recent = sum(counts[-RECENT:]) / RECENT
        left = max(size - done, 0)
        layers.append({"code": code, "name": _layer_name(code), "size": size, "approved": done,
                       "per_week": counts, "recent": round(recent, 1),
                       "weeks_left": round(left / recent) if recent and left else (0 if not left else None)})
    layers.sort(key=lambda lay: (-sum(lay["per_week"]), -lay["approved"], lay["name"]))
    boss = is_super_admin(request.user)
    reviewers = []
    for row in (events.values("user__first_name", "user__username", "layer").annotate(n=Count("id"))
                .order_by("-n")[:50]):
        name = row["user__first_name"] or ("" if not boss else row["user__username"]) or "A reviewer"
        reviewers.append({"name": row["user__username"] if boss else name, "display": name,
                          "layer": row["layer"], "layer_name": _layer_name(row["layer"]), "approvals": row["n"]})
    return Response({"weeks": weeks, "recent_weeks": RECENT, "layers": layers, "reviewers": reviewers})
