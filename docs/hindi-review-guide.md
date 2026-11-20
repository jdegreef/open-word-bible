# Hindi review guide

For native Hindi speakers who review the Open Word Bible in Hindi. It says
how review works on the site, which choices to settle first because they
change wording across the whole Bible, where the drafters were unsure, and
which passages to read first. The drafting rules themselves are in
`docs/hindi-style.md` (the New Testament and the levels) and
`docs/hindi-terms.md` (the Old Testament's words, formulas and names); the
founder's Translation Charter is above them both.

## सारांश (summary in Hindi)

- पूरी बाइबल (30,637 वाक्य) इब्रानी और यूनानी से हिन्दी में अनुवाद की गई है।
  यह अनुवाद AI की सहायता से बना प्रारूप है: हर वाक्य तब तक प्रारूप
  (`ai_draft`) रहता है जब तक कोई नामित समीक्षक उसे स्वीकृत न करे।
- हर वाक्य तीन स्तरों पर है: शाब्दिक (L), संतुलित (B) और सरल (R)।
- पाठक की सेटिंग केवल शब्द बदलती है, अर्थ नहीं: प्रभु या याहवे, मीटर या हाथ,
  "भाइयो और बहनो" या "भाइयो"।
- समीक्षा साइट के Admin में होती है: Review → Hindi wording। हर वाक्य को
  स्वीकृत करें (Approve), समस्या हो तो चिह्नित करें (Flag), या टिप्पणी लिखें
  (Comment)।
- कहाँ से शुरू करें: पहले वे निर्णय जो पूरी बाइबल में दोहराए जाते हैं (भाग 3),
  फिर सबसे अधिक पढ़े जानेवाले अंश (भाग 5), फिर अनिश्चित निर्णय (भाग 4)।
- निर्णय और टिप्पणियाँ अभी अंग्रेज़ी में हैं।

(This summary was drafted with AI help too; a reviewer is welcome to correct
it.)

Counts in this guide were made from `content/` on 18 November 2026 with the
scripts named in section 6; they will drift as the text is revised. Verse
numbers are those of the Hebrew and Greek: in the Old Testament a psalm's
title is verse 1 (Psalm 51:1 in English is 51:3 here) and Micah 5:2 in
English is 5:1 here. `data/versification.json` maps one to the other.

## 1. How to review

### What you are reviewing

- **One record per source sentence.** Each record in `content/<BOOK>/` holds
  the source words, a literal English gloss, the renderings in every language
  at three levels, and the *decisions* that explain them. Every one of the
  30,637 records has a Hindi rendering, and every record is `ai_draft`: the
  Hindi was drafted by Claude, an AI, and nothing is marked reviewed by an AI.
- **The three levels.** The site calls them **शाब्दिक** (Literal, L),
  **संतुलित** (Balanced, B) and **सरल** (Readable, R). Literal keeps the
  source's words and grammar, with words Hindi needs in [square brackets]
  (postpositions and verb endings are grammar, not additions). Balanced is
  careful standard written Hindi for public reading. Readable is plain
  everyday Hindi for new and young readers. Psalm 23:1 as drafted:
  - L: दाऊद का भजन। `{{divine_name:प्रभु|याहवे}}` मेरे चरवाहे [हैं]; मुझे [किसी चीज़ की] कमी न होगी।
  - B: दाऊद का भजन। `{{divine_name:प्रभु|याहवे}}` मेरे चरवाहे हैं; मुझे कभी किसी चीज़ की कमी नहीं होगी।
  - R: दाऊद का गीत। `{{divine_name:प्रभु|याहवे}}` चरवाहे की तरह मेरी देखभाल करते हैं। जो कुछ मुझे चाहिए, वह सब मेरे पास है।
- **Two layers of decisions.** *Meaning* decisions (ids `m1`, `m2`, ...) say
  what the Hebrew or Greek means. They are shared by every language and are
  reviewed by scholar reviewers of Hebrew and Greek. *Rendering* decisions
  (ids `r-hi-1`, `r-hi-2`, ..., `"language": "hi"`) say how Hindi words that
  meaning; there are 16,375 of them. Decision text is in English and quotes
  the Hindi. A Hindi rendering may not narrow or widen what the meaning
  decisions say: if you think the meaning itself is wrong, that is a flag on
  the meaning, for every language, not a change to the Hindi alone.
- **Your approval is of the Hindi wording**: the three Hindi levels and the
  Hindi rendering decisions of one sentence. Approving the meaning (by a
  scholar reviewer) is what moves a sentence from `ai_draft` to
  `meaning_reviewed`; wording approvals are kept per language.

### Reader settings

A reader setting lets the reader choose between two wordings of the **same
meaning**: in the text it is a span `{{setting:default|alternative}}`.
Settings change wording, never meaning; a difference of meaning is a decision
and a footnote, never a setting. Hindi uses three:

| Setting | Example | Records | Check |
|---|---|---:|---|
| `divine_name` | `{{divine_name:प्रभु\|याहवे}}`, postpositions outside the span; प्रभु `{{divine_name:परमेश्वर\|याहवे}}` for *Adonai* YHWH | 5,933 | Is याहवे the spelling you want? Is प्रभु right as the default, given that प्रभु is also *Adonai*? |
| `gender` | `{{gender:भाइयो और बहनो\|भाइयो}}`, `{{gender:इस्राएल की सन्तान\|इस्राएल के पुत्र}}` | 1,232 | Only where Hindi really has two wordings; words already inclusive (लोग, मनुष्य, कोई) take none. |
| `units` | `{{units:135 मीटर\|300 हाथ}}`; coins as wages | 399 | Metric by default, the original unit as the alternative; Literal keeps the original unit. |

Hindi has no `deity_pronoun` spans (Devanagari has no capitals; respect comes
from honorific agreement) and no `christos` spans (मसीह is both the name and
the word Messiah). The first record of a passage file says so in a decision.

### What to check in each sentence

1. **Meaning**: compare with the literal gloss, the English and the meaning
   decisions. The Hindi says what they say, no more and no less, at every
   level.
2. **Natural Hindi for the level**: word order, verb forms, connectives;
   Balanced should not sound Sanskritised, Readable should sound like speech.
3. **Address and honorifics** (`docs/hindi-style.md` section 4,
   `docs/hindi-terms.md` "Address and pronouns"): God and Jesus take honorific
   plural agreement in narrative; people say तू to God and आप to Jesus; God
   says तुम to people; आप to rulers. A scene should not change relationship
   between verses.
4. **Consistency**: key terms and names keep one form across books (the terms
   file). A choice you would change everywhere is raised once (below), not
   verse by verse.
5. **Spelling and punctuation**: standard modern spelling, nukta where Hindi
   writes it, danda ।, straight quotation marks `"` and `'` in the records.
   Each level must open and close the same quotations as the English: the
   site colours the words of Jesus by counting them.
6. **Our own wording**: the drafts must not reproduce a copyrighted Hindi
   Bible (the Hindi Old Version and its revisions, the Hindi Common Language
   Bible, ERV-HI, the Pavitra Bible and others; `docs/hindi-style.md`
   section 1). Flag any run longer than a short common phrase that matches a
   well-known version; the familiar passages of section 5 pull hardest.

### Where and how: the admin

Nothing in this repository, ticking a box in these lists included, changes a
record's status. Review happens in the site's admin, one sentence at a time.

1. **Get the role.** Sign in at <https://openwordbible.org> and ask the
   founder for the **Language reviewer** role for **Hindi** (a super admin
   grants it in the admin's **Team & access** page). It opens **Review** and
   the progress pages.
2. **Open the queue.** Admin → **Review** → **Hindi wording**. Filter by book
   and by state (*To review*, *Not reviewed*, *Changed since approval*,
   *Flagged*, *Approved*); the queue is in Bible order.
3. **Read the sentence.** The page shows the source words (hover for lemma,
   gloss and grammar), the literal gloss, the Hindi at all three levels, the
   meaning decisions and the Hindi decisions. The **Verse inspector** link
   shows the whole verse in every language, the English included, with every
   decision and the file it lives in.
4. **Act** (keys: `a` approve, `f` flag):
   - **Approve the Hindi wording** when the three levels and the Hindi
     decisions are right. The approval records your name and a digest of what
     you approved; if the sentence changes later it returns to your queue as
     *changed since approval*.
   - **Flag** a problem, with a note: which level, what is wrong, and the
     Hindi you propose. Say "meaning" if the problem is the meaning.
   - **Comment** to leave a note without approving or flagging.
5. **Changes are made through fix requests.** Editors see open flags in
   **Reviewer flags** and, from the **Verse inspector**, file a **fix
   request**: a GitHub issue labelled `fix-request` that a Claude session
   works into a pull request, which a person merges. Once deployed, the
   changed sentence comes back to your queue; the flag stays open until the
   Hindi layer is approved again. (If you hold the editor role you can file
   the fix request yourself, from the verse inspector's "File a fix request".)
6. **Book-wide choices.** For a choice that should change everywhere (a term,
   a name's spelling, a form of address), flag the first verse where it
   occurs, write "throughout", and name the item in section 3 below. The
   editors change `docs/hindi-terms.md` or `docs/hindi-style.md` and revise
   every passage drafted under it. The admin's **Consistency**, **Key terms**
   and **Uncertain decisions** pages (filter by layer "Hindi") help find all
   the places.

## 2. Book-wide defaults to confirm

These are settled in the briefs and applied everywhere; agree or say what you
want instead before reading passages:

- the level names शाब्दिक, संतुलित, सरल;
- `{{divine_name:प्रभु|याहवे}}` (and *यहोवा* not used), परमेश्वर for *Elohim*,
  परमप्रधान for *ʿElyon*, सेनाओं के प्रभु for "the LORD of hosts";
- honorific agreement for God (प्रभु ने कहा, वे, उन्होंने) and तू in prayer;
- no `christos` spans; मसीह throughout;
- the key terms of `docs/hindi-style.md` section 6 and the tables of
  `docs/hindi-terms.md` (वाचा, अटल प्रेम for *ḥesed*, व्यवस्था / शिक्षा for
  *torah*, शिओल / अधोलोक / मृत्यु का लोक for Sheol, दास for *ʿeved*, ...).

The terms file's one remaining clean-up note (Sheol at Readable in Genesis,
Numbers, Deuteronomy and 1 Samuel to be brought into line with मृत्यु का लोक)
is done: no Sheol record has अधोलोक at Readable any more (54 have
मृत्यु का लोक).

## 3. Decisions that affect the whole Bible: settle these first

Each item below is open: the drafts made one choice, the data shows it
applied unevenly or the drafters asked for a ruling. One ruling changes many
records, so settle these before reading passages. Counts are records (one
record is one sentence, at all three levels).

### 3.1 Zechariah: जकर्याह, ज़कर्याह or जकरयाह

- **Question.** Several people are called Zechariah. Should they share one
  spelling, and with or without the nukta?
- **Now.** Three spellings, by book group: जकर्याह in **29** records (2 Kings
  14-18, 1 Chronicles, 2 Chronicles, Isaiah 8:2); ज़कर्याह in **18** (Ezra,
  Nehemiah, the prophet in Zechariah 1:1-7, and Matthew 23:35); जकरयाह in
  **17** (Luke 1, the father of John the Baptist).
- **Alternatives.** (a) One Old Testament form for every Zechariah, either
  जकर्याह or ज़कर्याह, with Luke keeping its New Testament form; (b) the
  nukta form for the prophet only (as Ezra and Matthew 23:35 have it) and
  जकर्याह for the others; (c) one form for the whole Bible, Luke included.
- **Examples.** 2 Kings 15:8; 1 Chronicles 15:20; Ezra 5:1; Zechariah 1:1;
  Matthew 23:35; Luke 1:5.
- **If changed.** Up to 64 records, a mechanical change; the policy for
  Hebrew *z* names (3.2) decides which way.
  `docs/review-notes/name-spellings.md` already lists this pair as "left for a
  reviewer".

### 3.2 The nukta in Hebrew *z* names

- **Question.** Hebrew *zayin* is written ज in the established Hindi Bible
  names (जबूलून, हिजकिय्याह) and ज़ in others. Should names transcribed from
  the Hebrew take the nukta?
- **Now.** Mixed. Counting the names that occur in three or more records and
  whose Hebrew has *z*: **16 names in 242 records** take ज़ (एलीआज़ार
  Eleazar 70, आहाज़ Ahaz 39, ज़कर्याह 25, गाज़ा Gaza 19, उज़्ज़ीएल Uzziel 16,
  एलीपज़ Eliphaz, एलीएज़ेर Eliezer, कनज़ Kenaz, बर्ज़िल्लै Barzillai, ...); **36
  names in 456 records** take plain ज (हिजकिय्याह Hezekiah, जबूलून Zebulun 43,
  अजर्याह Azariah 31, एज्रा Ezra 22, जेरह Zerah 21, जरुब्बाबेल Zerubbabel 20,
  उज्जियाह Uzziah 18, जकर्याह, जिक्री Zichri, उज्जा Uzzah, ...). So उज़्ज़ीएल
  has the nukta while उज्जियाह and उज्जा do not.
- **Alternatives.** (a) The established Hindi Bible form wherever there is
  one, plain ज otherwise (no nukta in names); (b) ज़ for every Hebrew *z*;
  (c) the present mixture, recorded name by name.
- **Examples.** Exodus 6:18-22 (Uzziel); 2 Samuel 6:6 (Uzzah); Numbers 3:2
  (Eleazar); 2 Kings 18:1 (Hezekiah).
- **If changed.** (a) changes about 240 records, (b) about 450; each is
  mechanical but touches every book from Genesis to Nehemiah. Settle 3.1 with
  it.

### 3.3 The Asherah pole: अशेरा-स्तंभ or अशेरा के खंभे

- **Question.** One term for the Asherim, the wooden poles set up for the
  goddess Asherah?
- **Now.** अशेरा-स्तंभ in **7** records (Exodus 34:13, Deuteronomy 12:3 and
  16:21, Judges 6:25-28), अशेरा के खंभे in **21** (1-2 Kings, 2 Chronicles,
  Isaiah, Jeremiah, Micah), which `docs/hindi-terms.md` sets. The decision at
  1 Kings 14:15 says it "replaces the अशेरा-स्तंभ of Exodus and Deuteronomy
  for Kings, so a reviewer may want the two harmonised". Readable explains
  (अशेरा देवी की पूजा के लिए ... खंभे). 40 records name Asherah in all.
- **Alternative.** अशेरा-स्तंभ everywhere.
- **If changed.** 7 records (to the terms file's form) or 21 (to the other).

### 3.4 Hyphens in compound place names: बेत-शेमेश or बेतशेमेश

- **Question.** Are compound names such as Beth-shemesh written with a hyphen?
- **Now.** Most are hyphenated: 93 records have a बेत- name with a hyphen.
  But Beth-shemesh is बेत-शेमेश in **12** records (Joshua, Judges 1:33,
  2 Kings 14, 1 Chronicles 6:44, 2 Chronicles, Jeremiah 43:13) and बेतशेमेश in
  **9** (1 Samuel 6, 1 Kings 4:9); Beth-shan is बेत-शान in 3 and बेतशान in 5;
  Endor is एनदोर in 2 and एन-दोर in 1 (Joshua 17:11).
- **Alternatives.** (a) A hyphen in every compound place name (as most are
  now); (b) none, one word; (c) the Hindi Bible's established form name by
  name.
- **If changed.** Under (a), about 15 records; under (b), about 100.
- **Related.** About 40 common compounds are also written both ways
  (आसपास 151 / आस-पास 60, चालचलन 64 / चाल-चलन 14, देखरेख 54 / देख-रेख 9,
  निवास-स्थान 27 / निवासस्थान 8, ...). A word on the house style for these
  would let the editors make them one.

### 3.5 जाति for "the nations" at Balanced and Readable

- **Question.** May Balanced and Readable say जाति / जातियाँ for the nations
  (*goyim*), or only देश / राष्ट्र?
- **Now.** `docs/hindi-terms.md` sets जातियाँ at Literal and देश / राष्ट्र at
  Balanced and Readable, "never caste-sounding at B and R" (the style guide's
  reason: जाति also means caste; the New Testament settled देश in Matthew). Of
  the **508** records with *goyim*, Literal has जाति in 505, as set; but
  Balanced still has it in **131** and Readable in **95**, mostly in the
  history books drafted first (Deuteronomy 40 at B, Joshua, Kings,
  Chronicles). The prophets and poetry follow the rule (Psalm 2:1 देश; Isaiah
  49:6 देशों).
- **Alternatives.** (a) Apply the rule: देश / राष्ट्र at B and R everywhere;
  (b) allow जाति at B where it means a people, not a caste (for example
  Genesis 25:23, "two nations are in your womb").
- **Examples.** Genesis 25:23; Exodus 34:10; Deuteronomy 4:6; Psalm 2:1
  (follows the rule).
- **If changed.** Under (a), about 150 records are revised.

### 3.6 *Peshaʿ* (transgression) at Balanced: विद्रोह or अपराध

- **Question.** One Balanced word for *peshaʿ*, the sin that is rebellion?
- **Now.** The terms table gives अपराध (sin पाप; iniquity अधर्म / दोष;
  transgression अपराध). Literal has अपराध in 88 of the **90** records with
  *peshaʿ*, but Balanced splits: विद्रोह in **49** (Psalms 12, Isaiah 9,
  Ezekiel 10, Micah 5, Job 3, Lamentations 3), अपराध in **32** (the
  Pentateuch, Job 7, Proverbs, Amos 10). Readable mostly explains (विद्रोह in
  18).
- **Alternatives.** (a) अपराध at B, as the terms table; (b) विद्रोह at B,
  which says the rebellion the word means, and the terms table changed.
- **Examples.** Psalm 32:1 (अपराध); Psalm 51:3 [51:1] (विद्रोह के कामों);
  Isaiah 53:5 (विद्रोहों); Amos 1:3 (अपराध).
- **If changed.** 49 or 32 records at Balanced.

### 3.7 Righteousness at Readable: सही, धार्मिकता or धर्मी

- **Question.** How does Readable say *tsedaqah* / *tsedeq* and *dikaiosynē*,
  and must an Old Testament line read the same as the New Testament line that
  quotes it?
- **Now.** The style guide sets धार्मिकता. At Readable the Old Testament mostly
  explains: of the records with *tsedaqah* or *tsedeq*, Readable has सही in
  **152**, धार्मिकता in **47** (most in Isaiah), धर्मी in **15**. The New
  Testament's Readable has धार्मिकता in **57**, धर्मी in **25**, सही in **16**.
  The clearest clash: Genesis 15:6 R "प्रभु ने उसे धर्मी गिना" but Romans 4:3
  R, quoting it, "परमेश्वर ने उसे धार्मिकता गिना" (also 4:9, 4:22), while
  Galatians 3:6 R has "धर्मी माना".
- **Alternatives.** (a) धार्मिकता at every level, Readable included;
  (b) Readable explains (सही, "जो सही है") as now, but one fixed wording for
  the Genesis 15:6 line in Genesis, Romans 4, Galatians 3 and James 2:23;
  (c) धर्मी गिनना / मानना for "counted as righteousness" everywhere.
- **If changed.** (b) is 6 records; (a) is about 180.

### 3.8 "Most High" in the Psalms at Readable

- **Question.** Does Readable keep the title परमप्रधान or paraphrase it?
- **Now.** All **22** Psalms records with *ʿElyon* paraphrase it at Readable
  (सबसे ऊपर विराजमान परमेश्वर, "तू जो सबसे ऊपर है", "उन परमेश्वर के पास ...
  जो सबसे ऊपर हैं" in Psalm 91:1), while Literal and Balanced say परमप्रधान
  (21 records) and Deuteronomy 32:8 keeps परमप्रधान at Readable.
- **Alternatives.** (a) परमप्रधान at Readable too (a title readers know from
  church); (b) one fixed paraphrase at every Readable use.
- **Examples.** Psalm 9:3; 46:5; 91:1, 91:9; 92:2.
- **If changed.** 22 records.

### 3.9 तू in lines the New Testament quotes

- **Question.** When the New Testament quotes an Old Testament line with
  तू, does the Old Testament line keep तू too?
- **Now.** `docs/hindi-terms.md` says quoted lines keep the New Testament's
  forms of address "even where they bend a rule" (Psalm 2:7 keeps तू, as
  Hebrews 1:5). But three prominent quotations do not:
  - Zechariah 9:9: तुम at every level; Matthew 21:5 and John 12:15 say
    "देख, तेरा राजा तेरे पास आता है" (L, B). The Zechariah decision gives the
    reason: in the Old Testament तू is kept for address to God.
  - Micah 5:1 [5:2]: Bethlehem is तुम; Matthew 2:6 has तू (its decision is
    marked uncertain).
  - Isaiah 49:6: God says तुम to the Servant; Acts 13:47 says तू.
- **Alternatives.** (a) The Old Testament line takes the New Testament's तू
  (the terms rule); (b) the New Testament quotations take तुम, to match the
  Old Testament; (c) leave both, each with its decision (now).
- **If changed.** 3 Old Testament records under (a); 4 New Testament records
  under (b). The same question then applies to the other quotations listed in
  `docs/hindi-terms.md` ("The New Testament quotes the Old").

### 3.10 Gideon's address to the angel (Judges 6)

- **Question.** How does Gideon address the visitor who turns out to be the
  angel of the LORD and speaks as the LORD (6:14, 16)?
- **Now.** आप and मेरे स्वामी through verse 18 (4 records: 6:13, 15, 17-18),
  as to a respected stranger, with प्रभु for *Adonai* in 6:15; then तू when he
  prays to God (6:22, 36-39). The visitor says तुम to Gideon (11 records).
- **Alternatives.** (a) तू from the point where the visitor speaks as the
  LORD (people say तू to God); (b) keep आप, which keeps the scene's surprise
  (verse 22).
- **If changed.** 3-4 records. A ruling may also bear on Manoah and the
  angel (Judges 13) and Abraham's visitors (Genesis 18).

### 3.11 Myrtle: मेंहदी

- **Question.** Is मेंहदी right for the myrtle?
- **Now.** मेंहदी in all **6** records (Nehemiah 8:15; Isaiah 41:19, 55:13;
  Zechariah 1:8, 10, 11), with हदस (the Hebrew name) as the recorded
  alternative. In everyday Hindi मेंहदी is henna, and the Song of Songs uses
  हिना for henna (1:14; 4:13), so the two plants may be confused.
- **Alternatives.** हदस; another name for the myrtle you know readers use.
- **If changed.** 6 records.

### 3.12 Isaiah 7:14: युवती

- **Question.** Confirm युवती for *ʿalmah*.
- **Now.** युवती at every level (1 record), with a footnoted decision naming
  Matthew 1:23's कुँवारी, which quotes the Greek Old Testament's *parthenos*.
  The meaning decision is "the young woman", and a rendering may not narrow
  it. Alternatives recorded: जवान स्त्री, कुँवारी.
- **If changed.** One record, but expect readers to ask about it: कुँवारी
  here would narrow the meaning decision, which is the scholar reviewers' to
  change, not the Hindi's.

## 4. Decisions marked uncertain

The drafters marked **662** Hindi rendering decisions uncertain, in 49 books.
The table gives the count for each book and its first two, in Bible order.
The largest groups are Matthew (64), Psalms (60), 1 Kings (49), Proverbs
(45), 2 Samuel and Ezekiel (36 each). Many are name spellings coined for one
book and word choices for plants, animals and objects whose identity is
uncertain; settling section 3 first will answer some of them.

The full list, every decision with a link to its verse, its levels, category,
choice and reason, is [`docs/review-notes/hi-uncertain.md`](review-notes/hi-uncertain.md),
regenerated with

    python3 scripts/review_checklist.py hi --write

and the admin's **Uncertain decisions** page (layer "Hindi") lists the same
decisions with a link to each in the verse inspector.

| Book | Uncertain | Reference | Choice | Reason (excerpt) |
|---|---:|---|---|---|
| Genesis | 30 | Genesis 24:60 | "तुम" in the blessing at every level | The family speaks to Rebekah with "तुम", as in verse 58 … |
|  |  | Genesis 25:6 | "रखेलियों" for concubines (L, B); "दूसरी पत्नियों" (R) | "रखेल" is the everyday Hindi word for a secondary wife without a wife's full standing … |
| Exodus | 17 | Exodus 2:3 | "पिटारी" (a small covered basket) | The Hebrew word is the one used of Noah's ark (m1), which this translation calls "जहाज़" (as Hebrews 11:7), and "संदूक" is kept for the ark of the … |
|  |  | Exodus 3:1 | "निर्जन प्रदेश" at every level | The wilderness is dry, empty grazing land. |
| Leviticus | 8 | Leviticus 11:5 | "चट्टानी बिज्जू" (rock badger) | Probably the rock hyrax, a small animal that lives among rocks (m1). |
|  |  | Leviticus 11:13 | Hindi bird names in verses 13-19 follow the English identifications | The exact identity of many of these birds is uncertain (m1). |
| Numbers | 33 | Numbers 1:5 | the leaders' names in their established Hindi Bible spelling (एलीसूर, … | Names that also occur in the New Testament (नहशोन, अम्मीनादाब, Matthew 1:4) keep the form used there … |
|  |  | Numbers 3:48 | "रुपया" for the money (silver) | The Hebrew word is "silver", used for money (m1). |
| Joshua | 7 | Joshua 15:17 | "कालेब के भाई कनज़ के पुत्र ओत्नीएल" | Hindi puts the descriptions before the name, so "the brother of Caleb" stands next to Kenaz, as in the English. |
|  |  | Joshua 17:11 | "ऊँचाइयों के तीन" (L); "पहाड़ी क्षेत्रों के तीन ज़िले" (B, R) | The phrase is unclear (m3). |
| Ruth | 4 | Ruth 1:15 | "देवरानी" (the wife of one's husband's younger brother) | Hindi has no neutral word for a husband's brother's wife: it says either "जेठानी" (elder brother's wife) or "देवरानी" (younger brother's wife). |
|  |  | Ruth 1:20 | "मारा" (Mara) | The name is transcribed as Hindi Bibles have it. |
| 1 Samuel | 5 | 1 Samuel 5:6 | tumors: "गिल्टियाँ" | The Hebrew names painful swellings of a kind not known for certain (m3). |
|  |  | 1 Samuel 10:5 | "सारंगी", "डफ़", "बाँसुरी", "वीणा" | The lyre (kinnor), the tambourine and the flute keep the words of Genesis 4:21 and 31:27 in this translation ("वीणा", "डफ़", "बाँसुरी"). |
| 2 Samuel | 36 | 2 Samuel 1:9 | "ऐंठन" (L); "घोर पीड़ा" (B, R) | The Hebrew word is rare and its exact sense uncertain: a cramp, agony or faintness (meaning m1). |
|  |  | 2 Samuel 2:9 | "अशूरियों" | A people not known elsewhere, perhaps the tribe of Asher (meaning m1) … |
| 1 Kings | 49 | 1 Kings 1:11 | "आप" from Nathan to Bathsheba | Nathan speaks to the king's wife with आप … |
|  |  | 1 Kings 1:33 | "तुम" from David to Zadok, Nathan and Benaiah together | The king gives orders to the three men as a group with the familiar imperative (लो, कराओ, ले जाओ), as he speaks to his officials in 2 Samuel. |
| 2 Kings | 14 | 2 Kings 12:10 | "संदूक" for the money chest | The Hebrew word is the one used for the ark, and Hindi "संदूक" is also the ark's word in this translation … |
|  |  | 2 Kings 13:13 | "गद्दी" for the throne | "गद्दी पर बैठना" is the everyday Hindi for succeeding to a throne … |
| 1 Chronicles | 10 | 1 Chronicles 3:21 | "येशायाह" | The English keeps this Jeshaiah apart from the prophet Isaiah, whose Hindi name is "यशायाह" … |
|  |  | 1 Chronicles 3:23 | "हिजकियाह" | As the English writes Hizkiah here and Hezekiah for the king (verse 13), the Hindi keeps the two men apart by spelling. |
| 2 Chronicles | 8 | 2 Chronicles 18:23 | "तुझसे" in Zedekiah's mouth | Kept from 1 Kings 22:24 in this translation, where the same Hebrew has the contemptuous तू of one prophet striking another … |
|  |  | 2 Chronicles 19:8 | "वे यरूशलेम को लौटे" at every level | The English keeps the Hebrew "they returned" (meaning m4), so the Hindi does too, without deciding who returned. |
| Ezra | 1 | Ezra 10:2 | "विदेशी स्त्रियाँ" (Literal), "विदेशी पत्नियाँ" (Balanced, Readable) | The Hebrew word (nokhri) is a woman of another people, not the resident outsider (ger) that the Pentateuch note renders "परदेशी". |
| Nehemiah | 7 | Nehemiah 2:17 | Nehemiah says "तुम" to the leaders of Judah | Nehemiah, the king's appointee, speaks to his own people as one of them ("आओ, हम ... |
|  |  | Nehemiah 3:31 | "निरीक्षण-फाटक" at every level | The English has "Muster Gate" at Literal and "Inspection Gate" at Balanced and Readable … |
| Job | 13 | Job 9:9 | सप्तर्षि, मृगशिरा, कृत्तिका | Hindi has its own names for the Great Bear, Orion and the Pleiades, which readers know from the night sky … |
|  |  | Job 10:17 | बदलती टुकड़ियाँ और सेना | A bare "changes" means nothing in Hindi … |
| Psalms | 60 | Psalms 6:1 | "शमीनीत" (L, B); "आठवें" (R) | The word means "the eighth", a musical direction whose exact sense is lost (meaning m3). |
|  |  | Psalms 8:1 | "गित्तीत", kept as a name | The gittith may be an instrument or a tune, perhaps from Gath (meaning m3) … |
| Proverbs | 45 | Proverbs 7:22 | "जैसे पायल मूर्ख के अनुशासन के लिए" | The Hebrew text reads "like an anklet to the discipline of a fool" (meaning m1), which is hard to follow … |
|  |  | Proverbs 7:26 | "बहुत" | The word can mean numerous or mighty (meaning m1) … |
| Ecclesiastes | 3 | Ecclesiastes 5:5 | "मन्दिर के दूत" | As the English Readable, Readable says where the messenger would be met, in the reading taken: probably the priest or temple official who dealt with … |
|  |  | Ecclesiastes 6:10 | "परमेश्वर ... जो उनसे अधिक बलवान हैं" | As the English Readable, Readable names God in the reading taken (m3), with the honorific verb. |
| Song of Songs | 25 | Song of Songs 1:11 | बनाएँगे (the plural without a gender of its own) | Who says "we" is uncertain: the man with others, or the women of Jerusalem (m1). |
|  |  | Song of Songs 1:17 | देवदार; सनोवर | Cedar is देवदार and the tree the English calls cypress is सनोवर, as in Psalm 104:16-17 in this translation. |
| Isaiah | 29 | Isaiah 3:18 | पायलें, माथे की पट्टियाँ, चंद्रहार ... (verses 18-23) | The finery of verses 18-23 is named with the nearest Hindi ornaments and garments (पायल, झुमके, नथ, कमरबंद, ताबीज़, पगड़ी, ओढ़नी). |
|  |  | Isaiah 4:2 | {{divine_name:प्रभु\|याहवे}} का अंकुर | tsemach is what sprouts from the ground … |
| Jeremiah | 16 | Jeremiah 6:27 | परखनेवाला (L), धातु परखनेवाला (B, R); गढ़ (L, B) | bachon is one who tests metal to find its worth (m2) … |
|  |  | Jeremiah 8:7 | "लगलग", "पंडुक", "अबाबील", "सारस" | The stork and turtledove keep the forms of Deuteronomy 14:18 and Leviticus 1:14 … |
| Ezekiel | 36 | Ezekiel 1:4 | दमकती धातु (L); चमकती धातु (B, R) | No one knows for certain what chashmal was (m1): a substance that shines in fire. |
|  |  | Ezekiel 1:12 | आत्मा (masculine agreement) | Ruach here is the power that moves the creatures, and the text does not say whose spirit it is (m1). |
| Daniel | 4 | Daniel 8:12 | "लोगों के पाप"; "परमेश्वर के लोग" (Readable) | Readable takes one reading of a hard verse (m1) and says whose sin and which host are meant, as the English does … |
|  |  | Daniel 9:27 | "वह शासक"; "सात वर्ष"; "मन्दिर के एक ऊँचे भाग पर"; "परमेश्वर ने" … | Readable takes the usual readings of m1 and m3 and says them plainly, as the English does … |
| Hosea | 1 | Hosea 13:2 | मनुष्यों की बलि चढ़ानेवाले (L) | Literal keeps the Hebrew order of "sacrificers of humankind", which could be read as human sacrifice … |
| Joel | 2 | Joel 1:17 | बीज ... ढेलों के नीचे सिकुड़ गए हैं | The line has three rare words and is uncertain (meaning decision m1) … |
|  |  | Joel 4:21 | निर्दोष ठहराऊँगा (L); बदला लूँगा (B); दंड दूँगा (R) | Literal keeps the Hebrew verb … |
| Amos | 7 | Amos 4:1 | feminine forms for the "cows" (करती हो, जाओगी); स्वामी (L), पति (B, R) | The cows of Bashan are the wealthy women of Samaria (meaning decision m2), so Hindi uses feminine verbs through verses 1-3, as the Hebrew does … |
|  |  | Amos 4:3 | हरमोन | Harmon is a place not otherwise known (meaning decision m3) … |
| Obadiah | 1 | Obadiah 1:20 | सारपत; सपारद | Zarephath keeps the form of Luke 4:26 in this translation … |
| Jonah | 1 | Jonah 2:9 | अपने अटल प्रेम (L, B); सच्चा प्रेम (R) | Their hesed may be the loyalty they owe or the God who shows them loyal love (m2). |
| Micah | 4 | Micah 1:3 | पृथ्वी के ऊँचे स्थान | Every level says ऊँचे स्थान, the word for the hilltop shrines (verse 5), so the hint the meaning decision notes (m2) is kept. |
|  |  | Micah 2:4 | वे (honorific) for the one who takes the land; no deity_pronoun spans | The one who changes, takes and divides is most likely the LORD (m2), though the words do not name him. |
| Nahum | 3 | Nahum 1:14 | हे अश्शूर के राजा (R) | Readable names the king of Assyria as the one addressed, as the English Readable does … |
|  |  | Nahum 2:11 | चेहरे पीले पड़ जाते हैं | The last line repeats Joel 2:6, which is not yet drafted in Hindi … |
| Habakkuk | 3 | Habakkuk 2:15 | अपना रोष (L) | The Hebrew shifts to "your wrath" in the middle of the woe (m2). |
|  |  | Habakkuk 3:1 | शिग्योनोत पर (L, B); गीत के रूप में गाई जाए (R) | Shigionoth is the plural of the shiggayon of Psalm 7:1 (शिग्गायोन). |
| Zechariah | 2 | Zechariah 14:6 | जम जाएँगी (L); मंद पड़ जाएँगी (B); फीकी पड़ जाएँगी (R) | The text is very uncertain (meaning m1). |
|  |  | Zechariah 14:18 | तो उन पर भी [वर्षा] न [होगी] | The Hebrew "and not on them" is a hard text (meaning m1) … |
| Matthew | 64 | Matthew 1:20 | "तुम" from the angel to Joseph | The angel speaks as God's messenger to a man, in the familiar form a respected speaker uses … |
|  |  | Matthew 2:1 | "ज्योतिषी" (L, B); "तारों का अध्ययन करनेवाले ज्ञानी लोग" (R) | The magi were learned men who read the stars. |
| Mark | 3 | Mark 13:14 | "उजाड़ की घृणित वस्तु" (L); "विनाश लानेवाली घृणित चीज़" (B); "विनाश … | Daniel's phrase in the forms used at Matthew 24:15. |
|  |  | Mark 15:21 | "सिकंदर", "रूफ़ुस"; "कुरेनी", "कुरेने" as in Matthew 27:32 | Alexander has a long-established Hindi form, "सिकंदर". |
| Luke | 26 | Luke 2:48 | Mary says "तुम" to her twelve-year-old son | People speaking to Jesus say "आप" in this translation, but that is the address of adults to a teacher. |
|  |  | Luke 2:49 | the boy Jesus says "आप" to his parents | Jesus speaking says "तुम" in this translation, but a Hindi son speaks to his parents with "आप" … |
| John | 15 | John 1:42 | "केफ़ा" for Cephas | Cephas is written "केफ़ा", close to the Aramaic Kepha, so that it is not confused with the high priest Caiaphas, "कैफ़ा" (style guide section 5). |
|  |  | John 2:5 | the mother speaks of her son plainly ("जो कुछ वह तुमसे कहे") | The narrator's "his mother" is honorific ("उनकी माता"), as for Jesus throughout … |
| Acts | 15 | Acts 1:24 | "तू" in this prayer to the Lord | The prayer may be to Jesus or to God (meaning decision m1). |
|  |  | Acts 13:6 | "प्रांतपति" (L, B); "रोमी शासक" (R) for the proconsul | The proconsul governed a province for the Roman senate (meaning decision m3). |
| Romans | 1 | Romans 16:1 | "सेविका" (L, B); "सेवा का काम करती है" (R) | Diakonos here names a recognized role of service in the church (meaning decision m3). |
| 1 Corinthians | 8 | 1 Corinthians 10:1 | "वह चट्टान मसीह था" | The verb agrees with the rock as the subject of the statement … |
|  |  | 1 Corinthians 10:23 | "उचित है" (L); "की छूट है" (B, R) | The Corinthian saying of 6:12 returns here (meaning decision m1), so it should read as it does there … |
| 2 Corinthians | 2 | 2 Corinthians 4:13 | "विश्वास का वही आत्मा" | The English marks the reading of meaning decision m2 (the Holy Spirit) with a capital letter. |
|  |  | 2 Corinthians 10:17 | "प्रभु" | Paul quotes Jeremiah with the Greek word for Lord, so Hindi says "प्रभु" … |
| Ephesians | 2 | Ephesians 3:14 | "घराना" (L, B); "परिवार" (R) | The Greek plays on "father" (pater) and "family" (patria), a group descended from one father (meaning decision m4) … |
|  |  | Ephesians 5:28 | "देह" for flesh (verse 29); "शरीर" for body (verses 28, 30) | Verse 31 quotes Genesis 2:24 in the words of Matthew 19:5, where "one flesh" is "एक देह". |
| 2 Timothy | 2 | 2 Timothy 1:3 | "नानी" for the grandmother | Hindi must say whether a grandmother is the mother's or the father's mother … |
|  |  | 2 Timothy 1:7 | "आत्मा" with masculine agreement ("का आत्मा", "दिया") | The spirit God gives is taken to be his own Spirit (meaning decision m1), so it takes the masculine agreement the style guide gives the Spirit as a … |
| Titus | 1 | Titus 3:13 | "व्यवस्थापक" (L); "व्यवस्था का ज्ञाता" (B); "व्यवस्था का जानकार" (R) | The word is Luke's nomikos, and Literal and Balanced keep Luke's forms. |
| Philemon | 1 | Philemon 1:20 | "तुम भी मेरे काम आओ" (B); "मुझे तुमसे कुछ लाभ मिले" (L) | The verb plays once more on the name Onesimus (meaning decision m1) … |
| Hebrews | 5 | Hebrews 1:13 | Psalm 110:1 in the wording of Luke 20:42-43 and Acts 2:34-35, with … | The same psalm verse, with the same Greek, is already rendered in Luke and Acts, so each level keeps that wording, including the familiar "तुम" with … |
|  |  | Hebrews 5:6 | "तू" in Psalm 110:4 | God speaks to the Son, and the author reads this verse together with Psalm 2:7 (verse 5), so the intimate "तू" of Acts 13:33 is kept. |
| James | 5 | James 3:6 | "जीवन के चक्र" | The wheel of existence is the whole course of human life (meaning decision m3). |
|  |  | James 3:15 | "शारीरिक" for psychikos | The word means belonging to human life without God's Spirit (meaning decision m2). |
| 1 Peter | 5 | 1 Peter 1:24 | "सब देहधारी" for "all flesh" | "सब शरीर" would read as "the whole body" in Hindi. |
|  |  | 1 Peter 3:3 | "छिपा हुआ मनुष्यत्व" (L); "छिपा हुआ व्यक्तित्व" (B) | The hidden person of the heart is the inner self (meaning decision m4). |
| 2 Peter | 1 | 2 Peter 2:4 | "भक्तिहीन" (asebes); "नियमहीन" (athesmos); "अधर्म के काम" (anomos); … | Four Greek words for the wicked stand in this sentence. |
| Revelation | 22 | Revelation 1:10 | "पुस्तक" (L, B); "किताब" (R) | The Greek word is the ordinary word for a book, which then took the form of a scroll (m3). |
|  |  | Revelation 1:14 | "उत्तम काँसा" (L, B); "काँसा" (R) | A highly polished bronze alloy (m2). |

## 5. Most-read passages to review first

These are read and memorised most, and memory of the Hindi Old Version pulls
hardest on them: check that the wording is right, natural and our own. Open
each in the admin's Review queue with the book filter. Records are sentences;
the last column counts the Hindi decisions marked uncertain in the passage.

| Passage | Records | Uncertain (hi) |
|---|---:|---:|
| Genesis 1-3 | 80 | 0 |
| Exodus 20 | 26 | 1 |
| Psalm 23 | 6 | 0 |
| Psalm 51 | 21 | 0 |
| Psalm 91 | 16 | 1 |
| Isaiah 9 | 20 | 0 |
| Isaiah 40 | 31 | 0 |
| Isaiah 53 | 12 | 0 |
| Jeremiah 31 | 40 | 1 |
| Micah 5 | 14 | 0 |
| Matthew 5-7 | 118 | 10 |
| Luke 2 | 42 | 2 |
| John 1 | 60 | 1 |
| John 3 | 38 | 1 |
| Romans 8 | 39 | 0 |
| 1 Corinthians 13 | 12 | 0 |
| Revelation 21-22 | 51 | 2 |
| **All 17 passages** | **626** | **19** |

Micah 5 here is the Hebrew chapter (English 5:2 is 5:1); Isaiah 9 starts at
English 9:2; Psalm 51 counts its two title verses. In the New Testament the
uncertain decisions cluster in Matthew 5-7 (10): the `gender` spans for
"sons of God" (5:9, 5:45), प्रतिफल (5:12), सिद्ध (5:48), the clothes of 5:40,
the "evil eye" of 6:22-23 and others.

## 6. The files and scripts

- `docs/hindi-style.md`: how the Hindi is drafted (levels, address,
  spelling, settings, the New Testament's words, Matthew's conventions).
- `docs/hindi-terms.md`: the Old Testament's terms, formulas, names, parallel
  passages and quotations. Section 3 of this guide changes it.
- `docs/review-notes/hi-uncertain.md`: every uncertain Hindi decision,
  generated by `python3 scripts/review_checklist.py hi --write`.
- `docs/review-notes/name-spellings.md`: names spelled more than one way,
  every language (`python3 scripts/name_spellings.py --lang hi`).
- The counts in section 3 and the tables in sections 4 and 5 were made with
  one-off scripts kept outside the repository (in the drafting session's
  scratch folder `review-fix/`: `owbdata.py` loads every record with its
  Strong's numbers from `data/hbo/` and `data/grc/`, `run*.py` hold the
  queries, `names.py` the nukta count, `hyphens.py` the hyphen pairs,
  `uncertain_table.py hi 2` the table of section 4 and `passages.py` the
  table of section 5). Each count is a plain text search over the Hindi
  renderings, restricted to the records whose source holds the Hebrew or
  Greek word where that matters; rerun the same search after a change.
- `content/<BOOK>/*.json`: the records. Reviewers do not need to edit them:
  the admin is the review tool.
