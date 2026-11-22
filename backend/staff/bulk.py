"""Bulk review: one reviewer approving or flagging several sentences of a
layer at once, from the review queue.

POST /api/admin/review/bulk/  {layer, action, note, records: [record ids]}
        approve or flag the sentences named (at most MAX)
POST /api/admin/review/bulk/  {layer, action: "approve", chapter: "JHN.3"}
        approve the rest of a chapter: its sentences in the layer that are
        not reviewed or changed since approval (flagged ones are left for
        a reviewer to look at one by one)
        dry_run: true answers what would be done, saving nothing

Each sentence goes through the same steps as the single action
(staff/review.py apply): the layer must be one the reviewer reviews and
hold the sentence, an approval keeps the digest and snapshot of what it
approves, and each is a ReviewEvent of its own, which brings the sentence's
ReviewState up to date. All of it is one transaction: if any sentence can't
be acted on, nothing is saved and the answer says which and why. A sentence
already approved (and unchanged since) is skipped, not approved again.

The answer lists every sentence asked for, in Bible order, with what was
done: {"results": [{record, verse, label, result: "applied" | "skipped" |
"would_apply" | "error", state, event, code, detail}], "applied", "skipped"}.
"""
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from owb import refs
from translation.models import ReviewState, Sentence

from . import review
from .inbox import verse_label
from .permissions import admin_view

RS = ReviewState.State
# The largest chapter (Psalm 119) has 176 sentences.
MAX = 200


def _row(s, **extra):
    return {"record": s.record_id, "verse": s.refs[0], "label": verse_label(s.refs[0]), **extra}


def _chapter(value):
    try:
        book, chapter = str(value).upper().split(".")
        chapter = int(chapter)
    except ValueError:
        raise ValidationError({"chapter": "Name a chapter as BOOK.N, e.g. JHN.3.", "code": "invalid_chapter"})
    if book not in refs.BOOK_NAMES or chapter < 1:
        raise ValidationError({"chapter": "Name a chapter as BOOK.N, e.g. JHN.3.", "code": "invalid_chapter"})
    return book, chapter


def _too_many(n):
    raise ValidationError({"detail": f"That is {n:,} sentences; act on at most {MAX} at once.", "code": "too_many"})


@admin_view("review", methods=("POST",))
def bulk(request):
    data = request.data if isinstance(request.data, dict) else {}
    try:
        layer = review._layer(str(data.get("layer") or ""), review.layers(request.user))
    except review._Forbidden as e:
        return review._forbidden(e)
    action = data.get("action")
    if action not in ("approve", "flag"):
        raise ValidationError({"action": "Choose approve or flag.", "code": "invalid_action"})
    note = str(data.get("note") or "").strip()
    if action == "flag" and not note:
        raise ValidationError({"note": "Say what you noticed.", "code": "empty"})
    if len(note) > 4000:
        raise ValidationError({"note": "Keep it under 4,000 characters.", "code": "too_long"})
    records, chapter = data.get("records"), data.get("chapter")
    if bool(records) == bool(chapter):
        raise ValidationError({"detail": "Send the records to act on, or a chapter.", "code": "invalid_request"})

    review.refresh(layer)
    loaded = review._with_texts(Sentence.objects.select_related("source_edition"), layer)
    errors = []
    if chapter:
        if action != "approve":
            raise ValidationError({"action": "A chapter at a time is for approving.", "code": "invalid_action"})
        book, number = _chapter(chapter)
        ids = list(review._in_layer(review._scope(layer).filter(book=book, chapter=number), layer)
                   .filter(st__in=["not_reviewed", RS.CHANGED]).values_list("id", flat=True))
        if len(ids) > MAX:
            _too_many(len(ids))
        sentences = list(loaded.filter(id__in=ids).order_by(*review.BIBLE_ORDER))
    else:
        if not isinstance(records, list) or not all(isinstance(r, str) for r in records):
            raise ValidationError({"records": "Send a list of record ids.", "code": "invalid_records"})
        asked = list(dict.fromkeys(records))
        if len(asked) > MAX:
            _too_many(len(asked))
        found = {s.record_id: s for s in loaded.filter(record_id__in=asked)}
        sentences = []
        for record_id in asked:
            s = found.get(record_id)
            if s is None:
                errors.append({"record": record_id, "result": "error", "code": "not_found",
                               "detail": f"No sentence {record_id}."})
            elif not review._fits(s, layer):
                errors.append(_row(s, result="error", code="not_in_layer",
                                   detail=f"{record_id} isn't in {review.layer_json(layer)['name']}."))
            else:
                sentences.append(s)
        sentences.sort(key=lambda s: (s.book_order, s.chapter, s.verse, s.number, s.id))
    if errors:
        return Response({"detail": "Some of these sentences can't be reviewed here, so nothing was saved.",
                         "code": "invalid_records", "results": errors}, status=status.HTTP_400_BAD_REQUEST)

    before = dict(ReviewState.objects.filter(layer=layer, sentence__in=sentences)
                  .values_list("sentence_id", "state"))
    todo = [s for s in sentences if action != "approve" or before.get(s.id) != RS.APPROVED]
    if data.get("dry_run"):
        return Response({"layer": review.layer_json(layer), "applied": 0, "skipped": len(sentences) - len(todo),
                         "results": [_row(s, result="would_apply" if s in todo else "skipped",
                                          state=before.get(s.id, "not_reviewed")) for s in sentences]})
    events = {}
    with transaction.atomic():
        for s in todo:
            events[s.id] = review.apply(request.user, s, layer, action, note)
    after = dict(ReviewState.objects.filter(layer=layer, sentence__in=sentences).values_list("sentence_id", "state"))
    results = []
    for s in sentences:
        if s.id in events:
            results.append(_row(s, result="applied", state=after.get(s.id, "not_reviewed"),
                                event=review._event_json(events[s.id])))
        else:
            results.append(_row(s, result="skipped", state=before.get(s.id, "not_reviewed")))
    return Response({"layer": review.layer_json(layer), "applied": len(events),
                     "skipped": len(sentences) - len(events), "results": results},
                    status=status.HTTP_201_CREATED if events else status.HTTP_200_OK)
