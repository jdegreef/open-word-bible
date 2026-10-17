"""Downloading the translation as a file (owb/export.py): one language at
one level, as a zip of USFM books or as JSON, for Bible software and for
the apps that carry our text (Take Root, Ochorus, Every Tongue).

GET /api/admin/export/
        the choices: each language's verses at each level, the settings it
        has, the books, the latest import and the recent downloads
GET /api/admin/export/preview/?lang=&level=&numbering=&books=&settings=
        what the file would hold: counts, and a few verses as they would read
GET /api/admin/export/file/?lang=&level=&type=&numbering=&books=&settings=
        the file itself

type is usfm or json (not "format", which DRF keeps for its own use);
books is a comma-separated list of book codes (none: the whole Bible);
settings is "name:index,..." (deity_pronoun:1 for "He"), each setting not
named at its default. The text comes from the database, which each deploy
brings up to date from content/ on main. Each download is logged in the
activity log.
"""
import os

from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from owb import export, languages, refs
from texts.models import Edition, Verse
from translation.models import ImportRun, Rendering

from .models import AdminAction, record
from .permissions import admin_view
from .inbox import verse_label
from .progress import book_name

# Shown in the preview, where the export has them.
SAMPLES = ("GEN.1.1", "PSA.23.1", "ISA.53.5", "JHN.3.16", "ROM.8.28", "PHP.4.6")


def _options(params):
    """The export asked for, checked: (lang, level, fmt, numbering, books, settings)."""
    lang = params.get("lang", "en")
    if lang not in languages.CODES:
        raise ValidationError({"lang": f"one of {', '.join(languages.CODES)}"})
    level = params.get("level", "B")
    if level not in export.LEVELS:
        raise ValidationError({"level": "L, B or R"})
    fmt = params.get("type", "usfm")
    if fmt not in export.FORMATS:
        raise ValidationError({"type": " or ".join(export.FORMATS)})
    numbering = params.get("numbering", "english")
    if numbering not in export.NUMBERINGS:
        raise ValidationError({"numbering": " or ".join(export.NUMBERINGS)})
    books = [b for b in params.get("books", "").upper().split(",") if b]
    unknown = [b for b in books if b not in refs.BOOK_NAMES]
    if unknown:
        raise ValidationError({"books": f"unknown: {', '.join(unknown)}"})
    known = export.settings_for(lang)
    settings = {}
    for item in filter(None, params.get("settings", "").split(",")):
        name, _, index = item.partition(":")
        if name not in known or not index.isdigit() or int(index) >= len(known[name]):
            raise ValidationError({"settings": f"unknown setting {item!r} for {lang}"})
        settings[name] = int(index)
    return lang, level, fmt, numbering, books, settings


def _records(lang, level, books):
    """Our sentences in lang at level, in the content/ shape export.build
    reads, in order within each chapter."""
    rows = Rendering.objects.filter(language=lang, level=level)
    if books:
        rows = rows.filter(sentence__book__in=books)
    rows = rows.order_by("sentence__book", "sentence__chapter", "sentence__verse", "sentence__number")
    return [{"refs": verse_ids, "status": status, "renderings": {lang: {level: text}}}
            for verse_ids, status, text in rows.values_list("sentence__refs", "sentence__status", "text")]


def _expected(books):
    """Every verse id our source texts have, for the manifest's missing list."""
    verses = Verse.objects.filter(edition__kind=Edition.Kind.ORIGINAL)
    if books:
        verses = verses.filter(book__in=books)
    return [f"{b}.{c}.{v}" for b, c, v in verses.values_list("book", "chapter", "verse")]


@admin_view("export")
def options(request):
    counts = {}
    for row in Rendering.objects.values("language", "level").annotate(n=Count("id")):
        counts.setdefault(row["language"], {})[row["level"]] = row["n"]
    run = ImportRun.objects.exclude(finished_at=None).first()
    recent = AdminAction.objects.filter(action="export.download")[:10]
    return Response({
        "languages": [{"code": c, "name": lang["name"], "sentences": counts.get(c, {}),
                       "settings": [{"name": n, "options": o} for n, o in export.settings_for(c).items()]}
                      for c, lang in languages.READING.items()],
        "levels": [{"code": c, "name": n} for c, n in export.LEVELS.items()],
        "formats": list(export.FORMATS),
        "books": [{"code": c, "name": book_name(c)} for c in refs.BOOK_CODES],
        "imported_at": run.finished_at if run else None,
        "licence": export.LICENCE,
        "recent": [{"by": a.actor_email, "target": a.target, "detail": a.detail, "at": a.created_at} for a in recent],
    })


@admin_view("export")
def preview(request):
    lang, level, _, numbering, books, settings = _options(request.query_params)
    records = _records(lang, level, books)
    *_, manifest = export.build(records, lang, level, "json", numbering, settings, books or None,
                                expected=_expected(books))
    verses = export.verse_texts(records, lang, level, settings)
    shown = [v for v in SAMPLES if v in verses] or list(verses)[:3]
    missing = manifest.get("missing", {})
    return Response({"verses": manifest["verses"], "books": manifest["books"], "status": manifest["status"],
                     "missing": missing.get("count", 0), "missing_by_book": missing.get("by_book", {}),
                     "combined": manifest["combined"], "settings": manifest["settings"],
                     "samples": [{"verse": v, "label": verse_label(v), "text": verses[v]} for v in shown]})


@admin_view("export")
def download(request):
    lang, level, fmt, numbering, books, settings = _options(request.query_params)
    name, content_type, body, manifest = export.build(
        _records(lang, level, books), lang, level, fmt, numbering, settings, books or None,
        expected=_expected(books), generated_at=timezone.now().isoformat(timespec="seconds"),
        commit=os.environ.get("RENDER_GIT_COMMIT", ""))
    record(request.user, "export.download", name, language=lang, level=level, format=fmt, numbering=numbering,
           books=books, settings=manifest["settings"], verses=manifest["verses"])
    response = HttpResponse(body, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{name}"'
    response["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response
