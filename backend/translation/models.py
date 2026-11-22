"""Our translation: sentence records with their renderings and decisions,
and the review trail.

Until the reviewer workflow ships, the JSON files in content/ are the master
copy and `manage.py import_content` loads them here; afterwards this
database becomes the master and content/ the published export.
"""
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from owb.refs import BOOK_CODES
from texts.models import Edition


class Status(models.TextChoices):
    AI_DRAFT = "ai_draft", "AI-assisted"
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
    alignments = models.JSONField(default=list, blank=True,
                                  help_text="Links from source tokens to rendering spans, as in content/")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AI_DRAFT)
    updated_at = models.DateTimeField(auto_now=True)
    # The book's place in the Bible (owb.refs.BOOK_CODES), worked out by the
    # database from book, so review queues are sorted and paged there.
    book_order = models.GeneratedField(
        expression=models.Case(*(models.When(book=code, then=models.Value(i))
                                 for i, code in enumerate(BOOK_CODES)),
                               default=models.Value(99), output_field=models.SmallIntegerField()),
        output_field=models.SmallIntegerField(), db_persist=True)

    class Meta:
        # updated_at: the admin's health page shows the last change.
        indexes = [models.Index(fields=["book", "chapter"]), models.Index(fields=["updated_at"]),
                   # Bible order: review queues are sorted and paged on it.
                   models.Index(fields=["book_order", "chapter", "verse", "number", "id"],
                                name="sentence_bible_order")]
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
        # One language's renderings (export, the wording review queue)
        # without reading the other languages' 90%.
        indexes = [models.Index(fields=["language", "sentence"], name="rendering_language")]
        ordering = ["sentence", "language", "level"]

    def __str__(self):
        return f"{self.sentence} {self.language}/{self.level}"


class DraftedCount(models.Model):
    """How many of a book's sentences are drafted in a language (have any
    rendering in it). import_content keeps these as it saves each file, so
    the admin's progress pages read 66 x languages rows instead of counting
    over a million renderings in a web request (translation/counts.py)."""
    book = models.CharField(max_length=3)
    language = models.CharField(max_length=3)
    sentences = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["book", "language"], name="one_count_per_book_language")]

    def __str__(self):
        return f"{self.book} {self.language}: {self.sentences}"


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
        indexes = [
            # A language's decisions: the meaning review queue.
            models.Index(fields=["language", "sentence"], name="decision_language_sentence"),
            # The admin's uncertain decisions, by language.
            models.Index(fields=["language"], condition=models.Q(uncertain=True),
                         name="decision_uncertain"),
        ]
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
    digest = models.CharField(max_length=64, blank=True,
                              help_text="What was reviewed (staff/review.py digest): an approval whose "
                                        "sentence no longer matches it has changed since")
    snapshot = models.JSONField(default=dict, blank=True,
                                help_text="What was approved (staff/snapshot.py), so the admin can show what has "
                                          "changed since word by word. Empty for approvals made before it was kept")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["sentence", "created_at"], name="review_event_trail"),
                   models.Index(fields=["action", "created_at"], name="review_event_action")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sentence} {self.action} by {self.user}"


