"""One search box for the whole admin.

GET /api/admin/search/?q=       what q names, in groups: a verse (by reference
                                or id), a sentence record (JHN.1.1.s1), key
                                terms, articles, decisions, and, for roles
                                that open them, accounts and reader messages

Each group holds a few results, each with the admin address ("#verse/...")
that opens it. For anyone on the team (overview); accounts only for the
users area and reader messages only for the inbox, as their own pages are.
"""
import json
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q
from rest_framework.response import Response

from feedback.models import ReaderMessage
from translation import search
from translation.models import Decision, Sentence

from .articles import check_translations
from .inbox import verse_label
from .permissions import admin_view
from .verses import verse_id

LIMIT = 6
RECORD = re.compile(r"^([1-3]?[A-Z]+)\.(\d+)\.(\d+)\.S(\d+)$")


def _short(text, n=90):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[:n - 1] + "…"


def _verse(q):
    """A verse the query names, if it has a number in it (a reference or an id)."""
    if not re.search(r"\d", q):
        return []
    try:
        vid = verse_id(q)
    except Exception:
        vid = None
    if not vid:
        return []
    return [{"title": verse_label(vid), "detail": "Open in the verse inspector", "href": f"#verse/{vid}"}]


def _record(q):
    if not RECORD.match(q.upper()):
        return []
    s = Sentence.objects.filter(record_id__iexact=q).values("record_id", "refs").first()
    if not s:
        return []
    return [{"title": s["record_id"], "detail": "Sentence in " + verse_label(s["refs"][0]),
             "href": f"#verse/{s['refs'][0]}"}]


def _terms(q):
    key = search.fold(q)
    terms = json.loads((settings.REPO_ROOT / "data" / "key_terms.json").read_text(encoding="utf-8"))["terms"]
    out = []
    for t in terms:
        english = t["english"] if isinstance(t["english"], list) else [w for ws in t["english"].values() for w in ws]
        names = [t["slug"], t["sense"], t["lemma"], t["strong"], *english]
        if any(key in search.fold(n) for n in names):
            out.append({"title": f"{t['lemma']} · {t['sense']}",
                        "detail": ("H" if t.get("language") == "hbo" else "G") + t["strong"] + " · "
                        + ", ".join(english), "href": "#terms"})
    return out[:LIMIT]


def _article_titles():
    """[(slug, title)] of the English articles, cached as the files only
    change with a deploy."""
    titles = cache.get("staff.search.articles")
    if titles is None:
        titles = []
        for path in sorted((settings.REPO_ROOT / "articles").glob("*.md")):
            meta, _ = check_translations.split(path.read_text(encoding="utf-8"))
            title = meta.get("title", path.stem)
            titles.append((path.stem, json.loads(title) if title.startswith('"') else title))
        cache.set("staff.search.articles", titles, 3600)
    return titles


def _articles(q):
    key = search.fold(q)
    return [{"title": title, "detail": slug, "href": "#articles"}
            for slug, title in _article_titles()
            if key in search.fold(title) or key in slug][:LIMIT]


def _decisions(q):
    if len(q) < 3:
        return []
    found = (Decision.objects.filter(Q(choice__icontains=q) | Q(reason__icontains=q))
             .select_related("sentence").order_by("id")[:LIMIT])
    return [{"title": _short(d.choice, 70),
             "detail": f"{verse_label(d.sentence.refs[0])} · {d.language or 'meaning'} · {d.category}",
             "href": f"#verse/{d.sentence.refs[0]}"} for d in found]


def _users(q):
    found = (get_user_model().objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q))
             .order_by("-date_joined")[:LIMIT])
    return [{"title": u.first_name or u.username, "detail": u.username, "href": f"#user/{u.id}"} for u in found]


def _messages(q):
    found = (ReaderMessage.objects.filter(Q(text__icontains=q) | Q(verse__iexact=q) | Q(user__username__icontains=q))
             .select_related("user")[:LIMIT])
    return [{"title": _short(m.text, 70),
             "detail": f"{verse_label(m.verse)} · {m.get_kind_display()} · {m.get_status_display()} · "
             f"{m.user.first_name or m.user.username}",
             "href": f"#verse/{m.verse}"} for m in found]


@admin_view("overview")
def find(request):
    q = " ".join(request.query_params.get("q", "").split())[:100]
    if len(q) < 2:
        return Response({"q": q, "groups": []})
    groups = [("verse", "Verses", _verse), ("record", "Sentences", _record), ("term", "Key terms", _terms),
              ("article", "Articles", _articles), ("decision", "Decisions", _decisions)]
    if "users" in request.admin_areas:
        groups.append(("user", "Accounts", _users))
    if "inbox" in request.admin_areas:
        groups.append(("message", "Reader messages", _messages))
    out = []
    for kind, label, run in groups:
        results = run(q)
        if results:
            out.append({"kind": kind, "label": label, "results": results})
    return Response({"q": q, "groups": out})
