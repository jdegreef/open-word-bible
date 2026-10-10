"""Read-only API for the reader and other consumers.

GET /api/editions/                       every imported edition
GET /api/text/<BOOK>/<chapter>/?editions=bsb,web
                                         verse text of a chapter in each edition
GET /api/passages/<BOOK>/<chapter>/      our sentence records for a chapter, in the
                                         same shape as the files in content/, plus
                                         the source words they refer to
GET /healthz                             liveness check
"""
from django.db import connection
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from owb import refs
from texts.models import Edition, Verse, Word
from translation.models import Sentence


def _book(code):
    code = code.upper()
    if code not in refs.BOOK_NAMES:
        raise NotFound(f"Unknown book {code!r}")
    return code


@api_view(["GET"])
def editions(request):
    return Response([
        {"code": e.code, "name": e.name, "language": e.language, "kind": e.kind,
         "licence": e.licence, "attribution": e.attribution}
        for e in Edition.objects.all()])


@api_view(["GET"])
def chapter_text(request, book, chapter):
    book = _book(book)
    wanted = [c for c in request.query_params.get("editions", "").split(",") if c]
    found = {e.code: e for e in Edition.objects.filter(code__in=wanted)} if wanted else \
        {e.code: e for e in Edition.objects.all()}
    missing = set(wanted) - set(found)
    if missing:
        raise ValidationError({"editions": f"unknown: {', '.join(sorted(missing))}"})
    verses = {}
    for v in Verse.objects.filter(edition__in=found.values(), book=book, chapter=chapter) \
            .select_related("edition").order_by("verse"):
        verses.setdefault(v.verse, {})[v.edition.code] = v.text
    if not verses:
        raise NotFound(f"No text for {book} {chapter}")
    return Response({"book": book, "chapter": chapter, "editions": list(found),
                     "verses": [{"verse": n, "text": t} for n, t in sorted(verses.items())]})


def record_json(sentence):
    """A sentence in the content/ file format."""
    renderings = {}
    for r in sentence.renderings.all():
        renderings.setdefault(r.language, {})[r.level] = r.text
    decisions = []
    for d in sentence.decisions.all():
        item = {"id": d.key, "layer": d.layer, "language": d.language or None}
        if d.layer == "rendering":
            item["levels"] = d.levels
        item.update(category=d.category, tokens=d.tokens, choice=d.choice,
                    alternatives=d.alternatives, reason=d.reason,
                    uncertain=d.uncertain, footnote=d.footnote)
        decisions.append(item)
    return {"id": sentence.record_id, "refs": sentence.refs,
            "source": {"language": sentence.source_edition.language, "text_id": sentence.source_text_id, "tokens": sentence.tokens,
                       "text": sentence.source_text},
            "literal_gloss": sentence.literal_gloss, "renderings": renderings,
            "decisions": decisions, "status": sentence.status}


@api_view(["GET"])
def passages(request, book, chapter):
    book = _book(book)
    sentences = list(Sentence.objects.filter(book=book, chapter=chapter)
                     .select_related("source_edition")
                     .prefetch_related("renderings", "decisions"))
    if not sentences:
        raise NotFound(f"No translated sentences in {book} {chapter}")
    token_ids = [t for s in sentences for t in s.tokens]
    words = {}
    for w in Word.objects.filter(id__in=token_ids).order_by("seq"):
        words.setdefault(f"{w.book}.{w.chapter}.{w.verse}", []).append(
            {"id": w.id, "position": w.position, "text": w.text, "after": w.after,
             "lemma": w.lemma, "morph": w.morph, "gloss": w.gloss, "english": w.english,
             "strong": w.strong})
    return Response({"book": book, "chapter": chapter,
                     "records": [record_json(s) for s in sentences], "words": words})


def healthz(request):
    with connection.cursor() as cursor:
        cursor.execute("select 1")
    return JsonResponse({"ok": True})
