# French, Spanish and Swahili: the Pentateuch

**Status: proposed, awaiting native French, Spanish and Swahili reviewers.**
These are the choices used to draft Genesis to Deuteronomy in French, Spanish
and Swahili, the first Old Testament books in French and Swahili, so that
five books drafted in parallel read as one translation. `docs/french-style.md`,
`docs/swahili-style.md` and `docs/nt-spanish-swahili-terms.md` still hold;
the Spanish follows the Spanish of Genesis 1–14, already in `content/`. If a
choice here changes, every passage drafted under it is revised.

Decision text stays in English, quoting the French, Spanish or Swahili words.

## All three languages

- Translate from the Hebrew, using the literal gloss, the English and the
  meaning decisions to see how a sentence was read. Never from a reference
  Bible, and never reproduce a copyrighted Bible's wording (Segond 21, NBS,
  Colombe, TOB, Bible de Jérusalem, Semeur, Parole de Vie, Français courant;
  Reina-Valera 1960 and later, NVI, DHH, NTV, LBLA, BTX; the Swahili Union
  Version, Habari Njema, Neno, Kiswahili Contemporary Version). Familiar
  verses (Genesis 1, Exodus 20, Deuteronomy 6) pull hardest: draft from the
  gloss and rewrite any sentence that matches a well-known version for more
  than a short common phrase.
- Keep every `\v N ` marker where the English has it, and each level's own
  poetry breaks (`\q `) where the English level has them (Genesis 49,
  Exodus 15, Numbers 23–24, Deuteronomy 32–33).
- Settings mirror the English spans where the language has the same choice:
  `divine_name`, `deity_pronoun` (Swahili only on free pronouns), `units`,
  `gender` (French and Spanish where they really have two wordings; Swahili
  normally none). Spanish adds `plural_you` wherever a plural "you" is
  addressed: `{{plural_you:ustedes|vosotros}}` and the verb forms with it, as
  Genesis 1:28 does.
