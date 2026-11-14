"""Text variants: list every text_variant decision and check its footnote.

docs/text-variants.md is the policy. In short, a variant gets a footnote when
a reader would notice the difference: a verse or a passage is added or left
out, a well-known English Bible follows the other reading, or the reading
changes the sense. A difference of spelling, of how the scribes marked a word
to be read, or one that leaves the sense the same gets no footnote.

Each decision is put in one category from the words of its reason (a
heuristic, not a judgement), and the category says whether the policy expects
a footnote:

  stated        the reason itself says "no footnote"                 no footnote
  covered       the reason only points to another verse's note    not judged
  verses        a verse, a passage or an ending added or left out   footnote
  english_bible a well-known English Bible follows the other reading footnote
  quoted        the New Testament quotes the other reading           footnote
  same_sense    the reason says the sense is the same or close       no footnote
  spelling      spelling, a written/read form, a scribal mark        no footnote
  sense         the reason says how the other reading would read    footnote
  versions      ancient translations read another Hebrew word        footnote
  manuscripts   Greek manuscripts differ, sense not stated          not judged
  other         no other reading named (a hard text, a number)       not judged

Usage:
    python3 scripts/variants.py              # summary and inconsistencies
    python3 scripts/variants.py --list       # every decision, tab-separated
    python3 scripts/variants.py --fix        # set footnote flags to the policy
                                             #   (never in --skip books, PSA by default)
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import refs  # noqa: E402

CONTENT = ROOT / "content"

_ADD = r"(?:add|adds|added|omit|omits|omitted|lack|lacks|leave out|leaves out|left out|include|includes|insert|inserts)"
_UNIT = r"(?:the |this |these |a |an |that |whole |entire |all of )*(?:verses?|passage|ending|story)\b"
VERSES = re.compile(
    rf"\b{_ADD}\s+{_UNIT}|\b(?:verses?|passage|ending)\s+(?:is|are)\s+(?:not|absent|missing|present|lacking)\b"
    r"|\b(?:longer|shorter|short|long) ending\b|\bthe verse is (?:present|kept)",
    re.IGNORECASE)
ENGLISH_BIBLE = re.compile(r"King James|\bKJV\b|English Bibles|English versions|older English|"
                           r"many English|Revised Version|\bRSV\b|\bNIV\b|\bESV\b|\bNRSV\b", re.IGNORECASE)
STATED_NONE = re.compile(r"\bno footnote\b", re.IGNORECASE)
SAME_SENSE = re.compile(
    r"(?:meaning|sense|point) (?:is|are|stays|remains) (?:much |nearly |almost |essentially |little |very )?"
    r"(?:the same|unchanged|alike|close|similar)"
    r"|(?:meaning|sense) is (?:little|hardly|not) changed|same (?:meaning|sense)|"
    r"(?:does not|doesn't|do not|did not) (?:change|affect|alter) the (?:meaning|sense)|"
    r"no (?:real |practical )?difference (?:in|to) (?:the )?(?:meaning|sense)|"
    r"\bboth (?:mean|say|give the same)|little difference|"
    r"(?:meaning|sense) is (?:close|nearly the same) either way|close either way|"
    r"either way,? the (?:meaning|sense|point)|the same either way", re.IGNORECASE)
SPELLING = re.compile(r"spell|orthograph|ketiv|qere|written (?:consonants|form|text|letters|Hebrew)|"
                      r"consonants (?:as )?written|scribes?'? (?:marked|mark|margin|note|reading)|margin|"
                      r"large letter|small letter|scribal mark|read aloud|as read, not as written|"
                      r"pronounced|reading tradition|written in a form|Hebrew notes", re.IGNORECASE)
SENSE_CHANGE = re.compile(r"\bwould (?:mean|give|make|picture|say|read|change|turn)(?! the same)|"
                          r"different (?:sense|meaning|picture)|changes? the (?:sense|meaning|picture)|"
                          r"with (?:different|other) vowels", re.IGNORECASE)
# The New Testament quotes the other reading (Genesis 2:24 "the two").
QUOTED = re.compile(r"\b(?:quotes?|quoted|quoting|cites?|cited)\b", re.IGNORECASE)
# A note that only points to the note on another verse ("As in verse 4").
COVERED = re.compile(r"^\s*(?:As in|As at|See the note|See verse|As the note)\b[^.]{0,60}\.?\s*$", re.IGNORECASE)
VERSIONS = re.compile(r"Greek|Septuagint|Syriac|Latin|Vulgate|Qumran|Dead Sea|Samaritan|Targum|"
                      r"Isaiah Scroll|ancient translations?|early translations?|Hebrew manuscripts|versions",
                      re.IGNORECASE)
MANUSCRIPTS = re.compile(r"manuscripts?|witness|copies|papyr|codex|SBLGNT", re.IGNORECASE)

# Whether each category gets a footnote (None: not judged), in the order
# category() tries them.
POLICY = {"stated": False, "covered": None, "verses": True, "english_bible": True, "quoted": True,
          "same_sense": False, "spelling": False, "sense": True, "versions": True,
          "manuscripts": None, "other": None}


def category(decision, record=None):
    """The decision's category, from the words of its choice and reason, and
    the record's source language (an Old Testament variant read by the
    ancient translations is a different word; a New Testament one in the
    manuscripts is judged only where the reason says what it changes)."""
    text = f"{decision.get('choice', '')} {decision.get('reason', '')}"
    hebrew = bool(record) and (record.get("source") or {}).get("language") in ("hbo", "arc")
    if STATED_NONE.search(text):
        return "stated"
    if COVERED.search(decision.get("reason", "")):
        return "covered"
    if VERSES.search(text):
        return "verses"
    if ENGLISH_BIBLE.search(text):
        return "english_bible"
    if hebrew and QUOTED.search(text):
        return "quoted"
    if SAME_SENSE.search(text) and not SENSE_CHANGE.search(text):
        return "same_sense"
    if SPELLING.search(text) and not SENSE_CHANGE.search(text):
        return "spelling"
    if SENSE_CHANGE.search(text):
        return "sense"
    if hebrew and VERSIONS.search(text):
        return "versions"
    if MANUSCRIPTS.search(text) or VERSIONS.search(text):
        return "manuscripts"
    return "other"


def expected_footnote(decision, record=None):
    """What the policy says the footnote flag should be, or None."""
    return POLICY[category(decision, record)]


def variants(books=None):
    """Yield (path, record, decision) for every text_variant decision."""
    for folder in sorted(CONTENT.iterdir()):
        if not folder.is_dir() or (books and folder.name not in books):
            continue
        for path in sorted(folder.glob("*.json")):
            for record in json.loads(path.read_text(encoding="utf-8"))["records"]:
                for d in record.get("decisions") or []:
                    if d.get("category") == "text_variant":
                        yield path, record, d


def inconsistent(books=None):
    """[(path, record, decision, expected)] where the flag breaks the policy."""
    out = []
    for path, record, d in variants(books):
        want = expected_footnote(d, record)
        if want is not None and bool(d.get("footnote")) != want:
            out.append((path, record, d, want))
    return out


def fix(skip=("PSA",), books=None):
    """Set footnote flags to the policy, file by file; returns the changes.
    Books in skip are only reported, never written."""
    changes = []
    by_path = {}
    for path, record, d, want in inconsistent(books):
        changes.append((record["id"], d["id"], want, path.parent.name in skip))
        if path.parent.name not in skip:
            by_path.setdefault(path, set()).add((record["id"], d["id"]))
    for path, keys in by_path.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        for record in data["records"]:
            for d in record.get("decisions") or []:
                if (record["id"], d["id"]) in keys:
                    d["footnote"] = POLICY[category(d, record)]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changes


def summary(books=None):
    counts = {}
    for _, record, d in variants(books):
        key = (category(d, record), bool(d.get("footnote")))
        counts[key] = counts.get(key, 0) + 1
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("books", nargs="*", help="book codes (default: all)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--skip", default="PSA", help="comma-separated books --fix never writes")
    args = ap.parse_args(argv)
    books = set(args.books) or None
    if args.list:
        for _, record, d in variants(books):
            print("\t".join([record["id"], d["id"], category(d, record), "footnote" if d.get("footnote") else "-",
                             d["choice"], " | ".join(d.get("alternatives") or [])]))
        return 0
    if args.fix:
        for rid, did, want, skipped in fix(tuple(args.skip.split(",")), books):
            print(f"{rid} {did}: footnote {'on' if want else 'off'}{' (skipped)' if skipped else ''}")
        return 0
    counts = summary(books)
    for cat in POLICY:
        print(f"{cat:14} footnote {counts.get((cat, True), 0):5}   none {counts.get((cat, False), 0):5}")
    bad = inconsistent(books)
    print(f"{len(bad)} inconsistent with the policy")
    for _path, record, d, want in sorted(bad, key=lambda x: refs.parse(x[1]["refs"][0]).sort_key()):
        print(f"  {record['id']} {d['id']} [{category(d, record)}] should {'have' if want else 'not have'} "
              f"a footnote: {d['choice'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
