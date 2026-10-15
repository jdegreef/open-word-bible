# Ezra to Job: recurring terms and book-wide choices

**Status: proposed, awaiting the founder's approval.** Ezra, Nehemiah, Esther
and Job were drafted chapter by chapter in parallel from one brief, and these
are the choices that keep them consistent with each other and with the books
before them. If a choice changes, every chapter drafted under it is revised.
Read with `docs/english-style.md`, which wins where the two differ, and with
`docs/numbers-ruth-terms.md`, whose table (YHWH, *'eved*, *sar*, *chesed*,
units and the rest) still applies.

## Ezra and Nehemiah

| Hebrew / Aramaic | Literal | Balanced | Readable |
|---|---|---|---|
| bene X in the lists (Ezra 2, Neh 7, 10–12) | [the] sons of X | the descendants of X (a place name: the people of X) | same as Balanced |
| bene haggolah, haggolah | [the] sons of the exile / the exile | the returned exiles / the exiles | the people who came back from exile |
| netinim | the Nethinim | the temple servants | the temple servants |
| bene 'avde shelomoh | [the] sons of [the] slaves of Solomon | the descendants of Solomon's servants | same as Balanced |
| tirshata' | the Tirshatha | the governor | the governor |
| pechah | governor | governor | governor |
| 'avar naharah / 'avar nahara' | Beyond the River | Beyond the River (the province) | the province west of the Euphrates |
| 'elah shemayya', 'elohe hashamayim | the God of heaven | the God of heaven | the God of heaven |
| beit 'elaha' / beit ha'elohim | [the] house of God | the house of God | God's temple (or the temple of God) |
| sofer (Ezra) | the scribe | the scribe | the teacher of the law (decision at Ezra 7:6) |
| torah | law | law | teaching / law (as Deuteronomy) |
| nashim nokhriyyot | foreign women | foreign wives | foreign wives |
| 'am ha'arets / 'amme ha'aratsot | [the] people(s) of the land(s) | the peoples of the land(s) | the people living in the land (decision at Ezra 3:3, 4:4) |
| zera' haqqodesh (Ezra 9:2) | the holy seed | the holy race | God's holy people (decision) |
| "Remember me, my God, for good" (Neh 5:19; 13:14, 22, 31) | Remember for me, my God, for good | Remember me, my God, for good | My God, remember me and be good to me |
| horim, seganim (Neh 2:16 and later) | nobles, officials | nobles and officials | leaders and officials |

- **Aramaic.** Ezra 4:8–6:18 and 7:12–26 are Aramaic; `build_skeleton.py`
  marks those records `arc`. The first record of each Aramaic section (4:8,
  7:12) has a meaning decision saying the text changes to Aramaic, the
  language of the Persian empire's letters, and the record after each ends
  (6:19, 7:27) says it returns to Hebrew. Ezra 4:7 ends with "written in
  Aramaic and translated" (or "in Aramaic script and Aramaic language"), with a
  decision.
- **Persian kings.** Cyrus, Darius, Artaxerxes, Ahasuerus (Ezra 4:6) as the
  data spells them; a culture decision names the king the first time in a book
  where it matters (Ezra 4:6–7, 7:1; Nehemiah 1:1, 2:1).
- **Money and weights.** Literal keeps the unit. Balanced and Readable use a
  `units` span: darics *'adarkonim* / *darkemonim* stay "darics" at every level
  (a gold Persian coin) with a culture decision the first time in a chapter;
  mina *maneh* `{{units:about 1 1/4 pounds|a mina}}`, talent
  `{{units:about 75 pounds|a talent}}`, kor `{{units:about 6 bushels|a kor}}`,
  bath `{{units:about 6 gallons|a bath}}`. Multiply out for the totals
  (5,000 minas: about 3 tons).
- **Lists.** The lists of returnees, builders and signatories keep every name
  as the Hebrew gives it, in the English spelling of the BSB/WEB form the data's
  gloss uses. Numbers above ninety-nine are numerals (2,172). A list verse may
  have only one or two decisions; do not pad them.
- **Versification (Nehemiah).** Hebrew 3:33–38 is English 4:1–6 and Hebrew
  4:1–17 is English 4:7–23; Hebrew 10:1 is English 9:38 and Hebrew 10:2–40 is
  English 10:1–39 (`data/versification.json`). The Hebrew has no line for the
  horses and mules of Ezra 2:66, so Hebrew 7:68–72 is English 7:69–73. A
  footnoted decision at 3:33, 4:1, 7:68, 10:1 and 10:2 says so, and the book is
  cited by the Hebrew numbers.
- **Nehemiah 8:8** *meforash*: "clearly" or "with interpretation"; an
  uncertain, footnoted meaning decision names both (and translating into
  Aramaic as a third).
- The first-person memoir (Ezra 7:27–9:15; Nehemiah 1–7, 12:31–13:31) keeps
  "I" at every level.

## Esther

- **No divine name.** Esther never names God. Do not add him at any level.
  4:14 ("from another place") has a footnoted meaning decision that many
  readers see God's hidden help here, while the text does not say so.
- *'Achashverosh*: "Ahasuerus" at every level; a footnoted culture decision at
  1:1 says he is the Persian king known in Greek as Xerxes (486–465 BC).
- *Shushan habbirah*: "Susa the citadel" (Literal), "the citadel of Susa"
  (Balanced), "the royal fortress in Susa" (Readable); the city alone is
  "Susa".
- *Saris*: "eunuch" at Literal and Balanced; Readable "official" or "palace
  official", with a word_sense decision at 1:10 (the word can mean a court
  officer; in the harem and the king's bedchamber it means a castrated
  servant).
