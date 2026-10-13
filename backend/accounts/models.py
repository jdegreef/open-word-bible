"""Accounts: who someone is, what they may do, and how they sign in.

Anyone with an email address can have an account. They sign in with a
password, a single-use link emailed to them, or Google; an account is
created the first time a link is used (or Google vouches for the address),
so there are never accounts for addresses nobody has proved they own. Every account is a reader
(highlights, bookmarks, notes, suggestions and questions). Further roles
are granted by a super admin:

- language reviewer, for one reading language: approves the wording;
- scholar reviewer, for Greek or Hebrew: approves the meaning;
- editor: triages suggestions and questions, revises drafts, writes
  articles, but never approves their own work;
- super admin: everything, including granting roles.

A sentence is "reviewed" only when a scholar reviewer and a language
reviewer have approved it. Approving takes a reviewer role even for a super
admin, so the badge always means someone qualified checked it.

The site and the API are on different hosts, so a signed-in browser holds an
API token (one per device), not a session cookie. Tokens and sign-in links
are stored only as SHA-256 hashes.
"""
import hashlib
import secrets

from django.conf import settings
from django.db import models
from django.db.models import Q

from owb import languages


def new_secret():
    """A random secret and the hash that is stored in its place."""
    secret = secrets.token_urlsafe(32)
    return secret, hash_secret(secret)


def hash_secret(secret):
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


class Role(models.Model):
    class Kind(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super admin"
        EDITOR = "editor", "Editor"
        SCHOLAR_REVIEWER = "scholar_reviewer", "Scholar reviewer"
        LANGUAGE_REVIEWER = "language_reviewer", "Language reviewer"

    # Original languages a scholar reviews, and reading languages a language
    # reviewer reviews (data/languages.json). A language added there changes
    # the check below, so it needs `manage.py makemigrations accounts`.
    ORIGINAL_LANGUAGES = {code: lang["name"] for code, lang in languages.ORIGINAL.items()}
    READING_LANGUAGES = {code: lang["name"] for code, lang in languages.READING.items()}

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roles")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    language = models.CharField(
        max_length=3, blank=True,
        help_text="Scholar reviewer: grc or hbo. Language reviewer: en, es, ... Others: blank.")
    granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "kind", "language"], name="unique_role"),
            models.CheckConstraint(
                name="role_language_matches_kind",
                condition=(Q(kind="scholar_reviewer", language__in=list(languages.ORIGINAL))
                           | Q(kind="language_reviewer", language__in=list(languages.READING))
                           | (Q(kind__in=["super_admin", "editor"]) & Q(language=""))),
            ),
        ]
        ordering = ["user", "kind", "language"]

    def __str__(self):
        return f"{self.get_kind_display()}{f' ({self.language})' if self.language else ''}"

    def as_json(self):
        names = self.ORIGINAL_LANGUAGES | self.READING_LANGUAGES
        label = self.get_kind_display()
        if self.language:
            label += f", {names.get(self.language, self.language)}"
        return {"kind": self.kind, "language": self.language, "label": label}


class SignInLink(models.Model):
    """A single-use link, valid for SIGN_IN_LINK_MINUTES. Each is emailed
    except Google's, which hands the browser back to the site."""
    class Purpose(models.TextChoices):
        SIGN_IN = "sign_in", "Sign in"
        SIGN_UP = "sign_up", "Confirm a new password"
        RESET = "reset", "Reset the password"
        GOOGLE = "google", "Signed in with Google"

    email = models.EmailField(db_index=True)
    token_hash = models.CharField(max_length=64, unique=True)
    purpose = models.CharField(max_length=10, choices=Purpose.choices, default=Purpose.SIGN_IN)
    # Sign-up: the chosen password, already hashed. It becomes the account's
    # password only when the link is used, so it never applies to an
    # address its owner has not confirmed.
    password_hash = models.CharField(max_length=128, blank=True)
    requested_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} at {self.created_at:%Y-%m-%d %H:%M}"


class FailedSignIn(models.Model):
    """A wrong password, kept for an hour to limit guessing."""
    email = models.EmailField(db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class ApiToken(models.Model):
    """A signed-in device. Signing out deletes it."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_tokens")
    key_hash = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=200, blank=True, help_text="The browser it was issued to")
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ({self.label or 'device'})"
