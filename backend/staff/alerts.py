"""Alerts: the super admins are emailed when something breaks, once for each
problem, so nobody has to open the dashboard to find out.

The problems (problems()):

- import: the latest content import failed, or left files for later;
- ci: a check on main's latest commit failed (GitHub);
- stalled: drafting jobs, fix requests or article jobs open for more than
  work.STALE_HOURS with no pull request (GitHub);
- inbox: reader messages new for more than INBOX_DAYS.

Each problem has a key (the import run, the failing commit, the issue or
message numbers), and each email sent is logged as an AdminAction
"alert.sent" holding it. A problem is emailed again only when its key
changes: a new import run or failing commit, or a newly stalled job or newly
overdue message. When an import or CI problem that was emailed clears, a
short note says so ("alert.resolved"). What can't be checked (GitHub out of
reach, no token, an import still running) is left alone: it is neither a
problem nor resolved.

`manage.py send_alerts` sends them, before each deploy and every 30 minutes
(render.yaml). The health page lists the problems and when each was last
emailed.
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone

from accounts.models import Role
from feedback.models import ReaderMessage
from translation.models import ImportRun

from . import jobs, progress, work
from .models import AdminAction, record

log = logging.getLogger(__name__)

INBOX_DAYS = 3
FAILED = {"failure", "timed_out", "cancelled"}
RESOLVABLE = {"import", "ci"}   # problems whose clearing is worth an email
SENT, RESOLVED = "alert.sent", "alert.resolved"


def _problem(kind, key, title, text, page):
    return {"kind": kind, "key": key, "title": title, "text": text, "href": f"#{page}"}


def _import_problem():
    """The import problem, None when the last import went well, or False
    when one is still running (not known yet)."""
    run = ImportRun.objects.first()
    if run is None:
        return None
    if run.error:
        return _problem("import", f"run-{run.id}", "The last content import failed",
                        f"The content import started {run.started_at:%d %B %H:%M} UTC failed: "
                        f"{run.error.splitlines()[0][:300]}", "health")
    if not run.finished_at:
        return False
    if run.skipped:
        n = len(run.skipped)
        return _problem("import", f"run-{run.id}", "The last content import left files for later",
                        f"The content import started {run.started_at:%d %B %H:%M} UTC left "
                        f"{n} file{'s' if n != 1 else ''} for later: {run.skipped[0][:300]}", "health")
    return None


def _ci_problem():
    """The CI problem, None when main's checks are passing, or False when
    GitHub can't be reached."""
    ci = progress._ci_status()
    if not ci:
        return False
    failed = [c["name"] for c in ci["checks"] if c["status"] == "completed" and c["conclusion"] in FAILED]
    if not failed:
        return None
    return _problem("ci", ci["sha"], "CI is failing on main",
                    f"On main's latest commit {ci['sha']} ({ci['message']}), "
                    f"{', '.join(failed)} failed. Render deploys main only once its checks pass, "
                    f"so nothing reaches the site until it is fixed. {ci['url']}", "health")


def _stalled_problem():
    """Stalled jobs, None when there are none, or False when GitHub can't
    be asked."""
    if not settings.OWB_GITHUB_TOKEN:
        return False
    try:
        items = work.fetch_work()
    except jobs.GitHubError:
        return False
    stalled = sorted((w for w in items if w["stale"]), key=lambda w: w["number"])
    if not stalled:
        return None
    listed = "\n".join(f"- {w['kind_label']} #{w['number']}: {w['title']} ({w['url']})" for w in stalled)
    return _problem("stalled", [w["number"] for w in stalled],
                    f"{len(stalled)} job{'s have' if len(stalled) != 1 else ' has'} stalled",
                    f"Open for more than {work.STALE_HOURS} hours with no pull request:\n{listed}", "work")


def _inbox_problem():
    overdue = list(ReaderMessage.objects.filter(
        status=ReaderMessage.Status.NEW, created_at__lt=timezone.now() - timedelta(days=INBOX_DAYS))
        .order_by("id").values_list("id", flat=True))
    if not overdue:
        return None
    n = len(overdue)
    return _problem("inbox", overdue, f"{n} reader message{'s have' if n != 1 else ' has'} waited "
                    f"more than {INBOX_DAYS} days",
                    f"{n} reader message{'s' if n != 1 else ''} still new after {INBOX_DAYS} days.", "inbox")


