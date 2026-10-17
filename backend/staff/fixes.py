"""Fix requests: an editor asks for a sentence's wording to be changed, and
the admin files a GitHub issue labelled fix-request for a Claude session to
work (.claude/skills/fix-worker). The session weighs the request against the
Greek or Hebrew and the language's style brief, edits content/ or explains
why not, and opens a pull request; the sentence stays an AI draft. Nothing
here approves anything.

GET  /api/admin/fixes/      open fix requests on GitHub
POST /api/admin/fixes/  {verse, record, language, levels, change, reason, message}
                            file one; message (a reader message id) links the
                            request to what prompted it

For editors and super admins (the inbox area). Filing needs
OWB_GITHUB_TOKEN, as drafting jobs do.
"""
import json

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from feedback.models import ReaderMessage
from owb import languages
from translation.models import Sentence

from . import jobs
from .inbox import verse_label, verse_url
from .models import record
from .permissions import admin_view
from .verses import content_file

LABEL = "fix-request"
LEVELS = {"L": "Literal", "B": "Balanced", "R": "Readable"}


def open_fixes():
    issues = jobs._github(f"issues?labels={LABEL}&state=open&per_page=100")
    out = []
    for i in issues:
        if "pull_request" in i:
            continue
        data = {}
        for line in (i.get("body") or "").splitlines():
            if line.startswith("<!-- fix-request "):
                try:
                    data = json.loads(line[len("<!-- fix-request "):-len(" -->")])
                except ValueError:
                    pass
        out.append({"number": i["number"], "title": i["title"], "url": i["html_url"], "created_at": i["created_at"],
                    "assignees": [a["login"] for a in i.get("assignees", [])], **data})
    return out


@admin_view("inbox", methods=("GET", "POST"))
def fixes(request):
    if request.method == "POST":
        return _file(request)
    answer = {"configured": bool(settings.OWB_GITHUB_TOKEN), "repo": settings.OWB_GITHUB_REPO}
    try:
        answer["fixes"] = open_fixes()
    except jobs.GitHubError:
        answer["fixes"], answer["error"] = [], "GitHub could not be reached, so open fix requests aren't listed."
    return Response(answer)


def _text(data, name, limit, required=True):
    value = str(data.get(name, "") or "").strip()
    if required and not value:
        raise ValidationError({name: "This is needed.", "code": "empty"})
    if len(value) > limit:
        raise ValidationError({name: f"Keep it under {limit:,} characters.", "code": "too_long"})
    return value


def _file(request):
    if not settings.OWB_GITHUB_TOKEN:
        return Response({"detail": "Set OWB_GITHUB_TOKEN on the API service to file fix requests from here.",
                         "code": "not_configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    data = request.data if isinstance(request.data, dict) else {}
    sentence = Sentence.objects.filter(record_id=str(data.get("record", ""))).first()
    if sentence is None:
        raise ValidationError({"record": "Choose a sentence.", "code": "invalid_record"})
    vid = str(data.get("verse") or sentence.refs[0])
    if vid not in sentence.refs:
        vid = sentence.refs[0]
    lang = data.get("language")
    if lang not in languages.CODES:
        raise ValidationError({"language": "Choose a language.", "code": "invalid_language"})
    if not sentence.renderings.filter(language=lang).exists():
        raise ValidationError({"language": f"This sentence isn't drafted in "
                               f"{languages.READING[lang]['name']} yet.", "code": "not_drafted"})
    levels = [lv for lv in LEVELS if lv in (data.get("levels") or [])] or list(LEVELS)
    change = _text(data, "change", 2000)
    reason = _text(data, "reason", 4000, required=False)
    message = None
    if data.get("message"):
        message = ReaderMessage.objects.select_related("user").filter(id=data["message"]).first()
    label = verse_label(vid)
    path = content_file(sentence.book, sentence.chapter, sentence.verse)
    name = languages.READING[lang]["name"]
    current = {r.level: r.text for r in sentence.renderings.filter(language=lang)}
    lines = [f"**Sentence:** `{sentence.record_id}` ({label}), {name}, "
             f"{', '.join(LEVELS[lv] for lv in levels)}",
             f"**File:** `{path or 'not found'}`",
             f"**Read it:** {verse_url(vid, lang)}", "",
             "**Now:**", ""]
    lines += [f"- {LEVELS[lv]}: {current.get(lv, '(none)')}" for lv in levels]
    lines += ["", "**Change requested:**", "", change]
    if reason:
        lines += ["", "**Why:**", "", reason]
    if message:
        quoted = "\n".join("> " + line for line in message.text.splitlines())
        lines += ["", f"**Prompted by a reader's {message.get_kind_display().lower()}** "
                  f"(admin inbox #{message.id}):", "", quoted]
    lines += ["", "Follow `.claude/skills/fix-worker/SKILL.md`: weigh the request against the source and "
              "the style brief, keep the record `ai_draft`, and open a pull request or say here why not.",
              "", f"Requested in the admin by {request.user.username}.", "",
              "<!-- fix-request " + json.dumps({"record": sentence.record_id, "verse": vid, "language": lang,
                                               "levels": levels, "message": message.id if message else None})
              + " -->"]
    try:
        issue = jobs._github("issues", "POST", {"title": f"Fix {label} ({name}): {change[:60]}",
                                                "body": "\n".join(lines), "labels": [LABEL]})
    except jobs.GitHubError:
        return Response({"detail": "GitHub refused the request. Check OWB_GITHUB_TOKEN can create issues.",
                         "code": "github"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    record(request.user, "fix.request", f"#{issue['number']} {sentence.record_id}", verse=vid, language=lang,
           number=issue["number"], url=issue["html_url"])
    if message:
        note = f"Fix requested: #{issue['number']}"
        message.note = f"{message.note}\n{note}".strip() if message.note else note
        message.save(update_fields=["note"])
    return Response({"number": issue["number"], "url": issue["html_url"]}, status=status.HTTP_201_CREATED)
