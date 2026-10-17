"""Review: people approving what the AI drafted, one sentence at a time.

GET  /api/admin/review/?layer=&book=&chapter=&state=&offset=
        the reviewer's queue for one layer, in Bible order, with each
        sentence's state and the counts by state
GET  /api/admin/review/<record_id>/?layer=
        one sentence for review: the record, its source words, its review
        trail, its state in the layer and the next sentence to review
POST /api/admin/review/<record_id>/  {layer, action, note}
        approve, flag (a note saying what is wrong) or comment
GET  /api/admin/review/flags/
        open flags in every layer, for editors to act on

A layer is the meaning of the sentences translated from one original
language ("grc", the New Testament; "hbo", the Old), which scholar reviewers
of that language approve, or the wording in one reading language ("en",
"fr", ...), which its language reviewers approve. Super admins may review
any layer. Every action is a ReviewEvent by the person who made it; Claude
never approves anything.

An approval keeps a digest of what was approved (the literal gloss and the
meaning decisions, or the language's renderings and rendering decisions). A
sentence whose digest has changed since, because an import changed it, is
"changed since approval" and goes back in the queue. A flag stays open until
the layer is approved again.

Approving the meaning moves a sentence from ai_draft to meaning_reviewed.
Wording approvals are kept per language and don't change the sentence's
status: when a sentence counts as "reviewed" is the charter's to decide.
"""
import hashlib
import json

from django.core.cache import cache
from django.db.models import Count, Max, Prefetch
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from accounts.models import Role
from api.views import record_json
from owb import languages, refs
from texts.models import Word
from translation.models import Decision, Rendering, ReviewEvent, Sentence, Status

from .inbox import verse_label
from .permissions import admin_view, is_super_admin

A = ReviewEvent.Action
PAGE = 50
ORDER = {code: i for i, code in enumerate(refs.BOOK_CODES)}
STATES = ("not_reviewed", "approved", "changed", "flagged")


def _meaning(layer):
    return layer in languages.ORIGINAL


def layer_json(code):
    if _meaning(code):
        name = languages.ORIGINAL[code]["name"]
        return {"code": code, "kind": "meaning", "name": f"Meaning ({name})",
                "books": "New Testament" if code == "grc" else "Old Testament"}
    return {"code": code, "kind": "wording", "name": f"{languages.READING[code]['name']} wording"}


def layers(user):
    """The layers user may review: originals first, then reading languages."""
    every = [*languages.ORIGINAL, *languages.READING]
    if is_super_admin(user):
        return every
    mine = set(user.roles.filter(kind__in=[Role.Kind.SCHOLAR_REVIEWER, Role.Kind.LANGUAGE_REVIEWER])
               .values_list("language", flat=True))
    return [code for code in every if code in mine]


def _scope(layer):
    """The sentences in a layer: translated from that original language, or
    drafted in that reading language."""
    if _meaning(layer):
        return Sentence.objects.filter(source_edition__language=layer)
    return Sentence.objects.filter(id__in=Rendering.objects.filter(language=layer).values("sentence_id"))


def _events(layer):
    if _meaning(layer):
        return ReviewEvent.objects.filter(language="", sentence__source_edition__language=layer)
    return ReviewEvent.objects.filter(language=layer)


def _approve(layer):
    return A.MEANING_REVIEWED if _meaning(layer) else A.REVIEWED


def _decision(d):
    return [d.key, d.category, d.levels, d.tokens, d.choice, d.alternatives, d.reason, d.uncertain, d.footnote]


def digest(sentence, layer):
    """What a reviewer of layer approves in sentence (renderings and
    decisions prefetched), as a hash."""
    if _meaning(layer):
        parts = [sentence.literal_gloss, [_decision(d) for d in sentence.decisions.all() if d.layer == "meaning"]]
    else:
        parts = [sorted((r.level, r.text) for r in sentence.renderings.all() if r.language == layer),
                 [_decision(d) for d in sentence.decisions.all()
                  if d.layer == "rendering" and d.language == layer]]
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()


def _with_texts(queryset, layer):
    if _meaning(layer):
        return queryset.prefetch_related(Prefetch("decisions", Decision.objects.filter(layer="meaning")))
    return queryset.prefetch_related(Prefetch("renderings", Rendering.objects.filter(language=layer)),
                                     Prefetch("decisions", Decision.objects.filter(language=layer)))


def _latest(events):
    """{sentence id: its latest approval or flag} among events."""
    return {e.sentence_id: e for e in events.filter(action__in=[A.MEANING_REVIEWED, A.REVIEWED, A.FLAGGED])
            .select_related("user").order_by("sentence_id", "-created_at", "-id").distinct("sentence_id")}


