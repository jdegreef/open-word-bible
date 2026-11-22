# Tagalog style guide

How Open Word Bible drafts Tagalog (Filipino, code `tl`). It builds on
`docs/english-style.md`, which still covers everything that is not about
wording: sources, one record per sentence, the three levels, decisions and
status. It also builds on each book's terms notes (`docs/john-terms.md` and
the others), whose book-wide choices hold in Tagalog unless this file says
otherwise. `docs/tagalog-terms.md` is the glossary of recurring terms and
names, Genesis to Revelation. Where this file and the founder's Translation
Charter disagree, the Charter wins; fix this file.

**Status: drafting brief, awaiting a native Tagalog reviewer.** The whole
Bible is to be drafted in Tagalog from this file. Every choice below is
**the rule drafters follow**, book by book, without re-deciding it; a
drafter who thinks a rule is wrong for a passage follows it anyway and says
so in a rendering decision marked uncertain. Section 14 lists the choices
that decide the most verses, for the founder and a native reviewer to
confirm or change once; a change is made here and then carried through every
book drafted under the old rule.

**Tagalog or Filipino.** Filipino, the national language of the
Philippines, is standard Tagalog with the wider alphabet and the loanwords
of national use. The text is written in that standard: the language most
Filipinos read in church, at school and in the press, whatever their first
language. The site lists it as *Tagalog*, the name readers search for
("Tagalog Bible") and the name of the language code; the native name is
section 14, item 1. The code is `tl` (ISO 639-1), which the site's
`<html lang>`, hreflang and `/tl/` folder use; `fil` (ISO 639-2) is not
used anywhere in the site.

Tagalog becomes a reading language (`tl` in `data/languages.json`, with the
other files `docs/adding-a-language.md` lists) in its own pull request,
after this brief; from then on the validator accepts a `tl` rendering.
Every Tagalog record is `ai_draft`.

## 1. Sources and independence

- Translate from the Hebrew and the Greek, never from the English. The
  English renderings and the literal gloss show how a sentence was read;
  the meaning decisions say what it means. Tagalog says that meaning in its
  own way.
- **Never reproduce the wording of a copyrighted Tagalog Bible.** Under
  copyright: the *Ang Bagong Ang Biblia* (ABAB, 2001, Philippine Bible
  Society), the *Magandang Balita Biblia* (MBB, 1980, revised 2005 and 2012,
  the common-language version read in many Catholic and Protestant
  churches), the *Filipino Standard Version* (FSV), *Ang Salita ng Diyos* /
  *Ang Salita ng Dios* (ASND/ASD, Biblica), the *Bibliya ng Sambayanang
  Pilipino* and the other Catholic editions, the *Bagong Sanlibutang Salin*
  (Watch Tower), the *Ang Biblia, Pinoy Version* and the paraphrases. *Ang
  Dating Biblia* (ADB, 1905) is in the public domain, but its Tagalog is
  more than a century old (*datapuwa't*, *anopa't*, *nangagsisi*,
  *sinasabi*-chains, *Dios* and the old plural verbs), so a draft that
  drifts toward it drifts out of the register this file asks for
  (section 3).
- Because ADB is still read aloud in many Protestant churches and MBB in
  many Catholic and Protestant ones, familiar verses pull drafts toward
  their wording. Draft from the Hebrew or Greek and the gloss, then
  **compare every well-known verse with ABAB, MBB and ASND and rewrite any
  sentence that matches one of them for more than a short common phrase.**
  A short common phrase is a term or a fixed collocation any Filipino
  Christian would use (*kaharian ng Diyos*, *Anak ng Tao*, *buhay na walang
  hanggan*, *Kordero ng Diyos*, *patawarin ang mga kasalanan*), not a
  clause.
- The conventional forms of names, the names of the books and the church's
  shared vocabulary (sections 6–8) are not wording and may be used.
- Reference Bibles in any language are for comparison and review only,
  never the basis for Open Word Bible wording.
