"""Drafting jobs: a super admin asks for a book to be drafted in some
languages, and the admin files a GitHub issue labelled drafting-job for a
Claude session to pick up (.claude/skills/drafting-worker).

GET  /api/admin/jobs/                         open drafting jobs on GitHub, and
                                              the queue board: each book in each
                                              language, drafted, asked for in an
                                              open job, or with a pull request open
POST /api/admin/jobs/  {book, languages, note} file one
POST /api/admin/jobs/bulk/  {languages, testament or books, note, dry_run}
                                              file one job per book still missing
                                              any of the languages, in Bible order,
                                              at most BULK_LIMIT at a time; dry_run
                                              answers with the plan only. Filing
                                              goes on in the background (202, with
                                              the run's id)
GET  /api/admin/jobs/bulk/<id>/               that filing's progress: state
                                              ("filing", "done", "stopped"), filed,
                                              not_filed, error

Filing needs OWB_GITHUB_TOKEN (a token that may create issues in
OWB_GITHUB_REPO); without it the page says so. Before filing, the request
is checked against the database (a language that already has the whole
book is refused) and against the open jobs (the same book and language
asked for twice is refused), as the check-book-before-translating skill
does for a session.
"""
import json
import logging
import threading
import uuid

from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from owb import languages, refs

from . import github, people
from .github import GitHubError
from .models import record
from .permissions import admin_view
from .progress import CHAPTERS, _coverage, book_name

log = logging.getLogger(__name__)
LABEL = "drafting-job"
BULK_LIMIT = 40     # jobs one bulk request files; the rest wait for the next
TESTAMENTS = {"ot": refs.OT_CODES, "nt": [c for c in refs.BOOK_CODES if c not in refs.OT_CODES],
              "all": refs.BOOK_CODES}


def marker(issue, name):
    """The machine-readable line the admin writes into an issue it files
    ("<!-- drafting-job {...} -->"), as a dict; {} when there is none, or
    when it isn't a JSON object (an issue body anyone can edit must not
    break the admin's lists)."""
    start = f"<!-- {name} "
    for line in (issue.get("body") or "").splitlines():
        if line.startswith(start) and line.endswith(" -->"):
            try:
                data = json.loads(line[len(start):-len(" -->")])
            except ValueError:
                return {}
            return data if isinstance(data, dict) else {}
    return {}


def _parse_job(issue):
    """The book and languages a drafting-job issue asks for."""
    return marker(issue, "drafting-job")


def listed(data, name):
    """data[name] as a list of strings (codes, slugs), or a 400."""
    value = data.get(name) or []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ValidationError({name: "Send a list.", "code": "invalid"})
    return value


def open_jobs():
    issues = github.call(f"issues?labels={LABEL}&state=open&per_page=100")
    # The issue's own fields last, so the marker can't stand in for them.
    return [{**_parse_job(i), "number": i["number"], "title": i["title"], "url": i["html_url"],
             "created_at": i["created_at"], "assignees": [a["login"] for a in i.get("assignees", [])]}
            for i in issues if "pull_request" not in i]


@admin_view("jobs", methods=("GET", "POST"), once=True)
def jobs(request):
    if request.method == "POST":
        return _file(request)
    books = [{"code": c, "name": book_name(c), "chapters": CHAPTERS[c]} for c in refs.BOOK_CODES]
    langs = [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items()]
    coverage = {b["code"]: {lang: s["state"] for lang, s in b["languages"].items()} for b in _coverage()}
    answer = {"configured": bool(settings.OWB_GITHUB_TOKEN), "repo": settings.OWB_GITHUB_REPO,
              "books": [{**b, "testament": "ot" if b["code"] in refs.OT_CODES else "nt"} for b in books],
              "languages": langs, "coverage": coverage, "bulk_limit": BULK_LIMIT}
    try:
        answer["jobs"] = open_jobs()
    except GitHubError:
        answer["jobs"], answer["error"] = [], "GitHub could not be reached, so open jobs aren't listed."
    answer["board"] = _board(coverage, answer["jobs"])
    return Response(answer)


def _board(coverage, open_):
    """{book: {lang: {"state", "url", "number"}}}: "drafted" or "partial"
    from the database, unless an open job asks for the pair: then "pr" when
    the job has a pull request open, else "filed". Pairs with nothing are
    left out."""
    from .work import cached_work   # work imports this module
    try:
        prs = {w["number"]: [p for p in w["prs"] if p["state"] in ("open", "draft")] for w in cached_work()}
    except GitHubError:
        prs = {}
    board = {}
    for code, langs in coverage.items():
        for lang, state in langs.items():
            if state != "none":
                board.setdefault(code, {})[lang] = {"state": state, "url": "", "number": None}
    for job in open_:
        for lang in job.get("languages", []):
            if job.get("book") not in coverage or coverage[job["book"]].get(lang) in (None, "drafted"):
                continue
            pr = (prs.get(job["number"]) or [None])[0]
            board.setdefault(job["book"], {})[lang] = (
                {"state": "pr", "url": pr["url"], "number": pr["number"]} if pr
                else {"state": "filed", "url": job["url"], "number": job["number"]})
    return board


