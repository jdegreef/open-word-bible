# Amharic: Obadiah to Malachi

> **Reference:** `docs/amharic-glossary.md` is the consolidated Amharic glossary for the whole Bible and the reference for every book; where this per-batch list and the glossary differ, the glossary wins.

**Status: proposed, awaiting a native Amharic reviewer.** The choices used to
draft the last nine books of the Old Testament in Amharic (Obadiah, Jonah,
Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi), so that books
drafted in parallel read as one translation. `docs/amharic-style.md` and the
earlier terms lists still hold, above all the prophets table of
`docs/ecclesiastes-lamentations-amharic-terms.md` and the formulas of
`docs/ezekiel-amos-amharic-terms.md`. Decision text stays in English, quoting
the Amharic words.

## Carried over

- Genesis to Amos are on main in Amharic. Names, places and recurring words
  keep the forms used there: grep before choosing a new one.
- "Thus says the LORD" «{{dn}} እንዲህ ይላል»; "declares the LORD" «ይላል {{dn}}»
  after the words; "the word of the LORD came to X" «{{divine_name:የእግዚአብሔር|የያህዌ}}
  ቃል ወደ X መጣ»; oracle (*massa*) የትንቢት ቃል; woe ወዮ; in that day በዚያ ቀን;
  the day of the LORD {{divine_name:የእግዚአብሔር|የያህዌ}} ቀን; remnant ቅሬታ; YHWH Tsevaot L «{{dn}}
  ጸባኦት», B, R «የሠራዊት አምላክ {{dn}}». Suffixes go after `}}` only where
  they are -ም; any other inflection goes inside both options.
- ḥesed ጽኑ ፍቅር; the covenant formula «ሕዝቤ ይሆናሉ፤ እኔም አምላካቸው እሆናለሁ».
- "Gracious and merciful, slow to anger, abounding in steadfast love" (Jonah
  4:2, as Exodus 34:6 and Joel 2:13 on main): copy Joel 2:13's wording.
- The satan (Zechariah 3:1–2): as Job 1–2 (L ሰይጣኑ; B, R ከሳሹ), with a
  decision following the meaning decision on the record.

## Names

| English | Amharic |
|---|---|
| Obadiah; Edom; Esau; Teman; Mount Esau | አብድዩ; ኤዶም; ዔሳው; ቴማን; የዔሳው ተራራ |
| Jonah son of Amittai; Nineveh; Tarshish; Joppa | የአማቴ ልጅ ዮናስ (2 Kings 14:25); ነነዌ; ተርሴስ; ኢዮጴ |
| Micah of Moresheth; Bethlehem Ephrathah | ሞሬሽታዊው ሚክያስ (as Jeremiah 26:18); ቤተ ልሔም ኤፍራታ |
| Nahum the Elkoshite | ኤልቆሻዊው ናሆም |
| Habakkuk; shigionoth | ዕንባቆም; ሽጋዮኖት (as Psalm 7's ሽጋዮን) |
| Zephaniah son of Cushi | የኩሲ ልጅ ሶፎንያስ |
| Haggai; Zerubbabel son of Shealtiel; Joshua son of Jehozadak | ሐጌ; የሰላትያል ልጅ ዘሩባቤል; የኢዮሴዴቅ ልጅ ኢያሱ (as Ezra 3:2) |
| Zechariah son of Berechiah son of Iddo | የአዶ ልጅ የበራክዩ ልጅ ዘካርያስ |
| Malachi; Elijah the prophet | ሚልክያስ; ነቢዩ ኤልያስ |

Where a name already has a form on main (grep the English name in content/), main wins over this table; report the difference. Darius ዳርዮስ, the months and Persian titles follow Ezra and Daniel on main.

## Parallels

- Obadiah 1–9 ~ Jeremiah 49:7–16 (on main): copy level by level where the
  Hebrew is the same; decision where it differs.
- Micah 4:1–3 = Isaiah 2:2–4 (on main): copy where the Hebrew is the same;
  4:4–5 is Micah's own.
- Nahum 1:15 (Hebrew 2:1) ~ Isaiah 52:7; Zephaniah 1:18 = Ezekiel 7:19;
  Zephaniah 1:14–16 and Joel 2:1–2 share the day of the LORD's words;
  Habakkuk 2:14 ~ Isaiah 11:9; Zechariah 8:8 and 13:9 use the covenant
  formula.
- Jonah 2 is a psalm: use the Psalms' vocabulary (on main) for its lines.

## New Testament quotations

For each verse, look in `data/crossrefs/<BOOK>.json` and keep the Amharic New
Testament's wording where the Hebrew agrees with the Greek; where they differ,
follow the Hebrew and say so in a decision. Among many: Jonah 1:17 (Matthew
12:40); Micah 5:2 (Matthew 2:6); Micah 7:6 (Matthew 10:35–36); Habakkuk 1:5
(Acts 13:41); Habakkuk 2:3–4 (Romans 1:17; Galatians 3:11; Hebrews 10:37–38);
Haggai 2:6 (Hebrews 12:26); Zechariah 9:9 (Matthew 21:5; John 12:15); 11:12–13
(Matthew 27:9–10); 12:10 (John 19:37; Revelation 1:7); 13:7 (Matthew 26:31);
8:16 (Ephesians 4:25); Malachi 1:2–3 (Romans 9:13); 3:1 (Matthew 11:10; Mark
1:2); 4:5–6 (Hebrew 3:23–24; Luke 1:17; Matthew 17:11).

## Book notes

- Jonah: the great fish ታላቅ ዓሣ; the plant (*qiqayon*) ቅል; "Arise, go to
  Nineveh, that great city" one wording in 1:2 and 3:2.
- Micah 6:8 is drafted fresh from the Hebrew.
- Habakkuk 3 is a prayer-psalm: its heading and Selah follow the Psalms list
  (ሴላ at the end of its line, «ለመዘምራን አለቃ» in 3:19).
- Zechariah's visions: the angel who talked with me «ከእኔ ጋር የሚነጋገረው
  መልአክ»; the angel of the LORD «{{divine_name:የእግዚአብሔር|የያህዌ}} መልአክ»; the Branch (*tsemaḥ*,
  3:8; 6:12) as Jeremiah 23:5 and 33:15 on main; the lampstand መቅረዝ; the
  flying scroll የሚበር ጥቅልል መጽሐፍ.
- Malachi's disputations keep one frame: "But you say, How …?" L «እናንተ
  ግን፦ … እንዴት ነው? ትላላችሁ», B and R the English wording.
