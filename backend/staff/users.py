"""Readers' accounts, for the users area.

GET    /api/admin/users/?q=&role=&offset=   accounts, newest first: search
                                            by address or name; role=any for
                                            the team, or a role's kind
GET    /api/admin/users/<id>/               one account: roles, devices,
                                            saved verses, messages
POST   /api/admin/users/<id>/sign-out/      sign every device out
DELETE /api/admin/users/<id>/               delete the account (super admin)

An account's highlights and bookmarks are counted, never listed: they are
the reader's own.
"""
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.response import Response

from accounts import auth
from accounts.models import Role, SignInLink
from feedback.models import ReaderMessage

from .models import record
from .permissions import admin_view, is_super_admin

PAGE = 50


def _ways_in(user):
    """How the account has signed in: password, link, google."""
    ways = set()
    if auth.has_password(user):
        ways.add("password")
    for purpose in SignInLink.objects.filter(email=user.username, used_at__isnull=False) \
            .values_list("purpose", flat=True).distinct():
        ways.add("google" if purpose == SignInLink.Purpose.GOOGLE else "link")
    return sorted(ways)


def _row(user):
    return {"id": user.id, "email": user.username, "name": user.first_name,
            "joined": user.date_joined, "signed_in": user.last_login, "active": user.is_active,
            "roles": [r.as_json()["label"] for r in user.roles.all()],
            "marks": getattr(user, "n_marks", None), "devices": getattr(user, "n_devices", None)}


@admin_view("users")
def user_list(request):
    params = request.query_params
    users = get_user_model().objects.prefetch_related("roles").annotate(
        n_marks=Count("marks", distinct=True), n_devices=Count("api_tokens", distinct=True))
    q = params.get("q", "").strip()
    if q:
        users = users.filter(Q(username__icontains=q) | Q(first_name__icontains=q))
    role = params.get("role", "")
    if role == "any":
        users = users.filter(roles__isnull=False).distinct()
    elif role in Role.Kind.values:
        users = users.filter(roles__kind=role).distinct()
    try:
        offset = max(int(params.get("offset", 0)), 0)
    except ValueError:
        offset = 0
    total = users.count()
    page = users.order_by("-date_joined")[offset:offset + PAGE]
    return Response({"users": [_row(u) for u in page], "total": total, "offset": offset, "page": PAGE,
                     "roles": [{"kind": k, "label": label} for k, label in Role.Kind.choices]})


@admin_view("users", methods=("GET", "DELETE"))
def user_detail(request, user_id):
    user = get_user_model().objects.filter(id=user_id).prefetch_related("roles", "api_tokens").first()
    if user is None:
        return Response({"detail": "No such account.", "code": "not_found"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "DELETE":
        return _delete(request, user)
    marks = user.marks.aggregate(bookmarks=Count("id", filter=Q(bookmark=True)),
                                 highlights=Count("id", filter=~Q(highlight="")))
    place = getattr(user, "reading_place", None)
    messages = ReaderMessage.objects.filter(user=user)
    return Response({
        **_row(user),
        "ways_in": _ways_in(user),
        "has_password": auth.has_password(user),
        "devices": [{"label": t.label, "created_at": t.created_at, "last_used_at": t.last_used_at}
                    for t in user.api_tokens.order_by("-created_at")],
        "marks": marks,
        "reading_place": {"book": place.book, "chapter": place.chapter} if place else None,
        "messages": [{"id": m.id, "kind": m.kind, "verse": m.verse, "status": m.status,
                      "created_at": m.created_at} for m in messages[:20]],
        "role_details": [r.as_json() for r in user.roles.all()],
        "can_delete": is_super_admin(request.user) and user != request.user,
    })


def _delete(request, user):
    if not is_super_admin(request.user):
        return Response({"detail": "Only a super admin can delete an account.", "code": "forbidden"},
                        status=status.HTTP_403_FORBIDDEN)
    if user == request.user:
        return Response({"detail": "Delete your own account from your account page.", "code": "self"},
                        status=status.HTTP_400_BAD_REQUEST)
    if user.roles.filter(kind=Role.Kind.SUPER_ADMIN).exists():
        return Response({"detail": "A super admin's account can't be deleted here.", "code": "super_admin"},
                        status=status.HTTP_400_BAD_REQUEST)
    email = user.username
    if not auth.delete_account(user):
        return Response({"detail": "This account has review history, which the record keeps.",
                         "code": "has_reviews"}, status=status.HTTP_409_CONFLICT)
    record(request.user, "user.delete", email)
    return Response(status=status.HTTP_204_NO_CONTENT)


@admin_view("users", methods=("POST",))
def sign_out(request, user_id):
    user = get_user_model().objects.filter(id=user_id).first()
    if user is None:
        return Response({"detail": "No such account.", "code": "not_found"}, status=status.HTTP_404_NOT_FOUND)
    n, _ = user.api_tokens.all().delete()
    record(request.user, "user.sign_out", user.username, devices=n)
    return Response({"signed_out": n})
