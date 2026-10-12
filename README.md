# Open Word Bible

Open Word Bible translates the Bible from Hebrew and Greek into modern
languages: English first, then Spanish, French, Portuguese and Swahili.

Every translated sentence carries a **reasoning record**: the original words,
a literal gloss, the translation at three levels, and each translation
decision with its reason. The original-language text is never typed by hand;
it is always loaded from the pinned source data.

## Three levels

| Level    | Code  | Aim                                              |
|----------|-------|--------------------------------------------------|
| Literal  | OWB-L | Follows the original closely; supplied words in [brackets]. |
| Balanced | OWB-B | Accurate and natural.                            |
| Readable | OWB-R | Plain modern language, made explicit where it helps. |

## Reasoning records

A record (`schema/sentence-record.schema.json`) holds one source sentence:
its verse ids, source token ids, literal gloss, renderings per language and
level, optional alignments, decisions and a status (`ai_draft`,
`meaning_reviewed`, `reviewed`, `revised`).

Decisions come in two layers:

- **meaning**: what the original says. Written once per passage and shared
  by every language and level (`language` is `null`).
- **rendering**: how one language says it at one or more levels
  (`language` and `levels` are set).

Each decision names its tokens, category, choice, alternatives and reason,
and whether it is uncertain or needs a footnote.

Content: Genesis 1–12 (`content/GEN/`) in English, with 1–8 also in Spanish; John 1–8
(`content/JHN/`) in English, with chapters 1–5 also in Spanish, chapters
1–2 in French and chapters 1–9 in Swahili; Romans 1–3 and 9–16 (`content/ROM/`) in
English; all of 1 and 2 Corinthians (`content/1CO/`,
`content/2CO/`) in English; all of Galatians (`content/GAL/`) in English; all of Philippians (`content/PHP/`) in English, with chapter 4
also in Spanish; all of Ephesians (`content/EPH/`), Colossians
(`content/COL/`), 1 and 2 Thessalonians (`content/1TH/`, `content/2TH/`) and Philemon (`content/PHM/`) in English; and all of James, 1 and 2 Peter and 1, 2 and 3
John (`content/JAS/`, `content/1PE/`, `content/2PE/`, `content/1JN/`,
`content/2JN/`, `content/3JN/`) in English. English runs
ahead of the other languages; `docs/english-style.md` is the brief for
drafting it and `data/key_terms.json` the settled key terms.
`docs/corinthians-terms.md` proposes the recurring choices for 1 and 2 Corinthians.
`docs/french-style.md` and
`docs/swahili-style.md` are the briefs for French and Swahili.

Matthew 1–9 (`content/MAT/`) is drafted in English.

Psalms 1–9 (`content/PSA/`) are drafted in English.

A record is one sentence of the source, not one verse. It ends where the
SBLGNT ends a sentence: a full stop, a question mark, or a raised dot (·)
where the next clause stands on its own. So a verse may hold two records
(Philippians 4:5) and a record may run across verses (John 1:12–13, marked
with `\v 13` in the renderings). A record that reads the punctuation
differently, as John 1:3 does with its last two words, says so in a
`punctuation` meaning decision. `owb.validate` enforces this, and
`build_skeleton.py` starts new passages with one record per sentence.

Alignments link source tokens to the words of one rendering, so the reader
can light up a Greek word and the English it became. A rendering's
alignments are listed in the order their `target_span`s appear, and each
span is found after the one before (so a repeated "the" is unambiguous);
a span may not hold a verse marker or cut through a setting span
(`markup.alignment_ranges`). A token may appear in more than one alignment
("not yet ... come"), and words with no counterpart are left out. John 2,
English Balanced, is aligned as a pilot.

The Old Testament is translated from the Westminster Leningrad Codex with
MACULA Hebrew word data (`text_id` `WLC@macula-hebrew`, `language` `hbo`, or
`arc` for Aramaic). MACULA Hebrew divides words into morphemes, so a word with
a prefix such as "and" or "the" has two token ids. The codex marks no
sentence ends inside a verse, so a Hebrew record holds whole verses: one by
default, or several where one sentence runs across them. The article that a
preposition swallows (la-, "to the") has a MACULA row with no text; records
and extracts leave it out, and the preposition's code says it is there.

Greek or Hebrew quoted in a gloss, rendering or decision must be copied from
the source data: the validator rejects any word that is not, code point for
code point, a form or lemma in MACULA.

The validator also keeps the two layers apart: a meaning decision may not
use a wording category (`word_choice`, `setting_alternative`, ...), contain a
reader setting, or name a target language. Every setting span needs a
default and at least one distinct, non-empty alternative, and a
`deity_pronoun` alternative only capitalises the default.

## Paragraphs and headings

