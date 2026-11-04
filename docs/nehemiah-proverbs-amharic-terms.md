# Amharic: Nehemiah, Esther, Job, Psalms and Proverbs

**Status: proposed, awaiting a native Amharic reviewer.** The choices used to
draft Nehemiah, Esther, Job, Psalms and Proverbs in Amharic, so that books
drafted in parallel read as one translation. `docs/amharic-style.md` (section
7a on poetry), `docs/pentateuch-amharic-terms.md`,
`docs/joshua-samuel-amharic-terms.md` and
`docs/kings-chronicles-ezra-amharic-terms.md` still hold; this list adds what
these books need. Decision text stays in English, quoting the Amharic words.

## Carried over

- Genesis to Ezra are on main in Amharic. Names, places and recurring words
  keep the forms used there: grep before choosing a new one.
- ḥesed is ጽኑ ፍቅር; "for his steadfast love endures forever" follows Ezra
  3:11 (L «… ጽኑ ፍቅሩ ለዘላለም ነውና።»; B, R «… ጽኑ ፍቅሩም ለዘላለም ይኖራል።»).
- Sheol: L ሲኦል; B, R የሙታን ዓለም. El Shaddai ሁሉን የሚችል አምላክ; Shaddai alone
  ሁሉን የሚችል (L, B), ሁሉን የሚችል አምላክ (R). Eloah አምላክ.
- YHWH Tsevaot: L `{{divine_name:እግዚአብሔር|ያህዌ}} ጸባኦት`; B, R `የሠራዊት አምላክ
  {{divine_name:እግዚአብሔር|ያህዌ}}`. Adonai ጌታ. -ም and other suffixes go after
  the closing `}}` of a divine_name span.
- Address to a king: እርስዎ, ጌታዬ ንጉሥ, ባሪያዎ (L) / አገልጋይዎ (B, R). Prayer and
  praise to God: አንተ; "your servant" in prayer ባሪያህ (L) / አገልጋይህ (B, R).
- No deity_pronoun spans (Ethiopic has no capitals); gender spans only where
  Amharic really has two wordings (ሰው already covers men and women).

## Poetry

- Job 3:1–42:6, the Psalms and Proverbs are poetry: keep every `\q ` line
  break of each level's English, one Amharic line per English line, the
  parallel lines balanced. Literal follows the Hebrew line order.
- Psalm headings are verse 1 (or 1–2) in the Hebrew numbering the records
  use. Keep them as a plain line before the psalm, no quotation marks.

| Heading word | Amharic |
|---|---|
| To the choirmaster (*lamnatseaḥ*) | ለመዘምራን አለቃ |
| A psalm (*mizmor*); a song (*shir*); a prayer (*tefillah*) | መዝሙር; ቅኔ (L), መዝሙር (B, R) where the English says song; ጸሎት |
| Of David (*le-David*) | የዳዊት |
| maskil; miktam; shiggaion | ማስኪል; ሚክታም; ሽጋዮን (names, with a decision; R may gloss) |
| with stringed instruments; on the sheminith; according to the gittith | በባለ አውታር መሣሪያዎች; በሸሚኒት (1 Chr 15:21); በጊቲት |
| A song of ascents | የመውጣት መዝሙር |
| Selah | ሴላ, kept at the end of its line at every level, as the English |
| Hallelujah (*halelu-yah*) | ሃሌ ሉያ (Revelation 19 on main); where the English translates it, «{{divine_name:እግዚአብሔርን\|ያህዌን}} አመስግኑ» |

## God and worship

| Hebrew (English) | Amharic |
|---|---|
| bless (God) / blessed be | ባረከ; ይባረክ (L, B), ይመስገን (R) |
| praise (*hillel*); give thanks (*hodah*); sing praise (*zimmer*) | አመሰገነ / አወደሰ; አመሰገነ; ዘመረ |
| how blessed (*ʾashrei*) | ምስጉን ነው (L), የተባረከ ነው (B), ደስተኛ ነው (R): follow the English level |
| steadfast love; faithfulness (*ʾemunah*); truth (*ʾemet*) | ጽኑ ፍቅር; ታማኝነት; እውነት |
| righteousness; justice (*mishpat*); salvation | ጽድቅ; ፍርድ (L), ፍትሕ (B, R); ማዳን, መዳን |
| refuge; rock; fortress; shield | መጠጊያ; ዓለት; ምሽግ; ጋሻ (as 2 Samuel 22) |
| the anointed (*mashiaḥ*) | `{{divine_name}}` የቀባው (L, B), the English R wording; NT quotations keep the NT form |
| Zion; the holy hill | ጽዮን; የተቀደሰው ተራራ |
| the nations (*goyim*); the peoples (*ʿammim*) | ሕዝቦች; ወገኖች where both stand in one line, else ሕዝቦች |
| the wicked (*rashaʿ*); the righteous (*tsaddiq*) | ክፉ ሰው, ክፉዎች (L ኃጥኣን where the English L says "the wicked" in parallel with sinners); ጻድቅ, ጻድቃን |
| enemies; foes (*tsarim*) | ጠላቶች; ባላጋራዎች |
| the poor (*ʿani*); the needy (*ʾevyon*) | ድሆች, ችግረኞች (L ጐስቋሎች where paired); ምስኪኖች |

## Psalm 119

