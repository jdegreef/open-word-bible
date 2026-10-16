# Jeremiah and Lamentations: the drafting brief

The brief each chapter drafter worked from, kept for reviewers. Paths to
session-only tools are left as they were; the binding rules are in
docs/english-style.md and the terms docs.

# Brief: draft one Old Testament chapter in English for Open Word Bible

Repo: the repository (do NOT run any git commands; do not edit any
file other than your chapter file and files in your own scratch folder).
Pinned sources are in vendor. Always export
`OWB_VENDOR=vendor` before running repo scripts.
Tools: tools
(call this TOOLS below). Your scratch folder: TOOLS/../work/<BOOK>.<CH>/ (create it).

## Read first (required)

1. `CLAUDE.md`
2. `docs/english-style.md` (the whole style guide;
   it is binding)
3. `docs/numbers-ruth-terms.md` (settled wording
   for these books; binding)
4. Two finished chapters as models of format, density and tone: one legal
   chapter (`content/LEV/LEV.27.json`) and one narrative chapter
   (`content/EXO/EXO.14.json` or `content/GEN/GEN.24.json`). Skim several
   records closely, including their decisions.
5. If your chapter is not the book's first, glance at the previous chapter
   file in `content/<BOOK>/` if it exists, for continuity (it may not exist
   yet: chapters are drafted in parallel).

## Steps

1. Skeleton (one record per Hebrew verse, already split correctly):
   `python3 scripts/build_skeleton.py BOOK.CH.1 BOOK.CH.LAST -o content/BOOK/BOOK.CH.json`
   (find LAST from the token viewer; create `content/BOOK/` if needed). Never
   change ids, refs, source tokens or source text in the skeleton.
2. Read the Hebrew word data: `python3 TOOLS/show_tokens.py BOOK.CH` (or
   `BOOK.CH FIRST LAST`). It gives each morpheme's token id, transliteration,
   lemma, morphology and MACULA gloss. Translate from this data.
3. Draft in parts of about 8–12 verses. For each part write a JSON file in
   your scratch folder keyed by record id:
   `{"NUM.3.1.s1": {"literal_gloss": "...", "L": "...", "B": "...", "R": "...", "decisions": [...]}}`
   and merge it with `python3 TOOLS/fill.py content/BOOK/BOOK.CH.json part1.json`.
   Write the JSON with a Python script or the Write tool; keep it valid
   (escape double quotes inside strings as `\"`).
4. Validate after every part and at the end, until it prints no errors:
   `python3 -m owb.validate content/BOOK/BOOK.CH.json`
5. If the chapter contains poetry (see the terms doc), set its lines with
   `\q` as the style guide's section 10 describes; `python3 scripts/poetry_lines.py BOOK CH`
   shows the Hebrew cola beside your renderings. Re-validate.
