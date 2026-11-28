"""Review assignments: an editor asks a reviewer to review a book, or a
range of its chapters, in one layer, by a date or not.

GET    /api/admin/assignments/?layer=&mine=1&closed=1
        assignments, each with its progress (the sentences in its range by
        review state) and whether it is open, done, overdue or closed.
        Editors and super admins see everyone's; anyone else their own.
        For those who may assign, also the reviewers and their layers.
POST   /api/admin/assignments/  {layer, book, chapter_from, chapter_to,
                                 assignee, due, note}
        assign (editors and super admins). A range with nothing drafted in
        the layer is refused (it could never be done); the answer's
        warnings name chapters in it not drafted yet and open assignments
        it overlaps.
        {layer, book, assignees: [ids], due, note} splits the book's
        drafted chapters between several reviewers, in runs of about the
        same number of sentences: {"assignments": [...], "warnings"}
PATCH  /api/admin/assignments/<id>/  {due, note, closed}
        change the date or note, close or reopen (editors and super admins)
DELETE /api/admin/assignments/<id>/
        take it back (editors and super admins)

An assignment is done when every sentence in its range is approved in the
layer; "reviewed" when every one has been looked at but some are flagged
(the reviewer's part is finished; the flags are an editor's to act on); and
overdue when its date has passed before either. Closing one is an
editor's: an assignment done stays listed until closed. Nothing here
approves anything or changes a sentence.
"""
import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, Max
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from accounts.models import Role
from owb import languages, refs
from texts.models import Verse

from .models import ReviewAssignment, record
from . import notify, people
from .permissions import admin_view
from .review import STATES, _in_layer, _scope, layer_json

K = Role.Kind
EVERY_LAYER = (*languages.ORIGINAL, *languages.READING)


def may_assign(request):
    """Editors and super admins assign (the inbox area: they act on flags)."""
    return "inbox" in request.admin_areas


def _forbidden():
    return Response({"detail": "Only editors and super admins assign review.", "code": "forbidden"},
                    status=status.HTTP_403_FORBIDDEN)


def in_range(sentences, a):
    """sentences cut to the assignment's book and chapters."""
    sentences = sentences.filter(book=a.book)
    if a.chapter_from:
        sentences = sentences.filter(chapter__gte=a.chapter_from)
    if a.chapter_to:
        sentences = sentences.filter(chapter__lte=a.chapter_to)
    return sentences


def progress(a):
    """{state: count, "total": n} for the sentences in a's range in its layer."""
    counts = {s: 0 for s in STATES}
    rows = _in_layer(in_range(_scope(a.layer), a), a.layer).order_by().values("st").annotate(n=Count("id"))
    for row in rows:
        counts[row["st"]] = row["n"]
    counts["total"] = sum(counts.values())
    return counts


def standing(a, counts, today):
    """"closed", "done" (every sentence in range approved), "reviewed"
    (every one approved or flagged, some flagged), "overdue" or "open"."""
    if a.closed_at:
        return "closed"
    if counts["total"] and counts["approved"] == counts["total"]:
        return "done"
    if counts["total"] and counts["flagged"] and counts["approved"] + counts["flagged"] == counts["total"]:
        return "reviewed"
    if a.due and a.due < today:
        return "overdue"
    return "open"


def range_label(a):
    name = refs.BOOK_NAMES.get(a.book, a.book)
    if not a.chapter_from and not a.chapter_to:
        return name
    lo, hi = a.chapter_from or 1, a.chapter_to
    if hi is None:
        return f"{name} {lo} to the end"
    return f"{name} {lo}" if lo == hi else f"{name} {lo}–{hi}"


def _person(user):
    return people.person(user)


def assignment_json(a, today=None, counts=None):
    today = today or timezone.localdate()
    counts = counts if counts is not None else progress(a)
    return {
        "id": a.id, "layer": layer_json(a.layer), "book": a.book, "chapter_from": a.chapter_from,
        "chapter_to": a.chapter_to, "label": range_label(a), "assignee": _person(a.assignee),
        "assigned_by": _person(a.assigned_by), "due": a.due, "note": a.note, "created_at": a.created_at,
        "closed_at": a.closed_at, "progress": counts, "standing": standing(a, counts, today),
        "days_left": (a.due - today).days if a.due else None,
    }


