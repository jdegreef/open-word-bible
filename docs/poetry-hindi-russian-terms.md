# Hindi and Russian: Job, Psalms, Proverbs, Ecclesiastes, Song of Songs

**Status: proposed, awaiting native Hindi and Russian reviewers.** These are
the choices used to draft the poetry and wisdom books in Hindi and Russian, so
that blocks of psalms drafted in parallel read as one translation.
`docs/pentateuch-hindi-russian-terms.md` and
`docs/history-hindi-russian-terms.md` still hold in full (the divine name and
its setting, forms of address, measures, cultic terms, the kingdom, names):
this note adds what poetry needs. Where an earlier book or the New Testament in
this translation already has a form, that form wins. If a choice here changes,
every passage drafted under it is revised. Decision text stays in English,
quoting the Hindi or Russian words.

## Both languages

- Translate from the Hebrew, using the literal gloss, the English and the
  meaning decisions to see how a line was read. Never from a reference
  Bible. Psalms 23, 51, 91, 103, Proverbs 3:5-6, Proverbs 31, Ecclesiastes 1-3
  and 12 pull hardest toward the Hindi Old Version and the Russian Synodal:
  draft from the gloss, and rewrite any line that matches a well-known version
  for more than a short common phrase.
- **Lines follow the English record.** Where an English level has `\q`
  breaks, that level is set in lines too, with the breaks at the language's
  own phrase boundaries; where the English level is prose, so is the
  language's.
- **Selah** stays at the end of its verse at every level, as the English has
  it: Hindi सेला, Russian Села. The first use in each block of psalms gets a
  decision (a word whose meaning is unknown, probably a musical direction).
- **Titles.** A psalm's title is verse 1 and is translated at every level as
  the English level does it: Literal keeps the Hebrew's words, Readable may
  explain.
- **Addressing God.** Hindi: तू (तेरा, तुझे) to God, as everywhere; God
  speaking uses मैं; God in the third person takes honorific forms (वे, उनका,
  उन्होंने), as Kings and Chronicles. Russian: ты to God; `deity_pronoun`
  spans on every pronoun for God (mid-sentence я too), none on reflexives,
  on a sentence-initial Я, or on anyone else.
- **People addressed.** Hindi: the psalmist speaks to people and to his
  enemies with तुम; to the king (Psalms 20, 21, 45, 72) with आप where he
  speaks to him directly. Russian: ты throughout, вы for a Hebrew plural.

## Parallels: draft once, reuse

Where the Hebrew is the same, the later passage copies the earlier wording at
each level; where it differs, the wording differs, with a decision naming the
other passage.

| Passage | Same as |
|---|---|
| Psalm 18 | 2 Samuel 22 (on main) |
| Psalm 96; 105:1-15; 106:1, 47-48 | 1 Chronicles 16:8-36 (on main) |
| Psalm 132:8-10 | 2 Chronicles 6:41-42 (on main) |
| Psalm 53 | Psalm 14 |
| Psalm 70 | Psalm 40:13-17 |
| Psalm 108 | Psalms 57:7-11 and 60:5-12 |
| Psalm 115:4-8 | Psalm 135:15-18 |
| Proverbs 22:17-24:22 | (no internal parallel; Proverbs 18:8 = 26:22, 20:16 = 27:13, 21:9 = 25:24: copy) |

## The New Testament quotes these books

Where the New Testament quotes a line and the Hebrew says the same, use the
New Testament's wording in your language at the matching level (grep the
book). Where the New Testament follows the Greek Old Testament and differs
(Psalm 40:6 "a body", 68:18 "gave gifts", 102:25-27 in part, Proverbs 3:34
"the proud"), translate the Hebrew and add a decision naming the New
Testament form. Lines the New Testament quotes keep its forms of address,
even where they bend a rule: Hindi Psalm 2:7 keeps तू as Hebrews 1:5 and
Acts 13:33 have it.

