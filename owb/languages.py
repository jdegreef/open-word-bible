"""The languages of Open Word Bible, from data/languages.json.

READING is the languages the translation is made into, in the site's order
(English first); ORIGINAL the languages it is made from. Adding a reading
language means adding it to data/languages.json, writing its catalog
(i18n/<code>.json), and giving it book names (data/books.json) and grammar
words (owb/morph.py); the site, the validator and the backend read the list
from here. The backend's reviewer roles check the list in the database, so
a new language also needs `manage.py makemigrations accounts`.
"""
import json
from pathlib import Path

_DATA = json.loads((Path(__file__).resolve().parents[1] / "data" / "languages.json")
                   .read_text(encoding="utf-8"))

# Code -> entry ({"code", "name", "native", ...}), in order.
READING = {lang["code"]: lang for lang in _DATA["reading"]}
ORIGINAL = {lang["code"]: lang for lang in _DATA["original"]}

# The reading languages' codes: ("en", "es", ...).
CODES = tuple(READING)


def native(code):
    """A reading language's own name: "Español"."""
    return READING[code]["native"]


def settings(code):
    """The reader settings only this language has, each with its options'
    labels: {"plural_you": ["ustedes", "vosotros"]} for Spanish."""
    return READING[code].get("settings", {})
