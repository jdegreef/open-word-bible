# Text variants: when a note becomes a footnote

Every place where the manuscripts, the scribes' reading tradition or the
ancient translations read differently gets a `text_variant` meaning decision:
the reading followed (`choice`), the others (`alternatives`) and the evidence
(`reason`). That record is always there for anyone who opens the reasoning
panel. The `footnote` flag decides whether the reader also sees it under the
text. This page says when.

## Footnote

1. **A verse, a passage or an ending is added or left out.** Mark 16:9-20,
   John 7:53-8:11, the verses the SBLGNT leaves out (Matthew 17:21), Hebrew
   verses the Greek translation lacks (the first note of such a section, as
   Jeremiah 39:4; later verses point back to it).
2. **A well-known English Bible follows the other reading.** A reader who
   has the King James Version or a modern Bible beside ours should find out
   why they differ (1 John 5:7-8, Luke 2:14, Romans 8:1).
3. **The New Testament quotes the other reading** (Genesis 2:24 "the two",
   Isaiah 40:6 "glory").
4. **The reading changes the sense a reader would notice**: who acts
   (Psalm 105:27, Moses and Aaron or God), what is said (Psalm 105:22, "to
   bind" or "to instruct"), a number, a name that matters to the story, a
   different picture (1 Thessalonians 5:4, "like a thief" or "like thieves").
   For the Old Testament this is the usual case when an ancient translation
   (Greek, Syriac, Latin, Aramaic), the Samaritan Pentateuch or a Dead Sea
   scroll reads another word.

## No footnote

5. **Spelling and form**: a name spelled two ways, a written form and the
   form the scribes marked to be read (ketiv and qere) where both mean the
   same, a large or small letter, a scribal mark.
6. **No change of sense**: the reason itself says the meaning is the same,
   or the difference is one a reader of the translation could not see ("in
   these things" or "in this"; "Christ Jesus" or "Jesus Christ"; an "Amen"
   added at the end of a letter, unless rule 2 applies).
7. **A note that only points to another verse's note** ("As in verse 4").

Where a ketiv and qere differ in sense (1 Chronicles 22:7, "his son" or "my
son"), rule 4 wins over rule 5. Where the reason says "no footnote", the
writer has already judged and the flag stays off.

## Wording of the note

The footnote shows the decision's `choice` and `reason`, so write them for a
reader, not a textual critic:

- Start the reason with the other reading and who has it: "The ancient Greek
  and Syriac translations read 'he set', with God as the one acting." Name
  witnesses plainly ("the earliest manuscripts", "the Greek translation", "the
  Great Isaiah Scroll"); sigla and manuscript numbers go after, if at all.
- Say what the difference changes, in one sentence, and which reading the
  translation follows and why (usually: the Hebrew text, or the SBLGNT).
- Meaning decisions state the sense only: no wording for one language, no
  language named. Quote the other reading in plain words, not in Greek or
  Hebrew typed by hand.
- Mark `uncertain` where the choice between readings is close.

## Checking it

`python3 scripts/variants.py` lists every text_variant decision, puts it in
a category from the words of its reason (a heuristic: it reads "the meaning
is the same", "the King James Version", "lack this verse", "the Greek
translation reads" and the like) and names each decision whose flag breaks
this policy; `--list` prints them all, `--fix` sets the flags (never in
books passed to `--skip`). A category the heuristic cannot judge (a New
Testament manuscript difference whose reason does not say what it changes;
a hard text with no other reading) is left to the writer. The site lists
every footnoted variant, book by book, at `/variants/`.
