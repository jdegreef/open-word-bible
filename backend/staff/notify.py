"""Telling people when the admin gives them work, by email.

    role_granted(user, role, by)   a role on an account that has signed in
                                   before (a new one gets the invitation,
                                   team.invite, which now names the same)
    assigned(a)                    a review assignment, to its reviewer
    send_due(now)                  what falls due: a reminder three days
                                   before an assignment's date and on it,
                                   and on Mondays each reviewer's week
                                   (their assignments, their open flags,
                                   what changed since they approved it)

Each email links to where the work is: My review for the layer, which
opens on the reviewer's brief and glossary (staff/hints.py guide). A
reminder or a week's email is sent once: the activity log records it
("notify.*"), and send_due looks there first. send_due runs from
send_alerts, so the hourly import job and the alerts cron both send what
is due. A failed email is logged and given up, never raised: no grant or
assignment fails because mail is down.
"""
import datetime
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from accounts.auth import site_url
from accounts.models import Role
from translation.models import ReviewState

from .models import AdminAction, ReviewAssignment, record

log = logging.getLogger(__name__)
K = Role.Kind
REMIND_BEFORE = 3   # days before the due date
DIGEST_WEEKDAY = 0  # Monday


def _send(to, subject, body):
    try:
        send_mail(subject=subject, message=body, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[to])
    except Exception:
        log.exception("staff email failed: %s", subject)
        return False
    return True


def workspace_url(layer=""):
    return site_url("/admin/", fragment=f"workspace/{layer}" if layer else "workspace")


def where_to_start(role):
    """The link a role's email opens, and a line on what to read first."""
    from . import hints   # hints reads review, which reads this module's callers
    if role.kind in (K.SCHOLAR_REVIEWER, K.LANGUAGE_REVIEWER) and role.language:
        docs = hints.guide(role.language)
        repo = f"https://github.com/{settings.OWB_GITHUB_REPO}/blob/main/"
        reading = "".join(f"\n  {d['label']}: {repo}{d['file']}" for d in docs)
        return workspace_url(role.language), ("Read first:" + reading + "\n\n") if reading else ""
    return site_url("/admin/"), ""


def role_granted(user, role, by):
    url, reading = where_to_start(role)
    name = by.first_name or "A super admin"
    return _send(user.username, f"You have a new role on Open Word Bible: {role.as_json()['label']}",
                 f"{name} has given you the role of {role.as_json()['label'].lower()} on Open Word Bible.\n\n"
                 f"{reading}Start here:\n\n{url}\n")


def _assignment_text(a):
    from .assignments import range_label
    from .review import layer_json
    due = f", by {a.due:%A %d %B %Y}" if a.due else ""
    note = f"\n\nA note from {a.assigned_by.first_name or 'the editor'}: {a.note}" if a.note and a.assigned_by else ""
    return range_label(a), layer_json(a.layer)["name"], due, note


def assigned(a):
    label, layer, due, note = _assignment_text(a)
    return _send(a.assignee.username, f"Review assigned to you: {label} ({layer})",
                 f"You have been asked to review {label} in {layer}{due}.{note}\n\n"
                 f"It is in My review, with the brief and glossary:\n\n{workspace_url(a.layer)}\n")


def _once(kind, key, user):
    """Whether kind for key has been sent already; if not, record it (by
    the admin itself, to user)."""
    if AdminAction.objects.filter(action=f"notify.{kind}", target=key).exists():
        return False
    record(None, f"notify.{kind}", key, to=user.username)
    return True


def send_due(now=None, dry_run=False, out=None):
    """Send the reminders and weekly emails due now. Returns how many."""
    from . import assignments as asg
    now = now or timezone.now()
    today = timezone.localdate(now)
    sent = 0
    for a in ReviewAssignment.objects.filter(closed_at__isnull=True, due__isnull=False,
                                             due__lte=today + datetime.timedelta(days=REMIND_BEFORE),
                                             due__gte=today).select_related("assignee", "assigned_by"):
        if asg.standing(a, asg.progress(a), today) not in ("open", "overdue"):
            continue
        when = "today" if a.due == today else f"soon-{a.due.isoformat()}"
        if a.due != today and (a.due - today).days != REMIND_BEFORE:
            continue
        key = f"assignment {a.id} {when}"
        if dry_run:
            out and out(f"would remind {a.assignee.username}: {key}")
            continue
        if not _once("reminder", key, a.assignee):
            continue
        label, layer, _, _ = _assignment_text(a)
        counts = asg.progress(a)
        left = counts["total"] - counts["approved"]
        heading = "Due today" if a.due == today else f"Due in {REMIND_BEFORE} days"
        day = "today" if a.due == today else f"on {a.due:%A %d %B}"
        sent += _send(a.assignee.username, f"{heading}: {label} ({layer})",
                      f"Your review of {label} in {layer} is due {day}. {left:,} of {counts['total']:,} "
                      f"sentences are still to approve.\n\n{workspace_url(a.layer)}\n")
    if today.weekday() == DIGEST_WEEKDAY:
        sent += _weekly(today, dry_run, out)
    return sent


def _weekly(today, dry_run, out):
    from . import assignments as asg
    from .review import layer_json
    week = f"{today.isocalendar()[0]}-W{today.isocalendar()[1]:02d}"
    sent = 0
    reviewers = (get_user_model().objects.filter(is_active=True, roles__kind__in=[K.SCHOLAR_REVIEWER,
                                                                                  K.LANGUAGE_REVIEWER])
                 .distinct())
    for user in reviewers:
        lines = []
        for a in ReviewAssignment.objects.filter(assignee=user, closed_at__isnull=True):
            counts = asg.progress(a)
            standing = asg.standing(a, counts, today)
            if standing in ("open", "overdue"):
                due = f", due {a.due:%d %B}" if a.due else ""
                lines.append(f"- {asg.range_label(a)} ({layer_json(a.layer)['name']}): {counts['approved']:,} of "
                             f"{counts['total']:,} approved{due}{' (overdue)' if standing == 'overdue' else ''}")
        flags = ReviewState.objects.filter(state=ReviewState.State.FLAGGED, event__user=user).count()
        changed = ReviewState.objects.filter(state=ReviewState.State.CHANGED, event__user=user).count()
        if flags:
            lines.append(f"- {flags:,} of your flags are still open.")
        if changed:
            lines.append(f"- {changed:,} sentences you approved have changed since, and wait for another look.")
        if not lines:
            continue
        key = f"{user.id} {week}"
        if dry_run:
            out and out(f"would send {user.username} their week")
            continue
        if not _once("week", key, user):
            continue
        sent += _send(user.username, "Your review this week on Open Word Bible",
                      "Where your review stands:\n\n" + "\n".join(lines) + f"\n\n{workspace_url()}\n")
    return sent
