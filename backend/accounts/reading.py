"""A reader's bookmarks, highlights, reading place, reading-plan progress and
reader settings, synced between their devices.

The browser keeps them (web/reader.js: owb.marks and owb.place) and, when
the reader is signed in, sends its whole copy (web/site.js). merge() keeps
the latest change to each verse, by the device's clock, and the answer is the
merged whole, which the browser takes in the same way. Sending the same copy
twice changes nothing, so a device can sync whenever it likes.

    marks: {"JHN.3.16": {"b": true, "h": "yellow", "n": "...", "text": "...", "lang": "en",
                         "at": 1791760739987}}
    place: {"book": "JHN", "chapter": 3, "verse": "16", "at": 1791760739987}
    plans: {"active": "mark", "at": 1791760739987,
            "plans": {"mark": {"start": "2026-10-12", "done": [1, 2], "at": 1791760739987}}}
    settings: {"v": {"level": "L", "gender": 1, ...}, "at": 1791760739987}
    notes: {"JHN.3.16-21": {"n": "...", "text": "...", "lang": "en", "t": ["Prayer"], "at": ...}}
    words: {"<lemma>": {"s": true, "n": "...", "g": "love", "l": "grc", "at": ...}}
    myplans: {"my-k3x9q2": {"name": "Advent", "days": [["LUK.1", "LUK.2"], ...], "at": ...}}

t on a mark or a passage note is the reader's collections it is in (web/
site.js, the saved verses page). A passage note is a note on several
verses of one chapter (owb.notes); a word is a Greek, Hebrew or Aramaic
dictionary form in the reader's word list (owb.words): saved (s) or with
the reader's note (n); the history of lookups stays in the browser. A
myplan is a reading plan the reader made (owb.myplans, web/plans.js), in
the shape of data/plans.json. Each of them merges like a mark, the latest
change winning whole, and a cleared one is kept as {at}.

Plans merge like marks, each plan by its own time and the active plan by
"at"; settings are taken whole, the later copy winning. The settings are the
reader's own choices, checked only for shape: web/reader.js reads the names
it knows and ignores the rest.

n is the reader's own note on the verse. A mark with none of b, h and n is a
cleared one, kept so the clearing reaches the other devices.
"""
import re
import time

from django.contrib.auth import get_user_model
from django.db import transaction

from owb import languages

from .models import Mark, PassageNote, ReaderState, ReadingPlace, SavedWord

MAX_MARKS = 10000
MAX_TEXT = 2000
MAX_NOTE = 5000
LANGS = set(languages.CODES)  # the site's languages (data/languages.json)
VERSE_ID = re.compile(r"^[1-4A-Z]{3}\.\d{1,3}\.\d{1,3}$")
PLACE_VERSE = re.compile(r"^\d{1,3}(:\d{1,3})?$")
BOOK = re.compile(r"^[1-4A-Z]{3}$")
DAY_MS = 86_400_000
MAX_PLANS = 200
MAX_DAYS = 400
PLAN_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,59}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_SETTINGS = 40
SETTING_NAME = re.compile(r"^[a-z][a-z_]{0,31}$")
SETTING_TEXT = re.compile(r"^[A-Za-z0-9_.-]{0,32}$")
MAX_TAGS = 20
MAX_TAG = 40
PASSAGE = re.compile(r"^([1-4A-Z]{3})\.(\d{1,3})\.(\d{1,3})-(\d{1,3})$")
MAX_NOTES = 5000
MAX_WORDS = 5000
MAX_LEMMA = 64
WORD_LANGS = {"grc", "hbo", "arc"}
MAX_GLOSS = 120
MAX_MYPLANS = 100
MYPLAN_ID = re.compile(r"^my-[a-z0-9]{4,20}$")
MAX_PLAN_NAME = 80
MAX_DAY_CHAPTERS = 30
CHAPTER = re.compile(r"^[1-4A-Z]{3}\.\d{1,3}$")


class Invalid(Exception):
    pass


