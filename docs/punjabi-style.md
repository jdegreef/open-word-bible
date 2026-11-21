# Punjabi style guide

How Open Word Bible drafts Punjabi (ਪੰਜਾਬੀ, code `pa`). It builds on
`docs/english-style.md`, which still covers everything that is not about
wording: sources, one record per sentence, the three levels, decisions and
status. It also builds on each book's terms notes (`docs/john-terms.md` and
the others), whose book-wide choices hold in Punjabi unless this file says
otherwise. `docs/punjabi-terms.md` is the glossary of recurring terms and
names, Genesis to Revelation. Where this file and the founder's Translation
Charter disagree, the Charter wins; fix this file.

**Status: drafting brief, awaiting native Punjabi reviewers.** Every choice
below is **the rule drafters follow**, book by book, without re-deciding it.
A drafter who thinks a rule is wrong for a passage follows it anyway and
says so in a rendering decision marked uncertain. Section 15 lists the
choices that decide the most verses, for the founder and a native reviewer
to confirm or change once; a change is made here and then carried through
every book drafted under the old rule.

**Script.** `pa` is Punjabi in **Gurmukhi** (ਗੁਰਮੁਖੀ), the script of
Indian Punjab and of the Punjabi Bibles printed in India. Punjabi in
Shahmukhi (the Perso-Arabic script of Pakistani Punjab, where most Punjabi
Christians live) would be a separate reading language, `pnb`, right to left
like Arabic; it is not drafted yet (section 15).

## Settled

- **How close the drafts may come to the Punjabi Bibles** (the rule the
  founder set for Arabic, 2026-11-20, applied to Punjabi). Literal rewrites
  any run of **10 or more words** shared with the Punjabi Bible of 1945 or
  the Indian Revised Version, and any run in a well-known verse; shorter
  runs are allowed where the Hebrew or Greek word order leaves no other
  natural wording. Balanced and Readable have **no run of 7 or more**.
  Section 14, step 4, has the command that measures it.

## 1. Sources and independence

- Translate from the Hebrew (and the Greek), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Punjabi says that meaning in its own
  way.
- **The Punjabi Bibles.** Two are read in Indian Punjabi churches, and both
  are close kin:
  - the *Punjabi Bible* (*ਪਵਿੱਤਰ ਬਾਈਬਲ*) of 1945 (Bible Society of India),
    in the public domain. Its spelling is older (ਪੁੱਤ੍ਰ, ਨਿਹਚਾ for faith,
    ਯਹੋਵਾਹ for the divine name), and its wording is what older readers
    remember;
  - the *Indian Revised Version* (IRV, 2019, Bridge Connectivity Solutions),
    a revision of the 1945 Bible in modern spelling, licensed CC BY-SA 4.0.
    ShareAlike is not compatible with Open Word Bible's CC0, so its wording
    must not be copied at all.
  Under copyright as well: the *Easy-to-Read Version* in Punjabi (ERV-PA)
  and the newer Bible Society of India editions. Open Word Bible does not
  copy public-domain Bibles either: reference Bibles in any language are for
  comparison and review only, never the basis for its wording.
- Draft from the Hebrew or Greek and the gloss, then **compare with the 1945
  Bible and the IRV and rewrite what is too close** (Settled, above). A
  short common phrase that any Punjabi Christian would use (ਪਰਮੇਸ਼ੁਰ ਦਾ ਰਾਜ,
  ਮਨੁੱਖ ਦਾ ਪੁੱਤਰ, ਸਬਤ ਦਾ ਦਿਨ, ਪਵਿੱਤਰ ਆਤਮਾ) is a term, not copied wording.
- The conventional forms of names, the names of the books and the church's
  shared vocabulary (sections 6 and 7) are not wording and may be used.
- **Hindi is a neighbour, not a source.** Open Word Bible's Hindi shares
  many choices with this brief (the divine name, the honorifics, the key
  terms), and reading it shows how a sentence was handled. A Punjabi
  sentence is not a transliteration of the Hindi one: Punjabi has its own
  words (ਨੂੰ, ਤੋਂ, ਵਿੱਚ, ਦਾ; ਕਿਹਾ, ਗਿਆ, ਆਇਆ) and its own order of
  auxiliaries.
- Never type Greek or Hebrew. A Greek or Hebrew word quoted in a decision is
  copied from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"pa": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, and the
  `\q ` line breaks of poetry (section 12), in every Punjabi level. Punjabi
  is verb-final, as Hindi is, so a clause often wants to move across a verse
  boundary. Keep each verse's own content after its marker, restructuring
  the sentence if needed (two Punjabi sentences for one Hebrew or Greek one
  is fine). Where that is impossible, say so in a `word_order` decision.
