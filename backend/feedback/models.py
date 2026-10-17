"""Suggestions and questions readers send about a verse. Editors answer
them in the admin (staff/inbox.py); an answer is emailed to the reader."""
from django.conf import settings
from django.db import models


class ReaderMessage(models.Model):
    class Kind(models.TextChoices):
        SUGGESTION = "suggestion", "Suggestion"
        QUESTION = "question", "Question"

    class Status(models.TextChoices):
        NEW = "new", "New"
        ANSWERED = "answered", "Answered"
        DONE = "done", "Done"
        DECLINED = "declined", "Declined"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reader_messages")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    verse = models.CharField(max_length=16, help_text='A verse id, "JHN.3.16"')
    language = models.CharField(max_length=3, help_text="The language the reader was reading")
    level = models.CharField(max_length=1, blank=True, help_text="L, B or R, if the reader was on one")
    text = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW, db_index=True)
    reply = models.TextField(blank=True)
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name="+")
    replied_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True, help_text="For editors only")
    fixed_at = models.DateTimeField(null=True, blank=True,
                                    help_text="When a fix it led to was merged and the reader was told")
    fix_url = models.URLField(blank=True, help_text="The pull request that made the change")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_kind_display()} on {self.verse}"
