# 1 and 2 Samuel in French, Spanish, Swahili, Vietnamese and Korean

**Status: proposed, awaiting native reviewers.** These are the choices used to
draft 1 and 2 Samuel in five languages at once, so that chapter blocks drafted
in parallel read as one translation in each language. They continue the
earlier notes, which still hold and are not repeated here:

- French, Spanish and Swahili: `docs/pentateuch-fr-es-sw-terms.md` (names of
  God, recurring terms, measures, narrative tenses, reference Bibles not to
  reproduce) and each language's style guide.
- Vietnamese and Korean: `docs/genesis-vietnamese-korean-terms.md` (names of
  God, recurring terms, address between people, measures) and each
  language's style guide.
- All five: `docs/psalms-proverbs-five-languages-terms.md` for *ḥesed*,
  Sheol, *ʿeved*, "the LORD of hosts", the anointed and the other words
  shared with Psalms.
- The English choices for these books: `docs/samuel-chronicles-terms.md`.

If a choice here changes, every passage drafted under it is revised.
Decision text stays in English, quoting the words of the language.

## All five languages

- Translate from the Hebrew, using the literal gloss, the English and the
  meaning decisions to see how a sentence was read. Never from a reference
  Bible. Hannah's song (1 Samuel 2), David and Goliath (17), David and
  Jonathan (18–20), David and Bathsheba with Nathan's parable (2 Samuel
  11–12) and David's lament over Absalom (2 Samuel 19:1) pull hardest:
  draft from the gloss and rewrite any line that matches a well-known
  version for more than a short common phrase.
- **Lines follow the English record**: where an English level has `\q`
  breaks, the language's same level is set in lines too, following the
  Hebrew's division (Hannah's song, the women's song in 1 Samuel 18:7, 21:12
  and 29:5, David's laments in 2 Samuel 1 and 3, 2 Samuel 22 and 23:1–7, and
  any other passage whose English has `\q`). Elsewhere, prose.
- **2 Samuel 22 is Psalm 18**, already published in all five languages:
  reuse the language's Psalm 18 wording at each level wherever the Hebrew is
  the same, and follow the English decisions on each difference.
- **Hebrew verse numbering**, as the English: 1 Samuel 21:1 (English 20:42b),
  24:1 (English 23:29) and 2 Samuel 19:1 (English 18:33) carry the English
  records' versification decisions; nothing changes in the wording.
- **Speech** takes the quotation marks of each language's narrative (the
  Pentateuch drafts for French, Spanish and Swahili; double quotes for
  Vietnamese and Korean, as Genesis). Speeches run across verses without
  closing the quotation at each verse.
- **Settings** mirror the English spans where the language has the same
  choice: `divine_name` always, `deity_pronoun` on free pronouns, `units`
  where the English converts (same metric values as the Pentateuch note:
  cubit 45 cm, span 23 cm, shekel 11.5 g, talent 34 kg, ephah 22 litres,
  seah 7 litres), `gender` only where the language really has two wordings,
  and Spanish `plural_you` wherever a group is addressed. In the tables
  below, SEIGNEUR, SEÑOR, BWANA, CHÚA and 주 standing for YHWH are always the
  `divine_name` span of the earlier notes (French and Spanish take the
  article into the span; Korean leaves the particle outside it:
  `{{divine_name:주|야훼}}의 궤`).
- Rendering decisions: zero to two per sentence, only where the language had
  to choose. A book-wide choice is recorded once in each block of chapters
  (its first use); later uses just follow it.

## Recurring terms

