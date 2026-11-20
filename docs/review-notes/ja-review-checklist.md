# Japanese review checklist

The starting point for native Japanese reviewers. Every book of the Bible is
drafted in Japanese at all three levels (30,637 records), with headings,
chapter summaries, book introductions, footnotes and articles, and every
record is `ai_draft`. Most of the wording follows a few dozen book-wide
choices made by the drafters: the speech styles of each level, the divine-name
span, the honorifics for God and Jesus, the key terms, the name forms. A
reviewer who settles those first settles the wording of thousands of verses at
once, so start with section 1.

How to use it:

- **Work down section 1 first.** Each item decides wording in many verses.
  Tick it when you agree, or write the change you want beside it.
- **Then section 2**, the uncertain decisions that recur. Each cluster is one
  question asked many times; answer it once.
- **Then sections 3 and 4**: places where the drafts disagree with each other,
  and the famous passages to read closely against the Japanese Bibles readers
  know (口語訳, 新共同訳, 聖書協会共同訳, 新改訳2017), for naturalness and to make
  sure the wording is Open Word Bible's own.
- The full list of every Japanese decision the drafters marked uncertain
  (2,021 of them, with links) is `docs/review-notes/ja-uncertain.md`. Tick
  items there as they are settled and regenerate it with
  `python3 scripts/review_checklist.py ja --write`.

A choice is changed by editing `docs/japanese-style.md`, which records it, and
then revising every passage drafted under it. Records stay `ai_draft` until a
named reviewer approves them; nothing is marked reviewed by Claude.

"Style" below is `docs/japanese-style.md`. Counts are Balanced renderings (one
per record) unless they say otherwise; L / B / R are Literal (逐語訳), Balanced
(標準訳) and Readable (平易訳). Counts were taken on 2026-11-20.

## 1. Settle these first

### Names of God and setting spans

- [ ] **The divine name (YHWH)** is `{{divine_name:主|ヤハウェ}}`: 主 by default,
  ヤハウェ as the reader setting, in 6,530 Balanced records. *Adonai YHWH* is
  `{{divine_name:主なる神|主ヤハウェ}}` (311) and *Yah* `{{divine_name:主|ヤハ}}`
  (45). Particles stay outside the span (`{{divine_name:主|ヤハウェ}}は`).
  エホバ is never used. *Adonai* alone is 主 with no span; *Elohim* is 神.
  Check that 主 for YHWH and 主 for *Adonai* / *kyrios* do not leave a reader
  unsure who is meant in passages that use both (Psalm 110:1, quoted in
  Matthew 22:44).
- [ ] **Christ** is `{{christos:キリスト|メシア}}` (552), and plain メシア where
  the Greek itself has *Messias* (John 1:41; 4:25). In the Old Testament the
  anointed king is 油注がれた者 with no span (Psalm 2:2; 84:10).
- [ ] **Brothers** (*adelphoi*, the believers) is
  `{{gender:きょうだいたち|兄弟たち}}` (168), one brother `{{gender:きょうだい|兄弟}}`
  (46): the inclusive kana spelling by default, 兄弟 as the traditional setting.
  Where the English has a gender span Japanese does not need (them / him), the
  drafts write その人, 人々 or nothing, with no span (style 7a).
- [ ] **Measures** are a `units` span with the modern measure first and the
  biblical unit as the setting (`{{units:約2.2メートル|五キュビト}}`); coins
  give the value in wages. Literal keeps the biblical unit.
- [ ] **No `deity_pronoun` span.** Japanese has no capitalised pronouns; the
  respect forms for God's acts do that work. Agree that nothing is lost.

### Speech styles and address

- [ ] **Narrative** is in the plain style (だ・である, past 〜た) at Literal and
  Balanced, and in です・ます at Readable (style 4). Readable's です・ます makes
  its sentences longer in characters than Balanced in 1-2 Samuel, 2 Kings,
  Haggai, Zechariah and Malachi, though its vocabulary is far plainer
  (`docs/review-notes/level-checks.md`). Confirm です・ます is right for the
  Readable level.
