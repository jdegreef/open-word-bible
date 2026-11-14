from django.db import migrations


class Migration(migrations.Migration):
    """Joins the two 0017 migrations, which were written in parallel."""

    dependencies = [
        ("accounts", "0017_indonesian_language_reviewers"),
        ("accounts", "0017_readerstate_memory"),
    ]

    operations = []
