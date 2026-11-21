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

Each sentence's state in a layer is kept in ReviewState (one row per
sentence approved or flagged in the layer, kept up to date as events are
saved), so queues are filtered, counted and paged in the database. refresh()
compares the approvals of sentences saved since they were last checked with
what the sentences say now, so "changed since approval" needs no full
rebuild after an import or a review.

Approving the meaning moves a sentence from ai_draft to meaning_reviewed.
Wording approvals are kept per language and don't change the sentence's
status: when a sentence counts as "reviewed" is the charter's to decide.
"""
import hashlib
import json
from datetime import timedelta
from functools import reduce
from operator import or_

from django.core.cache import cache
from django.db import transaction
from django.db.models import Count, F, FilteredRelation, Max, Prefetch, Q, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from accounts.models import Role
from api.views import record_json
from owb import languages, refs
from texts.models import Word
from translation.models import Decision, Rendering, ReviewEvent, ReviewState, Sentence, Status

from .inbox import verse_label
from .permissions import admin_view, is_super_admin
from .snapshot import snapshot

A = ReviewEvent.Action
RS = ReviewState.State
PAGE = 50
BIBLE_ORDER = ("book_order", "chapter", "verse", "number", "id")
# Longer than an import takes to commit one file's sentences (refresh).
SLACK = timedelta(minutes=15)
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


def _in_layer(sentences, layer):
    """sentences with their state in layer (st) and the id of their latest
    approval or flag there (last_id), from ReviewState."""
    return (sentences.annotate(rs=FilteredRelation("review_states", condition=Q(review_states__layer=layer)))
            .annotate(st=Coalesce("rs__state", Value("not_reviewed")), last_id=F("rs__event_id")))


def refresh(layer):
    """Compare each approval in layer whose sentence has been saved since it
    was last compared (an import saves the sentences it changes) with what
    the sentence says now: "approved" if it still matches, "changed" if not.
    Only approvals never compared, and sentences saved after the last
    refresh of the layer began, are looked at; or SLACK before, for an
    import that had not committed yet then (updated_at is when a sentence
    was saved, not when the import committed it)."""
    began = timezone.now()
    newest = Sentence.objects.aggregate(t=Max("updated_at"))["t"]
    key = f"staff.review.refreshed.{layer}"
    since = cache.get(key)
    approvals = (ReviewState.objects.filter(layer=layer, state__in=[RS.APPROVED, RS.CHANGED])
                 .values_list("id", "sentence_id", "event_id", "event__digest"))
    saved = approvals.filter(checked_at__lt=F("sentence__updated_at"))
    if since is not None:
        saved = saved.filter(sentence__updated_at__gt=since)
    stale = list({*approvals.filter(checked_at__isnull=True), *saved})
    for start in range(0, len(stale), 500):
        chunk = stale[start:start + 500]
        sentences = _with_texts(Sentence.objects.filter(id__in=[row[1] for row in chunk]), layer).in_bulk()
        groups = {}
        for pk, sentence_id, event_id, approved in chunk:
            s = sentences[sentence_id]
            state = RS.APPROVED if digest(s, layer) == approved else RS.CHANGED
            groups.setdefault((state, s.updated_at), []).append(Q(pk=pk, event_id=event_id))
        for (state, checked), rows in groups.items():
            # Only rows still on the approval compared: one made meanwhile
            # has reset its row, to be compared next time.
            ReviewState.objects.filter(reduce(or_, rows)).update(state=state, checked_at=checked)
    # Every sentence saved by then has been compared.
    done = min(newest, began - SLACK) if newest else None
    if done is not None and (since is None or done > since + timedelta(minutes=1)):
        cache.set(key, done, 30 * 86400)


def states(layer):
    """{sentence id: "approved", "changed" or "flagged"} for every sentence
    in the layer that has been approved or flagged."""
    refresh(layer)
    return dict(ReviewState.objects.filter(layer=layer).values_list("sentence_id", "state"))


def state_of(layer, sentence_id):
    refresh(layer)
    return (ReviewState.objects.filter(layer=layer, sentence_id=sentence_id).values_list("state", flat=True).first()
            or "not_reviewed")


def open_flag_count():
    return ReviewState.objects.filter(state=RS.FLAGGED).count()


def _next(layer, s):
    """The record id of the next sentence after s in the layer's queue that
    isn't approved, or None: one query, read along the Bible order index
    from s's book."""
    o, c, v, n = s.book_order, s.chapter, s.verse, s.number
    after = (Q(book_order__gt=o) | Q(book_order=o, chapter__gt=c) | Q(book_order=o, chapter=c, verse__gt=v)
             | Q(book_order=o, chapter=c, verse=v, number__gt=n)
             | Q(book_order=o, chapter=c, verse=v, number=n, id__gt=s.id))
    return (_in_layer(_scope(layer), layer).filter(after, ~Q(st=RS.APPROVED), book_order__gte=o)
            .order_by(*BIBLE_ORDER).values_list("record_id", flat=True).first())


