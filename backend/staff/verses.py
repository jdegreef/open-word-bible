"""The verse inspector: one verse's sentence records, whole.

GET /api/admin/verses/?q=John 1:1     find a verse by reference ("jn 1 1",
                                      "Juan 3:16", "JHN.1.1")
GET /api/admin/verses/<JHN.1.1>/      the sentences that hold the verse, in
                                      the content/ file format (with every
                                      language, level and decision), the
                                      source words, the file each lives in,
                                      the verses either side, and the reader
                                      messages and fix requests about it

For anyone on the team (overview); the reader messages only for those whose
roles open the inbox, since they carry the reader's name.
"""
import functools
import json
import re

from django.conf import settings
from django.db.models import Max
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from api.views import record_json
from feedback.models import ReaderMessage
from owb import languages, refs
from texts.models import Word
from translation import search
from translation.models import ContentFile, SearchLanguage, Sentence

from .inbox import message_json, verse_label, verse_url
from .models import AdminAction
from .permissions import admin_view
from .progress import _BOOKS, CHAPTERS, book_name

# content/JHN/JHN.3.json (a chapter), JHN.1.1-18.json (verses), JHN.7.53-8.11.json
FILE = re.compile(r"(?P<book>[1-3]?[A-Z]+)\.(?P<c1>\d+)(?:\.(?P<v1>\d+)-(?:(?P<c2>\d+)\.)?(?P<v2>\d+))?\.json$")


def covers(name, chapter, verse):
    """Does a content file's name cover chapter:verse?"""
    m = FILE.search(name)
    if not m:
        return False
    c1 = int(m["c1"])
    if m["v1"] is None:
        return c1 == chapter
    start, end = (c1, int(m["v1"])), (int(m["c2"] or c1), int(m["v2"]))
    return start <= (chapter, verse) <= end


def content_file(book, chapter, verse):
    paths = ContentFile.objects.filter(path__startswith=f"content/{book}/").values_list("path", flat=True)
    return next((p for p in sorted(paths) if covers(p, chapter, verse)), "")


def verse_id(value):
    """A verse id ("JHN.1.1") from an id or a reference in any site
    language; None if it names no verse."""
    value = str(value or "").strip()
    try:
        ref = refs.parse(value.upper())
        return f"{ref.book}.{ref.chapter}.{ref.verse}"
    except ValueError:
        pass
    for language in SearchLanguage.objects.order_by("code"):
        found = search.reference(value, language.books, language.code)
        if found:
            return f"{found['book']}.{found['chapter']}.{found['verse'] or 1}"
    return _by_name(value)


_ABBREVIATIONS = json.loads((settings.REPO_ROOT / "data" / "book_abbreviations.json")
                            .read_text(encoding="utf-8"))["books"]


@functools.cache
def _aliases():
    """Each book's code, and its name and short name in every site language,
    folded and without spaces: {"JHN": {"jhn", "john", "juan", ...}}."""
    def folded(name):
        return re.sub(r"[\s.]+", "", search.fold(name))
    return {code: {code.lower()}
            | {folded(n) for k, n in _BOOKS[code].items() if k not in ("chapters", "chapter_names")}
            | {folded(n) for n in _ABBREVIATIONS.get(code, {}).values()}
            for code in CHAPTERS}


def _by_name(value):
    """"John 1:1", "1 jn 2 3" by data/books.json's names, for when the search
    tables (with their abbreviations) aren't built: a name, a code, or the
    start of a name of three letters or more."""
    m = search.REFERENCE.match(search.fold(value))
    if not m:
        return None
    key = re.sub(r"[\s.]+", "", m[1])
    if not key or key.isdigit():
        return None
    aliases = _aliases()
    book = next((c for c, names in aliases.items() if key in names), None)
    if not book and len(re.sub(r"^\d", "", key)) >= 3:
        book = next((c for c, names in aliases.items() if any(n.startswith(key) for n in names)), None)
    return f"{book}.{int(m[2])}.{int(m[3]) if m[3] else 1}" if book else None


@admin_view("overview")
def find(request):
    vid = verse_id(request.query_params.get("q"))
    if not vid:
        raise ValidationError({"q": "Enter a reference such as John 1:1.", "code": "not_a_reference"})
    return Response({"verse": vid})


def _neighbours(book, chapter, verse):
    """The previous and next verses that have a sentence, within the book."""
    here = Sentence.objects.filter(book=book)
    before = (here.filter(chapter=chapter, verse__lt=verse) | here.filter(chapter__lt=chapter)) \
        .order_by("-chapter", "-verse").values("chapter", "verse").first()
    after = (here.filter(chapter=chapter, verse__gt=verse) | here.filter(chapter__gt=chapter)) \
        .order_by("chapter", "verse").values("chapter", "verse").first()
    return [f"{book}.{n['chapter']}.{n['verse']}" if n else None for n in (before, after)]


@admin_view("overview")
def verse(request, vid):
    try:
        ref = refs.parse(vid.upper())
    except ValueError:
        raise NotFound(f"Not a verse: {vid!r}")
    vid = f"{ref.book}.{ref.chapter}.{ref.verse}"
    # A sentence is filed under its first verse, which may be in the chapter
    # before (book, chapter is indexed; refs is not).
    sentences = list(Sentence.objects.filter(book=ref.book, chapter__in=[ref.chapter - 1, ref.chapter],
                                             refs__contains=[vid]).select_related("source_edition")
                     .prefetch_related("renderings", "decisions").order_by("chapter", "verse", "number"))
    records = [record_json(s) for s in sentences]
    tokens = [t for s in sentences for t in s.tokens]
    words = {w.id: {"text": w.text, "lemma": w.lemma, "gloss": w.gloss, "morph": w.morph, "strong": w.strong}
             for w in Word.objects.filter(id__in=tokens)}
    files = {s.record_id: content_file(s.book, s.chapter, s.verse) for s in sentences}
    answer = {
        "verse": vid, "label": verse_label(vid), "book": book_name(ref.book) if ref.book in CHAPTERS else ref.book,
        "url": verse_url(vid, "en"), "records": records,
        "languages": [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items()],
        "words": words, "files": files,
        "updated": Sentence.objects.filter(id__in=[s.id for s in sentences]).aggregate(t=Max("updated_at"))["t"],
        "neighbours": _neighbours(ref.book, ref.chapter, ref.verse),
        "fixes": [{"at": a.created_at, "by": a.actor_email, "target": a.target, **a.detail}
                  for a in AdminAction.objects.filter(action="fix.request", detail__verse=vid)[:20]],
    }
    if "inbox" in request.admin_areas:
        answer["messages"] = [message_json(m) for m in ReaderMessage.objects.filter(verse=vid)
                              .select_related("user", "replied_by")[:20]]
    return Response(answer)
