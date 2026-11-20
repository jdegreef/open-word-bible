"""Count each book's drafted sentences per language again from the
renderings (translation/counts.py). import_content keeps the counts as it
goes; this repairs them if anything else ever changed renderings."""
from django.core.management.base import BaseCommand

from translation import counts


class Command(BaseCommand):
    help = "Recount drafted sentences per book and language for the admin's progress pages."

    def add_arguments(self, parser):
        parser.add_argument("books", nargs="*", help="Book codes (default: every book)")

    def handle(self, *args, books, **options):
        counts.recount([b.upper() for b in books] or None)
        self.stdout.write("Recounted " + (", ".join(books) if books else "every book"))
