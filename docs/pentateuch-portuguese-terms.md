# Portuguese: the Pentateuch and the Old Testament

**Status: proposed, awaiting a native Brazilian Portuguese reviewer.** The
choices used to draft the Old Testament in Portuguese, so that books drafted
in parallel read as one translation. `docs/portuguese-style.md` still holds
(section 10 on poetry and the Old Testament); these tables add the recurring
words. If a choice here changes, every passage drafted under it is revised.
Decision text stays in English, quoting the Portuguese words.

## Drafting

- Translate from the Hebrew, using the literal gloss, the English and the
  meaning decisions to see how a verse was read; never from a reference
  Bible, and never reproduce a copyrighted Portuguese Bible's wording (NVI,
  NVT, NAA, ARA, ARC, ACF, NTLH, A Mensagem, Bíblia de Jerusalém, CNBB,
  Pastoral, Ave-Maria). Familiar chapters (Genesis 1, Exodus 20,
  Deuteronomy 6, Psalm 23) pull hardest: draft from the gloss and rewrite any
  sentence that matches a well-known version for more than a short common
  phrase.
- A Hebrew record holds whole verses. Keep every `\v N ` marker where the
  English has it, and each level's own poetry breaks (`\q `) where the
  English level has them (Genesis 49, Exodus 15, Numbers 23–24,
  Deuteronomy 32–33, the poetic books).
- Narrative: *pretérito perfeito* at every level. Literal keeps the chain of
  "e" that the Hebrew narrative tense makes; Balanced and Readable join
  clauses with ordinary Portuguese connectives, as the English does.
