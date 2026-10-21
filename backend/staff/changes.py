"""What each deploy changed in the translation (import_content records it).

GET /api/admin/changes/?run=&lang=&book=&offset=
        the latest imports, each with how many renderings it changed and how
        many sentences it drafted in a language for the first time; and the
        changed renderings of one import (the latest that changed any, unless
        run names one), before and after, filtered by language or book

A rendering counts as changed when an import added, rewrote or removed it in
a sentence already drafted in that language. A sentence drafted in a
language for the first time is only counted, by book and language.
"""
from django.db.models import Count
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from owb import languages, refs
from translation.models import ImportRun

from .inbox import verse_label
from .permissions import admin_view

PAGE = 100
RUNS = 20


def _run_json(run):
    drafted = {}
    for counts in run.drafted.values():
        for lang, n in counts.items():
            drafted[lang] = drafted.get(lang, 0) + n
    return {"id": run.id, "started_at": run.started_at, "finished_at": run.finished_at,
            "files": run.files, "records": run.records, "error": run.error,
            "changed": run.n_changes, "drafted": drafted}


@admin_view("overview")
def changes(request):
    runs = list(ImportRun.objects.annotate(n_changes=Count("changes")).order_by("-started_at", "-id")[:RUNS])
    answer = {"runs": [_run_json(r) for r in runs],
              "languages": [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items()]}
    try:
        wanted = int(request.query_params.get("run") or 0)
        offset = max(int(request.query_params.get("offset") or 0), 0)
    except ValueError:
        raise ValidationError({"detail": "run and offset are numbers."})
    if wanted:
        run = ImportRun.objects.annotate(n_changes=Count("changes")).filter(id=wanted).first()
        if run is None:
            raise NotFound(f"No import {wanted}")
    else:
        run = next((r for r in runs if r.n_changes), None)
    if run is None:
        return Response({**answer, "run": None})
    rows = run.changes.all()
    lang = request.query_params.get("lang") or ""
    book = (request.query_params.get("book") or "").upper()
    if lang:
        rows = rows.filter(language=lang)
    if book:
        rows = rows.filter(book=book)
    by_book = {}
    for code, n in run.changes.values_list("book").annotate(n=Count("id")):
        by_book[code] = n
    drafted = [{"code": code, "name": refs.BOOK_NAMES.get(code, code), "languages": counts}
               for code, counts in sorted(run.drafted.items(), key=lambda kv: refs.BOOK_CODES.index(kv[0])
                                          if kv[0] in refs.BOOK_CODES else 99)]
    page = list(rows[offset:offset + PAGE + 1])
    return Response({
        **answer, "run": {**_run_json(run), "drafted_books": drafted,
                          "books": [{"code": c, "name": refs.BOOK_NAMES.get(c, c), "changes": by_book[c]}
                                    for c in refs.BOOK_CODES if c in by_book]},
        "offset": offset, "more": len(page) > PAGE,
        "changes": [{"record": c.record_id, "verse": c.verse, "label": verse_label(c.verse),
                     "language": c.language, "level": c.level, "kind": c.kind,
                     "before": c.before, "after": c.after} for c in page[:PAGE]],
    })
