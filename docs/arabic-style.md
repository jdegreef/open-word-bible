# Arabic style guide

How Open Word Bible drafts Arabic (العربية, code `ar`). It builds on
`docs/english-style.md`, which still covers everything that is not about
wording: sources, one record per sentence, the three levels, decisions and
status. It also builds on each book's terms notes (`docs/john-terms.md` and
the others), whose book-wide choices hold in Arabic unless this file says
otherwise. `docs/arabic-terms.md` is the glossary of recurring terms and
names, Genesis to Revelation. Where this file and the founder's Translation
Charter disagree, the Charter wins; fix this file.

**Status: drafting brief, awaiting native Arabic reviewers.** Every choice
below is **the rule drafters follow**, book by book, without re-deciding it;
a drafter who thinks a rule is wrong for a passage follows it anyway and
says so in a rendering decision marked uncertain. Section 15 lists the
choices that decide the most verses, for the founder and a native reviewer
to confirm or change once; a change is made here and then carried through
every book drafted under the old rule.

Arabic is the first reading language written right to left
(`docs/adding-a-language.md` section 11). Direction is a matter of display
only: records hold Arabic in its typed (logical) order, and nothing in this
file depends on how a line is shown.

## 1. Sources and independence

- Translate from the Hebrew (and the Greek), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Arabic says that meaning in its own
  way.
- **Never reproduce the wording of a copyrighted Arabic Bible.** Under
  copyright: the *Arabic Life Bible* / *Ketab El Hayat* and the *New Arabic
  Version* (Biblica), the *Good News Arabic* (*الترجمة العربية المشتركة*,
  1993, Bible Society of Lebanon), the *Sharif Arabic Bible*
  (*الترجمة العربية الشريفة*, 2000), the *New Jerusalem* Jesuit Arabic
  (Dar el-Machreq, 1989), the *Arabic Easy-to-Read Version*, the *Kitab
  al-Hayat* paraphrase and the Catholic editions with the deuterocanonical
  books. The *Van Dyck* (or *Smith–Van Dyck*, *البستاني–فاندايك*, 1865) and
  the old Jesuit Bible (1881) are in the public domain, but Open Word Bible
  does not copy public-domain Bibles either: reference Bibles in any language
  are for comparison and review only, never the basis for its wording.
- **Van Dyck is what readers hear.** It is still read aloud in most
  Protestant, Evangelical and Coptic Orthodox churches of Egypt and the
  Levant, so familiar verses pull a draft toward its wording as strongly as
  the Union Version pulls Chinese. Draft from the Hebrew or Greek and the
  gloss, then **compare every well-known verse with Van Dyck and the Good
  News Arabic and rewrite any sentence that matches either for more than a
  short common phrase.** A short common phrase is a term or a fixed
  collocation any Arab Christian would use (*ملكوت الله*, *ابن الإنسان*,
  *يوم السبت*, *رب الجنود*, *الروح القدس*), not a clause.
- The conventional forms of names, the names of the books and the church's
  shared vocabulary (sections 6–7) are not wording and may be used.
- Never type Greek or Hebrew. A Greek or Hebrew word quoted in a decision is
  copied from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"ar": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, and the
  `\q ` line breaks of poetry (section 11), in every Arabic level. Arabic
  narrative is verb-first, as the Hebrew is, so a verse's content rarely
  has to cross a marker; where it must, say so in a `word_order` decision.
