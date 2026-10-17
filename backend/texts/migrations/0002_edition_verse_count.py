from django.db import migrations, models
from django.db.models import Count


def count_verses(apps, schema_editor):
    Edition = apps.get_model("texts", "Edition")
    Verse = apps.get_model("texts", "Verse")
    for edition_id, n in Verse.objects.values("edition").annotate(n=Count("id")).values_list("edition", "n"):
        Edition.objects.filter(id=edition_id).update(verse_count=n)


class Migration(migrations.Migration):

    dependencies = [
        ("texts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="edition",
            name="verse_count",
            field=models.PositiveIntegerField(default=0, help_text="Verses loaded, kept by import_texts"),
        ),
        migrations.RunPython(count_verses, migrations.RunPython.noop),
    ]
