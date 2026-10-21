---
title: "AI-assisted translation and human review: how a sentence becomes \"reviewed\""
summary: Everything on this site today is translated with AI assistance. Here is how a sentence is drafted, what its record holds, what AI drafting cannot do, and how a sentence moves to reviewed.
date: 2026-10-10
order: 10
section: method
---
Open Word Bible is translated with the help of AI. We say so plainly, because a project that promises to show its work cannot be vague about who did the work. This article explains how a sentence is drafted, what you can see of it, where AI drafting falls short, and what has to happen before any sentence is called reviewed.

## How a sentence is drafted

Take Philippians 4:6–7, one long Greek sentence about worry and prayer. It goes through four steps.

**1. The source is loaded, not typed.** A script reads the pinned source data, the SBL Greek New Testament with the MACULA word data for the New Testament and the Westminster Leningrad Codex for the Old. It splits the text where the edition ends a sentence and writes an empty record for each one, with the id of every Greek word and the Greek text itself. No one, human or AI, types the original. See [Why we never type Greek or Hebrew by hand](/articles/never-typed-by-hand/).

**2. The AI writes a draft.** Working from the Greek, the word data and a written style guide, an AI model fills in the record: a literal gloss in Greek word order, the translation at three levels in each language, and the decisions behind them. The style guide sets the rules: which English words are settled key terms, how each level differs, what may go in brackets, which reader settings apply where. For some books there is a separate list of settled terms, so that the same Hebrew word does not come out three different ways across sixty-six chapters of Isaiah.

**3. Software checks the rules.** A validator runs on every record. It rejects any Greek or Hebrew word that is not, letter for letter, a form or dictionary word in the source data. It checks that each key term uses its settled English word at every level, unless a decision explains why not. It checks that every record has all three levels, that a record ends where a sentence ends, and that meaning decisions stay free of wording for any one language. A record that breaks a rule does not go in.

**4. The change is made in public.** Every new passage arrives as a proposed change on GitHub, where the tests and the site build run before it is merged. Its whole history stays there to read.

## What the record holds

Here is the Balanced level of the sentence that came out of those steps:

> {{OWB:PHP.4.6.s1:B}}

The record for it holds the Greek, which begins {{GREEK:PHP.4.6:1-2}}, "nothing be anxious about"; a literal gloss; Literal, Balanced and Readable English; and the same three levels in other languages as they are drafted. It also holds twelve decisions. Seven are meaning decisions, shared by every language. One says that {{LEMMA:PHP.4.6:2}} here means anxious worry, the word Jesus uses in Matthew 6, and not the good concern Paul uses it for in 2:20. Another says the verb for "guard" is what a garrison does, an image the people of Philippi, a Roman colony with retired soldiers among its citizens, would have felt. The other five are rendering decisions for one language each. One English decision, for example, explains why Balanced says the peace will "stand guard over" your hearts: it keeps the soldier's image without the old-fashioned "keep".

Two decisions in this record are marked uncertain. One is about meaning: the peace that "surpasses every understanding" may be peace beyond what the mind can grasp, or peace that achieves more than any human plan could. The record follows the more common reading and gives the other in a footnote. The second is about English. The Readable level says the peace guards you "because you are joined to Christ Jesus", where the Greek says only "in". The rendering decision says plainly that this adds a reason the Greek leaves unstated, and that reviewers should check it:

> {{OWB:PHP.4.6.s1:R}}

That is the pattern everywhere. Across the drafts so far, a sentence carries about four decisions on average, and about one decision in twelve is marked uncertain. The AI is told to mark a close call as uncertain rather than present it as settled, and the reader shows the label.

## What the AI does not do

It does not decide that its own work is correct. **Nothing is marked reviewed by an AI.** Every sentence starts with the status *AI-assisted*, and it stays that way until a named human reviewer approves it. In the project's database, every step in a sentence's review trail belongs to a named person's account; the AI has no way to approve its own drafts.

It also does not use other translations as a basis. English Bibles in the public domain may be consulted to check a draft, never to supply its wording, and the wording of copyrighted translations is never reproduced.

## The limits of AI drafting

A reader is right to ask what an AI gets wrong. We have seen several kinds of mistake, and the process is built around them.

