"""Load the original-language editions and the public-domain reference
Bibles from the pinned sources (see sources.lock.json and
scripts/fetch_sources.py).

    python manage.py import_texts                # every edition
    python manage.py import_texts sblgnt bsb     # just these
    python manage.py import_texts --missing      # run on every deploy

Each edition is replaced wholesale in one transaction, so the command can
be re-run safely and a failed import leaves the edition as it was.
Rows are saved in batches as they are read, so the Hebrew Bible (about
475,000 words) never has to be in memory all at once. One edition per run
peaks at about 410 MB (the BSB and the Greek; the Hebrew about 180 MB). A
run of every edition holds on to more, since Python keeps memory it has
used, so on a 512 MB server import them one at a time.

--missing imports only the editions that are not in the database yet, or
were imported from a different commit than sources.lock.json pins. It
fetches just the sources those editions need, then imports each edition in
a process of its own, so memory never builds up. When nothing is missing it
does nothing, so it costs a deploy almost nothing. A failed fetch or import
is reported but does not fail the command: the deploy goes ahead with the
texts already loaded, and the next deploy tries again.
"""
import itertools
import logging
import subprocess
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from owb import refs
from owb.sources import LOCK, macula_greek, macula_hebrew, open_bibles, sblgnt
from texts.models import Edition, Verse, Word

BATCH = 5000

logger = logging.getLogger(__name__)

ORIGINALS = {
    "sblgnt": dict(
        name="SBL Greek New Testament", language="grc", licence="CC BY 4.0",
        source="sblgnt", source_path="data/sblgnt/text",
        attribution="SBLGNT v1.2. Copyright 2010 by the Society of Biblical Literature and "
                    "Logos Bible Software. Word data: MACULA Greek, © 2022–2024 Biblica, Inc., CC BY 4.0."),
    "wlc": dict(
        name="Westminster Leningrad Codex", language="hbo", licence="Public domain (word data CC BY 4.0)",
        source="macula-hebrew", source_path=macula_hebrew.TSV_PATH,
        attribution="Hebrew text of the Westminster Leningrad Codex (public domain), with word data from "
                    "MACULA Hebrew, © 2022–2024 Biblica, Inc., CC BY 4.0, which incorporates the Open "
                    "Scriptures Hebrew Bible (CC BY 4.0)."),
}


