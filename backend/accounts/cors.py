"""CORS for the API: the reader site (openwordbible.org) calls the API on
another host (api.openwordbible.org). Only origins in CORS_ALLOWED_ORIGINS
get the headers, only under /api/, and no cookies are involved: the site
sends an API token in the Authorization header."""
import hmac

from django.conf import settings
from django.http import HttpResponse, JsonResponse


class ApiCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        api = request.path.startswith("/api/")
        allowed = api and origin and origin in settings.CORS_ALLOWED_ORIGINS
        if allowed and request.method == "OPTIONS" and "Access-Control-Request-Method" in request.headers:
            response = HttpResponse(status=204)
            response["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
            # Idempotency-Key: the admin's guard against sending twice (staff/permissions.py).
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Idempotency-Key"
            response["Access-Control-Max-Age"] = "86400"
        else:
            response = self.get_response(request)
        if allowed:
            response["Access-Control-Allow-Origin"] = origin
        if api:
            # Answers differ by Origin (and by token), so caches must not share them.
            response["Vary"] = ", ".join(filter(None, [response.get("Vary"), "Origin, Authorization"]))
        return response


# Addresses a browser opens directly (a link in an email, Google sending the
# reader back), or a mail app posts to (one-click unsubscribe), so they come
# with no Origin, or with this API's own.
OPEN_PATHS = ("/api/auth/google/start", "/api/auth/google/callback", "/api/email/unsubscribe")


class ApiOriginGate:
    """The API is for openwordbible.org and its partner sites, nobody else.

    CORS alone only stops another site's page from reading an answer: the
    request is still made, and a program that isn't a browser ignores CORS
    entirely. So, under /api/ (settings.API_ORIGIN_GATE):

    - a request from a page whose Origin is not in CORS_ALLOWED_ORIGINS is
      refused (403), before any view runs;
    - a request with no Origin, which every call from our sites has (they
      are on other hosts than the API, so the browser always sends one), is
      refused too, unless it carries one of settings.API_KEYS in X-API-Key:
      for our own servers and apps, never for a web page;
    - OPEN_PATHS stay open, since browsers and mail apps reach them
      directly.

    A program can still claim an Origin it doesn't have; the rate limits
    (config/throttles.py) and the sign-in checks are what hold against
    that. Off in development and the tests (DJANGO_DEBUG) unless
    OWB_API_ORIGIN_GATE=1."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (getattr(settings, "API_ORIGIN_GATE", False) and request.path.startswith("/api/")
                and not request.path.startswith(OPEN_PATHS) and not self.allowed(request)):
            response = JsonResponse({"detail": "This API is only for Open Word Bible and Logia.",
                                     "code": "forbidden_origin"}, status=403)
            response["Vary"] = "Origin"
            return response
        return self.get_response(request)

    @staticmethod
    def allowed(request):
        origin = request.headers.get("Origin")
        if origin:
            return origin in settings.CORS_ALLOWED_ORIGINS or origin == settings.OWB_API_URL
        key = request.headers.get("X-API-Key", "")
        return bool(key) and any(hmac.compare_digest(key, k) for k in getattr(settings, "API_KEYS", []))
