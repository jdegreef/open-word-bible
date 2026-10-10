"""Signing in: email links, API tokens, and roles.

A browser asks for a link (request_link), the email carries
<site>/account/#token=<secret>, and the account page trades the secret for an
API token (redeem_link) when the reader presses "Finish signing in", so an
email scanner that opens the link does not use it up. The token goes in an
Authorization: Bearer header.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import authentication

from .models import ApiToken, Role, SignInLink, hash_secret, new_secret

log = logging.getLogger(__name__)

LINKS_PER_EMAIL_PER_HOUR = 5
LINKS_PER_IP_PER_HOUR = 20
LINKS_PER_HOUR = 300          # every address together: a cap on what the site can be made to send
TOKEN_IDLE_DAYS = 180         # a device unused this long is signed out


class RateLimited(Exception):
    pass


class EmailUnavailable(Exception):
    pass


def request_link(email, ip=None):
    """Email a single-use sign-in link. email must already be validated and
    normalised (views.normalise_email). Raises RateLimited when the address,
    the network or the site has sent too many links in the last hour, and
    EmailUnavailable when email is not set up or the mail server fails."""
    if settings.EMAIL_BACKEND.endswith("console.EmailBackend") and not settings.DEBUG:
        # Without SMTP the link would be printed to the log, where anyone who
        # can read the log could sign in as anyone.
        raise EmailUnavailable
    hour_ago = timezone.now() - timedelta(hours=1)
    recent = SignInLink.objects.filter(created_at__gte=hour_ago)
    if (recent.filter(email=email).count() >= LINKS_PER_EMAIL_PER_HOUR
            or (ip and recent.filter(requested_ip=ip).count() >= LINKS_PER_IP_PER_HOUR)
            or recent.count() >= LINKS_PER_HOUR):
        raise RateLimited
    secret, token_hash = new_secret()
    link = SignInLink.objects.create(email=email, token_hash=token_hash, requested_ip=ip)
    url = f"{settings.OWB_SITE_URL}/account/#token={secret}"
    minutes = settings.SIGN_IN_LINK_MINUTES
    try:
        send_mail(
            subject="Sign in to Open Word Bible",
            message=(f"Open this link to sign in to Open Word Bible:\n\n{url}\n\n"
                     f"It works once, for {minutes} minutes. If you did not ask to sign in, "
                     f"you can ignore this email."),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
    except Exception:
        log.exception("sign-in email to a %s address failed", email.rsplit("@", 1)[-1])
        link.delete()
        raise EmailUnavailable


@transaction.atomic
def redeem_link(secret, label=""):
    """Trade a sign-in link's secret for (user, api_token_secret), creating
    the account the first time. Returns None for an unknown, used or
    expired link. Redeeming one link retires that address's other links."""
    now = timezone.now()
    oldest = now - timedelta(minutes=settings.SIGN_IN_LINK_MINUTES)
    link = (SignInLink.objects.select_for_update()
            .filter(token_hash=hash_secret(secret), used_at__isnull=True, created_at__gte=oldest)
            .first())
    if link is None:
        return None
    SignInLink.objects.filter(email=link.email, used_at__isnull=True).update(used_at=now)
    User = get_user_model()
    user, _ = User.objects.get_or_create(username=link.email, defaults={"email": link.email})
    if not user.is_active:
        return None
    user.last_login = now
    user.save(update_fields=["last_login"])
    sync_super_admin(user)
    key, key_hash = new_secret()
    ApiToken.objects.create(user=user, key_hash=key_hash, label=label[:200])
    return user, key


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
    roles = list(user.roles.all())
    return {
        "email": user.username,
        "display_name": user.first_name,
        "roles": [r.as_json() for r in roles],
        "is_super_admin": any(r.kind == Role.Kind.SUPER_ADMIN for r in roles),
        "joined": user.date_joined.date().isoformat(),
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
