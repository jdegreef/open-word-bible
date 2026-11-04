# Amharic: Ecclesiastes, Song of Songs, Isaiah, Jeremiah and Lamentations

**Status: proposed, awaiting a native Amharic reviewer.** The choices used to
draft these five books in Amharic, so that books drafted in parallel read as
one translation. `docs/amharic-style.md` (7a on poetry), the Pentateuch,
Joshua–Samuel and Kings–Ezra terms lists, and the Nehemiah–Proverbs list
(`docs/nehemiah-proverbs-amharic-terms.md`) still hold; this list adds what
these books need. Decision text stays in English, quoting the Amharic words.

## Carried over

- Genesis to Ezra are on main in Amharic; Nehemiah to Proverbs are drafted
  (their branches are named in the drafting brief). Names, places and
  recurring words keep the forms used there: grep before choosing a new one.
- Divine names: YHWH `{{divine_name:እግዚአብሔር|ያህዌ}}` with the whole inflected
  word in each option; Yah `{{divine_name:እግዚአብሔር|ያህ}}`; Adonai ጌታ; Adonai
  YHWH L «ጌታ {{dn}}», B, R the English order; YHWH Tsevaot L «{{dn}} ጸባኦት»,
  B, R «የሠራዊት አምላክ {{dn}}»; El and Elohim እግዚአብሔር (አምላክ with a
  possessor, as a predicate, or beside YHWH in one verse); Eloah አምላክ;
  Shaddai ሁሉን የሚችል (L, B), ሁሉን የሚችል አምላክ (R). Suffixes go after `}}`.
- ḥesed ጽኑ ፍቅር; ʾemunah ታማኝነት; tsedeq / tsedaqah ጽድቅ; mishpat ፍርድ
  (L), ፍትሕ (B, R) where it means justice; Sheol ሲኦል (L), የሙታን ዓለም (B, R).
- No deity_pronoun spans; gender spans only where Amharic really has two
  wordings. Poetry keeps each level's `\q` breaks.

## The prophets (Isaiah, Jeremiah)

| Hebrew (English) | Amharic |
|---|---|
| Thus says the LORD | `{{divine_name:እግዚአብሔር\|ያህዌ}}` እንዲህ ይላል |
| declares the LORD (*neʾum YHWH*) | L ይላል `{{dn}}` (after the words); B, R the English wording |
| the word of the LORD came to me | `{{divine_name:የእግዚአብሔር\|የያህዌ}}` ቃል ወደ እኔ መጣ |
| oracle (*massa*) | የትንቢት ቃል (as Proverbs 30:1) |
| woe (*hoy*) | ወዮ |
| in that day | በዚያ ቀን |
| the Holy One of Israel | የእስራኤል ቅዱስ (as 2 Kings 19:22) |
| Redeemer (*goʾel*) | ቤዢ (L, B), the English R wording |
| my servant (Isaiah 41–53) | ባሪያዬ (L), አገልጋዬ (B, R) |
| remnant | ቅሬታ |
| the coastlands (*ʾiyyim*) | ደሴቶች (L), ጠረፎች (B, R) |
| comfort | አጽናና |
| idol (*pesel*); idols (*ʾelilim*) | የተቀረጸ ምስል; ከንቱ ጣዖታት |
| return / repent (*shuv*) | ተመለሰ |
| backsliding (*meshuvah*, Jeremiah) | ክህደት (L ከእግዚአብሔር መራቅ where the English says turning away) |
| the daughter of Zion / of my people | የጽዮን ልጅ / የሕዝቤ ልጅ (L); B, R the English wording |
| sword, famine and pestilence | ሰይፍ፣ ራብና ቸነፈር (one order and wording throughout Jeremiah) |
| the king of Babylon; the Chaldeans | የባቢሎን ንጉሥ; ከለዳውያን |

