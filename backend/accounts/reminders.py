"""Reading-plan reminders: an email a day, for readers who turn them on
(accounts/controls.py prefs), with the next day of the plan they are
reading. A plan waits for its reader (web/plans.js), so the email names the
first day not marked done, whatever the date: a day missed is offered again,
not skipped. Nothing is sent to a reader with no plan under way, or whose
plan is finished.

The plans are data/plans.json and the reader's own (ReaderState.custom_plans);
progress is what their devices synced (ReaderState.plans).
"""
import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings

from .controls import local_now, unsubscribe_url
from .models import EmailPrefs, ReaderState

DATA = Path(__file__).resolve().parents[2] / "data"


@lru_cache(maxsize=1)
def built_in_plans():
    return {p["id"]: p for p in json.loads((DATA / "plans.json").read_text(encoding="utf-8"))["plans"]}


@lru_cache(maxsize=1)
def book_names():
    return json.loads((DATA / "books.json").read_text(encoding="utf-8"))["books"]


def chapter_name(ref, lang):
    book, chapter = ref.split(".")
    names = book_names().get(book, {})
    return f"{names.get(lang) or names.get('en') or book} {chapter}"


def chapter_url(ref, lang):
    book, chapter = ref.split(".")
    prefix = "" if lang == "en" else f"/{lang}"
    return f"{settings.OWB_SITE_URL}{prefix}/{book.lower()}/{chapter}/"


def todays_reading(state, lang="en"):
    """(plan name, day number, total days, [chapter refs]) for the reader's
    current plan's first day not done, or None."""
    plans = (state.plans or {}) if state else {}
    pid = plans.get("active")
    progress = (plans.get("plans") or {}).get(pid) if pid else None
    if not progress:
        return None
    plan = built_in_plans().get(pid)
    if plan:
        name = plan["name"].get(lang) or plan["name"]["en"]
    else:
        plan = (state.custom_plans or {}).get(pid)
        if not plan or not plan.get("days"):
            return None
        name = plan["name"]
    done = set(progress.get("done") or [])
    for n, day in enumerate(plan["days"], 1):
        if n not in done:
            return name, n, len(plan["days"]), day
    return None


SUBJECT = "Today’s reading: {refs}"
BODY = """Day {day} of {total} in {plan}: {refs}

{links}

When you have read it, mark the day done at the end of the chapter, and the next email
will have the next day. If you miss a day, the plan waits for you.

--
You get this because you turned on reading-plan emails on Open Word Bible.
Change the time or stop them: {account}
Stop them now: {unsubscribe}
"""


def reminder(user, prefs, state):
    """(subject, body, headers) for the reader's next day, or None."""
    lang = prefs.language
    today = todays_reading(state, lang)
    if today is None:
        return None
    plan, day, total, refs = today
    names = ", ".join(chapter_name(r, lang) for r in refs)
    links = "\n".join(f"{chapter_name(r, lang)}: {chapter_url(r, lang)}" for r in refs)
    prefix = "" if lang == "en" else f"/{lang}"
    unsubscribe = unsubscribe_url(user)
    body = BODY.format(day=day, total=total, plan=plan, refs=names, links=links,
                       account=f"{settings.OWB_SITE_URL}{prefix}/account/#email", unsubscribe=unsubscribe)
    headers = {"List-Unsubscribe": f"<{unsubscribe}>", "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"}
    return SUBJECT.format(refs=names), body, headers


def due(now=None):
    """(user, prefs, state, their date) for each reader whose reminder hour
    has come on their own day, and who has not had that day's email."""
    for prefs in EmailPrefs.objects.filter(plan_reminders=True, user__is_active=True).select_related("user"):
        local = local_now(prefs, now)
        if local.hour < prefs.reminder_hour or prefs.last_reminder == local.date():
            continue
        yield prefs.user, prefs, ReaderState.objects.filter(user=prefs.user).first(), local.date()