The reader breaks the text into paragraphs where SBLGNT does: SBLGNT
capitalises a paragraph's first word (`paragraph_starts` in
`scripts/build_site.py`). Section headings are editorial aids, not
translation: `data/headings.json` keys each one by the record it stands
above, per language, and they stay AI drafts until a named reviewer
approves them. A page shows a heading only in the language its sentence is
shown in.

## Reader settings

Reader settings are stored as marked alternatives inside the text. The first
option is the default:

    the light of {{gender:all people|men}}

Settings: `gender`, `christos`, `divine_name`, `units`, `deity_pronoun`,
`spelling`. `owb/markup.py` lists and renders the spans.

## Licences

MACULA's word-sense columns (Louw-Nida `domain` and `ln`; Hebrew SDBH
`lexdomain`, `coredomain`, `contextualdomain`, `sdbh`) are used with
permission but not openly licensed. They are never extracted or published;
`tests/test_licensing.py` checks the extracts and the built site, and the
backend tests check the word table and API.

- Translation, reasoning records and other data in this repository:
  **CC0 1.0** (`LICENSE`).
- Code (`owb/`, `scripts/`, `tests/`): **MIT** (`LICENSE-CODE`).
- Source texts and linguistic data keep their own licences and are not
  included here; they are fetched into `vendor/`. See `CREDITS.md` for the
  required attributions.

## Setup and tests

Python 3, standard library only. GitHub Actions runs the tests, the
validator, the extract check, the site build and the backend tests on every
pull request (`.github/workflows/ci.yml`).

    python3 scripts/fetch_sources.py          # clone pinned sources into vendor/
    python3 -m unittest discover -s tests -t .

To use sources elsewhere, set `OWB_VENDOR` to a directory containing
`sblgnt/`, `macula-greek/`, ... A source may be a git clone without a working
tree; files are then read with `git show` at the pinned commit.

