"""PreToolUse hook: holds Claude to two rules in CLAUDE.md before an edit lands.

1. Never type Hebrew or Greek. Every Greek or Hebrew word that an edit adds
   to content/, data/, docs/ or articles/ must be a form or lemma in the
   pinned source data, the same test owb.validate applies to records
   (check_original_language). Words the edited text already had are let
   through, so moving or reindenting copied text is fine.
2. Nothing is marked reviewed by Claude. An edit to content/ may not add a
   record status other than ai_draft.

Edit, MultiEdit, Write and NotebookEdit are checked, and Bash commands that
name one of those folders. A refused edit exits with status 2; its message
goes back to Claude. CI (owb.validate) stays the backstop: a script Claude
runs can still write files this hook never sees.

The source forms take several seconds to load from vendor/, so they are
cached in vendor/.forms-<key>.txt; the session start hook builds the cache
(--build-cache). Without the pinned sources the first rule is skipped.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from owb import validate  # noqa: E402
from owb.sources import LOCK, vendor_dir  # noqa: E402
from owb.sources import macula_greek, macula_hebrew  # noqa: E402

TEXT_DIRS = ("content/", "data/", "docs/", "articles/")
NOT_DRAFT = [s for s in validate._PROPS["status"]["enum"] if s != "ai_draft"]
STATUS = re.compile(r'"status"\s*:\s*"(%s)"' % "|".join(NOT_DRAFT))
# In a shell command: a non-draft status as a quoted value, and a command
# that writes (sed -i, a redirect, tee, a Python write).
SHELL_STATUS = re.compile(r"""["'](%s)["']""" % "|".join(NOT_DRAFT))
SHELL_WRITES = re.compile(r"\bsed\s+-i|\bperl\s+-i|>|\btee\b|json\.dump|write_text|\.write\(")


def cache_path():
    key = json.dumps([LOCK["macula-greek"], LOCK["macula-hebrew"]], sort_keys=True)
    return vendor_dir() / f".forms-{hashlib.sha256(key.encode()).hexdigest()[:12]}.txt"


def source_forms():
    """Every Greek and Hebrew form and lemma in the pinned sources, or None
    when the sources haven't been fetched."""
    path = cache_path()
    if path.is_file():
        return frozenset(path.read_text(encoding="utf-8").split("\n"))
    try:
        forms = macula_greek.forms() | macula_hebrew.forms()
    except (OSError, subprocess.CalledProcessError):
        return None
    tmp = path.with_suffix(".tmp")
    tmp.write_text("\n".join(sorted(forms)), encoding="utf-8")
    tmp.replace(path)
    return forms


def words(text):
    """The Greek and Hebrew words in text, as owb.validate splits them."""
    out = []
    for pattern, _ in validate._SCRIPTS.values():
        out += pattern.findall(text)
    return out


def relative(path):
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None


def change(tool, tool_input):
    """(path relative to the repo or None, text added, text replaced)."""
    if tool == "Bash":
        return None, tool_input.get("command", ""), ""
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    rel = relative(path) if path else None
    if tool == "Write":
        p = Path(path)
        old = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
        return rel, tool_input.get("content", ""), old
    if tool == "Edit":
        return rel, tool_input.get("new_string", ""), tool_input.get("old_string", "")
    if tool == "MultiEdit":
        edits = tool_input.get("edits", [])
        return (rel, "\n".join(e.get("new_string", "") for e in edits),
                "\n".join(e.get("old_string", "") for e in edits))
    if tool == "NotebookEdit":
        return rel, tool_input.get("new_source", ""), ""
    return rel, "", ""


def problems(tool, tool_input, forms=source_forms):
    """The reasons to refuse this tool call; empty when it may go ahead."""
    rel, new, old = change(tool, tool_input)
    if tool == "Bash":
        in_text_dirs = any(d in new for d in TEXT_DIRS)
        in_content = "content/" in new
    else:
        in_text_dirs = rel is not None and rel.startswith(TEXT_DIRS)
        in_content = rel is not None and rel.startswith("content/")
    out = []

    if in_text_dirs:
        added = sorted(set(words(new)) - set(words(old)))
        if added:
            known = forms()
            unknown = [w for w in added if known is not None and w not in known]
            if unknown:
                out.append(
                    "Greek or Hebrew not found in the pinned source data: "
                    + ", ".join(unknown[:10]) + (" ..." if len(unknown) > 10 else "")
                    + ". CLAUDE.md: never type Hebrew or Greek. Look the word up by "
                    "script (data/grc, data/hbo, owb.sources) and copy the data's form.")

    if in_content:
        if tool == "Bash":
            if SHELL_STATUS.search(new) and SHELL_WRITES.search(new):
                out.append("This command looks like it sets a record status other than "
                           "ai_draft. CLAUDE.md: nothing is marked reviewed by Claude.")
        elif len(STATUS.findall(new)) > len(STATUS.findall(old)):
            out.append("This edit sets a record status other than ai_draft. CLAUDE.md: "
                       "nothing is marked reviewed by Claude; records stay ai_draft until "
                       "a named human reviewer approves them.")
    return out


def main():
    if sys.argv[1:] == ["--build-cache"]:
        print("source forms:", "cached" if source_forms() is not None else "sources missing")
        return 0
    event = json.load(sys.stdin)
    found = problems(event.get("tool_name", ""), event.get("tool_input", {}) or {})
    if found:
        print("\n".join(found), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
