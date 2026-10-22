# Open Word Bible

Open Word Bible translates the Bible from Hebrew and Greek into modern
languages: English first, then Spanish, French, Swahili, Vietnamese, Korean
and Portuguese.

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

`content/<BOOK>/` holds the translation, one folder per book. What is
drafted, and in which languages, is listed on the site's Read page
(<https://openwordbible.org/read/>), built from `content/` itself, so this
README does not keep a list that every new chapter would have to edit.
English runs ahead of the other languages; `docs/english-style.md` is the
brief for drafting it and `data/key_terms.json` the settled key terms.
`docs/corinthians-terms.md` proposes the recurring choices for 1 and 2
Corinthians. `docs/french-style.md`, `docs/swahili-style.md`,
`docs/vietnamese-style.md`, `docs/korean-style.md` and
`docs/portuguese-style.md` are the briefs for French, Swahili, Vietnamese,
Korean and (Brazilian) Portuguese.

Adding a book needs no shared file edited: `data/books.json` already lists
all 66 books (names in each language, chapter counts), section headings go
in `data/headings/<BOOK>.json`, chapter summaries in
`data/summaries/<BOOK>.json`, the sentences where Jesus speaks (the
reader's red letters, found in each language from its own quotation marks;
`owb/words_of_jesus.py`) in `data/words_of_jesus/<BOOK>.json`, and each share card's digest sits in its own
`web/og/<card>.digest`. Two pull requests that add different chapters touch
different files, so they don't conflict.

Old Testament verses are numbered as in the Hebrew text (a psalm's title is
verse 1), not as in English Bibles; `data/versification.json` maps one to the
other (`owb/versification.py`).

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

Poetry is set in lines. A rendering marks each break inside a verse with
`\q ` (`"my shepherd; \q I will not lack"`); a verse start is always a line
start, and a rendering with no `\q` is prose. Lines are wording, so each
language and level places its own, following the Hebrew accents' division
of the verse; `scripts/poetry_lines.py` prints that division beside the
renderings, and `docs/english-style.md` ("Poetry: lines") gives the rules.
Everywhere text is shown on one line, a break reads as a space
(`markup.flat`). Psalms 1, 2, 3 and 23 are marked as a pilot.

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
translation: `data/headings/<BOOK>.json` keys each one by the record it stands
above, per language, and they stay AI drafts until a named reviewer
approves them. A page shows a heading only in the language its sentence is
shown in.

A chapter summary is one or two sentences under a chapter's title saying
what the chapter is about. `data/summaries/<BOOK>.json` keys each by chapter
number, per language. Like headings, summaries are AI drafts until reviewed,
state the sense only (no reader settings), and are shown in the language the
chapter's text is shown in: the page's language, or English, marked as such,
where the chapter has no sentence in the page's language yet.

## Cross-references

Beside the text, on screens wide enough, each verse's margin lists other
passages on the same subject; the reasoning panel lists a chosen sentence's
all, so phones have them too. They come from OpenBible.info's crowd-voted
cross-references (CC BY, credited on the page), not from us: like headings
they are an aid, not translation, and the reader can hide them.
Pointing at a reference (tapping it on a touch screen) previews the
passage without leaving the page; on phones, where the margin has no room, a
small dot by a verse number opens its references' previews. The margin shows
in the Study and Interlinear views. Previews read `/verses/<BOOK>/<chapter>.json`,
one small file per chapter written by the build: our text at every level, with
its reader-setting spans, or for a verse not translated yet the comparison
text, labelled as not ours.
`scripts/extract_crossrefs.py` keeps each verse's most-voted few in
`data/crossrefs/<BOOK>.json`, with both ends in our verse numbering
(`owb/crossrefs.py`), so the build needs no source clone.

## Reader settings

Reader settings are stored as marked alternatives inside the text. The first
option is the default:

    the light of {{gender:all people|men}}

Settings: `gender`, `christos`, `divine_name`, `deity_pronoun`, `units`,
`plural_you` (a future `spelling` setting needs a reader control first).
`owb/markup.py` and `web/markup.js` list and render the spans;
`tests/markup_vectors.json` holds the two to the same answers.

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
    python3 scripts/build_versification.py    # rebuild data/versification.json after a source update
    python3 scripts/extract_comparison.py     # rebuild data/comparison/ (WEB, RV1909) after a source update
    python3 scripts/extract_crossrefs.py      # rebuild data/crossrefs/ after a source update

## The site

`scripts/build_site.py` builds a static site into `site/` from `content/` and
the word extracts in `data/grc/`. It needs no source clones and nothing beyond
Python 3. Preview it with:

    python3 scripts/build_site.py && python3 -m http.server -d site 8000

`render.yaml` deploys it to Render as a static site on openwordbible.org.
The build also writes `sitemap.xml`, `robots.txt` and a canonical link on
every page, all using `SITE_URL` in `scripts/build_site.py`.

For search engines and AI tools, which mostly read a page as served:

- A chapter page has its Balanced text and its footnotes in the HTML
  (`chapter_text`, `chapter_notes`); the reader redraws both in place.
- Chapter pages, articles and the English about page (the records as a
  dataset) carry schema.org data.
- `/about/status/` counts the sentences drafted and reviewed, by status,
  language and book, from `content/` at every build.
- `llms.txt` is a short guide to the site for AI tools, with the same counts.

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

A translation copies its English article's `date`, `order`, `section` and
`part`, and records the English it was made from as `source:`, a digest
written by `python3 scripts/check_translations.py --stamp
articles/<lang>/<slug>.md`. Stamp a translation when you write it and again
when you bring it up to date. `python3 scripts/check_translations.py` lists,
for each language, the articles not yet translated and the translations whose
English has changed since they were stamped (`scripts/check.sh` prints it).

To add a language: list it in `data/languages.json` (its code, English and
own names, quotation marks, and any reader setting only it has), add every
book's name in it to `data/books.json`, write `i18n/<lang>.json`, add its
words to `owb/morph.py`, and run `python backend/manage.py makemigrations
accounts` so it can have language reviewers. The site, the validator and the
backend all read the list from `owb/languages.py`. A drafting brief in `docs/<language>-style.md` settles
the book-wide wording choices.

### Book pages

A book has a page (`/jhn/`) once it has an introduction:
`data/intros/<BOOK>.md` in English, `data/intros/<lang>/<BOOK>.md` in
another language. The file starts with a front matter block holding only
`summary:` (one sentence, for the page and link previews), and its body is
Markdown as in an article, placeholders included. The page adds an outline
of the chapters from their section headings and the articles that read the
book. Chapter pages link to it and carry a breadcrumb trail
(Read › book › chapter) in their schema.org data. An introduction is a draft
until a named reviewer has checked it, and its page says so.

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

### Verse of the day

The home page shows one verse a day from `data/verse_of_the_day.json`, in
turn. `/verse-of-the-day.xml` (and `/es/verse-of-the-day.xml`, ...) is the
same as an Atom feed: the last 14 days up to the day the site was built,
each with the verse, the notes that say why it reads as it does, and a link
that opens its reasoning in the reader.

### Comparing translations

`/compare/?v=JHN.3.16` sets one verse of ours, at its three levels, beside
the Berean Standard Bible, the World English Bible and the Reina-Valera 1909,
then lists the decisions that say why ours reads as it does. The reader's
verse panel links each verse there. It is one page per language
(`web/compare.js`), not a page per verse: our text and decisions come from
the verse's chapter page, and the other Bibles from
`/editions/<BOOK>/<chapter>.json`, written by the build from
`data/comparison/` in our verse numbering. They are for comparison only.

### Dictionary words

`/word/?w=<lemma>` is a Greek, Hebrew or Aramaic dictionary form: its
MACULA glosses and how often each is given, how often and where it occurs
in the translation so far, its key-term page if it has one, and the
translation decisions that name it. The word panel in the reader links each
word there. Like the comparison page it is one page per language
(`web/word.js`); the build writes the words to 256 shards,
`/words/<n>.json`, `n` being a hash of the lemma that `build_site.word_shard`
and `web/word.js` compute alike (`tests/word_shard_vectors.json`). MACULA's
word-sense fields are never used.

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

The API answers each search (`/api/search/`, below), using Postgres
full-text search, as Ochorus does. It searches one set of documents per
interface language, which `search_documents` in `scripts/build_site.py`
lists:

- every sentence, at each level, with its setting spans kept;
- every note, both the meaning notes and the wording notes for the shown
  language;
- the articles and the passages.

`web/search.js` asks the API as the reader types. The build writes only a
small file per language (`search-ui-en.json`, `search-ui-es.json`) with the
interface text, the palette's page shortcuts and the book names. Until the
API had search, the build wrote each language's whole index
(`search-en.json`, 22 MB) and the browser searched it; the service worker
drops copies of it that browsers kept.

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
- **export** (in staff): the site admin's Export section downloads one
  language at one level as a zip of USFM books or as JSON, for Bible
  software and the apps that carry our text (`owb/export.py`). Reader
  settings are applied, poetry runs on one line, Old Testament verses take
  English numbers by default (a psalm title becomes the chapter's `\d`
  title), and untranslated verses are left out; each file's
  `manifest.json` gives its licence, review states and missing verses.
- **search** (in translation): `import_content` brings the search tables
  up to date with `search_documents` in `scripts/build_site.py`, in every
  site language, rewriting only the entries whose documents changed. Words are matched by the
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

On Render (render.yaml) every deploy migrates, runs `import_texts --missing`
(which fetches and imports only the editions not yet loaded) and imports the
content/ files changed since the last deploy (`import_content --all` imports
every file and rewrites all of search). Errors and warnings go to the log, and to Sentry when `SENTRY_DSN`
is set; no query strings or searches are sent.
