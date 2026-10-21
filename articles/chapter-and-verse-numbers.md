---
title: Chapter and verse numbers
summary: The Bible's authors wrote no chapters and no verses. Here is where the numbers came from, a few places where they cut a sentence or a poem in two, why Hebrew and English Bibles number some verses differently, and how Open Word Bible handles both.
date: 2026-10-17
order: 100
section: translation
---
"John 3:16" is so familiar that it is easy to forget that John never wrote a "3" or a "16". None of the biblical authors divided their books into chapters and verses. The numbers are a reference system, added many centuries later by scholars and printers, and like any reference system they are useful, imperfect and here to stay.

## Where the numbers came from

**Chapters.** Ancient and medieval manuscripts already had ways of marking sections. Hebrew scrolls were divided into paragraphs, and Greek manuscripts of the Gospels had their own numbered sections. But the chapters used today go back to Stephen Langton, a teacher in Paris who later became Archbishop of Canterbury. Early in the thirteenth century he divided the Latin Bible into chapters, and his system spread through the Bibles copied in Paris and from there across Europe. Jewish printers later adopted the same chapters for the Hebrew Bible, so that Jews and Christians could refer to the same places.

**Verses in the Old Testament.** The Hebrew Bible was divided into verses long before it was numbered. The Masoretes, the scribes who guarded the Hebrew text in the early Middle Ages, marked the end of each verse with a sign, and those divisions are older still. See [The Masoretes](/articles/the-masoretes/). Numbering the verses came later, in the age of concordances and printing.

**Verses in the New Testament.** The New Testament's verse numbers come from Robert Estienne, a printer of Paris who later settled in Geneva. He added them to his edition of the Greek New Testament with Latin translations, printed in 1551. His son later told the story that Estienne marked the divisions while travelling, which some have taken to explain a few odd breaks. Whether or not that is so, his numbers were quickly copied.

**English Bibles.** The Geneva New Testament of 1557 was the first English New Testament divided into numbered verses, and the Geneva Bible of 1560 did the same for the whole Bible. Every English Bible since, including the King James Version, has followed. See [From Coverdale to Geneva](/articles/english-bibles-before-1611/).

## Where the numbers cut the sense

Because the numbers were added to the text, they sometimes fall in awkward places. A chapter break is a strong signal to a reader that one thing has ended and another begun, and occasionally it is in the wrong place.

**1 Corinthians 12:31 and 13:1.** Paul's famous chapter on love begins, in most Bibles, with "If I speak in the tongues of men and of angels". But Paul's introduction to it is the last sentence of chapter 12:

> {{OWB:1CO.12.31.s2:B}}

The record for this sentence says plainly that the way is love, which chapter 13 describes.

**Isaiah 52:13 to 53:12.** The song of the servant who suffers and is exalted, one of the best-known passages of the Old Testament, does not begin at chapter 53. The record for Isaiah 52:13 notes that verses 13 to 15 and chapter 53 form one poem. A reader who starts at 53:1 misses its opening, where God himself announces that his servant will be lifted up.

**John 7:53 and 8:1.** "Then each of them went home. But Jesus went to the Mount of Olives." In the Greek these two clauses make one sentence, and Open Word Bible's record for them is one sentence. The chapter break falls in the middle. See [The woman caught in adultery](/articles/the-woman-caught-in-adultery/).

**Acts 21:40 and 22:1.** Paul stands on the steps of the barracks, quiets the crowd and begins to speak. The chapter ends before he says a word:

> {{OWB:ACT.21.40.s1:B}}

The record has a decision on exactly this: the sentence runs on into Paul's speech, which begins at 22:1, so it ends with the speech still to come.

**Ephesians 5:21 and 5:22.** Here the problem is not the numbers but the headings many Bibles put between them. In the SBL Greek text, verse 22, "Wives, to your own husbands", has no verb of its own. It borrows "submitting" from verse 21, "submitting to one another in the fear of Christ". The record for 5:22 says that what verse 21 asks of everyone, verse 22 applies to wives toward their own husbands. A heading that begins a new section at 5:22 hides that link. Open Word Bible's sentences follow the Greek punctuation, so 5:22 does begin a new sentence, but the meaning decisions on both records say that the two verses belong together.

