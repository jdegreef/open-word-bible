"""The translation's open questions, for the team to read and act on.

GET /api/admin/decisions/?layer=&category=&book=&q=&offset=&all=
        decisions marked uncertain (all=1 for every decision), in Bible
        order, with counts by layer and category to filter by. layer is
        "meaning" or a reading language's code.
GET /api/admin/terms/
        the key terms (data/key_terms.json), each with how many drafted
        sentences use it (as staff/consistency.py finds them) and the first
        of them

Read-only: a decision is changed by a fix request (staff/fixes.py) that a
Claude session works into a pull request.
"""

from django.core.cache import cache
from django.db.models import Case, Count, IntegerField, Q, Value, When
from rest_framework.response import Response

from owb import languages, refs
from translation.models import Decision, Rendering

from . import consistency
from .inbox import verse_label
from .permissions import admin_view
from .progress import book_name

PAGE = 50
# Bible order, for a decision (by its sentence).
ORDER = Case(*[When(sentence__book=code, then=Value(i)) for i, code in enumerate(refs.BOOK_CODES)],
             output_field=IntegerField())


def _decision_json(d):
    s = d.sentence
    return {"id": d.id, "key": d.key, "record": s.record_id, "verse": s.refs[0], "label": verse_label(s.refs[0]),
            "layer": d.layer, "language": d.language, "levels": d.levels, "category": d.category,
            "choice": d.choice, "alternatives": d.alternatives, "reason": d.reason,
            "uncertain": d.uncertain, "footnote": d.footnote}


@admin_view("overview")
def decisions(request):
    params = request.query_params
    base = Decision.objects.all() if params.get("all") == "1" else Decision.objects.filter(uncertain=True)
    layer = params.get("layer", "")
    by_layer = {row["language"] or "meaning": row["n"]
                for row in base.values("language").annotate(n=Count("id"))}
    if layer == "meaning":
        base = base.filter(language="")
    elif layer in languages.CODES:
        base = base.filter(language=layer)
    by_category = dict(base.values("category").annotate(n=Count("id")).values_list("category", "n"))
    found = base
    if params.get("category"):
        found = found.filter(category=params["category"])
    book = params.get("book", "").upper()
    if book:
        found = found.filter(sentence__book=book)
    if params.get("q"):
        q = params["q"].strip()
        found = found.filter(Q(choice__icontains=q) | Q(reason__icontains=q))
    by_book = dict(found.values("sentence__book").annotate(n=Count("id")).values_list("sentence__book", "n"))
    try:
        offset = max(int(params.get("offset", 0)), 0)
    except ValueError:
        offset = 0
    total = found.count()
    page = (found.select_related("sentence").annotate(book_order=ORDER)
            .order_by("book_order", "sentence__chapter", "sentence__verse", "sentence__number", "order")
            [offset:offset + PAGE])
    return Response({
        "decisions": [_decision_json(d) for d in page], "total": total, "offset": offset, "page": PAGE,
        "layers": [{"code": "meaning", "name": "Meaning (every language)", "count": by_layer.get("meaning", 0)}]
        + [{"code": c, "name": lang["name"], "count": by_layer.get(c, 0)} for c, lang in languages.READING.items()],
        "categories": [{"code": c, "count": n} for c, n in sorted(by_category.items(), key=lambda kv: -kv[1])],
        "books": [{"code": c, "name": book_name(c), "count": by_book[c]} for c in refs.BOOK_CODES if c in by_book],
    })


@admin_view("overview")
def terms(request):
    cached = cache.get("staff.terms")
    if cached is None:
        # The sentences come from consistency's lookup: two queries for every
        # term, in Bible order. The languages each is drafted in, one more.
        uses, _ = consistency.term_uses()
        every = {r["id"] for rows in uses.values() for r in rows}
        drafted = {}
        # order_by(): the model's ordering adds level, and DISTINCT with it.
        for sid, lang in (Rendering.objects.filter(sentence_id__in=every).order_by()
                          .values_list("sentence_id", "language").distinct()):
            drafted.setdefault(sid, set()).add(lang)
        cached = []
        for term in consistency.TERMS:
            rows = uses[term["slug"]]
            by_lang = {c: sum(1 for r in rows if c in drafted.get(r["id"], ())) for c in languages.CODES}
            cached.append({**term, "language": term.get("language", "grc"), "uses": len(rows),
                           "by_language": by_lang,
                           "first": [{"verse": r["refs"][0], "label": verse_label(r["refs"][0])}
                                     for r in rows[:8] if r["refs"]]})
        cache.set("staff.terms", cached, 600)
    return Response({"terms": cached,
                     "languages": [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items()]})
