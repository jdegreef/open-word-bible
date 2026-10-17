"""Who may open what in the admin.

The admin is split into areas. Each /api/admin/ endpoint names its area
with @admin_view, and an account may use it only if one of its roles opens
that area (AREAS). The site's admin page asks GET /api/me which areas the
account has (user_json "admin") and shows only those; that is a courtesy,
never the check, which is made here on every request.

backend_tests/test_admin.py fails if an /api/admin/ endpoint is left without
an area.
"""
from functools import wraps

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from accounts.models import Role

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
    # Reader suggestions and questions: they carry the reader's name.
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


def admin_view(area, methods=("GET",)):
    """An /api/admin/ endpoint in area: an API view taking JSON that answers
    401 to anyone signed out and 403 to an account whose roles don't open
    area. The view gets the account's areas as request.admin_areas."""
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
            return view(request, *args, **kwargs)

        endpoint = api_view(list(methods))(parser_classes([JSONParser])(checked))
        endpoint.admin_area = area
        return endpoint

    return wrap
