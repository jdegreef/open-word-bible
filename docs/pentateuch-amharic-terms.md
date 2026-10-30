# Amharic: the Pentateuch

**Status: proposed, awaiting a native Amharic reviewer.** The choices used to
draft Genesis to Deuteronomy in Amharic, so that books drafted in parallel
read as one translation. `docs/amharic-style.md` still holds (section 7a on
the Old Testament and poetry, 7b on the conventions settled in the New
Testament); these tables add the recurring words. If a choice here changes,
every passage drafted under it is revised. Decision text stays in English,
quoting the Amharic words.

## Drafting

- Translate from the Hebrew, using the literal gloss, the English and the
  meaning decisions to see how a verse was read; never from a reference
  Bible, and never reproduce the wording of an Amharic Bible (1962, 1980,
  the New Amharic Standard Version). Familiar chapters (Genesis 1–3,
  Exodus 20, Deuteronomy 6) pull hardest: draft from the gloss and reword any
  sentence that matches a well-known version beyond a short fixed phrase.
- A Hebrew record holds whole verses. Keep every `\v N ` marker where the
  English has it, and each level's own poetry breaks (`\q `) where the
  English level has them (Genesis 49, Exodus 15, Numbers 23–24,
  Deuteronomy 32–33).
- Narrative is in the past at every level. Literal keeps the chain of "and"
  that the Hebrew narrative tense makes (…አለ፤ …አደረገ፤ or -ም / -ና linking);
  Balanced and Readable join clauses as ordinary Amharic does.
- Laws and instructions: the imperfect or the jussive at Literal and
  Balanced (አትግደል, ያቀርባል, ያቅርብ); -አለበት ("must") or the imperative at
  Readable.
- **Address.** God speaks to one person, and to Israel addressed in the
  singular, with አንተ (አንቺ to a woman); to Israel or a group in the plural,
  with እናንተ. People pray to God with አንተ. People speak to each other with
  አንተ, አንቺ, እናንተ; to a king, Pharaoh, a master, a lord or a stranger they
  honour with እርስዎ (with ጌታዬ, and "your servant" as አገልጋይዎ where the
  Hebrew uses the courtly third person). Keep one choice for each pair of
  speakers through a book.
- Settings: `divine_name` on every YHWH; `units` as below; `gender` only
  where Amharic really has two wordings (ልጆች already includes daughters).
  No `deity_pronoun` spans (no capitals; the note goes on the first record of
  a file whose English has a span).
- **Measures:** metric by default where the English converts, the original
  unit as the alternative; Literal keeps the original unit. Where the English
  has no units span, neither does the Amharic. Use the English values in
  metric: cubit (ክንድ) 45 ሳንቲ ሜትር, span (ስንዝር) 23 ሳንቲ ሜትር, handbreadth (መዳፍ)
  7.5 ሳንቲ ሜትር; shekel (ሰቅል) 11.5 ግራም, beka (ቤካ) 5.7 ግራም, gerah (ጌራ)
  0.6 ግራም, talent (መክሊት) 34 ኪሎ, mina (ምናን) 0.6 ኪሎ; ephah (ኢፍ)
  22 ሊትር, omer (ጎሞር) 2.2 ሊትር, seah 7 ሊትር, hin (ኢን) 3.7 ሊትር, homer and kor
  (ቆሮስ) 220 ሊትር. Decimals with a point (1.10 ሜትር), as Ethiopian print
  does.
- Rendering decisions: zero to two per verse, only where Amharic had to
  choose. A book-wide choice is recorded once, in its first passage of each
  book; later chapters follow it.
- **New Testament quotations.** Where the New Testament quotes a verse and
  the Hebrew agrees with the Greek, keep the Amharic the New Testament already
  has (Genesis 2:24 and Matthew 19:5; Genesis 15:6 and Romans 4:3;
  Deuteronomy 6:5 and Matthew 22:37; Deuteronomy 8:3 and Matthew 4:4;
  Exodus 20 and Matthew 19:18–19); where they differ, follow the Hebrew and
  say so in a decision.

## The names of God