def listed(assignments):
    today = timezone.localdate()
    out = [assignment_json(a, today) for a in assignments.select_related("assignee", "assigned_by")]
    # Overdue first, then by date (none last), then oldest first.
    rank = {"overdue": 0, "open": 1, "reviewed": 2, "done": 3, "closed": 4}
    out.sort(key=lambda x: (rank[x["standing"]], x["due"] is None, x["due"] or datetime.date.max))
    return out


def attention(user):
    """(open, overdue): the assignments to user not closed nor done, and
    those of them past their date, for the dashboard."""
    today = timezone.localdate()
    mine = [a for a in ReviewAssignment.objects.filter(assignee=user, closed_at__isnull=True)]
    left = [a for a in mine if standing(a, progress(a), today) in ("open", "overdue")]
    return len(left), sum(1 for a in left if a.due and a.due < today)


def reviews(user, layer):
    """Whether user holds a role that reviews layer (a super admin too
    needs one: review.reviewing)."""
    kind = K.SCHOLAR_REVIEWER if layer in languages.ORIGINAL else K.LANGUAGE_REVIEWER
    return user.roles.filter(kind=kind, language=layer).exists()


def reviewers():
    """Everyone who reviews something: [{id, email, name, layers: [codes]}].
    A super admin is one of them only through a reviewer role."""
    User = get_user_model()
    out = []
    for u in (User.objects.filter(roles__kind__in=[K.SCHOLAR_REVIEWER, K.LANGUAGE_REVIEWER])
              .distinct().prefetch_related("roles").order_by("username")):
        codes = [r.language for r in u.roles.all() if r.kind in (K.SCHOLAR_REVIEWER, K.LANGUAGE_REVIEWER)]
        out.append({**_person(u), "layers": [c for c in EVERY_LAYER if c in codes]})
    return out


@admin_view("overview", methods=("GET", "POST"))
def assignments(request):
    if request.method == "POST":
        if not may_assign(request):
            return _forbidden()
        return _assign(request)
    rows = ReviewAssignment.objects.all()
    everyone = may_assign(request)
    if not everyone or request.query_params.get("mine"):
        rows = rows.filter(assignee=request.user)
    layer = request.query_params.get("layer")
    if layer:
        rows = rows.filter(layer=layer)
    if not request.query_params.get("closed"):
        rows = rows.filter(closed_at__isnull=True)
    answer = {"assignments": listed(rows), "may_assign": everyone}
    if everyone:
        answer["reviewers"] = reviewers()
        answer["layers"] = [layer_json(code) for code in EVERY_LAYER]
        answer["books"] = [{"code": c, "name": refs.BOOK_NAMES[c], "testament": "ot" if c in refs.OT_CODES else "nt"}
                           for c in refs.BOOK_CODES]
    return Response(answer)


def _chapter(data, name):
    value = data.get(name)
    if value in (None, ""):
        return None
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValidationError({name: "Chapters are numbers.", "code": "invalid_chapter"})
    if value < 1:
        raise ValidationError({name: "Chapters start at 1.", "code": "invalid_chapter"})
    return value


def _due(data):
    value = data.get("due")
    if value in (None, ""):
        return None
    try:
        due = datetime.date.fromisoformat(str(value))
    except ValueError:
        raise ValidationError({"due": "Give the date as YYYY-MM-DD.", "code": "invalid_date"})
    # A date typed digit by digit can be sent part-way ("0001-12-01"): a due
    # date is within a few years of today, or it's a slip.
    today = timezone.localdate()
    if not today.replace(year=today.year - 1) <= due <= today.replace(year=today.year + 10):
        raise ValidationError({"due": "Give a date from last year to ten years from now.", "code": "invalid_date"})
    return due


def _note(data):
    note = str(data.get("note") or "").strip()
    if len(note) > 2000:
        raise ValidationError({"note": "Keep it under 2,000 characters.", "code": "too_long"})
    return note