class Command(BaseCommand):
    help = "Import original-language editions and public-domain reference Bibles."

    def add_arguments(self, parser):
        parser.add_argument("editions", nargs="*",
                            help=f"Editions to import (default: all of {self.all_codes()})")
        parser.add_argument("--missing", action="store_true",
                            help="Fetch and import only the editions not loaded at their pinned commit")

    @staticmethod
    def all_codes():
        return list(ORIGINALS) + list(open_bibles.EDITIONS)

    @staticmethod
    def sources(code):
        """The sources.lock.json entries an edition is read from."""
        if code == "sblgnt":
            return ["sblgnt", "macula-greek"]
        if code == "wlc":
            return ["macula-hebrew"]
        return ["open-bibles"]

    @classmethod
    def missing_codes(cls):
        """Editions that have no verses in the database, or whose verses came
        from a different commit than the one pinned now."""
        loaded = dict(Edition.objects.filter(verses__isnull=False).distinct()
                      .values_list("code", "source_commit"))
        return [code for code in cls.all_codes()
                if loaded.get(code) != LOCK[cls.sources(code)[0]]["commit"]]

    def handle(self, *args, editions, missing=False, **options):
        if missing:
            if editions:
                raise CommandError("Give editions or --missing, not both")
            return self.import_missing()
        codes = editions or self.all_codes()
        unknown = set(codes) - set(self.all_codes())
        if unknown:
            raise CommandError(f"Unknown editions: {', '.join(sorted(unknown))}")
        for code in codes:
            started = time.monotonic()
            if code in ORIGINALS:
                verses, words = getattr(self, f"load_{code}")()
            else:
                verses, words = self.load_reference(code)
            n_verses, n_words = self.save(code, verses, words)
            self.stdout.write(f"{code}: {n_verses} verses, {n_words} words "
                              f"({time.monotonic() - started:.1f}s)")

    def import_missing(self):
        codes = self.missing_codes()
        if not codes:
            self.stdout.write("Every edition is loaded.")
            return
        self.stdout.write(f"Missing or out of date: {' '.join(codes)}")
        self.stdout.flush()   # before the subprocesses write theirs
        sources = list(dict.fromkeys(s for code in codes for s in self.sources(code)))
        fetch = [sys.executable, str(settings.REPO_ROOT / "scripts" / "fetch_sources.py"), *sources]
        if subprocess.run(fetch).returncode != 0:
            return self.fail(f"Could not fetch {' '.join(sources)}; nothing imported")
        failed = []
        for code in codes:
            # One process per edition: Python keeps memory it has used, so
            # imports run one after another in the same process would not fit.
            run = [sys.executable, str(settings.BASE_DIR / "manage.py"), "import_texts", code]
            if subprocess.run(run).returncode != 0:
                failed.append(code)
        if failed:
            self.fail(f"Could not import {' '.join(failed)}")

    def fail(self, message):
        # Logged as an error (and so sent to Sentry when it is set up), but the
        # deploy goes on with the texts already loaded.
        logger.error("import_texts --missing: %s; the next deploy will try again", message)

    # Loaders return ([(book, chapter, verse, text)], [word dicts]), as lists
    # or as iterables that are read once.

    def load_sblgnt(self):
        verses = []
        for code, _ in refs.NT_BOOKS:
            for ref, v in sblgnt.load_book(code).items():
                verses.append((ref.book, ref.chapter, ref.verse, v.text))
        tokens = (t for toks in macula_greek._all_tokens().values() for t in toks)
        words = (dict(id=t.id, book=t.ref.book, chapter=t.ref.chapter, verse=t.ref.verse,
                      position=t.position, seq=seq, text=t.text, after=t.after,
                      lemma=t.lemma, morph=t.morph, gloss=t.gloss, english=t.english,
                      strong=t.strong, lang="grc")
                 for seq, t in enumerate(tokens))
        return verses, words

    def load_wlc(self):
        # Two passes over the file, each streamed, rather than one pass that
        # keeps everything.
        verses = ((ref.book, ref.chapter, ref.verse, macula_hebrew.verse_text(morphemes))
                  for ref, morphemes in macula_hebrew.iter_verses())
        morphemes = (m for _, ms in macula_hebrew.iter_verses() for m in ms)
        words = (dict(id=m.id, book=m.ref.book, chapter=m.ref.chapter, verse=m.ref.verse,
                      position=m.position, seq=seq, text=m.text, after=m.after,
                      lemma=m.lemma, morph=m.morph, gloss=m.gloss, english=m.english,
                      strong=m.strong, transliteration=m.transliteration, lang=m.lang)
                 for seq, m in enumerate(morphemes))
        return verses, words

    def load_reference(self, code):
        data = open_bibles.load(code)
        order = {c: i for i, c in enumerate(refs.BOOK_CODES)}
        verses = sorted(((b, c, v, t) for (b, c, v), t in data.items()),
                        key=lambda row: (order[row[0]], row[1], row[2]))
        return verses, []

    def edition_fields(self, code):
        if code in ORIGINALS:
            fields = dict(ORIGINALS[code], kind=Edition.Kind.ORIGINAL)
        else:
            filename, _, language, name, licence = open_bibles.EDITIONS[code]
            fields = dict(name=name, language=language, licence=licence, kind=Edition.Kind.REFERENCE,
                          source="open-bibles", source_path=filename,
                          attribution=f"{name}, from github.com/seven1m/open-bibles ({licence}).")
        fields["source_commit"] = LOCK[fields["source"]]["commit"]
        return fields

    @transaction.atomic
    def save(self, code, verses, words):
        """Replace the edition's verses and words; return how many of each."""
        edition, _ = Edition.objects.update_or_create(code=code, defaults=self.edition_fields(code))
        edition.verses.all().delete()
        edition.words.all().delete()
        n_verses = bulk_create(
            Verse, (Verse(edition=edition, book=b, chapter=c, verse=v, text=t) for b, c, v, t in verses))
        n_words = bulk_create(Word, (Word(edition=edition, **w) for w in words))
        edition.verse_count = n_verses
        edition.save(update_fields=["verse_count"])
        return n_verses, n_words


def bulk_create(model, objs):
    """Insert objs BATCH at a time. Django's bulk_create makes a list of
    everything it is given first, so a generator passed to it whole would
    still be held in memory."""
    total = 0
    objs = iter(objs)
    while batch := list(itertools.islice(objs, BATCH)):
        model.objects.bulk_create(batch)
        total += len(batch)
    return total
