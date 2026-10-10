"""Imported texts: the original-language editions our translation is made
from, and the public-domain Bibles readers and reviewers compare against.

Nothing here is edited by hand; everything is loaded by `manage.py
import_texts` from the pinned sources in sources.lock.json.
"""
from django.db import models


class Edition(models.Model):
    class Kind(models.TextChoices):
        ORIGINAL = "original", "Original-language base text"
        REFERENCE = "reference", "Reference translation"

    code = models.SlugField(max_length=32, unique=True, help_text="e.g. sblgnt, wlc, bsb, rv1909")
    name = models.CharField(max_length=200)
    language = models.CharField(max_length=3, help_text="ISO 639-3: grc, hbo, eng, spa")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    licence = models.CharField(max_length=200)
    source = models.CharField(max_length=64, help_text="Key in sources.lock.json")
    source_commit = models.CharField(max_length=40)
    source_path = models.CharField(max_length=200, blank=True)
    attribution = models.TextField(blank=True)
    imported_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind", "language", "code"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Verse(models.Model):
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="verses")
    book = models.CharField(max_length=3)
    chapter = models.PositiveSmallIntegerField()
    verse = models.PositiveSmallIntegerField()
    text = models.TextField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["edition", "book", "chapter", "verse"],
                                               name="unique_verse_per_edition")]
        indexes = [models.Index(fields=["book", "chapter"])]
        ordering = ["edition", "book", "chapter", "verse"]

    def __str__(self):
        return f"{self.edition.code} {self.book}.{self.chapter}.{self.verse}"


class Word(models.Model):
    """One word (Greek) or morpheme (Hebrew) of an original-language edition,
    keyed by its MACULA id. The record files refer to these ids."""
    id = models.CharField(max_length=16, primary_key=True)
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE, related_name="words")
    book = models.CharField(max_length=3)
    chapter = models.PositiveSmallIntegerField()
    verse = models.PositiveSmallIntegerField()
    position = models.PositiveSmallIntegerField(help_text="Word number within the verse")
    seq = models.PositiveIntegerField(help_text="Order within the edition")
    text = models.CharField(max_length=64)
    after = models.CharField(max_length=16, blank=True)
    lemma = models.CharField(max_length=64, blank=True)
    morph = models.CharField(max_length=32, blank=True)
    gloss = models.CharField(max_length=200, blank=True)
    english = models.CharField(max_length=200, blank=True)
    strong = models.CharField(max_length=16, blank=True)
    transliteration = models.CharField(max_length=64, blank=True)
    lang = models.CharField(max_length=3, blank=True, help_text="grc, H (Hebrew) or A (Aramaic)")

    class Meta:
        indexes = [models.Index(fields=["book", "chapter", "verse"])]
        ordering = ["seq"]

    def __str__(self):
        return f"{self.id} {self.text}"