- Laws and instructions: future at Literal and Balanced ("não matarás",
  "ele trará"), "deve", "tem de" or the imperative at Readable. God speaks
  to one person, and to Israel addressed in the singular, with "tu"; to
  Israel or a group addressed in the plural, with "vocês" (docs/portuguese-
  style.md, section 4). People speak to each other with "você"; to a king,
  a master or a superior with "o senhor" ("meu senhor", "o rei", "o seu
  servo" in the courtly third person where the Hebrew uses it).
- Settings mirror the English spans where Portuguese has the same choice:
  `divine_name`, `deity_pronoun`, `units`, `gender` (only where Portuguese
  really has two wordings; "filhos" already includes daughters).
- Measures: metric by default where the English converts, the original unit
  as the alternative; Literal keeps the original unit. Where the English has
  no units span, neither does the Portuguese. Use the English values in
  metric: cubit 45 cm (palmo 7,5 cm), shekel 11,5 g, beka 5,7 g, gerah
  0,6 g, talent 34 kg, mina 0,6 kg, ephah 22 litros, omer 2,2 litros, seah
  7 litros, hin 3,7 litros, homer and cor 220 litros. Decimals with a comma
  (1,10 m), thousands with a point (1.000).
- Rendering decisions: zero to two per verse, only where Portuguese had to
  choose. A book-wide choice is recorded once, in its first passage of each
  book; later chapters follow it.

## The names of God

| Hebrew (English) | Portuguese |
|---|---|
| YHWH (the LORD) | `{{divine_name:o SENHOR\|Javé}}`, `{{divine_name:do SENHOR\|de Javé}}`, `{{divine_name:ao SENHOR\|a Javé}}`, `{{divine_name:pelo SENHOR\|por Javé}}`, `{{divine_name:no SENHOR\|em Javé}}`, `{{divine_name:O SENHOR\|Javé}}` at a sentence start |
| YHWH Elohim (the LORD God) | `{{divine_name:o SENHOR\|Javé}} Deus` |
| Adonai YHWH (Lord GOD) | o Senhor `{{divine_name:DEUS\|Javé}}` |
| Adonai (Lord) | o Senhor |
| Elohim (God) | Deus |
| El Shaddai (God Almighty) | o Deus Todo-Poderoso |
| El Elyon (God Most High) | o Deus Altíssimo |
| the angel of the LORD | o anjo `{{divine_name:do SENHOR\|de Javé}}` |
| YHWH Tsevaot (the LORD of hosts) | `{{divine_name:o SENHOR\|Javé}}` dos Exércitos |

The span takes in the article and its contraction, so that both options read
naturally ("o Javé" is wrong). *Jeová* is not used. Exodus 3:14–15 and 6:2–3,
where the name itself is the subject, follow the English wording and
decisions.

## Recurring terms

| Hebrew (English) | Portuguese |
|---|---|
| the sons of Israel | os filhos de Israel (L); os israelitas (B, R); no span: "filhos" already includes daughters |
| Egypt, Egyptians; Pharaoh | o Egito, os egípcios; o faraó (Faraó as a name, no article, where the English says "Pharaoh" without one) |
| covenant | a aliança |
| bless, blessing; curse | abençoar, a bênção; amaldiçoar, a maldição |
| holy; the Most Holy Place | santo; o Lugar Santíssimo |
| the holy place, the sanctuary | o lugar santo, o santuário |
| clean, unclean (ritually) | puro, impuro |
| sin, iniquity, transgression | o pecado, a iniquidade (L) / a maldade, a rebeldia |
| make atonement for | fazer expiação por (L, B); as the English at R |
| the tent of meeting | a tenda do encontro |
| the tabernacle (*mishkan*) | o tabernáculo |
| the ark (of the covenant, of the testimony); Noah's ark | a arca (da aliança, do Testemunho); a arca |
| the testimony (*ʿedut*) | o Testemunho |
| the atonement cover (*kapporet*) | o propiciatório |
| cherub, cherubim | um querubim, os querubins |
| altar; priest; high priest; Levites | o altar; o sacerdote; o sumo sacerdote; os levitas |
| ephod; breastpiece; Urim and Thummim | o éfode; o peitoral; o Urim e o Tumim |
| lampstand | o candelabro |
| burnt offering; grain offering | o holocausto; a oferta de cereal |
| sin offering; guilt offering | a oferta pelo pecado; a oferta pela culpa |
| peace offering (*shelamim*) | o sacrifício de comunhão |
| food offering (*ʾishsheh*) | a oferta queimada |
| soothing aroma | aroma agradável |
| without defect | sem defeito |
| statute; rule; commandment | o estatuto; a ordenança; o mandamento |
| a lasting statute | um estatuto perpétuo |
| the congregation (*ʿedah*); the assembly (*qahal*) | a comunidade; a assembleia |
| tribe; clan; father's house | a tribo; o clã; a família |
| the Sabbath | o sábado |
| the Passover; Unleavened Bread | a Páscoa; a festa dos Pães sem Fermento |
| the Day of Atonement | o Dia da Expiação |
| serious skin disease (*tsaraʿat*) | uma doença de pele grave (B, R), "lepra" in a decision |
| steadfast love (*ḥesed*) | as the English level: o amor leal, a lealdade, a bondade fiel |
| Sheol | o Sheol (L); o mundo dos mortos (B, R) |
| the land flowing with milk and honey | uma terra onde corre leite e mel |
| the wilderness | o deserto |
| slave, servant (*ʿeved*) | escravo (L); servo (B, R); escravo at every level for slavery in Egypt and for slaves bought and sold |
| foreigner, sojourner (*ger*) | o estrangeiro, o imigrante |
| firstborn | o primogênito |

## Names

Proper names take their usual Brazilian form; keep one form through a book.

| English | Portuguese |
|---|---|
| Adam, Eve, Cain, Abel, Seth | Adão, Eva, Caim, Abel, Sete |
| Noah, Shem, Ham, Japheth | Noé, Sem, Cam, Jafé |
| Abram, Abraham; Sarai, Sarah | Abrão, Abraão; Sarai, Sara |
| Lot, Hagar, Ishmael, Isaac | Ló, Agar, Ismael, Isaque |
| Rebekah, Esau, Jacob, Laban | Rebeca, Esaú, Jacó, Labão |
| Leah, Rachel, Bilhah, Zilpah | Lia, Raquel, Bila, Zilpa |
| Reuben, Simeon, Levi, Judah | Rúben, Simeão, Levi, Judá |
| Dan, Naphtali, Gad, Asher | Dã, Naftali, Gade, Aser |
| Issachar, Zebulun, Dinah, Joseph, Benjamin | Issacar, Zebulom, Diná, José, Benjamim |
| Ephraim, Manasseh; Tamar, Perez, Zerah | Efraim, Manassés; Tamar, Perez, Zerá |
| Moses, Aaron, Miriam; Joshua, Caleb | Moisés, Arão, Miriã; Josué, Calebe |
| Pharaoh; Potiphar; Melchizedek | Faraó; Potifar; Melquisedeque |
| Eden, Babel, Ur, Haran, Canaan | Éden, Babel, Ur, Harã, Canaã |
| Sodom, Gomorrah, Bethel, Hebron, Beersheba | Sodoma, Gomorra, Betel, Hebrom, Berseba |
| Goshen, Sinai, Horeb, Kadesh, Moab, Edom | Gósen, Sinai, Horebe, Cades, Moabe, Edom |
| Amalek, Midian; the Jordan; the Nile | Amaleque, Midiã; o Jordão; o Nilo |
