"""Articles: which translations are missing or behind their English, and
translation jobs for them.

GET  /api/admin/articles/                  every English article and its state
                                           in each language (current, out of
                                           date, not stamped, missing)
POST /api/admin/articles/  {language, slugs, note}
                                           file a GitHub issue labelled
                                           article-job for a Claude session
                                           (.claude/skills/article-worker)

The states come from scripts/check_translations.py, the same report
scripts/check.sh prints, read from the articles/ the API was deployed with.
Seeing them is for the team (overview); filing a job is for super admins
(jobs), as drafting jobs are.
"""
import importlib.util
import json

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from owb import languages

from . import jobs
from .models import record
from .permissions import admin_view

LABEL = "article-job"

_spec = importlib.util.spec_from_file_location("check_translations",
                                               settings.REPO_ROOT / "scripts" / "check_translations.py")
check_translations = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_translations)


def _articles(root=None):
    root = root or settings.REPO_ROOT / "articles"
    english = []
    for path in sorted(root.glob("*.md")):
        meta, body = check_translations.split(path.read_text(encoding="utf-8"))
        title = meta.get("title", path.stem)
        # A value with quotes in it is written as JSON, as build_site.py reads it.
        title = json.loads(title) if title.startswith('"') else title
        english.append({"slug": path.stem, "title": title,
                        "date": meta.get("date", ""), "section": meta.get("section", ""),
                        "words": len(body.split())})
    report = check_translations.report(root)
    for a in english:
        a["languages"] = {}
        for lang, r in report.items():
            slug = a["slug"]
            a["languages"][lang] = ("missing" if slug in r["missing"] else "out_of_date" if slug in r["out_of_date"]
                                    else "not_stamped" if slug in r["not_stamped"] else "current")
    totals = {lang: {key: len(r[key]) for key in ("missing", "out_of_date", "not_stamped", "orphaned")}
              for lang, r in report.items()}
    return english, totals


def open_article_jobs():
    issues = jobs._github(f"issues?labels={LABEL}&state=open&per_page=100")
    out = []
    for i in issues:
        if "pull_request" in i:
            continue
        data = {}
        for line in (i.get("body") or "").splitlines():
            if line.startswith("<!-- article-job "):
                try:
                    data = json.loads(line[len("<!-- article-job "):-len(" -->")])
                except ValueError:
                    pass
        out.append({"number": i["number"], "title": i["title"], "url": i["html_url"],
                    "created_at": i["created_at"], **data})
    return out


@admin_view("overview", methods=("GET", "POST"))
def articles(request):
    if request.method == "POST":
        if "jobs" not in request.admin_areas:
            return Response({"detail": "Only a super admin files article jobs.", "code": "forbidden"},
                            status=status.HTTP_403_FORBIDDEN)
        return _file(request)
    english, totals = _articles()
    answer = {"articles": english, "totals": totals, "can_file": "jobs" in request.admin_areas,
              "configured": bool(settings.OWB_GITHUB_TOKEN),
              "languages": [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items() if c != "en"]}
    if answer["can_file"]:
        try:
            answer["jobs"] = open_article_jobs()
        except jobs.GitHubError:
            answer["jobs"], answer["error"] = [], "GitHub could not be reached, so open article jobs aren't listed."
    return Response(answer)


def _file(request):
    if not settings.OWB_GITHUB_TOKEN:
        return Response({"detail": "Set OWB_GITHUB_TOKEN on the API service to file jobs from here.",
                         "code": "not_configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    data = request.data if isinstance(request.data, dict) else {}
    lang = data.get("language")
    if lang not in languages.CODES or lang == "en":
        raise ValidationError({"language": "Choose a language other than English.", "code": "invalid_language"})
    english, _ = _articles()
    states = {a["slug"]: a["languages"][lang] for a in english}
    titles = {a["slug"]: a["title"] for a in english}
    slugs = [s for s in dict.fromkeys(data.get("slugs") or []) if s in states and states[s] != "current"]
    if not slugs:
        raise ValidationError({"slugs": "Choose articles that are missing or out of date in that language.",
                               "code": "nothing_to_do"})
    try:
        taken = {s for j in open_article_jobs() if j.get("language") == lang for s in j.get("slugs", [])}
    except jobs.GitHubError:
        return Response({"detail": "GitHub could not be reached. Try again in a minute.", "code": "github"},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    clash = sorted(set(slugs) & taken)
    if clash:
        raise ValidationError({"slugs": f"Already in an open job: {', '.join(clash)}.", "code": "duplicate"})
    name = languages.READING[lang]["name"]
    note = str(data.get("note", "") or "").strip()[:2000]
    verbs = {"missing": "translate", "out_of_date": "bring up to date with the English",
             "not_stamped": "check against the English and stamp"}
    lines = [f"Articles for **{name}** (`articles/{lang}/`):", ""]
    lines += [f"- `{s}` ({titles[s]}): {verbs[states[s]]}" for s in slugs]
    lines += ["", "Follow `.claude/skills/article-worker/SKILL.md`, and stamp each translation with "
              "`python3 scripts/check_translations.py --stamp articles/<lang>/<slug>.md`."]
    if note:
        lines += ["", "**Note from the admin:**", "", note]
    lines += ["", f"Filed from the admin by {request.user.username}.", "",
              "<!-- article-job " + json.dumps({"language": lang, "slugs": slugs}) + " -->"]
    title = f"Articles in {name}: {len(slugs)} to translate or update" if len(slugs) > 1 else \
        f"Article in {name}: {titles[slugs[0]]}"
    try:
        issue = jobs._github("issues", "POST", {"title": title, "body": "\n".join(lines), "labels": [LABEL]})
    except jobs.GitHubError:
        return Response({"detail": "GitHub refused the job. Check OWB_GITHUB_TOKEN can create issues.",
                         "code": "github"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    record(request.user, "article.job", f"#{issue['number']} {lang}", language=lang, slugs=slugs)
    return Response({"number": issue["number"], "url": issue["html_url"]}, status=status.HTTP_201_CREATED)
