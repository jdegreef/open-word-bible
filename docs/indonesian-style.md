# Indonesian style guide

How Open Word Bible drafts Indonesian (Bahasa Indonesia, code `id`). It
builds on `docs/english-style.md`, which still covers everything that is not
about wording: sources, one record per sentence, the three levels, decisions
and status. It also builds on each book's terms notes (`docs/john-terms.md`
and the others), whose book-wide choices hold in Indonesian unless this file
says otherwise. `docs/indonesian-terms.md` is the glossary of recurring terms
and names, Genesis to Revelation. Where this file and the founder's
Translation Charter disagree, the Charter wins; fix this file.

**Status: proposed, awaiting a native Indonesian reviewer.** Indonesian is
not yet a reading language: it is not in `data/languages.json`, and no
record has an `id` rendering. `docs/adding-a-language.md` lists what has to
change before the first Indonesian rendering can be validated. Every
Indonesian record will be `ai_draft`. The level names, the forms of address,
the name forms and the key terms below are first proposals; a reviewer is
expected to change some of them. The choices the founder is asked to confirm
before drafting starts are collected in section 13.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Indonesian says that meaning in its
  own way.
- **Never reproduce the wording of a copyrighted Indonesian Bible.** The
  Lembaga Alkitab Indonesia (LAI) owns the two versions most readers know:
  the *Terjemahan Baru* (TB, 1974, and its revision TB2, 2023), read aloud
  in nearly every Protestant and Catholic church, and the *Bahasa Indonesia
  Masa Kini* (BIS, 1985), the common-language version. Also under copyright:
  *Firman Allah Yang Hidup* (FAYH), *Alkitab Yang Terbuka* (AYT), the
  *Terjemahan Sederhana Indonesia* (TSI), the *Indonesian Literal
  Translation* (ILT), the Catholic editions with the deuterocanonical books,
  the *Kitab Suci Torat dan Injil* and the Sacred Name editions. The
  *Terjemahan Lama* (1958) is also treated as protected. Klinkert (1879),
  Leydekker (1733) and Shellabear (1912) are in the public domain, but they
  are classical Malay (*bahasa Melayu Klasik*), not modern Indonesian, so a
  draft that drifts toward them drifts out of the register this file asks
  for (section 3).
- Because TB is what readers hear every Sunday, familiar verses pull drafts
  toward its wording more strongly than in any other language Open Word
  Bible has. Draft from the Greek and the gloss, then **compare every
  well-known verse with TB and BIS and rewrite any sentence that matches
  either for more than a short common phrase.** A short common phrase is a
  term or a fixed collocation that any Indonesian Christian would use
  (*kasih karunia*, *Kerajaan Allah*, *Anak Manusia*, *hari Sabat*, *TUHAN
  semesta alam*), not a clause.
- The conventional forms of names, the names of the books and the church's
  shared vocabulary (sections 6–8) are not wording and may be used.
- Reference Bibles in any language are for comparison and review only,
  never the basis for Open Word Bible wording.
- Never type Greek or Hebrew. A Greek or Hebrew word quoted in a decision is
  copied from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"id": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked once `id`
  is a reading language)**
- Keep the `\v N ` verse markers exactly where the English has them, and the
  `\q ` line breaks of poetry (section 10), in every Indonesian level.
  Indonesian word order (subject, verb, object; the modifier after the noun)
  is close enough to the Greek and to English that a verse's content rarely
  has to cross a marker. Where it must, say so in a `word_order` decision.
- The meaning decisions are shared: do not change them. Indonesian needs
  only its own rendering decisions, with ids `r-id-1`, `r-id-2`, ... counted
  from 1 in each record, `"layer": "rendering"`, `"language": "id"`, the
  `levels` they apply to, and a wording category (word_choice, word_order,
  register, supplied_words, setting_alternative).
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions; the Indonesian words under discussion are
  quoted in it ("\"kasih karunia\" rather than \"anugerah\""). The site tells
  Indonesian readers that notes are in English for now.
- Write an Indonesian rendering decision where Indonesian had to choose and
  a reader might ask why: a word chosen against a familiar church
  alternative (often the TB word), a form of address, a setting span that
  differs from the English one, a word chosen for its Islamic overtones or
  to avoid them (section 9), or a term settled here for the whole book
  (once, where it first appears in a passage). Do not repeat the English
  rendering decisions. Typical density: zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language, so each Indonesian level opens and closes the same
  quotations, in the same order, as the English one.

## 3. The three levels in Indonesian

The level names on the site are proposed as **Harfiah** (Literal),
**Seimbang** (Balanced) and **Mudah Dibaca** (Readable).

The language is **standard modern Indonesian** (*bahasa Indonesia baku*), in
the spelling of the current *Ejaan yang Disempurnakan* (EYD, fifth edition,
2022) and with the words of the *Kamus Besar Bahasa Indonesia* (KBBI). Two
registers are avoided at every level:

- **Classical Malay and old Bible Malay**: *maka* opening a clause, *hatta*,
  *syahdan*, *sebermula*, *adapun*, *bahwasanya*, *tatkala*, *beroleh*,
  *kamu sekalian* as the normal plural, *hamba* as "I", *patik*, *baginda*
  for anyone but a king in a court scene, *-lah* on every imperative, and
  verbs of speaking such as *bersabda* for anyone but a king. These are the
  marks of the old versions and of TB's echoes of them.
- **Colloquial and Jakarta Indonesian**: *nggak*, *enggak*, *gimana*,
  *banget*, *aja*, *udah*, *kok*, *dong*, *deh*, *sih*, the *-in* suffix
  (*bikinin*), *bikin*, *kasih* meaning "give", *sama* meaning "to" or "with",
  *gue* and *lu*. Readable is plain, not spoken.

**Literal (Harfiah, OWB-L).** Follows the Greek order and wording where
Indonesian allows; keeps participles as clauses (*sambil ...*, *setelah ...*),
genitives as a noun after a noun (*anak Daud*, *firman Allah*), the Greek's
repetitions (*dan ... dan ...*) and the historic present (*Yesus berkata*
with no aspect word). Words Indonesian needs but the Greek lacks go in
[square brackets]. What Indonesian grammar requires is not bracketed: the
classifiers *seorang*, *sebuah*, *seekor*; *yang*; *adalah* in a nominal
sentence; the aspect words *telah*, *sudah*, *sedang*, *akan* where the
sense needs them; and *para* for a group of people. Literal may read
stiffly; it must not be wrong Indonesian.