- [ ] **Letters** are in です・ます at every level, with commands 〜なさい (L, B)
  and 〜てください (R); Paul asking a favour takes 〜てください at Balanced too
  (1 Thessalonians 5:25, 2 Thessalonians 3:1, Philemon).
- [ ] **Poetry** (Psalms, Job, Proverbs, Song of Songs, Lamentations, the
  prophets' oracles) is in the plain style at every level, Readable too.
- [ ] **Requests to God** take 〜てください / 〜ないでください in every book,
  inside plain-style verse as in prose (Psalm 3:8; Numbers 10:35). Until
  pull request #1076 the prophets, Lamentations, Job and Proverbs 30 used
  〜てほしい instead; that pull request aligns them with the Psalter. Job's
  challenges to God are the most arguable case. Prose prayers (Solomon in 1 Kings 8, Ezra 9,
  Nehemiah, Elisha in 2 Kings 6) are in です・ます.
- [ ] **Honorifics for God and Jesus in narration**: light respect forms only
  (言われた, 来られた, お答えになった; R 言われました), and for nobody else, not
  apostles or angels (style 4). People speak of God's acts with 〜てくださる.
  Jesus prays to the Father plainly and intimately, with 〜てください (Mark
  14:36, John 17).
- [ ] **Pronouns.** God and Jesus say わたし; people say あなた to God, or a
  title (主よ, 先生). 彼 is never used for God. "You" plural is あなたがた (L, B),
  あなたたち (R, 2,230 records) or みなさん (R, 819, mostly in the letters).
- [ ] **おまえ** is used in 619 Balanced records: a father to his son (Genesis
  28:4; 46:30), a king to his men, enemies in a quarrel (2 Samuel 2:22), God or
  a prophet to hostile kings and nations (Ezekiel's oracles against Tyre and
  Egypt, Isaiah 47), and things addressed in poetry (the sea in Job 38:11, the
  soul in Jeremiah 4:19). Check that it is not too rough for a loving father
  and not used where God speaks to his own people.
- [ ] **見よ.** Commands to look are 見なさい (L, B) and 見てください (R) in the
  letters and Gospels; Revelation keeps a solemn 見よ (L, B) for prophetic
  announcements (1:7) and すると見よ (L) when a vision opens (4:1). Confirm
  the exception.
- [ ] **No bungo.** 〜たまえ, 〜べし, 〜なり are not used at any level, and the
  drafts have none. Agree that the prayers and psalms still sound like prayer
  without them.

### Key theological terms

Each of these is one choice through the whole Bible (style 6 and the OT
conventions in the decisions):

- [ ] grace 恵み (key term, every level, 240 B); mercy あわれみ (kana, 152 B).
- [ ] *chesed* (steadfast love) 誠実 (L), 変わらぬいつくしみ (B, R) (165 B), in
  every book; see section 3 for 慈しみ in the letters.
- [ ] righteousness 義 (L, B), with 正しい / 神の前に正しいこと at Readable; justify
  義とされる (L, B), 正しい者と認められる (R).
- [ ] covenant 契約 at every level (290 B).
- [ ] redeem 贖う (L, B), with plainer words at Readable (買い戻す, 救い出す).
- [ ] sin 罪; repent 悔い改める (L, B), 心を入れ替えて神に立ち返る and similar (R).
- [ ] faith 信仰, believe 信じる at every level; trust 信頼する.
- [ ] Holy Spirit 聖霊; spirit 霊; 御霊 is not used.
- [ ] kingdom of God 神の国, kingdom of heaven 天の国; Son of Man 人の子 (a
  title, every level).
- [ ] gospel 福音 (L, B), 良い知らせ (R); baptize 洗礼を授ける, John the Baptist
  洗礼者ヨハネ.
- [ ] the Law 律法; scribes 律法学者; Pharisees ファリサイ派の人々.
- [ ] slave / servant: 奴隷 (L), しもべ (B, R), as the English at each level, and
  奴隷 at every level where slavery itself is the point.
- [ ] Sheol 陰府 (L, B), 死者の世界 (R); Gehenna ゲヘナ (L, B), 地獄 (R); Hades
  陰府.
- [ ] forgive 赦す (L, B), ゆるす (R); heal 癒やす (L, B), いやす (R).
- [ ] angel 天使; demon 悪霊; church 教会; the assembly of Israel 集会 (121 B), with 会衆 in a few places (16).
- [ ] peace: 平和 (between people, and with God), 平安 (a greeting, inner
  peace). Check the split in Paul's greetings and Philippians 4:7.
- [ ] holy ones 聖なる者たち (not 聖徒).
- [ ] the Lord of Armies 万軍の主; the Almighty (*Shaddai*) 全能者.

### Names and spelling

- [ ] **Name forms** follow modern ecumenical Japanese usage, nearer the Greek
  and Hebrew sounds than the older forms: ペトロ, フィリポ, カファルナウム, エフェソ,
  ファリサイ派 (style 5). Old Testament names follow each book's Hebrew
  spelling, so the same person may be spelled two ways where the Hebrew is
  (Jehosheba ヨシェバ in 2 Kings 11:2, Jehoshabeath ヨシャブアト in 2 Chronicles
  22:11). Decide whether a reviewer wants one form per person instead.
- [ ] **Furigana.** The reader's furigana tool shows readings over the kanji of
  Balanced. John's were drafted by hand; the other 65 books' readings were
  drafted by a morphological analyser with the Bible's own readings added (主
  しゅ, 御心 みこころ, 罪人 つみびと, 第一の月の一日 ついたち), in pull request
  #1075. They agree with John's hand readings on 99% of kanji runs; spot-check
  方 (かた / ほう), 何 (なに / なん), 後 (あと / のち), 行 (い / おこな).
