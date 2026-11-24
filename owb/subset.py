"""A subset of the books, for tests: OWB_ONLY_BOOKS="GEN,JHN" makes the
site build (scripts/build_site.py chapters()) and import_content read only
those books' files in content/. Unset or empty, every book.

The backend tests set it (backend_tests/__init__.py): importing all of
content/ and building search from it in every language came to take 17
minutes before the first search test, and the job neared its 45-minute
limit as languages were added. .github/workflows/backend-full.yml runs the
tests on everything each night.
"""
import os


def only_books():
    """The books OWB_ONLY_BOOKS names, or None for all of them."""
    names = {b.strip().upper() for b in os.environ.get("OWB_ONLY_BOOKS", "").split(",") if b.strip()}
    return frozenset(names) or None


def content_files(content_dir):
    """content_dir/<BOOK>/*.json, sorted, for the books only_books() keeps."""
    keep = only_books()
    return sorted(p for p in content_dir.glob("*/*.json") if keep is None or p.parent.name in keep)
