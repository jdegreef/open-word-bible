# Open Word Bible — conventions for Claude

A CC0 Bible translation from Hebrew and Greek with the reasoning behind every
sentence. The translation charter (decisions, levels, settings, review rules)
lives in the founder's "Open Word Bible — Translation Charter" doc; README.md
summarises the data model.

## Where work goes

- Everything is pushed to https://github.com/jdegreef/open-word-bible.
  `main` is what Render deploys to openwordbible.org.

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
  named human reviewer approves them, and readers always see the status.
- Don't use or redistribute MACULA's `ln` / `domain` fields (UBS MARBLE,
  used with permission, not openly licensed).

## Before pushing

    OWB_VENDOR=<sources dir> python3 -m unittest discover -s tests -t .
    OWB_VENDOR=<sources dir> python3 -m owb.validate content/*/*.json
    python3 scripts/extract_tokens.py --check   # after adding verses
    python3 scripts/build_site.py               # the site must still build

`scripts/fetch_sources.py` clones the pinned sources into `vendor/`.