def states(layer):
    """{sentence id: "approved", "changed" or "flagged"} for every sentence
    in the layer that has been approved or flagged. Cached until a review is
    made or a sentence is imported again."""
    stamp = Sentence.objects.aggregate(n=Count("id"), t=Max("updated_at"))
    last = ReviewEvent.objects.aggregate(i=Max("id"))["i"] or 0
    key = "staff.review.{}.{}.{}.{}".format(layer, last, stamp["n"], stamp["t"].timestamp() if stamp["t"] else 0)
    out = cache.get(key)
    if out is None:
        latest = _latest(_events(layer))
        out = {sid: "flagged" for sid, e in latest.items() if e.action == A.FLAGGED}
        approved = {sid: e for sid, e in latest.items() if e.action != A.FLAGGED}
        for s in _with_texts(Sentence.objects.filter(id__in=list(approved)), layer):
            out[s.id] = "approved" if digest(s, layer) == approved[s.id].digest else "changed"
        cache.set(key, out, 7 * 86400)
    return out


def _rows(layer, book=None, chapter=None):
    """(id, record_id, book, chapter, verse, number) of the layer's sentences,
    in Bible order."""
    rows = _scope(layer)
    if book:
        rows = rows.filter(book=book)
        if chapter:
            rows = rows.filter(chapter=chapter)
    rows = list(rows.values_list("id", "record_id", "book", "chapter", "verse", "number"))
    rows.sort(key=lambda r: (ORDER.get(r[2], 99), r[3], r[4], r[5]))
    return rows


def _next(layer, sentence_id):
    """The record id of the next sentence after sentence_id in the layer's
    queue that isn't approved, or None."""
    rows = _rows(layer)
    st = states(layer)
    ids = [r[0] for r in rows]
    start = ids.index(sentence_id) + 1 if sentence_id in ids else 0
    return next((r[1] for r in rows[start:] if st.get(r[0]) != "approved"), None)


def _layer(layer, allowed):
    layer = layer or (allowed[0] if allowed else "")
    if not allowed:
        raise _Forbidden("Your roles don't review any part of the translation.")
    if layer not in allowed:
        raise _Forbidden("Your roles don't review this layer.")
    return layer


class _Forbidden(Exception):
    pass


def _forbidden(e):
    return Response({"detail": str(e), "code": "forbidden"}, status=status.HTTP_403_FORBIDDEN)


def _event_json(e, current=None):
    """A review event; current is the layer's digest now, for an approval."""
    return {"id": e.id, "action": e.action, "label": e.get_action_display(), "language": e.language,
            "by": e.user.get_full_name() or e.user.username, "note": e.note, "at": e.created_at,
            **({"changed": e.digest != current} if current is not None else {})}


@admin_view("review")
def queue(request):
    allowed = layers(request.user)
    try:
        layer = _layer(request.query_params.get("layer"), allowed)
    except _Forbidden as e:
        return _forbidden(e)
    book = (request.query_params.get("book") or "").upper()
    if book and book not in ORDER:
        raise ValidationError({"book": "Choose a book.", "code": "invalid_book"})
    try:
        chapter = int(request.query_params.get("chapter") or 0)
        offset = max(int(request.query_params.get("offset") or 0), 0)
    except ValueError:
        raise ValidationError({"detail": "Chapter and offset are numbers."})
    state = request.query_params.get("state") or ""
    if state and state not in (*STATES, "todo"):
        raise ValidationError({"state": "Choose a state.", "code": "invalid_state"})
    rows = _rows(layer, book, chapter)
    st = states(layer)
    counts = {s: 0 for s in STATES}
    for r in rows:
        counts[st.get(r[0], "not_reviewed")] += 1
    if state == "todo":
        rows = [r for r in rows if st.get(r[0]) != "approved"]
    elif state:
        rows = [r for r in rows if st.get(r[0], "not_reviewed") == state]
    page = rows[offset:offset + PAGE]
    ids = [r[0] for r in page]
    if _meaning(layer):
        preview = dict(Sentence.objects.filter(id__in=ids).values_list("id", "literal_gloss"))
    else:
        preview = {}
        for sid, level, text in (Rendering.objects.filter(sentence_id__in=ids, language=layer)
                                 .values_list("sentence_id", "level", "text")):
            if level == "B" or sid not in preview:
                preview[sid] = text
    latest = _latest(_events(layer).filter(sentence_id__in=ids))
    books = sorted(_scope(layer).values_list("book", flat=True).distinct(), key=lambda b: ORDER.get(b, 99))
    return Response({
        "layer": layer_json(layer), "layers": [layer_json(code) for code in allowed],
        "books": [{"code": b, "name": refs.BOOK_NAMES.get(b, b)} for b in books],
        "counts": {**counts, "total": sum(counts.values())},
        "offset": offset, "more": offset + PAGE < len(rows), "matching": len(rows),
        "sentences": [{
            "record": r[1], "verse": f"{r[2]}.{r[3]}.{r[4]}", "label": verse_label(f"{r[2]}.{r[3]}.{r[4]}"),
            "state": st.get(r[0], "not_reviewed"), "preview": preview.get(r[0], ""),
            "last": _event_json(latest[r[0]]) if r[0] in latest else None,
        } for r in page],
    })


