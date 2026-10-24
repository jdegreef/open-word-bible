"""Search: Postgres full-text search over what the site shows (GET /api/search/).

The site's static build already decides what search can find in each site
language: search_documents in scripts/build_site.py lists every passage,
sentence, note and article, with what the page needs to show each one.
rebuild() stores those same documents here, so the site and the API never
disagree about what exists. import_content calls it after every import; it
rewrites only the entries whose documents changed (plan).

Matching follows the language of each document's own text, not the
site's: notes are written in English, and a sentence not yet translated is
shown, and found, in English. Each language has a text search
configuration that removes accents and then stems (migrations 0003 and
0009): owb_english, owb_spanish, owb_french, owb_portuguese, and
owb_simple for languages Postgres has no stemmer for. Every entry is also
indexed word for word (owb_simple, the lowest weight), so words a stemmer
drops ("I am") or shortens ("runn" while typing "running") still match. A
query word matches an entry in its stemmed forms, in the entry's own
language only, or word for word as the start of a word (tsquery explains
why). A "quoted phrase" matches word for word, in order.
"""
import functools
import hashlib
import itertools
import json
import re
import subprocess
import sys
import time
import unicodedata
from collections import Counter
from typing import NamedTuple

from django.conf import settings
from django.db import connection, transaction

from translation.models import SearchEntry, SearchLanguage, SearchWord

# The document kinds, by the names the API uses and the site's one-letter codes.
KINDS = {"passage": "c", "verse": "v", "note": "n", "article": "a"}
NAMES = {code: name for name, code in KINDS.items()}
CONFIGS = {"en": "owb_english", "es": "owb_spanish", "fr": "owb_french", "pt": "owb_portuguese"}
SIMPLE = "owb_simple"
MIN_QUERY = 2
SPAN = re.compile(r"\{\{([a-z_]+):([^{}]*)\}\}")
VERSE_MARK = re.compile(r"\\v \d+ ?")
# Between fields and alternatives, so a phrase never runs from one into the next.
GAP = " ‖ "


def config(lang):
    return CONFIGS.get(lang, SIMPLE)


@functools.cache
def _marks():
    """Every combining mark, for str.translate to remove."""
    return dict.fromkeys(c for c in range(sys.maxunicode + 1) if unicodedata.combining(chr(c)))


def fold(text):
    """Lower case, accents removed, curly quotes straightened (as the site's
    search.js folds text)."""
    # Composed again after the marks go, so a Korean syllable stays one
    # character, as Postgres indexes it (NFD splits it into its letters).
    text = unicodedata.normalize("NFC", unicodedata.normalize("NFD", text.lower()).translate(_marks()))
    text = text.replace("\u0111", "d")   # Vietnamese đ, as unaccent does
    return re.sub("[‘’ʼ]", "'", re.sub("[“”«»]", '"', text))


# ---- Building the tables ----------------------------------------------------

