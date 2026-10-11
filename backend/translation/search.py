"""Search: Postgres full-text search over what the site shows (GET /api/search/).

The site's static build already decides what search can find in each site
language: search_documents in scripts/build_site.py lists every passage,
sentence, note and article, with what the page needs to show each one.
rebuild() stores those same documents here, so the site and the API never
disagree about what exists. import_content calls it after every import.

Matching follows the language of each document's own text, not the
site's: notes are written in English, and a sentence not yet translated is
shown, and found, in English. Each language has a text search
configuration that removes accents and then stems (migration 0003): owb_english,
owb_spanish, owb_french, and owb_simple for languages Postgres has no
stemmer for. Every entry is also indexed word for word (owb_simple, the
lowest weight), so words a stemmer drops ("I am") or shortens ("runn" while
typing "running") still match. Every word of a query also matches as the
start of a word, so results appear as the reader types; a single letter
matches only itself.
"""
import json
import re
import sys
import unicodedata
from collections import Counter

from django.conf import settings
from django.db import connection, transaction

from translation.models import SearchEntry, SearchLanguage, SearchWord

# The document kinds, by the names the API uses and the site's one-letter codes.
KINDS = {"passage": "c", "verse": "v", "note": "n", "article": "a"}
NAMES = {code: name for name, code in KINDS.items()}
CONFIGS = {"en": "owb_english", "es": "owb_spanish", "fr": "owb_french"}
SIMPLE = "owb_simple"
MIN_QUERY = 2
SPAN = re.compile(r"\{\{([a-z_]+):([^{}]*)\}\}")
VERSE_MARK = re.compile(r"\\v \d+ ?")
# Between fields and alternatives, so a phrase never runs from one into the next.
GAP = " ‖ "


def config(lang):
    return CONFIGS.get(lang, SIMPLE)


def fold(text):
    """Lower case, accents removed, curly quotes straightened (as the site's
    search.js folds text)."""
    text = "".join(c for c in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(c))
    return re.sub("[‘’ʼ]", "'", re.sub("[“”«»]", '"', text))


# ---- Building the tables ----------------------------------------------------

