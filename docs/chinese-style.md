# Chinese style guide

How Open Word Bible drafts Chinese in Simplified characters (简体中文, code
`zh`). It builds on `docs/english-style.md`, which still covers everything
that is not about wording: sources, one record per sentence, the three
levels, decisions and status. It also builds on each book's terms notes
(`docs/john-terms.md` and the others), whose book-wide choices hold in
Chinese unless this file says otherwise. `docs/chinese-terms.md` is the
glossary of recurring terms and names, Genesis to Revelation. Where this
file and the founder's Translation Charter disagree, the Charter wins; fix
this file.

**Status: proposed, awaiting native Chinese reviewers.** This brief is
written before Chinese is registered as a reading language and before any
Chinese text is drafted. Every choice below is a first proposal with its
main alternative; section 15 lists the ones that decide the most verses, for
the founder and a native reviewer to confirm or change once, before drafting
starts. Once confirmed, drafters follow them book by book without
re-deciding them; a drafter who thinks a rule is wrong for a passage follows
it anyway and says so in a rendering decision marked uncertain. Every
Chinese record will be `ai_draft`. Nothing is marked reviewed by Claude.

## 1. Sources and independence

- Translate from the Hebrew (and the Aramaic) and the Greek, never from the
  English. The English renderings and the literal gloss show how a sentence
  was read; the meaning decisions say what it means. Chinese says that
  meaning in its own way.
- **The Chinese Union Version (和合本, 1919) is not a source.** Its text is
  in the public domain in many places, and almost every Chinese Protestant
  knows its wording by heart, in both its editions (the 神 edition and the
  上帝 edition, section 4). That is exactly why it pulls hardest: a drafter
  who knows it reproduces it without noticing. The Charter's rule holds for
  it as for every reference Bible: **for comparison and review only, never
  the basis for wording.** Being out of copyright does not make it a source.
- **Never reproduce the wording of a copyrighted Chinese Bible**: the
  和合本修订版 (RCUV, 2010), the 新译本 (CNV) and 环球圣经译本, the 当代译本
  (CCB), the 现代中文译本 (TCV, and its 1995 revision), the 中文标准译本 (CSB),
  the 新普及译本, the 吕振中译本, the Catholic 思高本 (Studium Biblicum) and
  牧灵圣经, and the others. Draft from the source, the gloss and the English
  levels, then **compare every well-known verse with the CUV and rewrite any
  sentence that matches it, or a modern version, for more than a short
  common phrase.** A short common phrase is a term or fixed collocation any
  Chinese Christian would use (恩典, 神的国, 人子, 安息日, 万军之, 圣灵), not a
  clause.
- The familiar passages pull hardest: Genesis 1-3, 12, 22; Exodus 3, 20;
  Numbers 6:24-26; Deuteronomy 6:4-9; Psalms 1, 23, 51, 91, 103, 121, 139;
  Proverbs 3:5-6; Ecclesiastes 3; Isaiah 9, 40, 53; Jeremiah 29:11; 31:31-34;
  Micah 6:8; Matthew 5-7, 28:18-20; Luke 2, 15; John 1:1-18, 3:16, 14:6;
  Romans 3, 5, 8, 12; 1 Corinthians 13; Galatians 5:22-23; Ephesians 2:8-10;
  Philippians 2, 4; Hebrews 11:1; 1 John 4; Revelation 21. For these the
  drafter works from the gloss and the English levels with the CUV closed,
  and opens it only afterwards, to check.
- The conventional forms of names, the names of the books, and the church's
  shared vocabulary (sections 6-7 and `docs/chinese-terms.md`) are not
  wording and may be used.
- Never type Greek or Hebrew. A Greek or Hebrew word quoted in a decision is
  copied from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"zh": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers in every Chinese level, in the order the
  English has them. **(checked)** Write the marker straight after the
  punctuation that ends the previous verse's words, with one space after the
  number and none before the backslash: `……他们就跟从了他。\v 3 第三天`.
- **Word order.** Chinese puts modifiers, relative clauses, time and place
  before what they modify (那在天上的父; 他在会堂里教导人). A Greek sentence
  that runs across verses with a relative clause after its noun often wants
  that clause before the noun in Chinese. Keep each verse's content after its
  own marker as far as Chinese allows: split the sentence at a ，or ；, or make
  two sentences at Balanced and Readable. Where content has to cross a verse
  boundary, say so in a `word_order` rendering decision.
