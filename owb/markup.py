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


# Quotations: where someone's words begin and end in a rendering. The
# outermost marks are straight double quotes (English, Swahili, Vietnamese,
# Korean) or guillemets (Spanish, French); quotations inside them use single
# quotes, curly quotes, or straight double quotes again at the third level.
# A straight quote opens at the start or after a space, bracket or dash,
# when a word follows it, and closes anywhere else (as
# build_site.smart_quotes curls it). A straight single quote can also be an
# apostrophe; see quotations().
_QUOTE_CHARS = re.compile("[\"'\u00ab\u00bb\u201c\u201d\u2018\u2019]")
_PAIRS = {"\u00bb": "\u00ab", "\u201d": "\u201c", "\u2019": "\u2018"}


def _opens_here(text, pos):
    return pos == 0 or text[pos - 1].isspace() or text[pos - 1] in "([\u2014-"


def _quotations(text, depth, level=1):
    """quotations() from one starting state, depth quotations deep (0, 1,
    or 2: inside a quotation inside the outer one), as ranges of the
    quotations level deep (1, the outermost; 2, those inside them);
    raises ValueError."""
    outer = "\u00ab" if re.search("[\u00ab\u00bb]", text) else '"'
    inner = "\u201c" if outer == "\u00ab" else "'"
    stack, ranges = [outer, inner][:depth], []
    start = 0
    # A setting span holds no quotation marks (quotations() checks), only
    # apostrophes: {{deity_pronoun:m’|M’}}.
    in_span = {i for s in spans(text) for i in range(s.start, s.end)}
    for m in _QUOTE_CHARS.finditer(text):
        pos, ch = m.start(), m[0]
        after = text[pos + 1:pos + 2]
        if pos in in_span:
            continue
        if ch in "\u00ab\u201c\u2018" or (ch in "\"'" and _opens_here(text, pos)
                                         and after and not after.isspace()):
            if stack and stack[-1] == ch:
                raise ValueError(f"quotation mark at {pos} opens inside a quotation of its own kind")
            stack.append(ch)
            if len(stack) == level:
                start = pos + 1
            continue
        want = _PAIRS.get(ch, ch)
        # A single quote followed by a Latin letter (or a setting span) is an
        # apostrophe ("don't", "qu\u2019{{deity_pronoun:il|Il}}"; Korean sets a
        # particle right after a closing quote), and so is one after a word
        # that closes nothing ("the disciples' feet"), unless it ends a
        # quotation open since before the sentence ('...'"). A curly one
        # (French and Spanish apostrophes) only ever closes a \u2018 it follows.
        if want in "'\u2018" and ((after.isalnum() and after < "\u0250") or after == "{"
                                   or (want not in stack and (after.isspace() or ch == "\u2019"))):
            continue
        if want not in stack and stack and want != stack[0]:
            # A quotation inside the outer one, open since before this
            # sentence began (the Lord's Prayer, Matthew 6:9-13).
            stack.insert(1, want)
            if level == 2:
                ranges, start = [], 0
        elif want not in stack:
            # Open since before this sentence began: everything so far,
            # quotations included, is inside it.
            stack.insert(0, want)
            if len(stack) >= level:
                ranges, start = [], 0
        before = len(stack)
        while stack.pop() != want:
            pass
        if before >= level > len(stack):
            ranges.append((start, pos))
    if len(stack) >= level:
        ranges.append((start, len(text)))
    return ranges


def quotations(text, inside=False, inner=False):
    """The quoted words in text, as [(start, end), ...]: each outermost
    quotation, from after its opening mark to before its closing one,
    without the spaces French sets inside guillemets.

    inside says whether the text begins inside a quotation an earlier
    sentence opened; text with no marks is then one whole quotation. A
    closing mark with nothing open to close says so too, at any depth:
    what came before it, quotations included, is inside that quotation.
    The text can end inside a quotation a later sentence closes. Where the
    marks do not pair from the state inside gives, the others are tried:
    inside text may be two deep (a speaker quoted inside a parable, who
    quotes in turn: Luke 15:18), and either may turn out not to be.

    inner gives the quotations inside the outermost ones instead (the
    words of Jesus as Paul retells them, Acts 22:7), and inside then says
    whether the text begins inside one of those.

    Raises ValueError where they pair from neither (a mark opens a
    quotation of the kind already innermost), or a quotation mark sits
    inside a {{setting:...}} span."""
    for s in spans(text):
        if re.search("[\"\u00ab\u00bb\u201c\u201d]", text[s.start:s.end]):
            raise ValueError(f"quotation mark inside the setting span at {s.start}")
    first = None
    if inner:
        order, level = ((2, 1, 0) if inside else (1, 0, 2)), 2
    else:
        order, level = ((1, 2, 0) if inside else (0, 1)), 1
    for depth in order:
        try:
            ranges = _quotations(text, depth, level)
            break
        except ValueError as e:
            first = first or e
    else:
        raise first
    out = []
    for s, e in ranges:
        while s < e and text[s].isspace():
            s += 1
        while e > s and text[e - 1].isspace():
            e -= 1
        if e > s:
            out.append((s, e))
    return out


def render(text, settings=None):
    settings = settings or {}

    def choose(m):
        options = m[2].split("|")
        index = settings.get(m[1], 0) if m[1] in SETTINGS else 0
        return options[index] if isinstance(index, int) and 0 <= index < len(options) else options[0]

    return SPAN.sub(choose, text)


def _whole(text, start, end):
    """True if text[start:end] does not begin or end inside a word."""
    inside_before = start > 0 and text[start - 1].isalnum() and text[start].isalnum()
    inside_after = end < len(text) and text[end].isalnum() and text[end - 1].isalnum()
    return not (inside_before or inside_after)


def alignment_ranges(text, targets):
    """Where each alignment's target_span sits in one rendering.

    A short span such as "the" can occur more than once, so a rendering's
    alignments are listed in the order their spans appear, and each is found
    after the end of the one before, as a whole word: "I" is never the start
    of "If". A span may not hold a verse or line marker or cut through a
    setting span. Returns [(start, end), ...]; raises ValueError naming the
    first span that breaks a rule."""
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
        while start >= 0 and not _whole(text, start, start + len(target)):
            start = text.find(target, start + 1)
        if start < 0:
            where = "after the previous alignment" if target in text else "in rendering"
            raise ValueError(f"{i}: target_span {target!r} not found {where}")
        end = start + len(target)
        if any(s.start < start < s.end or s.start < end < s.end for s in whole):
            raise ValueError(f"{i}: target_span {target!r} cuts a setting span")
        ranges.append((start, end))
        at = end
    return ranges