def _books(layer):
    """The layer's books in Bible order, cached until a sentence is added or
    saved again."""
    stamp = Sentence.objects.aggregate(n=Count("id"), t=Max("updated_at"))
    key = "staff.review.books.{}.{}.{}".format(layer, stamp["n"], stamp["t"].timestamp() if stamp["t"] else 0)
    books = cache.get(key)
    if books is None:
        books = [b for _, b in _scope(layer).order_by("book_order").values_list("book_order", "book").distinct()]
        cache.set(key, books, 7 * 86400)
    return books


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
    refresh(layer)
    rows = _scope(layer)
    if book:
        rows = rows.filter(book=book)
        if chapter:
            rows = rows.filter(chapter=chapter)
    rows = _in_layer(rows, layer)
    counts = {s: 0 for s in STATES}
    for row in rows.order_by().values("st").annotate(n=Count("id")):
        counts[row["st"]] = row["n"]
    total = sum(counts.values())
    if state == "todo":
        rows, matching = rows.filter(~Q(st=RS.APPROVED)), total - counts["approved"]
    elif state:
        rows, matching = rows.filter(st=state), counts[state]
    else:
        matching = total
    page = list(rows.order_by(*BIBLE_ORDER)
                .values_list("id", "record_id", "book", "chapter", "verse", "st", "last_id")[offset:offset + PAGE])
    ids = [r[0] for r in page]
    if _meaning(layer):
        preview = dict(Sentence.objects.filter(id__in=ids).values_list("id", "literal_gloss"))
    else:
        preview = {}
        for sid, level, text in (Rendering.objects.filter(sentence_id__in=ids, language=layer)
                                 .values_list("sentence_id", "level", "text")):
            if level == "B" or sid not in preview:
                preview[sid] = text
    latest = ReviewEvent.objects.select_related("user").in_bulk([r[6] for r in page if r[6]])
    books = _books(layer)
    return Response({
        "layer": layer_json(layer), "layers": [layer_json(code) for code in allowed],
        "books": [{"code": b, "name": refs.BOOK_NAMES.get(b, b)} for b in books],
        "counts": {**counts, "total": total},
        "offset": offset, "more": offset + PAGE < matching, "matching": matching,
        "sentences": [{
            "record": r[1], "verse": f"{r[2]}.{r[3]}.{r[4]}", "label": verse_label(f"{r[2]}.{r[3]}.{r[4]}"),
            "state": r[5], "preview": preview.get(r[0], ""),
            "last": _event_json(latest[r[6]]) if r[6] in latest else None,
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
        "state": state_of(layer, s.id),
        "trail": [_event_json(e, currents.get(e.language or s.source_edition.language)
                              if e.action in (A.MEANING_REVIEWED, A.REVIEWED) else None) for e in trail],
        "next": _next(layer, s),
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
    with transaction.atomic():
        # Saving the event brings the sentence's ReviewState up to date.
        event = ReviewEvent.objects.create(sentence=s, user=request.user, action=kind, note=note,
                                           language="" if _meaning(layer) else layer,
                                           digest=digest(s, layer) if action == "approve" else "",
                                           snapshot=snapshot(s, layer) if action == "approve" else {})
        if action == "approve":
            # The digest was just taken from s as loaded: no need to compare again.
            ReviewState.objects.filter(sentence=s, layer=layer, event=event).update(checked_at=s.updated_at)
        if kind == A.MEANING_REVIEWED:
            # update(), not save(): updated_at says when the text last changed.
            Sentence.objects.filter(pk=s.pk, status=Status.AI_DRAFT).update(status=Status.MEANING_REVIEWED)
    return Response({"event": _event_json(event), "state": state_of(layer, s.id),
                     "next": _next(layer, s)}, status=status.HTTP_201_CREATED)


def open_flags():
    """Flags not followed by an approval of the same layer, newest first."""
    out = []
    for row in (ReviewState.objects.filter(state=RS.FLAGGED)
                .select_related("event__user", "sentence__source_edition")
                .order_by("-event__created_at", "-event_id")):
        row.event.sentence = row.sentence
        out.append(row.event)
    return out


@admin_view("inbox")
def flags(request):
    out = []
    for e in open_flags():
        code = e.language or e.sentence.source_edition.language
        out.append({**_event_json(e), "layer": layer_json(code), "record": e.sentence.record_id,
                    "verse": e.sentence.refs[0], "label": verse_label(e.sentence.refs[0])})
    return Response({"flags": out})
