# Persian style guide

How Open Word Bible drafts Persian (فارسی), in the standard written Persian
of Iran, which readers in Afghanistan (Dari) also read. It builds on
`docs/english-style.md`, which still covers everything that is not about
wording: sources, one record per sentence, the three levels, decisions and
status. It also builds on each book's terms notes (`docs/john-terms.md` and
the others): their book-wide choices hold in Persian unless this file says
otherwise. `docs/persian-terms.md` is the glossary, Genesis to Revelation.
Where this file and the founder's Translation Charter disagree, the Charter
wins; fix this file.

**Status: proposed, awaiting native Persian reviewers.** Nothing in Persian
is drafted yet. Every Persian record will be `ai_draft`. The level names,
the grammar words in `owb/morph.py`, the register and address rules, the
name forms and the key terms below are first proposals, written before
drafting so that books drafted in parallel agree, and a reviewer is expected
to change some of them. Section 15 lists the defaults the founder should
confirm first.

Reviewers: start with
[`docs/review-notes/fa-review-checklist.md`](review-notes/fa-review-checklist.md).

## 1. Sources and independence

- Translate from the Hebrew (and the Aramaic of Daniel 2:4-7:28, Ezra
  4:8-6:18 and 7:12-26, and Jeremiah 10:11) and the Greek, never from the
  English. The English renderings and the literal gloss show how a sentence
  was read; the meaning decisions say what it means. Persian says that
  meaning in its own way.
- **Never reproduce the wording of a copyrighted Persian Bible**: the
  Today's Persian Version (ترجمهٔ مژده, 1976, revised 1995), the New
  Millennium Version (ترجمهٔ هزارهٔ نو, 2014), the Persian Contemporary Bible
  (ترجمهٔ تفسیری), the Dari versions and the others. The Old Persian Version
  (ترجمهٔ قدیم, Robert Bruce and Mirza Abdullah, 1895) is in the public
  domain, but it is for comparison too: Open Word Bible's text is its own.
  The familiar passages pull hardest toward the Old Version and Muzhdeh:
  Genesis 1-3, Exodus 20, Numbers 6:24-26, Deuteronomy 6, Psalms 1, 23, 51,
  91, 121, Isaiah 9, 40, 53, the Sermon on the Mount, the Lord's Prayer, John
  1 and 3, Romans 8, 1 Corinthians 13. Draft from the gloss and the English
  levels, then rewrite any sentence that matches a well-known version for
  more than a short common phrase.
- The vocabulary of this file and the glossary is the church's shared
  vocabulary (فیض, کاهن, خیمهٔ ملاقات, روح‌القدس), and the names are the
  conventional forms; using them is not copying wording. A clause is
  wording.
- **Persian and Arabic.** Persian shares its script and much religious
  vocabulary with Arabic, and Persian Muslims know many of the same people
  under their Qur'anic names (عیسی, موسی, ابراهیم, یحیی, داوود). Use the forms
  Persian Bibles and Persian churches use (section 6); where a Bible form and
  the Qur'anic form are the same, that is the form. Do not copy wording from
  an Arabic Bible either, and never write an Arabic phrase where Persian has
  its own (no ان‌شاءالله, no سبحان‌الله as a translation of praise).
- Never type Greek or Hebrew. A Greek or Hebrew word quoted in a decision is
  copied from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"fa": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- The text is stored in logical (typed) order, as every language's is. The
  site sets direction; never add a direction mark (U+200E, U+200F, U+202A to
  U+202E, U+2066 to U+2069) to a rendering. **(checked: the registration
  pull request adds the check)**
- Keep the `\v N ` verse markers in every Persian level, in the order the
  English has them, with ASCII digits (`\v 3 `). **(checked)** The marker
  comes straight after the punctuation that ends the previous verse's
  words, with one space after the number: `...ایمان شما. \v 3 زیرا`.
  Persian puts the verb last, so a sentence running across verses often
  wants its parts in another order. Keep each verse's content after its own
  marker as far as Persian allows (split at a comma, or make two sentences
  at Balanced and Readable); where content has to cross a verse boundary,
  say so in a `word_order` rendering decision.
