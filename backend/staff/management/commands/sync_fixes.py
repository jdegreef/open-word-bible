"""Tell readers when their suggestion led to a change.

    python backend/manage.py sync_fixes            email and mark done
    python backend/manage.py sync_fixes --dry-run  say what it would do

A fix request filed from a reader message names the message in its issue
(staff/fixes.py). Once that issue is closed and a pull request that names
it ("Fixes #N") has merged, the reader is emailed a thank-you with a link
to the verse, and the message is marked done with the pull request's link.
Each message is told once (ReaderMessage.fixed_at).

A fix request closed without a merged change (declined: the session or an
editor decided the wording stays) puts its message back among the new
ones, with a reply to the reader drafted from the issue's closing comment
for an editor to read, change and send (ReaderMessage.follow_up). Nothing
is sent to the reader without an editor.

It runs on every deploy (render.yaml's preDeployCommand), since a merged
fix is what triggers one; without OWB_GITHUB_TOKEN, or when GitHub can't be
reached, it says so and exits cleanly, so it never blocks a deploy.
"""
import json
import logging
import re

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts import controls
from feedback.models import ReaderMessage
from staff import github
from staff.inbox import verse_label, verse_url
from staff.models import record
from staff.work import fetch_work

log = logging.getLogger(__name__)

THANKS = ("Your {kind} about {verse} changed Open Word Bible",
          "Thank you for writing to Open Word Bible about {verse}.\n\n"
          "You wrote:\n\n{quoted}\n\n"
          "An editor asked for a change because of it, and the change has now been made. "
          "It reaches the site within a few minutes:\n\n{url}\n\n"
          "Every sentence is still an AI-assisted draft until a reviewer approves it, "
          "so the wording may change again in review.\n\n"
          "This is about the message you sent from the site; we won't email you otherwise.")


FOLLOW_UP = ("Thank you for writing to Open Word Bible about {verse}. An editor asked for the change you "
             "suggested to be looked at against the Hebrew or Greek and our style guide, and the wording is "
             "staying as it is for now. {reason}\n\nWe read every message, and yours is kept with the verse "
             "for when it is reviewed again.")


def _fix_number(item):
    for line in item.get("body", "").splitlines():
        if line.startswith("<!-- fix-request "):
            try:
                return json.loads(line[len("<!-- fix-request "):-len(" -->")])
            except ValueError:
                return None
    return None


def declined_messages(work):
    """(message id, issue number) for each fix request closed with no merged
    pull request that names a reader message."""
    for item in work:
        if item["kind"] != "fix-request" or item["state"] != "closed":
            continue
        if any(p["state"] == "merged" for p in item["prs"]):
            continue
        data = _fix_number(item)
        if data and data.get("message"):
            yield data["message"], item["number"]


def closing_reason(number):
    """The issue's last comment, in short: why the fix was declined."""
    try:
        comments = github.call(f"issues/{number}/comments?per_page=100")
    except github.GitHubError:
        return ""
    text = " ".join((comments[-1].get("body") or "").split()) if comments else ""
    text = re.sub(r"<!--.*?-->", "", text).strip()
    return text[:600] + ("…" if len(text) > 600 else "")


def fixed_messages(work):
    """(message id, pull request url) for each closed fix request with a
    merged pull request that names a reader message."""
    for item in work:
        if item["kind"] != "fix-request" or item["state"] != "closed":
            continue
        merged = [p for p in item["prs"] if p["state"] == "merged"]
        if not merged:
            continue
        for line in item.get("body", "").splitlines():
            if line.startswith("<!-- fix-request "):
                try:
                    data = json.loads(line[len("<!-- fix-request "):-len(" -->")])
                except ValueError:
                    continue
                if data.get("message"):
                    yield data["message"], merged[0]["url"]


class Command(BaseCommand):
    help = "Email readers whose suggestion led to a merged change."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, dry_run=False, **options):
        if not settings.OWB_GITHUB_TOKEN:
            self.stdout.write("OWB_GITHUB_TOKEN is not set; no fixes checked.")
            return
        try:
            work = fetch_work()
        except github.GitHubError:
            self.stdout.write("GitHub could not be reached; no fixes checked.")
            return
        told = 0
        for message_id, pr_url in fixed_messages(work):
            m = ReaderMessage.objects.select_related("user").filter(id=message_id, fixed_at__isnull=True).first()
            if m is None:
                continue
            if dry_run:
                self.stdout.write(f"would tell the writer of message {m.id} ({m.verse}): {pr_url}")
                continue
            subject, body = THANKS
            if not controls.wants(m.user, "replies"):
                # Not emailed: the account page shows the message done.
                m.fixed_at, m.fix_url, m.status = timezone.now(), pr_url, ReaderMessage.Status.DONE
                m.save(update_fields=["fixed_at", "fix_url", "status"])
                record(None, "message.fixed", f"{m.get_kind_display()} on {m.verse}", message=m.id, url=pr_url)
                continue
            quoted = "\n".join("> " + line for line in m.text.splitlines())
            try:
                send_mail(subject.format(kind=m.get_kind_display().lower(), verse=verse_label(m.verse)),
                          body.format(verse=verse_label(m.verse), quoted=quoted, url=verse_url(m.verse, m.language)),
                          settings.DEFAULT_FROM_EMAIL, [m.user.username])
            except Exception:
                log.exception("fix email failed")
                continue
            m.fixed_at, m.fix_url, m.status = timezone.now(), pr_url, ReaderMessage.Status.DONE
            m.save(update_fields=["fixed_at", "fix_url", "status"])
            record(None, "message.fixed", f"{m.get_kind_display()} on {m.verse}", message=m.id, url=pr_url)
            told += 1
        self.stdout.write(f"{told} reader(s) told their suggestion led to a change.")
        back = 0
        for message_id, number in declined_messages(work):
            m = ReaderMessage.objects.filter(id=message_id, status=ReaderMessage.Status.FIXING,
                                             fix_issue=number).first()
            if m is None:
                continue
            if dry_run:
                self.stdout.write(f"would put message {m.id} back: fix #{number} was declined")
                continue
            reason = closing_reason(number)
            m.status = ReaderMessage.Status.NEW
            m.follow_up = FOLLOW_UP.format(verse=verse_label(m.verse),
                                           reason=f"The editors' note: {reason}" if reason else "")
            note = f"Fix #{number} closed without a change; a reply is drafted."
            m.note = f"{m.note}\n{note}".strip() if m.note else note
            m.save(update_fields=["status", "follow_up", "note"])
            record(None, "message.fix_declined", f"{m.get_kind_display()} on {m.verse}", message=m.id,
                   number=number)
            back += 1
        self.stdout.write(f"{back} message(s) back in the inbox: their fix was declined.")
