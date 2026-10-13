"""Compare the site's search with the API's, query by query.

Search is moving from the browser (web/search.js over the static index the
build writes, search-<lang>.json) to the API (/api/search/, Postgres
full-text search). Before the site switches over, this checks that the API
finds everything the browser finds. It may find more: it also matches other
forms of a word ("loving" finds "love").

For each query and site language it fetches every result of each kind from
both: the browser's matching is applied here to the live index (the rules in
search.js, ported below), and the API is paged through. It prints a Markdown
report and exits non-zero when the API misses something the browser finds.

Usage: python3 scripts/compare_search.py [--site URL] [--api URL] [--lang en] [-q QUERY ...]

The API allows 120 searches a minute, so requests are paced; a full run
takes a few minutes. Run it when the site and the API have deployed the same
commit of main, or documents added in between show up as differences.
"""
import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

SITE = "https://openwordbible.org"
API = "https://api.openwordbible.org"
KINDS = {"c": "passage", "v": "verse", "n": "note", "a": "article"}
# Words, phrases, half-typed words and references in each site language.
QUERIES = {
    "en": ["light", "grace", "love", "Messiah", "peace", "faith", "Word", "joy", "born again",
           '"born from above"', '"I am"', "ligh", "mess", "Eden", "wreath", "God's love",
           "John 3:16", "Fil 4:6-7"],
    "es": ["senor", "gracia", "luz", "Verbo", "paz", "wreath", "Juan 3:16"],
    "fr": ["lumiere", "grâce", "Agneau", "vie", "Jean 1:14"],
    "sw": ["neema", "Neno", "nuru", "Mungu", "Yohana 1:14"],
}
PAGE = 50
# The API pages no further than this offset (api/views.py).
MAX_OFFSET = 1000
PAUSE = 0.55   # 120 requests a minute
# The site turns away Python's default user agent.
HEADERS = {"User-Agent": "open-word-bible scripts/compare_search.py"}


def fetch(url, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=timeout)


# ---- The browser's matching (web/search.js) ---------------------------------

SPAN = re.compile(r"\{\{([a-z_]+):([^{}]*)\}\}")
VERSE_MARK = re.compile(r"\\v \d+ ?|\\q ?")


def fold(text):
    """search.js fold(): lower case, accents removed, curly quotes straightened."""
    text = unicodedata.normalize("NFD", text)
    text = re.sub("[\u0300-\u036f]", "", text).lower()
    return re.sub("[\u201c\u201d\u00ab\u00bb]", '"', re.sub("[\u2018\u2019\u02bc]", "'", text))


def parse(q):
    """search.js parse(): "quoted phrases" whole, other words split at
    anything but letters, digits and apostrophes; each matches at the start
    of a word."""
    terms = []
    for m in re.finditer(r'"([^"]+)"|(\S+)', fold(q)):
        parts = [m[1].strip()] if m[1] else re.split(r"[^\w']+|_+", m[2])
        for p in parts:
            p = p.strip("'")
            if p and p not in terms:
                terms.append(p)
    return [re.compile(r"(?:^|[\W_])" + re.escape(t).replace(r"\ ", r"\s+")) for t in terms]


def haystacks(doc):
    """search.js prepare(): the folded fields of a document."""
    k = doc["k"]
    if k == "c":
        return [fold(doc["h"])]
    if k == "v":
        return [fold(" \u2016 ".join(VERSE_MARK.sub(" ", SPAN.sub(lambda m: " ".join(m[2].split("|")), t))
                                     for t in doc["x"].values()))]
    if k == "n":
        return [fold(doc["t"]), fold(" \u2016 ".join(doc["al"])), fold(doc["s"])]
    return [fold(doc["t"]), fold(doc["s"]), fold(doc["x"])]


def browser_results(index, q):
    terms = parse(q)
    found = {kind: [] for kind in KINDS}
    for doc in index["docs"]:
        fields = haystacks(doc)
        if terms and all(any(t.search(f) for f in fields) for t in terms):
            found[doc["k"]].append(doc)
    return found


# ---- The API ----------------------------------------------------------------

def get_json(url):
    for attempt in range(5):
        time.sleep(PAUSE)
        try:
            with fetch(url) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 30))


