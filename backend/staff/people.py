"""How the admin shows a team member to another.

Team addresses go to super admins (who manage the team) and to the person
themselves; everyone else sees a name. Someone with no name on their
account is "Team member 12" rather than their address, so a reviewer or an
editor is never handed a colleague's address because a name is missing.

admin_view sets who is asking (VIEWER) for the length of each request, so
any part of an answer can call person() without being handed the request.
"""
import contextvars

VIEWER = contextvars.ContextVar("staff_viewer", default=(None, False))


def name(user):
    """user's name as the team sees it; never their address."""
    return user.get_full_name().strip() or f"Team member {user.id}"


def public_name(user):
    """How user is named where anyone can read it (a GitHub issue in the
    public repository): their first name, or "an editor"; never their
    address. Who did it is in the activity log."""
    return user.first_name.strip() or "an editor"


def person(user):
    """{"id", "name"} for user, with "email" when the one asking is a super
    admin or user themselves; None for no user."""
    if user is None:
        return None
    viewer, super_admin = VIEWER.get()
    out = {"id": user.id, "name": name(user)}
    if super_admin or (viewer is not None and viewer.id == user.id):
        out["email"] = user.username
    return out