- The meaning decisions are shared: do not change them. Punjabi needs only
  its own rendering decisions, with ids `r-pa-1`, `r-pa-2`, ... counted from
  1 in each record, `"layer": "rendering"`, `"language": "pa"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions; the Punjabi words under discussion are
  quoted in it ("\"ਵਿਸ਼ਵਾਸ\" rather than \"ਨਿਹਚਾ\""). The site tells Punjabi
  readers that notes are in English for now.
- Write a Punjabi rendering decision where Punjabi had to choose and a
  reader might ask why: a word chosen against the familiar 1945 word, a form
  of address, a structure Punjabi cannot copy, a setting span that differs
  from the English one, a word chosen to avoid a Sikh or Hindu theological
  sense (section 9), or a term settled here for the whole book (once, where
  it first appears in a passage). Do not repeat the English rendering
  decisions. Typical density: zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language, so each Punjabi level opens and closes the same
  quotations, in the same order, as the English one: no quotation added,
  dropped, merged or split.

## 3. The three levels in Punjabi

The level names on the site are **ਸ਼ਾਬਦਿਕ** (Literal), **ਸੰਤੁਲਿਤ**
(Balanced) and **ਸਰਲ** (Readable).

The language is **standard written Punjabi** of Indian Punjab, the register
of newspapers, schoolbooks and a careful public reading, based on the Majhi
of Amritsar and Lahore. No dialect forms (Doabi, Malwai, Pothohari) at any
level, and no Hindi or Urdu grammar where Punjabi has its own.

**Literal (OWB-L).** Keeps the Hebrew's or Greek's words, their grammar
(participles, genitives, the sequence of clauses where Punjabi allows) and
its repetitions. Punjabi is verb-final with postpositions, so the original
word order cannot be followed; Literal keeps the original's units and the
sequence of its clauses instead. Words Punjabi needs but the original lacks
go in [square brackets]. Postpositions (ਨੇ, ਨੂੰ, ਤੋਂ, ਵਿੱਚ, ਨਾਲ, ਦਾ/ਦੇ/ਦੀ/ਦੀਆਂ)
and verb endings are grammar, not added words, and are not bracketed. Keep
the historic present (ਕਹਿੰਦਾ ਹੈ, ਆਉਂਦਾ ਹੈ) where the Greek has it, and the
Hebrew narrative chain as ਅਤੇ / ਤਾਂ + past (section 12).

**Balanced (OWB-B).** Careful standard modern Punjabi; tracks the original
closely; no brackets. Use the established Punjabi church words where they
are the living word for the thing (ਬਪਤਿਸਮਾ, ਖ਼ੁਸ਼ਖ਼ਬਰੀ, ਕਿਰਪਾ, ਕਲੀਸਿਯਾ).
Avoid heavily Sanskritised or Persianised words where a common Punjabi word
says the same: Balanced sounds like an educated speaker, not a commentary.

**Readable (OWB-R).** Plain everyday Punjabi for new and young readers:
short sentences and common words. Where both are current, prefer the
everyday word to the learned one (ਸੱਚ beside ਸਚਾਈ, ਰਾਹ beside ਮਾਰਗ). Explains
idioms and may make explicit what the context implies, as the English
Readable does, with a decision where the English has one.

## 4. God, the Lord and the divine name

### God: *ਪਰਮੇਸ਼ੁਰ*

*theos* and *Elohim* are **ਪਰਮੇਸ਼ੁਰ** at every level, with no setting:
the word of every Punjabi Bible and of Indian Punjabi churches. "Our God"
is ਸਾਡਾ ਪਰਮੇਸ਼ੁਰ; a false god or the gods of the nations are ਦੇਵਤਾ,
ਦੇਵਤੇ, a goddess ਦੇਵੀ, an idol ਮੂਰਤੀ (L, B) or ਬੁੱਤ (R).

Not used for the God of Israel: *ਰੱਬ* (the everyday Punjabi word, shared
with Muslim and Sikh speech; section 15 asks whether Readable should use
it), *ਖ਼ੁਦਾ* (the word of Pakistani Punjabi Christians, which belongs to a
Shahmukhi edition), *ਵਾਹਿਗੁਰੂ* and *ਅਕਾਲ ਪੁਰਖ* (Sikh names of God), and
*ਈਸ਼ਵਰ* / *ਭਗਵਾਨ* (Hindu).

### Lord: *ਪ੍ਰਭੂ*

*kyrios* of God or of Jesus, and *Adonai*, are **ਪ੍ਰਭੂ**; "Lord!" in
address is ਹੇ ਪ੍ਰਭੂ. A human master is ਮਾਲਕ (ਸੁਆਮੀ at L where the master
stands for God in a parable). "Sir" to a stranger or a superior is ਸੁਆਮੀ at
L and ਜੀ after the address the scene needs at B and R (ਮਾਲਕ ਜੀ, ਸਰਦਾਰ ਜੀ is
not used); ਪ੍ਰਭੂ stays for God and Jesus.

### The divine name: *ਪ੍ਰਭੂ* by default, *ਯਾਹਵੇ* as the setting

YHWH is `{{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}}` at every level, as the Hindi is.
*ਪ੍ਰਭੂ* stands where the English has "the LORD"; the alternative gives the
name as most scholars think it was said. Both options take the same
postpositions, so these stay outside the span:
`{{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}} ਨੇ ਕਿਹਾ`, `{{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}} ਦਾ ਬਚਨ`.
In address: `ਹੇ {{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}}`.

*ਯਹੋਵਾਹ*, the form of both Punjabi Bibles, is not used: it is a
seventeenth-century European hybrid, and the default reading follows the
Jewish and New Testament practice of saying "Lord" (as the Septuagint's
*kyrios*, which the New Testament quotes). Section 15 asks the founder to
confirm this, since ਯਹੋਵਾਹ is what Punjabi readers know.

- *YHWH Elohim*: `{{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}} ਪਰਮੇਸ਼ੁਰ`.
- *Adonai YHWH* ("the Lord GOD"): `ਪ੍ਰਭੂ {{divine_name:ਪਰਮੇਸ਼ੁਰ|ਯਾਹਵੇ}}`.
- *YHWH tsevaot*: `ਸੈਨਾਂ ਦਾ {{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}}`, every level.
- *Yah*: `{{divine_name:ਪ੍ਰਭੂ|ਯਾਹ}}`.
- Because *ਪ੍ਰਭੂ* is both YHWH and *Adonai*, the first record of each book
  says in a setting_alternative decision how the setting tells them apart.
- God takes honorific plural agreement in both options
  (`{{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}} ਨੇ ਕਿਹਾ`, ਉਹ ਆਏ, ਉਨ੍ਹਾਂ ਨੇ), section 5.

### Pronouns for God: no `deity_pronoun` spans

Gurmukhi has no capital letters, so the setting has nothing to change, and
the Punjabi text has **no** `deity_pronoun` spans. Respect for God and Jesus
comes from the honorific plural (section 5) at every level. The first record
of a passage file where the English has a span says so once, or
`scripts/settings_parity.py` lists it as by design (it does: section 8).

## 5. Address and honorifics

Punjabi has two words for *you*: **ਤੂੰ** (one person, intimate or plain;
ਤੈਨੂੰ, ਤੇਰਾ, ਤੈਥੋਂ) and **ਤੁਸੀਂ** (many people, or one person with respect;
ਤੁਹਾਨੂੰ, ਤੁਹਾਡਾ, ਤੁਹਾਥੋਂ). Formal ਆਪ is a written register and is not
used in speech in the drafts. Third persons are plain singular (ਉਹ ਆਇਆ, ਉਸ
ਨੇ, ਉਸ ਦਾ) or honorific plural (ਉਹ ਆਏ, ਉਨ੍ਹਾਂ ਨੇ, ਉਨ੍ਹਾਂ ਦਾ). The choices
below hold through the Bible, so a scene does not change relationship
between verses.

- **God and Jesus in the narrative** take the honorific plural at every
  level: "ਯਿਸੂ ਗਲੀਲ ਵਿੱਚ ਆਏ", "ਉਨ੍ਹਾਂ ਨੇ ਉਨ੍ਹਾਂ ਨੂੰ ਕਿਹਾ". This is ordinary
  modern Punjabi for a respected person, not an addition to the text. Name
  the subject ("ਯਿਸੂ ਨੇ") where the honorific plural would leave it unclear
  among other plurals.
- **People speaking to God**, and Jesus praying to the Father, say **ਤੂੰ**
  (ਤੇਰਾ, ਤੈਨੂੰ). This is the intimate address of Punjabi devotion, the way
  people pray. It is not disrespect.
- **People speaking to Jesus** say **ਤੁਸੀਂ**, disciples, petitioners and
  opponents alike: the address anyone in the scene would give a teacher.
- **Jesus speaking** says **ਤੂੰ** to one person and **ਤੁਸੀਂ** to many, so the
  Greek's singular and plural *you* stay apart. (Punjabi ਤੂੰ to one person
  is far less sharp than Hindi तू, and is what a teacher says to a pupil.)
- **God speaking** says ਤੂੰ to one person and ਤੁਸੀਂ to many, as Jesus does.
- **Ordinary people** use the address the scene calls for: ਤੂੰ between
  equals, within the family and to inferiors; ਤੁਸੀਂ to parents-in-law, to
  elders, to rulers (Pharaoh, Herod, Pilate) and from slaves to their
  master. Ruth and Naomi: Naomi says ਤੂੰ to her daughters-in-law, they say
  ਤੁਸੀਂ to her; Boaz says ਤੂੰ to Ruth, she says ਤੁਸੀਂ to him.
- **Kings**: ਮਹਾਰਾਜ in address (ਹੇ ਮਹਾਰਾਜ) at B and R, ਹੇ ਰਾਜਾ at L;
  "your servant" as self-reference (ਤੁਹਾਡਾ ਦਾਸ, ਤੁਹਾਡੀ ਦਾਸੀ) at L and B, ਮੈਂ
  at R where the English Readable says "I".
- **Third person of others.** Opponents, the crowd and the soldiers speak
  of Jesus in the plain singular (ਇਹ ਬੰਦਾ, ਉਹ); prophets, John the Baptist
  and kings are plain in the narrative. When Jesus speaks of himself in the
  third person (ਮਨੁੱਖ ਦਾ ਪੁੱਤਰ), the title takes plain singular forms
  (ਆਵੇਗਾ, ਉਸ ਦਾ).
- **"Woman" in address**: ਹੇ ਇਸਤਰੀ (L), ਬੀਬੀ (B, R); ਮਾਂ to Jesus' mother
  at R.

### Brothers and sisters

*adelphoi* meaning believers is `{{gender:ਭਰਾਵੋ ਅਤੇ ਭੈਣੋ|ਭਰਾਵੋ}}` in the
vocative, `{{gender:ਭਰਾਵਾਂ ਅਤੇ ਭੈਣਾਂ|ਭਰਾਵਾਂ}}` in the oblique, and
`{{gender:ਭਰਾ ਜਾਂ ਭੈਣ|ਭਰਾ}}` in the singular (section 8).

### Verbs of speaking

ਕਹਿਣਾ for *legō* / *amar* (ਕਿਹਾ, ਆਖਿਆ for variety at B and R); "answered
and said" ਉੱਤਰ ਦਿੱਤਾ ਅਤੇ ਕਿਹਾ (L), ਉੱਤਰ ਦਿੱਤਾ (B), ਕਿਹਾ (R).

## 6. Names

### Principles

- Use the **established Punjabi Bible form** of a name where both Punjabi
  Bibles agree on it (ਯਿਸੂ, ਮੂਸਾ, ਦਾਊਦ, ਯੂਹੰਨਾ, ਪਤਰਸ, ਯਰੂਸ਼ਲਮ). Names are not
  wording, and readers know them.
- Where the two Bibles differ, take the IRV's modern spelling; where an
  older form misleads, follow the Hebrew or Greek and note it in the
  glossary.
- Spell names in modern Gurmukhi (section 10): ਅੰਦਰਿਯਾਸ, not ਅੰਦ੍ਰਿਯਾਸ,
  but keep the nukta where the Punjabi Bibles write it (ਯੂਸੁਫ਼, ਬੋਅਜ਼,
  ਫ਼ਿਰਊਨ).
- A name not in the glossary is formed from the Hebrew or Greek on the
  pattern of the established names, and added to the glossary in the same
  pull request.

### The common forms

People: ਯਿਸੂ, ਮਰਿਯਮ, ਯੂਸੁਫ਼, ਯੂਹੰਨਾ, ਯੂਹੰਨਾ ਬਪਤਿਸਮਾ ਦੇਣ ਵਾਲਾ, ਸ਼ਮਊਨ
ਪਤਰਸ, ਅੰਦਰਿਯਾਸ, ਯਾਕੂਬ, ਜ਼ਬਦੀ, ਫ਼ਿਲਿਪੁੱਸ, ਥੋਮਾ, ਮੱਤੀ, ਯਹੂਦਾ ਇਸਕਰਿਯੋਤੀ,
ਹੇਰੋਦੇਸ, ਪਿਲਾਤੁਸ, ਕਯਾਫ਼ਾ, ਲਾਜ਼ਰ, ਮਾਰਥਾ, ਪੌਲੁਸ, ਆਦਮ, ਹੱਵਾਹ, ਨੂਹ, ਅਬਰਾਹਾਮ,
ਇਸਹਾਕ, ਯਾਕੂਬ, ਮੂਸਾ, ਹਾਰੂਨ, ਦਾਊਦ, ਸੁਲੇਮਾਨ, ਏਲੀਯਾਹ, ਅਲੀਸ਼ਾ, ਕੈਸਰ.
Places: ਯਰੂਸ਼ਲਮ, ਗਲੀਲ, ਯਹੂਦਿਯਾ, ਸਾਮਰਿਯਾ, ਨਾਸਰਤ, ਬੈਤਲਹਮ, ਕਫ਼ਰਨਾਹੂਮ, ਯਰਦਨ,
ਮਿਸਰ, ਮੋਆਬ, ਰੋਮ. Peoples: ਇਸਰਾਏਲੀ, ਯਹੂਦੀ, ਸਾਮਰੀ, ਯੂਨਾਨੀ, ਰੋਮੀ.
`docs/punjabi-terms.md` has the rest, book by book.

## 7. Words for the whole Bible

| Source (English) | Punjabi | Notes |
|---|---|---|
| God | ਪਰਮੇਸ਼ੁਰ | Section 4. |
| Lord | ਪ੍ਰਭੂ | Section 4. |
| Jesus; Christ | ਯਿਸੂ; ਮਸੀਹ | ਯਿਸੂ ਮਸੀਹ, ਮਸੀਹ ਯਿਸੂ. No christos spans (section 8). |
| Holy Spirit; the Spirit | ਪਵਿੱਤਰ ਆਤਮਾ; ਆਤਮਾ | Masculine agreement where the Spirit acts (ਪਵਿੱਤਰ ਆਤਮਾ ਉੱਤਰਿਆ), as the Hindi. |
| Word (*logos*, John 1) | ਸ਼ਬਦ | Section 9 and 15: ਸ਼ਬਦ is also the Sikh word for a hymn of the Guru Granth. Alternative ਵਚਨ / ਬਚਨ. |
| word of God, word of the LORD | ਬਚਨ | ਪਰਮੇਸ਼ੁਰ ਦਾ ਬਚਨ. |
| kingdom of God; kingdom of heaven | ਪਰਮੇਸ਼ੁਰ ਦਾ ਰਾਜ; ਸਵਰਗ ਦਾ ਰਾਜ | |
| Son of Man | ਮਨੁੱਖ ਦਾ ਪੁੱਤਰ | A title; never under the gender setting. |
| disciple(s) | ਚੇਲਾ; ਚੇਲੇ | Every level. |
| apostle | ਰਸੂਲ | |
| prophet | ਨਬੀ | Every level; ਪੈਗੰਬਰ is not used. |
| the Law | ਬਿਵਸਥਾ | ਮੂਸਾ ਦੀ ਬਿਵਸਥਾ at R where Moses' Law is meant. |
| scribes | ਗ੍ਰੰਥੀ is **not** used (a Sikh office); ਸ਼ਾਸਤਰੀ (L), ਬਿਵਸਥਾ ਦੇ ਸਿੱਖਿਅਕ (B, R) | |
| Pharisees; Sadducees | ਫ਼ਰੀਸੀ; ਸਦੂਕੀ | |
| priest; high priest; chief priests | ਜਾਜਕ; ਮਹਾਂ ਜਾਜਕ; ਮੁੱਖ ਜਾਜਕ | ਪੁਜਾਰੀ for the priests of other gods. |
| elders | ਬਜ਼ੁਰਗ (L, B), ਬਜ਼ੁਰਗ ਆਗੂ (R) | Church elders: ਬਜ਼ੁਰਗ (L, B), ਕਲੀਸਿਯਾ ਦੇ ਆਗੂ (R). |
| tax collectors; sinners | ਮਸੂਲੀਏ (L, B), ਟੈਕਸ ਲੈਣ ਵਾਲੇ (R); ਪਾਪੀ | |
| Gentiles, nations | ਪਰਾਈਆਂ ਕੌਮਾਂ (L, B), ਗ਼ੈਰ-ਯਹੂਦੀ (R); ਕੌਮਾਂ | ਜਾਤ / ਜਾਤੀ is not used: it means caste. |
| synagogue; temple | ਪ੍ਰਾਰਥਨਾ ਘਰ (*synagōgē*, B, R; ਸਭਾ-ਘਰ at L); ਹੈਕਲ | ਮੰਦਰ only for a pagan temple. ਗੁਰਦੁਆਰਾ is never used. |
| Sabbath; Passover | ਸਬਤ; ਪਸਾਹ | |
| church, assembly | ਕਲੀਸਿਯਾ | |
| repent; repentance | ਤੋਬਾ ਕਰਨਾ; ਤੋਬਾ | ਮਨ ਫਿਰਾਉਣਾ at L where the Greek's "change of mind" matters, with a decision. |
| sin | ਪਾਪ | |
| believe; faith | ਵਿਸ਼ਵਾਸ ਕਰਨਾ; ਵਿਸ਼ਵਾਸ | The 1945 Bible's ਨਿਹਚਾ is not used. |
| grace | ਕਿਰਪਾ | Key term, every level. Mercy is ਦਯਾ; compassion ਤਰਸ. |
| truth | ਸਚਾਈ (L, B); ਸੱਚ (R) | Key term. |
| glory; glorify | ਮਹਿਮਾ; ਮਹਿਮਾ ਕਰਨਾ | Key term. |
| peace | ਸ਼ਾਂਤੀ | Key term; *shalom* as a greeting ਸ਼ਾਂਤੀ ਹੋਵੇ. |
| righteousness; righteous | ਧਾਰਮਿਕਤਾ; ਧਰਮੀ | Justify: ਧਰਮੀ ਠਹਿਰਾਉਣਾ. ਧਰਮ alone means religion and is not used for righteousness. |
| holy; saints | ਪਵਿੱਤਰ; ਸੰਤ is **not** used: ਪਵਿੱਤਰ ਲੋਕ | ਸੰਤ is a Sikh and Hindu holy man. |
| gospel, good news | ਖ਼ੁਸ਼ਖ਼ਬਰੀ | Every level. |
| baptize | ਬਪਤਿਸਮਾ ਦੇਣਾ | |
| covenant | ਨੇਮ | |
| love (*agapē*, *ahavah*) | ਪਿਆਰ; ਪ੍ਰੇਮ (L, B) where the English "love" is a key term | One per book, noted once. |
| steadfast love (*hesed*) | ਅਟੱਲ ਪਿਆਰ | Kept apart from mercy (ਦਯਾ). |
| salvation; save | ਮੁਕਤੀ; ਬਚਾਉਣਾ | ਮੁਕਤੀ also means Sikh and Hindu liberation; it is the word of both Punjabi Bibles and stays. |
| redeem; redeemer (*goʾel*) | ਛੁਡਾਉਣਾ; ਛੁਡਾਉਣ ਵਾਲਾ | In Ruth, the kinsman-redeemer is ਛੁਡਾਉਣ ਵਾਲਾ ਰਿਸ਼ਤੇਦਾਰ (B, R), ਛੁਡਾਉਣ ਵਾਲਾ (L). |
| eternal life | ਸਦੀਪਕ ਜੀਵਨ (L, B); ਸਦਾ ਦਾ ਜੀਵਨ (R) | |
| world (*kosmos*) | ਸੰਸਾਰ | |
| angel; demon; devil, Satan | ਦੂਤ (ਸਵਰਗ ਦੂਤ where a messenger could be human); ਭੂਤ; ਸ਼ੈਤਾਨ | |
| heaven; Hades; Gehenna | ਸਵਰਗ; ਪਤਾਲ (L, B), ਮੁਰਦਿਆਂ ਦਾ ਥਾਂ (R); ਨਰਕ | *Sheol* as Hades. |
| cross; crucify | ਸਲੀਬ; ਸਲੀਬ ਉੱਤੇ ਚੜ੍ਹਾਉਣਾ | |
| altar; sacrifice; offering | ਜਗਵੇਦੀ; ਬਲੀਦਾਨ; ਭੇਟ | |
| Truly I tell you (*amēn*) | ਮੈਂ ਤੁਹਾਨੂੰ ਸੱਚ ਆਖਦਾ ਹਾਂ (ਤੈਨੂੰ to one person) | Every level. |
| Amen; Hosanna; Hallelujah | ਆਮੀਨ; ਹੋਸੰਨਾ; ਹਲਲੂਯਾਹ | |
| Rabbi; Teacher | ਰੱਬੀ; ਗੁਰੂ | Section 9 and 15 on ਗੁਰੂ. Alternative ਉਸਤਾਦ. |
| slave (*doulos*, *ʿeved*) | ਦਾਸ | ਸੇਵਕ for *diakonos* and where service alone is the point. |
| pray; prayer | ਪ੍ਰਾਰਥਨਾ ਕਰਨਾ; ਪ੍ਰਾਰਥਨਾ | ਅਰਦਾਸ is not used: it is the Sikh congregational prayer. |
| worship | ਅਰਾਧਨਾ ਕਰਨਾ | Bow down: ਮੱਥਾ ਟੇਕਣਾ (L ਝੁਕ ਕੇ ਪ੍ਰਣਾਮ ਕਰਨਾ) |
| verse | ਆਇਤ | Interface word. |

## 8. Reader settings in Punjabi

Settings change wording, never meaning, exactly as in English.

- `divine_name`: `{{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}}`, postpositions outside the
  span (section 4).
- `deity_pronoun`: **none**. Gurmukhi has no capitals (section 4).
  `scripts/settings_parity.py` lists (pa, deity_pronoun) as by design.
- `christos`: **none**. *ਮਸੀਹ* is both the name in ਯਿਸੂ ਮਸੀਹ and the word
  Messiah itself, so the choice the English setting offers is already made;
  the only other candidate, *ਖ੍ਰਿਸਤ*, is a transliteration few readers use.
  Write *ਮਸੀਹ* plainly wherever the English has a christos span, as the Hindi
  and Arabic do. `scripts/settings_parity.py` lists (pa, christos) as by
  design.
- `gender`: an inclusive default where the original means men and women,
  with the traditional form as the alternative, only where Punjabi really
  has two wordings: `{{gender:ਭਰਾਵੋ ਅਤੇ ਭੈਣੋ|ਭਰਾਵੋ}}` and its oblique and
  singular forms (section 5); `{{gender:ਲੋਕ|ਮਨੁੱਖ}}` where *anēr* means people
  in general; `{{gender:ਸੰਤਾਨ|ਪੁੱਤਰ}}` for "sons" meaning children of God or
  of Israel where the English has a span. Punjabi ਲੋਕ, ਮਨੁੱਖ (a human),
  ਕੋਈ, ਸਭ, ਬੱਚੇ are already inclusive and get no span, so the Punjabi has
  fewer gender spans than the English; `scripts/settings_parity.py` lists
  (pa, gender) as documented here. Never for God, Christ or named men. A
  setting_alternative decision records a difference from the English the
  first time in a passage.
- `units`: metric by default, the original unit as the alternative, as in
  every language but English: `{{units:ਲਗਭਗ 3 ਕਿਲੋਮੀਟਰ|ਪੰਦਰਾਂ ਸਟੇਡੀਆ}}`.
  Literal keeps the original unit with no span. Coins: the value in wages by
  default and the coin as the alternative (`{{units:ਇੱਕ ਦਿਨ ਦੀ ਮਜ਼ਦੂਰੀ|ਇੱਕ
  ਦੀਨਾਰ}}`). This differs from the English (US units) and needs a rendering
  decision the first time in a passage. The conversions are the English
  ones (`docs/punjabi-terms.md` section 6).
- `plural_you` is Spanish only; `god_term` is Chinese only.
- A setting span holds no quotation marks (`owb/markup.py` checks).

## 9. Sikh, Hindu and Muslim vocabulary

Most Punjabi speakers in India are Sikh, and Punjabi's religious vocabulary
is mostly Sikh. Many words are simply Punjabi and are used by everyone
(ਪਾਪ, ਪਵਿੱਤਰ, ਕਿਰਪਾ, ਸੇਵਾ, ਦਇਆ), and the Punjabi Bibles have used them for
two centuries. Others name Sikh institutions or Sikh theology and would make
the Bible say something it does not.

- **Not used**: ਵਾਹਿਗੁਰੂ, ਅਕਾਲ ਪੁਰਖ, ਸਤਿਗੁਰੂ, ਸਤਿਨਾਮ (names of God);
  ਗੁਰਬਾਣੀ, ਬਾਣੀ (scripture); ਗ੍ਰੰਥ for the Bible's books (ਪੋਥੀ instead, as in
  ਪਰਕਾਸ਼ ਦੀ ਪੋਥੀ); ਗੁਰਦੁਆਰਾ, ਸੰਗਤ (for the church or the assembly, though the IRV uses it; ਕਲੀਸਿਯਾ, ਸਭਾ), ਗ੍ਰੰਥੀ, ਅਰਦਾਸ,
  ਅੰਮ੍ਰਿਤ (for baptism), ਖ਼ਾਲਸਾ, ਸੰਤ; Hindu ਭਗਵਾਨ, ਈਸ਼ਵਰ, ਅਵਤਾਰ, ਕਰਮ (for
  works; ਕੰਮ), ਮੋਕਸ਼.
- **Flagged for the founder** (section 15): ਗੁਰੂ for "Teacher" (the
  ordinary Punjabi word for a teacher, used by the IRV, but also the title
  of the ten Sikh Gurus); ਸ਼ਬਦ for the Logos (John 1:1, used by the IRV; the
  Sikh word for the Guru's hymns, and the Gurus taught that the Shabad is
  the Guru). The drafts use both, as the IRV does, with a decision in the
  first passage of each book.
- **Persian and Arabic loanwords** that are ordinary Punjabi stay (ਕਿਤਾਬ,
  ਹੁਕਮ, ਤੋਬਾ, ਨਬੀ, ਰਸੂਲ, ਕੌਮ, ਜ਼ਮੀਨ). Words that are specifically Islamic in
  Punjabi (ਖ਼ੁਦਾ, ਅੱਲ੍ਹਾ, ਪੈਗੰਬਰ, ਜੰਨਤ, ਦੋਜ਼ਖ਼, ਨਮਾਜ਼) are not used in the
  Gurmukhi edition.

## 10. Spelling, punctuation and typography

- **Script.** Gurmukhi only, with no Latin letters and no Greek or Hebrew.
  The content checks treat Gurmukhi as its own script
  (`owb/content_checks.py`).
- **Modern standard spelling**, as the Punjabi University and Punjab School
  Education Board write it, not the 1945 Bible's older forms:
  - full ਰ, not subscript (pairin) ੍ਰ, after a vowel-bearing syllable:
    ਪੁੱਤਰ, ਮਿੱਤਰ, ਸ਼ਾਸਤਰ, ਪਵਿੱਤਰ (not ਪੁੱਤ੍ਰ, ਪਵਿੱਤ੍ਰ); pairin ਰ stays in
    the clusters standard Punjabi keeps (ਪ੍ਰਭੂ, ਪ੍ਰੇਮ, ਪ੍ਰਾਰਥਨਾ, ਪ੍ਰਕਾਸ਼,
    ਕ੍ਰੋਧ);
  - pairin ਹ (੍ਹ) in ਉਨ੍ਹਾਂ, ਤੁਹਾਨੂੰ is written as standard Punjabi writes
    it (ਉਨ੍ਹਾਂ, ਜਿਨ੍ਹਾਂ, ਕਿਨ੍ਹਾਂ);
  - the addak ੱ for a doubled consonant where it is pronounced (ਪੁੱਤਰ, ਚੱਲ,
    ਸੱਚ);
  - tippi ੰ and bindi ਂ by the standard rule: tippi with ਿ ੁ ੂ and the
    inherent vowel (ਅੰਤ, ਕੁੰਜੀ), bindi with the other vowel signs (ਮੈਂ, ਹਾਂ,
    ਹੈਂ, ਜਾਂਦਾ);
  - the nukta where standard Punjabi dictionaries write it (ਸ਼, ਖ਼, ਗ਼, ਜ਼,
    ਫ਼; ਲ਼ only in words that need it): ਖ਼ੁਸ਼ਖ਼ਬਰੀ, ਜ਼ਮੀਨ, ਫ਼ਰੀਸੀ, ਬਜ਼ੁਰਗ;
  - ਦੇਸ਼ (country), ਸ਼ਹਿਰ, ਸ਼ਾਂਤੀ with ਸ਼.
  The overlap check folds these differences away, so spelling a word in the
  modern way does not make a copied run original.
- **Punctuation.** The full stop is the danda **।** (U+0964); the double
  danda ॥ is not used. The comma, `?`, `!`, `:` and `;` are as in English.
  Quotation marks are typed straight in the records, `"` outside and `'`
  for a quotation inside a quotation, as in the English and Hindi records;
  the site shows them curly. A sentence still ends with its own mark inside
  the closing quotation mark ("...ਮੇਰੇ ਪਿੱਛੇ ਚੱਲੋ।").
