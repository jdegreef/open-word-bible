# Ukrainian: the Old Testament and the rest of the New

**Status: proposed, awaiting a native Ukrainian reviewer.** These are the
choices used to draft the 58 books that Ukrainian still lacked after the
Gospels, Acts, Romans, Ephesians and James: the rest of the New Testament
and the whole Old Testament. The books are drafted in parallel, so this note
settles in advance what they share. `docs/ukrainian-style.md` still holds in
full; where the books already drafted in Ukrainian have a form, that form
wins. Each book's own terms note (`docs/isaiah-terms.md`,
`docs/psalms-proverbs-five-languages-terms.md` and the others) still settles
the meaning; this note settles only the Ukrainian wording. If a choice here
changes, every passage drafted under it is revised.

Decision text stays in English, quoting the Ukrainian words.

## Drafting

- Translate from the Hebrew (and the Greek), using the literal gloss, the
  English levels and the meaning decisions to see how a sentence was read.
  Never from a reference Bible, never through Russian, and never reproduce
  a copyrighted Ukrainian Bible's wording (`docs/ukrainian-style.md` section
  1 names them). Familiar passages pull hardest (Genesis 1-3, Exodus 20,
  Deuteronomy 6, Psalms 1, 23, 51, 91, Isaiah 53, Numbers 6:24-26): draft
  from the gloss and rewrite any sentence that matches a well-known version
  for more than a short common phrase.
- Keep every `\v N ` marker where the English level has it, and each level's
  own poetry breaks (`\q `) where the English level has them.
- Each level opens and closes the same quotations as the English level, in
  the same order, with « » outside, “ ” inside, ‘ ’ inside that.
- Narrative: perfective past for events (сказав, пішов, побудував),
  imperfective for what went on or kept happening (ходив, приносив). The
  Hebrew *wayyiqtol* chain is "і... і..." at Literal, smoothed at Balanced,
  split into short sentences at Readable.
- Laws and instructions: imperative or future at L and B (не вбивай; нехай
  принесе; він принесе), «не можна», «мусить», «має» at R.
- Rendering decisions: zero to two per sentence, only where Ukrainian had to
  choose. A book-wide choice is recorded once, in the book's first file;
  later chapters follow it.
- Measures: metric by default where the English converts, the original unit
  as the alternative; Literal keeps the original unit where the English
  Literal does. Where the English has no `units` span, Ukrainian has none.
  Use the English conversion's values (cubit 45 cm, shekel 11.5 g, talent
  34 kg, ephah 22 litres, hin 3.7 litres, homer and cor 220 litres), with a
  decimal comma (11,5 г) and a thin no-break space in numbers of five digits
  or more (603 550). Days, years, ages and counts are not units.

## Forms of address

As in the New Testament: ти to God and from God at every level, with
`deity_pronoun` spans on God's pronouns (`{{deity_pronoun:він|Він}}`,
`{{deity_pronoun:я|Я}}` mid-sentence; reflexive свій, себе exempt). The
Hebrew singular and plural *you* come through as ти and ви. Courtly address
to a king or a master is carried by the words (мій пане, царю, мій володарю)
and by "твій раб" for "I", not by ви. The vocative throughout: Господи, Боже,
царю, сину мій, доню.

## The names of God

| Hebrew (English) | Ukrainian |
|---|---|
| YHWH (the LORD) | `{{divine_name:ГОСПОДЬ\|Ягве}}`, inflected inside each option: `ГОСПОДА\|Ягве`, `ГОСПОДУ\|Ягве` (dative), `ГОСПОДОМ\|Ягве`, `ГОСПОДІ\|Ягве` (locative), vocative `ГОСПОДИ\|Ягве`. With a preposition, keep it outside the span unless its form changes (`від {{divine_name:ГОСПОДА\|Ягве}}`). |
| YHWH Elohim (the LORD God) | `{{divine_name:ГОСПОДЬ\|Ягве}} Бог` |
| Adonai YHWH (Lord GOD) | Владика `{{divine_name:ГОСПОДЬ\|Ягве}}` |
| Adonai (Lord) | Господь, never in capitals (to a man: пан) |
| Elohim (God) | Бог; *бог*, *боги* for other gods |
| El Shaddai (God Almighty) | Бог Всемогутній |
| El Elyon (God Most High) | Всевишній, Бог Всевишній (as Hebrews 7:1) |
| YHWH Tsebaot (the LORD of hosts) | `{{divine_name:ГОСПОДЬ\|Ягве}}` Саваот (L), `{{divine_name:ГОСПОДЬ\|Ягве}}` Небесних Військ (B), `{{divine_name:ГОСПОДЬ\|Ягве}}` Вседержитель (R), following the English level's sense |
| the angel of the LORD | ангел `{{divine_name:ГОСПОДА\|Ягве}}` |
| the Holy One of Israel | Святий Ізраїлів |

