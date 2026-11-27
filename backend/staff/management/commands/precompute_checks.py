"""Measure every reading language's content checks after an import and keep
them, so the admin's Checks page opens at once.

The Checks page (staff/checks.py) takes 10-15 seconds a language to measure
on the whole Bible, which is most of the web server's time for a request.
The owb-import job (backend/import_job.sh) runs this after import_content
and before warm_admin; it keeps each answer in a ChecksAnswer row (and the
cache), which the page reads.

    python manage.py precompute_checks [--deadline EPOCH] [--lang es ...] [--force]

A language whose kept answer is for the content as it is now is skipped, so
a run after an import that changed nothing takes a second or two. Nothing
here fails the job: a language that errors is reported and the next one is
tried, and none is started after --deadline; the page measures any that are
left when it is first opened, as it did before.
"""
import time

from django.core.management.base import BaseCommand, CommandError

from owb import languages
from staff import checks


class Command(BaseCommand):
    help = "Measure and keep each reading language's content checks, for the admin's Checks page."

    def add_arguments(self, parser):
        parser.add_argument("--deadline", type=float, default=0,
                            help="Start no language after this time (seconds since the epoch)")
        parser.add_argument("--lang", action="append", default=[],
                            help="Only this language (repeat for more); every reading language by default")
        parser.add_argument("--force", action="store_true", help="Measure even languages whose answer is current")

    def handle(self, *args, deadline, lang, force, **options):
        unknown = [code for code in lang if code not in languages.READING]
        if unknown:
            raise CommandError(f"Not a reading language: {', '.join(unknown)}")
        started = time.perf_counter()
        measured = current = failed = 0
        for code in lang or list(languages.READING):
            if deadline and time.time() > deadline:
                self.stdout.write(f"Stopped at the deadline before {code}; the page measures the rest when opened.")
                break
            try:
                took = checks.precompute(code, force=force)
            except Exception as e:   # noqa: BLE001 -- one language must not stop the rest
                failed += 1
                self.stdout.write(f"FAIL {code}: {e.__class__.__name__}: {e}")
                continue
            if took is None:
                current += 1
                self.stdout.write(f"  ok {code}: current")
            else:
                measured += 1
                self.stdout.write(f"  ok {code}: measured in {took:.1f} s")
        self.stdout.write(f"Content checks: {measured} measured, {current} already current"
                          + (f", {failed} failed" if failed else "")
                          + f", in {time.perf_counter() - started:.0f} s.")
