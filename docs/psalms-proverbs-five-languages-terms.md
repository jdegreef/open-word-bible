# Psalms and Proverbs in French, Spanish, Swahili, Vietnamese and Korean

**Status: proposed, awaiting native reviewers.** These are the choices used to
draft Psalms and Proverbs in five languages at once, so that books drafted in
parallel, chapter block by chapter block, read as one translation in each
language. Each language's style guide still holds (`docs/french-style.md`,
`docs/swahili-style.md`, `docs/vietnamese-style.md`, `docs/korean-style.md`;
Spanish follows `docs/nt-spanish-swahili-terms.md` and the Spanish already in
`content/`), and so does `docs/pentateuch-fr-es-sw-terms.md` for French,
Spanish and Swahili: its names of God, its recurring terms and its measures
are not repeated here. If a choice here changes, every passage drafted under
it is revised.

Decision text stays in English, quoting the words of the language.

## All five languages

- Translate from the Hebrew, using the literal gloss, the English and the
  meaning decisions to see how a sentence was read. Never from a reference
  Bible. Psalm 23, Psalm 51, Psalm 91, Psalm 103, Proverbs 3:5–6 and
  Proverbs 31 pull hardest: draft from the gloss, and rewrite any line that
  matches a well-known version for more than a short common phrase.
- **Lines follow the English record.** Where an English level has `\q`
  breaks, that level in the language is set in lines too, with breaks placed
  by the language's own phrase boundaries (`docs/english-style.md` section
  10). Where the English level is prose, so is the language's. Most of
  Proverbs is lined; much of Psalms is not yet.
- *Selah* stays at the end of its verse at every level, as the English has
  it: French *Sélah*, Spanish *Selah*, Swahili *Sela*, Vietnamese *Sê-la*,
  Korean *셀라*. Its first use in each block of psalms gets a decision (a word
  whose meaning is unknown, probably a musical direction).
- **Titles.** A psalm's title is verse 1 and is translated at every level as
  the English level does it (Literal keeps the Hebrew's words; Readable may
  explain).
- **Addressing God.** The psalmist speaks to God with the language's
  ordinary second person of prayer, as its style guide says: French *tu*,
  Spanish *tú*, Swahili second person singular, Vietnamese *Ngài* or *Chúa*,
  Korean 합쇼체 with 저/제. God speaking uses French *je*, Spanish *yo*,
  Swahili *mimi*, Vietnamese *Ta*, Korean 해라체 with 나.
- `deity_pronoun` spans stand where the English has them and the language
  has the same choice (French, Spanish, Vietnamese; Swahili only on free
  pronouns; Korean none). Spanish adds `plural_you` wherever a plural "you"
  is addressed, as in "Praise the LORD, all you nations".
- **Proverbs.** The father's address *beni* ("my son") is the language's
  natural address to a child at every level. Personified Wisdom (1:20–33;
  8–9) and Folly (9:13–18) are women in the Hebrew: French and Spanish keep
  *elle/ella*; Swahili has no gender to keep; Vietnamese refers to Wisdom as
  *nàng* or repeats *sự khôn ngoan*; Korean repeats 지혜 or leaves the subject
  unspoken, without 그녀.
- Rendering decisions: zero to two per sentence, only where the language had
  to choose. A book-wide choice is recorded once in each block of chapters
  (its first use); later uses just follow it.

## Psalm titles and musical terms

| Hebrew (English L / B / R) | French | Spanish | Swahili | Vietnamese | Korean |
|---|---|---|---|---|---|
| *lamnatseach* (For the director / For the music director / For the leader of the music) | Au chef de chœur (L, B); Pour le chef des musiciens (R) | Al director del coro (L, B); Para el director de la música (R) | Kwa kiongozi wa kwaya (L, B); Kwa kiongozi wa waimbaji (R) | Cho người chỉ huy [ban nhạc] (L); Cho nhạc trưởng (B); Cho người hướng dẫn ban nhạc (R), as Psalm 139:1 | 지휘자를 위하여 (L); 음악 지휘자를 위하여 (B); 찬양 인도자를 위해 (R), as Psalm 139:1 |
| *mizmor* (a psalm / a song at R) | un psaume; un chant (R) | un salmo; un canto (R) | zaburi; wimbo (R) | thi thiên; bài ca (R) | 시; 노래 (R) |
| *shir* (a song) | un cantique (L, B); un chant (R) | un cántico (L, B); un canto (R) | wimbo | bài ca | 노래 |
| *maskil*, *miktam*, *shiggayon* | maskil, miktam, shiggayon | masquil, mictam, sigayón | maskili, mikitamu, shigayoni | bài Mát-kin, bài Mích-tam, bài Si-ga-giôn | 마스길, 믹담, 식가욘 |
| *Hallelu Yah* (Praise {{divine_name:the LORD\|Yah}}) | Louez {{divine_name:le SEIGNEUR\|Yah}} | `{{plural_you:Alaben\|Alabad}}` {{divine_name:al SEÑOR\|a Yah}} | Msifuni {{divine_name:BWANA\|Yah}} | Hãy ca ngợi {{divine_name:CHÚA\|Gia}} | {{divine_name:주\|야}}를 찬양하여라 |