ГОСПОДЬ in capitals mirrors the English "the LORD", and keeps the name
apart from Adonai, Господь. *Єгова* is not used. The alternative is Ягве,
with г for the Hebrew h as Ukrainian transcribes it (Авраам, Агар, Гедеон);
a reviewer may prefer Яхве. The first file of each book says in a
setting_alternative decision that the setting tells the name apart from
Adonai. Exodus 3:14-15 and 6:2-3, where the name itself is the subject,
follow the English wording and decisions.

In the New Testament, "Lord" quoting the divine name stays Господь with no
span, as in the books already drafted.

## Recurring terms

| Hebrew (English) | Ukrainian |
|---|---|
| the sons of Israel | `{{gender:нащадки Ізраїля\|сини Ізраїля}}` (L); ізраїльтяни (B, R), no span |
| Israel, Israelite(s); Judah (the kingdom); Jew(s) | Ізраїль, ізраїльтянин, ізраїльтяни; Юдея, юдеї |
| Egypt; Pharaoh; Hebrew(s) | Єгипет, єгиптяни; фараон; єврей, євреї |
| covenant | завіт (as Acts 7:8) |
| bless, blessing; curse | благословляти, благословення; проклинати, прокляття |
| holy; the Most Holy Place | святий; Святеє Святих (L, B), найсвятіше місце (R) |
| the sanctuary | святилище |
| clean, unclean (ritually) | чистий, нечистий |
| sin; iniquity; transgression | гріх; беззаконня (L), провина (B, R); переступ |
| make atonement for | звершити очищення за (L, B); as the English at R |
| the tent of meeting | намет зустрічі |
| the tabernacle (*mishkan*) | скинія (L, B); священний намет (R) |
| the ark (of the covenant, of the testimony) | ковчег (завіту, свідчення); Noah's ark ковчег |
| the testimony (the tablets) | свідчення |
| the atonement cover (*kapporet*) | віко ковчега (B, R); місце очищення (L) |
| cherub, cherubim | херувим, херувими |
| altar; priest; high priest | жертовник; священник; первосвященик |
| Levites | левити |
| ephod; breastpiece; Urim and Thummim | ефод; нагрудник; урім і туммім |
| lampstand | світильник |
| burnt offering; grain offering | всепалення; хлібна жертва |
| sin offering; guilt offering; peace offering | жертва за гріх; жертва за провину; мирна жертва |
| food offering (*ʾishsheh*) | вогняна жертва |
| soothing aroma | приємний запах (L, B); запах, що тішить (R) |
| without defect | без вади |
| statute; rule; commandment | постанова; правило; заповідь |
| a lasting statute | вічна постанова |
| the congregation (*ʿedah*); the assembly (*qahal*) | громада; зібрання |
| tribe; clan; father's house | племʼя (every level; not коліно); рід; батьківський дім (L), родина (B, R) |
| the Sabbath; Passover; Unleavened Bread | субота; Пасха; свято Опрісноків (L, B), свято Прісного хліба (R) |
| Feast of Weeks; Booths; Ingathering | свято Тижнів; свято Кущів (L, B), свято Наметів (R), as John 7:2, the booths кущі (L, B); свято Збору врожаю |
| the Day of Atonement | День Очищення |
| serious skin disease (*tsaraʿat*) | тяжка шкірна хвороба, "проказа" in a decision |
| steadfast love (*ḥesed*) | незмінна любов (L, B); вірна любов or милість (R); between people, a kindness: незмінна любов (L), доброта (B, R) |
| faithfulness (*ʾemunah*, *ʾemet*) | вірність; істина where the sense is truth |
| righteousness; justice (*mishpat*) | праведність; правосуддя, справедливість |
| salvation; save | спасіння (L, B), порятунок (R); спасати, рятувати |
| glory (*kavod*) | слава |
| Sheol | шеол (L); світ мертвих (B, R), as Revelation's Hades |
| the pit | яма (L); могила (B, R) |
| the land flowing with milk and honey | край, що тече молоком і медом |
| wilderness | пустеля |
| slave, servant (*ʿeved*) | раб, every level, as the New Testament; слуга only where service alone is the point, with a decision; "your servant" for "I" in courtly speech твій раб (L, B), я (R) where the English Readable says "I" |
| foreigner, sojourner (*ger*) | приходько (L, B); чужинець (R) |
| firstborn | первісток |
| idols | ідоли; Baal Ваал, Asherah Ашера (the pole: Ашера, ашерівський стовп at R) |
| high places | пагірки (L), узвишшя (B, R), with a decision once per book |
| prophesy; vision; oracle (*massaʾ*) | пророкувати; видіння; пророцтво |
| "thus says the LORD" | так говорить `{{divine_name:ГОСПОДЬ\|Ягве}}` (every level) |
| "declares the LORD" (*neʾum YHWH*) | говорить `{{divine_name:ГОСПОДЬ\|Ягве}}` (L, B); каже `{{divine_name:ГОСПОДЬ\|Ягве}}` (R) |
| "the word of the LORD came to" | було слово `{{divine_name:ГОСПОДА\|Ягве}}` до (L, B); `{{divine_name:ГОСПОДЬ\|Ягве}}` сказав (R) |
| "on that day"; "the day of the LORD" | того дня; день `{{divine_name:ГОСПОДА\|Ягве}}` |
| Selah | села (L, B), left out at R where the English Readable leaves it out |
| hallelujah | алілуя |
| wisdom; folly; the fool | мудрість; безумство (L, B), дурість (R); безумний (L, B), нерозумний (R) |
| the fear of the LORD | страх `{{divine_name:ГОСПОДНІЙ\|перед Ягве}}` (L), страх перед `{{divine_name:ГОСПОДОМ\|Ягве}}` (B), шанувати `{{divine_name:ГОСПОДА\|Ягве}}` (R), following the English level |