6. Final self-check: run the validator; re-read every record once for
   (a) the three levels meaning the same thing, (b) no contractions, no
   archaic English, (c) every pronoun for God in a deity_pronoun span
   (except "I" and sentence-initial "He"), (d) every YHWH as a divine_name
   span, (e) gender spans only where people of both sexes are meant,
   (f) units spans at Balanced and Readable only, (g) no Hebrew script typed
   anywhere (use Latin transliteration in notes, e.g. *cherem*, *go'el*),
   (h) wording not copied from any copyrighted translation (NIV, ESV, NRSV,
   NLT, CSB, NASB, NKJV, NET...): draft from the Hebrew, then if a sentence
   matches a familiar version beyond a short common phrase, rewrite it.

## Record content

- `literal_gloss`: word for word in Hebrew order, verb first, no object
  marker, [brackets] for supplied "to be" and articles; `\v N ` marks where a
  later verse starts inside a multi-verse record (the skeleton already put
  the markers; keep them at the right place in gloss and every rendering).
- `L`, `B`, `R` per the style guide section 4. Quotation marks: use straight
  double quotes `"` for speech, single `'` for speech inside speech, as the
  models do. A speech that runs across several records opens a quote in the
  first and closes it in the last, and records in between carry no quote
  marks unless a new paragraph of speech starts (follow the models: a
  continuing speech record that starts a new verse often reopens with `"`
  only when the previous record closed it).
- `decisions`: per style guide section 7. Typical density two to four
  meaning decisions (ids m1, m2, ...) and one or two English rendering
  decisions (r-en-1, ...) per record; fewer for simple or repetitive verses
  (a repeated census line or offering list may have one decision or a short
  one that refers back to the first occurrence: "As in verse 13."). Every
  decision object has exactly these keys:
  `id, layer ("meaning"|"rendering"), language (null for meaning, "en" for
  rendering), levels (rendering only: list of "L","B","R"), category, tokens
  (list of token ids from this record), choice, alternatives (list of
  strings), reason, uncertain (bool), footnote (bool)`.
  Meaning categories: text_variant, punctuation, word_sense, grammar,
  allusion, idiom, culture, theology. Rendering categories: word_choice,
  word_order, register, supplied_words, setting_alternative. Meaning
  decisions never mention English, any language name, or a setting span; they
  state the sense only.
- Reasons are plain language a lay reader can follow; cite Scripture by
  Hebrew verse numbers; no claims about named scholars or "most
  translations".
- `status` stays "ai_draft". Never mark anything reviewed.
- Do not add `alignments`.

## Done

Report back in under 150 words: the file path, number of records, that the
validator passes, any poetry marked, and any choices you were unsure about
(especially where you departed from the terms doc). Do not paste the chapter.

## Consistency notes from chapters already drafted (follow these too)

- Numbers *tsava'* (an army unit in the camp lists): Literal "armies", Balanced
  "divisions", Readable "troops"; *degel*: "standard" (Readable "flag").
  Census "every one going out to war": Balanced/Readable may add "men" with a
  rendering decision.
- The 'elef ("thousand") size question has its uncertain, footnoted note at
  Numbers 1; later chapters refer back to it briefly, do not repeat it.
- Name spellings follow the data's English form (e.g. "Ochran", "Reuel" in 2:14).
- Korah's band (*'edah* of Korah, chapters 16-17, 26-27): "company" at Literal and Balanced, "followers" at Readable.

## Poetry helper

`scripts/poetry_lines.py` needs the chapter's word extract. If
`data/hbo/BOOK.CH.json` is missing, run `python3 scripts/extract_tokens.py`
(it only writes data/hbo/ extracts; if it fails reading another chapter that
is mid-write, wait a minute and retry). That is the only shared script you may
run besides the validator and poetry_lines.py.

## Deuteronomy: speeches and quotation marks

Deuteronomy is mostly Moses speaking. A speech that runs across chapters opens
its double quote once, in the record where it starts, and closes it once, in
the record where it ends; records in between carry no outer quote marks (as
Leviticus 1:2-3:17 does). Inside Moses' speech, words of God or of others he
quotes take single quotes, and quotes inside those take double quotes again.
Speech spans (Hebrew numbering):
- 1:1-5 narrator; Moses' first speech 1:6 to 4:40 (opens 1:6, closes 4:40);
  4:41-49 narrator.
- 5:1 narrator then Moses: "Hear, Israel..." opens in 5:1 and runs to 26:19
  (closes 26:19). 10:6-9 is a narrator's aside inside the speech: leave the
  outer quote open, and say so in a decision.
- 27:1 Moses and the elders: opens 27:1, closes 27:8. 27:9-10 Moses and the
  priests: open and close within. 27:11 narrator; Moses' words open 27:12 and
  run through 28:68 (closes 28:68). 28:69 narrator.
- 29:1 narrator then Moses: opens 29:1, closes 30:20.
- Chapters 31-34: shorter speeches inside narrative; open and close each where
  it starts and ends. The Song (32:1-43) is introduced at 31:30 and is one
  quotation opening at 32:1 and closing at 32:43. The Blessing (33:2-29)
  opens at 33:2 and closes at 33:29.
- *'eved* meaning a king's court official or envoy: "servants" at Literal, "officials" or "servants" at Balanced and Readable, with a rendering decision (as Isaiah does). *Sar*: "princes" (L), "officials" (B), "leaders" (R).

## Overlap self-check (do this before reporting)

