"""Signing in: email links, API tokens, and roles.

A browser asks for a link (request_link), the email carries
<site>/account/#token=<secret>, and the account page trades the secret for an
API token (redeem_link). The token goes in an Authorization: Bearer header.
"""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import authentication, exceptions

from .models import ApiToken, Role, SignInLink, hash_secret, new_secret

LINKS_PER_EMAIL_PER_HOUR = 5
LINKS_PER_IP_PER_HOUR = 20


class RateLimited(Exception):
    pass


def request_link(email, ip=None):
    """Email a single-use sign-in link to email. Raises RateLimited when an
    address or a network has asked for too many links in the last hour."""
    email = email.strip().lower()
    hour_ago = timezone.now() - timedelta(hours=1)
    recent = SignInLink.objects.filter(created_at__gte=hour_ago)
    if recent.filter(email=email).count() >= LINKS_PER_EMAIL_PER_HOUR:
        raise RateLimited
    if ip and recent.filter(requested_ip=ip).count() >= LINKS_PER_IP_PER_HOUR:
        raise RateLimited
    secret, token_hash = new_secret()
    SignInLink.objects.create(email=email, token_hash=token_hash, requested_ip=ip)
    url = f"{settings.OWB_SITE_URL}/account/#token={secret}"
    minutes = settings.SIGN_IN_LINK_MINUTES
    send_mail(
        subject="Sign in to Open Word Bible",
        message=(f"Open this link to sign in to Open Word Bible:\n\n{url}\n\n"
                 f"It works once, for {minutes} minutes. If you did not ask to sign in, "
                 f"you can ignore this email."),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )


@transaction.atomic
def redeem_link(secret, label=""):
    """Trade a sign-in link's secret for (user, api_token_secret), creating
    the account the first time. Returns None for an unknown, used or
    expired link."""
    oldest = timezone.now() - timedelta(minutes=settings.SIGN_IN_LINK_MINUTES)
    link = (SignInLink.objects.select_for_update()
            .filter(token_hash=hash_secret(secret), used_at__isnull=True, created_at__gte=oldest)
            .first())
    if link is None:
        return None
    link.used_at = timezone.now()
    link.save(update_fields=["used_at"])
    User = get_user_model()
    user, _ = User.objects.get_or_create(username=link.email, defaults={"email": link.email})
    if not user.is_active:
        return None
    user.last_login = link.used_at
    user.save(update_fields=["last_login"])
    sync_super_admin(user)
    key, key_hash = new_secret()
    ApiToken.objects.create(user=user, key_hash=key_hash, label=label[:200])
    return user, key


def sync_super_admin(user):
    """Accounts listed in OWB_SUPER_ADMIN_EMAILS are super admins, with the
    Django admin open to them. The list lives in the environment, not the
    repository, so the address is not published."""
    if user.email.lower() not in settings.OWB_SUPER_ADMIN_EMAILS:
        return
    Role.objects.get_or_create(user=user, kind=Role.Kind.SUPER_ADMIN, language="")
    if not (user.is_staff and user.is_superuser):
        user.is_staff = user.is_superuser = True
        user.save(update_fields=["is_staff", "is_superuser"])


def user_json(user):
    roles = list(user.roles.all())
    return {
        "email": user.email,
        "display_name": user.first_name,
        "roles": [r.as_json() for r in roles],
        "is_super_admin": any(r.kind == Role.Kind.SUPER_ADMIN for r in roles),
        "joined": user.date_joined.date().isoformat(),
    }


class TokenAuthentication(authentication.BaseAuthentication):
    """Authorization: Bearer <api token>. A missing header is anonymous; a
    wrong or revoked token is a 401, so the browser knows to sign in again."""

    def authenticate(self, request):
        parts = authentication.get_authorization_header(request).split()
        if not parts or parts[0].lower() != b"bearer":
            return None
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("Malformed Authorization header.")
        token = (ApiToken.objects.select_related("user")
                 .filter(key_hash=hash_secret(parts[1].decode("utf-8", "replace"))).first())
        if token is None or not token.user.is_active:
            raise exceptions.AuthenticationFailed("Signed out. Sign in again.")
        now = timezone.now()
        if token.last_used_at is None or now - token.last_used_at > timedelta(hours=1):
            token.last_used_at = now
            token.save(update_fields=["last_used_at"])
        return token.user, token

    def authenticate_header(self, request):
        return "Bearer"
