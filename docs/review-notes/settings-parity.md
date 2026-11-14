# Settings parity audit

Are the reader settings used alike across languages, and across the three
levels of one language? `scripts/settings_parity.py` answers both; rerun it
after drafting (`python3 scripts/settings_parity.py --levels`, and `--strict`
to fail on an outlier nobody has explained). Records stay `ai_draft`: this
note lists what was found and changed for a reviewer to check.

## 1. Across languages

### Spans per language (November 2026)

Hindi and Russian cover 15,449 records, Ukrainian 5,325 and Japanese 2,432,
so their raw counts are not comparable with the rest; the parity table below
is.

| lang | records | gender | christos | divine_name | deity_pronoun | units | plural_you |
|---|---|---|---|---|---|---|---|
| en | 30637 | 5973 | 1649 | 20785 | 34458 | 1254 | 0 |
| es | 30637 | 1199 | 1654 | 20784 | 27587 | 1271 | 34887 |
| fr | 30637 | 4288 | 1650 | 20783 | 36524 | 1258 | 0 |
| sw | 30637 | 13 | 1650 | 20787 | 22289 | 1271 | 0 |
| vi | 30637 | 701 | 1656 | 20791 | 38293 | 1280 | 0 |
| ko | 30637 | 961 | 1660 | 20874 | 0 | 1257 | 0 |
| pt | 30637 | 1888 | 1649 | 20737 | 33216 | 1244 | 0 |
| am | 30637 | 776 | 1653 | 20786 | 0 | 1272 | 0 |
| hi | 15449 | 1555 | 0 | 7760 | 0 | 561 | 0 |
| ru | 15449 | 1578 | 1654 | 7751 | 16912 | 565 | 0 |
| uk | 5325 | 435 | 610 | 0 | 10296 | 98 | 0 |
| ja | 2432 | 202 | 508 | 0 | 0 | 24 | 0 |

`plural_you` is a Spanish-only setting (`data/languages.json`). Ukrainian and
Japanese have no Old Testament records yet, so no `divine_name` spans.

### Parity with English

Of the records where the English spans a setting (at any level), the share
where the language spans the same setting (at any level).

| lang | gender | christos | divine_name | deity_pronoun | units |
|---|---|---|---|---|---|
| es | 643/2295 (28%) | 483/483 (100%) | 5933/5933 (100%) | 6783/7769 (87%) | 399/399 (100%) |
| fr | 1667/2295 (73%) | 483/483 (100%) | 5933/5933 (100%) | 7726/7769 (99%) | 399/399 (100%) |
| sw | 7/2295 (0%) | 483/483 (100%) | 5933/5933 (100%) | 5696/7769 (73%) | 399/399 (100%) |
| vi | 246/2295 (11%) | 483/483 (100%) | 5933/5933 (100%) | 7332/7769 (94%) | 399/399 (100%) |
| ko | 372/2295 (16%) | 483/483 (100%) | 5933/5933 (100%) | 0/7769 (0%) | 399/399 (100%) |
| pt | 877/2295 (38%) | 483/483 (100%) | 5933/5933 (100%) | 7632/7769 (98%) | 399/399 (100%) |
| am | 298/2295 (13%) | 483/483 (100%) | 5933/5933 (100%) | 0/7769 (0%) | 399/399 (100%) |
| hi | 874/1482 (59%) | 0/483 (0%) | 2173/2173 (100%) | 0/3768 (0%) | 203/203 (100%) |
| ru | 875/1482 (59%) | 483/483 (100%) | 2173/2173 (100%) | 3563/3768 (95%) | 203/203 (100%) |
| uk | 162/450 (36%) | 180/180 (100%) | - | 2277/2361 (96%) | 43/43 (100%) |
| ja | 78/241 (32%) | 143/143 (100%) | - | 0/908 (0%) | 10/10 (100%) |

`christos`, `divine_name` and `units` are at full parity in every language
that uses them. `gender` varies widely, as it should: whether a language
needs a span depends on whether its own word for people is gendered.

### Outliers and verdicts

