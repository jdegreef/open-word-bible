"""Content checks: footnotes whose verse words something else, and verses
and glossary rows at odds with a language's terms glossary
(owb/content_checks.py says what each flags; scripts/content_checks.py
prints the same lists).

GET /api/admin/checks/?lang=id
        {language, languages: [{code, name, glossary}],
         notes: {total, kinds, hits: [...]},
         glossary: {file, verses: {total, kinds, hits}, rows: [...]}}

The sentences, renderings and decisions come from the database; the
translated notes (data/notes/<lang>/) and the glossary
(docs/<language>-terms.md) from the files the deploy carries, as the site
reads them. These are heuristics for a person to look at, not rules: nothing
here fails a build or changes a record.

Measuring a language takes 10-15 seconds on the whole Bible, so each answer
is kept, under a stamp of what it was measured from (the sentences, the
language's notes and its glossary): in the cache, and in a ChecksAnswer row,
which outlives the cache being emptied. The import job measures every
language after an import (precompute_checks), so the page opens on a kept
answer; only when the content has changed since (a review, say) does a
request measure again, as before, and keep what it found.
"""
import hashlib
import time

from django.core.cache import cache
from django.db.models import Count, Max
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from owb import content_checks as cc
from owb import languages, notes, refs
from translation.models import Decision, Rendering, Sentence

from .inbox import verse_label
from .models import ChecksAnswer
from .permissions import admin_view

LEVELS = ("L", "B", "R")


def _stamp():
    s = Sentence.objects.aggregate(n=Count("id"), t=Max("updated_at"))
    return "{}.{}".format(s["n"], s["t"].timestamp() if s["t"] else 0)


# Each file's digest, by where it is and its size and modification time, so
# a request reads a file again only once it has changed.
_digests = {}


def _file_digest(path):
    st = path.stat()
    key = (str(path), st.st_size, st.st_mtime_ns)
    digest = _digests.get(key)
    if digest is None:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        _digests[key] = digest
    return digest


def _files_stamp(lang):
    """A digest of the language's note files and glossary by what they hold.

    By content, not modification time: the import job (warm_admin) and the
    API each have their own checkout, with their own file times, and the
    answer the job keeps must be the one the API looks for."""
    h = hashlib.sha256()
    folder = notes.NOTES / lang
    paths = sorted(folder.glob("*.json")) if folder.is_dir() else []
    glossary = cc.glossary_path(languages.READING[lang]["name"])
    if glossary.is_file():
        paths.append(glossary)
    for path in paths:
        h.update(f"{path.name}:{_file_digest(path)};".encode())
    return h.hexdigest()[:16]


def _notes(lang):
    return cc.load_notes(lang)


def _glossary(lang):
    return cc.load_glossary(languages.READING[lang]["name"])


def records(lang):
    """The database's sentences as owb.content_checks reads records: id,
    refs, renderings in lang and English, footnoted meaning decisions."""
    order = {code: i for i, code in enumerate(refs.BOOK_CODES)}
    rows = sorted(Sentence.objects.values_list("id", "record_id", "refs", "book", "chapter", "verse", "number"),
                  key=lambda r: (order.get(r[3], 99), r[4], r[5], r[6]))
    out, by_id = [], {}
    for sid, record_id, verse_ids, *_ in rows:
        r = {"id": record_id, "refs": verse_ids, "renderings": {}, "decisions": []}
        out.append(r)
        by_id[sid] = r
    for sid, language, level, text in (Rendering.objects.filter(language__in={lang, "en"})
                                       .values_list("sentence_id", "language", "level", "text")):
        if sid in by_id:
            by_id[sid]["renderings"].setdefault(language, {})[level] = text
    for sid, key, category, choice, alternatives, reason in (
            Decision.objects.filter(layer="meaning", footnote=True, category__in=cc.CATEGORIES)
            .order_by("sentence_id", "order")
            .values_list("sentence_id", "key", "category", "choice", "alternatives", "reason")):
        if sid in by_id:
            by_id[sid]["decisions"].append({"id": key, "layer": "meaning", "footnote": True, "category": category,
                                            "choice": choice, "alternatives": list(alternatives), "reason": reason})
    return out