| Hebrew (English L / B / R) | French | Spanish | Swahili | Vietnamese | Korean |
|---|---|---|---|---|---|
| the ark of God / of the LORD / of the covenant | l’arche de Dieu / du SEIGNEUR / de l’alliance | el arca de Dios / del SEÑOR / del pacto | sanduku la Mungu / la BWANA / la agano | hòm của Đức Chúa Trời / của CHÚA / hòm giao ước | 하나님의 궤 / 주의 궤 / 언약궤 |
| *mashiaḥ YHWH* (the LORD's anointed; R: the king the LORD has anointed) | l’oint du SEIGNEUR (L, B); le roi que le SEIGNEUR a oint (R) | el ungido del SEÑOR (L, B); el rey que el SEÑOR ha ungido (R) | masihi wa BWANA (L); mfalme wa BWANA aliyempaka mafuta (B); mfalme ambaye BWANA amempaka mafuta (R) | người được xức dầu của CHÚA (L); vị vua được CHÚA xức dầu (B); vị vua CHÚA đã xức dầu (R) | 주의 기름 부음 받은 이 (L); 주께서 기름 부으신 이 (B); 주께서 기름 부어 세우신 왕 (R) |
| anoint (a king) | oindre | ungir | kumpaka mafuta | xức dầu | 기름을 붓다 |
| YHWH tseba'ot (the LORD of hosts / of Armies) | le SEIGNEUR des armées | el SEÑOR de los ejércitos (L), de los Ejércitos (B, R) | BWANA wa majeshi | CHÚA Vạn Quân (span on CHÚA only) | 만군의 주 (L, B); 하늘의 군대를 거느리신 주 (R) |
| Lord GOD (*Adonai YHWH*, 2 Samuel 7) | Seigneur DIEU | Señor DIOS | Bwana MUNGU | Chúa là CHÚA | 주 하나님 (span on 하나님) |
| *nagid* (ruler / ruler / leader) | chef | gobernante (L, B); líder (R) | kiongozi | người lãnh đạo | 지도자 |
| seer (*roʾeh*), prophet, man of God | le voyant, le prophète, l’homme de Dieu | el vidente, el profeta, el hombre de Dios | mwonaji, nabii, mtu wa Mungu | nhà tiên kiến, nhà tiên tri, người của Đức Chúa Trời | 선견자, 예언자, 하나님의 사람 |
| a band / company of prophets | une troupe de prophètes | un grupo de profetas | kundi la manabii | một đoàn tiên tri | 예언자 무리 |
| ephod; the linen ephod | l’éphod; un éphod de lin | el efod; un efod de lino | efodi; efodi ya kitani | áo ê-phót; áo ê-phót bằng vải gai | 에봇; 베 에봇 |
| Urim and Thummim | les ourim et les toummim | el urim y el tumim | Urimu na Thumimu | U-rim và Thu-mim | 우림과 둠밈 |
| household gods (L) / god (B) / idol (R) | les dieux domestiques; le dieu domestique; l’idole domestique | los dioses domésticos; el ídolo doméstico (B, R) | miungu ya nyumbani (L); sanamu ya miungu ya nyumbani (B, R) | các tượng thần gia đình (L, B); tượng thần nhỏ của gia đình (R) | 드라빔 (L); 집안 우상 (B, R) |
| high place (R: hilltop shrine) | le haut lieu (L, B); le sanctuaire sur la colline (R) | el lugar alto (L, B); el santuario sobre la colina (R), now worded as the Kings note (*santuarios sobre las colinas*) | mahali pa juu (L, B); patakatifu pa kilimani (R) | nơi cao | 산당 |
| the king's servants (officials) | les serviteurs du roi (L); les officiers du roi (B, R) | los siervos del rey (L); los oficiales del rey (B, R) | watumishi wa mfalme (L); maafisa wa mfalme (B, R) | các đầy tớ của vua (L); các quần thần (B, R) | 왕의 신하들 |
| "your servant" (to the king) | ton serviteur | tu siervo | mtumishi wako | đầy tớ của vua (L, B); tôi (R) | 임금님의 종, 이 종 (L, B); 저 (R) |
| "my lord the king" | mon seigneur le roi | mi señor el rey | bwana wangu mfalme | chúa tôi là vua (L); bệ hạ (B); đức vua (R) | 내 주 임금님 |
| commander of the army | le chef de l’armée | el jefe del ejército | jemadari wa jeshi (L); mkuu wa jeshi (B, R) | tướng chỉ huy quân đội | 군대 사령관 |
| "As the LORD lives" (oath) | Aussi vrai que le SEIGNEUR est vivant | Vive el SEÑOR (L); tan cierto como que el SEÑOR vive (B, R) | Kama BWANA aishivyo | Thật như CHÚA hằng sống | 주께서 살아 계심을 두고 맹세하는데 |
| "May God do so to me and more also" (oath) | Que Dieu me traite avec sévérité et plus encore | Que Dios me castigue, y aun más | Mungu anitendee hivyo, na kuzidi | Nguyện Đức Chúa Trời phạt tôi nặng nề | 하나님께서 내게 벌을 내리시고 더 내리셔도 좋다 |
| "the Spirit of the LORD rushed on" | l’Esprit du SEIGNEUR fondit sur | el Espíritu del SEÑOR vino con poder sobre | Roho wa BWANA alimjia kwa nguvu | Thần Linh của CHÚA giáng mạnh trên | 주의 영이 크게 임하였다 |
| an evil / harmful spirit from the LORD | un esprit mauvais venant du SEIGNEUR | un espíritu malo de parte del SEÑOR | roho mbaya kutoka kwa BWANA | một ác thần từ CHÚA | 주께서 보내신 악한 영 |
| inquire of the LORD | consulter le SEIGNEUR | consultar al SEÑOR | kumwuliza BWANA | cầu hỏi CHÚA | 주께 여쭈다 |
| uncircumcised (of the Philistines) | incirconcis | incircunciso | asiyetahiriwa | không chịu cắt bì | 할례를 받지 않은 |
| worthless men ("sons of Belial") | des vauriens | hombres perversos | watu wasiofaa kitu | những kẻ vô lại | 불량배 |
| the lords (rulers) of the Philistines | les princes des Philistins | los jefes de los filisteos | wakuu wa Wafilisti | các lãnh chúa Phi-li-tin | 블레셋 통치자들 |
| "from Dan to Beersheba" | depuis Dan jusqu’à Beer-Shéba | desde Dan hasta Beerseba | tangu Dani mpaka Beer-sheba | từ Đan đến Bê-e-Sê-ba | 단에서 브엘세바까지 |
| the City of David | la cité de David | la ciudad de David | mji wa Daudi | thành Đa-vít | 다윗 성 |
| *ḥesed* (steadfast love L / faithful love B, R), also between people | amour loyal (L); amour fidèle (B, R) | amor leal (L); amor fiel (B, R) | upendo usiokoma (L); fadhili (B, R) | tình yêu thương thành tín (L); lòng nhân từ (B, R) | 한결같은 사랑 (L); 인애 (B, R) |
| covenant (between David and Jonathan) | alliance | pacto | agano | giao ước | 언약 |
| sackcloth | le sac | el cilicio | gunia | vải thô | 굵은 베 |
| "Have you come in peace?" (*shalom*) | Viens-tu en paix ? | ¿Vienes en paz? | Je, umekuja kwa amani? | Ông đến có bình an không? | 평안한 일로 오십니까? (to a superior); 평안하냐? (해라체) |

## Names

Proper names follow each language's usual form, and the forms already used
in the language's published books (the New Testament, Psalm titles, the
Pentateuch for French, Spanish and Swahili, Genesis for Vietnamese and
Korean). Published forms win. A name not in the table follows the usual form
in the language and stays the same through both books: keep a list as you
draft, and check `content/` (Psalm titles, the New Testament) before
choosing.

