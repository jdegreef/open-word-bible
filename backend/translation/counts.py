"""Drafted sentences per book and language (DraftedCount), and finding the
sentences that use given source words.

Counting every rendering takes seconds on a warm database, and can take
longer than the web server's 15-second statement limit when the table no
longer fits in memory: the admin's Coverage page failed with a 500.
import_content changes renderings, so it keeps DraftedCount as it saves
each file (apply); recount() rebuilds the counts from the renderings, for
the migration that adds them and for `manage.py recount_drafted`.
"""
from collections import Counter

from django.db import transaction
from django.db.models import Count, F
from django.db.models.expressions import RawSQL

from .models import DraftedCount, Rendering, Sentence


def drafted(books=None):
    """Counter {(book, language): sentences drafted}, for books (default:
    every book). A plain join filtered by book: `sentence IN (subquery)`
    was planned as a nested loop over every rendering on a database
    without statistics yet (CI's), and ran for most of an hour."""
    renderings = Rendering.objects.all() if books is None else Rendering.objects.filter(sentence__book__in=books)
    rows = renderings.values("sentence__book", "language").annotate(n=Count("sentence", distinct=True))
    return Counter({(r["sentence__book"], r["language"]): r["n"] for r in rows})


def apply(delta):
    """Add a Counter {(book, language): change} to the stored counts."""
    for (book, language), n in delta.items():
        if not n:
            continue
        row, _ = DraftedCount.objects.get_or_create(book=book, language=language)
        DraftedCount.objects.filter(id=row.id).update(sentences=F("sentences") + n)


@transaction.atomic
def recount(books=None):
    """Count the renderings of books (default: every book) again and store
    the result."""
    counts = drafted(books)
    old = DraftedCount.objects.all() if books is None else DraftedCount.objects.filter(book__in=books)
    old.delete()
    DraftedCount.objects.bulk_create(DraftedCount(book=b, language=lang, sentences=n)
                                     for (b, lang), n in counts.items())


def by_book():
    """{book: {language: sentences drafted}}."""
    out = {}
    for book, language, n in DraftedCount.objects.filter(sentences__gt=0).values_list("book", "language",
                                                                                       "sentences"):
        out.setdefault(book, {})[language] = n
    return out


# `tokens && ARRAY[...]` compares every id with every token of every
# sentence: 27 seconds for the 6,513 occurrences of one Hebrew word. Joining
# the unnested tokens to the ids hashes them instead (about 0.1 s for every
# key term at once).
_USING = ("SELECT DISTINCT s.id FROM {table} s CROSS JOIN LATERAL unnest(s.tokens) AS t(id) "
          "JOIN unnest(%s::varchar[]) AS w(id) ON w.id = t.id")


def using(word_ids):
    """The sentences whose source tokens include any of word_ids."""
    ids = sorted(set(word_ids))
    if not ids:
        return Sentence.objects.none()
    return Sentence.objects.filter(id__in=RawSQL(_USING.format(table=Sentence._meta.db_table), (ids,)))
