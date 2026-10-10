"""Account endpoints.

POST   /api/auth/link       {email}         email a sign-in link (always 202)
POST   /api/auth/verify     {token}         trade a link for an API token
POST   /api/auth/sign-out                   forget this device's token
GET    /api/me                              the signed-in account
PATCH  /api/me              {display_name}  change the display name

The two sign-in endpoints take JSON only, which a browser cannot send from
another site without a CORS preflight, and ignore any Authorization header,
so a stale token never gets in the way of signing in again.
"""
import ipaddress

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes, parser_classes,
                                       permission_classes)
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import auth

# Django's User.username, where the address is kept.
MAX_EMAIL = 150


def client_ip(request):
    """The client's address. Render appends it to X-Forwarded-For, so the
    last entry is the one Render saw; earlier entries are whatever the
    client sent."""
    candidates = [p.strip() for p in request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")]
    for value in (candidates[-1], request.META.get("REMOTE_ADDR", "")):
        try:
            return str(ipaddress.ip_address(value))
        except ValueError:
            continue
    return None


def normalise_email(value):
    """A valid address, lower-cased with its domain in ASCII (IDNA), so one
    mailbox is always one account. Raises ValidationError."""
    email = str(value or "").strip()
    try:
        local, domain = email.rsplit("@", 1)
        email = f"{local}@{domain.encode('idna').decode('ascii')}".lower()
        validate_email(email)
    except (ValueError, UnicodeError, DjangoValidationError):
        raise ValidationError({"email": "Enter a valid email address."})
    if len(email) > MAX_EMAIL:
        raise ValidationError({"email": f"Use an address under {MAX_EMAIL} characters."})
    return email


def _field(request, name):
    return request.data.get(name, "") if isinstance(request.data, dict) else ""


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def request_link(request):
    origin = request.headers.get("Origin")
    if origin and origin not in settings.CORS_ALLOWED_ORIGINS:
        return Response({"detail": "Sign in on Open Word Bible."}, status=status.HTTP_403_FORBIDDEN)
    email = normalise_email(_field(request, "email"))
    try:
        auth.request_link(email, ip=client_ip(request))
    except auth.RateLimited:
        return Response({"detail": "Too many sign-in links. Try again in an hour."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)
    except auth.EmailUnavailable:
        return Response({"detail": "Sign-in email is not working right now. Please try again later."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"sent": True}, status=status.HTTP_202_ACCEPTED)


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def verify(request):
    secret = str(_field(request, "token")).strip()
    result = auth.redeem_link(secret, label=request.META.get("HTTP_USER_AGENT", "")) if secret else None
    if result is None:
        return Response({"detail": "This sign-in link has expired or was already used. "
                                   "Ask for a new one."}, status=status.HTTP_400_BAD_REQUEST)
    user, key = result
    return Response({"token": key, "user": auth.user_json(user)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sign_out(request):
    request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def me(request):
    user = request.user
    if request.method == "PATCH":
        name = str(_field(request, "display_name")).strip()
        if len(name) > 80:
            raise ValidationError({"display_name": "Keep it under 80 characters."})
        user.first_name = name
        user.save(update_fields=["first_name"])
    return Response(auth.user_json(user))
