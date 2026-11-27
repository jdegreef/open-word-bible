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
POST /api/admin/fixes/  {verse, record, language, levels: [level], links, reason}
                            file a word-links request: links is the record's
                            alignments for that language and level in
                            scripts/align.py's spec form, from the verse
                            inspector's word-links editor

For editors and super admins (the inbox area). Filing needs
OWB_GITHUB_TOKEN, as drafting jobs do.

POST /api/admin/fixes/meaning/  {record, decision, change, reason}
                            a meaning-change request against one meaning
                            decision (its key): for the sentence's meaning
                            reviewers (scholars of its original language) as
                            well as editors. The worker changes the decision
                            and every language's renderings it moves, in one
                            pull request (fix-worker, "Meaning changes").
"""
import json

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from feedback.models import ReaderMessage
from owb import languages
from translation.models import ReviewEvent, Sentence

from . import github, jobs, kept, people
from .inbox import verse_label, verse_url
from .models import FlagReply, record
from .permissions import admin_view
from .verses import content_file

LABEL = "fix-request"
LEVELS = {"L": "Literal", "B": "Balanced", "R": "Readable"}


def open_fixes():
    issues = github.call(f"issues?labels={LABEL}&state=open&per_page=100")
    out = []
    for i in issues:
        if "pull_request" in i:
            continue
        out.append({**jobs.marker(i, "fix-request"), "number": i["number"], "title": i["title"],
                    "url": i["html_url"], "created_at": i["created_at"],
                    "assignees": [a["login"] for a in i.get("assignees", [])]})
    return out


@admin_view("inbox", methods=("GET", "POST"), once=True)
def fixes(request):
    if request.method == "POST":
        return _file(request)
    answer = {"configured": bool(settings.OWB_GITHUB_TOKEN), "repo": settings.OWB_GITHUB_REPO}
    try:
        answer["fixes"] = kept.kept("staff.kept.fixes", open_fixes, 120)
    except github.GitHubError:
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
    links = _text(data, "links", 4000, required=False)
    if links:
        if len(levels) != 1:
            raise ValidationError({"levels": "Word links are for one level.", "code": "one_level"})
        if not links.startswith(sentence.record_id + ":"):
            raise ValidationError({"links": "Links must name this sentence.", "code": "invalid_links"})
        return _file_links(request, sentence, vid, lang, levels[0], links, _text(data, "reason", 4000, required=False))
    change = _text(data, "change", 2000)
    reason = _text(data, "reason", 4000, required=False)
    message = None
    if data.get("message"):
        if not str(data["message"]).isdigit():
            raise ValidationError({"message": "That isn't a reader message's number.", "code": "invalid"})
        message = ReaderMessage.objects.select_related("user").filter(id=int(data["message"])).first()
    # Filed from a reviewer's flag (staff/flags.py): the flag's thread says so.
    flag = None
    if data.get("flag"):
        if not str(data["flag"]).isdigit():
            raise ValidationError({"flag": "That isn't a flag's number.", "code": "invalid"})
        flag = (ReviewEvent.objects.filter(id=int(data["flag"]), action=ReviewEvent.Action.FLAGGED,
                                           sentence=sentence).select_related("user", "sentence").first())
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
        # Readers write to us privately and the repository is public: the
        # message stays in the admin, and the editor's reason says the point.
        lines += ["", f"Prompted by a reader's {message.get_kind_display().lower()} (admin inbox #{message.id})."]
    lines += ["", "Follow `.claude/skills/fix-worker/SKILL.md`: weigh the request against the source and "
              "the style brief, keep the record `ai_draft`, and open a pull request or say here why not.",
              "", f"Requested in the admin by {people.public_name(request.user)}.", "",
              "<!-- fix-request " + json.dumps({"record": sentence.record_id, "verse": vid, "language": lang,
                                               "levels": levels, "message": message.id if message else None})
              + " -->"]
    try:
        issue = github.call("issues", "POST", {"title": f"Fix {label} ({name}): {change[:60]}",
                                                "body": "\n".join(lines), "labels": [LABEL]})
    except github.GitHubError:
        return Response({"detail": "GitHub refused the request. Check OWB_GITHUB_TOKEN can create issues.",
                         "code": "github"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    record(request.user, "fix.request", f"#{issue['number']} {sentence.record_id}", verse=vid, language=lang,
           number=issue["number"], url=issue["html_url"])
    if flag:
        from . import flags   # flags imports review, which this module's importers need first
        r = FlagReply.objects.create(flag=flag, user=request.user, kind=FlagReply.Kind.FIX, fix_issue=issue["number"],
                                     text=change)
        if flag.user_id != request.user.id:
            flags.tell(flag, r)
    if message:
        note = f"Fix requested: #{issue['number']}"
        message.note = f"{message.note}\n{note}".strip() if message.note else note
        # Awaiting the fix, not an editor: out of the waiting count and the
        # three-day alert until sync_fixes settles it.
        if message.status == ReaderMessage.Status.NEW:
            message.status = ReaderMessage.Status.FIXING
        message.fix_issue = issue["number"]
        message.save(update_fields=["note", "status", "fix_issue"])
    return Response({"number": issue["number"], "url": issue["html_url"]}, status=status.HTTP_201_CREATED)


@admin_view("review", methods=("POST",), once=True)
def meaning(request):
    """A meaning-change request, from the meaning review page."""
    if not settings.OWB_GITHUB_TOKEN:
        return Response({"detail": "Set OWB_GITHUB_TOKEN on the API service to file requests from here.",
                         "code": "not_configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    from . import review   # review imports what imports this module
    data = request.data if isinstance(request.data, dict) else {}
    sentence = (Sentence.objects.filter(record_id=str(data.get("record", ""))).select_related("source_edition")
                .first())
    if sentence is None:
        raise ValidationError({"record": "Choose a sentence.", "code": "invalid_record"})
    layer = sentence.source_edition.language
    if "inbox" not in request.admin_areas and layer not in review.reviewing(request.user):
        return Response({"detail": f"Editors and the {review.layer_json(layer)['name']} reviewers ask for meaning "
                                   "changes.", "code": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
    decision = sentence.decisions.filter(layer="meaning", key=str(data.get("decision", ""))).first()
    if decision is None:
        raise ValidationError({"decision": "Choose one of the sentence's meaning decisions.", "code": "invalid"})
    change = _text(data, "change", 2000)
    reason = _text(data, "reason", 4000, required=False)
    vid = sentence.refs[0]
    label = verse_label(vid)
    path = content_file(sentence.book, sentence.chapter, sentence.verse)
    drafted = sorted(set(sentence.renderings.values_list("language", flat=True)))
    lines = [f"**Sentence:** `{sentence.record_id}` ({label})",
             f"**File:** `{path or 'not found'}`",
             f"**Meaning decision:** `{decision.key}` ({decision.category})", "",
             "**Now:**", "", f"- Choice: {decision.choice}",
             f"- Alternatives: {'; '.join(decision.alternatives) or '(none)'}",
             f"- Reason: {decision.reason}", "",
             "**Change requested:**", "", change]
    if reason:
        lines += ["", "**Why:**", "", reason]
    lines += ["", f"**Languages drafted:** {', '.join(drafted)}. Each one's renderings that the change moves "
              "change with it, in the same pull request.", "",
              "Follow `.claude/skills/fix-worker/SKILL.md` (Meaning changes): weigh it against the source, change "
              "the decision and the renderings it moves in every language, keep the record `ai_draft`, and open "
              "one pull request or say here why not.", "",
              f"Requested in the admin by {people.public_name(request.user)}.", "",
              "<!-- fix-request " + json.dumps({"record": sentence.record_id, "verse": vid, "kind": "meaning",
                                               "decision": decision.key, "languages": drafted, "message": None})
              + " -->"]
    try:
        issue = github.call("issues", "POST", {"title": f"Meaning change {label}: {change[:60]}",
                                                "body": "\n".join(lines), "labels": [LABEL]})
    except github.GitHubError:
        return Response({"detail": "GitHub refused the request. Check OWB_GITHUB_TOKEN can create issues.",
                         "code": "github"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    record(request.user, "fix.request", f"#{issue['number']} {sentence.record_id}", verse=vid, kind="meaning",
           decision=decision.key, number=issue["number"], url=issue["html_url"])
    return Response({"number": issue["number"], "url": issue["html_url"]}, status=status.HTTP_201_CREATED)


def _file_links(request, sentence, vid, lang, level, links, reason):
    """A word-links request: the reviewer's links for one language and level,
    for a Claude session to apply with scripts/align.py and validate."""
    label = verse_label(vid)
    path = content_file(sentence.book, sentence.chapter, sentence.verse)
    name = languages.READING[lang]["name"]
    lines = [f"**Sentence:** `{sentence.record_id}` ({label}), {name}, {LEVELS[level]}",
             f"**File:** `{path or 'not found'}`",
             f"**Read it:** {verse_url(vid, lang)}", "",
             f"**Word links requested** for {name} {LEVELS[level]}, replacing the ones there now "
             "(token numbers count the sentence's source words from 1):", "",
             "```", links, "```"]
    if reason:
        lines += ["", "**Why:**", "", reason]
    lines += ["", "Apply them with `python3 scripts/align.py apply <file> <spec> --lang "
              f"{lang} --level {level}` (the block above is the spec), check they link what the words "
              "say, run `owb.validate`, keep the record `ai_draft`, and open a pull request or say here why not. "
              "Follow `.claude/skills/fix-worker/SKILL.md`.",
              "", f"Requested in the admin by {people.public_name(request.user)}.", "",
              "<!-- fix-request " + json.dumps({"record": sentence.record_id, "verse": vid, "language": lang,
                                               "levels": [level], "kind": "links", "message": None}) + " -->"]
    try:
        issue = github.call("issues", "POST", {"title": f"Word links {label} ({name}, {LEVELS[level]})",
                                                "body": "\n".join(lines), "labels": [LABEL]})
    except github.GitHubError:
        return Response({"detail": "GitHub refused the request. Check OWB_GITHUB_TOKEN can create issues.",
                         "code": "github"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    record(request.user, "fix.request", f"#{issue['number']} {sentence.record_id}", verse=vid, language=lang,
           number=issue["number"], url=issue["html_url"], kind="links")
    return Response({"number": issue["number"], "url": issue["html_url"]}, status=status.HTTP_201_CREATED)
