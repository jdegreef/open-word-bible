"""Middleware for the API's speed: compressing answers, and saying where a
request's time went."""
import time

from django.conf import settings
from django.db import connection
from django.middleware.gzip import GZipMiddleware


class ApiGzipMiddleware(GZipMiddleware):
    """Gzip the API's JSON reads of a kilobyte or more (coverage, the verse
    inspector, search), when the browser accepts it.

    Only GET answers are compressed. BREACH needs a secret and text the
    attacker chose in the same compressed answer: the answers that carry a
    secret (an API token from signing in, a sign-in link) are all answers to
    POSTs, so leaving POSTs alone keeps them out whatever an endpoint later
    echoes back. Django adds its own random padding as well."""
    MIN_LENGTH = 1024

    def process_response(self, request, response):
        if (request.method != "GET" or not request.path.startswith("/api/")
                or not response.get("Content-Type", "").startswith("application/json")
                or (not response.streaming and len(response.content) < self.MIN_LENGTH)):
            return response
        return super().process_response(request, response)


class ServerTimingMiddleware:
    """Server-Timing on /api/ answers: time in the database (and how many
    queries) and in total, for the browser's network panel."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)
        db = {"time": 0.0, "queries": 0}

        def timed(execute, sql, params, many, context):
            start = time.perf_counter()
            try:
                return execute(sql, params, many, context)
            finally:
                db["time"] += time.perf_counter() - start
                db["queries"] += 1

        start = time.perf_counter()
        with connection.execute_wrapper(timed):
            response = self.get_response(request)
        total = time.perf_counter() - start
        response["Server-Timing"] = (f'db;dur={db["time"] * 1000:.1f};desc="{db["queries"]} queries", '
                                     f"app;dur={total * 1000:.1f}")
        # The site calls from another origin; without this its pages can't
        # read the timings.
        origin = request.headers.get("Origin")
        if origin and origin in settings.CORS_ALLOWED_ORIGINS:
            response["Timing-Allow-Origin"] = origin
        return response
