# Isaiah, Jeremiah and Ezra in French, Spanish, Swahili, Vietnamese and Korean

**Status: proposed, awaiting native reviewers.** These are the choices used to
draft Isaiah, Jeremiah and Ezra in five languages at once, so that chapter
blocks drafted in parallel read as one translation in each language. They
continue the earlier five-language notes, which hold here and are not
repeated: `docs/samuel-five-languages-terms.md` and
`docs/kings-chronicles-five-languages-terms.md` (names of the kings, prophets
and peoples, the regnal and messenger formulas, address forms), and the notes
they list (Pentateuch, Genesis, Psalms). The English choices are in
`docs/isaiah-terms.md`, `docs/jeremiah-lamentations-terms.md` and
`docs/ezra-job-terms.md`.

If a choice here changes, every passage drafted under it is revised.
Decision text stays in English, quoting the words of the language.

## All five languages

- Translate from the Hebrew (and the Aramaic of Ezra 4:8–6:18 and 7:12–26),
  using the literal gloss, the English and the meaning decisions; never from
  a reference Bible. Isaiah 6, 7:14, 9:5–6, 40, 52:13–53:12, 61 and Jeremiah
  31 pull hardest: draft from the gloss and rewrite any line that matches a
  well-known version for more than a short common phrase.
- **Lines follow the English record**: most of Isaiah and much of Jeremiah is
  set in `\q` lines; where an English level has them, the language's same
  level has them, following the Hebrew's division. Narrative chapters
  (Isaiah 6–8, 20, 36–39; most of Jeremiah 26–45; all of Ezra) are prose.
- **Speech**: in the oracles the prophet's words and God's first-person speech
  take no quotation marks, and "Thus says the LORD" is followed by a colon, as
  the English does; speech quoted inside an oracle takes the language's
  quotation marks. Narrative chapters quote speech as prose does.
- **Parallels — reuse the language's existing wording where the Hebrew is the
  same, and change only what the Hebrew changes:**
  - Isaiah 36:1–39:8 is 2 Kings 18:13–20:19 (drafted in all five).
  - Jeremiah 52 is 2 Kings 24:18–25:30; Jeremiah 39:1–10 overlaps 2 Kings 25.
  - Ezra 1:1–3a is 2 Chronicles 36:22–23.
  - Ezra 2 is Nehemiah 7 (not drafted yet: draft it here; Nehemiah will reuse
    it).
  - Ezra 3:11 is the temple refrain of Psalm 136 (published).
- **New Testament quotations**: Isaiah is quoted often (7:14; 9:1–2; 40:3–5;
  42:1–4; 53; 61:1–2 and others) and Jeremiah 31:31–34 in Hebrews 8. The
  New Testament quotes mostly from the Greek; do not copy its wording, but
  keep the same key terms (servant, the Spirit of the Lord, the new covenant)
  so a reader can see the quotation, and where the English records point to
  the New Testament, read the language's published verse.
- **Settings**: `divine_name` on every YHWH ("the Lord GOD" as in the earlier
  notes); `deity_pronoun` where the English has one and the language has a
  free pronoun (the servant, the king of 9:5 and 11:1, Cyrus and the speaker
  of 61:1 take none, as in English); `units` where the English converts;
  Spanish `plural_you` for every plural "you" (frequent in the oracles to
  Israel); `gender` only where the language really has two wordings.
- Rendering decisions: zero to two per sentence, only where the language had
  to choose. A book-wide choice is recorded once per block of chapters.

## Terms and names each language settles

Each language section below gives its wording, at L / B / R where they
differ, for:

- **Formulas**: declares the LORD (*neʾum YHWH*); thus says the LORD; the
  word of the LORD came to me, saying; woe (*hoy*); in that day; oracle
  (*massa*); hear the word of the LORD; the LORD of hosts; the Holy One of
  Israel; the Mighty One of Jacob; Redeemer (*goʾel*, of God); I am he
  (*ʾani hu*).
- **Isaiah**: daughter Zion / daughter Babylon; remnant (*sheʾar*); the
  servant of the LORD; coastlands (*iyyim*); righteousness (*tsedeq,
  tsedaqah*); salvation; glory; Sheol; the shades (*rephaim*); bearer of good
  news (*mebasser*); signal flag (*nes*); ships of Tarshish; the young woman
  (7:14); Immanuel; Wonderful Counselor, Mighty God (9:5); the Branch;
  shining one (14:12); the new heavens and the new earth.
- **Jeremiah**: falsehood (*sheqer*); return / turn back (*shuv*, of repentance
  and of exile); rising early and speaking; the sword, famine and plague;
  the potter; the yoke; the seventy years; the new covenant (31:31); the
  Chaldeans; the king of Babylon; the Rechabites; the scroll.
- **Ezra**: the God of heaven; the house of God in Jerusalem; the returned
  exiles (*bene haggolah*); the temple servants (*netinim*); the sons of
  Solomon's servants; the scribe skilled in the law of Moses; the hand of the
  LORD his God was on him; foreign wives; the Aramaic letters' formulas
  ("to Artaxerxes the king, your servants ..."), and the Persian titles.
- **Names**: Isaiah son of Amoz, Shear-jashub, Maher-shalal-hash-baz,
  Immanuel, Rabshakeh, Merodach-baladan, Cyrus, Bel and Nebo, Moab, Edom,
  Kedar, Dumah, Tyre, Sidon, Elam, Kittim; Jeremiah son of Hilkiah, Anathoth,
  Baruch son of Neriah, Pashhur, Hananiah son of Azzur, Shemaiah, Gedaliah son
  of Ahikam, Ishmael son of Nethaniah, Johanan son of Kareah, Ebed-melech the
  Cushite, Nebuzaradan, Tahpanhes, Pharaoh Hophra, Jehoiakim, Zedekiah,
  Jeconiah / Coniah; Ezra, Zerubbabel, Jeshua son of Jozadak, Sheshbazzar,
  Darius, Artaxerxes, Ahasuerus, Tattenai, Shethar-bozenai, Rehum, Shimshai,
  Haggai, Zechariah son of Iddo, Shecaniah, Persia, the river Ahava.
  Published forms win (the New Testament, the earlier books).


## French

`docs/french-style.md` and the French rules of the Samuel and Kings notes hold. SEIGNEUR is always `{{divine_name:le
SEIGNEUR|Yahvé}}` (`du SEIGNEUR|de Yahvé`, `au SEIGNEUR|à Yahvé`); the Lord GOD is `le Seigneur
{{divine_name:DIEU|Yahvé}}`, the vocative `{{divine_name:SEIGNEUR|Yahvé}}` without article.

**Tenses.**
- Narrative (Isaiah 6–8, 20, 36–39; Jeremiah 26–45, 52; all of Ezra): passé simple at L and B, passé composé at R,
  imparfait for repeated action. First-person narrative (Isaiah 6 and 8; Jeremiah 1, 13, 18, 32; Ezra 7:27–9:15) too:
  « je vis » at L and B, « j’ai vu » at R, as Revelation.
- Oracles are speech: present, future, and passé composé for the past at every level, never passé simple (as the
  Psalms and the speeches of Acts). The prophetic perfect follows the English level: « Babylone est tombée » where it
  keeps a past, the future where it turns it into one. Jeremiah's laments, Ezra's prayer (9:6–15) and the Aramaic
  letters count as speech.
- « tu » or « vous » follows the Hebrew's number (Zion « tu », the people « vous »); the Persian king is « tu » (« tes
  serviteurs »), as Samuel.

**Formulas.**
- *neʾum YHWH*: « déclare le SEIGNEUR » (L, B), « dit le SEIGNEUR » (R), as 2 Kings 19:33, 22:19; with Adonai
  « déclare le Seigneur DIEU ».
- Thus says the LORD: « Ainsi parle le SEIGNEUR : » (L), « Le SEIGNEUR dit ceci : » (B), « Voici ce que dit le
  SEIGNEUR : » (R), as 2 Kings 19:6, 20:1. In a narrative frame: « Ainsi me parla le SEIGNEUR » / « Le SEIGNEUR me dit
  ceci » / « Voici ce que le SEIGNEUR m’a dit ».
- The word of the LORD came to me, saying: « La parole du SEIGNEUR me fut adressée, disant : » (L), « La parole du
  SEIGNEUR me fut adressée : » (B), « Le SEIGNEUR m’a donné ce message : » (R), as Kings' « fut adressée à X ».
  Jeremiah's headings: « La parole qui fut adressée à Jérémie de la part du SEIGNEUR, disant : » / « Ce message fut
  adressé à Jérémie par le SEIGNEUR : » / « Voici le message que le SEIGNEUR a donné à Jérémie : ».
- *hoy*: « Malheur, … » (L), « Malheur à … » (B), « Quel malheur pour … ! » (R, as Matthew 23:13); « Malheur à moi » /
  « Quel malheur pour moi ! » said of oneself; « Hélas » (L, B), « Quelle tristesse » (R) in Jeremiah's funeral cries
  (22:18; 34:5); « Ah » in a plea.
- In that day: « en ce jour-là » (L), « ce jour-là » (B), « en ce temps-là » or « ce jour-là » (R). Hear the word of
  the LORD: « Écoutez la parole du SEIGNEUR » (L, B), « Écoutez le message du SEIGNEUR » (R).
- *massa* (title): « Oracle [concernant] Babylone » (L), « Oracle sur Babylone » (B), « Message au sujet de Babylone »
  (R) (« oracle » as 2 Kings 9:25); Jeremiah 23:33–40 « fardeau » at every level, for the wordplay.
- « le SEIGNEUR des armées » at every level (Samuel, Psalms, 2 Kings 19:31); « le Saint d’Israël » at every level (2
  Kings 19:22; Psalm 78:41); « le Puissant de Jacob / d’Israël » (L, B, as Psalm 132:2), « le Dieu puissant de Jacob »
  (R).
- *goʾel* of God: « Rédempteur » (L, as Proverbs 23:11), « Libérateur » (B, as Psalm 19:15), « celui qui te délivre »
  or « ton Libérateur » (R), capitalised as a title; the verb « racheter ».
- *ʾani hu*: « c’est {{deity_pronoun:moi|Moi}} » (L, B: « que c’est moi »), « moi seul, je suis Dieu » (R, decision).

**Isaiah.**
- Daughter Zion: « la fille de Sion » (L, B, as 2 Kings 19:21), « le peuple de Sion » (R); daughter Babylon « fille de
  Babylone » (L, B), « peuple de Babylone » (R), as Psalm 137:8; « la vierge, la fille de Sion » (37:22).
- Remnant: « le reste » (L, B, as Romans 9:27; 2 Kings 19:31), « ceux qui resteront », « les survivants » (R).
- Servant: « serviteur » at every level (Matthew 12:18 « Voici mon serviteur »); no `deity_pronoun` on the servant,
  the king of 9:5 and 11:1, Cyrus or the speaker of 61:1.
- Coastlands: « les îles » (L), « les îles lointaines » (B), « les pays lointains » (R), as Psalm 97:1 and 72:10.
- *tsedeq*, *tsedaqah*: « la justice » (Psalm 98:2); paired with *mishpat*, « le droit et la justice ». Where the
  English has a word_sense decision (vindication, victory), « victoire », « délivrance ». *Mishpat* in 42:1–4 is « la
  justice », as Matthew 12:18–20.
- Salvation « le salut » (L, B), « sauver » freely at R; glory « la gloire » at every level; Sheol « le Shéol » (L),
  « le séjour des morts » (B, R), as the Psalms and Proverbs; the shades « les ombres » (L), « les morts » (B, R), as
  Proverbs 9:18.
