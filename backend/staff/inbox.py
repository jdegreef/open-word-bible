"""Reader suggestions and questions, for editors.

GET   /api/admin/inbox/?status=new&kind=&lang=&book=&offset=
                                    messages, newest first, with counts by status
PATCH /api/admin/inbox/<id>/  {status, reply, note}
                                    answer (the reply is emailed to the reader),
                                    mark done or declined, or keep a note

A reply is sent once: a message that has been answered keeps its reply.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.auth import site_url
from feedback.models import ReaderMessage
from owb import refs

from .models import record
from .permissions import admin_view

log = logging.getLogger(__name__)
S = ReaderMessage.Status
PAGE = 50

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


def message_json(m):
    return {"id": m.id, "kind": m.kind, "verse": m.verse, "verse_label": verse_label(m.verse),
            "language": m.language, "level": m.level, "text": m.text, "status": m.status,
            "reply": m.reply, "replied_by": m.replied_by.username if m.replied_by else "",
            "replied_at": m.replied_at, "note": m.note, "created_at": m.created_at,
            "fixed_at": m.fixed_at, "fix_url": m.fix_url,
            "from": {"id": m.user_id, "name": m.user.first_name, "email": m.user.username},
            "url": verse_url(m.verse, m.language)}


@admin_view("inbox")
def inbox(request):
    params = request.query_params
    messages = ReaderMessage.objects.select_related("user", "replied_by")
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
    try:
        offset = max(int(params.get("offset", 0)), 0)
    except ValueError:
        offset = 0
    total = messages.count()
    return Response({"messages": [message_json(m) for m in messages[offset:offset + PAGE]],
                     "total": total, "offset": offset, "page": PAGE,
                     "counts": {s: counts.get(s, 0) for s in S.values}})


@admin_view("inbox", methods=("PATCH",))
def message(request, message_id):
    m = ReaderMessage.objects.select_related("user", "replied_by").filter(id=message_id).first()
    if m is None:
        return Response({"detail": "No such message.", "code": "not_found"}, status=status.HTTP_404_NOT_FOUND)
    data = request.data if isinstance(request.data, dict) else {}
    reply = str(data.get("reply", "") or "").strip()
    if "note" in data:
        m.note = str(data["note"] or "")[:4000]
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


def _send_reply(m, reply, editor):
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
