# Amharic review guide

For native Amharic speakers who review the Open Word Bible in Amharic. It
says what the text is, what to check, how review works on the site and where
to start. The drafting rules themselves are in `docs/amharic-style.md` and the
Amharic terms notes; the founder's Translation Charter is above them all.
The lists this guide points to are generated in
[`docs/review-notes/am-review-priorities.md`](review-notes/am-review-priorities.md).

## አጭር መግለጫ (summary in Amharic)

ይህ መመሪያ የ Open Word Bible የአማርኛ ትርጉምን ለሚገመግሙ አማርኛ ተናጋሪዎች
ነው። መጽሐፍ ቅዱስ በሙሉ ከዕብራይስጥና ከግሪክ ወደ አማርኛ በረቂቅ ተተርጉሟል።
ረቂቁ የተዘጋጀው በሰው ሠራሽ አስተውሎት (AI) እገዛ ነው፤ ስለዚህ እያንዳንዱ
ዓረፍተ ነገር ስሙ የታወቀ ገምጋሚ እስኪያጸድቀው ድረስ ረቂቅ ሆኖ ይቆያል።

- እያንዳንዱ ጥቅስ በሦስት ደረጃ ተተርጉሟል፦ ቃል በቃል (L)፣ ሚዛናዊ (B) እና
  ቀላል (R)።
- የአንባቢ ምርጫዎች ቃላትን እንጂ ትርጉምን አይለውጡም፦ እግዚአብሔር ወይም ያህዌ፣
  ክርስቶስ ወይም መሲሕ፣ ሜትር ወይም ክንድ፣ «ወንድሞችና እኅቶች» ወይም «ወንድሞች»።
- የሚገመገመው፦ ትርጉሙ ከዕብራይስጡና ከግሪኩ ጋር ይስማማል? (ውሳኔዎቹንና
  እንግሊዝኛውን ይመልከቱ)፤ አማርኛው ተፈጥሯዊ ነው? የአነጋገር ሥርዓቱ (አንተ፣
  እርስዎ) ትክክል ነው? ቃላትና ስሞች በመጻሕፍቱ ሁሉ አንድ ዓይነት ናቸው?
- ገምጋሚው በድረ ገጹ አስተዳደር ክፍል (Admin፣ Review፣ Amharic wording)
  እያንዳንዱን ዓረፍተ ነገር ያጸድቃል (Approve)፣ ችግር ካለ ይጠቁማል (Flag)፣
  ወይም አስተያየት ይጽፋል (Comment)።
- የት እንደሚጀመር፦ በመጀመሪያ በብዙ ጥቅሶች ላይ የሚደጋገሙትን ውሳኔዎች (ክፍል 6)፣
  ከዚያ የታወቁትን ምንባቦች፣ ከዚያ ተርጓሚዎቹ ያልተረጋገጡባቸውን ውሳኔዎች።
- ውሳኔዎቹና ማስታወሻዎቹ ለጊዜው በእንግሊዝኛ ናቸው።

(This summary was drafted with AI help too; a reviewer is welcome to correct it.)

## 1. What you are reviewing

- **The whole Bible in Amharic**, 66 books and about 30,600 sentence
  records, translated from the Hebrew and Greek (with the Aramaic of Daniel
  and Ezra), not from English or from an earlier Amharic Bible. The text is
  CC0: anyone may use it freely.
- **One record per source sentence.** Each record in `content/<BOOK>/` holds
  the source words, a literal English gloss, the renderings in each language
  at three levels, and the *decisions* that explain them.
- **Decisions come in two layers.** *Meaning* decisions say what the Hebrew or
  Greek means; they are shared by every language and are written once.
  *Rendering* decisions say how one language words it: the Amharic ones have
  `"language": "am"` and ids `r-am-1`, `r-am-2`, ... Decision text is in
  English, quoting the Amharic words ("\"ደቀ መዛሙርት\" rather than
  \"ተማሪዎች\""). A decision the drafter was unsure of is marked uncertain.
- **Every record is `ai_draft`.** The Amharic was drafted by Claude, an AI,
  and nothing is marked reviewed by an AI. A record moves on only when a named
  person approves it in the site's admin (section 5).
- **Verse numbers** are those of the Hebrew and Greek. In the Old Testament
  they sometimes differ from English Bibles (a psalm's title is verse 1, so
  Psalm 51:1 in English is 51:3 here; Micah 5:2 in English is 5:1 here). The
  priorities list gives the English number in brackets where it differs.

## 2. The three levels

The site calls them **ቃል በቃል** (Literal, L), **ሚዛናዊ** (Balanced, B) and
**ቀላል** (Readable, R). One meaning, three ways of saying it.