- Narrative tenses follow each style guide: French *passé simple* at L and
  B, *passé composé* at R; Spanish preterite; Swahili *-li-* then *-ka-*.
  Laws and instructions (Exodus 20–40, Leviticus, much of Numbers,
  Deuteronomy's speeches) use the language's ordinary forms for commands:
  French future or present ("tu ne tueras pas", "il apportera") at L and B,
  "tu dois", "il faut" or the imperative at R; Spanish future at L and B
  ("no matarás", "traerá"), "debe", "tiene que" or the imperative at R;
  Swahili subjunctive or *-ta-* ("usiue", "atamleta") at L and B, *lazima*
  or plain commands at R.
- Rendering decisions: zero to two per sentence, only where the language had
  to choose. A book-wide choice is recorded once, in its first passage of
  each book (one file); later chapters just follow it.
- Measures: metric by default where the English converts, the original unit
  as the alternative; Literal keeps the original unit, as the English does.
  Where the English has no units span, neither does the translation. Use the
  same values as the English conversion, in metric: cubit 45 cm (a
  "handbreadth" 7.5 cm), shekel 11.5 g, beka 5.7 g, gerah 0.6 g, talent 34
  kg, mina 0.6 kg, ephah 22 litres (a tenth of an ephah 2.2 litres), omer 2.2
  litres, seah 7 litres, hin 3.7 litres, homer 220 litres, cor 220 litres.
  Round as the English rounds ("about 4 ounces" → "about 115 g"). French and
  Spanish write decimals with a comma (1,10 m) and thousands with a space
  (1 000); Swahili writes decimals with a point and thousands with a comma.
  Days, years, ages and counts are not units.

## The names of God

| Hebrew (English) | French | Spanish | Swahili |
|---|---|---|---|
| YHWH (the LORD) | `{{divine_name:le SEIGNEUR\|Yahvé}}`, `du SEIGNEUR\|de Yahvé`, `au SEIGNEUR\|à Yahvé`, `Le SEIGNEUR\|Yahvé` at a sentence start | `{{divine_name:el SEÑOR\|Yahvé}}`, `del SEÑOR\|de Yahvé`, `al SEÑOR\|a Yahvé`, `El SEÑOR\|Yahvé` | `{{divine_name:BWANA\|Yahwe}}` |
| YHWH Elohim (the LORD God) | `{{divine_name:le SEIGNEUR\|Yahvé}} Dieu` | `{{divine_name:el SEÑOR\|Yahvé}} Dios` | `{{divine_name:BWANA\|Yahwe}} Mungu` |
| Adonai YHWH (Lord GOD) | le Seigneur `{{divine_name:DIEU\|Yahvé}}` | Señor `{{divine_name:DIOS\|Yahvé}}` | Bwana `{{divine_name:MUNGU\|Yahwe}}` |
| Adonai (Lord) | le Seigneur | el Señor | Bwana |
| Elohim (God) | Dieu | Dios | Mungu |
| El Shaddai (God Almighty) | le Dieu tout-puissant | el Dios Todopoderoso | Mungu Mwenyezi |
| El Elyon (God Most High) | le Dieu Très-Haut | el Dios Altísimo | Mungu Aliye Juu Kabisa |
| the angel of the LORD | l’ange du SEIGNEUR | el ángel del SEÑOR | malaika wa BWANA |

The span takes in the article and its contraction, so that both options read
naturally. The French default is "le SEIGNEUR" in capitals, like the English
"the LORD" and the Spanish "el SEÑOR"; "l’Éternel", the Segond tradition, is
the alternative a reviewer may prefer, and the first passage of each book
records it in a decision. The Swahili default is *BWANA* in capitals, with
*Yahwe* as the alternative. Exodus 3:14–15 and 6:2–3, where the name itself
is the subject, follow the English wording and decisions.

## Recurring terms

| Hebrew (English) | French | Spanish | Swahili |
|---|---|---|---|
| the sons of Israel | les `{{gender:enfants\|fils}}` d’Israël (L); les `{{gender:Israélites\|fils d’Israël}}` (B, R) | los hijos de Israel (L); los israelitas (B, R), no span: "hijos" already includes daughters | wana wa Israeli (L); Waisraeli (B, R), no span |
| Israel, Israelite(s) | Israël, israélite, les Israélites | Israel, israelita, los israelitas | Israeli, Mwisraeli, Waisraeli |
| Egypt, Egyptians; Pharaoh | l’Égypte, les Égyptiens; le pharaon (Pharaon as a name, no article, where the English says "Pharaoh" without one) | Egipto, los egipcios; el faraón | Misri, Wamisri; Farao |
| covenant | l’alliance | el pacto (as Genesis 6–17) | agano |
| bless, blessing; curse | bénir, la bénédiction; maudire | bendecir, la bendición; maldecir | kubariki, baraka; kulaani |
| holy; the Most Holy Place | saint; le lieu très saint | santo; el lugar santísimo | takatifu; Patakatifu pa Patakatifu |
| the holy place, the sanctuary | le lieu saint, le sanctuaire | el lugar santo, el santuario | mahali patakatifu |
| clean, unclean (ritually) | pur, impur | puro, impuro | safi, najisi |
| sin, iniquity, transgression | le péché, la faute, la transgression | el pecado, la iniquidad (L)/la maldad, la rebelión | dhambi, uovu, uasi |
| make atonement for | faire l’expiation pour (L, B); as the English at R | hacer expiación por (L, B); as the English at R | kufanya upatanisho kwa ajili ya |
| the tent of meeting | la tente de la Rencontre | la Tienda del Encuentro | Hema la Kukutania |
| the tabernacle (*mishkan*) | la Demeure (L, B); as the English at R | el tabernáculo | maskani |
| the ark (of the covenant, of the testimony) | l’arche (de l’alliance, du Témoignage) | el arca (del pacto, del Testimonio) | sanduku (la agano, la Ushuhuda) |
| Noah's ark | l’arche | el arca | safina |
| the testimony (*ʿedut*, the tablets) | le Témoignage | el Testimonio | Ushuhuda |
| the atonement cover (*kapporet*) | le propitiatoire | el propiciatorio | kiti cha rehema |
| cherub, cherubim | un chérubin, les chérubins | un querubín, los querubines | kerubi, makerubi |
| altar | l’autel | el altar | madhabahu |
| priest; high priest | le prêtre; le grand prêtre | el sacerdote; el sumo sacerdote | kuhani, makuhani; kuhani mkuu |
| Levites | les Lévites | los levitas | Walawi |
| ephod; breastpiece; Urim and Thummim | l’éphod; le pectoral; les ourim et les toummim | el efod; el pectoral; el urim y el tumim | efodi; kifuko cha kifuani; Urimu na Thumimu |
| lampstand | le chandelier | el candelabro | kinara cha taa |
| burnt offering | l’holocauste | el holocausto | sadaka ya kuteketezwa |
| grain offering | l’offrande végétale | la ofrenda de cereal | sadaka ya nafaka |
| sin offering | le sacrifice pour le péché | el sacrificio por el pecado | sadaka ya dhambi |
| guilt offering | le sacrifice de réparation | el sacrificio por la culpa | sadaka ya hatia |
| peace offering (*shelamim*) | le sacrifice de communion | el sacrificio de paz | sadaka ya amani |
| food offering (*ʾishsheh*) | l’offrande consumée par le feu | la ofrenda quemada | sadaka ya kuteketezwa kwa moto |
| soothing aroma | une odeur apaisante (L, B); une odeur qui plaît (R) | aroma grato (L, B); olor agradable (R) | harufu ya kupendeza |
| without defect | sans défaut | sin defecto | isiyo na kasoro |
| statute; rule; commandment | la prescription, la loi; la règle; le commandement | el estatuto; la norma; el mandamiento | kanuni; agizo; amri |
| a lasting statute | une loi perpétuelle | un estatuto perpetuo | kanuni ya kudumu milele |
| the congregation (*ʿedah*); the assembly (*qahal*) | la communauté; l’assemblée | la comunidad; la asamblea | jumuiya; kusanyiko |
| tribe; clan; father's house | la tribu; le clan; la famille | la tribu; el clan; la familia | kabila; ukoo; jamaa |
| the Sabbath | le sabbat | el sábado (L, B); el día de descanso where the English Readable explains | Sabato |
| the Passover; Unleavened Bread | la Pâque; la fête des Pains sans levain | la Pascua; la fiesta de los Panes sin Levadura | Pasaka; Sikukuu ya Mikate Isiyotiwa Chachu |
| the Day of Atonement | le jour des Expiations | el día de la Expiación | Siku ya Upatanisho |
| serious skin disease (*tsaraʿat*) | une maladie de peau grave (B, R), "lèpre" in a decision | una enfermedad grave de la piel | ugonjwa mbaya wa ngozi |
| steadfast love (*ḥesed*) | l’amour loyal (L), l’amour fidèle (B, R), la fidélité; now follows `psalms-proverbs-five-languages-terms.md` (was « amour fidèle » at L as the English level) | el amor fiel | upendo usiokoma, fadhili |
| Sheol | le séjour des morts (L: le Shéol) | el Seol (L); el lugar de los muertos (B, R) | Kuzimu |
| the land flowing with milk and honey | un pays où coulent le lait et le miel | una tierra que fluye leche y miel | nchi itiririkayo maziwa na asali |
| the wilderness | le désert | el desierto | jangwa, nyika |
| slave, servant (*ʿeved*) | esclave (L); serviteur (B, R); esclave at every level for slavery in Egypt and for slaves bought and sold | esclavo (L); siervo (B, R), as above | mtumwa (L); mtumishi (B, R), as above |
| foreigner, sojourner (*ger*) | l’étranger, l’immigré | el extranjero, el inmigrante | mgeni |
| firstborn | le premier-né | el primogénito | mzaliwa wa kwanza |

## Names

Proper names take their usual form in each language. Keep a list for the
book as you draft and use one form throughout.

| English | French | Spanish | Swahili |
|---|---|---|---|
| Adam, Eve, Cain, Abel, Seth | Adam, Ève, Caïn, Abel, Seth | Adán, Eva, Caín, Abel, Set | Adamu, Hawa, Kaini, Habili, Sethi |
| Noah, Shem, Ham, Japheth | Noé, Sem, Cham, Japhet | Noé, Sem, Cam, Jafet | Nuhu, Shemu, Hamu, Yafethi |
| Abram, Abraham; Sarai, Sarah | Abram, Abraham; Saraï, Sara | Abram, Abraham; Saray, Sara | Abramu, Abrahamu; Sarai, Sara |
| Lot, Hagar, Ishmael, Isaac | Loth, Agar, Ismaël, Isaac | Lot, Agar, Ismael, Isaac | Lutu, Hajiri, Ishmaeli, Isaka |
| Rebekah, Esau, Jacob, Laban | Rébecca, Ésaü, Jacob, Laban | Rebeca, Esaú, Jacob, Labán | Rebeka, Esau, Yakobo, Labani |
| Leah, Rachel, Bilhah, Zilpah | Léa, Rachel, Bilha, Zilpa | Lea, Raquel, Bilhá, Zilpá | Lea, Raheli, Bilha, Zilpa |
| Reuben, Simeon, Levi, Judah | Ruben, Siméon, Lévi, Juda | Rubén, Simeón, Leví, Judá | Reubeni, Simeoni, Lawi, Yuda |
| Dan, Naphtali, Gad, Asher | Dan, Nephtali, Gad, Aser | Dan, Neftalí, Gad, Aser | Dani, Naftali, Gadi, Asheri |
| Issachar, Zebulun, Dinah | Issacar, Zabulon, Dina | Isacar, Zabulón, Dina | Isakari, Zabuloni, Dina |
| Joseph, Benjamin, Ephraim, Manasseh | Joseph, Benjamin, Éphraïm, Manassé | José, Benjamín, Efraín, Manasés | Yusufu, Benyamini, Efraimu, Manase |
| Moses, Aaron, Miriam, Joshua, Caleb | Moïse, Aaron, Myriam, Josué, Caleb | Moisés, Aarón, Miriam, Josué, Caleb | Musa, Haruni, Miriamu, Yoshua, Kalebu |
| Jethro, Balaam, Balak, Korah, Phinehas | Jéthro, Balaam, Balak, Coré, Phinéas | Jetro, Balaam, Balac, Coré, Finés | Yethro, Balaamu, Balaki, Kora, Finehasi |
| Canaan, Sinai, Horeb, Jordan, Moab, Edom | Canaan, le Sinaï, l’Horeb, le Jourdain, Moab, Édom | Canaán, el Sinaí, Horeb, el Jordán, Moab, Edom | Kanaani, Sinai, Horebu, Yordani, Moabu, Edomu |
| Amorites, Canaanites, Hittites | les Amoréens, les Cananéens, les Hittites | los amorreos, los cananeos, los hititas | Waamori, Wakanaani, Wahiti |

Other names: French follows the usual French form where one is established,
otherwise transcribes the Hebrew as the English does, with French accents
where French writes them (Éliézer, Ésaü); Spanish follows the usual Spanish
form (with accents: Aarón, Leví, Neftalí); Swahili follows the usual Swahili
form, ending in a vowel where Swahili writes one (Kalebu, Moabu).