- *Dat* (a royal law or edict): "law" / "decree" as context needs;
  "the laws of Persia and Media, which cannot be revoked" (1:19).
- *Hayyehudim*: "the Jews"; *yehudi* (2:5): "a Jew" / "a Judean" with a
  decision.
- Haman "the Agagite": a meaning decision at 3:1 on the link with Agag king of
  Amalek (1 Samuel 15), marked as a reading the text invites, not states.
- *Pur* / Purim: "Pur (that is, the lot)" as the Hebrew explains it (3:7; 9:24).
- *Achashdarpenim*: "satraps" at Literal and Balanced, "regional governors" at
  Readable.
- *'Ets* for Haman's gallows (5:14; 6:4; 7:9–10; 9:13, 25): "gallows" at
  Balanced and Readable, with an uncertain, footnoted decision that the word is
  "tree" or "pole" and the death may be impaling or hanging up the body.
- *Chesed* between people (2:9, 17) is a superior's goodwill: "kindness" /
  "favor", not "faithful love", with a word_sense decision.
- 3:9 "ten thousand talents of silver":
  `{{units:about 375 tons of silver|ten thousand talents of silver}}`.
- Dates: "in the twelfth month, which is the month Adar" at Literal and
  Balanced; Readable may add the season with a decision.

## Job

- **Prose and poetry.** 1:1–2:13 and 42:7–17 are prose. 3:1–42:6 is poetry:
  set every poetic verse in lines with `\q` at Literal and Balanced (and at
  Readable where it keeps the cola), following `docs/english-style.md`
  section 10 and `scripts/poetry_lines.py`. The speech introductions ("And Job
  answered and said:" 3:1–2, 4:1, 6:1, 8:1, ...; 32:1–6 prose; 38:1; 40:1, 3,
  6; 42:1) stay prose, with no `\q`. Their wording is fixed: Literal "And Job
  answered and said:", Balanced "Then Job answered:", Readable "Then Job
  said:", with the speaker's full name ("Eliphaz the Temanite") at every
  level. 27:1 and 29:1 ("took up his discourse") and 36:1 ("continued") follow
  their own verbs.
- No quotation marks around the speeches; words quoted inside a speech take
  them.
- *Hassatan* (1:6–12; 2:1–7): Literal "the satan", Balanced and Readable "the
  Accuser". A footnoted meaning decision at 1:6 says the word has the article,
  so it is a title, "the adversary" or "the accuser", one who opposes in a
  court; later tradition names him Satan. Other chapters refer to 1:6.
- *Bene ha'elohim* (1:6; 2:1; 38:7): "the sons of God" at Literal and Balanced,
  "the heavenly beings" at Readable, with a meaning decision at 1:6.
- *Barekh* as a euphemism (1:5, 11; 2:5, 9): the verb is "bless" but means
  "curse". Every level says "curse"; the gloss keeps "bless"; a footnoted
  idiom decision at 1:5 explains it (the scribes would not write "curse God").
  1:21 and 42:12 are real blessing.
- Names of God: *YHWH* `{{divine_name:the LORD|Yahweh}}` (prologue, epilogue,
  12:9, 38:1, 40:1, 3, 6; 42:1, 7–12); *'Eloah* and *'El* "God"; *Shaddai*
  "the Almighty" (Readable "God All-Powerful"); *'Adonai* "the Lord".
- *Tam veyashar*: "blameless and upright" (Readable "honest and did what was
  right" may be avoided: keep "blameless" at every level, it is the book's
  theme word, with a decision at 1:1).
- *Sheol*: "Sheol" (Literal, Balanced), "the grave" (Readable). *'Avaddon*:
  "Abaddon" (Literal, Balanced), "the place of destruction" (Readable).
- *Livyatan*, *behemot*, *Rahav*: "Leviathan", "Behemoth", "Rahab" at every
  level, with a meaning decision the first time (3:8; 9:13; 40:15; 40:25) on
  what is known (a sea monster of the old poems; a great land beast; the sea
  monster of chaos, not Rahab of Jericho).
- *Go'el* (19:25): "Redeemer" at Literal and Balanced; Readable "the one who
  will defend me (my Redeemer)". 19:25–27 has uncertain, footnoted meaning
  decisions: who the go'el is (God, or a heavenly defender), and whether Job
  sees God "in" or "without" his flesh.
- **Hard verses.** Job has more rare words and difficult lines than any other
  book. Where the Hebrew is uncertain, translate the most likely sense, mark
  the decision `uncertain` and `footnote`, and give the alternative. Known
  cases include 13:15 (written "not", read "to him": "I have no hope" /
  "I will hope in him"), 19:25–27, 28 (the wisdom poem), 36:33, 42:6 ("I
  despise myself" / "I retract", "repent in dust and ashes" / "am comforted
  concerning dust and ashes").
- *Ruach*: "wind", "breath" or "spirit" as the line needs, with a decision
  where the choice changes the sense (4:15; 32:8; 33:4).
- The friends: Eliphaz the Temanite, Bildad the Shuhite, Zophar the
  Naamathite, Elihu son of Barachel the Buzite. Job's address to God uses
  "you"/"your" with `deity_pronoun` spans.
- *Yir'at 'Adonai* (28:28) and *yere' 'elohim* (1:1): "the fear of the Lord",
  "feared God"; Readable "honored God" or "respected God" with a decision.
- **Versification.** Hebrew 40:25–32 is English 41:1–8, and Hebrew 41:1–26 is
  English 41:9–34 (`data/versification.json`). A footnoted decision at 40:25
  and 41:1 says so, and the book is cited by the Hebrew numbers.