Quoted lines include: Psalms 2:1-2, 7, 9; 4:4; 5:9; 8:2, 4-6; 10:7; 14:1-3;
16:8-11; 18:49; 19:4; 22:1, 18, 22; 24:1; 31:5; 32:1-2; 34:8, 12-16, 20;
35:19; 36:1; 40:6-8; 41:9; 44:22; 45:6-7; 51:4; 62:12; 68:18; 69:4, 9, 22-23,
25; 78:2, 24; 82:6; 89:20; 91:11-12; 94:11; 95:7-11; 97:7; 102:25-27; 104:4;
109:8; 110:1, 4; 112:9; 116:10; 117:1; 118:6, 22-23, 25-26; 140:3; 143:2;
Job 5:13; 41:11; Proverbs 3:11-12, 34; 10:12; 11:31; 25:21-22; 26:11.

## Psalm titles and musical terms

| Hebrew (English L / R) | Hindi | Russian |
|---|---|---|
| *lamnatseach* (For the director / For the leader of the music) | संगीत-निर्देशक के लिए (L, B); गायक-मंडली के अगुवे के लिए (R) | Руководителю хора (L, B); Для руководителя музыкантов (R) |
| *mizmor* (a psalm / a song at R) | भजन; गीत (R) | псалом; песнь (R) |
| *shir* (a song) | गीत | песнь (L, B); песня (R) |
| *maskil*, *miktam*, *shiggayon* | मस्कील, मिक्ताम, शिग्गायोन | маскиль, михтам, шиггайон |
| *tefillah* (a prayer) | प्रार्थना | молитва |
| *Hallelu Yah* (Praise the LORD) | `{{divine_name:प्रभु\|याह}}` की स्तुति करो | Хвалите `{{divine_name:ГОСПОДА\|Ях}}` |
| *shir hamma'alot* (A song of ascents / for the journey up to Jerusalem) | चढ़ाई का गीत (L, B); यरूशलेम की ओर जाने की यात्रा का गीत (R) | Песнь восхождения (L, B); Песня для пути в Иерусалим (R) |

The short name *Yah* is `{{divine_name:...|याह}}` / `{{divine_name:...|Ях}}`
with the language's "the LORD" as the default. Where the English keeps
"Hallelujah" as a word (as Revelation 19 does), use हल्लेलूयाह / Аллилуйя.
Instruments and tunes ("to the tune of ...") and the terms whose meaning is
lost (*gittit*, *sheminit*, *alamot*, *neginot*, *mahalat*) follow the
English level: kept as names where it keeps them (Hindi गित्तीत, शमीनीत,
अलामोत; Russian гиттит, шеминит, аламот), translated where it translates,
with the English decision's uncertainty carried into the language's own.

## Names of God and recurring terms

