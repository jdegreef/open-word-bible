"""A reader's bookmarks, highlights and reading place, synced between their
devices.

The browser keeps them (web/reader.js: owb.marks and owb.place) and, when
the reader is signed in, sends its whole copy (web/site.js). merge() keeps
the latest change to each verse, by the device's clock, and the answer is the
merged whole, which the browser takes in the same way. Sending the same copy
twice changes nothing, so a device can sync whenever it likes.

    marks: {"JHN.3.16": {"b": true, "h": "yellow", "text": "...", "lang": "en", "at": 1791760739987}}
    place: {"book": "JHN", "chapter": 3, "verse": "16", "at": 1791760739987}

A mark with neither b nor h is a cleared one, kept so the clearing reaches
the other devices.
"""
import re
import time

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Mark, ReadingPlace

MAX_MARKS = 10000
MAX_TEXT = 2000
LANGS = {"en", "es", "fr", "sw"}
VERSE_ID = re.compile(r"^[1-4A-Z]{3}\.\d{1,3}\.\d{1,3}$")
PLACE_VERSE = re.compile(r"^\d{1,3}(:\d{1,3})?$")
BOOK = re.compile(r"^[1-4A-Z]{3}$")
DAY_MS = 86_400_000


class Invalid(Exception):
    pass


def _when(value):
    """A device's time in milliseconds; one set in the future (a wrong
    clock) counts as now, so it cannot win every later change."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Invalid("Each change needs its time, in milliseconds.")
    now = int(time.time() * 1000)
    return min(value, now) if value > now + DAY_MS else value


def _mark(verse, data):
    if not VERSE_ID.match(verse) or not isinstance(data, dict):
        raise Invalid(f"Not a verse mark: {verse}")
    hue = data.get("h") or ""
    if hue and hue not in Mark.HUES:
        raise Invalid(f"Not a highlight colour: {hue}")
    lang = data.get("lang") or ""
    text = data.get("text") or ""
    return Mark(verse=verse, bookmark=data.get("b") is True, highlight=hue,
                text=str(text)[:MAX_TEXT], lang=lang if lang in LANGS else "",
                updated_at=_when(data.get("at")))


def mark_json(m):
    out = {"at": m.updated_at}
    if m.bookmark:
        out["b"] = True
    if m.highlight:
        out["h"] = m.highlight
    if m.bookmark or m.highlight:
        out["text"] = m.text
        out["lang"] = m.lang
    return out


def state(user):
    place = ReadingPlace.objects.filter(user=user).first()
    return {
        "marks": {m.verse: mark_json(m) for m in Mark.objects.filter(user=user)},
        "place": place and {"book": place.book, "chapter": place.chapter, "verse": place.verse,
                            "at": place.updated_at},
    }


def merge(user, data):
    """Take in a device's copy; raises Invalid for one the browser would not
    send, without saving any of it."""
    if not isinstance(data, dict):
        raise Invalid("Send {marks, place}.")
    marks = data.get("marks") or {}
    if not isinstance(marks, dict) or len(marks) > MAX_MARKS:
        raise Invalid(f"Send up to {MAX_MARKS} marks.")
    incoming = [_mark(verse, m) for verse, m in marks.items()]
    place = data.get("place")
    if place is not None:
        if (not isinstance(place, dict) or not BOOK.match(str(place.get("book", "")))
                or not isinstance(place.get("chapter"), int) or not 0 < place["chapter"] < 200
                or not PLACE_VERSE.match(str(place.get("verse", "")))):
            raise Invalid("Not a reading place.")
        place_at = _when(place.get("at", 0))
    with transaction.atomic():
        # One sync at a time per reader, so two devices cannot both create a
        # verse's row.
        get_user_model().objects.select_for_update().filter(pk=user.pk).first()
        have = {m.verse: m for m in Mark.objects.filter(user=user)}
        new, changed = [], []
        for m in incoming:
            old = have.get(m.verse)
            if old is None:
                m.user = user
                new.append(m)
            elif m.updated_at > old.updated_at:
                for field in ("bookmark", "highlight", "text", "lang", "updated_at"):
                    setattr(old, field, getattr(m, field))
                changed.append(old)
        Mark.objects.bulk_create(new)
        Mark.objects.bulk_update(changed, ["bookmark", "highlight", "text", "lang", "updated_at"])
        if place is not None:
            current = ReadingPlace.objects.filter(user=user).first()
            if current is None or place_at > current.updated_at:
                ReadingPlace.objects.update_or_create(user=user, defaults={
                    "book": place["book"], "chapter": place["chapter"], "verse": str(place["verse"]),
                    "updated_at": place_at})
    return state(user)
