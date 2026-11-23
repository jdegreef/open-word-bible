"""Who may use the API: Open Word Bible's own site and apps, not outsiders.

Two kinds of caller reach /api/:

* Our own servers and scripts carry a key (OWB_API_KEYS, sent as the
  X-OWB-Key header). The key never goes to a browser.
* Our sites' pages (CORS_ALLOWED_ORIGINS: openwordbible.org and the partner
  sites) call from a reader's browser, which cannot keep a secret. What they
  carry instead is the Origin header every browser adds to a cross-origin
  request and no web page can change. So another website's pages are always
  turned away. A script outside a browser can write any Origin it likes, so
  for it this is a fence rather than a lock: the rate limits (search's
  SearchThrottle, the sign-in limits in accounts/) are what bound it.

The read endpoints the site never calls (KEY_ONLY: editions, chapter text,
sentence records) need the key whatever the Origin.

A few addresses are opened by a reader's browser itself, not by a page's
script, so they carry no Origin and stay open (OPEN): "Continue with Google"
and its callback, and the unsubscribe link in reading-plan emails (whose
POST also comes from mail apps' one-click unsubscribe).

Preflights (OPTIONS) are answered by accounts.cors before this runs, and
this runs inside it, so the site can read a refusal.

OWB_API_REQUIRE_ORIGIN turns the Origin rule off ("0"); it is off by default
with DJANGO_DEBUG=1, so local tools and the tests' plain requests work. The
key rule is always on.
"""
import hmac
import re

from django.conf import settings
from django.http import JsonResponse

KEY_HEADER = "X-OWB-Key"
KEY_ONLY = re.compile(r"^/api/(editions|text|passages)/")
OPEN = ("/api/auth/google/start", "/api/auth/google/callback", "/api/email/unsubscribe")


def has_key(request):
    given = request.headers.get(KEY_HEADER, "")
    return bool(given) and any(hmac.compare_digest(given.encode(), k.encode())
                               for k in settings.OWB_API_KEYS)


def refuse(code, message):
    return JsonResponse({"detail": message, "code": code}, status=403)


class ApiAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not path.startswith("/api/") or path in OPEN or has_key(request):
            return self.get_response(request)
        if KEY_ONLY.match(path):
            return refuse("key_required", "This part of the API is for Open Word Bible's own use.")
        if settings.OWB_API_REQUIRE_ORIGIN and request.headers.get("Origin") not in settings.CORS_ALLOWED_ORIGINS:
            return refuse("origin_not_allowed", "The Open Word Bible API is only for openwordbible.org.")
        return self.get_response(request)
