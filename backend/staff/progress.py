"""The admin's progress pages: numbers about the translation, from the
database (which import_content keeps in step with content/ on main).

GET /api/admin/overview/        the dashboard: totals, what needs attention,
                                recent activity
GET /api/admin/coverage/        every book: chapters and sentences drafted,
                                and sentences in each language
GET /api/admin/languages/       each reading language's progress and team
GET /api/admin/books/<BOOK>/    one book, chapter by chapter
GET /api/admin/health/          the last imports, the loaded texts, CI on main and
                                what the super admins are alerted to (staff/alerts.py)
GET /api/admin/engagement/      what signed-in readers keep: totals only

A sentence counts as drafted in a language when it has any rendering in it;
statuses are a sentence's, shared by its languages. Nothing here names a
reader.
"""
import json
import logging
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, Max, Q, Sum
from django.db.models.functions import TruncWeek
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from accounts.models import ApiToken, Mark, ReadingPlace, Role
from feedback.models import ReaderMessage
from owb import languages, refs
from texts.models import Edition
from translation import counts
from translation.models import ContentFile, Decision, DraftedCount, ImportRun, Rendering, ReviewEvent, Sentence

from . import assignments, inbox
from .models import AdminAction
from .permissions import admin_view
from .review import open_flag_count

log = logging.getLogger(__name__)

_BOOKS = json.loads((settings.REPO_ROOT / "data" / "books.json").read_text(encoding="utf-8"))["books"]
CHAPTERS = {code: _BOOKS[code]["chapters"] for code in refs.BOOK_CODES}
LANGS = languages.CODES
OT = set(refs.OT_CODES)


def book_name(code):
    return _BOOKS[code]["en"]


def _languages():
    return [{"code": code, "name": lang["name"], "native": lang["native"]}
            for code, lang in languages.READING.items()]


def _stamps():
    """(content, review): strings that change when a sentence is added or
    saved again (import_content saves a sentence, bumping its updated_at,
    whenever its renderings change), when the drafted counts change
    (import_content, `manage.py recount_drafted`), and when a review is
    made. Cache keys for what is counted from them."""
    stamp = Sentence.objects.aggregate(n=Count("id"), t=Max("updated_at"))
    drafted = DraftedCount.objects.aggregate(n=Sum("sentences"))["n"] or 0
    content = "{}.{}.{}".format(stamp["n"], stamp["t"].timestamp() if stamp["t"] else 0, drafted)
    return content, f"{content}.{ReviewEvent.objects.aggregate(i=Max('id'))['i'] or 0}"


def _by_book():
    """{book: {"sentences", "chapters", "statuses": {status: n}, "langs": {lang: n}}}
    for every book with a sentence. Drafted counts come from DraftedCount,
    which import_content keeps, so nothing here reads the renderings; the
    rest is two small queries over the sentences."""
    out = {}
    for row in Sentence.objects.values("book").annotate(n=Count("id"), chapters=Count("chapter", distinct=True)):
        out[row["book"]] = {"sentences": row["n"], "chapters": row["chapters"], "statuses": {}, "langs": {}}
    for row in Sentence.objects.values("book", "status").annotate(n=Count("id")):
        out[row["book"]]["statuses"][row["status"]] = row["n"]
    for book, langs in counts.by_book().items():
        if book in out:
            out[book]["langs"] = langs
    return out


def _state(book, rendered, sentences, chapters_drafted):
    """A book in one language: "none", "partial" (some of it) or "drafted"
    (every chapter, every sentence)."""
    if not rendered:
        return "none"
    if rendered >= sentences and chapters_drafted >= CHAPTERS[book]:
        return "drafted"
    return "partial"


def _coverage():
    data = _by_book()
    books = []
    for code in refs.BOOK_CODES:
        row = data.get(code, {"sentences": 0, "chapters": 0, "statuses": {}, "langs": {}})
        books.append({
            "code": code, "name": book_name(code), "testament": "ot" if code in OT else "nt",
            "chapters": CHAPTERS[code], "chapters_drafted": row["chapters"],
            "sentences": row["sentences"], "statuses": row["statuses"],
            "languages": {lang: {"sentences": row["langs"].get(lang, 0),
                                 "state": _state(code, row["langs"].get(lang, 0), row["sentences"],
                                                 row["chapters"])}
                          for lang in LANGS},
        })
    return books