- The meaning decisions are shared: do not change them. Arabic needs only
  its own rendering decisions, with ids `r-ar-1`, `r-ar-2`, ... counted from
  1 in each record, `"layer": "rendering"`, `"language": "ar"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative).
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions; the Arabic words under discussion are
  quoted in it ("\"النعمة\" rather than \"الفضل\""). The site tells Arabic
  readers that notes are in English for now.
- Write an Arabic rendering decision where Arabic had to choose and a reader
  might ask why: a word chosen against the familiar Van Dyck word, a dual or
  feminine form the Greek does not mark (section 5), a setting span that
  differs from the English one, a word chosen for or against an Islamic
  overtone (section 9), or a term settled here for the whole book (once,
  where it first appears in a passage). Do not repeat the English rendering
  decisions. Typical density: zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language, so each Arabic level opens and closes the same quotations,
  in the same order, as the English one.

## 3. The three levels in Arabic

The level names on the site are **حرفية** (Literal), **متوازنة** (Balanced)
and **ميسّرة** (Readable).

The language is **Modern Standard Arabic** (*الفصحى المعاصرة*): the written
standard every Arabic-speaking country reads, as in a serious newspaper, a
school textbook or a sermon, with no dialect at any level. A reader in Cairo,
Beirut, Baghdad, Khartoum or Casablanca must read each level as his own.
Two registers are avoided at every level:

- **Old Bible Arabic** (the marks of Van Dyck and its imitators): *هوذا*
  for "behold" outside Literal, *إصحاح* for chapter, *خطية* (write
  *خطيئة*), *ناموس* for the Law (section 7), *عشّار* outside Literal,
  *الحق الحق أقول لكم* outside Literal, *فأجاب وقال* chains, *لما كان ...
  إذا ...* sentence frames, *قائلًا* after every verb of speaking, and the
  vocative *أيها* stacked on every address. They are not wrong Arabic; they
  are the sound of 1865.
- **Dialect** (عامية): no Egyptian, Levantine, Gulf, Iraqi or Maghrebi words
  or forms: not *إيه*, *ده*, *دي*, *مش*, *عايز*, *كده*, *بدّو*, *هيك*,
  *شو*, *زي*, *اللي* for the relative, *بـ* on a present verb (*بيقول*),
  *ح/ها* for the future. Readable is plain, not spoken.

**Literal (حرفية, OWB-L).** Follows the Hebrew or Greek order and wording
where Arabic allows: the Hebrew *wayyiqtol* chain as *و* + perfect verb; the
construct chain as the Arabic *إضافة*, which Arabic shares with Hebrew
(*بيت الرب*, *كلمة الله*, *ابن داود*); the Greek participle as a *حال* or a
relative clause; the repetitions of the original. Words Arabic needs but the
original lacks go in [square brackets]. What Arabic grammar requires is not
bracketed: the article, the verb's agreement, the dual (section 5), *أنّ* and
*أن*, the pronoun of separation (*هو*) in a nominal sentence, *قد* with the
perfect where the sense needs it, and the copula's absence. Literal may read
stiffly; it must not be wrong Arabic.

**Balanced (متوازنة, OWB-B).** Careful written Arabic, the register of a
good public reading in church. It tracks the original closely, with no
brackets, and in its own word order: verb-first in narrative, subject-first
where Arabic puts the topic first. Church words stay where they are the
living word for the thing (*النعمة*, *التوبة*, *ملكوت الله*, *رئيس الكهنة*).

**Readable (ميسّرة, OWB-R).** Plain Modern Standard Arabic for new and young
readers and for readers whose daily Arabic is a dialect: short sentences,
common words, explained idioms, and what the context implies made explicit
where the English Readable does so, with a decision. Readable prefers the
nominal sentence and the ordinary present where they read more easily,
avoids rare broken plurals and verbal nouns where a verb will do, and does
not use the *حال* chains of literary prose.

### Vowel marks (تشكيل)

- **No full vocalisation at any level.** Arabic is read without short
  vowels; a fully vowelled text is the register of the Qur'an and of
  children's primers, and the marks make spans and search harder.
- Write a mark only where a word would otherwise be misread in context, at
  every level alike: the **shadda** where it separates two words (*علّم*
  "taught" / *علم* "knew"; *قدّس* / *قدس*), a **damma** or **kasra** that
  marks a passive the context does not show (*قُتل*), and the **tanwin
  fatha** written on the *alif* as standard spelling requires (*أيضًا*,
  *شكرًا*). Not on names, not on the divine name, never inside a setting
  span.
- **Hamza** and the **alif** are written as current standard spelling has
  them (*إله*, *أنا*, *آمن*, *مسؤول*, *شيء*); the final *ى* and *ي* are
  distinguished (*على*, *موسى*, *في*), not merged as Egyptian print merges
  them; *ة* and *ه* are distinguished. No *tatweel* (ـ) anywhere.

## 4. God, the Lord and the divine name

### God: *الله*

- *theos* and *Elohim* (of the God of Israel) are **الله** at every level.
  Arabic-speaking Christians called God *الله* before Islam, and every Arabic
  Bible since the earliest Gospel translations (ninth century) does: it is the
  Arabic word for God, not a Muslim name. With a pronoun suffix the noun is
  **إله**: *إلهي*, *إلهك*, *إلهنا*, *إله إبراهيم*, *الرب إلهك* — as every
  Arabic Bible writes it.
- A false god or gods: *إله* / *آلهة* (*آلهة أخرى*, *آلهة الأمم*), or the
  god's name (*البعل*, *أرطاميس*). Not *الله* with a lowercase sense, which
  Arabic cannot mark.
- *El* compounds: *الله العلي* (*El Elyon*), *الله القدير* (*El Shaddai*),
  *القدير* (*Shaddai* alone), *الإله السرمدي* (*El Olam*).

### Lord: *الرب*

- *kyrios* for God or for Jesus, and *Adonai*, are **الرب** at every level.
  "The Lord Jesus" is *الرب يسوع*. "Lord!" in address is *يا رب*.
- *kyrios* or *adon* for a human master is **السيّد** (*سيّده*, *سيّدي*),
  and *kyrie* to a stranger is *يا سيّد*. Where it is unclear whether a
  speaker means "Lord" or "sir" (John 4; 9:36), follow the English choice and
  its decision.
- "my lord" from a subject to a king is *سيّدي الملك* (L, B) and *يا جلالة
  الملك* (R) by context (section 5).

### The divine name: *الرب* by default, *يهوه* as the setting

- YHWH is `{{divine_name:الرب|يهوه}}` at every level. Arabic has no
  capitals, so the default cannot be told apart from *الرب* for *Adonai* and
  *kyrios* by its letters: this is the price every Arabic Bible pays, and the
  setting is how a reader sees where the name stands. Van Dyck and the modern
  versions all print *الرب*; *يهوه* is the form used in Arabic scholarship and
  in some recent versions.
- **The article.** The default *الرب* carries the article, and *يهوه* does
  not take one. So nothing that fuses with the article goes against the span:
  - **Never *لـ* before the span.** *لـ* + *الرب* is *للرب*, which a span
    cannot write. Use *إلى* (*صلّى إلى الرب*), *من أجل*, *أمام*, or reword
    (*ذبيحة للرب* is `ذبيحة مقدّمة إلى {{divine_name:الرب|يهوه}}`). The
    validator cannot see this; the drafting check (section 14) searches for
    it.
  - *و*, *ف*, *ب* and *ك* join the span as written: `و{{divine_name:الرب|يهوه}}`
    (*والرب* / *ويهوه*), `ب{{divine_name:الرب|يهوه}}` (*بالرب* / *بيهوه*). Both
    options read correctly.
  - In an *إضافة* the name is the second term, with its article:
    `كلمة {{divine_name:الرب|يهوه}}`, `بيت {{divine_name:الرب|يهوه}}`,
    `ملاك {{divine_name:الرب|يهوه}}`, `يوم {{divine_name:الرب|يهوه}}`.
  - In address, the default loses its article: `يا {{divine_name:رب|يهوه}}`.
- *YHWH Elohim* (Genesis 2–3) is `{{divine_name:الرب|يهوه}} الإله`.
  "The LORD my God" is `{{divine_name:الرب|يهوه}} إلهي`; "the LORD your God"
  `{{divine_name:الرب|يهوه}} إلهك` (singular, masculine), *إلهكِ* (feminine:
  Zion, Jerusalem), *إلهكم* (plural).
- *Adonai YHWH* ("Lord GOD") is `السيّد {{divine_name:الرب|يهوه}}`, with
  *السيّد* outside the span, as the English writes `Lord {{divine_name:GOD|Yahweh}}`;
  in address `يا سيّدي {{divine_name:الرب|يهوه}}`.
- *YHWH tsevaot* is `{{divine_name:رب|يهوه}} الجنود` at every level: the
  construct *رب الجنود* is the established title, and the alternative reads
  *يهوه الجنود* as the Hebrew does. Readable may say
  `{{divine_name:الرب|يهوه}} القدير` where the English Readable explains the
  title, with a decision.
- The short form *Yah* is `{{divine_name:الرب|ياه}}`; in *Hallelu Yah* it is
  *هللويا*, with no span, as the English writes "Hallelujah".
- *يهوه* is the spelling of the alternative. *يَهْوَه* with vowels, *ياهوه*
  and *يهوا* are not used; *الجيهوفاه* never.
- In a New Testament quotation of the Old Testament the Greek has *kyrios*,
  so write *الرب* and note the Hebrew original in a decision, as the English
  does (John 1:23).

### Pronouns for God: no `deity_pronoun` spans

Arabic has no capital letters and no reverent pronoun forms, so there is
nothing for `deity_pronoun` to change: Arabic renderings have **no
deity_pronoun spans**, as Hindi, Amharic, Korean and Japanese have none
(`scripts/settings_parity.py` lists this as by design). Arabic pronouns are
marked for gender and number, and most are suffixes or inside the verb, so
the reader can usually tell who is meant; where a Hebrew *he* could be God
or a man and Arabic would leave it unclear, Balanced and Readable may name
him (*الرب*, *الله*) with a decision, as the English Readable sometimes
does. God's "Let us" (Genesis 1:26) is *لنصنع* / *نصنع*, with no span.

## 5. Address and speech

Arabic marks gender and number in every pronoun and verb of the second
person: one man (*أنتَ*), one woman (*أنتِ*), two people (*أنتما*), a group
of men or a mixed group (*أنتم*), a group of women (*أنتنّ*). Greek and
Hebrew mark gender and number too, though Greek has no dual; these choices
follow the original's own marks, and where Arabic needs what the original
does not say, they are rendering decisions, never meaning decisions.

### Number: the dual

- **The dual is grammar, not a choice.** Where the text speaks to, about or
  of exactly two people or things, Arabic uses the dual at every level, as it
  must: Jesus sending two disciples (*اذهبا إلى القرية*, Mark 11:2), the two
  blind men (*أتؤمنان*, Matthew 9:28), Adam and Eve after Genesis 2, the two
  tablets (*اللوحان*). It is not bracketed at Literal.
- Where the Greek plural covers two people only because Greek has no dual,
  the Arabic dual is not a departure from the Greek and needs no decision;
  where it is unclear whether two or more are meant, keep the plural and say
  so in a decision.

### Gender

- **A group of men or of men and women** is masculine plural (*أنتم*,
  *تعالوا*), as the Greek and Hebrew masculine plural is. It is inclusive in
  Arabic; the `gender` setting is for nouns (section 8), not for verbs and
  pronouns.
- **A group of women** is feminine plural (*يا بنات أورشليم، لا تبكين*,
  Luke 23:28; the women at the tomb, *لا تخفن*, Matthew 28:5).
- **A city or a people addressed as a woman** (Zion, Jerusalem, Babylon,
  "daughter of Zion") keeps the feminine: *افرحي*, *إلهكِ*. Arabic city names
  are feminine already.

### "You" and respect

- MSA has no polite pronoun: *أنت* is said to God, to a king and to a child
  alike. Respect is shown by titles of address, not by the pronoun.
- **To God and to Jesus**: *أنت* and *يا رب* / *يا سيّد* / *يا معلّم* as the
  Greek has it, from disciples, petitioners and opponents alike.
- **To a superior or a stranger**: *يا سيّدي* (L, B; R may say *يا سيّد*),
  *يا معلّم* for *didaskale*, *يا رابّي* for *rabbi* (L, B; *يا معلّم* at
  R, as the English Readable says "Teacher").
- **To a king**: *أيها الملك* (L, B), *يا جلالة الملك* (R); "your servant"
  as "I" (the Hebrew humble self-reference): *عبدك* at Literal and Balanced,
  *أنا* at Readable, with a decision the first time in a book. "May the king
  live for ever": *ليحيَ الملك إلى الأبد*.
- **Woman** (*gynai*) as an address: *يا امرأة* at Literal and Balanced,
  with a decision (the Greek word is not cold, and the Arabic is plainer than
  it); *يا سيّدتي* at Readable to a stranger (John 4:21), and *يا أمّي* where
  Jesus speaks to his mother (John 2:4; 19:26), with a decision.
- *أيها* + noun (*أيها الإخوة*, *أيها الملك*) is the standard vocative of a
  speech; *يا* (*يا رب*, *يا ابني*) is the vocative of direct, personal
  address. Use one per address, not both (*يا أيها*) outside Literal.

### "I" and "we"

- *أنا* and *نحن*; Arabic has no inclusive or exclusive "we". The writer of a
  letter says *أنا* and *نحن* as the Greek has them, and the "we" of an
  apostle and his companions is not resolved in the text.

### Brothers and sisters

- *adelphoi* meaning believers is `{{gender:الإخوة والأخوات|الإخوة}}` where
  the English has the gender span: the inclusive pair by default, the
  traditional *الإخوة* as the alternative. In address: `{{gender:أيها الإخوة والأخوات|أيها الإخوة}}`.
  Arabic *إخوة* is grammatically masculine and is heard as men in modern
  usage, so the setting is needed here, unlike Indonesian *saudara*.
- "My brothers" with a suffix: `{{gender:إخوتي وأخواتي|إخوتي}}`.
- *إخوة* (siblings, fellow believers) is written, not *إخوان* (which in
  modern usage names a political movement).
- A specific brother or sister: *أخ*, *أخت*.

### Verbs of speaking

- God speaks: **قال** at every level, and his word is *كلمة* (*كلام* for
  speech in general). Not *تكلّم* for every *dabar*; not the Islamic *أوحى*.
- Jesus speaks: **قال**, as everyone else does. *أجاب*, *سأل*, *وبّخ*, *نادى*,
  *صرخ* where the original has them.
- A quotation is introduced with a **colon**: *قال يسوع: «اتبعني».* Arabic
  print uses the colon before direct speech at every length.
- *قائلًا* for the Greek *legōn* is kept at Literal only; Balanced and
  Readable drop it or write *فقال*.

## 6. Names

### Principles

Open Word Bible uses **the established forms of the Arabic church**: the
forms Arab Christians, Orthodox, Catholic and Protestant alike, have read for
generations (they go back to the Van Dyck and the Jesuit Bibles and the
liturgical books before them). The names are not wording and may be used.

How to decide a name:

1. **An established church form exists**: use it, even where it is far from
   the Hebrew or Greek (*يسوع*, *بطرس*, *بولس*, *يوحنا*, *أورشليم*).
   Reconstructed Hebrew forms (*يشوع* for Jesus, *موشيه*) are not used.
2. **The church form and the Qur'anic form differ**: use the church form
   (*يسوع*, not *عيسى*; *يوحنا المعمدان*, not *يحيى*; *إيليا*, not
   *إلياس*; *أليشع*, not *اليسع*; *يونان*, not *يونس*; *أخنوخ*, not
   *إدريس*; *أيوب* is shared). Where the two coincide (*إبراهيم*, *موسى*,
   *هارون*, *داود*, *سليمان*, *نوح*, *آدم*, *حواء*, *يعقوب*, *يوسف*,
   *إسحاق*, *إسماعيل*, *مريم*, *زكريا*, *لوط*), keep the shared form:
   avoiding it would be its own kind of polemic. Section 9 gives the reasons.
3. **Two church forms compete** (Van Dyck and a modern version, or Orthodox
   and Protestant): use the one closer to current standard spelling and to
   the source, and record it in a decision the first time.
4. **No established form** (the minor names of Chronicles, Ezra and
   Nehemiah): transliterate from the Hebrew or Greek by the patterns of the
   established forms: Hebrew consonants to their Arabic cognates
   (*ח* > ح, *ע* > ع, *צ* > ص, *ק* > ق, *ט* > ط, *שׁ* > ش, *שׂ* > س,
   *ת* > ت), final *-ah* as *ـة* for a woman's name and *ـا* otherwise;
   Greek *ph* > ف, *th* > ث, *ch* > خ, *-os* > ـس, *ē* > ي. Note the new
   form in a decision where it first appears in the book, and add it to
   `docs/arabic-terms.md`.
5. **One person, one form, through the whole Bible.** A name shared by
   several people keeps one spelling. An Old Testament name quoted in the New
   Testament keeps its Old Testament form (*إيليا*, *إشعياء*, *أخنوخ*), not
   a form taken from the Greek.

### The common forms

Jesus and the Gospels: *يسوع*, *مريم*, *يوسف*, *يوحنا* (the Baptist and the
apostle), *يوحنا المعمدان*, *سمعان بطرس*, *بطرس*, *أندراوس*, *يعقوب* (the
apostles and the patriarch alike), *زبدي*, *فيلبس*, *برثولماوس*, *توما*,
*متّى*, *نثنائيل*, *يهوذا الإسخريوطي*, *نيقوديموس*, *لعازر*, *مرثا*,
*مريم المجدلية*, *بيلاطس*, *قيافا*, *حنّان*, *باراباس*, *هيرودس*, *زكريا*,
*أليصابات*, *سمعان*, *حنّة*. Acts and the letters: *بولس*, *شاول*,
*برنابا*, *إسطفانوس*, *سيلا*, *تيموثاوس*, *تيطس*, *أبلّوس*, *بريسكلّا*,
*أكيلا*, *كرنيليوس*, *غمالائيل*, *فيلكس*, *فستوس*, *أغريباس*, *فيبي*,
*تيخيكس*, *أنسيمس*, *فليمون*. Places: *أورشليم*, *الجليل*, *اليهودية*,
*السامرة*, *الناصرة*, *بيت لحم*, *كفرناحوم*, *بيت صيدا*, *بيت عنيا*, *نهر
الأردن*, *روما*, *أنطاكية*, *أفسس*, *كورنثوس*, *فيلبي*, *تسالونيكي*,
*أثينا*, *دمشق*, *قيصرية*, *قبرص*, *الإسكندرية*, *مصر*, *بابل*. Peoples:
*اليهود*, *السامريون*, *اليونانيون*, *الرومان*, *الفريسيون*, *الصدوقيون*,
*اللاويون*, *بنو إسرائيل* (L, B) / *الإسرائيليون* (R). The Old Testament
forms are in `docs/arabic-terms.md`.

### Places that still exist

A place with a modern Arabic name keeps the church form where the two
differ in the Bible (*أورشليم*, not *القدس*, which a footnote may give where
the English names the modern city), and uses the modern form where the
church form is the modern form (*دمشق*, *صور*, *صيدا*, *مصر*, *أريحا*,
*الخليل* for Hebron only where the English Readable modernises).

### Book names

The names of `data/books.json` are the established Arabic ones (*التكوين* …
*الرؤيا*), with *مزمور* for one psalm. The letters are named by their
recipients (*رومية*, *كورنثوس الأولى*), as the tables of contents of Arabic
Bibles print them; the site's book names carry no *سفر* or *رسالة*, which
the Arabic Bibles' running heads also leave out.

## 7. Words for the whole Bible

The sixteen key terms of `data/key_terms.json` keep one Arabic word at every
level (with the same exceptions as the English: Readable may say "good news"
for "gospel", and a sense such as "being right with God" at Readable needs a
decision). The Old Testament terms after them are settled for every book.

| Greek / Hebrew (English) | Arabic | Why |
|---|---|---|
| grace (*charis*) | **النعمة** | Key term. The church word in every Arabic Bible. *الفضل* is "favour" and *الإحسان* "kindness": neither is used for *charis*. |
| glory (*doxa*); glorious | **المجد**; *مجيد* | Key term. |
| glorify (*doxazō*) | **مجّد**; *تمجّد* | Key term; the same root as *المجد*, as the Greek has. |
| truth (*alētheia*) | **الحق** | Key term. *حقيقي* for "true" as "real" (*النور الحقيقي*), *صادق* for a true statement or a truthful person. |
| righteousness (*dikaiosynē*) | **البِرّ** (L, B); R may say *الصلاح أمام الله*, *برّره الله*, with a decision | Key term. *البرّ* is the church word and keeps the root of *برّر* (justify). Write the shadda: *البر* without it reads as "land" (*البَرّ* / *البُرّ*). *العدل* where a meaning decision says the sense is God's just judging (Acts 17:31). |
| justify (*dikaioō*) | *برّر* (L, B); *اعتبره بارًّا* (R) | Same root as *البرّ*, which keeps Paul's argument visible. |
| faith (*pistis*) | **الإيمان** | Key term. *الأمانة* where a meaning decision says "faithfulness". |
| believe (*pisteuō*) | **آمن بـ**; *صدّق* for believing a statement | Key term. |
| joy (*chara*) | **الفرح** | Key term. *فرح* for the verb. |
| salvation (*sōtēria*); save | **الخلاص**; *خلّص*, *خَلَص* | Key term. Not *النجاة*, which is rescue from a danger (kept where the Greek means that: Acts 27:34). |
| gospel (*euangelion*) | **الإنجيل** (L, B); **البشارة** (R) | Key term, levels as the English. *الإنجيل* is the Christian word for the gospel message, not only a book; *البشارة* (the good news) at Readable, and at Balanced where the English says "good news". |
| world (*kosmos*) | **العالم** | Key term. *الأرض* for the earth. |
| eternal (*aiōnios*); eternal life | **أبدي**; *الحياة الأبدية* | Key term. |
| sign (*sēmeion*) | **آية** | Key term. The established word for John's signs. Never *معجزة* alone, which means "miracle". (*آية* is also the word for a verse of the Qur'an and, in Arabic Bibles, of the Bible; context keeps them apart.) |
| mystery (*mystērion*) | **السرّ** | Key term. |
| YHWH | `{{divine_name:الرب\|يهوه}}` | Key term (Hebrew). Section 4. |
| steadfast love (*hesed*) | **المحبة الثابتة** (L, B); *محبته التي لا تتغيّر* (R) | *رحمة* is Van Dyck's word, but it is also the word for mercy (*eleos*, *rahamim*), and *hesed* is love that keeps faith. Proposed with *الرحمة* as the main alternative (section 15). |
| faithfulness (*emunah*); truth (*emet*) | *الأمانة*; *الأمانة* or *الحق* by a meaning decision | *hesed* paired with *emet*: *المحبة الثابتة والأمانة*. |
| covenant (*berit*; *diathēkē*) | **العهد** | Every level, both testaments. *الوصية* only where the Greek means a will (Hebrews 9:16–17). |
| holy; sanctify; the saints | *قدّوس* (God), *مقدّس* (things, places); *قدّس*; *القدّيسون* (L, B), *شعب الله* (R) | |
| justice (*mishpat*); righteousness (*tsedaqah*) | *العدل*; *البرّ* | The pair *العدل والبرّ*. *الحق* for *mishpat* as a legal claim. |
| peace (*eirēnē*; *shalom*) | **السلام** | Key term (*eirēnē*). The greeting *eirēnē hymin*: *السلام لكم* (L, B), *سلام عليكم* (R). |
| sin; transgression; iniquity | *الخطيئة* (plural *الخطايا*); *المعصية*; *الإثم* | *خطيئة* with hamza, as standard spelling writes it, not Van Dyck's *خطية*. |
| atone (*kipper*); atonement | *كفّر عن* (L, B); *محا الخطيئة* (R); *الكفّارة* | |
| redeem; redeemer (*go'el*) | *فدى*; *الفادي* (God); *الوليّ* (the kinsman, Ruth) | Ruth: *وليّ* is the kinsman who has the right to redeem, *فادٍ* where the sense is the act. |
| repent; repentance | *تاب*; *التوبة* | Shared with Islam and the established church word. |
| forgive | *غفر* | |
| law (*torah*; *nomos*, the Law of Moses) | **الشريعة** (L, B, R); *شريعة موسى* | The modern versions' word, replacing Van Dyck's *الناموس* (a loan of the Greek *nomos*, now obscure). Readers know *شريعة* as the Islamic word too, but it is the ordinary Arabic word for a revealed law, used by Arab Christians and in the Good News Arabic. *التوراة* for the five books of Moses as a book (*التوراة والأنبياء*). *torah* as "teaching" (Proverbs) is *التعليم*, *الإرشاد*. Lowercase law in general (Romans 7:23) is *قانون*, *ناموس* at L where Paul plays on it. Section 15. |
| the Law and the Prophets | *الشريعة والأنبياء* (L, B); *كتب موسى والأنبياء* (R) | |
| prophet | *نبي*; *الأنبياء* | |
| priest; high priest; Levites | *كاهن*; *رئيس الكهنة*; *اللاويون* | Not *إمام*. |
| sacrifice; offering | **ذبيحة**; *تقدمة*, *قربان* | |
| burnt offering; sin offering; guilt offering; peace offering; grain offering | *المحرقة*; *ذبيحة الخطيئة*; *ذبيحة الإثم*; *ذبيحة السلامة*; *تقدمة الدقيق* | |
| altar | *المذبح* | |
| tabernacle; tent of meeting; ark of the covenant | *المسكن*; *خيمة الاجتماع*; *تابوت العهد* | |
| temple (*hieron*; *naos*; *bayit*, *hekhal*) | *الهيكل* (L, B), *بيت الله* (R); `بيت {{divine_name:الرب\|يهوه}}` | |
| synagogue | *المجمع* (L, B); *مجمع اليهود* (R) | Not *الكنيس* (the modern word for a building in Israel) and not *المعبد*. |
| church, assembly (*ekklēsia*) | *الكنيسة* | *جماعة* for *qahal* in the Old Testament (*جماعة إسرائيل*). |
| elder; overseer; deacon | *شيخ* (*الشيوخ*); *أسقف* (L, B), *راعٍ* (R); *شمّاس* | Jewish elders: *شيوخ الشعب*. |
| apostle; disciple | *رسول*; *تلميذ* | *رسول* is shared with Islam; the context gives the Christian sense. |
| scribes; Pharisees; Sadducees | *الكتبة* (L, B), *معلّمو الشريعة* (R); *الفرّيسيّون*; *الصدّوقيّون* | |
| tax collectors; sinners | *العشّارون* (L), *جباة الضرائب* (B, R); *الخطاة* | |
| Gentiles, nations (*ethnē*; *goyim*) | *الأمم* (L, B); *الشعوب الأخرى*, *غير اليهود* (B, R) | Never *الكفّار* (section 9). |
| angel; demon; unclean spirit | *ملاك*; *شيطان* (L), *روح شرير* (B, R); *روح نجس* (L, B), *روح شرير* (R) | Not *جنّي*. |
| devil; Satan | *إبليس*; *الشيطان* | *إبليس* for *diabolos*; *الشيطان* for *satanas*. |
| heaven; sky | *السماء* (*السماوات*); *السماء* | *ملكوت السماوات*. |
| Gehenna; Hades; Sheol | *جهنّم*; *الهاوية* (L), *عالم الأموات* (B, R); *الهاوية* (L), *عالم الأموات* (B, R) | *جهنّم* is the Arabic form of Gehenna itself. |
| paradise (*paradeisos*) | *الفردوس* | Not *الجنّة* (section 9). |
| Holy Spirit; spirit | *الروح القدس*; *الروح* (God's), *روح* (other); *ruakh* as wind or breath: *ريح*, *نَفَس* | |
| soul (*nephesh*; *psychē*) | *النفس*; *الحياة* (life that can be lost); *نفسه* (self) | By meaning decision. |
| heart | *القلب* | |
| flesh (*sarx*, Paul's moral sense) | *الجسد* (L); *الطبيعة الخاطئة*, *رغبات الإنسان الخاطئة* (B, R) by the meaning decision | |
| Son of Man; Son of God; Son of David | *ابن الإنسان*; *ابن الله*; *ابن داود* | Titles, never under the gender setting. |
| kingdom of God; of heaven | *ملكوت الله*; *ملكوت السماوات* | *ملكوت*, the church word, not *مملكة* (a political kingdom), at every level. |
| Lamb of God | *حمل الله* | |
| the Word (John 1) | *الكلمة* | Every level. |
| Christ | *المسيح* | Section 8: no `christos` span. |
| Messiah (*Messias*, John 1:41; 4:25) | *مسيّا* | The Aramaic word as the Greek transliterates it, then *الذي تفسيره المسيح* as the Greek explains it. |
| baptize; John the Baptist | *عمّد*; *يوحنا المعمدان* | |
| cross; crucify | *الصليب*; *صلب* | |
| resurrection; rise | *القيامة*; *قام* | |
| love (*agapē*; *agapaō*) | *المحبة*; *أحبّ* | *الحبّ* for the Song of Songs and human love. |
| mercy (*eleos*); compassion (*rahamim*) | *الرحمة*; *الرأفة*, *الشفقة* | |
| hope | *الرجاء* (L, B); *الأمل* (R) | |
| wisdom; knowledge | *الحكمة*; *المعرفة* | |
| fear of the LORD | `مخافة {{divine_name:الرب\|يهوه}}` | A fixed phrase. |
| blessed (*makarios*); bless (*barak*, *eulogeō*) | *طوبى لـ* (L, B), *ما أسعد* (R); *بارك* | |
| woe | *الويل لـ* | |
| Amen; Hallelujah; Hosanna | *آمين*; *هللويا*; *أوصنا* | |
| Truly I tell you (*amēn legō hymin*) | *آمين، أقول لكم* (L); *الحق أقول لكم* (B); *أقول لكم الحقّ* (R) | One decision per passage. John's doubled *amēn*: *آمين آمين* (L), *الحق الحق* (B). |
| slave (*doulos*; *ʿeved*) | *عبد* (L, B); *عبد* or *خادم* (R) as the English | As the English: *عبد* at every level where slavery itself is the point. *عبد الله*, `عبد {{divine_name:الرب\|يهوه}}` for God's servants. |
| Sabbath; Passover; Pentecost | *السبت*; *الفصح*; *يوم الخمسين* | |
| Feast of Booths; Unleavened Bread | *عيد المظالّ*; *عيد الفطير* | |
| Rabbi; Teacher | *رابّي*; *معلّم* | |

## 8. Reader settings in Arabic

Settings change wording, never meaning, exactly as in English.

- `divine_name`: `{{divine_name:الرب|يهوه}}`; `يا {{divine_name:رب|يهوه}}` in
  address; `{{divine_name:رب|يهوه}} الجنود`; `السيّد {{divine_name:الرب|يهوه}}`
  for *Adonai YHWH* (section 4).
- `deity_pronoun`: **none**. Arabic has no capitals and no reverent pronoun
  forms (section 4).
- `christos`: **none**. *المسيح* is both "Christ" and "the Messiah" in Arabic:
  the two options would be the same word, and the validator refuses a span
  whose options repeat. Write *المسيح* plainly wherever the English has a
  christos span (*يسوع المسيح*, *المسيح يسوع*), as Hindi writes *मसीह*. A
  decision is not needed; `scripts/settings_parity.py` lists this as by
  design.
- `gender`: an inclusive default where the original means men and women,
  with the traditional form as the alternative. Arabic needs it where its
  masculine plural is heard as men: `{{gender:الإخوة والأخوات|الإخوة}}` for
  *adelphoi* (section 5), `{{gender:أبناء الله وبناته|أبناء الله}}` for
  *huioi theou* where sons and daughters are meant (Galatians 3:26),
  `{{gender:الناس|الرجال}}` for *anēr* meaning people in general. *الناس*,
  *الإنسان*, *كل من*, *من* and *أولاد* are already inclusive and get no span.
  "Fathers" as ancestors: `{{gender:الآباء والأجداد|الآباء}}` only where the
  English has the span; *آباؤنا* alone is usually heard as "our ancestors".
  Never for God, Christ or named men. A rendering decision
  (setting_alternative) records a difference from the English the first time
  in a passage.
- `units`: metric by default, the original unit as the alternative, as in
  every language but English: `{{units:نحو ثلاثة كيلومترات|خمس عشرة غلوة}}`.
  Literal keeps the original unit with no span. Coins: the value in wages by
  default and the coin as the alternative (`{{units:أجرة يوم|دينار واحد}}`).
  This differs from the English (US units) and needs a rendering decision the
  first time in a passage. The units: *ذراع* (cubit, about 45 cm), *شبر*
  (span), *شاقل*, *وزنة*, *مَنًا*, *دينار*, *درهم* (the Greek *drachma*),
  *إيفة*, *حومر*, *بثّ*, *كيل*, *غلوة* (stadion), *ميل*.
- `plural_you` is Spanish only; Arabic has none (section 5). `god_term` is
  Chinese only.
- A setting span holds no quotation marks (`owb/markup.py` checks), and no
  vowel marks.

## 9. Christian Arabic and Islamic usage

Most readers of an Arabic page are Muslims, and Arabic religious vocabulary
is shared by Christians and Muslims: *الله*, *نبي*, *رسول*, *ملاك*, *إيمان*,
*صلاة*, *صوم*, *توبة*, *غفران*, *رحمة*, *آية*, *كتاب*. Arab Christians have
their own long tradition inside that shared language, which is older than
Islam in places. The rules:

1. **Use the church's own vocabulary.** Most of it is shared with Islam, and
   replacing it with rare or invented words to sound "less Islamic" would make
   the text foreign to the Christians it is first for. *الله*, *صلّى*, *صام*,
   *نبي*, *ملاك*, *إيمان* stay.
2. **Do not import Qur'anic names or Islamic technical terms where the church
   has its own.** Not *عيسى* or *عيسى ابن مريم* (*يسوع*), *يحيى*, *إلياس*,
   *يونس*, *إدريس* (section 6); not *الجنّة* for paradise (*الفردوس*), *يوم
   القيامة* for the day of judgment (*يوم الدينونة*; *القيامة* is the
   resurrection), *الآخرة* (*الدهر الآتي*, *الحياة الآتية*), *الوضوء*
   (*الغسل*), *الزكاة* (*الصدقة*), *الحج* (*الصعود إلى أورشليم*, *العيد*),
   *المسجد*, *الجهاد*, *الشهيد* for the Greek *martys* (*شاهد*; *شهيد* only
   where the sense is a martyr's death, Revelation 2:13 by a meaning
   decision), *الأجر* as religious merit (*المكافأة*), *الحواريّون* for the
   apostles (*الرسل*, *التلاميذ*). No *سبحانه وتعالى*, *عزّ وجلّ*, *عليه
   السلام*, *صلّى الله عليه وسلّم*, *بسم الله الرحمن الرحيم*, *إن شاء الله*
   in the text.
3. **Avoid the words that draw a line between religions.** *كافر* / *الكفّار*
   ("infidel") is not used for Gentiles or unbelievers: *الأمم*, *غير
   المؤمنين*, *الذين لا يعرفون الله*. *حلال* and *حرام* are not used for clean
   and unclean: *طاهر* and *نجس* (L, B), *طاهر* and *غير طاهر* (R). *المشركون*
   is not used for the nations or idolaters: *عبدة الأوثان*.
4. **Shared words keep their biblical sense.** Where a word is shared but its
   Islamic sense differs (*نبي*, *رسول*, *كتاب*, *وحي*, *الإنجيل*,
   *التوراة*, *شريعة*), the context gives the Christian sense; no footnote is
   needed unless the English has one. *ابن الله* is translated as the Greek
   says it, at every level, with no softening.
5. **No polemic, no imitation.** The wording is not chosen to answer or
   contradict Islam, and not chosen to imitate Qur'anic style or *saj'*
   (rhymed prose) for Muslim readers. A decision that turns on an Islamic
   overtone says so plainly, in neutral terms.

## 10. Punctuation, spacing and typography

- **Punctuation**: the Arabic comma **،**, semicolon **؛** and question mark
  **؟**; the full stop **.**, colon **:** and exclamation mark **!** are the
  common characters. No space before any of them, one after. The Latin comma
  and question mark are errors.
- **Quotation marks**: **« »** outside and **“ ”** inside, typed in the data
  as French and Spanish type them (in logical order: « opens, » closes; the
  page shows them mirrored), with **no space inside the guillemets**:
  *قال: «اتبعني».* The sentence's full stop goes after the closing mark when
  the quotation ends the sentence and has no mark of its own; a question or
  exclamation that belongs to the quotation goes inside it (*«من أنت؟»*). A
  quotation that runs over several sentences opens in the first record and
  closes in the last, as in English. Arabic has no apostrophes; do not type
  `'` or `’`.