- **Numbers.** International (Arabic) digits (12, 5000), not Gurmukhi
  digits (੧੨), in the text and in verse numbers; section 15 asks whether
  readers want Gurmukhi digits as a display option. Indian digit grouping
  for large numbers (6,03,550), as the Hindi. Spell out short numbers in
  running text (ਦੋ ਆਦਮੀ).
- **Clock time.** Literal keeps the original count ("ਛੇਵੇਂ ਘੰਟੇ"); Balanced
  and Readable give the time as a modern reader counts it ("ਦੁਪਹਿਰ ਦੇ ਬਾਰਾਂ
  ਵਜੇ"), with a decision.

## 11. Grammar at each level

- **Postpositions** are written as separate words (ਉਸ ਦਾ, ਉਸ ਨੂੰ, ਘਰ ਵਿੱਚ),
  except the fused pronoun forms standard Punjabi writes as one word
  (ਮੈਨੂੰ, ਤੈਨੂੰ, ਸਾਨੂੰ, ਤੁਹਾਨੂੰ, ਉਹਨੂੰ only in speech at R; ਮੇਰਾ, ਤੇਰਾ,
  ਸਾਡਾ, ਤੁਹਾਡਾ).
- **The ergative ਨੇ** with a transitive perfect (ਉਸ ਨੇ ਕਿਹਾ, ਬੋਅਜ਼ ਨੇ ਆਖਿਆ),
  at every level; the verb then agrees with the object.
- **Auxiliaries**: ਹੈ, ਹਨ, ਹਾਂ, ਹੋ; past ਸੀ, ਸਨ. Readable keeps them; it does
  not drop the auxiliary as casual speech does.
- **Commands**: ਤੂੰ ... ਕਰ, ਤੁਸੀਂ ... ਕਰੋ; polite requests ਕਰਨਾ / ਕਰਿਓ at R
  where the English Readable softens; laws (Exodus to Deuteronomy) ਤੂੰ ...
  ਨਾ ਕਰੀਂ (L, B), ਤੈਨੂੰ ... ਨਹੀਂ ਕਰਨਾ ਚਾਹੀਦਾ (R).
- **Participles** at Literal: ਕਰਦਿਆਂ, ਕਰ ਕੇ, ਕਰਨ ਵਾਲਾ, kept where the Greek
  has them; Balanced and Readable may make them clauses.

## 12. Poetry, headings and the Old Testament

- **Lines.** Poetry is set in lines, as `docs/english-style.md` section 10
  describes: mark each break inside a verse with `\q `, following the Hebrew
  accents' division (`python3 scripts/poetry_lines.py` prints it), at every
  level. Do not rhyme.
- **Psalm titles** are verse 1, as in the Hebrew: ਦਾਊਦ ਦਾ ਭਜਨ (L, B), ਦਾਊਦ
  ਦਾ ਲਿਖਿਆ ਭਜਨ (R). *Selah* is ਸਲਹ.
- **The psalmist** speaks to God as ਤੂੰ and ਹੇ {{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}}.
- **Old Testament narrative**: the *wayyiqtol* chain is ਅਤੇ / ਤਦ + past
  at Literal (ਅਤੇ ਉਸ ਨੇ ਕਿਹਾ ... ਅਤੇ ਉਹ ਗਿਆ); Balanced and Readable use the
  conjunctive participle (ਜਾ ਕੇ, ਉੱਠ ਕੇ) and new sentences where the chain
  would be monotonous.
- **Section headings and summaries.** Where a book's
  `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json` has the
  languages beside English, add `"pa"` beside them as each book is drafted,
  written from Open Word Bible's own Punjabi wording. They are AI drafts
  until reviewed, and never the headings of the 1945 Bible or the IRV.

## 12a. Recurring formulas

One form each, at every book; the first record of a passage that uses one
notes it once.

| Source (English) | Literal | Balanced | Readable |
|---|---|---|---|
| Thus says the LORD | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਇਹ ਆਖਦਾ ਹੈ* | as L | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਦਾ ਇਹ ਕਹਿਣਾ ਹੈ* |
| declares the LORD | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਦਾ ਵਾਕ ਹੈ* | as L | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਆਖਦਾ ਹੈ* |
| The word of the LORD came to ... | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਦਾ ਬਚਨ ... ਕੋਲ ਆਇਆ* | as L | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਨੇ ... ਨਾਲ ਗੱਲ ਕੀਤੀ* |
| I am the LORD | *ਮੈਂ {{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਹਾਂ* | as L | as L |
| behold (*hinneh*, *idou*) | *ਵੇਖੋ* (ਵੇਖ to one person) | left out where it only marks attention | left out |
| and it came to pass (*wayehi*) | *ਅਤੇ ਅਜਿਹਾ ਹੋਇਆ* | left out, or a time clause | as B |
| son of man (Ezekiel's address) | *ਹੇ ਆਦਮੀ ਦੇ ਪੁੱਤਰ* | as L | *ਹੇ ਮਨੁੱਖ* |
| lifted up his eyes and saw | *ਆਪਣੀਆਂ ਅੱਖਾਂ ਚੁੱਕ ਕੇ ਵੇਖਿਆ* | *ਨਜ਼ਰ ਚੁੱਕ ਕੇ ਵੇਖਿਆ* | *ਵੇਖਿਆ* |
| to this day | *ਅੱਜ ਦੇ ਦਿਨ ਤੱਕ* | as L | *ਅੱਜ ਤੱਕ* |
| Fear not | *ਨਾ ਡਰ* (*ਨਾ ਡਰੋ*) | as L | as L |
| Woe to you | *ਤੁਹਾਡੇ ਉੱਤੇ ਹਾਇ* | as L | *ਹਾਇ ਤੁਹਾਡੇ ਲਈ* |
| grace and peace to you | *ਤੁਹਾਨੂੰ ਕਿਰਪਾ ਅਤੇ ਸ਼ਾਂਤੀ* | *ਤੁਹਾਨੂੰ ਕਿਰਪਾ ਅਤੇ ਸ਼ਾਂਤੀ ਮਿਲੇ* | as B |
| As the LORD lives | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਦੇ ਜੀਵਨ ਦੀ ਸਹੁੰ* | as L | *ਮੈਂ ਜਿਉਂਦੇ {{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਦੀ ਸਹੁੰ ਖਾਂਦਾ ਹਾਂ* |
| May the LORD do so to me and more | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਮੇਰੇ ਨਾਲ ਇਸੇ ਤਰ੍ਹਾਂ ਕਰਨ, ਅਤੇ ਇਸ ਤੋਂ ਵੀ ਵੱਧ ਕਰਨ* | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਮੈਨੂੰ ਕਰੜੀ ਤੋਂ ਕਰੜੀ ਸਜ਼ਾ ਦੇਣ* | *{{divine_name:ਪ੍ਰਭੂ\|ਯਾਹਵੇ}} ਮੈਨੂੰ ਕਰੜੀ ਸਜ਼ਾ ਦੇਣ* (honorific plural, as everywhere God is the subject) |

## 13. Search

Punjabi is written with spaces, so site search indexes it word by word
(`owb_simple`: Postgres has no Punjabi stemmer). A term written two ways
(ਖੁਸ਼ਖਬਰੀ / ਖ਼ੁਸ਼ਖ਼ਬਰੀ) is two words to search, so keep the glossary's
spelling throughout. Folding the nukta and the addak for search, as the
overlap check does, is a later improvement.

## 14. Drafting book by book

Each book is drafted the same way, so the books agree with each other
without a later harmonising pass.

1. **Check the book is free** (`check-book-before-translating` skill) and
   that the English is drafted: Punjabi is drafted from records that already
   have their meaning decisions.
2. **Read this file, the book's section of `docs/punjabi-terms.md`, and the
   book's English terms notes.** The glossary's form is the form.
3. **Draft each record at L, then B, then R**, from the Hebrew or Greek,
   the gloss and the meaning decisions. Keep the English record's verse
   markers, line breaks and quotations (section 2).
4. **Compare with the 1945 Bible and the IRV** and rewrite what is too
   close (Settled, above). Measure with
   `python3 scripts/ngram_overlap.py --language pa --usfm
   pb1945=<bible-punjabi-pavitr-bible-1945>/usfm --usfm
   irv=<punjabi_bible>/usfm --min 7 content/BOOK/*.json`, from clones of
   github.com/tfbf/bible-punjabi-pavitr-bible-1945 (public domain) and
   github.com/FreeBiblesIndia/punjabi_bible (CC BY-SA 4.0), neither
   vendored: no Balanced or Readable run of 7 or more, no Literal run of 10
   or more, and none in a well-known verse. The tool folds spelling
   differences (nukta, addak, halant, tippi and bindi) before comparing.
5. **Write the decisions** (section 2): the first use in the book of a
   glossary choice, a name not in the glossary, every setting span that
   differs from the English.
6. **Add new names** to the book's section of `docs/punjabi-terms.md` in
   the same pull request, by the rules of section 6.
7. **Before the pull request, search the book's Punjabi** for what this file
   excludes, at every level: ਯਹੋਵਾਹ, ਨਿਹਚਾ, ਖ਼ੁਦਾ, ਰੱਬ (outside a decision),
   ਵਾਹਿਗੁਰੂ, ਸਤਿਗੁਰ, ਅਰਦਾਸ, ਗੁਰਦੁਆਰਾ, ਸੰਗਤ, ਭਗਵਾਨ, ਪੁੱਤ੍ਰ and the other
   pairin-ਰ forms of section 10, ॥, Gurmukhi digits, a Latin full stop at
   the end of a sentence, and a `deity_pronoun` or `christos` span.
8. **Headings and summaries** for the book in Punjabi, from our own text
   (section 12).
9. One pull request per book; `scripts/check.sh` must pass.

## 15. Defaults for the founder to confirm

Each of these decides the wording of thousands of verses. Drafting follows
them as written; the founder confirms or changes each once, and the outcome
is recorded under "Settled" at the top of this file. Changing one later
means revising every book drafted under it, so the earlier they are
confirmed the cheaper.

1. **Script**: Gurmukhi for `pa`. Shahmukhi (`pnb`, Pakistani Punjabi, the
   larger Christian community) would be a separate language later, with
   ਖ਼ੁਦਾ-type vocabulary in Perso-Arabic script and right-to-left display.
2. **YHWH**: `{{divine_name:ਪ੍ਰਭੂ|ਯਾਹਵੇ}}` by default. The alternative is
   ਯਹੋਵਾਹ (both Punjabi Bibles) as the default, with ਪ੍ਰਭੂ or ਯਾਹਵੇ as the
   setting.
3. **God is ਪਰਮੇਸ਼ੁਰ** at every level. The alternative is ਰੱਬ at Readable,
   the everyday Punjabi word.
4. **Honorific plural** for God and Jesus in the narrative; ਤੂੰ to God;
   ਤੁਸੀਂ to Jesus; Jesus and God say ਤੂੰ to one person and ਤੁਸੀਂ to many
   (section 5).
5. **No `deity_pronoun` and no `christos` spans** (section 8).
6. **ਗੁਰੂ for "Teacher" and ਸ਼ਬਦ for the Logos**, as the IRV, despite their
   Sikh senses (section 9). Alternatives: ਉਸਤਾਦ and ਬਚਨ.
7. **Faith is ਵਿਸ਼ਵਾਸ**, not the 1945 Bible's ਨਿਹਚਾ; repentance is ਤੋਬਾ.
8. **Modern standard spelling** (ਪੁੱਤਰ, not ਪੁੱਤ੍ਰ; section 10).
9. **Brothers**: `{{gender:ਭਰਾਵੋ ਅਤੇ ਭੈਣੋ|ਭਰਾਵੋ}}`, inclusive by default.
10. **Digits**: international digits in the text and verse numbers. The
    alternative is Gurmukhi digits (੦–੯) as a display option, which would
    be a build and reader step, never a change to records.
11. **Level names**: ਸ਼ਾਬਦਿਕ, ਸੰਤੁਲਿਤ, ਸਰਲ.

## 16. Status

A Punjabi rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.
