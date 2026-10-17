"""Wording consistency: how one language words each key term across the
drafted sentences that use it, so a term worded two ways shows up.

GET /api/admin/consistency/?lang=en&level=B&term=&min=2
        each key term (data/key_terms.json) with the forms its sentences
        use at that level, their counts, books and example sentences, the
        terms split between forms first. term (a slug) gives one term with
        more examples; a form needs min sentences (default 2) to count
        towards a split.

A sentence uses a term when its tokens include a word with the term's
Strong's number (as staff/text.py counts them). The forms a language may use
come from what the records say about those words: the alignments' target
spans, the term's allowed English words (for English), and the word_choice
rendering decisions on its tokens ("x (L); y (B, R)"). Each sentence's
rendering, at the settings' defaults, is then searched for those forms, a
form matching as a whole word or with a short ending (plurals, particles).
A sentence with none of them is counted as "other". Answers are cached
until a sentence changes.
"""
import hashlib
import json
import re

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Max
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from owb import export, languages, refs
from texts.models import Word
from translation.models import Decision, Rendering, Sentence

from .inbox import verse_label
from .permissions import admin_view

_DATA = (settings.REPO_ROOT / "data" / "key_terms.json").read_bytes()
TERMS = json.loads(_DATA.decode("utf-8"))["terms"]
TERMS_DIGEST = hashlib.sha256(_DATA).hexdigest()[:12]
LEVELS = ("L", "B", "R")
EXAMPLES = 5             # example sentences per form in the list
TERM_EXAMPLES = 25       # for one term
LONGEST = 4              # words in a decision's choice that can still be a form
ENDING = 3               # letters a form may gain (grace -> graces, 은혜 -> 은혜가)

LEVEL_NOTE = re.compile(r"\(\s*([LBR](?:\s*,\s*[LBR])*)\s*\)")
ASIDE = re.compile(r"\([^)]*\)")


def _plain(text):
    """A rendering as searchable text: settings at their defaults, no
    markers, lower case."""
    return re.sub(r"\\[vq]\b", " ", export.plain(text)).lower()


def _norm(form):
    return " ".join(re.sub(r"[^\w\s'-]", " ", export.plain(form)).lower().split())


def _choice_forms(choice, levels):
    """{level: forms} from a word_choice decision's choice: "x, y (L); z (B, R)"
    gives x and y at L and z at B and R; a part without a note is for the
    decision's own levels. Long phrases and explanations are left out."""
    out = {}
    for part in choice.split(";"):
        note = LEVEL_NOTE.search(part)
        at = [lv.strip() for lv in note.group(1).split(",")] if note else levels
        part = ASIDE.sub(" ", part)
        for form in re.split(r"[,/]", part):
            form = _norm(form)
            if form and len(form.split()) <= LONGEST:
                for lv in at:
                    out.setdefault(lv, set()).add(form)
    return out


def _pattern(form):
    return re.compile(r"(?<!\w)" + re.escape(form) + r"\w{0,%d}(?!\w)" % ENDING)


def _stamp():
    s = Sentence.objects.aggregate(n=Count("id"), t=Max("updated_at"))
    return "{}.{}".format(s["n"], s["t"].timestamp() if s["t"] else 0)


def _uses():
    """{term slug: [sentence rows]} for every key term, in two queries: the
    words by Strong's number (Greek ids start n, Hebrew o), then the
    sentences holding any of them."""
    wanted = {(t.get("language", "grc"), t["strong"]) for t in TERMS}
    ids = {}
    for wid, strong in Word.objects.filter(strong__in={s for _, s in wanted}).values_list("id", "strong"):
        key = ("hbo" if wid.startswith("o") else "grc", strong)
        if key in wanted:
            ids.setdefault(key, set()).add(wid)
    every = set().union(*ids.values()) if ids else set()
    out = {t["slug"]: [] for t in TERMS}
    if not every:
        return out, ids
    rows = (Sentence.objects.filter(tokens__overlap=list(every))
            .values("id", "record_id", "book", "chapter", "verse", "number", "refs", "tokens"))
    order = {code: i for i, code in enumerate(refs.BOOK_CODES)}
    rows = sorted(rows, key=lambda r: (order[r["book"]], r["chapter"], r["verse"], r["number"]))
    for t in TERMS:
        mine = ids.get((t.get("language", "grc"), t["strong"]), set())
        out[t["slug"]] = [{**r, "term_tokens": mine & set(r["tokens"])} for r in rows if mine & set(r["tokens"])]
    return out, ids