- The meaning decisions are shared: do not change them. Chinese needs only
  its own rendering decisions, with ids `r-zh-1`, `r-zh-2`, ... counted from
  1 in each record, `"layer": "rendering"`, `"language": "zh"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions. Quote the Chinese words under discussion
  ("\"恩典\" rather than \"恩惠\""). The site tells Chinese readers that notes
  are in English for now.
- Write a Chinese rendering decision where Chinese had to choose and a
  reader might ask why: a word chosen against the familiar CUV word, a form
  of address (你 / 您), a verse boundary moved, a setting span that differs
  from the English one, or a term settled here for the whole book (once,
  where it first appears in a passage). Do not repeat the English rendering
  decisions. Typical density: zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language. So each Chinese level must open and close the same
  quotations, in the same order, as the English one: no quotation added,
  dropped, merged or split. A sentence that begins or ends inside a speech
  begins or ends inside it in Chinese too (an opening “ with no ”, or a
  closing ” with no “). Speech broken by a verb of saying in English
  ("Lord," he said, "you...") takes two pairs in Chinese too:
  “主啊，”他说，“你……”.

## 3. The three levels in Chinese

The language is **Modern Standard Written Chinese** (现代汉语书面语) as
written in Mainland China: 普通话 vocabulary and grammar, Simplified
characters of the 通用规范汉字表 (2013), punctuation by GB/T 15834-2011 and
numbers by GB/T 15835-2011. Two registers are avoided at every level:

- **Classical and old-Bible Chinese**: 文言 forms (之乎者也 as grammar, 曰, 乃,
  其 as a plain pronoun, 焉, 矣, 尔 for "you", 吾, 彼 for "he"), and the CUV's
  early-twentieth-century forms that modern readers hear as "Bible
  language": 甚么, 晓得, 岂不是 in every question, 与 for "to" (归与你们), 必
  as a plain future in every clause, 便 as the normal "then", 凡……的 in
  every rule. Fixed terms keep their 之 (万军之,
  至圣所, 馨香之气); grammar does not.
- **Colloquial and regional speech**: northern 咱们 / 啥 / 甭 / 俺, Cantonese
  or Taiwanese usage (嘅, 系, 就是说 as filler), internet words, and slang.
  Readable is plain, not spoken.

The level names on the site are proposed as **直译** (Literal), **均衡**
(Balanced) and **易读** (Readable):

- **直译** is the ordinary Chinese word for a literal translation (the
  opposite of 意译), understood by every reader and the word Chinese
  translation studies use.
- **均衡** means "balanced", the English level's own idea: weighing the
  source's form against natural Chinese. 标准 ("standard") was considered and
  is not proposed, because 中文标准译本 is a published Bible's name and a
  standard suggests the other two levels are not; 意译 is not proposed either,
  because it suggests a free paraphrase.
- **易读** means "easy to read": the level's purpose, in two common
  characters. 白话 was considered and rejected (every level is 白话, written
  vernacular, as against 文言), and 浅白 or 通俗 can sound condescending.
- Two characters each, so the level switch and the interface fit, as the
  Japanese 逐語訳 / 標準訳 / 平易訳 fit. Main alternative for a reviewer:
  逐字 / 标准 / 浅白; or with 译 added (直译本 ...), which is longer and reads
  as the name of a separate Bible.

**Literal (直译, OWB-L).** Keeps the source's words and their grammar as
far as Chinese can: participles as 着 / 了 / ……之后 clauses, genitives as
……的, the source's repetitions (又……又……; 并且……并且……), its order of
clauses where Chinese allows, the historic present without a 了. Words
Chinese needs but the source lacks go in [square brackets] (ASCII `[` `]`,
as in every language). What Chinese grammar requires is **not** bracketed:
measure words (一个人, 一位天使, 一只羊), 的 / 地 / 得, the aspect particles
了 / 着 / 过, the copula 是, the plural 们, a resultative complement (打开,
看见), and a subject Chinese cannot leave out. Literal may read stiffly; it
must not be wrong Chinese, and it never falls back on 文言 to be close.

**Balanced (均衡, OWB-B).** Careful, natural formal written Chinese, the
register of a good public reading in church or of a serious book or
newspaper. Tracks the source closely; no brackets. Church words stay where
they are the living word for the thing (恩典, 悔改, 神的国, 大祭司, 门徒).
Four-character expressions (成语) are used where they are the natural
written Chinese for the sense, not as ornament, and never to echo the CUV.

**Readable (易读, OWB-R).** Plain, clear Chinese for a general reader: one
new to the church, a young reader, or a reader whose first language is
another Chinese language or a minority language. Short sentences; common
words and characters (the first level of the 通用规范汉字表, 3,500
characters, wherever a common word will do); everyday words over church ones
where both are current (收税的人 for 税吏, 坏人 for 恶人 where it fits);
idioms explained; and what the context implies made explicit where the
English Readable does so, with a decision. No 成语 a reader would need a
dictionary for.

**Characters.** Simplified characters of the 通用规范汉字表 only, with
Mainland word forms: 着 (aspect particle, not 著), 里 (not 裏), 于 (not 於),
台 (not 臺), 只 (not 祇), 么 / 吗 / 呢 as standard, 的 / 地 / 得 kept apart,
那 / 哪 kept apart, 作 / 做 by the dictionary (《现代汉语词典》). The only
characters outside the general list are the ones a convention needs (祂 and
祢 in a `deity_pronoun` span, section 4, and the established characters of
names). A Traditional-character Chinese (繁體中文, `zh-Hant`) for Taiwan, Hong
Kong and the diaspora is a separate future reading language with its own
brief (its quotation marks are 「 」, and its pronoun and name conventions
differ), not a conversion of this one.

## 4. God, the Lord and the divine name

### God: 神 by default, 上帝 as a Chinese reader setting

The word for God is the oldest dispute in Chinese Bible translation, the
Term Question (译名之争) of the nineteenth century. The missionaries could
not agree between 神 and 上帝, so the Union Version was printed in two
editions, word for word the same except for that one word, and both are
still printed and read. 神 (the 神版) is the edition most Mainland Protestant
churches use, and the 新译本 and the 中文标准译本 follow it; 上帝 (the 上帝版)
is preferred by many readers and churches, and by the 现代中文译本 and the
当代译本. (Chinese Catholics say 天主; the 思高本 uses it. It is not offered:
see below.)

Both words name the same God; the choice changes wording, never meaning.
That is what a reader setting is for (Settings change wording, never
meaning). So:

- **Proposed: a Chinese-only reader setting, `god_term`**, declared in
  `data/languages.json` as Spanish declares `plural_you`:
  `"settings": {"god_term": ["神", "上帝"]}`. Every word for the one God,
  *theos* in the New Testament and *Elohim* (*El*, *Eloah*) where it means
  the God of Israel, is written `{{god_term:神|上帝}}`, at every level.
- **Default 神**, the alternative 上帝. 神 is the word most Mainland
  Protestant readers know from the Bible they hold and the hymns they sing,
  and it joins naturally with what follows (神的国, 神的儿子, 神的话, 神啊).
  The main alternative is **上帝 as the default**: it is unambiguous for every
  Chinese speaker, Christian or not (神 alone also means "a god", "a spirit"
  and "spirit, mind"), and it may suit the Readable level's general reader
  better. A reviewer may prefer it; the setting makes either one click away.
- **Only the word goes inside the span**: `{{god_term:神|上帝}}的国`,
  `我的{{god_term:神|上帝}}`, `{{god_term:神|上帝}}啊`,
  `{{divine_name:上主|雅威}}你的{{god_term:神|上帝}}`. Check that the sentence
  reads with both: avoid a construction that works with one word only (神子
  as a compound; 上帝 cannot be shortened). Write 神的儿子, never 神子.
- **No span** where the word does not name the one God: gods and idols (别
  神, 外邦人的神, 众神, 神明, 大衮神), a "god" in a comparison ("I have made
  you like God to Pharaoh" follows the English level), *elohim* meaning
  heavenly beings or judges where the English level says so, and every
  compound in which 神 is not God at all (神迹, 神圣, 精神, 神庙, 神殿 for a
  pagan temple). A reader who chooses 上帝 still reads 神迹; that is right,
  since a 神迹 is a sign, not "God".
- The setting is implemented in the registration pull request before the
  first Chinese book is drafted (section 14): a new setting needs its reader
  control first. **If the founder decides against a setting**, the fallback
  is a fixed 神 at every level, with no span, and a note on the site; the
  spans would then not be written.
- **天主** is not a third option. It is the Catholic word and belongs with a
  Catholic vocabulary as a whole (names such as 梅瑟, 达味, 伯多禄 and book
  names such as 创世纪 differ too); one setting cannot give it. A Catholic
  Chinese edition would be a reviewer's later question.

### Lord: 主

- *kyrios* of God or Jesus, and *ʾAdonai*, is **主** at every level, with no
  span. "Lord!" in address: 主啊. The Lord Jesus: 主耶稣.
- A human master: 主人 (and 主 in a parable where the master stands for God,
  as the English level does). "Sir" to a stranger or a superior: 先生 (John
  4:11, 15, 19; 20:15), with a decision.

### The divine name: 上主 by default, 雅威 as the setting

The English writes YHWH as the title "the LORD" by default, with the name
"Yahweh" as the reader's alternative. Four Chinese forms were weighed:

| Form | Where it is used | For | Against |
|---|---|---|---|
| **上主** | 现代中文译本, the Catholic 思高本, much liturgy | A title, as "the LORD" is: "the Lord above". Distinct from 主 (*Adonai*, *kyrios*), as the English LORD is distinct from Lord. Understood by every reader. | Less familiar to Mainland Protestants than 耶和华. |
| 主 | Many modern prayers; the Japanese brief's choice | Short and familiar. | Merges YHWH with *Adonai* and with Jesus as 主: the reader loses what the English small capitals keep. |
| 耶和华 | Both CUV editions; nearly all Mainland Protestant use | The form Mainland Protestants know best. | A name, not a title, so it cannot be the default that matches "the LORD". It is the "Jehovah" form, the Hebrew consonants read with the vowels of *Adonai*; Open Word Bible does not use that form in any language (Hindi यहोवा, Japanese エホバ, Indonesian *Yehova* are not used). |
| **雅威** | Chinese scholarship; some Catholic and modern Protestant writing | The name as scholars reconstruct it, as English "Yahweh"; 雅 and 威 ("elegant", "majestic") read well and carry no other sense. | New to many readers. |

**Proposed: `{{divine_name:上主|雅威}}` at every level.** 上主 is the title,
the default, as "the LORD" is; 雅威 is the name, the reader's alternative,
as "Yahweh" is. Chinese has no case or article, so only the word goes inside
the span and everything else stays outside: `{{divine_name:上主|雅威}}是我的
牧者`, `{{divine_name:上主|雅威}}的话`, `{{divine_name:上主|雅威}}的殿`.

**Main alternatives** for a reviewer: `{{divine_name:上主|耶和华}}`, with the
CUV's form as the setting's name, for the Mainland Protestant reader who
expects it (a reviewer may judge that familiarity outweighs consistency with
the other languages); or 耶和华 as the default, which would break the rule
that the default is a title. The spelling 亚威 (seen occasionally) is not
proposed: 雅威 is the common form.

How it combines (the full table is in `docs/chinese-terms.md`):

| Hebrew (English) | Chinese |
|---|---|
| YHWH (the LORD) | `{{divine_name:上主\|雅威}}` |
| YHWH *Elohim* (the LORD God) | `{{divine_name:上主\|雅威}}{{god_term:神\|上帝}}` (上主神, 上主上帝, 雅威神, 雅威上帝) |
| the LORD your God | `{{divine_name:上主\|雅威}}你的{{god_term:神\|上帝}}`; plural 你们的 |
| *ʾAdonai* YHWH (the Lord GOD) | `主宰{{divine_name:上主\|雅威}}` |
| YHWH *tsevaot* (the LORD of hosts) | `万军之{{divine_name:上主\|雅威}}` (L, B); `统领万军的{{divine_name:上主\|雅威}}` (R) |
| *Yah* | `{{divine_name:上主\|雅}}` |
| *Hallelu Yah* | `你们要赞美{{divine_name:上主\|雅}}` (L, B), `要赞美{{divine_name:上主\|雅}}` (R); where the English keeps "Hallelujah" as a word (Revelation 19): 哈利路亚, no span |

- ***ʾAdonai* YHWH** is the hard case. English writes "Lord GOD"; the CUV
  writes 主耶和华. With 上主 the plain pattern gives 主上主, which a reader can
  parse as 主上 ("the sovereign, His Majesty") followed by 主. So the
  proposal is **主宰** ("Sovereign, the one who rules") for *ʾAdonai* in this
  phrase only: 主宰上主 by default, 主宰雅威 with the name. Main alternative:
  `主{{divine_name:上主|雅威}}` (主上主 / 主雅威), closer to the Hebrew's two
  words and to 主耶和华. Each book's first record with the phrase notes the
  choice in a decision.
- **雅 for *Yah*** follows the English, which shows "Yah"; a reviewer may
  find 雅 alone too slight in Chinese and prefer 雅威 there too. Note it once
  per block of psalms.
- **Exodus 3:14-15 and 6:2-3**, where the name itself is the subject, follow
  the English wording and decisions. "I am who I am" is drafted from the
  Hebrew and the gloss, not from the CUV's 我是自有永有的.
- In a New Testament quotation of the Old Testament the Greek has *kyrios*,
  so write 主 and note the Hebrew original in a decision, as the English does
  (John 1:23).
- 上主 never stands for Jesus or for *kyrios* in the New Testament, and 主
  never stands for YHWH in the Old outside a quotation the New Testament
  makes.

### Pronouns for God: the `deity_pronoun` setting

English capitalises pronouns for God and Christ by default (He, Him, You) and
lets the reader choose lowercase. Chinese has no capitals, but it has its own
reverent forms: **祂** for "he" (他 with the "spirit" radical 礻) and **祢**
for "you" (你 with the same radical). They are used widely in Chinese church
writing, hymns and some modern versions, and not in the CUV,
the 新译本 or general Mainland usage, which write 他 and 你 for God.

The two forms do exactly what the English capital does: the same pronoun,
marked as God's, with nothing else changed. So:

- **Proposed: `deity_pronoun` spans in Chinese**, written plain first and
  reverent second, as other languages write lowercase first:
  `{{deity_pronoun:他|祂}}` and `{{deity_pronoun:你|祢}}`. Readers see the
  second option by default, as they see "He" in English (`owb/markup.py`
  `DEFAULTS`), and can choose 他 / 你.
- **Where**: wherever the English has a span for the same person (God, and
  Christ: he, him, his; "you" when someone speaks to him). Only the
  character goes inside: `{{deity_pronoun:他|祂}}的名`, `{{deity_pronoun:你|祢}}的
  国降临`, `跟从{{deity_pronoun:他|祂}}`. Chinese has no reverent first person,
  so 我 (God or Jesus speaking) takes no span, as English "I" takes none. 们
  never follows a span (God is not addressed in the plural). At the start of
  a sentence the span is still written (Chinese has no capital to show it).
- **Not for** the Spirit as "it" (Chinese 他 for the Spirit follows the
  English: where the English spans "He" for the Spirit, so does the Chinese),
  figures in a parable, angels, the king of a psalm unless the English spans
  him.
- **The validator needs a change first.** `owb/validate.py` accepts a
  `deity_pronoun` span only when the alternative is the default with a
  capital letter. Chinese needs the two pairs 他 / 祂 and 你 / 祢 accepted for
  `zh`, and nothing else (section 14). The site's other rule holds: the
  setting changes only how the pronoun is written, never the wording.
- **Main alternative**: no `deity_pronoun` spans in Chinese, 他 and 你 plainly
  for God, as the CUV and Mainland general usage write, as the Japanese and
  Korean briefs have no spans. That needs no code. It is the choice if
  reviewers judge that 祂 and 祢 as the default would feel like Taiwanese or
  Hong Kong church usage to a Mainland reader; but then the default would
  differ from every other language's, and a reader who wants the reverent
  forms would have no way to get them.
- One more option was considered and is not proposed: 祂 by default with no
  setting. A reader setting is cheaper than a fixed choice nobody can undo.

## 5. Address and speech

Chinese marks the relation between speaker and hearer in a few places (你 /
您, terms of address). The Greek and Hebrew do not; these are wording
choices, rendering decisions, never meaning decisions. They hold through a
book so a scene does not change relationship from verse to verse.

### "I" and "we"

- **God and Jesus** say 我 at every level. **Kings** say 我 too: 朕, 寡人
  and 本王 are not used (they belong to Chinese court drama, not to an
  Israelite king).
- **People** say 我. The Hebrew humble "your servant" for "I" is kept as
  仆人 / 你的仆人 at Literal (仆人有一句话) and at Balanced where the English
  Balanced keeps it; Readable says 我, with a decision the first time in a
  book.
- **We** is 我们 at every level. Mainland written Chinese does not need the
  inclusive 咱们 (northern spoken usage), and choosing it would force a
  decision the source does not make. God's "Let us" (Genesis 1:26; 3:22;
  11:7) is 我们, with no span (Chinese has no reverent form of it).

### "You" singular: 你 and 您

The Greek and Hebrew have one singular "you". Mainland Chinese has the plain
你 and the polite 您. Proposed:

- **God and Jesus addressed: 你** (with the `deity_pronoun` span, 祢 by
  default), at every level, by everyone: the psalmist, the disciples,
  petitioners and opponents alike. Prayer in the Bible speaks to God
  directly and closely, and the Chinese church tradition does so with 你.
  Main alternative: 您 for God at Balanced and Readable, which some modern
  prayers use; it would also need the span to be dropped (there is no
  reverent form of 您).
- **God and Jesus speaking to people: 你** at every level.
- **People to each other**: 你 between equals, to family, to inferiors; and
  at **Literal everywhere** (Literal keeps the source's single "you").
  At **Balanced and Readable**, **您** where the scene is plainly respectful
  address to a superior: a subject to a king, a servant to a master, a
  petitioner to a governor or an official, a son asking a favour of a
  father in a formal scene (Isaac to Abraham, Genesis 22:7), Paul before
  Festus and Agrippa. Choose once per speaker in a scene and keep it;
  record the first use in a book in a `register` decision.
- **To a king**: 王啊 (L); 陛下 (B, R) as the term of address, and 您 as the
  pronoun at B and R. "My lord the king" is 我主我王 (L, B; a fixed address,
  four characters), 陛下 (R). "May the king live forever": 愿王万岁 (L, B),
  祝陛下万岁 (R).
- **"My lord"** (*ʾadoni*) to a superior who is not a king: 我主 (L), 大人 or
  主人 by context (B, R).
- **"Woman"** (*gynai*) as an address: 妇人 (L), with a decision; 女士 (B, R),
  Jesus's mother included (John 2:4; 19:26). Main alternative: 母亲 at R for
  his mother only.
- **"Teacher"** (*didaskale*) 老师 at every level; **"Rabbi"** 拉比. 夫子 (the
  CUV's word) is not used.

### "You" plural

- **你们** at every level, to people. 您们 is not standard written Chinese and
  is not used; respect to a group is shown by the term of address
  (诸位, 各位 at B and R in a formal speech, Acts 2:14 and 17:22).
- **No `plural_you` setting**: Chinese has no regional split in the plural.

### Brothers and sisters

- *adelphoi* meaning believers: `{{gender:弟兄姐妹|弟兄}}` at every level,
  inclusive by default, the traditional 弟兄 as the alternative. In address:
  `{{gender:弟兄姐妹|弟兄}}们` (L, B: 我的`{{gender:弟兄姐妹|弟兄}}`们; R:
  `{{gender:弟兄姐妹|弟兄}}`们). "Beloved brothers": 亲爱的`{{gender:弟兄姐妹|弟兄}}`们
  (L, B, R). 弟兄姐妹 is the everyday Chinese church address for a mixed
  congregation.
- A single brother in the faith: `{{gender:弟兄姐妹|弟兄}}` only where the
  English has a span; otherwise 弟兄. A sibling: 兄弟, 哥哥, 弟弟, 姐妹 as the
  source and context say (Chinese must choose older or younger: choose from
  the context and note it where it is a guess; where it cannot be known, 兄弟
  / 姐妹).

### Verbs of speaking

- **说** for everyone, God and Jesus included, at every level. Chinese has no
  honorific verb of speaking in modern use; 曰 and 谕 are not used.
- 回答说 for "answered and said" at L, 回答 at B and R; 问, 吩咐 (commanded),
  责备 (rebuked), 宣告 (declared) where the source has them.
- A quotation is introduced with a full-width colon: 耶稣说：“……” (section 9).

## 6. Names

### Principles

1. **Use the form in common use in Chinese Bibles** for every well-known
   name: in practice the Protestant forms that Mainland readers know
   (亚伯拉罕, 摩西, 大卫, 以利亚, 耶稣, 马利亚, 彼得, 保罗). These are the
   conventional forms of names, shared by all the Protestant versions; using
   them is not copying wording.
2. **Where a modern standard Chinese form is far better known for a place
   that still exists**, use it: 大马士革 (not 大马色), 塞浦路斯, 埃及, 罗马,
   雅典, 叙利亚 (Greek *Syria*; Hebrew *Aram* stays 亚兰). People keep their
   Bible forms (尼布甲尼撒, 古列, 大利乌, 亚哈随鲁); a reviewer may prefer the
   historians' forms (居鲁士, 大流士, 薛西斯) for the Persian kings, and the
   glossary lists both. Caesar is 凯撒 (the modern standard form), not the
   CUV's 该撒.
3. **One person, one form, in every book.** The glossary's form is the form.
   Where two people share a Hebrew name, they share the Chinese one; where the
   English distinguishes two names, Chinese does too (Abram 亚伯兰 / Abraham
   亚伯拉罕; Sarai 撒莱 / Sarah 撒拉).
4. **A new transliteration** (a minor name in a list or genealogy, with no
   established form) is made from the Hebrew or Greek sounds, by these rules:
   use the characters Chinese Bibles already use for the same sounds (以 for
   initial *yi-*, 亚 for *a*, 利 for *li*, 拿 for *na*, 撒 for *sa*, 米 for
   *mi*, 雅 for *ya*, 约 for *yo*, 哈 for *ha*, 西 for *si*, 巴 for *ba*); use
   neutral characters with no unfortunate sense (no 死, 鬼, 杀, 凶, 屎, and no
   character that makes the name read as a phrase); men's and women's names
   keep the usual distinction (女 radical characters, 拉 / 娜, for women only
   where the Bibles use them, 拿俄米, 底拿); keep names short, usually one
   character per syllable; and check the form is not already a different
   person's. Add the form to the book's section of `docs/chinese-terms.md`
   in the same pull request, and note it in a decision where it first
   appears.
5. **Catholic forms** (亚巴郎, 梅瑟, 达味, 依撒意亚, 若望, 伯多禄, 保禄) are not
   used; they belong to the Catholic vocabulary as a whole (section 4).
6. **No middle dot** in Bible names: the Bibles write 西门彼得, 加略人犹大,
   拿撒勒人耶稣 without one. The middle dot · (U+00B7) is used only where a
   modern Chinese name style would demand it for a foreign given name and
   surname, which the Bible hardly has.

### The common forms

The table in `docs/chinese-terms.md` ("Names") is the list; a few that recur
everywhere: 耶稣, 基督 / 弥赛亚 (section 8), 马利亚, 约瑟, 约翰, 施洗约翰,
西门彼得, 彼得, 安得烈, 雅各, 腓力, 多马, 马太, 加略人犹大, 保罗,
巴拿巴, 提摩太; 亚当, 夏娃, 挪亚, 亚伯拉罕, 以撒, 雅各, 约瑟, 摩西, 亚伦,
约书亚, 大卫, 所罗门, 以利亚, 以赛亚, 耶利米; 以色列, 犹大, 耶路撒冷, 锡安,
加利利, 撒玛利亚, 拿撒勒, 伯利恒, 埃及, 巴比伦, 亚述.

Jacob the patriarch and James the apostle are both 雅各 in Chinese, as in
the Chinese Bibles (the Greek name is the same); no distinction is invented.

### Book names

The book names of the Protestant Chinese Bibles, the conventions every
reader knows (they go in `data/books.json`, step 2 of
`docs/adding-a-language.md`): 创世记, 出埃及记, 利未记, 民数记, 申命记,
约书亚记, 士师记, 路得记, 撒母耳记上, 撒母耳记下, 列王纪上, 列王纪下, 历代志上,
历代志下, 以斯拉记, 尼希米记, 以斯帖记, 约伯记, 诗篇, 箴言, 传道书, 雅歌,
以赛亚书, 耶利米书, 耶利米哀歌, 以西结书, 但以理书, 何西阿书, 约珥书, 阿摩司书,
俄巴底亚书, 约拿书, 弥迦书, 那鸿书, 哈巴谷书, 西番雅书, 哈该书, 撒迦利亚书,
玛拉基书; 马太福音, 马可福音, 路加福音, 约翰福音, 使徒行传, 罗马书, 哥林多前书,
哥林多后书, 加拉太书, 以弗所书, 腓立比书, 歌罗西书, 帖撒罗尼迦前书,
帖撒罗尼迦后书, 提摩太前书, 提摩太后书, 提多书, 腓利门书, 希伯来书, 雅各书,
彼得前书, 彼得后书, 约翰一书, 约翰二书, 约翰三书, 犹大书, 启示录. A psalm is
诗篇第N篇 (the `chapter_names` word: 篇). The usual one- and two-character
abbreviations (创, 出, 利 ... 太, 可, 路, 约, 徒, 罗, 林前, 林后 ... 启) go in
`data/book_abbreviations.json`. Note for step 2: the alias check compares
the first three characters, and 约翰福音 / 约翰一书 / 约翰二书 / 约翰三书, 以赛亚书 /
以斯拉记 / 以斯帖记 / 以西结书 / 以弗所书, 撒母耳记 / 撒迦利亚书 must each still find
the right book.

## 7. Words for the whole Bible

The New Testament's words, and the ones both testaments share. The Old
Testament's (sacrifices, sanctuary, officials, formulas) are in
`docs/chinese-terms.md`. Key terms (data/key_terms.json) are the same word
at every level unless the table says otherwise.

| Greek / Hebrew (English) | Chinese | Notes |
|---|---|---|
| God (*theos*, *Elohim*) | `{{god_term:神\|上帝}}` | Section 4. Gods, idols: 神, 神明, plain. |
| Lord (*kyrios*, *ʾAdonai*) | 主 | Master: 主人; "sir": 先生. |
| the LORD (YHWH) | `{{divine_name:上主\|雅威}}` | Section 4. |
| Jesus | 耶稣 | |
| Christ | `{{christos:基督\|弥赛亚}}` | Section 8. 弥赛亚 plainly where the Greek has *Messias* (John 1:41; 4:25). |
| Holy Spirit; the Spirit | 圣灵; 灵 (圣灵 where the English says "the Spirit" of God) | The Spirit of God: `{{god_term:神\|上帝}}的灵`. |
| the Word (*logos*, John 1) | 道 | Every level, a key term; the decision at John 1:1 names 话语 / 圣言 as alternatives. |
| grace | 恩典 | Key term. Not 恩惠 (the CUV's word in greetings) or 恩宠 (Catholic). |
| faith; believe | 信心 (noun, L, B), 信 (R where natural); 信 / 相信 | Keep the verb 信 at every level (信他的人, 相信这道). 信仰 is "religion, creed", not *pistis*. |
| faithfulness (*pistis* of God; *ʾemunah*) | 信实 | |
| righteousness; righteous | 义 (L, B), 公义 where it is God's justice; 义人 / 公义的 | Key term. Readable may say 在神面前正直 / 与神关系正确 with a decision. |
| justify | 称义 (L, B); 算为义人, 接纳为义人 (R) | |
| truth | 真理 | Key term. Readable may say 真实的事 / 实话 where the sense is "what is true", with a decision. |
| glory; glorify | 荣耀; 使……得荣耀 / 荣耀 (verb) | Key term. |
| love (*agapē*, *agapaō*) | 爱 | |
| steadfast love (*hesed*) | 慈爱 (L, B); 始终不变的爱 (R) | See the glossary for its three uses. |
| mercy (*eleos*); compassion | 怜悯; 怜悯, 同情 | |
| peace | 平安 (greeting, inner peace, well-being); 和平 (between peoples, war's end) | Key term; *shalom* the same. |
| joy | 喜乐 (L, B), 快乐 / 喜悦 (R) | |
| salvation; save | 救恩 (God's saving, as a thing); 得救; 拯救, 救 | Key term. 救赎 is redemption. |
| redeem; redemption | 救赎 | Hebrew *goʾel*: see the glossary. |
| gospel, good news | 福音 (L, B); 好消息 (R) | |
| kingdom of God; kingdom of heaven | `{{god_term:神\|上帝}}的国`; 天国 | 天国 at every level; R may say 天上的国 with a decision. |
| repent; repentance | 悔改 | Readable may say 回心转意 / 改变心意归向神 with a decision. |
| sin; sinner | 罪; 罪人 | |
| forgive | 赦免 (L, B); 饶恕 / 原谅 (R) | |
| holy; sanctify; saints | 圣 / 圣洁; 使……成圣; 圣徒 (L, B), 属于神的人 (R) | |
| eternal life | 永生 | |
| world (*kosmos*) | 世界 (L, B); 世人 where it means people | |
| flesh (Paul's moral sense) | 肉体 (L, B); 罪性 / 人败坏的本性 (R) | With a decision where it first appears. |
| Son of Man | 人子 | A title, every level. Never under the gender setting. |
| Son of God | `{{god_term:神\|上帝}}的儿子` | Never 神子. |
| disciple(s) | 门徒 | |
| apostle | 使徒 | |
| prophet | 先知 | |
| the Law; the Law and the Prophets | 律法; 律法和先知 | |
| scribes | 文士 (L, B); 律法教师 (R) | |
| Pharisees; Sadducees | 法利赛人; 撒都该人 | |
| chief priests; high priest | 祭司长; 大祭司 | |
| elders | 长老 | |
| tax collectors | 税吏 (L, B); 收税的人 (R) | |
| Gentiles; the nations | 外邦人 (L, B), 非犹太人 (R); 万国 / 列国 | |
| synagogue; temple | 会堂; 圣殿 (*hieron*), 殿 (*naos*, where the distinction matters, L) | |
| church, assembly | 教会 | Every level; 会众 for an assembly that is not the church (Acts 19). |
| Sabbath; Passover | 安息日; 逾越节 | |
| baptize; John the Baptist | 施洗 / 受洗; 施洗约翰 | |
| angel | 天使 | |
| demon; unclean spirit | 鬼 (L), 邪灵 (B, R); 污灵 | 鬼 alone at B and R reads as "ghost". |
| devil; Satan | 魔鬼; 撒但 | 撒但 (the Bibles' form); main alternative the general 撒旦. |
| heaven; Gehenna; Hades | 天 / 天上; 欣嫩子谷 (L), 地狱 (B, R); 阴间 | |
| cross; crucify | 十字架; 钉在十字架上 | |
| Truly I tell you (*amēn*) | 阿们，我告诉你们 (L); 我确实告诉你们 (B); 我把实话告诉你们 (R) | In John doubled: 阿们，阿们 (L), 我确确实实地告诉你们 (B). One decision per passage. |
| Amen; Hosanna; Hallelujah | 阿们; 和散那; 哈利路亚 | |
| Rabbi; Teacher | 拉比; 老师 | |
| crowd | 群众 / 一群人 (L, B), 很多人 (R) | |
| hypocrites | 假冒为善的人 (L, B), 伪君子 (R) | |
| Woe to you | 你们有祸了 (L, B); 你们真是可悲 (R) | |
| slave (*doulos*, *ʿeved*) | 奴隶 (L); 仆人 (B, R) | As the English: slave at Literal, servant at Balanced and Readable, except where slavery itself is the point (slave and free), where 奴隶 stays at every level. |
| deacon (*diakonos* as a church office) | 执事 | Every level. |
| Advocate (*paraklētos*) | 辩护者 (L, B); 帮助者 (R) | Main alternative 保惠师 (the CUV's coinage, familiar to Protestants). |
| covenant | 约 (L, B); 盟约 (R) | New covenant 新约. |
| brothers (*adelphoi*, the believers) | `{{gender:弟兄姐妹\|弟兄}}` | Section 5. |

## 8. Reader settings in Chinese

Settings change wording, never meaning, exactly as in English.

- `divine_name`: `{{divine_name:上主|雅威}}`, with *ʾAdonai* YHWH as
  `主宰{{divine_name:上主|雅威}}` and *Yah* as `{{divine_name:上主|雅}}`
  (section 4).
- `god_term` (Chinese only, proposed): `{{god_term:神|上帝}}` for every word
  naming the one God (section 4).
- `deity_pronoun`: `{{deity_pronoun:他|祂}}`, `{{deity_pronoun:你|祢}}`
  wherever the English has a span for the same person (section 4); needs the
  validator change of section 14 before it is written.
- `christos`: `{{christos:基督|弥赛亚}}` at every level where the English has
  a christos span. With the name, where the English has
  `Jesus {{christos:Christ|the Messiah}}`, Chinese writes
  `耶稣{{christos:基督|弥赛亚}}` (耶稣基督 / 耶稣弥赛亚); in Paul's order,
  `{{christos:基督|弥赛亚}}耶稣`. Where the Greek has the article and the
  English Literal keeps it ("the Christ"), Chinese has nothing to keep:
  `{{christos:基督|弥赛亚}}` alone, and 那位 only where the English Balanced
  says "the Messiah" as a title being asked about (是那位`{{christos:基督|弥赛亚}}`
  吗？). Check that both options read naturally with what follows.
- `gender`: an inclusive default where the original means men and women,
  with the traditional form as the alternative. Chinese needs it less than
  English: 人, 人们, 世人, 众人, 凡……的人, 谁, 各人 and the third person 他们 for
  a mixed group are already inclusive, and get no span. Spans appear where
  Chinese has two ways of saying it:
  `{{gender:弟兄姐妹|弟兄}}` (believers), `{{gender:儿女|儿子}}` for *huioi*
  where sons and daughters are meant (`{{gender:神的儿女|神的儿子}}` is not
  written: only the noun is spanned, `{{god_term:神|上帝}}的{{gender:儿女|儿子}}`),
  `{{gender:人|男人}}` for *anēr* / *ʾish* meaning people in general,
  `{{gender:祖先|列祖}}` for "fathers" as ancestors. Never for God, Christ or
  named men, and never for the Son of Man. The English pronoun spans
  ("them / him" for "anyone") usually become 人, 这人, 自己 or nothing in
  Chinese, with no span; a `setting_alternative` decision records a
  difference from the English the first time in a passage.
- `units`: metric by default, the original unit as the alternative, as in
  every language but English: `{{units:约3公里|十五个斯塔迪亚}}`. Literal keeps
  the original unit with no span. Modern measures are written in Arabic
  digits with the unit (约45厘米, 约22升, 11.5克, 34公斤), as Mainland usage
  writes measurements (GB/T 15835); the original unit keeps Chinese
  numerals (三十肘). Coins have no metric form: a `units` span gives the value
  in wages by default and the coin as the alternative
  (`{{units:一天的工钱|一个银币}}`), as the English does. This differs from the
  English (US units) and needs a rendering decision the first time in a
  passage. The unit words are in `docs/chinese-terms.md`.
- `plural_you` is Spanish only.
- A setting span holds no quotation marks (`owb/markup.py` checks).

## 9. Punctuation, spacing and typography

- **Full-width punctuation** (GB/T 15834-2011) everywhere in the text:
  ，(comma) 、(enumeration comma, between items of a list: 彼得、雅各和约翰)
  ；：？！。. ？and ！only where the source asks or exclaims. No ASCII
  punctuation in Chinese text except the square brackets of Literal and the
  markers `\v N ` and `\q `.
- **Quotation marks: “ ” outside, ‘ ’ inside** (U+201C / U+201D and U+2018 /
  U+2019), the Mainland standard, and “ ” again for a third level. They are
  written as these curly characters in the data, never as straight `"` or
  `'`: the site curls straight quotes only after a space, a bracket or a
  dash (`build_site.smart_quotes`, `owb/markup.py` `_opens_here`), and
  Chinese puts a ：or ，or nothing before an opening quote, so a straight
  quote would be read as closing. The corner brackets 「 」 『 』 are Taiwan and
  Hong Kong usage and are not used.