- **Prefixes are joined**: *و*, *ف*, *ب*, *ك*, *ل* and the article are
  written joined to the next word (*والرب*, *فقال*, *بالإيمان*), never with a
  space after them. *و* starting a sentence is normal Arabic, and is kept at
  every level where the Hebrew *wa-* or Greek *kai* links the narrative;
  Readable may start a new sentence without it.
- **Numbers**: a number that is one or two words is written in words, with
  the rules of agreement (*اثنا عشر تلميذًا*, *خمسة آلاف رجل*, *ثلاثمئة
  ذراع*); *مئة*, not the old *مائة*. A number that would be long in words is
  written in digits (*930 سنة*, *603550 رجلًا*), with **Western digits
  (0–9)**, the digits of the site's verse numbers and references (section
  15 asks whether to show Arabic-Indic ٠–٩ instead). A list of counts in one
  verse is uniform. A sentence does not begin with digits.
- **Clock time**: Literal keeps the Greek count (*الساعة السادسة*); Balanced
  and Readable give the modern time (*نحو الظهر*, *نحو الثانية عشرة
  ظهرًا*), with a decision, as the English does.
- **Dates**: months by number at Literal (*الشهر الأول*); Balanced and
  Readable may add the Hebrew name where the English does (*شهر نيسان*).
