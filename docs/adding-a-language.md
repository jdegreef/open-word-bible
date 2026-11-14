# Adding a reading language

Every file a new reading language touches, in the order to change them, as
Japanese (`ja`) and Ukrainian (`uk`) were added in November 2026 (commits
"Add Japanese as a reading language (code, data and brief)", "Japanese
interface catalog (i18n/ja.json)", "Search Japanese by character bigrams"
and "Add Ukrainian as a reading language"). `README.md` ("Languages") and
`owb/languages.py` give the short version; this is the checklist.

The site, the validator and the backend read the list of languages from
`data/languages.json` through `owb/languages.py`. The moment a code is in
that list, the build needs its catalog and its book names, the tests
check its grammar words, and the validator accepts renderings in it. So
steps 1–6 go into **one pull request**, before any text is drafted; the
style brief may go first, on its own.

Indonesian (`id`) is prepared but not yet added: `docs/indonesian-style.md`,
`docs/indonesian-terms.md`, `docs/review-notes/id-review-checklist.md` and
its book names in `data/books.json` (step 2) are in place. Steps 1 and 3–10
remain.

## 0. Before the code: the brief

- `docs/<language>-style.md`: the drafting brief (levels and their names,
  register, address, the divine name and the setting spans, names, key
  terms, punctuation, numbers, poetry). Copy the structure of a recent one
  (`docs/japanese-style.md`, `docs/indonesian-style.md`).
- `docs/<language>-terms.md`: the glossary of recurring terms and names,
  Genesis to Revelation, so books drafted in parallel agree.
- `docs/review-notes/<code>-review-checklist.md`: the reviewer's starting
  point, and a row in `docs/review-notes/README.md`.

## 1. Register the language

- **`data/languages.json`**: an entry in `reading`, in the order the site
  lists languages (new ones go last): `code`, `name` (English), `native`
  (the footer's language switch), `quotes` (how a quoted verse is wrapped on
  a passage card: `&ldquo;{}&rdquo;` for languages that use “ ”), and
  `settings` only if the language has a reader setting no other has (as
  Spanish has `plural_you`).
- **`README.md`**: the language in the opening list and its brief in the
  list of briefs.
- **Tests** that name every language in a docstring or list:
  `tests/test_languages.py` (the module docstring lists the `/<code>/`
  folders).

## 2. Book names, abbreviations and plans

- **`data/books.json`**: the language's name for all 66 books, after the
  last language on each line, and its word for "Psalm" in the Psalms'
  `chapter_names`. Use the names in common use in that language's Bibles
  (book names are conventions, not wording). Every name is also a search
  and admin alias in every language (`book_aliases` in
  `scripts/build_site.py`, `_aliases` in `backend/staff/verses.py`), so
  check that no new name or its first three letters finds a different book
  than before (a 3-letter prefix finds the first book in canonical order
  whose name starts with it).
- **`data/book_abbreviations.json`**: the short names used in the quotation
  tags of the chapter reader, as the language's Bibles abbreviate them;
  update the file's description, which lists the languages.
- **`data/plans.json`**: each reading plan's name in the language.

## 3. The interface catalog

- **`i18n/<code>.json`**: every message in `i18n/en.json`, with the same
  keys and `{placeholders}`, including the three level names (`levels`).
  Written as a separate commit (Japanese's was "Japanese interface catalog").
- **Every other catalog**: the language's name in `language_names` and in
  `reader.ui.lang_names`, in the order of `data/languages.json`
  (`tests/test_languages.py` checks the order).
- `python3 scripts/check_catalogs.py` names anything missing.

## 4. Grammar words for the word panel

- **`owb/morph.py`**: an entry in `WORDS` (Greek parsing: parts of speech,
  case, number, gender, tense, voice, mood, person, suffixes) and in
  `HEBREW_WORDS` (Hebrew: parts of speech, stems are names, conjugations,
  person, gender, number, state), in the language.
- **`tests/test_morph.py`**: one Greek and one Hebrew assertion for the
  language, as for `uk` and `ja`.

## 5. The backend

- **Reviewer roles**: `python backend/manage.py makemigrations accounts`
  writes the next migration (`0017_<language>_language_reviewers.py` after
  0016), which rewrites the `role_language_matches_kind` constraint with
  the new code in the list of language reviewers.
- **Search**: `backend/translation/search.py` `CONFIGS` maps a language to
  its Postgres text search configuration. Postgres has Snowball stemmers for
  many languages: where it has one, add a migration in
  `backend/translation/migrations/` creating `owb_<language>` (copy
  `0010_russian_search.py`: `COPY = <language>`, mapped `WITH unaccent,
  <language>_stem`) and map the code to it; where it has none, leave the
  code out and it uses `owb_simple`. Languages written without spaces
  need bigrams, as Japanese (`owb_cjk`, `ngrams`). For Indonesian: Postgres
  12 and later has an `indonesian` stemmer; check with `\dFd` on the
  database before writing `0012_indonesian_search.py`.
- **`backend/staff/overlap.py`** `EDITION_LANGUAGE`: the code of the
  language's reference Bibles in the `Edition` table (ISO 639-3: `ind` for
  Indonesian), so the overlap report compares drafts with them.
