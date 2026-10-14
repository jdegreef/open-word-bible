# Vietnamese style guide

How Open Word Bible drafts Vietnamese. It sits on top of
`docs/english-style.md`, which still governs everything that is not about
wording (sources, one record per sentence, the three levels, decisions,
status), and of `docs/john-terms.md`, whose book-wide choices for John hold
in Vietnamese unless this file says otherwise. Where this file and the
founder's Translation Charter disagree, the Charter wins; fix this file.

**Status: proposed, awaiting a native Vietnamese reviewer.** Every
Vietnamese record is `ai_draft`. The level names, the grammar labels in
`owb/morph.py`, the forms of address and the key terms below are first
proposals, and a reviewer is expected to change some of them. The biggest
open question is the tradition the names and key terms follow (section 4).

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Vietnamese says that meaning in its
  own way.
- **Never reproduce the wording of a copyrighted Vietnamese Bible**: Bản Dịch
  Mới (NVB), Bản Hiệu Đính Truyền Thống, Bản Phổ Thông, Bản Dịch 2011, Kinh
  Thánh Công Giáo (Nhóm Phiên Dịch CGKPV), Bản Dịch Đức Ông Nguyễn Văn Thích
  and others. The 1926 Bản Truyền Thống (Cadman) is in the public domain and
  shapes how most Protestant readers remember familiar verses; it is archaic,
  so drafts that drift toward it also drift out of modern Vietnamese. Draft
  from the Greek and the gloss, then rewrite any sentence that matches a
  well-known version for more than a short common phrase.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied
  from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"vi": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, in
  every Vietnamese level. **(checked)**
