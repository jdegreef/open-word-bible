# Russian style guide

How Open Word Bible drafts Russian (русский). It builds on
`docs/english-style.md`, which still covers everything that is not about
wording: sources, one record per sentence, the three levels, decisions and
status. It also builds on each book's terms notes (`docs/john-terms.md` and
the others). Their book-wide choices hold in Russian unless this file says
otherwise. Where this file and the founder's Translation Charter disagree,
the Charter wins; fix this file.

**Status: proposed, awaiting a native Russian reviewer.** Every Russian
record is `ai_draft`. The level names, the grammar labels in
`owb/morph.py`, the forms of address and the key terms below are first
proposals, and a reviewer is expected to change some of them.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Russian says that meaning in its own
  way.
- **Never reproduce the wording of a copyrighted Russian Bible**: the
  Modern Russian Translation (Российское библейское общество, 2011), the
  New Russian Translation (Biblica), «Слово Жизни», Kulakov's New Testament,
  «Радостная весть» (Kuznetsova) and others. The Synodal translation (1876)
  is in the public domain. It shapes how readers remember familiar verses,
  but its Church Slavonic forms (сей, оный, дабы, ибо) are out of place in a
  modern translation. Do not copy it either: draft from the Greek and the
  gloss. Then rewrite any sentence that matches a well-known version for
  more than a short common phrase.
- Never type Greek or Hebrew. A Greek word quoted in a decision is copied
  from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"ru": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the other languages. Every level is required. **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, in
  every Russian level. **(checked)** Russian word order is free enough that
  this is rarely a problem. Where it is, say so in a rendering decision.
