# Spanish and Swahili: recurring terms for the rest of the New Testament

**Status: proposed, awaiting native Spanish and Swahili reviewers.** These
are the choices used to draft Spanish and Swahili for Matthew, Mark, Luke,
Acts, 1 and 2 Corinthians, Philippians, the Thessalonian and Pastoral letters,
Philemon, 1-3 John and Revelation, so the books read alike. They carry over
what John, Romans, Galatians, Hebrews and the other drafted books already
settled; `docs/swahili-style.md` and `docs/john-terms.md` still hold, and
the Spanish follows the patterns of the Spanish already in `content/`. If a
choice here changes, every passage drafted under it is revised.

Decision text stays in English, quoting the Spanish or Swahili words.

## Both languages

- Translate from the Greek, using the gloss, the English and the meaning
  decisions to see how a sentence was read; never from a reference Bible.
  Never reproduce a copyrighted Bible's wording (Reina-Valera 1960 and later,
  NVI, DHH, NTV; the Swahili Union Version, Habari Njema, Neno).
- Keep every `\v N ` marker where the English has it, and each language's own
  poetry line breaks (`\q `) where the English has them.
- Settings mirror the English spans where the language has the same choice:
  `christos`, `deity_pronoun` (Swahili only on free pronouns, per its style
  guide), `units`. Spanish adds `plural_you`; Swahili normally has no
  `gender` span, and Spanish only where Spanish really has two wordings
  ("hermanos" already includes sisters, so it stays plain).
- Measures: metric by default where the English converts to US units; wages
  for coins, as John 6:7 and 12:5.
- Readable may explain, as the English Readable does; follow the English
  Readable's explanations rather than adding new ones.
- Rendering decisions: zero to two per sentence, only where the language had
  to choose. A book-wide choice is recorded once, in its first passage of
  each book (one file).

## Recurring terms