def _fits(sentence, layer):
    if _meaning(layer):
        return sentence.source_edition.language == layer
    return any(r.language == layer for r in sentence.renderings.all())


@admin_view("review", methods=("GET", "POST"))
def sentence(request, record_id):
    s = (Sentence.objects.filter(record_id=record_id).select_related("source_edition")
         .prefetch_related("renderings", "decisions").first())
    if s is None:
        raise NotFound(f"No sentence {record_id!r}")
    allowed = layers(request.user)
    data = request.data if request.method == "POST" and isinstance(request.data, dict) else {}
    asked = str(data.get("layer") or "") if request.method == "POST" else request.query_params.get("layer")
    fitting = [code for code in allowed if _fits(s, code)]
    try:
        layer = _layer(asked or (fitting[0] if fitting else ""), allowed)
    except _Forbidden as e:
        return _forbidden(e)
    if not _fits(s, layer):
        raise ValidationError({"layer": f"{record_id} isn't in {layer_json(layer)['name']}.", "code": "not_in_layer"})
    if request.method == "POST":
        return _act(request, s, layer, data)
    trail = list(s.review_events.select_related("user"))
    currents = {}
    for e in trail:
        if e.action in (A.MEANING_REVIEWED, A.REVIEWED):
            code = e.language or s.source_edition.language
            if code not in currents:
                currents[code] = digest(s, code)
    words = {w.id: {"text": w.text, "lemma": w.lemma, "gloss": w.gloss, "morph": w.morph}
             for w in Word.objects.filter(id__in=s.tokens)}
    return Response({
        "layer": layer_json(layer), "layers": [layer_json(code) for code in fitting],
        "record": record_json(s), "verse": s.refs[0], "label": verse_label(s.refs[0]), "words": words,
        "languages": [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items()],
        "state": states(layer).get(s.id, "not_reviewed"),
        "trail": [_event_json(e, currents.get(e.language or s.source_edition.language)
                              if e.action in (A.MEANING_REVIEWED, A.REVIEWED) else None) for e in trail],
        "next": _next(layer, s.id),
    })


def _act(request, s, layer, data):
    action = data.get("action")
    if action not in ("approve", "flag", "comment"):
        raise ValidationError({"action": "Choose approve, flag or comment.", "code": "invalid_action"})
    note = str(data.get("note") or "").strip()
    if action != "approve" and not note:
        raise ValidationError({"note": "Say what you noticed.", "code": "empty"})
    if len(note) > 4000:
        raise ValidationError({"note": "Keep it under 4,000 characters.", "code": "too_long"})
    kind = {"approve": _approve(layer), "flag": A.FLAGGED, "comment": A.COMMENT}[action]
    event = ReviewEvent.objects.create(sentence=s, user=request.user, action=kind, note=note,
                                       language="" if _meaning(layer) else layer,
                                       digest=digest(s, layer) if action == "approve" else "")
    if kind == A.MEANING_REVIEWED:
        # update(), not save(): updated_at says when the text last changed.
        Sentence.objects.filter(pk=s.pk, status=Status.AI_DRAFT).update(status=Status.MEANING_REVIEWED)
    return Response({"event": _event_json(event), "state": states(layer).get(s.id, "not_reviewed"),
                     "next": _next(layer, s.id)}, status=status.HTTP_201_CREATED)


def open_flags():
    """Flags not followed by an approval of the same layer, newest first."""
    latest = (ReviewEvent.objects.filter(action__in=[A.MEANING_REVIEWED, A.REVIEWED, A.FLAGGED])
              .select_related("user", "sentence__source_edition")
              .order_by("sentence_id", "language", "-created_at", "-id").distinct("sentence_id", "language"))
    return sorted((e for e in latest if e.action == A.FLAGGED), key=lambda e: e.created_at, reverse=True)


@admin_view("inbox")
def flags(request):
    out = []
    for e in open_flags():
        code = e.language or e.sentence.source_edition.language
        out.append({**_event_json(e), "layer": layer_json(code), "record": e.sentence.record_id,
                    "verse": e.sentence.refs[0], "label": verse_label(e.sentence.refs[0])})
    return Response({"flags": out})
