"""Load the sentence records in content/ into the database.

    python manage.py import_content
    python manage.py import_content --if-texts-loaded --budget 900   # every deploy
    python manage.py import_content --all               # every file, all of search

Every record is checked first with owb.validate against the words already in
the database (run import_texts before this). A file with any error is not
imported. With --if-texts-loaded, the command does nothing (and succeeds)
while no source words are in the database yet, and skips, with a notice, a
file whose source text has not been imported (Genesis before the Hebrew is
loaded), so a deploy is never blocked by import_texts not having run yet.
Renderings and decisions are replaced from the file, since content/
is still the master copy. A sentence's status is set only when it is created:
once review starts, the review trail owns it and a re-import never resets it.

A file is imported only if it has changed since it was last imported
(ContentFile keeps each file's digest), or the texts it is checked against
have, or this command has (IMPORT_VERSION); --all imports every file. A
deploy usually changes a few chapters, and importing all of content/ every
time came to take longer than Render allows a pre-deploy command. With
--budget SECONDS, no new file is started once that long has passed: the rest
are left for the next run, so a deploy after a big change (or the first one,
with no digests yet) still finishes, and the next deploys catch up.

Afterwards the search tables are brought up to date (translation/search.py)
from all of content/ and articles/, whichever files were imported: only the
entries whose documents changed are rewritten, or all of them with --all.
"""
import hashlib
import json
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from owb import refs, validate
from texts.models import Edition, Word
from translation import search
from translation.models import ContentFile, Decision, Rendering, Sentence

TEXT_ID_EDITION = {"SBLGNT@v1.2": "sblgnt", "WLC@macula-hebrew": "wlc"}
# Raise when save() or validate_records() changes what they do with a file,
# so the next deploy imports every file again.
IMPORT_VERSION = 1