class ReviewState(models.Model):
    """Where a sentence stands in one review layer, kept from its review
    trail so the admin's queues are filtered and paged in the database: the
    latest approval or flag in the layer, and what that makes the sentence.
    A sentence with no approval or flag in a layer has no row ("not
    reviewed").

    Saving or deleting a ReviewEvent brings its row up to date (sync).
    Whether an approval still matches the sentence ("approved") or not
    ("changed") is worked out by staff/review.py's refresh, for the rows
    whose sentence was saved after they were last checked, as an import
    saves every sentence it touches. Nothing here changes Sentence.status."""
    class State(models.TextChoices):
        APPROVED = "approved", "Approved"
        CHANGED = "changed", "Changed since approval"
        FLAGGED = "flagged", "Flagged"

    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name="review_states")
    layer = models.CharField(max_length=3, help_text="grc or hbo for the meaning, a reading language for wording")
    state = models.CharField(max_length=8, choices=State.choices)
    event = models.ForeignKey(ReviewEvent, on_delete=models.CASCADE, related_name="+",
                              help_text="The latest approval or flag in the layer")
    checked_at = models.DateTimeField(null=True, blank=True,
                                      help_text="The sentence's updated_at when its approval was last "
                                                "compared with it; empty until then")

    DECIDING = (ReviewEvent.Action.MEANING_REVIEWED, ReviewEvent.Action.REVIEWED, ReviewEvent.Action.FLAGGED)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["sentence", "layer"], name="one_review_state_per_layer")]
        indexes = [models.Index(fields=["layer", "state"], name="review_state_layer"),
                   models.Index(fields=["state"], name="review_state_state")]

    def __str__(self):
        return f"{self.sentence_id} {self.layer} {self.state}"

    @classmethod
    def sync(cls, sentence_id, language, saved=None):
        """Bring the row for one sentence and layer (an event's language,
        blank for the meaning) up to date with the sentence's trail, after
        the event with id saved was saved or deleted."""
        original = (Sentence.objects.filter(pk=sentence_id)
                    .values_list("source_edition__language", flat=True).first())
        if original is None:   # the sentence is being deleted
            return
        layer = language or original
        latest = (ReviewEvent.objects.filter(sentence_id=sentence_id, language=language, action__in=cls.DECIDING)
                  .order_by("-created_at", "-id").first())
        if latest is None:
            cls.objects.filter(sentence_id=sentence_id, layer=layer).delete()
            return
        state = cls.State.FLAGGED if latest.action == ReviewEvent.Action.FLAGGED else cls.State.APPROVED
        row = cls.objects.filter(sentence_id=sentence_id, layer=layer).first()
        if row and row.event_id == latest.id and latest.id != saved:
            return   # a comment, say: nothing changes, nor needs comparing again
        cls.objects.update_or_create(sentence_id=sentence_id, layer=layer,
                                     defaults={"event": latest, "state": state, "checked_at": None})


@receiver(post_save, sender=ReviewEvent)
@receiver(post_delete, sender=ReviewEvent)
def _sync_review_state(sender, instance, **kwargs):
    ReviewState.sync(instance.sentence_id, instance.language, saved=instance.pk)


class ContentFile(models.Model):
    """A file in content/ as import_content last imported it, so a deploy
    imports only the files that have changed since."""
    path = models.CharField(max_length=200, primary_key=True,
                            help_text="Relative to the repository, e.g. content/JHN/JHN.1.json")
    digest = models.CharField(max_length=64)

    def __str__(self):
        return self.path


class ImportRun(models.Model):
    """One run of import_content: when it ran, what it imported and what
    stopped it. The admin's health page lists the latest."""
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    everything = models.BooleanField(default=False, help_text="--all")
    files = models.PositiveIntegerField(default=0, help_text="Files imported")
    records = models.PositiveIntegerField(default=0)
    unchanged = models.PositiveIntegerField(default=0, help_text="Files skipped as unchanged")
    skipped = models.JSONField(default=list, blank=True, help_text="Files left for a missing source text")
    drafted = models.JSONField(default=dict, blank=True,
                               help_text="Sentences drafted in a language for the first time: {book: {lang: n}}")
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"import {self.started_at:%Y-%m-%d %H:%M}"

    def finish(self, error=""):
        self.finished_at = timezone.now()
        self.error = error[:5000]
        self.save()


class SentenceChange(models.Model):
    """A rendering an import changed, added or removed in a sentence that was
    already drafted in that language, with its text before and after (the
    admin's Changes page). A sentence drafted in a language for the first
    time is only counted, in ImportRun.drafted."""
    class Kind(models.TextChoices):
        ADDED = "added", "Added"
        CHANGED = "changed", "Changed"
        REMOVED = "removed", "Removed"

    run = models.ForeignKey(ImportRun, on_delete=models.CASCADE, related_name="changes")
    record_id = models.CharField(max_length=24)
    verse = models.CharField(max_length=16, help_text="The sentence's first verse, e.g. JHN.1.12")
    book = models.CharField(max_length=3)
    chapter = models.PositiveSmallIntegerField()
    language = models.CharField(max_length=3)
    level = models.CharField(max_length=1, choices=Rendering.Level.choices)
    kind = models.CharField(max_length=7, choices=Kind.choices)
    before = models.TextField(blank=True)
    after = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.record_id} {self.language}/{self.level} {self.kind}"


