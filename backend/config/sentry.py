"""Optional error reporting to Sentry, switched on by SENTRY_DSN.

We never log what readers search for, so nothing about a request leaves the
server except its method and its address without the query string: no
cookies, headers, body, query string or local variables, and no `q`
anywhere in an event or its breadcrumbs.
"""
import re

# Anything after a "?" in a URL or a logged path.
QUERY_STRING = re.compile(r"\?[^\s\"'<>]*")
# Request fields that may hold a search, a session or a token.
REQUEST_FIELDS = ("query_string", "cookies", "headers", "data", "env")


def strip_query(text):
    return QUERY_STRING.sub("", text)


def _clean(value):
    """Drop `q` keys and query strings from every dict, list and string."""
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items() if k != "q"}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    if isinstance(value, str):
        return strip_query(value)
    return value


def scrub_breadcrumb(crumb, hint=None):
    # SQL breadcrumbs can carry a search's parameters.
    if crumb.get("category") in ("query", "db"):
        return None
    if isinstance(crumb.get("data"), dict):
        crumb["data"].pop("http.query", None)
        crumb["data"].pop("http.fragment", None)
    return _clean(crumb)


def scrub_event(event, hint=None):
    request = event.get("request")
    if isinstance(request, dict):
        for field in REQUEST_FIELDS:
            request.pop(field, None)
    breadcrumbs = event.get("breadcrumbs")
    if isinstance(breadcrumbs, dict) and isinstance(breadcrumbs.get("values"), list):
        breadcrumbs["values"] = [c for c in map(scrub_breadcrumb, breadcrumbs["values"]) if c]
    return _clean(event)


def init(dsn, environment, **options):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[DjangoIntegration()],
        # Collect nothing about people or requests. This is send_default_pii=
        # False spelled out (sentry-sdk 2.7x deprecates that option); the
        # scrubber below still checks every event.
        data_collection={
            "user_info": False,
            "cookies": {"mode": "off"},
            "http_headers": {"request": {"mode": "off"}},
            "http_bodies": [],
            "url_query_params": {"mode": "off"},
            "database_query_data": False,
            "stack_frame_variables": False,
        },
        include_local_variables=False,
        max_request_body_size="never",
        before_send=scrub_event,
        before_breadcrumb=scrub_breadcrumb,
        **options,
    )