CHECKS = {"import": _import_problem, "ci": _ci_problem, "stalled": _stalled_problem, "inbox": _inbox_problem}


def problems(kinds=CHECKS):
    """{kind: problem, None (none) or False (not known)} for each kind."""
    return {kind: CHECKS[kind]() for kind in kinds}


def last_alert(kind):
    return AdminAction.objects.filter(action__in=[SENT, RESOLVED], detail__kind=kind).first()


def _is_new(problem, last):
    """Whether problem needs an email, given the last alert of its kind."""
    if last is None or last.action != SENT:
        return True
    before = last.detail.get("key")
    if isinstance(problem["key"], list):   # a list of jobs or messages: news is one not yet emailed
        return bool(set(problem["key"]) - set(before or []))
    return problem["key"] != before


def recipients():
    users = get_user_model().objects.filter(is_active=True, roles__kind=Role.Kind.SUPER_ADMIN)
    return sorted(set(users.values_list("username", flat=True)) | set(settings.OWB_SUPER_ADMIN_EMAILS))


def due(found):
    """[(action, kind, problem or None)] to email now: new problems, and
    the clearing of import or CI problems that were emailed."""
    out = []
    for kind, problem in found.items():
        last = last_alert(kind)
        if problem:
            if _is_new(problem, last):
                out.append((SENT, kind, problem))
        elif problem is None and kind in RESOLVABLE and last and last.action == SENT:
            out.append((RESOLVED, kind, None))
    return out


def _email(action, kind, problem, last):
    admin = f"{settings.OWB_SITE_URL}/admin/"
    if action == SENT:
        subject = f"Open Word Bible: {problem['title']}"
        body = f"{problem['text']}\n\n{admin}{problem['href']}"
    else:
        title = last.detail.get("title", kind)
        subject = f"Open Word Bible: resolved: {title}"
        body = f"Resolved: {title[0].lower()}{title[1:]} — no longer the case.\n\n{admin}#health"
    return subject, body + ("\n\n--\nAn alert for Open Word Bible's super admins, sent once for each "
                            "problem (backend/staff/alerts.py).")


def send(dry_run=False, out=None):
    """Email what is due. Returns the number of alerts sent. Without an
    email server (EMAIL_HOST) nothing is sent or logged, so the alerts go
    out once one is set."""
    write = out or (lambda text: log.info("%s", text))
    to = recipients()
    sent = 0
    for action, kind, problem in due(problems()):
        last = last_alert(kind)
        subject, body = _email(action, kind, problem, last)
        if dry_run or not settings.EMAIL_HOST:
            write(f"{'Would send' if dry_run else 'No EMAIL_HOST; not sent'}: {subject}")
            continue
        if not to:
            write(f"No super admins to tell: {subject}")
            continue
        delivered = 0
        for address in to:   # one email each, so nobody sees the others' addresses
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [address])
                delivered += 1
            except Exception:
                log.exception("alert email failed")
        if not delivered:
            continue   # try again next run
        detail = {"kind": kind, "recipients": delivered}
        if problem:
            detail.update(key=problem["key"], title=problem["title"])
        else:
            detail.update(key=last.detail.get("key"), title=last.detail.get("title", ""))
        record(None, action, subject[len("Open Word Bible: "):], **detail)
        write(f"Sent to {delivered} super admin(s): {subject}")
        sent += 1
    return sent


def current():
    """The problems for the health page, without asking GitHub for the jobs
    (the work page's cached answer is used if there is one), each with when
    it was last emailed."""
    found = problems(("import", "ci", "inbox"))
    out = [p for p in found.values() if p]
    out += [p for p in [_cached_stalled()] if p]
    for p in out:
        last = last_alert(p["kind"])
        emailed = last and last.action == SENT and not _is_new(p, last)
        p["emailed_at"] = last.created_at if emailed else None
    return out


def _cached_stalled():
    items = cache.get("staff.work") or []
    stalled = sorted((w for w in items if w["stale"]), key=lambda w: w["number"])
    if not stalled:
        return None
    n = len(stalled)
    return _problem("stalled", [w["number"] for w in stalled], f"{n} job{'s have' if n != 1 else ' has'} stalled",
                    f"Open for more than {work.STALE_HOURS} hours with no pull request.", "work")
