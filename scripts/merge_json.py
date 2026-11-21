#!/usr/bin/env python3
"""A git merge driver for the translation's JSON (content/ and data/).

Pull requests drafted in parallel often edit the same file: two languages of
one chapter, or headings for one book in several languages. Each adds its
own keys (renderings.<lang>, its r-<lang>-N decisions), so git's line merge
conflicts where the meaning doesn't. This merges the parsed JSON instead:

- an object merges key by key; keys only one side added are kept, in place;
- a list whose items all have a unique "id" (records, decisions) merges item
  by item, the same way;
- any other list merges when both sides only appended to it;
- a value both sides changed differently is a real conflict.

On a real conflict, or a file that isn't JSON, it falls back to git's own
line merge (conflict markers, a non-zero exit) and names the path on stderr.
The output is written as the repository writes JSON: indent 2, UTF-8, a
final newline.

Registered by .claude/hooks/session-start.sh, or by hand:

    git config merge.owbjson.driver "python3 scripts/merge_json.py %O %A %B %P"

.gitattributes then applies it to content/ and data/. Without that config
line git ignores the attribute and merges lines as usual.
"""
import json
import subprocess
import sys

MISSING = object()   # a key or item that isn't there (added or deleted)


class Conflict(Exception):
    """Both sides changed the same value differently; the message is its path."""


def _ids(items):
    """The items' ids, if every item is an object with a unique "id"."""
    if not all(isinstance(x, dict) and "id" in x for x in items):
        return None
    ids = [x["id"] for x in items]
    return ids if len(set(ids)) == len(ids) else None


def _order(ours, theirs, base):
    """Every key of ours and theirs, in ours' order. A key ours lacks goes
    after the key it follows in theirs, and after anything new that is
    already there, so ours' additions come before theirs'."""
    order = list(ours)
    for i, k in enumerate(theirs):
        if k in order:
            continue
        pos = 0
        for prev in reversed(theirs[:i]):
            if prev in order:
                pos = order.index(prev) + 1
                break
        while pos < len(order) and order[pos] not in base:
            pos += 1
        order.insert(pos, k)
    return order


def merge(base, ours, theirs, path=()):
    """The three-way merge of parsed JSON values; MISSING for an absent one.
    Raises Conflict when both sides changed one value differently."""
    if ours == theirs:
        return ours
    if base == ours:
        return theirs
    if base == theirs:
        return ours
    if isinstance(ours, dict) and isinstance(theirs, dict):
        b = base if isinstance(base, dict) else {}
        out = {}
        for k in _order(list(ours), list(theirs), b):
            v = merge(b.get(k, MISSING), ours.get(k, MISSING), theirs.get(k, MISSING), path + (k,))
            if v is not MISSING:
                out[k] = v
        return out
    if isinstance(ours, list) and isinstance(theirs, list):
        b = base if isinstance(base, list) else []
        bi, oi, ti = _ids(b), _ids(ours), _ids(theirs)
        if bi is not None and oi is not None and ti is not None:
            bm = {x["id"]: x for x in b}
            om = {x["id"]: x for x in ours}
            tm = {x["id"]: x for x in theirs}
            out = []
            for k in _order(oi, ti, bm):
                v = merge(bm.get(k, MISSING), om.get(k, MISSING), tm.get(k, MISSING), path + (k,))
                if v is not MISSING:
                    out.append(v)
            return out
        n = len(b)
        if ours[:n] == b and theirs[:n] == b:
            return ours + [x for x in theirs[n:] if x not in ours[n:]]
    raise Conflict("/".join(map(str, path)) or "(top level)")


def _load(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return json.loads(text) if text.strip() else MISSING


def main(argv):
    base, ours, theirs, name = argv[1:5]
    try:
        result = merge(_load(base), _load(ours), _load(theirs))
    except (ValueError, Conflict) as e:
        print(f"merge_json: {name}: {e}; falling back to a line merge", file=sys.stderr)
        return subprocess.call(["git", "merge-file", "-L", "ours", "-L", "base", "-L", "theirs",
                                ours, base, theirs])
    with open(ours, "w", encoding="utf-8") as f:
        if result is not MISSING:
            f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