**Familiar wording pulls hard.** An AI model has read many Bibles. Early drafts of Philippians 4:6–8 came out almost word for word like existing translations and had to be rewritten from the Greek. The style guide now tells every draft to start from the Greek and the gloss, compare afterwards, and rewrite any sentence that matches a well-known version for more than a short common phrase.

**Facts can be recalled wrongly.** When a record describes manuscript evidence, a Hebrew scroll's reading or a writer in the early church, it is drawing on what the model learned, not on a library open in front of it. The records are told to say so. Many decisions on textual variants end with a note that a reviewer must check the evidence against the apparatus, the scholarly list of manuscript readings. Some of the Isaiah records go further and mark a reading "from memory; to be checked". See [When the manuscripts disagree](/articles/when-manuscripts-disagree/).

**Fluency is not judgment.** A draft can read smoothly and still be wrong, or right for reasons that are not quite the stated ones. The confident tone of a sentence is no evidence for it.

**Natural wording needs native speakers.** An AI can write grammatical Spanish, French, Swahili, Vietnamese or Korean. Whether a sentence sounds natural to a reader who grew up with the language is another question. The Spanish record for John 1:1, for example, chooses *el Verbo* for "the Word" over *la Palabra* and flags the choice for a native speaker's review.

**Consistency across books is hard.** Thousands of sentences drafted at different times can drift. Key terms checked by software, term lists for long books, and decisions that cite earlier ones all work against it, but some drift will remain for reviewers to find.

## Why use AI at all?

A thoughtful skeptic might say that Scripture is too important to draft by machine. We take the point seriously. Our answer is that the AI does not replace the scholars; it changes what they are asked to do.

Writing out the reasons for every sentence of the Bible, in plain language, with the alternatives considered, is more work than most translation teams have ever had time for. A draft with its reasoning laid out gives a reviewer something definite to check: a stated choice, the options set aside, and a reason that is either sound or not. It also gives every reader the same view the reviewer has. If the reasoning is weak, anyone can see that it is weak.

What AI drafting cannot give is trust. That has to be earned by people who read the original languages and put their names to their work.

## The review steps

A sentence moves through these statuses:

- **AI-assisted.** Written with AI, checked by software, not yet read by a reviewer.
- **Meaning reviewed.** A scholar reviewer who reads the original language, Greek for the New Testament and Hebrew for the Old, has checked the meaning decisions: what the text says.
- **Reviewed.** A language reviewer, a fluent reader of the language the sentence is translated into, has also checked the wording.
- **Revised.** The sentence has been changed after review, with the reason recorded.

Each step is recorded with the reviewer's name, the date and a note, so the history of every sentence can be traced. A reviewer can also flag a problem or leave a comment without approving anything. Importing new drafts never resets a sentence's review status.

## Where things stand today

The review records and reviewer roles are in place in the project's database, but the tools reviewers will use are still being built. Until they are, the files on GitHub are the master copy of the translation, and every sentence keeps its status there in the open data.

Today no sentence on this site has been reviewed. Every one of them, in every language, is an AI-assisted draft.

## How you can check the work

You do not have to wait for reviewers to test what you read.

- **Open the record.** Tap any verse to see its gloss, its three levels and every decision, with the alternatives the record considered.
- **Look at the Greek or Hebrew.** Tap a word in the panel to see its dictionary form, its grammar and a gloss from the source data.
- **Find the close calls.** The reader can mark where the meaning is uncertain, so you can see at a glance which decisions are judgment calls.
- **Compare the levels.** Literal shows the shape of the original; Readable shows where the translation has spelled something out. See [Three levels, one meaning](/articles/three-levels-one-meaning/).
- **Read the history.** Every record and every change to it is on GitHub.

## Help review

If you read Greek or Hebrew, or are a native speaker of Spanish, French, Swahili, Vietnamese or Korean who can judge whether a sentence reads naturally, we would value your help. Everything is open on [GitHub](https://github.com/jdegreef/open-word-bible), including every decision and its reasoning, and the "Report a problem" link at the foot of every page opens an issue there. Disagreeing with a decision, and saying why, is exactly the kind of help the project needs.
