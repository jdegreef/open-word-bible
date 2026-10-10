"""Load the sentence records in content/ into the database.

    python manage.py import_content
    python manage.py import_content --if-texts-loaded   # run on every deploy

Every record is checked first with owb.validate against the words already in
the database (run import_texts before this). A file with any error is not
imported. With --if-texts-loaded, the command does nothing (and succeeds)
while no source words are in the database yet, so a fresh deploy is not
blocked before import_texts has run. Renderings and decisions are replaced from the file, since content/
is still the master copy. A sentence's status is set only when it is created:
once review starts, the review trail owns it and a re-import never resets it.
"""
import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from owb import refs, validate
from texts.models import Edition, Word
from translation.models import Decision, Rendering, Sentence

TEXT_ID_EDITION = {"SBLGNT@v1.2": "sblgnt"}


class Command(BaseCommand):
    help = "Import the sentence records in content/ into the database."

    def add_arguments(self, parser):
        parser.add_argument("paths", nargs="*", help="Content files (default: content/*/*.json)")
        parser.add_argument("--if-texts-loaded", action="store_true",
                            help="Skip quietly if import_texts has not been run yet")

    def handle(self, *args, paths, if_texts_loaded=False, **options):
        if if_texts_loaded and not Word.objects.exists():
            self.stdout.write("No source texts in the database yet; run import_texts, "
                              "then import_content. Nothing imported.")
            return
        files = paths or sorted(str(p) for p in (settings.REPO_ROOT / "content").glob("*/*.json"))
        if not files:
            raise CommandError("No content files found")
        total = 0
        for path in files:
            records = json.loads(open(path, encoding="utf-8").read())["records"]
            errors = self.validate_records(records)
            if errors:
                for e in errors:
                    self.stderr.write(f"{path}: {e}")
                raise CommandError(f"{path}: {len(errors)} error(s); nothing imported from it")
            with transaction.atomic():
                for record in records:
                    self.save(record)
            total += len(records)
            self.stdout.write(f"{path}: {len(records)} records")
        self.stdout.write(f"{total} records imported")

    def validate_records(self, records):
        verse_ids = {v for r in records for v in r.get("refs", [])}
        known = {}
        for vid in verse_ids:
            ref = refs.parse(vid)
            for w in Word.objects.filter(book=ref.book, chapter=ref.chapter, verse=ref.verse):
                known[w.id] = w
        if not known:
            return ["no source words in the database for these verses; run import_texts first"]
        errors = []
        for record in records:
            mine = {}
            for vid in record.get("refs", []):
                ref = refs.parse(vid)
                mine.update({k: w for k, w in known.items()
                             if (w.book, w.chapter, w.verse) == (ref.book, ref.chapter, ref.verse)})
            # Greek and Hebrew quoted in notes may come from anywhere in the
            # Bible, and the database may hold only the words for content/;
            # owb.validate checks them against the full MACULA data in CI.
            errors += [f"{record.get('id')}: {e}"
                       for e in validate.validate_record(record, mine, original_language=False)]
        return errors

    def save(self, record):
        first = refs.parse(record["refs"][0])
        source = record["source"]
        edition = Edition.objects.get(code=TEXT_ID_EDITION[source["text_id"]])
        fields = dict(
            book=first.book, chapter=first.chapter, verse=first.verse,
            number=int(record["id"].rsplit(".s", 1)[1]), refs=record["refs"],
            source_edition=edition, source_text_id=source["text_id"],
            tokens=source["tokens"], source_text=source.get("text", ""),
            literal_gloss=record["literal_gloss"])
        sentence, created = Sentence.objects.update_or_create(
            record_id=record["id"], defaults=fields,
            create_defaults=dict(fields, status=record["status"]))
        sentence.renderings.all().delete()
        sentence.decisions.all().delete()
        Rendering.objects.bulk_create(
            Rendering(sentence=sentence, language=lang, level=level, text=text)
            for lang, levels in record["renderings"].items() for level, text in levels.items())
        Decision.objects.bulk_create(
            Decision(sentence=sentence, key=d["id"], order=i, layer=d["layer"],
                     language=d["language"] or "", levels=d.get("levels", []),
                     category=d["category"], tokens=d["tokens"], choice=d["choice"],
                     alternatives=d["alternatives"], reason=d["reason"],
                     uncertain=d["uncertain"], footnote=d["footnote"])
            for i, d in enumerate(record["decisions"]))
        return created
