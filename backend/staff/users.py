"""Readers' accounts, for the users area.

GET    /api/admin/users/?q=&role=&system=&offset=
                                            accounts, newest first: search
                                            by address or name; role=any for
                                            the team, or a role's kind.
                                            System accounts (accounts/
                                            system.py) are left out unless
                                            system=1 (or system=only)
GET    /api/admin/users/<id>/               one account: roles, devices,
                                            saved verses, messages
PATCH  /api/admin/users/<id>/ {name, system, active}
                                            set the display name (as the
                                            reader can on their account
                                            page), or mark the account a
                                            system account or a person;
                                            active false deactivates it
                                            (super admin): no sign-in, devices
                                            signed out, everything kept
POST   /api/admin/users/<id>/sign-out/      sign every device out (a team
                                            member's: super admin only)
DELETE /api/admin/users/<id>/               delete the account (super admin)

An account's highlights and bookmarks are counted, never listed: they are
the reader's own. Each account comes with display_name: its name, or one
made from its address when it has none (display_name_is_fallback).
"""
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from accounts import auth
from accounts.models import Role, SignInLink, SystemAccount
from accounts.system import name_from_email, people
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


def _is_system(user):
    try:
        return user.system_account is not None
    except SystemAccount.DoesNotExist:
        return False


def _row(user):
    return {"id": user.id, "email": user.username, "name": user.first_name,
            "display_name": user.first_name or name_from_email(user.username),
            "display_name_is_fallback": not user.first_name, "system": _is_system(user),
            "joined": user.date_joined, "signed_in": user.last_login, "active": user.is_active,
            "roles": [r.as_json()["label"] for r in user.roles.all()],
            "marks": getattr(user, "n_marks", None), "devices": getattr(user, "n_devices", None)}


@admin_view("users")
def user_list(request):
    params = request.query_params
    users = get_user_model().objects.select_related("system_account").prefetch_related("roles").annotate(
        n_marks=Count("marks", distinct=True), n_devices=Count("api_tokens", distinct=True))
    shown = params.get("system", "")
    hidden = 0
    if shown == "only":
        users = users.filter(system_account__isnull=False)
    elif shown not in ("1", "true", "all"):
        hidden = SystemAccount.objects.count()
        users = people(users)
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
                     "system_hidden": hidden,
                     "roles": [{"kind": k, "label": label} for k, label in Role.Kind.choices]})


@admin_view("users", methods=("GET", "PATCH", "DELETE"))
def user_detail(request, user_id):
    user = (get_user_model().objects.filter(id=user_id).select_related("system_account")
            .prefetch_related("roles", "api_tokens").first())
    if user is None:
        return Response({"detail": "No such account.", "code": "not_found"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "DELETE":
        return _delete(request, user)
    if request.method == "PATCH":
        _change(request, user)
        user = (get_user_model().objects.filter(id=user.id).select_related("system_account")
                .prefetch_related("roles", "api_tokens").first())
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
        "can_deactivate": (is_super_admin(request.user) and user != request.user
                           and not user.roles.filter(kind=Role.Kind.SUPER_ADMIN).exists()),
        "can_sign_out": _may_sign_out(request.user, user),
        "system_reason": user.system_account.reason if _is_system(user) else "",
    })


def _may_sign_out(actor, user):
    """Whether actor may sign user's devices out: anyone with the users area
    for a reader, only a super admin for a member of the team (someone with
    a role), so the users role can't lock the team out."""
    return is_super_admin(actor) or not user.roles.exists()


def _change(request, user):
    """PATCH: the display name (under 80 characters, as on the account
    page), and whether the account is a system account."""
    data = request.data if isinstance(request.data, dict) else {}
    if "name" in data:
        name = " ".join(str(data["name"] or "").split())
        if len(name) > 80:
            raise ValidationError({"name": "Keep it under 80 characters."})
        if name != user.first_name:
            user.first_name = name
            user.save(update_fields=["first_name"])
            record(request.user, "user.name", user.username, name=name)
    if "system" in data:
        if not isinstance(data["system"], bool):
            raise ValidationError({"system": "Send true or false."})
        if data["system"] and not _is_system(user):
            if user == request.user:
                raise ValidationError({"system": "Your own account is a person's.", "code": "self"})
            if user.roles.exists():
                raise ValidationError({"system": "Take this account's roles away first: a system account "
                                       "holds none.", "code": "has_roles"})
            SystemAccount.objects.create(user=user, reason=f"Marked by {request.user.username}")
            record(request.user, "user.system", user.username)
        elif not data["system"] and _is_system(user):
            SystemAccount.objects.filter(user=user).delete()
            record(request.user, "user.person", user.username)
    if "active" in data:
        _activate(request, user, data["active"])


def _activate(request, user, active):
    """Deactivate an account (a super admin's call): it can't sign in by any
    way and its devices are signed out, but it is kept, with its reviews
    and messages, as deleting can't when it has review history; or let it
    sign in again."""
    if not isinstance(active, bool):
        raise ValidationError({"active": "Send true or false."})
    if not is_super_admin(request.user):
        raise PermissionDenied("Only a super admin can deactivate or reactivate an account.")
    if active == user.is_active:
        return
    if not active:
        if user == request.user:
            raise ValidationError({"active": "You can't deactivate your own account here.", "code": "self"})
        if user.roles.filter(kind=Role.Kind.SUPER_ADMIN).exists():
            raise ValidationError({"active": "A super admin's account can't be deactivated here.",
                                   "code": "super_admin"})
    user.is_active = active
    user.save(update_fields=["is_active"])
    if not active:
        user.api_tokens.all().delete()
    record(request.user, "user.activate" if active else "user.deactivate", user.username)


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
    if not _may_sign_out(request.user, user):
        return Response({"detail": "Only a super admin can sign out a member of the team.", "code": "forbidden"},
                        status=status.HTTP_403_FORBIDDEN)
    n, _ = user.api_tokens.all().delete()
    record(request.user, "user.sign_out", user.username, devices=n)
    return Response({"signed_out": n})