def _when(value):
    """A device's time in milliseconds; one set in the future (a wrong
    clock) counts as now, so it cannot win every later change."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise Invalid("Each change needs its time, in milliseconds.")
    now = int(time.time() * 1000)
    return min(value, now) if value > now + DAY_MS else value


def _tags(data, where):
    """A mark's or note's collections: distinct names, in the order given."""
    tags = data.get("t") or []
    if not isinstance(tags, list) or len(tags) > MAX_TAGS:
        raise Invalid(f"Up to {MAX_TAGS} collections each: {where}")
    out = []
    for tag in tags:
        if not isinstance(tag, str):
            raise Invalid(f"A collection is a name: {where}")
        tag = " ".join(tag.split())[:MAX_TAG]
        if tag and tag.casefold() not in (o.casefold() for o in out):
            out.append(tag)
    return out


def _mark(verse, data):
    if not VERSE_ID.match(verse) or not isinstance(data, dict):
        raise Invalid(f"Not a verse mark: {verse}")
    hue = data.get("h") or ""
    if hue and hue not in Mark.HUES:
        raise Invalid(f"Not a highlight colour: {hue}")
    lang = data.get("lang") or ""
    text = data.get("text") or ""
    note = data.get("n") or ""
    if not isinstance(note, str):
        raise Invalid(f"A note is text: {verse}")
    return Mark(verse=verse, bookmark=data.get("b") is True, highlight=hue, note=note[:MAX_NOTE],
                text=str(text)[:MAX_TEXT], lang=lang if lang in LANGS else "", tags=_tags(data, verse),
                updated_at=_when(data.get("at")))


def mark_json(m):
    out = {"at": m.updated_at}
    if m.bookmark:
        out["b"] = True
    if m.highlight:
        out["h"] = m.highlight
    if m.note:
        out["n"] = m.note
    if m.tags:
        out["t"] = m.tags
    if m.bookmark or m.highlight or m.note or m.tags:
        out["text"] = m.text
        out["lang"] = m.lang
    return out


def _passage_note(passage, data):
    match = PASSAGE.match(passage)
    if not match or not isinstance(data, dict) or not 0 < int(match[3]) < int(match[4]):
        raise Invalid(f"Not a passage note: {passage}")
    note = data.get("n") or ""
    if not isinstance(note, str):
        raise Invalid(f"A note is text: {passage}")
    lang = data.get("lang") or ""
    return PassageNote(passage=passage, note=note[:MAX_NOTE], text=str(data.get("text") or "")[:MAX_TEXT * 4],
                       lang=lang if lang in LANGS else "", tags=_tags(data, passage) if note else [],
                       updated_at=_when(data.get("at")))


def passage_note_json(p):
    out = {"at": p.updated_at}
    if p.note:
        out.update(n=p.note, text=p.text, lang=p.lang)
        if p.tags:
            out["t"] = p.tags
    return out


def _is_lemma(lemma):
    """A dictionary form as the source data spells it: Greek or Hebrew
    letters with their marks, no control characters."""
    return (isinstance(lemma, str) and 0 < len(lemma) <= MAX_LEMMA and lemma == lemma.strip()
            and all(c.isprintable() for c in lemma)
            and any("\u0370" <= c <= "\u03ff" or "\u1f00" <= c <= "\u1fff" or "\u0590" <= c <= "\u05ff"
                    or "\ufb1d" <= c <= "\ufb4f" for c in lemma))


def _word(lemma, data):
    if not _is_lemma(lemma) or not isinstance(data, dict):
        raise Invalid("Not a word in the list.")
    note = data.get("n") or ""
    if not isinstance(note, str):
        raise Invalid(f"Not a word in the list: {lemma}")
    language = data.get("l") or ""
    return SavedWord(lemma=lemma, saved=data.get("s") is True, note=note[:MAX_NOTE],
                     gloss=str(data.get("g") or "")[:MAX_GLOSS], language=language if language in WORD_LANGS else "",
                     updated_at=_when(data.get("at")))


def word_json(w):
    out = {"at": w.updated_at}
    if w.saved:
        out["s"] = True
    if w.note:
        out["n"] = w.note
    if w.saved or w.note:
        out.update(g=w.gloss, l=w.language)
    return out


def _myplans(data):
    """A device's owb.myplans: {id: {name, days, at}}, a deleted plan {at}."""
    if not isinstance(data, dict) or len(data) > MAX_MYPLANS:
        raise Invalid(f"Send up to {MAX_MYPLANS} plans of your own.")
    out = {}
    for pid, p in data.items():
        if not MYPLAN_ID.match(pid) or not isinstance(p, dict):
            raise Invalid(f"Not a plan of your own: {pid}")
        at = _when(p.get("at"))
        if "days" not in p:
            out[pid] = {"at": at}
            continue
        name, days = p.get("name"), p.get("days")
        if (not isinstance(name, str) or not name.strip() or not isinstance(days, list)
                or not 0 < len(days) <= MAX_DAYS
                or not all(isinstance(d, list) and 0 < len(d) <= MAX_DAY_CHAPTERS
                           and all(isinstance(c, str) and CHAPTER.match(c) for c in d) for d in days)):
            raise Invalid(f"Not a plan of your own: {pid}")
        out[pid] = {"name": " ".join(name.split())[:MAX_PLAN_NAME], "days": days, "at": at}
    return out