- Never type Greek or Hebrew. A Greek or Hebrew word quoted in a decision
  is copied from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"tl": {"L": ..., "B": ..., "R": ...}` to each record's
  `renderings`, after the other languages. Every level is required.
  **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, and
  the `\q ` line breaks of poetry (section 12), in every Tagalog level.
  Tagalog puts the predicate first (*Umalis si Elimelec*), close to the
  Hebrew verb-first narrative, so a verse's content seldom has to cross a
  marker. Where it must, say so in a `word_order` decision.
- The meaning decisions are shared: do not change them. Tagalog needs only
  its own rendering decisions, with ids `r-tl-1`, `r-tl-2`, ... counted
  from 1 in each record, `"layer": "rendering"`, `"language": "tl"`, the
  `levels` they apply to, and a wording category (word_choice, word_order,
  register, supplied_words, setting_alternative).
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions; the Tagalog words under discussion are
  quoted in it ("\"biyaya\" rather than \"grasya\""). The site tells
  Tagalog readers that notes are in English for now.
- Write a Tagalog rendering decision where Tagalog had to choose and a
  reader might ask why: a word chosen against a familiar church alternative,
  a form of address or the use of *po*, a setting span that differs from the
  English one, a *tayo*/*kami* choice that is not obvious, or a term settled
  here for the whole book (once, where it first appears in a passage). Do
  not repeat the English rendering decisions. Typical density: zero to two
  per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language, so each Tagalog level opens and closes the same
  quotations, in the same order, as the English one.

## 3. The three levels in Tagalog

The level names on the site are proposed as **Literal**, **Balanse**
(Balanced) and **Madaling Basahin** (Readable).

The language is **standard modern Filipino**: the spelling of the Komisyon
sa Wikang Filipino's *Ortograpiyang Pambansa* (2013) and *Manwal sa
Masinop na Pagsulat*, the words of the *UP Diksiyonaryong Filipino*. Two
registers are avoided at every level:

- **Old Bible Tagalog**: *datapuwa't*, *anopa't*, *sapagka't* (write
  *sapagkat*), *gayon ma'y*, *kaya't* as a clause opener in a chain,
  *yaon*, *yaong*, *niyaon*, *aniya* outside a quotation tag, *Dios*, the
  old plural verbs with *nag-*/*nang-* plus reduplication for every plural
  subject (*nangagsisi*, *nangagsialis*), *ikaw ay* + noun in every
  address, and *sinabi niya* after every clause of a speech. These are the
  marks of ADB and of the versions that echo it.
- **Taglish and street Filipino**: English words where Filipino has its own
  (*pero* is Filipino; *but*, *so*, *talaga namang*, *actually*, *basically*
  are not), texting forms, *nung* for *noong*, *pa'no*, *'di ba*, *kasi*
  opening a sentence at Literal and Balanced, *grabe*, *sobra* for "very",
  *pare*, *tol*, *'yung* for *iyong*. Readable is plain, not spoken.
- **Purist coinages** (*salumpuwit*, *salipawpaw*, *sipnayan*) are avoided
  too: where Filipino uses a Spanish or English loanword as its ordinary
  word (*mesa*, *barko*, *templo*, *krus*, *propeta*), use it.

**Literal (OWB-L).** Follows the Hebrew or Greek order and wording where
Tagalog allows; keeps participles as clauses (*habang ...*, *pagkatapos
...*), genitives as noun + *ng* + noun (*anak ni David*, *salita ng
Diyos*), the source's repetitions (*at ... at ...*) and the historic
present where Tagalog's aspect allows (*Sinabi ni Jesus*, the completed
aspect, is the default; the contemplated *sasabihin* only where the sense
is future). The *ay* inversion is used where the source fronts the
subject (*Ang Salita ay kasama ng Diyos*). Words Tagalog needs but the
source lacks go in [square brackets]. What Tagalog grammar requires is not
bracketed: the markers *ang*, *ng*, *sa*, *si*, *ni*, *kay*, *sina*,
*nina*, *kina*; the linkers *na* and *-ng*; *ay*; *mga* for a plural; the
enclitics (*na*, *pa*, *nga*, *rin*, *din*, *lamang*) where the sense needs
them; and the pronoun a Tagalog verb needs to be a sentence. Literal may
read stiffly; it must not be wrong Tagalog.

**Balanced (Balanse, OWB-B).** Careful written Filipino, the register of a
good public reading in church or of a serious newspaper. Tracks the source
closely; no brackets. Uses the predicate-first order as the normal one and
the *ay* inversion where it gives weight or eases a long subject. Church
words stay where they are the living word for the thing (*biyaya*,
*magsisi*, *kaharian ng Diyos*, *punong pari*).

**Readable (Madaling Basahin, OWB-R).** Plain Filipino for new and young
readers and for those whose first language is another Philippine language
(Cebuano, Ilocano, Hiligaynon, Bikol, Waray, Kapampangan ...): short
sentences, common words, explained idioms, and what the context implies
made explicit where the English Readable does so, with a decision.
Readable puts the predicate first, avoids long *ay* chains, and writes *ay*
in full (no *ako'y*, *siya'y*). Section 11 gives the Readable rules for
focus and affixes.

## 4. God, the Lord and the divine name

### God: *Diyos*

- *theos* and *Elohim* (of the God of Israel) are **Diyos** at every level,
  the spelling of the Ortograpiya and of every modern Tagalog Bible; ADB's
  *Dios* is not used. Catholics and Protestants alike say *Diyos*.
- A false god or gods: *diyos* lowercase (*ibang diyos*, *mga diyos ng mga
  bansa*), *diyosa* for a goddess (*ang diyosang si Artemis*), *Baal* as a
  name. *Bathala* (the precolonial Tagalog high god) is never used.
- *El* compounds: *Diyos na Kataas-taasan* (*El Elyon*), *Diyos na
  Makapangyarihan sa Lahat* (*El Shaddai*), *ang Makapangyarihan sa Lahat*
  (*Shaddai* alone), *Diyos na walang hanggan* (*El Olam*).
- *Diyos* is a common noun in Tagalog grammar and takes *ang*, *ng*, *sa*
  (*ang Diyos*, *salita ng Diyos*, *sa Diyos*), not *si*, *ni*, *kay*.

### Lord: *Panginoon*

- *kyrios* for God or for Jesus, and *Adonai*, are **Panginoon** (capital
  P) at every level, with *ang*, *ng*, *sa*. "The Lord Jesus" is *ang
  Panginoong Jesus*. "Lord!" in address is *Panginoon!*
- *kyrios* or *adon* for a human master is **panginoon** (lowercase) at
  Literal and Balanced, *amo* at Readable where it means a slave's or a
  servant's master. *kyrie* to a stranger is *Ginoo* in address. Where it
  is unclear whether a speaker means "Lord" or "sir" (John 4; 9:36), follow
  the English choice and its decision.
- "my lord" from a subject to a king is *panginoon kong hari* (L), *Mahal
  na Hari* (B, R) (section 5).

### The divine name: *PANGINOON* by default, *Yahweh* as the setting

Tagalog marks a noun's role with a particle before it, and it uses one set
of particles for common nouns (*ang*, *ng*, *sa*) and another for personal
names (*si*, *ni*, *kay*). *PANGINOON* is a title and takes the first set;
*Yahweh* is a name and takes the second. So **the marker goes inside the
`divine_name` span**, as the English writes `{{divine_name:the LORD|Yahweh}}`
with the article inside:

| Role | Default (title) | Alternative (name) | Span |
|---|---|---|---|
| subject, topic | *ang PANGINOON* | *si Yahweh* | `{{divine_name:ang PANGINOON\|si Yahweh}}` |
| possessor, agent | *ng PANGINOON* | *ni Yahweh* | `{{divine_name:ng PANGINOON\|ni Yahweh}}` |
| to, for, in | *sa PANGINOON* | *kay Yahweh* | `{{divine_name:sa PANGINOON\|kay Yahweh}}` |
| address, after *O* | *PANGINOON* | *Yahweh* | `{{divine_name:PANGINOON\|Yahweh}}` |
| after a preposition with *sa* (*para sa*, *laban sa*, *tungkol sa*) | *sa PANGINOON* | *kay Yahweh* | `para {{divine_name:sa PANGINOON\|kay Yahweh}}` |

- **A linker also goes inside.** *PANGINOON* ends in *n* and takes *-g*
  (*PANGINOONG*); *Yahweh* ends in a consonant and takes *na*. So "the LORD
  your God" is `{{divine_name:ang PANGINOONG|si Yahweh na}} inyong Diyos`,
  and "the LORD God" (*YHWH Elohim*, Genesis 2–3) is
  `{{divine_name:ang PANGINOONG|si Yahweh na}} Diyos`. Read both options
  aloud before committing a span.
- **The *ay* inversion** needs nothing extra: `{{divine_name:Ang PANGINOON|Si Yahweh}} ay aking pastol`.
  At the start of a sentence the marker is capitalised in both options.
- **Plural markers.** Where the name is one of several people named
  together (*sina Moises at Aaron*), keep the divine name out of the group
  or reword; never write *sina* inside the span.
- **Capitals.** *PANGINOON* is printed in capitals, like the English "the
  LORD", as ABAB and ASND print it; *Panginoon* with only a capital P is
  *Adonai* and *kyrios*. *Yahweh* is the spelling of the alternative: it is
  the form MBB made familiar to Filipino readers and the form scholars use.
  *Jehova* and *Jehovah* (ADB, Watch Tower usage) are not used.
- ***Adonai YHWH*** ("Lord GOD") is `Panginoong {{divine_name:DIYOS|Yahweh}}`,
  with *ang*, *ng* or *sa* before it outside the span (*ang Panginoong
  DIYOS*, *ang Panginoong Yahweh*): *Panginoon* is a common noun in both
  options, so the marker does not change.
- ***YHWH tsevaot*** is `{{divine_name:ang PANGINOON|si Yahweh}} ng mga hukbo`
  at Literal and Balanced (with *ng* or *sa* as the role needs); Readable
  may say `{{divine_name:ang PANGINOON|si Yahweh}} na Makapangyarihan sa Lahat`
  where the English Readable explains the title, with a decision.
- The short form *Yah* is `{{divine_name:ang PANGINOON|si Yah}}` (and the
  other roles); in *Hallelu Yah* it is *Aleluya*, with no span, as the
  English writes "Hallelujah".
- In a New Testament quotation of the Old Testament the Greek has *kyrios*,
  so write *Panginoon* and note the Hebrew original in a decision, as the
  English does (John 1:23).

### Pronouns for God: the `deity_pronoun` setting

Tagalog pronouns have no gender, so *siya* and *niya* can mean any person
in the sentence. Tagalog Bibles do not capitalise pronouns for God, but
much Filipino Christian writing does (*sa Kaniyang pangalan*, *Siya ang
...*), and where two men are in a sentence the capital is often the only
sign of who is meant. So, as in English, the capitalised form is the
default and the `deity_pronoun` setting lets a reader choose lowercase.

- **Put a span wherever the English has one for the same person**, and only
  there. English capitalises "I" anyway and has no span on it, so Tagalog
  *ako*, *ko*, *akin* for God speaking take **no** span. The spans are:
  - third person: `{{deity_pronoun:siya|Siya}}`, `{{deity_pronoun:niya|Niya}}`,
    `{{deity_pronoun:kaniya|Kaniya}}`, `{{deity_pronoun:kaniyang|Kaniyang}}`
    (the linker inside the span);
  - God or Jesus spoken to: `{{deity_pronoun:ikaw|Ikaw}}`,
    `{{deity_pronoun:ka|Ka}}`, `{{deity_pronoun:mo|Mo}}`,
    `{{deity_pronoun:iyo|Iyo}}`, `{{deity_pronoun:iyong|Iyong}}`;
  - God's "Us" (Genesis 1:26; 3:22; 11:7), where the English has a span:
    `{{deity_pronoun:natin|Natin}}`, `{{deity_pronoun:tayo|Tayo}}`.
- A pronoun at the start of a sentence is written plainly with its capital
  and no span (*Siya ang ...*), as in English.
- **Where the English starts a sentence with a plain "He"**, the Tagalog
  pronoun usually falls after the verb (*Inihiwalay niya ...*). It takes the
  span there, so it shows the same capital as every other pronoun for God;
  a lowercase *niya* with no span in the middle of a sentence would break
  the default. The count of spans may therefore exceed the English one.
  (Settled in Genesis 1:4.)
- **Enclitics.** Tagalog's short pronouns come second in the clause (*Pinuri
  {{deity_pronoun:ka|Ka}} namin*, *Hindi {{deity_pronoun:niya|Niya}} sila
  iniwan*). A span does not move them: write the clause as Tagalog orders
  it and put the span on the pronoun where it falls.
- Spans for people in a parable stay out, as in English.
- **One form for "his/to him".** *kaniya*, *kaniyang* at every level, the
  Ortograpiya's preferred spelling, for God and for people alike; *kanya*
  (the common short spelling) is not used, so search finds one form.

## 5. Address and speech

Tagalog marks the relation between speaker and hearer with *po* and *opo*,
with titles, and in how it says "you". The source does not; these are
wording choices, rendering decisions, never meaning decisions. They hold
through a book so a scene does not change relationship from verse to verse.

### "I"

- **God and Jesus** say *ako*, *ko*, *akin* at every level (no span).
- **People** say *ako*. The Hebrew humble self-reference "your servant" is
  kept at Literal (*ang iyong lingkod*, *ang iyong alipin*) and is *ako* at
  Balanced and Readable, with *po* where the speaker defers (below), with
  a decision the first time in a book.

### "You" singular

- **To God and to Jesus**: *ikaw*, *ka*, *mo*, *iyo*, with the span (section
  4), at every level, from disciples, petitioners and opponents alike;
  their words show their attitude. This is how Filipino prayer and every
  Tagalog Bible speak to God. The respectful plural (*kayo*, *ninyo* to one
  person) is **not** used for God or Jesus, so a reader can always tell one
  from many.
- **People to each other**: *ikaw*, *ka*, *mo* at every level. The
  respectful plural for one person is not used in the text either, for the
  same reason; respect is carried by *po* and by titles.
- **To a king**: *Mahal na Hari* (B, R) or *panginoon kong hari* (L) as the
  form of address, with singular pronouns and *po* at B and R
  (*Mabuhay po ang Mahal na Hari!*).
- **Woman** (*gynai*) as an address: *Babae* at Literal, with a decision;
  *Ginang* at Balanced and Readable, and *Ina* where Jesus speaks to his
  mother at Readable (John 2:4; 19:26), since *Babae* sounds curt in
  Filipino.

### *Po* and *opo*

- **Literal** has no *po*: the source has nothing it stands for.
- **Balanced and Readable** use *po* (and *opo* for "yes") where a person
  speaks to a superior, an elder, a king, a priest or a prophet, or to a
  stranger with deference: servants to their masters, petitioners to Jesus
  (*Ginoo, tulungan po ninyo* is not used; *Panginoon, tulungan mo po ako*
  is), a younger person pleading with an older one. Not between equals,
  not from a superior to an inferior, not from Jesus, and **not in prayer
  to God**, where the Tagalog Bible tradition speaks without it.
- Decide once per speaker in a scene and record it in the first record
  that uses it.

### "You" plural and "we"

- **kayo**, **ninyo**, **inyo** for "you" plural at every level. There is no
  regional split in the plural, so no `plural_you` setting.
- **We**: Tagalog distinguishes inclusive *tayo*, *natin*, *atin* (the
  hearers included) from exclusive *kami*, *namin*, *amin* (not included),
  and the Hebrew and Greek do not. Every "we" is a choice: the eyewitnesses
  of John 1:14 and 1 John 1:1 are *kami*; Paul with his readers is *tayo*;
  Paul and his companions *kami*; a people praying to God is *kami*.
  Where the choice is not obvious, record it in a decision.
- **Israel addressed as "you" singular** (Deuteronomy above all): Literal
  follows the Hebrew number, singular *ikaw*, *mo*, *iyo* where the Hebrew
  is singular. Balanced and Readable use *kayo*, *ninyo* for the assembly,
  since a Tagalog speaker addressing a crowd says *kayo*. Keep the singular
  at every level where the singular is the point: the Ten Words, the
  Shema, the father answering his son (Deut 6:20-25), the one who entices
  "you" in secret (Deut 13:7-12), each worshipper's rite (Deut 26:1-15),
  the Song of Moses (Deut 32), and words to one person (Joshua, Moses).
  Record the choice in the first verse of a chapter that switches.
- **Dual** *kita* ("you and I") is standard; use it where two people speak
  to each other (Ruth 1:16 context), never as a plural.

### Brothers and sisters

- *adelphoi* meaning believers is **mga kapatid**, with **no gender span**.
  Tagalog *kapatid* means a sibling of either sex, so the inclusive meaning
  needs no second option.
- In address: *Mga kapatid* (L, B, R), *mga minamahal kong kapatid* for
  "beloved brothers".
- A specific brother is *kapatid na lalaki*, a sister *kapatid na babae*,
  where the sex matters (Mark 6:3).

### Verbs of speaking

- God speaks: *sinabi*, *nagsalita*, *ipinahayag*, *iniutos* as the source
  says; there is no separate royal verb. His word is *salita*.
- Jesus and everyone else: *sinabi*, *nagsabi*, *sumagot*, *nagtanong*,
  *sinaway* where the source has them. *wika* and *aniya* are not used as
  the ordinary speech verb (old register).
- A quotation is introduced with a comma: *Sinabi ni Jesus, "..."*. A colon
  only before a long, formal speech or a letter.

## 6. Names

### Principles

Open Word Bible uses **the established forms of the Filipino church**: the
Spanish-derived forms that Catholics and Protestants have shared since the
first Tagalog Bibles, which the press and schools use for biblical people
and places (*Jesus*, *Juan*, *Pedro*, *Santiago*, *Moises*, *Josue*,
*Isaias*, *Jerusalem*, *Egipto*). They are not wording and may be used.

How to decide a name:

1. **An established church form exists** (most Filipino Christians would
   recognise it): use it, even where it is far from the Hebrew or Greek
   (*Jesus*, *Juan*, *Santiago*, *Pedro*, *Pablo*, *Moises*, *Noe*). Hebrew
   reconstructions (*Yeshua*, *Moshe*) are not used.
2. **The Spanish-derived spelling is kept** with its letters *c*, *j*,
   *qu*, *z* (*Cristo*, *Jacob*, *Ezequias* where established), but
   without written accents (*Jose*, *Moises*, *Noe*, *Efraim*): Filipino
   writes no accents in names.
3. **Two church forms compete** (ADB's and MBB's): use the one most
   readers recognise today, and if they are equal, the one closer to the
   source; record it in a decision the first time and in the glossary.
4. **No established form** (the minor names of Chronicles, Ezra and
   Nehemiah): start from the English draft's form and adapt it: *ph* > *f*,
   *th* > *t*, *ch* and *kh* > *k*, *sh* kept, final *-ah* kept, *y* kept
   (no new *j* forms). Note the new form in a decision where it first
   appears in the book, and add it to `docs/tagalog-terms.md`.
5. **One person, one form, through the whole Bible.** A name shared by
   several people keeps one spelling. An Old Testament name quoted in the
   New Testament keeps its Old Testament form (*Elias*, *Isaias*,
   *Enoc*), not a form taken from the Greek.

**Grammar of names.** Personal names take *si*, *ni*, *kay* (*si Pedro*,
*ni Pedro*, *kay Pedro*; plural *sina*, *nina*, *kina*). Place names take
*ang*, *ng*, *sa* (*sa Jerusalem*). A people is *ang mga Judio*, *ang mga
Israelita*; the nation is *ang Israel*, *ang bayang Israel*.

### The common forms

Jesus and the Gospels: *Jesus*, *Maria*, *Jose*, *Juan* (the Baptist and
the apostle), *Juan na Tagapagbautismo*, *Simon Pedro*, *Pedro*, *Andres*,
*Santiago* (the apostles and the brother of the Lord; the patriarch is
*Jacob*), *Zebedeo*, *Felipe*, *Bartolome*, *Tomas*, *Mateo*, *Natanael*,
*Judas Iscariote*, *Nicodemo*, *Lazaro*, *Marta*, *Maria Magdalena*,
*Pilato*, *Caifas*, *Anas*, *Barabas*, *Herodes*, *Zacarias*, *Elisabet*,
*Simeon*, *Ana*. Acts and the letters: *Pablo*, *Saulo*, *Bernabe*,
*Esteban*, *Silas*, *Timoteo*, *Tito*, *Apolos*, *Priscila*, *Aquila*,
*Cornelio*, *Gamaliel*, *Felix*, *Festo*, *Agripa*, *Febe*, *Tiquico*,
*Onesimo*, *Filemon*, *Lucas*, *Marcos*. Places: *Jerusalem*, *Galilea*,
*Judea*, *Samaria*, *Nazaret*, *Betlehem*, *Capernaum*, *Betsaida*,
*Betania*, *Ilog Jordan*, *Roma*, *Antioquia*, *Efeso*, *Corinto*,
*Filipos*, *Tesalonica*, *Atenas*, *Damasco*, *Cesarea*, *Chipre*,
*Alejandria*. Peoples: *mga Judio*, *mga Samaritano*, *mga Griego*, *mga
Romano*, *mga Pariseo*, *mga Saduceo*, *mga Levita*, *mga Israelita*. The
Old Testament forms are in `docs/tagalog-terms.md`.

## 7. Words for the whole Bible

The key terms of `data/key_terms.json` keep one Tagalog word at every
level (with the same exceptions as the English: Readable may say "good
news" for "gospel", and a sense such as "being right with God" at Readable
needs a decision). The terms after them are settled for every book.

| Greek / Hebrew (English) | Tagalog | Why |
|---|---|---|
| grace (*charis*) | **biyaya** | Key term. The common church word of both traditions. *grasya* (Spanish loan) is everyday and Catholic-devotional; *kagandahang-loob* is kindness. |
| glory (*doxa*); glorious | **kaluwalhatian**; *maluwalhati* | Key term. |
| glorify (*doxazō*) | **luwalhatiin**; *niluwalhati*, *luluwalhatiin* | Key term; the same root as *kaluwalhatian*, as the Greek has. Readable keeps it; *parangalan* (honour) is not a substitute. |
| truth (*alētheia*) | **katotohanan** | Key term. *totoo* for "true" of statements, *tunay* for "true" as "real" (*ang tunay na ilaw*). |
| righteousness (*dikaiosynē*); righteous | **katuwiran**; *matuwid* (L, B); R may say *pagiging matuwid sa harap ng Diyos* with a decision | Key term. Distinct from *katotohanan* (truth) and *katarungan* (justice). |
| justify (*dikaioō*) | *ariing-matuwid* (L, B); *ituring na matuwid* (R) | Same root as *katuwiran*, which keeps Paul's argument visible. ADB's *ariing-ganap* is a familiar alternative, not used. |
| faith (*pistis*) | **pananampalataya** | Key term. *katapatan* where a meaning decision says "faithfulness". |
| believe (*pisteuō*) | **sumampalataya**, *manampalataya*; *sumampalataya sa* (*eis*) | Key term. *maniwala* where a meaning decision says the sense is "believe that (a statement is true)". |
| joy (*chara*) | **kagalakan**; *magalak* | Key term. |
| salvation (*sōtēria*); save | **kaligtasan**; *iligtas*, *maligtas*, *ligtas* | Key term. |
| gospel (*euangelion*) | **Ebanghelyo** (L, B); **Magandang Balita** (R) | Key term, levels as the English. Capitalised. *Magandang Balita* is also used at B where the English says "good news". |
| world (*kosmos*) | **sanlibutan** | Key term, every level. *mundo* is everyday but not used for *kosmos*, so the term can be followed; *daigdig* for the earth as a place. |
| eternal (*aiōnios*); eternal life | **walang hanggan**; *buhay na walang hanggan* | Key term. |
| sign (*sēmeion*) | **tanda** | Key term. Never *himala* alone, which means "miracle". |
| mystery (*mystērion*) | **hiwaga** | Key term. *misteryo* has a detective-story sense. |
| peace (*eirēnē*; *shalom*) | **kapayapaan** | Key term. The greeting *eirēnē hymin*: *Sumainyo ang kapayapaan* (L, B), *Kapayapaan sa inyo* (R). *shalom* as welfare or safety: *kalagayan*, *ligtas*, *mabuti* by the key-term list. |
| YHWH | `{{divine_name:ang PANGINOON\|si Yahweh}}` and the other roles | Key term (Hebrew). Section 4. |
| steadfast love (*hesed*) | **tapat na pag-ibig** | Love and loyalty in one phrase, every level, Readable included. ADB's *kagandahang-loob* and *kaawaan* are not used. |
| faithfulness (*emunah*); truth (*emet*) | *katapatan*; *katapatan* or *katotohanan* by a meaning decision | *emet* paired with *hesed*: *tapat na pag-ibig at katapatan*. |
| covenant (*berit*; *diathēkē*) | **tipan** (L, B); *tipan* or *kasunduan* (R) | *kasunduan* for a treaty between people. *huling habilin* only where the Greek means a will (Hebrews 9:16–17). |
| holy; sanctify; the saints | *banal*; *gawing banal*, *pakabanalin*; *mga banal* (L, B), *mga mananampalataya*, *bayan ng Diyos* (R) | |
| justice (*mishpat*); righteousness (*tsedaqah*) | *katarungan*; *katuwiran* | The pair *katarungan at katuwiran*. |
| sin; transgression; iniquity | *kasalanan*; *paglabag*; *kasamaan* | |
| atone (*kipper*); atonement | *gumawa ng pagtubos sa kasalanan* (L, B); *alisin ang kasalanan* (R) | *pantubos* for the price. |
| mercy seat (*kapporet*) | *Luklukan ng Awa* (L, B); *takip ng Kaban* (R) | |
| redeem; redeemer (*go'el*) | *tubusin*; *manunubos*, *tagapagtubos* (the kinsman of Ruth and Leviticus 25) | |
| repent; repentance | *magsisi*; *pagsisisi* | *pagbabalik-loob* for "turn back" (*shuv*). |
| forgive | *patawarin* | |
| law (*torah*; *nomos*, the Law of Moses) | **Kautusan** (capitalised as the Law of Moses); *kautusan* (law in general) | *torah* as "teaching" (Proverbs) is *aral*, *turo*. |
| the Law and the Prophets | *ang Kautusan at ang mga Propeta* | |
| prophet | *propeta*; *mga propeta* | *propetisa* for a woman. |
| priest; high priest; Levites | *pari*; *punong pari*; *mga Levita* | *pari* for Israel's priests too, as MBB and ASND have it; ADB's *pari* is old. |
| sacrifice; offering | **handog**; *alay* | |
| burnt offering; sin offering; guilt offering; peace offering; grain offering | *handog na sinusunog*; *handog para sa kasalanan*; *handog na pambayad sa pagkakasala*; *handog para sa pakikipag-isa*; *handog na pagkaing butil* | *handog para sa pakikipag-isa* for *shelamim* at every level (the meal shared with God). |
| altar | *altar* | |
| tabernacle; tent of meeting; ark of the covenant | *Tabernakulo* (L, B), *Toldang Sambahan* (R); *Toldang Tipanan*; *Kaban ng Tipan* | |
| temple (*hieron*; *naos*; *bayit*, *hekhal*) | *templo*; *bahay ng PANGINOON* (in the span) | "the house of the LORD": `bahay {{divine_name:ng PANGINOON\|ni Yahweh}}`. |
| synagogue | *sinagoga* | |
| church, assembly (*ekklēsia*) | *iglesya* (L, B); *iglesya* or *mga mananampalataya* (R) | Lowercase as a common noun; never part of a denomination's name. Israel's assembly (*qahal*): *kapulungan*. |
| elder; overseer; deacon | *matanda*, *pinuno ng iglesya*; *tagapangasiwa*; *diakono* | Jewish elders: *mga pinuno ng bayan* (B, R), *mga matanda* (L). |
| apostle; disciple | *apostol*; *alagad* | |
| scribes; Pharisees; Sadducees | *mga eskriba* (L), *mga tagapagturo ng Kautusan* (B, R); *mga Pariseo*; *mga Saduceo* | |
| tax collectors; sinners | *maniningil ng buwis*; *makasalanan* | |
| Gentiles, nations (*ethnē*; *goyim*) | *mga bansa* (L); *mga Hentil* (B); *mga hindi Judio* (R) | |
| angel; demon; unclean spirit | *anghel*; *demonyo*; *maruming espiritu* (L, B), *masamang espiritu* (R) | |
| devil; Satan | *diyablo*; *Satanas* | |
| heaven; sky | *langit*; *langit*, *himpapawid* | "kingdom of heaven": *kaharian ng langit*. |
| Gehenna; Hades; Sheol | *Gehenna* (L), *impiyerno* (B, R); *Hades* (L), *daigdig ng mga patay* (B, R); *Sheol* (L, B), *daigdig ng mga patay* (R) | Sheol by the key-term list. |
| Holy Spirit; spirit (*ruakh*) | *Banal na Espiritu*; *Espiritu* (God's), *espiritu* (other); as wind or breath *hangin*, *hininga* | *Espiritu Santo* is the Catholic and older form; section 14, item 7. |
| soul (*nephesh*; *psychē*) | *kaluluwa*; *buhay*; *sarili*, *tao* | By meaning decision, within the key-term list. |
| heart | *puso* | The seat of thought and will, as *lev*; *loob* where the sense is the inner self (*kalooban*). |
| flesh (*sarx*, Paul's moral sense) | *laman* (L); *makasalanang pagkatao*, *likas na pagkamakasalanan* (B, R) by the meaning decision | |
| Son of Man; Son of God; Son of David | *Anak ng Tao*; *Anak ng Diyos*; *Anak ni David* | Titles, capitalised, never under the gender setting. |
| kingdom of God | *kaharian ng Diyos* | |
| Lamb of God | *Kordero ng Diyos* (L, B); *Tupa ng Diyos* (R) | |
| the Word (John 1) | *Salita* | Every level, capitalised as a person. |
| Christ | `{{christos:si Cristo\|ang Mesiyas}}` and the other roles | Section 8. |
| Messiah (*Messias*, John 1:41; 4:25) | *Mesiyas* | Plainly, no setting. |
| baptize; John the Baptist | *bautismuhan*, *binautismuhan*; *Juan na Tagapagbautismo* | *binyagan* is the Catholic everyday word; section 14, item 8. |
| cross; crucify | *krus*; *ipako sa krus* | |
| resurrection; rise | *muling pagkabuhay*; *muling mabuhay*, *bumangon* | |
| love (*agapē*; *agapaō*) | *pag-ibig*; *ibigin*, *mahalin* | *pagmamahal* also at R. |
| mercy (*eleos*); compassion (*rahamim*) | *awa*; *habag* | |
| hope | *pag-asa* | |
| wisdom; knowledge | *karunungan*; *kaalaman* | |
| fear of the LORD | *takot `{{divine_name:sa PANGINOON\|kay Yahweh}}`* | Write the span with its marker: *ang takot sa PANGINOON*. |
| blessed (*makarios*); bless (*barak*, *eulogeō*) | *mapalad*; *pagpalain* | |
| woe | *kawawa* (B, R); *sa aba* (L) | |
| Amen; Hallelujah; Hosanna | *Amen*; *Aleluya*; *Hosana* | |
| Truly I tell you (*amēn legō hymin*) | *Amen, sinasabi ko sa inyo* (L); *Totoo ang sinasabi ko sa inyo* (B); *Tandaan ninyo ito* (R) | One decision per passage. John's doubled *amēn*: *Amen, amen* (L); *Totoong-totoo* (B). |
| slave (*doulos*; *ʿeved*) | *alipin* (L, B, R) where slavery is the point; *lingkod* for a servant | *lingkod ng Diyos*, `lingkod {{divine_name:ng PANGINOON\|ni Yahweh}}` for God's servants at every level. |
| Sabbath; Passover; Pentecost | *Sabbath* (L), *Araw ng Pamamahinga* (B, R); *Paskuwa*; *Pentecostes* | |
| Feast of Booths; Unleavened Bread | *Pista ng mga Kubol*; *Pista ng Tinapay na Walang Pampaalsa* | |
| Rabbi; Teacher | *Rabi*; *Guro* | |

## 8. Reader settings in Tagalog

Settings change wording, never meaning, exactly as in English.

- `divine_name`: the marker and any linker inside the span (section 4):
  `{{divine_name:ang PANGINOON|si Yahweh}}`, `{{divine_name:ng PANGINOON|ni Yahweh}}`,
  `{{divine_name:sa PANGINOON|kay Yahweh}}`, `{{divine_name:ang PANGINOONG|si Yahweh na}}`;
  and `Panginoong {{divine_name:DIYOS|Yahweh}}` for *Adonai YHWH*.
- `deity_pronoun`: where the English has a span for the same person,
  lowercase first, capitalised second; none on *ako*, *ko*, *akin*
  (section 4).
- `christos`: the marker inside the span, as for the divine name.
  Filipino church speech treats *Cristo* as a name (*si Cristo*, *kay
  Cristo*), while *Mesiyas* is a title (*ang Mesiyas*, *sa Mesiyas*), so
  the two options take different markers (table below). Read both options
  aloud before committing a span.
- `gender`: an inclusive default where the original means men and women,
  with the traditional form as the alternative. Tagalog needs it rarely:
  *tao*, *mga tao*, *sinuman*, *bawat isa*, *mga kapatid*, *mga anak* and
  every pronoun are already inclusive, and get no span. Spans appear where
  Tagalog really has two ways of saying it: `{{gender:mga tao|mga lalaki}}`
  for *anēr* meaning people in general, `{{gender:mga anak|mga anak na lalaki}}`
  for *huioi* where sons and daughters are meant, `{{gender:mga ninuno|mga ama}}`
  for "fathers" as ancestors. Never for God, Christ or named men. A
  rendering decision (setting_alternative) records a difference from the
  English the first time in a passage: most English gender spans have no
  Tagalog counterpart.
- `units`: metric by default, the original unit as the alternative, as in
  every language but English: `{{units:mga tatlong kilometro|labinlimang estadio}}`.
  Literal keeps the original unit with no span. Coins: the value in wages by
  default and the coin as the alternative (`{{units:isang araw na sahod|isang denaryo}}`).
  This differs from the English (US units) and needs a rendering decision
  the first time in a passage. The units: *siko* (cubit, about 45 cm;
  Ezekiel's long cubit about 53 cm), *dangkal* (span), *siklo*, *talento*,
  *mina*, *denaryo*, *drakma*, *efa*, *homer*, *bat*, *estadio*, *milya*.
- `plural_you` and `god_term` belong to other languages; Tagalog has none
  (section 5).
- A setting span holds no quotation marks (`owb/markup.py` checks).

**The `christos` spans.**

| English | Tagalog, every level |
|---|---|
| `{{christos:Christ\|the Messiah}}` as subject | `{{christos:si Cristo\|ang Mesiyas}}` |
| ... as possessor or agent | `{{christos:ni Cristo\|ng Mesiyas}}` |
| ... after *sa* (*en Christō*, "in Christ") | `{{christos:kay Cristo\|sa Mesiyas}}` |
| "the Christ" as a title (Gospels: "Are you the Christ?") | `{{christos:ang Cristo\|ang Mesiyas}}` |
| `Jesus {{christos:Christ\|the Messiah}}` | `si Jesus {{christos:Cristo\|na Mesiyas}}` (*ni*, *kay* as the role needs) |
| `{{christos:Christ\|the Messiah}} Jesus` (Paul's order) | `{{christos:si Cristo\|ang Mesiyas na si}} Jesus`; `{{christos:kay Cristo\|sa Mesiyas na si}} Jesus` |
| the Lord Jesus Christ | `ang Panginoong Jesus {{christos:Cristo\|na Mesiyas}}` |

*Jesu-Cristo* (one hyphenated word, common in church speech) cannot take
the span and is not used; *Jesus Cristo* is written as two words.

## 9. Catholic and Protestant usage

About eight in ten Filipinos are Catholic, and most of the rest belong to
Protestant, evangelical and independent churches (and the Iglesia ni
Cristo, which has its own usage). Tagalog church vocabulary is largely
shared, much of it Spanish-derived: *Diyos*, *Panginoon*, *Espiritu*,
*krus*, *propeta*, *apostol*, *anghel*, *templo*, *Ebanghelyo*. The rules:

1. **Use the shared vocabulary.** Where both traditions use a word, use it;
   do not swap a familiar Spanish loan for a Tagalog coinage to sound
   "more Filipino".
2. **Where the traditions differ, choose the form both understand** and
   note the other in the glossary: *bautismuhan* (Protestant) and
   *binyagan* (Catholic everyday) are both understood; *Banal na Espiritu*
   and *Espiritu Santo* likewise. Section 14 lists these so a reviewer from
   each tradition can weigh in once.
3. **No denominational names.** *Iglesia*, *Simbahan*, *Kristiyano*,
   *Katoliko* are not used as translations of *ekklēsia* or of the Greek
   words for believers; *iglesya* is the common noun (section 7). *Simbahan*
   is the everyday word for a church building and the Catholic Church, and
   does not appear in the Bible text.
4. **No Marian or saints' titles** in the text beyond what the source says:
   *Maria* (not *Birheng Maria* or *Mahal na Birhen*) unless the source
   calls her "the virgin" (*ang birhen*, Matthew 1:23; Luke 1:27).
5. **Neutral notes.** A decision that turns on a traditional reading says
   so plainly, without polemic.

## 10. Spelling, punctuation and typography

- **Spelling**: the Ortograpiyang Pambansa. *Diyos*, *iglesya*,
  *Ebanghelyo*, *kaniya*, *sapagkat*, *subalit*, *ngunit*. The 28-letter
  alphabet (with *c*, *f*, *j*, *ñ*, *q*, *v*, *x*, *z*) is used for names
  and established loans; common loans are spelled the Filipino way
  (*pari*, *krus*, *diyablo*, *demonyo*, *kordero*).
- ***ng* and *nang***: *ng* marks the possessor and the object (*salita ng
  Diyos*, *kumain ng tinapay*); *nang* means "when", "so that", "in a ...
  way", and joins a repeated verb (*nang dumating siya*, *tumakbo nang
  mabilis*, *iyak nang iyak*). A wrong *ng*/*nang* is an error at every
  level.
- ***din*/*rin*, *daw*/*raw*, *doon*/*roon***: *r* after a vowel or *w*, *y*
  (*siya rin*), *d* after a consonant (*Diyos din*).
- **Linkers**: *-ng* after a vowel (*mabuting tao*), *-g* after *n*
  (*Panginoong Jesus*), *na* after other consonants (*mabait na tao*).
- **Contractions**: only the *ay* contraction (*ako'y*, *siya'y*,
  *ito'y*, *sila'y*) at Literal and Balanced and in poetry, with a
  straight apostrophe; Readable writes *ay* in full. No other contraction
  (*'di*, *'yan*, *n'yo*, *'wag*) at any level.
- **Quotation marks**: write straight double quotes `"` for the outer
  quotation and straight single quotes `'` for one inside it, exactly as
  English does; the site curls them into “ ” and ‘ ’, the Filipino marks. A
  quotation that runs over several sentences opens in the first record and
  closes in the last, as in English. The closing mark follows the full
  stop, comma, question or exclamation mark: *Sinabi ni Jesus, "Sumunod ka
  sa akin."* The *ay* apostrophe always stands between two letters
  (*ako'y*), where the quotation finder reads it as an apostrophe; never
  write an apostrophe at the start or end of a word.
- **Hyphens**: between a prefix and a word starting with a vowel
  (*pag-ibig*, *mag-aral*, *nag-iisa*), in reduplicated words
  (*araw-araw*, *bahay-bahay*, *kataas-taasan*), in compounds
  (*bahay-kubo*), and between a prefix and a proper name (*taga-Galilea*,
  *maka-Diyos*). *Mga Taga-Roma* in book names.
- **Capitals**: *Diyos*, *Panginoon*, *PANGINOON*, *Ama*, *Anak*, *Banal
  na Espiritu*, *Anak ng Tao*, *Kordero ng Diyos*, *Salita* (John 1),
  *Kasulatan*, *Kautusan* (of Moses), *Ebanghelyo*, *Araw ng Pamamahinga*,
  *Paskuwa*, the pronouns of section 4. Lowercase: *propeta*, *pari*,
  *alagad*, *apostol*, *kaharian ng Diyos*, *templo*.
- **Numbers**: Tagalog number words in the text (*labindalawang alagad*,
  *limanlibong tao*, *tatlong daang siko*); digits only where words would
  be long and the English uses digits (*930 taon*, *603,550 lalaki*), with
  a comma for thousands and a full stop for decimals, as the Philippines
  writes them. A list of counts in one verse is uniform. A sentence does
  not begin with digits. Ordinals *una*, *ikalawa*, *ikatlo*, *ikaapat*.
  Spanish number words (*dose*, *singko*) are not used.
- **Clock time**: Literal keeps the source's count (*ikaanim na oras*);
  Balanced and Readable give the modern time (*bandang tanghali*, *mga
  alas-tres ng hapon*), with a decision, as the English does.
- **Dates**: months by number as the Hebrew does at Literal (*unang
  buwan*); Balanced and Readable may add the name where the English does
  (*buwan ng Nisan*).

## 11. Focus, aspect and affixes at each level

Tagalog verbs mark which noun is the focus (*ang*) and the aspect
(completed, ongoing, contemplated). These are grammar, not supplied words,
so Literal does not bracket them; but they shape register, and the levels
use them differently.

- **Focus.** Where the source's subject is the doer, actor focus (*Kumain
  si Jesus ng tinapay*) reads most naturally when the object is indefinite;
  where the object is definite, Tagalog prefers object focus (*Kinain ni
  Jesus ang tinapay*). Follow Tagalog's preference at every level; it is
  not a change of meaning. Literal keeps the source's passive as an
  object-focus verb with the agent in *ng*/*ni* (*Binautismuhan siya ni
  Juan*).
- **Aspect.** The Greek aorist and the Hebrew *wayyiqtol* are completed
  (*sinabi*, *umalis*); the present and imperfect of ongoing action are
  ongoing (*nagtuturo*, *sinasabi*); the future and the Hebrew *yiqtol* of
  the future are contemplated (*sasabihin*). The Greek historic present in
  narrative is completed at every level.
- **Plural verbs.** The old reduplicated plural forms (*nagsiyaon*,
  *nangagsialis*, *nagsipagsisi*) are not used at any level; *mga* and the
  pronoun mark the plural.
- **Heavy affixes.** Readable avoids stacked forms where a plain one
  exists: *pinagpala* is common enough, *ipinagkaloob* becomes
  *ibinigay*, *pakikipagkasundo* may become *pakikipag-ayos* with a
  decision. Causatives in *pa-* (*pinagaling*, *pinatawad*) are ordinary
  and kept.
- **Enclitics and particles.** *nga*, *pa*, *na*, *lamang*, *man*, *kaya*,
  *sana*, *yata* carry meaning; use them where the source's sense needs
  them, not as filler. *lamang* (L, B) and *lang* (R) for "only". *Sana*
  for wishes (*Pagpalain ka sana ng Diyos*).
- **Imperatives.** The plain imperative (*Sumunod ka sa akin*) at every
  level; *Huwag* for prohibitions; *nawa* in blessings and wishes at
  Literal and Balanced (*Sumainyo nawa ang biyaya*), *sana* at Readable.

## 12. Poetry, headings and the Old Testament

- **Lines.** Poetry is set in lines, as `docs/english-style.md` section 10
  describes: mark each break inside a verse with `\q `, following the
  Hebrew accents' division (`python3 scripts/poetry_lines.py` prints it),
  at every level. Tagalog places its own breaks; a verse start is always a
  line start. Tagalog poetry keeps its lines short; do not pad a line to
  match the English.
- **Psalm titles** are verse 1, as in the Hebrew: *Awit ni David* (L, B),
  *Isang awit na isinulat ni David* (R). Musical terms the English
  transliterates are transliterated (*Sela*, *Maskil*, *Miktam*), with the
  English decision's note.
- **The psalmist** says *ako* and speaks to God as *ikaw* (with the span);
  God speaking says *ako*.
- **Old Testament narrative**: the Hebrew *wayyiqtol* chain is joined with
  *at*, *pagkatapos* and *saka* at Literal; Balanced and Readable use
  ordinary connectives (*Kaya*, *Pagkatapos*, *Nang*) and new sentences.
- **Kings and courts**: subjects address the king as *panginoon kong
  hari* (L), *Mahal na Hari* (B, R), call themselves *ang iyong lingkod* at
  Literal only (section 5), and use *po* at B and R; the king says *ako* and
  *ikaw* to subjects.
- **Section headings and summaries.** Where a book's
  `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json` has the
  languages beside English, add `"tl"` beside them as each book is drafted,
  written from Open Word Bible's own Tagalog wording. They are AI drafts
  until reviewed, and never the headings of ABAB, MBB or ASND.

## 12a. Recurring formulas

One form each, in every book; the first record of a passage that uses one
notes it once. `[NG]` stands for `{{divine_name:ng PANGINOON|ni Yahweh}}`,
`[ANG]` for `{{divine_name:ang PANGINOON|si Yahweh}}`, `[SA]` for
`{{divine_name:sa PANGINOON|kay Yahweh}}`.

| Source (English) | Literal | Balanced | Readable |
|---|---|---|---|
| Thus says the LORD (*koh amar YHWH*) | *Ganito ang sabi [NG]* | as L | *Ito ang sinasabi [NG]* |
| declares the LORD (*ne'um YHWH*) | *sabi [NG]* | *ang sabi [NG]* | as B |
| The word of the LORD came to ... | *Dumating ang salita [NG] kay ...* | as L | *Nagsalita [ANG] kay ...* |
| I am the LORD | *Ako [ANG]* | as L | *Ako [ANG]* |
| behold (*hinneh*, *idou*) | *narito* | *tingnan ninyo*, or left out where it only marks attention | left out |
| and it came to pass (*wayehi*) | *At nangyari* | left out, or a time clause (*Nang panahong iyon*) | as B |
| son of man (Ezekiel's address) | *anak ng tao* (lowercase) | as L | *ikaw na tao* |
| answered and said | *sumagot at sinabi* | *sumagot* | as B |
| lifted up his eyes and saw | *itiningin niya ang kaniyang mga mata at nakita* | *tumingin siya at nakita* | *nakita niya* |
| fell on his face | *nagpatirapa siya* | as L | *lumuhod siya at yumuko hanggang lupa* |
| all the days of his life | *sa lahat ng araw ng kaniyang buhay* | *habang siya'y nabubuhay* | *habang siya ay nabubuhay* |
| to this day | *hanggang sa araw na ito* | as L | *hanggang ngayon* |
| Fear not | *Huwag kang matakot* | as L | as L |
| Woe to you | *Sa aba ninyo* | *Kawawa kayo* | as B |
| grace and peace to you | *Biyaya at kapayapaan sa inyo* | *Sumainyo nawa ang biyaya at kapayapaan* | *Pagpalain sana kayo at bigyan ng kapayapaan* |

## 12b. Drafting book by book

Each book is drafted the same way, so the books agree with each other
without a later harmonising pass.

1. **Check the book is free** (`check-book-before-translating` skill) and
   that the English is drafted: Tagalog is drafted from records that
   already have their meaning decisions.
2. **Read this file, the book's section of `docs/tagalog-terms.md`, and the
   book's English terms notes.** The glossary's form is the form; a drafter
   does not choose another spelling of a name or another word for a key
   term in one book.
3. **Draft each record at L, then B, then R**, from the Hebrew or Greek,
   the gloss and the meaning decisions. Keep the English record's verse
   markers, line breaks and quotations (section 2).
4. **Compare each familiar verse with ABAB, MBB and ASND** and rewrite any
   clause that matches (section 1). Do not open them for unfamiliar verses:
   the check is for memory's pull, not a source.
5. **Write the decisions** (section 2): the first use in the book of a
   glossary choice, a name not in the glossary, every setting span that
   differs from the English, every *tayo*/*kami* choice that is not
   obvious, the first *po* of a speaker.
