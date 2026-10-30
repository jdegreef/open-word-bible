# Spanish review checklist

Where a native Spanish reviewer starts. Every book of the Bible is drafted in
Spanish, and every record is `ai_draft`. This page puts first the choices
that decide wording in the most verses, so that a reviewer settles each one
once instead of meeting it verse by verse.

How to use it:

1. Work through **Settle these first** (section 2) before reading passages.
   Each item decides wording in many verses, often in many books. Agree with
   the choice as drafted, or name the wording you want instead.
2. Then go through the **Recurring uncertain choices** (section 3). These are
   choices the drafters marked uncertain again and again. The full list of
   284 uncertain Spanish decisions, with links, is
   [es-uncertain.md](es-uncertain.md).
3. Settle the **Known inconsistencies** (section 4), where the books do not
   agree with each other, and read the **Passages to read closely**
   (section 5).

To change a settled choice, edit the terms doc that records it and revise
every passage drafted under it, in every book. The docs say so themselves:
"If a choice here changes, every passage drafted under it is revised."
Records stay `ai_draft` until a named human reviewer approves them. Nothing
here, and no drafter, marks a record reviewed.

Spanish has no style guide of its own. Its rules are spread across the terms
docs below, and the drafters were told to follow "the Spanish already in
`content/`". Short names for the docs used on this page:

- **NT**: `docs/nt-spanish-swahili-terms.md` (sections "Recurring terms",
  "Spanish")
- **Pent**: `docs/pentateuch-fr-es-sw-terms.md`
- **JosRuth**: `docs/joshua-ruth-five-languages-terms.md`
- **Sam**: `docs/samuel-five-languages-terms.md`
- **KgsChr**: `docs/kings-chronicles-five-languages-terms.md`
- **PsPr**: `docs/psalms-proverbs-five-languages-terms.md`
- **IsaJerEzr**: `docs/isaiah-jeremiah-ezra-five-languages-terms.md`, section
  "Spanish"
- **NehSong**: `docs/nehemiah-to-song-five-languages-terms.md`, section
  "Spanish"
- **LamTwelve**: `docs/lamentations-ezekiel-daniel-twelve-five-languages-terms.md`,
  section "Spanish"

L, B and R are the Literal, Balanced and Readable levels. The counts are
rough. They give the number of Spanish records (usually one verse each) that
contain the wording, found by searching `content/`.

## 2. Settle these first

### Names of God and setting spans

- [ ] **The divine name.** The default is `{{divine_name:el SEÑOR|Yahvé}}`,
  in capitals like the English "the LORD", and the reader setting gives
  *Yahvé*. The span takes in the article and its contraction (`del SEÑOR|de
  Yahvé`, `al SEÑOR|a Yahvé`, `El SEÑOR|Yahvé` at the start of a sentence).
  YHWH addressed directly is `{{divine_name:SEÑOR|Yahvé}}`, with no "oh".
  Alternatives a reviewer may prefer: *Jehová* (the Reina-Valera tradition),
  *Yahveh*, or *el Eterno*. About 5,900 verses in 37 books. Pent "The names of
  God"; NehSong "Settings recap".