| Hebrew (English) | Amharic |
|---|---|
| YHWH (the LORD) | `{{divine_name:እግዚአብሔር\|ያህዌ}}`; with a prefix or suffix, the whole word in each option: `{{divine_name:የእግዚአብሔር\|የያህዌ}}`, `{{divine_name:ለእግዚአብሔር\|ለያህዌ}}`, `{{divine_name:እግዚአብሔርን\|ያህዌን}}`, `{{divine_name:በእግዚአብሔር\|በያህዌ}}` |
| YHWH Elohim (the LORD God) | `{{divine_name:እግዚአብሔር\|ያህዌ}} አምላክ` |
| Adonai YHWH (Lord GOD) | ጌታ `{{divine_name:እግዚአብሔር\|ያህዌ}}` |
| Adonai (Lord); adoni (my lord) | ጌታ; ጌታዬ |
| Elohim (God) | እግዚአብሔር where the one God is meant and YHWH does not stand beside it (Genesis 1); አምላክ for "a god", "the God of …" (የአብርሃም አምላክ), "my God, your God" (አምላኬ, አምላክህ); አማልክት for "gods" |
| El Shaddai (God Almighty) | ሁሉን የሚችል አምላክ |
| El Elyon (God Most High) | ልዑል አምላክ |
| the angel of the LORD; the angel of God | `{{divine_name:የእግዚአብሔር\|የያህዌ}}` መልአክ; የእግዚአብሔር መልአክ |

Exodus 3:14–15 and 6:2–3, where the name itself is the subject, follow the
English wording and decisions: the alternative ያህዌ there is the name the
passage explains.

## Recurring terms

| Hebrew (English) | Amharic |
|---|---|
| heavens and earth; the expanse; the deep | ሰማያትና ምድር (L), ሰማይና ምድር (B, R); ጠፈር; ጥልቁ |
| These are the generations (*toledot*) of … | የ… ትውልድ ታሪክ ይህ ነው (L, B); ይህ የ… ታሪክ ነው (R) |
| offspring, seed (*zeraʿ*) | ዘር (L, B); ዘር, ልጆች (R, as the English level) |
| the sons of Israel | የእስራኤል ልጆች (L, B); እስራኤላውያን (R); no span: ልጆች already includes daughters |
| Egypt, Egyptians; Pharaoh | ግብፅ, ግብፃውያን; ፈርዖን |
| covenant | ቃል ኪዳን |
| bless, blessing; curse | መባረክ, በረከት; መርገም, እርግማን |
| holy; the Most Holy Place | ቅዱስ; ቅድስተ ቅዱሳን (L, B), እጅግ ቅዱስ የሆነው ስፍራ (R) |
| the holy place; the sanctuary | ቅዱሱ ስፍራ; መቅደስ |
| clean, unclean (ritually) | ንጹሕ, ርኩስ |
| sin; iniquity; transgression | ኃጢአት; በደል; መተላለፍ (L), ዓመፅ (B, R) |
| make atonement for | ማስተስረይ (L, B: ያስተሰርይላቸዋል); R as the English level (ኃጢአታቸው እንዲሰረይላቸው) |
| the tent of meeting | የመገናኛው ድንኳን |
| the tabernacle (*mishkan*) | ማደሪያው (L, B); የማደሪያው ድንኳን (R) |
| the ark (of the covenant, of the testimony); Noah's ark | ታቦት (የቃል ኪዳኑ ታቦት, የምስክሩ ታቦት); መርከብ |
| the testimony (*ʿedut*) | ምስክሩ |
| the atonement cover (*kapporet*) | የስርየት መክደኛ |
| cherub, cherubim | ኪሩብ, ኪሩቤል |
| altar; priest; high priest; Levites | መሠዊያ; ካህን; ሊቀ ካህናት; ሌዋውያን |
| ephod; breastpiece; Urim and Thummim | ኤፉድ; የደረት ኪስ; ኡሪምና ቱሚም |
| lampstand | መቅረዝ |
| burnt offering; grain offering | የሚቃጠል መሥዋዕት; የእህል ቁርባን |
| sin offering; guilt offering | የኃጢአት መሥዋዕት; የበደል መሥዋዕት |
| peace offering (*shelamim*) | የኅብረት መሥዋዕት |
| food offering (*ʾishsheh*) | በእሳት የሚቀርብ መሥዋዕት |
| soothing aroma | ደስ የሚያሰኝ መዓዛ |
| without defect | ነውር የሌለበት |
| statute; rule; commandment; law (*torah*) | ሥርዓት; ደንብ; ትእዛዝ; ሕግ |
| a lasting statute | የዘላለም ሥርዓት |
| the congregation (*ʿedah*); the assembly (*qahal*) | ማኅበሩ; ጉባኤው |
| tribe; clan; father's house | ነገድ; ጎሳ; የአባት ቤት (L), ቤተሰብ (B, R) |
| the Sabbath | ሰንበት |
| the Passover; Unleavened Bread | ፋሲካ; የቂጣ በዓል |
| the Day of Atonement | የስርየት ቀን |
| serious skin disease (*tsaraʿat*) | ለምጽ (L); ከባድ የቆዳ በሽታ (B, R), with a decision where it first appears |
| steadfast love (*ḥesed*) | ጽኑ ፍቅር; ታማኝነት, ቸርነት where the English level says "kindness" or "loyalty" |
| faithfulness (*ʾemet*) | ታማኝነት (truth: እውነት) |
| Sheol | ሲኦል (L); የሙታን ዓለም (B, R): ሲኦል now reads as hell, with a decision |
| the land flowing with milk and honey | ወተትና ማር የምታፈስ ምድር |
| the wilderness | ምድረ በዳ |
| slave, servant (*ʿeved*) | ባሪያ (L); አገልጋይ (B, R); ባሪያ at every level for slavery in Egypt and for slaves bought and sold |
| foreigner, sojourner (*ger*) | መጻተኛ (L, B); ስደተኛ, እንግዳ (R) |
| firstborn | በኩር (L, B); የመጀመሪያ ልጅ (R) |
| the flood | የጥፋት ውኃ |
| the Red Sea (*yam suf*) | ቀይ ባሕር, with a decision on "Sea of Reeds" |
| the Nile (*yeʾor*, "the river") | ወንዙ (L); የዓባይ ወንዝ (B, R) |

