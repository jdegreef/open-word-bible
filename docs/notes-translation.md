# Translating notes and cards

`content/` keeps every decision's choice, alternatives and reason in English,
and `data/glossary.json`, `data/names.json` and `data/key_terms.json` state
their senses in English. The reader shows them to every language. This page
is the workflow for translating them, so that a Spanish reader reads Spanish
footnotes. One agent (or person) per language can follow it without further
guidance.

Translations live beside the English, one file per language:

| What | File | Keyed by |
|---|---|---|
| Decision notes | `data/notes/<lang>/<BOOK>.json` | record id, then decision id |
| Glossary cards | `data/cards/<lang>/glossary.json` | `<Strong's>|<lemma>` |
| Name cards | `data/cards/<lang>/names.json` | `<Strong's>|<lemma>` |
| Key terms | `data/cards/<lang>/key_terms.json` | `<language>|<Strong's>` (`grc|5485`) |

Every entry carries `source`, a digest of the English it was translated from
(`owb/notes.py`). When the English changes, the digest no longer matches: the
entry is **stale**, the site shows the English again, and the next export
lists it for translation. Never edit `source` by hand; `import` writes it.

Files are per language (and per book for notes), like `data/headings/`, so
pull requests for different languages or books never touch the same file,
and `scripts/merge_json.py` (the `data/**/*.json` rule in `.gitattributes`)
merges the rest.

## The workflow

All commands run from the repository root, with the pinned sources fetched
(`scripts/fetch_sources.py`) and `OWB_VENDOR` pointing at them.

### 1. Export a worklist

    python3 scripts/notes.py export es --books JHN --footnotes-only -o work-es-JHN.jsonl

- `--books` takes one or more book codes (`JHN ROM`); without it, every book.
- `--chapters 1-3` (with one book) keeps the records that start in those
  chapters, to split a long book into batches.
- `--footnotes-only` keeps the decisions the reader footnotes. **Do these
  first**: there are 6,211 footnoted meaning decisions, and they are what
  readers see under the text. Without the flag, every meaning decision is
  exported (they show in the reasoning panel).
- `--rendering` also exports the language's own rendering decisions
  (`r-es-1`, ...), whose reasons are written in English too.

Each line of the worklist is one decision that has no current translation:

    {"kind": "note", "lang": "es", "book": "JHN", "record": "JHN.1.1.s1",
     "decision": "m3", "refs": ["JHN.1.1"], "category": "grammar",
     "uncertain": false, "footnote": true, "status": "new",
     "source": "aa869c03fcf6",
     "english": {"choice": "with God", "alternatives": ["toward God", "face to face with God"],
                 "reason": "⟦1⟧ with the accusative normally means \"toward\"; ..."},
     "original": {"1": "<the Greek word>"},
     "rendering": {"L": "...", "B": "...", "R": "..."},
     "rendering_en": "In the beginning was the Word, ...",
     "translation": {"choice": "", "alternatives": ["", ""], "reason": ""}}

`rendering` is the record in your language at the three levels (null if the
sentence is not translated into it yet), `rendering_en` the English Balanced,
for context. `status` is `new`, or `stale` with the old translation under
`previous`: bring it up to date rather than starting again.

For the cards:

    python3 scripts/notes.py export-cards es -o cards-es.jsonl
    python3 scripts/notes.py export-cards es --kinds glossary key_terms -o cards-es.jsonl

A glossary or name line has `english.senses` (each with `name`, `kind` and
`note`) and `translation.senses`, one `{name, note}` per English sense, in
the same order. A key-term line has `english.sense` and `english.note`, and
`english_words`, the settled English words (for reference only).

### 2. Translate

Fill in `translation` on each line and leave everything else as it is. You
may translate a few lines at a time and import as you go; lines left empty
are skipped.

**Greek and Hebrew: keep the slots.** The export replaces every Greek or
Hebrew word in the English with a numbered slot, `⟦1⟧`, `⟦2⟧`, ..., and lists
the words under `original`. Put the same slot where the word belongs in your
sentence (`⟦1⟧ con acusativo suele significar «hacia»`); `import` copies the
word back from the English. Never type or paste Greek or Hebrew yourself:
CLAUDE.md forbids it, and import refuses any word that is not in the source
data. Transliterations in Latin letters in the English (*hesed*,
*unigenitus*) are not slots: keep them, or write them in your script as your
style guide does.

### 3. Import

    python3 scripts/notes.py import es work-es-JHN.jsonl --dry-run   # check only
    python3 scripts/notes.py import es work-es-JHN.jsonl

