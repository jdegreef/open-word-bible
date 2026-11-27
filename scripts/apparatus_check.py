"""Check what New Testament notes say about manuscripts against the data.

Reads every New Testament meaning decision that is a text variant, or whose
reason mentions the apparatus, and compares each claim it makes about
witnesses ("many later manuscripts add ...", "Codex Vaticanus lacks ...",
"the King James Version follows ...") with the SBLGNT apparatus (WH, Treg,
NIV, RP, NA28) and the CNTR transcriptions of the early manuscripts and of
the Greek text behind the King James Version. See owb/apparatus.py.

Usage:
    python3 scripts/apparatus_check.py                 # counts by status
    python3 scripts/apparatus_check.py --list          # one line per claim
    python3 scripts/apparatus_check.py --status contradicted --list
    python3 scripts/apparatus_check.py --book ROM --json
    python3 scripts/apparatus_check.py --hedged        # only notes that ask for a check

Exit status 1 if --strict and a claim is contradicted.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import apparatus, refs  # noqa: E402

CONTENT = ROOT / "content"


def _order(path):
    """content/ROM/ROM.10.json, 1CO.15.1-34.json: by chapter, then first verse."""
    parts = path.stem.split(".")
    return [int(x.split("-")[0]) for x in parts[1:]]


def decisions(books, hedged_only):
    for book in books:
        for path in sorted((CONTENT / book).glob("*.json"),
                           key=_order):
            data = json.loads(path.read_text(encoding="utf-8"))
            for record in data["records"]:
                for d in record.get("decisions", []):
                    if d.get("layer") != "meaning":
                        continue
                    hedged = bool(apparatus._HEDGE.search(d.get("reason", "")))
                    if hedged_only and not hedged:
                        continue
                    if d.get("category") != "text_variant" and not hedged:
                        continue
                    yield path, record["id"], d, hedged


def evidence_line(ev):
    eds = [e for e, v in ev["editions"].items() if v == "differ"]
    wit = {k: c.status[0] + (c.detail[:1] if c.detail else "") for k, c in ev["witnesses"].items()}
    agree = sorted(k for k, v in wit.items() if v == "a")
    differ = sorted(k for k, v in wit.items() if v != "a")
    return (f"editions differing: {' '.join(eds) or '-'}; agree: {' '.join(agree) or '-'}; "
            f"differ: {' '.join(differ) or '-'}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--book", action="append", help="book code (repeatable); default all NT books")
    ap.add_argument("--status", action="append", help="only notes with this status (repeatable)")
    ap.add_argument("--hedged", action="store_true", help="only notes that ask for a check against the apparatus")
    ap.add_argument("--list", action="store_true", help="print each note and its claims")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--strict", action="store_true", help="exit 1 if a claim is contradicted")
    args = ap.parse_args(argv)
    books = args.book or [code for code, _ in refs.NT_BOOKS]
    counts, claim_counts, out = collections.Counter(), collections.Counter(), []
    for path, rid, d, hedged in decisions(books, args.hedged):
        result = apparatus.check_note(d)
        counts[result["status"]] += 1
        for c in result["claims"]:
            claim_counts[c.verdict] += 1
        if args.status and result["status"] not in args.status:
            continue
        out.append({
            "record": rid, "decision": d["id"], "file": str(path.relative_to(ROOT)),
            "hedged": hedged, "status": result["status"], "reason": d.get("reason", ""),
            "choice": d.get("choice", ""), "evidence": evidence_line(result["evidence"]),
            "units": [{"lemma": u.lemma.text,
                       "others": [{"text": r.text, "witnesses": list(r.witnesses)} for r in u.others]}
                      for u in result["evidence"]["units"]],
            "claims": [{"group": c.group, "side": c.side, "strength": c.strength,
                        "verdict": c.verdict, "why": c.why, "clause": c.clause} for c in result["claims"]],
        })
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    elif args.list:
        for o in out:
            print(f"{o['record']} {o['decision']} [{o['status']}] {o['reason']}")
            print(f"    {o['evidence']}")
            for u in o["units"]:
                print("    unit: " + u["lemma"] + " ] " + "; ".join(
                    f"{r['text']} {' '.join(r['witnesses'])}" for r in u["others"]))
            for c in o["claims"]:
                print(f"    - {c['verdict']}: {c['group']} ({c['strength']}, {c['side']}) {c['why']}")
            print()
    print("notes: " + ", ".join(f"{k} {v}" for k, v in counts.most_common()), file=sys.stderr)
    print("claims: " + ", ".join(f"{k} {v}" for k, v in claim_counts.most_common()), file=sys.stderr)
    return 1 if args.strict and claim_counts["contradicted"] else 0


if __name__ == "__main__":
    sys.exit(main())
