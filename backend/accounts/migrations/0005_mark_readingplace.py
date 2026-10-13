from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_passwords_and_google"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Mark",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("verse", models.CharField(help_text='A verse id, "JHN.3.16"', max_length=16)),
                ("bookmark", models.BooleanField(default=False)),
                ("highlight", models.CharField(blank=True, max_length=8)),
                ("text", models.TextField(blank=True, help_text="The verse's words as shown when it was marked")),
                ("lang", models.CharField(blank=True, max_length=3)),
                ("updated_at", models.BigIntegerField()),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="marks",
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["user", "verse"],
                "constraints": [models.UniqueConstraint(fields=("user", "verse"), name="unique_mark")],
            },
        ),
        migrations.CreateModel(
            name="ReadingPlace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("book", models.CharField(max_length=3)),
                ("chapter", models.PositiveSmallIntegerField()),
                ("verse", models.CharField(help_text='"16", or "7:53" for a verse of the chapter before',
                                           max_length=8)),
                ("updated_at", models.BigIntegerField()),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                              related_name="reading_place", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
