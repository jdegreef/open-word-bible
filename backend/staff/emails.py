"""Emailing the team: everyone with a role, or everyone with one kind of
role. Readers are not emailed from here: the privacy page promises an
account's address is used for signing in (and for replies to a reader's
own message), so a reader newsletter would need that page changed first.

GET  /api/admin/emails/                         sent emails, and the audiences
POST /api/admin/emails/  {subject, body, audience, test}
                                                send; test=true sends only to you
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.models import Role

from .models import Broadcast, record
from .permissions import admin_view

log = logging.getLogger(__name__)

K = Role.Kind
AUDIENCES = {"team": "Everyone on the team", K.SUPER_ADMIN: "Super admins", K.EDITOR: "Editors",
             K.SCHOLAR_REVIEWER: "Scholar reviewers", K.LANGUAGE_REVIEWER: "Language reviewers",
             K.REPORTING: "People with reporting access", K.USERS: "People with user-records access",
             K.EMAIL: "People with email access"}
FOOTER = ("\n\n--\nYou're getting this because you're on the Open Word Bible team ({role}). "
          "Reply to this email if you'd rather not get these.")


def recipients(audience):
    users = get_user_model().objects.filter(is_active=True, roles__isnull=False)
    if audience != "team":
        users = users.filter(roles__kind=audience)
    return sorted(set(users.values_list("username", flat=True)))


@admin_view("email", methods=("GET", "POST"))
def emails(request):
    if request.method == "POST":
        return _send(request)
    return Response({
        "audiences": [{"key": k, "label": label, "count": len(recipients(k))} for k, label in AUDIENCES.items()],
        "sent": [{"id": b.id, "subject": b.subject, "audience": AUDIENCES.get(b.audience, b.audience),
                  "recipients": b.recipients, "failed": b.failed, "sent_at": b.sent_at,
                  "sent_by": b.sent_by.username if b.sent_by else ""}
                 for b in Broadcast.objects.select_related("sent_by")[:50]],
    })


def _send(request):
    data = request.data if isinstance(request.data, dict) else {}
    subject = str(data.get("subject", "") or "").strip()
    body = str(data.get("body", "") or "").strip()
    audience = data.get("audience")
    if not subject or len(subject) > 200 or "\n" in subject:
        raise ValidationError({"subject": "Write a subject of one line, under 200 characters."})
    if not body or len(body) > 20000:
        raise ValidationError({"body": "Write the email (under 20,000 characters)."})
    if audience not in AUDIENCES:
        raise ValidationError({"audience": "Choose who gets it."})
    footer = FOOTER.format(role=AUDIENCES[audience].lower())
    if data.get("test"):
        to = [request.user.username]
    else:
        to = recipients(audience)
        if not to:
            raise ValidationError({"audience": "Nobody has that role yet."})
    failed = 0
    for address in to:   # one email each, so nobody sees the others' addresses
        try:
            send_mail(subject=("[Test] " if data.get("test") else "") + subject, message=body + footer,
                      from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[address])
        except Exception:
            log.exception("team email failed")
            failed += 1
    if data.get("test"):
        if failed:
            return Response({"detail": "The test email could not be sent.", "code": "email_unavailable"},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"test": True, "sent": 1})
    b = Broadcast.objects.create(subject=subject, body=body, audience=audience, recipients=len(to) - failed,
                                 failed=failed, sent_by=request.user)
    record(request.user, "email.send", subject, audience=audience, recipients=len(to) - failed, failed=failed)
    return Response({"id": b.id, "sent": len(to) - failed, "failed": failed}, status=status.HTTP_201_CREATED)
