"""The account page's controls: signed-in devices, the email address, and
which emails the reader wants.

GET    /api/me/devices                 the account's signed-in devices
DELETE /api/me/devices/<id>            sign one out
POST   /api/me/devices/sign-out-others sign out every device but this one
POST   /api/me/email   {email, lang}   email the new address a link that
                                       moves the account to it (202)
POST   /api/me/email/confirm {token}   use that link: the account's address
                                       becomes the new one, and the old
                                       address is told
GET    /api/me/prefs                   which emails the reader wants
PATCH  /api/me/prefs   {replies, plan_reminders, reminder_hour, timezone, language}
GET    /api/email/unsubscribe?t=       a page with a button that turns
POST   /api/email/unsubscribe?t=       reminders off (one-click, RFC 8058)

A device is an API token (accounts/models.py ApiToken); its label is the
browser it signed in from, shown as "Firefox on Windows".
"""
import html
import logging
from datetime import timedelta
from zoneinfo import ZoneInfo, available_timezones

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, parser_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from owb import languages

from . import auth
from .models import EmailPrefs, SignInLink, hash_secret, new_secret

log = logging.getLogger(__name__)
Purpose = SignInLink.Purpose
UNSUBSCRIBE_SALT = "owb.unsubscribe"


# Browsers and systems, in the order they are looked for: Edge and Opera
# also say Chrome, and Chrome also says Safari.
BROWSERS = (("Edg/", "Edge"), ("OPR/", "Opera"), ("Firefox/", "Firefox"), ("FxiOS", "Firefox"),
            ("CriOS", "Chrome"), ("Chrome/", "Chrome"), ("Safari/", "Safari"))
SYSTEMS = (("iPhone", "iPhone"), ("iPad", "iPad"), ("Android", "Android"), ("Windows", "Windows"),
           ("Mac OS X", "macOS"), ("CrOS", "ChromeOS"), ("Linux", "Linux"))


def describe_agent(agent):
    """"Firefox on Windows" from a User-Agent header; "" if it says neither."""
    browser = next((name for key, name in BROWSERS if key in agent), "")
    system = next((name for key, name in SYSTEMS if key in agent), "")
    if browser and system:
        return f"{browser} on {system}"
    return browser or system