- [ ] **deity_pronoun spans.** God's and Jesus's free pronouns get spans,
  lowercase by default and capitalised in the alternative: *mí, me, mi, te,
  tú, ti, tu, él, lo, le, su, sí mismo*. Pronouns joined to a verb
  (*sígueme*), *conmigo* and *contigo* get none, and neither does God's or
  Jesus's *yo*. The servant of Isaiah, the king of Isaiah 9:5 and 11:1, Cyrus
  and the speaker of 61:1 get none, while the king of Psalm 110 does
  ([PSA 110:1](https://openwordbible.org/es/psa/110/#v1)). Mark, following Romans and Hebrews,
  spans every pronoun written for God or Christ, including object pronouns
  before the verb ([MRK 1:2](https://openwordbible.org/es/mrk/1/#v2)). About
  6,800 verses in 61 books. NT "Spanish"; IsaJerEzr "Address, speech and
  settings".
- [ ] **plural_you spans.** Every plural "you" is a span: pronoun, verb and
  possessive. The Latin American *ustedes* form is the default and the
  *vosotros* form the alternative (`{{plural_you:Escuchen|Escuchad}}`,
  `{{plural_you:les|os}}`). The span covers the smallest word or phrase that
  changes, and takes in the noun where *su* could be misread
  (`{{plural_you:la paz de ustedes|vuestra paz}}`). This is the most
  widespread rule after the two above: about 4,900 verses in 64 books. Check
  that the span boundaries read naturally both ways. NT "Spanish"; Pent "All
  three languages".
- [ ] **Lord GOD** (*Adonai YHWH*) is *el Señor* `{{divine_name:DIOS|Yahvé}}`,
  with the article and any preposition outside the span. About 300 verses,
  most of them in Ezekiel. Pent table; LamTwelve "Formulas and recurring
  terms".
- [ ] **The LORD of hosts** is *el SEÑOR de los ejércitos* at L and *de los
  Ejércitos* at B and R. The capital changes by level, and the drafts follow
  that consistently. Decide whether readers will understand the difference,
  or whether one form is better. About 360 verses. Sam table; PsPr "Settled
  while drafting".
- [ ] **christos spans.** `{{christos:Cristo|el Mesías}}`;
  `{{christos:Jesucristo|Jesús, el Mesías}}`; `{{christos:Cristo Jesús|el
  Mesías Jesús}}`; with the article as a title, `el {{christos:Cristo|Mesías}}`;
  "antichrist" is *anticristo*, with no span. About 480 verses in 26 books.
  NT "Spanish".
- [ ] **Gender spans** go only where the English has one and Spanish really
  has two wordings (`{{gender:la persona|el hombre}}`). *Hermanos*, *hijos*,
  *padres* and *su* stay plain because they already include women. A
  singular *adelphos* meaning any believer is
  `{{gender:su hermano o hermana|su hermano}}`
  ([JAS 1:9](https://openwordbible.org/es/jas/1/#v9)). There are about 640
  verses with a span (L 607, B 296, R 166). Confirm that the plain
  *hermanos* and *hijos de Israel* are right. NT "Spanish"; PsPr "Language by
  language"; LamTwelve "Gender spans".
- [ ] **Units spans.** At B and R the metric value is the default and the
  original unit the alternative. L keeps the original unit. The values are
  cubit 45 cm, shekel 11.5 g, talent 34 kg and ephah 22 litres, with the long
  cubit of 53 cm in Ezekiel 40–48. About 400 verses at B and R. Pent "All
  three languages"; LamTwelve "Ezekiel's temple vision" (its table of
  values).

### Address forms and speech

- [ ] **One person is always *tú*, never *usted*.** This covers God, kings,
  Pharaoh, prophets, angels and strangers. Respect is carried by *mi señor el
  rey* and *tu siervo* instead. Court courtesy uses the third person (*si al
  rey le parece bien*). The rule touches almost every dialogue: about 5,200
  verses contain speech marks. If a reviewer wants *usted* for courtiers or
  strangers, many books change. Sam "Language by language"; IsaJerEzr
  "Address"; NehSong "Address and tenses".
- [ ] **"Your Majesty"** is *oh rey* or *mi rey* (R; *oh rey* at L and B in
  Daniel), never *Majestad*, because *Majestad* would need *usted*. About 100
  verses use *mi señor el rey*, *oh rey* or *mi rey*. Sam "Settled while
  drafting"; LamTwelve "Daniel's court". See the exception in Acts 26
  (section 4).
- [ ] **Quotation marks**: « », then “ ” inside them, then ‘ ’ inside those.
  A question or exclamation inside a quotation keeps both of its marks:
  «¿...?». The oracles take no marks. *Así dice el SEÑOR:* is followed by a
  colon, and speech quoted inside an oracle takes « ». About 5,200 verses.
  NT "Spanish"; IsaJerEzr "Address, speech and settings".
- [ ] **Cities and peoples addressed as women** (Zion, Jerusalem, Samaria,
  Babylon, Nineveh, Tyre as a ship) take feminine *tú* (*estás desolada*).
  A king addressed directly takes masculine *tú*. Israel and Judah as
  sisters agree in the feminine (*la infiel Israel*). This affects most of
  Lamentations, Ezekiel 16 and 23, Isaiah 47 and 54, and Nahum 2–3. LamTwelve
  "Cities and peoples addressed as women"; IsaJerEzr "Address".
- [ ] **Addressing a superior who is not God**: lowercase *señor* (for
  example an angel, [ACT 10:4](https://openwordbible.org/es/act/10/#v4)), *mi
  señor* (L, B) to the angel in Daniel and Zechariah, and Jesus's *Mujer* (L,
  B) / *Señora* (R) ([JHN 20:13](https://openwordbible.org/es/jhn/20/#v13)).
  LamTwelve "Angels".

### Key theological terms

- [ ] **Servant and slave** (*ʿeved*, *doulos*). The drafts use *esclavo* at
  L and *siervo* at B and R, with *esclavo* at every level where slavery
  itself is meant (Egypt, people bought and sold). God's named servants
  (Moses, David, "your servant" in prayer) are *siervo* at every level.
  *Criado* is used for household staff
  ([1PE 2:18](https://openwordbible.org/es/1pe/2/#v18)). About 820 verses
  have *siervo* and 420 have *esclavo*. NT table; Pent table; JosRuth
  "Language by language"; PsPr "Settled while drafting".
- [ ] **Righteousness and justice**: *justicia*, with *rectitud* for the
  parallel word. *Mishpat* / *tsedaqah* are *derecho* / *justicia* at L and
  B and *lo que es justo* at R. About 540 verses. IsaJerEzr "Isaiah";
  LamTwelve table.
- [ ] **Covenant** is *pacto* everywhere ("the ark of the covenant" is *el
  arca del pacto*), not *alianza*. About 350 verses. Pent table.
- [ ] **Burnt offering** is *holocausto*, and the other offerings are *el
  sacrificio por el pecado*, *por la culpa*, *de paz* and *la ofrenda de
  cereal*. The drafter of
  [GEN 8:20](https://openwordbible.org/es/gen/8/#v20) asks whether
  *holocausto* now makes readers think first of the Shoah. Alternative:
  *ofrenda quemada* at B. About 270 verses. Pent table.
- [ ] ***Ḥesed*** is *amor leal* (L) / *amor fiel* (B, R), and *bondad*
  between people. Alternatives are *misericordia* (the Reina-Valera
  tradition, set aside) and *lealtad*. About 230 verses, plus the Exodus 34:6
  formula wherever it is echoed. PsPr "Recurring terms"; JosRuth table. The
  books do not agree at L (section 4).
- [ ] **Saints** (*hagioi*) are *los santos* (L), *el pueblo santo de Dios*
  (B) and *el pueblo de Dios* (R). "The holy ones of the Most High" in Daniel
  follow the same pattern. About 190 verses. NT table; LamTwelve "Daniel".
- [ ] **Sheol and the dead**: *el Seol* (L), *el lugar de los muertos* (B, R);
  Hades is *el Hades* (L, B), *el lugar de los muertos* (R); Gehenna is
  *Gehena* (L), *el infierno* (B, R). The English keeps "Sheol" at B, and the
  Spanish does not. About 140 verses. Pent table; IsaJerEzr "Isaiah"; NT
  table.
- [ ] **The tent and its furniture**: *la Tienda del Encuentro*, *el
  tabernáculo*, *el arca del Testimonio*, *el propiciatorio*, *el
  candelabro*. About 140 verses for the tent alone, from Exodus to Numbers.
  Pent table.
- [ ] ***Torah*** is *instrucción* (L, B) and *enseñanza* (R), never a legal
  code. *La ley* is kept for "the law of Moses" and "the book of the law".
  Alternative: *ley* at L. About 90 verses. PsPr "Settled while drafting";
  IsaJerEzr "Isaiah".
- [ ] **Blessed** (*makarios*, *ʾashre*) is *dichoso* at L and B. At R the
  drafts use *Dios bendice a* or *felices*. *Bienaventurado* was set aside as
  church language ([MAT 11:6](https://openwordbible.org/es/mat/11/#v6)).
  About 130 verses. NT table. Some books use *bienaventurado* anyway
  (section 4).
- [ ] **Son of Man**: *el Hijo del Hombre* in the Gospels (about 80 verses).
  God's address to Ezekiel is *hijo de hombre*, lowercase, never the Gospel
  title (about 110 verses). Daniel 7:13 is *uno semejante a un hijo de
  hombre*, as Revelation 1:13. NT table; LamTwelve "Formulas and recurring
  terms".
- [ ] **Human officials (*sarim*)** are *los príncipes* (L), *los jefes* (B)
  and *los dirigentes* (R) in the prophets, where the English Twelve says
  "officials". The king's servants in Samuel and Kings are *los siervos del
  rey* (L) and *los oficiales del rey* (B, R). This choice is listed as open
  for the reviewer. It affects hundreds of verses (*jefes* alone appears in
  about 520). IsaJerEzr "Settled while drafting" and "Before review";
  LamTwelve "Open for the reviewer".
- [ ] ***Ḥerem***: *lo consagrado al exterminio*, *consagrar al exterminio*
  (L, B), *destruir por completo* (R). About 70 verses from Numbers to
  Samuel. JosRuth table.
- [ ] **Skin disease** (*tsaraʿat*) is *enfermedad (grave) de la piel*, never
  *lepra*. About 60 verses in Leviticus, Numbers and Kings. Pent table;
  KgsChr "Settled while drafting". The Gospels say *lepra* (section 4).
- [ ] **Repentance and God's relenting.** *Shuv* is *volver* / *volverse*,
  never *arrepentirse*. When God relents, the drafts use *retractarse* at L,
  and the Samuel note says God's regret is "never *arrepentirse*". *Metamelomai*
  is *cambiar de parecer*. NT table; IsaJerEzr "Jeremiah" and "Settled while
  drafting"; Sam "Settled while drafting". The books disagree here
  (section 4).
- [ ] **The high places** are *los lugares altos* (L, B) and *santuarios
  sobre las colinas* (R). About 80 verses. KgsChr "The high places";
  Sam table.
- [ ] **Logos** is *el Verbo* (JHN 1:1, 14; 1JN 1:1). The drafter notes that
  *la Palabra* shows the link to God's speech better but is feminine
  ([JHN 1:1](https://openwordbible.org/es/jhn/1/#v1)). There are only a few
  verses, but every reader sees them.
- [ ] **Ecclesiastes' key words** shape the whole book. *Hevel* is *soplo*
  (never *vanidad*), and Qoheleth is *Qohélet* (L) and *el Maestro* (B, R),
  next to a book title that says *Eclesiastés*. About 60 verses. NehSong
  "Ecclesiastes" and "Before review".

### Recurring formulas

- [ ] **"He aquí" at Literal** for *hinneh* / *idou*. B and R leave it out
  or say *mira* / *miren*. This is the most frequent formula: about 810
  verses at L in 43 books. Meanwhile
  [GEN 11:6](https://openwordbible.org/es/gen/11/#v6) calls *he aquí*
  archaic and uses *ya* instead. Decide whether L keeps *he aquí*. NT table
  ("look"); LamTwelve "Poetry reminders".
- [ ] **"Thus says the LORD"**: *Así dice el SEÑOR:* (L), *El SEÑOR dice
  esto:* (B), *Esto es lo que dice el SEÑOR:* (R). About 450 verses. Sam
  "Settled while drafting"; IsaJerEzr "Formulas".
- [ ] **"Declares the LORD"** (*neʾum YHWH*): *declara* (L), *afirma* (B),
  *dice* (R), always after a comma. About 350 verses. IsaJerEzr "Formulas".
- [ ] **"In that day"**: *en aquel día* (L), *aquel día* (B), *en ese
  tiempo* / *ese día* (R). About 250 verses. IsaJerEzr "Formulas".
- [ ] **"Truly I tell you"**: *En verdad {{plural_you:les|os}} digo* (L, B);
  *{{plural_you:Les|Os}} digo la verdad* (R). About 150 verses. NT table.
- [ ] **Woe** (*hoy*): *¡Ay de ...!* (L, B), *¡Qué terrible será para ...!*
  (R). A funeral cry is *¡Ay, hermano mío!* at every level. A summons is
  *¡Eh!* / *¡Vengan!* / *¡Rápido!* (uncertain,
  [ZEC 2:10](https://openwordbible.org/es/zec/2/#v10)). About 90 verses.
  IsaJerEzr "Formulas"; LamTwelve table.
- [ ] **Ezekiel's recognition formula**: *y {{plural_you:sabrán|sabréis}} que
  yo [soy] el SEÑOR* (L); *Entonces sabrán que yo soy el SEÑOR* (B, R). About
  75 verses. LamTwelve "Formulas and recurring terms".
- [ ] **Psalm titles**: *Al director del coro* (L, B) / *Para el director de
  la música* (R); *masquil*, *mictam*, *sigayón*; *Cántico de las subidas*.
  *Selah* is kept at the end of its verse at every level (74 verses). The
  title is verse 1, at every level. PsPr "Psalm titles and musical
  terms". Twenty-four of these titles are marked uncertain (section 3).
- [ ] **The regnal formulas of Kings and Chronicles.** Accession: *Tenía N
  años cuando comenzó a reinar*. Verdict: *hizo lo malo a los ojos del SEÑOR*
  (L, B), *hizo lo que el SEÑOR reprueba* (R). Death: *durmió con sus padres*
  (L), *descansó con sus antepasados* (B), *murió* (R). The sources: *los
  demás hechos de X ... están escritos en el libro de la Historia de los
  Reyes de Israel*. About 60 verses for the verdict alone, with the same
  pattern repeated through four books. KgsChr "The regnal formulas".
- [ ] **"The word of the LORD came to me"**: *Vino a mí la palabra del
  SEÑOR, diciendo:* (L), *La palabra del SEÑOR vino a mí:* (B), *El SEÑOR me
  dio este mensaje:* (R), with the headings of Jeremiah and the Twelve on the
  same pattern. It opens most oracles in Jeremiah, Ezekiel and the Twelve.
  IsaJerEzr "Formulas"; LamTwelve "The Twelve".
- [ ] **Oaths**: *Vive el SEÑOR* (L), *tan cierto como que el SEÑOR vive*
  (B, R); God's *Vivo yo* (L) / *Tan cierto como que yo vivo* (B, R); *Que
  Dios me castigue, y aun más*. About 30 verses. Sam table; LamTwelve table.
- [ ] **"Restore the fortunes"**: *restaurar la suerte* (L, B), *hacer que
  todo vuelva a ir bien* (R). There are about 20 verses, in Jeremiah 29–33,
  Ezekiel, Hosea, Amos, Zephaniah, Psalms and Job. IsaJerEzr "Jeremiah". Other
  books word it differently (section 4).

### Names and spelling conventions

- [ ] **Usual Spanish forms, and published forms win.** Examples: Jesús,
  Santiago (James), Pablo, Moisés, Aarón, Josué, Isaí, Betsabé, Joás,
  Nabucodonosor. Each terms doc has a names table. Where one Hebrew name
  belongs to two people, Spanish sometimes spells it two ways to keep them
  apart (Uzía and Uzías, Sala and Sela, *guesureos* and *guesuritas*, Saúl
  and Saulo). Thirty-five name choices are marked uncertain (section 3).
  Pent "Names"; JosRuth "Names"; Sam "Names"; KgsChr "Names"; IsaJerEzr
  "Names"; NehSong names table; LamTwelve "Names".
- [ ] **Kings with two names keep the form of each verse**, except that
  *Joás* is used for both Jehoash and Joash
  ([2KI 12:1](https://openwordbible.org/es/2ki/12/#v1)). Nebuchadrezzar is
  *Nabucodorosor* where the Hebrew has the -r- form. KgsChr "Names" and
  "Settled while drafting"; IsaJerEzr "Names".
- [ ] **Pharaoh** is *el faraón*, lowercase with the article, like *el rey*
  (about 250 verses). Pent table;
  [GEN 12:15](https://openwordbible.org/es/gen/12/#v15). The New Testament
  books do not follow this (section 4).
- [ ] **Peoples** are lowercase with the article (*los filisteos*, *los
  cusitas*). The peoples of Genesis 10 keep their Hebrew plural names,
  capitalised (*los Ludim*,
  [GEN 10:13](https://openwordbible.org/es/gen/10/#v13)). Pent "Names";
  NehSong names table.
- [ ] **Names that carry a meaning** stay in Hebrew at L and are translated
  at B and R, with every word capitalised: *No Compadecida*, *No Es Mi
  Pueblo*, *Mi Deleite Está en Ella*. The reviewer is asked about the Hosea
  forms, and *No Pueblo Mío* is the alternative. LamTwelve "Hosea" and "Open
  for the reviewer".
- [ ] **Titles with capitals**: *el Altísimo*, *el Santo de Israel*,
  *Redentor*, *el Retoño* (as a title), *el Anciano de Días* (L, B) / *el
  Anciano* (R). The servant and *el mensajero del pacto* stay lowercase.
  IsaJerEzr "Formulas" and "Isaiah"; LamTwelve "Daniel".

### Style

- [ ] **Tense by level.** Narration is in the preterite. Laws use the future
  at L and B (*no matarás*, *traerá*) and *debe*, *tiene que* or the
  imperative at R. John's historic present is kept at L only
  ([JHN 18:17](https://openwordbible.org/es/jhn/18/#v17)). This covers all
  the narrative books and all the law. Pent "All three languages"; KgsChr
  "All five languages".
- [ ] **Numbers.** Figures are used above ninety-nine and for every list
  total. Thousands take a space (*2 172*, *185 000*), and decimals take a
  comma (*3,2*). Days, months and ages are written in words. The drafts do
  not follow this consistently (section 4). NT "Both languages"; IsaJerEzr
  "Settled while drafting"; NehSong "Numbers".
- [ ] **Poetry lines and punctuation.** `\q` breaks go where the English
  level has them, at Spanish phrase boundaries. They never fall between ¡ or
  ¿ and the word it opens, and never inside a `{{...}}` span. Every ¿ and ¡
  has its closing mark. This covers Psalms, Proverbs, Job, the Song and most
  of the prophets. LamTwelve "Poetry reminders for Spanish".

## 3. Recurring uncertain choices

These groups come from [es-uncertain.md](es-uncertain.md) (284 decisions),
sorted by size. Decide each group once, then tick its items in that list.
About 230 of the 284 decisions fall into these groups. The rest are one-off
questions about a single verse.

- [ ] **Spelling of proper names and peoples** (35): the Genesis 10
  peoples, rare names in Chronicles, Babylonian names, Micah's towns, NT
  forms of OT names.
  [GEN 10:13](https://openwordbible.org/es/gen/10/#v13),
  [1CH 11:44](https://openwordbible.org/es/1ch/11/#v44),
  [MIC 1:10](https://openwordbible.org/es/mic/1/#v10)
- [ ] **Psalm titles and musical terms** (24): *masquil*, *mictam*,
  *sigayón*, *la guitit*, *Selah*, tune names, "Song of Ascents".
  [PSA 45:1](https://openwordbible.org/es/psa/45/#v1),
  [PSA 46:4](https://openwordbible.org/es/psa/46/#v4),
  [PSA 120:1](https://openwordbible.org/es/psa/120/#v1)
- [ ] **Identifying animals, plants, stones, instruments and materials**
  (22): Leviticus 11, the high priest's stones, *encina*, *ámbar* / *metal
  reluciente*, *pannag*.
  [LEV 11:13](https://openwordbible.org/es/lev/11/#v13),
  [EXO 28:17](https://openwordbible.org/es/exo/28/#v17),
  [EZK 1:4](https://openwordbible.org/es/ezk/1/#v4)
- [ ] **Setting spans: where a deity_pronoun, gender or units span goes or
  is left out** (15).
  [1SA 28:17](https://openwordbible.org/es/1sa/28/#v17),
  [MRK 1:2](https://openwordbible.org/es/mrk/1/#v2),
  [REV 3:12](https://openwordbible.org/es/rev/3/#v12)
- [ ] **Temple and worship words in Kings and Chronicles** (15): high
  places, the inner room (*devir*), the wheeled stands (*basas*), the Feast
  of Booths.
  [1KI 3:2](https://openwordbible.org/es/1ki/3/#v2),
  [1KI 6:5](https://openwordbible.org/es/1ki/6/#v5),
  [1KI 8:2](https://openwordbible.org/es/1ki/8/#v2)
- [ ] **Literal keeping a Hebrew picture or idiom** (13), for example *el
  hombre de en medio* and *oídos me has abierto*.
  [1SA 17:4](https://openwordbible.org/es/1sa/17/#v4),
  [PSA 40:7](https://openwordbible.org/es/psa/40/#v7),
  [2KI 4:16](https://openwordbible.org/es/2ki/4/#v16)
- [ ] **Plural you: when a span is used and on which words** (12):
  quotations within quotations, a group addressed as one man, a switch
  between singular and plural.
  [2SA 19:43](https://openwordbible.org/es/2sa/19/#v43),
  [JER 29:28](https://openwordbible.org/es/jer/29/#v28),
  [ZEC 9:12](https://openwordbible.org/es/zec/9/#v12)
- [ ] **Addressing kings and superiors** (10): *oh rey* / *mi rey* for "Your
  Majesty", *tú* to the king, *señor*, *Mujer*.
  [1SA 17:55](https://openwordbible.org/es/1sa/17/#v55),
  [1KI 1:2](https://openwordbible.org/es/1ki/1/#v2),
  [ACT 26:2](https://openwordbible.org/es/act/26/#v2)
- [ ] **Court and army roles** (9): *saris* as *eunuco* or *funcionario*;
  the "runners" as *la guardia*; *criado*; *turnos* and *divisiones*.
  [1KI 22:9](https://openwordbible.org/es/1ki/22/#v9),
  [2KI 10:25](https://openwordbible.org/es/2ki/10/#v25),
  [1CH 23:6](https://openwordbible.org/es/1ch/23/#v6)
- [ ] **Traditional church wording kept or set aside** (9): *holocaustos*,
  *la joven* in Isaiah 7:14, the names of Isaiah 9:5, no *Lucero*, *el
  Verbo*, *el viejo yo*, *ley real*.
  [ISA 7:14](https://openwordbible.org/es/isa/7/#v14),
  [ISA 9:5](https://openwordbible.org/es/isa/9/#v5),
  [COL 3:9](https://openwordbible.org/es/col/3/#v9)
- [ ] **Ezekiel's temple vision (40–48)** (8): *nicho*, *jambas*, *el área
  separada*, *escalón*, *el fogón del altar*.
  [EZK 40:7](https://openwordbible.org/es/ezk/40/#v7),
  [EZK 41:12](https://openwordbible.org/es/ezk/41/#v12),
  [EZK 43:15](https://openwordbible.org/es/ezk/43/#v15)
- [ ] **Human *sarim* as *príncipes* / *jefes* / *dirigentes*, against the
  English "officials"** (7).
  [EZK 11:1](https://openwordbible.org/es/ezk/11/#v1),
  [HOS 7:3](https://openwordbible.org/es/hos/7/#v3),
  [ZEP 1:8](https://openwordbible.org/es/zep/1/#v8)
- [ ] **Parallel passages that differ in the Hebrew** (7): Samuel and Kings
  against Chronicles, 2 Samuel 22 against Psalm 18, Habakkuk against Micah.
  [2SA 22:26](https://openwordbible.org/es/2sa/22/#v26),
  [2CH 7:21](https://openwordbible.org/es/2ch/7/#v21),
  [HAB 2:12](https://openwordbible.org/es/hab/2/#v12)
- [ ] **Titles of God, Christ and angels** (7): *el Autor de la vida*,
  *Líder*, *el Anciano de Días*, *el satán* / *el Acusador*, *ángel
  gobernante*.
  [ACT 3:14](https://openwordbible.org/es/act/3/#v14),
  [DAN 7:9](https://openwordbible.org/es/dan/7/#v9),
  [ZEC 3:1](https://openwordbible.org/es/zec/3/#v1)
- [ ] **Locust names** (5): *la langosta cortadora / migratoria / saltadora
  / devoradora*.
  [JOL 1:4](https://openwordbible.org/es/jol/1/#v4),
  [JOL 2:25](https://openwordbible.org/es/jol/2/#v25),
  [NAM 3:15](https://openwordbible.org/es/nam/3/#v15)
- [ ] **Ezekiel's words for laws, idols and sin** (5): *decretos* / *normas*,
  *estatutos* / *leyes*, *cosas detestables* / *ídolos viles*, *ídolos
  inmundos*, *transgresión* / *delito* / *pecado*.
  [EZK 5:6](https://openwordbible.org/es/ezk/5/#v6),
  [EZK 20:7](https://openwordbible.org/es/ezk/20/#v7),
  [DAN 8:12](https://openwordbible.org/es/dan/8/#v12)
- [ ] **Luke's *epistata* as *Maestro*** (4), the same word as for
  "Teacher".
  [LUK 5:5](https://openwordbible.org/es/luk/5/#v5),
  [LUK 8:24](https://openwordbible.org/es/luk/8/#v24),
  [LUK 17:12](https://openwordbible.org/es/luk/17/#v12)
- [ ] **Wordplay Spanish cannot keep** (4): *adam* / *adamah*, *Varona* /
  *Varón*, Jonah's *trastornada* and *malestar*.
  [GEN 2:7](https://openwordbible.org/es/gen/2/#v7),
  [GEN 2:23](https://openwordbible.org/es/gen/2/#v23),
  [JON 4:6](https://openwordbible.org/es/jon/4/#v6)
- [ ] **Hosea's children's names** (3).
  [HOS 1:6](https://openwordbible.org/es/hos/1/#v6),
  [HOS 1:9](https://openwordbible.org/es/hos/1/#v9),
  [HOS 2:3](https://openwordbible.org/es/hos/2/#v3)
- [ ] **Blessed: *dichoso* or *bienaventurado*** (3).
  [MAT 11:6](https://openwordbible.org/es/mat/11/#v6),
  [LUK 7:23](https://openwordbible.org/es/luk/7/#v23),
  [JAS 5:11](https://openwordbible.org/es/jas/5/#v11)
- [ ] **God relenting or repenting** (3): *se arrepintió*, *ni me
  arrepentiré*.
  [PSA 106:45](https://openwordbible.org/es/psa/106/#v45),
  [EZK 24:14](https://openwordbible.org/es/ezk/24/#v14),
  [JOB 42:6](https://openwordbible.org/es/job/42/#v6)
- [ ] **Slaves and household servants** (3): *esclavos y esclavas*,
  *criados*, *la esclava* / *la criada*.
  [NEH 7:67](https://openwordbible.org/es/neh/7/#v67),
  [1PE 2:18](https://openwordbible.org/es/1pe/2/#v18),
  [JHN 18:17](https://openwordbible.org/es/jhn/18/#v17)
- [ ] **Smaller pairs** (2 each):
  - a town's "daughters" as *aldeas*:
    [1CH 18:1](https://openwordbible.org/es/1ch/18/#v1),
    [2CH 13:19](https://openwordbible.org/es/2ch/13/#v19)
  - Haman's *horca*:
    [EST 2:23](https://openwordbible.org/es/est/2/#v23),
    [EST 5:14](https://openwordbible.org/es/est/5/#v14)
  - *padres* for fathers or parents:
    [EPH 6:4](https://openwordbible.org/es/eph/6/#v4),
    [COL 3:21](https://openwordbible.org/es/col/3/#v21)
  - *levantar* for raising from the dead:
    [ACT 5:30](https://openwordbible.org/es/act/5/#v30),
    [ACT 13:32](https://openwordbible.org/es/act/13/#v32)
  - the pointer word as *ya*, *he aquí* or *mira*:
    [GEN 11:6](https://openwordbible.org/es/gen/11/#v6),
    [REV 9:12](https://openwordbible.org/es/rev/9/#v12)

## 4. Known inconsistencies to resolve

Each of these was checked in `content/` before it was listed. Pick one
wording, record it in the terms doc, and align the other books.

- [ ] **The Feast of Booths has three names.** It is *la fiesta de las
  Cabañas* in Leviticus, Numbers and Deuteronomy
  ([LEV 23:34](https://openwordbible.org/es/lev/23/#v34),
  [DEU 16:13](https://openwordbible.org/es/deu/16/#v13); lowercase
  *cabañas* at L in Deuteronomy). It is *la fiesta de las Enramadas* in
  Kings, Chronicles, Ezra, Nehemiah and Zechariah
  ([1KI 8:2](https://openwordbible.org/es/1ki/8/#v2),
  [EZR 3:4](https://openwordbible.org/es/ezr/3/#v4),
  [ZEC 14:16](https://openwordbible.org/es/zec/14/#v16)). John 7:2 has *la de
  los Tabernáculos* at L and B and *las Enramadas* at R
  ([JHN 7:2](https://openwordbible.org/es/jhn/7/#v2)). NehSong settles
  *Enramadas* "[Ezra 3:4]" without mentioning the Pentateuch.
- [ ] ***Ḥesed* at Literal.** The Pentateuch, Nehemiah, Joel, Jonah and
  Micah 7 say *amor fiel* at L
  ([GEN 24:12](https://openwordbible.org/es/gen/24/#v12),
  [EXO 34:6](https://openwordbible.org/es/exo/34/#v6),
  [NEH 9:17](https://openwordbible.org/es/neh/9/#v17)). Joshua to Psalms and
  most of the prophets say *amor leal*
  ([PSA 103:8](https://openwordbible.org/es/psa/103/#v8), against
  [NUM 14:18](https://openwordbible.org/es/num/14/#v18) for the same
  formula). The Pentateuch table gives *el amor fiel* for every level. The
  temple refrain at B also differs: *su amor leal permanece para siempre* in
  [2CH 5:13](https://openwordbible.org/es/2ch/5/#v13) and
  [2CH 7:3](https://openwordbible.org/es/2ch/7/#v3), against Psalm 136's *su
  amor fiel dura para siempre*
  ([PSA 136:1](https://openwordbible.org/es/psa/136/#v1)), which KgsChr says
  to reuse. Likewise
  [2SA 22:51](https://openwordbible.org/es/2sa/22/#v51) B *amor leal*
  against [PSA 18:51](https://openwordbible.org/es/psa/18/#v51) B *amor
  fiel*. LamTwelve already lists Joel 2:13 against Jonah 4:2 as an open
  question.
- [ ] **God relenting is worded five ways at L.** The Samuel note says
  "never *arrepentirse*", and IsaJerEzr sets *retractarse*. The drafts have
  *desistió* ([EXO 32:14](https://openwordbible.org/es/exo/32/#v14)),
  *me pesa* / *le pese*
  ([1SA 15:29](https://openwordbible.org/es/1sa/15/#v29)), *me retractaré*
  ([JER 18:8](https://openwordbible.org/es/jer/18/#v8),
  [AMO 7:3](https://openwordbible.org/es/amo/7/#v3)) and *se arrepintió* /
  *ni me arrepentiré*
  ([PSA 106:45](https://openwordbible.org/es/psa/106/#v45),
  [EZK 24:14](https://openwordbible.org/es/ezk/24/#v14)).
- [ ] **Blessed: *bienaventurado* against *dichoso*.** The NT table settles
  *dichosos*, and Matthew, Luke, Revelation and Psalms follow it. James, 1
  Peter, Romans and 1 Timothy use *bienaventurado* at L and B
  ([JAS 1:12](https://openwordbible.org/es/jas/1/#v12),
  [1PE 3:14](https://openwordbible.org/es/1pe/3/#v14),
  [ROM 4:7](https://openwordbible.org/es/rom/4/#v7)). Romans 4:7 quotes
  [PSA 32:1](https://openwordbible.org/es/psa/32/#v1), which says *¡Dichoso
  ...!*.
- [ ] **Numbers are written three ways.** Ezra, Nehemiah, Ezekiel, Exodus
  and Joshua write four-digit numbers with a space (*42 360*, *5 000*,
  [EZR 2:64](https://openwordbible.org/es/ezr/2/#v64)). 1 Chronicles, Judges,
  Mark and Revelation write them without one (*6800*,
  [1CH 12:25](https://openwordbible.org/es/1ch/12/#v25)). About 180
  renderings, mostly in 2 Chronicles, 2 Kings, Judges and 1 Samuel, spell
  round thousands in words. One units span uses a point:
  *Unos 22.000 litros* ([LUK 16:7](https://openwordbible.org/es/luk/16/#v7)
  B, R).
- [ ] **The shofar.** It is *cuerno de carnero* at every level in Judges,
  Samuel, Psalms and Isaiah
  ([2SA 6:15](https://openwordbible.org/es/2sa/6/#v15),
  [PSA 150:3](https://openwordbible.org/es/psa/150/#v3),
  [ISA 18:3](https://openwordbible.org/es/isa/18/#v3)). It is *trompeta*
  (L, R) / *cuerno de carnero* (B) from Jeremiah on
  ([JER 4:5](https://openwordbible.org/es/jer/4/#v5),
  [JOL 2:1](https://openwordbible.org/es/jol/2/#v1)), and *cuernos* /
  *cuernos de carnero* / *trompetas* in
  [JOS 6:4](https://openwordbible.org/es/jos/6/#v4). LamTwelve says its
  wording is "as Isaiah", but Isaiah does not have it.
- [ ] **The teraphim have seven wordings.** They are *dioses domésticos*,
  *ídolos domésticos*, *ídolo doméstico*, *terafines*, *ídolos familiares*,
  *ídolos de la familia*, *ídolos de la casa* and *imágenes de los dioses de
  la familia*
  ([GEN 31:19](https://openwordbible.org/es/gen/31/#v19),
  [JDG 17:5](https://openwordbible.org/es/jdg/17/#v5),
  [1SA 19:13](https://openwordbible.org/es/1sa/19/#v13),
  [HOS 3:4](https://openwordbible.org/es/hos/3/#v4),
  [EZK 21:26](https://openwordbible.org/es/ezk/21/#v26)). The Samuel table
  gives *los dioses domésticos* (L), *el ídolo doméstico* (B, R).
- [ ] ***Lepra* in the Gospels.** The OT never uses *lepra*, but Matthew,
  Mark and Luke say *leproso* / *lepra* at L and B, and *enfermedad de la
  piel* at R ([MAT 8:2](https://openwordbible.org/es/mat/8/#v2)). In
  [LUK 4:27](https://openwordbible.org/es/luk/4/#v27), Naaman's disease is
  *leprosos* (L) and *lepra* (B), but *enfermedad de la piel* in
  [2KI 5:1](https://openwordbible.org/es/2ki/5/#v1).
- [ ] **Pharaoh as a name.** The OT says *el faraón*. The NT has *Faraón*
  without the article
  ([ROM 9:17](https://openwordbible.org/es/rom/9/#v17),
  [HEB 11:24](https://openwordbible.org/es/heb/11/#v24),
  [ACT 7:13](https://openwordbible.org/es/act/7/#v13)), and so do two
  vocatives at R ([ISA 19:12](https://openwordbible.org/es/isa/19/#v12),
  [EZK 31:18](https://openwordbible.org/es/ezk/31/#v18)). The drafter flags
  this at GEN 12:15.
- [ ] ***Usted* and *Majestad* despite the rule.**
  [NUM 36:2](https://openwordbible.org/es/num/36/#v2) R has *le ordenó a
  usted*. [ACT 26:6](https://openwordbible.org/es/act/26/#v6) and
  [ACT 26:12](https://openwordbible.org/es/act/26/#v12) R address Agrippa as
  *Majestad*, and
  [ACT 25:21](https://openwordbible.org/es/act/25/#v21) L has *Su Majestad*
  for the emperor. That may be right as a title, but it needs a decision.
- [ ] **The *saris*.** KgsChr gives *eunucos* (L) / *funcionarios* (B, R).
  Esther has *eunuco* at L and B
  ([EST 2:3](https://openwordbible.org/es/est/2/#v3)), and
  [1KI 22:9](https://openwordbible.org/es/1ki/22/#v9) has *funcionario* even
  at L. Jeremiah also had an English conflict over this word (see
  `docs/review-notes/jeremiah-lamentations.md`, chapter 41).
- [ ] **High places at R.** Samuel has *el santuario de la colina* (9
  verses, [1SA 9:12](https://openwordbible.org/es/1sa/9/#v12)). Kings and
  Chronicles have *santuario(s) sobre la(s) colina(s)* (about 45,
  [2KI 17:9](https://openwordbible.org/es/2ki/17/#v9)). Isaiah, Jeremiah and
  Ezekiel have *santuarios en las colinas*
  ([JER 17:3](https://openwordbible.org/es/jer/17/#v3)).
- [ ] **The inner room (*devir*) at R.** It is *el lugar santísimo* in Kings
  ([1KI 6:19](https://openwordbible.org/es/1ki/6/#v19)) and *el cuarto
  interior* in Chronicles
  ([2CH 3:16](https://openwordbible.org/es/2ch/3/#v16),
  [2CH 5:7](https://openwordbible.org/es/2ch/5/#v7)). At B, 1 Kings uses both
  *santuario interior* and *cuarto interior*.
- [ ] **"Restore the fortunes".** IsaJerEzr sets *restaurar la suerte*
  (L, B), and Jeremiah, Ezekiel and Amos follow it. The drafts also have
  *hará volver tu suerte* / *cambiará tu suerte*
  ([DEU 30:3](https://openwordbible.org/es/deu/30/#v3)), *cambie la suerte*
  at B ([PSA 14:7](https://openwordbible.org/es/psa/14/#v7)), and *hizo
  volver la cautividad* at L
  ([JOB 42:10](https://openwordbible.org/es/job/42/#v10)).
- [ ] **"He aquí" at B.** The rule is that B and R leave it out, but 8
  B renderings keep it ([NUM 23:24](https://openwordbible.org/es/num/23/#v24),
  [JDG 19:9](https://openwordbible.org/es/jdg/19/#v9),
  [JER 47:2](https://openwordbible.org/es/jer/47/#v2) and five more in
  Jeremiah 48–50).
- [ ] **Salem**: *Salén* in
  [GEN 14:18](https://openwordbible.org/es/gen/14/#v18) (an uncertain
  decision), *Salem* in [PSA 76:3](https://openwordbible.org/es/psa/76/#v3)
  and [HEB 7:1](https://openwordbible.org/es/heb/7/#v1).
- [ ] **Nazōraios**: *el Nazoreo* at L in John and Matthew 2:23
  ([JHN 18:5](https://openwordbible.org/es/jhn/18/#v5)), but *el Nazareno*
  (capitalised) at L in Acts ([ACT 2:22](https://openwordbible.org/es/act/2/#v22)),
  and lowercase *nazareno* elsewhere.

## 5. Passages to read closely

The terms docs name these as pulling hardest toward copyrighted Spanish
Bibles (Reina-Valera 1960 and later, NVI, DHH, NTV, LBLA, BTX). Check that
each level is the drafter's own wording, with no run that matches a known
version for more than a short common phrase. Where a doc names the wording
to avoid, it is given here.

- [ ] **Pentateuch** (Pent): [Genesis 1](https://openwordbible.org/es/gen/1/#v1),
  [Exodus 20](https://openwordbible.org/es/exo/20/#v1),
  [Deuteronomy 6](https://openwordbible.org/es/deu/6/#v4).
- [ ] **Joshua to Ruth** (JosRuth):
  [Joshua 1](https://openwordbible.org/es/jos/1/#v1),
  [Joshua 24:15](https://openwordbible.org/es/jos/24/#v15),
  [Judges 6](https://openwordbible.org/es/jdg/6/#v11)–7,
  [Judges 16](https://openwordbible.org/es/jdg/16/#v4),
  [Ruth 1:16–17](https://openwordbible.org/es/rut/1/#v16).
- [ ] **Samuel** (Sam): Hannah's song
  ([1 Samuel 2](https://openwordbible.org/es/1sa/2/#v1)), David and Goliath
  ([1 Samuel 17](https://openwordbible.org/es/1sa/17/#v1)), David and
  Jonathan ([1 Samuel 18](https://openwordbible.org/es/1sa/18/#v1)–20),
  Bathsheba and Nathan's parable
  ([2 Samuel 11](https://openwordbible.org/es/2sa/11/#v1)–12), the lament
  over Absalom ([2 Samuel 19:1](https://openwordbible.org/es/2sa/19/#v1)).
- [ ] **Psalms and Proverbs** (PsPr):
  [Psalm 23](https://openwordbible.org/es/psa/23/#v1),
  [51](https://openwordbible.org/es/psa/51/#v1),
  [91](https://openwordbible.org/es/psa/91/#v1),
  [103](https://openwordbible.org/es/psa/103/#v1),
  [Proverbs 3:5–6](https://openwordbible.org/es/pro/3/#v5),
  [Proverbs 31](https://openwordbible.org/es/pro/31/#v10).
- [ ] **Isaiah and Jeremiah** (IsaJerEzr):
  [Isaiah 6](https://openwordbible.org/es/isa/6/#v1),
  [7:14](https://openwordbible.org/es/isa/7/#v14),
  [9:5–6](https://openwordbible.org/es/isa/9/#v5) (avoid *Admirable
  Consejero, Dios fuerte, Padre eterno*),
  [40](https://openwordbible.org/es/isa/40/#v1),
  [52:13–53:12](https://openwordbible.org/es/isa/52/#v13),
  [61](https://openwordbible.org/es/isa/61/#v1),
  [Jeremiah 31](https://openwordbible.org/es/jer/31/#v31) (against Hebrews
  8).
- [ ] **Nehemiah to the Song** (NehSong):
  [Job 1–2](https://openwordbible.org/es/job/1/#v1),
  [3](https://openwordbible.org/es/job/3/#v1),
  [19:25–27](https://openwordbible.org/es/job/19/#v25),
  [28](https://openwordbible.org/es/job/28/#v1),
  [38–42](https://openwordbible.org/es/job/38/#v1);
  [Ecclesiastes 1:2–11](https://openwordbible.org/es/ecc/1/#v2),
  [3:1–8](https://openwordbible.org/es/ecc/3/#v1) (avoid *Todo tiene su
  tiempo, y todo lo que se quiere debajo del cielo tiene su hora*),
  [12:1–8](https://openwordbible.org/es/ecc/12/#v1);
  [Song 2:7](https://openwordbible.org/es/sng/2/#v7),
  [2:10–13](https://openwordbible.org/es/sng/2/#v10),
  [8:6–7](https://openwordbible.org/es/sng/8/#v6);
  [Esther 4:14](https://openwordbible.org/es/est/4/#v14) (avoid *para esta
  hora*); [Nehemiah 1:5–11](https://openwordbible.org/es/neh/1/#v5),
  [9](https://openwordbible.org/es/neh/9/#v6).
- [ ] **Lamentations, Ezekiel, Daniel and the Twelve** (LamTwelve):
  [Lamentations 3:22–23](https://openwordbible.org/es/lam/3/#v22) (avoid
  *misericordias*, *nunca decayeron*);
  [Ezekiel 36:26](https://openwordbible.org/es/ezk/36/#v26),
  [37:1–14](https://openwordbible.org/es/ezk/37/#v1);
  [Daniel 7:13–14](https://openwordbible.org/es/dan/7/#v13),
  [12:2–3](https://openwordbible.org/es/dan/12/#v2);
  [Hosea 6:6](https://openwordbible.org/es/hos/6/#v6),
  [11:1–4](https://openwordbible.org/es/hos/11/#v1);
  [Joel 2:13](https://openwordbible.org/es/jol/2/#v13) (avoid *Rasgad
  vuestro corazón, y no vuestros vestidos*),
  [3:1–5](https://openwordbible.org/es/jol/3/#v1) (English 2:28–32);
  [Amos 5:24](https://openwordbible.org/es/amo/5/#v24) (avoid *como
  impetuoso arroyo*) and the refrain of 1:3–2:6 (avoid *no revocaré su
  castigo*); [Micah 5:1](https://openwordbible.org/es/mic/5/#v1),
  [6:8](https://openwordbible.org/es/mic/6/#v8) (avoid *amar misericordia*,
  *humillarte ante tu Dios*);
  [Habakkuk 2:4](https://openwordbible.org/es/hab/2/#v4),
  [3:17–19](https://openwordbible.org/es/hab/3/#v17);
  [Zephaniah 3:17](https://openwordbible.org/es/zep/3/#v17);
  [Zechariah 4:6](https://openwordbible.org/es/zec/4/#v6) (avoid *No con
  ejército, ni con fuerza* and *No será por la fuerza ni por ningún poder*),
  [9:9](https://openwordbible.org/es/zec/9/#v9);
  [Malachi 3:10](https://openwordbible.org/es/mal/3/#v10),
  [3:20](https://openwordbible.org/es/mal/3/#v20) (English 4:2).
- [ ] **New Testament.** The NT terms doc forbids reproducing Reina-Valera
  1960, NVI, DHH and NTV, but it names no passages. The passages that pull
  hardest are probably the same as in other languages: the Lord's Prayer
  ([MAT 6:9](https://openwordbible.org/es/mat/6/#v9)), the Beatitudes
  ([MAT 5:3](https://openwordbible.org/es/mat/5/#v3)),
  [Luke 2](https://openwordbible.org/es/luk/2/#v1),
  [John 1:1](https://openwordbible.org/es/jhn/1/#v1),
  [John 3:16](https://openwordbible.org/es/jhn/3/#v16) and
  [1 Corinthians 13](https://openwordbible.org/es/1co/13/#v1). These are not
  flagged in the docs and are suggested here.
