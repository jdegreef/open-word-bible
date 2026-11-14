# Hindi terms: Genesis to Revelation

**Status: proposed, awaiting native Hindi reviewers.** Every Hindi record is
`ai_draft`. If a choice here changes, every passage drafted under it is
revised.

## How this glossary relates to the style guide

`docs/hindi-style.md` is the brief for drafting Hindi and still holds in
full: the three levels, forms of address, spelling, typography, the reader
settings, the New Testament's words (section 6) and the conventions settled
in Matthew (section 7b). This glossary is the single reference for the
words and formulas the Old Testament adds, and it settles section 7a (the
divine name, poetry lines) for Genesis to Malachi. It replaces four notes
written book group by book group (`docs/pentateuch-hindi-russian-terms.md`,
`docs/history-hindi-russian-terms.md`, `docs/poetry-hindi-russian-terms.md`,
`docs/prophets-hindi-russian-terms.md`); where a later note changed an
earlier one, only the later rule is given here, with what it replaced.
`docs/russian-terms.md` is its Russian counterpart. Each book's own terms
note (`docs/isaiah-terms.md` and the others) still settles the meaning; this
file settles only the Hindi wording.

Where an earlier book or the New Testament in this translation already has a
form, that form wins. Decision text stays in English, quoting the Hindi
words.

## Drafting

- Translate from the Hebrew (and the Aramaic in Daniel 2:4-7:28 and
  Jeremiah 10:11), using the literal gloss, the English and the meaning
  decisions to see how a sentence was read. Never from a reference Bible,
  and never reproduce a copyrighted Bible's wording (the style guide names
  them). The familiar passages pull hardest toward the Hindi Old Version:
  Genesis 1-3, Exodus 20, Deuteronomy 6, Numbers 6:24-26; Psalms 23, 51, 91,
  103, Proverbs 3:5-6, Proverbs 31, Ecclesiastes 1-3 and 12; Isaiah 9, 40, 53,
  Jeremiah 31 and Micah 5. Draft from the gloss and rewrite any sentence that
  matches a well-known version for more than a short common phrase.