def site_build():
    """scripts/build_site.py, with its caches cleared, so it reads content/ afresh."""
    scripts = str(settings.REPO_ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import build_site
    for value in vars(build_site).values():
        if hasattr(value, "cache_clear"):
            value.cache_clear()
    return build_site


def everything(levels):
    """Every word a sentence can show: all levels, every option of each
    setting span, without verse markers. "Messiah" finds a verse even
    while the reader has "Christ" chosen."""
    return GAP.join(VERSE_MARK.sub(" ", SPAN.sub(lambda m: " ".join(m[2].split("|")), text))
                    for text in levels.values())


def fields(doc):
    """A document's (title, extra, body): weighted A, B and C."""
    kind = doc["k"]
    if kind == "c":
        return doc["h"], "", ""
    if kind == "v":
        return "", "", everything(doc["x"])
    if kind == "n":
        return doc["t"], GAP.join(doc["al"]), doc["s"]
    return doc["t"], doc["s"], doc["x"]


@transaction.atomic
def rebuild():
    """Replace the search tables with the site's documents in every site
    language. Returns {language: number of entries}."""
    site = site_build()
    SearchEntry.objects.all().delete()
    SearchWord.objects.all().delete()
    SearchLanguage.objects.all().delete()
    counts = {}
    for lang in site.LANGUAGES:
        data = site.search_documents(lang)
        SearchLanguage.objects.create(code=lang, books=data["books"], pages=data["pages"])
        entries, words = [], Counter()
        for position, doc in enumerate(data["docs"]):
            title, extra, body = fields(doc)
            entries.append(SearchEntry(language=lang, kind=doc["k"], position=position,
                                       config=config(doc.get("l", lang)),
                                       title=title, extra=extra, body=body, doc=doc))
            words.update(w for w in re.findall(r"[^\W\d_][\w']{2,62}", fold(f"{title} {extra} {body}")))
        SearchEntry.objects.bulk_create(entries, batch_size=2000)
        SearchWord.objects.bulk_create(
            (SearchWord(language=lang, word=w, count=n) for w, n in words.items()), batch_size=5000)
        counts[lang] = len(entries)
    with connection.cursor() as cursor:
        cursor.execute(f"""UPDATE {SearchEntry._meta.db_table} SET vector =
            setweight(to_tsvector(config::regconfig, title), 'A')
            || setweight(to_tsvector(config::regconfig, extra), 'B')
            || setweight(to_tsvector(config::regconfig, body), 'C')
            || setweight(to_tsvector('{SIMPLE}', concat_ws(' ', title, extra, body)), 'D')""")
    return counts


# ---- Queries ------------------------------------------------------------

def terms(q):
    """The query's terms as (text, is_phrase): "quoted phrases" whole,
    other words one by one."""
    out = []
    for m in re.finditer(r'"([^"]+)"|(\S+)', fold(q)):
        if m[1]:
            phrase = m[1].strip()
            if phrase:
                out.append((phrase, True))
        else:
            out += [(w, False) for w in re.split(r"[\W_]+", m[2]) if w]
    return out


def tsquery(lang, query_terms):
    """SQL (with its parameters) for a tsquery matching every term, in each
    text search configuration used on lang's pages: the language's own,
    English for notes and sentences not yet translated, and word for word.
    A word matches as the start of a word (prefix), except a single letter,
    which would match nearly everything."""
    alternatives, params = [], []
    for cfg in sorted({config(lang), config("en"), SIMPLE}):
        parts = []
        for text, phrase in query_terms:
            if phrase:
                parts.append("phraseto_tsquery(%s::regconfig, %s)")
                params += [cfg, text]
            else:
                # Only letters and digits reach to_tsquery, so a query can't
                # inject tsquery operators.
                parts.append("to_tsquery(%s::regconfig, %s)")
                params += [cfg, text if len(text) == 1 else f"{text}:*"]
        alternatives.append("(" + " && ".join(parts) + ")")
    return " || ".join(alternatives), params


def _table():
    return SearchEntry._meta.db_table


def _rows(sql, params):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def _headline():
    """A short passage of a note's reason or an article's text around the
    match, with the matches marked ⟦ ⟧."""
    return ("CASE WHEN e.kind IN ('n', 'a') THEN ts_headline(e.config::regconfig, e.body, q.query, "
            "'StartSel=⟦, StopSel=⟧, MinWords=18, MaxWords=40, ShortWord=2, "
            "MaxFragments=1, FragmentDelimiter=\" … \"') END")


def _result(doc, headline):
    # Django has psycopg return jsonb as text, for JSONField to parse; raw
    # queries parse it themselves.
    if isinstance(doc, str):
        doc = json.loads(doc)
    if headline and "⟦" in headline:
        return {**doc, "hl": headline}
    return doc


def counts(lang, query_sql, params):
    rows = _rows(f"""WITH q AS (SELECT {query_sql} AS query)
        SELECT e.kind, count(*) FROM {_table()} e, q
        WHERE e.language = %s AND e.vector @@ q.query GROUP BY e.kind""", [*params, lang])
    return {NAMES[kind]: n for kind, n in rows}


def best_of_each(lang, query_sql, params, per):
    """The best `per` documents of each kind."""
    rows = _rows(f"""WITH q AS (SELECT {query_sql} AS query),
        hits AS (
          SELECT e.id, e.kind, row_number() OVER (
            PARTITION BY e.kind ORDER BY ts_rank_cd(e.vector, q.query) DESC, e.position) AS n
          FROM {_table()} e, q WHERE e.language = %s AND e.vector @@ q.query)
        SELECT e.doc, {_headline()} FROM hits h JOIN {_table()} e ON e.id = h.id, q
        WHERE h.n <= %s ORDER BY e.kind = 'c' DESC, e.kind = 'v' DESC, e.kind = 'n' DESC, h.n""",
                 [*params, lang, per])
    return [_result(doc, hl) for doc, hl in rows]


def page(lang, query_sql, params, kind, offset, limit, sort):
    order = "e.position" if sort == "order" else "ts_rank_cd(e.vector, q.query) DESC, e.position"
    rows = _rows(f"""WITH q AS (SELECT {query_sql} AS query)
        SELECT e.doc, {_headline()} FROM {_table()} e, q
        WHERE e.language = %s AND e.kind = %s AND e.vector @@ q.query
        ORDER BY {order} LIMIT %s OFFSET %s""", [*params, lang, KINDS[kind], limit, offset])
    return [_result(doc, hl) for doc, hl in rows]


# ---- References ("John 3:16") -------------------------------------------

REFERENCE = re.compile(r"^\s*(.+?)\.?\s*(\d+)(?:\s*[:.,\s]\s*(\d+)(?:\s*[-–]\s*(\d+))?)?\s*$")


def reference(q, books, lang):
    """The passage a query names, if it is a reference: "John 3:16",
    "jn 3 16", "Filipenses 4:6-7", "1 John 2". The same rules as the site's
    search.js: a book's names, codes and abbreviations; or the start of a
    name, but only for a book with passages or when a verse is given, so
    "son 3" stays a search for words."""
    m = REFERENCE.match(fold(q))
    if not m:
        return None
    key = re.sub(r"[\s.]+", "", m[1])
    if not key or key.isdigit():
        return None
    chapter, verse = int(m[2]), int(m[3]) if m[3] else None
    book = next((b for b in books if key in b["aliases"]), None)
    if not book and len(re.sub(r"^\d", "", key)) >= 3:
        book = next((b for b in books if (b.get("chapters") or verse)
                     and any(a.startswith(key) for a in b["aliases"])), None)
    if not book:
        return None
    end = max(int(m[4]), verse) if m[4] else verse
    label = f"{book['name']} {chapter}"
    ref = {"book": book["code"], "chapter": chapter, "verse": verse, "end": end,
           "chapter_label": label,
           "label": label + (f":{verse}" + (f"–{end}" if end != verse else "") if verse else "")}
    found = (book.get("chapters") or {}).get(str(chapter))
    if found:
        ref["shown"] = [v for v in found["verses"] if verse and verse <= v <= end]
        ref["url"] = found["url"] + (f"#v{ref['shown'][0]}" if ref["shown"] else "")
        ref["sentences"] = sentences_for(ref, lang) if ref["shown"] else []
    return ref


def sentences_for(ref, lang):
    """The sentences that hold a reference's verses (the site shows them in
    the reference card, at the reader's own settings)."""
    shown = set(ref["shown"])
    docs = SearchEntry.objects.filter(language=lang, kind="v", doc__bk=ref["book"],
                                      doc__c=ref["chapter"]).order_by("position").values_list("doc", flat=True)
    return [d for d in docs if shown & set(d["vv"])]


# ---- Did you mean ----------------------------------------------------------

def suggest(lang, query_terms):
    """The query with each word that finds nothing swapped for the closest
    common word in lang's documents, if that query finds something."""
    changed, words = False, []
    for text, phrase in query_terms:
        if phrase or len(text) < 3:
            words.append(text)
            continue
        sql, params = tsquery(lang, [(text, False)])
        if counts(lang, sql, params):
            words.append(text)
            continue
        found = _rows(f"""SELECT word FROM {SearchWord._meta.db_table}
            WHERE language = %s AND word %% %s AND word <> %s
            ORDER BY similarity(word, %s) DESC, count DESC LIMIT 1""", [lang, text, text, text])
        if found:
            words.append(found[0][0])
            changed = True
        else:
            words.append(text)
    if not changed:
        return None
    suggestion = " ".join(words)
    sql, params = tsquery(lang, terms(suggestion))
    return suggestion if counts(lang, sql, params) else None


# ---- The search ------------------------------------------------------------

def search(lang, q, kind=None, offset=0, limit=20, sort="relevance", per=8):
    """The API's answer to q on lang's pages. With no kind: the reference
    if q is one, or else counts for each kind, the best `per` of each, and
    a suggestion when nothing matched. With a kind: one page of that kind,
    by relevance or in Bible order ("order")."""
    q = q.replace("\x00", "").strip()[:200]
    answer = {"query": q, "lang": lang}
    query_terms = terms(q)
    if len(q) < MIN_QUERY or not query_terms:
        return {**answer, "reference": None, "totals": {}, "results": [], "suggestion": None}
    sql, params = tsquery(lang, query_terms)
    if kind:
        total = counts(lang, sql, params).get(kind, 0)
        return {**answer, "type": kind, "sort": sort, "offset": offset, "total": total,
                "results": page(lang, sql, params, kind, offset, limit, sort) if total > offset else []}
    books = SearchLanguage.objects.get(code=lang).books
    ref = reference(q, books, lang)
    if ref:
        # A reference is answered by its verses alone: its words and numbers
        # would otherwise match every note that mentions them.
        return {**answer, "reference": ref, "totals": {}, "results": [], "suggestion": None}
    totals = counts(lang, sql, params)
    return {**answer, "reference": None, "totals": totals,
            "results": best_of_each(lang, sql, params, per) if totals else [],
            "suggestion": None if totals else suggest(lang, query_terms)}
