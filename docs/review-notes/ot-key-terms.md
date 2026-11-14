# Old Testament key terms: measurement and rules

Item 18 of the consistency audits. Twenty Hebrew words were added to `data/key_terms.json` (language `hbo`, lemmas copied from `data/hbo/` by Strong's number). This note records how the drafted English rendered each one before the rule was settled, the rule chosen, what was harmonised, and how the other languages spread. Counts are of sentence records that contain the word; a record can show more than one candidate (a record with "loyal love and faithfulness" counts for both), and `<none>` means none of the measured candidates appears (often a pronoun or an idiom). Sections: Law (Genesis-Deuteronomy), history (Joshua-Esther), Psalms, wisdom (Job, Proverbs, Ecclesiastes, Song of Songs), prophets (Isaiah-Malachi, with Lamentations and Daniel).

Seventeen terms are checked by `owb.validate` (each English level must use one of the term's words, or a decision on the word must explain why not). *Nephesh*, *ruach* and *mishpat* are settled by sense rather than by one word, so they are listed with their rules and `"checked": false`. Three Psalms sentences whose fixes wait in `pending-psalms-patches-b.jsonl` are listed under `pending` in the data and skipped until the patch is applied.

## The hesed question

The article (articles/hesed-steadfast-love.md) says Literal "steadfast love" and Balanced "faithful love" in the Law and history, and "loyal love" at Literal and Balanced in the Psalms and the prophets. The whole-Old-Testament count (Balanced "loyal love" 165 records, "faithful love" 52) looked like a contradiction, but it is the same rule seen through uneven books: 126 of the 165 are in the Psalms. By section the data followed the article, with these exceptions:

- the temple refrain "for he is good, his hesed is forever" in 1 Chronicles 16:34, 41; 2 Chronicles 5:13; 7:3, 6; 20:21, and 2 Samuel 22:51 (= Psalm 18:51), said "loyal love": kept, and made the rule (a historical book that sings a psalm keeps the Psalms' wording); Ezra 3:11, the same refrain, said "steadfast/faithful love" and was brought into line;
- Job 6:14; 10:12; 37:13 used the Law/history wording; the article named no rule for the wisdom books, whose other uses (Proverbs) say "loyal love", so the wisdom books now follow the Psalms;
- Jonah 4:2 said "steadfast/faithful love" while Joel 2:13 said "loyal love" for the same quotation of Exodus 34:6 (the open question the article flagged): Jonah now follows its section, so the two prophets agree;
- Genesis 24:12, 14; 32:11 and Proverbs 16:6; 19:22 used "loyalty", "kindness" or "kept faith": harmonised.

The sectional rule was kept rather than replaced by one wording for the whole canon: the article states it, the decisions and footnotes of some 230 records already explain it, and the change would have touched about a hundred Law and history sentences for no gain in meaning. The article now states the wisdom-book and refrain rules.

## Each term

### loyal love (hesed) (חֶסֶד, H2617), 239 records

Rule: Settled by section (articles/hesed-steadfast-love.md). In the Law and the historical books (Genesis to Esther) Literal says "steadfast love" and Balanced "faithful love"; in Job, Psalms, Proverbs, Ecclesiastes, Song of Songs, Lamentations and the prophets Literal and Balanced say "loyal love". Readable says "faithful love" everywhere. Where a historical book sings or repeats a psalm (the refrain "his loyal love is forever" in 1 and 2 Chronicles and Ezra 3:11; 2 Samuel 22, which is Psalm 18) it keeps the Psalms' wording, and quotations of Exodus 34:6 follow their own book's section (Numbers 14:18 and Nehemiah 9:17 as Exodus; Joel 2:13 and Jonah 4:2 as the Psalms). A departure (Esther 2:9 "favor", Micah 6:8 "loyalty", Isaiah 40:6 "loyalty") needs a decision.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | steadfast love 12, loyalty 5, faithfulness 4, love 3, favor 3 | steadfast love 38, loyal love 8, faithfulness 4, <none> 2, kindness 2 | loyal love 127, faithfulness 23, favor 2, love 2, goodness 2 | loyal love 12, faithfulness 4 | loyal love 28, love 4, faithfulness 3, kindness 1, loyalty 1 |
| B | faithful love 12, love 3, kindness 3, loyalty 2, <none> 2 | faithful love 37, loyal love 8, <none> 3, faithfulness 2, favor 2 | loyal love 126, faithfulness 20, love 3, goodness 2, mercy 1 | loyal love 10, faithfulness 4, <none> 1, loyalty 1 | loyal love 27, love 3, faithfulness 2, loyalty 2, kindness 1 |
| R | faithful love 12, <none> 8, love 3, kindness 1, mercy 1 | faithful love 45, <none> 5, mercy 2, loyalty 1, love 1 | faithful love 112, love 13, faithfulness 5, kindness 4, <none> 4 | faithful love 6, <none> 6 | faithful love 27, love 5, mercy 4, faithfulness 2, <none> 1 |

Senses stated by meaning decisions: "loyal love" 98, "the refrain" 26, "steadfast love" 20, "loyal love and faithfulness" 5, "chesed" 3, "my steadfast love" 2, "keeping the covenant and the steadfast love" 2, "his faithful deeds" 2.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (239): amor fiel 217, su amor 65, tu amor 48, fiel y 43
- fr (239): fidèle 222, amour 164, dure toujours 43, car son 38
- sw (239): usiokoma 193, upendo 199, unadumu 43, uaminifu 49
- vi (239): thương thành 200, thành tín 207, tình yêu 200, yêu thương 201
- ko (239): 한결같은 217, 사랑을 74, 사랑이 64, 영원하다 39
- pt (239): leal 201, amor 200, dura para 43, para sempre 50
- am (239): ጽኑ 194, ፍቅር 59, ለዘላለም ይኖራል። 36, ፍቅሩም 35
- hi (31): अटल प्रेम 24, कृपा 11, अपना अटल 7, प्रेम और 5
- ru (31): милость 12, неизменную любовь 10, неизменной 7, любви 4

### law, instruction (torah) (תּוֹרָה, H8451), 214 records

Rule: "law" for the Law of Moses and the Book of the Law (the Law and the historical books) at Literal and Balanced; Readable says "law" or "teaching", and "rules" for the priestly regulations ("this is the law of the burnt offering", Leviticus 6-7, 11-15; Numbers 5-6). In the Psalms and the prophets Literal and Balanced say "instruction" and Readable "teaching". In Proverbs and Job, where it is a parent's or a teacher's instruction, "teaching" at every level.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | law 54, command 2, instruction 1 | law 63, teaching 1, <none> 1, rule 1 | instruction 35 | teaching 8, instruction 3, law 3, command 2 | instruction 40, law 7 |
| B | law 40, instruction 13, ruling 5, command 3, teaching 2 | law 63, ruling 9, command 3, <none> 1, teaching 1 | instruction 35, ruling 1 | teaching 8, instruction 5, command 4, <none> 1 | instruction 40, law 7, ruling 2 |
| R | rule 26, teaching 25, law 16, command 5 | law 48, teaching 22, command 14, rule 9, instruction 2 | teaching 33, law 2, <none> 2, rule 1 | teaching 8, <none> 4, command 4 | teaching 40, law 12, rule 3, ruling 1, instruction 1 |

Senses stated by meaning decisions: "instruction" 40, "law" 14, "the law" 4, "this law" 4, "instruction (torah)" 3, "my instruction" 3, "the book of the law of moses" 3, "the law of the lord" 2.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (214): ley 104, instrucción 76, libro 24, estatutos 24
- fr (214): loi 103, instruction 44, livre de 20, prescriptions 23
- sw (214): sheria 108, mafundisho 92, kitabu 24, kanuni 24
- vi (214): luật pháp 110, dạy 89, dỗ 64, pháp của 39
- ko (214): 가르침을 54, 율법을 27, 율법의 17, 기록된 20
- pt (214): lei 103, instrução 46, ensino 41, livro da 19
- am (214): ሕግ 77, መጽሐፍ 22, ትምህርት 12, በሙሴ 15
- hi (63): व्यवस्था 39, निर्देश 18, पुस्तक 12, इस 16
- ru (63): закона 22, слова этого 8, все слова 8, предписания о 7

### peace, well-being (shalom) (שָׁלוֹם, H7965), 209 records

Rule: "peace" by default at every level. Where it means someone's welfare or safety, Balanced and Readable may say "well", "safe", "safely" or "welfare"; "Is it peace?" is "Is all well?", and to ask about someone's peace is to greet them or ask how they are. "Man of my peace" is an idiom for a friend, and Balanced and Readable may say "friend"; other idioms take a rendering decision.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | peace 16, well 4, welfare 3, <none> 1 | peace 69, welfare 5, well 4, whole 3, greet 1 | peace 26, friend 1, <none> 1, safety 1 | peace 8, safe 1 | peace 65, welfare 3, secure 2, safety 1, <none> 1 |
| B | peace 11, well 7, <none> 3, safely 2, prosperity 1 | peace 44, <none> 10, safely 8, well 7, safe 6 | peace 21, friend 4, well 3, secure 2, whole 1 | peace 6, well 1, safe 1, secure 1 | peace 57, peaceful 4, safely 3, <none> 3, friend 3 |
| R | peace 10, well 5, <none> 5, safe 2, safely 2 | peace 34, <none> 16, safely 10, well 7, safe 6 | peace 18, safe 6, friend 4, <none> 3, well 2 | peace 5, safe 3, peaceful 1 | peace 57, safely 4, safe 4, <none> 4, well 4 |

Senses stated by meaning decisions: "peace" 33, "in peace" 8, "is it peace?" 5, "peace and stability" 2, "welfare" 2, "solomon ... peace" 1, "peace and quiet" 1, "peace and a covenant" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (209): paz 140, salvo 16, sano 12, bien 24
- fr (209): paix 140, sain 14, et sauf 13, va 20
- sw (209): amani 138, salama 35, mema 9, hofu 9
- vi (209): bình 155, an 142, hòa 21, hỏi 24
- ko (209): 평안히 22, 평화를 19, 평안을 19, 무사히 15
- pt (209): paz 136, bem 23, são e 9, respondeu 19
- am (209): ሰላም 48, ደኅና 14, ነውን 9, አለ። 13
- hi (51): शान्ति 19, कुशल से 8, से जाओ। 4, पूछा। 5
- ru (51): с миром 11, мира 4, здоров 3, благополучно 3

### soul, life, self (nephesh) (נֶפֶשׁ, H5315), 683 records

Rule: Settled by sense, so owb.validate does not hold the English to one word; a meaning decision says which sense a passage has. "soul" for the inner self that longs, grieves and praises ("my soul", Psalms); "life" where a life is at stake, saved or taken; "person" or "anyone" for a person in the laws; "throat", "appetite" or "desire" where the body or a craving is meant; "creature" or "being" for living beings (Genesis 1-2; 2:7 "a living being"). Literal keeps "soul" for the self; Balanced and Readable may say "I", "me" or "yourself" where "my soul" or "your soul" stands for the person. Never "spirit", which is ruach. (Not checked by the validator.)

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | person 67, soul 39, life 27, people 23, <none> 21 | life 48, soul 45, lives 18, heart 14, person 11 | soul 126, life 17, desire 6, heart 5, neck 2 | soul 42, life 36, person 13, heart 10, appetite 8 | soul 68, life 39, lives 15, people 14, himself 9 |
| B | <none> 54, person 31, anyone 31, people 31, life 20 | life 47, <none> 22, lives 20, heart 14, people 12 | <none> 56, life 36, people 13, soul 12, being 10 | life 29, <none> 23, soul 12, people 11, lives 8 | <none> 46, life 31, people 22, lives 16, heart 13 |
| R | <none> 66, people 38, person 37, anyone 26, life 17 | <none> 38, life 27, people 17, lives 16, heart 12 | <none> 72, people 41, life 14, lives 9, heart 8 | <none> 32, people 31, life 17, heart 8, yourself 7 | people 57, <none> 47, life 19, lives 13, themselves 10 |

Senses stated by meaning decisions: "my soul" 9, "soul" 8, "their soul" 5, "appetite" 4, "the soul" 4, "life" 3, "with all your heart and all your soul" 2, "your soul" 2.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (683): vida 205, alma 50, con todo 35, persona 40
- fr (683): vie 203, âme 46, mort 53, être 50
- sw (683): maisha 102, nafsi 73, uhai 76
- vi (683): mạng 164, sống 205, hồn 57, linh 48
- ko (683): 목숨을 155, 자신을 29
- pt (683): vida 204, alma 60, a minha 87, pessoa 42
- am (683): ሕይወቴን 35, ሕይወት 36
- hi (229): प्राण 37, किसी 54, अपने आप 25, से काट 18
- ru (229): жизнь 28, кто 46, себя 29, истреблён 14

### spirit, wind, breath (ruach) (רוּחַ, H7307), 348 records

Rule: Settled by sense (articles/wind-breath-and-spirit.md), so owb.validate does not hold the English to one word. "Spirit" with a capital where God's Spirit is meant; "spirit" for a person's spirit or a spirit God sends; "wind" for moving air, and "side" or "wind" for a quarter of the compass; "breath" for the breath of life. Where it is a mood or temper ("short of spirit", "his spirit revived") Balanced and Readable may say what the mood is ("quick-tempered", "felt alive again"). Where the sense is open (Genesis 1:2) a meaning decision says so. (Not checked by the validator.)

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | spirit 17, Spirit 8, wind 5, heart 4, breath 4 | spirit 31, Spirit 25, wind 4, anger 2, heart 2 | wind 16, spirit 14, heart 6, breath 5, Spirit 4 | spirit 31, wind 29, breath 19, heart 5, anger 4 | wind 50, spirit 41, Spirit 33, breath 16, heart 10 |
| B | spirit 13, Spirit 8, heart 5, wind 5, <none> 5 | Spirit 25, spirit 22, <none> 6, wind 4, side 2 | wind 14, spirit 13, breath 6, heart 6, Spirit 4 | wind 27, breath 20, spirit 20, <none> 9, anger 5 | wind 49, spirit 36, Spirit 33, breath 14, heart 11 |
| R | <none> 12, Spirit 8, breath 6, wind 5, spirit 3 | Spirit 25, spirit 13, <none> 12, wind 4, side 2 | wind 16, <none> 14, Spirit 4, breath 3, spirit 2 | wind 26, breath 18, <none> 18, spirit 13, anger 4 | wind 40, <none> 32, Spirit 32, spirit 17, breath 12 |

Senses stated by meaning decisions: "spirit" 9, "the spirit" 9, "my spirit" 6, "wind" 5, "breath" 5, "a spirit" 3, "a chasing of wind" 3, "a spirit of falsehood" 2.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (348): espíritu 169, viento 88, aliento 37, soplo 16
- fr (348): vent 91, l’esprit 88, souffle 52, un esprit 29
- sw (348): roho 170, upepo 94, pumzi 48, ndani 46
- vi (348): linh 123, gió 99, thần 121, hơi 45
- ko (348): 영이 80, 영을 41, 바람을 29, 바람이 19
- pt (348): espírito 167, vento 89, fôlego 24, sopro 26
- am (348): መንፈስ 102, ነፋስ 50, እስትንፋስ 25
- hi (61): आत्मा 36, हवा 6, बुरी 7, तब प्रभु 10
- ru (61): дух 32, сошёл 13, на него 12, злой 7

### holy (qadosh) (קָדוֹשׁ, H6918), 106 records

Rule: "holy" at every level; "the Holy One of Israel" in Isaiah, "holy ones" for heavenly beings. "Set apart" may explain it but does not replace it.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | holy 30, holy ones 1 | holy 8, Holy One 1 | holy 8, holy ones 4, Holy One 3 | Holy One 3, holy ones 2, holy 1 | Holy One 36, holy 9, holy ones 2 |
| B | holy 30, set apart 4, holy ones 1 | holy 8, Holy One 1 | holy 8, Holy One 3, set apart 2, holy ones 2, sacred 1 | Holy One 3, holy ones 2, holy 1 | Holy One 36, holy 9, holy ones 2 |
| R | holy 30, set apart 4 | holy 8, set apart 1, Holy One 1 | holy 9, <none> 3, set apart 1, Holy One 1, holy ones 1 | holy 3, <none> 2, Holy One 1 | Holy One 33, holy 13, holy ones 1 |

Senses stated by meaning decisions: "the holy one" 3, "his holy ones" 2, "the holy ones" 2, "the holy one of israel" 2, "a holy one" 1, "holy" 1, "a holy nation" 1, "city of the lord, zion of the holy one of israel" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (106): santo 83, de israel 36, porque yo 8, un lugar 8
- fr (106): saint 84, d’israël 36, un lieu 8, libérateur 6
- sw (106): mtakatifu 67, watakatifu 18, wa israeli 33, ni 46
- vi (106): thánh 106, đấng 53, của y-sơ-ra-ên 34, trời của 23
- ko (106): 거룩한 60, 거룩하신 29, 이스라엘의 34, 구별된 7
- pt (106): santo 86, de israel 36, senhor o 28, num lugar 8
- am (106): ቅዱስ 63, ቅዱሳን 11, በተቀደሰ 8, የእስራኤል 20
- hi (34): पवित्र 34, स्थान में 8, परमेश्वर 17, क्योंकि 13
- ru (34): свят 11, месте 8, потому что 10, я господь 6

### holiness, holy things (qodesh) (קֹדֶשׁ, H6944), 382 records

Rule: "holy" in "holy place", "Most Holy Place", "holy mountain", "holy things"; "holiness" for the quality ("the splendor of holiness"); "sanctuary" where it names the sanctuary; "dedicated" or "consecrated" for gifts given to God. Readable may say "temple" for the sanctuary.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | holy 115, sanctuary 34, holy place 19, holiness 16 | holy 52, holiness 5, holy place 5, consecrated 4, sanctuary 3 | holiness 19, holy 18, sanctuary 5, holy place 4 | holy 1 | holy 74, holiness 15, sanctuary 11, holy place 5 |
| B | holy 121, sanctuary 42, holy place 22, holiness 1 | holy 37, holy place 16, sanctuary 8, dedicated 8, consecrated 3 | holy 30, holy place 9, holiness 4, sanctuary 1, sacred 1 | holy 1 | holy 84, sanctuary 12, holy place 5, holiness 3, sacred 2 |
| R | holy 125, holy place 33, sanctuary 23, <none> 2 | holy 39, holy place 20, <none> 7, dedicated 1 | holy 34, holy place 8, <none> 2, holiness 1 | <none> 1 | holy 82, holy place 10, <none> 7, holiness 2 |

Senses stated by meaning decisions: "the holy place" 9, "most holy" 7, "the holy things" 6, "the splendor of holiness" 3, "holy convocation" 3, "holy things" 2, "holy things of david" 2, "the holy vessels" 2.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (382): santo 151, santa 60, santuario 63, santísimo 36
- fr (382): saint 135, sanctuaire 61, très 53, lieu 59
- sw (382): patakatifu 114, mtakatifu 64, mahali 91, matakatifu 40
- vi (382): thánh 378, nơi 124, lễ 129, vật 99
- ko (382): 거룩한 257, 한다 63, 거룩하게 32, 지극히 27
- pt (382): santo 136, santuário 64, santa 44, lugar 71
- am (382): ቅዱስ 84, በመቅደሱ 31, የተቀደሱ 30, የተቀደሰ 32
- hi (180): पवित्र 122, सम्मेलन 16, के मान 16, किलो 19
- ru (180): святилища 31, святыня 19, святилище 20, по мере 14

### covenant (berit) (בְּרִית, H1285), 264 records

Rule: "covenant" at every level, Readable included, for every covenant God makes (Genesis 9 and 17 as Exodus and Deuteronomy). For an agreement between peoples or rulers Literal keeps "covenant" or says "treaty", Balanced and Readable say "treaty", Readable also "agreement". "Men of your covenant" (allies) takes a rendering decision.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | covenant 75, <none> 1 | covenant 91, treaty 2 | covenant 21 | covenant 4 | covenant 70, pact 2 |
| B | covenant 75, treaty 1 | covenant 83, treaty 10 | covenant 20, treaty 1 | covenant 4 | covenant 65, treaty 3, <none> 2, pact 2 |
| R | covenant 68, agreement 5, <none> 3 | covenant 82, treaty 9, agreement 3 | covenant 18, <none> 2, treaty 1 | agreement 2, <none> 2 | covenant 50, agreement 15, treaty 3, <none> 2 |

Senses stated by meaning decisions: "covenant" 10, "the book of the covenant" 3, "the covenant" 2, "keeping the covenant and the steadfast love" 2, "make a covenant" 2, "the covenant and the steadfast love" 2, "peace and a covenant" 1, "entered into a covenant" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (264): pacto 247, arca del 40, el arca 36, tratado 12
- fr (264): alliance 140, l’arche de 40, conclue 19, rompu 14
- sw (264): agano 251, sanduku la 40, langu 48, la bwana 42
- vi (264): giao ước 248, ước của 99, lập 107, ước với 50
- ko (264): 언약을 137, 맺은 28, 언약의 25, 언약궤를 24
- pt (264): aliança 253, arca da 40, a arca 36, minha 56
- am (264): ኪዳን 162, ቃል 198, ጋር 109, ኪዳኔን 28
- hi (108): वाचा 101, साथ 47, का संदूक 20, बाँधी 15
- ru (108): завет 59, заключил 15, ковчег 21, мой 22

### make atonement (kipper) (כִּפֶּר, H3722), 94 records

Rule: "make atonement" ("atone") at every level in the rites of the Law and wherever a priest or God atones for sin; Readable may say that God "forgives" where he is the one who covers sin (Psalms, prophets). Other uses take a decision: covering with pitch (Genesis 6:14), appeasing (Genesis 32:21), buying off a disaster (Isaiah 47:11), making amends (Proverbs 16:6).

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | atonement 68, cleanse 2, purify 1, appease 1, cover 1 | atonement 5, <none> 1 | atone 2, <none> 1 | <none> 1, appease 1 | atonement 6, <none> 4, purify 2, atone 1, ransom 1 |
| B | atonement 68, cleanse 2, <none> 2 | atonement 5, pardon 1 | cover 2, wipe 1 | <none> 2 | atonement 7, <none> 4, purify 2, atone 1, forgive 1 |
| R | atonement 68, forgive 2, cover 1 | atonement 5, forgive 1 | forgive 2, wipe 1 | <none> 2 | atonement 6, <none> 5, forgive 2 |

Senses stated by meaning decisions: "make atonement" 3, "to make atonement" 2, "make atonement for her" 2, "make atonement for israel" 1, "make atonement for" 1, "make atonement for his land, his people" 1, "atonement was made" 1, "to make atonement for your lives" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (94): expiación 79, hará 38, por 82, pecado 35
- fr (94): l’expiation 78, pour 83, péché 37, fera 33
- sw (94): upatanisho 81, dhambi 42, kwa ajili 46, sadaka 41
- vi (94): chuộc tội 79, tội cho 70, để chuộc 28, lễ chuộc 34
- ko (94): 위하여 61, 속죄해야 20, 한다 40, 속죄하면 12
- pt (94): expiação 83, fará 34, pelo 45, pecado 35
- am (94): መሥዋዕት 30, ያስተሰርይለታል፤ 12, የኃጢአት 16, ይቅር 13
- hi (71): प्रायश्चित 69, लिए 68, पापबलि 20, याजक 26
- ru (71): умилостивление 66, за 68, совершит 30, грех 26

### mercy seat (kapporet) (כַּפֹּרֶת, H3727), 22 records

Rule: "mercy seat" at Literal and Balanced, Leviticus 16 included; Readable says what it is, "the lid" or "the cover" of the ark, and where it is first described (Exodus 25:17) adds that it is the place where sins are covered.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | mercy seat 21, cover 1 | mercy seat 1 |  |  |  |
| B | mercy seat 21, cover 2 | mercy seat 1 |  |  |  |
| R | lid 17, cover 4 | lid 1 |  |  |  |

Senses stated by meaning decisions: "the mercy seat" 4, "mercy seat" 3, "the house of the mercy seat" 1, "the ark of the testimony and the mercy seat" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (22): propiciatorio 22, testimonio 9, querubines 8, arca 10
- fr (22): propitiatoire 22, témoignage 9, l’arche 10, chérubins 8
- sw (22): cha rehema 22, kiti cha 22, ushuhuda 9, sanduku 10
- vi (22): thi ân 22, nắp thi 22, chứng ước 9, trên hòm 7
- ko (22): 속죄소 10, 증거궤 5, 그룹 5, 휘장 4
- pt (22): propiciatório 22, testemunho 9, querubins 8, arca 10
- am (22): መክደኛው 13, የስርየት 13, ከስርየት 5, ኪሩቤል 5
- hi (21): प्रायश्चित 21, ढकने 14, ढकना 7, साक्षी-पत्र 9
- ru (21): умилостивления 21, место 11, свидетельства 6, места 6

### righteousness (tsedaqah) (צְדָקָה, H6666), 150 records

Rule: Literal says "righteousness" ("righteous", "righteously"). Balanced keeps "righteousness" for God's and people's right conduct and standing, and says "right", "just" or "justice" where it is fairness or doing what is right (in the pair "justice and righteousness" both words stay). Readable usually says "what is right", or "fair" and "honest". Not "good" or "goodness".

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | righteousness 9, just 1, justice 1 | righteousness 10, justice 4, righteous 4, right 2 | righteousness 32, justice 3, righteous 2, goodness 1 | righteousness 21, justice 4 | righteousness 67, justice 29, righteous 15, victory 1, vindication 1 |
| B | righteousness 3, righteous 3, justice 1, right 1, just 1 | right 8, righteousness 6, just 2, justice 2, righteous 2 | righteousness 21, justice 10, right 6, just 3, righteous 2 | righteousness 17, right 3, justice 2, <none> 1, righteous 1 | righteousness 54, justice 22, righteous 15, right 10, just 8 |
| R | right 5, righteous 3, honest 2, just 1 | right 10, righteousness 4, justice 2, righteous 2, honest 1 | right 25, righteousness 3, <none> 3, justice 2, righteous 2 | right 20, just 1, honest 1, <none> 1 | right 42, righteousness 24, justice 11, righteous 5, <none> 4 |

Senses stated by meaning decisions: "righteousness" 12, "justice and righteousness" 6, "my righteousness" 3, "his righteousness" 3, "your righteousness" 3, "doing justice and righteousness" 2, "to do justice and righteousness" 2, "righteous acts" 2.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (150): justicia 117, justo 28, derecho 24, recto 17
- fr (150): justice 122, droit 47, juste 28, et la 30
- sw (150): haki 143, uadilifu 26, na kutenda 11, yaliyo 13
- vi (150): công chính 123, sự công 93, chính của 48, và sự 31
- ko (150): 의를 36, 의는 18, 의로 16, 정의와 12
- pt (150): justiça 94, retidão 46, justo 28, que é 17
- am (150): ጽድቅ 19, ፍትሕንና 10, ትክክልና 8, ቅን 11
- hi (12): धार्मिकता 5, धर्मी 3, आगे 4, प्रभु तुम्हारा 3
- ru (12): праведность 4, праведен 3, перед 5, господь твой 3

### righteousness (tsedeq) (צֶדֶק, H6664), 112 records

Rule: As tsedaqah: Literal "righteousness"; Balanced "righteousness", or "right", "just", "fair", "honest" for fair judging and honest weights ("just scales", Leviticus 19:36); Readable "what is right", "fair" or "honest".

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | righteousness 4, <none> 1, right 1, righteous 1 |  | righteousness 47, justice 5, right 4, righteous 1 | righteousness 18, justice 6, righteous 2, just 1, right 1 | righteousness 35, justice 7, righteous 2, honest 1, right 1 |
| B | <none> 3, right 2, fair 1, honest 1 |  | right 19, righteousness 11, justice 9, righteous 8, just 5 | right 8, justice 7, righteousness 5, honest 3, <none> 3 | righteousness 29, justice 7, righteous 4, right 4, honest 1 |
| R | right 4, <none> 2, fair 2, honest 2 |  | right 39, fair 5, justice 4, honest 3, <none> 3 | right 12, fair 6, honest 5, justice 2, <none> 1 | right 18, righteousness 16, justice 3, <none> 3, honest 2 |

Senses stated by meaning decisions: "righteousness" 7, "sacrifices of righteousness" 3, "in righteousness" 3, "of righteousness" 2, "his righteousness" 2, "my righteousness" 2, "your righteousness" 2, "righteously" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (112): justicia 63, justo 22, que es 14, derecho 11
- fr (112): justice 63, juste 24, droit 23, équité 8
- sw (112): haki 103, hukumu 14, yaliyo 14, usawa 5
- vi (112): công chính 68, sự công 37, chính và 19, chính của 19
- ko (112): 의를 14, 의로운 14, 공정하게 9, 의가 9
- pt (112): justiça 43, retidão 28, justo 20, justas 10
- am (112): ጽድቅን 14, ትክክል 15, የጽድቅ 8, ትክክለኛ 7
- hi (7): दे रहे 3, तुम्हें दे 3, परमेश्वर तुम्हें 3, न्याय 3
- ru (7): даёт тебе 3, бог даёт 3, господь твой 3, твой бог 3

### justice, judgment (mishpat) (מִשְׁפָּט, H4941), 406 records

Rule: Settled by sense, so owb.validate does not hold the English to one word. "justice" for justice done (beside "righteousness" in the pair); "judgment" for a court's or God's judging; for the decrees of the covenant ("statutes and judgments") Literal says "judgments", Balanced "rulings" and Readable "rules" or "laws"; "custom", "way" or "manner" for a customary practice; "case" or "right" for someone's legal claim; Readable may say "fair" of fair judging. (Not checked by the validator.)

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | judgment 55, ordinance 10, justice 7, judge 6, way 5 | judgment 32, law 11, justice 8, custom 8, rule 7 | judgment 44, justice 16, way 3, right 2, custom 1 | justice 28, judgment 11, right 5, <none> 4, way 3 | justice 71, judgment 51, way 10, judge 9, right 7 |
| B | ruling 35, <none> 17, case 8, justice 7, way 7 | ruling 21, <none> 15, law 12, way 10, custom 6 | ruling 25, justice 17, just 11, right 10, judgment 5 | justice 25, right 13, <none> 6, judgment 5, way 4 | justice 54, judgment 20, ruling 19, right 16, <none> 16 |
| R | rule 46, law 37, right 14, way 13, <none> 10 | rule 28, law 26, <none> 17, way 12, judge 7 | right 24, <none> 17, fair 13, judge 9, justice 5 | right 17, fair 12, justice 10, <none> 10, judge 5 | right 39, fair 30, justice 24, rule 23, <none> 23 |

Senses stated by meaning decisions: "judgments" 24, "justice and righteousness" 7, "judgment" 5, "justice" 5, "statutes and judgments" 4, "your judgments" 4, "righteousness and justice" 3, "doing justice and righteousness" 2.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (406): justicia 115, normas 67, estatutos 63, derecho 42
- fr (406): justice 116, droit 81, prescriptions 62, règles 52
- sw (406): haki 182, hukumu 75, kanuni 67, maagizo 62
- vi (406): công 181, lý 94, mạng lệnh 67, luật lệ 75
- ko (406): 법도를 57, 규례와 42, 정의를 34, 규례를 24
- pt (406): ordenanças 93, justiça 108, estatutos 63, justo 41
- am (406): ፍትሕ 40, ፍርድ 31, ደንቦች 18, ደንቦቼን 17
- hi (95): नियम 27, विधियों 19, न्याय 19, पालन 16
- ru (95): правила 28, установления 24, предписано 8, числу как 7

### glory, honor (kavod) (כָּבוֹד, H3519), 189 records

Rule: "glory" for God's glory and its visible presence ("the glory of the LORD") at every level; "honor" for the honor of people; "wealth" or "riches" where it means riches ("riches and honor"). In poetry "my glory" for the self, beside "my soul", takes a decision.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | glory 21, honor 2, wealth 1, soul 1 | glory 14, honor 13, riches 9, wealth 3, splendor 2 | glory 46, splendor 4, majesty 3, heart 2, honor 2 | honor 15, wealth 4, glory 3, soul 1, heart 1 | glory 65, honor 3, wealth 3, <none> 2, splendor 2 |
| B | glory 20, honor 3, riches 1 | glory 12, honor 12, riches 7, wealth 5, splendor 2 | glory 32, honor 10, glorious 6, splendor 5, heart 2 | honor 17, wealth 3, riches 3, heart 1, <none> 1 | glory 59, honor 5, wealth 4, splendor 4, <none> 3 |
| R | glory 18, <none> 4, honor 2 | honor 9, <none> 9, glory 7, glorious 4, wealth 2 | glorious 17, glory 14, honor 11, <none> 7, heart 2 | honor 9, <none> 9, riches 4, wealth 1 | glory 56, honor 9, <none> 7, riches 4, glorious 2 |

Senses stated by meaning decisions: "my glory" 8, "glory" 7, "honor" 4, "their glory" 3, "your glory" 2, "my honor" 2, "in glory" 2, "for the honor of your servant" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (189): gloria 126, honra 34, riquezas 17, glorioso 10
- fr (189): gloire 133, l’honneur 18, richesse 15, au-dessus 17
- sw (189): utukufu 126, heshima 46, wa bwana 36, utajiri 16
- vi (189): vinh 161, quang 117, dự 31, hiển 17
- ko (189): 영광이 54, 영광을 38, 주의 44, 영광과 13
- pt (189): glória 123, honra 45, glorioso 9, riqueza 12
- am (189): ክብር 66, የእግዚአብሔር 40, ክብሩ 8, ከፍ 12
- hi (29): महिमा 24, प्रभु की 13, दिखाई 9, दी। 6
- ru (29): слава 14, явилась 6, славу 6, господа 13

### faithfulness (emunah) (אֱמוּנָה, H530), 49 records

Rule: "faithfulness" ("faithful", "faithfully") at every level for God's faithfulness and steady conduct (Habakkuk 2:4 keeps "faithfulness", not "faith", with a footnote on Romans 1:17); Balanced and Readable say "honest(ly)" or "trusted" of honest dealing (2 Kings 12:16; 22:7), and "truth" of truthful speech.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | faithfulness 1, <none> 1 | faithfulness 7, trust 3, faithfully 1 | faithfulness 22, trust 1, truth 1 | truth 1, faithfully 1, faithful 1 | faithfulness 10, <none> 1, trust 1 |
| B | faithful 1, firm 1 | faithfully 3, honestly 3, trust 2, <none> 1, faithfulness 1 | faithfulness 18, faithful 3, <none> 1, trust 1, truth 1 | honest 1, faithfully 1, faithful 1 | faithfulness 7, firm 1, honestly 1, faithful 1, truth 1 |
| R | faithful 1, honest 1, <none> 1 | faithful 4, <none> 3, honest 2, trust 1, honestly 1 | faithful 16, faithfulness 5, <none> 3, firm 2, trust 1 | honest 2, truth 1, <none> 1 | faithful 6, faithfulness 2, honest 2, <none> 1, trust 1 |

Senses stated by meaning decisions: "faithfulness" 12, "in faithfulness" 2, "in their trust" 1, "in trust" 1, "in their faithfulness they consecrated themselves" 1, "not reckoned with them ... in faithfulness" 1, "a god of faithfulness" 1, "steady" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (49): fidelidad 28, fiel 15, amor 11, justicia 8
- fr (49): fidélité 27, fidèle 14, amour 8, ta 11
- sw (49): uaminifu 33, usiokoma 11, upendo 11, haki 13
- vi (49): tín 37, sự thành 24, của ngài 20, thương thành 11
- ko (49): 주님의 17, 신실하심을 7, 한결같은 11, 신실하심은 4
- pt (49): fidelidade 28, amor leal 11, com honestidade 4, tua 11
- am (49): ጽኑ 12, በታማኝነት 7, ታማኝነትህ 5, እግዚአብሔር ሆይ፣ 7
- ru (3): его 3

### truth, faithfulness (emet) (אֱמֶת, H571), 125 records

Rule: "truth" or "true" for the truth of words and of God; "faithfulness" or "faithful" for reliability, especially in the pair with hesed ("loyal love and faithfulness"; Exodus 34:6 Balanced "faithful love and truth"). Balanced and Readable may say "honest(ly)" or "fair(ly)" of honest dealing and fair judging.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | faithfulness 4, true 3, truth 2, right 2, faithfully 1 | truth 10, faithfulness 8, true 3, faithful 2, right 1 | faithfulness 21, truth 17, reliable 1, right 1 | faithfulness 5, truth 3, true 3, firm 1 | truth 17, faithfulness 10, true 8, faithfully 2, stability 2 |
| B | true 5, faithful 3, truth 3, <none> 1, right 1 | faithful 8, true 6, faithfully 6, truth 4, faithfulness 3 | faithfulness 16, truth 11, faithful 7, right 4, true 3 | faithfulness 4, truth 3, <none> 3, sure 1, reliable 1 | truth 12, true 9, faithfulness 7, faithfully 6, stability 2 |
| R | true 4, faithful 3, <none> 3, fact 1, honest 1 | faithful 9, true 5, <none> 4, faithfully 3, truth 3 | faithful 21, truth 9, right 6, faithfulness 4, true 4 | truth 4, right 3, <none> 3, honest 2, true 2 | faithful 11, truth 10, true 6, right 6, <none> 5 |

Senses stated by meaning decisions: "faithfulness" 8, "truth" 7, "in truth" 5, "loyal love and faithfulness" 4, "in faithfulness" 3, "peace and stability" 3, "in faithfulness and with a whole heart" 2, "steadfast love and faithfulness" 2.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (125): fidelidad 37, verdad 40, fiel 40, amor 30
- fr (125): fidélité 36, vérité 30, fidèle 38, amour 17
- sw (125): uaminifu 52, kweli 54, usiokoma 27, upendo 27
- vi (125): tín 61, chân thật 34, sự thành 23, tình yêu 28
- ko (125): 한결같은 31, 사랑과 20, 진실을 10, 신실하심을 10
- pt (125): fidelidade 42, verdade 40, leal e 21, amor leal 28
- am (125): ጽኑ 28, እውነት 19, ፍቅርና 11, ታማኝነት 9
- hi (18): सच्चाई 10, प्रेम और 5, अटल प्रेम 5, सच हो 3
- ru (18): милость 4, если 9, неизменной 3, итак 4

### salvation (yeshuah) (יְשׁוּעָה, H3444), 77 records

Rule: Literal says "salvation" ("deliverance" where it is a battle won). Balanced keeps "salvation" in the prophets and may use the verb ("save", "rescue") in the Psalms where the noun names God's act of saving; Readable says "save" or "rescue". The Greek counterpart is salvation (G4991).

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | salvation 4 | salvation 4, deliverance 1, help 1 | salvation 42, victory 1, deliverance 1, <none> 1 | salvation 1, <none> 1 | salvation 19, save 1, deliverance 1 |
| B | salvation 2, save 2 | saves 1, deliverance 1, help 1, salvation 1, save 1 | rescue 11, saves 10, salvation 7, saving 6, help 6 | deliverance 1, <none> 1 | salvation 18, rescue 1, deliverance 1, saves 1 |
| R | salvation 1, rescue 1, rescued 1, save 1 | saved 2, saves 1, victory 1, rescue 1, help 1 | save 17, saves 11, saved 6, <none> 5, help 4 | saves 1, <none> 1 | salvation 10, save 7, saves 4, help 1 |

Senses stated by meaning decisions: "salvation" 11, "your salvation" 4, "the salvation of yahweh" 2, "salvations" 2, "deliverance" 1, "help, to help" 1, "deliverances" 1, "her righteousness" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (77): salvación 29, rescate 7, ayuda 8, con esperanza 5
- fr (77): salut 34, sauve 14, mon 25, joie 12
- sw (77): wokovu 34, wa kuokoa 7, wangu 21, yangu 19
- vi (77): cứu 70, rỗi 29, giải 38, ngài 54
- ko (77): 구원을 15, 구원하시는 14, 구원이 8, 나의 12
- pt (77): salvação 28, livramento 7, salvar 9, minha 19
- am (77): የማዳን 7, ደስ 11, መዳን 4, እግዚአብሔር ሆይ፣ 10
- hi (6): उद्धार 5, परमेश्वर 3, मैं 3
- ru (6): но 3

### Sheol, the realm of the dead (שְׁאוֹל, H7585), 63 records

Rule: As articles/sheol-hades-and-gehenna.md: "Sheol" at Literal everywhere, and at Balanced everywhere but Jacob's sayings in Genesis (37:35; 42:38; 44:29, 31), where Balanced says "the grave". Readable says "the place of the dead" in the Psalms (and 2 Samuel 22, which is Psalm 18) and "the grave" elsewhere. Never "hell".

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | Sheol 7 | Sheol 4, death 1 | Sheol 15, death 6 | Sheol 19, death 3, depths 1 | Sheol 18, death 5 |
| B | grave 4, Sheol 3, depths 1 | Sheol 4, death 2 | Sheol 15, death 6 | Sheol 19, death 3 | Sheol 18, death 5, depths 1 |
| R | grave 7 | grave 3, death 3, place of the dead 1 | place of the dead 15, death 4, grave 3 | grave 19, death 4 | grave 18, death 5 |

Senses stated by meaning decisions: "sheol" 19, "the lowest sheol" 1, "sheol ... its throat" 1, "sheol and abaddon" 1, "distresses of sheol" 1, "lowest sheol" 1, "the hand of sheol" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (63): los muertos 63, lugar de 63, de los 63, al lugar 23
- fr (63): séjour des 63, des morts 63, au séjour 24, du séjour 19
- sw (63): kuzimu 63, kifo 10, mvi 5, mauti 5
- vi (63): âm phủ 62, xuống âm 19, sự chết 13, sâu 13
- ko (63): 스올로 21, 스올의 8, 스올에서 6, 스올과 5
- pt (63): mundo dos 63, dos mortos 63, ao mundo 18, do mundo 18
- am (63): ዓለም 56, ሙታን 29, ጥልቅ 6, ገመዶች ተጠመጠሙብኝ፤ 3
- hi (8): अधोलोक 8, में उतर 3, में पहुँचा 3, पके 3
- ru (8): мёртвых 8, в мир 7, если 3, но 3

### redeem, redeemer (ga'al) (גָּאַל, H1350), 83 records

Rule: "redeem" and "redeemer" at Literal and Balanced, "avenger" for the avenger of blood; for land, houses and people in the laws (Leviticus 25; 27) Balanced and Readable say "buy back". Readable says "the relative who avenges the death", "relative" for the family redeemer in Ruth, and "rescue" or "set free" where God redeems his people, keeping "Redeemer" where it is his title.

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | avenger 8, redeemed 8, redeem 8, redeemer 3, redemption 2 | redeemer 9, avenger 4, redeem 3, redemption 1 | redeemed 4, redeem 3, redeemer 2, redeems 1 | redeemer 2, claim 1 | redeemer 14, redeemed 12, redeem 2 |
| B | avenger 8, redeem 8, redeemed 4, relative 3, bought back 3 | redeemer 10, avenger 4, redeem 3, relative 2, redemption 1 | free 6, bought back 2, <none> 1, rescued 1, freed 1 | redeemer 1, claim 1, <none> 1 | redeemer 14, redeemed 12, redeem 2, rescued 1, claim 1 |
| R | relative 13, <none> 5, bought back 5, buy back 4, free 2 | relative 8, redeemer 8, redeem 2, <none> 1 | free 3, rescue 3, <none> 2, rescued 2, set free 1 | <none> 2, redeemer 1 | rescue 11, redeemer 6, bought back 5, rescued 5, free 3 |

Senses stated by meaning decisions: "redeemer" 6, "redeemed" 5, "redeem" 5, "the redeemed" 2, "your redeemer" 1, "i have redeemed you" 1, "has redeemed" 1, "redeemed without money" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (83): redentor 25, vengador 12, pariente 11, redimido 9
- fr (83): libérateur 15, vengeur 12, racheté 13, proche parent 11
- sw (83): mkombozi 25, mlipiza kisasi 12, kisasi wa 10, wa damu 10
- vi (83): chuộc 61, cứu 33, thù máu 11, báo thù 13
- ko (83): 피의 11, 무를 8, 구속자 7, 얹어서 5
- pt (83): redentor 16, vingador 12, resgatador 9, do sangue 11
- am (83): ተበቃዩ 11, ቤዢ 10, ዘመድ 6, ሊቤዠው 5
- hi (40): ख़ून का 10, का बदला 10, बदला लेनेवाले 8, तो 23
- ru (40): выкупить 14, за кровь 10, выкупщик 6, если 17

### breath, vapor (hevel) (הֶבֶל, H1892), 64 records

Rule: In Ecclesiastes "breath" at every level ("Breath of breaths"), keeping the book's picture of what is brief and cannot be grasped; elsewhere "breath" or "vapor" for what passes, "empty", "nothing" or "in vain" for what is futile, and "worthless idols" or "idols" where it names false gods (Deuteronomy 32:21; Jeremiah).

| Level | law | history | psalms | wisdom | prophets |
|---|---|---|---|---|---|
| L | worthless 1, idols 1 | worthless 3, idols 3 | breath 6, nothing 2, vanities 1, empty 1 | breath 31, nothing 3, emptiness 3, vapor 2, empty 1 | worthless 4, idols 3, futility 3, emptiness 2, vapor 2 |
| B | worthless 1, idols 1 | worthless 3, idols 3 | breath 4, nothing 2, useless 1, idols 1, vapor 1 | breath 32, nothing 3, empty 3, in vain 1, <none> 1 | empty 8, idols 7, breath 5, nothing 3, worthless 3 |
| R | useless 1, idols 1 | useless 3, idols 3 | breath 4, nothing 3, <none> 1, idols 1, worthless 1 | breath 31, nothing 7, <none> 4, empty 2 | idols 10, useless 6, worthless 5, nothing 5, breath 2 |

Senses stated by meaning decisions: "breath" 21, "a breath" 5, "their vanities" 2, "worthless idols" 2, "futility" 2, "the vanity" 1, "breaths" 1, "breath and an evil sickness" 1.

Other languages (Balanced; distinctive words of the records, with record counts):

- es (64): soplo 41, es un 21, también esto 14, esto es 14
- fr (64): souffle 39, n’est qu’un 27, cela aussi 14, aussi n’est 13
- sw (64): pumzi 42, tu 37, hili nalo 14, nalo ni 13
- vi (64): hơi 44, thở 41, chỉ là 36, là một 29
- ko (64): 한낱 15, 이것 또한 14, 헛된 14, 입김이다 11
- pt (64): sopro 43, é um 21, também isso 14, isso é 14
- am (64): እስትንፋስ 29, ነው። 25, ይህም 15, ነፋስን መከተል 7

## What was changed (English)

Sentences outside the Psalms were edited directly; Psalms changes are in `pending-psalms-patches-b.jsonl`.

- JOB.6.14.s1 L: "steadfast love" -> "loyal love" (hesed key-term rule (data/key_terms.json): wisdom books follow the Psalms: loyal love at Literal and Balanced)
- JOB.6.14.s1 B: "faithful love" -> "loyal love" (hesed key-term rule (data/key_terms.json): wisdom books follow the Psalms: loyal love at Literal and Balanced)
- JOB.10.12.s1 L: "steadfast love" -> "loyal love" (hesed key-term rule (data/key_terms.json): wisdom books follow the Psalms: loyal love at Literal and Balanced)
- JOB.10.12.s1 B: "faithful love" -> "loyal love" (hesed key-term rule (data/key_terms.json): wisdom books follow the Psalms: loyal love at Literal and Balanced)
- JOB.37.13.s1 L: "steadfast love" -> "loyal love" (hesed key-term rule (data/key_terms.json): wisdom books follow the Psalms: loyal love at Literal and Balanced)
- JOB.37.13.s1 B: "faithful love" -> "loyal love" (hesed key-term rule (data/key_terms.json): wisdom books follow the Psalms: loyal love at Literal and Balanced)
- JON.4.2.s1 L: "great in steadfast love" -> "great in loyal love" (hesed key-term rule (data/key_terms.json): the prophets say loyal love at Literal and Balanced; Jonah now agrees with Joel 2:13)
- JON.4.2.s1 B: "rich in faithful love" -> "rich in loyal love" (hesed key-term rule (data/key_terms.json): the prophets say loyal love at Literal and Balanced; Jonah now agrees with Joel 2:13)
- JON.4.2.s1: decision r-en-1 updated (hesed key-term rule (data/key_terms.json): Jonah 4:2 agrees with Joel 2:13)
- EZR.3.11.s1 L: "steadfast love toward Israel" -> "loyal love toward Israel" (hesed key-term rule (data/key_terms.json): the temple refrain keeps the Psalms' wording wherever it is sung)
- EZR.3.11.s1 B: "faithful love for Israel" -> "loyal love for Israel" (hesed key-term rule (data/key_terms.json): the temple refrain keeps the Psalms' wording wherever it is sung)
- EZR.3.11.s1: decision r-en-1 updated (hesed key-term rule (data/key_terms.json): refrain)
- GEN.32.11.s1 B: "all the steadfast love and faithfulness" -> "all the faithful love and truth" (hesed key-term rule (data/key_terms.json): Law and history: faithful love at Balanced, paired with "truth" as in Exodus 34:6)
- GEN.32.11.s1 R: "all the kindness" -> "all the faithful love" (hesed key-term rule (data/key_terms.json): faithful love at Readable everywhere)
- GEN.24.14.s1 L: "have shown loyalty to my master" -> "have shown steadfast love to my master" (hesed key-term rule (data/key_terms.json): Law: steadfast love at Literal)
- GEN.24.14.s1 B: "have kept faith with my master" -> "have shown faithful love to my master" (hesed key-term rule (data/key_terms.json): Law: faithful love at Balanced)
- GEN.24.14.s1 R: "have been kind to my master" -> "have shown faithful love to my master" (hesed key-term rule (data/key_terms.json): faithful love at Readable)
- GEN.24.12.s1 L: "show loyalty to my master Abraham" -> "show steadfast love to my master Abraham" (hesed key-term rule (data/key_terms.json): Law: steadfast love at Literal)
- GEN.24.12.s1 R: "Show your kindness to my master" -> "Show your faithful love to my master" (hesed key-term rule (data/key_terms.json): faithful love at Readable)
- PRO.16.6.s1 R: "Guilt is taken away by love and faithfulness." -> "Faithful love and truth take guilt away." (hesed key-term rule (data/key_terms.json): faithful love at Readable)
- PRO.19.22.s1 B: "is loyalty;" -> "is loyal love;" (hesed key-term rule (data/key_terms.json): wisdom books: loyal love at Balanced)
- PRO.19.22.s1 R: "People want friends who are loyal." -> "People want friends who show faithful love." (hesed key-term rule (data/key_terms.json): faithful love at Readable)
- PRO.13.14.s1 B: "What the wise teach is a spring of life" -> "The teaching of the wise is a spring of life" (torah key-term rule: in Proverbs the word is "teaching" at every level)
- PRO.6.20.s1 B: "do not let go of what your mother teaches you" -> "do not let go of your mother's teaching" (torah key-term rule: in Proverbs the word is "teaching" at every level)
- PRO.6.20.s1 R: "Do not turn away from what your mother teaches you." -> "Do not turn away from your mother's teaching." (torah key-term rule: in Proverbs the word is "teaching" at every level)
- 2KI.5.21.s1 B: "asked, "Is everything all right?"" -> "asked, "Is all well?"" (shalom key-term rule: "Is it peace?" is "Is all well?")
- 2KI.5.21.s1 R: "He asked, "Is everything all right?"" -> "He asked, "Is all well?"" (shalom key-term rule: "Is it peace?" is "Is all well?")
- 2KI.5.22.s1 R: "Gehazi answered, "Everything is fine." -> "Gehazi answered, "All is well." (shalom key-term rule: the answer to "Is all well?")
- JDG.11.13.s1 R: "Now give it back to me without a fight."" -> "Now give it back to me peacefully."" (shalom key-term rule: peace / peacefully)
- JER.43.12.s1 B: "and he will leave there unharmed." -> "and he will leave there in peace." (shalom key-term rule: peace)
- GEN.43.28.s1 B: "is in good health" -> "is well" (shalom key-term rule: "peace to your servant" is "he is well")
- 1SA.17.18.s1: rendering decision (B, R) "see how your brothers are (doing)"
- 1SA.17.22.s1: rendering decision (B) "ask his brothers how they were"
- JER.15.5.s1: rendering decision (B, R) "ask how you are"
- 2KI.10.13.s1: rendering decision (L, R) "to greet (L); to visit (R)"
- JER.20.10.s1: rendering decision (B, R) "trusted friends (B); closest friends (R)"
- JER.38.22.s1: rendering decision (B, R) "trusted friends (B); closest friends (R)"
- PSA.41.10.s1: rendering decision (R) "my best friend"
- GEN.37.4.s1: rendering decision (B, R) "a friendly word (B); speak kindly (R)"
- GEN.41.16.s1: rendering decision (B, R) "for his good (B); good for you (R)"
- PSA.46.5.s1 B: "the sacred home of the Most High" -> "the holy home of the Most High" (qadosh key-term rule: "holy" at every level)
- 1CH.26.26.s1 R: "where the gifts given to God were kept" -> "where the holy gifts given to God were kept" (qodesh key-term rule: "holy" for holy things)
- LEV.27.21.s1 R: "this field will belong to" -> "this field will be holy and will belong to" (qodesh key-term rule: "holy to the LORD")
- EZK.36.38.s1: rendering decision (R) "sheep ... to offer as sacrifices"
- PRO.20.25.s1: rendering decision (R) "make promises to God without thinking"
- GEN.17.4.s1 R: "{{deity_pronoun:my|My}} promise to you:" -> "{{deity_pronoun:my|My}} covenant with you:" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.7.s1 R: "My promise to you and your descendants" -> "My covenant with you and your descendants" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.9.s1 R: "your part of {{deity_pronoun:my|My}} promise" -> "your part of {{deity_pronoun:my|My}} covenant" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.10.s1 R: "to keep {{deity_pronoun:my|My}} promise:" -> "to keep {{deity_pronoun:my|My}} covenant:" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.11.s1 R: "that I have made this promise to you" -> "that I have made this covenant with you" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.13.s1 R: "{{deity_pronoun:my|My}} promise lasts forever" -> "{{deity_pronoun:my|My}} covenant lasts forever" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.14.s1 R: "he has broken {{deity_pronoun:my|My}} promise" -> "he has broken {{deity_pronoun:my|My}} covenant" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.19.s1 R: "I will keep {{deity_pronoun:my|My}} promise to him" -> "I will keep {{deity_pronoun:my|My}} covenant with him" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.21.s1 R: "I will keep {{deity_pronoun:my|My}} special promise with Isaac" -> "I will keep {{deity_pronoun:my|My}} covenant with Isaac" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.17.2.s1 R: "I will keep {{deity_pronoun:my|My}} promise to you" -> "I will keep {{deity_pronoun:my|My}} covenant with you" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.9.11.s1 R: "This is {{deity_pronoun:my|My}} promise:" -> "This is {{deity_pronoun:my|My}} covenant:" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.9.13.s1 R: "the sign of {{deity_pronoun:my|My}} promise to the earth" -> "the sign of {{deity_pronoun:my|My}} covenant with the earth" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.9.15.s1 R: "I will remember {{deity_pronoun:my|My}} promise to you" -> "I will remember {{deity_pronoun:my|My}} covenant with you" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- GEN.9.17.s1 R: "the sign of the promise I have made" -> "the sign of the covenant I have made" (berit key-term rule: "covenant" at every level for God's covenants (Readable in Genesis 9 and 17 had "promise", while 9:9 and the rest of the Law say "covenant"))
- HOS.10.4.s1 B: "making agreements" -> "making treaties" (berit key-term rule: "treaty" for agreements between peoples at Balanced)
- GEN.14.13.s1: rendering decision (L, R) "allies (L); partners (R)"
- OBA.1.7.s1: rendering decision (B, R) "allies ... friends"
- DAN.9.24.s1 R: "He will take away guilt." -> "He will make atonement for guilt." (kipper key-term rule: "atonement" at every level)
- ISA.47.11.s1: rendering decision (L, B, R) "ransom (L); pay off (B); pay to make it stop (R)"
- PRO.16.6.s1: rendering decision (B, R) "make amends for wrong (B); take guilt away (R)"
- LEV.16.2.s1 L: "before the cover which [is] on the ark, so that he does not die; for in the cloud I appear over the cover." -> "before the mercy seat which [is] on the ark, so that he does not die; for in the cloud I appear over the mercy seat." (kapporet key-term rule: "mercy seat" at Literal and Balanced, as in Exodus 25)
- LEV.16.13.s1 L: "shall cover the cover which" -> "shall cover the mercy seat which" (kapporet key-term rule: "mercy seat" at Literal and Balanced, as in Exodus 25)
- LEV.16.14.s1 L: "on the front of the cover, on the east side; and before the cover he" -> "on the front of the mercy seat, on the east side; and before the mercy seat he" (kapporet key-term rule: "mercy seat" at Literal and Balanced, as in Exodus 25)
- LEV.16.15.s1 L: "sprinkle it on the cover and before the cover." -> "sprinkle it on the mercy seat and before the mercy seat." (kapporet key-term rule: "mercy seat" at Literal and Balanced, as in Exodus 25)
- EZK.33.13.s1 R: "trust in the good they have done" -> "trust in the right things they have done" (tsedaqah key-term rule: Readable says "right" or "righteousness")
- EZK.33.13.s1 R: "None of the good things they did" -> "None of the right things they did" (tsedaqah key-term rule: Readable says "right" or "righteousness")
- JOB.35.8.s1 R: "and the good you do helps only other people" -> "and the right things you do help only other people" (tsedaqah key-term rule: Readable says "right" or "righteousness")
- PRO.16.31.s1 R: "People get it by living a long and good life." -> "People get it by doing what is right." (tsedaqah key-term rule: Readable says "right" or "righteousness")
- PSA.71.19.s1 R: "{{deity_pronoun:your|Your}} goodness is higher than the sky" -> "{{deity_pronoun:your|Your}} righteousness is higher than the sky" (tsedaqah key-term rule: Readable says "right" or "righteousness")
- PRO.12.17.s1 L: "declares what is right" -> "declares righteousness" (tsedeq key-term rule: Literal says "righteousness")
- PRO.8.15.s1 L: "decree what is right" -> "decree righteousness" (tsedeq key-term rule: Literal says "righteousness")
- GEN.49.6.s1: rendering decision (R) "I (the whole self)"
- ISA.10.18.s1: rendering decision (R) "the king's great forests"
- ISA.5.13.s1: rendering decision (B, R) "leading men (B); important leaders (R)"
- PRO.25.2.s1 R: "God shows {{deity_pronoun:his|His}} greatness by keeping some things secret." -> "God is honored for keeping some things secret." (kavod key-term rule: "glory" or "honor")
- PRO.25.2.s1 R: "A king shows his greatness by finding out" -> "A king is honored for finding out" (kavod key-term rule: "glory" or "honor")
- PRO.12.22.s1 B: "people who keep faith are" -> "people who act faithfully are" (emunah key-term rule: "faithfulness", "faithful(ly)")
- JER.28.9.s1 R: "really sent him" -> "truly sent him" (emet key-term rule: "truth", "true", "truly")
- EZK.18.9.s1 R: "is careful to obey {{deity_pronoun:my|My}} rules" -> "faithfully obeys {{deity_pronoun:my|My}} rules" (emet key-term rule: "faithfully")
- GEN.24.48.s1: rendering decision (L, R) "by the right way (L); straight to (R)"
- NEH.7.2.s1: rendering decision (R) "a man people could trust"
- ISA.33.6.s1 R: "a great supply of help, wisdom, and knowledge" -> "a great supply of salvation, wisdom, and knowledge" (yeshuah key-term rule: "salvation" or "save")
- PRO.15.11.s1 R: "can see even the world of the dead" -> "can see even into the grave" (Sheol key-term rule (articles/sheol-hades-and-gehenna.md): Readable says "the grave" outside the Psalms)
- LEV.25.26.s1 R: "to buy the land back for him" -> "to buy back the land for him" (goel key-term rule: "buy back" for property at Readable)
- LEV.27.15.s1 R: "wants to buy the house back" -> "wants to buy back the house" (goel key-term rule: "buy back" for property at Readable)
- LEV.27.19.s1 R: "wants to buy the field back" -> "wants to buy back the field" (goel key-term rule: "buy back" for property at Readable)
- LEV.25.33.s1: rendering decision (B, R) "is acquired from a Levite (B); buys a house from a Levite (R)"
- LAM.4.17.s1 R: "but it was no use" -> "but it was useless" (hevel key-term rule)
- PSA.66.2.s1: rendering decision (R) "how great his name is"

## Other languages

Not harmonised in this pass. The lists above are a measure, not a judgement: each language carries the senses in its own words, and several (Swahili "upendo usiokoma" for hesed, as agreed with the Psalms) already state book-wide choices in their style briefs. Points for each language's reviewer:

- hesed: the English sectional split is English wording only; the other languages use one phrase across the canon, which is the better outcome for them and should stay so.
- covenant: every language with Old Testament text uses one word for berit (pacto, alliance, agano, giao ước, 언약, aliança, ኪዳን, वाचा, завет) in over 90% of records; the remainder are treaties between peoples.
- nephesh: Spanish, French and Portuguese use "vida" / "vie" far more than "alma" / "âme"; that matches the English Balanced practice (soul kept mostly in the Psalms).
- Russian hesed mixes "милость" (mercy) and "неизменная любовь" (unfailing love) in the books drafted so far; the Russian reviewer should settle one, as the other languages have.
- Hindi and Russian have only part of the Old Testament drafted, so their counts are small; Ukrainian and Japanese have none yet.
