"""System accounts (accounts.models.SystemAccount), and marking the ones
already there by accounts/system.py's SYSTEM_RULE: the username is not an
email address, the account has never signed in, and it holds no role (the
"render" account a deploy made, say). Nothing is deleted; reversing only
drops the marks."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def mark(apps, schema_editor):
    from accounts.system import SYSTEM_RULE, fits_rule
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    SystemAccount = apps.get_model("accounts", "SystemAccount")
    for user in User.objects.filter(last_login__isnull=True, roles__isnull=True).only("id", "username", "last_login"):
        if fits_rule(user, has_roles=False):
            SystemAccount.objects.get_or_create(user=user, defaults={"reason": "Migration 0024: " + SYSTEM_RULE})


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0023_punjabi_language_reviewers"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemAccount",
            fields=[
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True,
                                              related_name="system_account", serialize=False,
                                              to=settings.AUTH_USER_MODEL)),
                ("reason", models.CharField(blank=True, help_text="Why it was marked, and by whom", max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RunPython(mark, migrations.RunPython.noop),
    ]
