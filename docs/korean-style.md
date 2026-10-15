# Korean style guide

How Open Word Bible drafts Korean. It sits on top of `docs/english-style.md`,
which still governs everything that is not about wording (sources, one record
per sentence, the three levels, decisions, status), and of
`docs/john-terms.md`, whose book-wide choices for John hold in Korean unless
this file says otherwise. Where this file and the founder's Translation
Charter disagree, the Charter wins; fix this file.

**Status: proposed, awaiting a native Korean reviewer.** Every Korean record
is `ai_draft`. The level names, the grammar labels in `owb/morph.py`, the
speech levels and the key terms below are first proposals, and a reviewer is
expected to change some of them.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Korean says that meaning in its own
  way.
- **Never reproduce the wording of a copyrighted Korean Bible**: 개역개정,
  새번역, 공동번역 개정판, 쉬운성경, 우리말성경, 현대인의성경, 새한글성경,
  가톨릭 성경 and others. 개역한글 (1961) shapes how most Korean readers
  remember familiar verses; its archaic endings (-니라, -노니, -지어다) are
  also out of place in a modern translation. Draft from the Greek and the
  gloss, then rewrite any sentence that matches a well-known version for more
  than a short common phrase.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied
  from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"ko": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, in
  every Korean level. **(checked)** Korean word order often moves a clause
  across a verse boundary; keep each verse's own content after its marker,
  restructuring the sentence if needed, and where that is impossible say so
  in a rendering decision.
- The meaning decisions are shared: do not change them. Korean needs only its
  own rendering decisions, with ids `r-ko-1`, `r-ko-2`, ... counted from 1 in
  each record, `"layer": "rendering"`, `"language": "ko"`, the `levels` they
  apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the Spanish and Swahili ones; the Korean words under discussion are quoted
  in it ("\"말씀\" rather than \"로고스\""). The site tells Korean readers
  that notes are in English for now.
- Write a Korean rendering decision where Korean had to choose and a reader
  might ask why: a word chosen against a familiar alternative, a speech level,
  a structure Korean cannot copy, a setting span that differs from the
  English one, a term settled here for the whole book (once, where it first
  appears in a passage). Do not repeat the English rendering decisions.
  Typical density: zero to two per sentence.

## 3. The three levels in Korean

The level names on the site are **직역** (Literal), **균형** (Balanced) and
**쉬운 말** (Readable).

**Literal (OWB-L).** Keeps the Greek's words, their grammar (participles,
genitives, the order of clauses where Korean allows) and its repetitions.
Korean is verb-final, so the Greek word order cannot be followed; Literal
keeps the Greek's units and their sequence of clauses instead. Words Korean
needs but the Greek lacks go in [square brackets]. Particles, endings and the
honorific *-시-* are grammar, not added words, and are not bracketed. Keep
the historic present (말한다, 말씀하신다) where the Greek has it.

**Balanced (OWB-B).** Careful standard modern Korean (표준어), the register of
a good public reading. Tracks the Greek closely; no brackets.

**Readable (OWB-R).** Plain Korean for new and young readers: short
sentences, common words, native Korean words over Sino-Korean ones where both
are current. Explains idioms and may make explicit what the context implies,
as the English Readable does, with a decision where the English has one.

## 4. Speech levels and honorifics

Korean must choose a speech level for every sentence; the choices below hold
through the book so a scene does not change relationship between verses.

- **Narrative**: the plain written style (해라체: -었다, -였다), with the
  subject honorific for God and Jesus at every level (예수께서 말씀하셨다,
  하나님께서 보내셨다). Others take no honorific (요한이 말했다).
- **Jesus speaking** to disciples, crowds and opponents: 해라체 (-다, -느냐,
  -라). Readable may soften to 해라체 with plainer words, not to 해요체.
- **People speaking to Jesus**: 합쇼체 (-습니다, -십니까, -십시오), from
  disciples, petitioners and officials alike. Open opponents may speak to him
  without honorifics (-느냐) where the scene is hostile, with a decision.
- **Jesus to the Father** (John 17): 합쇼체 (아버지, 때가 되었습니다).
- **Ordinary people among themselves**: as the scene requires; the default is
  해라체 between equals and 합쇼체 to superiors.

## 5. Spelling, names and typography

- Standard Korean spelling and spacing (한글 맞춤법, 띄어쓰기). Text is
  Hangul only: no Chinese characters, no Latin letters.
- Quotation marks as in English: “ ” outside, ‘ ’ for a quotation inside a
  quotation. Store them straight in `content/`, as the English does. Korean
  punctuation is otherwise the same as English (. , ? !).
- Proper names in their established Protestant forms: 예수, 요한, 시몬 베드로,
  안드레, 빌립, 나다나엘, 모세, 엘리야, 이사야, 예루살렘, 갈릴리, 가나,
  가버나움, 베다니, 나사로, 마르다, 마리아, 막달라 마리아, 가룟 유다, 도마,
  디두모, 빌라도, 가야바, 안나스, 사마리아, 야곱, 아브라함, 니고데모, 요셉,
  베들레헴, 실로암, 기드론, 바라바, 골고다, 디베랴, 말고, 세베대, 글로바,
  벳새다, 애논, 살렘, 수가, 베데스다, 에브라임, 가바다, 가이사, 솔로몬, 유대,
  요단, 다윗; peoples: 유대인, 바리새파 사람들, 레위인, 사마리아 사람,
  그리스 사람, 로마 사람.