Other tools:

    python3 scripts/build_skeleton.py JHN.1.3 JHN.1.5 -o new.json
    python3 -m owb.validate content/JHN/*.json
    python3 scripts/extract_tokens.py         # refresh data/grc/ and data/hbo/ after adding verses

## The site

`scripts/build_site.py` builds a static site into `site/` from `content/` and
the word extracts in `data/grc/`. It needs no source clones and nothing beyond
Python 3. Preview it with:

    python3 scripts/build_site.py && python3 -m http.server -d site 8000

`render.yaml` deploys it to Render as a static site on openwordbible.org.
The build also writes `sitemap.xml`, `robots.txt` and a canonical link on
every page, all using `SITE_URL` in `scripts/build_site.py`.

### Languages

The whole site, menus and controls included, is built once per interface
language, as on Ochorus: English at the root (`/jhn/1/`), Spanish under
`/es/` (`/es/jhn/1/`), French under `/fr/` (`/fr/jhn/1/`) and Swahili under
`/sw/` (`/sw/jhn/1/`). The footer's Languages row switches to the same page
in another language; the browser remembers the choice and opens later pages
in it. Pages carry `<html lang>`, hreflang links and a canonical URL.

Interface text lives in `i18n/<lang>.json`, one flat catalog per language
with the same keys and `{placeholders}` (`tests/test_languages.py` checks
this). The reader shows each sentence in the page's language, or in grey
English where it is not translated yet.

An article is translated by adding `articles/<lang>/<slug>.md` with the same
slug. Until then, the other language's page shows the English under a note,
names the English page as canonical and stays out of the sitemap.

To add a language: add it to `LANGUAGES` and `BOOK_NAMES` in
`scripts/build_site.py`, write `i18n/<lang>.json`, add its words to
`owb/morph.py`, and add it to `Role.READING_LANGUAGES` and the role
constraint in `backend/accounts/models.py` (with a migration) so it can have
language reviewers. A drafting brief in `docs/<language>-style.md` settles
the book-wide wording choices.

### Articles

Articles live in `articles/*.md`, one file each, starting with a front
matter block:

    ---
    title: Why another Bible translation?
    summary: One sentence for the article list and link previews.
    date: 2026-10-10
    order: 1
    ---

The body is plain Markdown (`##` headings, paragraphs, `-` lists, `>` quotes,
`**bold**`, `*italic*`, `[links](/jhn/1/)`). Greek and Hebrew are never
typed: quote them with placeholders the build fills from `data/grc/` and
`data/hbo/`, and quote our own translation from `content/` the same way:

    {{GREEK:JHN.1.1:14-17}}   words 14-17 of John 1:1, as the SBLGNT has them
    {{HEBREW:GEN.1.1:1-3}}    words 1-3 of Genesis 1:1, as the WLC has them
    {{LEMMA:JHN.1.14:17}}     the dictionary form of word 17 of John 1:14
    {{LEMMA:GEN.1.1:1.2}}     a Hebrew word in parts (prefix, word, suffix):
                              the dictionary form of part 2 of word 1
    {{OWB:JHN.1.1.s1:B}}      our English for that sentence, Balanced level

`tests/test_articles.py` fails if an article contains typed Greek or Hebrew,
an unfilled placeholder or a broken internal link.

### Colour modes

The gear at the top right of every page offers Automatic (follow the device)
and five colour modes: Light, Sepia, Dark, Night and High contrast. The modes
are blocks of colour tokens in `web/style.css`; `web/site.js` runs the menu and
remembers the choice in the browser, and a small script in each page's head
applies it before the first paint.

### Search

Search works as it does on Ochorus. The search button in the header, or
Ctrl K / Cmd K (or `/`) on any page, opens a palette that searches as you
type. Its "All results" row leads to `/search/`. That page groups results
into passages, verses, notes and articles, with filters, and keeps the
query in the address (`?q=`), so a search can be shared. A reference such as
"John 3:16" or "Fil 4:6-7" shows those verses with a link into the reader;
in the palette it is the first row, so Enter goes straight there. The
reader's "Go to…" button, beside the chapter pills, opens the palette.
A verse opened from a result has the query's words marked.

The site is static, so there is no search server. The build writes one
index per interface language (`search-en.json`, `search-es.json`):

- every sentence, at each level, with its setting spans kept;
- every note, both the meaning notes and the wording notes for the shown
  language;
- the articles and the passages.

`web/search.js` loads the index the first time someone searches and matches
in the browser. Matching ignores accents and matches from the start of a
word.

Search is moving to the API, because the index grows by about 2 KB for
every verse translated. `/api/search/` (below) already answers from the
same documents, using Postgres full-text search, as Ochorus does. The next
step switches `web/search.js` over to it, and after that the build stops
writing the index.

### Pointing openwordbible.org at Render

The custom domains are listed in `render.yaml`; the DNS records are set at
the domain registrar. In the Render dashboard, open the `open-word-bible`
static site, then **Settings → Custom Domains**, and check that
`openwordbible.org` and `www.openwordbible.org` are listed (add them if
not). Render shows the exact records to create; they are normally:

| Host  | Type                     | Value                               |
|-------|--------------------------|-------------------------------------|
| `@`   | A (or ALIAS/ANAME)       | Render's IP, `216.24.57.1` (or `open-word-bible.onrender.com` for ALIAS) |
| `www` | CNAME                    | `open-word-bible.onrender.com`      |
| `api` | CNAME                    | `owb-api.onrender.com` (the Django service) |

Remove any other A, AAAA or CNAME records for those hosts (parking pages),
then press **Verify** in Render. Render issues the HTTPS certificates and
redirects `www` to the bare domain once both are verified.

## Backend (Django + Postgres)

`backend/` is a Django project with Django REST Framework, run on Render
against Postgres (`render.yaml`). It holds:

- **texts**: imported editions, verses and words. The base texts are the
  SBL Greek New Testament and the Westminster Leningrad Codex, each with
  MACULA word data. The reference Bibles are the BSB, WEB, ASV, KJV, YLT and
  Reina-Valera 1909, from open-bibles.
- **translation**: our sentence records, renderings, decisions and the review
  trail. `content/` is still the master copy and is loaded with
  `import_content`.
- **api**: read-only JSON at `/api/editions/`, `/api/text/<BOOK>/<ch>/`,
  `/api/passages/<BOOK>/<ch>/` and `/api/search/?q=…&lang=…`. The Django
  admin at `/admin/` is the first review tool.
- **search** (in translation): `import_content` rebuilds the search tables
  from `search_documents` in `scripts/build_site.py`, the same documents as
  the site's search index, in every site language. Words are matched by the
  language of their own text, with accents ignored and stemming for English,
  Spanish and French (Swahili matches whole words and their beginnings).
  `/api/search/` returns the best of each kind (passages, verses, notes,
  articles), or with `&type=` one kind a page at a time (`&offset`,
  `&limit`, `&sort=relevance|order`). A reference such as "John 3:16" is
  answered by its verses alone, and a query that finds nothing gets a "Did
  you mean". Nothing about searches is logged.

Local setup:

    pip install -r backend/requirements.txt
    python scripts/fetch_sources.py                       # pinned sources into vendor/
    export DATABASE_URL=postgres://postgres@localhost:5432/owb DJANGO_DEBUG=1
    python backend/manage.py migrate
    python backend/manage.py import_texts                 # about 90 seconds
    python backend/manage.py import_content
    python backend/manage.py test backend_tests           # needs Postgres
