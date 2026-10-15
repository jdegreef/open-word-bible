# French style guide

How Open Word Bible drafts French. It sits on top of `docs/english-style.md`,
which still governs everything that is not about wording (sources, one record
per sentence, the three levels, decisions, status), and of
`docs/john-terms.md`, whose book-wide choices for John hold in French unless
this file says otherwise. Where this file and the founder's Translation
Charter disagree, the Charter wins; fix this file.

**Status: proposed, awaiting a native French reviewer.** Every French record is
`ai_draft`.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. French says that meaning in its own way.
- **Never reproduce the wording of a copyrighted French Bible** (Segond 21,
  NBS, Colombe, TOB, Bible de Jérusalem, Parole de Vie, Français courant,
  Semeur, NFC). Familiar verses pull drafts toward familiar wording; draft from
  the Greek and the gloss, then rewrite any sentence that matches a well-known
  version for more than a short common phrase. The Louis Segond of 1910 is in
  the public domain but, like the English reference Bibles, it is for
  comparison, not a basis for our wording.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied from
  the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"fr": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after `"es"` (or after `"en"`). Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, in every
  French level. **(checked)**
- The meaning decisions are shared: do not change them. French needs only its
  own rendering decisions, with ids `r-fr-1`, `r-fr-2`, ... counted from 1 in
  each record, `"layer": "rendering"`, `"language": "fr"`, the `levels` they
  apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the Spanish ones; the French words under discussion are quoted in it
  ("\"le Verbe\" rather than \"la Parole\""). The site tells French readers that
  notes are in English for now.
- Write a French rendering decision where French had to choose and a reader
  might ask why: a word chosen against a familiar alternative, a tense, a
  structure French cannot copy, a setting span that differs from the English
  one, a term settled here for the whole book (once, where it first appears in
  a passage). Do not repeat the English rendering decisions; where French
  simply follows the English choice, no decision is needed. Typical density:
  zero to two per sentence.

## 3. The three levels in French

**Literal (OWB-L).** Follows the Greek order and wording where French allows.
Words French needs but the Greek lacks go in [square brackets], as in English
("[il y avait] six jarres"). An article French requires after a preposition
("Au commencement", where the Greek has no article) needs no bracket, because
it is part of the preposition. Keep the historic present ("il dit") where
the Greek has it.

**Balanced (OWB-B).** Careful modern French, the register of a good public
reading. Tracks the Greek closely; no brackets. Narration in the *passé simple*
("il dit", "ils vinrent", "Jésus répondit"), the normal tense of written
narrative, with the *passé composé* in speech ("nous avons trouvé le Messie").

**Readable (OWB-R).** Plain French for new and young readers: short
sentences, common words. Narration in the *passé composé* ("Jésus a répondu"),
which is how French is spoken and read in school today; no *passé simple*.
Explains idioms and may make explicit what the context implies, as the English
Readable does, with a decision where the English has one.

One rendering decision in the first record of each passage that has
narration records the tense choice by level.

## 4. Spelling and typography

- Standard French of France and of the francophone world, in the 1990
  reformed spelling only where it is now usual; no regionalisms.
- Apostrophe: the typographic ’ (U+2019), never '.
- Quotation marks: « » outside, “ ” for a quotation inside a quotation.
  A no-break space (U+00A0) goes inside « and before », and before a colon.
  A narrow no-break space (U+202F) goes before ; ! and ?. Never an ordinary
  space before these marks, so a line never begins with one.
- Capitals: Dieu, le Père, le Fils, l’Esprit, le Seigneur, le Fils de l’homme,
  l’Agneau de Dieu, la Loi (the Law of Moses), les Écritures. Accents on
  capitals (É, À).
- Numbers in words up to *cent* in running text; clock times and measures in
  figures ("seize heures", "80 à 120 litres").
- Proper names in their usual French form: Jean, Jésus, Moïse, Élie, Simon
  Pierre, André, Philippe, Nathanaël, Bethsaïda, Béthanie, Cana en Galilée,
  Capharnaüm, Céphas, les Pharisiens, les Lévites.

## 5. Words for the whole of John

