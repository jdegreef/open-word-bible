"""Load the original-language editions and the public-domain reference
Bibles from the pinned sources (see sources.lock.json and
scripts/fetch_sources.py).

    python manage.py import_texts                # every edition
    python manage.py import_texts sblgnt bsb     # just these

Each edition is replaced wholesale, so the command can be re-run safely.
"""
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from owb import refs
from owb.sources import LOCK, macula_greek, macula_hebrew, open_bibles, sblgnt
from texts.models import Edition, Verse, Word

BATCH = 5000

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

    @staticmethod
    def all_codes():
        return list(ORIGINALS) + list(open_bibles.EDITIONS)

    def handle(self, *args, editions, **options):
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
            self.save(code, verses, words)
            self.stdout.write(f"{code}: {len(verses)} verses, {len(words)} words "
                              f"({time.monotonic() - started:.1f}s)")

    # Loaders return (edition fields, [(book, chapter, verse, text)], [word dicts]).

    def load_sblgnt(self):
        verses = []
        for code, _ in refs.NT_BOOKS:
            for ref, v in sblgnt.load_book(code).items():
                verses.append((ref.book, ref.chapter, ref.verse, v.text))
        words = []
        for seq, t in enumerate(t for toks in macula_greek._all_tokens().values() for t in toks):
            words.append(dict(id=t.id, book=t.ref.book, chapter=t.ref.chapter, verse=t.ref.verse,
                              position=t.position, seq=seq, text=t.text, after=t.after,
                              lemma=t.lemma, morph=t.morph, gloss=t.gloss, english=t.english,
                              strong=t.strong, lang="grc"))
        return verses, words

    def load_wlc(self):
        verses, words, seq = [], [], 0
        for ref, morphemes in macula_hebrew.verses().items():
            verses.append((ref.book, ref.chapter, ref.verse, macula_hebrew.verse_text(morphemes)))
            for m in morphemes:
                words.append(dict(id=m.id, book=ref.book, chapter=ref.chapter, verse=ref.verse,
                                  position=m.position, seq=seq, text=m.text, after=m.after,
                                  lemma=m.lemma, morph=m.morph, gloss=m.gloss, english=m.english,
                                  strong=m.strong, transliteration=m.transliteration, lang=m.lang))
                seq += 1
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
        edition, _ = Edition.objects.update_or_create(code=code, defaults=self.edition_fields(code))
        edition.verses.all().delete()
        edition.words.all().delete()
        Verse.objects.bulk_create(
            (Verse(edition=edition, book=b, chapter=c, verse=v, text=t) for b, c, v, t in verses),
            batch_size=BATCH)
        Word.objects.bulk_create((Word(edition=edition, **w) for w in words), batch_size=BATCH)
