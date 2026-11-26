"""A sentence's status said "meaning reviewed" from its first meaning
approval on, even after the meaning was flagged, changed since the
approval or the approval was taken back. staff/review.py settle_status now
keeps it in step with the meaning layer's state; this puts the statuses
already saved in step once. Only "ai_draft" and "meaning_reviewed" move."""
from django.db import migrations

from owb import languages


def settle(apps, schema_editor):
    Sentence = apps.get_model("translation", "Sentence")
    ReviewState = apps.get_model("translation", "ReviewState")
    for layer in languages.ORIGINAL:   # the meaning layers
        sentences = Sentence.objects.filter(source_edition__language=layer)
        approved = ReviewState.objects.filter(layer=layer, state="approved").values("sentence_id")
        sentences.filter(status="ai_draft", pk__in=approved).update(status="meaning_reviewed")
        sentences.filter(status="meaning_reviewed").exclude(pk__in=approved).update(status="ai_draft")


class Migration(migrations.Migration):
    dependencies = [("translation", "0017_review_state_and_bible_order")]
    operations = [migrations.RunPython(settle, migrations.RunPython.noop)]