- Numbers in Korean words in running text where short (다섯 사람); measures
  and large numbers in figures.
- Clock time: Literal keeps the Greek count ("열째 시쯤"); Balanced and
  Readable give the modern time ("오후 네 시쯤"), as the English does.

## 6. Words for the whole of John

| Greek (English) | Korean | Notes |
|---|---|---|
| God | 하나님 | Every level. *하느님* is the Catholic and Common Translation word; a reviewer may prefer it. Recorded as uncertain in 1:1. |
| the Word | **말씀** | Every level; as a person it takes the honorific (말씀이 계셨다). |
| grace | 은혜 | Key term: the same word at every level. |
| truth | 진리 | Key term. *참* for the adjective ("참 빛"); *사실* for a plain fact. |
| glory; glorify | 영광; 영광스럽게 하다 | Key term. |
| peace | 평안 | Key term (14:27; 16:33; 20:19-26). |
| righteousness | 의 | Key term. |
| believe | 믿다 | Keep the verb at every level. |
| life (*zōē*) | 생명 | |
| eternal life | 영원한 생명 | Every level; *영생* is the familiar contraction and may be noted. |
| light, darkness | 빛, 어둠 | |
| the world | 세상 | |
| sign | 표적 | Never 기적 (miracle). |
| testify, testimony, witness | 증언하다, 증언, 증인 | |
| the Jews | 유대인들 (L); 유대 지도자들 (B, R) where the authorities are meant | As `docs/john-terms.md`. |
| Truly, truly | 진실로 진실로 너희에게 말한다 (L, B); 내가 분명히 말한다 (R) | One decision per passage. |
| Son of Man | 인자 | A title, every level; Readable may add "사람의 아들" once per passage with a decision. Never under the gender setting. |
| Lamb of God | 하나님의 어린양 | |
| Rabbi | 랍비 | As an address, 랍비님 at Balanced and Readable. |
| Messiah | 메시아 | Plainly, no setting, at 1:41 and 4:25. |
| Christ | `{{christos:그리스도\|메시아}}` | With the name: `예수 {{christos:그리스도\|메시아}}`. |
| Holy Spirit; the Spirit | 성령 | 영 where it is not the Holy Spirit (4:24 "하나님은 영이시다"). |
| Advocate (*paraklētos*) | 변호자 | Every level; a footnote gives 보혜사, 위로자, 돕는 분. |
| disciples | 제자들 | Every level. |
| slave (*doulos*) | 종 | Every level; 노예 where slavery itself is the point. |
| Lord / Sir (*kyrie*) | 주님 / 선생님 | As `docs/john-terms.md`. |
| Woman (2:4; 19:26) | 여자여 (L); 어머니 (B, R) where it is his mother | Needs a decision where it first appears. Elsewhere 여자여 (L), 여인이여 or a respectful address (B, R). |
| temple (*hieron*; *naos*) | 성전 (L), 성전 뜰 (B, R); 성전 | As `docs/john-terms.md`. |
| "I am" (*egō eimi* with no predicate) | 내가 나임을 (8:24, 8:28, 13:19); 나는 있다 (8:58); 나다 (6:20) | Uncertain. |
| remain, stay | 머무르다 | Every sense, so 1:38-39 and 15:4-10 stay linked. |
| life (*psychē*) | 목숨 | 생명 stays for *zōē*. |
| prophet; the Prophet | 예언자; 그 예언자 | 선지자 is the older Protestant word, the alternative. |
| bread | 빵 | Never 떡. |
| hour | 때 | Every level, Jesus's appointed hour included. |
| only (*monogenēs*) | 하나뿐인 / 유일한 | Not 독생자. |
| Passover; Sabbath; synagogue | 유월절; 안식일; 회당 | |
| chief priests; council | 대제사장들; 공의회 | |
| devil | 마귀 | |
| the disciple whom Jesus loved | 예수께서 사랑하시는 제자 | |

## 7. Reader settings in Korean

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: Korean has no capital letters, so the setting has nothing
  to change and the Korean text has **no** deity_pronoun spans. Respect for
  God and Jesus is carried by the honorific *-시-*, 께서 and 그분, at every
  level. The first record of a passage says so once where the English has a
  span.
- `christos`: `{{christos:그리스도|메시아}}`, and
  `예수 {{christos:그리스도|메시아}}`.
- `gender`: Korean nouns for people are already inclusive (사람, 누구든지,
  자녀), and Korean rarely uses a pronoun where English says "he". Use a span
  only where Korean really has two ways of saying the same thing:
  `{{gender:형제자매|형제}}` for *adelphoi* meaning believers.
- `units`: metric by default, the original unit as the alternative, as in
  French and Swahili: `{{units:3킬로미터|십오 스타디온}}`. Literal keeps the
  original unit. This differs from the English (US units) and needs a
  rendering decision.

## 8. Status

A Korean rendering added to a record does not change its status. Nothing is
marked reviewed by an AI.