## Regnal formulas (Samuel, Kings, Chronicles)

One wording per level through the history books.

- **Accession.** L: «У N-му році X, царя Юдеї, зацарював Y, син Z, над
  Ізраїлем у Самарії, і царював N років.» B smooths; R may split the
  sentence.
- **Age and mother.** «Йому було N років, коли він зацарював, і N років він
  царював у Єрусалимі; імʼя його матері — X».
- **Verdict.** «він робив те, що було зле / правильне в очах
  `{{divine_name:ГОСПОДА|Ягве}}`» (L, B); «що не подобалося / подобалося
  ГОСПОДУ» at R, in the same span.
- **Source.** «Хіба це не записано в книзі хронік царів Ізраїлю?»
- **Death.** «спочив зі своїми батьками» (L, B), with the English span where
  it has one; «помер» (R).

Chronicles reuses the Samuel or Kings wording at each level where its
Hebrew is the same; where the Hebrew differs, the wording differs.

## Poetry and prophecy

- Psalms, Proverbs, Job, the Song, Lamentations and the poetic prophets keep
  the English level's `\q ` breaks exactly, one Ukrainian line for each
  English line. Ukrainian need not rhyme or keep a metre.
- Psalm titles (the superscriptions, verse 1 in the Hebrew numbering where
  the records have them) follow the English: «Псалом Давида», «Для
  диригента», «Маскіл», «Міктам» at L; B and R as the English explains them.
- Parallel lines: keep the parallel at L and B (the same word for the same
  Hebrew word where the English does), even where Ukrainian style would
  vary it.
- Acrostics (Psalms 119 and the others, Lamentations 1-4, Proverbs 31) are
  not imitated; the English decisions say so, and Ukrainian follows them.
- The prophets' oracle formulas use the table above every time, so the
  formula reads the same through Isaiah to Malachi.

## The rest of the New Testament

- Hebrews and Revelation take their cultic words from the table above
  (скинія, Святеє Святих, первосвященик, жертовник, ковчег завіту, віко
  ковчега / місце очищення), so the Old Testament and its quotation in the
  New read alike.
- Old Testament quotations in Hebrews, Peter and Revelation are drafted from
  the Greek as quoted; where the Hebrew and Greek agree, reuse the Old
  Testament book's Ukrainian wording at each level once that book is on
  main.
