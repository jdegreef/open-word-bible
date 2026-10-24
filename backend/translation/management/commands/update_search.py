"""Bring one site language's search entries up to date with content/ and
articles/ (translation/search.py; import_content does every language).

    python manage.py update_search pt          # only the entries that changed
    python manage.py update_search pt --all    # every entry

import_content --separate-processes runs this once per language: one
language's documents fit the API's 512 MB, but every language's in turn in
one process outgrew it, since Python keeps the memory it has used. The last
line written is the language's Change, as JSON.
"""
import json

from django.core.management.base import BaseCommand, CommandError

from translation import search


class Command(BaseCommand):
    help = "Update one site language's search entries."

    def add_arguments(self, parser):
        parser.add_argument("language")
        parser.add_argument("--all", action="store_true", dest="everything", help="Rewrite every entry")

    def handle(self, *args, language, everything=False, **options):
        site = search.site_build(language)
        if language not in site.LANGUAGES:
            raise CommandError(f"{language} is not a site language")
        try:
            change = search._rebuild_language(site, language, everything)
        finally:
            search.site_build()
        self.stdout.write(json.dumps(change._asdict()))
