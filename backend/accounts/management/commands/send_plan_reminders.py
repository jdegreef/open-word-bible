"""Email each reader who asked for them the next day of their reading plan
(accounts/reminders.py).

    python backend/manage.py send_plan_reminders            send what is due
    python backend/manage.py send_plan_reminders --dry-run  print it instead

Run it every hour from a Render cron job with the API service's environment
(DATABASE_URL, the EMAIL_* settings, OWB_SITE_URL, OWB_API_URL, and
DJANGO_SECRET_KEY, which signs the unsubscribe links), e.g. schedule
"5 * * * *". Each reader gets at most one a day, at or after the hour they
chose in their own time zone, so a missed run catches up on the next.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand

from accounts import reminders

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Email readers the next day of their reading plan."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, dry_run=False, **options):
        sent = skipped = failed = 0
        for user, prefs, state, day in reminders.due():
            email = reminders.reminder(user, prefs, state)
            if email is None:
                skipped += 1
                continue
            subject, body, headers = email
            if dry_run:
                self.stdout.write(f"To {user.username}: {subject}\n{body}")
                continue
            try:
                EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.username], headers=headers).send()
            except Exception:
                log.exception("reading-plan email failed")
                failed += 1
                continue
            prefs.last_reminder = day
            prefs.save(update_fields=["last_reminder"])
            sent += 1
        self.stdout.write(f"{sent} reading-plan email(s) sent, {skipped} reader(s) with no day to read, "
                          f"{failed} failed.")
