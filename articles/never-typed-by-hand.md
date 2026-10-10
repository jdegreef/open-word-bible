---
title: Why we never type Greek or Hebrew by hand
summary: One firm rule protects the accuracy of everything Open Word Bible shows of the original languages. Here is the rule, and how the software enforces it.
date: 2026-10-10
order: 9
---
Open Word Bible has a rule that surprises people: no one, human or AI, ever types a Greek or Hebrew word into the translation or its notes. Every original-language word you see on this site, including the Greek in these articles, is copied by software from fixed source data.

## Why

Greek and Hebrew are hard to type correctly. Greek has accents and breathing marks; Hebrew has vowel points and cantillation marks. Many of them look almost identical on screen but are different characters underneath. A word typed from memory can look right and still be wrong: a different accent, a missing breathing, a letter that does not exist in the source at all.

In early testing, Greek typed from memory contained exactly these errors. A translation that claims to show its work cannot show the wrong words.

## The sources

The text comes from fixed, openly licensed editions, each pinned to an exact version so that every result can be reproduced:

- **New Testament:** the SBL Greek New Testament (version 1.2), with word-by-word data from MACULA Greek.
- **Old Testament:** the Westminster Leningrad Codex, with word data from MACULA Hebrew and the Open Scriptures Hebrew Bible.

Full credits are on the [About](/about/) page.

## How it is enforced

The rule is not just a habit; the software checks it on every change.

- The original text of each sentence is rebuilt from the source data, and a sentence whose text does not match is rejected.
- Any Greek or Hebrew word anywhere else, in a gloss, a translation or a note, must match a form or dictionary word in the source data exactly, character for character. A word with a wrong accent fails the check.
- These articles quote Greek through placeholders that the site fills in from the data when it is built. When this article shows the first words of John's Gospel, {{GREEK:JHN.1.1:1-5}}, the words come from the SBL Greek New Testament data, not from a keyboard.

These checks run automatically before anything is published.