| English | French | Spanish | Swahili | Vietnamese | Korean |
|---|---|---|---|---|---|
| Samuel, Hannah, Elkanah, Peninnah | Samuel, Anne, Elqana, Peninna | Samuel, Ana, Elcana, Penina | Samweli, Hana, Elkana, Penina | Sa-mu-ên, An-ne, Ên-ca-na, Phê-ni-na | 사무엘, 한나, 엘가나, 브닌나 |
| Eli, Hophni, Phinehas, Ichabod | Éli, Hophni, Phinéas, I-Kabod | Elí, Ofni, Finés, Icabod | Eli, Hofni, Finehasi, Ikabodi | Hê-li, Hóp-ni, Phi-nê-a, Y-ca-bốt | 엘리, 홉니, 비느하스, 이가봇 |
| Saul son of Kish, Jonathan, Michal, Merab, Abner | Saül fils de Kis, Jonathan, Mikal, Merab, Abner | Saúl hijo de Cis, Jonatán, Mical, Merab, Abner | Sauli mwana wa Kishi, Yonathani, Mikali, Merabu, Abneri | Sau-lơ con trai Kích, Giô-na-than, Mi-canh, Mê-ráp, Áp-ne | 기스의 아들 사울, 요나단, 미갈, 메랍, 아브넬 |
| David son of Jesse, Eliab, Goliath | David fils de Jessé, Éliab, Goliath | David hijo de Isaí, Eliab, Goliat | Daudi mwana wa Yese, Eliabu, Goliathi | Đa-vít con trai Gie-sê, Ê-li-áp, Gô-li-át | 이새의 아들 다윗, 엘리압, 골리앗 |
| Agag, Ahimelech, Abiathar, Doeg the Edomite, Achish | Agag, Ahimélek, Abiathar, Doëg l’Édomite, Akish | Agag, Ahimelec, Abiatar, Doeg el edomita, Aquis | Agagi, Ahimeleki, Abiathari, Doegi Mwedomu, Akishi | A-ga, A-hi-mê-léc, A-bi-a-tha, Đô-e người Ê-đôm, A-kích | 아각, 아히멜렉, 아비아달, 에돔 사람 도엑, 아기스 |
| Nabal, Abigail, Ahinoam | Nabal, Abigaïl, Ahinoam | Nabal, Abigail, Ahinoam | Nabali, Abigaili, Ahinoamu | Na-banh, A-bi-ga-in, A-hi-nô-am | 나발, 아비가일, 아히노암 |
| Joab, Abishai, Asahel (sons of Zeruiah) | Joab, Abishaï, Asahel (fils de Tserouya) | Joab, Abisai, Asael (hijos de Sarvia) | Yoabu, Abishai, Asaheli (wana wa Seruya) | Giô-áp, A-bi-sai, A-sa-ên (con trai Xê-ru-gia) | 요압, 아비새, 아사헬 (스루야의 아들들) |
| Ish-bosheth, Mephibosheth, Ziba | Ishbosheth, Mephibosheth, Tsiba | Isboset, Mefiboset, Siba | Ishboshethi, Mefiboshethi, Siba | Ích-bô-sết, Mê-phi-bô-sết, Xíp-ba | 이스보셋, 므비보셋, 시바 |
| Bathsheba, Uriah the Hittite, Nathan | Bethsabée, Urie le Hittite, Nathan | Betsabé, Urías el hitita, Natán | Bathsheba, Uria Mhiti, Nathani | Bát-sê-ba, U-ri người Hê-tít, Na-than | 밧세바, 헷 사람 우리야 (as Matthew 1:6), 나단 |
| Absalom, Amnon, Tamar, Solomon | Absalom, Amnon, Tamar, Salomon | Absalón, Amnón, Tamar, Salomón | Absalomu, Amnoni, Tamari, Sulemani | Áp-sa-lôm, Am-nôn, Ta-ma, Sa-lô-môn | 압살롬, 암논, 다말, 솔로몬 |
| Ahithophel, Hushai, Zadok, Shimei | Ahitofel, Houshaï, Sadok, Shiméï | Ahitofel, Husai, Sadoc, Simei | Ahithofeli, Hushai, Sadoki, Shimei | A-hi-tô-phe, Hu-sai, Xa-đốc, Si-mê-i | 아히도벨, 후새, 사독, 시므이 |
| Amasa, Sheba son of Bichri, Benaiah | Amasa, Shéba fils de Bikri, Benaya | Amasa, Seba hijo de Bicri, Benaía | Amasa, Sheba mwana wa Bikri, Benaya | A-ma-sa, Sê-ba con trai Biếc-ri, Bê-na-gia | 아마사, 비그리의 아들 세바, 브나야 |
| Ramah, Shiloh, Mizpah, Gibeah, Bethel, Gilgal | Rama, Silo, Mitspa, Guibea, Béthel, Guilgal | Ramá, Silo, Mizpa, Guibeá, Betel, Gilgal | Rama, Shilo, Mizpa, Gibea, Betheli, Gilgali | Ra-ma, Si-lô, Mích-ba, Ghi-bê-a, Bê-tên, Ghinh-ganh | 라마, 실로, 미스바, 기브아, 벧엘, 길갈 |
| Gath, Ekron, Ashdod, Ziklag, Jabesh-gilead | Gath, Eqrôn, Ashdod, Tsiqlag, Yabesh de Galaad | Gat, Ecrón, Asdod, Siclag, Jabes de Galaad | Gathi, Ekroni, Ashdodi, Siklagi, Yabeshi ya Gileadi | Gát, Éc-rôn, Ách-đốt, Xiếc-lác, Gia-be ở Ga-la-át | 가드, 에그론, 아스돗, 시글락, 길르앗 야베스 |
| Endor, Mount Gilboa, Kiriath-jearim, Hebron, Jerusalem, Zion | Endor, le mont Guilboa, Qiryath-Yearim, Hébron, Jérusalem, Sion | Endor, el monte Gilboa, Quiriat-jearim, Hebrón, Jerusalén, Sion | Endori, mlima Gilboa, Kiriath-yearimu, Hebroni, Yerusalemu, Sayuni | Ên-đô-rơ, núi Ghinh-bô-a, Ki-ri-át Giê-a-rim, Hếp-rôn, Giê-ru-sa-lem, Si-ôn | 엔돌, 길보아 산, 기럇여아림, 헤브론, 예루살렘, 시온 |
| Bethlehem, Ziph and the Ziphites, Zobah, the Valley of Salt, Tyre | Bethléem, Ziph et les Ziphiens, Soba, la vallée du Sel, Tyr | Belén, Zif y los zifeos, Soba, el valle de la Sal, Tiro | Bethlehemu, Zifu na Wazifi, Soba, Bonde la Chumvi, Tiro | Bết-lê-hem, Xíp và người Xíp, Xô-ba, thung lũng Muối, Ty-rơ | 베들레헴, 십과 십 사람들, 소바, 소금 골짜기, 두로 |
| Philistines, Amalekites, Ammonites, Jebusites, Kenites | les Philistins, les Amalécites, les Ammonites, les Jébusiens, les Kéniens | los filisteos, los amalecitas, los amonitas, los jebuseos, los ceneos | Wafilisti, Waamaleki, Waamoni, Wayebusi, Wakeni | người Phi-li-tin, người A-ma-léc, người Am-môn, người Giê-bu-sít, người Kê-nít | 블레셋 사람들, 아말렉 사람들, 암몬 사람들, 여부스 사람들, 겐 사람들 |

