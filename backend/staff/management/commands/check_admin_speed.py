"""Open every admin page's API, as a super admin, under the web server's
statement limit, and fail if one errors or is slow.

The backend tests run on a handful of sentences, where a query that takes
27 seconds on the whole Bible passes; the admin's Coverage, Key terms and
Consistency pages failed in production that way. CI's nightly job
(.github/workflows/admin-speed.yml) imports all of content/ and runs this.

    python manage.py check_admin_speed [--limit 5] [--cold]

Each GET endpoint in staff/urls.py is called once, with a book, verse or
sentence filled in where its path takes one, plus the EXTRA addresses
below. Endpoints that take only POST, or an id of a row that may not
exist, are left out. A temporary super admin account makes the calls and
is deleted afterwards.
"""
import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.test import Client, override_settings
from django.urls import get_resolver

from accounts.models import ApiToken, Role, new_secret
from translation.models import Sentence

# Addresses with a query worth timing as well as the bare one.
EXTRA = [
    "search/?q=love", "verses/?q=JHN.3.16", "consistency/?lang=es", "decisions/?all=1",
    "export/preview/?book=JHN", "review/?layer=en", "history/release-notes/?lang=en&since=2026-01-01",
]
# Answers that may stream a large file, or that act; not timed.
SKIP = {"export/file/", "jobs/bulk/", "team/invite/"}
USERNAME = "admin-speed-check@localhost"


def addresses():
    """Every GET admin address to time, in urls.py order, then EXTRA."""
    staff = next(p for p in get_resolver().url_patterns if str(p.pattern) == "api/admin/")
    record = Sentence.objects.filter(book="JHN").values_list("record_id", flat=True).first() or "JHN.3.16.s1"
    out = []
    for p in staff.url_patterns:
        pattern = str(p.pattern)
        methods = [m for m in p.callback.cls().allowed_methods if m != "OPTIONS"]
        if pattern in SKIP or "GET" not in methods or "<int:" in pattern:
            continue
        out.append(pattern.replace("<str:code>", "JHN").replace("<str:vid>", "JHN.3.16")
                   .replace("<str:record_id>", record))
    return out + EXTRA


class Command(BaseCommand):
    help = "Time every admin GET endpoint under the web server's statement limit."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=float, default=5.0,
                            help="Fail if an endpoint takes longer than this many seconds (default 5)")
        parser.add_argument("--cold", action="store_true",
                            help="Empty the cache first, as after a deploy that changed the content")

    def handle(self, *args, limit, cold, **options):
        # manage.py commands run without the web server's statement limit
        # (config/settings.py statement_timeout_ms); this one needs it.
        with connection.cursor() as cursor:
            cursor.execute("SET statement_timeout = 15000")
        if cold:
            cache.clear()
        User = get_user_model()
        User.objects.filter(username=USERNAME).delete()
        user = User.objects.create(username=USERNAME, email=USERNAME)
        Role.objects.create(user=user, kind=Role.Kind.SUPER_ADMIN)
        secret, key_hash = new_secret()
        ApiToken.objects.create(user=user, key_hash=key_hash, label="check_admin_speed")
        client = Client(HTTP_AUTHORIZATION=f"Bearer {secret}")
        problems = []
        try:
            with override_settings(ALLOWED_HOSTS=["*"]):
                for path in addresses():
                    url = "/api/admin/" + path
                    start = time.perf_counter()
                    status = client.get(url).status_code
                    took = time.perf_counter() - start
                    bad = status >= 500 or took > limit
                    self.stdout.write(f"{'FAIL' if bad else 'ok':>4} {status} {took * 1000:8.0f} ms  {url}")
                    if bad:
                        problems.append(f"{url}: {status} in {took:.1f} s")
        finally:
            user.delete()
        if problems:
            raise CommandError(f"{len(problems)} admin endpoint(s) failed or took over {limit:g} s:\n  "
                               + "\n  ".join(problems))
        self.stdout.write(f"Every admin endpoint answered within {limit:g} s.")