| Hebrew (English) | Hindi | Russian |
|---|---|---|
| YHWH; YHWH of hosts | as the earlier notes | as the earlier notes |
| *Elohim* (God) | परमेश्वर | Бог |
| *ʾAdonai* (Lord) | प्रभु (the first record of each block's file says how the setting tells it from YHWH) | Господь |
| *ʿElyon* (Most High) | परमप्रधान | Всевышний |
| *Shaddai* (Almighty) | सर्वशक्तिमान | Всемогущий |
| the Holy One of Israel | इस्राएल का पवित्र | Святой Израиля |
| my rock (*tsur*); my crag (*selaʿ*); my fortress | मेरी चट्टान; मेरी ऊँची चट्टान; मेरा गढ़ | моя скала; мой утёс; моя твердыня (as 2 Samuel 22) |
| refuge; shield; stronghold | शरणस्थान; ढाल; ऊँचा गढ़ | прибежище; щит; крепость |
| *ḥesed* (steadfast love / loyal love) | अटल प्रेम (every level, God's); between people as the Pentateuch note | неизменная любовь (every level, God's); between people as the Pentateuch note |
| the refrain "for he is good, his steadfast love is forever" (106; 107; 118; 136) | copy 1 Chronicles 16:34 at each level | copy 1 Chronicles 16:34 at each level |
| *ʾemunah*, *ʾemet* (faithfulness, truth) | सच्चाई (L), विश्वासयोग्यता (B, R) where it is God's; सत्य | верность; истина |
| *nefesh* (soul) | प्राण (L); मन, जीवन or "मैं" at B and R as the English does | душа (L); B and R as the English does |
| the wicked; evildoers | दुष्ट; कुकर्मी | нечестивые (L, B), злые люди (R); злодеи |
| the righteous; the upright | धर्मी; सीधे लोग | праведные; честные / прямодушные |
| the poor, the afflicted, the needy | ग़रीब, दीन, दरिद्र | бедный, угнетённый, нищий |
| salvation; save, deliver | उद्धार; बचाना, छुड़ाना | спасение; спасать, избавлять |
| Sheol; the Pit | शिओल (L), अधोलोक (B), मृत्यु का लोक (R), as 2 Samuel 22; गड्ढा (L), क़ब्र (B, R) | шеол (L), мир мёртвых (B, R); яма (L), могила (B, R) |
| Zion; Jerusalem | सिय्योन; यरूशलेम | Сион; Иерусалим |
| the nations; the peoples | जातियाँ (L), देश / राष्ट्र (B, R), never caste-sounding at B and R; लोग | народы; племена |
| the fear of the LORD | `{{divine_name:प्रभु\|याहवे}}` का भय (L, B); `{{divine_name:प्रभु\|याहवे}}` का आदर और भय मानना (R) | страх перед `{{divine_name:ГОСПОДОМ\|Яхве}}` (L, B); благоговение перед `{{divine_name:ГОСПОДОМ\|Яхве}}` (R) |
| the anointed (the king) | अभिषिक्त | помазанник |
| bless (God); praise (*hallel*); give thanks (*hodu*) | धन्य कहना; स्तुति करना; धन्यवाद करना | благословлять; хвалить; благодарить |
| God's *torah* | व्यवस्था (L, B); शिक्षा (R) | Закон (L, B); наставление (R) |
| *ʿeved* (the psalmist's "your servant"; Moses, David) | दास at every level | раб at every level |

Psalm 119's eight words (law, testimonies, precepts, statutes,
commandments, rules, word, promise) each have one fixed word per level,
recorded in decisions at 119:1-11 and kept through the psalm.

## Proverbs

| Hebrew (English) | Hindi | Russian |
|---|---|---|
| *ḥokmah* (wisdom) | बुद्धि | мудрость |
| *binah*, *tevunah* (understanding) | समझ | разум (L, B); понимание (R) |
| *daʿat* (knowledge) | ज्ञान | знание |
| *musar* (discipline; correction at R) | अनुशासन (L, B); सुधार (R) | наставление (L, B); вразумление (R) |
| *torah* of father or mother (teaching) | शिक्षा | наставление |
| *kesil*, *ʾewil* (fool) | मूर्ख | глупец |
| *lets* (mocker) | ठट्ठा करनेवाला | насмешник |
| *peti* (the simple / naive / easily fooled) | भोला (L, B); आसानी से बहकनेवाला (R) | простак (L), наивный (B), легковерный (R) |
| *ʿatsel* (sluggard) | आलसी | ленивец |
| *beni* (my son) | हे मेरे पुत्र (L, B); बेटा (R) | сын мой |
| the strange woman (as the English level: foreign / forbidden / another man's wife) | पराई स्त्री; R as the English | чужая жена; R as the English |

Wisdom and Folly personified are women in the Hebrew; बुद्धि and мудрость are
feminine, so the verbs and pronouns follow.

## Job, Ecclesiastes, Song of Songs

- **Job.** "The satan" (Literal) / "the Accuser" (Readable): Hindi शैतान (L),
  दोष लगानेवाला (B, R) as the English level has a title or a name; Russian
  сатана (L), Обвинитель (B, R). "The sons of God" are परमेश्वर के पुत्र (L),
  स्वर्गदूत / स्वर्गीय प्राणी (B, R), as the English level; сыны Божьи (L),
  небесные существа (B, R). Job's friends speak to him with तुम; Job to God
  with तू.
- **Ecclesiastes.** Qoheleth: कोहेलेत (L), उपदेशक (B, R); Когелет (L),
  Учитель (B, R), as the English level. *hevel* follows the English level:
  भाप / साँस (L, the image), व्यर्थ, क्षणभंगुर (B, R); дуновение / пар (L),
  тщетно, мимолётно (B, R), never the Synodal's суета сует. "Under the sun":
  सूर्य के नीचे / под солнцем at every level.
- **Song of Songs.** The lovers speak to each other with तुम in Hindi and ты
  in Russian. The speakers follow the English level's marks. The book is
  translated as love poetry; an allegorical reading is not added.

## Settled while drafting

(Recorded here as the blocks are harmonised.)
