"""Readers' messages sent before the site used NIV numbers (2026-11-21)
name their verse by our own numbers: move them to the NIV's
(owb/renumber.py), so the inbox and the verse links show the verse the
reader was reading."""
from datetime import datetime, timezone

from django.db import migrations

from owb import renumber


def forwards(apps, schema_editor):
    switched = datetime.fromtimestamp(renumber.SWITCHED_MS / 1000, tz=timezone.utc)
    ReaderMessage = apps.get_model("feedback", "ReaderMessage")
    for message in ReaderMessage.objects.filter(created_at__lt=switched, verse__in=list(renumber.table())):
        message.verse = renumber.verse(message.verse)
        message.save(update_fields=["verse"])


class Migration(migrations.Migration):
    dependencies = [("feedback", "0005_reader_message_status_index")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