- *mebasser*: « porteuse de bonne nouvelle » (40:9), « celui qui annonce la bonne nouvelle » (52:7) (L, as Romans
  10:15); « messager de bonnes nouvelles » (B), « messager qui apporte une bonne nouvelle » (R).
- *nes*: « un étendard » (L, B), « un drapeau » (R). Ships of Tarshish: « navires de Tarsis » (L, B), « grands navires
  de commerce » (R), as 1 Kings 10:22.
- 7:14: « la jeune femme » (L, B), « une jeune femme » (R), with the English meaning decision and its footnote citing
  Matthew 1:23 « la vierge »; « elle l’appellera Emmanuel »; R adds « ce qui veut dire “Dieu est avec nous” », as
  Matthew 1:23 R.
- 9:5: L « Merveille de conseiller, Dieu puissant, Père d’éternité, Prince de paix »; B « Celui qui conçoit des
  merveilles, Dieu le Guerrier puissant, Père pour toujours, Chef de la paix »; R the same names, « Chef qui apporte
  la paix ». 10:21 « le Dieu puissant » (L, B), as the English.
- The Branch (*tsemach*, Jeremiah 23:5; 33:15): « un Germe juste » at every level (R adds « un roi de sa famille »);
  Isaiah 4:2 « le germe du SEIGNEUR » lowercase; 11:1 « un rameau … de la souche de Jessé, un rejeton ».
- 14:12: « astre brillant, fils de l’aurore » (L, B), « brillante étoile du matin » (R); the footnote names
  « Lucifer ». New heavens and new earth: « de nouveaux cieux et une nouvelle terre » (L, B), « un nouveau ciel et une
  nouvelle terre » (R), as 2 Peter 3:13.
- New Testament echoes keep the published key words: 40:3 « Préparez le chemin du SEIGNEUR » (Matthew 3:3); 42:3
  « roseau broyé », « mèche qui fume » (L), « roseau plié », « mèche qui brûle à peine » (B) (Matthew 12:20); 49:6
  « lumière des nations … jusqu’à l’extrémité de la terre » (Acts 13:47); 53:1 « qui a cru à notre message ? » (Romans
  10:16); 53:4 « il a porté nos maladies » (Matthew 8:17); 53:7 « comme une brebis … comme un agneau muet devant celui
  qui le tond » (Acts 8:32); 61:1–2 « l’Esprit du Seigneur DIEU est sur moi », « la bonne nouvelle aux pauvres »,
  « l’année de la faveur du SEIGNEUR » (Luke 4:18–19).

**Jeremiah.**
- *sheqer*: « le mensonge » (L, B), « des mensonges », « ce qui est faux » (R).
- *shuv*: « revenir » at every level, for repentance and return from exile alike, to keep the wordplay (« Reviens,
  Israël infidèle », 3:12); R may say « revenir à moi », « changer de conduite » where the English R loosens it.
- Rising early and speaking: « me levant de bonne heure et parlant » (L), « sans relâche » (B), « encore et encore »
  (R). Sword, famine and plague: « l’épée, la famine et la peste » (L, B), « la guerre, la famine et la maladie » (R).
- The potter « le potier »; his house « la maison du potier » (L, B), « l’atelier du potier » (R). The yoke « le
  joug »; straps and yoke bars « des courroies et des barres de joug ».
- Seventy years « soixante-dix ans » (never « septante »). The scroll « un rouleau de livre » (L), « un rouleau » (B,
  R). The Rechabites « les Rékabites » (« Rékab », 2 Kings 10:15).
- New covenant (31:31): « une alliance nouvelle » at every level, as Hebrews 8:8; 31:31–34 keeps Hebrews 8's key words
  (« la maison d’Israël et la maison de Juda », « je serai leur Dieu, et ils seront mon peuple », « du plus petit
  jusqu’au plus grand »). God's *torah* as the Psalms: « ma loi » (L), « mon instruction » (B), « mon enseignement »
  (R). « Voici, des jours viennent » (L), « Des jours viennent » (B), « Un temps vient » (R). 31:15 keeps « Rama …
  Rachel pleure ses enfants » (Matthew 2:18).
- The Chaldeans « les Chaldéens » (L, B), « les Babyloniens » (R), as 2 Kings 25; the king of Babylon « le roi de
  Babylone ».

**Ezra.**
- The God of heaven « le Dieu des cieux » (L, B), « le Dieu du ciel » (R), as 2 Chronicles 36:23. The house of God in
  Jerusalem « la maison de Dieu [qui est] à Jérusalem » (L, B), « le temple de Dieu à Jérusalem » (R).
- *bene haggolah*: « les fils de l’exil » (L), « les exilés revenus » (B), « les gens revenus de l’exil » (R);
  *haggolah* alone « l’exil », « les exilés ». *Netinim*: « les Nethinim » (L), « les serviteurs du temple » (B, R).
  « les fils des esclaves de Salomon » (L), « les descendants des serviteurs de Salomon » (B, R).
