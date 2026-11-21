# Russian review guide

For native Russian speakers who review the Open Word Bible in Russian. It
says how review works on the site, which choices to settle first because they
change wording across the whole Bible, where the drafters were unsure, and
which passages to read first. The drafting rules themselves are in
`docs/russian-style.md` (the New Testament and the levels) and
`docs/russian-terms.md` (the Old Testament's words, formulas and names); the
founder's Translation Charter is above them both.

## Кратко (summary in Russian)

- Вся Библия (30 637 предложений) переведена на русский с еврейского и
  греческого. Это черновик, подготовленный с помощью ИИ: каждое предложение
  остаётся черновиком (`ai_draft`), пока его не одобрит рецензент, указанный
  по имени.
- Каждое предложение дано в трёх вариантах: Буквальный (L), Сбалансированный
  (B) и Простой (R).
- Настройки читателя меняют слова, но не смысл: ГОСПОДЬ или Яхве, он или Он,
  Христос или Мессия, метры или локти, «братья и сёстры» или «братья».
- Рецензирование идёт в разделе Admin сайта: Review → Russian wording. Каждое
  предложение можно одобрить (Approve), отметить проблему (Flag) или
  прокомментировать (Comment).
- С чего начать: сначала решения, которые повторяются по всей Библии
  (раздел 3), затем самые читаемые места (раздел 5), затем неуверенные
  решения (раздел 4).
- Решения и примечания пока написаны по-английски.

(This summary was drafted with AI help too; a reviewer is welcome to correct
it.)

Counts in this guide were made from `content/` on 18 November 2026 with the
scripts named in section 6; they will drift as the text is revised. Verse
numbers are those of the Hebrew and Greek: in the Old Testament a psalm's
title is verse 1 (Psalm 51:1 in English is 51:3 here) and Micah 5:2 in
English is 5:1 here. `data/versification.json` maps one to the other.

## 1. How to review

### What you are reviewing

- **One record per source sentence.** Each record in `content/<BOOK>/` holds
  the source words, a literal English gloss, the renderings in every language
  at three levels, and the *decisions* that explain them. Every one of the
  30,637 records has a Russian rendering, and every record is `ai_draft`: the
  Russian was drafted by Claude, an AI, and nothing is marked reviewed by an
  AI.
- **The three levels.** The site calls them **Буквальный** (Literal, L),
  **Сбалансированный** (Balanced, B) and **Простой** (Readable, R). Literal
  keeps the source's words and grammar, with words Russian needs in [square
  brackets]. Balanced is careful standard modern literary Russian for public
  reading, without Slavonicisms (сей, оный, дабы, ибо). Readable is plain
  everyday Russian for new and young readers. Psalm 23:1 as drafted:
  - L: Псалом Давида. `{{divine_name:ГОСПОДЬ|Яхве}}` — пастух мой; не будет у меня недостатка [ни в чём].
  - B: Псалом Давида. `{{divine_name:ГОСПОДЬ|Яхве}}` — мой пастух; у меня никогда не будет нужды.
  - R: Песнь Давида. `{{divine_name:ГОСПОДЬ|Яхве}}` заботится обо мне, как пастух. У меня есть всё, что мне нужно.
- **Two layers of decisions.** *Meaning* decisions (ids `m1`, `m2`, ...) say
  what the Hebrew or Greek means. They are shared by every language and are
  reviewed by scholar reviewers of Hebrew and Greek. *Rendering* decisions
  (ids `r-ru-1`, `r-ru-2`, ..., `"language": "ru"`) say how Russian words
  that meaning; there are 14,001 of them. Decision text is in English and
  quotes the Russian. A Russian rendering may not narrow or widen what the
  meaning decisions say: if you think the meaning itself is wrong, that is a
  flag on the meaning, for every language, not a change to the Russian alone.
- **Your approval is of the Russian wording**: the three Russian levels and
  the Russian rendering decisions of one sentence. Approving the meaning (by
  a scholar reviewer) is what moves a sentence from `ai_draft` to
  `meaning_reviewed`; wording approvals are kept per language.

### Reader settings

A reader setting lets the reader choose between two wordings of the **same
meaning**: in the text it is a span `{{setting:default|alternative}}`.
Settings change wording, never meaning; a difference of meaning is a decision
and a footnote, never a setting. Russian uses five:

| Setting | Example | Records | Check |
|---|---|---:|---|
| `deity_pronoun` | `{{deity_pronoun:он\|Он}}`, `{{deity_pronoun:я\|Я}}` | 8,609 | On every pronoun for God (not on свой, себя, or a sentence-initial Я), and on no one else. |
| `divine_name` | `{{divine_name:ГОСПОДЬ\|Яхве}}`, inflected in each option (`ГОСПОДА\|Яхве`, vocative `ГОСПОДИ\|Яхве`) | 5,934 | Is ГОСПОДЬ in capitals right as the default, kept apart from Господь for *Adonai*? Is Яхве the form you want? |
| `gender` | `{{gender:дети Израиля\|сыны Израиля}}`, `{{gender:братья и сёстры\|братья}}` | 1,220 | Only where Russian really has two wordings; люди, человек, кто need none. |
| `christos` | `{{christos:Христа\|Мессии}}` | 488 | Both options read naturally in their case. |
| `units` | `{{units:135 метров\|300 локтей}}`; coins as wages | 400 | Metric by default, the original unit as the alternative; Literal keeps the original unit. |

