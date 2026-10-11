"""Account endpoints.

GET    /api/auth/methods                    which ways in are switched on
POST   /api/auth/sign-in    {email, password}         an API token
POST   /api/auth/sign-up    {email, password, lang, redirect}
                                            email a link that confirms the
                                            address and sets the password (202)
POST   /api/auth/link       {email, lang, redirect}   email a sign-in link (202)
POST   /api/auth/verify     {token}         trade a link for an API token
POST   /api/auth/reset      {email, lang}   email a reset link (202, account or not)
POST   /api/auth/reset/confirm {token, password}      new password, and an API token
GET    /api/auth/google/start, /callback    Google (accounts/google.py)
POST   /api/auth/sign-out                   forget this device's token
GET    /api/me                              the signed-in account
PATCH  /api/me              {display_name}  change the display name
DELETE /api/me                              delete the account

The sign-in endpoints take JSON only, which a browser cannot send from
another site without a CORS preflight, and ignore any Authorization header,
so a stale token never gets in the way of signing in again.

Errors are {"detail": "...", "code": "..."}: the site shows its own message
for the code, in the page's language, and the English detail otherwise.
"""
import ipaddress

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.decorators import (api_view, authentication_classes, parser_classes,
                                       permission_classes)
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import auth, google

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
        raise ValidationError({"email": "Enter a valid email address.", "code": "invalid_email"})
    if len(email) > MAX_EMAIL:
        raise ValidationError({"email": f"Use an address under {MAX_EMAIL} characters.",
                               "code": "invalid_email"})
    return email


def checked_password(value, email):
    """The password if it passes Django's validators (AUTH_PASSWORD_VALIDATORS),
    else ValidationError with the first reason."""
    password = str(value or "")
    try:
        validate_password(password, get_user_model()(username=email, email=email))
    except DjangoValidationError as e:
        raise ValidationError({"password": e.messages[0], "code": "weak_password"})
    return password


def error(detail, code, http_status):
    return Response({"detail": detail, "code": code}, status=http_status)


def foreign(request):
    """A request from a page that is not Open Word Bible's."""
    origin = request.headers.get("Origin")
    return bool(origin and origin not in settings.CORS_ALLOWED_ORIGINS)


FOREIGN = ("Sign in on Open Word Bible.", "forbidden", status.HTTP_403_FORBIDDEN)
LIMITED = ("Too many attempts. Wait a few minutes and try again.", "rate_limited",
           status.HTTP_429_TOO_MANY_REQUESTS)
NO_EMAIL = ("Sign-in email is not working right now. Please try again later.", "email_unavailable",
            status.HTTP_503_SERVICE_UNAVAILABLE)
EXPIRED = ("This link has expired or was already used. Ask for a new one.", "link_expired",
           status.HTTP_400_BAD_REQUEST)


def _field(request, name):
    return request.data.get(name, "") if isinstance(request.data, dict) else ""


def signed_in(result):
    user, key = result
    return Response({"token": key, "user": auth.user_json(user)})


def _label(request):
    return request.META.get("HTTP_USER_AGENT", "")


@api_view(["GET"])
@authentication_classes([])
def methods(request):
    return Response({"password": True, "link": True, "google": google.enabled()})


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def sign_in(request):
    if foreign(request):
        return error(*FOREIGN)
    email = normalise_email(_field(request, "email"))
    try:
        result = auth.sign_in_with_password(email, str(_field(request, "password")),
                                            ip=client_ip(request), label=_label(request))
    except auth.RateLimited:
        return error(*LIMITED)
    if result is None:
        return error("That email and password don't match.", "invalid_credentials",
                     status.HTTP_400_BAD_REQUEST)
    return signed_in(result)


def _send(request, purpose, password=None):
    if foreign(request):
        return error(*FOREIGN)
    email = normalise_email(_field(request, "email"))
    if purpose == auth.Purpose.SIGN_UP:
        password = checked_password(_field(request, "password"), email)
    try:
        auth.send_link(email, purpose, ip=client_ip(request), lang=str(_field(request, "lang")),
                       redirect=str(_field(request, "redirect")), password=password)
    except auth.RateLimited:
        return error(*LIMITED)
    except auth.EmailUnavailable:
        return error(*NO_EMAIL)
    return Response({"sent": True}, status=status.HTTP_202_ACCEPTED)


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def sign_up(request):
    return _send(request, auth.Purpose.SIGN_UP)


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def request_link(request):
    return _send(request, auth.Purpose.SIGN_IN)


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def request_reset(request):
    return _send(request, auth.Purpose.RESET)


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def verify(request):
    secret = str(_field(request, "token")).strip()
    result = auth.redeem_link(secret, label=_label(request)) if secret else None
    return signed_in(result) if result else error(*EXPIRED)


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def confirm_reset(request):
    secret = str(_field(request, "token")).strip()
    if not secret:
        return error(*EXPIRED)
    password = checked_password(_field(request, "password"), "")
    result = auth.reset_password(secret, password, label=_label(request))
    return signed_in(result) if result else error(*EXPIRED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sign_out(request):
    request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def me(request):
    user = request.user
    if request.method == "DELETE":
        if not auth.delete_account(user):
            return error("Accounts with review history are kept with the record. "
                         "Ask an editor to close yours.", "has_reviews", status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
    if request.method == "PATCH":
        name = str(_field(request, "display_name")).strip()
        if len(name) > 80:
            raise ValidationError({"display_name": "Keep it under 80 characters."})
        user.first_name = name
        user.save(update_fields=["first_name"])
    return Response(auth.user_json(user))
