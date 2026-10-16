# Open Word Bible — conventions for Claude

A CC0 Bible translation from Hebrew and Greek with the reasoning behind every
sentence. The translation charter (decisions, levels, settings, review rules)
lives in the founder's "Open Word Bible — Translation Charter" doc; README.md
summarises the data model.

## Where work goes

- Everything is pushed to https://github.com/jdegreef/open-word-bible.
  `main` is what Render deploys to openwordbible.org.
- Before translating a book, run the `check-book-before-translating` skill:
  other sessions draft in parallel, and a book may already be done or in an
  open pull request.

## Rules that are easy to break

- **Never type Hebrew or Greek.** Original-language text, in records and in
  notes, comes from the pinned source data (MACULA, SBLGNT, OSHB). Look words
  up by script and copy the data's form.
- **Meaning decisions state the sense only.** Wording for a particular
  language belongs in that language's rendering decisions.
- **Settings change wording, never meaning.** A reader setting is a
  `{{setting:default|alt}}` span; disagreements about meaning are decisions
  and footnotes, not settings.
- **Nothing is marked reviewed by Claude.** Records stay `ai_draft` until a
  named human reviewer approves them.
- Don't use or redistribute MACULA's `ln` / `domain` fields (UBS MARBLE,
  used with permission, not openly licensed).
- **Stamp article translations.** After writing or updating
  `articles/<lang>/<slug>.md`, run `python3 scripts/check_translations.py
  --stamp articles/<lang>/<slug>.md` so the report can tell when its English
  changes later.
- **A new interface message goes in every catalog in `i18n/`**, not only the
  languages a branch started with: merge main first, since languages get
  added. `scripts/check_catalogs.py` names anything missing.

`.claude/hooks/guard_edits.py` refuses edits that add Greek or Hebrew not
found in the source data, or a status other than `ai_draft`; CI's
`owb.validate` is still the check of record.

## Before pushing

`scripts/check.sh` runs all of these but the backend tests;
`scripts/check.sh --fast` is the quick pass while working (lint, reader tests,
changed books). `scripts/git-hooks/pre-commit` lints and validates what is
staged (`git config core.hooksPath scripts/git-hooks`).

    OWB_VENDOR=<sources dir> python3 -m unittest discover -s tests -t .
    OWB_VENDOR=<sources dir> python3 -m owb.validate content/*/*.json
    python3 scripts/extract_tokens.py --check   # after adding verses
    python3 scripts/build_site.py               # the site must still build
    uvx ruff@0.16.9 check .                     # lint (settings in pyproject.toml)
    node --test tests/js/*.test.mjs             # reader JS against tests/markup_vectors.json

Backend changes also need, against a Postgres database:

    DATABASE_URL=postgres://... DJANGO_DEBUG=1 python backend/manage.py test backend_tests

`scripts/fetch_sources.py` clones the pinned sources into `vendor/`.

## Backend

- `backend/` is Django + DRF on Postgres (Render). `content/` stays the master
  copy of the translation until the reviewer workflow ships;
  `import_content` loads it and never resets a sentence's review status.
- Reference Bibles (BSB, WEB, KJV, RV1909, ...) are for comparison and review.
  Never use them as the basis for Open Word Bible wording.
