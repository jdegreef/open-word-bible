"""Reader-setting alternatives inside translation text.

A span looks like {{gender:all people|men}}: a setting name, then options
separated by "|". The first option is the default. A settings dict maps a
setting name to the index of the option to show. A setting name not in
SETTINGS, a setting missing from the dict, or an index out of range all show
the default.
"""
import re
from typing import NamedTuple

SETTINGS = ("gender", "christos", "divine_name", "units", "deity_pronoun", "spelling")

SPAN = re.compile(r"\{\{([a-z_]+):([^{}]*)\}\}")

# A sentence that crosses a verse boundary marks where each later verse
# starts with a USFM-style marker: "... children of God \v 13 children born ...".
VERSE = re.compile(r"\\v (\d+) ?")


class Span(NamedTuple):
    setting: str
    options: tuple
    start: int
    end: int


def spans(text):
    """List every {{setting:a|b}} span in text."""
    return [Span(m[1], tuple(m[2].split("|")), m.start(), m.end())
            for m in SPAN.finditer(text)]


def stray_braces(text):
    """True if text has "{{" or "}}" outside a well-formed span."""
    rest = SPAN.sub("", text)
    return "{{" in rest or "}}" in rest


def verse_markers(text):
    """The verse numbers marked inside text, in order."""
    return [int(m[1]) for m in VERSE.finditer(text)]


def split_verses(text):
    """Split text at verse markers: [(None, first part), (13, rest), ...]."""
    parts, verse, pos = [], None, 0
    for m in VERSE.finditer(text):
        parts.append((verse, text[pos:m.start()].rstrip()))
        verse, pos = int(m[1]), m.end()
    parts.append((verse, text[pos:]))
    return parts


def render(text, settings=None):
    settings = settings or {}

    def choose(m):
        options = m[2].split("|")
        index = settings.get(m[1], 0) if m[1] in SETTINGS else 0
        return options[index] if isinstance(index, int) and 0 <= index < len(options) else options[0]

    return SPAN.sub(choose, text)
