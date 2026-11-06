# Hindi and Russian: the Pentateuch

**Status: proposed, awaiting native Hindi and Russian reviewers.**
These are the choices used to draft Genesis to Deuteronomy in Hindi and
Russian, the first Old Testament books in both languages, so that five books
drafted in parallel read as one translation. `docs/hindi-style.md` and
`docs/russian-style.md` still hold, including section 7a (the divine name,
poetry lines), which this note settles for the Pentateuch. If a choice here
changes, every passage drafted under it is revised.

Decision text stays in English, quoting the Hindi or Russian words.

## Both languages

- Translate from the Hebrew, using the literal gloss, the English and the
  meaning decisions to see how a sentence was read. Never from a reference
  Bible, and never reproduce a copyrighted Bible's wording (the style
  guides name them). Familiar passages (Genesis 1-3, Exodus 20,
  Deuteronomy 6, Numbers 6:24-26) pull hardest: draft from the gloss and
  rewrite any sentence that matches a well-known version for more than a
  short common phrase.
- Keep every `\v N ` marker where the English has it, and each level's own
  poetry breaks (`\q `) where the English level has them (Genesis 49,
  Exodus 15, Numbers 23-24, Deuteronomy 32-33).
- Quotation marks as in the New Testament: Hindi types straight `"` and `'`;
  Russian « » outside and “ ” inside, never „. Each level opens and closes
  the same quotations as the English level.
- Settings mirror the English spans where the language has the same choice:
  `divine_name` (both), `deity_pronoun` (Russian only, as in the New
  Testament), `units` (both), `gender` (where the language really has two
  wordings; Russian люди, человек, кто need none, as in the New Testament).
- Narrative: Hindi simple past (उसने कहा, वह गया); Russian perfective past
  (сказал, пошёл), imperfective for what went on or kept happening.
- Laws and instructions (Exodus 20-40, Leviticus, much of Numbers,
  Deuteronomy's speeches): Hindi `तुम ... न करना` / `वह ... लाए` at L and B,
  `तुम्हें ... करना है`, `उसे ... लाना होगा` at R; Russian imperative or
  future at L and B (`не убивай`, `пусть принесёт`, `он принесёт`), `нельзя`,
  `должен` at R.
- Rendering decisions: zero to two per sentence, only where the language
  had to choose. A book-wide choice is recorded once, in the first passage
  file of each book; later chapters follow it.
- Measures: metric by default where the English converts, the original unit
  as the alternative; Literal keeps the original unit where the English
  Literal does. Where the English has no units span, neither does the
  translation. Use the English conversion's values: cubit 45 cm
  (handbreadth 7.5 cm), shekel 11.5 g, beka 5.7 g, gerah 0.6 g, talent
  34 kg, mina 0.6 kg, ephah 22 litres (a tenth 2.2 litres), omer 2.2 litres,
  seah 7 litres, hin 3.7 litres, homer and cor 220 litres. Round as the
  English rounds. Hindi writes a decimal point and Indian digit grouping
  (6,03,550), as Revelation does; Russian writes a decimal comma and a
  thin no-break space in numbers of five digits or more (603 550), as
  Revelation does. Days, years, ages and counts are not units.

## Forms of address

- **Hindi.** God takes the honorific third person in narrative (परमेश्वर ने
  कहा, उन्होंने), as in the New Testament. People speaking or praying to God
  say तू. God speaking to people says तुम, to one person or many. Moses and
  Aaron say आप to Pharaoh, and anyone to a ruler or a master; Pharaoh says
  तुम to them. Family and equals say तुम; a servant to a master and children
  to a father say आप where the scene is formal (Isaac to Abraham in Genesis
  22 says आप; Esau and Jacob between themselves say तुम).
- **Russian.** ты to God and from God, as in the New Testament, with
  `deity_pronoun` spans on God's pronouns (`{{deity_pronoun:он|Он}}`,
  `{{deity_pronoun:я|Я}}` mid-sentence, reflexive свой/себя exempt). The
  Hebrew singular and plural "you" come through as ты and вы. Courtly
  address to Pharaoh is carried by господин, not by вы.

## The names of God

| Hebrew (English) | Hindi | Russian |
|---|---|---|
| YHWH (the LORD) | `{{divine_name:प्रभु\|याहवे}}` (postpositions outside the span: `{{divine_name:प्रभु\|याहवे}} ने`) | `{{divine_name:ГОСПОДЬ\|Яхве}}`, inflected in each option: `ГОСПОДА\|Яхве`, `ГОСПОДУ\|Яхве`, `ГОСПОДОМ\|Яхве`, `ГОСПОДЕ\|Яхве`, vocative `ГОСПОДИ\|Яхве` |
| YHWH Elohim (the LORD God) | `{{divine_name:प्रभु\|याहवे}} परमेश्वर` | `{{divine_name:ГОСПОДЬ\|Яхве}} Бог` |
| Adonai YHWH (Lord GOD) | प्रभु `{{divine_name:परमेश्वर\|याहवे}}` | Владыка `{{divine_name:ГОСПОДЬ\|Яхве}}` |
| Adonai (Lord) | प्रभु | Господь (to a man: господин) |
| Elohim (God) | परमेश्वर | Бог |
| El Shaddai (God Almighty) | सर्वशक्तिमान परमेश्वर | Бог Всемогущий |
| El Elyon (God Most High) | परमप्रधान परमेश्वर (as Hebrews 7:1) | Бог Всевышний (as Hebrews 7:1) |
| the angel of the LORD | `{{divine_name:प्रभु\|याहवे}}` का दूत | Ангел `{{divine_name:ГОСПОДА\|Яхве}}` |