Instruments, tunes ("to the tune of ...") and the terms whose meaning is lost
(*gittit*, *sheminit*, *alamot*, *neginot*) follow the English level: kept as
names where the English keeps them, translated where it translates, with the
English decision's uncertainty carried into the language's own decision. The
Songs of Ascents (120–134) are *Cantique des montées*, *Cántico de las
subidas*, *Wimbo wa kupanda*, *Bài ca cho những lần đi lên* (L), *Bài ca đi lên* (B), *Bài ca cho cuộc hành
trình lên Giê-ru-sa-lem* (R), and 올라감을 위한 노래 (L), 올라가며 부르는 노래 (B),
예루살렘으로 올라가며 부르는 노래 (R), as the published Psalm 121:1; French, Spanish
and Swahili at R as the English R explains them.

## Recurring terms

| Hebrew (English) | French | Spanish | Swahili | Vietnamese | Korean |
|---|---|---|---|---|---|
| *ḥesed* (loyal love L, B / faithful love R; "kindness" where the English has it) | amour loyal (L); amour fidèle (B, R); bonté | amor leal (L); amor fiel (B, R); bondad | upendo usiokoma; fadhili | tình yêu thương thành tín (L, B); tình thương không hề thay đổi (R), as Psalm 23:6; lòng nhân từ | 한결같은 사랑 (L, B); 변함없는 사랑 (R), as Psalm 23:6; 인자 (kindness) |
| the refrain "for his loyal love [is] forever" (106; 107; 118; 136) | car son amour loyal [est] pour toujours (L); car son amour fidèle dure toujours (B, R) | porque su amor leal [es] para siempre (L); su amor fiel dura para siempre (B, R) | kwa maana upendo wake usiokoma [ni] wa milele (L); upendo wake usiokoma unadumu milele (B, R) | vì tình yêu thương thành tín của {{deity_pronoun:ngài\|Ngài}} [là] đời đời (L); tình yêu thương thành tín của {{deity_pronoun:ngài\|Ngài}} còn đến đời đời (B); R with "tình thương không hề thay đổi" | 그분의 한결같은 사랑은 영원하다 (L); 그분의 한결같은 사랑이 영원하다 (B); 그분의 변함없는 사랑은 영원하다 (R) |
| *ʾemunah*, *ʾemet* (faithfulness, truth) | fidélité, vérité | fidelidad, verdad | uaminifu, kweli | sự thành tín, chân thật | 신실하심, 진실 |
| *nefesh* (soul; life, self at B and R) | âme (L) | alma (L) | nafsi (L) | linh hồn (L) | 영혼 (L) |
| the wicked (*reshaʿim*) | les méchants | los malvados | waovu | kẻ ác | 악인 (L, B); 악한 사람 (R) |
| the righteous (*tsaddiq*) | le juste | el justo | mwenye haki | người công chính | 의인 (L, B); 바르게 사는 사람 (R) |
| the upright | les hommes droits, ceux qui ont le cœur droit | los rectos | wanyofu | người ngay thẳng | 정직한 사람 |
| the poor, the afflicted, the needy | le pauvre, l’humble, l’indigent | el pobre, el afligido, el necesitado | maskini, mnyonge, mhitaji | người nghèo, người khốn khổ, người thiếu thốn | 가난한 사람, 고난받는 사람, 궁핍한 사람 |
| salvation, save | le salut, sauver | la salvación, salvar | wokovu, kuokoa | sự cứu rỗi, giải cứu (B, R as the English) | 구원, 구원하다 |
| refuge, rock, fortress, shield | refuge, rocher, forteresse, bouclier | refugio, roca, fortaleza, escudo | kimbilio, mwamba, ngome, ngao | nơi ẩn náu, vầng đá, đồn lũy, cái khiên | 피난처, 반석, 요새, 방패 |
| Zion; Jerusalem | Sion; Jérusalem | Sion; Jerusalén | Sayuni; Yerusalemu | Si-ôn; Giê-ru-sa-lem | 시온; 예루살렘 |
| Sheol | le Shéol (L); le séjour des morts (B, R) | el Seol (L); el lugar de los muertos (B, R) | Kuzimu | Âm Phủ (L, B); nơi của người chết (R), as Psalm 139:8 | 스올 (L, B); 죽은 사람들이 있는 곳 (R), as Psalm 139:8 |
| the nations; the peoples | les nations; les peuples | las naciones; los pueblos | mataifa; watu, mataifa | các dân tộc; các dân | 민족들; 백성들 |
| the fear of the LORD (Readable: honoring the LORD with awe) | la crainte du SEIGNEUR (span on *du SEIGNEUR*); R: honorer le SEIGNEUR avec respect | el temor del SEÑOR; R: honrar al SEÑOR con reverencia | kumcha BWANA; R: kumheshimu BWANA kwa hofu takatifu | sự kính sợ CHÚA; R: tôn kính CHÚA | 주를 경외함; R: 주를 두려운 마음으로 섬김 |
| the anointed (*mashiach*, the king) | l’oint | el ungido | masihi wake, mpakwa mafuta | người được xức dầu | 기름 부음 받은 이 |
| bless (God), praise (*hallel*), give thanks (*hodu*) | bénir, louer, rendre grâce | bendecir, alabar, dar gracias | kubariki, kusifu, kushukuru | chúc tụng, ca ngợi, cảm tạ | 송축하다, 찬양하다, 감사하다 |