6. **Add new names** (the minor names of genealogies and lists) to the
   book's section of `docs/tagalog-terms.md` in the same pull request, by
   the rules of section 6.
7. **Before the pull request, search the book's Tagalog** for what this
   file excludes. At every level: *Dios*, *datapuwa't*, *sapagka't*,
   *anopa't*, *yaon*, *Jehova*, *kanya*, *nung*, *'di*, *'yan*, *n'yo*,
   *'wag*, *sobra*, *grabe*, Spanish number words, and the reduplicated
   plural verbs (*nangag-*, *nagsi-*). At Literal: *po*, *opo*. At
   Readable: *'y* contractions. A pronoun for God in lowercase outside a
   span where the English has a span, *PANGINOON* outside a `divine_name`
   span, and a `divine_name` span without its marker (except in address)
   are errors too.
8. **Headings and summaries** for the book in Tagalog, from our own text
   (section 12).
9. One pull request per book; `scripts/check.sh` must pass.

## 13. Search

Tagalog is written with spaces, so site search indexes it word by word.
Postgres has no Tagalog stemmer, so search uses `owb_simple`: a word is
found as it is written. Tagalog builds verbs with prefixes, infixes and
reduplication (*sumampalataya*, *sumasampalataya*, *nanampalataya*,
*pananampalataya*), so a search for one form does not find the others.
This does not affect drafting, but a term spelled two ways (*kaniya* /
*kanya*) is two words to search: keep the one spelling this file gives.

