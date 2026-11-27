"""What a reviewer needs beside the sentence they review: where to start
(the language's brief, glossary and review guide, and what approving and
flagging mean), and for one sentence its key terms with the form expected,
any content check hit on it and any long run it shares with a reference
Bible.

Nothing here measures anything: the hints are read from what Consistency,
Checks and Similarity have already kept, so a sentence opens at once, and
a hint is missing (not wrong) until one of those has been measured.
"""
from django.conf import settings
from django.core.cache import cache

from owb import languages
from texts.models import Word

from .models import ChecksAnswer

DOCS = settings.REPO_ROOT / "docs"
SHARED_RUN = 8   # words shared with a reference Bible worth pointing out


def _file(path, label):
    return {"label": label, "file": str(path.relative_to(settings.REPO_ROOT))} if path.is_file() else None


def guide(layer):
    """[{label, file}]: the documents for reviewing layer that exist."""
    if layer in languages.ORIGINAL:
        found = [_file(settings.REPO_ROOT / "README.md", "How the translation is made"),
                 _file(DOCS / "text-variants.md", "Text variants"),
                 _file(settings.REPO_ROOT / "data" / "key_terms.json", "Key terms")]
    else:
        name = languages.READING[layer]["name"].lower()
        notes = DOCS / "review-notes"
        found = [_file(DOCS / f"{name}-style.md", "Style brief"),
                 _file(DOCS / f"{name}-terms.md", "Terms glossary"),
                 _file(DOCS / f"{name}-glossary.md", "Glossary"),
                 _file(DOCS / f"{name}-review-guide.md", "Review guide"),
                 _file(notes / f"{layer}-review-checklist.md", "Review checklist"),
                 _file(notes / f"{layer}-uncertain.md", "Uncertain renderings")]
    return [f for f in found if f]


def _terms(s, layer):
    """The key terms in s's words, with the form expected in layer: the
    term's English words for English, else the form most sentences use in
    the kept Consistency measurement (none until it has been measured)."""
    from . import consistency   # it, checks and overlap import review, which imports this
    strongs = {(("hbo" if w.startswith("o") else "grc"), strong)
               for w, strong in Word.objects.filter(id__in=s.tokens).values_list("id", "strong") if strong}
    found = [t for t in consistency.TERMS if (t.get("language", "grc"), t["strong"]) in strongs]
    if not found:
        return []
    meaning = layer in languages.ORIGINAL
    kept = None if meaning or layer == "en" else cache.get(f"staff.consistency.{layer}.B")
    usual = {t["slug"]: t["forms"][0]["form"] for t in (kept or {}).get("measured", {}).get("terms", []) if t["forms"]}
    text = "" if meaning else consistency._plain(
        next((r.text for r in s.renderings.all() if r.language == layer and r.level == "B"), ""))
    out = []
    for t in found:
        english = t["english"] if isinstance(t["english"], list) else t["english"].get("B", [])
        expected = english if meaning or layer == "en" else ([usual[t["slug"]]] if t["slug"] in usual else [])
        row = {"slug": t["slug"], "lemma": t["lemma"], "sense": t["sense"], "expected": expected}
        if expected and text:
            row["found"] = any(consistency._pattern(consistency._norm(f)).search(text) for f in expected)
        out.append(row)
    return out


def _check_hits(s, layer):
    """Content check hits on s in layer, from the kept answer (the current
    one, else the last measured)."""
    from . import checks
    if layer not in languages.READING:
        return []
    answer = cache.get(f"staff.checks.{layer}.{checks.content_stamp(layer)}")
    if answer is None:
        answer = ChecksAnswer.objects.filter(language=layer).values_list("answer", flat=True).first()
    if not answer:
        return []
    hits = answer["notes"]["hits"] + answer["glossary"]["verses"]["hits"]
    return [{"kind": h["kind"], "levels": h.get("levels", [h.get("level")]), "text": h.get("text", ""),
             "term": h.get("term") or h.get("choice", "")} for h in hits if h.get("record") == s.record_id]


def _shared_runs(s, layer):
    """Long runs s shares with a reference Bible, from Similarity's kept answer."""
    from . import overlap
    if layer not in languages.READING:
        return []
    answer = cache.get(overlap.cache_key(s.book, layer, 6))
    if not answer:
        return []
    return [{"level": r["level"], "edition": r["edition"], "length": r["length"], "text": r["text"]}
            for r in answer["longest_runs"] if r["record"] == s.record_id and r["length"] >= SHARED_RUN]


def sentence_hints(s, layer):
    return {"terms": _terms(s, layer), "checks": _check_hits(s, layer), "shared": _shared_runs(s, layer)}
