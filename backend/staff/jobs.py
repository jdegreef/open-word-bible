"""Drafting jobs: a super admin asks for a book to be drafted in some
languages, and the admin files a GitHub issue labelled drafting-job for a
Claude session to pick up (.claude/skills/drafting-worker).

GET  /api/admin/jobs/                         open drafting jobs on GitHub
POST /api/admin/jobs/  {book, languages, note} file one

Filing needs OWB_GITHUB_TOKEN (a token that may create issues in
OWB_GITHUB_REPO); without it the page says so. Before filing, the request
is checked against the database (a language that already has the whole
book is refused) and against the open jobs (the same book and language
asked for twice is refused), as the check-book-before-translating skill
does for a session.
"""
import json
import logging
import urllib.error
import urllib.request

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from owb import languages, refs

from .models import record
from .permissions import admin_view
from .progress import CHAPTERS, _coverage, book_name

log = logging.getLogger(__name__)
LABEL = "drafting-job"


class GitHubError(Exception):
    pass


def _github(path, method="GET", body=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "open-word-bible-admin",
               "X-GitHub-Api-Version": "2022-11-28"}
    if settings.OWB_GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.OWB_GITHUB_TOKEN}"
    data = json.dumps(body).encode() if body is not None else None
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"https://api.github.com/repos/{settings.OWB_GITHUB_REPO}/{path}",
                                 data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r)
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        log.warning("GitHub %s %s failed: %s", method, path, e)
        raise GitHubError from e


def _parse_job(issue):
    """The book and languages a drafting-job issue asks for, from the
    machine-readable line the admin writes into its body."""
    for line in (issue.get("body") or "").splitlines():
        if line.startswith("<!-- drafting-job "):
            try:
                return json.loads(line[len("<!-- drafting-job "):-len(" -->")])
            except ValueError:
                return {}
    return {}


def open_jobs():
    issues = _github(f"issues?labels={LABEL}&state=open&per_page=100")
    return [{"number": i["number"], "title": i["title"], "url": i["html_url"], "created_at": i["created_at"],
             "assignees": [a["login"] for a in i.get("assignees", [])], **_parse_job(i)}
            for i in issues if "pull_request" not in i]


@admin_view("jobs", methods=("GET", "POST"))
def jobs(request):
    if request.method == "POST":
        return _file(request)
    books = [{"code": c, "name": book_name(c), "chapters": CHAPTERS[c]} for c in refs.BOOK_CODES]
    langs = [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items()]
    answer = {"configured": bool(settings.OWB_GITHUB_TOKEN), "repo": settings.OWB_GITHUB_REPO,
              "books": books, "languages": langs,
              "coverage": {b["code"]: {lang: s["state"] for lang, s in b["languages"].items()}
                           for b in _coverage()}}
    try:
        answer["jobs"] = open_jobs()
    except GitHubError:
        answer["jobs"], answer["error"] = [], "GitHub could not be reached, so open jobs aren't listed."
    return Response(answer)


def _file(request):
    if not settings.OWB_GITHUB_TOKEN:
        return Response({"detail": "Set OWB_GITHUB_TOKEN on the API service to file jobs from here.",
                         "code": "not_configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    data = request.data if isinstance(request.data, dict) else {}
    book = str(data.get("book", "")).upper()
    if book not in CHAPTERS:
        raise ValidationError({"book": "Choose a book.", "code": "invalid_book"})
    wanted = [c for c in languages.CODES if c in (data.get("languages") or [])]
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
    lines += ["", f"Filed from the admin by {request.user.username}.", "",
              "<!-- drafting-job " + json.dumps({"book": book, "languages": wanted}) + " -->"]
    try:
        issue = _github("issues", "POST", {"title": f"Draft {book_name(book)} in {names}",
                                           "body": "\n".join(lines), "labels": [LABEL]})
    except GitHubError:
        return Response({"detail": "GitHub refused the job. Check OWB_GITHUB_TOKEN can create issues.",
                         "code": "github"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    record(request.user, "job.file", f"#{issue['number']} {book}", languages=wanted)
    return Response({"number": issue["number"], "url": issue["html_url"]}, status=status.HTTP_201_CREATED)