- **Brackets**: Literal's [ ] for supplied words; parentheses ( ) as in the
  English. Both are typed in logical order and the page mirrors them.
- **No italics**: Arabic has no italic; the site turns them off.

## 11. Poetry, headings and the Old Testament

- **Lines.** Poetry is set in lines, as `docs/english-style.md` section 10
  describes: mark each break inside a verse with `\q `, following the Hebrew
  accents' division (`python3 scripts/poetry_lines.py` prints it), at every
  level. Arabic places its own breaks; a verse start is always a line start.
  Do not rhyme.
- **Psalm titles** are verse 1, as in the Hebrew: *مزمور لداود* (L, B),
  *مزمور كتبه داود* (R). Musical terms the English transliterates are
  transliterated (*سلاه*, *قصيدة* for *maskil*, *مذهبة* for *miktam* as the
  English decision explains them).
- **The psalmist** speaks to God as *أنت* and *يا رب*.
- **Old Testament narrative**: the *wayyiqtol* chain is *و* + perfect at
  Literal (*وقال ... وذهب ... وأخذ*), the natural Arabic narrative chain, and
  *ثم* or *ف* where the Hebrew sequence is sharp. Balanced and Readable vary
  the connectives (*ف*, *ثم*, *وبعد ذلك*, a new sentence) where the chain
  would be monotonous.
