"""Signing in: passwords, email links, Google, API tokens and roles.

Three ways in, all ending in an API token (one per device) that goes in an
Authorization: Bearer header:

- a password (sign_in_with_password). Choosing one is confirmed by email:
  sign_up emails a link carrying the hashed password, and the password
  applies only when that link is used, so nobody can set the password of an
  address they do not own, and asking reveals nothing about who has an
  account;
- a single-use link emailed to the address (send_link); redeeming one creates
  the account the first time. Email links land on <site>/login/#token=<secret>,
  and the page trades the secret for a token (redeem_link) only when the
  reader presses "Finish signing in", so an email scanner that opens the link
  does not use it up. Reset links land on /reset-password/ instead, where the
  new password goes with the secret (reset_password);
- Google (accounts/google.py), which hands the browser back to the site with
  a link of its own.
"""
import logging
from datetime import timedelta
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import authentication

from owb import languages

from .models import ApiToken, FailedSignIn, Role, SignInLink, hash_secret, new_secret

log = logging.getLogger(__name__)

LINKS_PER_EMAIL_PER_HOUR = 5
LINKS_PER_IP_PER_HOUR = 20
LINKS_PER_HOUR = 300          # every address together: a cap on what the site can be made to send
FAILURES_PER_EMAIL = 10       # wrong passwords in FAILURE_WINDOW before an address is paused
FAILURES_PER_IP = 30
FAILURE_WINDOW = timedelta(minutes=15)
TOKEN_IDLE_DAYS = 180         # a device unused this long is signed out
LANGUAGES = languages.CODES  # the site's languages (data/languages.json)
Purpose = SignInLink.Purpose


def has_password(user):
    """Accounts made before passwords, or by a link, have none: a blank
    password field, which Django would call usable, or an unusable one."""
    return bool(user.password) and user.has_usable_password()


class RateLimited(Exception):
    pass


class EmailUnavailable(Exception):
    pass


def safe_redirect(path):
    """A path on the site to return to after signing in, or "". Only rooted
    paths on the same site: never //host, /\\host or control characters."""
    path = str(path or "")
    if (not path.startswith("/") or path.startswith("//") or path.startswith("/\\")
            or any(ord(c) < 32 or c == "\x7f" for c in path) or len(path) > 300):
        return ""
    return path


def site_url(page, lang="en", redirect="", fragment=""):
    """A page on the site in lang ("/login/"), with ?redirect= and #fragment."""
    prefix = "" if lang == "en" else f"/{lang}"
    query = f"?redirect={quote(redirect, safe='/')}" if redirect else ""
    return f"{settings.OWB_SITE_URL}{prefix}{page}{query}{'#' + fragment if fragment else ''}"


def link_url(purpose, secret, lang="en", redirect=""):
    page = "/reset-password/" if purpose == Purpose.RESET else "/login/"
    key = "google" if purpose == Purpose.GOOGLE else "token"
    return site_url(page, lang, redirect, f"{key}={secret}")


EMAILS = {
    Purpose.SIGN_IN: ("Sign in to Open Word Bible",
                      "Open this link to sign in to Open Word Bible:\n\n{url}\n\n"
                      "It works once, for {minutes} minutes. If you did not ask to sign in, "
                      "you can ignore this email."),
    Purpose.SIGN_UP: ("Confirm your Open Word Bible account",
                      "Open this link to confirm your email and finish creating your "
                      "Open Word Bible account:\n\n{url}\n\n"
                      "It works once, for {minutes} minutes. If you already have an account, "
                      "using it sets the password you just chose. If you did not ask for this, "
                      "you can ignore this email."),
    Purpose.RESET: ("Reset your Open Word Bible password",
                    "Open this link to choose a new password for Open Word Bible:\n\n{url}\n\n"
                    "It works once, for {minutes} minutes. If you did not ask to reset your "
                    "password, you can ignore this email; your password has not changed."),
}


# A reset asked for an address with no account.
NO_ACCOUNT = ("Open Word Bible password reset",
              "Someone asked to reset the Open Word Bible password for this address, but there is "
              "no account for it. To create one, go to {url}\n\n"
              "If you did not ask, you can ignore this email.")


