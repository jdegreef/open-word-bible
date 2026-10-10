"""MACULA Greek word tokens for the SBLGNT.

Reads SBLGNT/tsv/macula-greek-SBLGNT.tsv. Columns used (as named in the file):
xml:id, ref ("JHN 1:1!3" = word 3 of John 1:1), text, after (punctuation that
follows the word), normalized, lemma, morph, gloss (Berean Interlinear),
english (Cherith gloss), strong.
"""
import csv
import io
import re
from functools import lru_cache
from typing import NamedTuple

from owb import refs
from owb.sources import read_text

TSV_PATH = "SBLGNT/tsv/macula-greek-SBLGNT.tsv"

# Louw-Nida domains (UBS MARBLE): used with permission but not openly
# licensed, so never read, stored or published. tests/test_licensing.py
# checks that nothing we publish carries them.
RESTRICTED = ("domain", "ln")
_REF = re.compile(r"(\w+) (\d+):(\d+)!(\d+)")


class Token(NamedTuple):
    id: str
    ref: refs.Ref
    position: int
    text: str
    after: str
    normalized: str
    lemma: str
    morph: str
    gloss: str
    english: str
    strong: str


@lru_cache(maxsize=None)
def _all_tokens():
    """Return {Ref: [Token]} for the whole New Testament."""
    reader = csv.DictReader(io.StringIO(read_text("macula-greek", TSV_PATH)),
                            delimiter="\t", quoting=csv.QUOTE_NONE)
    by_verse = {}
    for row in reader:
        m = _REF.fullmatch(row["ref"])
        ref = refs.Ref(m[1], int(m[2]), int(m[3]))
        by_verse.setdefault(ref, []).append(Token(
            id=row["xml:id"], ref=ref, position=int(m[4]),
            text=row["text"], after=row["after"],
            normalized=row["normalized"], lemma=row["lemma"],
            morph=row["morph"], gloss=row["gloss"],
            english=row["english"], strong=row["strong"]))
    return by_verse


def load_tokens(start, end=None):
    """Return [Token] for verses start..end (inclusive), in text order."""
    start = refs.parse(start) if isinstance(start, str) else start
    end = start if end is None else (refs.parse(end) if isinstance(end, str) else end)
    return [t for ref, toks in _all_tokens().items()
            if refs.in_range(ref, start, end) for t in toks]


def tokens_for_refs(verse_ids):
    """Return {token id: Token} for a list of verse ids."""
    out = {}
    for vid in verse_ids:
        for tok in _all_tokens().get(refs.parse(vid), []):
            out[tok.id] = tok
    return out


@lru_cache(maxsize=None)
def forms():
    """Every word form, normalized form and lemma in the New Testament."""
    return frozenset(x for toks in _all_tokens().values() for t in toks
                     for x in (t.text, t.normalized, t.lemma) if x)


# SBLGNT punctuation in a token's `after`: full stop, Greek question mark,
# and the raised dot (ano teleia), which can end a sentence or join clauses.
FULL_STOPS = ".;"
RAISED_DOT = "·"


def sentences(tokens):
    """Group tokens (in text order) into source sentences.

    A sentence ends at a full stop or question mark, or at a raised dot that
    ends a verse. A raised dot inside a verse joins clauses and does not end
    one. This is a starting point: a record may be split at another raised
    dot, or two sentences merged, when the clauses call for it."""
    out, current = [], []
    for i, tok in enumerate(tokens):
        current.append(tok)
        verse_ends = i + 1 == len(tokens) or tokens[i + 1].ref != tok.ref
        if any(c in tok.after for c in FULL_STOPS) or (verse_ends and RAISED_DOT in tok.after):
            out.append(current)
            current = []
    if current:
        out.append(current)
    return out
