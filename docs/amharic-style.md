# Amharic style guide

How Open Word Bible drafts Amharic (አማርኛ). It sits on top of
`docs/english-style.md`, which still governs everything that is not about
wording (sources, one record per sentence, the three levels, decisions,
status), and of the book's terms notes (`docs/john-terms.md` and the
others), whose book-wide choices hold in Amharic unless this file says
otherwise. Where this file and the founder's Translation Charter disagree,
the Charter wins; fix this file.

**Status: proposed, awaiting a native Amharic reviewer.** Every Amharic
record is `ai_draft`. The level names, the grammar labels in `owb/morph.py`,
the forms of address and the key terms below are first proposals, and a
reviewer is expected to change some of them.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Amharic says that meaning in its own
  way.
- **Never reproduce the wording of a copyrighted Amharic Bible**: the 1954
  E.C. (1962) Bible and its 1980 revision (Bible Society of Ethiopia), the
  New Amharic Standard Version (አዲሱ መደበኛ ትርጉም), the Amharic Living Bible,
  the Easy-to-Read Version and others. The 1962 Bible shapes how most readers
  remember familiar verses, and its Ge'ez-flavoured forms are out of place in
  a modern translation. Draft from the Greek and the gloss, then rewrite any
  sentence that matches a well-known version for more than a short common
  phrase.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied
  from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"am": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, in
  every Amharic level. **(checked)** Amharic is verb-final, so a clause often
  wants to move across a verse boundary; keep each verse's own content after
  its marker, restructuring the sentence if needed (two Amharic sentences for
  one Greek one is fine), and where that is impossible say so in a rendering
  decision.