- The meaning decisions are shared: do not change them. Persian needs only
  its own rendering decisions, with ids `r-fa-1`, `r-fa-2`, ... counted from
  1 in each record, `"layer": "rendering"`, `"language": "fa"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions. Quote the Persian words under discussion
  ("\"فیض\" rather than \"لطف\""). The site tells Persian readers that notes
  are in English for now.
- Write a Persian rendering decision where Persian had to choose and a
  reader might ask why: a word chosen over a familiar church alternative; an
  address form (تو or شما); a verse boundary moved; a setting span that
  differs from the English one; or a term settled here for the whole book
  (note it once, where it first appears in a passage). Do not repeat the
  English rendering decisions. Typical density: zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language. So each Persian level opens and closes the same
  quotations, in the same order, as the English level: no quotation added,
  dropped, merged or split. A sentence that begins or ends inside a speech
  does so in Persian too (an opening « with no », or a closing » with no «).
  Speech broken by a verb of saying in English ("Lord," he said, "you...")
  takes two pairs in Persian too: «سرورم،» او گفت، «تو...».

## 3. The three levels in Persian

The level names on the site are **تحت‌اللفظی** (Literal), **متعادل**
(Balanced) and **روان** (Readable).

**Literal (تحت‌اللفظی, OWB-L).** Keeps the source's words and grammar as far
as Persian can: participles as clauses (در حالی که...), the Hebrew chain of
"and ... and ..." as و ... و ..., the Greek and Hebrew order of clauses where
Persian allows, the Semitic idioms word for word (به روی خود افتاد, دهان
خود را گشود و گفت). Words Persian needs but the source lacks go in [square
brackets] (ASCII `[` `]`, as in every language). Keep the historic present
(می‌گوید, می‌آید) where the source has it. Literal may read stiffly; it must
not be wrong Persian.

**Balanced (متعادل, OWB-B).** Careful standard written Persian (فارسی
معیار), the register of a good public reading in church. Tracks the source
closely; no brackets. Church words stay where they are the living word for
the thing (فیض, توبه, ملکوت خدا, کاهن اعظم). Old-fashioned forms the Old
Version uses are not used: no همی- prefix, no ب- before a past verb (بگفت),
no -مر, no اینک at B, no ایشان for a plain "they", no plural verbs for one
person.

**Readable (روان, OWB-R).** Plain standard written Persian for new and young
readers, and for readers whose Persian is a second language: short
sentences, common words, Persian words over Arabic loans where both are
current (پادشاهی over ملکوت, درستکاری beside پارسایی with a decision).
Explains idioms and may make explicit what the context implies, as the
English Readable does, with a decision where the English has one. Still
written Persian: never the spoken forms (میخوام, میگه, اون), which differ
between Tehran, Kabul and Dushanbe.

## 4. God, the Lord and the divine name

- **God** (*Elohim*, *El*, *Eloah*; *theos*) is خدا at every level. Other
  gods are خدایان or بت‌ها by context. اللّه is not used for the God of
  Israel (it is the word Arabic Bibles use, not Persian ones); ایزد and
  یزدان are poetic and not used.
- **Lord** (*kyrios* of God or Jesus; *ʾAdonai*) is خداوند. To a man, or for
  a master in a parable: سَرور / ارباب; "Sir" to a stranger: آقا (R), سرورم
  (L, B).
- **The divine name** (YHWH) is `{{divine_name:خداوند|یهوه}}` at every
  level: خداوند by default, the usual form in Persian Bibles, with the name
  itself as the reader setting, as the English has LORD / Yahweh. The ezafe
  and any suffix go outside the span (`{{divine_name:خداوند|یهوه}}ِ` is not
  written; ezafe is not written at all, section 7). یَهُوَه (with vowels) and
  the older یهُوَه spelling of the Old Version are not used: یهوه.
- **YHWH and *ʾAdonai*.** Because خداوند is both, as 主 is in Japanese and
  प्रभु in Hindi, the first record of each book says how a reader can tell
  them apart (the span). *ʾAdonai* never takes a span; YHWH never stands
  outside one.
- ***ʾAdonai* YHWH** ("the Lord GOD") is `خداوند {{divine_name:خدا|یهوه}}`:
  "the Lord God" by default, as the English writes "the Lord GOD", and
  خداوند یهوه, the Old Version's form, as the setting. YHWH *Elohim* ("the
  LORD God") is `{{divine_name:خداوند|یهوه}} خدا`.
- ***Yah*** is `{{divine_name:خداوند|یاه}}`. *Hallelu Yah*: `{{divine_name:خداوند|یاه}} را ستایش کنید`;
  where the English keeps "Hallelujah" as a word (Revelation 19): هَلِلویاه,
  no span.
- **Pronouns for God.** Persian has no capital letters and one third-person
  pronoun (او) for he and she, so the `deity_pronoun` setting has nothing to
  change: Persian renderings have **no** deity_pronoun spans. Respect comes
  from the verbs (section 5). The first record of a passage file says so
  once where the English has a span.

## 5. Address, register and speech

The source has no polite forms; Persian must choose. These choices are
wording, the same meaning in other clothes, so they are rendering
decisions, never meaning decisions.

- **"You" to God** is تو, at every level, as Persian prayer and poetry
  address God. **"You" to Jesus** is تو at Literal; at Balanced and Readable
  تو from his disciples and from God, شما from strangers, petitioners and
  officials who speak to him with respect (the Syrophoenician woman, the
  centurion, Pilate), noted once per scene.
- **Among people.** شما to kings, masters, governors and elders from those
  below them, at Balanced and Readable; Literal keeps تو for every singular
  "you", as the source has one form. Kings and masters say تو to servants.
  Keep a speaker's form through a scene. **"You" plural** is شما at every
  level.
- **Verbs for God's and Jesus' speech.** The narrator writes فرمود (and
  فرمودن in its other forms) for God speaking at Literal and Balanced, and
  گفت at Readable; for Jesus, گفت at every level, as the Gospels' narration
  is plain. Other respect verbs (تشریف آوردن, میل فرمودن) are not used. One
  decision per book, where it first appears.
- **Pronouns.** God and Jesus speak of themselves as من. The writer of a
  letter speaks of himself as من and of "we" as ما. Persian leaves the
  subject pronoun out where the verb's ending shows it: do not add او for
  God or Jesus where the ending or a name will do. Never ایشان for one
  person.
- **Narrative** is in the simple past (گفت, رفت, آمد) at every level; the
  past continuous (می‌گفت) where the source has an imperfect of ongoing or
  repeated action. Letters speak to their readers in the present and
  imperative of written Persian.
- **Commands**: the plain imperative (بروید, بیایید, دوست بدارید) at L and B;
  R may soften (باید ... کنید) where the English Readable does. The negative
  imperative is نـ (نترسید); the older مـ (مترسید) only at Literal where it
  is the Old Version's familiar form, and not at all if a reviewer prefers.

### Brothers and sisters

*adelphoi* meaning the believers is `{{gender:برادران و خواهران|برادران}}`
at every level, as an address `ای {{gender:برادران و خواهران|برادران}}،`
(L, B) and `{{gender:برادران و خواهران عزیز|برادران عزیز}}،` (R). A single
brother in the faith: `{{gender:برادر یا خواهر|برادر}}`. Persian words for
people are already inclusive (مردم, انسان, کسی, همه, فرزندان), so no span is
needed where the English spans "people / men" or "children / sons"; note it
once per passage (setting_alternative).

## 6. Names

### Principles

- **The forms of Persian Bibles and churches**, which are close to the
  Arabic Bible forms and, for many people, to the Qur'anic ones: عیسی,
  مسیح, یحیای تعمیددهنده, پطرس, یوحنا, پولس, موسی, ابراهیم, داوود. A name in
  the glossary is written as the glossary has it.
- **Persian kings and places**, which matter more to Persian readers than to
  any other: Cyrus is کوروش, Darius داریوش, Xerxes (*Ahashverosh*) خشایارشا,
  Artaxerxes اردشیر, Persia پارس, Media ماد, Susa شوش, Elam عیلام, Ecbatana
  هگمتانه. These are the forms Iranian schoolbooks use; the Old Version's
  کورش, اَخشورش and ارتحشستا are the alternatives a reviewer should weigh.
- **Places that still exist** take their modern Persian names where those
  are the Bible's own (مصر, دمشق, بابل, روم, آتن, قبرس).
- **A name not in the glossary**: transliterate the Hebrew or Greek form by
  the same patterns (ש as ش, צ as ص, ט as ط, ח as ح, ע as ع where the
  Persian Bible tradition writes it; Greek -os as -وس, -as as -اس), and add
  it to the book's section of `docs/persian-terms.md` in the same pull
  request, with a decision where it first appears.
- No vowel signs on names, except a name a reader would misread without
  them, and then only where it first appears in a book, at Literal.

### Book names

The names of `data/books.json`: پیدایش, خروج, لاویان, اعداد, تثنیه, یوشع,
داوران, روت, اول سموئیل ... مکاشفه; Gospels without انجیل in the book list
(متی, مرقس, لوقا, یوحنا), and the letters by their addressees (رومیان,
قرنتیان, عبرانیان). A Psalm is مزمور (مزمور ۲۳), the book مزامیر.

## 7. Spelling and typography

- **Letters.** Persian ی (U+06CC) and ک (U+06A9), never the Arabic ي (U+064A)
  and ك (U+0643), which look the same in many fonts but break search and
  sorting. **(checked: the registration pull request adds the check)**
  Persian digits, where a digit is written in the text, are ۰۱۲۳۴۵۶۷۸۹
  (U+06F0 to U+06F9), never the Arabic-Indic ٠١٢٣ (U+0660 to U+0669).
- **The half-space** (نیم‌فاصله, zero-width non-joiner U+200C) joins the
  parts of one word without joining their letters, as the Academy of
  Persian Language and Literature's spelling rules have it: می‌گوید,
  نمی‌دانم, خانه‌ها, شاگردانش but کتاب‌ها, روح‌القدس, بیت‌لحم, تعمیددهنده (one
  word, letters that join), دوست‌داشتنی. Never a full space and never no
  space where the half-space belongs; never a Latin hyphen.
- **Ezafe** is not written (پسر انسان, not پسرِ انسان), except after a final
  silent ه, where it is هٔ (خانهٔ خدا, کلمهٔ خداوند), and after final ا or و,
  where it is ی (خدای اسرائیل, موسای خادم is not used: موسی، خادم). Vowel
  signs (fatha, kasra, damma, tashdid, sukun) are not written, except to
  prevent a misreading (section 6).
- **Punctuation.** The Persian comma ، (U+060C), semicolon ؛ (U+061B) and
  question mark ؟ (U+061F); the full stop, colon and exclamation mark are
  the ASCII ones (. : !). The ASCII comma, semicolon and question mark are
  not used in Persian text. Quotation marks are « » outside and “ ”
  inside, typed in that logical order (« opens even though a right-to-left
  line shows it on the right); a quotation inside that one takes « » again.
  The dash is — (U+2014), the ellipsis … (U+2026). Words a speech is
  introduced by end with a colon: عیسی گفت: «...».
- **Numbers.** In running text, numbers in words, as Persian Bibles write
  them (دوازده شاگرد, روز سوم, پنج هزار نفر, صد و بیست و هفت ولایت). Digits
  only where a modern measure from the `units` setting needs them
  (`{{units:حدود ۳ کیلومتر|پانزده ستادیون}}`), and then Persian digits.
  Chapter and verse references in decisions stay in English form (1:2), and
  verse markers are ASCII. Whether the site shows verse and chapter numbers
  in Persian digits is a decision for the founder (section 15), made in the
  build, never in the records.
- **No direction marks, no tatweel** (ـ U+0640, for stretching), no
  presentation forms (U+FB50 to U+FEFF): the plain letters only.

## 8. Words for the whole Bible

The New Testament's words, and those both Testaments share. The Old
Testament's (sanctuary, offerings, officials, formulas) are in
`docs/persian-terms.md`. Below, *dn* is `{{divine_name:خداوند|یهوه}}`.

| Greek / Hebrew (English) | Persian | Notes |
|---|---|---|
| God | خدا | Every level. |
| Lord (*kyrios* of God or Jesus) | خداوند | "Lord!" as an address: ای خداوند (L, B), خداوندا (R). |
| Jesus | عیسی | With ezafe and suffixes: عیسای ناصری, not عیسیِ. |
| Christ | مسیح | No christos span (section 9). |
| Holy Spirit; the Spirit | روح‌القدس; روح | روح خدا where the source has "Spirit of God". |
| kingdom of God; of heaven | ملکوت خدا; ملکوت آسمان (L, B); پادشاهی خدا; پادشاهی آسمان (R) | |
| Son of Man | پسر انسان | A title, every level; never under the gender setting. |
| Son of God; Son of David | پسر خدا; پسر داوود | |
| disciple(s) | شاگرد; شاگردان | |
| apostle | رسول; رسولان | |
| prophet | نبی; انبیا (L, B); پیامبر; پیامبران (R) | |
| the Law; the Law and the Prophets | شریعت; تورات و کتب انبیا | تورات for the Torah as a book. |
| scribes | علمای دین | کاتبان at L where the English Literal says scribes. |
| Pharisees; Sadducees | فریسیان; صدوقیان | |
| chief priests; high priest | سران کاهنان; کاهن اعظم | |
| elders | مشایخ (L, B); بزرگان قوم (R) | |
| tax collectors; sinners | باجگیران; گناهکاران | |
| Gentiles, nations | غیریهودیان (B, R); قوم‌ها / اقوام (L) | "all the nations": همهٔ قوم‌ها. |
| synagogue; temple | کنیسه; معبد | |
| Sabbath; Passover | شَبّات (روز شبات); عید پِسَح | No vowel signs after the first use in a book. |
| church, assembly | کلیسا | جماعت for the assembly of Israel (*qahal*) and for *synagōgē* as a gathering. |
| repent; repentance | توبه کردن; توبه | |
| sin; sinner | گناه; گناهکار | |
| believe; faith | ایمان آوردن (to come to believe), ایمان داشتن (to believe); ایمان | |
| grace | فیض | Key term, every level. |
| truth | حقیقت | Key term. R may say راستی with a decision. |
| glory; glorify | جلال; جلال دادن | Key term. |
| peace | آرامش (inner, with God); صلح (between people); سلامتی (in a blessing) | A greeting: سلام بر شما. |
| righteousness; righteous | پارسایی; پارسا | Key term. R may say درستکاری, درستکار with a decision. |
| justify | پارسا شمردن (L, B); در نظر خدا پارسا به حساب آوردن (R) | |
| mercy; love (*agapē*) | رحمت; محبت | محبت for *agapē* at every level; عشق is not used for it. |
| gospel, good news | انجیل (L, B); خبر خوش (R) | |
| baptize; John the Baptist | تعمید دادن; یحیای تعمیددهنده | |
| angel | فرشته | |
| demon; unclean spirit | دیو; روح پلید | |
| devil; Satan | ابلیس; شیطان | |
| heaven; Gehenna; Hades | آسمان; جهنم; عالم مردگان | |
| Truly I tell you (*amēn*) | آمین، به شما می‌گویم (L); براستی به شما می‌گویم (B); حقیقت را به شما می‌گویم (R) | In John doubled: آمین، آمین (L); براستی، براستی (B). |
| crowd | جمعیت | |
| hypocrites | ریاکاران | |
| Woe to you | وای بر شما | |
| eternal life | حیات جاودان (L, B); زندگی جاودان (R) | |
| cross; crucify | صلیب; به صلیب کشیدن | |
| Amen; Hosanna | آمین; هوشیعانا | |
| Rabbi; Teacher | ربی; استاد | |
| slave (*doulos*, *ʿeved*) | برده (L); خادم (B, R) | As the English: Literal says slave, Balanced and Readable servant, except where slavery itself is the point (slave and free), where برده stays at every level. "Servant of the LORD": خادم *dn*. |
| covenant | عهد | |
| holy; saints | مقدس; مقدسین (L, B), ایمانداران / قوم خدا (R) | |
| flesh (Paul's moral sense) | نفس (L, B: "the flesh" as a power, with a decision); طبیعت گناه‌آلود (R) | جسم for the body. |
| world (*kosmos*) | دنیا (L, B: جهان where it means the created world) | |
| forgive | بخشیدن; آمرزیدن (L, for sins) | |
| hesed (steadfast love) | محبت وفادارانه (L); محبت پایدار (B); محبت همیشگی (R) | One form per level, Genesis to Malachi. |

## 9. Reader settings in Persian

Settings change wording, never meaning, exactly as in English.

- `divine_name`: `{{divine_name:خداوند|یهوه}}` (section 4).
- `deity_pronoun`: **no spans** (section 4).
- `christos`: **no spans**, as in Hindi. مسیح is both the title in عیسی
  مسیح and the word Messiah itself, so the choice the English setting offers
  is already made; ماشیح (the Hebrew word in Persian letters) is a scholar's
  transliteration, not a second Persian way of saying it. The first record
  of a passage file where the English spans *Christos* says so once. A
  reviewer may ask for `{{christos:مسیح|ماشیح}}` instead; then every passage
  is revised.
- `gender`: section 5, "Brothers and sisters".
- `units`: metric by default, the original unit as the alternative:
  `{{units:حدود ۳ کیلومتر|پانزده ستادیون}}`. Literal keeps the original unit.
  Coins have no metric form: a `units` span gives the value in wages by
  default and the coin as the alternative (`{{units:مزد یک روز|یک دینار}}`), as
  the English does. Literal keeps the coin. This differs from the English
  (US units) and needs a rendering decision the first time in a passage.
- `plural_you` is Spanish only, `god_term` Chinese only.
- A setting span holds no quotation marks (`owb/markup.py` checks), and
  its options have no space or half-space at their edges.

## 10. Poetry, headings and the Old Testament

- **Lines.** Poetry is set in lines, as `docs/english-style.md` section 10
  describes: each break inside a verse is a `\q ` marker. Persian follows
  the English level exactly: where an English level has `\q` breaks, that
  Persian level has the same number of lines, broken at Persian's own phrase
  boundaries; where the English level is prose, so is the Persian. A verse
  start is always a line start. Write a space on both sides of the marker.
  Persian has a great tradition of metre and rhyme; do not impose it on
  Hebrew poetry, and do not pad or force the parallel lines into equal
  length.
- **Psalm titles** are verse 1, as in the Hebrew: translated as the English
  level does it. Selah is سِلاه (the vowel signs only at its first use in a
  book).
- **Old Testament narrative**: the Hebrew chain of "and ... and ..." is
  kept with و at Literal; Balanced and Readable use Persian's own
  connectives (پس, آنگاه, سپس) and new sentences.
- **Laws and instructions**: the imperative and نباید (قتل نکن at L, نباید
  کسی را بکشی at R); the Ten Commandments as the glossary has them.
- **Section headings and summaries.** Where a book's
  `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json` has languages
  beside English, add `"fa"` beside them as each book is drafted, written
  from Open Word Bible's own Persian wording, never the headings of a
  Persian Bible. They are AI drafts until reviewed.

## 11. Recurring formulas

One form each, in every book; the first record of a passage that uses one
notes it once. `docs/persian-terms.md` has the rest.

| Source (English) | Literal | Balanced | Readable |
|---|---|---|---|
| Thus says the LORD | *dn* چنین می‌گوید | *dn* چنین می‌فرماید | *dn* می‌گوید |
| declares the LORD (*neʾum YHWH*) | این فرمودهٔ *dn* است | *dn* می‌فرماید | *dn* می‌گوید |
| The word of the LORD came to ... | کلام *dn* بر ... نازل شد | as L | *dn* به ... فرمود |
| I am the LORD | من *dn* هستم | as L | as L |
| behold (*hinneh*, *idou*) | اینک | ببین / ببینید, or left out where it only marks attention | left out |
| and it came to pass (*wayehi*) | و واقع شد که / a time clause (هنگامی که ...) | left out, or a time clause | as B |
| answered and said | پاسخ داد و گفت | پاسخ داد | as B |
| fell on his face | به روی خود به زمین افتاد | رو به خاک افتاد | به خاک افتاد |
| In that day | در آن روز | as L | در آن زمان |
| Fear not | مترس / مترسید | نترس / نترسید | as B |
| grace and peace to you | فیض و آرامش بر شما باد | as L | فیض و آرامش با شما باشد |

## 12. Drafting book by book

1. **Check the book is free** (`check-book-before-translating` skill) and
   that the English is drafted: Persian is drafted from records that
   already have their meaning decisions.
2. **Read this file, the book's section of `docs/persian-terms.md`, and the
   book's English terms notes.** The glossary's form is the form.
3. **Draft each record at L, then B, then R**, from the Hebrew or Greek, the
   gloss, the meaning decisions and the English levels. Keep the English
   record's verse markers, line breaks and quotations (section 2).
4. **Compare each familiar verse with the Old Version and Muzhdeh** and
   rewrite any clause that matches (section 1). Do not open them for
   unfamiliar verses: the check is for memory's pull, not a source.
5. **Write the decisions** (section 2): the first use in the book of a
   glossary choice, a name not in the glossary, every setting span that
   differs from the English, every شما to Jesus.
6. **Add new names** to the book's section of `docs/persian-terms.md` in
   the same pull request.
7. **Before the pull request, search the book's Persian** at every level for
   what this file excludes: the Arabic ي and ك, Arabic-Indic digits, ASCII
   `,` `;` `?` in the text, straight `"` quotes, a full space inside می‌,
   نمی‌ or before ‌ها where a half-space belongs, a direction mark, a vowel
   sign outside a first-use name, همی-, بگفت-type past forms, اللّه, ایشان
   for one person; and errors: یهوه outside a `divine_name` span, a
   `deity_pronoun` or `christos` span.
