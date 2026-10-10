"""Account endpoints.

POST   /api/auth/link       {email}         email a sign-in link (always 202)
POST   /api/auth/verify     {token}         trade a link for an API token
POST   /api/auth/sign-out                   forget this device's token
GET    /api/me                              the signed-in account
PATCH  /api/me              {display_name}  change the display name
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import auth


def _ip(request):
    # Render puts the client first in X-Forwarded-For.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR") or None


@api_view(["POST"])
def request_link(request):
    email = str(request.data.get("email", "")).strip()
    try:
        validate_email(email)
    except DjangoValidationError:
        raise ValidationError({"email": "Enter a valid email address."})
    try:
        auth.request_link(email, ip=_ip(request))
    except auth.RateLimited:
        return Response({"detail": "Too many sign-in links. Try again in an hour."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS)
    return Response({"sent": True}, status=status.HTTP_202_ACCEPTED)


@api_view(["POST"])
def verify(request):
    secret = str(request.data.get("token", "")).strip()
    result = auth.redeem_link(secret, label=request.META.get("HTTP_USER_AGENT", "")) if secret else None
    if result is None:
        return Response({"detail": "This sign-in link has expired or was already used. "
                                   "Ask for a new one."}, status=status.HTTP_400_BAD_REQUEST)
    user, key = result
    return Response({"token": key, "user": auth.user_json(user)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sign_out(request):
    request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    if request.method == "PATCH":
        name = str(request.data.get("display_name", "")).strip()
        if len(name) > 80:
            raise ValidationError({"display_name": "Keep it under 80 characters."})
        user.first_name = name
        user.save(update_fields=["first_name"])
    return Response(auth.user_json(user))
