"""A reader's suggestions and questions about a verse.

POST /api/messages  {kind, verse, lang, level, text}   send one (signed in)
GET  /api/messages                                      your own, with replies

Editors answer them in the admin (staff/inbox.py).
"""
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from owb import languages, refs

from .models import ReaderMessage

PER_HOUR = 10
MAX_TEXT = 2000


def _verse(value):
    value = str(value or "")
    try:
        ref = refs.parse(value)
    except Exception:
        ref = None
    if ref is None or ref.book not in refs.BOOK_NAMES or f"{ref.book}.{ref.chapter}.{ref.verse}" != value:
        raise ValidationError({"verse": "Not a verse.", "code": "invalid_verse"})
    return value


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def messages(request):
    mine = ReaderMessage.objects.filter(user=request.user)
    if request.method == "GET":
        return Response([{"id": m.id, "kind": m.kind, "verse": m.verse, "text": m.text, "status": m.status,
                          "reply": m.reply, "replied_at": m.replied_at, "created_at": m.created_at}
                         for m in mine[:100]])
    data = request.data if isinstance(request.data, dict) else {}
    kind = data.get("kind")
    if kind not in ReaderMessage.Kind.values:
        raise ValidationError({"kind": "suggestion or question", "code": "invalid_kind"})
    lang = data.get("lang") if data.get("lang") in languages.CODES else "en"
    level = data.get("level") if data.get("level") in ("L", "B", "R") else ""
    text = str(data.get("text", "") or "").strip()
    if not text:
        raise ValidationError({"text": "Write your message.", "code": "empty"})
    if len(text) > MAX_TEXT:
        raise ValidationError({"text": f"Keep it under {MAX_TEXT} characters.", "code": "too_long"})
    verse = _verse(data.get("verse"))
    if mine.filter(created_at__gte=timezone.now() - timedelta(hours=1)).count() >= PER_HOUR:
        return Response({"detail": "You've sent a lot of messages this hour. Try again later.",
                         "code": "rate_limited"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    m = ReaderMessage.objects.create(user=request.user, kind=kind, verse=verse, language=lang,
                                     level=level, text=text)
    return Response({"id": m.id, "status": m.status}, status=status.HTTP_201_CREATED)