The name *Yah* (the short form) is `{{divine_name:...|Yah}}` with the
language's form of "the LORD" as the default (Vietnamese *Gia*, Korean 야).

## Proverbs

| Hebrew (English L / B / R) | French | Spanish | Swahili | Vietnamese | Korean |
|---|---|---|---|---|---|
| *ḥokmah* (wisdom) | la sagesse | la sabiduría | hekima | sự khôn ngoan | 지혜 |
| *binah*, *tevunah* (understanding, insight) | l’intelligence | el entendimiento, la inteligencia | ufahamu, busara | sự hiểu biết, sự thông sáng | 명철 (L, B); 깨달음 (R) |
| *daʿat* (knowledge) | la connaissance | el conocimiento | maarifa | tri thức, sự hiểu biết | 지식 |
| *musar* (discipline / correction) | la discipline (L, B); la correction (R) | la disciplina (L, B); la corrección (R) | nidhamu (L, B); maonyo (R) | sự sửa dạy | 훈계 |
| *torah* of father or mother (teaching) | l’enseignement | la enseñanza | mafundisho | lời dạy | 가르침 |
| *kesil*, *ʾewil* (fool) | l’insensé | el necio | mpumbavu | kẻ ngu dại (L, B); người ngu dại (R) | 미련한 자 (L, B); 미련한 사람 (R) |
| *lets* (mocker) | le moqueur | el burlón | mwenye dharau | kẻ nhạo báng | 비웃는 자 (L, B); 남을 비웃는 사람 (R) |
| *peti* (simple / naive / easily fooled) | les simples (L); les naïfs (B); ceux qui se laissent tromper (R) | los simples (L); los ingenuos (B); los que se dejan engañar (R) | wajinga (L, B); watu wanaodanganywa kwa urahisi (R) | người khờ dại (L, B); người dễ bị lừa (R) | 어리석은 자 (L); 순진한 사람 (B); 쉽게 속는 사람 (R) |
| *ʿatsel* (sluggard / lazy) | le paresseux | el perezoso | mvivu | kẻ lười biếng (L, B); người lười biếng (R) | 게으른 자 (L, B); 게으른 사람 (R) |
| *beni* (my son) | mon fils | hijo mío | mwanangu | con ơi (L: hỡi con ta) | 내 아들아 |
| the strange/foreign woman (as the English level: foreign woman / forbidden woman / another man's wife) | la femme étrangère; R: la femme d’un autre | la mujer ajena, la extranjera; R: la mujer de otro | mwanamke mgeni; R: mke wa mtu mwingine | người đàn bà lạ; R: vợ người khác | 낯선 여자; R: 남의 아내 |
| the way, the path (*derek*, *ʾorach*) | le chemin, la voie | el camino, la senda | njia | đường lối, con đường | 길 |
| heart (*lev*, the seat of thought and will) | le cœur | el corazón | moyo | lòng | 마음 |

Names: Solomon, Agur son of Jakeh, Lemuel, Hezekiah, David, Asaph, the sons
of Korah, Heman, Ethan, Moses take each language's usual form (Salomon,
Salomón, Sulemani, Sa-lô-môn, 솔로몬; Agur, Agur, Aguri, A-gu-rơ, 아굴;
Lemuel, Lemuel, Lemueli, Lê-mu-ên, 르무엘; Asaph, Asaf, Asafu, A-sáp, 아삽;
les fils de Coré, los hijos de Coré, wana wa Kora, con cháu Cô-ra, 고라
자손). Vietnamese and Korean names already used in the New Testament keep
their published form.

## Settled while drafting

AI-draft choices recorded so later work follows them; reviewers may change
any of them.

## Before meaning review

Rendering decisions only were added; the meaning decisions are the English
records' own and keep their claims-to-check lists in the English notes.