- **Kings and courts**: section 5.
- **Section headings and summaries.** Where a book's
  `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json` has the
  languages beside English, add `"ar"` beside them as each book is drafted,
  written from Open Word Bible's own Arabic wording. They are AI drafts until
  reviewed, and never the headings of Van Dyck or the Good News Arabic.

## 12. Recurring formulas

One form each, at every book; the first record of a passage that uses one
notes it once.

| Source (English) | Literal | Balanced | Readable |
|---|---|---|---|
| Thus says the LORD (*koh amar YHWH*) | *هكذا قال {{divine_name:الرب\|يهوه}}* | as L | *هذا ما يقوله {{divine_name:الرب\|يهوه}}* |
| declares the LORD (*ne'um YHWH*) | *يقول {{divine_name:الرب\|يهوه}}* | as L | as L |
| The word of the LORD came to ... | *وكانت كلمة {{divine_name:الرب\|يهوه}} إلى ...* | *وجاءت كلمة {{divine_name:الرب\|يهوه}} إلى ...* | *وكلّم {{divine_name:الرب\|يهوه}} ...* |
| I am the LORD | *أنا {{divine_name:الرب\|يهوه}}* | as L | as L |
| behold (*hinneh*, *idou*) | *هوذا* | *ها*, *انظر*, or left out where it only marks attention | left out, or *انظروا* |
| and it came to pass (*wayehi*) | *وكان* | left out, or a time clause (*وفي تلك الأيام*) | as B |
| son of man (Ezekiel's address) | *يا ابن آدم* | as L | *يا إنسان* |
| answered and said | *أجاب وقال* | *أجاب* | as B |
| lifted up his eyes and saw | *رفع عينيه ونظر* | *نظر فرأى* | *رأى* |
| fell on his face | *سقط على وجهه* | *سجد إلى الأرض* | *انحنى إلى الأرض* |
| all the days of his life | *كل أيام حياته* | as L | *طوال حياته* |
| to this day | *إلى هذا اليوم* | as L | *حتى اليوم* |
| Fear not | *لا تخف* (*لا تخافوا*, *لا تخافي*) | as L | as L |
| Woe to you | *الويل لكم* | as L | *ما أتعسكم* |
| grace and peace to you | *نعمة لكم وسلام* | *النعمة والسلام لكم* | *أرجو لكم النعمة والسلام* |
| As the LORD lives | *حيّ هو {{divine_name:الرب\|يهوه}}* | as L | *أُقسم بـ{{divine_name:الرب\|يهوه}} الحيّ* |

## 13. Search

Arabic is written with spaces, so site search indexes it word by word.
Postgres ships an Arabic Snowball stemmer, which strips the article, the
joined *و*, *ف*, *ب*, *ك*, *ل* and the common suffixes, so *والإيمان* finds
*الإيمان* (search uses `owb_arabic`, translation migration `0014`). The
search text is normalised so that a reader's spelling finds the drafts'
(`backend/translation/search.py` `normalize_arabic`): short vowels and the
shadda are removed, *أ إ آ* are read as *ا*, final *ى* as *ي*, *ة* as *ه*,
and the Persian *ی* and *ک* as *ي* and *ك*. This does not affect drafting,
but a term written two ways (*خطيئة* / *خطية*) is two words to search: keep
the glossary's spelling throughout.

## 14. Drafting book by book

Each book is drafted the same way, so the books agree with each other
without a later harmonising pass.

1. **Check the book is free** (`check-book-before-translating` skill) and
   that the English is drafted: Arabic is drafted from records that already
   have their meaning decisions.
2. **Read this file, the book's section of `docs/arabic-terms.md`, and the
   book's English terms notes.** The glossary's form is the form; a drafter
   does not choose another spelling of a name or another word for a key term
   in one book.
3. **Draft each record at L, then B, then R**, from the Hebrew or Greek,
   the gloss and the meaning decisions. Keep the English record's verse
   markers, line breaks and quotations (section 2).
4. **Compare each familiar verse with Van Dyck and the Good News Arabic**
   and rewrite any clause that matches (section 1). Do not open them for
   unfamiliar verses: the check is for memory's pull, not a source.
5. **Write the decisions** (section 2): the first use in the book of a
   glossary choice, a name not in the glossary, every setting span that
   differs from the English, every dual or feminine form the original does
   not mark.
6. **Add new names** to the book's section of `docs/arabic-terms.md` in the
   same pull request, by the rules of section 6.
7. **Before the pull request, search the book's Arabic** for what this file
   excludes, at every level: *لل{{divine_name* and *ل{{divine_name* (the
   article rule of section 4), *عيسى*, *يحيى*, *إلياس*, *يونس*, *الجنّة*,
   *الكفّار*, *حلال*, *حرام*, *سبحانه*, *الناموس* (outside Literal's
   Romans 7), *خطية*, *مائة*, *إصحاح*, *هوذا* (outside Literal), the
   dialect words of section 3, a Latin comma or question mark, a space
   inside « », a `deity_pronoun` or `christos` span, and *تطويل*.
8. **Headings and summaries** for the book in Arabic, from our own text
   (section 11).
9. One pull request per book; `scripts/check.sh` must pass.

## 15. Defaults for the founder to confirm

Each of these decides the wording of thousands of verses. Drafting follows
them as written; the founder confirms or changes each once, and the outcome
is recorded under a "Settled" heading at the top of this file, as the
Vietnamese and Korean briefs do. Changing one later means revising every
book drafted under it, so the earlier they are confirmed the cheaper.

1. **YHWH**: `{{divine_name:الرب|يهوه}}` by default, with the article rule
   (no *لـ* before the span), `يا {{divine_name:رب|يهوه}}` in address,
   *رب الجنود*, *السيّد الرب* for *Adonai YHWH*.
2. **God is *الله*** (*إله* with a suffix) at every level, with no setting.
3. **No `deity_pronoun` and no `christos` spans** (sections 4 and 8).
4. **Register**: Modern Standard Arabic at every level, no dialect;
   Readable is simple MSA, not Egyptian or Levantine.
5. **No full vocalisation**; marks only to prevent a misreading (section 3).
6. **The Law is *الشريعة***, not Van Dyck's *الناموس*; *التوراة* for the
   books of Moses.
7. ***hesed* is *المحبة الثابتة***, keeping *الرحمة* for mercy; the
   alternative is Van Dyck's *الرحمة* for both.
8. **Brothers**: `{{gender:الإخوة والأخوات|الإخوة}}`, inclusive by default.
9. **Names**: the established church forms, church forms over Qur'anic forms
   where they differ (*يسوع*, *يوحنا*, *إيليا*, *يونان*).
10. **Digits**: Western digits (0–9) in the text, as in the verse numbers.
    The alternative is Arabic-Indic digits (٠–٩), which most readers in Egypt,
    the Levant, Iraq and the Gulf read in print; that would be a display step
    in the build and the reader for verse numbers too, never a change to
    records or references (`docs/adding-a-language.md` section 11).
11. **Level names**: *حرفية*, *متوازنة*, *ميسّرة*.

## 16. Status

An Arabic rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.
