---
title: "Showing our work: what a reasoning record is"
summary: Every sentence in Open Word Bible carries a record of the original words, a gloss, three translations and every decision behind them.
date: 2026-10-10
order: 2
nav_title: What a reasoning record is
section: method
---
Open any verse on this site and a panel opens beside it. What you see there is the verse's *reasoning record*. It is the heart of the project, and it is worth knowing what is in it.

## One record per sentence

A record covers one sentence of the original, not one verse. Verse numbers were added to the Bible centuries after it was written, and they do not always fall at the ends of sentences. Philippians 4:5 holds two sentences, so it has two records; John 1:12–13 is one long sentence across two verses, so it has one. Paul's longest sentences stay whole in a single record, even when the English breaks them into two or three sentences to keep them readable.

Where the record ends is itself sometimes a decision. The ancient manuscripts had almost no punctuation, so editors decide where sentences stop. At the end of John 1:3 the record reads the punctuation differently from the Greek edition it follows, and a decision explains why. See [Punctuation the apostles never wrote](/articles/punctuation-the-apostles-never-wrote/).

## What a record holds

- **The original words**, loaded from a fixed edition of the source text. For the New Testament that is the SBL Greek New Testament, with word-by-word grammar from the MACULA project; for the Old Testament, the Westminster Leningrad Codex. Tap a word in the panel to see its dictionary form, its grammar and a gloss.
- **A literal gloss**: the words in the original order, as near word for word as English allows. It is not meant to read well. It lets you see the shape of the sentence.
- **The translation at three levels**, Literal, Balanced and Readable, in each language. See [Three levels, one meaning](/articles/three-levels-one-meaning/).
- **The decisions.** Each one names the words it is about, the choice made, the alternatives considered, and the reason, in plain language. It also has a category, such as word sense, grammar, allusion, culture or text variant, so you can see at a glance what kind of question it answers.
- **A status**, which says whether anyone has reviewed the sentence yet. Today every sentence is an AI-assisted draft.

## A record, step by step

Here is the record for John 1:5, one short sentence.

The Greek, word by word, runs "and the light in the darkness shines, and the darkness it not overcame". The gloss keeps that order. It shows that John puts "in the darkness" before the verb, and that the second clause ends on its verb.

Then come the three levels. Literal reads "And the light shines in the darkness, and the darkness did not overcome it." Balanced reads:

> {{OWB:JHN.1.5.s1:B}}

and Readable says the darkness "has never put it out".

Then the decisions. The record has three.

- **The present tense.** John has told the story so far in the past tense. Here he switches to the present: the light *shines*. The record says every level keeps the switch, because the light is still shining.
- **What the darkness did.** The verb, {{LEMMA:JHN.1.5:13}}, can mean to seize or overpower, or to grasp with the mind. The choice is "overcome"; the alternative is "understand, grasp". The reason is that John uses the same verb in 12:35 of darkness overtaking someone. The decision is marked *uncertain*, because John may mean both, and it has a footnote that gives the other reading.
- **"Has not" rather than "did not".** This one is about English only. The Greek tense looks back on a whole history of opposition, and the English perfect, "has not overcome", says that the result still holds. Readable's "put it out" keeps the picture of a light that darkness cannot quench.

A reader who only wanted the verse has it, and need never open the panel. A reader who wondered why it differs from the King James Version's "comprehended it not" has the answer, and the evidence for it, in three short paragraphs.

## Two kinds of decision

The John 1:5 record shows the two layers every decision belongs to.

**Meaning decisions** say what the original means. They are made once and shared by every language and every level. In John 1:1, for example, the record decides that {{GREEK:JHN.1.1:14-17}} means "the Word was God", and explains why "a god" and "divine" were rejected. That decision holds whether you read in English or Spanish, Literal or Readable.

**Rendering decisions** say how one language puts that meaning into words. The Spanish record for John 1:1 explains why it says *el Verbo* rather than *la Palabra*; the English Readable record explains why it adds "already there". These are choices about wording, and they belong to one language only.

Keeping the layers apart matters. It means a new language never has to decide again what the Greek means. It starts from the shared meaning and makes only its own wording choices, so every translation says the same thing. The software enforces the line: a meaning decision may not name a target language or use a wording category, and a record that breaks the rule is rejected.

## Marked as uncertain

Some decisions are close calls. Where the evidence is evenly balanced, the record says so and marks the decision *uncertain*, and the reader shows a label. The article [Grace upon grace](/articles/grace-upon-grace/) looks at one.

An uncertain label tells you what a translation committee usually knows and seldom says: the other reading has a real case. Philippians 4:13 is a good example. Balanced reads:

> {{OWB:PHP.4.13.s1:B}}

where many Bibles say "all things". The record explains that "all things" in this verse are the conditions Paul has just listed, plenty and hunger, and that the verse is often heard as a promise of success in any task. It also marks its own wording uncertain and asks reviewers whether Balanced should keep the wider "all things" and leave the context to the note. That is a question we have not settled, and the record says so.

## What you can do with a record

On the site, the record is more than a page of notes.

- **Tap a word** for its dictionary form and grammar, and see the other verses translated so far that use it.
- **Switch levels** to see the same sentence three ways, or open all three side by side in the panel.
- **Mark the uncertain places**, so that every close call in a chapter is highlighted in the text.
- **Browse a chapter's notes by topic**, to see its text variants, or its notes on culture, together.
- **Read in parallel** with another language, to see how Spanish or French handled the same meaning.

All of it is also open data. Every record is a plain file in the project's public repository, and anyone may copy, check or build on it.

## Questions a skeptic might ask

**Is this a translation or a commentary?** A translation. The decisions explain the wording; they do not preach or apply it. A rule of the project is that a decision cites only what it can stand behind: other passages, facts about the text and its manuscripts, and well-established history.

**Who decides?** For now, an AI drafts each record within strict rules, and software checks those rules. Named human reviewers who read the original languages will approve, change or reject each sentence, and their names will be recorded with it. Until then, every record says it is a draft. See [AI-assisted translation and human review](/articles/ai-assisted-translation-and-human-review/).

**What if a decision is wrong?** Then it can be shown to be wrong, which is the point of writing it down. The reason is right there to argue with. If you think a decision is mistaken, say so on [GitHub](https://github.com/jdegreef/open-word-bible), and say why.
