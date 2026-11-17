"""History in the admin: what has changed in a sentence since a reviewer
approved it, and what changed in a language over a stretch of deploys.

GET /api/admin/history/verse/<JHN.1.1>/
        for each sentence holding the verse, the latest approval in each
        layer and what has changed since, level by level, as a word diff
        (the verse inspector)
GET /api/admin/history/approvals/?before=<id>
        the latest approvals, newest first, each with what has changed in
        the sentence since (the activity log)
GET /api/admin/history/release-notes/?lang=en&since=2026-10-01&until=&file=md
        what changed in one language between two dates: sentences drafted
        in it, renderings changed (with word diffs), decisions added,
        changed or removed, and footnotes added, by book. file=md answers
        with a Markdown file to download.

A word diff is a list of segments, {"op": "same" | "ins" | "del", "text"},
made here (difflib on words), so the admin only has to draw them. A setting
span ({{setting:default|alt}}) and a verse marker (\\v 12) count as one word.

What was approved comes from the approval's snapshot (staff/snapshot.py).
An approval made before snapshots were kept has only a digest; for wording,
its text is then worked out from the imports since (SentenceChange keeps
each rendering's text before an import changed it), and marked
"reconstructed". The release notes come from what import_content records
(SentenceChange, RecordChange, ImportRun.drafted); nothing here changes a
sentence or its review status.
"""
import datetime
import difflib
import re

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from owb import languages, refs
from translation.models import ImportRun, RecordChange, Rendering, ReviewEvent, Sentence, SentenceChange

from .inbox import verse_label
from .permissions import admin_view
from .review import A, digest, layer_json
from .snapshot import snapshot

LEVELS = ("L", "B", "R")
LEVEL_NAMES = {"L": "Literal", "B": "Balanced", "R": "Readable"}
ORDER = {code: i for i, code in enumerate(refs.BOOK_CODES)}
APPROVALS = (A.MEANING_REVIEWED, A.REVIEWED)
PAGE = 50
# Listed in full in the Markdown; in the page, up to this many per book and kind.
SHOWN = 200

WORD = re.compile(r"\{\{[^{}]*\}\}|\\v \d+|\\q|\s+|[^\s{\\]+|.", re.S)
SETTING = re.compile(r"\{\{[a-z_]+:([^{}|]*)\|[^{}]*\}\}")


def words(text):
    """text as words and the spaces between them; a setting span or verse
    marker is one word."""
    return WORD.findall(text or "")


def word_diff(before, after):
    """[{"op": "same" | "del" | "ins", "text"}] turning before into after,
    word by word, with neighbouring segments of one kind joined."""
    a, b = words(before), words(after)
    out = []

    def put(op, items):
        text = "".join(items)
        if not text:
            return
        if out and out[-1]["op"] == op:
            out[-1]["text"] += text
        else:
            out.append({"op": op, "text": text})

    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            put("same", a[i1:i2])
        else:
            put("del", a[i1:i2])
            put("ins", b[j1:j2])
    return out


def _sort_key(record_id):
    book, chapter, verse, number = record_id.split(".")
    return ORDER.get(book, 99), int(chapter), int(verse), int(number.lstrip("s") or 0)


# ---- What changed since an approval ---------------------------------------

def _layer_of(event):
    return event.language or event.sentence.source_edition.language


def _approved_texts(event, sentence, current):
    """({part: text} as approved, how it is known: "snapshot",
    "reconstructed", "unchanged" or "unknown"). current is the same parts
    now: {"gloss": ...} for a meaning layer, {level: text} for wording."""
    layer = _layer_of(event)
    if event.digest and event.digest == digest(sentence, layer):
        return dict(current), "unchanged"
    snap = event.snapshot or {}
    if layer in languages.ORIGINAL:
        if "literal_gloss" in snap:
            return {"gloss": snap["literal_gloss"]}, "snapshot"
        return {}, "unknown"
    if "renderings" in snap:
        return dict(snap["renderings"]), "snapshot"
    # Before snapshots: each level as the first import after the approval
    # found it, or as it is now if no import has changed it since.
    approved = dict(current)
    seen = set()
    for c in (SentenceChange.objects.filter(record_id=sentence.record_id, language=event.language,
                                            run__started_at__gte=event.created_at).order_by("id")):
        if c.level in seen:
            continue
        seen.add(c.level)
        if c.kind == SentenceChange.Kind.ADDED:
            approved.pop(c.level, None)
        else:
            approved[c.level] = c.before
    return approved, "reconstructed"


