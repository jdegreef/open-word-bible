"""Smaller copies of the reader's scripts and style sheets for the built
site: comments, indentation and blank lines taken out. web/ keeps the
commented sources; scripts/build_site.py writes these into site/.

The scripts and styles were served with all their comments: reader.js was
204 KB (54 KB gzipped, 93% of its budget in scripts/check_budgets.py).

Deliberately conservative, with nothing outside the standard library (the
site builds with a bare Python):

- Scripts keep every line break, so automatic semicolon insertion reads the
  code exactly as before; only comments, the whitespace that starts and ends
  a line, runs of spaces and empty lines go. Strings, template literals
  (with their ${...}) and regular expression literals are copied as they
  are.
- Style sheets lose comments, the whitespace around { } ; and , and the
  last ; of a block; other whitespace (which can separate selectors or
  values) becomes one space.

    python3 scripts/minify.py web/reader.js     # prints the smaller copy

tests/test_minify.py checks it on the cases that trip such tools, and that
every web/ script still parses (node --check) and the reader's tests pass
on the smaller copies.
"""
import re
import sys

# Before a "/", these leave an expression unfinished: a regular expression
# literal follows, not a division.
_REGEX_AFTER_PUNCT = set("(,=:[!&|?{};+-*%<>~^")
_REGEX_AFTER_WORDS = {"return", "typeof", "case", "do", "else", "in", "of", "new", "delete", "void",
                      "throw", "instanceof", "yield", "await"}


def js(source):
    """source without comments, indentation or blank lines."""
    out = []
    i, n = 0, len(source)
    last = ""          # the last significant character written
    word = ""          # the last identifier written, for "return /x/"
    braces = []        # for each open template ${, the brace depth inside it
    depth = 0

    def emit(text):
        nonlocal last
        out.append(text)
        stripped = text.rstrip(" \t\n")
        if stripped:
            last = stripped[-1]

    def string(quote, start):
        j = start + 1
        while j < n:
            c = source[j]
            if c == "\\":
                j += 2
                continue
            if c == quote:
                return j + 1
            if c == "\n" and quote != "`":
                raise ValueError(f"unterminated string at {start}")
            if quote == "`" and c == "$" and source[j + 1:j + 2] == "{":
                return j + 2   # into the expression; the template resumes at its }
            j += 1
        raise ValueError(f"unterminated string at {start}")

    def template_rest(start):
        """From inside a template literal (after a ${...}'s closing brace)
        to its end or its next ${."""
        j = start
        while j < n:
            c = source[j]
            if c == "\\":
                j += 2
                continue
            if c == "`":
                return j + 1, False
            if c == "$" and source[j + 1:j + 2] == "{":
                return j + 2, True
            j += 1
        raise ValueError("unterminated template literal")

    def regex(start):
        j, in_class = start + 1, False
        while j < n:
            c = source[j]
            if c == "\\":
                j += 2
                continue
            if c == "\n":
                raise ValueError(f"unterminated regular expression at {start}")
            if in_class:
                in_class = c != "]"
            elif c == "[":
                in_class = True
            elif c == "/":
                j += 1
                while j < n and (source[j].isalnum() or source[j] in "_$"):
                    j += 1   # flags
                return j
            j += 1
        raise ValueError(f"unterminated regular expression at {start}")

    while i < n:
        c = source[i]
        if c in " \t\r":
            j = i
            while j < n and source[j] in " \t\r":
                j += 1
            # One space between tokens on a line; none at its start or end.
            if out and out[-1][-1:] not in ("\n", " ") and j < n and source[j] != "\n" \
                    and source[j:j + 2] not in ("//", "/*"):
                out.append(" ")
            i = j
            continue
        if c == "\n":
            while out and out[-1].endswith(" "):
                out[-1] = out[-1][:-1]
            if out and not out[-1].endswith("\n"):
                out.append("\n")
            i += 1
            continue
        if source.startswith("//", i):
            j = source.find("\n", i)
            i = n if j < 0 else j
            continue
        if source.startswith("/*", i):
            j = source.find("*/", i + 2)
            if j < 0:
                raise ValueError(f"unterminated comment at {i}")
            # A comment between two tokens on one line still separates them.
            if out and out[-1][-1:] not in ("\n", " ") and "\n" not in source[i:j]:
                out.append(" ")
            elif "\n" in source[i:j] and out and not out[-1].endswith("\n"):
                out.append("\n")
            i = j + 2
            continue
        if c in "'\"`":
            j = string(c, i)
            emit(source[i:j])
            if c == "`" and source[j - 2:j] == "${":
                braces.append(depth)
                depth += 1
            word = ""
            i = j
            continue
        if c == "/":
            if not last or last in _REGEX_AFTER_PUNCT or (word in _REGEX_AFTER_WORDS and last == word[-1:]):
                j = regex(i)
                emit(source[i:j])
                word = ""
                i = j
                continue
            emit(c)
            word = ""
            i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if braces and braces[-1] == depth:
                # The end of a template's ${...}: the template goes on.
                braces.pop()
                j, again = template_rest(i + 1)
                emit(source[i:j])
                if again:
                    braces.append(depth)
                    depth += 1
                word = ""
                i = j
                continue
        if c.isalnum() or c in "_$":
            j = i
            while j < n and (source[j].isalnum() or source[j] in "_$"):
                j += 1
            word = source[i:j]
            emit(word)
            i = j
            continue
        emit(c)
        word = ""
        i += 1
    text = "".join(out).strip("\n")
    return re.sub(r"\n{2,}", "\n", text) + "\n"


_CSS_TOKEN = re.compile(r"""("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')|(/\*.*?\*/)|(\s+)|([^"'/\s]+|/)""", re.S)


def css(source):
    """source without comments, with whitespace cut down."""
    parts = []
    for m in _CSS_TOKEN.finditer(source):
        quoted, comment, space, other = m.groups()
        if comment:
            # A comment may sit between two words: they stay apart.
            if parts and parts[-1] != " ":
                parts.append(" ")
            continue
        if space:
            if parts and parts[-1] != " ":
                parts.append(" ")
            continue
        parts.append(quoted or other)
    text = "".join(parts).strip()
    # No space is needed around these, or after a declaration's ":".
    text = re.sub(r" ?([{};]) ?", r"\1", text)
    text = re.sub(r" ?, ?", ",", text)
    text = re.sub(r";}", "}", text)
    return text + "\n"


def minify(name, text):
    """The smaller copy of web/<name>."""
    if name.endswith(".js"):
        return js(text)
    if name.endswith(".css"):
        return css(text)
    return text


if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        sys.stdout.write(minify(path, f.read()))
