"""warm_admin: the admin's slow pages opened once after a deploy's import."""
import io
import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command

from staff import consistency
from staff.management.commands import warm_admin

from .test_admin import AdminTestCase, sentence


class WarmAdminTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        sentence("JHN.1.1.s1", ("en", "fr"))

    def run_warm(self, **options):
        out = io.StringIO()
        call_command("warm_admin", stdout=out, **options)
        return out.getvalue()

    def test_opens_every_page_and_leaves_no_account(self):
        out = self.run_warm()
        self.assertIn(f"Warmed {len(warm_admin.pages())} admin page(s)", out)
        self.assertNotIn("FAIL", out)
        self.assertFalse(get_user_model().objects.filter(username=warm_admin.USERNAME).exists())
        # What it opened is kept for the first person in.
        self.assertIsNotNone(cache.get(f"staff.terms.{consistency.TERMS_DIGEST}.{consistency._stamp()}"))

    def test_starts_nothing_after_the_deadline(self):
        out = self.run_warm(deadline=time.time() - 1)
        self.assertIn("Stopped at the deadline before overview/", out)
        self.assertIn("Warmed 0 admin page(s)", out)