| Level | Aim | Check that |
|---|---|---|
| ቃል በቃል (L) | Keeps the source's words, their grammar and its repetitions, as far as Amharic allows. Words Amharic needs but the source lacks are in [square brackets]. | Brackets are only real additions (prefixes, suffixes and object markers are grammar, not additions); it is still Amharic, not a word list. |
| ሚዛናዊ (B) | Careful standard modern written Amharic, the register of a good public reading. Tracks the source closely; no brackets. | It could be read aloud in church; Ge'ez church words appear only where they are the living word (መንግሥተ ሰማያት, ቤተ ክርስቲያን, ሊቀ ካህናት). |
| ቀላል (R) | Plain everyday Amharic for new and young readers: short sentences, common words, idioms explained. | A young reader would understand it; nothing is added beyond what the context implies (the English Readable and its decisions show how far to go). |

Psalm 23:1 as drafted:

- L: የዳዊት መዝሙር። {{divine_name:እግዚአብሔር|ያህዌ}} እረኛዬ [ነው]፤ ምንም አይጎድልብኝም።
- B: የዳዊት መዝሙር። {{divine_name:እግዚአብሔር|ያህዌ}} እረኛዬ ነው፤ ከቶ አልቸገርም።
- R: ዳዊት የዘመረው መዝሙር። {{divine_name:እግዚአብሔር|ያህዌ}} እንደ እረኛ ይንከባከበኛል። የሚያስፈልገኝ ሁሉ አለኝ።

1 Corinthians 13:4, Balanced: «ፍቅር ትዕግሥተኛ ነው፤ ፍቅር ቸር ነው። ፍቅር
አይመቀኝም፤ ራሱን ለማሳየት አይሞክርም፤ በትዕቢት አይነፋም።» Readable: «ፍቅር
ሌሎችን ይታገሣል፤ ደግነትም ያሳያቸዋል። ፍቅር በሌሎች አይቀናም። ጉራ አይነዛም፤
አይኮራምም።»

In the files, a `\v 5 ` marks where a verse starts inside a sentence and a
`\q ` a line break in poetry. They must stay where they are: each verse keeps
its own content after its number, even though Amharic puts the verb last.

## 3. Reader settings

A reader setting lets the reader choose between two wordings of the **same
meaning**. In the text it is a span `{{setting:default|alternative}}`.
Settings never carry a difference of meaning: that is a decision and a
footnote. The Amharic uses four:

| Setting | Amharic span | Count | Check |
|---|---|---:|---|
| `divine_name` | `{{divine_name:እግዚአብሔር\|ያህዌ}}`, with any prefix or suffix inside both options (`{{divine_name:የእግዚአብሔር\|የያህዌ}}`, `{{divine_name:እግዚአብሔርን\|ያህዌን}}`) | about 20,800 | The Old Testament's YHWH, at every level: እግዚአብሔር as Ethiopian Bibles have long given the name, ያህዌ as most scholars think it was said. Is ያህዌ the right spelling? Do both options read with their affixes? *Adonai* is ጌታ; *Elohim* is አምላክ, or እግዚአብሔር where the one God is meant and YHWH is not beside it. |
| `christos` | `{{christos:ክርስቶስ\|መሲሕ}}`, also `{{christos:የክርስቶስ\|የመሲሑ}}`, `{{christos:በክርስቶስ\|በመሲሕ}}` | about 1,650 | The New Testament's *Christos*. Both options must read naturally; the definite መሲሑ where the Greek has the article. |
| `units` | `{{units:2.25 ሜትር ያህል\|አምስት ክንድ}}`, `{{units:115 ግራም ያህል\|አሥር ሰቅል}}`; coins `{{units:የአንድ ቀን ደመወዝ\|አንድ ዲናር}}` | about 1,270 | Metric by default, the original unit as the alternative (the English has US units by default). Literal keeps the original unit. Are the conversions sensible and the unit names (ክንድ, ሰቅል, ኢፍ, ምዕራፍ) the ones readers know? |
| `gender` | `{{gender:ወንድሞችና እኅቶች\|ወንድሞች}}`, `{{gender:ቅድመ አያቶቻችን\|አባቶቻችን}}` | about 780 | Only where Amharic really has two ways of saying the same thing (*adelphoi* meaning believers). Words already inclusive in Amharic (ሰው, ሰዎች, ማንም, ልጆች) take no span, with a decision saying why. |

The Ethiopic script has no capital letters, so the English `deity_pronoun`
setting (he / He) has nothing to change in Amharic and there are no such
spans; the first record of a passage says so once.

## 4. What to check

Read each sentence at all three levels. For each one ask:

