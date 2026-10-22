"""How closely a book's drafts follow the public-domain Bibles in the
database, by scripts/ngram_overlap.py's own measure: runs of MIN or more
words in a rendering that also appear in the same verses of a reference
Bible.

GET /api/admin/overlap/<BOOK>/?lang=en&min=6
        for each reference Bible in the language: the share of the drafts'
        words that sit in such runs, at each level, and the longest run; and
        the sentences with the longest runs, to read in the verse inspector

Shared runs with the public-domain Bibles are often the common heritage of
the language's Bible wording; a high share, or long runs, are where to
check that a draft was not built on a reference Bible, which CLAUDE.md
forbids. Copyrighted Bibles are never in the database; the script's
--extra compares against one locally. Cached an hour per book, language
and run length, and refreshed when the book's sentences change.
"""
import importlib.util

from django.conf import settings
from django.core.cache import cache
from django.db.models import Max
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from api.views import record_json
from texts.models import Edition, Verse
from translation.models import Sentence

from .permissions import admin_view
from .progress import CHAPTERS, book_name

_spec = importlib.util.spec_from_file_location("ngram_overlap", settings.REPO_ROOT / "scripts" / "ngram_overlap.py")
ngram = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ngram)

# A reading language's code and the Edition.language of its reference Bibles.
EDITION_LANGUAGE = {"en": "eng", "es": "spa", "fr": "fra", "sw": "swh", "vi": "vie", "ko": "kor", "am": "amh"}
LEVELS = ("L", "B", "R")
TOP = 25


def measure(book, lang, n):
    sentences = list(Sentence.objects.filter(book=book).select_related("source_edition")
                     .prefetch_related("renderings", "decisions").order_by("chapter", "verse", "number"))
    records = [record_json(s) for s in sentences]
    editions = list(Edition.objects.filter(kind=Edition.Kind.REFERENCE, language=EDITION_LANGUAGE.get(lang, ""))
                    .order_by("code"))
    texts = {e.code: {} for e in editions}
    for v in Verse.objects.filter(edition__in=editions, book=book).select_related("edition"):
        texts[v.edition.code][f"{v.book}.{v.chapter}.{v.verse}"] = v.text
    results = ngram.compare(records, lang, LEVELS, texts, n)
    by_level = {lv: {"words": 0, "covered": {e.code: 0 for e in editions}} for lv in LEVELS}
    longest = {e.code: 0 for e in editions}
    runs = []
    refs = {r["id"]: r["refs"][0] for r in records}
    for result in results:
        level = by_level[result["level"]]
        level["words"] += len(result["words"])
        for code, spans in result["runs"].items():
            level["covered"][code] += len({i for s, e in spans for i in range(s, e)})
            for s, e in spans:
                longest[code] = max(longest[code], e - s)
                runs.append({"record": result["id"], "verse": refs[result["id"]], "level": result["level"],
                             "edition": code, "length": e - s, "text": " ".join(result["words"][s:e])})
    runs.sort(key=lambda r: -r["length"])
    return {
        "book": book, "name": book_name(book), "language": lang, "min": n, "sentences": len(records),
        "editions": [{"code": e.code, "name": e.name, "longest": longest[e.code],
                      "share": {lv: round(100 * by_level[lv]["covered"][e.code] / by_level[lv]["words"], 1)
                                if by_level[lv]["words"] else None for lv in LEVELS}}
                     for e in editions],
        "words": {lv: by_level[lv]["words"] for lv in LEVELS},
        "longest_runs": runs[:TOP],
    }


@admin_view("overview")
def overlap(request, code):
    book = code.upper()
    if book not in CHAPTERS:
        raise NotFound(f"Unknown book {code!r}")
    lang = request.query_params.get("lang", "en")
    if lang not in EDITION_LANGUAGE:
        raise ValidationError({"lang": "Choose a reading language."})
    try:
        n = min(max(int(request.query_params.get("min", 6)), 4), 12)
    except ValueError:
        n = 6
    # Fresh when the book's sentences change or a reference Bible is re-imported.
    changed = Sentence.objects.filter(book=book).aggregate(t=Max("updated_at"))["t"]
    loaded = Edition.objects.filter(kind=Edition.Kind.REFERENCE).aggregate(t=Max("imported_at"))["t"]
    key = "staff.overlap.{}.{}.{}.{}.{}".format(book, lang, n, *(t.timestamp() if t else 0 for t in (changed, loaded)))
    answer = cache.get(key)
    if answer is None:
        answer = measure(book, lang, n)
        cache.set(key, answer, 3600)
    return Response(answer)
