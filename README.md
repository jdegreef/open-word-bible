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

Content: `content/JHN/JHN.1.1-18.json` (John 1:1–18) and
`content/PHP/PHP.4.1-9.json` (Philippians 4:1–9), in English and Spanish.

A record is one sentence of the source, not one verse. It ends where the
SBLGNT ends a sentence: a full stop, a question mark, or a raised dot (·)
where the next clause stands on its own. So a verse may hold two records
(Philippians 4:5) and a record may run across verses (John 1:12–13, marked
with `\v 13` in the renderings). A record that reads the punctuation
differently, as John 1:3 does with its last two words, says so in a
`punctuation` meaning decision. `owb.validate` enforces this, and
`build_skeleton.py` starts new passages with one record per sentence.

Greek or Hebrew quoted in a gloss, rendering or decision must be copied from
the source data: the validator rejects any word that is not, code point for
code point, a form or lemma in MACULA.

## Reader settings

Reader settings are stored as marked alternatives inside the text. The first
option is the default:

    the light of {{gender:all people|men}}

Settings: `gender`, `christos`, `divine_name`, `units`, `deity_pronoun`,
`spelling`. `owb/markup.py` lists and renders the spans.

## Licences

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
    python3 scripts/extract_tokens.py         # refresh data/grc/ after adding verses

## The site

`scripts/build_site.py` builds a static site into `site/` from `content/` and
the word extracts in `data/grc/`. It needs no source clones and nothing beyond
Python 3. Preview it with:

    python3 scripts/build_site.py && python3 -m http.server -d site 8000

`render.yaml` deploys it to Render as a static site on openwordbible.org.

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
- **api**: read-only JSON at `/api/editions/`, `/api/text/<BOOK>/<ch>/` and
  `/api/passages/<BOOK>/<ch>/`. The Django admin at `/admin/` is the first
  review tool.

Local setup:

    pip install -r backend/requirements.txt
    python scripts/fetch_sources.py                       # pinned sources into vendor/
    export DATABASE_URL=postgres://postgres@localhost:5432/owb DJANGO_DEBUG=1
    python backend/manage.py migrate
    python backend/manage.py import_texts                 # about 90 seconds
    python backend/manage.py import_content
    python backend/manage.py test backend_tests           # needs Postgres
