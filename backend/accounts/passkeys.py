"""Passkeys: signing in with the device's own lock (WebAuthn), without a
password or an email.

POST   /api/me/passkeys/options        options for adding a passkey (signed in)
POST   /api/me/passkeys  {credential}  keep the passkey the browser made
GET    /api/me/passkeys                the account's passkeys
DELETE /api/me/passkeys/<id>           remove one
POST   /api/auth/passkey/options       options for signing in with one
POST   /api/auth/passkey {credential}  sign in: an API token, as other ways in give

A passkey belongs to the site's host (settings.PASSKEY_RP_ID), though the
API that checks it is on another; the browser says which page used it, and
only the site's own origins (settings.PASSKEY_ORIGINS) are accepted. Only a
passkey's public key is kept. Each ceremony's challenge is stored, used
once, and good for PASSKEY_MINUTES; signing in asks for a discoverable
passkey, so the reader need not type their address.
"""
import json
import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from webauthn import (base64url_to_bytes, generate_authentication_options, generate_registration_options,
                      options_to_json, verify_authentication_response, verify_registration_response)
from webauthn.helpers import bytes_to_base64url
from webauthn.helpers.exceptions import InvalidAuthenticationResponse, InvalidRegistrationResponse
from webauthn.helpers.structs import (AuthenticatorSelectionCriteria, PublicKeyCredentialDescriptor,
                                      ResidentKeyRequirement, UserVerificationRequirement)

from . import auth
from .controls import describe_agent
from .models import Passkey, PasskeyChallenge

log = logging.getLogger(__name__)

PASSKEY_MINUTES = 5
MAX_PASSKEYS = 20


def _error(detail, code, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"detail": detail, "code": code}, status=http_status)


FAILED = ("That passkey didn't work. Try again, or sign in another way.", "passkey_failed")


def _clear_stale():
    PasskeyChallenge.objects.filter(created_at__lt=timezone.now() - timedelta(minutes=PASSKEY_MINUTES)).delete()


def _take_challenge(credential, user=None):
    """The stored challenge the browser signed (from its clientDataJSON),
    used up; None if it is unknown, stale, or for another account."""
    try:
        client = json.loads(base64url_to_bytes(credential["response"]["clientDataJSON"]))
        challenge = str(client["challenge"])
    except (KeyError, TypeError, ValueError):
        return None
    oldest = timezone.now() - timedelta(minutes=PASSKEY_MINUTES)
    with transaction.atomic():
        row = (PasskeyChallenge.objects.select_for_update()
               .filter(challenge=challenge, created_at__gte=oldest, user=user).first())
        if row is None:
            return None
        row.delete()
    return base64url_to_bytes(challenge)


def _options(options, user=None):
    PasskeyChallenge.objects.create(challenge=bytes_to_base64url(options.challenge), user=user)
    return Response(json.loads(options_to_json(options)))


def _credential(request):
    data = request.data if isinstance(request.data, dict) else {}
    credential = data.get("credential")
    return credential if isinstance(credential, dict) else None


def passkey_json(p):
    return {"id": p.id, "label": describe_agent(p.label), "created_at": p.created_at, "last_used_at": p.last_used_at}


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_options(request):
    _clear_stale()
    user = request.user
    options = generate_registration_options(
        rp_id=settings.PASSKEY_RP_ID, rp_name="Open Word Bible", user_name=user.username,
        user_id=f"owb-{user.pk}".encode(), user_display_name=user.first_name or user.username,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED, user_verification=UserVerificationRequirement.PREFERRED),
        exclude_credentials=[PublicKeyCredentialDescriptor(id=base64url_to_bytes(p.credential_id))
                             for p in user.passkeys.all()])
    return _options(options, user)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def passkeys(request):
    user = request.user
    if request.method == "GET":
        return Response([passkey_json(p) for p in user.passkeys.all()])
    if user.passkeys.count() >= MAX_PASSKEYS:
        return _error(f"An account can have up to {MAX_PASSKEYS} passkeys.", "too_many")
    credential = _credential(request)
    challenge = credential and _take_challenge(credential, user)
    if challenge is None:
        return _error(*FAILED)
    try:
        verified = verify_registration_response(
            credential=credential, expected_challenge=challenge, expected_rp_id=settings.PASSKEY_RP_ID,
            expected_origin=settings.PASSKEY_ORIGINS)
    except (InvalidRegistrationResponse, ValueError, KeyError, TypeError) as e:
        log.info("passkey not added: %s", e)
        return _error(*FAILED)
    transports = (credential.get("response") or {}).get("transports") or []
    p, created = Passkey.objects.get_or_create(
        credential_id=bytes_to_base64url(verified.credential_id),
        defaults={"user": user, "public_key": verified.credential_public_key, "sign_count": verified.sign_count,
                  "transports": [t for t in transports if isinstance(t, str)][:10],
                  "label": request.META.get("HTTP_USER_AGENT", "")[:200]})
    if not created and p.user_id != user.id:
        return _error(*FAILED)
    return Response(passkey_json(p), status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def passkey(request, passkey_id):
    deleted, _ = request.user.passkeys.filter(id=passkey_id).delete()
    if not deleted:
        return _error("No such passkey.", "not_found", status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authentication_classes([])
def sign_in_options(request):
    _clear_stale()
    options = generate_authentication_options(rp_id=settings.PASSKEY_RP_ID,
                                              user_verification=UserVerificationRequirement.PREFERRED)
    return _options(options)


@api_view(["POST"])
@authentication_classes([])
@parser_classes([JSONParser])
def sign_in(request):
    from .views import FOREIGN, error, foreign, signed_in
    if foreign(request):
        return error(*FOREIGN)
    credential = _credential(request)
    challenge = credential and _take_challenge(credential)
    p = credential and Passkey.objects.select_related("user").filter(
        credential_id=str(credential.get("id", ""))).first()
    if challenge is None or p is None or not p.user.is_active:
        return _error(*FAILED)
    try:
        verified = verify_authentication_response(
            credential=credential, expected_challenge=challenge, expected_rp_id=settings.PASSKEY_RP_ID,
            expected_origin=settings.PASSKEY_ORIGINS, credential_public_key=bytes(p.public_key),
            credential_current_sign_count=p.sign_count)
    except (InvalidAuthenticationResponse, ValueError, KeyError, TypeError) as e:
        log.info("passkey sign-in refused: %s", e)
        return _error(*FAILED)
    p.sign_count = verified.new_sign_count
    p.last_used_at = timezone.now()
    p.save(update_fields=["sign_count", "last_used_at"])
    return signed_in(auth.issue_token(p.user, request.META.get("HTTP_USER_AGENT", "")))
