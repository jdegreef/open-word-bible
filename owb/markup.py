"""Reader-setting alternatives inside translation text.

A span looks like {{gender:all people|men}}: a setting name, then options
separated by "|". The first option is the default. A settings dict maps a
setting name to the index of the option to show. A setting name not in
SETTINGS, a setting missing from the dict, or an index out of range all show
the default.
"""
import re
from typing import NamedTuple

# The settings a span may name: each has a control in the reader
# (web/markup.js SETTINGS is the same list).
SETTINGS = ("gender", "christos", "divine_name", "deity_pronoun", "units", "plural_you")

SPAN = re.compile(r"\{\{([a-z_]+):([^{}]*)\}\}")

# A sentence that crosses a verse boundary marks where each later verse
# starts with a USFM-style marker: "... children of God \v 13 children born ...".
VERSE = re.compile(r"\\v (\d+) ?")

# Poetry is set in lines. A line marker "\q " starts a new poetic line inside
# a verse: "the wicked, \q nor stands in the way of sinners". A verse start is
# always a line start, so \q marks only breaks within a verse's text: never
# at the start or end of a rendering, never doubled, never next to a \v
# marker, never inside a {{setting:...}} span or an alignment's target_span.
# A rendering with no \q is prose. Each language and level places its own
# breaks; see docs/english-style.md ("Poetry: lines").
LINE = re.compile(r" ?\\q ?")


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


def line_markers(text):
    """How many line markers text holds."""
    return len(LINE.findall(text))


def split_lines(text):
    """Split text (one verse's part, or any rendering) at its line markers:
    "a, \\q b" -> ["a,", "b"]. Text with no marker is one line."""
    return [part.strip() for part in LINE.split(text)]


def is_poetry(text):
    return bool(LINE.search(text))


def flat(text):
    """Text with its line markers turned into spaces: how a line break reads
    wherever text is shown on one line (search, quotes, share cards, speech)."""
    return LINE.sub(" ", text)


def line_errors(text):
    """What is wrong with text's line markers, as a list of reasons."""
    found = []
    stripped = text.strip()
    if stripped.startswith("\\q"):
        found.append("starts with a line marker")
    if re.search(r"\\q\s*$", stripped):
        found.append("ends with a line marker")
    if re.search(r"\\q\s*\\q", text):
        found.append("doubled line marker")
    if re.search(r"\\q\s*\\v |\\v \d+\s*\\q", text):
        found.append("line marker next to a verse marker (a verse already starts a line)")
    if re.search(r"\\q(?!\s)", text) or re.search(r"\S\\q", text):
        found.append('line marker must stand alone: "... \\q ..."')
    if any("\\q" in text[s.start:s.end] for s in spans(text)):
        found.append("line marker inside a setting span")
    if re.search(r"\\(?![vq] )", text):
        found.append("unknown backslash marker (only \\v N and \\q)")
    return found


def render(text, settings=None):
    settings = settings or {}

    def choose(m):
        options = m[2].split("|")
        index = settings.get(m[1], 0) if m[1] in SETTINGS else 0
        return options[index] if isinstance(index, int) and 0 <= index < len(options) else options[0]

    return SPAN.sub(choose, text)


def alignment_ranges(text, targets):
    """Where each alignment's target_span sits in one rendering.

    A short span such as "the" can occur more than once, so a rendering's
    alignments are listed in the order their spans appear, and each is found
    after the end of the one before. A span may not hold a verse or line marker or
    cut through a setting span. Returns [(start, end), ...]; raises
    ValueError naming the first span that breaks a rule."""
    whole = spans(text)
    ranges, at = [], 0
    for i, target in enumerate(targets):
        if not target.strip():
            raise ValueError(f"{i}: empty target_span")
        if VERSE.search(target):
            raise ValueError(f"{i}: target_span holds a verse marker")
        if "\\q" in target:
            raise ValueError(f"{i}: target_span holds a line marker")
        start = text.find(target, at)
        if start < 0:
            where = "after the previous alignment" if target in text else "in rendering"
            raise ValueError(f"{i}: target_span {target!r} not found {where}")
        end = start + len(target)
        if any(s.start < start < s.end or s.start < end < s.end for s in whole):
            raise ValueError(f"{i}: target_span {target!r} cuts a setting span")
        ranges.append((start, end))
        at = end
    return ranges
