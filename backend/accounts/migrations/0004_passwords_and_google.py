from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_swahili_language_reviewers"),
    ]

    operations = [
        migrations.AddField(
            model_name="signinlink",
            name="purpose",
            field=models.CharField(choices=[("sign_in", "Sign in"), ("sign_up", "Confirm a new password"),
                                            ("reset", "Reset the password"), ("google", "Signed in with Google")],
                                   default="sign_in", max_length=10),
        ),
        migrations.AddField(
            model_name="signinlink",
            name="password_hash",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.CreateModel(
            name="FailedSignIn",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(db_index=True, max_length=254)),
                ("ip", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
    ]
