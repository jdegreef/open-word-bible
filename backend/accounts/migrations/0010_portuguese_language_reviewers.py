from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_mark_note"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="role",
            name="role_language_matches_kind",
        ),
        migrations.AddConstraint(
            model_name="role",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("kind", "scholar_reviewer"), ("language__in", ["grc", "hbo"])),
                    models.Q(("kind", "language_reviewer"),
                             ("language__in", ["en", "es", "fr", "sw", "vi", "ko", "pt"])),
                    models.Q(("kind__in", ["super_admin", "editor", "reporting", "users", "email"]),
                             ("language", "")),
                    _connector="OR",
                ),
                name="role_language_matches_kind",
            ),
        ),
    ]