An outlier is a share of zero or below half the median of the languages. All
eight are by design, and each brief now says why.

| Outlier | Verdict | Where it is explained |
|---|---|---|
| hi christos, 0 spans (every other language about 1,650) | **Design.** मसीह is both the familiar name in यीशु मसीह and the word Messiah, so the choice the English setting offers is already made; ख्रीष्ट is a church transliteration, not a second way of saying "Messiah". Every one of the 166 passage files where the English spans *Christos* has a Hindi decision that says so. | `docs/hindi-style.md` section 7 (now marked checked) |
| sw gender, 13 spans (en 5,973, fr 4,288) | **Design.** Swahili words for people (*watu*, *mtu*, *watoto*, *wana*, *ndugu*, *wazazi*, *mababu*) carry no gender, and the gendered alternative (*wanaume*) would change the meaning. The Swahili decisions say so record by record (for example Acts 3:13, 7:11, 13:17; Hebrews 1:1, 3:7, 8:8; Numbers 20:15; 2 Kings 14:6; Jeremiah 31:29; Ezekiel 18:2; Proverbs 17:6). | `docs/swahili-style.md` section 7, now with the list of English spans and what Swahili says instead |
| am, hi, ko, ja deity_pronoun, 0 spans | **Design.** The Ethiopic, Devanagari, Hangul and Japanese scripts have no capital letters, so the setting has nothing to change. | the four briefs, section on settings |
| am, vi gender, 13% and 11% | **Design.** Amharic and Vietnamese nouns for people are inclusive; spans only for *adelphoi* and *andres*. | `docs/amharic-style.md`, `docs/vietnamese-style.md` |

One inconsistency inside the Swahili design is left for a reviewer: for
"ancestors / fathers" most passages say *mababu* plainly, but John 6:49 and
6:58 and Acts 24:14 and 26:6 give `{{gender:wahenga|mababu}}`. Both are
defensible (the brief says so); a reviewer should settle one practice
before it spreads. Nothing was changed.

Swahili `deity_pronoun` (73%) is below the others but not an outlier: most
Swahili pronouns are verb prefixes, which cannot take a capital
(`docs/swahili-style.md` section 7).

## 2. Across levels

A record's three levels say the same thing, so a pronoun for God (or the
title *Christos*, or the divine name) that one level spans should be spanned
at another level wherever that level uses the same word. The English brief
asks for a span on every pronoun for God or Christ at every level, except a
capitalised pronoun starting a sentence.

`settings_parity.py --levels` looks at every record, language and pair of
levels where one level spans `deity_pronoun`, `christos` or `divine_name`
and the other has no span of it, and checks whether the other level holds
the first level's default wording (the span's first option: "he", "my",
*mimi*, "Christ", "the LORD") outside a span:

- **fine**: it does not. The other level says it differently: "God" or
  "Jesus" instead of "he", the pronoun left out, or "He" starting a sentence.
- **candidate**: it does. The same "he" is often someone else (Moses, the
  angel, the man in a parable), so a candidate needs a reader.
- **likely gap**: a candidate where at least two other languages span the
  setting at that level of the same record.

`python3 scripts/settings_parity.py --list <lang> <setting>` lists the
candidates and likely gaps of one language.

### English: Balanced spans a pronoun for God and Readable has none

The question that started this: 1,016 English records span `deity_pronoun`
at Balanced and have no span at Readable. In 981 of them the Readable does
not use the pronoun at all (it names God or Jesus, or starts the sentence
with "He"): fine. 35 had the pronoun unwrapped; 3 were real gaps (Isaiah
54:8, 54:10, Micah 6:3), the rest someone else's pronoun. After the fixes:
1,013 records, 32 with the pronoun unwrapped, all read and found to be
someone else's.

### Counts before and after

Records (per language and setting, each counted once) where one level spans
the setting and another has none of it.