def _file(request):
    if not settings.OWB_GITHUB_TOKEN:
        return Response({"detail": "Set OWB_GITHUB_TOKEN on the API service to file jobs from here.",
                         "code": "not_configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    data = request.data if isinstance(request.data, dict) else {}
    book = str(data.get("book", "")).upper()
    if book not in CHAPTERS:
        raise ValidationError({"book": "Choose a book.", "code": "invalid_book"})
    wanted = [c for c in languages.CODES if c in listed(data, "languages")]
    if not wanted:
        raise ValidationError({"languages": "Choose at least one language.", "code": "invalid_language"})
    note = str(data.get("note", "") or "").strip()[:2000]
    coverage = next(b for b in _coverage() if b["code"] == book)["languages"]
    done = [c for c in wanted if coverage[c]["state"] == "drafted"]
    if done:
        raise ValidationError({"languages": f"{book_name(book)} is already drafted in "
                               f"{', '.join(languages.READING[c]['name'] for c in done)}.",
                               "code": "already_drafted"})
    if "en" not in wanted and coverage["en"]["state"] != "drafted":
        raise ValidationError({"languages": f"{book_name(book)} isn't drafted in English yet; "
                               "English comes first.", "code": "english_first"})
    try:
        clash = [j for j in open_jobs() if j.get("book") == book and set(j.get("languages", [])) & set(wanted)]
    except GitHubError:
        return Response({"detail": "GitHub could not be reached. Try again in a minute.", "code": "github"},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    if clash:
        raise ValidationError({"languages": f"Job #{clash[0]['number']} already asks for that.",
                               "code": "duplicate"})
    try:
        issue = _file_issue(request.user, book, wanted, coverage, note)
    except GitHubError:
        return Response({"detail": "GitHub refused the job. Check OWB_GITHUB_TOKEN can create issues.",
                         "code": "github"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"number": issue["number"], "url": issue["html_url"]}, status=status.HTTP_201_CREATED)


def _file_issue(user, book, wanted, coverage, note, bulk=False):
    """File the drafting-job issue asking for book in the languages wanted,
    and log it. coverage is the book's {lang: {"state", ...}}."""
    names = ", ".join(languages.READING[c]["name"] for c in wanted)
    lines = [f"Draft **{book_name(book)}** ({CHAPTERS[book]} chapters) in {names}.", ""]
    for c in wanted:
        state = coverage[c]["state"]
        lines.append(f"- {languages.READING[c]['name']}: "
                     f"{'partly drafted; finish what is missing' if state == 'partial' else 'not started'}")
    lines += ["", "Follow `.claude/skills/drafting-worker/SKILL.md`: run check-book-before-translating "
              "first, draft as `ai_draft` only, and open one pull request per book and language."]
    if note:
        lines += ["", "**Note from the admin:**", "", note]
    lines += ["", f"Filed from the admin by {people.public_name(user)}.", "",
              "<!-- drafting-job " + json.dumps({"book": book, "languages": wanted}) + " -->"]
    issue = github.call("issues", "POST", {"title": f"Draft {book_name(book)} in {names}",
                                       "body": "\n".join(lines), "labels": [LABEL]})
    record(user, "job.file", f"#{issue['number']} {book}", languages=wanted, **({"bulk": True} if bulk else {}))
    return issue


def _plan(books, wanted, coverage, open_):
    """What a bulk request would file, [{"book", "languages"}] in Bible
    order, and the books it leaves out, [{"book", "reason"}]. A book gets the
    languages it still lacks that no open job already asks for; as for one
    job, English comes first."""
    plan, skipped = [], []
    for book in books:
        cov = coverage[book]
        missing = [c for c in wanted if cov[c]["state"] != "drafted"]
        if not missing:
            skipped.append({"book": book, "reason": "already drafted"})
            continue
        asked = {}
        for job in open_:
            if job.get("book") == book:
                for c in job.get("languages", []):
                    asked.setdefault(c, job["number"])
        free = [c for c in missing if c not in asked]
        if not free:
            skipped.append({"book": book, "reason": "already asked for in "
                            + ", ".join(sorted({f"#{asked[c]}" for c in missing}))})
            continue
        if "en" not in free and cov["en"]["state"] != "drafted":
            skipped.append({"book": book, "reason": "not drafted in English yet"})
            continue
        plan.append({"book": book, "languages": free})
    return plan, skipped


@admin_view("jobs", methods=("POST",), once=True)
def bulk(request):
    data = request.data if isinstance(request.data, dict) else {}
    dry_run = bool(data.get("dry_run"))
    if not dry_run and not settings.OWB_GITHUB_TOKEN:
        return Response({"detail": "Set OWB_GITHUB_TOKEN on the API service to file jobs from here.",
                         "code": "not_configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    wanted = [c for c in languages.CODES if c in listed(data, "languages")]
    if not wanted:
        raise ValidationError({"languages": "Choose at least one language.", "code": "invalid_language"})
    if data.get("books"):
        asked = {b.upper() for b in listed(data, "books")}
        if asked - set(CHAPTERS):
            raise ValidationError({"books": f"Unknown book {sorted(asked - set(CHAPTERS))[0]!r}.",
                                   "code": "invalid_book"})
        books = [c for c in refs.BOOK_CODES if c in asked]
    elif data.get("testament") in TESTAMENTS:
        books = list(TESTAMENTS[data["testament"]])
    else:
        raise ValidationError({"testament": "Choose the Old Testament, the New Testament or both.",
                               "code": "invalid_testament"})
    note = str(data.get("note", "") or "").strip()[:2000]
    coverage = {b["code"]: b["languages"] for b in _coverage()}
    try:
        open_ = open_jobs()
    except GitHubError:
        return Response({"detail": "GitHub could not be reached. Try again in a minute.", "code": "github"},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    plan, skipped = _plan(books, wanted, coverage, open_)
    now, later = plan[:BULK_LIMIT], plan[BULK_LIMIT:]
    answer = {"dry_run": dry_run, "plan": now, "skipped": skipped, "remaining": len(later),
              "limit": BULK_LIMIT, "filed": []}
    if dry_run or not now:
        return Response(answer)
    # Filing is one GitHub request a job, up to 10 s each: 40 of them would
    # outlast the web server's 60 s. A thread files them and keeps its
    # progress where GET jobs/bulk/<id>/ reads it, on any worker.
    run = {**answer, "id": uuid.uuid4().hex[:12], "state": "filing", "not_filed": [], "error": "",
           "by": request.user.username, "started_at": timezone.now().isoformat()}
    cache.set(_run_key(run["id"]), run, RUN_KEEP)
    _start(_file_all, request.user, run, {b: coverage[b] for b in {j["book"] for j in now}}, note)
    return Response(cache.get(_run_key(run["id"])) or run, status=status.HTTP_202_ACCEPTED)


RUN_KEEP = 86400   # how long a bulk filing's progress can be read


def _run_key(run_id):
    return f"staff.jobs.bulk.{run_id}"


def _start(target, *args):
    threading.Thread(target=target, args=args, daemon=True).start()


def _file_all(user, run, coverage, note):
    """File run's plan one job at a time, saving the progress after each;
    stop at the first refusal and report the rest as not filed."""
    try:
        for i, job in enumerate(run["plan"]):
            try:
                issue = _file_issue(user, job["book"], job["languages"], coverage[job["book"]], note, bulk=True)
            except GitHubError:
                run["not_filed"] = run["plan"][i:]
                run["error"] = (f"GitHub refused the job for {book_name(job['book'])}: "
                                f"{len(run['filed'])} filed, {len(run['plan']) - i} not.")
                break
            run["filed"].append({**job, "number": issue["number"], "url": issue["html_url"]})
            cache.set(_run_key(run["id"]), run, RUN_KEEP)
    except Exception as e:   # noqa: BLE001 -- the page must hear that filing stopped
        log.exception("Bulk filing %s stopped", run["id"])
        run["not_filed"] = run["plan"][len(run["filed"]):]
        run["error"] = f"Filing stopped: {e.__class__.__name__}. {len(run['filed'])} filed."
    finally:
        run["state"] = "stopped" if run["error"] else "done"
        run["finished_at"] = timezone.now().isoformat()
        cache.set(_run_key(run["id"]), run, RUN_KEEP)
        if threading.current_thread() is not threading.main_thread():
            connections.close_all()   # this thread's own database connection


@admin_view("jobs")
def bulk_run(request, run_id):
    run = cache.get(_run_key(run_id))
    if run is None:
        raise NotFound("That bulk filing isn't known here any more; the open jobs above show what was filed.")
    return Response(run)