def _decision_changes(old, new):
    """{"added": [keys], "changed": [keys], "removed": [keys]} between two
    {key: decision} maps."""
    return {"added": sorted(new.keys() - old.keys()), "removed": sorted(old.keys() - new.keys()),
            "changed": sorted(k for k in old.keys() & new.keys() if old[k] != new[k])}


def since_approval(event, sentence):
    """What has changed in sentence (renderings and decisions prefetched)
    since event, an approval: each level's text then and now with a word
    diff (the literal gloss, for a meaning layer), and the decisions added,
    changed or removed when the approval kept a snapshot."""
    layer = _layer_of(event)
    meaning = layer in languages.ORIGINAL
    now = snapshot(sentence, layer)
    current = {"gloss": now["literal_gloss"]} if meaning else now["renderings"]
    approved, known = _approved_texts(event, sentence, current)
    parts = ["gloss"] if meaning else [lv for lv in LEVELS if lv in approved or lv in current]
    texts = []
    if known != "unknown":
        for part in parts:
            before, after = approved.get(part, ""), current.get(part, "")
            texts.append({"level": part, "name": "Literal gloss" if part == "gloss" else LEVEL_NAMES[part],
                          "before": before, "after": after, "changed": before != after,
                          "segments": word_diff(before, after) if before != after else []})
    decisions = None
    if known == "unchanged":
        decisions = {"added": [], "changed": [], "removed": []}
    elif "decisions" in (event.snapshot or {}):
        decisions = _decision_changes(event.snapshot["decisions"], now["decisions"])
    return {
        "id": event.id, "record": sentence.record_id, "verse": sentence.refs[0], "label": verse_label(sentence.refs[0]),
        "layer": layer_json(layer), "action": event.action, "label_action": event.get_action_display(),
        "by": event.user.get_full_name() or event.user.username, "note": event.note, "at": event.created_at,
        "changed": known != "unchanged", "known": known, "texts": texts, "decisions": decisions,
    }


def _latest_approvals(events):
    """The latest approval in each layer, per sentence, among events."""
    latest = {}
    for e in events.filter(action__in=APPROVALS).order_by("-created_at", "-id"):
        latest.setdefault((e.sentence_id, e.language), e)
    return latest


@admin_view("overview")
def verse(request, vid):
    try:
        ref = refs.parse(vid.upper())
    except ValueError:
        raise NotFound(f"Not a verse: {vid!r}")
    vid = f"{ref.book}.{ref.chapter}.{ref.verse}"
    sentences = list(Sentence.objects.filter(book=ref.book, chapter__in=[ref.chapter - 1, ref.chapter],
                                             refs__contains=[vid]).select_related("source_edition")
                     .prefetch_related("renderings", "decisions").order_by("chapter", "verse", "number"))
    latest = _latest_approvals(ReviewEvent.objects.filter(sentence__in=sentences)
                               .select_related("user", "sentence__source_edition"))
    out = []
    for s in sentences:
        approvals = [since_approval(e, s) for (sid, _), e in latest.items() if sid == s.id]
        approvals.sort(key=lambda a: (a["layer"]["kind"] != "meaning", a["layer"]["code"]))
        out.append({"record": s.record_id, "approvals": approvals})
    return Response({"verse": vid, "label": verse_label(vid), "sentences": out})


@admin_view("team")
def approvals(request):
    events = (ReviewEvent.objects.filter(action__in=APPROVALS)
              .select_related("user", "sentence__source_edition").order_by("-id"))
    before = request.query_params.get("before")
    if before and before.isdigit():
        events = events.filter(id__lt=int(before))
    page = list(events[:PAGE + 1])
    sentences = {s.id: s for s in Sentence.objects.filter(id__in={e.sentence_id for e in page})
                 .select_related("source_edition").prefetch_related("renderings", "decisions")}
    return Response({"approvals": [since_approval(e, sentences[e.sentence_id]) for e in page[:PAGE]],
                     "more": len(page) > PAGE})


# ---- Release notes -----------------------------------------------------------

def _date(value, name):
    try:
        day = datetime.date.fromisoformat(str(value))
    except ValueError:
        raise ValidationError({name: "Give a date as YYYY-MM-DD.", "code": "invalid_date"})
    return timezone.make_aware(datetime.datetime.combine(day, datetime.time.min))


def _collapse(rows, key):
    """The first "before" and last "after" of rows (in order) for each key."""
    out = {}
    for r in rows:
        k = key(r)
        if k in out:
            out[k]["after"] = r.after
        else:
            out[k] = {"row": r, "before": r.before, "after": r.after}
    return out