1. **Is the meaning right?** Compare it with the English and the literal
   gloss, which show how the sentence was read, and with the meaning
   decisions, which say what it means and which alternatives were weighed.
   The Amharic must say what the meaning decisions say, no more and no less,
   at every level. If you think the *meaning* itself is wrong (the Hebrew or
   Greek has been misread), say so in a flag: that is a change for every
   language, which the scholar reviewers of Hebrew and Greek decide, not a
   change to the Amharic alone.
2. **Is it natural Amharic** for its level? Word order, verb forms, the
   connectives between clauses (ስለዚህ, ነገር ግን, ይልቁንም), and whether a long
   Greek sentence has been split well. Two Amharic sentences for one source
   sentence is fine.
3. **Is the register and address right?** The drafts follow
   `docs/amharic-style.md` section 4:
   - God and Jesus in the narrative take the plain singular (ኢየሱስ መለሰ፤
     እግዚአብሔር አለ), as in the Ethiopian Bible tradition.
   - People speaking to God and to Jesus say አንተ, opponents included.
   - Slaves to their master and subjects to a ruler say እርስዎ (Matthew 18:26;
     1 Kings 1); equals and family say አንተ / አንቺ (Genesis 16:2).
   - Pronouns are እርሱ, እርሷ, እነርሱ, not እሱ, እሷ, እነሱ.
   Check that a scene does not change relationship between verses, and that
   the frank passages (Ezekiel 16 and 23, the Song of Songs, Leviticus 18) are
   close at Literal and sober at Balanced and Readable, and fit to be read
   aloud.
4. **Is it consistent?** Key terms and names keep one form across the books.
   The book-wide choices are in:
   - `docs/amharic-style.md` (the New Testament table in section 6, and the
     conventions settled in Matthew and later in section 7b);
   - `docs/pentateuch-amharic-terms.md` (Genesis to Deuteronomy);
   - `docs/joshua-samuel-amharic-terms.md` (Joshua to 2 Samuel);
   - `docs/kings-chronicles-ezra-amharic-terms.md` (1 Kings to Ezra);
   - `docs/nehemiah-proverbs-amharic-terms.md` (Nehemiah, Esther, Job, Psalms,
     Proverbs);
   - `docs/ecclesiastes-lamentations-amharic-terms.md` (Ecclesiastes to
     Lamentations);
   - `docs/ezekiel-amos-amharic-terms.md` (Ezekiel to Amos);
   - `docs/obadiah-malachi-amharic-terms.md` (Obadiah to Malachi).
   A choice you would change everywhere is better raised once against its
   terms note than verse by verse (section 5).
5. **Spelling and punctuation.** The church spelling of names and key terms
   (እግዚአብሔር, ኃጢአት, ዓለም, ሥጋ, ጸጋ, ቅዱስ, ሐዋርያ), one spelling of each word
   through a book, ። ፣ ፤ ፦, guillemets « » with “ ” inside, no old word
   divider ፡, no Ge'ez numerals.
6. **Is it our own wording?** The drafts must not reproduce a copyrighted
   Amharic Bible (the 1954 E.C. / 1962 Bible and its 1980 revision, the New
   Amharic Standard Version, the Amharic Living Bible and others). Short fixed
   phrases may match (ልቅሶና ጥርስ ማፋጨት); a longer run that matches a
   well-known version should be flagged. Section 4 of the priorities list
   collects the places where the drafters mention the older Bibles.

The quotation marks matter for more than looks: the site colours the words of
Jesus by counting each sentence's quotations, so an Amharic level must open
and close the same quotations as the English. If you suggest wording, keep
the same « » structure.

## 5. How to approve or report

Review happens in the site's admin, one sentence at a time. Nothing in this
repository, ticking a box in the priorities list included, changes a record's
status.

1. **Get the role.** Sign in at <https://openwordbible.org> (a password, an
   emailed link, or Google) and ask the founder for the **Language reviewer**
   role for **Amharic**. A super admin grants it in the admin's Team & access
   page. The role opens the admin's **Review** page and the progress pages.
2. **Open the queue.** Admin → Review → **Amharic wording**. Filter by book
   and by state: *To review*, *Not reviewed*, *Approved*, *Changed since
   approval*, *Flagged*. The queue is in Bible order.
3. **Read the sentence.** The page shows the source words (hover for lemma,
   gloss and grammar), the literal gloss, the Amharic at all three levels, the
   meaning decisions and the Amharic decisions. For the English beside it use
   the link to the verse inspector, or the reader's Study view on the site.
