# English style guide

How Open Word Bible drafts English. It applies to every English rendering and
every English rendering decision, and it is the brief for drafting new
passages. It was compiled from the project overview (`docs/overview.html`),
the rules in `CLAUDE.md`, and the conventions the first passages (John 1:1–18,
Philippians 4:1–9) actually follow. Where it and the founder's Translation
Charter disagree, the Charter wins; fix this file.

Rules the software enforces are marked **(checked)**.

## 1. Sources and independence

- Translate from the original language only: the SBL Greek New Testament for
  the New Testament, the Westminster Leningrad Codex for the Old. English Bibles
  may be consulted as a check, never as the source.
- **Never reproduce the wording of a copyrighted translation** (NIV, ESV, NLT,
  NRSV, CSB, NASB and others). Familiar verses pull drafts toward familiar
  wording: early drafts of Philippians 4:6–8 came out almost word for word like
  existing versions and had to be rewritten. Draft from the Greek and the
  gloss, then compare; if a sentence matches a well-known version for more than
  a short common phrase, rewrite it.
- The public-domain reference Bibles in the database (BSB, WEB, ASV, KJV, YLT)
  are for comparison and review, not a basis for our wording.
- Never type Greek or Hebrew. **(checked)** The source text comes from the data;
  a Greek word quoted in a note must be a form or lemma copied from MACULA.

## 2. One record per sentence

- A record is one source sentence. It ends where the SBLGNT ends a sentence: a
  full stop, a question mark, or a raised dot (·) where the next clause stands
  on its own. **(checked)** Start new passages with
  `scripts/build_skeleton.py`, which already splits by sentence.
- A long Greek sentence (Paul writes many) stays one record, however many
  English sentences it becomes. Philippians 1:3–7 or 3:8–11 may be a single
  record; the English levels may break it into several sentences.
- Mark each later verse inside a record with `\v N ` at the point where it
  starts, in the gloss and in every rendering. **(checked)**
- A decision of category `punctuation` explains a record that reads the
  punctuation differently from the SBLGNT (as John 1:3 does).

## 3. The literal gloss

