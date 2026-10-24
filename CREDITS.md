# Credits

Open Word Bible is built on the following sources. Each is pinned to an exact
commit in `sources.lock.json`. The original-language text is always loaded
from these files; it is never typed by hand.

## SBL Greek New Testament (SBLGNT)

The SBLGNT, v1.2, is licensed under a Creative Commons Attribution 4.0
International License (CC BY 4.0). Copyright 2010 by the Society of Biblical
Literature and Logos Bible Software.
<https://github.com/LogosBible/SBLGNT>

## MACULA Greek Linguistic Datasets

MACULA Greek Linguistic Datasets, available at
<https://github.com/Clear-Bible/macula-greek/>. © 2022–2024 by Biblica, Inc.,
licensed under CC BY 4.0.

MACULA Greek includes:

- Glosses (`gloss`) from the Berean Interlinear Bible
  (<https://interlinearbible.com/>). The Berean Bible and Majority Bible texts
  were officially placed into the public domain as of April 30, 2023.
- Cherith Glosses for the Greek New Testament (`english`), by Andi Wu,
  Copyright (C) 2023 by Cherith Analytics, licensed under CC BY 4.0.
- Word-sense data from the United Bible Societies MARBLE project
  (`ln`, `domain`), used with permission. Open Word Bible does not use or
  redistribute these fields.

The word extracts in `data/grc/` are derived from MACULA Greek and carry its
CC BY 4.0 licence. They hold, per word: id, text, following punctuation,
lemma, morphology, the Berean and Cherith glosses, and Strong's number.

## MACULA Hebrew Linguistic Datasets

MACULA Hebrew Linguistic Datasets, available at
<https://github.com/Clear-Bible/macula-hebrew/>. © 2022–2024 by Biblica, Inc.,
licensed under CC BY 4.0.

MACULA Hebrew includes Cherith Glosses for the Hebrew Old Testament, by Andi
Wu, Copyright (C) 2022 by Cherith Analytics, licensed under CC BY 4.0; and the
Westminster Hebrew Syntax, Copyright (C) 1991–2018 by The J. Alan Groves Center
for Advanced Biblical Research, licensed under CC BY 4.0.

The word extracts in `data/hbo/` are derived from MACULA Hebrew and carry its
CC BY 4.0 licence. They hold, per morpheme: id, text, following punctuation,
transliteration, lemma, morphology (from the Open Scriptures Hebrew Bible),
the MACULA and Cherith glosses, Strong's number and language (Hebrew or
Aramaic). The word-sense columns (`sdbh`, `lexdomain`, `coredomain`,
`contextualdomain`) are not used or redistributed.

## Open Scriptures Hebrew Bible

Original work of the Open Scriptures Hebrew Bible available at https://github.com/openscriptures/morphhb

Licensed under CC BY 4.0.

The Hebrew-to-English verse numbering table in `data/versification.json` is
derived from its `wlc/VerseMap.xml` and carries its CC BY 4.0 licence.

## Westminster Leningrad Codex

The Hebrew text of the Westminster Leningrad Codex is in the public domain.

## Reference Bibles (public domain)

From [seven1m/open-bibles](https://github.com/seven1m/open-bibles), pinned in
`sources.lock.json`: the Berean Standard Bible, the World English Bible, the
American Standard Version (1901), the King James Version (Crown copyright
applies in the United Kingdom), Young's Literal Translation (New Testament)
and the Reina-Valera 1909. These are used for comparison and review only; Open
Word Bible is translated from the Hebrew and Greek.

The Berean Standard Bible, World English Bible and Reina-Valera 1909 verse
texts are kept in `data/comparison/`. The comparison page (`/compare/`) sets
a verse of ours beside all three. Where a note or a cross-reference names a
verse Open Word Bible has not yet translated, the reader shows that verse
from the World English Bible or the Reina-Valera 1909. Each is labelled as a
comparison text and not Open Word Bible wording.

## Cross-references

Cross-references from OpenBible.info
(<https://www.openbible.info/labs/cross-references/>), 2024-11-04, licensed
under CC BY. Pinned in `sources.lock.json` as the verbatim copy kept in
[scrollmapper/bible_databases](https://github.com/scrollmapper/bible_databases)
(`sources/extras/cross_references.txt`).

The files in `data/crossrefs/` are derived from it and carry its CC BY
licence. They hold, for each verse, its most-voted references (at most five,
each with at least three votes), with both ends moved to Open Word Bible's
verse numbering. The reader shows them in the margin and with each verse's
reasoning, credited to OpenBible.info. They are an aid to study, not part of
the translation.

## Fonts

The reading text and Greek are set in Gentium Book Plus, Copyright (c)
2003–2022 SIL International, Hebrew in Noto Serif Hebrew, Copyright 2022
The Noto Project Authors, and Amharic in Noto Serif Ethiopic and Noto Sans
Ethiopic, Copyright 2022 The Noto Project Authors. Headings are set in Fraunces, Copyright 2020 The
Fraunces Project Authors, and the interface in Hanken Grotesk, Copyright 2021
The Hanken Grotesk Project Authors. Readers can choose Atkinson Hyperlegible
for the reading text, Copyright 2020 Braille Institute of America, Inc. All
seven are licensed under the SIL Open Font License 1.1; the licences are in
`web/fonts/`.
