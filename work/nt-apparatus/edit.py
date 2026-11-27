"""One-off (NT apparatus pass; kept for the record): remove or narrow the "check against the apparatus" hedges of the
English NT meaning notes, using owb/apparatus.py verdicts and a file of
manual decisions. Usage: python3 edit.py [--write] [--report out.json]"""
import argparse
import glob
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, '.')
from owb import apparatus as A, refs  # noqa: E402

WORK = Path(__file__).parent
NT = [c for c, _ in refs.NT_BOOKS]

PAREN = re.compile(r"\s*\((?:From general knowledge of the manuscripts(?:; [^)]*)?|"
                   r"To be checked against the apparatus)\.?\)")
# whole sentences that only ask for the check
PURE = [
    re.compile(r"^(?:A |The )?[Rr]eviewers? (?:should|must) check\b[^.]*\bapparatus\b[^.]*\.$"),
    re.compile(r"^(?:A |The )?[Rr]eviewers? (?:should|must) check "
               r"(?:the evidence|the witnesses|this|the manuscript evidence)\.$"),
    re.compile(r"^(?:This|The)\b[^.]*\bgeneral knowledge\b[^.]*\.$"),
    re.compile(r"^From general knowledge; [^.]*apparatus[^.]*\.$"),
    re.compile(r"^A reviewer must check this account against the SBLGNT apparatus[^.]*\.$"),
]
TAIL = re.compile(r";\s*(?:a |the )?reviewers? (?:should|must) check\b[^.]*\bapparatus\b[^.]*\.$")
KNOW_MID = re.compile(r"([;,])\s*from general knowledge,\s*")


def strip_hedges(reason):
    text = PAREN.sub("", reason)
    out = []
    for s in A._sentences(text):
        t = s.strip()
        if any(p.match(t) for p in PURE):
            continue
        t = TAIL.sub(".", t)
        t = KNOW_MID.sub(r"\1 ", t)
        t = A.without_knowledge(t)
        out.append(t)
    new = " ".join(out).strip()
    return re.sub(r"\s+", " ", new)


def names(claims):
    """What the data could not settle, for a narrowed hedge."""
    out = []
    for c in claims:
        if c.verdict not in ("unsupported", "not covered", "unclear", "mixed"):
            continue
        if c.group == "versions":
            item = "the ancient translations and early writers"
        elif c.group in A.MANUSCRIPTS:
            item = A.MANUSCRIPTS[c.group]
        elif c.group.startswith("P"):
            item = "Papyrus " + c.group[1:]
        elif c.group == "later":
            item = "the later manuscripts"
        elif c.group in ("early", "earliest"):
            item = "the early manuscripts"
        elif c.group == "western":
            item = "the Western witnesses"
        elif c.group == "KJTR":
            item = "the King James Version's Greek text"
        else:
            item = "the other manuscripts"
        if item not in out:
            out.append(item)
    return out


def join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def narrowed(claims):
    items = names(claims)
    if not items:
        return ""
    return f"Reviewers should check {join(items)} against a full apparatus."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--report")
    args = ap.parse_args()
    manual = json.loads((WORK / "manual.json").read_text()) if (WORK / "manual.json").exists() else {}
    changes, pending = [], []
    for b in NT:
        for f in sorted(glob.glob(f"content/{b}/*.json")):
            data = json.loads(open(f, encoding="utf-8").read())
            dirty = False
            for r in data["records"]:
                for d in r.get("decisions", []):
                    if d.get("layer") != "meaning" or not A._HEDGE.search(d.get("reason", "")):
                        continue
                    k = f"{r['id']} {d['id']}"
                    res = A.check_note(d)
                    status = res["status"]
                    m = manual.get(k)
                    old = d["reason"]
                    if m:
                        action = m["action"]
                    elif status in ("confirmed", "no claims"):
                        action = "confirm"
                    elif status == "partly":
                        action = "narrow"
                    else:
                        pending.append((k, status))
                        continue
                    if action == "keep":
                        continue
                    if action == "rewrite":
                        new = m["text"]
                    else:
                        base = old
                        for a, b in (m or {}).get("pairs", []):
                            if a not in base:
                                raise SystemExit(f"{k}: {a!r} not in the note")
                            base = base.replace(a, b)
                        new = strip_hedges(base)
                        hedge = m.get("hedge") if m else None
                        if action == "narrow":
                            hedge = hedge or narrowed(res["claims"])
                        if hedge:
                            new = new + " " + hedge
                    if A._HEDGE.search(new) and action not in ("rewrite", "narrow", "replace") \
                            and not (m and m.get("hedge")):
                        pending.append((k, "hedge left: " + new[-90:]))
                        continue
                    if new != old:
                        d["reason"] = new
                        dirty = True
                        changes.append({"key": k, "file": f, "status": status, "action": action,
                                        "old": old, "new": new})
            if dirty and args.write:
                open(f, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"changes {len(changes)}, pending {len(pending)}", file=sys.stderr)
    for p in pending:
        print("PENDING", *p)
    if args.report:
        Path(args.report).write_text(json.dumps(changes, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
