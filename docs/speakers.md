# Speakers: who is talking (proposal and pilot)

Much of the Bible is speech, and in some books the reader cannot easily tell
who is speaking: Job is a debate of five voices and God's; in the prophets
the prophet's voice, God's and the people's turn into one another without a
word of introduction. The red letters (`data/words_of_jesus/`) already mark
one speaker in the Gospels. This proposes the general layer, and pilots it in
Job and Jeremiah.

## What is marked

`data/speakers/<BOOK>.json`, one file per book, like the headings:

    {"description": "...", "status": "ai_draft",
     "speakers": {"eliphaz": {"en": "Eliphaz", "es": "Elifaz", ...}, ...},
     "records": {"JOB.4.1.s1": "narrator", "JOB.4.2.s1": "eliphaz", ...}}

- Every record of the book names one voice: the one that holds most of the
  sentence. A heading-like line that introduces a speech ("Then Eliphaz the
  Temanite answered:") is the narrator's; the speech after it is Eliphaz's.
- A sentence that reports an exchange of two voices ("The LORD said to the
  Accuser, '...' The Accuser answered, '...'", Job 1:7) is the narrator's.
- Speaker ids are stable words (`narrator`, `god`, `job`, `eliphaz`,
  `jeremiah`, `people`, `other`), and each has a name in every language,
  spelled as that language's renderings spell it (Ayubu, Gióp, 욥, Jó).
- Who speaks is a fact about the original, the same in every language and at
  every level, so it is marked once, as the words of Jesus are. Where it is
  disputed (does Jeremiah 4:19-21 speak as the prophet or as God?) the
  meaning decision belongs in the record, as for any other question of
  meaning, and the speaker file follows it.
- It is an editorial aid, not translation: no reader settings, AI draft until
  a named reviewer approves it, and `owb/speakers.py` checks that every
  record has a listed speaker and every speaker a name in every language.

## What the reader shows

Where the voice changes, the chapter starts a new paragraph and sets a small
label above it with the speaker's name in the page's language
(`speakers.labels`, `.speaker-label` in `web/style.css`). The labels are
editorial aids like the section headings, so the headings control hides
both. A screen reader hears "Speaker: Eliphaz".

## The pilot

- **Job** (`data/speakers/JOB.json`, 1,070 records): the speeches by the
  book's own headings (3:1-2, 4:1, 6:1 ... 42:1), with Elihu from 32:6, God
  from 38:2 and 40:7, and Job's two replies (40:4-5, 42:2-6); the prose
  frame (1-2, 42:7-17) read sentence by sentence. This is reliable: the book
  says who speaks.
- **Jeremiah** (`data/speakers/JER.json`, 1,364 records): drafted from the
  English Balanced rendering's quotation marks and speech formulas ("declares
  the LORD", God's own "my" and "me" as `deity_pronoun` spans, "The word of
  the LORD came to me:" handing the next sentence to God, "I said" to
  Jeremiah), following an open quotation from one sentence into the next, and
  carrying an oracle's voice on where nothing changes it. It is a first draft
  for review: the prophet's laments inside oracles (4:19-21, 8:18-9:1), the
  people's words quoted without marks and the narrative chapters' reported
  speech (26, 36-44) need a reader's judgment sentence by sentence.

## Next steps (not built)

- Finer than a sentence: a list of quotation numbers per voice, as the words
  of Jesus have (`[0, 2]`), where two voices share a sentence.
- Other books where the voice is hard to follow: Song of Songs (the woman,
  the man, the friends), Ecclesiastes (the narrator and Qohelet), Isaiah
  40-55 (the servant), Lamentations, Malachi's dialogues, Revelation.
- A reader setting to colour each voice, not only label it, and a search
  filter ("everything Elihu says").
- The words of Jesus as one speaker of this layer in the Gospels, so both
  share one file format.
