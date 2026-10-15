# Swahili style guide

How Open Word Bible drafts Swahili. It sits on top of `docs/english-style.md`,
which still governs everything that is not about wording (sources, one record
per sentence, the three levels, decisions, status), and of
`docs/john-terms.md`, whose book-wide choices for John hold in Swahili unless
this file says otherwise. Where this file and the founder's Translation
Charter disagree, the Charter wins; fix this file.

**Status: proposed, awaiting a native Swahili reviewer.** Every Swahili record
is `ai_draft`. The level names, the grammar labels in `owb/morph.py` and the
key terms below are first proposals, and a reviewer is expected to change
some of them.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Swahili says that meaning in its own
  way.
- **Never reproduce the wording of a copyrighted Swahili Bible**: the Swahili
  Union Version (Biblia Takatifu, 1952), Biblia Habari Njema, Neno: Biblia
  Takatifu, Kiswahili Contemporary Version, and the Catholic Biblia ya
  Kiswahili. The Union Version shapes how most Swahili speakers remember
  familiar verses, so drafts drift towards it. Draft from the Greek and the
  gloss, then rewrite any sentence that matches a well-known version for more
  than a short common phrase ("neema juu ya neema", "amejaa neema na kweli").
  There is no public-domain Swahili Bible in modern standard Swahili to
  compare with; the English reference Bibles serve for comparison.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied from
  the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"sw": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, in every
  Swahili level. **(checked)**
- The meaning decisions are shared: do not change them. Swahili needs only its
  own rendering decisions, with ids `r-sw-1`, `r-sw-2`, ... counted from 1 in
  each record, `"layer": "rendering"`, `"language": "sw"`, the `levels` they
  apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the Spanish ones; the Swahili words under discussion are quoted in it
  ("\"nuru\" rather than \"mwanga\""). The site tells Swahili readers that
  notes are in English for now.
- Write a Swahili rendering decision where Swahili had to choose and a reader
  might ask why: a word chosen against a familiar alternative, a structure
  Swahili cannot copy, a setting span that differs from the English one, a
  term settled here for the whole book (once, where it first appears in a
  passage). Do not repeat the English rendering decisions; where Swahili
  simply follows the English choice, no decision is needed. Typical density:
  zero to two per sentence.

## 3. The three levels in Swahili

The level names on the site are **Halisi** (Literal), **Linganifu**
(Balanced) and **Rahisi** (Readable).

**Literal (OWB-L).** Follows the Greek order and wording where Swahili allows.
Words Swahili needs but the Greek lacks go in [square brackets], as in
English. Swahili has no articles, so the English bracketed "[the]" has no
Swahili counterpart, and a pronoun that Swahili marks inside the verb (the
subject prefix *a-*, the object marker *-m-*) is part of the verb and is not
bracketed. Keep the historic present ("anasema") where the Greek has it.

**Balanced (OWB-B).** Careful standard Swahili (Kiswahili Sanifu), the register
of a good public reading. Tracks the Greek closely; no brackets. Narrative
uses *-li-* for the first verb of a sequence and *-ka-* for the verbs that
follow ("alikuja, akasema"), as written Swahili narrative does.

**Readable (OWB-R).** Plain Swahili for new and young readers: short
sentences, common words. Explains idioms and may make explicit what the
context implies, as the English Readable does, with a decision where the
English has one.

## 4. Spelling and typography

- Standard Swahili as written in Tanzania and Kenya; no Sheng, no regional
  forms. Spell *ng'* with the apostrophe ("inang'aa"); the site turns it into
  the typographic ’.
- Quotation marks as in English: “ ” outside, ‘ ’ for a quotation inside a
  quotation. Store them straight in `content/`, as the English does.
- Capitals: Mungu, Baba, Mwana, Roho Mtakatifu, Bwana (the Lord), Mwana wa
  Adamu, Mwanakondoo wa Mungu, Maandiko. "sheria" (the Law) is lowercase, as
  "law" is in English.
- Numbers in words in running text ("watu watano"); measures in figures.
- Clock time: the Greek counts hours from sunrise, as Swahili time does, so
  "the tenth hour" is simply *saa kumi* at every level, in the afternoon.
  Readable may add *jioni*. No conversion is needed, unlike English.
- Proper names in their usual Swahili form: Yesu, Yohana, Musa, Eliya, Isaya,
  Simoni Petro, Andrea, Filipo, Nathanaeli, Bethsaida, Bethania, Kana ya
  Galilaya, Kapernaumu, Kefa, Yerusalemu, Mafarisayo, Walawi, Wayahudi.

## 5. Words for the whole of John

