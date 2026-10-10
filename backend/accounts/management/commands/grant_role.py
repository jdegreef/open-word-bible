"""Grant (or with --remove, take away) a role.

    python backend/manage.py grant_role someone@example.org scholar_reviewer grc
    python backend/manage.py grant_role someone@example.org language_reviewer es
    python backend/manage.py grant_role someone@example.org editor --remove

The account is created if it does not exist yet, so a reviewer can be set
up before they first sign in.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from accounts.models import Role
from accounts.views import normalise_email


class Command(BaseCommand):
    help = "Grant or remove a role: EMAIL KIND [LANGUAGE]"

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("kind", choices=Role.Kind.values)
        parser.add_argument("language", nargs="?", default="")
        parser.add_argument("--remove", action="store_true")

    def handle(self, email, kind, language, remove, **options):
        try:
            email = normalise_email(email)
        except ValidationError:
            raise CommandError(f"not a valid email address: {email!r}")
        User = get_user_model()
        if remove:
            n, _ = Role.objects.filter(user__username=email, kind=kind, language=language).delete()
            self.stdout.write(f"removed {n} role(s) from {email}")
            return
        try:
            with transaction.atomic():
                user, _ = User.objects.get_or_create(username=email, defaults={"email": email})
                role, created = Role.objects.get_or_create(user=user, kind=kind, language=language)
        except IntegrityError:
            raise CommandError(f"{kind} needs a language: scholar_reviewer takes "
                               f"{'/'.join(Role.ORIGINAL_LANGUAGES)}, language_reviewer takes "
                               f"{'/'.join(Role.READING_LANGUAGES)}, others none")
        self.stdout.write(f"{email}: {role} ({'granted' if created else 'already had it'})")