8. **Headings and summaries** for the book in Persian (section 10).
9. One pull request per book; `scripts/check.sh` must pass.

## 13. What the registration pull request needs

Steps 1-6 of `docs/adding-a-language.md`, and section 11 there (right to
left), go into one pull request before any Persian is drafted. Beyond the
usual files:

- **`data/languages.json`**: `{"code": "fa", "name": "Persian", "native":
  "فارسی", "quotes": "&laquo;{}&raquo;", "dir": "rtl"}`.
- **Right to left**: the Arabic-script fonts, the `:lang()` rules for
  letter spacing and italics, and the shared right-to-left fixes come from
  the Arabic registration (one shared pull request for both); Persian adds
  `fa` beside `ar` in each.
- **Catalog arrows** (`i18n/fa.json`): "Previous" points right, "Next"
  left, as `docs/adding-a-language.md` section 11 says.
- **Validation** (`owb/validate.py`): in `fa` renderings, refuse the Arabic
  ي and ك, Arabic-Indic digits, and direction marks, with tests.
- **Sentence ends**: ؟ ends a sentence in the verse-of-the-day checks
  (`tests/test_site.py`, `scripts/check_verses_of_the_day.py`), and ، ؛ ؟
  are stripped as punctuation in `scripts/level_checks.py` and
  `scripts/name_spellings.py`.