def _verse_ranges(verses):
    """[(chapter, verse)] as "3:1-18, 20; 4:2"."""
    by_chapter = {}
    for c, v in sorted(set(verses)):
        by_chapter.setdefault(c, []).append(v)
    parts = []
    for c, vs in by_chapter.items():
        runs, start = [], vs[0]
        for prev, v in zip(vs, vs[1:] + [None]):
            if v is None or v != prev + 1:
                runs.append(f"{start}" if start == prev else f"{start}–{prev}")
                start = v
        parts.append(f"{c}:{', '.join(runs)}")
    return "; ".join(parts)


def release_notes(lang, since, until):
    """What changed in lang from since to until (aware datetimes), by book."""
    runs = ImportRun.objects.filter(started_at__gte=since, started_at__lt=until)
    drafted_counts = {}
    for counts in runs.values_list("drafted", flat=True):
        for book, by_lang in counts.items():
            if by_lang.get(lang):
                drafted_counts[book] = drafted_counts.get(book, 0) + by_lang[lang]
    books = {}

    def book(code):
        return books.setdefault(code, {"code": code, "name": refs.BOOK_NAMES.get(code, code), "drafted": 0,
                                       "added": [], "renderings": [], "decisions": [], "footnotes": []})

    for code, n in drafted_counts.items():
        book(code)["drafted"] = n
    new = {}
    for r in (RecordChange.objects.filter(run__in=runs, language=lang, kind=RecordChange.Kind.DRAFTED)
              .order_by("id")):
        new.setdefault(r.record_id, r)
    for rid in sorted(new, key=_sort_key):
        r = new[rid]
        book(r.book)["added"].append({"record": rid, "verse": r.verse, "label": verse_label(r.verse)})

    rendered = _collapse(SentenceChange.objects.filter(run__in=runs, language=lang).order_by("id"),
                         lambda c: (c.record_id, c.level))
    for (rid, level), c in sorted(rendered.items(), key=lambda kv: (_sort_key(kv[0][0]), LEVELS.index(kv[0][1]))):
        if rid in new or c["before"] == c["after"]:
            continue
        kind = "added" if not c["before"] else "removed" if not c["after"] else "changed"
        row = c["row"]
        book(row.book)["renderings"].append({
            "record": rid, "verse": row.verse, "label": verse_label(row.verse), "level": level,
            "name": LEVEL_NAMES[level], "kind": kind, "before": c["before"], "after": c["after"],
            "segments": word_diff(c["before"], c["after"])})

    # Meaning decisions count in the sentences drafted in lang.
    drafted_here = set(Rendering.objects.filter(language=lang).values_list("sentence__record_id", flat=True))
    decided = _collapse(RecordChange.objects.filter(run__in=runs).filter(Q(language=lang) | Q(language=""))
                        .exclude(kind=RecordChange.Kind.DRAFTED).order_by("id"),
                        lambda r: (r.record_id, r.key))
    for (rid, key), d in sorted(decided.items(), key=lambda kv: (_sort_key(kv[0][0]), kv[0][1])):
        row = d["row"]
        old, now = d["before"] or {}, d["after"] or {}
        if rid in new or old == now or (not row.language and rid not in drafted_here):
            continue
        kind = "added" if not old else "removed" if not now else "changed"
        item = {"record": rid, "verse": row.verse, "label": verse_label(row.verse), "key": key,
                "layer": "rendering" if row.language else "meaning", "kind": kind,
                "choice": (now or old).get("choice", ""), "was": old.get("choice", "") if kind == "changed" else "",
                "reason": (now or old).get("reason", ""), "category": (now or old).get("category", ""),
                "fields": sorted(f for f in set(old) | set(now) if old.get(f) != now.get(f))
                if kind == "changed" else []}
        book(row.book)["decisions"].append(item)
        if now.get("footnote") and not old.get("footnote"):
            book(row.book)["footnotes"].append(item)

    ordered = sorted(books.values(), key=lambda b: ORDER.get(b["code"], 99))
    for b in ordered:
        b["added_verses"] = _verse_ranges([(int(a["verse"].split(".")[1]), int(a["verse"].split(".")[2]))
                                           for a in b["added"]])
        b["counts"] = {k: len(b[k]) for k in ("added", "renderings", "decisions", "footnotes")}
    totals = {k: sum(b["counts"][k] for b in ordered) for k in ("added", "renderings", "decisions", "footnotes")}
    totals["drafted"] = sum(b["drafted"] for b in ordered)
    return {"language": {"code": lang, "name": languages.READING[lang]["name"]}, "since": since, "until": until,
            "imports": runs.count(), "totals": totals, "books": ordered}


