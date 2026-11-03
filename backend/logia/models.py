"""Logia (logia.faith), the commentary site that shares these accounts.

A reader signs in on Open Word Bible and is handed back to Logia with a
single-use code (Handoff), which Logia trades for an API token of its own. What
they save and like on Logia is kept here, against the same account, so it
follows them to every device and is deleted with the account.

Logia's comments are named by a key, <work>.<BOOK>.<chapter>.<verse>
("calvin.JHN.1.14": Calvin on John 1:14), which stays the same however the
excerpts behind it are cut.
"""
from django.conf import settings
from django.db import models


class Handoff(models.Model):
    """A single-use code that hands a signed-in reader to a partner site
    (settings.PARTNER_SITES). Only its hash is stored."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="handoffs")
    site = models.CharField(max_length=32)
    code_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} to {self.site} at {self.created_at:%Y-%m-%d %H:%M}"


class Saved(models.Model):
    """A comment the reader saved on Logia."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="logia_saved")
    key = models.CharField(max_length=80)
    chapter = models.CharField(max_length=16, db_index=True, help_text="BOOK.chapter, from the key")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "key"], name="logia_saved_once")]
        verbose_name_plural = "saved"

    def __str__(self):
        return f"{self.user}: {self.key}"


class Like(models.Model):
    """A comment the reader liked on Logia. The counts are public; who liked
    what is not."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="logia_likes")
    key = models.CharField(max_length=80)
    chapter = models.CharField(max_length=16, db_index=True, help_text="BOOK.chapter, from the key")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["user", "key"], name="logia_liked_once")]

    def __str__(self):
        return f"{self.user}: {self.key}"
