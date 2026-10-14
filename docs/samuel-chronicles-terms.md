# Samuel, Kings and Chronicles: recurring terms and book-wide choices

**Status: proposed, awaiting the founder's approval.** 1 and 2 Samuel, 1 and 2
Kings and 1 and 2 Chronicles were drafted chapter by chapter in parallel from
one brief. These are the choices that keep them consistent with each other and
with the books before them. Read with `docs/english-style.md` and
`docs/numbers-ruth-terms.md` (whose shared table still applies: *chesed*,
*ger*, *sar*, *'eved*, units). The style guide wins where they differ.

## Titles and names of God

| Hebrew | Literal | Balanced | Readable |
|---|---|---|---|
| YHWH tseba'ot | the LORD of hosts | the LORD of Armies | the LORD of Armies |
| Adonai YHWH | {{divine_name:Lord GOD\|Lord Yahweh}} | same | same |
| ne'um YHWH | declares the LORD | declares the LORD | says the LORD |
| koh amar YHWH | Thus says the LORD | The LORD says this | This is what the LORD says |
| ha'elohim, "the God" | God | God | God |
| mashiach YHWH | the LORD's anointed | the LORD's anointed | the king the LORD has anointed (decision at 1 Samuel 24:7) |

The divine name is always a `divine_name` span, as before.

## Kings and the court

| Hebrew | Literal | Balanced | Readable |
|---|---|---|---|
| nagid | ruler | ruler | leader |
| 'avdei hammelekh | the king's servants | the king's officials | the king's officials |
| "my servant David" ('eved) | my slave David | my servant David | my servant David |
| sar hatsava' | commander of the army | commander of the army | army commander |
| sarisim | eunuchs (decision where the sense may be "official") | officials | officials |
| bamot | high places | high places | hilltop shrines |
| matstsevot, asherim | standing stones, Asherah poles | same | stone pillars, poles used to worship Asherah |
| teraphim | household gods | household gods | household idols |
| ephod; Urim and Thummim | names kept, with decisions | | |
| ish ha'elohim | man of God | man of God | man of God |
| bene hannevi'im | sons of the prophets | company of prophets | group of prophets |
| ro'eh, chozeh | seer | seer | seer (explained once) |

## Formulas

The regnal formulas recur hundreds of times. Use one wording at each level:

- **Accession:** "In the Nth year of X king of Judah, Y son of Z became king
  over Israel in Samaria, and he reigned N years" (Balanced). Literal follows
  the Hebrew ("Y reigned"). Readable may split it into two sentences.
- **Verdict:** "did the evil in [the] eyes of the LORD" / "did what was evil
  in the sight of the LORD" / "did what the LORD said was evil"; and "did
  what was right in the sight of the LORD" for the good kings, as in Judges.
- **Death:** "lay down with his fathers" (Literal) / "rested with his
  ancestors" (Balanced) / "died" (Readable, with "and was buried with his
  ancestors" where the Hebrew names the burial).
- **Sources:** "the book of the matters of the days of the kings of Israel"
  (Literal) / "the Book of the History of the Kings of Israel" (Balanced) /
  "the history of the kings of Israel" (Readable), with a decision at its
  first use. The question form "Are they not written ...?" stays a question at
  Literal and becomes a statement at Balanced and Readable.
- **"Until this day":** "to this day" at every level, with a decision at its
  first use in each book that it is the writer's own day.

## Places and people

- Names keep the data's English forms. A king with two names (Azariah and
  Uzziah, Jehoahaz and Shallum) keeps the form each verse uses, and has a
  decision where the switch could confuse.
- The divided kingdom: "Israel" for the northern kingdom and "Judah" for the
  southern at every level, with a decision at 1 Kings 12.

## Poetry set in lines

Hannah's song (1 Samuel 2:1-10); the women's song (1 Samuel 18:7; 21:12;
29:5); David's laments (2 Samuel 1:19-27; 3:33-34); David's song (2 Samuel 22,
which is Psalm 18: reuse Psalm 18's wording wherever the Hebrew is the same,
with a decision on each difference); David's last words (2 Samuel 23:1-7);
the oracle against Sennacherib (2 Kings 19:21-28); the psalm of 1 Chronicles
16:8-36 (Psalms 105:1-15, 96, 106:1, 47-48: reuse their wording).

## Parallels

- **2 Kings 18:13-20:19** is Isaiah 36-39, already translated: reuse Isaiah's
  wording where the Hebrew is the same and note each difference.
- **Chronicles** retells Samuel and Kings. Where its Hebrew matches the earlier
  books, reuse their wording; where it differs, a decision says how.
- **1 Chronicles 1-9** are genealogies: keep the list formulas identical and
  the decisions short.

## Versification

Hebrew numbering throughout, with a footnoted decision at the first verse of
each shift (`data/versification.json`): 1 Samuel 20:42, 21:1 and 24:1;
2 Samuel 19:1; 1 Kings 5:1 (Hebrew 5:1-14 is English 4:21-34), 18:34, 20:3,
22:21 and 22:44; 2 Kings 12:1; 1 Chronicles 5:27 (Hebrew 5:27-41 is English
6:1-15), 6:1 and 12:4; 2 Chronicles 1:18, 2:1, 13:23 and 14:1.