def site_build(lang=None):
    """scripts/build_site.py, with its caches cleared, so it reads content/ afresh,
    keeping only what search needs of each record (SEARCH_ONLY), in lang
    and English (SEARCH_LANG). Every language's renderings at once came to
    outgrow the API's 512 MB."""
    scripts = str(settings.REPO_ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import build_site
    build_site.SEARCH_ONLY = True
    build_site.SEARCH_LANG = lang
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


ENTRY_COLUMNS = ("language", "kind", "position", "sub", "config", "title", "extra", "body", "doc")


def _copy(cursor, table, columns, rows):
    """Load rows into table with COPY: many times faster than INSERTs for
    the tens of thousands of entries a rebuild writes."""
    with cursor.cursor.copy(f"COPY {table} ({', '.join(columns)}) FROM STDIN") as copy:
        for row in rows:
            copy.write_row(row)


def _jsonb_order(value):
    """value with every object's keys in jsonb's order: shortest first, then
    in byte order."""
    if isinstance(value, dict):
        return {k: _jsonb_order(value[k]) for k in sorted(value, key=lambda k: (len(k.encode()), k.encode()))}
    if isinstance(value, list):
        return [_jsonb_order(v) for v in value]
    return value


def jsonb_text(value):
    """value as Postgres prints it as jsonb (doc::text): keys in jsonb's
    order, ", " and ": " between items. key() hashes this, so a document
    built here can be matched with the one already stored without sending it
    to the database. One json.dumps for the whole value: a rebuild keys every
    document in every language, and a call for each string took most of a
    no-op rebuild."""
    return json.dumps(_jsonb_order(value), ensure_ascii=False)


# The same key, worked out by the database for the entries it holds. An
# entry's title, extra, body and vector follow from its config and doc.
KEY_SQL = "md5(config || doc::text)"


def key(config_name, doc):
    return hashlib.md5((config_name + jsonb_text(doc)).encode()).hexdigest()


class Change(NamedTuple):
    entries: int
    added: int
    removed: int


def plan(old, new):
    """Which entries to keep, and where the new ones go.

    old: the stored entries as (id, position, sub, key), in order; new: the
    documents' keys, in order. Returns (ids to delete, [(position, sub)] for
    and [(index in new, position, sub)] for each document that is not kept),
    or None when the new ones cannot be fitted between those kept.

    An entry whose document is unchanged keeps its row, vector and place, so
    a rebuild writes only what changed: computing the vectors is most of the
    work, and on a small database a full rebuild takes longer than a deploy
    may. The order is (position, sub): documents added after a kept entry at
    (p, s) take (p, s + 1), (p, s + 2), ..., so nothing else moves."""
    stored = {}
    for row in old:
        stored.setdefault(row[3], []).append(row)
    kept, last = [], (-1, -1)
    for i, k in enumerate(new):
        # A key can repeat (two identical notes): match them in order. A
        # stored entry that has moved behind one kept already is replaced.
        rows = stored.get(k)
        if rows and (rows[0][1], rows[0][2]) > last:
            row = rows.pop(0)
            kept.append((i, row))
            last = (row[1], row[2])
    keep_ids = {row[0] for _, row in kept}
    delete = [row[0] for row in old if row[0] not in keep_ids]
    places = []
    bounds = [(-1, None)] + [(i, (row[1], row[2])) for i, row in kept] + [(len(new), None)]
    for (i, before), (j, after) in itertools.pairwise(bounds):
        count = j - i - 1
        if not count:
            continue
        if before is None:
            # Before the first entry kept: the position below it.
            if after is not None and after[0] == 0:
                return None
            p = after[0] - 1 if after is not None else 0
            places += [(i + 1 + n, p, n) for n in range(count)]
        else:
            p, s = before
            if after is not None and after[0] == p and after[1] - s <= count:
                return None
            places += [(i + n, p, s + n) for n in range(1, count + 1)]
    return delete, places


def rebuild(full=False, until=None, separate=False):
    """Bring the search tables up to date with the site's documents in every
    site language, rewriting only the entries whose documents changed (all
    of them with full=True). Each language is a transaction of its own, so
    a deploy stopped part way keeps the languages it finished, and the next
    picks up from there. With until (a time.monotonic() value), no language
    is started after that time: those left out wait for the next rebuild.
    With separate=True, each language is updated in a process of its own
    (manage.py update_search), so memory doesn't build up from one to the
    next. Returns {language: Change} for the languages it brought up to date."""
    site = site_build()
    with transaction.atomic():
        SearchLanguage.objects.exclude(code__in=site.LANGUAGES).delete()
        SearchEntry.objects.exclude(language__in=site.LANGUAGES).delete()
        SearchWord.objects.exclude(language__in=site.LANGUAGES).delete()
    changes = {}
    try:
        for lang in site.LANGUAGES:
            if until is not None and time.monotonic() > until:
                break
            changes[lang] = (_rebuild_separately(lang, full) if separate
                             else _rebuild_language(site_build(lang), lang, full))
        return changes
    finally:
        # Records that hold one language's renderings must not outlive the
        # rebuild: anything else reading build_site would find the others empty.
        site_build()


def _rebuild_separately(lang, full):
    command = [sys.executable, str(settings.BASE_DIR / "manage.py"), "update_search", lang]
    if full:
        command.append("--all")
    out = subprocess.run(command, check=True, stdout=subprocess.PIPE, text=True).stdout
    return Change(**json.loads(out.splitlines()[-1]))


@transaction.atomic
def _rebuild_language(site, lang, full):
    data = site.search_documents(lang)
    # One language's documents at a time: search_documents caches each.
    site.search_documents.cache_clear()
    SearchLanguage.objects.update_or_create(code=lang, defaults=dict(books=data["books"], pages=data["pages"]))
    docs = [(doc, config(doc.get("l", lang))) for doc in data["docs"]]
    entries, words = _table(), SearchWord._meta.db_table
    with connection.cursor() as cursor:
        # A full rebuild, or the first, matches nothing, so needs no keys.
        cursor.execute(f"SELECT id, position, sub, {'NULL' if full else KEY_SQL} FROM {entries} "
                       "WHERE language = %s ORDER BY position, sub", [lang])
        old = cursor.fetchall()
        # When the new documents don't fit between the ones kept (rare:
        # one added before the first), every entry is replaced.
        delete, places = (None if full or not old else plan(old, [key(c, doc) for doc, c in docs])) or (
            [row[0] for row in old], [(i, i, 0) for i in range(len(docs))])
        if not delete and not places and SearchWord.objects.filter(language=lang).exists():
            return Change(len(docs), 0, 0)
        if delete:
            cursor.execute(f"DELETE FROM {entries} WHERE id = ANY(%s)", [delete])
        # New entries go through a scratch table, so each row is written
        # once, with its vector, rather than inserted and then updated.
        cursor.execute("""CREATE TEMPORARY TABLE search_load (language text, kind text,
            position integer, sub integer, config text, title text, extra text, body text, doc jsonb)
            ON COMMIT DROP""")
        # A generator: a full rebuild's rows, held at once, are as big again
        # as the documents.
        rows = ((lang, docs[i][0]["k"], position, sub, docs[i][1], *fields(docs[i][0]),
                 json.dumps(docs[i][0], ensure_ascii=False)) for i, position, sub in places)
        _copy(cursor, "search_load", ENTRY_COLUMNS, rows)
        cursor.execute(f"""INSERT INTO {entries} ({', '.join(ENTRY_COLUMNS)}, vector)
            SELECT {', '.join(ENTRY_COLUMNS)},
              setweight(to_tsvector(config::regconfig, title), 'A')
              || setweight(to_tsvector(config::regconfig, extra), 'B')
              || setweight(to_tsvector(config::regconfig, body), 'C')
              || setweight(to_tsvector('{SIMPLE}', concat_ws(' ', title, extra, body)), 'D')
            FROM search_load ORDER BY position, sub""")
        # Dropped now as well as at commit: inside a test the transaction
        # never commits, and the next rebuild would find it still there.
        cursor.execute("DROP TABLE search_load")
        found = Counter()
        for doc, _ in docs:
            found.update(w for w in re.findall(r"[^\W\d_][\w']{2,62}", fold(" ".join(fields(doc)))))
        SearchWord.objects.filter(language=lang).delete()
        _copy(cursor, words, ("language", "word", "count"), ((lang, w, n) for w, n in found.items()))
        # Fresh statistics for the planner. Without them it can take the
        # tables for empty (after a full rebuild's delete, or a vacuum that
        # ran while they were) and plan a search that ranks every match
        # once for every entry: hours instead of milliseconds.
        for model in (SearchEntry, SearchWord, SearchLanguage):
            cursor.execute(f"ANALYZE {model._meta.db_table}")
    return Change(len(docs), len(places), len(delete))


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


class Query(NamedTuple):
    """A query as SQL for a CTE named q: one tsquery column per text search
    configuration used on a site language's pages (sql, with params), and
    the expressions that match and rank an entry e with its own column."""
    sql: str
    params: list
    configs: list

    @property
    def match(self):
        return "(" + " OR ".join(f"(e.config = '{c}' AND e.vector @@ q.{c})" for c in self.configs) + ")"

    def own(self, e="e"):
        """The tsquery for entry e's own configuration."""
        return f"CASE {e}.config " + " ".join(f"WHEN '{c}' THEN q.{c}" for c in self.configs) + " END"


def tsquery(lang, query_terms):
    """The query for lang's pages. Each entry is matched in its own text's
    language: lang's, or English for notes and sentences not yet translated.
    A word matches there in its stemmed forms ("loving" finds "love"), or
    word for word as the start of a word, so results appear as the reader
    types; a single letter matches only itself. Stemmed forms never match
    as prefixes, nor across languages: Spanish "verbo" stems to "verb",
    which would otherwise find English notes about verbs. A quoted phrase
    matches word for word only, in order: a stemmer drops common words
    ("from", "above"), and "born from above" would shrink to "born"."""
    configs = sorted({config(lang), config("en")})
    columns, params = [], []
    for cfg in configs:
        parts = []
        for text, phrase in query_terms:
            prefix = text if len(text) == 1 else f"{text}:*"
            # Only letters and digits reach to_tsquery, so a query can't
            # inject tsquery operators.
            if phrase:
                parts.append("phraseto_tsquery(%s::regconfig, %s)")
                params += [SIMPLE, text]
            elif cfg == SIMPLE:
                parts.append("to_tsquery(%s::regconfig, %s)")
                params += [SIMPLE, prefix]
            else:
                parts.append("(to_tsquery(%s::regconfig, %s) || to_tsquery(%s::regconfig, %s))")
                params += [cfg, text, SIMPLE, prefix]
        columns.append(" && ".join(parts) + f" AS {cfg}")
    return Query("SELECT " + ", ".join(columns), params, configs)


def _table():
    return SearchEntry._meta.db_table


def _rows(sql, params):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def _headline(query, e="e"):
    """A short passage of a note's reason or an article's text around the
    match, with the matches marked ⟦ ⟧ (e is the entry's table alias)."""
    return (f"CASE WHEN {e}.kind IN ('n', 'a') THEN ts_headline({e}.config::regconfig, {e}.body, {query.own(e)}, "
            "'StartSel=⟦, StopSel=⟧, MinWords=18, MaxWords=40, ShortWord=2, "
            "MaxFragments=1, FragmentDelimiter=\" … \"') END")


def _result(doc, headline):
    # Django has psycopg return jsonb as text, for JSONField to parse; raw
    # queries parse it themselves.
    if isinstance(doc, str):
        doc = json.loads(doc)
    # An article's whole text ("x", kilobytes each) stays out of answers:
    # the headline shows the part that matched.
    if doc["k"] == "a":
        doc = {k: v for k, v in doc.items() if k != "x"}
    if headline and "\u27e6" in headline:
        return {**doc, "hl": headline}
    return doc


def counts(lang, query):
    rows = _rows(f"""WITH q AS ({query.sql})
        SELECT e.kind, count(*) FROM {_table()} e, q
        WHERE e.language = %s AND {query.match} GROUP BY e.kind""", [*query.params, lang])
    return {NAMES[kind]: n for kind, n in rows}


def best_of_each(lang, query, per):
    """The best `per` documents of each kind."""
    # One pass over the matches, with no join back to the table: a join
    # lets the planner rank every match again for each row it joins.
    rows = _rows(f"""WITH q AS ({query.sql})
        SELECT h.doc, {_headline(query, "h")} FROM (
          SELECT e.doc, e.kind, e.config, e.body, row_number() OVER (
            PARTITION BY e.kind ORDER BY ts_rank_cd(e.vector, {query.own()}) DESC, e.position, e.sub) AS n
          FROM {_table()} e, q WHERE e.language = %s AND {query.match}) h, q
        WHERE h.n <= %s ORDER BY h.kind = 'c' DESC, h.kind = 'v' DESC, h.kind = 'n' DESC, h.n""",
                 [*query.params, lang, per])
    return [_result(doc, hl) for doc, hl in rows]


def page(lang, query, kind, offset, limit, sort):
    order = "e.position, e.sub" if sort == "order" else f"ts_rank_cd(e.vector, {query.own()}) DESC, e.position, e.sub"
    rows = _rows(f"""WITH q AS ({query.sql})
        SELECT e.doc, {_headline(query)} FROM {_table()} e, q
        WHERE e.language = %s AND e.kind = %s AND {query.match}
        ORDER BY {order} LIMIT %s OFFSET %s""", [*query.params, lang, KINDS[kind], limit, offset])
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
                                      doc__c=ref["chapter"]).order_by("position", "sub").values_list("doc", flat=True)
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
        if counts(lang, tsquery(lang, [(text, False)])):
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
    return suggestion if counts(lang, tsquery(lang, terms(suggestion))) else None