| Greek (English) | Swahili | Notes |
|---|---|---|
| the Word | **Neno** | Every level. *Neno* is a class 5 noun, but because it names a person it takes personal agreement (*Neno alikuwa*, *Neno akawa mwili*), as names for living beings do in Swahili. Recorded as an uncertain rendering decision in 1:1 for a native reviewer. |
| grace | neema | Key term: the same word at every level. |
| truth | kweli | Key term. The older noun, still standard, and the same word as "true" (*nuru ya kweli*), which keeps John's link between them. *Ukweli* is the everyday modern noun; a reviewer may prefer it at Readable. Recorded as uncertain in 1:14. |
| glory | utukufu | Key term. |
| peace | amani | Key term. |
| righteousness | haki | Key term. So *haki* is never used for "right" or "authority" (1:12 uses *mamlaka*, *uwezo*). |
| faith; believe | imani; kuamini | Keep the verb at every level. |
| life (*zōē*) | uzima | *Maisha* is a lifetime or daily living; *uzima* is life itself, the word for eternal life. |
| eternal life | uzima wa milele | |
| light, darkness | nuru, giza | *Mwanga* is everyday light; *nuru* is the word for light as a figure, and John's light is one. |
| the world | ulimwengu | |
| through (*dia*, of an agent) | kupitia | Not *kwa*, which can also mean "by", "with" or "to". |
| sign | ishara | Never "muujiza" (miracle). |
| glorify | kutukuza | |
| testify, testimony, witness | kushuhudia, ushuhuda, shahidi | Readable may say *kuwaambia watu habari za* with a decision where the English Readable also loosens it. |
| remain, stay | kukaa | |
| the Jews | Wayahudi (L); viongozi wa Wayahudi (B, R) where the authorities are meant; Wayahudi, -a Kiyahudi where the people are meant | As `docs/john-terms.md`. |
| Truly, truly | Kweli kweli nawaambia (L, B); Nawaambia ukweli (R) | One decision per passage. |
| Son of Man | Mwana wa Adamu | The settled Swahili title (*Adamu* is also "humankind"); never under the gender setting. *Mwana wa Mtu* is more literal; recorded as uncertain where it first appears. |
| Lamb of God | Mwanakondoo wa Mungu | |
| Rabbi | Rabi | |
| Messiah (1:41) | Masihi | Plainly, no setting; the explanation is `{{christos:Kristo|Masihi}}`. |
| disciples | wanafunzi | Every level. |
| slave (*doulos*) | mtumwa (L); mtumishi (B, R) | As the English: *mtumwa* at every level where slavery itself is the point (slave and free, bought and sold, slavery in Egypt, slavery to sin). |
| Sir / Lord (*kyrie*) | bwana / Bwana | Swahili uses one word for both: lowercase *bwana* as polite address, *Bwana* for those who believe, as `docs/john-terms.md`. |
| Woman (2:4) | Mama | At every level: a man calling a woman *Mwanamke!* to her face is rude in Swahili, while *Mama* is the respectful address to any older woman. Needs a decision where it first appears. |

## 6. Forms of address

Swahili has distinct singular and plural "you" (*wewe*, *ninyi*, and the verb
prefixes *u-*, *m-*), so the Greek distinction comes through without a
setting. God and Jesus are addressed with *wewe*.

## 7. Reader settings in Swahili

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: Swahili marks most pronouns inside the verb (*alikuja*,
  *hawakumpokea*), and a prefix cannot take a capital, so a span goes only on
  a free pronoun: `{{deity_pronoun:yeye|Yeye}}`,
  `{{deity_pronoun:mwenyewe|Mwenyewe}}`, and the possessives, which agree
  with the thing possessed: `utukufu {{deity_pronoun:wake|Wake}}`,
  `jina {{deity_pronoun:lake|Lake}}`, `ndani {{deity_pronoun:yake|Yake}}`,
  `habari {{deity_pronoun:zake|Zake}}`, `kilicho {{deity_pronoun:chake|Chake}}`.
  When Jesus speaks of himself: `mimi|Mimi`, `yangu|Yangu`, `wangu|Wangu`
  and so on, and when he is spoken to, `wewe|Wewe`, `yako|Yako`. The joined
  forms are free pronouns too and take the span when they mean God or
  Jesus: `nami|Nami`, `nawe|Nawe`, `naye|Naye` (and I, with you, with him),
  and `kwangu|Kwangu`, `kwako|Kwako`, `kwake|Kwake`. Only the
  capitalisation differs. **(checked)** A pronoun at the start of a sentence
  is written plainly with its capital. Swahili therefore has fewer spans than
  English; the first record of a passage notes this once.
- `christos`: `{{christos:Kristo|Masihi}}`, and
  `Yesu {{christos:Kristo|Masihi}}`. Swahili has no article, so both read
  naturally at every level.
- `gender`: Swahili nouns for people are already inclusive (*mtu*, *watu*,
  *wanadamu*, *binadamu*, *ndugu*, *watoto*), and the only "traditional"
  alternative would be *wanaume*, which means males and would change the
  meaning. So the Swahili text normally has no gender spans, and the setting
  has nothing to change. Use one only where Swahili really has two ways of
  saying the same thing.
- `units`: metric by default, the original unit as the alternative, as in
  French: `{{units:lita 80 hadi 120|vipimo viwili au vitatu}}`. Literal keeps
  the original unit. This differs from the English (US gallons) and needs a
  rendering decision.

## 8. Status

Every new record keeps its status; a Swahili rendering added to a record does
not change it. Nothing is marked reviewed by an AI.