Hindi agreement with God is honorific plural (`{{divine_name:प्रभु|याहवे}} ने
कहा`, `वे`, `उन्होंने`) in both options. Because Hindi प्रभु is both YHWH and
Adonai, the first passage of each book says in a setting_alternative
decision that the setting tells them apart. Russian ГОСПОДЬ in capitals
mirrors the English "the LORD"; *Иегова* and *यहोवा* are not used. Exodus
3:14-15 and 6:2-3, where the name itself is the subject, follow the English
wording and decisions.

## Recurring terms

| Hebrew (English) | Hindi | Russian |
|---|---|---|
| the sons of Israel | `{{gender:इस्राएल की सन्तान\|इस्राएल के पुत्र}}` (L); इस्राएली (B, R), no span | `{{gender:дети Израиля\|сыны Израиля}}` (L); израильтяне (B, R), no span |
| Israel, Israelite(s) | इस्राएल, इस्राएली | Израиль, израильтянин, израильтяне |
| Egypt, Egyptians; Pharaoh; Hebrew(s) | मिस्र, मिस्री; फ़िरौन; इब्रानी (as Philippians 3:5) | Египет, египтяне; фараон; еврей, евреи |
| covenant | वाचा | завет |
| bless, blessing; curse | आशीष देना, आशीष; शाप देना, शाप | благословлять, благословение; проклинать, проклятие |
| holy; the Most Holy Place | पवित्र; परमपवित्र स्थान | святой; Святое святых (as Hebrews) |
| the holy place, the sanctuary | पवित्र स्थान; पवित्रस्थान | святилище |
| clean, unclean (ritually) | शुद्ध, अशुद्ध | чистый, нечистый |
| sin; iniquity; transgression | पाप; अधर्म (L), दोष (B, R); अपराध | грех; беззаконие (L), вина (B, R); преступление |
| make atonement for | के लिए प्रायश्चित करना (L, B); as the English at R | совершить умилостивление за (L, B); as the English at R |
| the tent of meeting | मिलन का तंबू | шатёр встречи |
| the tabernacle (*mishkan*) | निवास-तंबू (L); पवित्र तंबू (B, R), as Hebrews | скиния (L, B); священный шатёр (R), as Hebrews |
| the ark (of the covenant, of the testimony) | (वाचा का, साक्षी का) संदूक, as Revelation | ковчег (завета, свидетельства) |
| Noah's ark | जहाज़, as Hebrews 11:7 | ковчег |
| the testimony (*ʿedut*, the tablets) | साक्षी-पत्र | свидетельство |
| the atonement cover (*kapporet*) | प्रायश्चित का ढकना, as Hebrews 9:5 | место умилостивления (L, B), as Hebrews 9:5; крышка ковчега (R) |
| cherub, cherubim | करूब, करूबों | херувим, херувимы |
| altar | वेदी | жертвенник |
| priest; high priest | याजक; महायाजक | священник; первосвященник |
| Levites | लेवी | левиты |
| ephod; breastpiece; Urim and Thummim | एपोद; सीनाबंद; ऊरीम और तुम्मीम | ефод; нагрудник; урим и туммим |
| lampstand | दीवट | светильник |
| burnt offering | होमबलि | всесожжение |
| grain offering | अन्नबलि | хлебное приношение |
| sin offering | पापबलि | жертва за грех |
| guilt offering | दोषबलि | жертва за вину |
| peace offering (*shelamim*) | मेलबलि | мирная жертва |
| food offering (*ʾishsheh*) | आग में चढ़ाई गई भेंट | огненная жертва |
| soothing aroma | सुखद सुगंध (L, B); ऐसी सुगंध जो प्रभु को भाती है (R) | приятный запах (L, B); запах, который радует (R) |
| without defect | निर्दोष | без изъяна |
| statute; rule; commandment | विधि; नियम; आज्ञा | установление; правило; заповедь |
| a lasting statute | सदा की विधि | вечное установление |
| the congregation (*ʿedah*); the assembly (*qahal*) | मंडली; सभा | община; собрание |
| tribe; clan; father's house | गोत्र; कुल; पितृकुल (L), परिवार (B, R) | колено (L, B), племя (R), as Hebrews; род; отцовский дом (L), семья (B, R) |
| the Sabbath | सब्त | суббота |
| the Passover; Unleavened Bread | फ़सह (as the New Testament); अख़मीरी रोटी का पर्व | Пасха; праздник Пресных хлебов |
| the Feast of Weeks; of Booths; of Ingathering | सप्ताहों का पर्व; झोपड़ियों का पर्व (as John 7:2); फ़सल बटोरने का पर्व | праздник Недель; праздник Кущей (as John 7:2), кущи for the huts; праздник Сбора урожая |
| the Day of Atonement | प्रायश्चित का दिन | День умилостивления |
| serious skin disease (*tsaraʿat*) | गंभीर चर्म रोग, "कोढ़" in a decision | тяжёлая кожная болезнь, "проказа" in a decision |
| steadfast love (*ḥesed*) | अटल प्रेम (L, B); अटल प्रेम or करुणा (R); between people, a favour or kindness: अटल प्रेम (L), कृपा (B, R) | неизменная любовь (L, B); верная любовь or милость (R); between people, a favour or kindness: неизменная любовь (L), милость (B, R) |
| Sheol | शिओल (L); अधोलोक (B, R) | шеол (L); мир мёртвых (B, R), as Revelation's Hades |
| the land flowing with milk and honey | ऐसा देश जिसमें दूध और मधु की धाराएँ बहती हैं | земля, где течёт молоко и мёд |
| the wilderness | निर्जन प्रदेश, as Matthew 3:1 | пустыня |
| slave, servant (*ʿeved*) | दास, every level, as the New Testament; सेवक only where service alone is the point, with a decision | раб, every level, as the New Testament; слуга only where service alone is the point, with a decision |
| foreigner, sojourner (*ger*) | परदेशी | пришелец (L, B); чужеземец (R) |
| firstborn | पहलौठा | первенец |