| Greek (English) | Spanish | Swahili |
|---|---|---|
| kingdom of heaven (Matthew) | el reino de los cielos | ufalme wa mbinguni |
| kingdom of God | el reino de Dios | ufalme wa Mungu |
| Truly I tell you (single *amēn*) | En verdad {{plural_you:les\|os}} digo (L, B); {{plural_you:Les\|Os}} digo la verdad (R) | Kweli nawaambia (L, B); Nawaambia ukweli (R) |
| Son of Man | el Hijo del Hombre | Mwana wa Adamu |
| Son of David | Hijo de David | Mwana wa Daudi |
| scribes (*grammateis*) | los escribas (L, B); los maestros de la ley (R) | waandishi (L, B); walimu wa sheria (R) |
| experts in the law (*nomikoi*) | los expertos en la ley | wataalamu wa sheria |
| Pharisees, Sadducees | los fariseos, los saduceos | Mafarisayo, Masadukayo |
| Herodians | los herodianos | wafuasi wa Herode |
| chief priests, elders | los jefes de los sacerdotes, los ancianos | wakuu wa makuhani, wazee |
| high priest | el sumo sacerdote | kuhani mkuu |
| tax collectors | los publicanos (L); los cobradores de impuestos (B, R) | watoza ushuru |
| sinners | pecadores | wenye dhambi |
| demon; unclean spirit | demonio; espíritu impuro (L, B), espíritu maligno (R) | pepo; pepo mchafu (L, B), pepo mbaya (R) |
| Gehenna | Gehena (L); el infierno (B, R) | Gehena (L); jehanamu (B, R) |
| Hades | el Hades (L, B); el lugar de los muertos (R) | Kuzimu |
| hypocrites | hipócritas | wanafiki |
| parable | parábola | mfano |
| repent, repentance | arrepentirse, arrepentimiento | kutubu, toba |
| gospel, good news | el evangelio (B where it names the message); la buena noticia (R) | Injili; habari njema (R) |
| baptize | bautizar | kubatiza |
| Sabbath | el sábado | Sabato |
| synagogue | la sinagoga | sinagogi |
| Gentiles, the nations | los gentiles; las naciones | watu wa mataifa; mataifa |
| church, assembly | la iglesia | kanisa |
| apostle | apóstol | mtume |
| saints (*hagioi*) | los santos (L); el pueblo santo de Dios (B); el pueblo de Dios (R) | watakatifu (L); watu watakatifu wa Mungu (B); watu wa Mungu (R) |
| brothers (*adelphoi*, believers) | hermanos | ndugu |
| slave (*doulos*) | esclavo (L); siervo (B, R), esclavo where slavery itself is meant | mtumwa (L); mtumishi (B, R), mtumwa where slavery itself is meant |
| the Lord (Jesus, God) | el Señor | Bwana |
| Sir (*kyrie*, polite) | señor | bwana |
| Teacher | Maestro | Mwalimu |
| Holy Spirit | el Espíritu Santo | Roho Mtakatifu |
| angel | ángel | malaika |
| grace, peace, glory | gracia, paz, gloria | neema, amani, utukufu |
| righteousness | justicia | haki |
| faith, believe | fe, creer | imani, kuamini |
| eternal life | vida eterna | uzima wa milele |
| the Lamb (Revelation) | el Cordero | Mwanakondoo |
| throne | el trono | kiti cha enzi |
| Alpha and Omega | el Alfa y la Omega | Alfa na Omega |
| woe | ¡ay! (L, B); as the English Readable explains it (R) | ole (L, B); as the English Readable (R) |
| Amen | Amén | Amina |
| overseer (*episkopos*) | supervisor (L, B); líder de la iglesia (R) | mwangalizi (L, B); kiongozi wa kanisa (R) |
| elders (church office) | ancianos (L, B); líderes de la iglesia (R) | wazee (L, B); viongozi wa kanisa (R) |
| godliness (*eusebeia*) | piedad | uchaji wa Mungu |
| sound teaching | la enseñanza sana | mafundisho mazima |
| self-controlled, sensible | sensato, sensatez | wenye kiasi |
| steward (*oikonomos*) | administrador | msimamizi |
| myths | mitos | ngano |
| heart (*splanchna*) | entrañas (L); corazón (B, R) | moyo |
| look (*idou*) | mira (L); omitted or reworded (B, R) as the English | tazama |
| the Sea of Galilee | el mar (L); el lago (B, R) | bahari (L); ziwa (B, R) |
| wind, winds | viento(s) | upepo (never plural "pepo", which is also "demons") |
| the evil one | el maligno | yule mwovu |
| antichrist | anticristo (no christos span) | mpinga-Kristo |
| little children (*teknia*) | hijitos | watoto wadogo (L); wanangu wapendwa (B, R) |
| beloved (one person) | amado (L); querido amigo (B, R) | mpendwa (L); rafiki mpendwa (B, R) |
| regret, change one's mind (*metamelomai*) | cambiar de parecer (not "arrepentirse") | kubadili nia (not "kutubu") |
| tenant farmers (*geōrgoi*) | labradores (L, R); arrendatarios (B) | wakulima |
| authority, right (*exousia*) | autoridad; derecho | mamlaka; ruhusa (not "haki") |
| disciples | discípulos (every level, even where the English Readable says "followers") | wanafunzi (every level) |
| blessed (*makarioi*) | dichosos | heri |
| weeds (*zizania*) | cizaña (L, B); mala hierba (R) | magugu |
| the end of the age | el fin de la era (L, B); el fin del mundo (R) | mwisho wa zama hizi (L, B); mwisho wa dunia (R) |
| lord, master (in parables) | señor | bwana |
| tetrarch | tetrarca (L, B); gobernante (R) | mtawala |
| mighty works (*dynameis*) | obras poderosas (L, B); milagros (R) | matendo ya nguvu (L, B); miujiza (R) |
| ghost (*phantasma*) | fantasma | mzuka |
| you of little faith | gente de poca fe | wenye imani ndogo |
| basket: *kophinos*; *spyris* | canasta; cesto grande | kikapu; kikapu kikubwa |
| Jesus's brothers | sus hermanos | ndugu zake |
| centurion | centurión (L, B); oficial del ejército romano (R) | akida (L, B); afisa wa jeshi la Kirumi (R) |
| lawlessness (*anomia*) | iniquidad (L); maldad (B, R) | uasi |
| gate (of a city, a road) | puerta | lango |
| harvest, workers | cosecha, trabajadores | mavuno, wafanyakazi |
| governors | gobernadores | magavana (L, B); watawala (R) |
| synagogues (plural) | sinagogas | masinagogi |
| mercy (*eleos*) | misericordia | huruma |
| sacrifice | sacrificio | dhabihu |
| Beelzebul | Beelzebul | Beelzebuli |
| servant (*diakonos*), serve | servidor, servir | mhudumu, kuhudumu |
| phylacteries | filacterias | visanduku vya maandiko |
| coming (*parousia*) | venida | kuja |
| the elect | los elegidos | wateule (L); waliochaguliwa (B, R) |
| lightning | relámpago | umeme wa radi |
| false christs | falsos {{christos:cristos\|mesías}} | {{christos:makristo\|masihi}} wa uongo |
| tomb (*mnēmeion*) | el sepulcro (L, B); la tumba (R) | kaburi |
| at the right (hand) | a la derecha (de) | upande wa kulia (wa) |

