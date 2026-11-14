# Hindi style guide

How Open Word Bible drafts Hindi (हिन्दी). It builds on
`docs/english-style.md`, which still covers everything that is not about
wording: sources, one record per sentence, the three levels, decisions and
status. It also builds on each book's terms notes (`docs/john-terms.md` and
the others). Their book-wide choices hold in Hindi unless this file says
otherwise. Where this file and the founder's Translation Charter disagree,
the Charter wins; fix this file.

**Status: proposed, awaiting a native Hindi reviewer.** Every Hindi record
is `ai_draft`. The level names, the grammar labels in `owb/morph.py`, the
forms of address and the key terms below are first proposals, and a
reviewer is expected to change some of them.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Hindi says that meaning in its own
  way.
- **Never reproduce the wording of a copyrighted Hindi Bible**: the Hindi
  Old Version (Bible Society of India) and its revisions, the Hindi Common
  Language Bible, the Easy-to-Read Version (ERV-HI), the Pavitra Bible and
  others. The Old Version shapes how most Hindi Christians remember
  familiar verses, and its older forms (तू to everyone, archaic verbs) are
  out of place in a modern translation. Draft from the Greek and the gloss,
  then rewrite any sentence that matches a well-known version for more than
  a short common phrase.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied
  from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"hi": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, in
  every Hindi level. **(checked)** Hindi is verb-final, so a clause often
  wants to move across a verse boundary. Keep each verse's own content after
  its marker, restructuring the sentence if needed (two Hindi sentences for
  one Greek one is fine). Where that is impossible, say so in a rendering
  decision.
- The meaning decisions are shared: do not change them. Hindi needs only
  its own rendering decisions, with ids `r-hi-1`, `r-hi-2`, ... counted from 1
  in each record, `"layer": "rendering"`, `"language": "hi"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions. Quote the Hindi words under discussion
  ("\"चेले\" rather than \"शिष्य\""). The site tells Hindi readers that
  notes are in English for now.
- Write a Hindi rendering decision where Hindi had to choose and a reader
  might ask why. That covers a word chosen over a familiar alternative, a
  form of address, a structure Hindi cannot copy, a setting span that
  differs from the English one, or a term settled here for the whole book
  (note it once, where it first appears in a passage). Do not repeat the
  English rendering decisions. Typical density: zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language. So each Hindi level must open and close the same
  quotations, in the same order, as the English one: no quotation added,
  dropped, merged or split. A sentence that begins or ends inside a speech
  begins or ends inside it in Hindi too.

## 3. The three levels in Hindi

The level names on the site are **शाब्दिक** (Literal), **संतुलित**
(Balanced) and **सरल** (Readable).

**Literal (OWB-L).** Keeps the Greek's words, their grammar (participles,
genitives, the order of clauses where Hindi allows) and its repetitions.
Hindi is verb-final with postpositions, so the Greek word order cannot be
followed. Literal keeps the Greek's units and the sequence of its clauses
instead. Words Hindi needs but the Greek lacks go in [square brackets].
Postpositions (ने, को, से, में, का/के/की) and verb endings are grammar, not
added words, and are not bracketed. Keep the historic present (कहता है,
आता है) where the Greek has it.

**Balanced (OWB-B).** Careful standard modern written Hindi, the register
of a good public reading. Tracks the Greek closely; no brackets. Use the
established Hindi church words where they are the living word for the
thing (बपतिस्मा, सुसमाचार, अनुग्रह, कलीसिया). Avoid heavily Sanskritised
words where a common Hindi word says the same: Balanced sounds like an
educated speaker, not like a commentary.

**Readable (OWB-R).** Plain everyday Hindi (the Hindustani of ordinary
speech) for new and young readers: short sentences and common words. Where
both are current, prefer the everyday word to the learned one (सच beside
सत्य, नबी beside भविष्यद्वक्ता). Explains idioms and may make explicit what
the context implies, as the English Readable does, with a decision where
the English has one.

## 4. Forms of address and honorifics

Hindi has three levels of *you*: intimate तू, familiar तुम and respectful
आप. Third persons are plain (वह, उसने) or honorific (वे, उन्होंने, with
plural agreement). The choices below hold through the book, so a scene does
not change relationship between verses.

- **God and Jesus in the narrative** take the honorific third person at
  every level: "यीशु गलील में आए", "उन्होंने उनसे कहा". This is ordinary modern
  Hindi for a respected person, not an addition to the text. Keep it
  consistent within a sentence, and avoid a verb form that leaves a plural
  honorific subject unclear among other plurals: name the subject
  ("यीशु ने") where that helps.
- **People speaking to Jesus** say आप, from disciples, petitioners and
  opponents alike. This is how anyone in the scene would address a
  teacher.
- **People speaking to God**, and Jesus praying to the Father, say तू
  (तेरा, तुझे). This is the intimate address of Hindi devotion, the way
  people pray in Hindi. It is not disrespect.
- **Jesus speaking** to one person or to many says तुम. The Greek's
  singular and plural *you* both come out as तुम, with तुम लोग or तुम सब
  where the plural must be clear. A Hindi decision says so once per passage
  where the number matters.
- **Ordinary people among themselves** use the address the scene calls for:
  तुम between equals and to inferiors, आप to rulers (Herod, Pilate) and from
  slaves to their master. A parable's master who stands for God is still
  addressed as the scene requires, with a decision.

## 5. Spelling, names and typography

- **Script.** Hindi is written in Devanagari only, with no Latin letters
  and no Greek. Use standard modern Hindi spelling (Central Hindi
  Directorate): the anusvara for a nasal before a consonant, with the fixed
  exceptions in section 7b, and the nukta in loanwords where standard Hindi
  writes it (ज़मीन, फ़ैसला). Biblical names keep their
  established Bible spelling (below).
- **Punctuation.** The full stop is the danda । (U+0964). The comma, `?`
  and `!` are as in English. Quotation marks are typed straight in the
  records, `"` outside and `'` for a quotation inside a quotation, as in the
  English, Portuguese and Korean records; the site shows them curly (“ ”,
  ‘ ’). Curly marks typed in a record confuse the red letters
  (`owb/markup.py` reads a sentence that begins inside a speech only from
  straight marks or guillemets). **A sentence still ends with its own mark
  inside the closing quotation mark** ("...मेरे पीछे हो लो।"), so the verse
  reads as a sentence on its own.
