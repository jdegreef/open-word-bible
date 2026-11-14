# Words of Jesus: does every language mark the same words?

`data/words_of_jesus/<BOOK>.json` marks a sentence once for all languages
(`owb/words_of_jesus.py`); each rendering's own quotation marks then decide
which of its words are red. So the set of marked sentences is the same in every
language by construction. What can differ is the *segments*: a quotation mark
missing, extra or misplaced in one language makes that language show Jesus'
words in black, or someone else's words in red.

`scripts/check_words_of_jesus.py` compares, for every marked sentence and
level, the share of each rendering that is red (as a reader sees it: settings
at their defaults, verse and line markers left out) with the other languages'
median, and flags a rendering that

- has no red letters where the others have some,
- differs from the median by more than 0.3 of its length, or
- has more quotations than any other language (usually a gloss or a term in
  quotation marks that the narrator, not Jesus, says).

A language that orders the sentence differently ("He said to them, '...'"
where English has "'...,' he said, '...'") has fewer quotations but the same
red share, so it is not flagged. `scripts/check.sh` runs the check, and
`tests/test_words_of_jesus.py` fails on any mismatch that is neither fixed nor
listed in `pending-quote-fixes.jsonl`.

## What the first run found (8 books, 2,068 marked sentences)

| Sentence | Language, level | What was wrong | Fixed in |
|---|---|---|---|
| John 1:42 (`JHN.1.42.s2`) | French, Readable | The narrator's note `(Céphas et Pierre veulent ... « pierre » ou « rocher ».)` quotes two words, which turned red | data: marked `[0]`, his one saying |
| John 9:6–7 (`JHN.9.6.s1`) | Korean, all levels | The note on Siloam's meaning, in single quotes, turned red | data: marked `[0]` |
| Mark 2:9 (`MRK.2.9.s1`) | Vietnamese and Korean, Balanced; every language, Literal and Readable | The sentence continues the speech Mark 2:8 opens, but was marked "quoted", so only the two sayings quoted inside it were red where the rendering does not reopen the quotation | data: marked `"all"`; the whole question is red in every language and level |
| Luke 5:10, Mark 8:29 and 21 more | French, Balanced (21) and Readable (2) | The incise naming Jesus (`dit-il`, `leur demanda-t-il`, `dit Jésus à Simon`, `a dit Jésus`) sits inside the guillemets, as French typography allows, so the narrator's words are red | pending: `pending-quote-fixes.jsonl` closes the guillemets before the incise and reopens them after |

The French entries are the same pattern in 23 renderings; the check's
thresholds flag the three where the incise is long (Luke 5:10 at two levels, Mark 8:29), and
the list in `pending-quote-fixes.jsonl` was made by finding every incise that
names Jesus inside his red letters. Both French styles are correct; the one
that keeps the incise outside the guillemets is the one that lets the reader
colour only his words. A note for `docs/french-style.md`: prefer it wherever
the sentence is marked as words of Jesus.

## Pending fixes

`pending-quote-fixes.jsonl` holds one JSON object per line: `record`,
`language`, `level`, `old` (the rendering today), `new` (the same rendering
with only its quotation marks moved) and `reason`. Content is not edited here:
a reviewer or drafting session applies each fix to `content/` and removes its
line. The test checks that every `old` is still the rendering's text (so a
fix made or overtaken shows up) and that every `new` turns fewer words red.

## Not caught by this check

A mistake every language shares (a sentence marked "quoted" that should be
"all" in all of them) has no outlier. Mark 2:9 was found because two
languages differed at one level; the same mistake in all twelve would pass.
A second check worth adding: a sentence marked "quoted" that follows one
whose renderings end inside an open quotation in most languages.