**Balanced (Seimbang, OWB-B).** Careful written Indonesian, the register of
a good public reading in church or of a serious newspaper. Tracks the Greek
closely; no brackets. Church words stay where they are the living word for
the thing (*kasih karunia*, *bertobat*, *Kerajaan Allah*, *imam besar*).

**Readable (Mudah Dibaca, OWB-R).** Plain Indonesian for new and young
readers and for those whose first language is a regional one (Javanese,
Sundanese, Batak, Minahasa, Toraja, Papuan languages...): short sentences,
common words, explained idioms, and what the context implies made explicit
where the English Readable does so, with a decision. Section 11 gives the
Readable rules for affixes and reduplication.

## 4. God, the Lord and the divine name

### God: *Allah*

- *theos* and *Elohim* (of the God of Israel) are **Allah** at every level.
  Indonesian Christians, Protestant and Catholic, have called God *Allah*
  since the first Malay Gospel (1629) and the Leydekker Bible (1733); every
  church Bible in Indonesia uses it, and Indonesian law and practice leave
  it unquestioned. *Allah* is the Arabic word for God, shared with Islam, as
  Arabic-speaking Christians have used it since before Islam.
- **The Malaysian controversy is not Indonesia's.** In Malaysia the use of
  *Allah* in Christian publications in Malay has been the subject of
  government restrictions and court cases (the *Herald* case, decided
  against the church in 2013–2014, and the Jill Ireland case, decided for
  the right to use it in religious education material in 2021). Christians
  in Sabah and Sarawak use *Allah* in their Malay Bible. None of this applies
  to Indonesian, which is a separate standard language with its own law. A
  future Malay (`ms`) edition would need its own decision and its own legal
  check; this file does not make one.
- **The Sacred Name movement.** A small number of Indonesian groups reject
  *Allah* as a name for the God of Israel and use *Elohim* and *Yahweh*
  instead (with their own editions). Open Word Bible keeps *Allah*: it is
  the ordinary Indonesian word for God, not a name, and the meaning of
  *theos* and *Elohim* is "God". The reader who wants the name itself has
  the `divine_name` setting (below), which concerns YHWH only. *Elohim* is
  never a setting.
- A false god or gods: *allah* lowercase (*allah lain*, *allah-allah
  bangsa-bangsa*), or *dewa*, *dewi* where a named pagan deity is meant
  (*dewi Artemis*, *Baal*). Do not write *tuhan-tuhan* for "gods".
- *El* compounds: *Allah Yang Mahatinggi* (*El Elyon*), *Allah Yang
  Mahakuasa* (*El Shaddai*), *Yang Mahakuasa* (*Shaddai* alone), *Allah yang
  kekal* (*El Olam*). The *Maha-* titles are written as one word with the
  root (*Mahatinggi*, *Mahakuasa*, *Mahakudus*), as the EYD writes them.

### Lord: *Tuhan*

- *kyrios* for God or for Jesus, and *Adonai*, are **Tuhan** (capital T) at
  every level. "The Lord Jesus" is *Tuhan Yesus*. "Lord!" in address is
  *Tuhan!* (*Ya Tuhan*, in prayer, at Literal and Balanced).
- *kyrios* or *adon* for a human master is **tuan** (lowercase), and
  *kyrie* to a stranger is *Tuan* in address. Where it is unclear whether a
  speaker means "Lord" or "sir" (John 4; 9:36), follow the English choice
  and its decision.
- "my lord" from a subject to a king is *Tuanku* (L, B) and *Raja* or
  *Baginda* (R) by context (section 5).

### The divine name: *TUHAN* by default, *Yahweh* as the setting

- YHWH is `{{divine_name:TUHAN|Yahweh}}` at every level, in capitals like the
  English "the LORD", which is how Indonesian Bibles have printed it since
  TB. Indonesian has no article and no case, so nothing else needs to go
  inside the span: `{{divine_name:TUHAN|Yahweh}} adalah gembalaku`,
  `firman {{divine_name:TUHAN|Yahweh}}`, `bait {{divine_name:TUHAN|Yahweh}}`.
- *Adonai YHWH* ("Lord GOD") is `Tuhan {{divine_name:ALLAH|Yahweh}}`, with
  *Tuhan* outside the span, as the English writes `Lord {{divine_name:GOD|Yahweh}}`.
  Printing the name as *ALLAH* in capitals where *TUHAN* would repeat the
  word (*Tuhan TUHAN*) is the established Indonesian convention.
- *YHWH Elohim* (Genesis 2–3) is `{{divine_name:TUHAN|Yahweh}} Allah`.
  "The LORD my God" is `{{divine_name:TUHAN|Yahweh}}, Allahku`;
  "the LORD your God" is `{{divine_name:TUHAN|Yahweh}}, Allahmu` (singular)
  or `{{divine_name:TUHAN|Yahweh}}, Allah kalian` (plural, section 5).
- *YHWH tsevaot* is `{{divine_name:TUHAN|Yahweh}} semesta alam` at every
  level, the established Indonesian title, with the span on the name only.
  Readable may say `{{divine_name:TUHAN|Yahweh}} Yang Mahakuasa` where the
  English Readable explains the title, with a decision.
- The short form *Yah* is `{{divine_name:TUHAN|Yah}}`; in *Hallelu Yah* it is
  *Haleluya*, with no span, as the English writes "Hallelujah".
- *Yahweh* is the spelling of the alternative because it is the form
  Indonesian scholarship and the Sacred Name groups both use and readers
  recognise; *Yahwe* (without the h) is seen in some Catholic writing and is
  a reviewer's alternative. *Yehova* and *Yehuwa* are not used.
- A particle such as *-lah* or *-kah* after the span would attach to both
  options; avoid it by rewording (*Dialah TUHAN*, not *TUHANlah*), or write
  it after a hyphen outside the span: `{{divine_name:TUHAN|Yahweh}}-lah`.
- In a New Testament quotation of the Old Testament the Greek has *kyrios*,
  so write *Tuhan* and note the Hebrew original in a decision, as the
  English does (John 1:23).

### Pronouns for God: the `deity_pronoun` setting