def _merge_myplans(have, theirs):
    plans = dict(have or {})
    for pid, p in theirs.items():
        if pid not in plans or p["at"] > plans[pid]["at"]:
            plans[pid] = p
    return plans


def _merge_rows(model, user, key, incoming, fields):
    """Keep the later of each row, by its updated_at; new rows are added."""
    have = {getattr(r, key): r for r in model.objects.filter(user=user)}
    new, changed = [], []
    for row in incoming:
        old = have.get(getattr(row, key))
        if old is None:
            row.user = user
            new.append(row)
        elif row.updated_at > old.updated_at:
            for field in fields:
                setattr(old, field, getattr(row, field))
            changed.append(old)
    model.objects.bulk_create(new)
    model.objects.bulk_update(changed, fields)


def _plans(data):
    """A device's owb.plans. A plan that is not one (a browser's stray copy)
    is left out rather than refusing the sync, and a plan or an active
    choice without its time is older than any with one."""
    if not isinstance(data, dict) or not isinstance(data.get("plans", {}), dict):
        raise Invalid("Not reading-plan progress.")
    plans = data.get("plans", {})
    if len(plans) > MAX_PLANS:
        raise Invalid(f"Send up to {MAX_PLANS} plans.")
    out = {}
    for pid, p in plans.items():
        if not PLAN_ID.match(pid) or not isinstance(p, dict) or not DATE.match(str(p.get("start", ""))):
            continue
        done = p.get("done")
        if (not isinstance(done, list) or len(done) > MAX_DAYS
                or not all(isinstance(d, int) and not isinstance(d, bool) and 0 < d <= MAX_DAYS for d in done)):
            continue
        out[pid] = {"start": p["start"], "done": sorted(set(done)), "at": _when(p.get("at", 0))}
    active = data.get("active")
    return {"active": active if active in out else None, "at": _when(data.get("at", 0)), "plans": out}


def _settings(data):
    """A device's owb.settings, as {v, at}; a value that is not a short word
    or a small number is left out."""
    if not isinstance(data, dict) or not isinstance(data.get("v"), dict) or len(data["v"]) > MAX_SETTINGS:
        raise Invalid("Send settings as {v, at}.")
    values = {name: value for name, value in data["v"].items()
              if name != "lang"  # the page's language, not a setting
              and SETTING_NAME.match(name)
              and (isinstance(value, int) and not isinstance(value, bool) and 0 <= value < 100
                   or isinstance(value, str) and SETTING_TEXT.match(value))}
    return values, _when(data.get("at"))