## Names

Proper names take their usual Ethiopian form; keep one form through a book.

| English | Amharic |
|---|---|
| Adam, Eve, Cain, Abel, Seth, Enosh | አዳም, ሔዋን, ቃየን, አቤል, ሴት, ሄኖስ |
| Enoch, Methuselah, Lamech | ሄኖክ, ማቱሳላ, ላሜሕ |
| Noah, Shem, Ham, Japheth, Nimrod, Terah | ኖኅ, ሴም, ካም, ያፌት, ናምሩድ, ታራ |
| Abram, Abraham; Sarai, Sarah | አብራም, አብርሃም; ሦራ, ሣራ |
| Lot, Hagar, Ishmael, Isaac | ሎጥ, አጋር, እስማኤል, ይስሐቅ |
| Rebekah, Esau, Jacob, Laban | ርብቃ, ዔሳው, ያዕቆብ, ላባ |
| Leah, Rachel, Bilhah, Zilpah | ልያ, ራሔል, ባላ, ዘለፋ |
| Reuben, Simeon, Levi, Judah | ሮቤል, ስምዖን, ሌዊ, ይሁዳ |
| Dan, Naphtali, Gad, Asher | ዳን, ንፍታሌም, ጋድ, አሴር |
| Issachar, Zebulun, Dinah, Joseph, Benjamin | ይሳኮር, ዛብሎን, ዲና, ዮሴፍ, ብንያም |
| Ephraim, Manasseh; Tamar, Perez, Zerah | ኤፍሬም, ምናሴ; ትዕማር, ፋሬስ, ዛራ |
| Melchizedek; Potiphar | መልከ ጼዴቅ; ጲጥፋራ |
| Moses, Aaron, Miriam; Joshua, Caleb | ሙሴ, አሮን, ማርያም; ኢያሱ, ካሌብ |
| Jethro, Zipporah; Nadab, Abihu, Eleazar, Ithamar | ዮቶር, ሲፓራ; ናዳብ, አብዩድ, አልዓዛር, ኢታምር |
| Phinehas, Korah, Balaam, Balak, Og, Sihon | ፊንሐስ, ቆሬ, በለዓም, ባላቅ, ዐግ, ሴዎን |
| Eden, Babel, Ur, Haran, Canaan | ኤደን, ባቤል, ዑር, ካራን, ከነዓን |
| Sodom, Gomorrah, Bethel, Hebron, Beersheba | ሰዶም, ገሞራ, ቤቴል, ኬብሮን, ቤርሳቤህ |
| Goshen, Sinai, Horeb, Kadesh, Moab, Edom | ጌሤም, ሲና, ኮሬብ, ቃዴስ, ሞዓብ, ኤዶም |
| Amalek, Midian; the Jordan | አማሌቅ, ምድያም; ዮርዳኖስ |
| Canaanites, Amorites, Hittites, Hivites | ከነዓናውያን, አሞራውያን, ኬጢያውያን, ኤውያውያን |
| Perizzites, Jebusites, Girgashites; Philistines | ፌርዛውያን, ኢያቡሳውያን, ጌርጌሳውያን; ፍልስጥኤማውያን |