Indonesian third-person pronouns have no gender, so *dia* and *-nya* can mean
any person in the sentence. Indonesian spelling (EYD) capitalises every
pronoun that refers to God, and Indonesian Bibles do: *Dia*, *Ia*, *-Nya*,
*Engkau*, *-Mu*, *Kau-*, *Aku*, *-Ku*. In Indonesian the capital is more than
reverence: it is often the only sign of who is meant ("he gave him his
word"). So the capitalised form is the default, as in English, and the
`deity_pronoun` setting lets a reader choose lowercase.

- Spans, written lowercase first (the validator allows only the first
  letter's capital to differ):
  - third person: `{{deity_pronoun:dia|Dia}}`; *ia* is not used for God (see
    below);
  - the enclitic: `firman-{{deity_pronoun:nya|Nya}}`, `kepada-{{deity_pronoun:nya|Nya}}`,
    with the EYD hyphen before the capital;
  - God or Jesus spoken to: `{{deity_pronoun:engkau|Engkau}}`,
    `nama-{{deity_pronoun:mu|Mu}}`, `{{deity_pronoun:kau|Kau}}berikan`
    (the proclitic is joined to the verb);
  - God or Jesus speaking: `{{deity_pronoun:aku|Aku}}`, `umat-{{deity_pronoun:ku|Ku}}`.
    Unlike English "I", which is always capitalised, Indonesian *aku* is not,
    so the first person takes a span too.
- A pronoun at the start of a sentence is written plainly with its capital
  and no span (*Dia berkata kepada mereka*), as in English.
- **The hyphen in the lowercase option.** The EYD writes *firman-Nya* with a
  hyphen and *firmannya* without one. The setting can change only the
  capital, so a reader who chooses lowercase reads *firman-nya*, with a
  hyphen standard spelling would not have. This is accepted as a small cost
  of the setting; the alternative is to let the validator accept
  `{{deity_pronoun:nya|-Nya}}`-style pairs where the hyphen comes and goes
  with the capital (a code change; see section 13).
- Put a span wherever the English has one for the same person; Indonesian
  needs more of them than English, because *-nya*, *-mu* and *-ku* attach to
  nouns, verbs and prepositions (*kasih-Nya*, *mengasihi-Nya*,
  *bersama-Nya*). The English spans on "he/him/his" for figures in a parable
  stay out, as in English.
- One form for "he" referring to God: **Dia**, at every level. Indonesian has
  both *ia* and *dia*; *Ia* is common in TB, but *dia* is the form that can
  stand anywhere in the sentence, and one form keeps the setting and search
  simple. For people, *ia* (subject) and *dia* are both standard at Literal
  and Balanced; Readable uses *dia*.

## 5. Address and speech

Indonesian marks the relation between speaker and hearer in its pronouns
and terms of address. The Greek does not; these are wording choices,
rendering decisions, never meaning decisions. They hold through a book so a
scene does not change relationship from verse to verse.

### "I"

- **God and Jesus** say *Aku* (with the span) at every level.
- **People** say *aku* to equals, to family and in prayer, and in poetry
  (the psalmist: *TUHAN adalah gembalaku*); *saya* when speaking politely to
  a superior, a stranger or a public (a servant to his master, the
  petitioners to Jesus, Paul before Festus). Choose once per speaker in a
  scene and keep it. *Hamba* as "I" ("your servant", the Hebrew humble
  self-reference) is kept only at Literal (*hambamu ini*); Balanced and
  Readable say *saya*, with a decision the first time in a book.
- **The writer of a letter** (Paul, Peter, James, John) says *aku* at
  Literal and Balanced, the voice of a father or brother in the faith, and
  *saya* at Readable, the voice of a letter to a congregation one has not
  met. To be confirmed (section 13).

### "You" singular

- **To God and to Jesus**: *Engkau*, *-Mu*, *Kau-*, with the span (section
  4), at every level, from disciples, petitioners and opponents alike; their
  words show their attitude. Not *Anda*.
- **God and Jesus to one person**: *engkau*, *-mu*, *kau-* at Literal and
  Balanced (*Dosamu sudah diampuni*), *kamu* at Readable.
- **People to each other**: *engkau* or *kamu* between equals and to those
  below (L, B: *engkau*; R: *kamu*); *Tuan*, *Bapak*, *Ibu* to a superior or
  a stranger, used as the pronoun (*Apakah Tuan ...?*, *Ibu, berilah aku
  minum* becomes *Ibu, tolong beri saya minum* at R).
- **To a king**: *Tuanku* (L, B), *Baginda* or *Raja* (R), used as the
  pronoun (*Ya Tuanku Raja, kiranya Tuanku hidup selama-lamanya*).
- **Woman** (*gynai*) as an address: *Perempuan* at Literal, with a
  decision; *Ibu* at Balanced and Readable, which is how Indonesian addresses
  a woman with respect, Jesus's mother included (John 2:4; 19:26).
- **Anda is not used in the Bible text.** It is the impersonal register of
  forms, advertising and the site's interface (`i18n/id.json` will use it),
  and has no place between people in a story.

### "You" plural

- **kalian** at every level. Greek distinguishes "you" singular and plural,
  and Indonesian *kamu* is both; *kalian* is the standard plural (KBBI), and
  it is how Indonesians speak to a group. With it go *kalian* as possessor
  (*Bapa kalian*, not *Bapamu*, which reads as singular) and *kepada
  kalian*.
- *kamu sekalian* is the formal plural of a sermon or a speech; it is not
  used, since repeated through a chapter it is heavy and old-fashioned.
- **No `plural_you` setting.** Spanish has one because Spain and the
  Americas use different plural pronouns. Indonesian has no such regional
  split: *kalian* is understood and used everywhere Indonesian is spoken.
  If a reviewer finds *kalian* too familiar for Jesus's teaching or for
  God's speech to Israel, the fix is a different default, decided once,
  not a setting.
- **We**: Indonesian distinguishes inclusive *kita* (the hearers included)
  from exclusive *kami* (not included), and the Greek and Hebrew do not.
  Every "we" is a choice: God's "Let us" (Genesis 1:26) is *Kita*; the
  eyewitnesses of John 1:14 and 1 John 1:1 are *kami*; Paul with his readers
  is *kita*, Paul and his companions *kami*. Where the choice is not obvious,
  record it in a decision. *Kami* takes no deity_pronoun span; *Kita* for God
  in Genesis 1:26, 3:22 and 11:7 does (`{{deity_pronoun:kita|Kita}}`), as the
  English capitalises "Us".

### Brothers and sisters

- *adelphoi* meaning believers is **saudara-saudara**, with **no gender
  span**. Indonesian *saudara* means a sibling of either sex, and
  *Saudara-saudara* is how a speaker addresses a mixed audience, so the
  inclusive meaning needs no second option. *Saudara-saudari* (with the
  feminine *saudari*) is a newer, marked form and is not used.
- In address: *Saudara-saudaraku* (L, B), *Saudara-saudara* (R); "beloved
  brothers": *saudara-saudaraku yang kukasihi* (L, B), *saudara-saudara yang
  saya kasihi* (R, with the letter writer's *saya*).
- A specific male brother is *saudara laki-laki*, a sister *saudara
  perempuan*, where the sex matters (Mark 6:3).

### Verbs of speaking

- God speaks: **berfirman** at every level, and his word is *firman*.
- Jesus speaks: **berkata** at every level, as everyone else does; not
  *bersabda*, which is a king's word in old Malay and sounds archaic.
  *menjawab*, *bertanya*, *menegur* where the Greek has them.
- A quotation is introduced with a comma, as the EYD writes it: *Yesus
  berkata, "..."* A colon is used only before a long, formal speech or a
  letter.

## 6. Names

### Principles

Open Word Bible uses **the established forms of the Indonesian church**:
the forms in common use by Protestants and Catholics alike, which
Indonesian Christians have read for two generations and which the KBBI and
the press use for biblical people and places. Indonesia, unlike Vietnam and
Korea, has one shared ecumenical tradition of names, so no Protestant or
Catholic choice is needed. The names are not wording and may be used.

How to decide a name:

1. **An established church form exists** (it is the form most Indonesian
   Christians would recognise): use it, even where it is far from the
   Hebrew or Greek (*Yesus*, *Musa*, *Salomo*, *Yohanes*, *Petrus*,
   *Babel*). Reconstructed Hebrew forms (*Yeshua*, *Moshe*, *Yokhanan*) are
   not used; they would make the most familiar names unrecognisable.
2. **The church form and the Islamic form differ**: use the church form
   (*Yesus*, not *Isa*; *Abraham*, not *Ibrahim*; *Salomo*, not *Sulaiman*;
   *Ishak*, not *Ishaq*; *Ismael*, not *Ismail*; *Elia*, not *Ilyas*;
   *Yunus* is shared). Where the two coincide (*Musa*, *Daud*, *Nuh*,
   *Yakub*, *Yusuf*, *Ayub*, *Harun*, *Hawa*, *Yunus*), keep the shared form:
   avoiding it would be its own kind of polemic. Section 9 gives the reasons.
3. **Two church forms compete** (an older and a newer spelling): use the one
   in current spelling (EYD: *sy*, not *sj*; *y*, not *j*; *c*, not *tj*;
   *kh* for the Hebrew *het* and the Greek *chi*) and closer to the source,
   and record it in a decision the first time.
4. **No established form** (the minor names of Chronicles, Ezra and
   Nehemiah): transliterate from the Hebrew or the Greek by the patterns of
   the established forms: Hebrew *y* > *y*, *sh* > *sy*, *ts* > *s* (*z* where
   an established name has it), *het* and *kaf* without dagesh > *kh*, final
   *-ah* kept; Greek *ph* > *f*, *th* > *t*, *ch* > *kh*, *-os* > *-us*,
   *-ēs* > *-es*, *ou* > *u*. Note the new form in a decision where it first
   appears in the book, and add it to `docs/indonesian-terms.md`.
5. **One person, one form, through the whole Bible.** A name shared by
   several people keeps one spelling (both Yohanes; all the Yakobus). An Old
   Testament name quoted in the New Testament keeps its Old Testament form
   (*Elia*, *Yesaya*, *Henokh*), not a form taken from the Greek.

### The common forms

Jesus and the Gospels: *Yesus*, *Maria*, *Yusuf*, *Yohanes* (the Baptist and
the apostle), *Yohanes Pembaptis*, *Simon Petrus*, *Petrus*, *Andreas*,
*Yakobus* (the apostles; the Old Testament patriarch is *Yakub*), *Zebedeus*,
*Filipus*, *Bartolomeus*, *Tomas*, *Matius*, *Natanael*, *Yudas Iskariot*,
*Nikodemus*, *Lazarus*, *Marta*, *Maria Magdalena*, *Pilatus*, *Kayafas*,
*Hanas*, *Barabas*, *Herodes*, *Zakharia*, *Elisabet*, *Simeon*, *Hana*.
Acts and the letters: *Paulus*, *Saulus*, *Barnabas*, *Stefanus*, *Silas*,
*Timotius*, *Titus*, *Apolos*, *Priskila*, *Akwila*, *Kornelius*,
*Gamaliel*, *Feliks*, *Festus*, *Agripa*, *Febe*, *Tikhikus*, *Onesimus*,
*Filemon*. Places: *Yerusalem*, *Galilea*, *Yudea*, *Samaria*, *Nazaret*,
*Betlehem*, *Kapernaum*, *Betsaida*, *Betania*, *sungai Yordan*, *Roma*,
*Antiokhia*, *Efesus*, *Korintus*, *Filipi*, *Tesalonika*, *Atena*,
*Damsyik*, *Kaisarea*, *Siprus*, *Aleksandria*. Peoples: *orang Yahudi*,
*orang Samaria*, *orang Yunani*, *orang Roma*, *orang Farisi*, *orang
Saduki*, *orang Lewi*, *orang Israel*. The Old Testament forms are in
`docs/indonesian-terms.md`.

## 7. Words for the whole Bible

The sixteen key terms of `data/key_terms.json` keep one Indonesian word at
every level (with the same exceptions as the English: Readable may say
"good news" for "gospel", and a sense such as "being right with God" at
Readable needs a decision). The Old Testament terms after them are settled
for every book.

| Greek / Hebrew (English) | Indonesian | Why |
|---|---|---|
| grace (*charis*) | **kasih karunia** | Key term. The common church term, distinct from *kasih* (love) and *anugerah* (a gift, a favour). *rahmat* is the Catholic word for grace and the Islamic word for mercy; it is not used for either, so the two terms stay apart. |
| glory (*doxa*); glorious | **kemuliaan**; *mulia* | Key term. |
| glorify (*doxazō*) | **memuliakan**; *dimuliakan* | Key term; the same root as *kemuliaan*, as the Greek has. |
| truth (*alētheia*) | **kebenaran** | Key term. *benar* for "true" as an adjective of statements, *sejati* for "true" as "real" (*terang yang sejati*). See righteousness. |
| righteousness (*dikaiosynē*) | **kebenaran** (L, B); R may say *hidup benar di hadapan Allah*, *dibenarkan oleh Allah*, with a decision | Key term. Indonesian has one noun for both truth and righteousness; Indonesian Bibles have always used *kebenaran* for both. The alternative is *keadilan* where the sense is God's just judging (Acts 17:31) — a meaning decision says which sense is meant. To be confirmed (section 13). |
| justify (*dikaioō*) | *membenarkan* (L, B); *menyatakan benar* (R) | Same root as *kebenaran*, which keeps Paul's argument visible. |
| faith (*pistis*) | **iman** | Key term. *kesetiaan* where a meaning decision says "faithfulness". |
| believe (*pisteuō*) | **percaya**; *percaya kepada* (*eis*) | Key term; the verb at every level, never *beriman* (which reads as "be religious"). |
| joy (*chara*) | **sukacita** | Key term. *bersukacita* for the verb. |
| salvation (*sōtēria*); save | **keselamatan**; *menyelamatkan*, *diselamatkan*, *selamat* | Key term. |
| gospel (*euangelion*) | **Injil** (L, B); **kabar baik** (R) | Key term, levels as the English. *Injil* is capitalised. *kabar baik* is also used at B where the English says "good news" (Mark 1:1 context). |
| world (*kosmos*) | **dunia** | Key term. *bumi* for the earth. |
| eternal (*aiōnios*); eternal life | **kekal**; *hidup yang kekal* (L), *hidup kekal* (B, R) | Key term. |
| sign (*sēmeion*) | **tanda** | Key term. Never *mukjizat* alone, which means "miracle"; Readable may say *tanda ajaib* with a decision. |
| mystery (*mystērion*) | **rahasia** | Key term. *misteri* is a loanword with a detective-story sense. |
| YHWH | `{{divine_name:TUHAN\|Yahweh}}` | Key term (Hebrew). Section 4. |
| steadfast love (*hesed*) | **kasih setia** | The established term: love and loyalty in one word. Readable may say *kasih yang setia* with a decision. |
| faithfulness (*emunah*); truth (*emet*) | *kesetiaan*; *kesetiaan* or *kebenaran* by a meaning decision | *emet* paired with *hesed* is *kasih setia dan kesetiaan*. |
| covenant (*berit*; *diathēkē*) | **perjanjian** | Every level, both testaments. *wasiat* only where the Greek means a will (Hebrews 9:16–17). |
| holy; sanctify; the saints | *kudus*; *menguduskan*; *orang-orang kudus* (L, B), *umat Allah* (R) | |
| justice (*mishpat*); righteousness (*tsedaqah*) | *keadilan*; *kebenaran* | The pair *keadilan dan kebenaran*. |
| peace (*eirēnē*; *shalom*) | **damai sejahtera** (L, B); **damai** (R) | Key term (*eirēnē*). *damai sejahtera* carries *shalom*'s wholeness; *damai* is the common core at every level, so the term can be followed. The greeting *eirēnē hymin*: *Damai sejahtera bagi kalian* (L, B), *Damai bagi kalian* (R); not *Salam*, which is a different greeting. |
| sin; transgression; iniquity | *dosa*; *pelanggaran*; *kesalahan* or *kejahatan* | |
| atone (*kipper*); atonement | *mengadakan pendamaian* (L, B); *menghapus dosa* (R) | |
| redeem; redeemer (*go'el*) | *menebus*; *penebus* | |
| repent; repentance | *bertobat*; *pertobatan* | The church word (from Arabic, shared with Islam). |
| forgive | *mengampuni* | |
| law (*torah*; *nomos*, the Law of Moses) | **hukum Taurat** (L, B); *hukum Taurat* or *hukum Musa* (R) | *Taurat* is the Indonesian name of the Torah. Lowercase *hukum* for law in general (Romans 7:23). *torah* as "teaching" (Proverbs) is *ajaran*. |
| the Law and the Prophets | *kitab Taurat dan kitab para nabi* | |
| prophet | *nabi*; *para nabi* | |
| priest; high priest; Levites | *imam*; *imam besar*; *orang Lewi* | *imam* is the church word for priest (and the Islamic word for a prayer leader); context makes it clear. |
| sacrifice; offering | **korban**; *persembahan* | Not *kurban*, the Idul Adha spelling. |
| burnt offering; sin offering; guilt offering; peace offering; grain offering | *korban bakaran*; *korban penghapus dosa*; *korban penebus salah*; *korban persekutuan*; *korban sajian* | *korban persekutuan* for *shelamim* is uncertain; the alternative is *korban keselamatan*. |
| altar | *mezbah* | |
| tabernacle; tent of meeting; ark of the covenant | *Kemah Suci*; *Kemah Pertemuan*; *tabut perjanjian* | |
| temple (*hieron*; *naos*; *bayit*, *hekhal*) | *Bait Allah* (L, B), *rumah Allah* (R); *bait {{divine_name:TUHAN\|Yahweh}}* | "the house of the LORD" keeps *bait*; *hieron* as the courts: *halaman Bait Allah* (B, R). |
| synagogue | *sinagoge* (L, B); *rumah ibadat orang Yahudi* (R) | |
| church, assembly (*ekklēsia*) | *jemaat* (a congregation, L, B, R); *gereja* where the whole body is meant (B, R) | |
| elder; overseer; deacon | *penatua*; *penilik jemaat*; *diaken* | Jewish elders: *tua-tua*. |
| apostle; disciple | *rasul*; *murid* | |
| scribes; Pharisees; Sadducees | *ahli Taurat* (L, B), *guru agama Yahudi* (R); *orang Farisi*; *orang Saduki* | |
| tax collectors; sinners | *pemungut cukai* (L, B), *penagih pajak* (R); *orang berdosa* | |
| Gentiles, nations (*ethnē*; *goyim*) | *bangsa-bangsa* (L); *bangsa-bangsa lain*, *orang bukan Yahudi* (B, R) | Never *orang kafir* (section 9). |
| angel; demon; unclean spirit | *malaikat*; *setan* (L), *roh jahat* (B, R); *roh najis* (L, B), *roh jahat* (R) | |
| devil; Satan | *Iblis*; *Satan* | *Iblis* (capitalised) for *diabolos*; *Satan* for *satanas*. Lowercase *setan* is the demon word above. |
| heaven; sky | *surga*; *langit* | *kerajaan surga* for "kingdom of heaven". |
| Gehenna; Hades; Sheol | *Gehena* (L), *neraka* (B, R); *Hades* (L), *dunia orang mati* (B, R); *Syeol* (L), *dunia orang mati* (B, R) | |
| Holy Spirit; spirit | *Roh Kudus*; *Roh* (God's), *roh* (other); *ruakh* as wind or breath: *angin*, *napas* | |
| soul (*nephesh*; *psychē*) | *jiwa*; *nyawa* (life that can be lost); *diri* (self) | By meaning decision. |
| heart | *hati* | Indonesian *hati* is the seat of feeling and will, as the Hebrew *lev*. |
| flesh (*sarx*, Paul's moral sense) | *daging* (L); *keinginan manusia yang berdosa*, *tabiat lama* (B, R) by the meaning decision | |
| Son of Man; Son of God; Son of David | *Anak Manusia*; *Anak Allah*; *Anak Daud* | Titles, capitalised, never under the gender setting. |
| kingdom of God; of heaven | *Kerajaan Allah*; *Kerajaan Surga* | |
| Lamb of God | *Anak Domba Allah* | |
| the Word (John 1) | *Firman* | Every level, capitalised as a person. |
| Christ | `{{christos:Kristus\|Mesias}}` | Section 8. |
| Messiah (*Messias*, John 1:41; 4:25) | *Mesias* | Plainly, no setting. |
| baptize; John the Baptist | *membaptis*; *Yohanes Pembaptis* | |
| cross; crucify | *salib*; *menyalibkan* | |
| resurrection; rise | *kebangkitan*; *bangkit* | |
| love (*agapē*; *agapaō*) | *kasih*; *mengasihi* | *cinta* for the Song of Songs and human love. |
| mercy (*eleos*); compassion (*rahamim*) | *belas kasihan* | |
| hope | *pengharapan* (L, B); *harapan* (R) | |
| wisdom; knowledge | *hikmat*; *pengetahuan* | *hikmat* is the church word for divine wisdom; *kebijaksanaan* is everyday wisdom. |
| fear of the LORD | *takut akan {{divine_name:TUHAN\|Yahweh}}* | A fixed phrase; *akan* here is not archaic. |
| blessed (*makarios*); bless (*barak*, *eulogeō*) | *berbahagialah* (L), *berbahagia* (B), *bahagia* (R); *memberkati* | |
| woe | *celakalah* | |
| Amen; Hallelujah; Hosanna | *Amin*; *Haleluya*; *Hosana* | |
| Truly I tell you (*amēn legō hymin*) | *Amin, Aku berkata kepada kalian* (L); *Sesungguhnya Aku berkata kepada kalian* (B); *Aku mengatakan yang sebenarnya kepada kalian* (R) | One decision per passage. John's doubled *amēn*: *Amin, amin* (L), *Sesungguhnya, sesungguhnya* (B). |
| slave (*doulos*; *ʿeved*) | *budak* (L); *hamba* (B, R) | As the English: *budak* at every level where slavery itself is the point. *hamba Allah*, *hamba {{divine_name:TUHAN\|Yahweh}}* for God's servants at every level. |
| Sabbath; Passover; Pentecost | *hari Sabat*; *Paskah*; *Pentakosta* | |
| Feast of Booths; Unleavened Bread | *Hari Raya Pondok Daun*; *Hari Raya Roti Tidak Beragi* | |
| Rabbi; Teacher | *Rabi*; *Guru* | |

## 8. Reader settings in Indonesian

Settings change wording, never meaning, exactly as in English.

- `divine_name`: `{{divine_name:TUHAN|Yahweh}}`, and `Tuhan {{divine_name:ALLAH|Yahweh}}`
  for *Adonai YHWH* (section 4).
- `deity_pronoun`: every pronoun for God or Christ, lowercase first,
  capitalised second, including *aku* and *-ku* (section 4).
- `christos`: `{{christos:Kristus|Mesias}}` where the English has a
  christos span. With the name, where the English has `Jesus {{christos:Christ|the Messiah}}`,
  Indonesian writes `Yesus {{christos:Kristus|Sang Mesias}}` at Balanced and
  Readable and `Yesus {{christos:Kristus|Mesias}}` at Literal; *Sang* is the
  Indonesian title particle that does the work of "the". Check that both
  options read naturally with what follows (*Kristus Yesus* / *Mesias Yesus*
  in Paul's order: `{{christos:Kristus|Mesias}} Yesus`).
- `gender`: an inclusive default where the original means men and women,
  with the traditional form as the alternative. Indonesian needs it rarely:
  *orang*, *manusia*, *setiap orang*, *siapa pun*, *saudara-saudara*, *anak-anak*
  and every pronoun are already inclusive, and get no span. Spans appear
  where Indonesian really has two ways of saying it:
  `{{gender:orang|laki-laki}}` for *anēr* meaning people in general,
  `{{gender:anak-anak|anak-anak laki-laki}}` for *huioi* where sons and
  daughters are meant, `{{gender:nenek moyang|bapa leluhur}}` for "fathers"
  as ancestors. Never for God, Christ or named men. A rendering decision
  (setting_alternative) records a difference from the English the first time
  in a passage: most English gender spans have no Indonesian counterpart.
- `units`: metric by default, the original unit as the alternative, as in
  every language but English: `{{units:sekitar tiga kilometer|lima belas stadia}}`.
  Literal keeps the original unit with no span. Coins: the value in wages by
  default and the coin as the alternative (`{{units:upah sehari|satu dinar}}`).
  This differs from the English (US units) and needs a rendering decision
  the first time in a passage. The units: *hasta* (cubit, about 45 cm;
  Ezekiel's long cubit about 53 cm), *jengkal* (span), *syikal*, *talenta*,
  *mina*, *dinar* (not *dirham*, the Islamic coin word), *drakhma*, *efa*,
  *gomer*, *bat*, *sukat*, *stadia*, *mil*.
- `plural_you` is Spanish only; Indonesian has none (section 5).
- A setting span holds no quotation marks (`owb/markup.py` checks).

## 9. Arabic-derived vocabulary and Islamic usage

About nine in ten Indonesians are Muslim, and much of Indonesian religious
vocabulary came through Arabic and is shared by Muslims and Christians:
*Allah*, *nabi*, *rasul*, *malaikat*, *iman*, *imam*, *doa*, *kitab*,
*mukjizat*, *ibadah*, *hikmat*, *kudus*, *jemaat*, *kubur*, *bertobat*,
*syukur*, *najis*, *Taurat*, *Injil*, *Mazmur*... Others came through Sanskrit
(*dosa*, *surga*, *neraka*, *puasa*), Portuguese (*gereja*, *misa*) or
Dutch (*diaken*, *pendeta*). The rules:

1. **Use the church's own vocabulary, whatever its origin.** Most of it is
   Arabic-derived, and replacing it with invented or Sanskrit-derived words
   to make the text sound "less Islamic" would make it sound foreign to the
   readers it is for. *Allah*, *nabi*, *malaikat*, *iman* stay.
2. **Do not import Islamic technical terms where the church has its own.**
   Not *Isa* or *Isa Almasih* (*Yesus*, *Kristus*), *Al-Masih* (*Mesias*),
   *Ruhul Kudus* (*Roh Kudus*), *Ibrahim*, *Sulaiman*, *Nabi Isa*; not
   *salat* or *sembahyang* (*berdoa*), *wudu* (*membasuh*), *kurban*
   (*korban*), *pahala* (*upah*), *amal* (*perbuatan*), *syariat* (*hukum*),
   *akhirat* (*dunia yang akan datang*), *hari kiamat* (*hari penghakiman*,
   *hari Tuhan*), *syahid* (*martir*, *saksi*), *ulama* (*ahli Taurat*),
   *jihad*, *masjid*, *dirham*. Each would pull the reader's mind to Islamic
   practice and change what the text means to them.
3. **Avoid the words that Indonesian uses to draw the line between
   religions.** *kafir* ("infidel") is not used for Gentiles or unbelievers:
   *bangsa-bangsa lain*, *orang yang tidak percaya*, *orang yang tidak
   mengenal Allah*. *halal* and *haram* are not used for clean and unclean:
   *tahir* and *najis* (L, B), *bersih* and *tidak bersih* in God's sight (R).
4. **Shared words keep their biblical sense.** Where a word is shared but
   its Islamic sense differs (*nabi*, *rasul*, *kitab*, *wahyu*, *Injil*),
   the context gives the Christian sense; no footnote is needed unless the
   English has one.
5. **No polemic, no imitation.** The wording is not chosen to answer or
   contradict Islam, and not chosen to imitate Qur'anic style for Muslim
   readers. Indonesian law protects religions from insult (the blasphemy
   provisions of the criminal code); a faithful translation of the text, in
   the church's ordinary vocabulary, is what the law and readers expect. A
   decision that turns on an Islamic overtone says so plainly, in neutral
   terms.

## 10. Spelling, punctuation and typography

- **Spelling**: EYD (fifth edition) and KBBI. *Mukjizat*, not *mujizat*;
  *nasihat*; *napas*; *sekadar*; *praktik*; *apotek*. Where TB's spelling
  differs from the current KBBI (*mujizat*, *nafas*), follow KBBI.
- **Quotation marks**: write straight double quotes `"` for the outer
  quotation and straight single quotes `'` for one inside it, exactly as
  English does; the site curls them into “ ” and ‘ ’, the Indonesian marks.
  A quotation that runs over several sentences opens in the first record and
  closes in the last, as in English. The closing mark follows the full stop,
  comma, question or exclamation mark: *Yesus berkata, "Ikutlah Aku."*
  Indonesian has almost no apostrophes; do not write one (the quotation
  finder reads a straight `'` before a letter as an apostrophe).
- **Capitals**: *Allah*, *Tuhan*, *TUHAN*, *Bapa*, *Anak*, *Roh Kudus*, *Anak
  Manusia*, *Anak Domba Allah*, *Firman* (John 1), *Kitab Suci*, *Kerajaan
  Allah*, *Bait Allah*, *Kemah Suci*, *Injil*, *Taurat*, *hari Sabat*,
  *Paskah*, the pronouns of section 4. Lowercase: *orang Farisi* (but
  *Farisi* capitalised as a name), *nabi*, *imam*, *murid*, *rasul*.
- **Hyphens**: reduplication always takes a hyphen (*orang-orang*,
  *murid-murid*, *berkali-kali*); the capitalised pronouns for God take one
  (*kasih-Nya*); otherwise clitics are joined (*rumahku*, *kaulihat*,
  *bukunya*). *di-* as a passive prefix is joined (*dibaptis*), *di* as a
  preposition is separate (*di Yerusalem*); likewise *ke*, *dari*.
- **Numbers**: as the EYD: a number that can be written in one or two words
  is written in words (*dua belas murid*, *lima ribu orang*, *tiga ratus
  hasta*); others in digits (*930 tahun*, *603.550 orang*), with a full stop
  for thousands and a comma for decimals. A list of counts in one verse is
  uniform: all digits if any needs digits. A sentence does not begin with
  digits. Ordinals *ketiga*, *keempat*; *pertama* for first.
- **Clock time**: Literal keeps the Greek count (*jam keenam*); Balanced and
  Readable give the modern time (*sekitar pukul dua belas siang*), with a
  decision, as the English does.
- **Dates**: months by number as the Hebrew does at Literal (*bulan
  pertama*); Balanced and Readable may add the name where the English does
  (*bulan Nisan*).

## 11. Affixes and reduplication at each level

Indonesian builds meaning with affixes and doubling. They are grammar, not
supplied words, so Literal does not bracket them; but they shape register,
and the levels use them differently.

- **Passive and active.** Indonesian narrative uses the object-focus
  passive (*di-*, *ter-*, and the pronoun passive *kaulihat*, *kuberikan*)
  far more than English; it is natural, not a Greek imitation. Literal
  follows the Greek voice. Balanced and Readable choose the voice that reads
  naturally; Readable avoids a chain of passives with *oleh* (*dibawa oleh
  ... diserahkan oleh ...*) and names the agent first.
- **Heavy affixes.** Readable avoids stacked forms where a plain one exists:
  *mendamaikan* over *memperdamaikan*, *dihadapkan* over *diperhadapkan*,
  *membuat jadi kudus* never (*menguduskan* is common enough). *-kan*
  and *-i* keep their meanings (*menyerahkan* hand over, *menyerahi* entrust
  with); Readable chooses the commoner verb rather than the precise affix
  pair.
- **ber- and ter-**: *bersukacita*, *bertobat*, *berdoa* at every level. The
  accidental *ter-* (*tertidur*, *terjatuh*) is natural and kept.
- **Plural.** Indonesian marks plurality only where needed. With a number or
  a quantifier no doubling: *dua belas murid*, *banyak orang*, *semua
  bangsa* (never *banyak orang-orang*). *para* for a group of people with a
  role (*para murid*, *para imam*, *para nabi*). Reduplication where the
  Greek plural matters and nothing else shows it (*murid-murid-Nya* at L,
  *para murid-Nya* at B and R).
- **Expressive reduplication** (*berjalan-jalan*, *pelan-pelan*,
  *sungguh-sungguh*, *berkali-kali*) is standard and may be used at every
  level where the Greek has the sense. Colloquial doubling (*pagi-pagi
  banget*) is not.
- **-lah, -kah, pun.** *-lah* softens or stresses an imperative (*Pergilah*);
  Literal and Balanced use it where the Greek imperative is solemn or
  repeated, Readable uses the bare verb or *tolong*, *silakan*, *ayo* where
  that is how the command would be said. *-kah* marks a question at L and B
  (*Engkaukah ...?*); Readable may use *apakah* or intonation. *pun* is
  written separately (*siapa pun*) except in the fixed words (*meskipun*,
  *walaupun*).

## 12. Poetry, headings and the Old Testament

- **Lines.** Poetry is set in lines, as `docs/english-style.md` section 10
  describes: mark each break inside a verse with `\q `, following the
  Hebrew accents' division (`python3 scripts/poetry_lines.py` prints it),
  at every level. Indonesian places its own breaks; a verse start is always a
  line start. Indonesian poetry keeps its lines short; do not pad a line to
  match the English.
- **Psalm titles** are verse 1, as in the Hebrew: *Mazmur Daud* (B), *Lagu
  pujian karangan Daud* (R); Literal keeps the Hebrew's words (*[Sebuah]
  mazmur Daud*). Musical terms the English transliterates are transliterated
  (*Sela*, *Maskil*, *Miktam*), with the English decision's note.
- **The psalmist** says *aku* and speaks to God as *Engkau* (with the span);
  God speaking says *Aku*.
- **Old Testament narrative**: the Hebrew *wayyiqtol* chain is joined with
  *dan*, *lalu* and *kemudian* at Literal (not the old *maka*, section 3);
  Balanced and Readable use ordinary connectives and new sentences.
- **Kings and courts**: subjects say *Tuanku* (L, B) and call themselves
  *hamba* at Literal only (section 5); the king says *aku* (L, B), *saya* is
  not used by kings, and *kamu* (R) or *engkau* (L, B) to subjects.
- **Section headings and summaries.** Where a book's `data/headings/<BOOK>.json`
  or `data/summaries/<BOOK>.json` has the languages beside English, add `"id"`
  beside them once Indonesian is a reading language, written from Open Word
  Bible's own Indonesian wording. They are AI drafts until reviewed, and
  never the headings of TB or BIS.

## 13. For the founder to confirm before drafting

Each of these decides the wording of thousands of verses. They are proposals
until confirmed; record the outcome under a "Settled" heading here, as the
Vietnamese and Korean briefs do.

1. **YHWH**: `{{divine_name:TUHAN|Yahweh}}` by default, *Tuhan ALLAH* for
   *Adonai YHWH*, *TUHAN semesta alam* for *YHWH tsevaot*; alternative
   spelling *Yahwe*.
2. **God is *Allah*** at every level, with no setting, and the Malaysian
   question left to a future Malay edition.
3. **Pronouns for God** capitalised by default (`deity_pronoun`), including
   *Aku* and *-Ku*; *Dia*, never *Ia*, for God; and whether the lowercase
   option should drop the hyphen (*firmannya*), which needs a validator
   change to accept a span whose options differ in a leading hyphen.
4. **Plural "you" is *kalian*** at every level; no `plural_you` setting.
5. **Address**: *engkau* (L, B) / *kamu* (R) to one person from God and
   Jesus; *Engkau* to God and Jesus from everyone; *Ibu* for "Woman" at B and
   R; no *Anda* in the text.
6. **Letter writers** say *aku* (L, B) and *saya* (R).
7. **Truth and righteousness** both *kebenaran*, as Indonesian Bibles have
   it, or a distinct word for one of them.
8. **Brothers**: *saudara-saudara* with no gender span.
9. **Christ**: `{{christos:Kristus|Mesias}}`, `Yesus {{christos:Kristus|Sang Mesias}}`.
10. **Speech verbs**: *berfirman* for God, *berkata* for Jesus.
11. **Names**: the established church forms, with the five rules of section
    6, and church forms over Islamic forms where they differ.
12. **Level names**: *Harfiah*, *Seimbang*, *Mudah Dibaca*.

## 14. Status

An Indonesian rendering added to a record does not change its status.
Nothing is marked reviewed by an AI.

## 15. Search

Indonesian is written with spaces, so site search indexes it word by word.
Postgres ships an Indonesian Snowball stemmer, which strips the particles
(*-lah*, *-kah*, *-pun*), the possessives (*-ku*, *-mu*, *-nya*) and the
common prefixes and suffixes (*meN-*, *ber-*, *di-*, *ter-*, *-kan*, *-i*,
*-an*), so *mengasihi* finds *kasih* and *keselamatan* finds *selamat*
(`docs/adding-a-language.md`). This does not affect drafting, but a term
spelled two ways (*mukjizat* / *mujizat*) is two words to search: keep the
KBBI spelling throughout.