- **Search**: Postgres has no Persian stemmer, so `fa` uses `owb_simple`;
  search should fold ي into ی and ك into ک (a query typed on an Arabic
  keyboard), ignore vowel signs and the half-space, and read Persian and
  Arabic-Indic digits in a query as ASCII (یوحنا ۳:۱۶).
- **`backend/staff/overlap.py`** `EDITION_LANGUAGE`: `pes` (Iranian Persian)
  for the Persian reference Bibles.
- **`owb/morph.py`**: grammar words in Persian (اسم, فعل, حالت فاعلی,
  مفرد, جمع, مذکر, مؤنث, ماضی مطلق, معلوم, مجهول, امری, ...), for a
  reviewer to check.

## 14. Status

A Persian rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.

## 15. Defaults for the founder to confirm

Each decides the wording of thousands of verses. Confirm or change each
once, before drafting goes far; the outcome is recorded under a "Settled"
heading at the top of this file.

1. **YHWH**: `{{divine_name:خداوند|یهوه}}`. Alternative: یهوه by default.
2. ***ʾAdonai* YHWH**: `خداوند {{divine_name:خدا|یهوه}}`. Alternative:
   `{{divine_name:خداوندگار|خداوند یهوه}}`, one span for the phrase.
3. **Christ**: مسیح with no christos span. Alternative:
   `{{christos:مسیح|ماشیح}}`.
4. **Address**: تو to God; تو to Jesus from disciples, شما from strangers
   and officials at B and R. Alternative: تو to Jesus throughout.
5. **Verbs**: فرمود for God's speech at L and B; گفت for Jesus.
   Alternative: فرمود for both; or گفت throughout.
6. **Persian kings**: کوروش, داریوش, خشایارشا, اردشیر. Alternative: the
   Old Version's forms.
7. **Kingdom**: ملکوت خدا at L and B, پادشاهی خدا at R. Alternative:
   پادشاهی at every level.
8. **Righteousness**: پارسایی. Alternative: عدالت (the Old Version's word,
   which today mostly means justice).
9. **Numerals on the site**: verse and chapter numbers in Persian digits
   (a display step in the build and the reader), or ASCII digits as every
   other language has them now. Records keep ASCII either way.
10. **Level names**: تحت‌اللفظی, متعادل, روان.
11. **Audience**: Iranian standard written Persian, which Afghan readers
    read; a Dari edition, if one comes, is another language code (`prs`).