@admin_view("overview")
def coverage(request):
    return Response({"languages": _languages(), "statuses": dict(Sentence._meta.get_field("status").choices),
                     "books": _coverage()})


def _language_rows(books):
    reviewers = dict(Role.objects.filter(kind=Role.Kind.LANGUAGE_REVIEWER).values("language")
                     .annotate(n=Count("id")).values_list("language", "n"))
    uncertain = dict(Decision.objects.filter(uncertain=True).exclude(language="").values("language")
                     .annotate(n=Count("id")).values_list("language", "n"))
    waiting = dict(ReaderMessage.objects.filter(status=ReaderMessage.Status.NEW).values("language")
                   .annotate(n=Count("id")).values_list("language", "n"))
    total = sum(b["sentences"] for b in books)
    rows = []
    for lang in _languages():
        code = lang["code"]
        states = [b["languages"][code]["state"] for b in books]
        brief = settings.REPO_ROOT / "docs" / f"{lang['name'].lower()}-style.md"
        rows.append({
            **lang,
            "sentences": sum(b["languages"][code]["sentences"] for b in books),
            "of": total,
            "books_drafted": states.count("drafted"), "books_partial": states.count("partial"),
            "nt_drafted": sum(1 for b in books
                              if b["testament"] == "nt" and b["languages"][code]["state"] == "drafted"),
            "uncertain": uncertain.get(code, 0),
            "reviewers": reviewers.get(code, 0),
            "messages": waiting.get(code, 0),
            "style_brief": f"docs/{brief.name}" if brief.is_file() else "",
        })
    return rows


@admin_view("overview")
def language_list(request):
    return Response({"languages": _language_rows(_coverage()),
                     "meaning_uncertain": Decision.objects.filter(uncertain=True, language="").count()})


@admin_view("overview")
def book(request, code):
    code = code.upper()
    if code not in CHAPTERS:
        raise NotFound(f"Unknown book {code!r}")
    chapters = {n: {"chapter": n, "sentences": 0, "languages": {lang: 0 for lang in LANGS}, "statuses": {}}
                for n in range(1, CHAPTERS[code] + 1)}
    for row in Sentence.objects.filter(book=code).values("chapter").annotate(n=Count("id")):
        chapters[row["chapter"]]["sentences"] = row["n"]
    for row in Sentence.objects.filter(book=code).values("chapter", "status").annotate(n=Count("id")):
        chapters[row["chapter"]]["statuses"][row["status"]] = row["n"]
    for row in (Rendering.objects.filter(sentence__book=code).values("sentence__chapter", "language")
                .annotate(n=Count("sentence", distinct=True))):
        chapters[row["sentence__chapter"]]["languages"][row["language"]] = row["n"]
    files = sorted(ContentFile.objects.filter(path__startswith=f"content/{code}/").values_list("path", flat=True))
    uncertain = (Decision.objects.filter(sentence__book=code, uncertain=True)
                 .values("language").annotate(n=Count("id")))
    messages = (ReaderMessage.objects.filter(verse__startswith=f"{code}.")
                .exclude(status__in=[ReaderMessage.Status.DONE, ReaderMessage.Status.DECLINED]).count())
    return Response({
        "code": code, "name": book_name(code), "testament": "ot" if code in OT else "nt",
        "languages": _languages(), "chapters": list(chapters.values()), "files": files,
        "uncertain": {row["language"] or "meaning": row["n"] for row in uncertain},
        "open_messages": messages,
        "updated": Sentence.objects.filter(book=code).aggregate(t=Max("updated_at"))["t"],
    })


