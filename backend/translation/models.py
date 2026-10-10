"""Our translation: sentence records with their renderings and decisions,
and the review trail.

Until the reviewer workflow ships, the JSON files in content/ are the master
copy and `manage.py import_content` loads them here; afterwards this
database becomes the master and content/ the published export.
"""
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from texts.models import Edition


class Status(models.TextChoices):
    AI_DRAFT = "ai_draft", "AI draft"
    MEANING_REVIEWED = "meaning_reviewed", "Meaning reviewed"
    REVIEWED = "reviewed", "Reviewed"
    REVISED = "revised", "Revised"


class Sentence(models.Model):
    record_id = models.CharField(max_length=24, unique=True, help_text="e.g. JHN.1.12.s1")
    book = models.CharField(max_length=3)
    chapter = models.PositiveSmallIntegerField()
    verse = models.PositiveSmallIntegerField(help_text="First verse")
    number = models.PositiveSmallIntegerField(help_text="Sentence number within the first verse")
    refs = ArrayField(models.CharField(max_length=16), help_text="Verse ids the sentence covers")
    source_edition = models.ForeignKey(Edition, on_delete=models.PROTECT)
    source_text_id = models.CharField(max_length=32)
    tokens = ArrayField(models.CharField(max_length=16), help_text="Source word ids, in order")
    source_text = models.TextField(blank=True)
    literal_gloss = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AI_DRAFT)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["book", "chapter"])]
        ordering = ["book", "chapter", "verse", "number"]

    def __str__(self):
        return self.record_id


class Rendering(models.Model):
    class Level(models.TextChoices):
        LITERAL = "L", "Literal"
        BALANCED = "B", "Balanced"
        READABLE = "R", "Readable"

    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name="renderings")
    language = models.CharField(max_length=3, help_text="e.g. en, es")
    level = models.CharField(max_length=1, choices=Level.choices)
    text = models.TextField(help_text="May contain {{setting:default|alt}} spans and \\v markers")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["sentence", "language", "level"],
                                               name="one_rendering_per_language_level")]
        ordering = ["sentence", "language", "level"]

    def __str__(self):
        return f"{self.sentence} {self.language}/{self.level}"


class Decision(models.Model):
    class Layer(models.TextChoices):
        MEANING = "meaning", "Meaning (shared by every language)"
        RENDERING = "rendering", "Rendering (one language)"

    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name="decisions")
    key = models.CharField(max_length=16, help_text="e.g. m1, r-en-2")
    order = models.PositiveSmallIntegerField()
    layer = models.CharField(max_length=10, choices=Layer.choices)
    language = models.CharField(max_length=3, blank=True, help_text="Blank for meaning decisions")
    levels = ArrayField(models.CharField(max_length=1), blank=True, default=list)
    category = models.CharField(max_length=24)
    tokens = ArrayField(models.CharField(max_length=16), blank=True, default=list)
    choice = models.TextField()
    alternatives = ArrayField(models.TextField(), blank=True, default=list)
    reason = models.TextField()
    uncertain = models.BooleanField(default=False)
    footnote = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["sentence", "key"], name="unique_decision_key")]
        ordering = ["sentence", "order"]

    def __str__(self):
        return f"{self.sentence} {self.key}"


class ReviewEvent(models.Model):
    """One step in a sentence's review trail. Only people create these; the
    AI never approves its own work."""
    class Action(models.TextChoices):
        MEANING_REVIEWED = "meaning_reviewed", "Approved the meaning"
        REVIEWED = "reviewed", "Approved the wording"
        REVISED = "revised", "Revised after review"
        FLAGGED = "flagged", "Flagged a problem"
        COMMENT = "comment", "Comment"

    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name="review_events")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=20, choices=Action.choices)
    language = models.CharField(max_length=3, blank=True, help_text="For wording reviews")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sentence} {self.action} by {self.user}"
