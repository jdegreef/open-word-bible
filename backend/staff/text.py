"""The translation's open questions, for the team to read and act on.

GET /api/admin/decisions/?layer=&category=&book=&q=&offset=&all=
        decisions marked uncertain (all=1 for every decision), in Bible
        order, with counts by layer and category to filter by. layer is
        "meaning" or a reading language's code.
GET /api/admin/terms/
        the key terms (data/key_terms.json), each with how many drafted
        sentences use it and the first of them

Read-only: a decision is changed by a fix request (staff/fixes.py) that a
Claude session works into a pull request.
"""
import json

from django.conf import settings
from django.core.cache import cache
from django.db.models import Case, Count, IntegerField, Q, Value, When
from rest_framework.response import Response

from owb import languages, refs
from texts.models import Word
from translation.models import Decision, Rendering, Sentence

from .inbox import verse_label
from .permissions import admin_view
from .progress import book_name

PAGE = 50
# Bible order, for a decision (by its sentence) and for a sentence.
ORDER = Case(*[When(sentence__book=code, then=Value(i)) for i, code in enumerate(refs.BOOK_CODES)],
             output_field=IntegerField())
BOOK_ORDER = Case(*[When(book=code, then=Value(i)) for i, code in enumerate(refs.BOOK_CODES)],
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


def _uses(term):
    """The drafted sentences that use a key term: Words by Strong's number,
    Greek ids starting n and Hebrew o, as owb.validate tells them apart."""
    prefix = "o" if term.get("language") == "hbo" else "n"
    ids = list(Word.objects.filter(strong=term["strong"], id__startswith=prefix).values_list("id", flat=True))
    if not ids:
        return Sentence.objects.none()
    return Sentence.objects.filter(tokens__overlap=ids)


@admin_view("overview")
def terms(request):
    cached = cache.get("staff.terms")
    if cached is None:
        data = json.loads((settings.REPO_ROOT / "data" / "key_terms.json").read_text(encoding="utf-8"))["terms"]
        cached = []
        for term in data:
            uses = _uses(term)
            ids = list(uses.values_list("id", flat=True))
            by_lang = dict(Rendering.objects.filter(sentence_id__in=ids).values("language")
                           .annotate(n=Count("sentence", distinct=True)).values_list("language", "n"))
            first = [r[0] for r in Sentence.objects.filter(id__in=ids).annotate(book_order=BOOK_ORDER)
                     .order_by("book_order", "chapter", "verse").values_list("refs", flat=True)[:8]]
            cached.append({**term, "language": term.get("language", "grc"), "uses": len(ids),
                           "by_language": {c: by_lang.get(c, 0) for c in languages.CODES},
                           "first": [{"verse": v, "label": verse_label(v)} for v in first]})
        cache.set("staff.terms", cached, 600)
    return Response({"terms": cached,
                     "languages": [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items()]})