Open Word Bible is built in a way that makes these breaks harder to miss. Its basic unit is not the verse but the sentence. As the project's data model puts it, a record is one sentence of the source, not one verse: a verse may hold two sentences, and a sentence may run across several verses. The verse numbers are carried inside the sentence where they fall. See [Punctuation the apostles never wrote](/articles/punctuation-the-apostles-never-wrote/) for why even the sentence breaks are decisions.

## When Hebrew and English Bibles disagree

A second surprise for readers is that the same verse can have a different number in a Hebrew Bible and an English one. Most of the differences come from three causes.

**Malachi has three chapters in Hebrew.** English Bibles, following the Greek and Latin, make the last six verses of Malachi into a chapter 4. In the Hebrew text they are Malachi 3:19–24.

**Joel has four chapters in Hebrew.** The Hebrew begins a new chapter with the promise "I will pour out my Spirit on all people". English Bibles continue chapter 2, so their Joel 2:28–32 is Hebrew 3:1–5, and their chapter 3 is Hebrew chapter 4.

**Psalm titles are verses in Hebrew.** In the Hebrew text, a psalm's title ("A psalm of David, when he fled from his son Absalom") is part of the psalm and counted as verse 1. English Bibles print the title above the psalm without a number. So in many psalms the Hebrew verse numbers are one higher than the English, and where the title is long, two higher: Psalm 51's title takes two verses in Hebrew, so the English 51:1 is Hebrew 51:3.

There are smaller differences elsewhere, as at the end of Genesis 31, where the Hebrew begins chapter 32 one verse earlier. The New Testament has none of these, because all its verse numbers go back to Estienne.

## How Open Word Bible handles the numbers

Open Word Bible numbers every verse as its source text does. For the Old Testament that is the Westminster Leningrad Codex, so Malachi has three chapters, Joel four, and a psalm's title is its first verse. Where this matters, the first verse affected carries a footnote. The one at Malachi 3:19 explains that its six verses are numbered 4:1–6 in many other Bibles, and that Open Word Bible follows the numbering of the Hebrew text it translates. Joel 3:1 has the same kind of note, and so does the title of Psalm 3:

> {{OWB:PSA.3.1.s1:B}}

Its record says that from Psalm 3 on the verse numbers here are one higher than in Bibles that print the title without a number.

Behind the scenes, a table in the project's data, `data/versification.json`, maps the two systems verse by verse. It is built from the verse map of the Open Scriptures Hebrew Bible, and it lists every Hebrew verse whose English number is different: a little over two thousand of them, about half in the Psalms. The site uses it wherever our numbering meets someone else's. When the reader shows another Bible for comparison, such as the World English Bible, its verses are moved into our numbering, so that the English Psalm 3:1 sits beside our Psalm 3:2. Cross-references from other sources are converted the same way. And the project's text service can give a comparison Bible either in our numbering or in the edition's own.

In the New Testament, Open Word Bible keeps Estienne's numbers even where the SBL Greek text has no verse to put under them. Matthew 17 goes from verse 20 to verse 22, with a footnote explaining why. See [Verses missing from modern Bibles](/articles/verses-missing-from-modern-bibles/).

## Useful, not inspired

None of this is a reason to distrust chapters and verses. They let millions of people find the same sentence in different languages and editions, and they make cross-references and concordances possible. But they are a map laid over the text, not part of it. Reading across a chapter break, or ignoring a verse number in the middle of a sentence, is often the best way to hear what an author actually wrote.

[Open 1 Corinthians 13](/1co/13/), [Isaiah 52](/isa/52/) or [Malachi 3](/mal/3/) to see the numbers at work.

## Sources

- Bruce M. Metzger and Bart D. Ehrman, *The Text of the New Testament: Its Transmission, Corruption, and Restoration*, 4th ed. (Oxford University Press, 2005).
- Emanuel Tov, *Textual Criticism of the Hebrew Bible*, 3rd ed. (Fortress, 2012).