Run `python3 scripts/ngram_overlap.py --min 12 --levels B,R content/BOOK/BOOK.CH.json`.
It lists runs of 12+ words your Balanced/Readable share with public-domain
Bibles (BSB, WEB, ASV, KJV). These are not copyright problems, but long shared
runs suggest wording borrowed rather than drafted from the Hebrew. Rewrite any
run of 12+ words outside fixed formulas, names lists and short legal formulas,
keeping the meaning; then re-validate.
- *'Edot*: testimonies (L), decrees (B), instructions (R).
- *Chesed* in Deuteronomy follows Exodus 34: Literal "steadfast love", Balanced and Readable "faithful love".
- *Sar* in a military setting (commanders of thousands, of the army): "commanders" at every level.
- *Ger*: "sojourner" (L), "outsider" (B), "stranger" or "outsider" (R), as Leviticus; "foreigner" is kept for *nokhri*.
- Joshua "Be strong and bold": Literal "be strong and bold", Balanced "be strong and courageous", Readable "be strong and brave".
- Judges "sold them into the hand of": Literal "sold them into [the] hand of", Balanced "sold them into the power of", Readable "handed them over to".
- Teraphim: Literal "household gods", Balanced "household gods", Readable "small household idols" (as Genesis 31:19).

## Samuel, Kings and Chronicles

For these books also read `docs/samuel-chronicles-terms.md` (binding; it adds
titles of God, court terms, the regnal formulas, poetry and parallels). Good
narrative models now in the repo: `content/JDG/JDG.6.json`,
`content/JOS/JOS.7.json`. Where your chapter parallels a translated passage
(Psalm 18, Isaiah 36-39, the Psalms in 1 Chronicles 16, or, for Chronicles,
Samuel and Kings once they exist in content/), reuse that wording wherever
the Hebrew is the same and add an allusion decision naming each difference.
Speech quote marks open and close where each speech starts and ends.
Hebrew numbering: check `data/versification.json` for your chapter and put a
footnoted decision at the first verse of any shift (model: content/NUM/NUM.17.json 17:1).
Do not run git, build_site.py or the unit tests; the coordinator does.
- 'Am meaning an army in the field: Literal "the people", Balanced "the troops", Readable "the army" or "the soldiers".
- Polite self-reference "your servant" (*'eved*): "your servant" at every level, with a decision, as Genesis 18:3 and 1 Samuel 20 do; Readable may say "me".

## Chronicles

- Genealogies (1 Chronicles 1-9): keep the list formulas identical ("The sons of X: A, B and C." Literal "[The] sons of X: A and B and C"; "X fathered Y" Literal "X begot Y", Balanced "X was the father of Y", Readable "X was the father of Y" or "X had a son Y"). Names keep the data's English forms. Decisions short: one per record is enough unless a name differs from Genesis, Numbers, Samuel or Kings (then an allusion decision naming the difference). Where the list repeats Genesis (1 Chronicles 1 = Genesis 5, 10, 11, 25, 36), reuse content/GEN wording.
- Where Chronicles retells Samuel or Kings (content/1SA, 2SA, 1KI, 2KI exist), reuse their wording wherever the Hebrew is the same and add an allusion decision naming each difference.
- "All Israel", "the Levites", "the priests the sons of Aaron", gatekeepers (sho'arim "gatekeepers"), singers: consistent.

## Jeremiah and Lamentations (this round)

The repo for this round is the repository (a separate checkout). Work
there: `cd the repository` before every command, and write your chapter
file under content/. Export
`OWB_VENDOR=vendor`. Do not touch /home/user/open-word-bible.

Read `docs/jeremiah-lamentations-terms.md` (binding) and `docs/isaiah-terms.md`
(binding; its table and speech rule hold for these books). Where they differ
from `docs/numbers-ruth-terms.md` or `docs/samuel-chronicles-terms.md`, the
Jeremiah/Isaiah docs win. In particular *hesed* is "loyal love" at Literal and
Balanced and "faithful love" at Readable, as Isaiah. Good models in the repo:
`content/ISA/ISA.1.json` (poetic oracle), `content/ISA/ISA.37.json` (prose
narrative with oracle), `content/PSA/PSA.137.json` (lament poetry in lines).

English phrases in your chapter notes describe content only. Never copy them
as wording; draft from the Hebrew.
