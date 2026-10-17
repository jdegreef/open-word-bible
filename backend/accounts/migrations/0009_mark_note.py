from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_readerstate"),
    ]

    operations = [
        migrations.AddField(
            model_name="mark",
            name="note",
            field=models.TextField(blank=True, help_text="The reader's own note, private to them"),
        ),
    ]
