"""How closely a book's drafts follow the public-domain Bibles in the
database, by scripts/ngram_overlap.py's own measure: runs of MIN or more
words in a rendering that also appear in the same verses of a reference
Bible.

GET /api/admin/overlap/<BOOK>/?lang=en&min=6
        for each reference Bible in the language: the share of the drafts'
        words that sit in such runs, at each level, and the longest run; the
        sentences with the longest runs, to read in the verse inspector; and
        every reading language, with how many reference Bibles it has loaded

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
from django.db.models import Count, Max
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from owb import languages
from texts.models import Edition, Verse
from translation.models import Rendering, Sentence

from .permissions import admin_view
from .progress import CHAPTERS, book_name

_spec = importlib.util.spec_from_file_location("ngram_overlap", settings.REPO_ROOT / "scripts" / "ngram_overlap.py")
ngram = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ngram)

# A reading language's code and the Edition.language of its reference Bibles.
# Every reading language needs one (backend_tests/test_admin.py checks).
EDITION_LANGUAGE = {"en": "eng", "es": "spa", "fr": "fra", "sw": "swh", "vi": "vie", "ko": "kor", "pt": "por",
                    "am": "amh", "hi": "hin", "ru": "rus", "uk": "ukr", "ja": "jpn",
                    "id": "ind", "zh": "zho", "ar": "arb", "tl": "tgl", "fa": "pes", "pa": "pan"}
LEVELS = ("L", "B", "R")
TOP = 25


def measure(book, lang, n):
    # What compare() reads, for the one language compared: its id, refs and
    # renderings. Building whole records loaded every language's renderings
    # and every decision (Psalms: 3.8 s for a 5.5 KB answer).
    records = [{"id": rid, "refs": verse_ids, "renderings": {lang: {}}}
               for rid, verse_ids in Sentence.objects.filter(book=book).order_by("chapter", "verse", "number")
               .values_list("record_id", "refs")]
    by_id = {r["id"]: r for r in records}
    for rid, level, text in (Rendering.objects.filter(sentence__book=book, language=lang)
                             .values_list("sentence__record_id", "level", "text")):
        by_id[rid]["renderings"][lang][level] = text
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


def cache_key(book, lang, n):
    """Where book's answer is kept: fresh when its sentences change or a
    reference Bible is re-imported."""
    changed = Sentence.objects.filter(book=book).aggregate(t=Max("updated_at"))["t"]
    loaded = Edition.objects.filter(kind=Edition.Kind.REFERENCE).aggregate(t=Max("imported_at"))["t"]
    return "staff.overlap.{}.{}.{}.{}.{}".format(book, lang, n, *(t.timestamp() if t else 0 for t in (changed, loaded)))


@admin_view("overview")
def overlap(request, code):
    book = _book(code)
    if book is None:
        raise NotFound(f"There's no book called \u201c{code}\u201d. Choose one from the list.")
    lang = request.query_params.get("lang", "en")
    if lang not in EDITION_LANGUAGE:
        raise ValidationError({"lang": "Choose a reading language."})
    try:
        n = min(max(int(request.query_params.get("min", 6)), 4), 12)
    except ValueError:
        n = 6
    key = cache_key(book, lang, n)
    answer = cache.get(key)
    if answer is None:
        answer = measure(book, lang, n)
        cache.set(key, answer, 3600)
    return Response({**answer, "languages": _languages(), "books": BOOKS})


# Every book, in Bible order, for the page's list.
BOOKS = [{"code": c, "name": book_name(c)} for c in CHAPTERS]


def _book(text):
    """A book's code from its code or its English name ("jhn", "John",
    "1 john"), else None."""
    key = " ".join(str(text).split()).casefold()
    for c in CHAPTERS:
        if key in (c.casefold(), book_name(c).casefold()):
            return c
    return None


def _languages():
    """Every reading language, for the page to choose from, with how many
    public-domain Bibles in it are loaded to compare against."""
    loaded = dict(Edition.objects.filter(kind=Edition.Kind.REFERENCE).values_list("language")
                  .annotate(n=Count("id")).values_list("language", "n"))
    return [{"code": code, "name": lang["name"], "references": loaded.get(EDITION_LANGUAGE[code], 0)}
            for code, lang in languages.READING.items()]