- Names: Isaiah son of Amoz የአሞጽ ልጅ ኢሳይያስ; Jeremiah son of Hilkiah
  የኬልቅያስ ልጅ ኤርምያስ; Anathoth ዓናቶት; Baruch son of Neriah የኔርያ ልጅ
  ባሮክ; Nebuchadnezzar ናቡከደነፆር (Jeremiah's Hebrew often spells it
  Nebuchadrezzar: follow the Hebrew only if the English does, with a
  decision); Gedaliah ጎዶልያስ; Ishmael son of Nethaniah የናታንያ ልጅ እስማኤል;
  Pashhur ፋስኮር; Hananiah ሐናንያ; Ebed-melech the Cushite ኩሻዊው አቤሜሌክ;
  Immanuel አማኑኤል (as Matthew 1:23); Cyrus ቂሮስ; Hezekiah ሕዝቅያስ.
- Isaiah 7:14 *ʿalmah*: follow the meaning decision ("a girl or young woman
  of age to marry"): ኮረዳ (L), ወጣት ሴት (B, R), with a decision noting that
  Matthew 1:23 quotes the Greek ድንግል.

## Parallels

- Isaiah 36–39 = 2 Kings 18:13–20:19 (on main): copy level by level where
  the Hebrew is the same; decision where it differs.
- Jeremiah 52 = 2 Kings 24:18–25:30 (on main); Jeremiah 39:1–10 overlaps
  both: copy where the Hebrew is the same.
- Inside Jeremiah: 6:13–15 = 8:10–12; 10:12–16 = 51:15–19; 16:14–15 =
  23:7–8; 23:5–6 ~ 33:15–16; 49:18–21 ~ 50:40–46; 30:10–11 = 46:27–28;
  10:25 = Psalm 79:6–7 (drafted in the Psalms branch).
- Isaiah 2:2–4 ~ Micah 4:1–3 (Isaiah drafts first).
- Ecclesiastes and Proverbs, Lamentations and Psalms share wisdom and lament
  vocabulary: follow the Nehemiah–Proverbs list (ጥበብ, ማስተዋል, ሞኝ, ሰነፍ ...).

## New Testament quotations

Isaiah and Jeremiah are quoted often. For each verse, look in
`data/crossrefs/<BOOK>.json` and keep the Amharic New Testament's wording
where the Hebrew agrees with the Greek; where they differ, follow the Hebrew
and say so. Among many: Isaiah 6:9–10; 7:14; 9:1–2; 11:10; 25:8; 28:16;
29:13; 40:3–5; 42:1–4; 49:6; 52:7, 15; 53:1–12; 54:1; 56:7; 61:1–2; 64:4;
65:1–2, 17; Jeremiah 7:11; 9:24; 31:15; 31:31–34.

## Ecclesiastes

- Qoheleth: L ቆሔሌት (as a name, with a decision); B, R መምህሩ (the English
  "the Teacher").
- *hevel* "breath" (the meaning decision: real but brief, beyond grasping):
  እስትንፋስ at every level of Literal and Balanced, as Psalm 39 and 62; "breath
  of breaths" L የእስትንፋስ እስትንፋስ; Readable follows the English R ("Nothing
  lasts", «ምንም አይዘልቅም»). One wording per phrase through all 12 chapters.
- "under the sun" ከፀሐይ በታች; "chasing wind" (*reʿut ruaḥ*) ነፋስን መከተል;
  "portion" (*ḥeleq*) ድርሻ; "gain" (*yitron*) ትርፍ; "toil" (*ʿamal*) ድካም;
  "God gives" with Elohim as እግዚአብሔር (Ecclesiastes has no YHWH).

## Song of Songs

- The lovers say አንተ / አንቺ to each other; "my beloved" (*dodi*) ውዴ; "my
  love / my darling" (*raʿyati*) ወዳጄ; "my sister, my bride" እኅቴ ሙሽራዬ;
  "daughters of Jerusalem" L የኢየሩሳሌም ሴቶች ልጆች, B, R the English wording.
- The adjuration refrain (2:7; 3:5; 8:4) and "my beloved is mine and I am
  his" (2:16; 6:3) read identically each time, as the Hebrew allows.
- The speakers' headings follow the English; no added labels.

## Lamentations

- Chapters 1–4 are acrostics; keep the English layout (no letter heads
  unless the English has them). "How!" (*ʾekhah*) ወዮ፣ እንዴት (L), the
  English B/R wording.
- The daughter of Zion as above; "the LORD has done what he planned" and
  the other echoes of Jeremiah keep Jeremiah's wording.