4. **Act on it**, with a note where useful:
   - **Approve the Amharic wording**: the three levels and the Amharic
     decisions are right as they stand. The approval records your name and a
     digest of exactly what you approved; if the sentence is changed later,
     it returns to the queue as *changed since approval*.
   - **Flag a problem**: a note is required. Say which level(s), what is
     wrong, and the wording you propose, in Amharic (in English too, if you
     can, for the editors). For a meaning problem say "meaning", and why.
   - **Comment**: a note for the next reviewer or the editors, without
     approving or flagging.
5. **What happens next.** Editors see open flags in the admin's Reviewer
   flags page. A change of wording is made in `content/` (often through a fix
   request from the verse inspector, which a Claude session turns into a pull
   request that a person merges). When the changed sentence is deployed it
   comes back to your queue, and the flag stays open until the Amharic layer
   is approved again.
6. **Book-wide choices.** If a choice should change everywhere (a key term, a
   name's spelling, a form of address), flag the first verse where it occurs,
   say "throughout" and name the terms note that sets it (section 4). The
   editors change the note and revise every passage drafted under it, rather
   than you flagging each verse.

Approving the Amharic wording does not by itself make a sentence "reviewed":
a scholar reviewer must also approve its meaning (Hebrew for the Old
Testament, Greek for the New). Approving the meaning moves a sentence from
`ai_draft` to `meaning_reviewed`; wording approvals are kept per language.

Readers without a reviewer role can still send a suggestion on any verse from
the reader; editors answer it in the reader inbox.

## 6. Where to start

The order below spends review time where one decision changes the most text,
then where readers will look first, then where the drafters were least sure.

1. **Book-wide choices** (a few hours; settle before reading passages). Agree,
   or give the wording you want, in a flag or comment on the verse named, or
   to the founder directly:
   - the level names ቃል በቃል, ሚዛናዊ, ቀላል;
   - the divine name `{{divine_name:እግዚአብሔር|ያህዌ}}` and the spelling ያህዌ;
     እግዚአብሔር against አምላክ for *Elohim* (Genesis 1:1; Exodus 3:14–15);
   - `{{christos:ክርስቶስ|መሲሕ}}` (Matthew 1:1; John 1:41);
   - the forms of address of section 4 above (Matthew 8; Matthew 18:26;
     Genesis 16:2);
   - እርሱ / እሱ, -ኩ / -ሁ in the first person past, ቆ against ቈ, ውኃ;
   - ደቀ መዛሙርት at every level, ጸሐፍት (L) against የሕግ መምህራን (B, R),
     ሐይቅ for the Sea of Galilee at B and R, በዓለ ሃምሳ for Pentecost,
     ክፍሎች for the members of the body, ጽኑ ፍቅር for *ḥesed*;
   - metric units by default; wages for coins; ሠላሳ የብር ሳንቲም so that ብር
     does not read as the birr;
   - Ethiopian clock time at B and R (ከቀኑ ስድስት ሰዓት);
   - the names lists in each terms note.
2. **The best-known passages**: section 2 of the priorities list, rows 1–32
   (Genesis 1–3, Exodus 20, Psalms 23 and 51, Isaiah 53, Matthew 5–7, John 1
   and 3, Romans 3–8, 1 Corinthians 13 and others). These are read most, and
   memory of the 1962 Bible pulls hardest here: check that the wording is
   right and that it is our own.
3. **The passages the drafting found hardest**: rows 33–43 (Ezekiel 16 and 23
   and the Song of Songs for register; Daniel 9:24–27; Hosea 6:6; Amos 9:7;
   Micah 1:10–15 and 5:1; Habakkuk 2:4; Zechariah 9:9; Malachi 3:1).
4. **The uncertain decisions**: section 1, 392 in all, grouped by book, each
   with a question. The largest groups are 2 Chronicles, Psalms, Ezekiel,
   Isaiah, 1 Chronicles and Exodus.
5. **New name forms**: section 3. Names the drafters coined because no earlier
   book had them, mostly in Chronicles, Nehemiah, Isaiah, Jeremiah and
   Romans 16; and names they meant in the traditional form but were unsure of.
6. **Closeness to older Amharic Bibles**: section 4, where the drafters
   mention the 1962 Bible or familiar wording. Compare each with that Bible.
7. **Then book by book**, in the admin's queue. Matthew was drafted first and
   set the New Testament conventions, so it is a good first book; Genesis
   does the same for the Old Testament.

## 7. The files

- `docs/amharic-style.md`: how the Amharic is drafted.
- `docs/*-amharic-terms.md`: the book-wide choices, book by book.
- `docs/review-notes/am-review-priorities.md`: the generated lists this guide
  refers to. Regenerate it after review work with
  `python3 scripts/review_priorities.py am --write`; decisions that are no
  longer uncertain drop out.
- `content/<BOOK>/*.json`: the records themselves. Reviewers do not need to
  edit them: the admin is the review tool.
