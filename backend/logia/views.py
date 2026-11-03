"""Logia's endpoints: the sign-in hand-off, and saves and likes.

POST   /api/auth/handoff        {site, redirect}   from openwordbible.org, signed in:
                                                   a link back to the partner site
                                                   carrying a single-use code
POST   /api/auth/handoff/redeem {code}             from the partner site: the code
                                                   for an API token of its own
GET    /api/logia/me                               the reader's saved and liked keys
PUT    /api/logia/saved/<key>                      save a comment (idempotent)
DELETE /api/logia/saved/<key>                      unsave it
PUT    /api/logia/likes/<key>                      like a comment (idempotent)
DELETE /api/logia/likes/<key>                      unlike it
GET    /api/logia/likes?chapter=JHN.1              how many readers like each
                                                   comment in a chapter (public)

Signing in itself stays on Open Word Bible: a partner site may not call the
sign-in endpoints (accounts.views.foreign), and the hand-off is the only way
it gets a token. The code travels in the link's #fragment, which never reaches
a server, works once, and only for SITE_MINUTES.
"""
import re
from datetime import timedelta
from urllib.parse import quote, urlsplit

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts import auth
from accounts.models import hash_secret, new_secret
from accounts.views import FOREIGN, error, foreign

from .models import Handoff, Like, Saved

CODE_MINUTES = 5
HANDOFFS_PER_HOUR = 30        # per account: a cap on codes made and never used
MARKS_PER_KIND = 5000         # saves (or likes) one account may keep
KEY = re.compile(r"^([a-z][a-z0-9-]{0,39})\.([1-3]?[A-Z]{2,3})\.(\d{1,3})\.(\d{1,3})$")
CHAPTER = re.compile(r"^[1-3]?[A-Z]{2,3}\.\d{1,3}$")
EXPIRED = ("This sign-in has expired. Sign in again.", "handoff_expired", status.HTTP_400_BAD_REQUEST)


def origin_of(url):
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def partner_for(origin):
    """The partner site whose origin this is, or None."""
    for name, url in settings.PARTNER_SITES.items():
        if origin == origin_of(url):
            return name
    return None


def _field(request, name):
    return request.data.get(name, "") if isinstance(request.data, dict) else ""


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def handoff(request):
    """Asked by Open Word Bible's /handoff/ page once the reader has agreed."""
    if foreign(request):
        return error(*FOREIGN)
    site = str(_field(request, "site"))
    if site not in settings.PARTNER_SITES:
        return error("That site does not share Open Word Bible accounts.", "unknown_site", status.HTTP_400_BAD_REQUEST)
    hour_ago = timezone.now() - timedelta(hours=1)
    if Handoff.objects.filter(user=request.user, created_at__gte=hour_ago).count() >= HANDOFFS_PER_HOUR:
        return error("Too many attempts. Wait a few minutes and try again.", "rate_limited",
                     status.HTTP_429_TOO_MANY_REQUESTS)
    code, code_hash = new_secret()
    Handoff.objects.create(user=request.user, site=site, code_hash=code_hash)
    to = auth.safe_redirect(_field(request, "redirect")) or "/"
    url = f"{settings.PARTNER_SITES[site]}/signed-in/#code={code}&to={quote(to, safe='/')}"
    return Response({"url": url})


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
@transaction.atomic
def redeem(request):
    """Asked by the partner site's /signed-in/ page: a code for an API token."""
    origin = request.headers.get("Origin")
    code = str(_field(request, "code")).strip()
    oldest = timezone.now() - timedelta(minutes=CODE_MINUTES)
    found = (Handoff.objects.select_for_update().select_related("user")
             .filter(code_hash=hash_secret(code), used_at__isnull=True, created_at__gte=oldest).first()
             if code else None)
    if found is None:
        return error(*EXPIRED)
    # Only the site the code was made for may use it (a browser always says
    # where a cross-site request comes from).
    if origin and partner_for(origin) != found.site:
        return error(*FOREIGN)
    found.used_at = timezone.now()
    found.save(update_fields=["used_at"])
    if not found.user.is_active:
        return error(*EXPIRED)
    label = f"{found.site.title()} · {request.META.get('HTTP_USER_AGENT', '')}"
    user, key = auth.issue_token(found.user, label)
    return Response({"token": key, "user": auth.user_json(user)})


def _key(key):
    m = KEY.match(key or "")
    if not m:
        return None, None
    return key, f"{m[2]}.{int(m[3])}"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({
        "saved": [{"key": s.key, "at": s.created_at.isoformat()} for s in Saved.objects.filter(user=request.user)],
        "liked": list(Like.objects.filter(user=request.user).values_list("key", flat=True)),
    })


def _mark(model, request, key):
    key, chapter = _key(key)
    if key is None:
        return error("That is not a Logia comment.", "bad_key", status.HTTP_400_BAD_REQUEST)
    if request.method == "DELETE":
        model.objects.filter(user=request.user, key=key).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    if (not model.objects.filter(user=request.user, key=key).exists()
            and model.objects.filter(user=request.user).count() >= MARKS_PER_KIND):
        return error("You have saved as many as an account can keep.", "too_many", status.HTTP_400_BAD_REQUEST)
    mark, _ = model.objects.get_or_create(user=request.user, key=key, defaults={"chapter": chapter})
    return Response({"key": mark.key, "at": mark.created_at.isoformat()})


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def saved(request, key):
    return _mark(Saved, request, key)


@api_view(["GET"])
@authentication_classes([])
def like_counts(request):
    chapter = request.query_params.get("chapter", "")
    if not CHAPTER.match(chapter):
        return error("Give a chapter, like JHN.1.", "bad_chapter", status.HTTP_400_BAD_REQUEST)
    book, number = chapter.split(".")
    rows = Like.objects.filter(chapter=f"{book}.{int(number)}").values("key").annotate(n=Count("id"))
    response = Response({"counts": {r["key"]: r["n"] for r in rows}})
    response["Cache-Control"] = "public, max-age=60"
    return response


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def liked(request, key):
    return _mark(Like, request, key)