# ---- The search ------------------------------------------------------------

def search(lang, q, kind=None, offset=0, limit=20, sort="relevance", per=8):
    """The API's answer to q on lang's pages. With no kind: the reference
    if q is one, or else counts for each kind, the best `per` of each, and
    a suggestion when nothing matched. With a kind: one page of that kind,
    by relevance or in Bible order ("order"), with the counts of every kind."""
    q = q.replace("\x00", "").strip()[:200]
    answer = {"query": q, "lang": lang}
    query_terms = terms(q)
    if len(q) < MIN_QUERY or not query_terms:
        return {**answer, "reference": None, "totals": {}, "results": [], "suggestion": None}
    query = tsquery(lang, query_terms)
    if kind:
        # Every kind's count comes with the page, for the site's filters.
        totals = counts(lang, query)
        total = totals.get(kind, 0)
        return {**answer, "type": kind, "sort": sort, "offset": offset, "total": total, "totals": totals,
                "results": page(lang, query, kind, offset, limit, sort) if total > offset else []}
    books = SearchLanguage.objects.get(code=lang).books
    ref = reference(q, books, lang)
    if ref:
        # A reference is answered by its verses alone: its words and numbers
        # would otherwise match every note that mentions them.
        return {**answer, "reference": ref, "totals": {}, "results": [], "suggestion": None}
    totals = counts(lang, query)
    return {**answer, "reference": None, "totals": totals,
            "results": best_of_each(lang, query, per) if totals else [],
            "suggestion": None if totals else suggest(lang, query_terms)}