def state(user):
    place = ReadingPlace.objects.filter(user=user).first()
    reader = ReaderState.objects.filter(user=user).first()
    return {
        "marks": {m.verse: mark_json(m) for m in Mark.objects.filter(user=user)},
        "place": place and {"book": place.book, "chapter": place.chapter, "verse": place.verse,
                            "at": place.updated_at},
        "plans": reader.plans if reader and reader.plans else None,
        "settings": {"v": reader.prefs, "at": reader.prefs_at} if reader and reader.prefs_at else None,
        "notes": {p.passage: passage_note_json(p) for p in PassageNote.objects.filter(user=user)},
        "words": {w.lemma: word_json(w) for w in SavedWord.objects.filter(user=user)},
        "myplans": reader.custom_plans if reader and reader.custom_plans else {},
    }


def _merge_plans(have, theirs):
    if not have:
        return theirs
    plans = dict(have["plans"])
    for pid, p in theirs["plans"].items():
        if pid not in plans or p["at"] > plans[pid]["at"]:
            plans[pid] = p
    active, at = (theirs["active"], theirs["at"]) if theirs["at"] > have["at"] else (have["active"], have["at"])
    return {"active": active if active in plans else None, "at": at, "plans": plans}


def merge(user, data):
    """Take in a device's copy; raises Invalid for one the browser would not
    send, without saving any of it."""
    if not isinstance(data, dict):
        raise Invalid("Send {marks, place, plans, settings, notes, words, myplans}.")
    marks = data.get("marks") or {}
    if not isinstance(marks, dict) or len(marks) > MAX_MARKS:
        raise Invalid(f"Send up to {MAX_MARKS} marks.")
    incoming = [_mark(verse, m) for verse, m in marks.items()]
    notes = data.get("notes") or {}
    if not isinstance(notes, dict) or len(notes) > MAX_NOTES:
        raise Invalid(f"Send up to {MAX_NOTES} passage notes.")
    notes = [_passage_note(passage, n) for passage, n in notes.items()]
    words = data.get("words") or {}
    if not isinstance(words, dict) or len(words) > MAX_WORDS:
        raise Invalid(f"Send up to {MAX_WORDS} words.")
    words = [_word(lemma, w) for lemma, w in words.items()]
    myplans = data.get("myplans")
    if myplans is not None:
        myplans = _myplans(myplans)
    place = data.get("place")
    if place is not None:
        if (not isinstance(place, dict) or not BOOK.match(str(place.get("book", "")))
                or not isinstance(place.get("chapter"), int) or not 0 < place["chapter"] < 200
                or not PLACE_VERSE.match(str(place.get("verse", "")))):
            raise Invalid("Not a reading place.")
        place_at = _when(place.get("at", 0))
    plans = data.get("plans")
    if plans is not None:
        plans = _plans(plans)
    settings = data.get("settings")
    if settings is not None:
        settings = _settings(settings)
    with transaction.atomic():
        # One sync at a time per reader, so two devices cannot both create a
        # verse's row.
        get_user_model().objects.select_for_update().filter(pk=user.pk).first()
        _merge_rows(Mark, user, "verse", incoming,
                    ["bookmark", "highlight", "note", "text", "lang", "tags", "updated_at"])
        _merge_rows(PassageNote, user, "passage", notes, ["note", "text", "lang", "tags", "updated_at"])
        _merge_rows(SavedWord, user, "lemma", words,
                    ["saved", "note", "gloss", "language", "updated_at"])
        if place is not None:
            current = ReadingPlace.objects.filter(user=user).first()
            if current is None or place_at > current.updated_at:
                ReadingPlace.objects.update_or_create(user=user, defaults={
                    "book": place["book"], "chapter": place["chapter"], "verse": str(place["verse"]),
                    "updated_at": place_at})
        if plans is not None or settings is not None or myplans:
            reader, _ = ReaderState.objects.get_or_create(user=user)
            if plans is not None:
                reader.plans = _merge_plans(reader.plans, plans)
            if myplans:
                reader.custom_plans = _merge_myplans(reader.custom_plans, myplans)
            if settings is not None and settings[1] > reader.prefs_at:
                reader.prefs, reader.prefs_at = settings
            reader.save()
    return state(user)
