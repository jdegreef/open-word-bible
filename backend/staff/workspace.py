"""A reviewer's workspace for one layer ("My review" in the admin): where the
layer's queue stands, book by book; the reviewer's open flags; their
approvals that have changed since, word by word (staff/history.py); and
their review assignments (staff/assignments.py). The admin adds the
language's content checks (GET /api/admin/checks/) for the books in
progress.

GET /api/admin/review/workspace/?layer=fr
        {layer, layers, counts, books: [{code, name, counts}],
         in_progress: [book codes], flags: [...], changes: {total, shown,
         items, last_approval}, assignments: [...], checks: lang or null}

Each list item carries what the admin needs to link it to the existing
views: the record and verse (the review sentence, the verse inspector),
the book (the queue).
"""
from django.db.models import Count
from rest_framework.response import Response

from owb import refs
from translation.models import ReviewEvent, ReviewState, Sentence

from . import assignments, history, review
from .inbox import verse_label
from .models import ReviewAssignment
from .permissions import admin_view

RS = ReviewState.State
SHOWN = 20


@admin_view("review")
def workspace(request):
    allowed = review.layers(request.user)
    try:
        layer = review._layer(request.query_params.get("layer"), allowed)
    except review._Forbidden as e:
        return review._forbidden(e)
    review.refresh(layer)
    me = request.user

    books, order = {}, {}
    for row in (review._in_layer(review._scope(layer), layer).order_by()
                .values("book", "book_order", "st").annotate(n=Count("id"))):
        counts = books.setdefault(row["book"], {s: 0 for s in review.STATES})
        counts[row["st"]] += row["n"]
        order[row["book"]] = row["book_order"]
    total = {s: sum(c[s] for c in books.values()) for s in review.STATES}
    total["total"] = sum(total.values())
    for counts in books.values():
        counts["total"] = sum(counts.values())

    mine = ReviewAssignment.objects.filter(assignee=me, layer=layer, closed_at__isnull=True)
    assigned = assignments.listed(mine)
    # Books in progress: assigned to the reviewer, or begun and not finished.
    in_progress = {a["book"] for a in assigned}
    in_progress |= {b for b, c in books.items() if c["not_reviewed"] < c["total"] and c["approved"] < c["total"]}

    flags = []
    for row in (ReviewState.objects.filter(layer=layer, state=RS.FLAGGED, event__user=me)
                .select_related("event__user", "sentence").order_by("-event__created_at", "-event_id")):
        vid = row.sentence.refs[0]
        flags.append({**review._event_json(row.event), "record": row.sentence.record_id, "verse": vid,
                      "label": verse_label(vid)})

    changed = (ReviewState.objects.filter(layer=layer, state=RS.CHANGED, event__user=me)
               .select_related("event__user", "event__sentence__source_edition")
               .order_by("-event__created_at", "-event_id"))
    shown = [row.event for row in changed[:SHOWN]]
    sentences = (Sentence.objects.filter(id__in=[e.sentence_id for e in shown])
                 .select_related("source_edition").prefetch_related("renderings", "decisions").in_bulk())
    last = (ReviewEvent.objects.filter(user=me, action=review._approve(layer),
                                       language="" if review._meaning(layer) else layer)
            .order_by("-created_at").values_list("created_at", flat=True).first())

    return Response({
        "layer": review.layer_json(layer), "layers": [review.layer_json(code) for code in allowed],
        "counts": total,
        "books": [{"code": b, "name": refs.BOOK_NAMES.get(b, b), "counts": books[b]}
                  for b in sorted(books, key=order.get)],
        "in_progress": sorted(in_progress, key=lambda b: review.ORDER.get(b, 99)),
        "flags": flags,
        "changes": {"total": changed.count(), "last_approval": last,
                    "items": [history.since_approval(e, sentences[e.sentence_id]) for e in shown]},
        "assignments": assigned,
        "checks": None if review._meaning(layer) else layer,
    })
