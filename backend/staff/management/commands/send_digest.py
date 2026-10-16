"""Email the super admins a digest of what needs attention in the admin.

    python backend/manage.py send_digest             email it
    python backend/manage.py send_digest --dry-run   print it instead
    python backend/manage.py send_digest --days 7    the period it covers

It says what came in over the period (reader messages, new accounts, what
was done in the admin), what is still waiting (unanswered messages,
invitations not taken up, open jobs and fix requests on GitHub), and how
the last content import went, with links into the admin. Nothing is sent
when there is nothing to report.

To send it every week, run it from a Render cron job with the API service's
environment (DATABASE_URL, the EMAIL_* settings, OWB_SITE_URL and
OWB_GITHUB_TOKEN), e.g. schedule "45 13 * * 1" (Mondays, 13:45 UTC).
"""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role
from feedback.models import ReaderMessage
from staff import articles, fixes, jobs
from staff.models import AdminAction, record
from translation.models import ImportRun, Sentence


def plural(n, one, many=None):
    return f"{n:,} {one if n == 1 else many or one + 's'}"


class Command(BaseCommand):
    help = "Email the super admins a digest of what needs attention."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, days=7, dry_run=False, **options):
        since = timezone.now() - timedelta(days=days)
        admin = f"{settings.OWB_SITE_URL}/admin/"
        User = get_user_model()
        lines, waiting = [], 0

        unanswered = ReaderMessage.objects.filter(status=ReaderMessage.Status.NEW)
        new_messages = ReaderMessage.objects.filter(created_at__gte=since).count()
        if new_messages or unanswered.exists():
            lines.append(f"Reader messages: {new_messages:,} new this period; "
                         f"{plural(unanswered.count(), 'waits', 'wait')} for an answer, the oldest from "
                         f"{unanswered.order_by('created_at').first().created_at:%d %B}. {admin}#inbox"
                         if unanswered.exists() else f"Reader messages: {new_messages:,} new, all answered.")
            waiting += unanswered.count()
        pending = User.objects.filter(last_login__isnull=True, roles__isnull=False).distinct()
        if pending.exists():
            lines.append(f"Invitations: {plural(pending.count(), 'team member hasn’t', 'team members haven’t')} "
                         f"signed in yet ({', '.join(pending.values_list('username', flat=True)[:5])}). {admin}#team")
            waiting += pending.count()

        if settings.OWB_GITHUB_TOKEN:
            for label, fetch, page in (("Drafting jobs", jobs.open_jobs, "jobs"),
                                       ("Fix requests", fixes.open_fixes, "fixes"),
                                       ("Article jobs", articles.open_article_jobs, "articles")):
                try:
                    found = fetch()
                except jobs.GitHubError:
                    lines.append(f"{label}: GitHub could not be reached.")
                    continue
                if found:
                    untaken = [j for j in found if not j.get("assignees")]
                    untaken_note = f", {len(untaken):,} not taken yet" if untaken else ""
                    lines.append(f"{label}: {len(found):,} open{untaken_note}. {admin}#{page}")

        last = ImportRun.objects.first()
        if last and last.error:
            lines.append(f"Content import: the last run ({last.started_at:%d %B %H:%M} UTC) failed: "
                         f"{last.error.splitlines()[0][:200]}. {admin}#health")
            waiting += 1
        elif last and last.skipped:
            lines.append(f"Content import: the last run left {plural(len(last.skipped), 'file')} for later. "
                         f"{admin}#health")

        accounts = User.objects.filter(date_joined__gte=since).count()
        actions = AdminAction.objects.filter(created_at__gte=since).exclude(action="digest.send").count()
        changed = Sentence.objects.filter(updated_at__gte=since).count()
        lines.append(f"This period: {plural(accounts, 'new account')}, {plural(changed, 'sentence')} imported "
                     f"or changed, {plural(actions, 'thing')} done in the admin. {admin}")

        if not waiting and not (new_messages or accounts or actions or changed):
            self.stdout.write("Nothing to report; no digest sent.")
            return
        subject = (f"Open Word Bible: {plural(waiting, 'thing')} waiting" if waiting
                   else "Open Word Bible: this week in the admin")
        body = "\n\n".join(lines) + ("\n\n--\nThe weekly digest for Open Word Bible's super admins "
                                     "(backend/staff/management/commands/send_digest.py).")
        to = sorted(set(User.objects.filter(is_active=True, roles__kind=Role.Kind.SUPER_ADMIN)
                        .values_list("username", flat=True)))
        if dry_run:
            self.stdout.write(f"To: {', '.join(to) or '(no super admins)'}\nSubject: {subject}\n\n{body}")
            return
        sent = 0
        for address in to:
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [address])
                sent += 1
            except Exception as e:
                self.stderr.write(f"digest to a {address.rsplit('@', 1)[-1]} address failed: {e}")
        record(None, "digest.send", f"{sent} super admin(s)", waiting=waiting)
        self.stdout.write(f"Digest sent to {sent} of {len(to)} super admin(s).")