- [ ] **Script.** Jōyō kanji with standard okurigana; words modern writing puts
  in kana stay in kana (こと, もの, ください, わたし, あなた). Readable uses only
  Jōyō kanji and writes a harder word in kana.

### Style

- [ ] Quotation marks 「 」, 『 』 inside; the sentence ends with its 。 inside
  the closing bracket (「わたしに従いなさい。」).
- [ ] Kanji numerals in running text (十二人, 三日目); Arabic digits only in a
  `units` measure.
- [ ] Poetry set in lines at every level, following the Hebrew accents.

## 2. Recurring uncertain choices

The drafters marked 2,021 Japanese rendering decisions uncertain: 1,810
word choices, 81 register choices, 64 supplied words, 39 word orders and 22
setting alternatives. 596 are in the Psalms, 158 in Jeremiah, 148 in Ezekiel,
84 in Isaiah and 83 in Genesis. Most follow an uncertain meaning decision
(the Hebrew or Greek is unclear and the footnote says so); for those, check
only that the Japanese leaves the question as open as the English does. The
clusters below are Japanese questions.

- [ ] **Who speaks to whom, and how politely.** The 81 uncertain register
  decisions, and many word choices besides, choose a speech style for a speaker the text does not rank: the serpent and
  the woman (Genesis 3), the man who wrestles with Jacob (Genesis 32:25,
  narrated without respect forms so as not to answer the story's question),
  the women who answer Jeremiah (44:19, です・ます at Readable), the king in
  Psalm 21:9-13 (plain verbs, not those used for God). Settle them scene by
  scene.
- [ ] **Subjects Japanese can leave out.** Many decisions leave a subject
  unnamed where the Hebrew or Greek is ambiguous (Acts 18:18, who shaved his
  head), or let a respect form show that God is the subject (Exodus 24:16,
  34:5). Check that the respect form does not decide more than the original.
- [ ] **Psalm titles and terms.** Selah セラ (every level, its meaning unknown);
  *maskil*, *miktam*, *shir hamma'alot* 上りの歌 (L), 都に上る歌 (B), エルサレムへ
  上る旅の歌 (R); the law words of Psalms 19 and 119 (教え, 証し, 命令, 戒め, 掟, 定め).
- [ ] **Rare plants, animals and objects** (the birds of Isaiah 38:14 and
  Jeremiah 12:9, the perfumes of Psalm 45:9, the parts of Ezekiel's temple):
  the drafts follow the English at each level. A reviewer may know the usual
  Japanese word.
- [ ] **Names that look like other names**: Shion シイオン (Joshua 19:19, so as
  not to read as Zion), Terah テラ for both Abraham's father and the camp of
  Numbers 33:27, Dishan / Dishon (Genesis 36, 1 Chronicles 1).
- [ ] **Rough first person.** Lamech (Genesis 4:23) and a few boasting
  speakers say おれ at Readable (34 R records). Check it fits a Bible for young
  readers.

## 3. Known inconsistencies to resolve

- [ ] **御心 / みこころ.** Style 10 asks for one spelling through a book.
  Fourteen New Testament books (and Ezra) write 御心; Psalms and Hebrews write
  みこころ; Acts has both (2 and 1). Choose one spelling for the whole Bible,
  or one per level.
- [ ] **慈しみ / いつくしみ.** The Old Testament *chesed* is 変わらぬいつくしみ in
  kana everywhere; Romans, Galatians, Ephesians, Titus, James and 1 Peter
  write 慈しみ in kanji for *chrēstotēs* (kindness). Confirm that the two are
  meant to be different words, or align the spelling.
- [ ] **裁き / さばき.** 裁き almost everywhere; Genesis, Numbers, Deuteronomy, Job
  and Proverbs mix in さばき (one to four times each).
- [ ] **癒やす / いやす at Balanced.** Balanced writes 癒やす, but Genesis, Psalms
  and Jeremiah have one いやす each at Balanced.
- [ ] **赦す at Balanced.** Deuteronomy has one ゆるす at Balanced against two 赦す.
- [ ] **Requests to God** (section 1): settled by #1076 once merged; until then
  the prophets differ from the Psalter.
- [ ] **Name spellings within one language** (`python3 scripts/name_spellings.py
  --lang ja`): Hezekiah ヒゼキヤ / ヒズキヤ (Nehemiah 7:21, 10:18; 1 Chronicles
  3:23); Iscariot, where the Greek gives it to Judas or to his father Simon
  (John 6:71, 13:2, 13:26, 14:22; Luke 22:3); Shelomith シェロミト / シェロモト;
  Jether エテル / イエテル (Judges 8:20); Micaiah ミカヤ / ミカ (2 Chronicles
  18:14). Most follow the Hebrew or Greek spelling; check the rest.
- [ ] **Readable sentence length** in 1-2 Samuel, 2 Kings, Haggai, Zechariah and
  Malachi (section 1, speech styles).

## 4. Passages to read closely

Read these at every level, aloud, for natural Japanese, for the right
register, and against the Japanese Bibles readers know so that the wording is
Open Word Bible's own and not a copy:

- [ ] Genesis 1:1-2:3; 3; 22:1-19
- [ ] Exodus 3:13-15 (the divine name explained); 20:1-17; 34:6-7
- [ ] Deuteronomy 6:4-9
- [ ] Ruth 1:16-17
- [ ] Psalms 1; 23; 51; 103; 139
- [ ] Isaiah 6:1-8; 7:14; 9:5-6 (Hebrew numbering); 40:1-11; 52:13-53:12
- [ ] Jeremiah 31:31-34; Lamentations 3:22-33; Micah 6:8
- [ ] Matthew 5:3-12; 6:9-13 (the Lord's Prayer: compare the prayer Japanese
  churches say); 28:18-20
- [ ] Luke 2:1-20; 15:11-32
- [ ] John 1:1-18 (言 ことば for *logos*); 3:16; 11:25-26; 14:6; 17
- [ ] Acts 2:1-41
- [ ] Romans 3:21-26; 5:1-11; 8:28-39
- [ ] 1 Corinthians 13; 15:3-8
- [ ] Galatians 2:20; Ephesians 2:8-10; Philippians 2:5-11
- [ ] Hebrews 11:1; 1 John 4:7-12
- [ ] Revelation 21:1-5
