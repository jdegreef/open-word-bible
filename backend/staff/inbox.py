"""Reader suggestions and questions, for editors.

GET   /api/admin/inbox/?status=new&kind=&lang=&book=&assigned=&offset=
                                    messages with counts by status, the
                                    editors they can be assigned to and the
                                    saved replies; new messages oldest
                                    waiting first, the rest newest first.
                                    assigned is me, none or a user id
PATCH /api/admin/inbox/<id>/  {status, reply, note, assigned_to}
                                    answer (the reply is emailed to the reader),
                                    mark done or declined, keep a note, or
                                    assign it ("me", an editor's id or email,
                                    or null for nobody)

A reply is sent once: a message that has been answered keeps its reply.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts import controls
from accounts.auth import site_url
from feedback.models import ReaderMessage
from owb import refs

from .models import record
from .permissions import AREAS, admin_view

log = logging.getLogger(__name__)
S = ReaderMessage.Status
PAGE = 50
WAITING_DAYS = 3   # a new message older than this needs attention

REPLY = ("Re: your {kind} about {verse}",
         "You wrote to Open Word Bible about {verse}:\n\n{quoted}\n\n"
         "{name} replied:\n\n{reply}\n\n"
         "Read the passage: {url}\n\n"
         "This is a reply to the message you sent from the site; we won't email you otherwise.")


def verse_label(verse):
    try:
        ref = refs.parse(verse)
    except Exception:
        return verse
    return f"{refs.BOOK_NAMES.get(ref.book, ref.book)} {ref.chapter}:{ref.verse}"


def verse_url(verse, lang):
    try:
        ref = refs.parse(verse)
    except Exception:
        return site_url("/", lang)
    return site_url(f"/{ref.book.lower()}/{ref.chapter}/", lang, fragment=f"v{ref.verse}")


# Saved replies an editor can start from: {name} is the reader's name,
# {verse} the verse and {url} its page.
SAVED_REPLIES = [
    ("thanks", "Thanks", "Hello {name},\n\nThank you for writing about {verse}. We read every message, "
     "and yours goes to the editors working on this passage."),
    ("considering", "Under consideration", "Hello {name},\n\nThank you for your suggestion. We're "
     "looking at {verse} again with it in mind, and if it leads to a change we'll let you know."),
    ("fixed", "Fixed", "Hello {name},\n\nThank you for writing. Your message led us to change the "
     "wording of {verse}, and the change is now on the site: {url}"),
    ("declined", "Declined, with reason", "Hello {name},\n\nThank you for writing about {verse}. "
     "We've kept the wording as it is, because "),
    ("answered", "Question answered", "Hello {name},\n\nThank you for your question about {verse}. "),
]


def saved_replies(m):
    values = {"name": m.user.first_name or "there", "verse": verse_label(m.verse),
              "url": verse_url(m.verse, m.language)}
    return [{"key": key, "label": label, "text": text.format(**values)} for key, label, text in SAVED_REPLIES]


def inbox_team():
    """The accounts that may be assigned a message: those with the inbox
    area."""
    return (get_user_model().objects.filter(roles__kind__in=AREAS["inbox"]).distinct()
            .order_by("username"))


def person(user):
    return {"id": user.id, "email": user.username, "name": user.first_name} if user else None


def message_json(m):
    age = timezone.now() - m.created_at
    return {"id": m.id, "kind": m.kind, "verse": m.verse, "verse_label": verse_label(m.verse),
            "language": m.language, "level": m.level, "text": m.text, "status": m.status,
            "reply": m.reply, "replied_by": m.replied_by.username if m.replied_by else "",
            "replied_at": m.replied_at, "note": m.note, "created_at": m.created_at,
            "fixed_at": m.fixed_at, "fix_url": m.fix_url,
            "from": {"id": m.user_id, "name": m.user.first_name, "email": m.user.username},
            "url": verse_url(m.verse, m.language),
            "assigned_to": person(m.assigned_to), "assigned_at": m.assigned_at,
            "age_days": age.days,
            "waiting": m.status == S.NEW and age > timedelta(days=WAITING_DAYS),
            "replies": [] if m.reply else saved_replies(m)}


@admin_view("inbox")
def inbox(request):
    params = request.query_params
    messages = ReaderMessage.objects.select_related("user", "replied_by", "assigned_to")
    counts = dict(messages.values("status").annotate(n=Count("id")).values_list("status", "n"))
    state = params.get("status", "new")
    if state in S.values:
        messages = messages.filter(status=state)
    if params.get("kind") in ReaderMessage.Kind.values:
        messages = messages.filter(kind=params["kind"])
    if params.get("lang"):
        messages = messages.filter(language=params["lang"])
    if params.get("book"):
        messages = messages.filter(verse__startswith=params["book"].upper() + ".")
    assigned = params.get("assigned", "")
    if assigned == "me":
        messages = messages.filter(assigned_to=request.user)
    elif assigned == "none":
        messages = messages.filter(assigned_to__isnull=True)
    elif assigned.isdigit():
        messages = messages.filter(assigned_to_id=int(assigned))
    if state == S.NEW:
        messages = messages.order_by("created_at")
    try:
        offset = max(int(params.get("offset", 0)), 0)
    except ValueError:
        offset = 0
    total = messages.count()
    return Response({"messages": [message_json(m) for m in messages[offset:offset + PAGE]],
                     "total": total, "offset": offset, "page": PAGE,
                     "counts": {s: counts.get(s, 0) for s in S.values},
                     "team": [person(u) for u in inbox_team()]})


@admin_view("inbox", methods=("PATCH",))
def message(request, message_id):
    m = ReaderMessage.objects.select_related("user", "replied_by", "assigned_to").filter(id=message_id).first()
    if m is None:
        return Response({"detail": "No such message.", "code": "not_found"}, status=status.HTTP_404_NOT_FOUND)
    data = request.data if isinstance(request.data, dict) else {}
    reply = str(data.get("reply", "") or "").strip()
    if "note" in data:
        m.note = str(data["note"] or "")[:4000]
    if "assigned_to" in data:
        _assign(m, data["assigned_to"], request.user)
    if reply:
        if m.reply:
            raise ValidationError({"reply": "This message has already been answered.", "code": "answered"})
        if len(reply) > 4000:
            raise ValidationError({"reply": "Keep the reply under 4,000 characters."})
        if not _send_reply(m, reply, request.user):
            return Response({"detail": "The reply could not be emailed; it was not saved.",
                             "code": "email_unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        m.reply, m.replied_by, m.replied_at, m.status = reply, request.user, timezone.now(), S.ANSWERED
        record(request.user, "message.reply", f"{m.get_kind_display()} on {m.verse}", message=m.id)
    new_status = data.get("status")
    if new_status:
        if new_status not in S.values or (new_status == S.ANSWERED and not m.reply):
            raise ValidationError({"status": "Choose new, done or declined (answering takes a reply)."})
        if new_status != m.status:
            record(request.user, f"message.{new_status}", f"{m.get_kind_display()} on {m.verse}", message=m.id)
        m.status = new_status
    m.save()
    return Response(message_json(m))


def _assign(m, who, editor):
    """Assign m to who: "me", an editor's id or email, or nobody (null or
    ""). Only accounts with the inbox area may be assigned."""
    if who in (None, ""):
        user = None
    else:
        team = inbox_team()
        if who == "me":
            user = team.filter(id=editor.id).first()
        elif isinstance(who, int) or str(who).isdigit():
            user = team.filter(id=int(who)).first()
        else:
            user = team.filter(username__iexact=str(who).strip()).first()
        if user is None:
            raise ValidationError({"assigned_to": "Assign it to someone who can open the reader inbox."})
    if user == m.assigned_to:
        return
    m.assigned_to, m.assigned_at = user, timezone.now() if user else None
    record(editor, "message.assign" if user else "message.unassign", f"{m.get_kind_display()} on {m.verse}",
           message=m.id, to=user.username if user else "")


def _send_reply(m, reply, editor):
    """Email the reply; True if it went, or if the reader turned these
    emails off (they read it on their account page)."""
    if not controls.wants(m.user, "replies"):
        return True
    subject, body = REPLY
    label = verse_label(m.verse)
    quoted = "\n".join("> " + line for line in m.text.splitlines())
    try:
        send_mail(subject=subject.format(kind=m.get_kind_display().lower(), verse=label),
                  message=body.format(verse=label, quoted=quoted, reply=reply,
                                      name=editor.first_name or "An Open Word Bible editor",
                                      url=verse_url(m.verse, m.language)),
                  from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[m.user.username])
    except Exception:
        log.exception("reply email failed")
        return False
    return True