def _md_escape(text):
    return re.sub(r"([\\`*_~\[\]<>#|])", r"\\\1", text)


def _md_plain(text):
    """A rendering's text as a reader sees it at the default settings."""
    text = SETTING.sub(lambda m: m[1], text or "")
    return re.sub(r"\\v \d+ ?", "", text).replace("\\q", " / ")


def _md_diff(segments):
    out = []
    for s in segments:
        text = _md_escape(_md_plain(s["text"]))
        if s["op"] == "same" or not text.strip():
            out.append(text)
        else:
            lead, core, trail = re.match(r"(\s*)(.*?)(\s*)$", text, re.S).groups()
            mark = "~~" if s["op"] == "del" else "**"
            out.append(f"{lead}{mark}{core}{mark}{trail}")
    return "".join(out)


def markdown(notes):
    lang = notes["language"]["name"]
    since = notes["since"].date().isoformat()
    until = notes["through"]
    t = notes["totals"]
    lines = [f"# Open Word Bible: what changed in {lang}", "",
             f"From {since} to {until}, over {notes['imports']} import(s) of the translation: "
             f"{t['drafted']} sentence(s) drafted, {t['renderings']} rendering(s) changed, "
             f"{t['decisions']} decision(s) added or changed, {t['footnotes']} footnote(s) added.", "",
             "Every sentence is an AI-assisted draft until a named reviewer approves it. "
             "Changes are shown at the default reading settings: ~~removed~~, **added**.", ""]
    if not notes["books"]:
        lines.append("Nothing changed in this language in that time.")
    for b in notes["books"]:
        lines += [f"## {b['name']}", ""]
        if b["drafted"] or b["added"]:
            lines.append(f"**Sentences drafted:** {b['drafted'] or len(b['added'])}"
                         + (f" ({b['name']} {b['added_verses']})" if b["added_verses"] else ""))
            lines.append("")
        if b["renderings"]:
            lines += ["### Renderings changed", ""]
            for r in b["renderings"]:
                text = (_md_diff(r["segments"]) if r["kind"] == "changed"
                        else f"**{_md_escape(_md_plain(r['after']))}**" if r["kind"] == "added"
                        else f"~~{_md_escape(_md_plain(r['before']))}~~")
                lines.append(f"- **{r['label']}** ({r['name']}, {r['kind']}): {text}")
            lines.append("")
        if b["decisions"]:
            lines += ["### Decisions", ""]
            for d in b["decisions"]:
                was = f" (was: {_md_escape(d['was'])})" if d["was"] and d["was"] != d["choice"] else ""
                lines.append(f"- **{d['label']}** `{d['key']}` {d['layer']} decision {d['kind']}: "
                             f"{_md_escape(d['choice'])}{was}")
            lines.append("")
        if b["footnotes"]:
            lines += ["### Footnotes added", ""]
            for d in b["footnotes"]:
                lines.append(f"- **{d['label']}** `{d['key']}`: {_md_escape(d['choice'])}: {_md_escape(d['reason'])}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


@admin_view("export")
def notes(request):
    lang = request.query_params.get("lang") or "en"
    if lang not in languages.READING:
        raise ValidationError({"lang": "Choose a reading language.", "code": "invalid_language"})
    if not request.query_params.get("since"):
        raise ValidationError({"since": "Give the date to start from.", "code": "invalid_date"})
    since = _date(request.query_params["since"], "since")
    until = (_date(request.query_params["until"], "until") + datetime.timedelta(days=1)
             if request.query_params.get("until") else timezone.now())
    found = {**release_notes(lang, since, until),
             "through": request.query_params.get("until") or timezone.localdate().isoformat()}
    if request.query_params.get("file") == "md":
        response = HttpResponse(markdown(found), content_type="text/markdown; charset=utf-8")
        response["Content-Disposition"] = (f'attachment; filename="open-word-bible-{lang}-changes-'
                                           f'{since.date().isoformat()}.md"')
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response
    for b in found["books"]:
        for k in ("added", "renderings", "decisions", "footnotes"):
            b[k] = b[k][:SHOWN]
    return Response({**found, "shown": SHOWN,
                     "languages": [{"code": c, "name": x["name"]} for c, x in languages.READING.items()]})