def _check_rate(email, ip):
    hour_ago = timezone.now() - timedelta(hours=1)
    recent = SignInLink.objects.filter(created_at__gte=hour_ago)
    if (recent.filter(email=email).count() >= LINKS_PER_EMAIL_PER_HOUR
            or (ip and recent.filter(requested_ip=ip).count() >= LINKS_PER_IP_PER_HOUR)
            or recent.count() >= LINKS_PER_HOUR):
        raise RateLimited


def send_link(email, purpose=Purpose.SIGN_IN, ip=None, lang="en", redirect="", password=None):
    """Email a single-use link. email must already be validated and
    normalised (views.normalise_email); password (sign-up) must already be
    validated. A reset link goes only to an existing account; an address
    with no account is emailed to say so, so the call looks and takes the
    same either way. Raises RateLimited when the address, the network or
    the site has sent too many links in the last hour, and EmailUnavailable
    when email is not set up or the mail server fails."""
    if settings.EMAIL_BACKEND.endswith("console.EmailBackend") and not settings.DEBUG:
        # Without SMTP the link would be printed to the log, where anyone who
        # can read the log could sign in as anyone.
        raise EmailUnavailable
    _check_rate(email, ip)
    secret, token_hash = new_secret()
    link = SignInLink.objects.create(
        email=email, token_hash=token_hash, requested_ip=ip, purpose=purpose,
        password_hash=make_password(password) if password else "")
    lang = lang if lang in LANGUAGES else "en"
    subject, body = EMAILS[purpose]
    url = link_url(purpose, secret, lang, safe_redirect(redirect))
    if purpose == Purpose.RESET and not get_user_model().objects.filter(username=email, is_active=True).exists():
        # Still an email, so the answer takes as long either way.
        subject, body = NO_ACCOUNT
        url = site_url("/login/", lang) + "?mode=signup"
    try:
        send_mail(
            subject=subject,
            message=body.format(url=url, minutes=settings.SIGN_IN_LINK_MINUTES),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
    except Exception:
        log.exception("sign-in email to a %s address failed", email.rsplit("@", 1)[-1])
        link.delete()
        raise EmailUnavailable


def google_link(email):
    """A link for an address Google has vouched for; the browser is sent
    straight to it (accounts/google.py), so it is never emailed."""
    secret, token_hash = new_secret()
    SignInLink.objects.create(email=email, token_hash=token_hash, purpose=Purpose.GOOGLE)
    return secret


def _take_link(secret, purposes):
    """The unused, unexpired link for secret, locked and marked used along
    with that address's other links; or None."""
    now = timezone.now()
    oldest = now - timedelta(minutes=settings.SIGN_IN_LINK_MINUTES)
    link = (SignInLink.objects.select_for_update()
            .filter(token_hash=hash_secret(secret), used_at__isnull=True, created_at__gte=oldest,
                    purpose__in=purposes)
            .first())
    if link is not None:
        SignInLink.objects.filter(email=link.email, used_at__isnull=True).update(used_at=now)
    return link


def issue_token(user, label):
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])
    sync_super_admin(user)
    key, key_hash = new_secret()
    ApiToken.objects.create(user=user, key_hash=key_hash, label=label[:200])
    return user, key


@transaction.atomic
def redeem_link(secret, label=""):
    """Trade a sign-in, sign-up or Google link's secret for (user,
    api_token_secret), creating the account the first time; a sign-up link
    also sets the password chosen with it. Returns None for an unknown, used
    or expired link. Redeeming one link retires that address's other links."""
    link = _take_link(secret, [Purpose.SIGN_IN, Purpose.SIGN_UP, Purpose.GOOGLE])
    if link is None:
        return None
    User = get_user_model()
    user, created = User.objects.get_or_create(username=link.email, defaults={"email": link.email})
    if not user.is_active:
        return None
    if link.password_hash:
        user.password = link.password_hash
        user.save(update_fields=["password"])
    elif created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    return issue_token(user, label)


