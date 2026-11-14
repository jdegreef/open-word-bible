# Ukrainian style guide

How Open Word Bible drafts Ukrainian (українська). It builds on
`docs/english-style.md`, which still covers everything that is not about
wording: sources, one record per sentence, the three levels, decisions and
status. It also builds on each book's terms notes (`docs/john-terms.md` and
the others). Their book-wide choices hold in Ukrainian unless this file says
otherwise. Where this file and the founder's Translation Charter disagree,
the Charter wins; fix this file.

**Status: proposed, awaiting a native Ukrainian reviewer.** Every Ukrainian
record is `ai_draft`. The level names, the grammar labels in
`owb/morph.py`, the forms of address and the key terms below are first
proposals, and a reviewer is expected to change some of them.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English, and
  never through Russian. The English renderings and the literal gloss show
  how a sentence was read; the meaning decisions say what it means.
  Ukrainian says that meaning in its own way. The Russian renderings are not
  a model: Ukrainian vocabulary, word order and idiom differ, and a
  Russianism (*являтися* for "to be", *приймати участь*, *на протязі*,
  *слідуючий*, *відноситися до*) is a mistake to avoid.
- **Never reproduce the wording of a copyrighted Ukrainian Bible**: Ohienko
  (Огієнко, 1962), Khomenko (Хоменко, 1963), Turkoniak (Турконяк), Hyzha
  (Гижа), Derevianko (Деревʼянко), the Ukrainian Bible Society's modern
  translation, «Слово Життя» and others. The Kulish–Puluj–Nechui-Levytskyi
  Bible (Куліш, Пулюй, Нечуй-Левицький, 1903) is in the public domain. Its
  forms and Ohienko's shape how readers remember familiar verses, but their
  archaisms (*бо* is fine; *сей*, *оцей* in narrative, *аж*, *ось* at every
  turn, *рече*, *глаголати*) are out of place in a modern translation. Do not
  copy either: draft from the Greek and the gloss. Then rewrite any sentence
  that matches a well-known version for more than a short common phrase.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied
  from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"uk": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, in
  every Ukrainian level. **(checked)** Ukrainian word order is free enough
  that this is rarely a problem. Where it is, say so in a rendering decision.