- Keep every `\v N ` marker where the English has it. Lines (`\q `): see
  [Poetry conventions](#poetry-conventions).
- Quotation marks as in the New Testament: straight `"` outside and `'`
  inside. Each level opens and closes the same quotations as the English
  level.
- Settings mirror the English spans where Hindi has the same choice:
  `divine_name`, `units`, and `gender` where Hindi really has two wordings.
  Hindi has no `deity_pronoun` setting.
- Narrative: simple past (उसने कहा, वह गया).
- Laws and instructions (Exodus 20-40, Leviticus, much of Numbers,
  Deuteronomy's speeches): `तुम ... न करना` / `वह ... लाए` at L and B;
  `तुम्हें ... करना है`, `उसे ... लाना होगा` at R.
- Rendering decisions: zero to two per sentence, only where Hindi had to
  choose. A book-wide choice is recorded once, in the first passage file of
  each book; later chapters follow it.
- Measures: metric by default where the English converts, the original unit
  as the alternative; Literal keeps the original unit where the English
  Literal does. Where the English has no `units` span, neither does the
  Hindi. Use the English conversion's values: cubit 45 cm (handbreadth
  7.5 cm), shekel 11.5 g, beka 5.7 g, gerah 0.6 g, talent 34 kg, mina
  0.6 kg, ephah 22 litres (a tenth 2.2 litres), omer 2.2 litres, seah
  7 litres, hin 3.7 litres, homer and cor 220 litres. Round as the English
  rounds. Write a decimal point and Indian digit grouping (6,03,550), as
  Revelation does. Days, years, ages and counts are not units. Ezekiel's
  temple measurements (40-48) take `units` spans where the English has them.

## Names of God and divine titles

| Hebrew (English) | Hindi |
|---|---|
| YHWH (the LORD) | `{{divine_name:प्रभु\|याहवे}}`, postpositions outside the span: `{{divine_name:प्रभु\|याहवे}} ने` |
| YHWH Elohim (the LORD God) | `{{divine_name:प्रभु\|याहवे}} परमेश्वर` |
| *ʾAdonai* YHWH (the Lord GOD) | प्रभु `{{divine_name:परमेश्वर\|याहवे}}` (Pentateuch, 2 Samuel 7, Psalms, Prophets) |
| *ʾAdonai* (Lord) | प्रभु |
| *Elohim* (God) | परमेश्वर |
| El Shaddai (God Almighty); *Shaddai* (Almighty) | सर्वशक्तिमान परमेश्वर; सर्वशक्तिमान |
| El Elyon (God Most High); *ʿElyon* (Most High) | परमप्रधान परमेश्वर (as Hebrews 7:1); परमप्रधान |
| YHWH of hosts (the LORD of hosts; of Armies at R) | सेनाओं के `{{divine_name:प्रभु\|याहवे}}` (as Romans 9:29), every level |
| *Yah* | `{{divine_name:प्रभु\|याह}}` (the default is the language's "the LORD") |
| the angel of the LORD | `{{divine_name:प्रभु\|याहवे}}` का दूत |
| the God of Israel | इस्राएल के परमेश्वर |
| the Holy One of Israel | इस्राएल का पवित्र (one form, Isaiah throughout) |
| the Mighty One of Jacob | याकूब का सामर्थी (Genesis 49:24) |
| Redeemer (*goʾel*) | छुटकारा दिलानेवाला (L, B); छुड़ानेवाला (R) |
| the Spirit of the LORD | `{{divine_name:प्रभु\|याहवे}}` का आत्मा (masculine, as the New Testament) |
| the man of God | परमेश्वर का जन |
| the LORD's anointed | `{{divine_name:प्रभु\|याहवे}}` का अभिषिक्त |
| the Ancient of Days (Daniel 7) | दिनों के प्राचीन (L, B) |
| "the LORD our righteousness" (Jeremiah 23:6) | one form; drafted as `{{divine_name:प्रभु\|याहवे}}` हमारी धार्मिकता [हैं] |
| my rock (*tsur*); my crag (*selaʿ*); my fortress | मेरी चट्टान; मेरी ऊँची चट्टान; मेरा गढ़ (as 2 Samuel 22) |
| refuge; shield; stronghold | शरणस्थान; ढाल; ऊँचा गढ़ |

- **Agreement.** God takes honorific plural agreement in both options
  (`{{divine_name:प्रभु|याहवे}} ने कहा`, `वे`, `उन्होंने`), as the New Testament
  does for God and Jesus.
- **YHWH and Adonai.** Because प्रभु is both YHWH and *ʾAdonai*, the first
  record of each book (in Psalms, of each block's file) says in a
  setting_alternative decision how the setting tells them apart.
- *यहोवा* (the Old Version's form) is not used. Exodus 3:14-15 and 6:2-3,
  where the name itself is the subject, follow the English wording and
  decisions.
- The crag (*sela*) and the rock (*tsur*) stay apart: ऊँची चट्टान / चट्टान.
- Where the English keeps "Hallelujah" as a word (as Revelation 19 does):
  हल्लेलूयाह. Otherwise *Hallelu Yah* is `{{divine_name:प्रभु|याह}}` की स्तुति
  करो.

## Address and pronouns

Hindi has intimate तू, familiar तुम and respectful आप (style guide section
4). One relationship holds through a book, so a scene does not change between
verses.

- **God in the third person** takes the honorific forms in narrative and
  poetry (परमेश्वर ने कहा, वे, उनका, उन्होंने), as the New Testament, Kings and
  Chronicles.
- **People speaking or praying to God** say तू (तेरा, तुझे): David, the
  psalmists, Job.
- **God speaking** uses मैं, and says तुम to people, one person or many;
  also to the Servant in Isaiah 42-53 (2 Corinthians 6:2 quotes 49:8 so).
- **To a ruler or a master**: आप. Moses and Aaron say आप to Pharaoh, and
  Pharaoh says तुम to them. People say आप and मेरे स्वामी राजा to the king
  (महाराज where the English B or R has "Your Majesty"). The psalmist says
  आप to the king where he speaks to him directly (Psalms 20, 21, 45, 72).
- **Family and equals** say तुम; a servant to a master and children to a
  father say आप where the scene is formal (Isaac to Abraham in Genesis 22
  says आप; Esau and Jacob between themselves say तुम). Nathan and David say
  आप to each other ("वह पुरुष आप ही हैं!", 2 Samuel 12:7).
- **The psalmist to people and to his enemies**: तुम. Job's friends to Job:
  तुम. The lovers in the Song of Songs: तुम.
- **Lines the New Testament quotes keep its forms of address**, even where
  they bend a rule: Psalm 2:7 keeps तू as Hebrews 1:5 and Acts 13:33 have
  it (Psalm 45:6-7 likewise keeps Hebrews 1:8-9's तू).

## Key theological terms

| Hebrew (English) | Hindi |
|---|---|
| covenant | वाचा |
| bless, blessing; curse | आशीष देना, आशीष; शाप देना, शाप |
| holy | पवित्र |
| clean, unclean (ritually) | शुद्ध, अशुद्ध |
| sin; iniquity; transgression | पाप; अधर्म (L), दोष (B, R); अपराध |
| make atonement for | के लिए प्रायश्चित करना (L, B); as the English at R |
| the righteous; the upright | धर्मी; सीधे लोग |
| righteousness | धार्मिकता, as the style guide (section 6) |
| the wicked; evildoers | दुष्ट; कुकर्मी |
| *ʾemunah*, *ʾemet* (faithfulness, truth) | सच्चाई (L), विश्वासयोग्यता (B, R) where it is God's; सत्य |
| salvation; save, deliver | उद्धार; बचाना, छुड़ाना |
| the fear of the LORD | `{{divine_name:प्रभु\|याहवे}}` का भय (L, B); `{{divine_name:प्रभु\|याहवे}}` का आदर और भय मानना (R) |
| *nefesh* (soul) | प्राण (L); मन, जीवन or "मैं" at B and R as the English does |
| "all flesh" | सब देहधारी (L, as 1 Peter 1:24), सारी मनुष्य जाति (B) |
| the remnant | बचे हुए लोग (L, B), जो बच गए (R) |
| statute; rule; commandment | विधि; नियम; आज्ञा |
| a lasting statute | सदा की विधि |
| Spirit | as the Spirit of the LORD above; masculine agreement |

### Hesed, in its three uses

| Use | Hindi |
|---|---|
| God's steadfast love | अटल प्रेम at every level. *Replaces* the Pentateuch note's "अटल प्रेम or करुणा" at R: from 2 Samuel on, and in Psalms, God's hesed is अटल प्रेम at R too. |
| Between people (a favour, a kindness) | अटल प्रेम (L), कृपा (B, R) |
| Israel's loyalty to God (Hosea 4:1, 6:4, 6:6, 10:12, 12:7) | अटल प्रेम (L, B), सच्चा प्रेम (R). Hosea 6:6 keeps Matthew 9:13's frame with a footnoted decision. |

The refrain "for he is good, his steadfast love is forever" (Psalms 106,
107, 118, 136) copies 1 Chronicles 16:34 at each level.

### Torah, law

| Where | Hindi |
|---|---|
| God's *torah* in the Psalms | व्यवस्था (L, B); शिक्षा (R) |
| *torah* in the Prophets (God's teaching through the prophets) | शिक्षा at every level; where the New Testament quotes a line with "law" (Jeremiah 31:33 in Hebrews 8:10), its word is kept there, with a decision |
| *torah* of father or mother (Proverbs) | शिक्षा |
| the Law (of Moses, in the New Testament) | व्यवस्था, as the style guide |

Psalm 119's eight words (law, testimonies, precepts, statutes,
commandments, rules, word, promise) each have one fixed word per level,
recorded in decisions at 119:1-11 and kept through the psalm.

### Sheol and the Pit

| Hebrew (English) | Hindi |
|---|---|
| Sheol | शिओल (L), अधोलोक (B), मृत्यु का लोक (R). *Replaces* the Pentateuch note's अधोलोक at R; 2 Samuel 22 set मृत्यु का लोक and the Psalms and Prophets follow it. Genesis, Numbers, Deuteronomy and 1 Samuel were drafted with अधोलोक at R and are to be brought into line in the consistency pass. |
| the Pit | गड्ढा (L), क़ब्र (B, R) |

### Nations and peoples

| Hebrew (English) | Hindi |
|---|---|
| the nations | जातियाँ (L), देश / राष्ट्र (B, R), never caste-sounding at B and R |
| the peoples | लोग |

## Worship and the sanctuary

| Hebrew (English) | Hindi |
|---|---|
| the holy place; the sanctuary | पवित्र स्थान; पवित्रस्थान |
| the Most Holy Place | परमपवित्र स्थान |
| the tent of meeting | मिलन का तंबू |
| the tabernacle (*mishkan*) | निवास-तंबू (L); पवित्र तंबू (B, R), as Hebrews |
| the ark (of the covenant, of the testimony) | (वाचा का, साक्षी का) संदूक, as Revelation |
| the ark of God; of the covenant of the LORD | परमेश्वर का संदूक; `{{divine_name:प्रभु\|याहवे}}` की वाचा का संदूक |
| Noah's ark | जहाज़, as Hebrews 11:7 |
| the testimony (*ʿedut*, the tablets) | साक्षी-पत्र |
| the atonement cover (*kapporet*) | प्रायश्चित का ढकना, as Hebrews 9:5 |
| cherub, cherubim | करूब, करूबों |
| altar | वेदी |
| priest; high priest | याजक; महायाजक |
| Levites | लेवी |
| ephod; breastpiece; Urim and Thummim | एपोद; सीनाबंद; ऊरीम और तुम्मीम |
| lampstand | दीवट |
| burnt offering | होमबलि |
| grain offering | अन्नबलि |
| sin offering | पापबलि |
| guilt offering | दोषबलि |
| peace offering (*shelamim*) | मेलबलि |
| food offering (*ʾishsheh*) | आग में चढ़ाई गई भेंट |
| soothing aroma | सुखद सुगंध (L, B); ऐसी सुगंध जो प्रभु को भाती है (R) |
| without defect | निर्दोष |
| the Sabbath | सब्त |
| the Passover; Unleavened Bread | फ़सह (as the New Testament); अख़मीरी रोटी का पर्व |
| the Feast of Weeks; of Booths; of Ingathering | सप्ताहों का पर्व; झोपड़ियों का पर्व (as John 7:2); फ़सल बटोरने का पर्व |
| the Day of Atonement | प्रायश्चित का दिन |
| serious skin disease (*tsaraʿat*) | गंभीर चर्म रोग, "कोढ़" in a decision |
| the house of the LORD; the temple (*hekhal*) | `{{divine_name:प्रभु\|याहवे}}` का भवन (L, and B or R where the English says "house"), मन्दिर (B, R where the English says "temple"), as Kings and the New Testament; *hekhal* मन्दिर. मन्दिर keeps the nasal consonant, one of the style guide's fixed spellings. |
| the high places (*bamot*) | ऊँचे स्थान |
| Baal, the Baals; Asherah, the Asherim | बाल, बाल देवता; अशेरा, अशेरा के खंभे |
| bless (God); praise (*hallel*); give thanks (*hodu*) | धन्य कहना; स्तुति करना; धन्यवाद करना |

The temple furnishings in Ezekiel 40-48 follow 1 Kings 7.

## Officials and social terms

| Hebrew (English) | Hindi |
|---|---|
| the sons of Israel | `{{gender:इस्राएल की सन्तान\|इस्राएल के पुत्र}}` (L); इस्राएली (B, R), no span |
| Israel, Israelite(s) | इस्राएल, इस्राएली |
| Egypt, Egyptians; Pharaoh; Hebrew(s) | मिस्र, मिस्री; फ़िरौन; इब्रानी (as Philippians 3:5) |
| the congregation (*ʿedah*); the assembly (*qahal*) | मंडली; सभा |
| tribe; clan; father's house | गोत्र; कुल; पितृकुल (L), परिवार (B, R) |
| firstborn | पहलौठा |
| foreigner, sojourner (*ger*) | परदेशी |
| slave, servant (*ʿeved*) | दास at every level, as the New Testament; सेवक only where service alone is the point, with a decision |
| the psalmist's "your servant"; Moses, David as God's servant | दास at every level |
| the king's officials (his "servants", 2 Samuel) | दास (L), अधिकारी (B, R) |
| king; queen; kingdom | राजा; रानी; राज्य |
| reign, become king | राज्य करना, राजा बनना |
| my lord the king | मेरे स्वामी राजा (people say आप to the king) |
| prophet; seer | भविष्यद्वक्ता (L, B), नबी (R), as the New Testament; दर्शी |
| anoint; the anointed (the king) | अभिषेक करना; अभिषिक्त |
| judge (*shofet*, in Judges) | न्यायी |
| the Philistines; uncircumcised | पलिश्ती; ख़तनारहित |
| mighty men (*gibborim*) | वीर योद्धा |
| the Three; the Thirty (David's men) | तीनों; तीसों |
| Cherethites and Pelethites | करेती और पलेती |
| chariots; horsemen | रथ; घुड़सवार |
| the poor, the afflicted, the needy | ग़रीब, दीन, दरिद्र |
| the wilderness | निर्जन प्रदेश, as Matthew 3:1 |
| the land flowing with milk and honey | ऐसा देश जिसमें दूध और मधु की धाराएँ बहती हैं |

## Recurring formulas

### Kings and Chronicles: the regnal formulas

One wording per level through Kings and Chronicles. B smooths; R may split
the sentence.

- **Accession.** "In the Nth year of X king of Judah, Y son of Z became king
  over Israel in Samaria, and he reigned N years." L: यहूदा के राजा X के Nवें
  वर्ष में Z का पुत्र Y सामरिया में इस्राएल पर राज्य करने लगा, और उसने N वर्ष
  राज्य किया।
- **Age and mother (Judah).** जब वह राजा बना तब N वर्ष का था, और उसने यरूशलेम
  में N वर्ष राज्य किया; उसकी माता का नाम X था।
- **Verdict.** "He did what was evil / right in the eyes of the LORD": उसने
  वह किया जो `{{divine_name:प्रभु|याहवे}}` की दृष्टि में बुरा / ठीक था।
- **Source.** "Are they not written in the book of the chronicles of the
  kings of Israel?": क्या वे इस्राएल के राजाओं के इतिहास की पुस्तक में नहीं
  लिखे हैं?
- **Death.** "He slept with his fathers and was buried": वह अपने
  `{{gender:पूर्वजों|पुरखाओं}}` के साथ सो गया (L, B), where the English has a
  span; उसकी मृत्यु हुई (R).
- **Genealogies (1 Chronicles 1-9)** keep one list formula per level ("the
  sons of X: A, B and C"; "X fathered Y", उत्पन्न किया at L, as Matthew 1),
  and every name in the forms of Genesis, Numbers and the name tables below.

### The Prophets

One wording per level, through all seventeen books.

| Hebrew (English L / R) | Hindi |
|---|---|
| *koh ʾamar YHWH* (Thus says the LORD / This is what the LORD says) | `{{divine_name:प्रभु\|याहवे}}` यों कहते हैं (L); `{{divine_name:प्रभु\|याहवे}}` यह कहते हैं (B, R), as Kings |
| *neʾum YHWH* (declares the LORD / says the LORD) | `{{divine_name:प्रभु\|याहवे}}` की यह वाणी है (L, B); `{{divine_name:प्रभु\|याहवे}}` कहते हैं (R) |
| the word of the LORD came to X | `{{divine_name:प्रभु\|याहवे}}` का वचन X के पास पहुँचा (L, B); `{{divine_name:प्रभु\|याहवे}}` ने X को यह संदेश दिया (R) |
| *ʾAdonai YHWH* (the Lord GOD) | प्रभु `{{divine_name:परमेश्वर\|याहवे}}` |
| YHWH of hosts (of Armies at R) | सेनाओं के `{{divine_name:प्रभु\|याहवे}}` |
| *massa* (oracle / message) | भारी वचन (L), संदेश (B, R), as Proverbs 30:1 |
| *massa* as a heading | X के विषय में भारी वचन (L), X के विषय में संदेश (B), यह X के बारे में एक संदेश है (R) |
| *hoy* (woe / how terrible) | हाय (L, B); R as the English |
| in that day | उस दिन |
| the day of the LORD | `{{divine_name:प्रभु\|याहवे}}` का दिन |
| "Son of man" (Ezekiel's address, *ben adam*) | हे मनुष्य की सन्तान at every level, kept apart from Jesus' title मनुष्य का पुत्र, as Job |
| "one like a son of man" (Daniel 7:13) | मनुष्य के पुत्र जैसा कोई, the form the Gospels quote |
| "they will know that I am the LORD" (Ezekiel) | one wording per level; drafted as तुम जान लोगे कि मैं `{{divine_name:प्रभु\|याहवे}}` [हूँ] |
| the Servant (*ʿeved YHWH*, Isaiah 42-53) | मेरा दास; where Matthew 12:18-21 or Acts 8:32-33 quotes the line, its wording |
| daughter Zion | सिय्योन की बेटी (one form, Lamentations too) |

### Psalm titles, musical terms and Selah

| Hebrew (English L / R) | Hindi |
|---|---|
| *lamnatseach* (For the director / For the leader of the music) | संगीत-निर्देशक के लिए (L, B); गायक-मंडली के अगुवे के लिए (R) |
| *mizmor* (a psalm / a song at R) | भजन; गीत (R) |
| *shir* (a song) | गीत |
| *maskil*, *miktam*, *shiggayon* | मस्कील, मिक्ताम, शिग्गायोन |
| *tefillah* (a prayer) | प्रार्थना |
| *Hallelu Yah* (Praise the LORD) | `{{divine_name:प्रभु\|याह}}` की स्तुति करो |
| *shir hamma'alot* (A song of ascents / for the journey up to Jerusalem) | चढ़ाई का गीत (L, B); यरूशलेम की ओर जाने की यात्रा का गीत (R) |

- **Titles.** A psalm's title is verse 1 and is translated at every level as
  the English level does it: Literal keeps the Hebrew's words, Readable may
  explain.
- Instruments and tunes ("to the tune of ...") and the terms whose meaning
  is lost (*gittit*, *sheminit*, *alamot*, *neginot*, *mahalat*) follow the
  English level: kept as names where it keeps them (गित्तीत, शमीनीत,
  अलामोत), translated where it translates, with the English decision's
  uncertainty carried into the Hindi one.
- **Selah** stays at the end of its verse at every level, as the English has
  it: सेला. The first use in each block of psalms gets a decision (a word
  whose meaning is unknown, probably a musical direction).

## Poetry conventions

- **Lines follow the English record.** Where an English level has `\q`
  breaks, that level is set in lines too, with the breaks at Hindi's own
  phrase boundaries; where the English level is prose, so is the Hindi. This
  settles style guide section 7a, which asked for lines at every level.
  Pentateuch poems in lines where the English has them: Genesis 49, Exodus
  15, Numbers 23-24, Deuteronomy 32-33. Jonah 2 and Habakkuk 3 are poetry;
  Jonah 1, 3-4 and Haggai are prose.
- **Acrostics** (Lamentations, and the acrostic psalms): follow the English;
  no letter headings unless it has them.
- **Personified women.** Wisdom and Folly are women in the Hebrew; बुद्धि is
  feminine, so the verbs and pronouns follow. Zion and Jerusalem pictured as
  a woman take feminine forms, as Lamentations.

## Names

**Policy.** Names that occur in the New Testament keep the New Testament form
in this translation (`grep` the name in content/MAT, LUK, ACT, ROM, HEB, JAS,
REV in Hindi). Keep a list for the book and use one form throughout. Other
names follow the established Hindi Bible form where one exists and otherwise
transcribe the Hebrew, with nukta where Hindi writes one. Each prophet's name
and his father's take the New Testament or earlier forms (or Ezra's).

- **Two names for one person.** Keep each name where the Hebrew has it.
  Uzziah is also called Azariah in Kings (अजर्याह). Jeremiah writes both
  Nebuchadnezzar and Nebuchadrezzar: नबूकदनेस्सर and नबूकदरेस्सर, each where
  the Hebrew has it (Ezekiel has the second); elsewhere नबूकदनेस्सर.
- Beersheba बेर्शेबा is kept apart from Bathsheba बतशेबा.

| English | Hindi |
|---|---|
| Adam, Eve, Cain, Abel, Seth | आदम, हव्वा, कैन, हाबिल, शेत |
| Enoch, Lamech, Noah, Shem, Ham, Japheth | हनोक, लेमेक, नूह, शेम, हाम, येपेत |
| Abram, Abraham; Sarai, Sarah | अब्राम, अब्राहम; सारै, सारा |
| Lot, Hagar, Ishmael, Isaac | लूत, हाजिरा, इश्माएल, इसहाक |
| Rebekah, Esau, Jacob, Laban | रिबका, एसाव, याकूब, लाबान |
| Leah, Rachel, Bilhah, Zilpah | लिआ, राहेल, बिल्हा, जिल्पा |
| Reuben, Simeon, Levi, Judah | रूबेन, शिमोन, लेवी, यहूदा |
| Dan, Naphtali, Gad, Asher | दान, नप्ताली, गाद, आशेर |
| Issachar, Zebulun, Dinah | इस्साकार, जबूलून, दीना |
| Joseph, Benjamin, Ephraim, Manasseh | यूसुफ़, बिन्यामीन, एप्रैम, मनश्शे |
| Melchizedek, Salem; Sodom, Gomorrah | मलिकिसिदक, शालेम; सदोम, अमोरा |
| Moses, Aaron, Miriam, Joshua, Caleb | मूसा, हारून, मिरियम, यहोशू, कालेब |
| Jethro, Balaam, Balak, Korah, Phinehas | यित्रो, बिलाम, बालाक, कोरह, पीनहास |
| Rahab, Achan, Gibeon | राहाब, आकान, गिबोन |
| Deborah, Barak, Gideon, Jephthah, Samson, Delilah | दबोरा, बाराक, गिदोन, यिप्तह, शिमशोन, दलीला |
| Ruth, Naomi, Boaz, Obed, Jesse | रूत, नाओमी, बोअज़, ओबेद, यिशै |
| Eli, Hannah, Samuel, Saul, Jonathan, Michal | एली, हन्ना, शमूएल, शाऊल, योनातान, मीकल |
| David, Goliath, Abner, Joab, Absalom, Bathsheba, Uriah, Nathan | दाऊद, गोलियत, अब्नेर, योआब, अबशालोम, बतशेबा, ऊरिय्याह, नातान |
| Ish-bosheth, Mephibosheth, Ziba, Asahel | ईशबोशेत, मपीबोशेत, सीबा, असाहेल |
| Amnon, Tamar, Jonadab, Adonijah | अम्नोन, तामार, योनादाब, अदोनिय्याह |
| Ahithophel, Hushai, Ittai the Gittite, Shimei, Amasa | अहीतोपेल, हूशै, इत्तै, शिमी, अमासा |
| Zadok, Abiathar, Ahimaaz, Benaiah, Barzillai | सादोक (as Matthew 1:14), अबियातार, अहीमास, बनायाह, बर्ज़िल्लै |
| Solomon, Rehoboam, Jeroboam, Ahab, Jezebel, Elijah, Elisha, Naaman | सुलैमान, रहबाम, यारोबाम, अहाब, ईज़ेबेल, एलिय्याह, एलीशा, नामान |
| Hezekiah, Josiah, Manasseh, Uzziah (Azariah), Jehoshaphat, Zedekiah | हिजकिय्याह, योशिय्याह, मनश्शे, उज्जियाह (अजर्याह), यहोशापात, सिदकिय्याह |
| Nebuchadnezzar (Nebuchadrezzar), Sennacherib, Hiram, the queen of Sheba | नबूकदनेस्सर (नबूकदरेस्सर), सन्हेरीब, हीराम, शेबा की रानी |
| Cyrus | कुस्रू (as Ezra) |
| Isaiah, Jeremiah, Daniel, Jonah | यशायाह, यिर्मयाह, दानिय्येल (Matthew 24:15), योना |
| Daniel's friends (Daniel 1:7): Hananiah, Mishael, Azariah; Shadrach, Meshach, Abednego | हनन्याह, मीशाएल, अजर्याह; शद्रक, मेशक, अबेदनगो (as drafted) |
| Belteshazzar, Belshazzar, Darius the Mede | बेलतशस्सर, बेलशस्सर, मादी दारा (as drafted) |
| Canaan, Sinai, Horeb, Jordan, Moab, Edom | कनान, सीनै, होरेब, यरदन, मोआब, एदोम |
| Jerusalem, Zion, Samaria, Bethlehem, Hebron, Shiloh, Jericho | यरूशलेम, सिय्योन, सामरिया, बैतलहम, हेब्रोन, शीलो, यरीहो |
| Mahanaim; Beersheba; the city of David | महनैम; बेर्शेबा; दाऊद का नगर (as Luke 2:11) |
| Babylon, Assyria, Egypt, Tyre, Sidon, Damascus | बाबुल, अश्शूर, मिस्र, सूर (as Matthew 11:21), सैदा, दमिश्क |
| Amorites, Canaanites, Hittites | एमोरी, कनानी, हित्ती |

## Parallel passages

**Policy.** Draft once, reuse. Where the Hebrew is the same, the later
passage copies the earlier wording at each level; where it differs, the
wording differs, with a decision naming the other passage. A rendering
decision is added only where Hindi made its own choice. Samuel and Kings are
drafted before Chronicles, which retells them. Where both sides are drafted
at once, the later passage copies the earlier once both exist; the
consistency pass checks.

| Passage | Same as |
|---|---|
| 1-2 Chronicles (where the Hebrew is the same) | Samuel and Kings |
| Psalm 18 | 2 Samuel 22 (22:50 keeps Romans 15:9's wording) |
| Psalm 96; 105:1-15; 106:1, 47-48 | 1 Chronicles 16:8-36 |
| Psalm 132:8-10 | 2 Chronicles 6:41-42 |
| Psalm 53 | Psalm 14 |
| Psalm 70 | Psalm 40:13-17 |
| Psalm 108 | Psalms 57:7-11 and 60:5-12 |
| Psalm 115:4-8 | Psalm 135:15-18 |
| Proverbs 18:8; 20:16; 21:9 | Proverbs 26:22; 27:13; 25:24 (Proverbs 22:17-24:22 has no internal parallel) |
| Isaiah 36:1-39:8 | 2 Kings 18:13-20:19 |
| Isaiah 37:16-20; 38:9-20 | Hezekiah's prayer as 2 Kings 19, and his song |
| Jeremiah 52 (and 39:1-10) | 2 Kings 24:18-25:30 |
| Isaiah 2:2-4 | Micah 4:1-3 |
| Obadiah 1-9 | Jeremiah 49:7-16 |
| Jeremiah 10:12-16 | Jeremiah 51:15-19 |
| Jeremiah 6:22-24 | Jeremiah 50:41-43 |
| Joel 3:16 (Hebrew 4:16) | Amos 1:2 |

## The New Testament quotes the Old

**Policy.** Where the New Testament quotes a line and the Hebrew says the
same, use the New Testament's Hindi wording at the matching level (grep the
quoting book). Where the New Testament follows the Greek Old Testament and
differs, translate the Hebrew and add a decision naming the New Testament
form: Psalm 40:6 "a body", 68:18 "gave gifts", 102:25-27 in part, Proverbs
3:34 "the proud", Isaiah 7:14 "virgin", 40:3 punctuation, 61:1 "recovery of
sight", Amos 9:11-12 in Acts 15, Joel 2:28-32 small differences. A rendering
may not narrow the meaning decision. Quoted lines keep the New Testament's
forms of address (see [Address and pronouns](#address-and-pronouns)).

The references below use English verse numbers; the records number as the
Hebrew (a psalm's title is verse 1), and `data/versification.json` maps one
to the other.

- **History:** 2 Samuel 22:50 (Romans 15:9, as Psalm 18:49).
- **Psalms:** 2:1-2, 7, 9; 4:4; 5:9; 8:2, 4-6; 10:7; 14:1-3; 16:8-11; 18:49;
  19:4; 22:1, 18, 22; 24:1; 31:5; 32:1-2; 34:8, 12-16, 20; 35:19; 36:1;
  40:6-8; 41:9; 44:22; 45:6-7; 51:4; 62:12; 68:18; 69:4, 9, 22-23, 25; 78:2,
  24; 82:6; 89:20; 91:11-12; 94:11; 95:7-11; 97:7; 102:25-27; 104:4; 109:8;
  110:1, 4; 112:9; 116:10; 117:1; 118:6, 22-23, 25-26; 140:3; 143:2.
- **Job and Proverbs:** Job 5:13; 41:11; Proverbs 3:11-12, 34; 10:12; 11:31;
  25:21-22; 26:11.
- **Prophets:** Isaiah 6:9-10; 7:14; 8:14; 9:1-2; 11:10; 22:13; 25:8;
  28:11-12, 16; 29:13-14; 40:3-5, 6-8; 42:1-4; 45:23; 49:6, 8; 52:5, 7, 11,
  15; 53:1, 4-5, 7-9, 12; 54:1; 56:7; 59:20-21; 61:1-2; 64:4; 65:1-2; 66:1-2;
  Jeremiah 7:11; 9:24; 31:15, 31-34; Hosea 1:10; 2:23; 6:6; 11:1; 13:14;
  Joel 2:28-32; Amos 5:25-27; 9:11-12; Micah 5:2; Habakkuk 1:5; 2:4; Haggai
  2:6; Zechariah 9:9; 11:12-13; 12:10; 13:7; Malachi 1:2-3; 3:1; 4:5-6
  (Hebrew 3:23-24); Daniel 7:13; 9:27; 12:11.

## Book notes

- **Genesis to Deuteronomy.** The first Old Testament books drafted in
  Hindi. Isaac to Abraham (Genesis 22) says आप; Esau and Jacob say तुम; Moses
  and Aaron say आप to Pharaoh. Exodus 3:14-15 and 6:2-3 follow the English
  on the name. Noah's ark is जहाज़.
- **Joshua to Ruth.** *shofet* in Judges is न्यायी.
- **1-2 Samuel.** Forms first used in 2 Samuel are for Kings, Chronicles and
  Psalms to reuse (names above). "How the mighty have fallen" (1:19, 25,
  27): वीर योद्धा कैसे गिर पड़े! (L), हाय, वीर योद्धा कैसे गिर पड़े! (B), हाय,
  बहादुर योद्धा कैसे मारे गए! (R). 2 Samuel 22 was drafted before Psalm 18 and
  sets the rock and Sheol words. 2 Samuel 7 sets प्रभु
  `{{divine_name:परमेश्वर|याहवे}}`.
- **1-2 Kings, 1-2 Chronicles.** Regnal formulas above; Chronicles reuses
  Samuel and Kings; the genealogies' list formula. 1 Chronicles 16:8-36
  (Psalms 105, 96, 106) and 2 Kings 18:13-20:19 (Isaiah 36-39) were drafted
  here first and the later books reuse them.
- **Job.** "The satan" (Literal) / "the Accuser" (Readable): शैतान (L),
  दोष लगानेवाला (B, R), as the English level has a title or a name. "The sons
  of God": परमेश्वर के पुत्र (L), स्वर्गदूत / स्वर्गीय प्राणी (B, R), as the
  English level.
- **Psalms.** Titles, Selah and parallels above; Psalm 119's eight words.
- **Proverbs.**

  | Hebrew (English) | Hindi |
  |---|---|
  | *ḥokmah* (wisdom) | बुद्धि |
  | *binah*, *tevunah* (understanding) | समझ |
  | *daʿat* (knowledge) | ज्ञान |
  | *musar* (discipline; correction at R) | अनुशासन (L, B); सुधार (R) |
  | *torah* of father or mother (teaching) | शिक्षा |
  | *kesil*, *ʾewil* (fool) | मूर्ख |
  | *lets* (mocker) | ठट्ठा करनेवाला |
  | *peti* (the simple / naive / easily fooled) | भोला (L, B); आसानी से बहकनेवाला (R) |
  | *ʿatsel* (sluggard) | आलसी |
  | *beni* (my son) | हे मेरे पुत्र (L, B); बेटा (R) |
  | the strange woman (as the English level: foreign / forbidden / another man's wife) | पराई स्त्री; R as the English |

- **Ecclesiastes.** Qoheleth: कोहेलेत (L), उपदेशक (B, R), as the English
  level. *hevel* follows the English level: भाप / साँस (L, the image),
  व्यर्थ, क्षणभंगुर (B, R). "Under the sun": सूर्य के नीचे at every level.
- **Song of Songs.** The lovers say तुम. The speakers follow the English
  level's marks. Translated as love poetry; an allegorical reading is not
  added.
- **Isaiah.** "The Holy One of Israel" one form. The Servant passages
  (42:1-9; 49:1-13; 50:4-11; 52:13-53:12) drafted with care: मेरा दास, God
  addressing him with तुम. 7:14 *ʿalmah*: the meaning decision is "the young
  woman", so युवती at every level, with a footnoted decision naming Matthew
  1:23's कुँवारी (from the Greek *parthenos*).
- **Jeremiah.** Baruch, the Rechabites and the kings of Judah as Kings;
  Nebuchadnezzar and Nebuchadrezzar each as the Hebrew has it; "the LORD our
  righteousness" one form. Aramaic in 10:11.
- **Lamentations.** Acrostics as the English; "daughter Zion" one form; Zion
  as a woman takes feminine forms.
- **Ezekiel.** "Son of man" as हे मनुष्य की सन्तान at every address; "they
  will know that I am the LORD" one wording per level; the temple
  measurements (40-48) with `units` spans where the English has them, and
  the furnishings as 1 Kings 7.
- **Daniel.** Aramaic 2:4-7:28. Names above (settled once). "The Ancient of
  Days" दिनों के प्राचीन (L, B); "the abomination of desolation" as Matthew
  24:15 where quoted (11:31 L: उजाड़नेवाली घृणित वस्तु); "the time of the end"
  (12:4 L: अंत का समय).
- **The Twelve.** Each prophet's name as the New Testament or Ezra. Hosea's
  hesed is Israel's loyalty (above). Jonah 2 and Habakkuk 3 are poetry; Jonah
  1, 3-4 and Haggai are prose. Malachi 3:1 and 4:5-6 (Hebrew 3:23-24) keep
  the Gospels' wording where the Hebrew agrees.
- **New Testament.** `docs/hindi-style.md` sections 6 and 7b and the book
  terms notes.

## Settled while drafting

Decisions recorded while the blocks were harmonised, kept here as they were
made (each is also in its topic section above).

- **Torah** in the Prophets: शिक्षा at every level; Jeremiah 31:33 keeps
  Hebrews 8:10's "law" with a decision.
- **The Servant** (Isaiah 42-53): मेरा दास, God addressing him with तुम
  (2 Corinthians 6:2 quotes 49:8 so).
- **Redeemer** (*goʾel*): छुटकारा दिलानेवाला (L, B), छुड़ानेवाला (R).
- **Mighty One of Jacob**: याकूब का सामर्थी (Genesis 49:24).
- **"All flesh"**: सब देहधारी (L, as 1 Peter 1:24), सारी मनुष्य जाति (B).
- **Massa headings**: X के विषय में भारी वचन (L), X के विषय में संदेश (B), यह X
  के बारे में एक संदेश है (R).
- **Zion and Jerusalem pictured as a woman** take feminine forms, as
  Lamentations.
- **Hesed as Israel's loyalty to God** (Hosea 4:1, 6:4, 6:6, 10:12, 12:7):
  अटल प्रेम (L, B), सच्चा प्रेम (R); Hosea 6:6 keeps Matthew 9:13's frame with a
  footnoted decision.
- **Isaiah 7:14**: युवती, with a footnoted decision naming कुँवारी.
- **Daniel**: "the Ancient of Days" दिनों के प्राचीन (L, B).
- **Sheol at R**: मृत्यु का लोक (2 Samuel 22, Psalms, Prophets), replacing
  the Pentateuch's अधोलोक at R.
- **God's hesed at R**: अटल प्रेम, replacing the Pentateuch's "अटल प्रेम or
  करुणा".