- The meaning decisions are shared: do not change them. Vietnamese needs only
  its own rendering decisions, with ids `r-vi-1`, `r-vi-2`, ... counted from 1
  in each record, `"layer": "rendering"`, `"language": "vi"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the Spanish and Swahili ones; the Vietnamese words under discussion are
  quoted in it ("\"Ngôi Lời\" rather than \"Lời\""). The site tells
  Vietnamese readers that notes are in English for now.
- Write a Vietnamese rendering decision where Vietnamese had to choose and a
  reader might ask why: a word chosen against a familiar alternative, a form
  of address, a structure Vietnamese cannot copy, a setting span that differs
  from the English one, a term settled here for the whole book (once, where
  it first appears in a passage). Do not repeat the English rendering
  decisions. Typical density: zero to two per sentence.

## 3. The three levels in Vietnamese

The level names on the site are **Sát nghĩa** (Literal), **Cân bằng**
(Balanced) and **Dễ đọc** (Readable).

**Literal (OWB-L).** Follows the Greek wording and, where Vietnamese allows,
its order. Words Vietnamese needs but the Greek lacks go in [square
brackets], as in English. Vietnamese has no articles or verb endings: the
English bracketed "[the]" has no counterpart, and the aspect words *đã*,
*đang*, *sẽ* are added only where the sense needs them, without brackets.
Respect words that Vietnamese grammar requires in a form of address (*Đức*,
*Ngài*, *thưa*) are not bracketed. Keep the historic present where the Greek
has it ("Ngài phán", "ông nói") by leaving out *đã*.

**Balanced (OWB-B).** Careful standard modern Vietnamese, the register of a
good public reading. Tracks the Greek closely; no brackets.

**Readable (OWB-R).** Plain Vietnamese for new and young readers: short
sentences, common words, few Sino-Vietnamese terms where a plain word will
do. Explains idioms and may make explicit what the context implies, as the
English Readable does, with a decision where the English has one.

## 4. Spelling, names and typography

- Standard modern Vietnamese spelling, with the tone mark placed as in
  current dictionaries ("hoà" and "hòa" are both seen: use **hòa**, **thủy**,
  **khỏe**, the placement most readers learned). Text is stored NFC.
- Quotation marks as in English: “ ” outside, ‘ ’ for a quotation inside a
  quotation. Store them straight in `content/`, as the English does.
- Proper names follow the Protestant tradition's transliterations, which most
  Vietnamese Bible readers online know and which the public-domain 1926
  version fixed: Giăng (John, both the Baptist and the apostle), Giê-xu,
  Si-môn Phi-e-rơ, Anh-rê, Phi-líp, Na-tha-na-ên, Môi-se, Ê-li, Ê-sai,
  Giê-ru-sa-lem, Ga-li-lê, Ca-na, Ca-bê-na-um, Bê-tha-ni, La-xa-rơ, Ma-thê,
  Ma-ri, Ma-ri Ma-đơ-len, Giu-đa Ích-ca-ri-ốt, Thô-ma, Đi-đim, Phi-lát,
  Cai-phe, An-ne, Sa-ma-ri, Gia-cốp, Áp-ra-ham, Ni-cô-đem, Giô-sép,
  Bết-lê-hem, Si-lô-ê, Xết-rôn, Ba-ra-ba, Gô-gô-tha, Ti-bê-ri-át, Man-chu,
  Xê-bê-đê, Cơ-lê-ô-pát, Bết-sai-đa, Ê-nôn, Sa-lim, Si-kha, Bê-tết-đa,
  Ép-ra-im, Ga-ba-tha, Sê-sa, Sa-lô-môn, Giu-đê, Giô-đanh, Đa-vít; peoples:
  người Do Thái, người Pha-ri-si, người Lê-vi, người Sa-ma-ri, người Hy Lạp,
  người La Mã. A Catholic reviewer may prefer Gio-an, Phê-rô, Đức Giê-su,
  Thiên Chúa; that is a book-wide change and is recorded as uncertain in
  John 1:1 and 1:6.
- Capitals: Đức Chúa Trời, Cha, Con, Đức Thánh Linh, Chúa (the Lord), Con
  Người, Chiên Con của Đức Chúa Trời, Kinh Thánh, Ngôi Lời. "luật pháp" (the
  Law) is lowercase, as "law" is in English.
- Numbers in words in running text ("năm người"); measures in figures.
- Clock time: Literal keeps the Greek count ("khoảng giờ thứ mười");
  Balanced and Readable give the modern time ("khoảng bốn giờ chiều"), as the
  English does.

## 5. Words for the whole of John

| Greek (English) | Vietnamese | Notes |
|---|---|---|
| God | Đức Chúa Trời | Every level. *Thiên Chúa* is the Catholic word; see section 4. |
| Jesus | Đức Giê-xu | Every level. A bare name for a revered person is disrespectful in Vietnamese, so the honorific *Đức* is not bracketed even at Literal; one decision in 1:17 says so. |
| the Word | **Ngôi Lời** | Every level. *Ngôi* marks a person, as John's Word is. |
| grace | ân điển | Key term: the same word at every level. |
| truth | chân lý | Key term. *thật* for the adjective ("ánh sáng thật"); *sự thật* for a plain fact. |
| glory; glorify | vinh quang; tôn vinh | Key term. |
| peace | bình an | Key term. |
| righteousness | sự công chính | Key term. |
| believe | tin; tin vào (*eis*) | Keep the verb at every level. |
| life (*zōē*) | sự sống | |
| eternal life | sự sống đời đời | Every level. |
| light, darkness | ánh sáng, bóng tối | |
| the world | thế gian | *thế giới* only for the physical world where the English says "the earth". |
| sign | dấu lạ | Never *phép lạ* (miracle). *dấu chỉ* is closer to "sign"; recorded as uncertain in 2:11 for a reviewer. |
| testify, testimony, witness | làm chứng, lời chứng, nhân chứng | |
| remain | ở lại; ở trong (15:4-10) | |
| the Jews | người Do Thái (L); các nhà lãnh đạo Do Thái (B, R) where the authorities are meant | As `docs/john-terms.md`. |
| Truly, truly | Thật vậy, thật vậy, Ta nói với... (L, B); Ta nói thật với... (R) | One decision per passage. |
| Son of Man | Con Người | A title; capitalised; never under the gender setting. |
| Lamb of God | Chiên Con của Đức Chúa Trời | |
| Rabbi | Ra-bi | |
| Messiah | Đấng Mê-si-a | Plainly, no setting, at 1:41 and 4:25. |
| Christ | `{{christos:Đấng Christ\|Đấng Mê-si-a}}` | With the name: `Đức Giê-xu {{christos:Christ\|Mê-si-a}}`. |
| Holy Spirit; the Spirit | Đức Thánh Linh; Thánh Linh | Lowercase *linh* or *thần linh* where it is not the Holy Spirit (4:24 "Đức Chúa Trời là thần linh"). |
| Advocate (*paraklētos*) | Đấng Biện Hộ | Every level; a footnote gives "Đấng Yên Ủi", "Đấng Trợ Giúp". |
| disciples | môn đồ | Every level. |
| slave (*doulos*) | nô lệ (L); đầy tớ (B, R) | As the English. |
| Lord / Sir (*kyrie*) | Chúa / thưa ông | As `docs/john-terms.md`: people who do not yet know him say *thưa ông*; disciples and believers say *Chúa*. |
| Woman (2:4; 19:26) | Thưa bà (L); Mẹ ơi / Thưa mẹ (B, R) where it is his mother | Needs a decision where it first appears. |
| temple (*hieron*; *naos*) | đền thờ (L), sân đền thờ (B, R); đền thờ | As `docs/john-terms.md`. |

## 6. Forms of address

Vietnamese has no neutral "I" and "you": the pronouns name the relation
between speaker and hearer. The choices below are kept through the book so
that a scene does not change relationship from verse to verse.

- **Narrator about Jesus and about God**: *Ngài*, with the setting
  (`{{deity_pronoun:ngài|Ngài}}`, see section 7).
- **Jesus speaking**: *Ta* for himself (`{{deity_pronoun:ta|Ta}}` in the
  middle of a sentence). To his disciples, *các con*; to crowds, opponents
  and officials, *các người*; to one person, *ông*, *bà*, *anh*, *chị*,
  *con* as age and relation require.
- **Disciples to Jesus**: *Thầy* ("Teacher", which is what *Rabbi* means),
  and *chúng con* for themselves. Others who respect him: *Thầy* or *ông*.
  Opponents speak of him as *ông ta* or *người này*.
- **Jesus to the Father**: *Cha*, and *Con* for himself (John 17).
- Ordinary people among themselves: *tôi*, *ông*, *bà*, *anh*, *chúng tôi*,
  *các ông* as the scene requires.

## 7. Reader settings in Vietnamese

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: `{{deity_pronoun:ngài|Ngài}}` for Jesus and God in the
  narrative, `{{deity_pronoun:ta|Ta}}` when Jesus speaks of himself. Only the
  capitalisation differs. **(checked)** A pronoun at the start of a sentence
  is written plainly with its capital. *Thầy*, *Cha* and *Con* are nouns of
  address, always capitalised, and take no span.
- `christos`: `{{christos:Đấng Christ|Đấng Mê-si-a}}`, and with the name,
  `Đức Giê-xu {{christos:Christ|Mê-si-a}}`.
- `gender`: Vietnamese nouns for people are already inclusive (*người*,
  *ai*, *mọi người*, *con cái*). Use a span only where Vietnamese really has
  two ways of saying the same thing: `{{gender:anh chị em|anh em}}` for
  *adelphoi* meaning believers.
- `units`: metric by default, the original unit as the alternative, as in
  French and Swahili: `{{units:3 km|mười lăm ếch-ta-đơ}}`. Literal keeps the
  original unit. This differs from the English (US units) and needs a
  rendering decision.

## 8. Status

A Vietnamese rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.