One agent drafts the whole psalm, so the eight law words keep one Amharic
word each through all 176 verses: law (*torah*) ሕግ; testimonies (*ʿedot*)
ምስክርነቶች; precepts (*piqqudim*) መመሪያዎች; statutes (*ḥuqqim*) ሥርዓቶች;
commandments (*mitswot*) ትእዛዛት; judgments (*mishpatim*) ፍርዶች; word
(*davar*) ቃል; promise / word (*ʾimrah*) ተስፋ ቃል (L ንግግር where the English L
says "word"). The acrostic letter heads are kept as the English has them.

## Wisdom words (Job, Proverbs)

| Hebrew (English) | Amharic |
|---|---|
| wisdom; understanding (*binah*, *tevunah*); knowledge | ጥበብ; ማስተዋል; እውቀት |
| discipline, instruction (*musar*); rebuke (*tokhaḥat*) | ተግሣጽ; ዘለፋ |
| prudence (*ʿormah*); discretion (*mezimmah*) | ብልሃት; ጥንቃቄ |
| the fear of the LORD | `{{divine_name:እግዚአብሔርን\|ያህዌን}}` መፍራት |
| fool (*kesil*); fool (*ʾewil*); fool (*naval*) | ሞኝ; ሰነፍ; ባለጌ |
| the simple (*peti*); mocker (*lets*); sluggard (*ʿatsel*) | አላዋቂ; ፌዘኛ; ታካች |
| the strange / forbidden woman (*zarah*, *nokhriyyah*) | ባዕድ ሴት (L), አመንዝራ ሴት (B, R where the English says so) |
| my son (Proverbs 1–9) | ልጄ |
| the satan (Job 1–2) | ሰይጣን, with a decision following the meaning decision on the record |
| redeemer (*goʾel*, Job 19:25) | ቤዢ (L), the English B/R wording, as Leviticus 25 and Ruth |

## Nehemiah and Esther

- Nehemiah 7:6–73 repeats Ezra 2: copy the Amharic of Ezra 2 (on main) name
  for name and line for line where the Hebrew is the same; where Nehemiah's
  Hebrew differs (a number, a spelling), follow it and add a decision.
- Nehemiah 9 recalls Genesis to Judges: keep the Amharic of the passages it
  echoes where the wording is the same (Exodus 34:6 for "gracious and
  merciful").
- Persian court words follow Ezra on main: Beyond the River የወንዝ ማዶ;
  province አውራጃ; governor (*peḥah*) አገረ ገዥ; satraps ጠቅላይ ገዢዎች; officials
  ሹማምንት (L, B), ባለ ሥልጣናት (R); decree አዋጅ, ትእዛዝ; letter ደብዳቤ.
- Nehemiah's memoir is first person (-ኩ / -ሁ as docs/amharic-style.md 7b).
- Esther has no divine name; do not add one.

| English | Amharic |
|---|---|
| Nehemiah; Hanani; Sanballat; Tobiah; Geshem; Ezra | ነህምያ; አናኒ; ሰንባላጥ; ጦቢያ; ጌሳም; ዕዝራ |
| Artaxerxes; Susa the citadel; Chislev; Nisan; Elul | አርጤክስስ; ሱሳ ግንብ; ካሴሉ; ኒሳን; ኤሉል |
| Ahasuerus; Vashti; Esther (Hadassah); Mordecai; Haman son of Hammedatha the Agagite | አሕሻዊሮስ; አስጢን; አስቴር (ሀደሳ); መርዶክዮስ; የአጋጋዊው የሐመዳቱ ልጅ ሐማ |
| Hegai; Zeresh; Hathach; Adar; Purim; pur (lot) | ሄጌ; ዞሳራ; አታክ; አዳር; ፉሪም; ፉር |
| India to Cush; 127 provinces | ከህንድ እስከ ኢትዮጵያ (ኩሽ at L, with a decision); 127 አውራጃዎች |
| Job; Uz; Eliphaz the Temanite; Bildad the Shuhite; Zophar the Naamathite; Elihu son of Barachel the Buzite | ኢዮብ; ዖፅ; ቴማናዊው ኤልፋዝ; ሹሐዊው በልዳዶስ; ነዕማታዊው ሶፋር; ቡዛዊው የባርክኤል ልጅ ኤሊሁ |
| Behemoth; Leviathan; Rahab (the sea monster) | ብሔሞት; ሌዋታን; ራሃብ (the Hebrew differs from Rahab of Jericho, ረዓብ; a decision says so) |
| Agur son of Jakeh; Lemuel; Massa | የያቄ ልጅ አጉር; ልሙኤል; ማሳ |

## New Testament quotations

The Psalms and Proverbs are quoted often in the Amharic New Testament on
main. For each verse, look it up in `vendor/openbible-crossrefs` (or grep the
New Testament English for the phrase) and keep the New Testament's Amharic
wording where the Hebrew agrees with the Greek: among many, Psalms 2:7; 8:4–6;
16:8–11; 22:1, 18; 40:6–8; 45:6–7; 69:9; 95:7–11; 110:1, 4; 118:22–23;
Proverbs 3:11–12, 34; 25:21–22; 26:11; Job 5:13.

## Parallels already drafted

- Psalm 18 = 2 Samuel 22 (on main): copy level by level where the Hebrew is
  the same.
- Psalm 105:1–15, 96 and 106:1, 47–48 = 1 Chronicles 16:8–36 (on main):
  copy where the Hebrew is the same.
- Psalm 14 = Psalm 53; Psalm 40:13–17 = Psalm 70; Psalm 57:7–11 and 60:5–12 =
  Psalm 108: the later psalm copies the earlier where the Hebrew is the
  same.
- Proverbs repeats sayings (e.g. 14:12 = 16:25; 18:8 = 26:22; 21:9 = 25:24;
  22:3 = 27:12): the second keeps the first's wording.
