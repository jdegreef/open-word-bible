"""The languages of Open Word Bible, from data/languages.json.

READING is the languages the translation is made into, in the site's order
(English first); ORIGINAL the languages it is made from. Adding a reading
language means adding it to data/languages.json, writing its catalog
(i18n/<code>.json), and giving it book names (data/books.json) and grammar
words (owb/morph.py); the site, the validator and the backend read the list
from here. The backend's reviewer roles check the list in the database, so
a new language also needs `manage.py makemigrations accounts`.

A language written right to left says so with "dir": "rtl" (Hebrew among
the originals; a reading language such as Arabic once one is added); the
others are left to right. Pages in such a language are built with
<html dir="rtl">, and text in a language whose direction differs from what
surrounds it gets its own dir (docs/adding-a-language.md, "Right to left").
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

DIRECTIONS = ("ltr", "rtl")
for _lang in (*_DATA["reading"], *_DATA["original"]):
    if _lang.get("dir", "ltr") not in DIRECTIONS:
        raise ValueError(f"data/languages.json: {_lang['code']}: dir must be one of {DIRECTIONS}")

# Other codes the site tags text with, and the language whose script they
# are written in: the Aramaic passages (arc) and a saved Hebrew word (he)
# are in the Hebrew script.
_SCRIPT_OF = {"arc": "hbo", "he": "hbo"}

# Every code written right to left, reading and original languages and
# their aliases: {"hbo", "arc", "he"} while no reading language is.
RTL = frozenset(code for code, lang in {**READING, **ORIGINAL}.items() if lang.get("dir") == "rtl")
RTL |= {alias for alias, code in _SCRIPT_OF.items() if code in RTL}

# The reading languages written right to left: () while there are none.
RTL_READING = tuple(code for code in CODES if code in RTL)


def native(code):
    """A reading language's own name: "Español"."""
    return READING[code]["native"]


def settings(code):
    """The reader settings only this language has, each with its options'
    labels: {"plural_you": ["ustedes", "vosotros"]} for Spanish."""
    return READING[code].get("settings", {})


def direction(code):
    """"rtl" for a language written right to left, else "ltr". A tag with a
    region or script ("ar-EG") counts as its language."""
    return "rtl" if code.split("-")[0] in RTL else "ltr"


# The digits a reading language shows numbers in, zero to nine, where they
# are not ASCII: {"fa": "۰۱۲۳۴۵۶۷۸۹"}. The records keep ASCII digits; the
# site shows these in their place (build_site.localize_digits, and
# web/site.js OWBDigits for text the scripts add).
DIGITS = {code: lang["digits"] for code, lang in READING.items() if lang.get("digits")}
for _code, _digits in DIGITS.items():
    if len(_digits) != 10:
        raise ValueError(f"data/languages.json: {_code}: digits must be ten characters, zero to nine")


def digits(code):
    """The digits code shows numbers in, zero to nine, or None for ASCII. A
    tag with a region or script ("fa-AF") counts as its language."""
    return DIGITS.get(code.split("-")[0]) if code else None