Word for word, in Greek order where English can follow, without smoothing:
"In beginning was the word, and the word was toward the God". It shows the
shape of the sentence and is not meant to read well. Keep the article where
the Greek has it ("the God") and leave it out where the Greek does. Use
[brackets] sparingly, only for a word the gloss cannot parse without ("in the
[one] strengthening me").

## 4. The three levels

Every English record has all three levels. **(checked)** The levels may differ
in how much they say, but never in what they mean. A level may keep an
ambiguity the original has; no level may choose a different reading from the
others.

**Literal (OWB-L).** Lets the reader see the original's form.
- Follow the Greek wording and order where English allows.
- Put every word English needs but the Greek lacks in [square brackets]:
  "In [the] beginning", "if [there is] any virtue". Nothing else uses brackets.
- Keep Greek structures English can bear: participles, long sentences joined
  with "and", the order of clauses.
- Keep key terms and repeated words as repeated words.

**Balanced (OWB-B).** Accurate and natural; the default level.
- Reads like careful modern English, the register of a good public reading.
- Tracks the Greek closely: one Greek clause usually becomes one English
  clause, and nothing is added that is not implied.
- Breaks Paul's longest sentences into two or three English sentences when
  that is the only way to keep them readable.
- No brackets.

**Readable (OWB-R).** Plain language for new and young readers.
- About a 6th–8th grade reading level: short sentences, common words.
- Explains idioms instead of reproducing them; may make explicit what the
  context implies ("already there", "because you are joined to").
- Every such expansion that adds a reason, a subject or a connection the Greek
  leaves implicit needs a rendering decision, and if it is a stretch, mark it
  `uncertain` for reviewers.
- Still says what the Greek says, no more: no applications, no commentary.

## 5. Words and spelling

- **Key terms** keep the same English word at every level. **(checked)** The
  list is in `data/key_terms.json`: grace, glory, truth, peace,
  righteousness, faith, joy, salvation, and gospel (which Readable renders
  "good news"), with more added as they are settled.
  If a passage needs a different word, record a meaning or rendering decision on
  those words saying why.
- US spelling (honor, Savior, practice as a verb). A future `spelling` setting
  will give UK forms.
- "Lord" for the Greek *kyrios* when it refers to Jesus or to God. "the LORD"
  for the divine name in the Old Testament, with Yahweh as a setting. In a New
  Testament quotation of the Old Testament the Greek has *kyrios*, so write
  "Lord" and note the Hebrew original in a decision (John 1:23).
- "slave" for *doulos* at every level, as Philippians 1:1 and 2:7 have it,
  with a meaning decision on what the person's position was; never the
  softer "servant".
- Modern English: no "thee", "thou", "-eth", "behold", "lo". "Brothers and
  sisters" through the gender setting, not "brethren".
- No contractions at any level, Readable included: "do not", "it is", "will
  not". The text is read aloud and printed; the full forms suit both.
- Numbers in words up to ninety-nine; numerals for larger numbers and in
  measurements.

## 6. Reader settings

Settings change wording, never meaning. **(checked)** Use a setting span
`{{setting:default|alternative}}` wherever one applies:

- `gender`: inclusive default where the original means men and women; the
  traditional form as the alternative. `{{gender:brothers and sisters|brothers}}`,
  `{{gender:all people|men}}`. Never for God, Christ or named men, and never
  where a specific male is meant.
- `gender` only where both options exist: an English word that is already
  inclusive ("everyone", "worshipers", "anyone who believes") needs no span.
  A pronoun for a figure in a parable or picture (the bridegroom, John
  3:29) is not a pronoun for God and takes no deity_pronoun span.
- `christos`: `{{christos:Christ|Messiah}}` (Literal) or
  `{{christos:Christ|the Messiah}}` (Balanced, Readable) for every Christos.
  Where the Greek has the article and Literal keeps it, write
  `the {{christos:Christ|Messiah}}`.
- `deity_pronoun`: every pronoun for God or Christ, lowercase default,
  capitalised alternative: `{{deity_pronoun:him|Him}}`. **(checked: only the
  capitalisation may differ)** This covers every pronoun for God or Christ
  except "I": he/him/his/himself, "me/my/mine" when he speaks of himself, and
  "you/your" when someone speaks to him. Never the Spirit as "it". At the start
  of a sentence the pronoun is capitalised either way, so write plain "He"
  with no span (as John 1:2 does).
- `units`: modern measures by default, the original unit as the alternative:
  `about {{units:20 to 30 gallons|two or three measures}}`. Literal keeps the
  original unit. US units are the modern default; metric belongs to a future
  UK/metric setting, not to `units`.
- `divine_name`, `units`, `spelling`: when they apply (the Old Testament,
  measures and money).

Disagreements about meaning are never settings. They are decisions, with
footnotes.

## 7. Decisions

Each decision names its tokens, a category, the choice, the alternatives that
were considered, and the reason, in plain language a lay reader can follow.

- **Meaning decisions** (`m1`, `m2`, ...) say what the original means. They are
  shared by every language, so they never name a target language or quote a
  setting span, and they use the meaning categories only: text_variant,
  punctuation, word_sense, grammar, allusion, idiom, culture, theology.
  **(checked)**
- **English rendering decisions** (`r-en-1`, ...) say how English puts that
  meaning into words, and list the levels they apply to. They use the wording
  categories: word_choice, word_order, register, supplied_words,
  setting_alternative.
- Write a decision wherever a reader might ask "why does it say that?": a word
  with several senses, a grammatical choice that changes the meaning, an
  allusion, a cultural fact the reader needs, a textual variant, an English
  word chosen against a familiar alternative, words supplied at Balanced or
  Readable.
- Typical density: two to four meaning decisions per sentence, plus one or two
  English rendering decisions. Do not write decisions for the obvious.
- Mark a decision `uncertain` when the evidence is evenly balanced or a
  Readable expansion goes beyond what is certain. Say what the other side is.
- Set `footnote` when a reader of the printed text should see the alternative:
  textual variants, uncertain decisions, and well-known renderings we depart
  from ("only begotten").
- Text variants: the SBLGNT text governs. The SBLGNT apparatus is not yet in
  the pinned sources, so a `text_variant` decision describes the manuscript
  evidence from general knowledge; reviewers must check it against the
  apparatus before the sentence is marked meaning reviewed.
- Cite only what the project can stand behind: other passages of Scripture,
  facts about the text and its manuscripts, and well-established historical
  facts. No unverifiable claims about scholars or "most translations".

## 8. Status

Every new record is `ai_draft`. Nothing is marked reviewed until a named human
reviewer approves it, and an AI never changes a status.