def _ci_status():
    """CI's checks on main's latest commit, from GitHub (cached five
    minutes), or None when GitHub can't be reached."""
    cached = cache.get("staff.ci")
    if cached is not None:
        return cached or None
    repo = settings.OWB_GITHUB_REPO
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "open-word-bible-admin"}
    if settings.OWB_GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.OWB_GITHUB_TOKEN}"

    def get(path):
        req = urllib.request.Request(f"https://api.github.com/repos/{repo}/{path}", headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.load(r)
    try:
        commit = get("commits/main")
        runs = get(f"commits/{commit['sha']}/check-runs?per_page=50")["check_runs"]
    except Exception:
        log.warning("GitHub status for main could not be fetched", exc_info=True)
        cache.set("staff.ci", {}, 60)
        return None
    status = {
        "sha": commit["sha"][:7], "url": commit["html_url"],
        "message": commit["commit"]["message"].splitlines()[0][:200],
        "date": commit["commit"]["committer"]["date"],
        "checks": [{"name": r["name"], "status": r["status"], "conclusion": r["conclusion"],
                    "url": r["html_url"]} for r in runs],
    }
    cache.set("staff.ci", status, 300)
    return status


def _run_json(run):
    return {"started_at": run.started_at, "finished_at": run.finished_at, "everything": run.everything,
            "files": run.files, "records": run.records, "unchanged": run.unchanged,
            "skipped": run.skipped, "error": run.error,
            "ok": bool(run.finished_at) and not run.error}


@admin_view("overview")
def health(request):
    from . import alerts   # alerts reads jobs, which reads this module
    return Response({
        "imports": [_run_json(r) for r in ImportRun.objects.all()[:15]],
        "content_files": ContentFile.objects.count(),
        "sentences": Sentence.objects.count(),
        "last_sentence_update": Sentence.objects.aggregate(t=Max("updated_at"))["t"],
        "editions": [{"code": e.code, "name": e.name, "kind": e.kind, "language": e.language,
                      "verses": e.verse_count, "imported_at": e.imported_at,
                      "source_commit": e.source_commit[:7]}
                     for e in Edition.objects.order_by("kind", "code")],
        "ci": _ci_status(),
        "alerts": alerts.current(),
    })


@admin_view("overview")
def engagement(request):
    """Totals over what accounts already keep (bookmarks, highlights,
    reading places, devices). The site itself records nothing about reading
    (see the privacy page), so readers without an account are not counted."""
    User = get_user_model()
    now = timezone.now()
    since = now - timedelta(weeks=12)
    signups = (User.objects.filter(date_joined__gte=since).annotate(week=TruncWeek("date_joined"))
               .values("week").annotate(n=Count("id")).order_by("week"))
    marks = Mark.objects.aggregate(bookmarks=Count("id", filter=Q(bookmark=True)),
                                   highlights=Count("id", filter=~Q(highlight="")),
                                   readers=Count("user", distinct=True))
    by_book = {}
    for row in Mark.objects.values("verse").annotate(n=Count("id")):
        code = row["verse"].split(".", 1)[0]
        by_book[code] = by_book.get(code, 0) + row["n"]
    places = ReadingPlace.objects.values("book").annotate(n=Count("id")).order_by("-n")[:12]
    return Response({
        "accounts": User.objects.count(),
        "active_30": User.objects.filter(last_login__gte=now - timedelta(days=30)).count(),
        "active_7": User.objects.filter(last_login__gte=now - timedelta(days=7)).count(),
        "devices_30": ApiToken.objects.filter(last_used_at__gte=now - timedelta(days=30)).count(),
        "signups": [{"week": row["week"].date().isoformat(), "accounts": row["n"]} for row in signups],
        "marks": marks,
        "marks_by_language": list(Mark.objects.exclude(lang="").values("lang").annotate(n=Count("id")).order_by("-n")),
        "marks_by_book": [{"code": c, "name": book_name(c), "marks": n}
                          for c, n in sorted(by_book.items(), key=lambda kv: -kv[1])[:12] if c in CHAPTERS],
        "reading_places": [{"code": p["book"], "name": book_name(p["book"]), "readers": p["n"]}
                           for p in places if p["book"] in CHAPTERS],
        "messages": ReaderMessage.objects.count(),
    })


def _summary():
    """The dashboard's numbers that are the same for every account, cached
    until the content changes or a review is made: the totals, each
    language's sentences, books not started or partly drafted, and the
    open flags."""
    stamps = _stamps()
    key = f"staff.overview.{stamps[1]}"
    out = cache.get(key)
    if out is not None:
        return out
    books = _coverage()
    statuses = {}
    for b in books:
        for status, n in b["statuses"].items():
            statuses[status] = statuses.get(status, 0) + n
    out = {
        "totals": {
            "sentences": sum(b["sentences"] for b in books),
            "books_started": sum(1 for b in books if b["sentences"]),
            "books_drafted": sum(1 for b in books if b["languages"]["en"]["state"] == "drafted"),
            "books": len(books),
            "chapters_drafted": sum(b["chapters_drafted"] for b in books),
            "chapters": sum(CHAPTERS.values()),
            "statuses": statuses,
        },
        "languages": [{**lang, "sentences": sum(b["languages"][lang["code"]]["sentences"] for b in books)}
                      for lang in _languages()],
        "not_started": sum(1 for b in books if not b["sentences"]),
        "partial": sum(1 for b in books if b["sentences"] and b["chapters_drafted"] < b["chapters"]),
        "flags": open_flag_count(),
    }
    cache.set(key, out, 7 * 86400)
    return out


@admin_view("overview")
def overview(request):
    """The dashboard. What needs attention comes first, each item linking to
    the admin page that deals with it; areas the account can't open are
    left out. The numbers about the translation come from _summary; the
    inbox, the team and the last import are read as they are (each a
    query on an index)."""
    mine = request.admin_areas
    summary = _summary()
    attention = []
    if "inbox" in mine:
        waiting = ReaderMessage.objects.filter(status=ReaderMessage.Status.NEW).aggregate(
            new=Count("id"),
            late=Count("id", filter=Q(created_at__lt=timezone.now() - timedelta(days=inbox.WAITING_DAYS))),
            mine=Count("id", filter=Q(assigned_to=request.user)))
        if waiting["late"]:
            attention.append({"key": "inbox_late", "count": waiting["late"], "tone": "hot",
                              "label": f"reader messages waiting more than {inbox.WAITING_DAYS} days",
                              "href": "#inbox"})
        if waiting["new"]:
            attention.append({"key": "inbox", "count": waiting["new"], "tone": "hot",
                              "label": "reader messages waiting for an answer", "href": "#inbox"})
        if waiting["mine"]:
            attention.append({"key": "inbox_mine", "count": waiting["mine"], "tone": "warn",
                              "label": "reader messages assigned to you", "href": "#inbox/mine"})
        if summary["flags"]:
            attention.append({"key": "flags", "count": summary["flags"], "tone": "hot",
                              "label": "sentences flagged by reviewers", "href": "#flags"})
    if "review" in mine:
        assigned, overdue = assignments.attention(request.user)
        if overdue:
            attention.append({"key": "assigned_overdue", "count": overdue, "tone": "hot",
                              "label": "review assignments past their date", "href": "#workspace"})
        if assigned:
            attention.append({"key": "assigned", "count": assigned, "tone": "warn",
                              "label": "review assignments assigned to you", "href": "#workspace"})
    if "team" in mine:
        pending = (get_user_model().objects.filter(last_login__isnull=True, roles__isnull=False)
                   .distinct().count())
        if pending:
            attention.append({"key": "invites", "count": pending, "tone": "warn",
                              "label": "invited team members who haven't signed in", "href": "#team"})
    last = ImportRun.objects.first()
    if last and last.error:
        attention.append({"key": "import", "count": 1, "tone": "hot",
                          "label": "the last content import failed", "href": "#health"})
    elif last and last.skipped:
        attention.append({"key": "import", "count": len(last.skipped), "tone": "warn",
                          "label": "content files skipped for a missing source text", "href": "#health"})
    if summary["not_started"]:
        attention.append({"key": "books", "count": summary["not_started"], "tone": "info",
                          "label": "books not started in English", "href": "#coverage"})
    if summary["partial"]:
        attention.append({"key": "partial", "count": summary["partial"], "tone": "info",
                          "label": "books partly drafted", "href": "#coverage"})
    activity = []
    if "team" in mine:
        activity = [_action_json(a) for a in AdminAction.objects.all()[:8]]
    return Response({
        "totals": summary["totals"],
        "languages": summary["languages"],
        "attention": attention,
        "activity": activity,
        "last_import": _run_json(last) if last else None,
    })


def _action_json(a):
    return {"id": a.id, "actor": a.actor_email, "action": a.action, "target": a.target,
            "detail": a.detail, "at": a.created_at}
