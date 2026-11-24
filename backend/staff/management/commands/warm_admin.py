"""Fill the admin's kept answers after an import, before anyone opens it.

Coverage, the dashboard, key terms, consistency and the review queues are
counted when first asked for and then kept until the content changes. An
import changes it, so the first person into the admin afterwards waited
for every count, which is when they most want to see what changed. The
owb-import job (backend/import_job.sh) runs this after import_content.

    python manage.py warm_admin [--deadline EPOCH]

Each address in PAGES is opened once as a temporary super admin, as
check_admin_speed does. Nothing here fails a deploy: a page that errors is
reported and the next one is tried, and none is started after --deadline.
"""
import time

from django.core.management.base import BaseCommand

from owb import languages

from .check_admin_speed import super_admin_client

USERNAME = "admin-warm@localhost"
# What the admin opens on, then what each reading language's reviewers do:
# their language's review queue and consistency, as those pages first show.
PAGES = ["overview/", "attention/", "coverage/", "languages/", "terms/", "consistency/", "review/",
         "checks/", "pace/", "decisions/"]


def pages():
    return PAGES + [p for code in languages.READING if code != "en"
                    for p in (f"review/?layer={code}", f"consistency/?lang={code}")]


class Command(BaseCommand):
    help = "Open the admin's slow pages once so their counts are kept before anyone visits."

    def add_arguments(self, parser):
        parser.add_argument("--deadline", type=float, default=0,
                            help="Start no page after this time (seconds since the epoch)")

    def handle(self, *args, deadline, **options):
        started = time.perf_counter()
        warmed = failed = 0
        with super_admin_client(USERNAME) as client:
            for path in pages():
                if deadline and time.time() > deadline:
                    self.stdout.write(f"Stopped at the deadline before {path}.")
                    break
                start = time.perf_counter()
                try:
                    status = client.get("/api/admin/" + path).status_code
                except Exception as e:   # noqa: BLE001 -- one page must not stop the rest
                    status = e.__class__.__name__
                took = time.perf_counter() - start
                ok = status == 200
                warmed += ok
                failed += not ok
                self.stdout.write(f"{'ok' if ok else 'FAIL':>4} {status} {took * 1000:8.0f} ms  /api/admin/{path}")
        self.stdout.write(f"Warmed {warmed} admin page(s) in {time.perf_counter() - started:.0f} s"
                          + (f"; {failed} failed." if failed else "."))
