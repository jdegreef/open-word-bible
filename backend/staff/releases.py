"""Releases as records: cutting a release of one language, with a check
of whether it is ready first.

GET  /api/admin/releases/?lang=fr
        the language's releases, newest first; what is ready and what
        isn't now (open flags, approvals the text has changed under, CI on
        main, the last import); and since: when the last release was cut,
        where the next release's notes start
POST /api/admin/releases/  {lang, name}
        cut one: main's commit, the readiness and the notes' totals since
        the last release are kept with it

What became fully reviewed counts the sentences drafted in the language
whose meaning and wording are both approved now, the later approval since
the last release. Nothing here changes a sentence or its review.
"""
from django.db.models import Max
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from owb import languages
from translation.models import ImportRun, ReviewState

from . import people
from .history import release_notes
from .models import Release, record
from .permissions import admin_view
from .progress import _ci_status
from .review import ORIGINAL_LAYERS, _scope, refresh

RS = ReviewState.State


def fully_reviewed(lang, since):
    """Sentences drafted in lang approved in its meaning and its wording now,
    the later of the two approvals after since (all of them if None)."""
    for code in (lang, *ORIGINAL_LAYERS):
        refresh(code)
    drafted = _scope(lang).values("id")
    wording = dict(ReviewState.objects.filter(layer=lang, state=RS.APPROVED, sentence__in=drafted)
                   .values_list("sentence_id", "event__created_at"))
    meaning = dict(ReviewState.objects.filter(layer__in=ORIGINAL_LAYERS, state=RS.APPROVED, sentence_id__in=wording)
                   .values_list("sentence_id", "event__created_at"))
    return sum(1 for sid, at in meaning.items() if since is None or max(at, wording[sid]) > since)


def readiness(lang):
    """What stands in the way of a release now: [{key, label, count, ok, href}]."""
    for code in (lang, *ORIGINAL_LAYERS):
        refresh(code)
    drafted = _scope(lang).values("id")
    flags = ReviewState.objects.filter(layer=lang, state=RS.FLAGGED).count()
    meaning_flags = ReviewState.objects.filter(layer__in=ORIGINAL_LAYERS, state=RS.FLAGGED,
                                               sentence__in=drafted).count()
    changed = ReviewState.objects.filter(layer=lang, state=RS.CHANGED).count()
    ci = _ci_status()
    failing = [c["name"] for c in (ci or {}).get("checks", []) if c["conclusion"] not in (None, "success", "skipped",
                                                                                        "neutral")]
    run = ImportRun.objects.order_by("-started_at").first()
    name = languages.READING[lang]["name"]
    return [
        {"key": "flags", "label": f"Open flags on the {name} wording", "count": flags, "ok": not flags,
         "href": "#flags"},
        {"key": "meaning_flags", "label": f"Open flags on the meaning of sentences drafted in {name}",
         "count": meaning_flags, "ok": not meaning_flags, "href": "#flags"},
        {"key": "changed", "label": "Approvals the wording has changed under", "count": changed, "ok": not changed,
         "href": f"#review/{lang}?state=changed"},
        {"key": "ci", "label": "CI on main" + (f" ({ci['sha']})" if ci else ""),
         "count": len(failing), "ok": bool(ci) and not failing, "href": "#health",
         "detail": ", ".join(failing) if failing else ("passing" if ci else "GitHub could not be reached")},
        {"key": "import", "label": "The last content import", "count": int(bool(run and run.error)),
         "ok": bool(run and run.finished_at and not run.error), "href": "#health",
         "detail": (run.error[:200] if run and run.error else "finished" if run and run.finished_at
                    else "none yet" if not run else "still running")},
    ], ci


def release_json(r):
    return {"id": r.id, "language": r.language, "name": r.name, "commit": r.commit, "cut_at": r.cut_at,
            "cut_by": people.name(r.cut_by) if r.cut_by else "", "summary": r.summary}


def _lang(value):
    if value not in languages.READING:
        raise ValidationError({"lang": "Choose a reading language.", "code": "invalid_language"})
    return value


@admin_view("export", methods=("GET", "POST"))
def releases(request):
    if request.method == "POST":
        return _cut(request)
    lang = _lang(request.query_params.get("lang") or "en")
    rows = Release.objects.filter(language=lang).select_related("cut_by")
    last = rows.first()
    checks, _ = readiness(lang)
    since = last.cut_at if last else None
    latest = dict(Release.objects.values("language").annotate(t=Max("cut_at")).values_list("language", "t"))
    return Response({
        "language": {"code": lang, "name": languages.READING[lang]["name"]},
        "releases": [release_json(r) for r in rows[:50]], "since": since,
        "readiness": checks, "ready": all(c["ok"] for c in checks),
        "fully_reviewed": fully_reviewed(lang, since),
        "languages": [{"code": c, "name": x["name"], "last": latest.get(c)} for c, x in languages.READING.items()],
    })


def _cut(request):
    data = request.data if isinstance(request.data, dict) else {}
    lang = _lang(data.get("lang"))
    name = " ".join(str(data.get("name") or "").split())
    if not name:
        raise ValidationError({"name": "Name the release.", "code": "empty"})
    if len(name) > 80:
        raise ValidationError({"name": "Keep the name under 80 characters.", "code": "too_long"})
    last = Release.objects.filter(language=lang).first()
    since = last.cut_at if last else None
    checks, ci = readiness(lang)
    now = timezone.now()
    notes = release_notes(lang, since or now.replace(year=2000), now)
    r = Release.objects.create(language=lang, name=name, commit=ci["sha"] if ci else "", cut_by=request.user,
                               summary={"totals": notes["totals"], "imports": notes["imports"],
                                        "since": since.isoformat() if since else None,
                                        "fully_reviewed": fully_reviewed(lang, since),
                                        "ready": all(c["ok"] for c in checks),
                                        "not_ready": [c["label"] for c in checks if not c["ok"]]})
    record(request.user, "release.cut", f"{name} ({lang})", language=lang, commit=r.commit)
    return Response({"release": release_json(r)}, status=status.HTTP_201_CREATED)
