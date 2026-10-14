---
title: Why we never type Greek or Hebrew by hand
summary: One firm rule protects the accuracy of everything Open Word Bible shows of the original languages. Here is the rule, and how the software enforces it.
date: 2026-10-10
order: 9
section: method
---
Open Word Bible has a rule that surprises people: no one, human or AI, ever types a Greek or Hebrew word into the translation or its notes. Every original-language word you see on this site, including the Greek and Hebrew in these articles, is copied by software from fixed source data.

## Why

Greek and Hebrew are hard to type correctly. Greek has accents and breathing marks; Hebrew has vowel points and cantillation marks. Many of them look almost identical on screen but are different characters underneath. A Greek omicron and a Latin "o" look the same in most fonts. Some accented Greek vowels can be stored in two different ways that display identically. A word typed from memory can look right and still be wrong: a different accent, a missing breathing, a letter that does not exist in the source at all.

In early testing, Greek typed from memory contained exactly these errors. A translation that claims to show its work cannot show the wrong words.

## The sources

The text comes from fixed, openly licensed editions, each pinned to an exact version so that every result can be reproduced:

- **New Testament:** the SBL Greek New Testament (version 1.2), with word-by-word data from MACULA Greek.
- **Old Testament:** the Westminster Leningrad Codex, with word data from MACULA Hebrew and the Open Scriptures Hebrew Bible.

"Pinned" means more than naming an edition. The project records the exact revision of each source it downloads, so the text cannot change underneath the translation without anyone noticing. Full credits are on the [About](/about/) page.

## How it is enforced

The rule is not just a habit; the software checks it on every change.

- The original text of each sentence is rebuilt from the source data, and a sentence whose text does not match is rejected.
- Any Greek or Hebrew word anywhere else, in a gloss, a translation or a note, must match a form or dictionary word in the source data exactly, character for character. A word with a wrong accent fails the check.
- These articles quote Greek and Hebrew through placeholders that the site fills in from the data when it is built. When this article shows the first words of John's Gospel, {{GREEK:JHN.1.1:1-5}}, the words come from the SBL Greek New Testament data, not from a keyboard.

A placeholder names a verse and a word number. The first word of Genesis, {{HEBREW:GEN.1.1:1}}, is written as one word but has two parts: a prefix meaning "in" and the noun "beginning". A placeholder can ask for the second part alone, in its dictionary form, {{LEMMA:GEN.1.1:1.2}}. The two do not look quite the same: the form in the text carries a cantillation mark for chanting, and the dictionary form does not. Typed by hand, that difference is easy to get wrong. Copied from the data, it cannot be.

These checks run automatically before anything is published. A placeholder that points to a Greek word in an Old Testament verse, or to a word that does not exist, stops the site from building.

## Fair questions

**Does this mean the source text can never be questioned?** No. The source text is never edited, but the translation may disagree with it, openly. In John 1:3 the record reads the punctuation differently from the SBL Greek New Testament, and a decision explains why. Where manuscripts differ, a decision describes the other reading. The base text stays fixed so that every departure from it is visible.

**Does a checked word guarantee a correct note?** No. The check proves that a word is really in the source. It cannot prove that a note says the right thing about it. That is what human reviewers are for.
