# Korean review checklist

The starting point for native Korean reviewers. Every book of the Bible is
drafted in Korean, and every record is `ai_draft`. Most of the wording follows
a few dozen book-wide choices made by the drafters: the speech levels, the
divine-name span, the key terms, the recurring formulas. A reviewer who
settles those first settles the wording of thousands of verses at once, so
start with section 1.

How to use it:

- **Work down section 1 first.** Each item decides wording in many verses. Tick
  it when you agree, or write the change you want beside it.
- **Then section 2**, the uncertain decisions that recur. Each cluster is one
  question asked many times; answer it once.
- **Then sections 3 and 4**: places where the drafts disagree with each other,
  and the famous passages to check for originality.
- The full list of every Korean decision the drafters marked uncertain (1,065
  of them, with links) is `docs/review-notes/ko-uncertain.md`. Tick items
  there as they are settled and regenerate it with
  `python3 scripts/review_checklist.py ko --write`.

A choice is changed by editing the terms doc that records it and then revising
every passage drafted under it (the docs say so: "If a choice here changes,
every passage drafted under it is revised"). Two choices were settled by the
founder (Protestant names and 하나님; the speech levels of korean-style.md
section 4); raise a change to those with the founder. Records stay `ai_draft`
until a named reviewer approves them; nothing is marked reviewed by Claude.

Doc names below are short: "style" is `docs/korean-style.md`; "Genesis",
"Pentateuch", "Joshua–Ruth", "Samuel", "Kings", "Psalms", "Isaiah–Ezra",
"Nehemiah–Song" and "Lamentations–Twelve" are the Vietnamese–Korean and
five-language terms docs in `docs/`. Counts are Balanced renderings (one per
record) unless they say otherwise; L / B / R are Literal (직역), Balanced
(균형) and Readable (쉬운 말).

## 1. Settle these first

### Names of God and setting spans

- [ ] **YHWH is `{{divine_name:주|야훼}}` at every level**, with the particle
  outside the span (`{{divine_name:주|야훼}}께서`, `...의`, `...를`, `...여`).
  여호와 is never used; a bare 주 never stands for YHWH. Alternatives: 여호와
  (the older Protestant form), 야훼 as the default. About 5,500 Balanced
  renderings, in every Old Testament book except Esther and Ecclesiastes.
  Style 7a; Genesis "The names of God"; Isaiah–Ezra Korean "The divine name".
- [ ] **Adonai is 주님; "Lord GOD" (*Adonai YHWH*) is
  `주 {{divine_name:하나님|야훼}}`.** Particles that change form (이/가, 은/는,
  을/를, 이여/여) may not follow that span: vocatives are bare ("아, 주
  {{divine_name:하나님|야훼}}!"), and only 께서, 께, 의, 도, 만, 에게, 인, 이다 are
  allowed after it. About 280 renderings, some 200 of them in Ezekiel.
  Alternatives: 주 하나님 with no span; 주 야훼. Lamentations–Twelve "All five
  languages" and Korean section 0.
- [ ] **Honorifics instead of deity_pronoun spans.** Korean text has no
  deity_pronoun spans; respect for God and Jesus is carried by -시-, 께서 and
  그분 (about 2,300 uses of 그분 at B). The figures the English leaves without
  a span get no -시-: the servant of Isaiah, the child of Isaiah 9:5, the
  Branch, "one like a son of man" (Daniel 7:13), the king of Zechariah 9:9,
  "my messenger" (Malachi 3:1). Style 7; Isaiah–Ezra Korean "No -시- for
  these figures"; Lamentations–Twelve Korean 4.
- [ ] **God never takes -시- in his own mouth**: 나 {{divine_name:주|야훼}}가
  말하였다, {{divine_name:주|야훼}}가 말한다, 이스라엘의 거룩한 이. When others
  speak about God they use -시- (이스라엘의 거룩하신 분). Applies to every
  oracle in the Prophets and every speech of God in the narrative. Isaiah–Ezra
  Korean "Speech levels and the name"; see section 3 for exceptions.
- [ ] **`christos` span**: `{{christos:그리스도|메시아}}` and
  `예수 {{christos:그리스도|메시아}}` (about 460 B renderings, all New
  Testament). 메시아 stands plainly, without a span, at John 1:41 and 4:25.
  Style 6 and 7.
- [ ] **`units`: metric by default, the original unit as the alternative,
  Literal keeps the unit**: `{{units:약 450미터|1,000규빗}}` (about 400 B
  renderings). This differs from the English (US units) and needs a rendering
  decision per block. The form is 약 X (not X쯤), and the alternative's number
  is in figures from 100 (founder's ruling 5); section 3 records how the
  Pentateuch and Kings were brought into line. Style 7; Nehemiah–Song Korean
  "Settings recap"; Lamentations–Twelve Korean "Units".
- [ ] **`gender` spans only where Korean has two wordings**:
  `{{gender:형제자매|형제}}` for believers (about 200 B renderings, mostly Acts
  and the letters), `{{gender:자녀들|아들들}}`, `{{gender:사람의 자녀들|사람의
  아들들}}`. 사람, 누구든지 and 자녀 take none. Style 7; Nehemiah–Song Korean
  "Settings recap".
- [ ] **"The LORD of hosts"**: 만군의 {{divine_name:주|야훼}} (L, B);
  하늘의 군대를 거느리신 {{divine_name:주|야훼}} (R), 거느린 in God's own mouth.
  About 275 B renderings, mostly Isaiah, Jeremiah, Haggai–Malachi. Samuel
  table; Isaiah–Ezra Korean "Formulas".
- [ ] **Other names of God**: El Shaddai 전능하신 하나님, Shaddai alone 전능자
  (L, B) / 전능하신 하나님 (R); El Elyon 지극히 높으신 하나님; the Most High
  지극히 높으신 분 / 가장 높으신 하나님 (R); the Holy One of Israel
  이스라엘의 거룩하신 분; Redeemer 구속자 (L, B) / 구해 주시는 분 (R); Yah
  `{{divine_name:주|야}}`. Genesis "The names of God"; Isaiah–Ezra Korean
  "Formulas"; Nehemiah–Song Korean "Job".

### Address forms and speech levels

- [ ] **Narration**: the plain written style (해라체, -었다) with -시- and 께서
  for God and Jesus at every level; others take no honorific. Every narrative
  verse of the Bible. *Settled by the founder* (style "Settled" and 4).
- [ ] **God speaks 해라체 with 나, 너, 너희** to everyone: patriarchs, Moses,
  prophets, Israel, the nations. Thousands of verses (the Pentateuch's laws,
  all oracles). Genesis "Both languages"; Isaiah–Ezra Korean.
- [ ] **People pray in 합쇼체 with 저/제 (communal 저희)**, addressing God as
  주님 and with the vocative {{divine_name:주|야훼}}여. In the Psalms the level
  follows each verse's turn between speaking *to* God (합쇼체, 저) and *about*
  God (plain style with -시-, 나), as Psalm 23. All 2,527 records of Psalms,
  Lamentations 3 and 5, Habakkuk 3, Jonah 2, the prayers of Nehemiah, Ezra 9
  and Daniel 9. Style 7a; Psalms "Settled while drafting" (Korean). 79 of the
  170 uncertain Psalms decisions are about this.
- [ ] **Jesus speaks 해라체; people speak to him in 합쇼체; he prays to the
  Father in 합쇼체.** Open opponents may drop honorifics (-느냐) with a
  decision. Every Gospel. *Settled by the founder*; single scenes (the trial,
  Jesus and his mother at John 2:4, where he speaks 해요체 with 저) may still
  be adjusted with a decision. Style 4.
- [ ] **The letters are in 합쇼체 with 여러분** for the readers (Romans to
  Jude, about 2,300 B renderings), and a single named reader (Timothy, Titus,
  Philemon, Gaius) is 당신 in 합쇼체. Alternatives: 해라체 or 하오체 with 그대
  for Paul to Timothy and Titus; 형제자매 여러분 for direct address. Recorded
  only in the first decision of each letter (for example
  [1CO 1:1](https://openwordbible.org/ko/1co/1/#v1),
  [1TI 1:1](https://openwordbible.org/ko/1ti/1/#v1)); no terms doc covers it.
- [ ] **Moses speaking to Israel** (Deuteronomy and the speeches in Exodus
  and Numbers): 해라체 with 너희 / 너 at L and B, 합쇼체 with 여러분 and 저 at
  R; the singular and plural "you" kept apart at L. Most of Deuteronomy's 959
  records. Nehemiah to the people follows it. Pentateuch "Both languages" and
  "Settled while drafting".
- [ ] **God's laws**: -하라 / -하지 말라 (L, B) and -해야 한다 / -하면 안 된다
  (R); third-person law in the plain style (-한다, -해야 한다). Exodus to
  Deuteronomy. Pentateuch "Both languages". Conflicts with the later rule
  against -하라 (section 3).
- [ ] **King and subjects**: subjects speak 합쇼체 with 임금님 or 내 주 임금님
  and call themselves 임금님의 종 / 이 종 (L, B) or 저 (R); the king speaks
  해라체. Prophets speak to kings in 합쇼체 and God's words inside stay
  해라체. Samuel to Chronicles, Esther, Daniel, the prophets' court scenes
  (임금님 in about 325 B renderings). Samuel "Language by language"; Kings
  "Address forms"; Isaiah–Ezra Korean "People and kings".
- [ ] **하오체 and 하게체 between characters**: 하오체 between equals in
  tension and from a superior who keeps distance (그대, -오, -소); 하게체 for
  an older man to a younger (자네, -게, -네). Job and his friends speak
  하오체 with 그대 at every level; the king speaks 하오체 to Esther; David
  speaks 하오체 to Nathan, Gad and Barzillai (uncertain); Nehemiah to the
  nobles. 그대 appears in about 520 B renderings. Alternative: 합쇼체 / 해요체,
  since 하오체 and 하게체 are dated in modern speech. Joshua–Ruth "Settled
  while drafting" (Korean); Samuel "Settled while drafting"; Nehemiah–Song
  Korean "Speech levels". 69 uncertain decisions (section 2).
- [ ] **Husband and wife**: 해요체 with 당신 both ways at B and R; Literal may
  keep the plain style. Sarah's "my lord" (Genesis 18:12) is 내 주인. Genesis
  "Address between people"; the lovers of the Song use 그대 (L, B) and 당신
  in 해요체 (R) (Nehemiah–Song Korean).
- [ ] **Older and younger brothers and sisters**: Korean must say which is
  older. The older speaks 해라체, the younger 해요체; Moses calls Aaron 형님 in
  해요체 at B and R. Many relations are a guess (Joab older than Abishai,
  Amnon than Absalom; Tamar calls Amnon 오라버니). Genesis "Address between
  people"; Pentateuch and Samuel "Settled while drafting"; Kings "Before
  review".
- [ ] **Strangers and hosts speak 합쇼체 with 당신**; parent to child 해라체,
  child to parent 합쇼체 or 해요체; master 해라체, servant 합쇼체 with 주인님 and
  저. 당신 appears in about 475 B renderings and can sound confrontational in
  modern Korean. Genesis "Address between people".

### Key theological terms

- [ ] ***ḥesed***: 한결같은 사랑 (L, B) / 변함없는 사랑 (R), as the published
  Psalm 23:6 (about 400 renderings, 126 of them Balanced Psalms). Between
  people the drafts use 친절, 은혜 (Genesis), 인애, 친절 (Joshua–Ruth), 신의,
  의리 (Judges); Samuel–Chronicles used 인애 at B and R, now aligned
  (section 3). Alternatives: 인애, 인자, 자비. Psalms "Recurring terms";
  Genesis; Samuel table; Lamentations–Twelve Korean.
- [ ] ***torah***: 율법 for the law of Moses and the book (율법책); 가르침 for
  God's *torah* in Psalms, Proverbs, Isaiah and Jeremiah 31:33 (with a
  decision that Hebrews 8:10 has 율법). 율법 in about 340 B renderings, 가르침
  in about 150. Pentateuch table; Psalms "Settled while drafting";
  Isaiah–Ezra Korean "Jeremiah".
- [ ] **Righteousness and justice**: *tsedeq*, *tsedaqah* 의 (L, B), 옳은 일 /
  바른 일 (R); *mishpat* 정의; "justice and righteousness" 정의와 의 (L, B), 옳고
  바른 일 or 정의와 옳은 일 (R); the righteous 의인 (L, B) / 바르게 사는 사람 (R);
  the wicked 악인 (L, B) / 악한 사람 (R). Psalms; Isaiah–Ezra Korean "Isaiah";
  Lamentations–Twelve Korean "The Twelve".
- [ ] **Spirit**: 성령 in the New Testament; 영 with -시- for God's Spirit in
  the Old Testament (하나님의 영께서, 내 영을 부어 주겠다), 영 for a human spirit.
  Paul's ambiguous *pneuma* is split by level in many places (영 at L, 성령 at B
  or R). Style 6; Lamentations–Twelve Korean "pour out my Spirit". 22
  uncertain decisions.
- [ ] **Covenant 언약 at every level**, Readable included (about 290 B
  renderings); 새 언약 at Jeremiah 31:31. Genesis; Pentateuch; Isaiah–Ezra.
- [ ] **Worship words of the Pentateuch**: 회막, 성막, 성소, 지성소, 속죄소,
  그룹들, 증거판; 번제, 곡식 제물, 속죄제, 속건제, 화목제, 불로 바치는 제물 (화제
  in a decision), 흔들어 바치는 제물; 속죄하다 (L, B); 정결하다 / 부정하다;
  악성 피부병 for *tsaraʿat* (나병 in a decision). Exodus to Numbers and
  Ezekiel 40–48. Pentateuch "Recurring terms".
- [ ] **Servant and slave**: 종 at every level for *ʿeved* and *doulos*, God's
  servants included; 노예 only for slavery itself (Egypt, people bought and
  sold). "Your servant" to a superior is 이 종 / 당신의 종 (L, B), 저 (R).
  About 1,150 B renderings contain 종. Style 6; Genesis; Joshua–Ruth and
  Psalms "Settled while drafting".
- [ ] **Sheol and the dead**: 스올 (L, B) / 죽은 사람들이 있는 곳 (R); the
  shades 망령들 / 죽은 자들 / 죽은 사람들; Abaddon 아바돈 (L) / 멸망의 자리;
  Hades 하데스 (L). Psalms; Isaiah–Ezra Korean "Isaiah"; Nehemiah–Song Korean
  "Job".
- [ ] **The modern word over the older church word**: 예언자 (not 선지자,
  about 450 B renderings), 표적 (not 기적), 올리브 산, 빵 (never 떡), 변호자
  for the Advocate (footnote 보혜사), 하나뿐인 / 유일한 (not 독생자), 영원한
  생명 (not 영생). The founder left these open for a native reviewer. Style
  "Settled" and 6.
- [ ] **Son of Man**: 인자 as Jesus's title in the Gospels (about 250
  renderings); 사람의 아들아 for God's address to Ezekiel (94 records, every
  level, never 인자야); 인자 같은 분 at Daniel 7:13, as Revelation 1:13. Style
  6; Lamentations–Twelve Korean "The prophetic frame" and "Daniel".
- [ ] **Return (*shuv*)**: 돌아오다 at every level for coming back to God and
  from exile, not 회개하다 (kept for the Greek); faithless Israel 돌아선
  이스라엘 (L) / 믿음을 저버린 이스라엘 (B, R). Restore the fortunes 운명을
  돌이키다 / 형편을 회복시키다 / 다시 잘되게 해 주다. Isaiah–Ezra Korean
  "Jeremiah" and "Settled while drafting".
- [ ] ***ḥerem***: 진멸하다, 진멸할 물건 (R 완전히 멸하다). Deuteronomy,
  Joshua, 1 Samuel 15. Pentateuch and Joshua–Ruth tables.
- [ ] **Faith in Christ**: *pistis Christou* is 예수 {{christos:그리스도|메시아}}를
  믿는 믿음 at every level (Romans 3:22, Galatians 2:16, 3:22, Philippians
  3:9); the alternative reading (Christ's own faithfulness) is not given in
  the text. Five uncertain decisions; no terms doc.

### Recurring formulas

- [ ] **"Thus says the LORD"**: L {{divine_name:주|야훼}}께서 이와 같이
  말씀하신다; B ...께서 이렇게 말씀하신다; R ...께서 하시는 말씀이다; ending in a
  period. It keeps the honorific even in God's own mouth (about 190 per
  level). Isaiah–Ezra Korean "Formulas" and "Settled while drafting".
- [ ] **"Declares the LORD"** (*neʾum YHWH*): L {{divine_name:주|야훼}}의
  선언이다; B, R {{divine_name:주|야훼}}가 말한다, as its own sentence (about 250
  L, 325 B and R). "Declares the Lord GOD": L 주
  {{divine_name:하나님|야훼}}의 선언이다; B, R ...의 말이다 (87 B; uncertain).
  Isaiah–Ezra; Lamentations–Twelve Korean 1.
- [ ] **The word-event and recognition formulas**: "the word of the LORD came
  to me": ...의 말씀이 나에게 임하여 말씀하셨다 (L), ...임했다 (B),
  ...께서 나에게 이 말씀을 주셨다 (R). "You will know that I am the LORD":
  내가 {{divine_name:주|야훼}}인 줄 알게 될 것이다 (about 60 B, mostly
  Ezekiel). "As I live": 내가 살아 있음을 두고 맹세한다. Kings "The regnal
  formulas"; Lamentations–Twelve Korean 1.
- [ ] **Woe (*hoy*) and oracle (*massa*)**: ~에게 화가 있다 (L, B), ~에게 끔찍한
  일이 닥칠 것이다 (R); funeral cry 아, / 슬프다; *massa* 신탁 (L, B), ~에 관한
  말씀 (R), 짐 in Jeremiah 23:33–40. Isaiah–Ezra Korean "Formulas".
- [ ] **The regnal formulas** of Kings and Chronicles, one wording per level:
  accession (유다 왕 X가 다스린 지 N년째 되는 해에 ... 왕이 되어 N년 동안
  다스렸다), the mother's name, the verdict (주의 눈에 / 주 보시기에 / 주께서
  악하다고 하신 일을 했다), the sources (...왕 실록, never 역대기), death (조상들과
  함께 누웠고 / 잠들었고 / 죽었고). Kings "The regnal formulas".
- [ ] **Oaths**: "As the LORD lives" 주께서 살아 계심을 두고 맹세하는데; "May
  God do so to me" 하나님께서 내게 벌을 내리시고 더 내리셔도 좋다. Samuel
  table.
- [ ] **"Truly, truly"**: 진실로 진실로 너희에게 말한다 (L, B); 내가 분명히
  말한다 (R), in John. Style 6.
- [ ] **"The sons of Israel"**: 이스라엘 자손 (L), 이스라엘 백성 (B), 이스라엘
  사람들 (R); "the house of Israel" 이스라엘 집. Pentateuch table;
  Lamentations–Twelve Korean 1.
- [ ] **Psalm titles and musical terms**: verse 1; 지휘자를 위하여 / 음악 지휘자를
  위하여 / 찬양 인도자를 위해; 다윗의 시 (L, B), 다윗이 지은 노래 (R); terms of
  unknown meaning kept as names (마스길, 믹담, 식가욘, 깃딧, 스미닛) at L and B and
  explained or simplified at R; 셀라 kept at the end of its verse at every
  level (about 100 renderings). Psalms "Psalm titles and musical terms". 26
  uncertain decisions.

### Names and spelling

- [ ] **Protestant name forms** (*settled by the founder*), with modern place
  names where they compete: 이집트 (not 애굽), 앗시리아 (never 앗수르 for the
  empire), 페르시아 (never 바사), 바빌론 (바벨 in Genesis 11), 바로 for
  Pharaoh, 홍해 (L 갈대 바다 where the English Literal says "Sea of Reeds"),
  염해 / 사해. Style 5; Genesis, Pentateuch and the five-language "Names"
  tables.
- [ ] **One king, two spellings**: each verse keeps its own Hebrew form (Hiram
  and Huram, Abijah and Abijam, Jehoram and Joram, 느부갓네살 and 느부갓레살,
  Jonadab and Jehonadab, Ornan and Araunah). Kings "Names"; Isaiah–Ezra
  "Settled while drafting".
- [ ] **Doubtful published forms kept**: 아모스 for Amoz (the same as the
  prophet Amos), 수산 for Susa, Shephatiah and Zebadiah both 스바댜, 그발 for
  both the river Kebar and Gebal, 아비갈 kept apart from 아비가일, month names
  with a space (아달 월) against 1 Kings' 시브월. Isaiah–Ezra Korean "Names" and
  "Before review"; Nehemiah–Song "Before review"; Samuel "Settled while
  drafting"; Lamentations–Twelve Korean 2.
- [ ] **Explained names**: Literal keeps the name with the Hebrew meaning in
  brackets where the English does; B and R say what the name sounds like
  (Eve, Cain, Isaac, Jacob, the twelve sons, Peniel). Genesis "Names".

### Style

- [ ] **Narrative past in 했다, not 하였다** (Kings, Isaiah–Ezra), now at
  Balanced and Readable in every book; Literal keeps 하였다 where it has it
  (section 3). Kings "All five
  languages".
- [ ] **Imperatives and archaic endings**: modern 해라체 imperatives (들어라,
  보아라, 하여라, 하지 마라); never 개역's -니라, -노니, -지어다, -리라, or -하라
  in proclamations. Style 1; Lamentations–Twelve Korean 4. The Pentateuch's
  -하라 rule conflicts (section 3).
- [ ] **Numbers**: years, ages and large numbers in figures (70년, 2,172명);
  months and days in words (열째 달 십일); under 100 in words in running text
  (사십 일). Kings, Isaiah–Ezra and Lamentations–Twelve Korean; Joshua–Ruth
  said the opposite ("Korean spells numbers out in Hangul"); see section 3.
- [ ] **Quotation marks** “ ” and ‘ ’, stored straight; oracles and the
  speeches of Job, Qoheleth and the Song take none; "Thus says the LORD" ends
  in a period, not a colon. Style 5; Isaiah–Ezra "All five languages".
- [ ] **Literal brackets**: words Korean needs but the source lacks go in [ ]
  at Literal only; particles, endings and -시- are not bracketed. About 8,200
  Literal renderings have brackets. Style 3.
- [ ] **Readable**: short sentences, native words over Sino-Korean (자비 for
  긍휼, 분노 for 진노), idioms explained where the English R explains them, but
  images the English keeps are kept (사람의 아들아, 의의 해, 다림줄, 셀라). Style
  3; Lamentations–Twelve Korean 4.
- [ ] **Hangul only**: no Chinese characters, Latin letters or Hebrew; MENE,
  MENE, TEKEL is 메네, 메네, 데겔, 그리고 바르신; acrostic letters stay in the
  English decision text. Style 5; Lamentations–Twelve Korean.

## 2. Recurring uncertain choices

Clusters from `docs/review-notes/ko-uncertain.md`, grouped by script (keyword
matches on each decision's choice and reason). Counts are approximate; a
decision can sit in two clusters.

- [ ] **Psalms: the level follows the turns to and about God** (79
  decisions). [PSA 23:4](https://openwordbible.org/ko/psa/23/#v4),
  [PSA 27:1](https://openwordbible.org/ko/psa/27/#v1),
  [PSA 104:1](https://openwordbible.org/ko/psa/104/#v1).
- [ ] **-시- given or withheld for a figure other than God speaking** (about
  85): the coming one, the servant, angels, the Spirit, gods of the nations,
  enemies speaking of God. [GEN 49:10](https://openwordbible.org/ko/gen/49/#v10),
  [ISA 9:5](https://openwordbible.org/ko/isa/9/#v5),
  [DAN 7:13](https://openwordbible.org/ko/dan/7/#v13).
- [ ] **하오체 and 하게체 between characters** (69; 그대, 자네, -소).
  [JDG 17:9](https://openwordbible.org/ko/jdg/17/#v9),
  [1KI 2:13](https://openwordbible.org/ko/1ki/2/#v13),
  [2CH 10:6](https://openwordbible.org/ko/2ch/10/#v6).
- [ ] **당신 as the address word** (50), from kings to guests, between
  strangers, and from spirits to Jesus.
  [GEN 47:8](https://openwordbible.org/ko/gen/47/#v8),
  [JOS 14:6](https://openwordbible.org/ko/jos/14/#v6),
  [MRK 1:23](https://openwordbible.org/ko/mrk/1/#v23).
- [ ] **Plants, woods, stones, animals and instruments** (38), including
  잣나무 for *berosh* five times and 백단목 for almug.
  [GEN 30:14](https://openwordbible.org/ko/gen/30/#v14),
  [EXO 39:6](https://openwordbible.org/ko/exo/39/#v6),
  [1KI 5:22](https://openwordbible.org/ko/1ki/5/#v22).
- [ ] **Psalm titles and musical terms kept as names** (26).
  [PSA 6:1](https://openwordbible.org/ko/psa/6/#v1),
  [PSA 56:1](https://openwordbible.org/ko/psa/56/#v1),
  [PSA 88:1](https://openwordbible.org/ko/psa/88/#v1).
- [ ] **영 or 성령 for *ruach* and *pneuma*** (22).
  [ROM 8:10](https://openwordbible.org/ko/rom/8/#v10),
  [1CO 14:2](https://openwordbible.org/ko/1co/14/#v2),
  [2TI 1:7](https://openwordbible.org/ko/2ti/1/#v7).
- [ ] **Ezekiel and Daniel formulas**: 사람의 아들아, 군주 (L, B) / 통치자 (R) for
  *nasi'*, 주 {{divine_name:하나님|야훼}}의 말이다 (21).
  [EZK 2:1](https://openwordbible.org/ko/ezk/2/#v1),
  [EZK 7:27](https://openwordbible.org/ko/ezk/7/#v27),
  [DAN 10:13](https://openwordbible.org/ko/dan/10/#v13).
- [ ] **Word order across verse boundaries** (19): Korean's verb-final order
  pushes a clause into the next verse.
  [NUM 10:29](https://openwordbible.org/ko/num/10/#v29),
  [ISA 10:10](https://openwordbible.org/ko/isa/10/#v10).
- [ ] **The whole letter in 합쇼체, 여러분 or 당신 for the readers** (17, one
  per letter). [1CO 1:1](https://openwordbible.org/ko/1co/1/#v1),
  [1TI 1:1](https://openwordbible.org/ko/1ti/1/#v1),
  [3JN 1:1](https://openwordbible.org/ko/3jn/1/#v1).
- [ ] **People speaking to Jesus without honorifics** (about 15): the
  hostile crowds of John 7–9, Pilate, the devil, unclean spirits (합쇼체 with
  당신 but no -시-). [JHN 8:48](https://openwordbible.org/ko/jhn/8/#v48),
  [MRK 5:6](https://openwordbible.org/ko/mrk/5/#v6),
  [LUK 4:3](https://openwordbible.org/ko/luk/4/#v3).
- [ ] **Wordplay and explained names** (14).
  [GEN 5:29](https://openwordbible.org/ko/gen/5/#v29),
  [GEN 27:36](https://openwordbible.org/ko/gen/27/#v36).
- [ ] **Older or younger: kin words chosen by guess** (13, plus Moses' 형님
  to Aaron). [GEN 10:25](https://openwordbible.org/ko/gen/10/#v25),
  [EXO 16:9](https://openwordbible.org/ko/exo/16/#v9),
  [1KI 11:19](https://openwordbible.org/ko/1ki/11/#v19).
- [ ] **"My lord"**: 내 주, 나리, 주인, 지도자님, and 내 주여 for an angel (13).
  [GEN 32:5](https://openwordbible.org/ko/gen/32/#v5),
  [NUM 32:25](https://openwordbible.org/ko/num/32/#v25),
  [ZEC 1:9](https://openwordbible.org/ko/zec/1/#v9).
- [ ] **Gender spans or none** (13).
  [GEN 9:5](https://openwordbible.org/ko/gen/9/#v5),
  [2CH 19:10](https://openwordbible.org/ko/2ch/19/#v10),
  [PSA 133:1](https://openwordbible.org/ko/psa/133/#v1).
- [ ] **God naming himself in the third person, with or without -시-** (12;
  see section 3). [JOS 24:7](https://openwordbible.org/ko/jos/24/#v7),
  [2SA 7:11](https://openwordbible.org/ko/2sa/7/#v11),
  [EZK 13:6](https://openwordbible.org/ko/ezk/13/#v6).
- [ ] **예언자 / 그 예언자** (11, seven in John).
  [JHN 6:14](https://openwordbible.org/ko/jhn/6/#v14),
  [2KI 19:2](https://openwordbible.org/ko/2ki/19/#v2).
- [ ] **Units** (7), including a span in X쯤.
  [JDG 3:16](https://openwordbible.org/ko/jdg/3/#v16),
  [GEN 20:16](https://openwordbible.org/ko/gen/20/#v16),
  [MAT 25:14](https://openwordbible.org/ko/mat/25/#v14).
- [ ] **복종하다 / 순종하다 for submitting and obeying** (6).
  [EPH 5:18](https://openwordbible.org/ko/eph/5/#v18),
  [COL 3:18](https://openwordbible.org/ko/col/3/#v18),
  [1TI 2:11](https://openwordbible.org/ko/1ti/2/#v11).
- [ ] ***Ḥesed* between people and in Kings** (5).
  [JDG 1:24](https://openwordbible.org/ko/jdg/1/#v24),
  [1KI 3:6](https://openwordbible.org/ko/1ki/3/#v6),
  [PSA 136:1](https://openwordbible.org/ko/psa/136/#v1).
- [ ] ***Pistis Christou*: 그리스도를 믿는 믿음** (5).
  [ROM 3:21](https://openwordbible.org/ko/rom/3/#v21),
  [GAL 2:15](https://openwordbible.org/ko/gal/2/#v15),
  [PHP 3:8](https://openwordbible.org/ko/php/3/#v8).

## 3. Known inconsistencies to resolve

Each was checked in `content/` (Korean renderings as of this list).

- [x] ***Ḥesed* at B and R in Samuel–Chronicles is 인애**, where every other
  book has 한결같은 사랑 (B) and 변함없는 사랑 (R). About 23 records:
  [1SA 20:8](https://openwordbible.org/ko/1sa/20/#v8),
  [2SA 9:1](https://openwordbible.org/ko/2sa/9/#v1),
  [1KI 3:6](https://openwordbible.org/ko/1ki/3/#v6),
  [1KI 8:23](https://openwordbible.org/ko/1ki/8/#v23),
  [2CH 6:42](https://openwordbible.org/ko/2ch/6/#v42). The Samuel table sets
  인애 for B and R, the Psalms and Genesis notes set 한결같은 / 변함없는 사랑, and
  [2SA 22:51](https://openwordbible.org/ko/2sa/22/#v51) already follows Psalm
  18:51, against the Samuel table. Genesis and Joshua–Ruth also differ for
  *ḥesed* between people (친절, 은혜 against 인애, 친절).
  Fixed: 24 Samuel–Chronicles records now say 한결같은 사랑 (B) and 변함없는 사랑
  (R), also between people as the Samuel table intends (2 Chronicles 24:22 L
  too); the Samuel table follows the Psalms and Genesis notes. Left for review:
  the word for *ḥesed* between people in Genesis and Joshua–Ruth.
- [x] **Measures: X쯤 against 약 X.** The Nehemiah–Song and
  Lamentations–Twelve notes say "always 약, never X쯤", but about 225 records
  use X쯤 inside the units span: nearly all of Exodus, Leviticus, Numbers,
  Judges, 1 Kings and 1 Chronicles, and part of 1 Samuel, 2 Kings and
  2 Chronicles ([EXO 25:10](https://openwordbible.org/ko/exo/25/#v10),
  [NUM 35:4](https://openwordbible.org/ko/num/35/#v4),
  [1KI 6:2](https://openwordbible.org/ko/1ki/6/#v2); against
  [1SA 1:24](https://openwordbible.org/ko/1sa/1/#v24) and Ezekiel). The Samuel
  and Kings notes recorded the split without settling it.
  Fixed: every metric `units` span now reads 약 X (680 spans in 227 records),
  as the later notes set; the Samuel and Kings notes say so. John 12:5's
  wage span (일 년 품삯쯤) is not a measure and was left.
- [x] **Units: the alternative's number in words above 100**, against the
  founder's ruling 5 (figures from 100): 백삼십 세겔, 백 규빗, 천 규빗
  ([NUM 7:13](https://openwordbible.org/ko/num/7/#v13),
  [EXO 27:18](https://openwordbible.org/ko/exo/27/#v18),
  [NUM 35:4](https://openwordbible.org/ko/num/35/#v4)).
  Fixed: 72 records; every alternative from 100 is in figures (130세겔,
  1,000규빗, 300데나리온), Old and New Testament. Literal running text keeps
  its words.
- [x] **Regnal numbers in words in 2 Kings, in figures in 2 Chronicles.**
  [2KI 18:2](https://openwordbible.org/ko/2ki/18/#v2) "이십오 세 ... 이십구 년"
  against [2CH 29:1](https://openwordbible.org/ko/2ch/29/#v1) "25세 ... 29년";
  [2KI 22:1](https://openwordbible.org/ko/2ki/22/#v1) against
  [2CH 34:1](https://openwordbible.org/ko/2ch/34/#v1); also 1 Kings 2:11 and
  11:42 against [1KI 22:42](https://openwordbible.org/ko/1ki/22/#v42). The
  Kings note says figures; the Joshua–Ruth note says Korean spells numbers in
  Hangul.
  Fixed: 2 Kings (and the few 1 Kings and 2 Chronicles cases) now write
  regnal years, ages and years in figures at every level, Readable included
  (25세, not 스물다섯 살), as the Kings note and the parallels in 2 Chronicles,
  Isaiah 36–39 and Jeremiah 52; about 60 records. Samuel keeps its own words.
- [x] **Narrative 하였다 against 했다.** The Kings note asks for 했다, and
  Samuel, Kings, Chronicles, Isaiah, Jeremiah, Daniel and Nehemiah use it
  throughout; at Balanced, 하였다 is about 60% of these endings in Exodus,
  Numbers and Deuteronomy, 45% in Genesis, 35% in Judges and Esther and
  100% in Revelation. Compare the verdict formula in
  [JDG 2:11](https://openwordbible.org/ko/jdg/2/#v11) (주께서 보시기에 악한 일을
  하였고) with [1KI 15:26](https://openwordbible.org/ko/1ki/15/#v26) (주 보시기에
  악한 일을 했다); the Joshua–Ruth and Kings tables give different wordings.
  Fixed: 하였- is 했- at Balanced and Readable in every book (1,446 records);
  Literal keeps 하였다 where it has it (the Ezekiel formula 말하였다 (L) /
  말했다 (B, R) is deliberate). The Judges verdict now uses the Kings formula
  at each level (8 records), and the Joshua–Ruth note says so.
- [ ] **Imperatives -하라 / -하지 말라 against -하여라 / -하지 마라.** The
  Pentateuch note prescribes -하라 for God's commands at L and B, and about
  350 Balanced commands in Exodus, Leviticus, Numbers and Deuteronomy use it
  ([EXO 20:8](https://openwordbible.org/ko/exo/20/#v8),
  [EXO 20:13](https://openwordbible.org/ko/exo/20/#v13)); the
  Lamentations–Twelve note forbids -하라 in proclamations, and Joshua to
  Revelation use -하여라 / -해라 ([ISA 1:17](https://openwordbible.org/ko/isa/1/#v17)).
  Left for review: the Pentateuch note chose -하라 deliberately for the law
  codes, and the later rule is about prophetic proclamations; which register
  suits law is a native reviewer's call, and changing it means recasting
  about 350 commands per level.
- [x] **"Thus says the LORD" without the honorific beyond the allowed
  exception.** The Isaiah–Ezra note keeps the formula honorific "except
  Isaiah 38:5 = 2 Kings 20:5", but L and B also drop it at
  [2KI 21:12](https://openwordbible.org/ko/2ki/21/#v12),
  [2KI 22:16](https://openwordbible.org/ko/2ki/22/#v16),
  [2KI 22:18](https://openwordbible.org/ko/2ki/22/#v18),
  [2CH 34:24](https://openwordbible.org/ko/2ch/34/#v24) and
  [2CH 34:26](https://openwordbible.org/ko/2ch/34/#v26).
  Fixed: the five records now say 께서 이와 같이 말씀하신다 / 이렇게 말씀하신다 /
  하시는 말씀이다 at L, B and R, with their decisions.
- [x] **God speaking of himself with -시-**, against "God never takes -시- in
  his own mouth": [JOS 24:7](https://openwordbible.org/ko/jos/24/#v7),
  [PSA 81:16](https://openwordbible.org/ko/psa/81/#v16),
  [EZK 13:6](https://openwordbible.org/ko/ezk/13/#v6); compare
  [2SA 7:11](https://openwordbible.org/ko/2sa/7/#v11) and
  [ZEC 3:2](https://openwordbible.org/ko/zec/3/#v2), without.
  Fixed: Joshua 24:7, Psalm 81:16 and Ezekiel 13:6 drop -시- and 께 at every
  level, with their decisions. 2 Samuel 7:11 Literal keeps the narrator's
  honorific by its own decision; left for review.
- [ ] **표적 and 표징 for the same Hebrew *ʾot* (sign).** 표적 in Exodus,
  Numbers and Deuteronomy ([EXO 3:12](https://openwordbible.org/ko/exo/3/#v12),
  [EXO 4:8](https://openwordbible.org/ko/exo/4/#v8),
  [DEU 4:34](https://openwordbible.org/ko/deu/4/#v34)); mostly 표징 in Samuel,
  Kings, Isaiah and Ezekiel, and both in Joshua ([JOS 4:6](https://openwordbible.org/ko/jos/4/#v6),
  [ISA 7:14](https://openwordbible.org/ko/isa/7/#v14),
  [EZK 4:3](https://openwordbible.org/ko/ezk/4/#v3)). No terms doc covers the
  Old Testament word.
  Left for review: 표징 is used mostly for symbolic acts and tokens (Isaiah,
  Ezekiel), 표적 for wonders; whether Korean keeps that sense split, and
  which church word wins, is open (style "Settled" leaves 표적 to a reviewer).
- [x] **Concubine: 첩 and 후궁.** The Joshua–Ruth table has 첩; the Samuel note
  says "Concubines are 후궁". Rizpah is 첩 at
  [2SA 3:7](https://openwordbible.org/ko/2sa/3/#v7) and 후궁 at
  [2SA 21:11](https://openwordbible.org/ko/2sa/21/#v11); David's concubines are
  첩 at [2SA 5:13](https://openwordbible.org/ko/2sa/5/#v13) and 후궁 from
  [2SA 15:16](https://openwordbible.org/ko/2sa/15/#v16).
  Fixed: a king's concubines are 후궁 and other men's 첩, as the drafts already
  do in Kings, Chronicles, Esther, Song and Daniel; 2 Samuel 3:7, 5:13 and
  1 Chronicles 3:9 now say 후궁 (3 records); the Samuel note says so.
- [ ] **Third-person verses inside a psalm prayer.** Some keep 합쇼체
  ([PSA 48:9](https://openwordbible.org/ko/psa/48/#v9),
  [PSA 102:17](https://openwordbible.org/ko/psa/102/#v17),
  [PSA 145:3](https://openwordbible.org/ko/psa/145/#v3)); others switch to the
  plain style ([PSA 123:2](https://openwordbible.org/ko/psa/123/#v2),
  [PSA 85:9](https://openwordbible.org/ko/psa/85/#v9)). Settle one rule.
  Left for review: the Psalms note follows the turns, but Psalms 48, 102 and
  145 carry decisions for keeping one level through a continuous prayer;
  changing them recasts whole stretches of verses.
- [x] **Psalm titles at Readable vary**: *maskil* is 가르치는 노래
  ([PSA 32:1](https://openwordbible.org/ko/psa/32/#v1)), 가르치고 깨닫게 하는 노래
  ([PSA 42:1](https://openwordbible.org/ko/psa/42/#v1)), 가르침과 깨달음을 주는
  노래 ([PSA 52:1](https://openwordbible.org/ko/psa/52/#v1)), 가르침과 깨달음을
  주려는 노래 ([PSA 74:1](https://openwordbible.org/ko/psa/74/#v1)) and 가르치려고
  지은 노래 ([PSA 142:1](https://openwordbible.org/ko/psa/142/#v1)); "Lilies" is
  ‘백합’ at [PSA 45:1](https://openwordbible.org/ko/psa/45/#v1) and "백합화" at
  [PSA 69:1](https://openwordbible.org/ko/psa/69/#v1) and
  [PSA 80:1](https://openwordbible.org/ko/psa/80/#v1).
  Fixed: *maskil* at Readable is 가르침과 깨달음을 주는 노래 in all 13 titles
  (8 records changed); Psalms 69 and 80 now say ‘백합’ / ‘언약의 백합’이라는
  곡조에 맞추어, as 45 and 60.
- [ ] **Husband and wife outside the Genesis rule** (해요체 with 당신 both
  ways): Samson answers his wife in 하오체
  ([JDG 14:16](https://openwordbible.org/ko/jdg/14/#v16)), the Shunammite's
  husband speaks 하오체 ([2KI 4:23](https://openwordbible.org/ko/2ki/4/#v23)),
  the king speaks 하오체 to Esther (Nehemiah–Song note), Hosea 해요체
  ([HOS 3:3](https://openwordbible.org/ko/hos/3/#v3)). Each has a decision;
  decide whether these exceptions stand.
  Left for review: each exception has its own decision; whether it stands is
  a native reviewer's judgment about the scene.

## 4. Passages to read closely

The terms docs name these as pulling hardest toward familiar Korean wording.
개역한글 (public domain, but archaic) shapes how most readers remember them,
and 개역개정, 새번역, 공동번역, 쉬운성경, 우리말성경 and 현대인의성경 are under
copyright. Check that each draft is original: no sentence should match a
well-known version for more than a short common phrase, and no 개역 ending
(-니라, -노니, -지어다) should have crept in.

- [ ] Genesis 1–3, 12, 22, 50
  ([GEN 1:1](https://openwordbible.org/ko/gen/1/#v1),
  [GEN 22:1](https://openwordbible.org/ko/gen/22/#v1)).
- [ ] Exodus 3, 12, 14–15, 20; Leviticus 19; Numbers 6:24–26; Deuteronomy 6,
  30 ([EXO 20:1](https://openwordbible.org/ko/exo/20/#v1),
  [NUM 6:24](https://openwordbible.org/ko/num/6/#v24),
  [DEU 6:4](https://openwordbible.org/ko/deu/6/#v4)).
- [ ] Joshua 1 and 24:15; Judges 6–7 and 16; Ruth 1:16–17
  ([RUT 1:16](https://openwordbible.org/ko/rut/1/#v16)).
- [ ] Hannah's song (1 Samuel 2), David and Goliath (17), David and Jonathan
  (18–20), David and Bathsheba with Nathan's parable (2 Samuel 11–12),
  David's lament over Absalom ([2SA 19:1](https://openwordbible.org/ko/2sa/19/#v1)).
- [ ] Psalms 23, 51, 91, 103; Proverbs 3:5–6 and 31
  ([PSA 23:1](https://openwordbible.org/ko/psa/23/#v1),
  [PRO 3:5](https://openwordbible.org/ko/pro/3/#v5)).
- [ ] Job 1–2, 3, 19:25–27, 28, 38–42; Ecclesiastes 1:2–11, 3:1–8, 12:1–8
  (avoid 범사에 기한이 있고, 헛되다); Song 2:7, 2:10–13, 8:6–7 (avoid 노루와
  들사슴); Esther 4:14 (avoid 이 때를 위함이 아닌지); Nehemiah 1:5–11 and 9
  ([ECC 1:2](https://openwordbible.org/ko/ecc/1/#v2),
  [ECC 3:1](https://openwordbible.org/ko/ecc/3/#v1),
  [EST 4:14](https://openwordbible.org/ko/est/4/#v14)).
- [ ] Isaiah 6, 7:14, 9:5–6 (names not from 개역's 기묘자, 모사, 영존하시는
  아버지, 평강의 왕), 40, 52:13–53:12, 61; Jeremiah 31, with 31:31–34 against
  Hebrews 8 ([ISA 9:5](https://openwordbible.org/ko/isa/9/#v5),
  [ISA 53:1](https://openwordbible.org/ko/isa/53/#v1),
  [JER 31:31](https://openwordbible.org/ko/jer/31/#v31)).
- [ ] Lamentations 3:22–23; Ezekiel 36–37 (not 생기); Daniel 7 and 12; Hosea 6
  and 11; Joel 2–3; Amos 5:24; Jonah 2; Micah 5:1 and 6:8; Habakkuk 2:4 and
  3:17–18; Zechariah 4:6 (not 개역's 되지 아니하며 ... 되느니라) and 9:9;
  Malachi 3 ([LAM 3:22](https://openwordbible.org/ko/lam/3/#v22),
  [EZK 37:1](https://openwordbible.org/ko/ezk/37/#v1),
  [MIC 6:8](https://openwordbible.org/ko/mic/6/#v8)).
- [ ] New Testament: no Korean doc lists passages, but the style guide warns
  that 개역한글 shapes familiar verses, and the English style guide records
  that Philippians 4:6–8 came out almost word for word like existing
  versions in English. Read at least
  [JHN 1:1](https://openwordbible.org/ko/jhn/1/#v1),
  [JHN 3:16](https://openwordbible.org/ko/jhn/3/#v16),
  [1CO 13:4](https://openwordbible.org/ko/1co/13/#v4) and
  [PHP 4:6](https://openwordbible.org/ko/php/4/#v6).