def drafted_chapters(layer, book):
    """{chapter: sentences} of book drafted in layer, in order."""
    rows = (_in_layer(_scope(layer).filter(book=book), layer).order_by()
            .values("chapter").annotate(n=Count("id")).values_list("chapter", "n"))
    return dict(sorted(rows))


def split(chapters, k):
    """chapters ({chapter: sentences}, in order) in k runs of about the same
    number of sentences: [(first, last)], fewer when there are fewer chapters."""
    items = list(chapters.items())
    k = max(1, min(k, len(items)))
    total = sum(n for _, n in items)
    runs, start, done = [], 0, 0
    for i in range(k):
        if i == k - 1:
            end = len(items)
        else:
            # The run ends where the running total comes closest to its
            # share, leaving at least one chapter for each run to come.
            target = total * (i + 1) / k
            end, cum = start + 1, done + items[start][1]
            while end < len(items) - (k - i - 1) and abs(cum + items[end][1] - target) < abs(cum - target):
                cum += items[end][1]
                end += 1
        runs.append((items[start][0], items[end - 1][0]))
        done += sum(n for _, n in items[start:end])
        start = end
    return runs


def _warnings(a, chapters):
    """What to know about a new assignment: chapters in its range not drafted
    in the layer yet, and open assignments of the same layer it overlaps."""
    out = []
    last = max(chapters) if chapters else 0
    lo, hi = a.chapter_from or 1, a.chapter_to or last
    missing = [c for c in range(lo, hi + 1) if c not in chapters]
    if missing:
        shown = ", ".join(map(str, missing[:8])) + ("…" if len(missing) > 8 else "")
        word = "chapters" if len(missing) > 1 else "chapter"
        out.append(f"Not drafted in {layer_json(a.layer)['name']} yet: {word} {shown}.")
    for other in (ReviewAssignment.objects.filter(layer=a.layer, book=a.book, closed_at__isnull=True)
                  .exclude(pk=a.pk).select_related("assignee")):
        o_lo, o_hi = other.chapter_from or 1, other.chapter_to or 10_000
        if o_lo <= hi and lo <= o_hi:
            out.append(f"Overlaps {people.name(other.assignee)}'s {range_label(other)}.")
    return out


def _assign(request):
    data = request.data if isinstance(request.data, dict) else {}
    if data.get("assignees") is not None:
        return _assign_split(request, data)
    layer = str(data.get("layer") or "")
    if layer not in EVERY_LAYER:
        raise ValidationError({"layer": "Choose a layer.", "code": "invalid_layer"})
    book = str(data.get("book") or "").upper()
    if book not in refs.BOOK_NAMES:
        raise ValidationError({"book": "Choose a book.", "code": "invalid_book"})
    if layer in languages.ORIGINAL and (book in refs.OT_CODES) != (layer == "hbo"):
        raise ValidationError({"book": f"{refs.BOOK_NAMES[book]} isn't in {layer_json(layer)['name']}.",
                               "code": "not_in_layer"})
    lo, hi = _chapter(data, "chapter_from"), _chapter(data, "chapter_to")
    if lo and hi and hi < lo:
        raise ValidationError({"chapter_to": "The last chapter comes after the first.", "code": "invalid_chapter"})
    last = Verse.objects.filter(book=book).aggregate(n=Max("chapter"))["n"]
    if last and max(lo or 0, hi or 0) > last:
        raise ValidationError({"chapter_to": f"{refs.BOOK_NAMES[book]} has {last} chapters.",
                               "code": "invalid_chapter"})
    assignee = get_user_model().objects.filter(id=data.get("assignee") if str(data.get("assignee", "")).isdigit()
                                               else None).first()
    if assignee is None:
        raise ValidationError({"assignee": "Choose a reviewer.", "code": "invalid_assignee"})
    if not reviews(assignee, layer):
        raise ValidationError({"assignee": f"{people.name(assignee)} doesn't review {layer_json(layer)['name']}.",
                               "code": "not_a_reviewer"})
    a = ReviewAssignment(layer=layer, book=book, chapter_from=lo, chapter_to=hi, assignee=assignee,
                         assigned_by=request.user, due=_due(data), note=_note(data))
    chapters = drafted_chapters(layer, book)
    if not progress(a)["total"]:
        raise ValidationError({"detail": f"Nothing in {range_label(a)} is drafted in {layer_json(layer)['name']} yet, "
                                         "so it could never be done. Assign it once it is drafted.",
                               "code": "not_drafted"})
    warnings = _warnings(a, chapters)
    a.save()
    record(request.user, "review.assign", assignee.username, layer=layer, range=range_label(a),
           due=a.due.isoformat() if a.due else None)
    notify.assigned(a)
    return Response({"assignment": assignment_json(a), "warnings": warnings}, status=status.HTTP_201_CREATED)