- **Numbers.** Write figures in international (Arabic) digits (12, 5000),
  not Devanagari digits. Spell out short numbers in running text
  (दो आदमी).
- **Proper names** take their established Hindi Bible forms: यीशु, मरियम,
  यूसुफ़, यूहन्ना, यूहन्ना बपतिस्मा देनेवाला, शमौन पतरस, अन्द्रियास, याकूब,
  जब्दी, फिलिप्पुस, बरतुल्मै, थोमा, मत्ती, हलफई, तद्दै, शमौन कनानी, यहूदा
  इस्करियोती, हेरोदेस, हेरोदियास, पिलातुस, कैफ़ा, बरअब्बा, मरियम मगदलीनी,
  नीकुदेमुस, लाज़र, मार्था, मूसा, एलिय्याह, यशायाह, यिर्मयाह, योना,
  दानिय्येल, दाऊद, सुलैमान, अब्राहम, इसहाक, नूह, कैसर. Places: यरूशलेम,
  गलील, यहूदिया, सामरिया, नासरत, बैतलहम, कफ़रनहूम, बैतसैदा, खुराज़ीन, यरदन,
  मिस्र, सीरिया, सूर, सैदा, सदोम, अमोरा, यरीहो, बैतनिय्याह, बैतफ़गे, जैतून
  पहाड़ (the Mount of Olives), गतसमनी, गुलगुता, रोम. Peoples: यहूदी, सामरी,
  रोमी, यूनानी.
