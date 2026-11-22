"""A trigram index on a reader message's text, for the inbox's search
(staff/inbox.py q=): text__icontains is an ILIKE '%word%', which this
index answers once there are more messages than a scan reads quickly.
pg_trgm is already there for the Bible search (translation 0003)."""
import django.contrib.postgres.indexes
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0005_reader_message_status_index"),
    ]

    operations = [
        TrigramExtension(),
        migrations.AddIndex(
            model_name="readermessage",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["text"], name="message_text_trgm", opclasses=["gin_trgm_ops"]
            ),
        ),
    ]
