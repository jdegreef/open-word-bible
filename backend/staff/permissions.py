"""Who may open what in the admin.

The admin is split into areas. Each /api/admin/ endpoint names its area
with @admin_view, and an account may use it only if one of its roles opens
that area (AREAS). The site's admin page asks GET /api/me which areas the
account has (user_json "admin") and shows only those; that is a courtesy,
never the check, which is made here on every request.

backend_tests/test_admin.py fails if an /api/admin/ endpoint is left without
an area.

An endpoint that fails answers JSON the admin can show, not Django's HTML
error page: {"detail", "code", "request_id"}, 503 "timeout" when the
database gave up on a query (statement_timeout), 500 "server_error"
otherwise. The request id is in the log line and on the Sentry event, so a
screenshot of the admin finds the traceback.
"""
import hashlib
import logging
import uuid
from functools import wraps

from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import OperationalError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from accounts.models import Role

try:
    import sentry_sdk
except ImportError:   # pragma: no cover - it is in requirements.txt
    sentry_sdk = None

log = logging.getLogger(__name__)

K = Role.Kind
EVERY_ROLE = frozenset(K.values)

# Area -> the roles that open it. A super admin opens every area.
AREAS = {
    # The dashboard, coverage, languages, books, health, engagement, help:
    # progress any member of the team may see. No reader's details.
    "overview": EVERY_ROLE,
    # Downloading the translation as a file (staff/export.py). The text is
    # CC0 and on the site already.
    "export": EVERY_ROLE,
    # Reviewing sentences (staff/review.py): the meaning for scholar
    # reviewers, a language's wording for its reviewers.
    "review": frozenset({K.SUPER_ADMIN, K.SCHOLAR_REVIEWER, K.LANGUAGE_REVIEWER}),
    # Reader suggestions and questions: they carry the reader's name. Also
    # the reviewers' open flags, for editors to act on.
    "inbox": frozenset({K.SUPER_ADMIN, K.EDITOR}),
    # Readers' accounts.
    "users": frozenset({K.SUPER_ADMIN, K.USERS}),
    # Emailing the team.
    "email": frozenset({K.SUPER_ADMIN, K.EMAIL}),
    # Filing drafting jobs, which start Claude sessions.
    "jobs": frozenset({K.SUPER_ADMIN}),
    # Granting roles, and the log of what was done in the admin.
    "team": frozenset({K.SUPER_ADMIN}),
}


def areas(user):
    """The admin areas user may open, in AREAS order."""
    if not user or not user.is_authenticated:
        return []
    kinds = set(user.roles.values_list("kind", flat=True))
    return [area for area, roles in AREAS.items() if kinds & roles]


def is_super_admin(user):
    return user.is_authenticated and user.roles.filter(kind=K.SUPER_ADMIN).exists()


# How long a change sent with an Idempotency-Key is remembered.
ONCE_SECONDS = 600


def admin_view(area, methods=("GET",), once=False):
    """An /api/admin/ endpoint in area: an API view taking JSON that answers
    401 to anyone signed out and 403 to an account whose roles don't open
    area. The view gets the account's areas as request.admin_areas.

    once: the endpoint files or sends something (a GitHub issue, emails).
    A change sent with an Idempotency-Key header that this account already
    sent in the last ONCE_SECONDS, or is still sending, answers 409
    "duplicate" instead of doing it again (a double click, a retry of a
    request that worked). A change that fails frees its key."""
    if area not in AREAS:
        raise ValueError(f"unknown admin area {area!r}")

    def wrap(view):
        @wraps(view)
        def checked(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({"detail": "Sign in to use the admin.", "code": "not_signed_in"},
                                status=status.HTTP_401_UNAUTHORIZED)
            request.admin_areas = areas(request.user)
            if area not in request.admin_areas:
                return Response({"detail": "Your roles don't open this part of the admin.",
                                 "code": "forbidden"}, status=status.HTTP_403_FORBIDDEN)
            slot = _once_slot(request) if once else None
            if slot and not cache.add(slot, "sending", ONCE_SECONDS):
                return Response({"detail": "This was sent a moment ago, so it wasn't sent again. Reload to see it.",
                                 "code": "duplicate"}, status=status.HTTP_409_CONFLICT)
            try:
                response = view(request, *args, **kwargs)
            except (APIException, Http404, PermissionDenied):
                if slot:
                    cache.delete(slot)
                raise   # DRF answers these itself, as JSON
            except Exception as e:
                response = failed(request, e)
            if slot and response.status_code >= 400:
                cache.delete(slot)   # nothing was done: trying again may
            return response

        endpoint = api_view(list(methods))(parser_classes([JSONParser])(checked))
        endpoint.admin_area = area
        return endpoint

    return wrap


def timed_out(error):
    """Whether error is Postgres cancelling a statement (statement_timeout)."""
    if not isinstance(error, OperationalError):
        return False
    cause = getattr(error, "__cause__", None)
    return type(cause).__name__ == "QueryCanceled" or "statement timeout" in str(error)


def failed(request, error):
    """The JSON answer for an admin endpoint that raised error, logged (and
    so sent to Sentry, when it is set up) with a short request id."""
    request_id = uuid.uuid4().hex[:8]
    if sentry_sdk is not None:
        sentry_sdk.set_tag("request_id", request_id)
    # The path without its query string: a query may hold a search.
    log.error("Admin %s %s failed (request %s)", request.method, request.path, request_id, exc_info=error)
    if timed_out(error):
        body = {"detail": "This took longer than the database allows, so it was stopped. Try again in a "
                          "minute; if it keeps happening, report it with the request id.",
                "code": "timeout", "request_id": request_id}
        code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        body = {"detail": "The server hit an error answering this. Report it with the request id.",
                "code": "server_error", "request_id": request_id}
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
    response = Response(body, status=code)
    response["X-Request-Id"] = request_id
    return response


def _once_slot(request):
    """The cache key for a change's Idempotency-Key, per account; None for a
    read or a change sent without one."""
    key = request.headers.get("Idempotency-Key", "")
    if request.method in ("GET", "HEAD", "OPTIONS") or not key:
        return None
    digest = hashlib.sha256(f"{request.path}\n{key}".encode()).hexdigest()[:32]
    return f"staff.once.{request.user.id}.{digest}"