- Paul's letters keep the Romans and Ephesians terms (`docs/ukrainian-style.md`
  section 7a): праведність, виправдати, Закон, тіло (L, B) / людська природа
  (R), Дух, благодать, «у Христі» inside the `christos` options.
- Revelation: Агнець (L, B), Ягня (R); печать, печатка (L, B, R); звір;
  «Той, хто сидить на престолі»; престол (L, B), трон (R); Вседержитель
  for *pantokratōr*; Гадес (L), світ мертвих (B, R).

## Names

Names that occur in the New Testament keep the New Testament form in this
translation (grep the name in `content/MAT`, `LUK`, `ACT`, `ROM`, `JAS` with
`uk`). Otherwise use the established Ukrainian Bible form of the name (a
traditional transcription is a name, not copyrighted wording), and
otherwise transcribe the Hebrew with г for h. One form per name through
every book.

| English | Ukrainian |
|---|---|
| Adam, Eve, Cain, Abel, Seth | Адам, Єва, Каїн, Авель, Сит |
| Enoch, Methuselah, Lamech, Noah, Shem, Ham, Japheth | Енох, Метушелах, Ламех, Ной, Сим, Хам, Яфет |
| Abram, Abraham; Sarai, Sarah | Аврам, Авраам; Сара (Sarai), Сарра (Sarah) |
| Lot, Hagar, Ishmael, Isaac | Лот, Агар, Ізмаїл, Ісаак |
| Rebekah, Esau, Jacob, Laban | Ревека, Ісав, Яків, Лаван |
| Leah, Rachel, Bilhah, Zilpah | Лія, Рахіль, Білга, Зілпа |
| Reuben, Simeon, Levi, Judah | Рувим, Симеон, Левій, Юда |
| Dan, Naphtali, Gad, Asher, Issachar, Zebulun, Dinah | Дан, Нефталим, Гад, Асир, Іссахар, Завулон, Дина |
| Joseph, Benjamin, Ephraim, Manasseh | Йосиф, Веніямин, Єфрем, Манасія |
| Moses, Aaron, Miriam, Joshua, Caleb | Мойсей, Аарон, Міріям, Ісус Навин (Joshua son of Nun; Ісус at B and R once he is named), Калев |
| Jethro, Balaam, Balak, Korah, Phinehas | Їтро, Валаам, Валак, Корей, Пінхас |
| Gideon, Samson, Deborah, Jephthah | Гедеон, Самсон, Девора, Єфтай |
| Ruth, Naomi, Boaz, Obed | Рут, Ноомі, Вооз, Овид (as Matthew 1:5) |
| Samuel, Eli, Hannah, Saul, Jonathan | Самуїл, Ілій, Анна, Саул, Йонатан |
| David, Goliath, Bathsheba, Nathan, Absalom, Joab | Давид, Голіят, Вірсавія, Натан, Авесалом, Йоав |
| Solomon, Rehoboam, Jeroboam, Ahab, Jezebel | Соломон, Ровоам, Єровоам, Ахав, Єзавель |
| Elijah, Elisha, Hezekiah, Josiah, Nebuchadnezzar | Ілля, Єлисей, Єзекія, Йосія, Навуходоносор |
| Ezra, Nehemiah, Esther, Mordecai, Haman, Job | Ездра, Неемія, Естер, Мордехай, Гаман, Йов |
| Isaiah, Jeremiah, Ezekiel, Daniel | Ісая, Єремія, Єзекіїл, Даниїл |
| Hosea, Joel, Amos, Obadiah, Jonah, Micah | Осія, Йоїл, Амос, Овдій, Йона, Михей |
| Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi | Наум, Авакум, Софонія, Огій, Захарія, Малахія |
| Canaan, Sinai, Horeb, Jordan, Moab, Edom | Ханаан, Синай, Хорив, Йордан, Моав, Едом |
| Amorites, Canaanites, Hittites, Philistines | амореї, ханаанеї, хетеї, филистимляни |
| Babylon, Assyria, Nineveh, Persia, Zion | Вавилон, Ассирія, Ніневія, Персія, Сіон |
| Melchizedek, Salem; Sodom, Gomorrah | Мелхиседек, Салим; Содом, Гоморра |

Book-specific names not listed here: settle them in the book's first file
and keep them through the book.
