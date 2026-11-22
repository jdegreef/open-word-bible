"""System accounts: accounts that are not people (accounts.models.SystemAccount).

people() is every account that is a person, for the reader counts; a
system account is left out of those and out of the admin's Users list
unless asked for.

SYSTEM_RULE is how the accounts already there were marked (migration
0024): an account is a system account when its username is not an email
address, it has never signed in and it holds no role. Every account made
by signing in has a proven address for its username, so a person's account
never fits the rule; a name like "render" was made by a script or a shell.
Nothing is deleted, and an admin can unmark any account.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

SYSTEM_RULE = ("username is not an email address, never signed in, holds no role")


def is_email(value):
    try:
        validate_email(value)
    except ValidationError:
        return False
    return True


def fits_rule(user, has_roles):
    """Whether user fits SYSTEM_RULE; has_roles says whether it holds one."""
    return not is_email(user.username or "") and user.last_login is None and not has_roles


def people(users=None):
    """The accounts that are people: users (every account by default)
    without the system accounts."""
    if users is None:
        users = get_user_model().objects.all()
    return users.filter(system_account__isnull=True)


def name_from_email(email):
    """A name to show for an account without one, from its address's local
    part: "jane.doe+bible@example.org" is "Jane Doe"."""
    local = str(email or "").split("@", 1)[0].split("+", 1)[0]
    words = [w for w in local.replace(".", " ").replace("_", " ").replace("-", " ").split() if w]
    return " ".join(w[:1].upper() + w[1:] for w in words) or str(email or "")