## 14. Defaults for the founder to confirm

Each of these decides the wording of thousands of verses. Drafting follows
them as written; the founder confirms or changes each once, and the outcome
is recorded under a "Settled" heading at the top of this file. Changing one
later means revising every book drafted under it, so the earlier they are
confirmed the cheaper.

1. **Language name and code**: `tl`, listed as *Tagalog* in English and
   *Tagalog* as its native name in the footer's language switch.
   Alternative native name: *Filipino*.
2. **YHWH**: *ang PANGINOON* by default, *si Yahweh* as the setting, with
   the case marker and any linker inside the span; *Panginoong DIYOS* for
   *Adonai YHWH*; *ang PANGINOON ng mga hukbo* for *YHWH tsevaot*.
3. **God is *Diyos*** at every level; no setting.
4. **Pronouns for God** capitalised by default (`deity_pronoun`) where the
   English has a span, *Siya*, *Niya*, *Kaniya*, *Ikaw*, *Mo*, *Iyo*; no
   span on *ako*, *ko*, *akin*.
5. **Address**: *ikaw* to God and Jesus from everyone; no respectful
   plural for one person; *po* at Balanced and Readable for speech to
   superiors, never in prayer; *Ginang* for "Woman" at B and R.
6. **Christ**: `{{christos:si Cristo|ang Mesiyas}}`, marker inside the span, by the table in section 8.
7. **Holy Spirit**: *Banal na Espiritu* at every level, rather than
   *Espiritu Santo*.
8. **Baptize**: *bautismuhan*, rather than *binyagan*; *Juan na
   Tagapagbautismo*, rather than *Juan Bautista*.
9. **Priest**: *pari*, rather than *pari*; **steadfast love**: *tapat
   na pag-ibig*; **world**: *sanlibutan*, not *mundo*; **grace**: *biyaya*.
10. **Names**: the Spanish-derived church forms without accents, by the
    rules of section 6.
11. **Level names**: *Literal*, *Balanse*, *Madaling Basahin*.

## 15. Status

A Tagalog rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.