def _error(detail, code, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"detail": detail, "code": code}, status=http_status)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def devices(request):
    return Response([{"id": t.id, "label": describe_agent(t.label), "created_at": t.created_at,
                      "last_used_at": t.last_used_at or t.created_at, "current": t.id == request.auth.id}
                     for t in request.user.api_tokens.all()])


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def device(request, token_id):
    deleted, _ = request.user.api_tokens.filter(id=token_id).delete()
    if not deleted:
        return _error("No such device.", "not_found", status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sign_out_others(request):
    count, _ = request.user.api_tokens.exclude(id=request.auth.id).delete()
    return Response({"signed_out": count})


CHANGE_EMAIL = ("Confirm your new Open Word Bible email address",
                "Open this link to make this address the one you sign in to Open Word Bible with:\n\n{url}\n\n"
                "It works once, for {minutes} minutes. Until then your account keeps its old address. "
                "If you did not ask for this, you can ignore this email.")
EMAIL_CHANGED = ("Your Open Word Bible email address was changed",
                 "The Open Word Bible account that used this address now signs in with {new}.\n\n"
                 "If you did not do this, reply to this email and we will help you get your account back.")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def change_email(request):
    """Email a link to the new address; the account moves only when it is
    used, so nobody can take an address they cannot read. Whether the new
    address already has an account is told only to whoever uses the link."""
    from .views import normalise_email, client_ip
    data = request.data if isinstance(request.data, dict) else {}
    new = normalise_email(data.get("email"))
    if new == request.user.username:
        return _error("That is already your address.", "same_email")
    if settings.EMAIL_BACKEND.endswith("console.EmailBackend") and not settings.DEBUG:
        return _error(*auth_unavailable())
    try:
        auth._check_rate(request.user.username, client_ip(request))
    except auth.RateLimited:
        return _error("Too many attempts. Wait a few minutes and try again.", "rate_limited",
                      status.HTTP_429_TOO_MANY_REQUESTS)
    secret, token_hash = new_secret()
    link = SignInLink.objects.create(email=request.user.username, new_email=new, token_hash=token_hash,
                                     purpose=Purpose.CHANGE_EMAIL, requested_ip=client_ip(request))
    lang = str(data.get("lang", "")) if str(data.get("lang", "")) in languages.CODES else "en"
    subject, body = CHANGE_EMAIL
    try:
        send_mail(subject=subject,
                  message=body.format(url=auth.site_url("/account/", lang, fragment=f"email={secret}"),
                                      minutes=settings.SIGN_IN_LINK_MINUTES),
                  from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[new])
    except Exception:
        log.exception("change-of-address email failed")
        link.delete()
        return _error(*auth_unavailable())
    return Response({"sent": True}, status=status.HTTP_202_ACCEPTED)


def auth_unavailable():
    return ("Email is not working right now. Please try again later.", "email_unavailable",
            status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def confirm_email(request):
    """Use a change-of-address link. It needs no sign-in: the link proves
    the new address, and it was asked for from inside the account."""
    data = request.data if isinstance(request.data, dict) else {}
    secret = str(data.get("token", "")).strip()
    oldest = timezone.now() - timedelta(minutes=settings.SIGN_IN_LINK_MINUTES)
    User = get_user_model()
    with transaction.atomic():
        link = (SignInLink.objects.select_for_update()
                .filter(token_hash=hash_secret(secret), used_at__isnull=True, created_at__gte=oldest,
                        purpose=Purpose.CHANGE_EMAIL).first()) if secret else None
        if link is None:
            return _error("This link has expired or was already used. Ask for a new one.", "link_expired")
        link.used_at = timezone.now()
        link.save(update_fields=["used_at"])
        user = User.objects.filter(username=link.email, is_active=True).first()
        if user is None:
            return _error("This link has expired or was already used. Ask for a new one.", "link_expired")
        if User.objects.filter(username=link.new_email).exists():
            return _error("That address already has an Open Word Bible account.", "email_taken",
                          status.HTTP_409_CONFLICT)
        old = user.username
        user.username = user.email = link.new_email
        try:
            with transaction.atomic():
                user.save(update_fields=["username", "email"])
        except IntegrityError:
            return _error("That address already has an Open Word Bible account.", "email_taken",
                          status.HTTP_409_CONFLICT)
        # Links asked for with the old address no longer sign in to anything.
        SignInLink.objects.filter(email=old, used_at__isnull=True).update(used_at=timezone.now())
    subject, body = EMAIL_CHANGED
    try:
        send_mail(subject=subject, message=body.format(new=link.new_email),
                  from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[old])
    except Exception:
        log.exception("address-changed notice failed")
    return Response(auth.user_json(user))


ZONES = available_timezones()


def prefs_json(p):
    return {"replies": p.replies, "plan_reminders": p.plan_reminders, "reminder_hour": p.reminder_hour,
            "timezone": p.timezone, "language": p.language}


def prefs_for(user):
    """The reader's choices, saved or the defaults (unsaved)."""
    return EmailPrefs.objects.filter(user=user).first() or EmailPrefs(user=user)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def prefs(request):
    p = prefs_for(request.user)
    if request.method == "PATCH":
        data = request.data if isinstance(request.data, dict) else {}
        for name in ("replies", "plan_reminders"):
            if name in data:
                if not isinstance(data[name], bool):
                    raise ValidationError({name: "Send true or false."})
                setattr(p, name, data[name])
        if "reminder_hour" in data:
            hour = data["reminder_hour"]
            if not isinstance(hour, int) or isinstance(hour, bool) or not 0 <= hour <= 23:
                raise ValidationError({"reminder_hour": "An hour from 0 to 23."})
            p.reminder_hour = hour
        if "timezone" in data:
            if data["timezone"] not in ZONES:
                raise ValidationError({"timezone": "Not a time zone."})
            if data["timezone"] != p.timezone:
                p.last_reminder = None
            p.timezone = data["timezone"]
        if "language" in data:
            if data["language"] not in languages.CODES:
                raise ValidationError({"language": "Not one of the site's languages."})
            p.language = data["language"]
        p.save()
    return Response(prefs_json(p))


def unsubscribe_token(user):
    return signing.dumps({"u": user.pk}, salt=UNSUBSCRIBE_SALT, compress=True)


def unsubscribe_url(user):
    return f"{settings.OWB_API_URL}/api/email/unsubscribe?t={unsubscribe_token(user)}"


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Reading-plan emails · Open Word Bible</title>
<style>body{{font:17px/1.5 system-ui,sans-serif;max-width:34em;margin:4em auto;padding:0 1em;
color:#221c15;background:#faf6ef}}
button{{font:inherit;padding:.5em 1.2em;border-radius:999px;border:0;background:#3f3d9a;color:#fff;
cursor:pointer}}</style>
</head><body><h1>Reading-plan emails</h1>{body}
<p><a href="{site}/account/#email">Your email choices</a></p></body></html>"""


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([])
@parser_classes([FormParser, JSONParser])
def unsubscribe(request):
    """GET shows a button (so a mail scanner opening the link changes
    nothing); POST, from that button or a mail app's one-click
    unsubscribe, turns the reminders off."""
    token = request.GET.get("t", "")
    try:
        user_id = signing.loads(token, salt=UNSUBSCRIBE_SALT)["u"]
    except (signing.BadSignature, KeyError, TypeError):
        user_id = None
    user = get_user_model().objects.filter(pk=user_id).first() if user_id else None
    site = html.escape(settings.OWB_SITE_URL)
    if user is None:
        body = "<p>This link doesn’t work any more. You can choose which emails you get on your account page.</p>"
        return HttpResponse(PAGE.format(body=body, site=site), status=400)
    if request.method == "POST":
        EmailPrefs.objects.update_or_create(user=user, defaults={"plan_reminders": False})
        body = "<p>Done: you won’t get reading-plan emails any more.</p>"
    else:
        body = (f'<p>Stop the daily emails with your reading plan’s next chapters?</p>'
                f'<form method="post" action="?t={html.escape(token)}">'
                f'<button type="submit">Stop these emails</button></form>')
    return HttpResponse(PAGE.format(body=body, site=site))


def wants(user, kind):
    """Whether the reader wants this kind of email ("replies")."""
    p = EmailPrefs.objects.filter(user=user).first()
    return getattr(p, kind) if p else getattr(EmailPrefs(), kind)


def local_now(p, now=None):
    try:
        zone = ZoneInfo(p.timezone)
    except Exception:
        zone = ZoneInfo("UTC")
    return (now or timezone.now()).astimezone(zone)