| lang | setting | fine | candidate | likely gap | after: fine | candidate | likely gap |
|---|---|---|---|---|---|---|---|
| en | deity_pronoun | 2330 | 116 | 14 | 2333 | 111 | 9 |
| es | deity_pronoun | 2156 | 120 | 61 | 2158 | 118 | 53 |
| fr | deity_pronoun | 2328 | 210 | 15 | 2329 | 208 | 13 |
| sw | deity_pronoun | 2272 | 51 | 46 | 2282 | 51 | 22 |
| vi | deity_pronoun | 2621 | 30 | 1 | 2621 | 30 | 1 |
| pt | deity_pronoun | 2208 | 187 | 26 | 2210 | 185 | 22 |
| ru | deity_pronoun | 1412 | 66 | 16 | 1412 | 66 | 16 |
| uk | deity_pronoun | 836 | 39 | 12 | 836 | 39 | 12 |
| all 11 | christos | 315 | 2 | 0 | 315 | 2 | 0 |
| all 10 | divine_name | 1126 | 36 | 0 | 1126 | 36 | 0 |

A record whose gap was fixed drops out of the table (both levels now have a
span), so the "fine" column moves only where another pair of levels in the
same record was already fine.

### What was read, and what was fixed

Every likely gap in every language was read, and every English candidate.
60 spans in 57 renderings (47 files) were added around the word that was
already there (no wording changed), and 1 Psalms rendering is in
`pending-psalms-patches.jsonl`. Spans per language:

- **English (10):** 2 Chronicles 32:22 L; Exodus 34:7 L; Job 36:11 L
  ("serve [him]"); Isaiah 54:8 R, 54:10 R; Daniel 9:3 L; Micah 6:3 R;
  Mark 15:37 L ("breathed [his] last"); Romans 3:5 L ("is he?");
  Revelation 21:6 R.
- **Spanish (11, and 1 in the patch file):** Isaiah 10:24 R, 26:20 R ("Pueblo mío"), 30:28 B and R
  ("su aliento"), 54:8 R, 54:10 R; Jeremiah 3:12 R, 29:14 L; Ezekiel 15:7
  R; Matthew 27:26 R; Acts 5:30 L; and Psalm 94:1 B (patch file).
- **French (5):** Isaiah 3:13 L, 41:4 R, 54:15 R; Luke 22:32 L and B
  ("Mais moi").
- **Portuguese (7):** Jeremiah 29:14 L; Ezekiel 20:31 L (twice), 35:11 L;
  Matthew 26:57 L; John 1:45 L; Revelation 21:6 R.
- **Swahili (27):** free pronouns for God or Jesus left plain at one level
  (*mimi*, *wewe*, *yeye*, *nami*, *naye*, *wangu*, *kwangu*, *kwake*):
  Exodus 12:13 L; 1 Samuel 10:19 B; Isaiah 1:11 L, 10:24 R, 20:3 R, 31:2 R,
  40:25 B; Jeremiah 6:14 R, 8:11 R, 9:23 R, 30:21 L; Matthew 4:21 L;
  Mark 1:13 L; Luke 8:32 L, 11:37 L; John 6:70 L, 7:23 R, 8:3 L, 8:45 R,
  8:48 R, 9:37 L, 12:8 B and R; Romans 16:25 L (three spans);
  Revelation 19:11 L.

The likely gaps still listed (en 9, es 53, fr 13, sw 22, pt 22, ru 16,
uk 12, vi 1) were read and are someone else's pronoun: "lo que" (Spanish
"what"), Portuguese and French articles *o* and *le*, the man Jesus healed,
Herod, Pilate, the scribe who asked. Russian and Ukrainian had no real gaps.
The **candidates** below the likely-gap line (es 118, fr 208, pt 185, sw 51,
ru 66, uk 39, vi 30) were not all read; the English ones were, and gave 5
of the 10 English fixes. They are the next list for a reviewer of each
language.

`christos` and `divine_name` have no gaps across levels. The candidates are
"antichrist" (Korean 적그리스도, Vietnamese *kẻ chống Đấng Christ*, which
takes no span), the Korean syllable 주 inside other words, Hindi प्रभु for
*Adonai* (Genesis 18:30-32), and Amharic እግዚአብሔር for *Elohim*, as the
English says "God".