- The backend tests run against Postgres (`CLAUDE.md`, "Backend").

## 6. Fonts, quotation marks and line breaking

- **Fonts** (`web/fonts/`, `@font-face` in `web/style.css`, which
  `scripts/build_og.py` reuses): a language in the Latin script with no
  extra letters needs nothing (Indonesian). Vietnamese needed the
  Vietnamese subsets, Hindi Noto Devanagari, Amharic Noto Ethiopic;
  Ukrainian's і, ї, є, ґ were already in the Cyrillic subsets; Japanese uses
  the reader's own fonts.
- **`web/style.css`**: `:lang(<code>)` rules where the script needs them
  (Korean `word-break: keep-all`, Japanese strict line breaking and no
  italics).
- **Quotation marks**: the red letters and the quotation checks find
  speech from the marks (`owb/markup.py`, `owb/words_of_jesus.py`).
  Straight `"` and `'` (English, Portuguese, Indonesian) and guillemets
  need nothing; a new kind of mark (Japanese 「 」) needs `_QUOTE_CHARS`,
  `_PAIRS` and the outer/inner choice in `owb/markup.py`, with tests in
  `tests/test_words_of_jesus.py`. A sentence-final mark the site has not
  seen (Japanese 。) goes in the verse-of-the-day regex in `tests/test_site.py`.
- **Apostrophes**: a straight `'` before a Latin letter is read as an
  apostrophe; a language whose apostrophe could be read as a closing quote
  needs its own character (Ukrainian uses U+02BC).

## 7. What does not change

- **Link-preview cards** (`web/og/`, `scripts/build_og.py`) show the English
  and the Greek or Hebrew; a language adds no cards.
- **Settings** (`owb/markup.py`, `web/markup.js`) are shared; a new setting
  needs a reader control first. A language-only setting is declared in
  `data/languages.json` (`settings`) and allowed for that language only by
  `owb/validate.py`.
- **Headings, summaries, articles**: added per book or per article as the
  language is drafted (`data/headings/`, `data/summaries/`,
  `articles/<code>/`, stamped with `scripts/check_translations.py`).

## 8. Check

    python3 scripts/check_catalogs.py
    OWB_VENDOR=<sources dir> python3 -m unittest discover -s tests -t .
    python3 scripts/build_site.py && python3 scripts/check_budgets.py
    DATABASE_URL=postgres://... DJANGO_DEBUG=1 python backend/manage.py test backend_tests

`scripts/check.sh` runs all but the backend tests. A new language adds a
folder of pages to the site; if a size budget fails because of it, raise the
limit in `scripts/check_budgets.py` and say why in the pull request.

## 9. A note on the code `id`

Indonesian's ISO 639-1 code is `id` (the older `in` is deprecated, and the
site's `<html lang>` and hreflang need `id`). It is also the name of the
`id` field of records, decisions and plans. A language map such as a
record's `renderings` or a heading's languages is never confused with a
record, but check two places when adding it:

- `scripts/merge_json.py` merges a list item by item when every item is an
  object with a unique `"id"`; a list of language maps
  (`[{"en": ..., "id": ...}]`) would be merged as if keyed by the
  Indonesian text. No file has such a list today.
- Any code that spreads a language map into an object that also has an
  `id` field (`{"id": record_id, **texts}`) would overwrite one with the
  other. Search the backend serializers and `web/*.js` for objects built
  that way before the first Indonesian rendering is imported.

## 10. After setup

Draft book by book with the `drafting-worker` skill or by hand, following
the brief; run `check-book-before-translating` first. Records stay
`ai_draft` until a named reviewer approves them.
