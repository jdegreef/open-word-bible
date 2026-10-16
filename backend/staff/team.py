"""The team: who holds a role, granting and taking roles away, and the log
of what was done in the admin. Super admins only.

GET    /api/admin/team/                     everyone with a role, and the
                                            roles that can be granted
POST   /api/admin/team/       {email, kind, language}
                                            grant a role, inviting the
                                            address by email if it has
                                            never signed in
DELETE /api/admin/team/roles/<id>/          take a role away
POST   /api/admin/team/invite/ {email}      send the invitation again
GET    /api/admin/activity/?before=<id>     what was done in the admin

Super admin is not granted here: the addresses in OWB_SUPER_ADMIN_EMAILS
are made super admins when they sign in (accounts.auth.sync_super_admin),
so the list lives outside the repository and outside the admin.

As with `manage.py grant_role`, granting a role to an address with no
account creates the account, unused until someone signs in with that
address; the invitation tells them how.
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.auth import site_url
from accounts.models import Role
from accounts.views import normalise_email

from .models import AdminAction, record
from .permissions import admin_view
from .progress import _action_json

log = logging.getLogger(__name__)
K = Role.Kind

# What each grantable role is for, as the team page explains it.
GRANTABLE = {
    K.EDITOR: "Answers reader suggestions and questions; sees progress.",
    K.SCHOLAR_REVIEWER: "Approves the meaning of Greek or Hebrew sentences (when review opens).",
    K.LANGUAGE_REVIEWER: "Approves the wording in one reading language (when review opens).",
    K.REPORTING: "Sees the progress pages: dashboard, coverage, languages, health, engagement.",
    K.USERS: "Sees readers' accounts and can sign their devices out.",
    K.EMAIL: "Emails the team from the admin.",
}

INVITATION = ("You've been added to the Open Word Bible team",
              "{inviter} has given you the role of {role} on Open Word Bible.\n\n"
              "Sign in with this address ({email}) to start:\n\n{url}\n\n"
              "You can sign in with a link emailed to you, with Google, or with a password "
              "you choose. If you weren't expecting this, you can ignore this email.")


def _languages_for(kind):
    if kind == K.SCHOLAR_REVIEWER:
        return Role.ORIGINAL_LANGUAGES
    if kind == K.LANGUAGE_REVIEWER:
        return Role.READING_LANGUAGES
    return {}


def _member(user):
    return {
        "id": user.id, "email": user.username, "name": user.first_name,
        "signed_in": user.last_login, "pending": user.last_login is None,
        "roles": [{"id": r.id, **r.as_json(), "granted_by": r.granted_by.username if r.granted_by else "",
                   "granted_at": r.created_at}
                  for r in user.roles.all()],
    }


def invite(user, role, inviter):
    """Email user that they hold role, with a link to sign in. Returns
    False when the email could not be sent."""
    subject, body = INVITATION
    try:
        send_mail(subject=subject,
                  message=body.format(inviter=inviter.first_name or inviter.username,
                                      role=role.as_json()["label"].lower(), email=user.username,
                                      url=site_url("/login/", redirect="/admin/")),
                  from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[user.username])
    except Exception:
        log.exception("invitation email failed")
        return False
    return True


@admin_view("team", methods=("GET", "POST"))
def team(request):
    if request.method == "POST":
        return _grant(request)
    User = get_user_model()
    members = (User.objects.filter(roles__isnull=False).distinct()
               .prefetch_related("roles__granted_by").order_by("username"))
    return Response({
        "members": [_member(u) for u in members],
        "grantable": [{"kind": k.value, "label": k.label, "about": about,
                       "languages": [{"code": c, "name": n} for c, n in _languages_for(k).items()]}
                      for k, about in GRANTABLE.items()],
        "super_admins_from": "OWB_SUPER_ADMIN_EMAILS",
    })


def _grant(request):
    data = request.data if isinstance(request.data, dict) else {}
    email = normalise_email(data.get("email"))
    kind = str(data.get("kind", ""))
    language = str(data.get("language", "") or "")
    if kind not in GRANTABLE:
        raise ValidationError({"kind": "Choose a role to grant.", "code": "invalid_role"})
    if language not in _languages_for(kind) and (language or _languages_for(kind)):
        raise ValidationError({"language": "Choose a language for this role.", "code": "invalid_language"})
    User = get_user_model()
    try:
        with transaction.atomic():
            user, created = User.objects.get_or_create(username=email, defaults={"email": email})
            role, granted = Role.objects.get_or_create(user=user, kind=kind, language=language,
                                                       defaults={"granted_by": request.user})
    except IntegrityError:
        raise ValidationError({"detail": "That role can't be granted with that language.", "code": "invalid_role"})
    if not granted:
        return Response({"detail": f"{email} already has that role.", "code": "already_granted"},
                        status=status.HTTP_409_CONFLICT)
    record(request.user, "role.grant", email, role=role.as_json()["label"], new_account=created)
    invited = invite(user, role, request.user) if user.last_login is None else None
    if invited:
        record(request.user, "role.invite", email)
    return Response({"member": _member(user), "invited": invited}, status=status.HTTP_201_CREATED)


@admin_view("team", methods=("DELETE",))
def revoke(request, role_id):
    role = Role.objects.select_related("user").filter(id=role_id).first()
    if role is None:
        return Response({"detail": "No such role.", "code": "not_found"}, status=status.HTTP_404_NOT_FOUND)
    if role.kind == K.SUPER_ADMIN:
        return Response({"detail": "Super admins come from OWB_SUPER_ADMIN_EMAILS on the server. "
                                   "Remove the address there, then the role in the database admin.",
                         "code": "super_admin"}, status=status.HTTP_400_BAD_REQUEST)
    label = role.as_json()["label"]
    email = role.user.username
    role.delete()
    record(request.user, "role.revoke", email, role=label)
    return Response(status=status.HTTP_204_NO_CONTENT)


@admin_view("team", methods=("POST",))
def resend(request):
    data = request.data if isinstance(request.data, dict) else {}
    email = normalise_email(data.get("email"))
    user = get_user_model().objects.filter(username=email).prefetch_related("roles").first()
    role = user.roles.exclude(kind=K.SUPER_ADMIN).first() if user else None
    if role is None:
        return Response({"detail": "That address has no role to invite them to.", "code": "not_found"},
                        status=status.HTTP_404_NOT_FOUND)
    if not invite(user, role, request.user):
        return Response({"detail": "The invitation email could not be sent.", "code": "email_unavailable"},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    record(request.user, "role.invite", email)
    return Response({"invited": True})


@admin_view("team")
def activity(request):
    actions = AdminAction.objects.all()
    before = request.query_params.get("before")
    if before and before.isdigit():
        actions = actions.filter(id__lt=int(before))
    page = list(actions[:50])
    return Response({"actions": [_action_json(a) for a in page],
                     "more": len(page) == 50})