## Names

Names that occur in the New Testament keep the New Testament form in this
translation (`grep` the name in content/ACT, HEB, ROM, MAT, LUK with your
language). Keep a list for the book and use one form throughout.

| English | Hindi | Russian |
|---|---|---|
| Adam, Eve, Cain, Abel, Seth | आदम, हव्वा, कैन, हाबिल, शेत | Адам, Ева, Каин, Авель, Сиф |
| Enoch, Lamech, Noah, Shem, Ham, Japheth | हनोक, लेमेक, नूह, शेम, हाम, येपेत | Енох, Ламех, Ной, Сим, Хам, Иафет |
| Abram, Abraham; Sarai, Sarah | अब्राम, अब्राहम; सारै, सारा | Аврам, Авраам; Сара, Сарра |
| Lot, Hagar, Ishmael, Isaac | लूत, हाजिरा, इश्माएल, इसहाक | Лот, Агарь, Измаил, Исаак |
| Rebekah, Esau, Jacob, Laban | रिबका, एसाव, याकूब, लाबान | Ревекка, Исав, Иаков, Лаван |
| Leah, Rachel, Bilhah, Zilpah | लिआ, राहेल, बिल्हा, जिल्पा | Лия, Рахиль, Валла, Зелфа |
| Reuben, Simeon, Levi, Judah | रूबेन, शिमोन, लेवी, यहूदा | Рувим, Симеон, Левий, Иуда |
| Dan, Naphtali, Gad, Asher | दान, नप्ताली, गाद, आशेर | Дан, Неффалим, Гад, Асир |
| Issachar, Zebulun, Dinah | इस्साकार, जबूलून, दीना | Иссахар, Завулон, Дина |
| Joseph, Benjamin, Ephraim, Manasseh | यूसुफ़, बिन्यामीन, एप्रैम, मनश्शे | Иосиф, Вениамин, Ефрем, Манассия |
| Moses, Aaron, Miriam, Joshua, Caleb | मूसा, हारून, मिरियम, यहोशू, कालेब | Моисей, Аарон, Мариам, Иисус Навин (Иисус, сын Навина), Халев |
| Jethro, Balaam, Balak, Korah, Phinehas | यित्रो, बिलाम, बालाक, कोरह, पीनहास | Иофор, Валаам, Валак, Корей, Финеес |
| Canaan, Sinai, Horeb, Jordan, Moab, Edom | कनान, सीनै, होरेब, यरदन, मोआब, एदोम | Ханаан, Синай, Хорив, Иордан, Моав, Едом |
| Amorites, Canaanites, Hittites | एमोरी, कनानी, हित्ती | аморреи, хананеи, хетты |
| Melchizedek, Salem; Sodom, Gomorrah | मलिकिसिदक, शालेम; सदोम, अमोरा | Мелхиседек, Салим; Содом, Гоморра |

Other names: Hindi follows the established Hindi Bible form where one exists
and otherwise transcribes the Hebrew, with nukta where Hindi writes one;
Russian follows the established Russian Bible form (the Synodal
transcriptions are traditional names, not copyrighted wording), and
otherwise transcribes the Hebrew.
