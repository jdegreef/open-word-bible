# Isaiah: recurring terms and book-wide choices

**Status: proposed, awaiting the founder's approval.** All 66 chapters of
Isaiah were drafted in parallel from one brief, and these are the choices that
keep the book consistent. If a choice changes, every chapter drafted under it
is revised. Read with `docs/english-style.md`.

## Settled wording

| Hebrew | Literal | Balanced | Readable |
|---|---|---|---|
| YHWH tseba'ot | the LORD of hosts | the LORD of Armies | the LORD of Armies |
| Adonai alone | the Lord | the Lord | the Lord |
| shaddai | the Almighty | the Almighty | God All-Powerful |
| qedosh yisrael | the Holy One of Israel | same | same |
| ne'um YHWH | declares the LORD | declares the LORD | says the LORD |
| koh amar YHWH | Thus says the LORD: | The LORD says this: | This is what the LORD says: |
| hoy | Woe, ... | Woe to ... | How terrible it will be for ... |
| 'oy said of oneself | Woe [is] me | Woe is me | How terrible this is for me |
| bayyom hahu | in that day | on that day | at that time / on that day |
| bat-tsiyyon | daughter of Zion | Daughter Zion | the people of Zion (R decision) |
| bat-babel etc. | daughter of Babylon | Daughter Babylon | (explain at R) |
| sheol | Sheol | Sheol | the grave |
| rephaim | shades | the dead | the dead |
| hesed | loyal love | loyal love | faithful love |
| go'el (God) | Redeemer | Redeemer | Redeemer / the one who rescues |
| iyyim | coastlands | coastlands | lands far away |
| ebed YHWH | servant | servant (lowercase) | servant |
| mashiach (45:1) | anointed | anointed | chosen (R decision) |
| tsedeq/tsedaqah | righteousness (or justice/vindication/victory with a word_sense decision) | | |
| torah | instruction | instruction | teaching |
| kavod | glory | glory | glory |
| yeshu'ah | salvation | salvation | salvation / save |
| shalom | peace | peace | peace (or well-being with a decision) |
| court officials (ebed) | servants | officials | officials |
| massa (title of an oracle) | oracle | oracle | message |
| oniyyot tarshish | ships of Tarshish | ships of Tarshish | great trading ships |
| helilu | Wail | Wail | Cry out in grief |
| Kittim | Kittim | Kittim | Cyprus |
| Chaldeans | Chaldeans | Chaldeans | Babylonians |
| se'irim | goats (fn goat-demons) | | |
| Jacob/Israel as the people | Jacob / Israel | Jacob / Israel | may say "people of Israel" with a decision |
| erets in world-judgment oracles | the earth (whole world) unless the context is Israel's land | | |
| shofar | trumpet | ram's horn | trumpet |
| the River (Euphrates) | the River | the Euphrates | the Euphrates |
| Leviathan, Rahab | names kept, with a note | | |
| YHWH addressed (vocative) | {{divine_name:LORD|Yahweh}} with no "O", as in Psalms | | |
| 'ani hu ("I am he") | I am {he} (dp span) | I am {he} | I alone am God (R decision); main note 43:10 |
| go'el verb | redeemed | redeemed | bought back |
| nes | signal flag | signal flag | signal flag |
| 'ob | spirit of the dead | ghost | ghost |
| karmel (orchard land) | orchard | orchard land | orchard |
| "There is no peace ... for the wicked" | as 48:22 (57:21 matches) | | |
| mebasser | bearer of good news | one who brings good news | messenger with good news (see 40:9) |
| Spirit of God | Spirit (capital S) | | |
| iniquity ('awon) | iniquity | guilt / sin | sin |

The divine name is always a `divine_name` span. Adonai with YHWH is "the Lord
{{divine_name:GOD|Yahweh}}" ("the Lord Yahweh" with the setting). YHWH
addressed directly is `{{divine_name:LORD|Yahweh}}` with no "O", as in the
Psalms. The main note on "the LORD of hosts" is at 1:9.

## Verse numbers

Isaiah is numbered as in the Hebrew text, and cited that way in decisions:
Hebrew 8:23 is 9:1 in most English Bibles, Hebrew 9:1-20 is 9:2-21, Hebrew
63:19b is 64:1, and Hebrew 64:1-11 is 64:2-12. Decisions at 8:23, 9:1, 63:19
and 64:1 say so. `owb/versification.py` maps these for the comparison Bibles.

## Speech

Most of the book is poetic oracle. The prophet's words and God's first-person
speech take no quotation marks, and "Thus says the LORD" is followed by a
colon. Speech quoted inside an oracle takes double quotes (single when nested).
The narrative chapters (6-8, 20, 36-39) quote speech as prose does.

## The servant

"Servant" in chapters 41-53 is sometimes Israel (41:8-9; 44:1-2, 21) and
sometimes a figure distinct from the people (49:5-6). The main note is at
41:8, and the four servant songs (42:1-4; 49:1-6; 50:4-9; 52:13-53:12) refer
back to it. The text never settles who the servant is; a theology decision may
say how the New Testament reads a passage. The servant, the king of 9:5 and
11:1, Cyrus and the speaker of 61:1 take no `deity_pronoun` span.

Other choices with notes: 7:14 "the young woman" (a meaning decision, uncertain
and footnoted, sets out the Hebrew word's range, the Septuagint's "virgin" and
Matthew 1:23); 14:12 "shining one" (the Latin "Lucifer" tradition is
footnoted); 45:7 "calamity", meaning disaster, not moral evil; 64:5 the
menstrual cloth, footnoted against "filthy rags".

## Before meaning review: manuscript claims to check

The drafts were written without the critical apparatus at hand. Every decision
below cites the Great Isaiah Scroll (1QIsa-a), the Septuagint or another
ancient witness from general knowledge. A reviewer must check each one
against the sources before the sentence is marked meaning reviewed.

- 1: 9 m1, 13 m3, 17 m1
- 2: 9 m3, 10 m3, 16 m2, 22 m3
- 3: 10 m3, 12 m2, 13 m2, 23 m1, 24 m3
- 5: 17 m2
- 6: 9 m3, 10 m2, 13 m4
- 7: 1 m2, 9 m3, 11 m2, 14 m1, 14 m2
- 8: 2 m1, 9 m1, 11 m2, 14 m1, 17 m2
- 9: 5 m3, 18 m1
- 10: 22 m2
- 11: 1 m3, 2 m3, 6 m3, 10 m1, 15 m1
- 12: 1 m2
- 14: 4 m2, 12 m1, 19 m1, 21 m2, 30 m2
- 15: 1 m1, 5 m2, 6 m1, 9 m1
- 16: 2 m3, 8 m2
- 17: 2 m2, 9 m1
- 18: 1 m2, 2 m3, 7 m1
- 19: 10 m1, 18 m1
- 21: 8 m1, 11 m1, 16 m2
- 23: 2 m3, 10 m1
- 24: 16 m2
- 25: 10 m2
- 27: 1 m1
- 28: 16 m2, 16 m3
- 29: 3 m2, 5 m1, 13 m1, 14 m2
- 32: 6 m2
- 34: 4 m3, 6 m2, 9 m2, 12 m1, 16 m2
- 35: 8 m3
- 36: 5 m1
- 37: 27 m2, 36 m3
- 38: 8 m2, 11 m1, 21 m1
- 40: 3 m1, 5 m2, 6 m1, 6 m2, 7 m2, 8 m2, 9 m2, 13 m1
- 41: 14 m2, 29 m1
- 42: 1 m3, 4 m2
- 43: 19 m3
- 44: 4 m1, 14 m1, 21 m1
- 45: 2 m1, 2 m3, 23 m3
- 48: 10 m1, 11 m1, 15 m2
- 49: 3 m2, 5 m1, 12 m2, 17 m1, 24 m1
- 51: 19 m2
- 52: 14 m1, 14 m2, 15 m1
- 53: 1 m2, 7 m2, 8 m3, 9 m1, 11 m1
- 54: 13 m2
- 55: 9 m2
- 58: 10 m1
- 59: 20 m1
- 60: 19 m1, 21 m1
- 61: 1 m4, 8 m1
- 62: 11 m1
- 63: 9 m1, 11 m2, 14 m1
- 64: 4 m2, 6 m2
- 65: 1 m3, 22 m1
- 66: 2 m1, 18 m2, 19 m3