def _assign_split(request, data):
    """One book's drafted chapters between several reviewers."""
    layer = str(data.get("layer") or "")
    if layer not in EVERY_LAYER:
        raise ValidationError({"layer": "Choose a layer.", "code": "invalid_layer"})
    book = str(data.get("book") or "").upper()
    if book not in refs.BOOK_NAMES:
        raise ValidationError({"book": "Choose a book.", "code": "invalid_book"})
    ids = data.get("assignees")
    if not isinstance(ids, list) or not ids or not all(str(i).isdigit() for i in ids):
        raise ValidationError({"assignees": "Choose the reviewers to share it.", "code": "invalid_assignee"})
    ids = list(dict.fromkeys(int(i) for i in ids))
    users = {u.id: u for u in get_user_model().objects.filter(id__in=ids)}
    if len(users) != len(ids):
        raise ValidationError({"assignees": "Choose reviewers from the list.", "code": "invalid_assignee"})
    for u in users.values():
        if not reviews(u, layer):
            raise ValidationError({"assignees": f"{people.name(u)} doesn't review {layer_json(layer)['name']}.",
                                   "code": "not_a_reviewer"})
    chapters = drafted_chapters(layer, book)
    if not chapters:
        raise ValidationError({"detail": f"Nothing in {refs.BOOK_NAMES[book]} is drafted in "
                                         f"{layer_json(layer)['name']} yet.", "code": "not_drafted"})
    due, note = _due(data), _note(data)
    made, warnings = [], []
    for (lo, hi), uid in zip(split(chapters, len(ids)), ids):
        a = ReviewAssignment(layer=layer, book=book, chapter_from=lo, chapter_to=hi, assignee=users[uid],
                             assigned_by=request.user, due=due, note=note)
        warnings += [w for w in _warnings(a, chapters) if w.startswith("Overlaps") and w not in warnings]
        a.save()
        record(request.user, "review.assign", users[uid].username, layer=layer, range=range_label(a),
               due=due.isoformat() if due else None)
        notify.assigned(a)
        made.append(a)
    return Response({"assignments": [assignment_json(a) for a in made], "warnings": warnings},
                    status=status.HTTP_201_CREATED)


@admin_view("overview", methods=("PATCH", "DELETE"))
def assignment(request, assignment_id):
    if not may_assign(request):
        return _forbidden()
    a = ReviewAssignment.objects.select_related("assignee", "assigned_by").filter(id=assignment_id).first()
    if a is None:
        raise NotFound("No such assignment.")
    if request.method == "DELETE":
        record(request.user, "review.unassign", a.assignee.username, layer=a.layer, range=range_label(a))
        a.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    data = request.data if isinstance(request.data, dict) else {}
    changed = []
    if "due" in data:
        a.due = _due(data)
        changed.append("due")
    if "note" in data:
        a.note = _note(data)
        changed.append("note")
    if "closed" in data:
        a.closed_at = timezone.now() if data["closed"] else None
        changed.append("closed_at")
    if changed:
        a.save(update_fields=changed)
        record(request.user, "review.assignment", a.assignee.username, layer=a.layer, range=range_label(a),
               changed=changed, closed=bool(a.closed_at))
    return Response({"assignment": assignment_json(a)})
