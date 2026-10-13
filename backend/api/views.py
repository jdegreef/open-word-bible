"""Read-only API for the reader and other consumers.

GET /api/editions/                       every imported edition
GET /api/text/<BOOK>/<chapter>/?editions=bsb,web
                                         verse text of a chapter in each edition,
                                         numbered as our source text is (a psalm's
                                         title is verse 1; owb/versification.py);
                                         &numbering=edition for each edition's own
GET /api/passages/<BOOK>/<chapter>/      our sentence records for a chapter, in the
                                         same shape as the files in content/, plus
                                         the source words they refer to
GET /api/search/?q=light&lang=en         search the site's passages, sentences, notes
                                         and articles (translation/search.py); add
                                         &type=verse|note|article|passage for one
                                         kind a page at a time (&offset, &limit,
                                         &sort=relevance|order)
GET /healthz                             liveness check
"""
from django.db import connection
from django.http import JsonResponse
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from owb import refs, versification
from texts.models import Edition, Verse, Word
from translation import search as site_search
from translation.models import SearchLanguage, Sentence


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
    """Each edition's text of a chapter. With numbering=source (the default)
    the verses are our source text's: a reference Bible's English-numbered
    verses are put under the Hebrew verses that hold the same text, and
    "refs" names them wherever their numbers differ ({"bsb": ["PSA.3.1"]}
    under verse 2). A psalm title has no verse in the reference Bibles."""
    book = _book(book)
    numbering = request.query_params.get("numbering", "source")
    if numbering not in ("source", "edition"):
        raise ValidationError({"numbering": "source or edition"})
    wanted = [c for c in request.query_params.get("editions", "").split(",") if c]
    found = {e.code: e for e in Edition.objects.filter(code__in=wanted)} if wanted else \
        {e.code: e for e in Edition.objects.all()}
    missing = set(wanted) - set(found)
    if missing:
        raise ValidationError({"editions": f"unknown: {', '.join(sorted(missing))}"})
    chapters = [chapter] if numbering == "edition" else versification.english_chapters(book, chapter)
    texts, english = {}, {}
    for v in Verse.objects.filter(edition__in=found.values(), book=book, chapter__in=chapters) \
            .select_related("edition").order_by("chapter", "verse"):
        code = v.edition.code
        if numbering == "edition" or v.edition.kind == Edition.Kind.ORIGINAL:
            numbers = [v.verse] if v.chapter == chapter else []
        else:
            ref = refs.Ref(book, v.chapter, v.verse)
            numbers = [r.verse for r in versification.to_source(ref) if r.chapter == chapter]
            for n in numbers:
                english.setdefault(n, {}).setdefault(code, []).append(ref)
        for n in numbers:
            verse = texts.setdefault(n, {})
            verse[code] = f"{verse[code]} {v.text}" if code in verse else v.text
    if not texts:
        raise NotFound(f"No text for {book} {chapter}")
    verses = []
    for n, text in sorted(texts.items()):
        verse = {"verse": n, "text": text}
        moved = {code: [str(r) for r in rs] for code, rs in english.get(n, {}).items()
                 if rs != [refs.Ref(book, chapter, n)]}
        if moved:
            verse["refs"] = moved
        verses.append(verse)
    return Response({"book": book, "chapter": chapter, "numbering": numbering,
                     "editions": list(found), "verses": verses})


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
            **({"alignments": sentence.alignments} if sentence.alignments else {}),
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
        word = {"id": w.id, "position": w.position, "text": w.text, "after": w.after,
                "lemma": w.lemma, "morph": w.morph, "gloss": w.gloss, "english": w.english,
                "strong": w.strong}
        if w.lang in ("H", "A"):   # a Hebrew or Aramaic morpheme, as in data/hbo/
            word.update(transliteration=w.transliteration, lang=w.lang)
        words.setdefault(f"{w.book}.{w.chapter}.{w.verse}", []).append(word)
    return Response({"book": book, "chapter": chapter,
                     "records": [record_json(s) for s in sentences], "words": words})


class SearchThrottle(UserRateThrottle):
    """Searches per visitor (or account) a minute: settings REST_FRAMEWORK."""
    scope = "search"


def _number(params, name, default, low, high):
    try:
        value = int(params.get(name, default))
    except ValueError:
        raise ValidationError({name: "must be a whole number"})
    return min(max(value, low), high)


@api_view(["GET"])
@throttle_classes([SearchThrottle])
def search(request):
    params = request.query_params
    lang = params.get("lang", "en")
    if not SearchLanguage.objects.filter(code=lang).exists():
        if not SearchLanguage.objects.exists():
            return Response({"detail": "Search is not ready: run import_content."}, status=503)
        raise ValidationError({"lang": f"unknown site language {lang!r}"})
    kind = params.get("type") or None
    if kind and kind not in site_search.KINDS:
        raise ValidationError({"type": f"one of {', '.join(site_search.KINDS)}"})
    sort = params.get("sort", "relevance")
    if sort not in ("relevance", "order"):
        raise ValidationError({"sort": "relevance or order"})
    answer = site_search.search(
        lang, params.get("q", ""), kind, sort=sort,
        offset=_number(params, "offset", 0, 0, 1000), limit=_number(params, "limit", 20, 1, 50),
        per=_number(params, "per", 8, 1, 20))
    response = Response(answer)
    # Answers change only when a deploy re-imports content/.
    response["Cache-Control"] = "public, max-age=300"
    return response


def healthz(request):
    with connection.cursor() as cursor:
        cursor.execute("select 1")
    return JsonResponse({"ok": True})