- **The site's quotation checker must recognise them** (step 6 of
  `docs/adding-a-language.md`). Today `owb/markup.py` takes the outermost
  marks to be straight `"` unless a text has guillemets or corner brackets,
  so a Chinese sentence that begins inside a speech (a closing ” with no
  opening one) would be misread. The registration pull request teaches it
  that a text with Han characters and curly double quotes has “ ” outside
  and ‘ ’ inside (section 14), with tests in `tests/test_words_of_jesus.py`.
- **Speech**: introduced with a full-width colon, 他说：“……”. A quotation that
  is a whole sentence ends with its own 。？！ **inside** the closing mark
  (耶稣说：“你们跟我来。”); a quotation embedded in a sentence has none
  inside (他们称他为“拉比”。). Speech broken by the verb of saying:
  “主啊，”他说，“你……。” Nested: where the inner quotation ends the outer one, the stop goes
  inside the inner mark and nothing follows it but the closing marks:
  他说：“经上写着：‘……。’” A quotation inside a sentence that goes on takes
  no stop inside (他说：“‘……’这句话是真的。”).
- **Ellipsis** …… (two U+2026), **dash** —— (two U+2014), never ASCII `...`
  or `--`.
- **Book titles** in the text (the Book of Psalms, the book of the Law where
  it is a title) take 《 》 (在《诗篇》里写着, "it is written in the book of
  Psalms", Luke 20:42); a book within a title takes 〈 〉.
- **Parentheses** where the English has them: full-width （ ）. Literal's
  supplied words keep the ASCII [ ] of every language.
- **No spaces** between characters or words. A space appears only after a
  verse number (`\v 3 `) and on both sides of a line marker (`…… \q ……`), as
  the markup requires. No space around digits either (约3公里, not
  约 3 公里).
- **Line breaking and fonts** are the site's (section 14): Chinese is set in
  the reader's own Simplified Chinese fonts, broken by the strict rules (no
  ，。、 or closing quote at a line start), with no italics.