@transaction.atomic
def reset_password(secret, password, label=""):
    """Set a new password with a reset link's secret, sign out every other
    device, and sign this one in. Returns (user, api_token_secret), or None
    for a bad link; raises django ValidationError, leaving the link unused,
    for a password the validators refuse."""
    link = _take_link(secret, [Purpose.RESET])
    if link is None:
        return None
    user = get_user_model().objects.filter(username=link.email, is_active=True).first()
    if user is None:
        return None
    validate_password(password, user)   # raises, undoing the transaction and keeping the link
    user.set_password(password)
    user.save(update_fields=["password"])
    user.api_tokens.all().delete()
    return issue_token(user, label)


# Compared against when there is no such account, so a wrong address takes
# as long to answer as a wrong password.
_DUMMY_PASSWORD = make_password("not a real password")


def sign_in_with_password(email, password, ip=None, label=""):
    """(user, api_token_secret) for the right password, or None. Raises
    RateLimited after too many wrong passwords for the address or network."""
    since = timezone.now() - FAILURE_WINDOW
    failures = FailedSignIn.objects.filter(created_at__gte=since)
    if (failures.filter(email=email).count() >= FAILURES_PER_EMAIL
            or (ip and failures.filter(ip=ip).count() >= FAILURES_PER_IP)):
        raise RateLimited
    user = get_user_model().objects.filter(username=email).first()
    if user is None or not has_password(user):
        check_password(password, _DUMMY_PASSWORD)
        ok = False
    else:
        ok = user.check_password(password) and user.is_active
    if not ok:
        FailedSignIn.objects.create(email=email, ip=ip)
        FailedSignIn.objects.filter(created_at__lt=timezone.now() - timedelta(hours=1)).delete()
        return None
    return issue_token(user, label)


def delete_account(user):
    """Delete the account, its roles and devices. Returns False, deleting
    nothing, when it has review history, which the record keeps."""
    from translation.models import ReviewEvent
    if ReviewEvent.objects.filter(user=user).exists():
        return False
    SignInLink.objects.filter(email=user.username).delete()
    FailedSignIn.objects.filter(email=user.username).delete()
    user.delete()
    return True


def sync_super_admin(user):
    """Accounts whose sign-in address is in OWB_SUPER_ADMIN_EMAILS are made
    super admins at every sign-in. The list lives in the environment, not
    the repository, so the address is not published. It bootstraps the first
    super admin; to revoke one, remove the address there and the role here.

    The username (the address that received the link) decides, never the
    editable email field. A super admin uses the Django admin after setting
    a password with `manage.py changepassword <email>`."""
    if user.username.lower() not in settings.OWB_SUPER_ADMIN_EMAILS:
        return
    Role.objects.get_or_create(user=user, kind=Role.Kind.SUPER_ADMIN, language="")
    if not (user.is_staff and user.is_superuser):
        user.is_staff = user.is_superuser = True
        user.save(update_fields=["is_staff", "is_superuser"])


def user_json(user):
    from staff.permissions import areas
    roles = list(user.roles.all())
    return {
        "email": user.username,
        "display_name": user.first_name,
        "roles": [r.as_json() for r in roles],
        "is_super_admin": any(r.kind == Role.Kind.SUPER_ADMIN for r in roles),
        # The parts of the admin (staff/permissions.py) the roles open.
        "admin": areas(user),
        "joined": user.date_joined.date().isoformat(),
        "has_password": has_password(user),
    }


class TokenAuthentication(authentication.BaseAuthentication):
    """Authorization: Bearer <api token>. A missing, wrong, revoked or idle
    token is anonymous, so public reading never fails over a stale token;
    endpoints that need an account answer 401, which tells the site to sign
    in again."""

    def authenticate(self, request):
        parts = authentication.get_authorization_header(request).split()
        if len(parts) != 2 or parts[0].lower() != b"bearer":
            return None
        token = (ApiToken.objects.select_related("user")
                 .filter(key_hash=hash_secret(parts[1].decode("utf-8", "replace"))).first())
        if token is None or not token.user.is_active:
            return None
        now = timezone.now()
        if now - (token.last_used_at or token.created_at) > timedelta(days=TOKEN_IDLE_DAYS):
            token.delete()
            return None
        if token.last_used_at is None or now - token.last_used_at > timedelta(hours=1):
            token.last_used_at = now
            token.save(update_fields=["last_used_at"])
        return token.user, token

    def authenticate_header(self, request):
        return "Bearer"