def _labelled(hits):
    for h in hits:
        h["label"] = verse_label(h["verse"])
    return hits


def _kinds(hits):
    out = {}
    for h in hits:
        out[h["kind"]] = out.get(h["kind"], 0) + 1
    return out


def _english_stop(recs):
    key = f"staff.checks.en-stop.{_stamp()}"
    stop = cache.get(key)
    if stop is None:
        stop = cc.language_function_words(recs, "en")
        cache.set(key, stop, 86400)
    return stop


def measure(lang):
    recs = records(lang)
    en_stop = _english_stop(recs)
    translated = None if lang == "en" else _notes(lang)
    note_hits = cc.note_mismatches(recs, lang, translated, stop=en_stop if lang == "en" else None, en_stop=en_stop)
    # The strongest first: an alternative against the English, then against
    # another level, then a missing choice; Bible order within each.
    rank = {("alternative", "english"): 0, ("alternative", "level"): 1}
    note_hits.sort(key=lambda h: rank.get((h["kind"], h.get("contrast")), 2))
    rows = [] if lang == "en" else _glossary(lang)
    verse_hits = cc.glossary_hits(rows, recs, lang) if rows else []
    name = languages.READING[lang]["name"]
    cc.flatten.cache_clear()  # a worker lives on: don't keep every verse's text
    return {
        "notes": {"total": len(note_hits), "kinds": _kinds(note_hits), "hits": _labelled(note_hits)},
        "glossary": {
            "file": f"docs/{name.lower()}-terms.md" if rows else None,
            "verses": {"total": len(verse_hits), "kinds": _kinds(verse_hits), "hits": _labelled(verse_hits)},
            "rows": cc.glossary_conflicts(rows),
        },
    }


def content_stamp(lang):
    """What lang's answer is measured from: the sentences, and its note and
    glossary files by what they hold."""
    return f"{_stamp()}.{_files_stamp(lang)}"


def store(lang, stamp, answer, seconds=0.0):
    ChecksAnswer.objects.update_or_create(language=lang,
                                          defaults={"stamp": stamp, "answer": answer, "seconds": seconds})
    cache.set(f"staff.checks.{lang}.{stamp}", answer, 86400)


def precompute(lang, force=False):
    """Measure lang and keep the answer, unless the one kept is for the
    content as it is (and not force). Returns the seconds measuring took,
    or None if the kept answer was current."""
    stamp = content_stamp(lang)
    if not force and ChecksAnswer.objects.filter(language=lang, stamp=stamp).exists():
        return None
    start = time.perf_counter()
    answer = measure(lang)
    took = time.perf_counter() - start
    store(lang, stamp, answer, took)
    return took


def kept_answer(lang):
    """lang's answer for the content as it is: from the cache, else the
    ChecksAnswer row, else measured now (and kept in both)."""
    stamp = content_stamp(lang)
    key = f"staff.checks.{lang}.{stamp}"
    answer = cache.get(key)
    if answer is not None:
        return answer
    row = ChecksAnswer.objects.filter(language=lang, stamp=stamp).values_list("answer", flat=True).first()
    if row is not None:
        cache.set(key, row, 86400)
        return row
    start = time.perf_counter()
    answer = measure(lang)
    store(lang, stamp, answer, time.perf_counter() - start)
    return answer


@admin_view("overview")
def checks(request):
    lang = request.query_params.get("lang", "en")
    if lang not in languages.READING:
        raise ValidationError({"lang": "Choose a reading language."})
    answer = kept_answer(lang)
    return Response({**answer, "language": lang,
                     "languages": [{"code": c, "name": entry["name"],
                                    "glossary": cc.glossary_path(entry["name"]).is_file()}
                                   for c, entry in languages.READING.items()]})