## Settled while drafting Genesis and Exodus

These came out of harmonising chapters drafted in parallel and hold for the
rest of the Pentateuch.

- **Address.** Family members, parents and in-laws included, say አንተ and
  አንቺ to each other; respect is carried by አባቴ and እባክህ (Genesis 27:19,
  Exodus 4:18). Moses and Aaron, as God's messengers, say አንተ to Pharaoh
  (Exodus 3:18; 5:3; 7:16); his officials and the Hebrew foremen say እርስዎ.
  A single honoured guest is ጌታዬ with እርስዎ, and the speaker is አገልጋይዎ.
- **"Here I am"** (*hinneni*): እነሆኝ (L); «አቤት» (B, R).
- **"Be fruitful and multiply"**: ተዋለዱ፣ ብዙ (ይዋለዱ፣ ይብዙ), not the 1962 Bible's
  wording. **Image** (*tselem*) is መልክ; **likeness** (*demut*) is አምሳል.
- **Most holy** of things and offerings is እጅግ ቅዱስ; ቅድስተ ቅዱሳን only for the
  Most Holy Place.
- **Wave offering**: የሚወዘወዝ መሥዋዕት for animal portions, የሚወዘወዝ መባ for
  things given (gold, a sheaf). **Drink offering**: የመጠጥ ቁርባን. **Ordination**:
  ሹመት; "fill the hand" እጅ መሙላት (L), መሾም (B, R).
- **Feasts**: የቂጣ በዓል, የመከር በዓል, የሳምንታት በዓል, የመሰብሰብ በዓል.
- **The tabernacle's craft words** are those of Exodus 25–40: bronze ነሐስ,
  acacia ግራር, frames ሳንቃዎች, bars መወርወሪያዎች, bases መሠረቶች, clasps ቁልፎች,
  loops ዙሮች, veil መጋረጃው, screen መከለያ, courtyard አደባባይ, pillars ምሰሶዎች,
  fine twisted linen የተፈተለ ቀጭን በፍታ, blue, purple and scarlet yarn ሰማያዊ፣
  ሐምራዊና ቀይ ፈትል, basin ሰን with its stand መቆሚያ. The priests' garments:
  tunic ቀሚስ, robe መጎናጸፊያ, band of the ephod መቀነት, sash ቀበቶ, turban
  ጥምጥም, caps ቆቦች, holy garments የቅድስና ልብሶች (L) / የተቀደሱ ልብሶች (B, R).
- **The LORD's name proclaimed** (Exodus 34:6–7): ርኅሩኅና ቸር አምላክ፣ ለቁጣ
  የዘገየ (L) / ቶሎ የማይቆጣ (B, R)፣ ጽኑ ፍቅር … ; later echoes keep it.
- **Pharaoh's heart**: Literal keeps the three Hebrew verbs apart (*ḥazaq*
  አጸና, *kabed* አከበደ, *qashah* አደነደነ); Balanced አደነደነ, Readable እልከኛ
  አደረገ.
- **Yam suf**: የሸምበቆ ባሕር (L), ቀይ ባሕር (B, R).
- **Names**: Abram ↔ Abraham and Sarai ↔ Sarah change at Genesis 17;
  Haran the man ሐራን, the city ካራን; Cush ኩሽ (a decision explains why not
  ኢትዮጵያ); Phicol ፊኮል, Machpelah ማክፌላ, Beer-lahai-roi ብኤርላሃይሮኢ,
  Judah's son Shelah ሴሎም, Reuel ራጉኤል, Bezalel ባስልኤል, Oholiab ኦሆሊያብ.
- **Measures** are written in words for the unit: N ሜትር ያህል, N ሳንቲ ሜትር ያህል,
  N ኪሎ ያህል, N ግራም ያህል, N ሊትር ያህል.
- A -ም after a divine-name span goes outside it:
  `{{divine_name:እግዚአብሔር|ያህዌ}}ም`.