- The meaning decisions are shared: do not change them. Amharic needs only
  its own rendering decisions, with ids `r-am-1`, `r-am-2`, ... counted from 1
  in each record, `"layer": "rendering"`, `"language": "am"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions; the Amharic words under discussion are
  quoted in it ("\"ደቀ መዛሙርት\" rather than \"ተማሪዎች\""). The site tells
  Amharic readers that notes are in English for now.
- Write an Amharic rendering decision where Amharic had to choose and a
  reader might ask why: a word chosen against a familiar alternative, a form
  of address, a structure Amharic cannot copy, a setting span that differs
  from the English one, a term settled here for the whole book (once, where
  it first appears in a passage). Do not repeat the English rendering
  decisions. Typical density: zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language, so each Amharic level must open and close the same
  quotations, in the same order, as the English one: no quotation added,
  dropped, merged or split. A sentence that begins or ends inside a speech
  begins or ends inside it in Amharic too. (The validator checks that
  the quotations the red letters name exist.)

## 3. The three levels in Amharic

The level names on the site are **ቃል በቃል** (Literal), **ሚዛናዊ** (Balanced)
and **ቀላል** (Readable).

**Literal (OWB-L).** Keeps the Greek's words, their grammar (participles,
genitives, the order of clauses where Amharic allows) and its repetitions.
Amharic is verb-final, so the Greek word order cannot be followed; Literal
keeps the Greek's units and the sequence of its clauses instead. Words
Amharic needs but the Greek lacks go in [square brackets]. Prefixes,
suffixes and the object markers on the verb are grammar, not added words,
and are not bracketed. Keep the historic present (ይላል, ይመጣል) where the
Greek has it.

**Balanced (OWB-B).** Careful standard modern written Amharic, the register
of a good public reading. Tracks the Greek closely; no brackets. Church words
of Ge'ez origin stay where they are the living word for the thing
(መንግሥተ ሰማያት, ቤተ ክርስቲያን, ሊቀ ካህናት), not where a plain Amharic word
says the same.

**Readable (OWB-R).** Plain everyday Amharic for new and young readers:
short sentences, common words, Amharic words over Ge'ez ones where both are
current (የሰማይ መንግሥት beside መንግሥተ ሰማያት). Explains idioms and may make
explicit what the context implies, as the English Readable does, with a
decision where the English has one.

## 4. Forms of address and honorifics

Amharic distinguishes the familiar *you* (አንተ, አንቺ) from the respectful
one (እርስዎ), and a respectful third person (እሳቸው, the plural verb) from the
plain one (እሱ). The choices below hold through the book, so a scene does not
change relationship between verses.

- **God and Jesus in the narrative** take the plain singular at every level
  (ኢየሱስ መለሰ፤ እግዚአብሔር አለ), as in the Ethiopian Bible tradition: the
  honorific plural is a social courtesy, and in Scripture its absence is not
  a slight. Respect is carried by the words used of them.
- **People speaking to God and to Jesus** use አንተ, from disciples,
  petitioners and opponents alike: the Bible's familiar address, also in
  prayer. A reviewer may move petitioners who do not know him (a centurion,
  an official) to እርስዎ, with a decision.
- **Jesus speaking** to one person: አንተ / አንቺ; to more than one: እናንተ.
  The Greek's singular and plural *you* come through without a setting.
- **Ordinary people among themselves**: as the scene requires; አንተ between
  equals and to inferiors, እርስዎ to rulers (Herod, Pilate) where the speaker
  is a subordinate.

## 5. Spelling, names and typography

- **Script.** Text is in the Ethiopic script (ፊደል) only: no Latin letters,
  no Greek. Words are separated by ordinary spaces, not by the old word
  divider ፡.
- **Punctuation.** The full stop is ። (U+1362), the comma ፣ (U+1363), the
  semicolon ፤ (U+1364). The question mark is `?`, the exclamation mark `!`.
  Direct speech is introduced with ፦ (U+1366) when the verb of saying comes
  first ("እንዲህ አላቸው፦ «...»"), or follows the quotation as Amharic
  normally has it («...» አላቸው።).
- **Quotation marks** are guillemets, « » outside and “ ” for a quotation
  inside a quotation, with no spaces inside the marks (as Spanish). **A
  sentence still ends with its own mark inside the closing guillemet**
  («...ተከተሉኝ።»), so the verse reads as a sentence on its own.
- **Spelling.** Amharic has letters that sound alike (ሀ ሐ ኀ; ሰ ሠ; አ ዐ;
  ጸ ፀ). Use the established church spelling for names and key terms
  (እግዚአብሔር, ኃጢአት, ዓለም, ሥጋ, ጸጋ, ጸሎት, ቅዱስ, ሐዋርያ, ሰማይ) and the
  common standard spelling otherwise, and keep one spelling of each word
  through a book. Mark gemination and vowel length only through the letters
  (no diacritics).
- **Numbers** are written in Arabic figures where a figure is wanted (12,
  5000); short numbers are spelled out in running text (ሁለት ሰዎች). Ge'ez
  numerals (፩ ፪ ፫) are not used.
- **Proper names** in their established Amharic Bible forms: ኢየሱስ, ማርያም,
  ዮሴፍ, ዮሐንስ, መጥምቁ ዮሐንስ, ስምዖን ጴጥሮስ, እንድርያስ, ያዕቆብ, ዘብዴዎስ,
  ፊልጶስ, በርተሎሜዎስ, ቶማስ, ማቴዎስ, እልፍዮስ, ታዴዎስ, ቀነናዊው ስምዖን, የአስቆሮቱ
  ይሁዳ, ሄሮድስ, ሄሮድያዳ, ጲላጦስ, ቀያፋ, በርባን, መግደላዊት ማርያም, ኒቆዲሞስ,
  አልዓዛር, ማርታ, ሙሴ, ኤልያስ, ኢሳይያስ, ኤርምያስ, ዮናስ, ዳንኤል, ዳዊት,
  ሰሎሞን, አብርሃም, ይስሐቅ, ያዕቆብ, ኖኅ, ቄሳር; places: ኢየሩሳሌም, ገሊላ,
  ይሁዳ (Judea), ሰማርያ, ናዝሬት, ቤተ ልሔም, ቅፍርናሆም, ቤተ ሳይዳ, ኮራዚን,
  ዮርዳኖስ, ግብፅ, ሶርያ, ጢሮስ, ሲዶና, ሰዶም, ገሞራ, ኢያሪኮ, ቢታንያ,
  ቤተ ፋጌ, ደብረ ዘይት (the Mount of Olives), ጌቴሴማኒ, ጎልጎታ, ሮም; peoples:
  አይሁድ, ሳምራውያን, ሮማውያን, ግሪኮች, አሕዛብ.
- Clock time: Literal keeps the Greek count ("በስድስተኛው ሰዓት"); Balanced and
  Readable give the time as Ethiopians count it from dawn where that matches
  the Greek count, or plainly ("እኩለ ቀን"), with a decision.

## 6. Words for the whole of the New Testament

| Greek (English) | Amharic | Notes |
|---|---|---|
| God | እግዚአብሔር | Every level. *አምላክ* for "a god", for "my God, your God" (አምላኬ, አምላካችሁ) and where *theos* is a predicate ("the Word was God": አምላክ). |
| Lord (*kyrios*, of God or Jesus) | ጌታ | "Lord!" as an address: ጌታ ሆይ (L), ጌታ ሆይ / ጌታዬ (B, R). "Sir" to a stranger: ጌታዬ. |
| Jesus | ኢየሱስ | |
| Christ | `{{christos:ክርስቶስ\|መሲሕ}}` | With the name: `ኢየሱስ {{christos:ክርስቶስ\|መሲሕ}}`. *መሲሕ* plainly, no setting, where the Greek has *Messias* (John 1:41; 4:25). |
| Holy Spirit; the Spirit | መንፈስ ቅዱስ; መንፈስ | |
| kingdom of heaven | መንግሥተ ሰማያት (L, B); የሰማይ መንግሥት (R) | One decision per passage where it first appears. |
| kingdom of God | የእግዚአብሔር መንግሥት | |
| Son of Man | የሰው ልጅ | A title, every level. Never under the gender setting. |
| Son of God; Son of David | የእግዚአብሔር ልጅ; የዳዊት ልጅ | |
| disciple(s) | ደቀ መዝሙር; ደቀ መዛሙርት | Every level. |
| apostle | ሐዋርያ (pl. ሐዋርያት) | |
| prophet | ነቢይ (pl. ነቢያት) | |
| the Law; the Law and the Prophets | ሕግ; ሕግና ነቢያት | *ኦሪት* where the five books of Moses are meant by name. |
| scribes | ጸሐፍት (L); የሕግ መምህራን (B, R) | They were teachers of the Law, not copyists. |
| Pharisees; Sadducees | ፈሪሳውያን; ሰዱቃውያን | |
| chief priests; high priest | የካህናት አለቆች; ሊቀ ካህናት | |
| elders | ሽማግሌዎች | *የሕዝቡ ሽማግሌዎች* where the Greek says so. |
| tax collectors; sinners | ቀራጮች; ኃጢአተኞች | |
| Gentiles, nations | አሕዛብ (L, B); ሌሎች ሕዝቦች / አይሁድ ያልሆኑ (R) | |
| synagogue; temple | ምኩራብ; ቤተ መቅደስ | |
| Sabbath; Passover | ሰንበት; ፋሲካ | |
| church, assembly | ቤተ ክርስቲያን | Of the believers (Matthew 16:18; 18:17). |
| repent; repentance | ንስሓ ግቡ; ንስሓ | |
| sin | ኃጢአት | |
| believe; faith | ማመን; እምነት | Keep the verb at every level. |
| grace | ጸጋ | Key term: the same word at every level. |
| truth | እውነት | Key term. |
| glory; glorify | ክብር; ማክበር | Key term. |
| peace | ሰላም | Key term. |
| righteousness; righteous | ጽድቅ; ጻድቅ | Key term. Readable may say ትክክል የሆነውን where the sense is conduct, with a decision. |
| gospel, good news | ወንጌል (L, B); የምሥራች (R) | |
| baptize; John the Baptist | ማጥመቅ; መጥምቁ ዮሐንስ | |
| angel | መልአክ (pl. መላእክት) | |
| demon; unclean spirit | ጋኔን (pl. አጋንንት); ርኩስ መንፈስ | |
| devil; Satan | ዲያብሎስ; ሰይጣን | |
| heaven; Gehenna; Hades | ሰማይ; ገሃነም; ሲኦል | "the heavens" ሰማያት (L), ሰማይ (B, R). |
| Truly I tell you (*amēn*) | እውነት እላችኋለሁ (L, B); እውነቱን እነግራችኋለሁ (R) | One decision per passage. |
| crowd | ሕዝብ, ብዙ ሕዝብ | |
| hypocrites | ግብዞች | |
| Woe to you | ወዮላችሁ | |
| eternal life | የዘላለም ሕይወት | |
| cross; crucify | መስቀል; መስቀል (ሰቀሉት) | |
| bread, loaf | እንጀራ (bread as food: the Lord's Prayer, "not by bread alone"); ዳቦ (loaves: the feedings, the Last Supper) | A decision where it first appears. |
| Amen; Hosanna | አሜን; ሆሣዕና | |
| Rabbi; Teacher | ረቢ; መምህር | |
| slave (*doulos*) | ባሪያ | Every level; አገልጋይ where only service is the point, with a decision. |

## 7. Reader settings in Amharic

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: the Ethiopic script has no capital letters, so the
  setting has nothing to change and the Amharic text has **no** deity_pronoun
  spans. The first record of a passage says so once where the English has a
  span.
- `christos`: `{{christos:ክርስቶስ|መሲሕ}}`, and
  `ኢየሱስ {{christos:ክርስቶስ|መሲሕ}}`. Amharic has no article, so both read
  naturally at every level. Suffixes go outside the span only where both
  options take the same form; otherwise put the whole word in each option
  (`{{christos:ክርስቶስን|መሲሑን}}`).
- `gender`: Amharic nouns for people are often already inclusive (ሰው,
  ሰዎች, ማንም, ልጆች). Use a span only where Amharic really has two ways of
  saying the same thing: `{{gender:ወንድሞችና እኅቶች|ወንድሞች}}` for *adelphoi*
  meaning believers, `{{gender:ሰዎች|ወንዶች}}` where *andres* means people in
  general.
- `units`: metric by default, the original unit as the alternative, as in
  French and Swahili: `{{units:3 ኪሎ ሜትር ያህል|15 ምዕራፍ}}`. Literal keeps the
  original unit. This differs from the English (US units) and needs a
  rendering decision.

## 7a. The Old Testament and poetry

- **The divine name** (YHWH) is `{{divine_name:እግዚአብሔር|ያህዌ}}` at every
  level, the name as Ethiopian Bibles have long given it, with the name as
  most scholars think it was said as the alternative (as the English
  "Yahweh"). Suffixes go inside each option (`{{divine_name:እግዚአብሔርን|ያህዌን}}`).
  *Adonai* ("Lord") is ጌታ; *Elohim* is አምላክ ("God", "a god"), or
  እግዚአብሔር where the text is plainly about the one God and YHWH does not
  stand beside it; the first record of a book says which.
- **Lines.** A psalm is set in lines, as `docs/english-style.md` section 10
  describes: mark each break inside a verse with `\q `, following the
  Hebrew accents' division (`python3 scripts/poetry_lines.py` prints it),
  at every level. Amharic places its own breaks; a verse start is always a
  line start.
- **Titles.** A psalm's title is verse 1, as in the Hebrew: የዳዊት መዝሙር
  (L, B), ዳዊት የዘመረው መዝሙር (R).

## 8. Status

An Amharic rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.