Psalm 34's title calls Achish "Abimelech"; that is the Psalm's own name and
does not change Achish in Samuel.

## Language by language

- **French, Spanish, Swahili**: narrative tenses as the Pentateuch note
  (French passé simple at L and B, passé composé at R; Spanish preterite;
  Swahili *-li-* then *-ka-*); *ʿeved* as the Psalms note ("my servant
  David", "your servant" in speech to the king or to God: *serviteur* /
  *siervo* / *mtumishi* at every level). One person is *tu* / *tú* in
  French and Spanish, the king included, as the published Pentateuch
  speaks to Pharaoh and Joseph; respect is carried by "mon seigneur le roi",
  "ton serviteur" / "mi señor el rey", "tu siervo". Spanish never uses
  *usted*; a group is `{{plural_you:ustedes|vosotros}}`.
- **Vietnamese**: narration as Genesis. Address forms are recorded once per
  pair in each block. Subjects call the king *vua* (L), *bệ hạ* (B) or
  *đức vua* (R) and themselves *đầy tớ của vua* (L, B) or *tôi* (R) where
  the Hebrew says "your servant"; the king says *ta* and *ngươi*. Elkanah
  calls Hannah *em* and she calls him *anh*; Eli calls Samuel *con*, and
  Samuel answers with *thầy* and *con*. David says *anh* to Jonathan and
  *em* for himself; Jonathan says *em* to David and *anh* for himself.
  Saul says *ta* and *ngươi* to David, then *con* where he calls him "my
  son" (1 Samuel 24:17; 26:17), and David *cha* where he says "my father"
  (24:12). Samuel and Saul say *ông* to each other at first; Nathan calls
  David *vua*.