## 10. Numbers

- **Chinese numerals in running text** (十二个门徒, 第三天, 五千人, 四十年,
  一百二十岁, 十四万四千), as Bible readers expect and as Chinese literary and
  religious prose writes them. Large census numbers too (四万六千五百), with
  万 as the unit of grouping; no Arabic digits in counts.
- **Arabic digits only in a measure the `units` setting gives in modern
  terms** (约3公里, 45厘米), and in decimals (11.5克).
- **Dates and times**: ordinals with 第 (第一个月 at L, 正月 at B and R only where
  the English names the month as the first; 第七天). Hebrew month names
  (亚笔月, 尼散月) follow the glossary. Clock time: Literal keeps the source's
  count (第六时, "about the sixth hour"); Balanced and Readable give the time
  as a modern reader counts it (中午十二点左右 / 正午), with a decision.
- Chapter and verse references in decisions stay in English form (1:2).

## 11. Poetry, headings and the Old Testament

- **Lines.** Poetry is set in lines, as `docs/english-style.md` section 10
  describes: each break inside a verse is a `\q ` marker. Chinese follows the
  English level exactly: where an English level has `\q` breaks, that
  Chinese level has the same number of lines, breaking at Chinese's own
  phrase boundaries; where the English level is prose, so is the Chinese. A
  verse start is always a line start. Write a space on both sides of the
  marker (`早晨我要歌唱， \q 晚上我要称谢。`): the markup checks it.
  Chinese lines are short; do not pad a line to match the English, and do not
  force the parallel lines into equal character counts.