def api_results(api, lang, q):
    """Every result of each kind, page by page, the totals, and the
    reference if q is one. A kind with more results than the API pages
    through is left empty: only its total can be compared."""
    base = f"{api}/api/search/?" + urllib.parse.urlencode({"q": q, "lang": lang})
    first = get_json(base)
    found = {kind: [] for kind in KINDS}
    for kind, name in KINDS.items():
        if not first["totals"].get(name) or first["totals"][name] > MAX_OFFSET + PAGE:
            continue
        offset = 0
        while offset < first["totals"][name]:
            page = get_json(f"{base}&type={name}&offset={offset}&limit={PAGE}")
            found[kind] += page["results"]
            offset += PAGE
    return first["reference"], first["totals"], found


def key(doc):
    # The API leaves out an article's whole text ("x").
    return json.dumps({k: v for k, v in doc.items() if k != "hl" and not (k == "x" and doc["k"] == "a")},
                      sort_keys=True, ensure_ascii=False)


def describe(doc):
    if doc["k"] in "vn":
        return f'{doc["bk"]} {doc["c"]}:{doc["v"]}' + (f' "{doc["t"][:50]}"' if doc["k"] == "n" else "")
    return doc["t"][:60]


# ---- The report ---------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--site", default=SITE)
    ap.add_argument("--api", default=API)
    ap.add_argument("--lang", action="append", help="Site languages to check (default: all in QUERIES)")
    ap.add_argument("-q", "--query", action="append", help="Queries to check (default: QUERIES)")
    args = ap.parse_args()
    missing_total = 0
    print("| Language | Query | Browser finds | API finds | API misses | API adds |")
    print("|---|---|---|---|---|---|")
    notes = []
    for lang in args.lang or QUERIES:
        prefix = "" if lang == "en" else f"/{lang}"
        page = fetch(f"{args.site}{prefix}/search/").read().decode()
        index_path = re.search(r'name="owb-search" content="([^"]+)"', page)[1]
        index = json.load(fetch(args.site + index_path, timeout=60))
        for q in args.query or QUERIES[lang]:
            ref, totals, api = api_results(args.api, lang, q)
            if ref:
                # The browser answers a reference with its verses alone too (#55).
                chapter = next((b.get("chapters", {}).get(str(ref["chapter"])) for b in index["books"]
                                if b["code"] == ref["book"]), None)
                ok = (chapter is None and "url" not in ref) or (
                    chapter and ref.get("url", "").split("#")[0] == chapter["url"]
                    and set(ref.get("shown", [])) <= set(chapter["verses"]))
                print(f"| {lang} | {q} | reference | {ref['label']} \u2192 {ref.get('url', 'not translated')} "
                      f"| {'' if ok else 'disagrees'} | |")
                missing_total += not ok
                continue
            browser = browser_results(index, q)
            counts, misses, adds = [], [], []
            for kind, name in KINDS.items():
                b, a = {key(d): d for d in browser[kind]}, {key(d): d for d in api[kind]}
                total = totals.get(name, 0)
                if b or total:
                    counts.append((name, len(b), total))
                if total > MAX_OFFSET + PAGE:
                    # Too many to page through: compare how many.
                    shortfall = len(b) - total
                    if shortfall > 0:
                        misses += [None] * shortfall
                    continue
                misses += [b[k] for k in b.keys() - a.keys()]
                adds += [a[k] for k in a.keys() - b.keys()]
            browser_found = ", ".join(f"{b} {name}s" for name, b, _ in counts if b) or "nothing"
            api_found = ", ".join(f"{a} {name}s" for name, _, a in counts if a) or "nothing"
            print(f"| {lang} | {q} | {browser_found} | {api_found} | {len(misses) or ''} | {len(adds) or ''} |")
            missing_total += len(misses)
            if misses:
                shown = [describe(d) for d in misses if d][:8]
                notes.append(f"- **{lang} `{q}`, missed by the API ({len(misses)}):** "
                             + ("; ".join(shown) or "counted, too many to list") + (" \u2026" if len(misses) > 8 else ""))
            if adds:
                notes.append(f"- {lang} `{q}`, found only by the API (first few): "
                             + "; ".join(describe(d) for d in adds[:4]))
    if notes:
        print("\n" + "\n".join(notes))
    print(f"\n{'No query found less through the API.' if not missing_total else f'{missing_total} documents missed by the API.'}")
    return 1 if missing_total else 0


if __name__ == "__main__":
    sys.exit(main())
