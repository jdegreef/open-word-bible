from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0016_japanese_language_reviewers"),
    ]

    operations = [
        migrations.AddField(
            model_name="readerstate",
            name="memory",
            field=models.JSONField(default=dict),
        ),
    ]