- The scribe skilled in the law of Moses: « un scribe expert dans la Loi de Moïse » (L, B), « un spécialiste de la
  Loi » (R, as the New Testament's scribes). The hand of the LORD his God was on him: « selon la main du SEIGNEUR son
  Dieu sur lui » (L), « car la main du SEIGNEUR son Dieu était sur lui » (B), « le SEIGNEUR son Dieu l’aidait » (R).
  Foreign wives: « des femmes étrangères » (L), « des épouses étrangères » (B, R).
- Letters: « À Artaxerxès, le roi, tes serviteurs, les hommes d’Au-delà du Fleuve » (L); « Au roi Artaxerxès, de la
  part de tes serviteurs … » (B, R); « paix » / « toute paix » (L), « Salut » (B), « Nous te souhaitons paix et
  prospérité » (R); « Qu’il soit connu du roi » (L), « Que le roi sache » (B), « Nous voulons que tu saches, ô roi »
  (R); « roi des rois ».
- Titles: Beyond the River « Au-delà du Fleuve » (L), « la province d’Au-delà du Fleuve » (B), « la province à l’ouest
  de l’Euphrate » (R); governor « le gouverneur »; Tirshatha « le Tirshatha » (L), « le gouverneur » (B, R); satraps
  « les satrapes » (L, B), « les gouverneurs des régions » (R); Rehum « le commandant » (L), « le haut fonctionnaire »
  (B, R); Shimshai « le scribe » (L, B), « le secrétaire » (R); darics « dariques », as 1 Chronicles 29:7.
- Ezra 1:1–3a reuses 2 Chronicles 36:22–23 and 3:11 Psalm 136 (« car {{deity_pronoun:il|Il}} est bon, car
  {{deity_pronoun:son|Son}} amour fidèle dure toujours », B).

**Names.** Isaïe fils d’Amots (Matthew 3:3; 2 Kings 19:2), Shear-Yashouv, Maher-Shalal-Hash-Baz, Emmanuel (Matthew
1:23), le Rabshaqé (L) / le grand échanson (B, R), as 2 Kings 18:17, Merodak-Baladân fils de Baladân (39:1; 2 Kings
20:12 has Berodak-), Cyrus, Bel et Nebo, Moab, Édom, Kédar, Douma, Tyr, Sidon, Élam, les Kittim (L, B) / Chypre (R);
Jérémie fils de Hilqiya, Anatoth (1 Chronicles 6:45), Baruch fils de Nériya, Pashhour fils d’Immer (1 Chronicles
9:12), Hanania fils d’Azzour, Shemaya le Néhélamite, Guedalia fils d’Ahiqam, Ismaël fils de Netania, Yohanân fils de
Qaréah (2 Kings 25:22–25), Ébed-Mélek le Koushite (2 Chronicles 14:8), Nebouzaradân, Tahpanhès, le pharaon Hophra,
Joïaqim, Sédécias, Joïakin, Jéchonias / Conia (each verse's form, as the English), Shalloum, Nabuchodonosor at every
level for both Hebrew spellings (one decision at the first « Nebuchadrezzar »); Esdras (the book's French name),
Zorobabel fils de Salathiel (Matthew 1:12), Yeshoua fils de Yotsadaq (1 Chronicles 5:40 has Yehotsadaq), Sheshbatsar,
Darius, Artaxerxès, Assuérus, Tattenaï, Shethar-Boznaï, Rehoum, Shimshaï, Aggée, Zacharie fils d’Iddo, Shekania (1
Chronicles 3:21), la Perse, le canal d’Ahava (B, R; « la rivière qui va vers Ahava » L).

**For a reviewer.** `data/books.json` names Isaiah « Ésaïe », while every published French verse says « Isaïe »; one
of them should change.

## Spanish

Published forms win; evidence in brackets. Where one form is given it holds at L, B and R.

**Address, speech and settings**
- One person is always *tú*: God, the king, Cyrus, Zion and Babylon spoken to as women, the prophet. Never *usted*. "Your Majesty" at R is *mi rey* / *oh rey*, as in Samuel.
- Every plural "you", whether pronoun, verb or possessive, is a `{{plural_you:ustedes form|vosotros form}}` span, Latin American by default. This applies throughout the oracles to Israel, Judah and the nations: `{{plural_you:Escuchen|Escuchad}}`, `{{plural_you:su Dios|vuestro Dios}}`, `{{plural_you:les|os}}`. Where *su* with *ustedes* could be misread, the span takes in the noun [Matthew 21:5 R; John 12:15 R; 2 Chronicles 36:23 R]. Isaiah 7:13–14 is plural ("all of you"): `{{plural_you:les|os}} dará una señal`.
- Quotation marks « », with “ ” inside them and ‘ ’ inside those. Oracles take none: *Así dice el SEÑOR:* is followed by a colon, and speech quoted inside an oracle takes « ».
- `divine_name` takes in the article: `{{divine_name:el SEÑOR|Yahvé}}`, `del SEÑOR|de Yahvé`, `al SEÑOR|a Yahvé`. Adonai YHWH is *el Señor* `{{divine_name:DIOS|Yahvé}}`. YHWH addressed directly is `{{divine_name:SEÑOR|Yahvé}}` with no "oh" [Psalm 19:15].
- `deity_pronoun` goes on God's free *mí, me, mi, te, tú, ti, tu, él, lo, le, su*, wherever the English has it. God's *yo* takes none. The servant, the king of 9:5 and 11:1, Cyrus and the speaker of 61:1 take no span, even though Matthew 12:18–21, Acts 8:32–33 and Luke 4:18 span Jesus.
- No `gender` span where *hijos* or *hermanos* already includes women (Jeremiah 3:14, 22, where the English has a span: *hijos infieles*).
- Units follow the Pentateuch values: mina 0.6 kg, talent 34 kg, bath 22 litres, cor 220 litres. Darics are *dáricos* at every level. Write thousands with a space (2 172).
- Narration is in the preterite. Israel and Judah personified as sisters agree in the feminine (*la infiel Israel*, *su hermana, la traidora Judá*, Jeremiah 3).

**Formulas**
- Declares the LORD (*neʾum YHWH*): L *declara el SEÑOR*, B *afirma el SEÑOR*, R *dice el SEÑOR*, always after a comma [1 Samuel 2:30 L; 2 Kings 22:19 B; 2 Chronicles 34:27]. In Isaiah 37:34 and 39:6, keep the wording of 2 Kings 19:33 and 20:17 (*dice*) wherever the Hebrew is the same.
- Thus says the LORD: L *Así dice el SEÑOR:*, B *El SEÑOR dice esto:*, R *Esto es lo que dice el SEÑOR:* [Kings–Chronicles note; Joshua 24:2; 2 Kings 9:3].
- The word of the LORD came to me, saying: L *Vino a mí la palabra del SEÑOR, diciendo:* [1 Chronicles 22:8 L], B *La palabra del SEÑOR vino a mí:* [1 Kings 17:2 B], R *El SEÑOR me dio este mensaje:* [1 Chronicles 22:8 R]. The headings of Jeremiah: L *La palabra que vino a Jeremías de parte del SEÑOR, diciendo:*, B *Este mensaje vino a Jeremías de parte del SEÑOR:*, R *Este es el mensaje que el SEÑOR le dio a Jeremías:*.
- Woe (*hoy*): L and B *¡Ay de ...!*, R *¡Qué terrible será para ...!* [Matthew 23:13]. Said of oneself: *¡Ay de mí!* (L, B), *¡Qué terrible es esto para mí!* (R). In a funeral cry: *¡Ay, hermano mío!* at every level [1 Kings 13:30; Jeremiah 22:18]. In a plea (47:6): *¡Ay!* (L, B), *¡Oh!* (R).
- In that day: L *en aquel día*, B *aquel día*, R *en ese tiempo* / *ese día* [as published from Joshua to Chronicles].
- Oracle (*massa*): L and B *Oráculo sobre X* / *Oráculo de X*, R *Este es un mensaje sobre X* [Proverbs 30:1; 2 Kings 9:25 R]. In Jeremiah 23:33–40 it is *carga* at every level, for the wordplay.
- Hear the word of the LORD: L *Oye* / `{{plural_you:Oigan|Oíd}}` *la palabra del SEÑOR*, B *Escucha* / `{{plural_you:Escuchen|Escuchad}}` *la palabra del SEÑOR*, R *Escucha(n) este mensaje del SEÑOR* [2 Kings 7:1; 20:16].
- The LORD of hosts: L *el SEÑOR de los ejércitos*, B and R *el SEÑOR de los Ejércitos* [Samuel note; Psalms 24:10; 46:8]. Adonai YHWH of hosts is *el Señor DIOS de los ejércitos / Ejércitos*.
- The Holy One of Israel: *el Santo de Israel* [2 Kings 19:22, also at R; Psalm 71:22].
- The Mighty One of Jacob: *el Poderoso de Jacob* [Genesis 49:24; Psalm 132:2, 5]. "The Mighty One of Israel" (1:24) is *el Poderoso de Israel*.
- Redeemer (*goʾel*, of God): *Redentor*, capitalized as a title (L, B) [Psalm 19:15; Proverbs 23:11 L]. At R it is *tu Redentor* or *el que te rescata*, where the English R explains [Psalm 19:15 R]. The verb is *redimir* (L, B), *rescatar* (R).
- I am he (*ʾani hu*, 43:10 and later): L *yo [soy]* `{{deity_pronoun:él|Él}}`, B *que yo soy* with a decision citing John 8:24, 28 and 13:19 (*que yo soy*), R *solo yo soy Dios*.
- Others: *Santo, santo, santo* (6:3, as Revelation 4:8); *Vive el SEÑOR* / *tan cierto como que yo vivo* (B, R) [Samuel note].

**Isaiah**
- Daughter Zion: L and B *la hija de Sion* [Psalm 9:15 L; Matthew 21:5; John 12:15], R *el pueblo de Sion* / *la gente de Jerusalén* [Matthew 21:5 R]. Daughter Babylon: L and B *hija de Babilonia*, R *pueblo de Babilonia* [Psalm 137:8].
- Remnant (*sheʾar*): L and B *el remanente*, R *los que queden* / *un remanente, los que queden* [Romans 9:27; 11:5].
- The servant of the LORD: *siervo* at every level, lowercase [Matthew 12:18; Samuel note]. Court officials are *siervos* (L), *funcionarios* / *oficiales* (B, R).
- Coastlands (*iyyim*): L *las costas*, B *las costas lejanas*, R *las tierras lejanas* / *las islas y costas lejanas* [Psalms 72:10; 97:1].
- Righteousness (*tsedeq, tsedaqah*): *justicia*, with *rectitud* for the parallel word [Psalms 72:1; 85:11; 98:2; Matthew 12:18]. Where the English decision reads justice / vindication / victory: *justicia*, *reivindicación*, *victoria*. At R it is *lo que es justo* where the English R explains.
- Salvation: *salvación* (L, B); verbs at R as the English (*cómo él salva*) [Psalm 98:2–3; Luke 3:6].
- Glory: *gloria*. *Hesed*: *amor leal* (L), *amor fiel* (B, R) [Psalms]. *Torah*: *instrucción* (L, B), *enseñanza* (R) [Psalms note].
- Sheol: L *el Seol*, B and R *el lugar de los muertos*. The English B keeps "Sheol", but the published Spanish B does not [Pentateuch and Psalms notes; Proverbs 9:18].
- The shades (*rephaim*): L *las sombras*, B and R *los muertos* [Psalm 88:11; Proverbs 9:18].
- Bearer of good news (*mebasser*, 52:7): L *el que anuncia buenas noticias*, B *el que trae la buena noticia*, R *el mensajero con buenas noticias* [Romans 10:15]. The feminine of 40:9 is L *Sion, que anuncias buenas noticias*, B *Sion, tú que traes la buena noticia*, R *pueblo de Sion, tienes buenas noticias que contar*. In 61:1–2: *el Espíritu del Señor DIOS*, *me ha ungido*, *anunciar buenas noticias*, *libertad a los cautivos*, *el año favorable del SEÑOR* [Luke 4:18–19 L, B].
- Signal flag (*nes*): *bandera* at every level, *alzar una bandera* [Psalm 60:6]. *Estandarte* stays the word of the name in Exodus 17:15.
- Ships of Tarshish: L and B *naves de Tarsis*, R *grandes barcos mercantes* [1 Kings 10:22; 22:49]. Wail (*helilu*): L and B *Giman*, R *Lloren de dolor*, each with `plural_you`.
- The young woman (7:14): *la joven* (L, B), *una joven* (R), never *la virgen*. A decision cites Matthew 1:23 (*la virgen*, from the Greek).
- Immanuel: *Emanuel*. At R add *que significa «Dios está con nosotros»* [Matthew 1:23].
- 9:5:
  - L *Consejero Maravilla, Dios Poderoso, Padre de Eternidad, Príncipe de Paz*.
  - B *Autor de planes maravillosos, Dios Guerrero Poderoso, Padre para siempre, Gobernante de paz*.
  - R *... Padre para siempre y Gobernante que trae la paz*.
  - Rewrite anything that drifts toward RV or NVI (*Admirable Consejero, Dios fuerte, Padre eterno*).
- The Branch: lowercase *el retoño del SEÑOR* (4:2). In 11:1, *un brote* (shoot) and *un retoño* (branch). The title in Jeremiah 23:5 and 33:15 is capitalized: L *un Retoño de justicia* (33:15), *un Retoño justo*; R *un Retoño justo, un rey de su familia*.
- Shining one (14:12): L *resplandeciente, hijo de la aurora*, B *astro resplandeciente, hijo de la Aurora*, R *brillante estrella de la mañana*. "Lucifer" goes in the footnote only.
- The new heavens and the new earth: L and B *cielos nuevos y una tierra nueva* [2 Peter 3:13 B], R *un cielo nuevo y una tierra nueva* [Revelation 21:1].
- Kittim: *Quitim* (L, B) [Genesis 10:4], *Chipre* (R). The Chaldeans: *los caldeos* (L, B), *los babilonios* (R) [2 Kings 25:4–5].

**Jeremiah**
- Falsehood (*sheqer*): *mentira*, *profetizan mentira(s)*, *palabras engañosas* (7:4, 8). "Swear falsely" is *jurar en falso*. At R: *mienten*.
- Return / turn back (*shuv*): *volver* / *volverse* for repentance, as Matthew 13:15 *se volverían*, never *arrepentirse*. *Regresar* / *volver* for the exiles. "Return, faithless Israel": L and B *Vuelve, infiel Israel*, R *Regresa, Israel infiel*. "Restore the fortunes": L and B *restaurar la suerte* [Psalm 14:7 L], R *hacer que todo vuelva a ir bien* [Psalm 126:4 R].
- Rising early and speaking: L *madrugando y hablando*, B and R *una y otra vez*.
- Sword, famine and plague: L and B *la espada, el hambre y la peste*, R *la guerra, el hambre y las enfermedades* [2 Chronicles 20:9].
- The potter: *el alfarero*, *la casa del alfarero* (L, B), *el taller del alfarero* (R).
- The yoke: *el yugo*. In 27:2 it is *correas y barras de yugo*.
- The seventy years: *setenta años* [2 Chronicles 36:21].
- The new covenant (31:31): L and B *un pacto nuevo con la casa de Israel y con la casa de Judá* [Hebrews 8:8], R *un pacto nuevo con el pueblo de Israel y el pueblo de Judá*. In 31:33–34, *pondré mi ley ... la escribiré en su corazón* and *nunca más me acordaré de su pecado*. Keep the key terms of Hebrews 8:10–12 without copying its Greek-based wording.
- The king of Babylon: *el rey de Babilonia*.
- The Rechabites: *los recabitas*, *Jonadab hijo de Recab* [2 Kings 10:15].
- The scroll: *el rollo* [Luke 4:17]. L *un rollo de libro* (36:2).
- Also:
  - *la reina del cielo*; *los baales*; *el Tofet, en el valle de Ben-hinom* [2 Kings 23:10].
  - *eunuco* (L), *funcionario* (B, R) [Kings note].
  - *guarida de bandidos* (7:11, as Matthew 21:13).
  - *Ramá ... Raquel llora por sus hijos* (31:15) [Matthew 2:18].
  - *quien se gloríe, que se gloríe en ...* (9:23) [1 Corinthians 1:31].

**Ezra**
- The God of heaven: *el Dios de los cielos* [2 Chronicles 36:23]. *Rey de reyes* (7:12) [Revelation 19:16].
- The house of God in Jerusalem: L and B *la casa de Dios que está en Jerusalén*, R *el templo de Dios en Jerusalén*.
- The returned exiles (*bene haggolah*): L *los hijos del destierro* / *el destierro*, B *los que habían vuelto del destierro*, R *los que regresaron del destierro* [*destierro* 24× in Kings and Chronicles]. In the lists, *bene X* is *los hijos de X* (L) and *los descendientes de X* (B, R); for a place, *los de X*.
- The temple servants (*netinim*): L *los netineos*, B and R *los servidores del templo* [1 Chronicles 9:2].
- The sons of Solomon's servants: L *los hijos de los esclavos de Salomón*, B and R *los descendientes de los siervos de Salomón*.
- The scribe skilled in the law of Moses: L *escriba experto en la ley de Moisés*, B *escriba muy versado en la ley de Moisés*, R *maestro de la ley* [NT note, scribes at R].
- The hand of the LORD his God was on him: L *conforme a la mano del SEÑOR su Dios sobre él*, B *porque la mano del SEÑOR su Dios estaba sobre él*, R *el SEÑOR su Dios lo ayudaba*.
- Foreign wives: L *mujeres extranjeras*, B and R *esposas extranjeras* [1 Kings 11:1, 8].
- The Aramaic letters:
  - The address: L *A Artajerjes el rey, tus siervos, los hombres de Más Allá del Río, y ahora:*; B *Al rey Artajerjes, de parte de tus siervos, los hombres de la provincia de Más Allá del Río. Y ahora:*; R *... de la provincia al oeste del Éufrates*.
  - *Sepa el rey* (L), *Que el rey sepa* (B), *Queremos informar al rey* (R).
  - The greeting: *paz completa* (L), *Saludos* (B, R).
  - Plural orders take `plural_you` (4:21; 6:6–7; 7:21, 24).
- The Persian titles:
  - *tirshata*: *el Tirsata* (L), *el gobernador* (B, R); *pechah* is *gobernador*.
  - *los sátrapas* (L, B), *gobernadores regionales* (R).
  - *el tesorero*; *decreto*; *los pueblos de la tierra* (L, B), *la gente que vivía en el país* (R).
- The refrain of 3:11: L *porque es bueno, porque su amor leal [es] para siempre*, B and R *porque él es bueno; su amor fiel dura para siempre* [Psalm 136:1].
- Ezra 1:1–3a reuses 2 Chronicles 36:22–23 word for word.

**Names** (Spanish forms; published ones marked †)
- Isaiah:
  - *Isaías hijo de Amoz*† [2 Kings 19:2], *Sear-jasub*, *Maher-salal-has-baz*, *Emanuel*†.
  - Rabshakeh: *el Rabsaces* (L)†, *el copero mayor* (B, R)† [2 Kings 18:17].
  - *Merodac-baladán hijo de Baladán* (39:1; 2 Kings 20:12† has *Berodac-*, as its Hebrew does).
  - *Ciro*†, *Bel y Nebo*, *Moab*†, *Edom*†, *Cedar*†, *Dumá*† [Genesis 25:14], *Tiro*†, *Sidón*†, *Elam*†, *Quitim*†.
- Jeremiah:
  - *Jeremías hijo de Hilcías*† [Matthew 2:17; 2 Kings 22:12], *Anatot*†, *Baruc hijo de Nerías*.
  - *Pasur hijo de Imer*† [1 Chronicles 9:12], *Hananías hijo de Azur*, *Semaías el nehelamita*.
  - *Gedalías hijo de Ahicam*†, *Ismael hijo de Netanías*†, *Johanán hijo de Carea*† [2 Kings 25:22–23].
  - *Ebed-melec el cusita* [*cusita* published], *Nabuzaradán*† [2 Kings 25:8], *Tafnes*, *el faraón Hofra*.
  - *Joacim*†, *Sedequías*†, *Jeconías*† [Matthew 1:11–12], *Conías*, *Joaquín*† [2 Kings 25:27], *Salum*†.
  - *Nabucodonosor*†. Where the Hebrew has the -r- form, it is *Nabucodorosor* at every level, with a decision, as the English does.
- Ezra:
  - *Esdras*, *Zorobabel*† [1 Chronicles 3:19], *Jesúa hijo de Josadac*† [2 Chronicles 31:15; 1 Chronicles 5:40], *Sesbasar*.
  - *Darío*, *Artajerjes*, *Asuero*.
  - *Tatenai*, *Setar-boznai*, *Rehúm el comandante*, *Simsai el escriba*.
  - *el profeta Hageo*, *Zacarías hijo de Ido*† [2 Chronicles 9:29], *Secanías*† [1 Chronicles 3:21].
  - *Persia*†, *el río Ahava* (L), *el canal que corre hacia Ahava* (B, R).

## Swahili

BWANA for YHWH is always `{{divine_name:BWANA|Yahwe}}`; "the Lord GOD" is
Bwana `{{divine_name:MUNGU|Yahwe}}`. One wording at every level unless L / B
/ R are given. Narrative uses *-li-* then *-ka-*. Published forms win (cited).

**Formulas**
- *neʾum YHWH*: *asema BWANA* (L, B); *anasema BWANA* (R) — 2 Kings 19:33.
- Thus says the LORD: *BWANA asema hivi:* (L); *Hivi ndivyo BWANA asemavyo:*
  (B); *Hili ndilo BWANA analosema:* (R) — 2 Kings 19:6, 1 Chronicles 17:4.
  Isaiah 36–39 keeps the 2 Kings wording, R variants included (19:20; 20:17).
- The word of the LORD came to me, saying: *Neno la BWANA likanijia, kusema:*
  (L; 1 Chronicles 22:8); *Neno la BWANA likanijia:* (B); *BWANA alinipa
  ujumbe huu:* (R). Headings: *Neno lililomjia Yeremia kutoka kwa BWANA,
  kusema:* / *Ujumbe huu ulimjia Yeremia kutoka kwa BWANA:* / *Huu ndio ujumbe
  ambao BWANA alimpa Yeremia:*
- *hoy*: *Ole, ...* (L); *Ole wao ...* (B); *Itakuwa vibaya sana kwa ...* (R),
  as Luke 6:24. Of oneself *Ole wangu* (L, B; 1 Kings 13:30), *Mambo ni mabaya
  sana kwangu* (R); funeral cry *Ole!* (L, B), *Inasikitisha!* (R).
- In that day: *katika siku ile* (L); *siku hiyo* (B); *wakati huo* (R).
- *massa*: *Unabii [juu ya] X* (L); *Unabii kuhusu X* (B); *Ujumbe kuhusu X*
  (R); Jeremiah 23:33–40 *mzigo* at every level, for the wordplay.
- Hear the word of the LORD: *Sikieni neno la BWANA* (L); *Sikilizeni neno la
  BWANA* (B); *Sikilizeni ujumbe huu kutoka kwa BWANA* (R) — 2 Kings 20:16.
- *BWANA wa majeshi* at every level (Samuel, Psalms; never *Sabaoth*).
- *Mtakatifu wa Israeli* (2 Kings 19:22; Psalm 71:22; R may add *Mungu*).
- *Mwenye Nguvu wa Yakobo* (Genesis 49:24; Psalm 132:2; R *Mungu Mwenye Nguvu
  wa Yakobo*); Isaiah 1:24 *Mwenye Nguvu wa Israeli*.
- Redeemer: *Mkombozi* (*Mkombozi wako*; Proverbs 23:11), R also *anayekuokoa*;
  the verb *kukomboa* (L, B), *kununua tena* where the English R says "bought
  back".
- *ʾani hu*: *Mimi ndiye* (L, B; span on *mimi* mid-sentence, none on
  *ndiye*); R *Mimi peke yangu ndiye Mungu*. Not John's *Mimi niko* (13:19).
- Vocative: *Ee BWANA*, as the published Psalms (19:15).

**Isaiah**
- Daughter Zion: *binti Sayuni* (L), *Binti Sayuni* (B), *watu wa Sayuni* (R)
  — 2 Kings 19:21; daughter Babylon likewise with *Babeli* (Psalm 137:8 R
  *watu wa Babeli*). Jeremiah's *bat-ʿammi*: *binti wa watu wangu* (L), *watu
  wangu wapendwa* (B), *watu wangu* (R).
- Remnant: *mabaki* (L, B; Romans 9:27; 2 Kings 19:31); *watu waliobaki* (R).
- Servant: *mtumishi wa BWANA*, *mtumishi wangu* at every level (Matthew
  12:18), never *mtumwa*; no deity span on the servant, though Matthew has one.
- *iyyim*: *visiwa* (L), *pwani za mbali* (B), *nchi za mbali ng'ambo ya
  bahari* (R) — Psalm 97:1; 72:10 R.
- *tsedeq*, *tsedaqah*: *haki* (John table), *ushindi* or *kuthibitishwa* where
  the English has victory or vindication. *mishpat*: *hukumu* (L), *haki* (B,
  R); *haki* at every level in 42:1–4, as Matthew 12:18–20.
- Salvation *wokovu* (R may use *kuokoa*); glory *utukufu*.
- Sheol *Kuzimu* at every level (Psalms note; Proverbs 9:18). Shades: *vivuli
  vya wafu* (L), *wafu* (B, R) — Psalm 88:11.
- *mebasser*: *anayeleta habari njema* (L, B); *mjumbe mwenye habari njema*
  (R) — Romans 10:15.
- *nes*: *bendera* (Psalm 60:6).
- Ships of Tarshish: *merikebu za Tarshishi* (L, B; Psalm 48:8); *meli kubwa
  za biashara* (R).
- 7:14: *msichana*, every level, with an uncertain decision naming *mwanamwali*
  and Matthew 1:23's *bikira* (from the Greek). *Imanueli* (Matthew 1:23); R
  adds *maana yake "Mungu yuko pamoja nasi"*.
- 9:5, as the English levels: L *Mshauri-Ajabu, Mungu Shujaa, Baba wa Milele,
  Mkuu wa Amani*; B *Mpangaji wa Maajabu, Mungu Shujaa Mwenye Nguvu, Baba wa
  Nyakati Zote, Mtawala wa Amani*; R the same with *Baba wa Milele, Mtawala
  Aletaye Amani*. This keeps clear of the Union Version's four names.
- Branch: *Chipukizi* as a title (Jeremiah 23:5; 33:15 *Chipukizi la haki*);
  *chipukizi la BWANA* (Isaiah 4:2); 11:1 *chipukizi* and *tawi*; 11:10 *shina
  la Yese*, near Romans 15:12 *mzizi wa Yese*.
- 14:12: *wewe ung'aaye, mwana wa alfajiri* (L, B); *ulikuwa kama nyota ya
  asubuhi inayong'aa* (R; Revelation 2:28). Never *Lusifa*.
- *mbingu mpya na nchi mpya* (Revelation 21:1).
- New Testament key terms: 61:1 *Roho wa Bwana MUNGU [yuko] juu yangu*,
  *amenipaka mafuta*, *habari njema*, *mwaka wa kibali* (Luke 4:18–19; no
  span on the speaker); 53:7 *kondoo*, *mwana-kondoo* (Acts 8:32); 53:1
  *habari yetu*, *mkono wa BWANA* (John 12:38); 40:3 *nyikani*, *njia ya
  BWANA* (Matthew 3:3).

**Jeremiah**
- *sheqer*: *uongo*. *shuv*: *kurudi*, *kunirudia* of repentance and *kurudi*
  from exile at every level.
- Rising early and speaking: *nikiamka mapema na kusema* (L); *tena na tena*
  (B); *mara nyingi sana* (R).
- *upanga, njaa na tauni* (L, B; 2 Samuel 24:13); *vita, njaa na magonjwa* (R).
- *mfinyanzi*; *nira* (1 Kings 12:4); *miaka sabini* (2 Chronicles 36:21).
- 31:31–34: *agano jipya*, *nyumba ya Israeli na nyumba ya Yuda*, *Mjue BWANA*,
  *tangu aliye mdogo hadi aliye mkubwa* (Hebrews 8:8–12). *torah* is *sheria*
  (L), *mafundisho* (B, R) as the Psalms note, but *sheria* at L and B in
  31:33 (Hebrews 8:10).
- Chaldeans: *Wakaldayo* (L, B), *Wababeli* (R) — 2 Chronicles 36:17. *mfalme
  wa Babeli*.
- *Warekabu* (*nyumba ya* L, *ukoo wa* B, R). Scroll: *gombo* (Luke 4:17).

**Ezra**
- *Mungu wa mbinguni* (2 Chronicles 36:23). The house of God in Jerusalem:
  *nyumba ya Mungu iliyoko Yerusalemu* (L, B); *hekalu la Mungu* (R).
- *bene haggolah*: *wana wa uhamisho* (L); *waliorudi kutoka uhamishoni* (B,
  R). *netinim*: *Wanethinimu* (L); *watumishi wa hekalu* (B, R; 1 Chronicles
  9:2). *wana wa watumwa wa Sulemani* (L); *wazao wa watumishi wa Sulemani*
  (B, R).
- 7:6: *mwandishi stadi katika sheria ya Musa* (L); *mwandishi aliyebobea
  katika sheria ya Musa* (B); *mwalimu wa sheria* (R; Matthew 2:4 R). The hand
  of the LORD: *mkono wa BWANA Mungu wake juu yake* (L; 2 Kings 3:15), *...
  ulikuwa juu yake* (B), *BWANA Mungu wake alikuwa akimsaidia* (R).
- Foreign wives: *wanawake wageni* (L; Proverbs 22:14); *wake wageni* (B, R).
- Letters: *Kwa Artashasta mfalme: watumishi wako, watu wa Ng'ambo ya Mto, na
  sasa:* (L); *Kwa Mfalme Artashasta, kutoka kwa watumishi wako, watu wa jimbo
  la Ng'ambo ya Mto. Basi sasa:* (B); R *jimbo lililo magharibi ya mto Frati*.
  *Amani* (L), *Salamu* (B, R); *Ijulikane kwa mfalme* (L, B), *Mfalme na
  ajue* (R). *Ng'ambo ya Mto* as Joshua 24:3.
- Titles: *mfalme wa wafalme*; *mkuu wa amri* (L), *afisa mkuu* (B, R);
  *mwandishi* (L, B), *katibu* (R); governor *liwali* (2 Kings 18:24);
  *Tirshatha* (L), *liwali* (B, R); satraps *maliwali wakuu* (L, B),
  *watawala wa majimbo* (R); *mtunza hazina*; *darkoni* (1 Chronicles 29:7),
  *mane*, *kori*.

**Names**
- *Isaya mwana wa Amozi*, *Shear-yashubu*, *Maher-shalal-hash-bazi*,
  *Imanueli*, *Rabshake*, *Merodaki-baladani* (2 Kings 20:12 keeps
  *Berodaki-*), *Koreshi*, *Beli*, *Nebo*, *Moabu*, *Edomu*, *Kedari*, *Duma*,
  *Tiro*, *Sidoni*, *Elamu*, *Kitimu* (R *Kipro*, as Acts).
- *Yeremia mwana wa Hilkia*, *Anathothi*, *Baruku mwana wa Neria*, *Pashuri*,
  *Hanania mwana wa Azuri*, *Shemaya*, *Gedalia mwana wa Ahikamu*, *Ishmaeli
  mwana wa Nethania*, *Yohana mwana wa Karea* (2 Kings 25:23; a decision says
  he is not John), *Ebed-meleki Mkushi*, *Nebuzaradani*, *Tahpanhesi*, *Farao
  Hofra*, *Yehoyakimu*, *Sedekia*, *Yekonia* / *Konia* (each verse's form).
- *Ezra*, *Zerubabeli*, *Yeshua mwana wa Yosadaki* (1 Chronicles 5:40 has the
  long *Yehosadaki*), *Sheshbaza*, *Dario*, *Artashasta*, *Ahasuero*,
  *Tatenai*, *Shethar-bozenai*, *Rehumu*, *Shimshai*, *Hagai*, *Zekaria mwana
  wa Ido* (Old Testament *Zekaria*, not Matthew 23:35's *Zakaria*), *Shekania*,
  *Uajemi*; *mto unaoelekea Ahava* (L), *mfereji unaoelekea Ahava* (B, R).

## Vietnamese

Every CHÚA below is `{{divine_name:CHÚA|Gia-vê}}`, with particles outside the span; "Lord GOD" is *Chúa là CHÚA* (Samuel, Psalms). Where the forms differ by level they are given as L / B / R; otherwise one form serves all three. Evidence is the published Vietnamese verse that is cited. The narration is plain, as in Kings, and Isaiah 36–39 and Jeremiah 52 reuse the 2 Kings wording.

**Address**
- **God speaking** says *Ta*, spanned (`{{deity_pronoun:ta|Ta}}`) in mid-sentence. To one person he says *ngươi* (L) and *con* (B, R), as he does to Hezekiah in 2 Kings 19:20; 20:5. This covers Isaiah, Jeremiah (1:5–19), the king, and Israel, Jacob or Zion addressed as one person (Isaiah 41:8–14; 43:1; 49:14–26; 54). To the people as a group he says *các ngươi* at every level, as in 2 Kings 17:13. *Các con* is used only where the Hebrew calls them children (Isaiah 1:2; Jeremiah 3:14, 22), at B and R. Foreign kings, nations and cities, including Cyrus, Babylon, Assyria and Tyre, are *ngươi* at every level (2 Kings 19:21–28).
- **The prophet and the people praying**: they call God *Ngài* (spanned) or *Chúa*, and say *lạy CHÚA* to him, with no "O" (Psalm 19:15; 2 Kings 19:15). The prophet calls himself *con*, and the people say *chúng con*. "Ah, Lord GOD" (Jeremiah 1:6; 4:10; 32:17) is *Ôi, lạy Chúa là CHÚA*. In Isaiah 63:16 and 64:7 God is *Cha* and they are *chúng con*. In Ezra 9:6–15, Ezra prays as *con* and *chúng con*, saying *Đức Chúa Trời của con*.
- **The prophet speaking to the people**: *các người* in rebuke, *anh em* where he pleads (Jeremiah 26; 42), and *tôi* for himself. The prophet and the king follow Kings: the prophet calls the king *vua* and himself *tôi*; the king says *ông* to the prophet and *ta* for himself (Zedekiah and Jeremiah, 37–38).
- **God's servants are *đầy tớ* at every level, Literal included, and never *nô lệ*.** This holds for the servant of the LORD, "my servant Jacob", the prophets, Nebuchadnezzar "my servant" (Jeremiah 25:9; 27:6; 43:10), and "your servant" in prayer (Kings rule; 2 Samuel 7:5; Matthew 12:18). *Nô lệ* is kept only for slavery itself (Jeremiah 34:8–22). Psalm 89:4 and 89:21 R, which had *người phục vụ Ta*, now follow it.
- **Who takes a deity_pronoun span**: the servant in Isaiah (*người*, lowercase), the king of 9:5 and 11:1, Cyrus and the speaker of 61:1 (*tôi*) take none. Matthew 12:18–21 and Acts 8:32–33 span *Người* and *Ngài* only because the New Testament applies those words to Jesus. Do not copy those spans into Isaiah.

**Formulas**
- *neʾum YHWH*: *CHÚA phán vậy* (L, B) / *CHÚA phán* (R), as 2 Kings 9:26; *Chúa là CHÚA phán vậy* for *neʾum Adonai YHWH*.
- Thus says the LORD: *CHÚA phán thế này:* / *CHÚA phán như vầy:* / *Đây là lời CHÚA phán:* (Samuel note; 2 Kings 19:6, 20; 20:1).
- The word of the LORD came to me, saying: *Lời CHÚA đến với tôi rằng:* / *Lời CHÚA đến với tôi:* / *CHÚA ban cho tôi sứ điệp này:* (the Kings form is *lời CHÚA đến với X*).
- The word that came to Jeremiah from the LORD: *Lời từ CHÚA đến với Giê-rê-mi rằng:* / *Sứ điệp này từ CHÚA đến với Giê-rê-mi:* / *Đây là sứ điệp CHÚA ban cho Giê-rê-mi:*.
- *hoy*:
  - As a threat: *Khốn cho ...* (L, B) / *Thật khốn khổ cho ...* (R), as Matthew 11:21 and 23:13.
  - Said of oneself (Isaiah 6:5): *Khốn cho tôi* / *Khốn cho tôi* / *Thật khốn khổ cho tôi*.
  - As a funeral cry (Jeremiah 22:18; 34:5): *Than ôi* (L, B) / *Thật đáng buồn* (R).
  - As a plea (Jeremiah 47:6): *Ôi*.
- In that day: *trong ngày ấy* / *vào ngày ấy* / *vào lúc ấy* (or *vào ngày ấy*).
- *massa*: *sấm ngôn* (L, B) / *sứ điệp* (R), as 2 Kings 9:25. In Jeremiah 23:33–40 it is *gánh nặng* at every level, to keep the wordplay.
- Hear the word of the LORD: *Hãy nghe lời của CHÚA* / *Hãy nghe lời CHÚA* / *Hãy nghe điều CHÚA phán* (2 Kings 20:16; 1 Kings 22:19).
- The LORD of hosts: *CHÚA Vạn Quân*, with the span on *CHÚA* only, at every level (2 Kings 19:31; Samuel; Psalms).
- The Holy One of Israel: *Đấng Thánh của Y-sơ-ra-ên* (2 Kings 19:22; Psalm 78:41).
- The Mighty One of Jacob: *Đấng Quyền Năng của Gia-cốp* (Genesis 49:24; Psalm 132:2). Isaiah 1:24 is *Đấng Quyền Năng của Y-sơ-ra-ên*.
- Redeemer (*goʾel*, of God):
  - The title is *Đấng Cứu Chuộc*, capitalised as a title (Proverbs 23:11; compare Psalm 19:15).
  - At R it may be *Đấng giải cứu* with a decision, as Psalm 19:15 R does.
  - The verb is *cứu chuộc* (L, B) / *chuộc lại, giải cứu* (R).
- *ʾani hu*: *Ta [là] Đấng ấy* / *chính Ta là Đấng ấy* / *chỉ một mình Ta là Đức Chúa Trời* (an R decision). The main decision at 43:10 cites John's *Ta là [Đấng Hằng Hữu]*. Mark it uncertain.

**Isaiah**
- Daughter Zion: *con gái Si-ôn* (L, B) / *dân Si-ôn* (R), as 2 Kings 19:21. Daughter Babylon follows the same pattern: *con gái Ba-by-lôn* / *dân Ba-by-lôn*, as Psalm 137:8.
- Remnant (*sheʾar*): *những người sót lại* or *số người sót lại* (L, B) / *những người còn sống sót* (R), as 2 Kings 19:4, 31 and Romans 9:27 (*phần dân sót lại*).
- The servant of the LORD: *đầy tớ của CHÚA*, and *đầy tớ Ta* (Matthew 12:18), at every level.
- Coastlands (*iyyim*): *các hải đảo* (L, B) / *những miền xa bên kia biển* (R), as Psalm 72:10 and 97:1.
- Righteousness (*tsedeq*, *tsedaqah*):
  - *sự công chính* (L, B) / *điều công chính* (R), as Romans and Genesis 15:6.
  - Where the English has "justice": *công lý* (Matthew 12:18, 20).
  - "Vindication" or "victory" takes a decision.
- Salvation: *sự cứu rỗi* (L, B) / *sự giải cứu* or the verb *cứu* (R), as Psalm 98:3 and Luke 3:6.
- Glory: *vinh quang* at every level.
- Sheol: *Âm Phủ* (L, B) / *nơi của người chết* (R), as Psalm 139:8 and Proverbs 9:18.
- The shades (*rephaim*): *vong linh* (L) / *người chết* (B, R), as Psalm 88:11. Proverbs 9:18 L has *âm hồn*; a reviewer should pick one of the two.
- Bearer of good news (*mebasser*): *người đem tin lành*, lowercase (L, B) / *người đưa tin vui* (R), as Romans 10:15. It is not *Tin Lành*, the gospel.
- Signal flag (*nes*): *cờ hiệu* at every level.
- Ships of Tarshish: *tàu Ta-rê-si* (L, B) / *những tàu buôn lớn* (R), as 1 Kings 10:22. Psalm 48:8 L and B wrongly span *{{deity_pronoun:ta|Ta}}-rê-si*: fix it, and never span the *Ta* of *Ta-rê-si*.
- The young woman (7:14): *người thiếu nữ* (L, B) / *một thiếu nữ* (R). *Thiếu nữ* is the published form for this word in Proverbs 30:19. The decision cites Matthew 1:23's *trinh nữ*, which comes from the Greek.
- Immanuel: *Em-ma-nu-ên* (Matthew 1:23), with the meaning given as *Đức Chúa Trời ở cùng chúng ta*. In 8:8 and 8:10 the name and the phrase stay apart, as the English keeps them.
- 9:5, the throne names: *Đấng Cố Vấn Kỳ Diệu, Đức Chúa Trời Quyền Năng, Cha Đời Đời, Hoàng Tử Bình An*. R may say *Vua mang lại bình an*. Mark these uncertain.
- The Branch: *Chồi của CHÚA* (4:2, *tsemach*) and *một chồi* (11:1, *netser*). Jeremiah 23:5 and 33:15 are *Chồi công chính*.
- Shining one (14:12): *hỡi kẻ sáng chói, con của rạng đông* (L) / *hỡi ngôi sao sáng, con của bình minh* (B, R). The footnote names *sao mai* and "Lucifer".
- New heavens and new earth: *trời mới và đất mới* (2 Peter 3:13; Revelation 21:1).
- 61:1, the Spirit: *Thần Linh của Chúa là CHÚA* (as 2 Samuel 23:2 and Psalm 139:7). A decision cites Luke 4:18's *Thánh Linh của Chúa*, and 42:1 does the same with Matthew 12:18.

**Jeremiah**
- Falsehood (*sheqer*): *sự giả dối* or *lời giả dối* (L, B) / *điều dối trá* (R). Prophesying falsehood is *nói tiên tri giả dối*.
- Return / turn back (*shuv*):
  - Repentance is *quay về*, *trở lại cùng Ta* (L, B) / *ăn năn quay về* (R).
  - Coming home from exile is *trở về*.
  - Jeremiah 3's *mashuvah* is *bội nghịch*, with a decision on the wordplay.
- Rising early and speaking: *dậy sớm mà nói* / *hết lần này đến lần khác* / *nhiều lần*.
- Sword, famine, plague: *gươm, nạn đói và ôn dịch* / *gươm đao, nạn đói và dịch bệnh* / *chiến tranh, nạn đói và bệnh tật*.
- The potter: *thợ gốm* (Romans 9:21).
- The yoke: *cái ách* (1 Kings 12:4).
- The seventy years: *bảy mươi năm* (2 Chronicles 36:21).
- The new covenant:
  - *giao ước mới với nhà Y-sơ-ra-ên và nhà Giu-đa* (L, B) / *với dân Y-sơ-ra-ên và dân Giu-đa* (R), as Hebrews 8:8.
  - 31:33 keeps Hebrews 8:10's terms: *Ta sẽ là Đức Chúa Trời của họ, và họ sẽ là dân của Ta*.
  - Hebrews has *Chúa phán*; Jeremiah has *CHÚA phán vậy*.
- The Chaldeans: *người Canh-đê* (L, B) / *người Ba-by-lôn* (R), as 2 Kings 25 and 2 Chronicles 36:17.
- The king of Babylon: *vua Ba-by-lôn*.
- The Rechabites: *người nhà Rê-cáp* (1 Chronicles 2:55).
- The scroll: *cuộn sách* (Luke 4:17).

**Ezra**
- The God of heaven: *Đức Chúa Trời trên trời* at every level, as 2 Chronicles 36:23, which is Ezra 1:2. Psalm 136:26 L and Jonah 1:9 L, which had *các tầng trời*, now follow it.
- The house of God in Jerusalem: *nhà của Đức Chúa Trời tại Giê-ru-sa-lem* (L, B) / *đền thờ của Đức Chúa Trời* (R), as Kings' *nhà của CHÚA* / *đền thờ*.
- The returned exiles (*bene haggolah*): *con cái của [những người] lưu đày* / *những người lưu đày trở về* / *những người từ chốn lưu đày trở về*.
- The temple servants (*netinim*): *người Nê-thi-nim* (L, as the English L) / *những người phục dịch đền thờ* (B, R), as 1 Chronicles 9:2 and its decision.
- The sons of Solomon's servants: *con cháu các đầy tớ của Sa-lô-môn* at every level; the English L "slaves" is not followed.
- The scribe skilled in the law of Moses: *thầy thông giáo thông thạo luật pháp Môi-se* (L, B) / *thầy dạy luật pháp, người hiểu rõ luật pháp Môi-se* (R). This follows the Gospels' scribes, with a decision at 7:6. Never use *thư ký*, which is the royal secretary.
- The hand of the LORD his God was on him: *tay của CHÚA Đức Chúa Trời ông ở trên ông* / *bàn tay của CHÚA Đức Chúa Trời ông ở cùng ông* / *CHÚA Đức Chúa Trời của ông giúp đỡ ông*. "The good hand" is *bàn tay nhân từ*.
- Foreign wives: *những người nữ ngoại bang* / *những người vợ ngoại bang* / *vợ người nước ngoài*.
- The Aramaic letters:
  - Opening (L): *Gửi vua Ạt-ta-xét-xe, các đầy tớ của vua, những người ở bên kia Sông ...*
  - Opening (B): *Kính tâu vua Ạt-ta-xét-xe ...*
  - Opening (R): *chúng tôi*, as Samuel's R *tôi*.
  - "Be it known to the king": *Xin vua biết rằng* / *Chúng tôi xin tâu để vua biết* / *Chúng tôi muốn vua biết*.
  - The king replies with *ta* and *các ngươi*. "King of kings" is *vua của các vua*.
  - The records (4:15) are *sách ghi chép* or *sách biên niên*, and never *Sử Ký*.
- Persian titles:
  - Governor (*pechah*): *tổng đốc*, as 2 Kings 25:22 B.
  - *Tirshatha*: *quan Tiệt-sa-tha* (L) / *quan tổng đốc* (B, R).
  - Satraps: *các tổng trấn* (L, B) / *các quan cai trị các miền* (R).
  - Beyond the River: *bên kia Sông* (L, as Joshua 24:2) / *tỉnh Bên Kia Sông* (B) / *tỉnh phía tây sông Ơ-phơ-rát* (R).
- Ezra 3:11 is the Psalm 136:1 refrain, word for word at each level.

**Names** (✓ = already published)
- Isaiah's book and the nations:
  - *Ê-sai con trai A-mốt* ✓ (2 Kings 19:20; Matthew 3:3).
  - *Sê-a Gia-súp* and *Ma-he-Sa-la-Hát-Bát*, with their meanings given as the English level gives them.
  - *Em-ma-nu-ên* ✓.
  - *Ráp-sa-kê* (L) / *viên quan trưởng* (B) / *viên chỉ huy A-si-ri* (R), as 2 Kings 18–19 ✓.
  - *Mê-rô-đác Ba-la-đan*, with a decision: 2 Kings 20:12 has *Bê-rô-đác* ✓.
  - *Si-ru* ✓ (2 Chronicles 36:22); *thần Bên* and *thần Nê-bô* (*Nê-bô* ✓ 1 Chronicles 5:8).
  - *Mô-áp, Ê-đôm, Kê-đa, Đu-ma, Ty-rơ, Si-đôn, Ê-lam, Kít-tim* ✓. At R, Kittim is *đảo Chíp-rơ*, as in Acts.
- Jeremiah:
  - *Giê-rê-mi con trai Hinh-kia* ✓ (Matthew 2:17; 2 Chronicles 36:12) and *A-na-tốt* ✓.
  - *Ba-rúc con trai Nê-ri-gia*: new. Luke 3:27 has *Nê-ri*, but that is another name.
  - *Pha-su-rơ* ✓ (1 Chronicles 9:12).
  - *Ha-na-nia con trai A-xua* and *Sê-ma-gia* ✓ (the Nehelamite is *người Nê-hê-lam*).
  - *Ghê-đa-lia con trai A-hi-cam*, *Ích-ma-ên con trai Nê-tha-nia* and *Giô-ha-nan con trai Ca-rê-át* ✓ (2 Kings 25:22–23).
  - *Ê-bết-Mê-léc người Cút* (*người Cút* ✓) and *Nê-bu-xa-a-đan* ✓.
  - *Tác-pha-nết* and *Pha-ra-ôn Hốp-ra*: new.
  - *Giê-hô-gia-kim* ✓, *Sê-đê-kia* ✓, *Giê-chô-nia* ✓ (Matthew 1:11), *Cô-nia* (new, with a decision) and *Giê-hô-gia-kin* ✓.
  - Nebuchadnezzar is *Nê-bu-cát-nết-sa* ✓. Nebuchadrezzar is *Nê-bu-cát-rết-sa*, with a decision.
- Ezra:
  - *E-xơ-ra*, the book title in `data/books.json`. 1 Chronicles 4:17's *Ê-xơ-ra* is a different man (Ezrah); a reviewer should confirm the spelling.
  - *Xô-rô-ba-bên con trai Sa-la-thi-ên* ✓ (Matthew 1:12).
  - *Giê-sua* ✓ *con trai Giô-xa-đác*: Ezra's short form, with a decision, since 1 Chronicles 5:40 has *Giê-hô-xa-đác*.
  - *Sết-ba-xa, Đa-ri-út, Ạt-ta-xét-xe, A-suê-ru, Tát-tê-nai, Sê-ta-Bô-xê-nai, Rê-hum, Sim-sai*: new.
  - *A-ghê* (the book title ✓) and *Xa-cha-ri con trai Y-đô* ✓ (*Y-đô*, 2 Chronicles 9:29).
  - *Sê-ca-nia* ✓, *Ba Tư* ✓ (2 Chronicles 36:20) and *sông A-ha-va* (new).
- *Sử Ký* is only ever the title of Chronicles: no source book, record or letter in these books takes that name.

## Korean

`docs/korean-style.md` (7a), the Genesis note and the Korean columns of the Samuel, Psalms and Kings–Chronicles notes hold. Every form below was checked against published Korean; where they differed, the published form won (evidence in brackets).

**Speech levels and the name**
- Narration: plain written style in 했다 (not 하였다), with -시- and 께서 for God at every level. Ezra's memoir (7:27–9:15) keeps 나 in the plain style.
- **God speaks 해라체** with 나, 너, 너희, and **names himself without -시-**: {{divine_name:주|야훼}}가 말한다; 나 {{divine_name:주|야훼}}가; 이스라엘의 거룩한 이 [2 Kings 19:22 = Isa 37:23]; 하늘의 군대를 거느린 {{divine_name:주|야훼}} [2 Kings 19:31 R]. When the prophet or the people speak *about* God, they use -시-: 이스라엘의 거룩하신 분; {{divine_name:주|야훼}}께서 말씀하신다.
- **Prayers are 합쇼체** with 저/제 (communal 저희), addressing God as 주님 and in the vocative {{divine_name:주|야훼}}여 (no "O") [Ps 19:15]. This covers Isa 37:16–20 (= 2 Kings 19:15–19), 38:3, 63:7–64:11; Jeremiah's laments and 32:17–25; Ezra 9:6–15.
- **People and kings.** A prophet speaks to a king in 합쇼체, and God's words inside his message stay 해라체 [2 Kings 20:1 = Isa 38:1]. Kings speak 해라체 to prophets and subjects. Officials writing to the Persian king use 합쇼체 with 임금님 and 종들; the king's decrees and replies are 해라체.
- **No -시- for these figures:** the servant, the child of 9:5, the king of 11:1, Cyrus and the speaker of 61:1. They are 그 [Mt 12:18–21; Acts 8:32–33]. Korean has no deity_pronoun spans.
- **The divine name.** Every YHWH is `{{divine_name:주|야훼}}`, with the particle outside the span: 께서, 의, 가, 를, 께, 여. A bare 주 never stands for YHWH, and 여호와 is never used.
  - Adonai alone is 주님 (7:14 주님께서 친히).
  - Lord GOD is 주 `{{divine_name:하나님|야훼}}`; Lord GOD of hosts is 만군의 주 `{{divine_name:하나님|야훼}}` [Ps 69:7 B].
  - Yah is `{{divine_name:주|야}}`.
  - "I am the LORD" is 나는 {{divine_name:주|야훼}}다; the recognition formula is 내가 {{divine_name:주|야훼}}인 줄 알게 될 것이다 [1 Kings 20:13].
- Lines: `\q` wherever the English level has it, with Korean placing its own breaks. Oracles take no quotation marks; speech inside an oracle takes " ", with ' ' when nested.

**Formulas**
- *declares the LORD*: L {{divine_name:주|야훼}}의 선언이다; B, R {{divine_name:주|야훼}}가 말한다. It stands as its own sentence [1 Sam 2:30; 2 Kings 19:33 = Isa 37:34; 2 Kings 22:19; 2 Chr 34:27]. Hebrews 8:8–10 says 주님께서 말씀하신다 because there the author is quoting; Jeremiah keeps the oracle form.
- *Thus says the LORD*: L {{divine_name:주|야훼}}께서 이와 같이 말씀하신다; B 이렇게 말씀하신다; R {{divine_name:주|야훼}}께서 하시는 말씀이다 [2 Kings 19:6 = Isa 37:6]. Speaking to a king, the forms are 말씀하십니다 and 하시는 말씀입니다 [2 Kings 19:20; 20:1]. The formula ends in a period, not the English colon, as published.
- *the word of the LORD came to me, saying*: L {{divine_name:주|야훼}}의 말씀이 나에게 임하여 말씀하셨다 [1 Chr 22:8]; B ...나에게 임했다; R {{divine_name:주|야훼}}께서 나에게 이 말씀을 주셨다.
- *the word that came to Jeremiah from the LORD*: L {{divine_name:주|야훼}}께로부터 예레미야에게 임한 말씀; B 이것은 {{divine_name:주|야훼}}께서 예레미야에게 주신 말씀이다; R {{divine_name:주|야훼}}께서 예레미야에게 주신 말씀은 이러하다.
- **Dated headings** follow the Kings formula:
  - "in the Nth year of X": L 유다 왕 X의 제4년에; B X가 다스린 지 4년째 되는 해에; R X가 왕이 된 지 4년째 되는 해에.
  - "in the days of X": X의 시대에 (L), X가 다스리던 때에 (B), X가 왕이었을 때에 (R).
- **Woe (*hoy*)**: L, B ~에게 화가 있다; R ~에게 끔찍한 일이 닥칠 것이다 [Mt 23:13 L, R]. The B form of Matthew 23:13, 얼마나 불행하냐, is not used.
  - In a funeral cry (Jer 22:18; 34:5): 아, (L, B) and 슬프다 (R).
  - Of oneself (6:5): 내게 화가 있다 (L, B) [Ps 120:5]; 아, 나는 이제 끝났다 (R).
- *in that day*: 그날에 (L, B) [1 Sam 3:12]; 그때에 (R).
- *oracle (massa)*: 신탁 (L, B) [2 Kings 9:25; Prov 30:1 L]; ~에 관한 말씀 (R). In Jer 23:33–40 it is 짐 at every level, for the wordplay.
- *hear the word of the LORD*: {{divine_name:주|야훼}}의 말씀을 들어라 (L, B); {{divine_name:주|야훼}}께서 하시는 말씀을 들어라 (R). To a king, 들으십시오.
- *the LORD of hosts*: 만군의 {{divine_name:주|야훼}} (L, B); 하늘의 군대를 거느리신 {{divine_name:주|야훼}} (R). In God's own mouth the R form is 거느린. 6:5 is 만군의 주이신 왕 [Rom 9:29; 2 Kings 19:31].
- *the Holy One of Israel*: 이스라엘의 거룩하신 분 at every level [Ps 71:22]; 이스라엘의 거룩한 이 when God speaks.
- *the Mighty One of Jacob*: 야곱의 전능하신 분 (L, B); 야곱의 강하신 하나님 (R) [Ps 132:2]. When God names himself (49:26; 60:16): 전능한 이 / 강한 하나님. The Mighty One of Israel (1:24) is 이스라엘의 전능하신 분.
- **Redeemer (*goʾel*)**: 구속자 (L, B) [Ps 19:15; Prov 23:11]; 구해 주시는 분 (R), and 너를 구해 주는 이 in God's mouth.
  - The verb: 구속하다 (L, B); 값을 치르고 되찾다 (R).
  - Savior: 구원자.
- *I am he (ʾani hu)*: L 내가 그다; B 내가 바로 그다; R 나만이 하나님이다, with an R decision as in English. Uncertain. The decision at 43:10 may point to John 8:24, 28 (내가 나임을).

**Isaiah**
- **Daughters.** Daughter Zion is 딸 시온 (L, B) and 시온 백성 (R) [2 Kings 19:21 = Isa 37:22]. Daughter Babylon is 딸 바빌론 (L, B) [Ps 137:8] and 바빌론 사람들 (R).
- **Remnant.** 남은 자 (L), 남은 사람들 (B), 살아남은 사람들 (R) [Rom 9:27; 2 Kings 19:31]. The escaped: 피한 자 (L), 피한 사람들 (B).
- **Servant.** 종 at every level: 나의 종 (L), 내 종 (B, R) [Mt 12:18]. The servant of the LORD is {{divine_name:주|야훼}}의 종; never 노예. Court officials are 종들 (L) and 신하들 (B, R).
- **Coastlands.** 섬들 (L), 바닷가 나라들 (B), 먼 나라들 (R) [Ps 72:10; 97:1].
- **Righteousness.** *tsedeq* and *tsedaqah* are 의 (L, B) and 옳은 일 or 바른 일 (R). Where the English has a word_sense decision they become 정의, 승리 or 구원.
  - *mishpat* is 정의 [Mt 12:18, 20]; "justice and righteousness" is 정의와 의 (L, B) and 옳고 바른 일 (R).
- **Salvation, glory.** Salvation is 구원 (L, B) [Lk 3:6], with R free to say 구해 주시다. Glory is 영광 at every level [Jn 12:41].
- **The dead.** Sheol is 스올 (L, B) and 죽은 사람들이 있는 곳 (R) [Ps 139:8; Prov 9:18]. The shades (*rephaim*) are 망령들 (L) [Ps 88:11], 죽은 자들 (B) and 죽은 사람들 (R).
- **Bearer of good news (*mebasser*).** 좋은 소식을 전하는 자 (L), 기쁜 소식을 전하는 사람 (B) [Rom 10:15], 기쁜 소식을 가지고 오는 사람 (R). Never 복음 in Isaiah.
- **Signal flag (*nes*).** 깃발 (L, R) [Ps 60:6]; 신호 깃발 (B).
- **Ships of Tarshish.** 다시스의 배들 (L, B) [Ps 48:8; 1 Kings 10:22]; 커다란 무역선들 (R) [1 Kings 10:22 R].
- **The young woman (7:14).** 그 젊은 여자 (L, B), 한 젊은 여자 (R), and 임신하여 for "is pregnant".
  - Never 처녀: that word is *betulah* [2 Kings 19:21 처녀 딸 시온] and the Greek of Mt 1:23, which the footnote cites.
  - Immanuel is 임마누엘 at every level [Mt 1:23]; R adds "하나님께서 우리와 함께 계신다"라는 뜻이다 [Mt 1:23 B]. The same wording serves 8:8 and 8:10.
- **9:5 names.** These follow the English reading, not 개역 (기묘자, 모사, 영존하시는 아버지, 평강의 왕); uncertain, with a decision.
  - L 놀라운 조언자, 용사이신 하나님, 영원의 아버지, 평화의 통치자.
  - B 놀라운 일을 계획하는 이, 용사이신 하나님, 영원한 아버지, 평화의 통치자.
  - R 놀라운 계획을 세우는 이, 용사이신 하나님, 영원한 아버지, 평화를 가져오는 통치자.
- **The Branch.** *tsemach* (4:2; Jer 23:5; 33:15) is 싹 at every level (Jer 23:5 의로운 싹), so the passages stay linked. In 11:1, *choter* is 새싹 and *netser* is 가지; the root of 11:10 is 이새의 뿌리 [Rom 15:12].
- **Shining one (14:12).** 빛나는 자 (L), 빛나는 별 (B), 밝은 샛별 (R); son of dawn is 새벽의 아들 (L, B). Not 계명성 or 루시퍼; the Lucifer tradition goes in the footnote.
- **New heavens and new earth.** 새 하늘들과 새 땅 (L) [2 Pet 3:13]; 새 하늘과 새 땅 (B, R) [Rev 21:1].

**Jeremiah**
- **Falsehood (*sheqer*).** 거짓; 거짓말 where words are meant; 거짓을 예언하다 for the prophets.
- **Return (*shuv*).** 돌아오다 at every level, for coming back to God and from exile; R may add 마음을 돌이켜.
  - Not 회개하다, which stays for the Greek. Turning away is 돌아서다.
  - Faithless Israel (*meshuvah*) is 돌아선 이스라엘 (L) and 믿음을 저버린 이스라엘 (B, R). 3:22 keeps the play: 돌아선 자식들아, 돌아오너라.
- **Rising early.** L 일찍 일어나 말하며 (or 보내며); B 거듭거듭; R 몇 번이고.
- **Sword, famine and plague.** 칼과 기근과 전염병 (L, B) [1 Chr 21:12; 1 Kings 8:37]; 전쟁과 굶주림과 질병 (R).
- **The potter.** 토기장이 (L, B) [Mt 27:7]; 그릇 만드는 사람 (R), and his house is 그릇 만드는 사람의 작업장 at R.
- **The yoke.** 멍에 at every level [1 Kings 12]. In 27:2, 줄과 멍에 막대 (L, B) and 나무 멍에와 가죽 끈 (R).
- **The seventy years.** 70년, in figures at every level [2 Chr 36:21].
- **The new covenant (31:31).** 새 언약 [Heb 8:8, 13]. 31:31–34 keeps Hebrews 8's key terms without copying its sentences:
  - 날들이 온다 (L), 때가 오고 있다 (B, R); 이스라엘 집과 유다 집.
  - 그들의 마음에 기록하다 / 새기다; 나는 그들의 하나님이 되고 그들은 내 백성이 될 것이다.
  - 작은 사람부터 큰 사람까지; 다시는 기억하지 않을 것이다.
  - *torah* here is 가르침, as the English "instruction", with a decision that Heb 8:10 has 율법 from the Greek.
- **The Chaldeans.** 갈대아 사람들 (L, B), 바빌로니아 사람들 (R) [2 Kings 25:4; 2 Chr 36:17, 19]. The king of Babylon is 바빌론 왕.
- **The Rechabites.** 레갑 사람들 (L), 레갑 집안 (B, R). Jonadab is 레갑의 아들 요나답, the Hebrew of Jeremiah 35; 2 Kings 10:15 has 여호나답.
- **The scroll.** 두루마리 책 (L) [Heb 10:7]; 두루마리 (B, R) [1 Sam 10:25].

**Ezra**
- **God and his house.** The God of heaven is 하늘의 하나님 [2 Chr 36:23; Gen 24:3]. The house of God in Jerusalem is 예루살렘에 있는 하나님의 집 (L, B) [1 Chr 22:2] and ...하나님의 성전 (R).
- **Returned exiles (*bene haggolah*).** 포로의 자손들 (L, with a decision that "sons" means members); 포로에서 돌아온 사람들 (B); 포로로 끌려갔다가 돌아온 사람들 (R).
- **Temple servants (*netinim*).** 느디님 사람들 (L, as the English L); 성전 봉사자들 (B) [1 Chr 9:2]; 성전에서 일을 돕는 사람들 (R) [1 Chr 9:2 R].
- **Solomon's servants.** 솔로몬의 종들의 자손 at every level.
- **Lists.** 바로스 자손 (L, B, R; a place name is 베들레헴 사람들) with 2,172명 in figures. Ezra 2 sets the wording Nehemiah 7 will reuse.
- **The scribe skilled in the law of Moses (7:6).** 모세의 율법에 능숙한 서기관 (L, B); 율법을 잘 아는 율법 선생 (R) [Mt 23:13 R 율법 선생들]. The law is 율법 at every level.
- **The hand of his God.** "The hand of the LORD his God was on him":
  - L 그의 하나님 {{divine_name:주|야훼}}의 손이 그 위에 [있었으므로]; B ...의 손이 그를 보살피셨으므로; R ...께서 그를 도우셨으므로.
  - The good hand: 선한 손 (L), 은혜로운 손 (B).
- **Foreign wives.** 이방 여자들 (L) [1 Kings 11:1]; 이방 아내들 (B, R), with 아내로 맞다 for marrying. The peoples of the land are 그 땅의 백성들 (L, B) and 그 땅에 사는 사람들 (R).
- **Aramaic letters.**
  - Beyond the River: 강 건너편 (L) [1 Kings 5:4]; 강 건너편 지방 (B); 유프라테스 강 서쪽 지방 (R) [1 Kings 5:4 R].
  - Heading, at L: 아닥사스다 왕께, 강 건너편 사람들인 왕의 종들이 [올립니다]. 그리고 이제.
  - Heading, at B and R: 아닥사스다 임금님께, ...임금님의 종들이 올립니다.
  - Greeting: 평안[을 빈다] (L), 평안을 빈다 (B), 평안하기를 빈다 (R). To the king it is 합쇼체: 임금님께 온갖 평안이 있기를 빕니다.
  - King of kings: 왕들의 왕 [Rev 17:14].
- **Persian titles.**
  - Governor (*pechah*) is 총독; the Tirshatha is 디르사다 (L) and 총독 (B, R).
  - Rehum is 사령관 (L) and 고위 관리 (B, R). Shimshai is 서기관 at every level.
  - Also 태수 (satrap), 재무관 (treasurer) and 고문관 (counselor).
- **Ezra 3:11.** Reuse Ps 136:1: L [그분은] 선하시기 때문이다...; B 그분은 선하시다. 그분의 한결같은 사랑이 ... 영원하다; R 그분은 좋으신 분이시다! 그분의 변함없는 사랑은 영원하다 [also 2 Chr 5:13]. Add 이스라엘을 향한.
- **Ezra 1:1–3a** reuses 2 Chr 36:22–23 at each level.

**Names** (each verse keeps its own form, as the English does)
- **Isaiah**
  - 아모스의 아들 이사야 [2 Kings 19:2; 2 Chr 26:22]. 아모스 as published for Amoz, though it is written like the prophet Amos; a decision notes it.
  - 스알야숩; 마헬살랄하스바스; 임마누엘 [Mt 1:23].
  - 랍사게 at every level [2 Kings 18:17–19:8], though the English B and R say "chief officer".
  - 므로닥발라단 (39:1; 2 Kings 20:12 has 브로닥발라단); 고레스 [2 Chr 36:22]; 벨, 느보 [1 Chr 5:8].
  - 모압, 에돔, 게달 [Ps 120:5], 두마 [Gen 25:14], 두로, 시돈, 엘람 [Gen 10:22].
  - Kittim is 깃딤 (L, B) [Gen 10:4] and 구브로 at R, where the English says Cyprus [Acts 4:36].
- **Jeremiah**
  - 힐기야의 아들 예레미야; 아나돗 [1 Chr 11:28]; 네리야의 아들 바룩; 바스훌 [1 Chr 9:12]; 앗술의 아들 하나냐; 느헬람 사람 스마야.
  - 사반의 손자 아히감의 아들 그다랴, 느다냐의 아들 이스마엘, 가레아의 아들 요하난 [2 Kings 25:22–23].
  - 구스 사람 에벳멜렉 [구스: 1 Chr 1:8]; *saris* is 내시 (L) and 관리 (B, R).
  - 느부사라단 [2 Kings 25:8]; 다바네스; 바로 호브라 (as 바로 느고).
  - 여호야김, 시드기야; Jeconiah is 여고냐 [Mt 1:12; 1 Chr 3:17], Coniah 고니야, Jehoiachin 여호야긴 [2 Kings 24:12].
  - Nebuchadnezzar is 느부갓네살 and Nebuchadrezzar 느부갓레살.
- **Ezra**
  - 에스라; 스룹바벨 [Mt 1:12; 1 Chr 3:19].
  - 요사닥의 아들 예수아: 예수아 as 1 Chr 24:11; Ezra's Hebrew is the short form, while 1 Chr 5:40 has 여호사닥.
  - 세스바살; 다리오, 아닥사스다, 아하수에로; 닷드내, 스달보스내, 르훔, 심새.
  - 학개, 잇도의 아들 스가랴; 여히엘의 아들 스가냐 [스가냐: 1 Chr 3:21].
  - 페르시아 [2 Chr 36:20–23], never 바사.
  - The river Ahava is 아하와 강 (L) and 아하와 운하 (B, R).

**Numbers, units, sources**
- **Numbers.** Years, ages and large numbers are in figures at every level: 70년, 2,172명, 42,360명 [Kings note; 2 Chr 36:21; 1 Chr 27:12]. Months and days stay in words (열째 달 십일) [2 Kings 25:1].
  - 2 Kings 24–25 wrote years in words (이십일 세, 십일 년). Jeremiah 52 reuses its wording but uses figures, with one decision.
- **Units.** The span takes the form `{{units:약 X|unit}}`, as 2 Kings 25:17, which Jeremiah 52 reuses.
  - Mina 약 570그램; talent 약 34킬로그램; bath 약 22리터; kor 약 220리터. Totals are multiplied out (5,000 minas: 약 2.9톤).
  - Darics are 다릭 at every level [1 Chr 29:7], with a culture decision.
  - Literal keeps the unit.
- **Sources.** 역대기 is used only as the title of Chronicles. The "book of the records" (Ezra 4:15) is 기록책 (L), 기록 문서 (B) and 이전 왕들의 기록 (R). The memorandum of 6:2 is 기록. The Kings source formula, wherever it recurs, keeps …왕 실록 (B).

## Settled while drafting

AI-draft choices recorded so later work follows them; reviewers may change
any of them.

- **All languages.** Repeated passages read word for word where the Hebrew is
  the same, and the later passage's decision names each difference: Jeremiah
  51:15–19 = 10:12–16, 50:41–43 = 6:22–24, 46:27–28 = 30:10–11, 30:23–24 =
  23:19–20, 6:13–15 = 8:10–12; Jeremiah 48:29–38 against Isaiah 15–16; Isaiah
  51:11 = 35:10 and 65:25 against 11:6–9. Isaiah 36–39, Jeremiah 39:1–10 and
  52, and Ezra 1:1–3a reuse the published Kings and Chronicles wording.
  Nebuchadrezzar keeps the Hebrew's r or n form verse by verse. Shephatiah's
  and Jonadab's long and short forms follow each verse's Hebrew.
- **French.** *torah* is « loi » (L) / « instruction » (B) / « enseignement »
  (R), as above, in Isaiah too. Shofar « cor » (L, B) / « trompette » (R).
  Restore the fortunes « rétablir le sort » (L, B) / « rendre … de nouveau
  heureux » (R). God relenting « renoncer à ». Life as plunder « pour seul
  butin ». Jerusalem in Jeremiah 22:20–23 is addressed in the singular at
  every level. In Ezra, Ouzziya (10:21) and Athalia (8:7) are men's names,
  kept apart from King Ozias and Queen Athalie.
- **Spanish.** Sackcloth *cilicio* (L, B) / *ropa áspera de luto* (R). God
  relenting *retractarse* at L (*me pesa* in Jeremiah 42:10). Black cumin is
  *comino negro* in Isaiah 28:25, 27. *Sarim* *príncipes / jefes /
  dirigentes*. *Hesed* at B *amor fiel*. Numbers of four digits and more take
  a space (185 000).
- **Swahili.** A father's brother is *baba mdogo* (Jeremiah 32:7–12). The 1:10
  verbs keep *kuangusha*. Restore the fortunes *kurudishia mafanikio* (L, B) /
  *kuyafanya mambo kuwa mema tena* (R). Shofar *baragumu*. Hissing
  *[kitu cha] kuzomewa*; curse *kiapo cha laana*. *Torah* in Jeremiah is
  *mafundisho* at B.
- **Vietnamese.** God says *ngươi* (L) / *con* (B, R) to Zion, Israel, Jacob
  and the prophet in promises, and *ngươi* at every level in rebukes. Ahava is
  *sông A-ha-va*. Sackcloth *vải thô*; shofar *kèn / tù và / kèn*; Memphis
  *Mem-phít*; restore the fortunes *phục hồi cơ đồ*. No deity_pronoun span
  touches a name's syllable (Ta-rê-si, Ta-bê-ên, Ta Vui Thích Nàng).
- **Korean.** Inside God's own speech his name takes no -시- and no 께; the
  formula "Thus says the LORD" stays honorific (께서 이와 같이 말씀하신다), as
  published Kings and Chronicles do, except Isaiah 38:5 = 2 Kings 20:5. Yah is
  `{{divine_name:주|야}}`. Restore the fortunes 운명을 돌이키다 / 형편을
  회복시키다 / 다시 잘되게 해 주다. Numbers and years in figures.

## Before review

Only rendering decisions were added; the meaning decisions are the English
records' own. Reviewers should look first at the decisions marked uncertain,
Isaiah 7:14 and 9:5, the servant songs, Jeremiah 31:31–34 against Hebrews 8,
and the Aramaic letters of Ezra. Two questions for the founder: the French
book title is *Ésaïe* in `data/books.json` but every published French verse
says *Isaïe*; and Vietnamese has both *vong linh* (Psalm 88:11) and *âm hồn*
(Proverbs 9:18) for the dead (*rephaim*). These chapters use *vong linh*.

Also for native reviewers: Spanish *funcionarios* or *jefes* for *sarim* at B,
and *derecho / justicia* in Isaiah 9:6; French « loi » at L in Isaiah, where
the drafters had « instruction »; Swahili *kuzomewa* for scornful hissing;
Vietnamese *ngươi* in Jeremiah 2:2; Korean 주에게 in God's mouth (Jeremiah
29:7, Isaiah 66:20) and Shephatiah and Zebadiah both being 스바댜.