Import checks every filled line and writes the good ones into
`data/notes/es/<BOOK>.json` (or `data/cards/es/<kind>.json`), in the book's
record order, with the English digest as `source`. It refuses a line, and
says why, when:

- the English changed after the line was exported (export again);
- the number of alternatives (or senses) differs from the English;
- a text is empty, holds a reader setting (`{{...}}`), a slot with no word in
  the English, a drafting placeholder (`@He@`), or Greek or Hebrew that is not
  in the source data;
- the decision is another language's rendering decision.

Fix the lines it names and import the file again; lines already imported are
simply written again.

### 4. Report and check

    python3 scripts/notes.py report            # every language
    python3 scripts/notes.py report --lang es
    python3 scripts/notes.py check             # validate every note and card file

The report gives, per language, footnoted meaning decisions translated (of
6,211), all meaning decisions, the language's own rendering notes, stale and
orphaned entries (their decision or card is gone), and each card file.
`check` is what CI runs (`tests/test_notes.py`, and
`python3 -m owb.validate data/notes/es/JHN.json` checks one file). Stale and
orphaned entries are not errors: they are reported, and the site ignores
them.

Then run `scripts/check.sh --fast` and commit. One commit per book (or per
batch of chapters) keeps review easy.

## Quality rules

1. **Translate the sense, nothing more.** A meaning decision states what the
   original says; its translation says the same thing in your language. Do
   not add, drop or soften a reason, change which reading is chosen, or turn
   an uncertain call into a certain one. A note never names a target
   language ("in Spanish ...") and never holds a reader setting.
2. **Use your language's own words for the text.** The `choice` names the
   sense as the translation renders it: take the wording from `rendering`
   (the record in your language) and from your style guide
   (`docs/<language>-style.md` and the book's terms doc, such as
   `docs/john-terms.md`). If the English choice is "the Word", the Spanish
   choice is "el Verbo", because that is the Spanish rendering; the key terms
   (grace, glory, sign, Son of Man, ...) keep their settled word in your
   language. Alternatives are senses set aside, translated plainly ("the
   Message" → "el Mensaje"), and keep the English count and order.
3. **Keep it short and plain.** A note is read in a small pop-up. Write the
   register of your Balanced level: clear sentences, no academic jargon your
   readers would not know. You may make a long English sentence two, but do
   not summarise away a step of the argument.
4. **References in your language.** Write book names exactly as
   `data/books.json` gives them for your language ("Génesis 1:1",
   "1 Juan 4:9"), with a space before the chapter, so the reader can link
   them. Psalms use the chapter name ("Salmo 69:10"). References inside John
   stay bare numbers ("3:16", "verse 17" → "versículo 17"). Names of people
   and places follow your style guide (Nicodemo, Ni-cô-đem, ニコデモ).
5. **Name the levels as your catalog does** (`i18n/<lang>.json`, `levels`):
   "Literal" in Spanish is "la versión Literal", "Readable" is
   "la versión Sencilla".
6. **Keep facts as they are.** Manuscript names (P66, Codex Sinaiticus),
   editions (SBLGNT, the King James Version) and dates are facts, not
   wording: translate the names conventionally, but do not swap the King
   James for your language's traditional Bible even where it reads the same.
7. **Quotation marks and punctuation** follow your style guide («...» in
   Spanish, French, Russian, Ukrainian and Amharic; 「...」 in Japanese).
   Straight double quotes are curled by the build.
8. **Nothing is reviewed by Claude.** Every file stays `"status": "ai_draft"`
   until a named human reviewer approves it.

For cards, the same rules hold: translate each sense's name the way your
language names the person, place or thing (from the records and your style
guide), and its note faithfully and plainly. A key term's `sense` is the
term's name in your language (gracia, Neema, 恵み); its `note` describes how
the English renders the term, so keep the English words it quotes in English.

## How the site uses them

`scripts/build_site.py` loads a language's current notes for each chapter
(`book_notes`, `page_notes`) and puts them in the page's data; `web/reader.js`
replaces the English choice, alternatives and reason with them in footnotes,
the reasoning panel, the "Why?" pop-up and handouts. A note without a current
translation shows in English, marked `lang="en"`, and the panel's "notes are
in English for now" line only appears while some note on screen is still
English. Cards work the same way (`card_translation`): the reader's word
cards and the key-term pages show the translated sense and note where they
are current. Everything else (the verse of the day, search, the Data page)
still uses the English for now.

`data/article_links.json` maps lemmas (Strong's number and lemma, copied
from `data/grc` and `data/hbo`) and decision categories to articles; a note
whose words include a mapped lemma shows "Read the article: <title> →",
linking to the article in the reader's language when it is translated.
