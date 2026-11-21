"""What a reviewer approved, kept with the approval (ReviewEvent.snapshot)
so the admin can show word by word what has changed since (staff/history.py).

The same parts as the review digest (staff/review.py digest): the literal
gloss and the meaning decisions for a meaning layer ("grc", "hbo"); one
language's renderings, level by level, and its rendering decisions for a
wording layer ("en", "fr", ...). Kept apart from review.py so history.py can
use it without importing the review views.
"""
from owb import languages


def decision_json(d):
    """A Decision's fields that a change to it would show."""
    return {"category": d.category, "levels": list(d.levels), "tokens": list(d.tokens), "choice": d.choice,
            "alternatives": list(d.alternatives), "reason": d.reason, "uncertain": d.uncertain,
            "footnote": d.footnote}


def snapshot(sentence, layer):
    """What a reviewer of layer approves in sentence (renderings and
    decisions prefetched or not), as JSON."""
    if layer in languages.ORIGINAL:
        return {"literal_gloss": sentence.literal_gloss,
                "decisions": {d.key: decision_json(d) for d in sentence.decisions.all() if d.layer == "meaning"}}
    return {"renderings": {r.level: r.text for r in sentence.renderings.all() if r.language == layer},
            "decisions": {d.key: decision_json(d) for d in sentence.decisions.all()
                          if d.layer == "rendering" and d.language == layer}}