def measure(lang, level, slug, least):
    uses, _ = _uses()
    sentence_ids = {r["id"] for rows in uses.values() for r in rows}
    texts = dict(Rendering.objects.filter(sentence_id__in=sentence_ids, language=lang, level=level)
                 .values_list("sentence_id", "text"))
    decisions = {}
    for sid, tokens, choice, levels in (Decision.objects
                                        .filter(sentence_id__in=sentence_ids, layer="rendering", language=lang,
                                                category="word_choice")
                                        .values_list("sentence_id", "tokens", "choice", "levels")):
        decisions.setdefault(sid, []).append((set(tokens), choice, levels))
    aligned = {}
    rows = Sentence.objects.filter(id__in=sentence_ids).exclude(alignments=[]).values_list("id", "alignments")
    for sid, spans in rows:
        aligned[sid] = [a for a in spans if a["language"] == lang and a["level"] == level]
    terms = []
    for t in TERMS:
        if slug and t["slug"] != slug:
            continue
        rows = uses[t["slug"]]
        forms = set()
        if lang == "en":
            english = t["english"]
            forms |= {_norm(w) for w in (english if isinstance(english, list) else english.get(level, []))}
        for r in rows:
            for tokens, choice, levels in decisions.get(r["id"], []):
                if tokens & r["term_tokens"]:
                    forms |= _choice_forms(choice, levels).get(level, set())
            for a in aligned.get(r["id"], []):
                if set(a["tokens"]) & r["term_tokens"]:
                    forms.add(_norm(a["target_span"]))
        forms.discard("")
        # Longest first, so "gift of grace" is found before "grace".
        patterns = [(f, _pattern(f)) for f in sorted(forms, key=lambda f: (-len(f), f))]
        found, other, rendered = {}, [], 0
        for r in rows:
            text = texts.get(r["id"])
            if text is None:
                continue
            rendered += 1
            text = _plain(text)
            hit = next((f for f, p in patterns if p.search(text)), None)
            (found.setdefault(hit, []) if hit else other).append(r)
        limit = TERM_EXAMPLES if slug else EXAMPLES
        listed = sorted(found.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        counted = [rows for _, rows in listed if len(rows) >= least]
        matched = sum(len(rows) for _, rows in listed)
        spread = round(1 - len(listed[0][1]) / matched, 3) if matched else 0
        terms.append({
            "slug": t["slug"], "strong": t["strong"], "lemma": t["lemma"], "sense": t["sense"],
            "language": t.get("language", "grc"), "uses": len(rows), "rendered": rendered,
            "split": len(counted) > 1, "spread": spread,
            "forms": [{"form": form, "sentences": len(rows), "books": _books(rows),
                       "examples": [_example(r) for r in rows[:limit]]} for form, rows in listed],
            "other": {"sentences": len(other), "examples": [_example(r) for r in other[:limit]]},
        })
    terms.sort(key=lambda t: (not t["split"], -t["spread"], -t["rendered"]))
    return {"terms": terms}


def _books(rows):
    seen = []
    for r in rows:
        if r["book"] not in seen:
            seen.append(r["book"])
    return seen


def _example(r):
    return {"record": r["record_id"], "verse": r["refs"][0], "label": verse_label(r["refs"][0])}


@admin_view("overview")
def consistency(request):
    params = request.query_params
    lang = params.get("lang", "en")
    if lang not in languages.READING:
        raise ValidationError({"lang": "Choose a reading language."})
    level = params.get("level", "B")
    if level not in LEVELS:
        raise ValidationError({"level": "Choose L, B or R."})
    slug = params.get("term", "")
    if slug and slug not in {t["slug"] for t in TERMS}:
        raise ValidationError({"term": "No key term has that slug."})
    try:
        least = min(max(int(params.get("min", 2)), 1), 50)
    except ValueError:
        least = 2
    key = f"staff.consistency.{lang}.{level}.{slug}.{least}.{TERMS_DIGEST}.{_stamp()}"
    answer = cache.get(key)
    if answer is None:
        answer = measure(lang, level, slug, least)
        cache.set(key, answer, 86400)
    return Response({**answer, "language": lang, "level": level, "min": least,
                     "languages": [{"code": c, "name": lang["name"]} for c, lang in languages.READING.items()]})