- The meaning decisions are shared: do not change them. Russian needs only
  its own rendering decisions, with ids `r-ru-1`, `r-ru-2`, ... counted from
  1 in each record, `"layer": "rendering"`, `"language": "ru"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages' decisions. Quote the Russian words under discussion
  ("\"Царство Небесное\" rather than \"Небесное Царство\""). The site tells
  Russian readers that notes are in English for now.
- Write a Russian rendering decision where Russian had to choose and a
  reader might ask why. That covers a word chosen over a familiar
  alternative, especially a Synodal one; a verb aspect the Greek leaves
  open; a setting span that differs from the English one; or a term settled
  here for the whole book (note it once, where it first appears in a
  passage). Do not repeat the English rendering decisions. Typical density:
  zero to two per sentence.
- **Quotations keep the English structure.** The red letters
  (`data/words_of_jesus/`) count a sentence's quotations from its marks, in
  every language. So each Russian level must open and close the same
  quotations, in the same order, as the English one: no quotation added,
  dropped, merged or split. A sentence that begins or ends inside a speech
  begins or ends inside it in Russian too. Russian often introduces speech
  with a dash in dialogue; do not: always use quotation marks, as below.

## 3. The three levels in Russian

The level names on the site are **Буквальный** (Literal),
**Сбалансированный** (Balanced) and **Простой** (Readable).

**Literal (OWB-L).** Keeps the Greek's words, their grammar (participles
as participles or деепричастия where Russian has them, genitives, the order
of words where Russian allows) and its repetitions ("и... и... и..."). Words
Russian needs but the Greek lacks go in [square brackets]. The copula
Russian leaves out in the present is not supplied. Keep the historic
present (говорит, приходит) where the Greek has it.

**Balanced (OWB-B).** Careful standard modern literary Russian, the register
of a good public reading. Tracks the Greek closely; no brackets. Church
words stay where they are the living word for the thing (благодать,
покаяние, Царство Небесное, первосвященник). Slavonicisms where a modern
word says the same (сей, оный, дабы, ибо, глаголать, токмо) are not used.

**Readable (OWB-R).** Plain everyday Russian for new and young readers:
short sentences, common words, everyday words over church ones where both
are current (сборщики налогов for мытари). Explains idioms and may make
explicit what the context implies, as the English Readable does, with a
decision where the English has one.

## 4. Forms of address

The Greek has no polite *you*. Russian Bibles and Russian prayer address
God and Jesus as ты, and so does this translation, at every level.

- **People speaking to God and to Jesus** say ты, from disciples,
  petitioners and opponents alike. A reviewer may move a petitioner who
  does not know him (a centurion, an official) to вы, with a decision.
- **Jesus speaking** to one person says ты, to more than one вы. The
  Greek's singular and plural *you* come through without a setting.
- **Ordinary people among themselves**: ты, as in the Bible tradition;
  вы only where the Greek has a plural. Courtly address to a ruler is
  carried by the words used (господин, правитель), not by вы.

## 5. Spelling, names and typography

- **Spelling.** Standard modern Russian orthography. Write **ё** wherever
  it is pronounced (ещё, всё, пришёл, Пётр). Write capitals for God, the
  Holy Spirit and Jesus' titles as below, and for pronouns for God only
  through the `deity_pronoun` setting (section 7).
- **Punctuation.** Quotation marks are «ёлочки» outside and “ ” for a
  quotation inside a quotation, and ‘ ’ inside that, with no spaces inside
  the marks. The low-high „лапки“ are not used: the reader finds speech
  (the red letters, `owb/markup.py`) from « » “ ” ‘ ’ only, where “ always
  opens. **A
  sentence still ends with its own mark inside the closing guillemet**
  («...следуй за Мной.»), so the verse reads as a sentence on its own. The
  dash is an em dash with spaces ( — ).
- **Numbers.** Write figures in Arabic digits where a figure is wanted
  (12, 5000), with a thin no-break space as the thousands separator in
  numbers of five digits or more (10 000). Spell out short numbers in running
  text (двое людей).
- **Proper names** take their traditional Russian Bible forms: Иисус,
  Мария, Иосиф, Иоанн, Иоанн Креститель, Симон Пётр, Андрей, Иаков,
  Зеведей, Филипп, Варфоломей, Фома, Матфей, Алфей, Фаддей, Симон Зилот,
  Иуда Искариот, Ирод, Иродиада, Пилат, Каиафа, Варавва, Мария Магдалина,
  Никодим, Лазарь, Марфа, Моисей, Илия, Исаия, Иеремия, Иона, Даниил, Давид,
  Соломон, Авраам, Исаак, Ной, кесарь. Places: Иерусалим, Галилея, Иудея,
  Самария, Назарет, Вифлеем, Капернаум, Вифсаида, Хоразин, Иордан, Египет,
  Сирия, Тир, Сидон, Содом, Гоморра, Иерихон, Вифания, Виффагия, Масличная
  гора (the Mount of Olives; not Елеонская), Гефсимания, Голгофа, Рим.
  Peoples: иудеи, самаритяне, римляне, греки.
- **Clock time.** Literal keeps the Greek count ("в шестом часу").
  Balanced and Readable give the time as a modern reader counts it
  ("около полудня"), with a decision.

## 6. Words for the whole of the New Testament

| Greek (English) | Russian | Notes |
|---|---|---|
| God | Бог | Every level; *бог* for "a god". |
| Lord (*kyrios*, of God or Jesus) | Господь | "Lord!" as an address: Господи. "Sir" to a stranger: господин. |
| Jesus | Иисус | |
| Christ | `{{christos:Христос\|Мессия}}` | Inflected inside each option: `{{christos:Христа\|Мессии}}`, `{{christos:Христу\|Мессии}}`. With the name: `Иисус {{christos:Христос\|Мессия}}`. Мессия plainly, no setting, where the Greek has *Messias* (John 1:41; 4:25). |
| Holy Spirit; the Spirit | Святой Дух; Дух | |
| kingdom of heaven | Царство Небесное (L, B); Небесное Царство (R) | One decision per passage where it first appears. |
| kingdom of God | Царство Божье | Божье, not Божие. |
| Son of Man | Сын Человеческий | A title, every level. Never under the gender setting. |
| Son of God; Son of David | Сын Божий; Сын Давида | |
| disciple(s) | ученик; ученики | Every level. |
| apostle | апостол | |
| prophet | пророк | |
| the Law; the Law and the Prophets | Закон; Закон и Пророки | |
| scribes | книжники (L); учители Закона (B, R) | They were teachers of the Law, not copyists. |
| Pharisees; Sadducees | фарисеи; саддукеи | |
| chief priests; high priest | старшие священники (L, B, R); первосвященник | Synodal "первосвященники" for the plural blurs the one high priest with the leading priests; one decision per passage. |
| elders | старейшины | |
| tax collectors; sinners | мытари (L); сборщики налогов (B, R); грешники | |
| Gentiles, nations | язычники (L, B); не-иудеи / другие народы (R) | "the nations": народы. |
| synagogue; temple | синагога; Храм | Храм with a capital when it is the Temple in Jerusalem. |
| Sabbath; Passover | суббота; Пасха | |
| church, assembly | церковь | Of the believers (Matthew 16:18; 18:17). |
| repent; repentance | покаяться; покаяние | Readable may say "изменить свою жизнь" with a decision. |
| sin | грех | |
| believe; faith | верить; вера | Keep the verb at every level. |
| grace | благодать | Key term: the same word at every level. |
| truth | истина (L, B); правда (R) | Key term. |
| glory; glorify | слава; прославлять | Key term. |
| peace | мир | Key term. |
| righteousness; righteous | праведность; праведный | Key term. Readable may say "жить правильно" where the sense is conduct, with a decision. |
| gospel, good news | Евангелие (L, B); Радостная весть (R) | |
| baptize; John the Baptist | крестить; Иоанн Креститель | Literal may say погружать where the sense of the washing matters, with a decision. |
| angel | ангел | |
| demon; unclean spirit | бес; нечистый дух | |
| devil; Satan | дьявол; сатана | |
| heaven; Gehenna; Hades | небо, небеса; геенна (L, B), ад (R); ад, мир мёртвых | |
| Truly I tell you (*amēn*) | Истинно говорю вам (L, B); Говорю вам правду (R) | One decision per passage. |
| crowd | толпа, народ | |
| hypocrites | лицемеры | |
| Woe to you | Горе вам | |
| eternal life | вечная жизнь | |
| cross; crucify | крест; распять | |
| bread, loaf | хлеб; хлебы (L), лепёшки / хлеба (B, R) | A decision where it first appears. |
| Amen; Hosanna | аминь; осанна | |
| Rabbi; Teacher | Равви; Учитель | |
| slave (*doulos*) | раб | Every level; слуга only where service alone is the point, with a decision. |

## 7. Reader settings in Russian

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: every pronoun for God or Christ is written lowercase
  first and capitalised second (shown by default), only the capitalisation
  differing. **(checked)** The Russian forms: `{{deity_pronoun:он|Он}}`,
  `{{deity_pronoun:его|Его}}`, `{{deity_pronoun:ему|Ему}}`,
  `{{deity_pronoun:него|Него}}`, `{{deity_pronoun:нему|Нему}}`,
  `{{deity_pronoun:нём|Нём}}`, `{{deity_pronoun:им|Им}}`, and when Jesus
  speaks of himself or is spoken to: `меня|Меня`, `мне|Мне`, `мной|Мной`,
  `мой|Мой` (and its forms), `ты|Ты`, `тебя|Тебя`, `тебе|Тебе`,
  `тобой|Тобой`, `твой|Твой` (and its forms), and `я|Я` for Jesus or God
  mid-sentence, so "я" is capitalised with "Меня" and not apart from it. The
  reflexive свой and себя take none. A pronoun at the start of a sentence
  is written plainly with its capital. Put a span wherever the English has
  one for the same person; Russian may need one where English does not (an
  object "его") and the reverse.
- `christos`: `{{christos:Христос|Мессия}}`, inflected inside each option
  (`{{christos:Христа|Мессии}}`, `{{christos:Христом|Мессией}}`). Where the
  English has `Jesus {{christos:Christ|the Messiah}}`, Russian writes
  `Иисус {{christos:Христос|Мессия}}`. Check that both options read
  naturally, and that words agreeing with it agree under both.
- `gender`: an inclusive default where the original means men and women,
  with the traditional Russian as the alternative:
  `{{gender:братья и сёстры|братья}}`, `{{gender:люди|мужи}}` where *andres*
  means people in general. Not for specific men, and not where Russian is
  already inclusive (человек, люди, каждый, никто, кто, дети). A rendering
  decision (setting_alternative) records a difference from the English the
  first time it occurs in a passage.
- `units`: metric by default, the original unit as the alternative, as in
  French and Swahili: `{{units:около трёх километров|пятнадцать стадий}}`.
  Literal keeps the original unit. This differs from the English (US units)
  and needs a rendering decision the first time in a passage. Coins have no
  metric form: a `units` span gives the value in wages by default and the
  coin as the alternative (`{{units:дневной заработок|один денарий}}`), as
  the English does. Literal keeps the coin.
- `plural_you` is Spanish only.

## 7a. The Old Testament and poetry (proposed, to settle before the Old Testament)

`docs/russian-terms.md` is the Russian glossary for the Old Testament (and
the words it shares with the New): the names of God, address, key terms,
formulas, names, parallels and quotations. It settles this section: lines
follow the English record, so a level is set in lines only where the
English level is.

- **The divine name** (YHWH) is `{{divine_name:ГОСПОДЬ|Яхве}}` at every
  level, in capitals like the English "the LORD", inflected inside each
  option (`{{divine_name:ГОСПОДА|Яхве}}`, `{{divine_name:ГОСПОДУ|Яхве}}`).
  *Иегова* is not used. *Adonai* ("Lord") is Господь, never in capitals;
  *Elohim* is Бог.
- **Lines.** A psalm is set in lines, as `docs/english-style.md` section 10
  describes: mark each break inside a verse with `\q `, following the
  Hebrew accents' division (`python3 scripts/poetry_lines.py` prints it),
  at every level.

## 7b. Conventions settled in Matthew

Matthew was drafted first, in parallel passages; these choices hold for the
later books. In the Synoptic parallels, keep the wording of the Matthew
passage where the Greek is the same, and differ where the Greek differs.

- **Pronouns.** "я" for Jesus or God mid-sentence takes the span
  `{{deity_pronoun:я|Я}}`, like меня and мне; the reflexive свой, себя and
  сам take none. (Matthew was drafted first with "я" plain or capitalised
  without a span, and is brought into line separately.)
- **Speech broken by a verb of saying** ("Lord," he said, "you...") takes
  two pairs of marks, «Господин», — сказал он, — «ты...», because the
  English counts two quotations and the red letters follow the count.
  Russian usually writes one pair here; a reviewer who prefers it needs the
  quotation count changed in every language.
- **Third-level quotations** use ‘ ’ inside “ ” inside « » (22:4; 22:44).
- **Words.** *idou* is вот at Literal, left out at Balanced and Readable;
  the Sea of Galilee is море (L), озеро (B, R); magi волхвы (L, B), мудрецы
  (R); the Beatitudes Блаженны (L, B), Счастливы (R); parable притча at every
  level; disciples ученики at every level, Readable included; *doulos* раб at
  every level, слуга for *diakonos* and *pais*; masters in parables
  господин; centurion сотник (L, B), римский офицер (R); the council
  Синедрион (L, B), Совет (R); governor наместник; Rabbi Равви; *parousia*
  пришествие; leaven закваска; weeds сорняки, not плевелы; yoke ярмо, not
  иго; *skandalizō* споткнуться / оступиться (L), отпасть от веры (B), not
  соблазниться, which now means to be tempted; Hades ад (L), мир мёртвых
  (B, R); "Father" as an address Отец, not Отче; greetings Здравствуй, not
  Радуйся. Settled in Mark: unclean spirit нечистый дух at every level;
  fig tree смоковница (L, B), инжировое дерево (R), its fruit смоквы (L),
  инжир (B, R); *euthys* тотчас at Literal, varied at Balanced and
  Readable (сразу, тут же) but kept where the English keeps it.
  Settled in Luke: *epistata* Наставник; Luke's lake (*limnē*) озеро at
  every level; *nomikos* законник (L), знаток Закона (B, R); *alēthōs*
  "Поистине говорю вам", kept apart from *amēn*; Всевышний; Назорей or
  Назарянин by the Greek word.
  Settled in John (with docs/john-terms.md): Слово; «Истинно, истинно
  говорю вам» (L, B), «Говорю вам правду» (R); пребывать (L, B), оставаться
  (R); Заступник; «Я есть» for the absolute "I am" (8:24, 8:28, 8:58,
  13:19), «Это Я» in 18:5-8; знамение (L, B), знак (R), never чудо; "the
  Jews" иудеи at L, иудейские власти (B) and иудейские вожди (R) where the
  authorities are meant; пастух; «Женщина» (L, B), «Мама» (R) for Jesus'
  address to his mother.
  Settled in Acts: Путь (the Way); старейшины (elders); блюстители
  (overseers); почитающие Бога for *sebomenoi*, боящиеся Бога for
  *phoboumenoi*; эллинисты (L), грекоязычные (B, R); Пятидесятница;
  проконсул (L, B), римский правитель (R); тысяченачальник (L), командир
  (B, R); благовествовать (L), возвещать Радостную весть (B); Савл for the
  apostle; партия for *hairesis* as a party.
  Settled in Romans: праведность; оправдать at every level; вера / верить;
  Закон for God's law, закон for a ruling principle (3:27; 7:21-8:2); дела
  Закона; плоть (L, B), человеческая / греховная природа (R) where the
  sense is moral; Дух; умилостивление (L), искупительная жертва (B, R);
  примирение; усыновление; обетование (L, B), обещание (R); *mē genoito*
  «Да не будет!» (L), «Ни в коем случае!» (B), «Конечно, нет!» (R);
  Christ with a preposition inside each option (`{{christos:во Христе|в
  Мессии}}`); no ибо at Literal.
  Settled in 1 Corinthians: глупость / глупый / глупец for the *mōria*
  family (not юродство); хвалиться (L, B); раздуваться [от гордости] (L, B),
  гордиться (R); камень преткновения for *skandalon*; блуд (L), распутство
  (B), сексуальный грех (R) for *porneia*; Кифа (Пётр at R); Вечеря Господня
  (B, R); глава for "head" in 11:3.
- **Coins.** The talent is `{{units:пять мешков серебра|пять талантов}}`
  where the English has bags of silver; small coins are
  `{{units:копейку|один ассарий}}`, `{{units:последнюю копейку|последний
  кодрант}}`; the thirty pieces of silver тридцать серебряных монет.
- **Fixed sayings** match through the book: "Истинно говорю вам" (L, B);
  the weeping and gnashing of teeth; "Змеиное отродье" (B) for the brood of
  vipers; the fulfilment formula «чтобы исполнилось слово, сказанное через
  пророка».

## 8. Status

A Russian rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.

## 9. Section headings and summaries

Where a book's `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json`
has languages other than English, add `"ru"` beside them, written from Open
Word Bible's own Russian wording. They are AI drafts until reviewed.