| Greek (English) | French | Notes |
|---|---|---|
| the Word | **le Verbe** | Every level. "La Parole" says "speech" more plainly, but it is feminine, so the Word would be "elle" until verse 14, and verse 2 would read "Elle était au commencement". "Le Verbe" is masculine and the traditional French term (from the Latin *Verbum*); its weakness is that "verbe" today is mostly a grammar word. Recorded as an uncertain rendering decision in 1:1 for a native reviewer, as the Spanish *el Verbo* is. |
| grace, truth, glory, peace | la grâce, la vérité, la gloire, la paix | Key terms: the same word at every level. |
| believe / believe in | croire / croire en | Keep the verb at every level, Readable included ("faire confiance" only with a decision). |
| the world | le monde | |
| eternal life | la vie éternelle | |
| sign | un signe | Never "miracle". |
| glorify | glorifier | |
| testify, testimony | rendre témoignage, le témoignage | Readable may say "dire", "affirmer" with a decision where the English Readable also loosens it. |
| remain, stay | demeurer (theological sense); rester, loger (ordinary sense) | 1:38-39: "où demeures-tu ?" is natural French and keeps the link to 15:4; Readable may say "où habites-tu ?". |
| the Jews | les Juifs (L); les chefs juifs, les autorités juives (B, R) where the authorities are meant; les Juifs, juif where the people are meant | As `docs/john-terms.md`. |
| Truly, truly | En vérité, en vérité, je vous le dis (L, B); Je vous le dis, c’est la vérité (R) | One decision per passage. |
| hour | l’heure | Jesus's appointed hour: "mon heure" at L and B; Readable may say "mon moment". Clock time 1:39: L "la dixième heure", B and R the modern time ("vers seize heures"). |
| Son of Man | le Fils de l’homme | A title; never under the gender setting. |
| Lamb of God | l’Agneau de Dieu | |
| Rabbi | Rabbi | |
| Messiah (1:41) | le Messie | Plainly, no setting; the explanation is `{{christos:Christ|Oint}}`. |
| the temple | le temple (naos, every level); le temple at L for hieron, la cour du temple, l’esplanade du temple at B and R | |
| disciples | les disciples | Every level. |
| slave (*doulos*, *ʿeved*) | esclave (L); serviteur, servante (B, R) | As the English: "esclave" at every level where slavery itself is the point (slave and free, bought and sold, slavery in Egypt, slavery to sin). |
| brothers (2:12) | ses frères | Specific men: no setting. |
| Woman (2:4) | Femme (L, B); Mère (R) | As the English: Readable names her as his mother, with a decision. |
| Sir / Lord (*kyrie*) | Monsieur / Seigneur | As `docs/john-terms.md`: "Seigneur" for those who believe. |

## 6. Forms of address

- **Tu** to one person, **vous** to several, as every modern French Bible does:
  people say "tu" to Jesus, Jesus says "tu" to Nathanael and to his mother, and
  "vous" to a group. No setting: "vous" for one person would be a different
  register, not a regional variant.
- God and Jesus are addressed with "tu" too.

## 7. Reader settings in French

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: every pronoun for God or Christ, lowercase default,
  capitalised alternative, only the capitalisation differing. **(checked)**
  The French forms: `{{deity_pronoun:il|Il}}`, `{{deity_pronoun:lui|Lui}}`,
  `{{deity_pronoun:le|Le}}`, `{{deity_pronoun:l’|L’}}` (elided: write the
  next word straight after the span, "{{deity_pronoun:l’|L’}}ont"),
  `{{deity_pronoun:son|Son}}`, `{{deity_pronoun:sa|Sa}}`,
  `{{deity_pronoun:ses|Ses}}`, `{{deity_pronoun:lui-même|Lui-même}}`, and
  when Jesus speaks of himself or is spoken to: `moi|Moi`, `me|Me`, `m’|M’`,
  `mon|Mon`, `ma|Ma`, `mes|Mes`, `toi|Toi`, `te|Te`, `t’|T’`, `tu|Tu`,
  `ton|Ton`, `ta|Ta`, `tes|Tes`. "Je" for Jesus has no span, and a pronoun
  at the start of a sentence is written plainly with its capital ("Il était
  au commencement avec Dieu"). Put a span wherever the English has one for
  the same person; French may need one where English does not (an object
  pronoun "le", "lui") and the reverse. A possessive agrees with the thing
  possessed, so "his glory" is `{{deity_pronoun:sa|Sa}} gloire`.
- `christos`: `{{christos:Christ|Messie}}` where English Literal has
  `{{christos:Christ|Messiah}}`; with the article, `le {{christos:Christ|Messie}}`
  ("Je ne suis pas le {{christos:Christ|Messie}}"). Where the English has
  `Jesus {{christos:Christ|the Messiah}}`, French writes
  `Jésus {{christos:Christ|le Messie}}`, without the usual hyphen of
  "Jésus-Christ", so that both options read naturally.
- `gender`: an inclusive default where the original means men and women,
  with the traditional French as the alternative:
  `{{gender:des humains|des hommes}}`, `{{gender:tout être humain|tout homme}}`,
  `{{gender:tout le monde|tout homme}}`. French "homme" is read as generic
  less and less, so the inclusive default says it plainly. Not for specific
  men, and not where French is already inclusive ("les enfants de Dieu",
  "chacun", "personne").
  The setting goes on a **noun** French has to choose, usually where the
  original has *anthrōpos* or *ʾādām*. Words that must agree with that noun
  go under the same setting ("ce {{gender:qu’elle a fait|qu’il a fait}}",
  John 7:51). Generic **pronouns** take none: "celui qui", "quiconque",
  "quelqu’un", "chacun" and "personne" already mean anyone, and the "il",
  "lui", "le" and "celui-là" that refer back to them are ordinary generic
  French. So where the English needs `{{gender:they|he}}` for a pronoun,
  French writes "celui qui … il" and adds no span. Don't bring in "la
  personne … elle" only to carry the setting. A rendering decision
  (setting_alternative) records the difference from the English the first
  time it occurs in a passage.
- `units`: metric by default in French, the original unit as the alternative:
  `{{units:80 à 120 litres|deux ou trois mesures}}` (a *metrētēs* held about
  39 litres). Literal keeps the original unit. This differs from the English
  (US gallons) and needs a rendering decision.

## 8. Status

Every new record keeps its status; a French rendering added to a record does
not change it. Nothing is marked reviewed by an AI.
