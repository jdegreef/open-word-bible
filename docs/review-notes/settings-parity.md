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