class RecordChange(models.Model):
    """What an import did to a sentence besides its renderings' text
    (SentenceChange): a sentence drafted in a language for the first time,
    and a decision added, changed or removed in a sentence already drafted
    (in that language, for a rendering decision; at all, for a meaning
    decision). The admin's release notes (staff/history.py) read these with
    SentenceChange. Never touches review status."""
    class Kind(models.TextChoices):
        DRAFTED = "drafted", "Drafted in the language"
        DECISION_ADDED = "decision_added", "Decision added"
        DECISION_CHANGED = "decision_changed", "Decision changed"
        DECISION_REMOVED = "decision_removed", "Decision removed"

    run = models.ForeignKey(ImportRun, on_delete=models.CASCADE, related_name="record_changes")
    record_id = models.CharField(max_length=24)
    verse = models.CharField(max_length=16, help_text="The sentence's first verse, e.g. JHN.1.12")
    book = models.CharField(max_length=3)
    chapter = models.PositiveSmallIntegerField()
    language = models.CharField(max_length=3, blank=True, help_text="Blank for a meaning decision")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    key = models.CharField(max_length=16, blank=True, help_text="The decision's key, e.g. m1, r-en-2")
    before = models.JSONField(default=dict, blank=True, help_text="The decision as it was")
    after = models.JSONField(default=dict, blank=True, help_text="The decision as it is now")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["language", "kind"])]
        ordering = ["id"]

    def __str__(self):
        return f"{self.record_id} {self.language or 'meaning'} {self.kind} {self.key}"


# Search (GET /api/search/, translation/search.py). import_content updates
# these tables from the same documents the site's own search file holds
# (search_documents in scripts/build_site.py), one set per site language.

class SearchLanguage(models.Model):
    """A site language search covers, with its books (names, abbreviations
    and translated chapters, for references such as "Juan 3:16") and the
    page shortcuts the search panel offers."""
    code = models.CharField(max_length=3, primary_key=True)
    books = models.JSONField()
    pages = models.JSONField()
    checked = models.DateTimeField(null=True, blank=True,
                                   help_text="When its entries were last brought fully up to date "
                                             "(search.rebuild takes the longest waiting first)")

    def __str__(self):
        return self.code


class SearchEntry(models.Model):
    """One thing a reader can find on the site in one language: a passage
    ("c"), a sentence ("v"), a note ("n") or an article ("a")."""
    language = models.CharField(max_length=3, help_text="The site language")
    kind = models.CharField(max_length=1)
    position = models.PositiveIntegerField(help_text="Canonical order: the order the site lists them in")
    sub = models.IntegerField(default=0, help_text="Order after position: entries added later "
                                      "between two that were kept (search.plan)")
    config = models.CharField(max_length=16, help_text="Text search configuration for the entry's own language")
    title = models.TextField(blank=True)
    extra = models.TextField(blank=True, help_text="A note's alternatives, an article's summary")
    body = models.TextField(blank=True)
    doc = models.JSONField(help_text="What the site needs to show it (the search file's document)")
    vector = SearchVectorField(null=True)

    class Meta:
        indexes = [GinIndex(fields=["vector"], name="search_entry_vector"),
                   models.Index(fields=["language", "kind", "position"], name="search_entry_order")]

    def __str__(self):
        return f"{self.language} {self.kind} {self.position}"


class SearchWord(models.Model):
    """A word the entries of one language contain, and how often: "Did you
    mean" picks the closest common one (pg_trgm)."""
    language = models.CharField(max_length=3)
    word = models.CharField(max_length=64)
    count = models.PositiveIntegerField()

    class Meta:
        indexes = [GinIndex(fields=["word"], opclasses=["gin_trgm_ops"], name="search_word_trgm")]

    def __str__(self):
        return f"{self.language} {self.word}"
