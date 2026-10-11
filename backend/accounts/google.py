"""Signing in with Google (OpenID Connect, authorization code with PKCE).

The site sends the browser to GET /api/auth/google/start?lang=..&redirect=..,
which sets a short-lived signed cookie on the API host (the state, the PKCE
verifier, and where to return) and goes on to Google. Google sends it back to
/api/auth/google/callback, which checks the state, trades the code for an ID
token, and sends the browser to the site's /login/ page with a single-use
link (#google=<secret>) that the page trades for an API token through
/api/auth/verify, as it does an email link. Nothing that signs in is ever in
a query string or a cookie on the site.

Only addresses Google has verified are accepted, and they sign in to the
account with that address, creating it the first time: an address is one
account however its owner signs in.

Needs GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET, with
https://<api host>/api/auth/google/callback as an authorised redirect URI.
Without them /api/auth/methods says so and the site hides the button.
"""
import base64
import hashlib
import json
import logging
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.core import signing
from django.shortcuts import redirect as http_redirect

from . import auth

log = logging.getLogger(__name__)

AUTHORIZE = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN = "https://oauth2.googleapis.com/token"
ISSUERS = ("https://accounts.google.com", "accounts.google.com")
COOKIE = "owb_google"
COOKIE_PATH = "/api/auth/google/"
SALT = "accounts.google"
MAX_AGE = 600


def enabled():
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


def _callback_url(request):
    return request.build_absolute_uri("/api/auth/google/callback")


def _site_login(lang, fragment, redirect=""):
    prefix = "" if lang == "en" else f"/{lang}"
    query = f"?redirect={urllib.parse.quote(redirect, safe='/')}" if redirect else ""
    return f"{settings.OWB_SITE_URL}{prefix}/login/{query}#{fragment}"


def start(request):
    lang = request.GET.get("lang", "en")
    lang = lang if lang in auth.LANGUAGES else "en"
    back = auth.safe_redirect(request.GET.get("redirect", ""))
    if not enabled():
        return http_redirect(_site_login(lang, "error=google_unavailable", back))
    state = secrets.token_urlsafe(24)
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    query = urllib.parse.urlencode({
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": _callback_url(request),
        "response_type": "code",
        "scope": "openid email",
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "prompt": "select_account",
    })
    response = http_redirect(f"{AUTHORIZE}?{query}")
    response.set_cookie(
        COOKIE, signing.dumps({"state": state, "verifier": verifier, "lang": lang, "redirect": back}, salt=SALT),
        max_age=MAX_AGE, path=COOKIE_PATH, secure=not settings.DEBUG, httponly=True, samesite="Lax")
    return response


def _decode_payload(id_token):
    payload = id_token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))


def _exchange(request, code, verifier):
    """The ID token's claims for an authorisation code. The token comes
    straight from Google's token endpoint over TLS, authenticated with the
    client secret, so its signature need not be checked again (OpenID
    Connect Core 3.1.3.7); its audience, issuer and expiry still are."""
    body = urllib.parse.urlencode({
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": _callback_url(request),
        "grant_type": "authorization_code",
        "code_verifier": verifier,
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN, data=body), timeout=10) as r:
        claims = _decode_payload(json.load(r)["id_token"])
    if (claims.get("aud") != settings.GOOGLE_CLIENT_ID or claims.get("iss") not in ISSUERS
            or int(claims.get("exp", 0)) < time.time()):
        raise ValueError("ID token is not for this site")
    return claims


def callback(request):
    try:
        saved = signing.loads(request.COOKIES.get(COOKIE, ""), salt=SALT, max_age=MAX_AGE)
    except signing.BadSignature:
        saved = None
    lang = saved["lang"] if saved else "en"
    back = saved["redirect"] if saved else ""
    fragment = "error=google_failed"
    if (saved and request.GET.get("code") and enabled()
            and secrets.compare_digest(request.GET.get("state", ""), saved["state"])):
        try:
            claims = _exchange(request, request.GET["code"], saved["verifier"])
        except (urllib.error.URLError, ValueError, KeyError, TimeoutError):
            log.exception("Google sign-in failed")
            claims = None
        if claims and claims.get("email") and claims.get("email_verified") in (True, "true"):
            from .views import normalise_email
            try:
                email = normalise_email(claims["email"])
            except Exception:
                email = None
            if email:
                fragment = "google=" + auth.google_link(email)
    elif request.GET.get("error") == "access_denied":
        fragment = "error=google_cancelled"
    response = http_redirect(_site_login(lang, fragment, back))
    response.delete_cookie(COOKIE, path=COOKIE_PATH)
    return response
