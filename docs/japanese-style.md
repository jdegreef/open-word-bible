# Japanese style guide

How Open Word Bible drafts Japanese (日本語). It builds on
`docs/english-style.md`, which still covers everything that is not about
wording: sources, one record per sentence, the three levels, decisions and
status. It also builds on each book's terms notes (`docs/john-terms.md` and
the others). Their book-wide choices hold in Japanese unless this file says
otherwise. Where this file and the founder's Translation Charter disagree,
the Charter wins; fix this file.

**Status: proposed, awaiting a native Japanese reviewer.** Every Japanese
record is `ai_draft`. The level names, the grammar labels in
`owb/morph.py`, the register and honorific rules, the name forms and the key
terms below are first proposals, and a reviewer is expected to change some
of them.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Japanese says that meaning in its own
  way.
- **Never reproduce the wording of a copyrighted Japanese Bible**: 新共同訳
  (1987), 聖書協会共同訳 (2018), 新改訳 (1970–2017), フランシスコ会訳, 新世界訳,
  リビングバイブル, 現代訳 and others. The 口語訳 (1954–55) and 文語訳 (明治元訳,
  大正改訳) shape how readers remember familiar verses, but do not copy them
  either: draft from the Greek and the gloss, then rewrite any sentence that
  matches a well-known version for more than a short common phrase. Shared
  vocabulary (神の国, 人の子, 悔い改め) and the conventional forms of names are
  not wording and may be used.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied
  from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"ja": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers in every Japanese level, in the order the
  English has them. **(checked)** Write the marker straight after the
  punctuation that ends the previous verse's words, with one space after the
  number and none before the backslash: `……知っているので、\v 3 あなたがたの信仰は`.
  Japanese puts the verb last, so a sentence running across verses often
  wants its parts in another order. Keep each verse's content after its own
  marker as far as Japanese allows (split the sentence at a 、 or make two
  sentences at Balanced and Readable); where content has to cross a verse
  boundary, say so in a `word_order` rendering decision.