## Spanish

- Quotation marks «», with “ ” inside and ‘ ’ inside those. A question or
  exclamation inside a quotation has both marks: «¿...?».
- Plural "you": every second-person plural form, pronoun or verb, is a
  `{{plural_you:ustedes form|vosotros form}}` span, default Latin American;
  the span covers the smallest whole word or phrase that changes.
- `christos`: `{{christos:Cristo|el Mesías}}`; "Jesus Christ" is
  `{{christos:Jesucristo|Jesús, el Mesías}}`; "Christ Jesus" is
  `{{christos:Cristo Jesús|el Mesías Jesús}}`; take in "de" where the
  article contracts (`{{christos:de Cristo|del Mesías}}`). With the
  article, as a title: `el {{christos:Cristo|Mesías}}`.
- `deity_pronoun`: `{{deity_pronoun:él|Él}}`, `lo|Lo`, `le|Le`, `sí
  mismo|Sí mismo`, and the possessive `su|Su`, wherever the English marks
  the pronoun, free clitics and pronouns included (lo, le, te, tú, ti); a clitic joined to the verb ("sígueme") and "conmigo", "contigo" take no span. "Jesús mismo" is an adjective and takes no
  span.
- Names in their usual Spanish form: Jesús, Juan, Pedro, Santiago (James),
  Mateo, Marcos, Lucas, Pablo, Bernabé, Esteban, Felipe, Herodes, Pilato,
  Jerusalén, Galilea, Cafarnaúm, Nazaret, Belén, Moisés, Elías, Isaías.

- Where "su" with ustedes could be misread, the span spells it out:
  `{{plural_you:la paz de ustedes|vuestra paz}}`.
- A gender span goes only where the English has one; it takes in the whole
  phrase that agrees (`{{gender:una persona sensata|un hombre sensato}}`).
- A single person is addressed with "tú", never "usted".
- A singular *adelphos* meaning any believer may take
  `{{gender:su hermano o hermana|su hermano}}`, as James 1:9 does.

## Swahili

- Quotation marks as in English, straight in `content/`.
- Names in their usual Swahili form: Yesu, Yohana, Petro, Yakobo, Mathayo,
  Marko, Luka, Paulo, Barnaba, Stefano, Filipo, Herode, Pilato, Yerusalemu,
  Galilaya, Kapernaumu, Nazareti, Bethlehemu, Musa, Eliya, Isaya, Daudi,
  Ibrahimu, Sulemani, Ninawi, Habili, Zakaria, Yudea.
- Narrative: *-li-* for the first verb of a sequence, *-ka-* for those that
  follow (Balanced and Readable); Literal keeps the historic present
  ("anasema") where the Greek has it.