### What to check in each sentence

1. **Meaning**: compare with the literal gloss, the English and the meaning
   decisions. The Russian says what they say, no more and no less, at every
   level.
2. **Natural Russian for the level**: word order, aspect, connectives; no
   Slavonicisms at Balanced and Literal where a modern word says the same;
   Readable should sound like speech.
3. **Address** (`docs/russian-style.md` section 4, `docs/russian-terms.md`
   "Address and pronouns"): ты to God and from God at every level; вы only for
   a Hebrew or Greek plural; courtly address in the words (господин, господин
   мой царь), not in вы.
4. **Consistency**: key terms and names keep one form across books (the terms
   file). A choice you would change everywhere is raised once (below), not
   verse by verse.
5. **Spelling and punctuation**: ё wherever it is pronounced, « » outside and
   “ ” inside, an em dash with spaces. Each level must open and close the
   same quotations as the English: the site colours the words of Jesus by
   counting them.
6. **Our own wording**: the drafts must not reproduce a copyrighted Russian
   Bible (the RBO Modern Russian Translation, the New Russian Translation,
   «Слово Жизни», Kulakov, «Радостная весть» and others;
   `docs/russian-style.md` section 1). The Synodal is in the public domain
   but is not copied either. Flag any run longer than a short common phrase
   that matches a well-known version; the familiar passages of section 5
   pull hardest.
### Where and how: the admin

Nothing in this repository, ticking a box in these lists included, changes a
record's status. Review happens in the site's admin, one sentence at a time.