- **Korean**: narration in the plain written style with the honorific -시-
  for God; God speaks 해라체 with 나 and 너. Subjects speak to the king in
  합쇼체, calling him 내 주 임금님 or 임금님 and themselves 임금님의 종 or
  이 종 (L, B), 저 (R). The king speaks 해라체 to subjects; Saul calls David
  내 아들 다윗아 where the Hebrew has "my son". Samuel speaks 해라체 to the
  young Saul and Saul answers in 합쇼체. David speaks 합쇼체 to Jonathan, the
  king's son, and 해요체 after their covenant; Jonathan speaks 해라체 to
  David. Eli speaks 해라체 to Samuel with 내 아들아.

## Settled while drafting

AI-draft choices recorded so later work follows them; reviewers may change
any of them. Each is also a rendering decision at its first use in each
block of chapters (1 Samuel 1–15, 16–31; 2 Samuel 1–12, 13–24).

- **All five**: "the people" meaning the army is the ordinary word for
  people at L and "troops", "soldiers" or "army" at B and R. The women's
  song (1 Samuel 18:7; 21:12; 29:5) has one wording per level each time.
  Where the English Readable says "Your Majesty", French and Spanish say
  "ô roi" / "mi rey" (no *Majesté*, *Majestad*, which would need *vous*,
  *usted*). God's "my servant David" is "servant" at every level, Literal
  included. No gender span where the language's word already covers men and
  women (Swahili, Vietnamese and Korean have almost none).