- **Clock time.** Literal keeps the Greek count ("छठे घंटे"). Balanced
  and Readable give the time as a modern reader counts it ("दोपहर के
  बारह बजे"), with a decision.

## 6. Words for the whole of the New Testament

| Greek (English) | Hindi | Notes |
|---|---|---|
| God | परमेश्वर | Every level. *ईश्वर* is not used for the God of Israel; *देवता* for "a god", *हमारा परमेश्वर* for "our God". |
| Lord (*kyrios*, of God or Jesus) | प्रभु | "Lord!" as an address: हे प्रभु. "Sir" to a stranger: श्रीमान (L), महोदय / साहब (B, R) as the scene requires. |
| Jesus | यीशु | |
| Christ | मसीह | Every level, no setting (section 7). With the name: यीशु मसीह. |
| Holy Spirit; the Spirit | पवित्र आत्मा; आत्मा | Masculine agreement where the Spirit acts as a person ("पवित्र आत्मा उतरा"), as Hindi Bibles have it. |
| kingdom of heaven | स्वर्ग का राज्य | Every level. |
| kingdom of God | परमेश्वर का राज्य | |
| Son of Man | मनुष्य का पुत्र | A title, every level. Never under the gender setting. |
| Son of God; Son of David | परमेश्वर का पुत्र; दाऊद का पुत्र | "दाऊद की सन्तान" is not used: it hides the royal title. |
| disciple(s) | चेला; चेले | Every level: the everyday word for a teacher's follower. |
| apostle | प्रेरित | |
| prophet | भविष्यद्वक्ता (L, B); नबी (R) | One decision per passage where it first appears. |
| the Law; the Law and the Prophets | व्यवस्था; व्यवस्था और भविष्यद्वक्ता | Readable may say मूसा की व्यवस्था where Moses' Law is meant. |
| scribes | शास्त्री (L); व्यवस्था के शिक्षक (B, R) | They were teachers of the Law, not copyists. |
| Pharisees; Sadducees | फ़रीसी; सदूकी | |
| chief priests; high priest | प्रधान याजक; महायाजक | |
| elders | पुरनिए (L); बुज़ुर्ग अगुवे (B, R) | |
| tax collectors; sinners | महसूल लेनेवाले (L); कर वसूलनेवाले (B, R); पापी | |
| Gentiles, nations | अन्यजाति (L, B); ग़ैर-यहूदी (R) | "the nations": जातियाँ. |
| synagogue; temple | आराधनालय; मन्दिर | |
| Sabbath; Passover | सब्त; फ़सह | |
| church, assembly | कलीसिया | Of the believers (Matthew 16:18; 18:17). |
| repent; repentance | मन फिराना (L, B); पापों से मुड़ना (R); मन फिराव | |
| sin | पाप | |
| believe; faith | विश्वास करना; विश्वास | Keep the verb at every level. |
| grace | अनुग्रह | Key term: the same word at every level. |
| truth | सत्य (L, B); सच (R) | Key term. |
| glory; glorify | महिमा; महिमा करना | Key term. |
| peace | शान्ति | Key term. |
| righteousness; righteous | धार्मिकता; धर्मी | Key term. Readable may say जो सही है where the sense is conduct, with a decision. |
| gospel, good news | सुसमाचार | Every level. |
| baptize; John the Baptist | बपतिस्मा देना; यूहन्ना बपतिस्मा देनेवाला | |
| angel | स्वर्गदूत | |
| demon; unclean spirit | दुष्टात्मा; अशुद्ध आत्मा | |
| devil; Satan | शैतान; शैतान | *diabolos* and *Satanas* are both शैतान. Literal notes the Greek "accuser" in a decision where the play on the name matters. |
| heaven; Gehenna; Hades | स्वर्ग; नरक (Gehenna: गेहन्ना at L); अधोलोक | "the heavens": आकाश where the sky is meant. |
| Truly I tell you (*amēn*) | मैं तुमसे सच कहता हूँ | Every level. Literal may keep आमीन where it opens the saying, with a decision. |
| crowd | भीड़ | |
| hypocrites | पाखंडियो (address); पाखंडी | |
| Woe to you | तुम पर हाय | |
| eternal life | अनन्त जीवन | |
| cross; crucify | क्रूस; क्रूस पर चढ़ाना | |
| bread, loaf | रोटी; रोटियाँ | |
| Amen; Hosanna | आमीन; होशाना | |
| Rabbi; Teacher | रब्बी; गुरु | "Teacher!" as an address: हे गुरु. |
| slave (*doulos*) | दास | Every level. सेवक only where service alone is the point, with a decision. |

## 7. Reader settings in Hindi

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: Devanagari has no capital letters, so the setting has
  nothing to change and the Hindi text has **no** deity_pronoun spans.
  Respect for God and Jesus comes from the honorific third person and from
  आप (section 4), at every level. The first record of a passage file says
  so once where the English has a span.
- `christos`: Hindi has **no** christos spans. *मसीह* is both the familiar
  name in यीशु मसीह and the word Messiah itself, so the choice the English
  setting offers is already made. *ख्रीष्ट* is not used. The first record of
  a passage file says so once where the English has a span. **(checked,
  settings parity audit: `docs/review-notes/settings-parity.md`)** So Hindi
  is the one language with no christos spans while every other language has
  one wherever the English does; each of the 166 passage files where the
  English spans *Christos* has the Hindi decision that says why. A span
  would need a second Hindi wording for the same title, and the only
  candidate, *ख्रीष्ट*, is a church transliteration most readers do not use,
  not a plainer or more traditional way of saying "Messiah".
- `gender`: Hindi nouns for people are often already inclusive (लोग, मनुष्य,
  कोई, सब, बच्चे), and the generic masculine verb is ordinary Hindi. Use a
  span only where Hindi really has two ways of saying the same thing:
  `{{gender:भाइयो और बहनो|भाइयो}}` for *adelphoi* meaning believers (and
  `{{gender:भाई या बहन|भाई}}` in the singular), and `{{gender:लोगो|पुरुषो}}`
  where *andres* means people in general. Where the English has a span on a
  word that is already inclusive in Hindi, the Hindi has no span and a
  setting_alternative decision says why, once per passage.
- `units`: metric by default, the original unit as the alternative, as in
  French and Swahili: `{{units:लगभग 3 किलोमीटर|पंद्रह स्टेडियम}}`. Literal
  keeps the original unit. This differs from the English (US units) and
  needs a rendering decision. Coins have no metric form: a `units` span
  gives the value in wages by default and the coin as the alternative
  (`{{units:एक दिन की मज़दूरी|एक दीनार}}`), as the English does. Literal
  keeps the coin.
- `plural_you` is Spanish only.

## 7a. The Old Testament and poetry (proposed, to settle before the Old Testament)

- **The divine name** (YHWH) is `{{divine_name:प्रभु|याहवे}}` at every
  level. *प्रभु* stands where the English has "the LORD", and the alternative
  gives the name as most scholars think it was said. Suffixes and
  postpositions go inside each option where they differ. *यहोवा* (the Old
  Version's form) is not used. Because *Adonai* ("Lord") is also प्रभु, the
  first record of a book says how a reader can tell them apart (the
  setting).
- **Lines.** A psalm is set in lines, as `docs/english-style.md` section 10
  describes: mark each break inside a verse with `\q `, following the
  Hebrew accents' division (`python3 scripts/poetry_lines.py` prints it),
  at every level.

## 7b. Conventions settled in Matthew

Matthew was drafted first, in parallel passages; these choices came out of
harmonising it and hold for the later books. In the Synoptic parallels, keep
the wording of the Matthew passage where the Greek is the same, and differ
where the Greek differs.

- **Spelling.** Anusvara, not the nasal consonant (संतुलित, अंत, तुरंत,
  आरंभ), except the fixed forms शान्ति, अनन्त, मन्दिर, सन्तान, दृष्टान्त and
  names (अन्द्रियास). Chandrabindu where it is pronounced (अँधेरा).
- **Honorifics.** The narrator uses honorific forms for Jesus and God. When
  Jesus speaks of himself in the third person (मनुष्य का पुत्र, "the Son",
  the Messiah), the title takes plain singular forms (आएगा, उसका). The Father
  speaking of the Son says यह, इससे (3:17; 17:5). Opponents, the crowd and
  the soldiers speak of Jesus plainly (इसने, उसे); to him they say आप,
  mockers included. Herod, John and the prophets are plain.
- **Words.** Reward (*misthos*) is प्रतिफल; parable is दृष्टान्त at every
  level; wilderness is निर्जन प्रदेश (L, B), सुनसान इलाक़ा (R), not जंगल
  (forest); the Sea of Galilee is समुद्र (L), झील (B, R); centurion
  सूबेदार; magi ज्योतिषी; governor राज्यपाल; the council महासभा; covenant
  वाचा; leaven ख़मीर; vineyard दाख की बारी (L, B), अंगूर का बाग़ (R);
  Hades अधोलोक (L, B), मृत्यु का लोक (R); *doulos* दास at every level,
  सेवक for *diakonos*. *ethnos* in Balanced and Readable is देश or लोग, not
  जाति, which also means caste.
- **Coins.** The talent is `{{units:चाँदी के पाँच थैले|पाँच तालन्त}}` where
  the English has bags of silver, and a sum in wages where the English has
  one (18:24); Literal keeps तालन्त. The denarius is दीनार; the thirty
  pieces of silver चाँदी के तीस टुकड़े (L), सिक्के (B, R).
- **Gender.** Spans for "sons" meaning children of God or of the kingdom
  (`{{gender:सन्तान|पुत्र}}`) and for *anēr* meaning a person
  (`{{gender:व्यक्ति|आदमी}}`), besides *adelphos* (proposed).
- **Fixed sayings** match through the book: "Truly I tell you" is मैं तुमसे
  सच कहता हूँ at every level, with no आमीन; the weeping and gnashing of
  teeth, the fulfilment formula and "whoever has ears" each have one form.

Settled in Mark:

- **Nukta** in loanwords where standard Hindi writes it (क़ब्र, बाक़ी, ग़रीब,
  मज़ाक़, चोग़ा, बग़ीचा), consistently.
- **euthys** is तुरंत at Literal; Balanced and Readable vary it with the
  sentence (जैसे ही, उसी समय, तुरंत), one decision per passage file.
- **God spoken of** by Jesus or anyone else takes honorific forms
  (उन्होंने, वे), as in the narrative.
- **Words.** The mat (*krabattos*) is बिछौना (L, B), बिस्तर (R); the
  Herodians हेरोदी; the divorce certificate तलाक़नामा, not त्यागपत्र (which
  now means a resignation letter).

Settled in Luke:

- *epistata* ("Master") is हे स्वामी; parable masters स्वामी (L), मालिक (B,
  R), addressed with आप; प्रभु stays for God and Jesus.
- Luke's lake (*limnē*) is झील at every level; *nomikos* व्यवस्थापक (L),
  व्यवस्था का ज्ञाता (B), परमेश्वर की व्यवस्था के जानकार (R); *alēthōs*
  मैं तुमसे सचमुच कहता हूँ, kept apart from *amēn*; परमप्रधान for the Most
  High; woe तुम पर हाय.

Settled in John (with docs/john-terms.md):

- वचन (the Word); मैं तुमसे सच सच कहता हूँ (every level, तुम also to one
  person, as section 4); बने रहना for *menō* in the weighty sense; सहायक
  (the Paraclete); सत्य का आत्मा; "मैं हूँ" for the absolute "I am" (8:24,
  8:28, 8:58, 13:19); चिह्न, never चमत्कार; "the Jews" यहूदी at L, यहूदी
  अगुवे (B, R) where the authorities are meant.
- संसार (world) at every level; ज्योति (L, B), रोशनी (R) for light, as
  Matthew 5:14; Jesus' hour घड़ी, समय at Readable where the English says
  "time"; प्रेम करना for both Greek verbs of love; *paroimia* उपमा (L, B),
  मिसाल (R); "Woman" as an address हे स्त्री (L), हे नारी (B), माँ to his
  mother and बहन to other women (R).

Settled in Acts:

- मार्ग (the Way); मसीही (Christians); पवित्र जन (L), पवित्र लोग (B, R) for
  the holy ones; पिन्तेकुस्त; अन्य भाषाओं में बोलना (tongues); परमेश्वर की
  आराधना करनेवाले for *sebomenoi*, परमेश्वर का भय माननेवाले for
  *phoboumenoi*; *hairesis* दल for a party, पंथ for a sect.
- Offices: proconsul प्रांतपति (L, B), रोमी शासक (R); governor राज्यपाल;
  tribune सेनापति; church elders पुरनिए (L), बुज़ुर्ग अगुवे (B), कलीसिया के
  अगुवे (R).
- Address: speeches to crowds and councils आप; believers among themselves
  तुम; prayer to God तू; prayer to the risen Jesus आप, as everyone
  addresses him in the Gospels.
- The brothers-and-sisters span: `{{gender:भाइयो और बहनो|भाइयो}}` in the
  vocative, `{{gender:भाई-बहनों|भाइयों}}` in the oblique.

Settled in Romans:

- धार्मिकता; धर्मी ठहराना; विश्वास; व्यवस्था for God's law, नियम for law as a
  ruling principle (3:27; 7:21-8:2, B and R); व्यवस्था के काम; works काम,
  never कर्म (which carries the idea of karma); अनुग्रह (grace) kept apart
  from कृपा (kindness); अपराध (trespass); गर्व करना (boast); गिनना
  (count).
- Flesh (*sarx*) शरीर (L, B), शारीरिक स्वभाव (R) where the sense is moral;
  the body (*sōma*) देह at L and B where flesh is in the context (Romans
  6-8), शरीर elsewhere.
- *mē genoito*: ऐसा कभी न हो! (L), कदापि नहीं! (B), बिलकुल नहीं! (R).
- "Sons": `{{gender:की सन्तान|के पुत्र}}`, the postposition inside each
  option.

Settled in 1 Corinthians:

- बुद्धि / बुद्धिमान (wisdom), ज्ञान (knowledge), मूर्खता / मूर्ख; आत्मिक
  (spiritual), never आध्यात्मिक; स्वाभाविक (*psychikos*, L); विवेक
  (conscience); वरदान (gifts); भेद (mystery); उन्नति (building up, L, B).
- *porneia* यौन अनैतिकता (L), यौन पाप (B, R); the Lord's Supper प्रभु का भोज
  (L), प्रभु-भोज (B, R), with देह for the Lord's body as Luke 22:19.
- The Corinthians' slogans stand in quotation marks; Readable adds "तुममें
  से कुछ कहते हैं".

## 8. Status

A Hindi rendering added to a record does not change its status. Nothing is
marked reviewed by an AI.

## 9. Section headings and summaries

Where a book's `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json`
has languages other than English, add `"hi"` beside them, written from Open
Word Bible's own Hindi wording. They are AI drafts until reviewed.