- **Psalm titles** are verse 1, as in the Hebrew: translated as the English
  level does it (Literal keeps the Hebrew's words: 大卫的诗; Readable may
  explain). Musical terms the English transliterates are transliterated
  (细拉; the others as the glossary has them).
- **The psalmist** says 我 and speaks to God as 你 (with the span); God
  speaking says 我.
- **Old Testament narrative**: the Hebrew chain of "and ... and ..." is
  joined with 就, 于是, 然后 and 又 at Literal, not with a 并且 or 和 between
  clauses (和 joins nouns only); Balanced and Readable use ordinary
  connectives and new sentences.
- **Laws and instructions** (Exodus 20-40, Leviticus, Deuteronomy): 你要……,
  不可…… at L and B (不可杀人); 你必须……, 不要…… at R. 不可 is a short common
  phrase of command, not CUV wording.
- **Section headings and summaries.** Where a book's
  `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json` has languages
  beside English, add `"zh"` beside them as each book is drafted, written
  from Open Word Bible's own Chinese wording, never the headings of a
  Chinese Bible. They are AI drafts until reviewed.

## 12. Recurring formulas

One form each, in every book; the first record of a passage that uses one
notes it once. `docs/chinese-terms.md` has the rest. Below, *dn* is
`{{divine_name:上主|雅威}}`.