- **"Thus says the LORD"**: French *Ainsi parle le SEIGNEUR* (L), *Le
  SEIGNEUR dit ceci* (B), *Voici ce que dit le SEIGNEUR* (R); Spanish *Así
  dice el SEÑOR* / *El SEÑOR dice esto* / *Esto es lo que dice el SEÑOR*;
  Vietnamese *CHÚA phán thế này* (L), *CHÚA phán như vầy* (B), *Đây là lời
  CHÚA phán* (R); Korean 이와 같이 말씀하신다 (L), 이렇게 말씀하신다 (B).
- **French**: passé simple at L and B, passé composé at R, imparfait for
  repeated action; spoken tenses inside speeches and the laments. The
  LORD addressed directly is `{{divine_name:SEIGNEUR|Yahvé}}` without the
  article. Book of Jashar: *le livre du Yashar* (L), *le livre du Juste*
  (B, R).
- **Spanish**: *tú* to everyone; quotation marks « “ ‘ ’ ” »; "Vive el
  SEÑOR" (L), "tan cierto como que el SEÑOR vive" (B, R); God's regret
  (1 Samuel 15) is never *arrepentirse*; *el pan de la Presencia* (B, R).
- **Swahili**: deity spans only on free possessives, never on verb
  prefixes; "the people" as army *watu* (L), *askari* / *jeshi* (B, R);
  *suria* for concubine, explained at R.
- **Vietnamese**: *Gát* is Gath and the land of Gad; the prophet Gad is
  always *nhà tiên tri Gát*, a Gadite *người Ga-đít*. Vietnamese has to
  say which brother is older: Joab is older than Abishai and Asahel, Amnon
  than Absalom, and Tamar is *em gái* to both (marked uncertain). Saul says
  *con* and David *cha* from 1 Samuel 24:12; Saul says *tao* / *mày* to
  Jonathan in his rage (20:30–31).
- **Korean**: Samuel speaks 해라체 to Saul and the people, who call him 어른
  in 합쇼체. David speaks 하오체 with 그대 to Nathan, Gad and Barzillai
  (uncertain). Amnon is 형 to Absalom; Tamar calls Amnon 오라버니. Amasa's
  mother is 아비갈, kept apart from Nabal's wife 아비가일. Concubines are
  후궁.

## Before review

Only rendering decisions were added; the meaning decisions are the English
records' own. Reviewers should look first at the decisions marked uncertain,
the address forms between David and Saul, David and Jonathan and David and
his officers, and the names. Known unevenness between blocks, left for a
reviewer rather than settled by the drafter:

- Numbers above one hundred: French and Swahili 1 Samuel 1–15 and
  Vietnamese 1 Samuel 1–15 write them in words; the other blocks use
  figures.
- Korean measures say "약 X" in some blocks and "X쯤" in others.
- Swahili "young men" at B is *vijana* in 1 Samuel 16–31 and *mtumishi* in
  1–15.
- 2 Samuel 22:51 keeps the published Psalm 18:51 wording for *ḥesed* in
  Swahili and Korean, which differs from the B and R choice above.
- Vietnamese uses *thẩm phán* for the judges in 1 Samuel, where the
  Joshua–Ruth drafts propose *quan xét*.
