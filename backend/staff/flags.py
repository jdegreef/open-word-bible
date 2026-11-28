"""Reviewer flags as a conversation that ends.

GET  /api/admin/review/flags/?closed=1
        open flags in every layer, newest first, each with its thread and
        where it stands (editors); closed=1 adds the flags closed in the
        last CLOSED_DAYS days
POST /api/admin/review/flags/<event id>/  {action, text}
        reply: an editor, or the reviewer who flagged it
        decline {text}: an editor settles it with the text as it is, for
            the reason given; the flag closes
        resolve {text}: an editor settles it another way; the flag closes

A flag is "open" until it is settled; "fix" once a fix request has been
filed from it (staff/fixes.py, flag=) and it waits on that; "declined" or
"resolved" once an editor closes it; "approved" once the layer is
approved again (which settles it as before). A closed flag no longer makes
the sentence flagged (translation ReviewState.sync), and the reviewer who
flagged it is emailed each reply and how it ended, and sees them in My
review. Nothing here approves anything.
"""
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from translation.models import ReviewEvent, ReviewState

from . import notify, people
from .inbox import verse_label
from .models import FlagReply, record
from .permissions import admin_view
from .review import _event_json, layer_json, settle_status

A = ReviewEvent.Action
RS = ReviewState.State
CLOSED_DAYS = 30


def outcome(flag, replies, current):
    """Where a flag stands: "open", "fix", "declined", "resolved" or
    "approved". current: the ReviewState row's event id for its layer."""
    if flag.closed_at:
        return flag.closed_as or "resolved"
    if current != flag.id:
        return "approved"
    return "fix" if any(r.kind == FlagReply.Kind.FIX for r in replies) else "open"


def reply_json(r):
    return {"id": r.id, "kind": r.kind, "label": r.get_kind_display(), "by": people.name(r.user) if r.user else "",
            "text": r.text, "fix_issue": r.fix_issue, "at": r.created_at}


def layer_of(flag):
    return flag.language or flag.sentence.source_edition.language


def flag_json(flag, current=None):
    replies = list(flag.replies.all())
    if current is None:
        current = (ReviewState.objects.filter(sentence_id=flag.sentence_id, layer=layer_of(flag))
                   .values_list("event_id", flat=True).first())
    vid = flag.sentence.refs[0]
    return {**_event_json(flag), "layer": layer_json(layer_of(flag)), "record": flag.sentence.record_id,
            "verse": vid, "label": verse_label(vid), "outcome": outcome(flag, replies, current),
            "closed_at": flag.closed_at, "thread": [reply_json(r) for r in replies]}


def listed(flags):
    flags = list(flags.select_related("user", "sentence__source_edition").prefetch_related("replies__user"))
    current = dict(((sid, layer), eid) for sid, layer, eid in ReviewState.objects.filter(
        sentence_id__in={f.sentence_id for f in flags}).values_list("sentence_id", "layer", "event_id"))
    return [flag_json(f, current.get((f.sentence_id, layer_of(f)))) for f in flags]


def open_flags():
    """The flags that make a sentence flagged now, newest first."""
    ids = ReviewState.objects.filter(state=RS.FLAGGED).values("event_id")
    return ReviewEvent.objects.filter(id__in=ids).order_by("-created_at", "-id")


def closed_recently(user=None):
    since = timezone.now() - timedelta(days=CLOSED_DAYS)
    flags = ReviewEvent.objects.filter(action=A.FLAGGED, closed_at__gte=since)
    if user is not None:
        flags = flags.filter(user=user)
    return flags.order_by("-closed_at", "-id")


@admin_view("inbox")
def flags(request):
    out = listed(open_flags())
    if request.query_params.get("closed"):
        out += listed(closed_recently())
    return Response({"flags": out})


@admin_view("overview", methods=("POST",))
def flag(request, event_id):
    f = (ReviewEvent.objects.filter(id=event_id, action=A.FLAGGED)
         .select_related("user", "sentence__source_edition").first())
    if f is None:
        raise NotFound("No such flag.")
    data = request.data if isinstance(request.data, dict) else {}
    action = data.get("action")
    text = str(data.get("text") or "").strip()
    if len(text) > 4000:
        raise ValidationError({"text": "Keep it under 4,000 characters.", "code": "too_long"})
    editor = "inbox" in request.admin_areas
    if action == "reply":
        if not (editor or f.user_id == request.user.id):
            return Response({"detail": "Editors, and the reviewer who flagged it, reply to a flag.",
                             "code": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
        if not text:
            raise ValidationError({"text": "Write the reply.", "code": "empty"})
        r = FlagReply.objects.create(flag=f, user=request.user, kind=FlagReply.Kind.REPLY, text=text)
    elif action in ("decline", "resolve"):
        if not editor:
            return Response({"detail": "Editors settle flags.", "code": "forbidden"},
                            status=status.HTTP_403_FORBIDDEN)
        if f.closed_at:
            raise ValidationError({"detail": "This flag is already settled.", "code": "closed"})
        if action == "decline" and not text:
            raise ValidationError({"text": "Say why the text stays as it is.", "code": "empty"})
        kind = FlagReply.Kind.DECLINED if action == "decline" else FlagReply.Kind.RESOLVED
        with transaction.atomic():
            r = FlagReply.objects.create(flag=f, user=request.user, kind=kind, text=text)
            ReviewEvent.objects.filter(pk=f.pk).update(closed_at=timezone.now(), closed_by=request.user,
                                                       closed_as=kind)
            f.refresh_from_db()
            ReviewState.sync(f.sentence_id, f.language, saved=f.pk)
            settle_status(layer_of(f), [f.sentence_id])
    else:
        raise ValidationError({"action": "Choose reply, decline or resolve.", "code": "invalid_action"})
    record(request.user, f"flag.{action}", f"{f.sentence.record_id} ({layer_json(layer_of(f))['name']})",
           flag=f.id)
    if f.user_id != request.user.id:
        tell(f, r)
    return Response({"flag": flag_json(f)}, status=status.HTTP_201_CREATED)


def tell(f, r):
    """Email the reviewer who flagged f what was said or done (r)."""
    name = layer_json(layer_of(f))["name"]
    what = {"reply": "replied to", "fix": "filed a fix request from", "declined": "declined",
            "resolved": "resolved"}[r.kind]
    by = people.name(r.user) if r.user else "An editor"
    body = f"{by} {what} your flag on {verse_label(f.sentence.refs[0])} ({name}).\n\n"
    if f.note:
        body += f"You wrote: {f.note}\n\n"
    if r.text:
        body += f"{by}: {r.text}\n\n"
    if r.fix_issue:
        body += f"The fix request is #{r.fix_issue}.\n\n"
    body += f"{notify.workspace_url(layer_of(f))}\n"
    notify._send(f.user.username, f"Your flag on {verse_label(f.sentence.refs[0])}: {r.get_kind_display().lower()}",
                 body)