| Source (English) | Literal | Balanced | Readable |
|---|---|---|---|
| Thus says the LORD (*koh ʾamar YHWH*) | *dn*如此说 | *dn*这样说 | *dn*说 |
| declares the LORD (*neʾum YHWH*) | 这是*dn*的宣告 | 这是*dn*的话 | *dn*说 |
| The word of the LORD came to ... | *dn*的话临到…… | as L | *dn*对……说 |
| I am the LORD | 我是*dn* | as L | as L |
| behold (*hinneh*, *idou*) | 看哪 | 看 / 你看, or left out where it only marks attention | left out, or 要知道 |
| and it came to pass (*wayehi*) | 那时 / a time clause (……的时候) | left out, or a time clause | as B |
| son of man (Ezekiel's address) | 人子啊 | 人哪 | as B |
| answered and said | 回答说 | 回答 | as B |
| fell on his face | 脸伏于地 | 俯伏在地 | 跪下, 脸贴着地 |
| In that day | 到那日 | as L | 到那时 |
| Fear not | 不要怕 | as L | 不要害怕 |
| Woe to you | 你们有祸了 | as L | 你们真是可悲 |
| grace and peace to you | 恩典与平安归给你们 | 愿你们得着恩典与平安 | 愿你们得到恩典和平安 |
| Truly I tell you | 阿们，我告诉你们 | 我确实告诉你们 | 我把实话告诉你们 |

Ezekiel's 人子啊 at Literal and 人哪 at B and R keep the prophet's address
apart from Jesus's title 人子 except where the source's words must show (L).
Main alternative: 人子 at every level, as the Chinese Bibles have it.

## 13. Drafting book by book

1. **Check the book is free** (`check-book-before-translating` skill) and
   that the English is drafted: Chinese is drafted from records that already
   have their meaning decisions.
2. **Read this file, the book's section of `docs/chinese-terms.md`, and the
   book's English terms notes.** The glossary's form is the form.
3. **Draft each record at L, then B, then R**, from the Hebrew or Greek, the
   gloss, the meaning decisions and the English levels. Keep the English
   record's verse markers, line breaks and quotations (section 2).
4. **Compare each familiar verse with the CUV** and a modern version and
   rewrite any clause that matches (section 1). Do not open them for
   unfamiliar verses: the check is for memory's pull, not a source.
5. **Write the decisions** (section 2): the first use in the book of a
   glossary choice, a name not in the glossary, every setting span that
   differs from the English, every 您.
6. **Add new names** to the book's section of `docs/chinese-terms.md` in the
   same pull request (section 6).
7. **Before the pull request, search the book's Chinese** for what this file
   excludes, at every level: 耶和华, 甚么, 晓得, 归与, 夫子, 该撒, 咱们, 您们, 神子,
   朕, 曰, Traditional characters (著 as a particle, 裏, 於, 祇), ASCII `"`
   `'` `,` `.` `?` `!` `:` `;` in the text, straight quotes, 「 」, and a
   space between characters. Errors too: 上主 or 雅威 outside a
   `divine_name` span; 神 or 上帝 naming the one God outside a `god_term`
   span; 祂 or 祢 outside a `deity_pronoun` span.
8. **Headings and summaries** for the book in Chinese (section 11).
9. One pull request per book; `scripts/check.sh` must pass.

## 14. What the registration pull request needs

Chinese is not yet a reading language. Steps 1-6 of
`docs/adding-a-language.md` go into one pull request before any Chinese is
drafted. Beyond the usual files, this brief's proposals need:

- **`data/languages.json`**: `{"code": "zh", "name": "Chinese", "native":
  "简体中文", "quotes": "“{}”", "settings": {"god_term": ["神", "上帝"]}}`
  (native name: 简体中文 marks the script; 中文 is the alternative if a
  Traditional edition never comes).
- **The `god_term` setting** (if confirmed): added to `SETTINGS` in
  `owb/markup.py` and `web/markup.js`, to the reader's settings and
  defaults (`web/reader.js`, `web/memorize.js`), its control in
  `scripts/build_site.py` beside `plural_you`'s, its hint and label in every
  `i18n/` catalog and in `web/admin.js`, and `scripts/settings_parity.py`
  (counted, not compared, as `plural_you`). `owb/validate.py` then allows it
  for `zh` only, as it does `plural_you` for Spanish.
- **`deity_pronoun` pairs** (if confirmed): `owb/validate.py` accepts, for
  `zh` renderings only, the pairs 他 / 祂 and 你 / 祢 as well as the capital
  rule, with a test.
- **Quotation marks**: `owb/markup.py` `_quotations` takes “ ” as the
  outermost and ‘ ’ as the inner marks in a text with Han characters and
  curly double quotes (the corner-bracket test stays first, for Japanese),
  so a sentence that starts or ends inside a speech pairs correctly; tests
  in `tests/test_words_of_jesus.py`. Check `scripts/check_verses_of_the_day.py`
  (`QUOTES`), the verse-of-the-day regex in `tests/test_site.py` (。！？ and ”
  as a sentence end), and the punctuation stripped in `scripts/level_checks.py`
  and `scripts/name_spellings.py` (add ，。、；：？！《》（）——).
- **`web/style.css`**: `:lang(zh)` rules as for Japanese: strict line
  breaking, no italics, and a font stack of the reader's own Simplified
  Chinese fonts (PingFang SC, Hiragino Sans GB, Microsoft YaHei, Noto Sans
  CJK SC / Source Han Sans SC for the interface; Songti SC, STSong, SimSun,
  Noto Serif CJK SC / Source Han Serif SC for the reading text). The curly
  quotes must take a Chinese font's full-width glyphs: in the Japanese stack
  the Latin font (Gentium) comes first and would draw “ ” as narrow Latin
  quotes, so the zh stack puts the CJK font first for the reading text, or
  gives the quotes a CJK font through a `unicode-range` face.
- **`lang` attribute**: the site should mark Chinese pages
  `lang="zh-Hans"` (and hreflang `zh-Hans`) even though the code is `zh`,
  so browsers choose Simplified Chinese glyphs rather than Japanese or
  Traditional ones for shared characters. A human decides whether the code
  itself should be `zh-Hans`.
- **Search**: `backend/translation/search.py` `CONFIGS` maps `zh` to
  `owb_cjk` (bigrams), as Japanese; Postgres has no Chinese stemmer.
- **`backend/staff/overlap.py`** `EDITION_LANGUAGE`: `zho` (or `cmn`) for the
  Chinese reference Bibles, so the overlap report compares drafts with the
  CUV, which matters more for Chinese than for any language but Indonesian.
- **`owb/morph.py`**: grammar words in Chinese (名词, 动词, 主格, 属格, 单数,
  复数, 阳性, 完成时, 不定过去时, 主动态, 被动态, 命令语气, ...), as Chinese
  grammars of Greek and Hebrew name them, for a reviewer to check.

## 15. Defaults for the founder to confirm

Each decides the wording of thousands of verses. Confirm or change each
once, before drafting; the outcome is recorded under a "Settled" heading at
the top of this file, as the Vietnamese and Korean briefs do.

1. **God**: a Chinese-only `god_term` setting, `{{god_term:神|上帝}}`,
   default 神. Alternatives: default 上帝; no setting and a fixed 神.
2. **YHWH**: `{{divine_name:上主|雅威}}`. Alternatives: 耶和华 as the
   setting's name; 主 as the default.
3. ***ʾAdonai* YHWH**: 主宰上主. Alternative: 主上主.
4. **Pronouns for God**: `{{deity_pronoun:他|祂}}`, `{{deity_pronoun:你|祢}}`,
   祂 / 祢 shown by default (a validator change). Alternative: no spans, 他 and
   你 plainly.
5. **Address**: 你 to God and Jesus; 你 at Literal everywhere; 您 to kings,
   masters and officials at Balanced and Readable. Alternative: 您 for God at
   B and R.
6. **Christ**: `{{christos:基督|弥赛亚}}`, 耶稣`{{christos:基督|弥赛亚}}`.
7. **Brothers**: `{{gender:弟兄姐妹|弟兄}}`.
8. **Quotation marks**: “ ” and ‘ ’ written curly in the data, with the
   checker change of section 14.
9. **Numbers**: Chinese numerals in the text, Arabic digits in modern
   measures.
10. **Names**: the Protestant forms in common use; modern standard forms
    for places that still exist (大马士革); 凯撒; the Persian kings in their
    Bible forms (alternative: 居鲁士, 大流士, 薛西斯).
11. **Level names**: 直译, 均衡, 易读.

## 16. Status

A Chinese rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.

## 17. Search

Chinese is written without spaces, so site search will index Chinese
sentences by character pairs, as Japanese (`backend/translation/search.py`,
`ngrams`): a word is found anywhere inside a clause, and a single character
on its own. Full-width digits and letters in a query are read as ASCII
(约翰福音３：１６). This does not affect drafting, but a word written two ways
(赦免 in one place, 饶恕 in another, for the same Greek at the same level) is
two words to search: keep the glossary's word through a book. The setting
spans are searched in their default form (神, 上主, 祂), so a reader who
searches 上帝 or 雅威 finds what the alternative shows only if search indexes
both options; the registration pull request should check which it does.