1. **Get the role.** Sign in at <https://openwordbible.org> and ask the
   founder for the **Language reviewer** role for **Russian** (a super admin
   grants it in the admin's **Team & access** page). It opens **Review** and
   the progress pages.
2. **Open the queue.** Admin → **Review** → **Russian wording**. Filter by
   book
   and by state (*To review*, *Not reviewed*, *Changed since approval*,
   *Flagged*, *Approved*); the queue is in Bible order.
3. **Read the sentence.** The page shows the source words (hover for lemma,
   gloss and grammar), the literal gloss, the Russian at all three levels, the
   meaning decisions and the Russian decisions. The **Verse inspector** link
   shows the whole verse in every language, the English included, with every
   decision and the file it lives in.
4. **Act** (keys: `a` approve, `f` flag):
   - **Approve the Russian wording** when the three levels and the Russian
     decisions are right. The approval records your name and a digest of what
     you approved; if the sentence changes later it returns to your queue as
     *changed since approval*.
   - **Flag** a problem, with a note: which level, what is wrong, and the
     Russian you propose. Say "meaning" if the problem is the meaning.
   - **Comment** to leave a note without approving or flagging.
5. **Changes are made through fix requests.** Editors see open flags in
   **Reviewer flags** and, from the **Verse inspector**, file a **fix
   request**: a GitHub issue labelled `fix-request` that a Claude session
   works into a pull request, which a person merges. Once deployed, the
   changed sentence comes back to your queue; the flag stays open until the
   Russian layer is approved again. (If you hold the editor role you can file
   the fix request yourself, from the verse inspector's "File a fix request".)
6. **Book-wide choices.** For a choice that should change everywhere (a term,
   a name's spelling, a form of address), flag the first verse where it
   occurs, write "throughout", and name the item in section 3 below. The
   editors change `docs/russian-terms.md` or `docs/russian-style.md` and revise
   every passage drafted under it. The admin's **Consistency**, **Key terms**
   and **Uncertain decisions** pages (filter by layer "Russian") help find all
   the places.

## 2. Book-wide defaults to confirm

These are settled in the briefs and applied everywhere; agree or say what you
want instead before reading passages:

- the level names Буквальный, Сбалансированный, Простой;
- `{{divine_name:ГОСПОДЬ|Яхве}}` in capitals (Иегова not used), Господь for
  *Adonai*, Владыка ГОСПОДЬ for *Adonai* YHWH, Бог Всевышний, ГОСПОДЬ Саваоф
  (L, B) / ГОСПОДЬ Воинств (R);
- `deity_pronoun` spans on God's pronouns, ты to God;
- the key terms of `docs/russian-style.md` section 6 and the tables of
  `docs/russian-terms.md` (завет, неизменная любовь for *ḥesed*, Закон /
  наставление for *torah*, шеол (L) / мир мёртвых (B, R) for Sheol, раб for
  *ʿeved*, ...).

## 3. Decisions that affect the whole Bible: settle these first

Each item below is open: the drafts made one choice, the data shows it
applied unevenly, or the terms file has no settled form. One ruling changes
many records, so settle these before reading passages. Counts are records
(one record is one sentence, at all three levels).

### 3.1 "The peoples" → племена: unapplied before Job, missed after

- **Question.** Is "the peoples" (*ʿammim*, beside "the nations", народы)
  племена everywhere, and how is a miss fixed?
- **Now.** `docs/russian-terms.md` sets народы for the nations and племена for
  the peoples ("peoples, nations and languages" in Daniel: племена, народы и
  языки). The rule came in with the poetry and prophets. Of the Old Testament
  records whose English has "peoples": **before Job, 87, of which 83 have no
  племя at any level** (народы instead, for example Genesis 28:3, 49:10,
  Exodus 19:5, Deuteronomy 2:25); **from Job on, 156, of which 96 have
  племена and 60 do not** (for example Psalms 96:3, 96:5, 96:7, 105:1, 117:1;
  Isaiah 10:13-14). Some misses may be deliberate (the English "peoples" does
  not always stand for *ʿammim*).
- **Alternatives.** (a) Apply the rule through Genesis to Esther and fix the
  misses after Job; (b) keep народы wherever the context has no "nations"
  beside it, and племена only in the paired phrase; (c) a different word for
  "peoples" (for example народности), which would also free племя for
  "tribe" (3.6).
- **If changed.** Under (a), about 140 records; under (b), about 100 records
  from Job on go back to народы.

### 3.2 храм or Храм, Old and New Testament

- **Question.** Is the Temple in Jerusalem written with a capital?
- **Now.** The two Testaments disagree. `docs/russian-style.md` (the New
  Testament) says Храм with a capital for the Temple in Jerusalem, and the
  New Testament has a mid-sentence Храм in **91** records (Matthew 18, Mark
  11, Luke 22, John 16, Acts 23, 1 Corinthians 1), lowercase храм in 45 (other
  temples, the body as a temple, Revelation). `docs/russian-terms.md` (the
  Old Testament) says храм, and the Old Testament has lowercase храм in
  **662** records and a capital in only **5** (Ezra 6:3; Psalm 118:19;
  Isaiah 43:28, 44:28, 66:20).
- **Alternatives.** (a) Храм for the Jerusalem Temple in both Testaments;
  (b) храм in both (modern Russian usage, the capital only in fixed names);
  (c) as now, each Testament its own rule.
- **If changed.** (a) revises several hundred Old Testament records (Kings,
  Chronicles, Ezra, the prophets), checking each that the Jerusalem Temple is
  meant; (b) about 96 records (91 New Testament, 5 Old).

### 3.3 One form for each of six names

The Hebrew sometimes spells one person's name two ways; the terms policy is
"keep each name where the Hebrew has it", but the drafts follow neither one
form nor the Hebrew consistently:

| Name | Forms now (records) | Hebrew | Question |
|---|---|---|---|
| Jonadab (David's nephew, 2 Samuel 13; the son of Rechab, 2 Kings 10 and Jeremiah 35) | Ионадав in 11 records (2 Samuel 13:3-35; 2 Kings 10:15-23; Jeremiah 35:6, 10, 19), Иегонадав in 4 (Jeremiah 35:8, 14, 16, 18) | *Yehonadab* in 2 Samuel 13:5, 2 Kings 10:15, 23 and Jeremiah 35:8, 14, 16, 18; *Yonadab* elsewhere | One form (Ионадав, the terms table's), or follow the Hebrew in Samuel and Kings too, as Jeremiah does? 15 records. |
| Elzaphan / Elizaphan the Kohathite | Элцафан (Exodus 6:22), Елцафан (Leviticus 10:4), Елицафан (Numbers 3:30; 1 Chronicles 15:8; 2 Chronicles 29:13) | *Elzaphan* in Exodus and Leviticus, *Elizaphan* in Numbers and Chronicles | At least Е or Э one way; one form or two? (Numbers 34:25 Елицафан is another man.) 5 records. |
| Mount Zalmon | Селмон (Judges 9:48), Цалмон (Psalm 68:15 [68:14]) | one name | One form; Цалмон also names David's warrior (2 Samuel 23:28). 2 records. |
| Eshtemoa | Естемоа (1 Samuel 30:28; 1 Chronicles 4:17, 19; 6:42), Ештемоа (Joshua 21:14), Ештемо (Joshua 15:50, Hebrew *Eshtemoh*) | two spellings | Е-с-т or Е-ш-т; keep Ештемо for the other spelling? 6 records. |
| the Maacathite(s) | маахатцы (Deuteronomy 3:14; Joshua 12:5, 13:11, 13), маахатянин (2 Kings 25:23; Jeremiah 40:8), маахитянин (2 Samuel 23:34; 1 Chronicles 4:19) | one gentilic | One form of the gentilic. 8 records. |
| Abinadab | Аминадав in all 11 records (1 Samuel 7:1, 16:8, 31:2; 2 Samuel 6:3; 1 Chronicles 2:13, 8:33, ...), the Synodal form | *Abinadab*, a different name from *Amminadab* | Аминадав is also Amminadab (14 records, Matthew 1:4). Keep the traditional form, or Авинадав (named in the decision at 1 Samuel 31:2) so the two men differ? |

**If changed.** 2-15 records each, 47 in all; mechanical once ruled.

### 3.4 Дарий Мидянин: capital or not

- **Question.** Is "the Mede" in Darius' epithet capitalised?
- **Now.** Дарий Мидянин in Daniel 6:1 and 11:1 (both records, every level),
  following the terms table ("as drafted"); Daniel 9:1 says мидянин по
  происхождению (B) and из потомков мидян (L). Russian writes ethnonyms in
  lowercase; the capital treats it as part of the name.
- **Alternatives.** Дарий мидянин; Дарий Мидийский.
- **If changed.** 2 records.

### 3.5 ибо and сей left at Literal

- **Question.** The style guide bans ибо, сей, оный, дабы at Balanced and
  says "no ибо at Literal". Clear what remains?
- **Now.** ибо at Literal in **83** records (Job 30, 2 Kings 22, Ezekiel
  11, Exodus 10, Numbers 5, 1 Chronicles 4, Proverbs 1), and at Balanced in
  11. Forms of сей: the idiom до сего дня ("to this day") at Literal in **47**
  records (Joshua 15, 2 Kings 10, Genesis 7, 1 Samuel 5, ...), at Balanced in
  24; по сей день at Balanced in 22; and как [это] в сей день at 1 Kings 3:6.
  Also до сих дойдёшь (Job 38:11). Other matches are not Slavonicisms (the
  verb сей, "sow", Leviticus 19:19; the name Сия, Nehemiah 7:47).
- **Alternatives.** (a) ибо to ведь / потому что / так как at Literal, and
  до сего дня to до сих пор / по сей день; (b) keep до сего дня at Literal as
  a fixed formula but remove ибо; (c) leave Literal as it is.
- **If changed.** Under (a), about 140 records; under (b), the 84 records
  with ибо.

### 3.6 племя: "tribe" at Readable and "peoples"

- **Question.** Can племя stand for both "tribe" (Readable) and "peoples"
  (every level, 3.1)?
- **Now.** Tribe is колено at Literal and Balanced and племя at Readable (as
  Hebrews). Readable has племя for "tribe" in **387** records (Numbers 102,
  Joshua 101, 1 Chronicles 45, ...), while племена for "the peoples" is in 94
  records at Literal, 84 at Balanced and 15 at Readable. The terms file asks
  for a decision wherever both stand in one passage; no Readable sentence has
  both now, but a reader meets both senses of племя in the same books.
- **Alternatives.** (a) As now; (b) колено at every level for "tribe";
  (c) another word for "the peoples" (3.1 (c)).
- **If changed.** Under (b), about 390 Readable records.

### 3.7 "All flesh"

- **Question.** One form for *kol basar*?
- **Now.** `docs/russian-terms.md`: "'All flesh' has a settled Hindi form but
  none yet in Russian: follow the English level and record the choice in the
  first book that needs it." Of the **41** records whose English Literal has
  "all flesh", Literal has всякая плоть in 37 (всяким живым 2, всего живого 1);
  Balanced varies (все люди 9, всякое [живое] существо 7, всё живое 2, ...);
  Readable mostly follows the English (люди, все живые существа).
- **Alternatives.** Literal всякая плоть, Balanced все люди where people are
  meant and всё живое where animals are included (Genesis 6-9), Readable as
  the English; or one Balanced form throughout.
- **If changed.** Up to 41 records; record the rule in the terms file.

### 3.8 Isaiah 7:14: девушка

- **Question.** Confirm девушка for *ʿalmah*.
- **Now.** девушка at every level (1 record), with a footnoted decision naming
  Matthew 1:23's дева, which quotes the Greek Old Testament's *parthenos*. The
  meaning decision is "the young woman", and a rendering may not narrow it.
  Alternatives recorded: молодая женщина, дева.
- **If changed.** One record, but expect readers to ask about it: дева here
  would narrow the meaning decision, which is the scholar reviewers' to
  change, not the Russian's.

### 3.9 Zechariah 9:9: the address and the king's pronoun

- **Question.** Confirm the address in a line Matthew 21:5 and John 12:15
  quote.
- **Now.** Zechariah 9:9 says ты to daughter Zion at Literal and Balanced
  ("Вот, царь твой идёт к тебе") and вы to the people at Readable ("Смотрите!
  Ваш царь идёт к вам", жители Сиона), as Matthew 21:5 does (жители
  Иерусалима at R); its decision keeps Matthew's кроткий. Two differences
  remain: Matthew 21:5 Balanced puts a `deity_pronoun` span on the king's
  "Он", which Zechariah does not (its decision: the setting is kept for God);
  and Readable names Zion in Zechariah, Jerusalem in Matthew, each as its
  English.
- **Alternatives.** Readable ты to daughter Zion as at L and B; the span in
  Matthew removed or added in Zechariah.
- **If changed.** 1-3 records.

## 4. Decisions marked uncertain

The drafters marked **521** Russian rendering decisions uncertain, in 50
books. The table gives the count for each book and its first two, in Bible
order. The largest groups are 1 Kings (60), Psalms (59), 2 Samuel (40),
Matthew (36), Jeremiah (32) and Isaiah (29). Many are name forms and word
choices for plants, animals and objects whose identity is uncertain;
settling section 3 first will answer some of them.

The full list, every decision with a link to its verse, its levels, category,
choice and reason, is [`docs/review-notes/ru-uncertain.md`](review-notes/ru-uncertain.md),
regenerated with

    python3 scripts/review_checklist.py ru --write

and the admin's **Uncertain decisions** page (layer "Russian") lists the same
decisions with a link to each in the verse inspector.

| Book | Uncertain | Reference | Choice | Reason (excerpt) |
|---|---:|---|---|---|
| Genesis | 27 | Genesis 4:18 | "Мафусаил" for Methushael, kept apart from "Мафусал" (Methuselah, … | The two names differ in Hebrew, and the traditional Russian form "Мафусал" has been used for both. |
|  |  | Genesis 13:18 | "дубы Мамре" for the great trees | The Hebrew names a large tree, oak or terebinth … |
| Exodus | 14 | Exodus 25:5 | "тонкая кожа" | The animal or material is uncertain (m1), so, as the English, every level names only a fine leather and does not choose between the suggested animals. |
|  |  | Exodus 26:15 | "рамы" | The word may mean open frameworks or solid boards (m1) … |
| Leviticus | 10 | Leviticus 3:4 | "придаток на печени" (L, B); "кусок, который покрывает печень" (R) | Probably the long lobe of the liver (m1). |
|  |  | Leviticus 4:22 | "вождь" | The word means a chief of a tribe or clan (m1). |
| Numbers | 12 | Numbers 5:19 | the priest's words (verses 19-22) in « » inside “ ” inside « » | The priest's oath is a quotation inside the LORD's instructions to the people, inside the LORD's words to Moses. |
|  |  | Numbers 6:2 | "назорей", lower case | The traditional Russian word for the Nazirite (nazir), "one set apart" (m1). |
| Deuteronomy | 4 | Deuteronomy 4:48 | "гора Сиион, то есть Ермон", kept apart from "Сион" (Zion) | Siyon is another name for Hermon (m1), written in Hebrew with a different first letter from Zion. |
|  |  | Deuteronomy 7:20 | "шершень" | The meaning of the word is uncertain (m1) … |
| Joshua | 1 | Joshua 17:11 | три возвышенности (L) / три горные области (B, R) | The Hebrew phrase is unclear (meaning m3) … |
| Judges | 9 | Judges 3:8 | "Кушан-Ришатаим, царь Арам-Нахараима" | The traditional Russian form "Хусарсафем" is far from the Hebrew name, so the name is transcribed from the Hebrew … |
|  |  | Judges 5:2 | "распустились кудри" (L); "воины распустили волосы" (B); "воины не … | The Hebrew is read as hair hanging loose, the uncut hair of men who had given themselves to the LORD's war (m1). |
| Ruth | 1 | Ruth 3:10 | "неизменная любовь" (Literal); "милость" (Balanced, Readable) | This is Ruth's hesed, shown by one person to others … |
| 1 Samuel | 8 | 1 Samuel 5:6 | "опухоли" | The kind of swelling is not known for certain (m3) … |
|  |  | 1 Samuel 6:4 | "мыши" | 'Akhbar names small rodents of the mouse and rat kind (m3). |
| 2 Samuel | 40 | 2 Samuel 2:9 | "ашуряне" | The people is otherwise unknown (meaning m1) … |
|  |  | 2 Samuel 2:29 | "Арава" (Literal, Balanced); "Иорданская долина" (Readable); "Битрон" | The Arabah is the Jordan rift valley (meaning m1) … |
| 1 Kings | 60 | 1 Kings 1:8 | "Рисий" | Traditional Russian Bible form of the name Rei … |
|  |  | 1 Kings 2:37 | "знай твёрдо, что непременно умрёшь" (L) | The Hebrew doubles each verb for emphasis (meaning m2) … |
| 2 Kings | 7 | 2 Kings 15:29 | Тиглатпаласар | The traditional Russian Bible form "Феглаффелассар" comes through the Greek and is now hard to recognise … |
|  |  | 2 Kings 22:14 | Хулда | The traditional Russian Bible form "Олдама" comes through the Greek and is hard to recognise … |
| 1 Chronicles | 4 | 1 Chronicles 16:6 | "Яхазиил" for Jahaziel | The name is transcribed from the Hebrew … |
|  |  | 1 Chronicles 20:7 | "Шимея" | Chronicles spells the name of David's brother as in 1 Chronicles 2:13, where this translation has "Шимея" … |
| 2 Chronicles | 14 | 2 Chronicles 2:2 | "Хурам" | Chronicles spells the king's name Huram, and the English keeps it apart from the Hiram of Kings (m1) … |
|  |  | 2 Chronicles 2:12 | "Хурам-Ави", indeclinable | Taken as a name, as the English does (m1), in the Hebrew form of Chronicles … |
| Ezra | 6 | Ezra 4:9 | "динеи, афарсафхеи, тарпелеи, афарсеи, дегавеи"; "эрехцы, сузцы" (L), … | The uncertain names (meaning decision m2) are transcribed as peoples … |
|  |  | Ezra 5:6 | "афарсехеи" (L); "чиновники" (B, R) | The Persian word is of uncertain meaning (meaning decision m1): Literal transcribes it, Balanced and Readable give the likely sense, officials. |
| Nehemiah | 4 | Nehemiah 3:15 | "пруд Шелах" | Russian keeps the Hebrew name as the English does … |
|  |  | Nehemiah 3:31 | "ворота Смотра" at every level | The English uses two words for the gate's name (Muster, Inspection) … |
| Esther | 2 | Esther 1:10 | the courtiers' names in their traditional Russian forms ("Мегуман", … | Minor names follow the traditional Russian Bible spelling, as elsewhere in this translation, where th is written ф. |
|  |  | Esther 9:7 | Haman's sons in their traditional Russian forms ("Паршандафа", … | As with the courtiers of chapter 1, the minor names follow the traditional Russian Bible spelling, with th written ф. |
| Job | 3 | Job 19:25 | "Искупитель", with a capital as the English level has it | The go'el is the next of kin who buys back and stands up for a family member (m1) … |
|  |  | Job 22:29 | the readings of the English levels | The verse is hard (m1) … |
| Psalms | 59 | Psalms 6:1 | шеминит (L, B), as 1 Chronicles 15:21; по «восьмой» (R) | The word means "the eighth", a musical direction whose exact sense is lost (m3). |
|  |  | Psalms 8:1 | на гиттите (L, B); на «гиттите» (R) | Gittith is an instrument or a tune, perhaps from Gath (m3) … |
| Proverbs | 14 | Proverbs 18:24 | "может погибнуть" | The verb may mean to be broken or to show friendship (m1) … |
|  |  | Proverbs 19:7 | the third line as the English reads it | The last line is obscure in the Hebrew (m1) … |
| Ecclesiastes | 3 | Ecclesiastes 3:11 | вечность (L); чувство вечности (B); тоска по вечному (R) | The book's settled wording for 'olam here: a sense of time beyond the present, of the whole that people cannot see (m2). |
|  |  | Ecclesiastes 5:5 | храмовому вестнику | The messenger is probably the priest or temple official who dealt with vows (m1) … |
| Song of Songs | 19 | Song of Songs 1:17 | "кипарисы" | The tree is not certainly known (a cypress or a juniper) … |
|  |  | Song of Songs 2:1 | "крокус" | The flower is not certainly known (m2): a crocus, a narcissus or an asphodel of the meadows. |
| Isaiah | 29 | Isaiah 1:24 | "Сильный Израиля" for the Mighty One of Israel | Built like "Святой Израиля", Isaiah's other title for God, with the modern genitive. |
|  |  | Isaiah 4:2 | "росток ГОСПОДА", lowercase | The word (tsemach) is a sprout or new growth. |
| Jeremiah | 32 | Jeremiah 37:12 | свою долю в имуществе (B); свою долю семейной земли (R) | The Hebrew has only the verb "to receive a share" … |
|  |  | Jeremiah 37:16 | дом водоёма, подземелья (L); подземный водоём, сводчатые камеры (B); … | An underground pit used as a cell (meaning m2), with arched cells probably inside it (meaning m3). |
| Lamentations | 6 | Lamentations 1:1 | feminine pronouns for the city: "Она стала как вдова"; Zion speaks of … | The Hebrew pictures the city as a woman: a widow, a princess, a mother with lovers and children (m4). |
|  |  | Lamentations 1:8 | "согрешила она, Иерусалим" | "Иерусалим" is masculine, and a masculine verb here would turn the woman of the verse (her nakedness, her groaning, m4) into a man. |
| Ezekiel | 1 | Ezekiel 47:16 | Емаф; Берофа; Сивраим; Гацер-Тихон; Хавран | Hamath standing alone is Емаф, as Kings, Isaiah and Jeremiah in Russian … |
| Daniel | 3 | Daniel 7:18 | святые Всевышнего (L, B); Божий святой народ (R) | The table for Daniel has "the holy ones of the Most High" at Literal and Balanced and "God's holy people" at Readable, through verse 27. |
|  |  | Daniel 8:12 | преступление (L); бунт (B); грех (R) | The Pentateuch note gives "преступление" for transgression … |
| Joel | 2 | Joel 1:4 | грызущая, налетающая, прыгающая, пожирающая саранча (L, B); одна стая … | The four Hebrew names (gazam, arbeh, yeleq, chasil) are kept apart by an adjective each, all with "саранча", because the meaning decision leaves open … |
|  |  | Joel 1:17 | Истлели зёрна под своими глыбами (L); Зёрна сморщились под комьями … | Three rare words make the line uncertain (meaning decision) … |
| Amos | 4 | Amos 1:3 | За три преступления X и за четыре не отвращу его (L); За три … | The refrain of Amos 1-2 keeps one wording per level in all eight oracles. |
|  |  | Amos 2:13 | шататься (L); качаться (B); трястись (R) | The rare verb is read as the ground tottering under Israel, like an overloaded cart (meaning decision) … |
| Zechariah | 3 | Zechariah 14:6 | застынут (L); померкнут (B); погаснут (R) | A very uncertain text (m1) … |
|  |  | Zechariah 14:18 | [прольётся дождь] (L); у них тоже не будет дождя (B, R) | A hard text (m1): the Hebrew says only "and not on them" … |
| Matthew | 36 | Matthew 1:20 | 'ангел Господа' | The genitive is the plain modern form … |
|  |  | Matthew 2:22 | 'Назорей' | The traditional form keeps the possible play on a prophetic word that the meaning note mentions … |
| Mark | 13 | Mark 5:20 | "Десятиградие" | The traditional Russian name already means "the Ten Towns", so Readable needs only to add that there were ten cities. |
|  |  | Mark 5:36 | "услышав" (L); "не обратив внимания" (B); both (R) | The Greek verb can mean to overhear or to ignore. |
| Luke | 13 | Luke 1:5 | 'Елизавета' | Elizabeth takes the modern Russian spelling of the name rather than the Synodal 'Елисавета' … |
|  |  | Luke 1:30 | 'благодать' at every level | Grace is a key term that the style guide keeps as the same word at every level, so Russian does not follow the English 'favor' and 'pleased'. |
| John | 2 | John 12:10 | "уходили от них" (B, R) | As in English, Balanced and Readable say whom the people were leaving: the authorities (meaning decision m1). |
|  |  | John 16:7 | "истину" (L, B); "вот правда" (R) | This is not the "amen" formula, so Readable does not use its fixed wording "Говорю вам правду" … |
| Acts | 7 | Acts 9:13 | "святые" (L, B), "святой народ" (R) | "Святые" is the living Russian word for the believers as the Lord's own people … |
|  |  | Acts 10:44 | "сошёл" for "fell" | Russian does not say that the Spirit "fell" … |
| Romans | 3 | Romans 8:15 | усыновление, with no gender span | Key term: huiothesia is "усыновление" at every level. |
|  |  | Romans 11:11 | проступок | Paraptoma is a false step, a wrong (meaning decision m2), "проступок" at Literal and Balanced as in 4:25 and 5:15-20 … |
| 1 Corinthians | 9 | 1 Corinthians 9:21 | беззаконные, подзаконный (L); не имеющие Закона, живу по закону (B, R) | Literal keeps the Greek's word play with Russian compounds. |
|  |  | 1 Corinthians 11:3 | глава (verse 3, all levels; verses 4-10 at Literal); голова (verses … | Greek has one word for the leader and for the head on the body, and verses 4-5 play on both (meaning decision m2 there). |
| 2 Corinthians | 5 | 2 Corinthians 4:13 | Дух, capitalised | The capital follows the reading chosen in m2, as in the English … |
|  |  | 2 Corinthians 5:2 | нагими, без тела | Readable says what nakedness stands for, following m5, as the English does … |
| Colossians | 1 | Colossians 4:10 | Иисус, называемый Иустом | The traditional Russian form of the name, as in Acts 1:23 and 18:7 ("Иуст"). |
| 1 Thessalonians | 2 | 1 Thessalonians 2:14 | иудеев в Иудее (B); те иудеи в Иудее, которые были против верующих (R) | As in the English: the reading of m3 is that Paul means those in Judea who persecuted the churches there, not the Jewish people as a whole. |
|  |  | 1 Thessalonians 4:3 | сосудом (L); телом (B, R) | Literal keeps the uncertain picture word "vessel" … |
| 2 Thessalonians | 1 | 2 Thessalonians 2:3 | храм Божий, lowercase | The style guide capitalises "Храм" for the Temple in Jerusalem. |
| 1 Timothy | 3 | 1 Timothy 2:12 | властвовать (L, B); иметь власть (R) | As in the English, the most common sense of the verb (m1), which is uncertain. |
|  |  | 1 Timothy 3:2 | мужем одной жены (L); верным своей единственной жене (B); у него … | As in the English: Literal keeps the Greek wording, Balanced states the sense chosen (m2), Readable keeps close to the Greek and leaves the question … |
| Titus | 2 | Titus 2:7 | Во всём, with verse 7 | "In all things" may belong with verse 6 or verse 7 (m1) … |
|  |  | Titus 3:13 | законник | Luke settles "законник" (L) and "знаток Закона" (B, R) for experts in the Jewish Law … |
| Philemon | 1 | Philemon 1:4 | общение (L); щедрость (B) | As in the English: Literal keeps "koinōnia" as "общение", Balanced states the sense chosen in m3, which is uncertain. |
| Hebrews | 3 | Hebrews 2:9 | без Бога (L); оставленный Богом (B); без Божьей помощи (R) | The text followed reads "apart from God" (m1), not the reading behind the Synodal "по благодати Божией" … |
|  |  | Hebrews 6:17 | прибегшие [к нему] (L); нашедшие в нём убежище (B); прибежавшие к … | The Greek verb has no object … |
| 1 John | 7 | 1 John 1:1 | "о слове жизни" (lowercase) | As in the English, the word is the message about the life (meaning decision m4). |
|  |  | 1 John 2:6 | "Тот" | Literal keeps the demonstrative "that one", which in this letter means Jesus (meaning decision m2) … |
| 2 John | 1 | 2 John 1:1 | "старейшина" | The word settled in Acts for church elders. |
| 3 John | 1 | 3 John 1:12 | "Димитрий" | The traditional Russian form of the name, as in Acts 19:24. |
| Jude | 7 | Jude 1:2 | "да умножатся" | The wish form of the Greek verb … |
|  |  | Jude 1:5 | "не сохранивших ... хранит" (L); "не остались ... держит" (B, R) | Literal keeps the play on the same verb (meaning decision m7) … |
| Revelation | 3 | Revelation 1:9 | "потому что возвещал" (R) | Readable gives the cause the grammar decision takes as most likely, as the English does: John was there because of his witness. |
|  |  | Revelation 1:12 | "подобный Сыну Человеческому", with capitals, at every level | Russian writes the phrase as the title used in the Gospels ("Сын Человеческий"), which is how Russian readers know Daniel 7:13 and how the Gospels in … |

## 5. Most-read passages to review first

These are read and memorised most, and memory of the Synodal pulls hardest on
them: check that the wording is right, natural and our own. Open each in the
admin's Review queue with the book filter. Records are sentences; the last
column counts the Russian decisions marked uncertain in the passage.

| Passage | Records | Uncertain (ru) |
|---|---:|---:|
| Genesis 1-3 | 80 | 0 |
| Exodus 20 | 26 | 0 |
| Psalm 23 | 6 | 0 |
| Psalm 51 | 21 | 0 |
| Psalm 91 | 16 | 0 |
| Isaiah 9 | 20 | 0 |
| Isaiah 40 | 31 | 0 |
| Isaiah 53 | 12 | 0 |
| Jeremiah 31 | 40 | 0 |
| Micah 5 | 14 | 0 |
| Matthew 5-7 | 118 | 2 |
| Luke 2 | 42 | 1 |
| John 1 | 60 | 0 |
| John 3 | 38 | 0 |
| Romans 8 | 39 | 1 |
| 1 Corinthians 13 | 12 | 0 |
| Revelation 21-22 | 51 | 0 |
| **All 17 passages** | **626** | **4** |

Micah 5 here is the Hebrew chapter (English 5:2 is 5:1); Isaiah 9 starts at
English 9:2; Psalm 51 counts its two title verses. In the New Testament the
Russian decisions marked uncertain in these passages are few: Блаженны /
Счастливы (Matthew 5:3), насущный (Matthew 6:11), one in Luke 2 and one in
Romans 8.

## 6. The files and scripts

- `docs/russian-style.md`: how the Russian is drafted (levels, address,
  spelling, settings, the New Testament's words, Matthew's conventions).
- `docs/russian-terms.md`: the Old Testament's terms, formulas, names, parallel
  passages and quotations. Section 3 of this guide changes it.
- `docs/review-notes/ru-uncertain.md`: every uncertain Russian decision,
  generated by `python3 scripts/review_checklist.py ru --write`.
- `docs/review-notes/name-spellings.md`: names spelled more than one way,
  every language (`python3 scripts/name_spellings.py --lang ru`).
- The counts in section 3 and the tables in sections 4 and 5 were made with
  one-off scripts kept outside the repository (in the drafting session's
  scratch folder `review-fix/`: `owbdata.py` loads every record with its
  Strong's numbers from `data/hbo/` and `data/grc/`, `run*.py` hold the
  queries, `names.py` the name forms, `uncertain_table.py ru 2` the table
  of section 4 and `passages.py` the table of section 5). Each count is a plain text search over the Russian
  renderings, restricted to the records whose source holds the Hebrew or
  Greek word where that matters; rerun the same search after a change.
- `content/<BOOK>/*.json`: the records. Reviewers do not need to edit them:
  the admin is the review tool.