- The meaning decisions are shared: do not change them. Japanese needs only
  its own rendering decisions, with ids `r-ja-1`, `r-ja-2`, ... counted from
  1 in each record, `"layer": "rendering"`, `"language": "ja"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions. Quote the Japanese words under discussion
  ("\"しもべ\" rather than \"奴隷\""). The site tells Japanese readers that notes
  are in English for now.
- Write a Japanese rendering decision where Japanese had to choose and a
  reader might ask why: a word chosen over a familiar church alternative; an
  honorific level; a verse boundary moved; a setting span that differs from
  the English one; or a term settled here for the whole book (note it once,
  where it first appears in a passage). Do not repeat the English rendering
  decisions. Typical density: zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language. So each Japanese level must open and close the same
  quotations, in the same order, as the English one: no quotation added,
  dropped, merged or split. A sentence that begins or ends inside a speech
  begins or ends inside it in Japanese too (an opening 「 with no 」, or a
  closing 」 with no 「). Speech broken by a verb of saying in English
  ("Lord," he said, "you...") takes two pairs in Japanese too:
  「主よ」と彼は言った。「あなたは……」.

## 3. The three levels in Japanese

The level names on the site are **逐語訳** (Literal), **標準訳** (Balanced)
and **平易訳** (Readable).

**Literal (逐語訳, OWB-L).** Keeps the Greek's words and their grammar as
far as Japanese can: participles as 〜して / 〜しながら clauses, genitives as
の, the Greek's repetitions (そして……そして……), its order of clauses where
Japanese allows. Words Japanese needs but the Greek lacks go in [square
brackets] (ASCII `[` `]`, as in every language). Keep the historic present
(言う, 来る) where the Greek has it. Literal may read stiffly; it must not be
wrong Japanese.

**Balanced (標準訳, OWB-B).** Careful standard modern written Japanese, the
register of a good public reading in church. Tracks the Greek closely; no
brackets. Church words stay where they are the living word for the thing
(恵み, 悔い改め, 神の国, 大祭司). Bungo (文語) forms (〜なり, 〜べし, 〜たまえ,
〜ぞ) are not used.

**Readable (平易訳, OWB-R).** Plain everyday Japanese for new and young
readers: short sentences, common words and kanji (Jōyō kanji only; write a
harder word in kana), everyday words over church ones where both are current
(税金を集める人 for 徴税人). Explains idioms and may make explicit what the
context implies, as the English Readable does, with a decision where the
English has one.

## 4. Register, honorifics and address

The Greek has no polite forms; Japanese must choose one. These choices are
wording, the same meaning in other clothes, so they are rendering decisions,
never meaning decisions.

- **Narrative** (the Gospels, Acts, the stories in Revelation): narration in
  the plain style (だ・である体, past 〜た) at Literal and Balanced; Readable
  narrates in です・ます体. Do not mix styles inside one level of a book.
- **Letters** (Romans to Jude) are a writer speaking to readers: です・ます体 at
  every level, with commands as 〜なさい (L, B) or 〜してください (R). Quoted
  Scripture inside a letter keeps the plain style.
- **Honorifics for God and Jesus in narration.** The narrator uses light
  respect forms for what God and Jesus do: 言われた, 来られた, なさった, お答えに
  なった (L, B); Readable keeps 言われました, 来られました. Use the 〜れる/〜られる
  form or お〜になる, not heavy 謙譲語 or double honorifics, and not for anyone
  else (not for the disciples, the apostles or angels). This is one decision
  per book, where it first appears.
- **Pronouns.** Jesus and God speak of themselves as わたし (hiragana). People
  speaking to God or Jesus say あなた, or a title (主よ, 先生). Japanese leaves
  pronouns out where the sense is clear; do not add 彼 for Jesus or God where a
  name or nothing will do, and never use 彼 for God. You plural is あなたがた
  (L, B), あなたたち or みなさん (R). The writer of a letter speaks of himself as
  わたし and of "we" as わたしたち.
- **Speech among people.** Choose a natural register for each speaker and
  keep it through a scene: a servant to a master, a petitioner to Jesus and
  an accused man to a governor speak politely (です・ます); Jesus speaks to
  people in the plain style with authority (〜しなさい, 〜である), and to
  someone he comforts gently. Rulers and crowds speak plainly. Note a
  noticeable choice in a decision the first time in a passage.

## 5. Spelling, names and typography

- **Script.** Standard modern orthography (常用漢字 and 現代仮名遣い, 送り仮名
  as in the 送り仮名の付け方). Write in kana the words modern writing usually
  writes in kana (こと, もの, とき as a noun of time, ください, いる, ある, できる,
  ～ように, わたし, あなた). No furigana: the reader cannot show ruby, so choose
  words a reader can read at the level, more kana at Readable.
- **Punctuation.** Full-width 、 and 。; ？ and ！ only where the Greek asks or
  exclaims, followed by nothing at the end of a sentence (a full-width space is
  not used). Quotation marks are 「 」 outside, 『 』 for a quotation inside a
  quotation, and 「 」 again inside that. **The sentence ends with its 。
  inside the closing bracket** (「わたしに従いなさい。」), so the verse reads as
  a sentence on its own; a sentence that continues after the quotation has no
  。 inside it (「来なさい」と言われた。). The reader finds speech (the red
  letters, `owb/markup.py`) from these brackets. Do not use “ ” or " in
  Japanese renderings. The dash is ―― (two U+2015) or ……(two U+2026) for
  an ellipsis.
- **Numbers.** Kanji numerals in running text (十二人, 三日目, 五千人), as Bible
  readers expect; Arabic digits only in a measure the `units` setting gives
  in modern terms (約3キロメートル). Chapter and verse references in decisions
  stay in English form (1:2).
- **Spaces.** None between words. A space appears only after a verse number
  (`\v 3 `), and between the parts of a foreign name written with a middle dot
  (シモン・ペトロ).
- **Proper names** take the forms of modern ecumenical Japanese usage, which
  follow the Greek and Hebrew sounds more closely than the older forms (these
  are the conventional forms of names, not wording to be copied): イエス,
  マリア, ヨセフ, ヨハネ, 洗礼者ヨハネ, シモン・ペトロ, ペトロ, アンデレ, ヤコブ,
  ゼベダイ, フィリポ, バルトロマイ, トマス, マタイ, ナタナエル, ユダ・イスカリオテ,
  ニコデモ, ラザロ, マルタ, マグダラのマリア, ピラト, カイアファ, アンナス, バラバ,
  ヘロデ, モーセ, アブラハム, イサク, ヤコブ, エリヤ, イザヤ, ダビデ, ソロモン.
  Acts and the letters: パウロ, サウロ, バルナバ, ステファノ, フィリポ, シラス,
  テモテ, テトス, アポロ, プリスキラ, アキラ, コルネリウス, ガマリエル, フェリクス,
  フェストゥス, アグリッパ, フィベ, ティキコ. Places: エルサレム, ガリラヤ,
  ユダヤ, サマリア, ナザレ, ベツレヘム, カファルナウム, ベトサイダ, ベタニア,
  ヨルダン川, ローマ, アンティオキア, エフェソ, コリント, フィリピ, テサロニケ,
  アテネ, ダマスコ, カイサリア, キプロス, アレクサンドリア, アジア州, マケドニア州,
  アカイア州. Peoples: ユダヤ人, サマリア人, ギリシア人, ローマ人. A name not
  listed here: transliterate the Greek form by the same pattern and note it in
  a decision where it first appears in the book.
- **Clock time.** Literal keeps the Greek count (第六の時). Balanced and
  Readable give the time as a modern reader counts it (正午ごろ), with a
  decision.

## 6. Words for the whole of the New Testament

| Greek (English) | Japanese | Notes |
|---|---|---|
| God | 神 | Every level; 神々 / 神 for "a god" by context. |
| Lord (*kyrios*, of God or Jesus) | 主 | "Lord!" as an address: 主よ. "Sir" to a stranger: だんなさま / あなた by context. Masters in parables: 主人. |
| Jesus | イエス | イエスさま is not used. |
| Christ | `{{christos:キリスト\|メシア}}` | With the name: `イエス・{{christos:キリスト\|メシア}}`. メシア plainly, no setting, where the Greek has *Messias* (John 1:41; 4:25). |
| Holy Spirit; the Spirit | 聖霊; 霊 (御霊 is not used) | |
| kingdom of heaven; kingdom of God | 天の国; 神の国 | |
| Son of Man | 人の子 | A title, every level. Never under the gender setting. |
| Son of God; Son of David | 神の子; ダビデの子 | |
| disciple(s) | 弟子; 弟子たち | Every level. |
| apostle | 使徒 | |
| prophet | 預言者 | Never 予言者. |
| the Law; the Law and the Prophets | 律法; 律法と預言者 | |
| scribes | 律法学者 | |
| Pharisees; Sadducees | ファリサイ派の人々; サドカイ派の人々 | |
| chief priests; high priest | 祭司長たち; 大祭司 | |
| elders | 長老たち | |
| tax collectors; sinners | 徴税人 (L, B), 税金を集める人 (R); 罪人 (つみびと is a reading, write 罪人) | |
| Gentiles, nations | 異邦人 (L, B), ユダヤ人でない人々 (R); "the nations": 諸国の民 | |
| synagogue; temple | 会堂; 神殿 | |
| Sabbath; Passover | 安息日; 過越祭 | |
| church, assembly | 教会 | |
| repent; repentance | 悔い改める; 悔い改め | Readable may say 心を入れ替えて神に立ち返る with a decision. |
| sin | 罪 | |
| believe; faith | 信じる; 信仰 | Keep the verb 信じる at every level. |
| grace | 恵み | Key term: the same word at every level. |
| truth | 真理 | Key term. Readable may say 本当のこと where the sense is "what is true", with a decision. |
| glory; glorify | 栄光; 栄光を現す / あがめる | Key term. |
| peace | 平和 (between people, with God); 平安 (as a greeting and inner peace) | Key term; a decision where the choice is not obvious. |
| righteousness; righteous | 義; 正しい | Key term. Readable may say 神の前に正しいこと with a decision. |
| justify | 義とする (L, B); 正しい者と認める (R) | |
| gospel, good news | 福音 (L, B); 良い知らせ (R) | |
| baptize; John the Baptist | 洗礼を授ける; 洗礼者ヨハネ | |
| angel | 天使 | |
| demon; unclean spirit | 悪霊; 汚れた霊 | |
| devil; Satan | 悪魔; サタン | |
| heaven; Gehenna; Hades | 天; ゲヘナ (L, B), 地獄 (R); 陰府 (L, B), 死者の世界 (R) | |
| Truly I tell you (*amēn*) | アーメン、あなたがたに言う (L); まことに、あなたがたに言う (B); 本当のことを言おう (R) | In John doubled: アーメン、アーメン (L); まことに、まことに (B). One decision per passage. |
| crowd | 群衆 | |
| hypocrites | 偽善者 | |
| Woe to you | ああ、あなたがたは災いだ | |
| eternal life | 永遠の命 | |
| cross; crucify | 十字架; 十字架につける | |
| Amen; Hosanna | アーメン; ホサナ | |
| Rabbi; Teacher | ラビ; 先生 | |
| slave (*doulos*) | 奴隷 (L); しもべ (B, R) | As the English: Literal says slave, Balanced and Readable servant, except where slavery itself is the point (slave and free), where 奴隷 stays at every level. |
| deacon (*diakonos* as a church office: Romans 16:1; Philippians 1:1; 1 Timothy 3:8, 12) | 執事 | Every level. *diakonos* as a plain servant or minister (Christ in Romans 15:8, Paul of the gospel in Ephesians 3:7) is 仕える者 / 奉仕者, as the context asks. |
| flesh (Paul's moral sense) | 肉 (L, B); 罪に傾く人間の性質 (R) | With a decision where it first appears. |
| brothers (*adelphoi*, the believers) | `{{gender:きょうだいたち\|兄弟たち}}` | See section 7. |

## 7. Reader settings in Japanese

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: Japanese has no capital letters, so Japanese renderings
  have **no** `deity_pronoun` spans. Where the English has one, Japanese
  writes the pronoun (or leaves it out) plainly. The reader shows the setting
  only where a span exists, so nothing is lost.
- `christos`: `{{christos:キリスト|メシア}}` at every level. Where the English
  has `Jesus {{christos:Christ|the Messiah}}`, Japanese writes
  `イエス・{{christos:キリスト|メシア}}`. Check that both options read
  naturally with the particle after the span.
- `gender`: an inclusive default where the original means men and women,
  with the traditional Japanese as the alternative:
  `{{gender:きょうだいたち|兄弟たち}}` (the inclusive kana spelling),
  `{{gender:人々|男たち}}` where *andres* means people in general. Not for
  specific men, and not where Japanese is already inclusive (人, 人々, 者, 皆,
  だれ, 子どもたち). An address keeps its form inside the span:
  `{{gender:きょうだいたち|兄弟たち}}、`. A rendering decision
  (setting_alternative) records a difference from the English the first time
  it occurs in a passage.
- `units`: metric by default, the original unit as the alternative:
  `{{units:約3キロメートル|十五スタディオン}}`. Literal keeps the original unit.
  This differs from the English (US units) and needs a rendering decision the
  first time in a passage. Coins have no metric form: a `units` span gives
  the value in wages by default and the coin as the alternative
  (`{{units:一日分の賃金|一デナリオン}}`), as the English does. Literal keeps
  the coin.
- `plural_you` is Spanish only.
- A setting span holds no quotation brackets (`owb/markup.py` checks).

## 7a. Conventions settled in the first books

James and Ephesians were drafted first, in parallel chapters; these choices
hold for the later books.

- **Address.** わたしの{{gender:きょうだいたち|兄弟たち}}、 at the start of the
  sentence; "my beloved brothers" わたしの愛する{{gender:きょうだいたち|兄弟たち}}
  (L, B), 愛する{{gender:きょうだいたち|兄弟たち}} (R); a single brother
  `{{gender:きょうだい|兄弟}}`. Plural "you" to the readers: あなたがた (L, B),
  みなさん (R).
- **Gender spans the English needs and Japanese does not.** English pronoun
  spans (them/him, they/he) and spans on *anthrōpos* or *anēr* for people in
  general become その人, 自分, 人, 人々, or nothing, with no span; note it once
  in a passage (setting_alternative).
- **God's actions in a letter** take the same light respect forms as in
  narration (与えてくださる, 約束された, おできになる) at every level; quoted
  Scripture stays plain.
- **Commands** 〜なさい (L, B), 〜てください (R). *idou* 見なさい (L, B),
  見てください (R), not 見よ.
- **Words.** trials 試練, tempt 誘惑する; endurance (*hypomonē*) 忍耐, and
  patience (*makrothymia*) 辛抱 / 寛容, kept apart; double-minded 二心; blessed
  (*makarios*) 幸い (L, B); works 行い (L, B), 行動 (R); justify 義とされる (L, B),
  神に正しい者と認められる (R); mercy あわれみ (kana); world (*kosmos*) 世 (L, B),
  この世 (R); bless God ほめたたえる (L, B), 賛美する (R); curse 呪う; the
  assembly (*synagōgē*, James 2:2) 集会; elders 長老たち (L, B); heal 癒やす (L,
  B), いやす (R); forgive 赦す (L, B), ゆるす (R); *parousia* 来臨 (L, B), 主が来ら
  れる (R); Gehenna ゲヘナ (L, B), 地獄 (R).

## 7b. The Old Testament (settled before it is drafted)

- **The divine name** (YHWH) is `{{divine_name:主|ヤハウェ}}` at every level:
  主 by default, the usual form in Japanese Bibles, with the name itself as
  the reader setting, as the English has LORD / Yahweh. Particles go outside
  the span (`{{divine_name:主|ヤハウェ}}は`). *Adonai* ("Lord") is 主 with no
  span; *Elohim* is 神. エホバ is not used.
- **Lines.** Poetry is set in lines (`\q `), following the Hebrew accents'
  division of the verse (`scripts/poetry_lines.py`), at every level, as
  `docs/english-style.md` section 10 describes.

## 8. Status

A Japanese rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.

## 9. Section headings and summaries

Where a book's `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json`
has languages other than English, add `"ja"` beside them, written from Open
Word Bible's own Japanese wording. They are AI drafts until reviewed.

## 10. Search

Japanese is written without spaces, so site search indexes Japanese
sentences by character pairs (`backend/translation/search.py`, `ngrams`): a
word is found anywhere inside a clause, and a single kanji is found on its
own. The kana voicing marks count (ガリラヤ is not カリラヤ), and full-width
digits and letters in a query are read as ASCII (ヨハネによる福音書３：１６).
This does not affect drafting, but a word written in kanji in one place and
kana in another (御心 / みこころ) is two words to search: keep one spelling
through a book, as the conventions above do.
