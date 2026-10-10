"""CORS for the API: the reader site (openwordbible.org) calls the API on
another host (api.openwordbible.org). Only origins in CORS_ALLOWED_ORIGINS
get the headers, only under /api/, and no cookies are involved: the site
sends an API token in the Authorization header."""
from django.conf import settings
from django.http import HttpResponse


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
            response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response["Access-Control-Max-Age"] = "86400"
        else:
            response = self.get_response(request)
        if allowed:
            response["Access-Control-Allow-Origin"] = origin
        if api:
            # Answers differ by Origin (and by token), so caches must not share them.
            response["Vary"] = ", ".join(filter(None, [response.get("Vary"), "Origin, Authorization"]))
        return response
