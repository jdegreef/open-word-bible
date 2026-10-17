"""Email the super admins about what has broken, once for each problem
(staff/alerts.py).

    python backend/manage.py send_alerts             email what is due
    python backend/manage.py send_alerts --dry-run   print it instead

It runs before every deploy, after the content import, and every 30 minutes
from a Render cron job (render.yaml). It never fails: a deploy must not
stop because an alert could not be sent.
"""
from django.core.management.base import BaseCommand

from staff import alerts


class Command(BaseCommand):
    help = "Email the super admins about what has broken, once for each problem."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, dry_run=False, **options):
        try:
            sent = alerts.send(dry_run=dry_run, out=self.stdout.write)
        except Exception as e:
            self.stderr.write(f"send_alerts failed: {type(e).__name__}: {e}")
            return
        self.stdout.write(f"{sent} alert(s) sent.")