- The meaning decisions are shared: do not change them. Ukrainian needs only
  its own rendering decisions, with ids `r-uk-1`, `r-uk-2`, ... counted from
  1 in each record, `"layer": "rendering"`, `"language": "uk"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions. Quote the Ukrainian words under discussion
  ("\"Царство Небесне\" rather than \"Небесне Царство\""). The site tells
  Ukrainian readers that notes are in English for now.
- Write a Ukrainian rendering decision where Ukrainian had to choose and a
  reader might ask why. That covers a word chosen over a familiar
  alternative, especially an Ohienko or Kulish one; a verb aspect the Greek
  leaves open; a setting span that differs from the English one; or a term
  settled here for the whole book (note it once, where it first appears in a
  passage). Do not repeat the English rendering decisions. Typical density:
  zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language. So each Ukrainian level must open and close the same
  quotations, in the same order, as the English one: no quotation added,
  dropped, merged or split. A sentence that begins or ends inside a speech
  begins or ends inside it in Ukrainian too. Ukrainian often introduces
  speech with a dash in dialogue; do not: always use quotation marks, as
  below.

## 3. The three levels in Ukrainian

The level names on the site are **Буквальний** (Literal),
**Збалансований** (Balanced) and **Простий** (Readable).

**Literal (OWB-L).** Keeps the Greek's words, their grammar (participles as
дієприслівники or дієприкметники where Ukrainian has them, though Ukrainian
uses active participles far less than Russian, so a clause with *який* is
often the closer match; genitives; the order of words where Ukrainian
allows) and its repetitions ("і... і... і..."). Words Ukrainian needs but the
Greek lacks go in [square brackets]. The copula Ukrainian leaves out in the
present is not supplied. Keep the historic present (каже, приходить) where
the Greek has it.

**Balanced (OWB-B).** Careful standard modern literary Ukrainian, the
register of a good public reading. Tracks the Greek closely; no brackets.
Church words stay where they are the living word for the thing (благодать,
покаяння, Царство Небесне, первосвященик). Archaisms where a modern word
says the same (сей, оний, рече, глаголати, понеже) are not used.

**Readable (OWB-R).** Plain everyday Ukrainian for new and young readers:
short sentences, common words, everyday words over church ones where both
are current (збирачі податків for митарі). Explains idioms and may make
explicit what the context implies, as the English Readable does, with a
decision where the English has one.

## 4. Forms of address

The Greek has no polite *you*. Ukrainian Bibles and Ukrainian prayer
address God and Jesus as ти, and so does this translation, at every level.

- **People speaking to God and to Jesus** say ти, disciples, petitioners and
  opponents alike. A reviewer may move a petitioner who does not know him (a
  centurion, an official) to ви, with a decision.
- **Jesus speaking** to one person says ти, to more than one ви. The Greek's
  singular and plural *you* come through without a setting.
- **Ordinary people among themselves**: ти, as in the Bible tradition; ви
  only where the Greek has a plural. Courtly address to a ruler is carried by
  the words used (пане, володарю, правителю), not by ви.
- **The vocative.** Ukrainian has a living vocative case; use it in every
  address: Господи, Учителю, Равві, Отче, Ісусе, Симоне, Петре, жінко,
  друже, брати (plural nominative serves), Сину Давидів.

## 5. Spelling, names and typography

- **Spelling.** Standard modern Ukrainian orthography (the 2019 *Український
  правопис*), with і, ї, є, ґ. Capitals for God, the Holy Spirit and Jesus'
  titles as below, and for pronouns for God only through the `deity_pronoun`
  setting (section 7).
- **The apostrophe is ʼ (U+02BC, MODIFIER LETTER APOSTROPHE)**: пʼять,
  зʼявився, мʼясо, обʼявлення, деревʼяний. Never ’ (U+2019) or '
  (U+0027): the reader takes those for quotation marks. **(checked by the
  red-letter count)**
- **Punctuation.** Quotation marks are «ялинки» outside and “ ” for a
  quotation inside a quotation, and ‘ ’ inside that, with no spaces inside
  the marks. The low-high „лапки“ are not used: the reader finds speech
  (the red letters, `owb/markup.py`) from « » “ ” ‘ ’ only, where “ always
  opens. **A sentence still ends with its own mark inside the closing
  guillemet** («...іди за Мною.»), so the verse reads as a sentence on its
  own. The dash is an em dash with spaces ( — ).
- **Numbers.** Write figures in Arabic digits where a figure is wanted (12,
  5000), with a thin no-break space as the thousands separator in numbers of
  five digits or more (10 000). Spell out short numbers in running text
  (двоє людей).
- **Proper names** take the forms of modern Ukrainian Bibles, which follow
  the Greek more closely than the Russian ones do:
  Ісус, Марія, Йосиф, Іван, Іван Хреститель, Симон Петро, Андрій, Яків,
  Зеведей, Филип, Варфоломій, Хома, Матвій, Алфей, Тадей, Симон Зилот, Юда
  Іскаріот, Ірод, Іродіада, Пилат, Каяфа, Анна, Варавва, Марія Магдалина,
  Никодим, Лазар, Марта, Закхей, Мойсей, Ілля, Єлисей, Ісая, Єремія, Йона,
  Даниїл, Давид, Соломон, Авраам, Ісаак, Яків (the patriarch), Ной, Адам,
  Єва, Авель, кесар (a title) / Кесар Август. Acts and the letters: Павло,
  Савл, Варнава, Степан, Филип, Корнилій, Сила, Тимофій, Тит, Лука, Марко,
  Аполлос, Прискилла, Акила, Агрипа, Фест, Фелікс, Гамалиїл, Ананій,
  Сапфіра, Тавіта, Енея, Симон Маг, Барсава, Матфій (the twelfth apostle, kept
  apart from Матвій), Тихик, Онисим.
  Places: Єрусалим, Галилея, Юдея, Самарія, Назарет, Вифлеєм, Капернаум,
  Віфсаїда, Хоразин, Йордан, Єгипет, Сирія, Тир, Сидон, Содом, Гоморра,
  Єрихон, Віфанія, Вітфагія, Оливна гора, Гетсиманія, Голгофа, Еммаус,
  Кана, Наїн, Декаполь, Ідумея; Рим, Антіохія, Дамаск, Кесарія, Йоппія,
  Лідда, Кіпр, Тарс, Ефес, Коринт, Афіни, Філіппи, Солунь, Верія,
  Македонія, Ахая, Галатія, Азія (the Roman province), Крит, Мальта. Peoples: юдеї, самаряни, римляни, греки
  (елліни where the Greek word means non-Jews generally and L keeps it).
- **Clock time.** Literal keeps the Greek count ("о шостій годині").
  Balanced and Readable give the time as a modern reader counts it
  ("близько полудня"), with a decision.

## 6. Words for the whole of the New Testament

| Greek (English) | Ukrainian | Notes |
|---|---|---|
| God | Бог | Every level; *бог* for "a god". |
| Lord (*kyrios*, of God or Jesus) | Господь | "Lord!" as an address: Господи. "Sir" to a stranger: пане. |
| Jesus | Ісус | Vocative Ісусе. |
| Christ | `{{christos:Христос\|Месія}}` | Inflected inside each option: `{{christos:Христа\|Месії}}`, `{{christos:Христові\|Месії}}`, `{{christos:Христом\|Месією}}`. With the name: `Ісус {{christos:Христос\|Месія}}`. Месія plainly, no setting, where the Greek has *Messias* (John 1:41; 4:25). |
| Holy Spirit; the Spirit | Святий Дух; Дух | |
| kingdom of heaven | Царство Небесне (L, B); Небесне Царство (R) | One decision per passage where it first appears. |
| kingdom of God | Царство Боже | |
| Son of Man | Син Людський | A title, every level. Never under the gender setting. |
| Son of God; Son of David | Син Божий; Син Давидів | |
| disciple(s) | учень; учні | Every level. |
| apostle | апостол | |
| prophet | пророк | |
| the Law; the Law and the Prophets | Закон; Закон і Пророки | |
| scribes | книжники (L); учителі Закону (B, R) | They were teachers of the Law, not copyists. |
| Pharisees; Sadducees | фарисеї; садукеї | |
| chief priests; high priest | старші священники (L, B, R); первосвященик | Ohienko's "первосвященики" for the plural blurs the one high priest with the leading priests; one decision per passage. Spelling: священник, священники (2019 orthography; the older священик is not used). |
| elders | старійшини | |
| tax collectors; sinners | митарі (L); збирачі податків (B, R); грішники | |
| Gentiles, nations | язичники (L, B); неюдеї / інші народи (R) | "the nations": народи. |
| synagogue; temple | синагога; храм | |
| Sabbath; Passover | субота; Пасха | |
| church, assembly | церква | Of the believers (Matthew 16:18; 18:17); громада where the sense is a gathering, with a decision. |
| repent; repentance | покаятися; покаяння | Readable may say "змінити своє життя" with a decision. |
| sin | гріх | |
| believe; faith | вірити; віра | Keep the verb at every level. |
| grace | благодать | Key term: the same word at every level. |
| truth | істина (L, B); правда (R) | Key term. |
| glory; glorify | слава; прославляти | Key term. |
| peace | мир | Key term. |
| righteousness; righteous | праведність; праведний | Key term. Readable may say "жити правильно" where the sense is conduct, with a decision. |
| gospel, good news | Євангеліє (L, B); Добра звістка (R) | |
| baptize; John the Baptist | хрестити; Іван Хреститель | Literal may say занурювати where the sense of the washing matters, with a decision. |
| angel | ангел | |
| demon; unclean spirit | біс; нечистий дух | |
| devil; Satan | диявол; сатана | |
| heaven; Gehenna; Hades | небо, небеса; геєна (L, B), пекло (R); Гадес (L), світ мертвих (B, R) | |
| Truly I tell you (*amēn*) | Істинно кажу вам (L, B); Кажу вам правду (R) | One decision per passage. |
| crowd | натовп, люди | |
| hypocrites | лицеміри | |
| Woe to you | Горе вам | |
| eternal life | вічне життя | |
| cross; crucify | хрест; розіпʼясти | |
| bread, loaf | хліб; хліби (L), хлібини (B, R) | A decision where it first appears. |
| Amen; Hosanna | амінь; осанна | |
| Rabbi; Teacher | Равві; Учитель | Vocatives Равві, Учителю. |
| slave (*doulos*) | раб | Every level; слуга only where service alone is the point, with a decision. |

## 7. Reader settings in Ukrainian

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: every pronoun for God or Christ is written lowercase
  first and capitalised second (shown by default), only the capitalisation
  differing. **(checked)** The Ukrainian forms: `{{deity_pronoun:він|Він}}`,
  `{{deity_pronoun:його|Його}}`, `{{deity_pronoun:йому|Йому}}`,
  `{{deity_pronoun:нього|Нього}}`, `{{deity_pronoun:ньому|Ньому}}`,
  `{{deity_pronoun:ним|Ним}}`, and when Jesus speaks of himself or is
  spoken to:
  `мене|Мене`, `мені|Мені`, `мною|Мною`, `мій|Мій` (and its forms: моя,
  моє, мої, мого, моїм...), `ти|Ти`, `тебе|Тебе`, `тобі|Тобі`, `тобою|Тобою`,
  `твій|Твій` (and its forms), and `я|Я` for Jesus or God mid-sentence, so
  "я" is capitalised with "Мене" and not apart from it. The reflexive свій,
  себе and сам take none. A pronoun at the start of a sentence is written
  plainly with its capital. Put a span wherever the English has one for the
  same person; Ukrainian may need one where English does not (an object
  "його") and the reverse.
- `christos`: `{{christos:Христос|Месія}}`, inflected inside each option
  (`{{christos:Христа|Месії}}`, `{{christos:Христом|Месією}}`). Where the
  English has `Jesus {{christos:Christ|the Messiah}}`, Ukrainian writes
  `Ісус {{christos:Христос|Месія}}`. Check that both options read naturally,
  and that words agreeing with it agree under both. With a preposition, put
  the preposition inside each option: `{{christos:у Христі|в Месії}}`.
- `gender`: an inclusive default where the original means men and women,
  with the traditional Ukrainian as the alternative:
  `{{gender:брати і сестри|брати}}`, `{{gender:люди|мужі}}` where *andres*
  means people in general. Not for specific men, and not where Ukrainian is
  already inclusive (людина, люди, кожен, ніхто, хто, діти). A rendering
  decision (setting_alternative) records a difference from the English the
  first time it occurs in a passage.
- `units`: metric by default, the original unit as the alternative, as in
  French, Swahili and Russian: `{{units:близько трьох кілометрів|пʼятнадцять
  стадій}}`. Literal keeps the original unit. This differs from the English
  (US units) and needs a rendering decision the first time in a passage.
  Coins have no metric form: a `units` span gives the value in wages by
  default and the coin as the alternative (`{{units:денний заробіток|один
  динарій}}`), as the English does. Literal keeps the coin.
- `plural_you` is Spanish only.

## 7a. Conventions for the Gospels, Acts and the letters

These are settled for the first Ukrainian books (Matthew, Mark, Luke, John,
Acts, Romans, Ephesians, James), drafted in parallel; they hold for the
later books. In the Synoptic parallels, keep the wording of the Matthew
passage where the Greek is the same, and differ where the Greek differs.

- **Speech broken by a verb of saying** ("Lord," he said, "you...") takes
  two pairs of marks, «Пане», — сказав він, — «ти...», because the English
  counts two quotations and the red letters follow the count.
- **Third-level quotations** use ‘ ’ inside “ ” inside « ».
- **Gospels.** *idou* is ось at Literal, left out at Balanced and Readable;
  the Sea of Galilee is море (L), озеро (B, R); magi мудреці зі сходу at every
  level, then мудреці; the Beatitudes Блаженні (L, B), Щасливі (R);
  parable притча at every level; *diakonos* and *pais* слуга; masters in
  parables пан; centurion сотник (L, B), римський офіцер (R); the council
  Синедріон (L, B), Рада (R); governor правитель (Pilate: намісник);
  *parousia* пришестя; leaven закваска; weeds бурʼян; yoke ярмо;
  *skandalizō* спіткнутися (L), відпасти від віри (B, R), not спокуситися,
  which now means to be tempted; "Father" as an address Отче (the vocative);
  greetings Радій (L), Вітаю (B, R); fig tree смоковниця (L, B), інжир (R),
  its fruit смокви (L), інжир (B, R); *euthys* зараз же / відразу at Literal,
  varied at Balanced and Readable; *epistata* Наставнику; Luke's lake
  (*limnē*) озеро; *nomikos* законник (L), знавець Закону (B, R); *alēthōs*
  «Справді кажу вам», kept apart from *amēn*; Всевишній; Назорей or
  Назарянин by the Greek word.
- **John** (with docs/john-terms.md): Слово; «Істинно, істинно кажу вам»
  (L, B), «Кажу вам правду» (R); перебувати (L, B), залишатися (R);
  Заступник; «Я є» for the absolute "I am" (8:24, 8:28, 8:58, 13:19), «Це Я»
  in 18:5-8; знак (L, B, R), never чудо; "the Jews" юдеї at L, юдейська влада
  (B) and юдейські провідники (R) where the authorities are meant; пастух;
  «Жінко» (L, B), «Мамо» (R) for Jesus' address to his mother.
- **Acts**: Дорога (the Way, capitalised); старійшини (elders); наглядачі
  (overseers); ті, що шанують Бога, for *sebomenoi*, ті, що бояться Бога, for
  *phoboumenoi*; елліністи (L), грекомовні (B, R); Пʼятидесятниця;
  проконсул (L, B), римський правитель (R); тисяцький (L), командир (B, R);
  благовістити (L), звіщати Добру звістку (B); Савл for the apostle until
  13:9; партія for *hairesis* as a party.
- **Romans, Ephesians, James**: праведність; виправдати at every level;
  віра / вірити; Закон for God's law, закон for a ruling principle (Romans
  3:27; 7:21-8:2); діла Закону; тіло (L, B), людська / грішна природа (R)
  where *sarx* is moral; Дух; умилостивлення (L), викупна жертва (B, R);
  примирення; усиновлення; обітниця (L, B), обіцянка (R); *mē genoito*
  «Нехай не буде!» (L), «Аж ніяк!» (B), «Звичайно, ні!» (R); in Ephesians
  таємниця for *mystērion*; у Христі with the preposition inside each
  `christos` option; in James стійкість for *hypomonē*, випробування for the
  trials of 1:2, спокушати from 1:13.
- **Coins.** The talent is `{{units:пʼять мішків срібла|пʼять талантів}}`
  where the English has bags of silver; small coins
  `{{units:копійку|один асарій}}`, `{{units:останню копійку|останній
  кодрант}}`; the thirty pieces of silver тридцять срібняків.
- **Fixed sayings** match through the books: «Істинно кажу вам» (L, B); the
  weeping and gnashing of teeth плач і скрегіт зубів; «Гадюче поріддя» (B)
  for the brood of vipers; the fulfilment formula «щоб здійснилося сказане
  Господом через пророка».

## 8. Status

A Ukrainian rendering added to a record does not change its status.
Nothing is marked reviewed by an AI.

## 9. Section headings and summaries

Where a book's `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json`
has languages other than English, add `"uk"` beside them, written from Open
Word Bible's own Ukrainian wording. They are AI drafts until reviewed.