class Command(BaseCommand):
    help = "Import the sentence records in content/ into the database."

    def add_arguments(self, parser):
        parser.add_argument("paths", nargs="*", help="Content files (default: content/*/*.json)")
        parser.add_argument("--if-texts-loaded", action="store_true",
                            help="Skip quietly if import_texts has not been run yet")
        parser.add_argument("--all", action="store_true", dest="everything",
                            help="Import files even if unchanged, and rewrite every search entry")
        parser.add_argument("--budget", type=float, metavar="SECONDS",
                            help="Start no new file after this long; the rest wait for the next run")

    def handle(self, *args, paths, if_texts_loaded=False, everything=False, budget=None, **options):
        started = time.monotonic()
        if if_texts_loaded and not Word.objects.exists():
            self.stdout.write("No source texts in the database yet; run import_texts, "
                              "then import_content. Nothing imported.")
            return
        files = paths or sorted(str(p) for p in (settings.REPO_ROOT / "content").glob("*/*.json"))
        if not files:
            raise CommandError("No content files found")
        total = unchanged = 0
        loaded = set(Edition.objects.filter(words__isnull=False).distinct().values_list("code", flat=True))
        editions = {e.code: e for e in Edition.objects.all()}
        imported = dict(ContentFile.objects.values_list("path", "digest"))
        texts = " ".join(sorted(f"{e.code}@{e.source_commit}" for e in editions.values()))
        left = []
        for i, path in enumerate(files):
            data = open(path, "rb").read()
            name = self.relative(path)
            digest = hashlib.sha256(f"{IMPORT_VERSION} {texts}\n".encode() + data).hexdigest()
            if not everything and imported.get(name) == digest:
                unchanged += 1
                continue
            if budget is not None and time.monotonic() - started > budget:
                left = files[i:]
                break
            records = json.loads(data.decode("utf-8"))["records"]
            missing = sorted({TEXT_ID_EDITION[r["source"]["text_id"]] for r in records} - loaded)
            if missing:
                message = (f"{path}: the {', '.join(missing)} text is not in the database; "
                           f"run import_texts {' '.join(missing)}")
                if if_texts_loaded:
                    self.stdout.write(f"{message}. Skipped.")
                    continue
                raise CommandError(message)
            errors = self.validate_records(records)
            if errors:
                for e in errors:
                    self.stderr.write(f"{path}: {e}")
                raise CommandError(f"{path}: {len(errors)} error(s); nothing imported from it")
            with transaction.atomic():
                self.save(records, editions)
                ContentFile.objects.update_or_create(path=name, defaults={"digest": digest})
            total += len(records)
            self.stdout.write(f"{path}: {len(records)} records")
        self.stdout.write(f"{total} records imported" + (f"; {unchanged} files unchanged" if unchanged else ""))
        if left:
            self.stdout.write(f"Budget of {budget:.0f} s used up: {len(left)} file(s) left for the next "
                              f"run, from {left[0]}")
        self.stdout.flush()
        changes = search.rebuild(full=everything)
        self.stdout.write("search: " + ", ".join(
            f"{lang} {c.entries} (+{c.added} -{c.removed})" for lang, c in changes.items()))

    @staticmethod
    def relative(path):
        path = Path(path).resolve()
        try:
            return path.relative_to(settings.REPO_ROOT.resolve()).as_posix()
        except ValueError:
            return path.as_posix()

    def validate_records(self, records):
        verse_ids = {v for r in records for v in r.get("refs", [])}
        verses = {(ref.book, ref.chapter, ref.verse) for ref in map(refs.parse, verse_ids)}
        # One query for the file's chapters, rather than one for each verse.
        by_verse = {}
        for book, chapter in {(b, c) for b, c, _ in verses}:
            for w in Word.objects.filter(book=book, chapter=chapter):
                if (w.book, w.chapter, w.verse) in verses:
                    by_verse.setdefault((w.book, w.chapter, w.verse), {})[w.id] = w
        if not by_verse:
            return ["no source words in the database for these verses; run import_texts first"]
        errors = []
        for record in records:
            mine = {}
            for vid in record.get("refs", []):
                ref = refs.parse(vid)
                mine.update(by_verse.get((ref.book, ref.chapter, ref.verse), {}))
            # Greek and Hebrew quoted in notes may come from anywhere in the
            # Bible, and the database may hold only the words for content/;
            # owb.validate checks them against the full MACULA data in CI.
            errors += [f"{record.get('id')}: {e}"
                       for e in validate.validate_record(record, mine, original_language=False)]
        return errors

    def save(self, records, editions):
        """Save one file's records, a handful of queries for the whole file."""
        records = list({r["id"]: r for r in records}.values())
        sentences = []
        for record in records:
            first = refs.parse(record["refs"][0])
            source = record["source"]
            sentences.append(Sentence(
                record_id=record["id"], book=first.book, chapter=first.chapter, verse=first.verse,
                number=int(record["id"].rsplit(".s", 1)[1]), refs=record["refs"],
                source_edition=editions[TEXT_ID_EDITION[source["text_id"]]],
                source_text_id=source["text_id"], tokens=source["tokens"],
                source_text=source.get("text", ""), literal_gloss=record["literal_gloss"],
                alignments=record.get("alignments", []), status=record["status"]))
        # A sentence already in the database keeps its status: the update
        # leaves it out.
        Sentence.objects.bulk_create(
            sentences, update_conflicts=True, unique_fields=["record_id"],
            update_fields=["book", "chapter", "verse", "number", "refs", "source_edition",
                           "source_text_id", "tokens", "source_text", "literal_gloss", "alignments",
                           "updated_at"],
            batch_size=2000)
        Rendering.objects.filter(sentence__in=sentences).delete()
        Decision.objects.filter(sentence__in=sentences).delete()
        Rendering.objects.bulk_create(
            (Rendering(sentence=sentence, language=lang, level=level, text=text)
             for sentence, record in zip(sentences, records)
             for lang, levels in record["renderings"].items() for level, text in levels.items()),
            batch_size=2000)
        Decision.objects.bulk_create(
            (Decision(sentence=sentence, key=d["id"], order=i, layer=d["layer"],
                      language=d["language"] or "", levels=d.get("levels", []),
                      category=d["category"], tokens=d["tokens"], choice=d["choice"],
                      alternatives=d["alternatives"], reason=d["reason"],
                      uncertain=d["uncertain"], footnote=d["footnote"])
             for sentence, record in zip(sentences, records) for i, d in enumerate(record["decisions"])),
            batch_size=2000)
