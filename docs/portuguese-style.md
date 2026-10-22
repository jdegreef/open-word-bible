# Portuguese style guide

How Open Word Bible drafts Portuguese. It sits on top of
`docs/english-style.md`, which still governs everything that is not about
wording (sources, one record per sentence, the three levels, decisions,
status), and of the book-wide terms files (`docs/john-terms.md`,
`docs/corinthians-terms.md`, ...), whose choices hold in Portuguese unless
this file says otherwise. Where this file and the founder's Translation
Charter disagree, the Charter wins; fix this file.

**Status: proposed, awaiting a native Brazilian Portuguese reviewer.** Every
Portuguese record is `ai_draft`.

The language is **Brazilian Portuguese** (`pt`), the variety of most of its
readers, in the spelling of the 1990 Orthographic Agreement (*ideia*,
*Galileia*, *Judeia*, *assembleia*, no diaeresis). Readers in Portugal and in
Lusophone Africa will find it Brazilian; a European form is not planned.

## 1. Sources and independence

- Translate from the Greek (and the Hebrew), never from the English. The
  English renderings and the literal gloss show how a sentence was read; the
  meaning decisions say what it means. Portuguese says that meaning in its
  own way.
- **Never reproduce the wording of a copyrighted Portuguese Bible** (NVI,
  NVT, NAA, ARA, ARC, ACF, NTLH, A Mensagem, King James Atualizada, Bíblia de
  Jerusalém, Ave-Maria, CNBB, Pastoral, TEB). Familiar verses pull drafts
  toward familiar wording; draft from the Greek and the gloss, then rewrite
  any sentence that matches a well-known version for more than a short
  common phrase. Old public-domain Almeida editions, like the English
  reference Bibles, are for comparison, never a basis for our wording.
- Never type Greek or Hebrew. A Greek or Hebrew word quoted in a decision is
  copied from the record's source text or from MACULA. **(checked)**

## 2. The record

- Add `"pt": {"L": ..., "B": ..., "R": ...}` to each record's `renderings`,
  after the last language already there. Every level is required.
  **(checked)**
- Keep the `\v N ` verse markers exactly where the English has them, and the
  `\q ` line breaks of poetry (section 10), in every Portuguese level.
  **(checked)**
- The meaning decisions are shared: do not change them. Portuguese needs only
  its own rendering decisions, with ids `r-pt-1`, `r-pt-2`, ... counted from 1
  in each record, `"layer": "rendering"`, `"language": "pt"`, the `levels`
  they apply to, and a wording category (word_choice, word_order, register,
  supplied_words, setting_alternative). **(checked)**
- Decision text (`choice`, `alternatives`, `reason`) is in **English**, like
  the other languages'; the Portuguese words under discussion are quoted in
  it ("\"cobradores de impostos\" rather than \"publicanos\""). The site tells
  Portuguese readers that notes are in English for now.
- Write a Portuguese rendering decision where Portuguese had to choose and a
  reader might ask why: a word chosen against a familiar alternative, a
  form of address, a structure Portuguese cannot copy, a setting span that
  differs from the English one, a term settled here for the whole book
  (once, where it first appears in a passage). Do not repeat the English
  rendering decisions; where Portuguese simply follows the English choice,
  no decision is needed. Typical density: zero to two per sentence.

## 3. The three levels in Portuguese

**Literal (OWB-L).** Follows the Greek order and wording where Portuguese
allows. Words Portuguese needs but the Greek lacks go in [square brackets],
as in English ("[havia] seis talhas"). An article Portuguese requires and
contracts with a preposition ("No princípio", where the Greek has no
article) needs no bracket. Keep the historic present ("ele diz") where the
Greek has it.

**Balanced (OWB-B).** Careful modern Brazilian Portuguese in the written
standard, the register of a good public reading. Tracks the Greek closely; no
brackets. Narration in the *pretérito perfeito* ("Jesus respondeu", "eles
vieram"), the normal past of narrative. Pronoun placement as educated
Brazilians write it: proclisis is normal ("Jesus lhe disse", "ele os
chamou"); no sentence opens with an unstressed pronoun ("Me disse" is
spoken, not written); no mesoclisis ("dir-lhe-ei"), which reads as
European or archaic.

**Readable (OWB-R).** Plain Brazilian Portuguese for new and young readers:
short sentences, common words, still correct written Portuguese. Explains
idioms and may make explicit what the context implies, as the English
Readable does, with a decision where the English has one. Prefer naming the
person to a chain of clitics ("Jesus respondeu a Pedro" rather than
"respondeu-lhe"); avoid *lhe/lhes* where *a ele*, *a vocês* or a name reads
more plainly, but never use the spoken "ele disse pra mim".

Portuguese has one past tense for narration at every level, so no tense
decision is needed for narrative, unlike French.

## 4. Forms of address

- **Você / vocês** between people at every level: people speak to each other
  with *você*, Jesus says *você* to one person and *vocês* to several. *Vós*
  is not used, even at Literal: it is archaic in Brazil, and *vocês* is the
  only living second person plural. With *você* go *o/a, lhe, seu/sua*, or
  *de você* where *seu* would be ambiguous ("a fé de você" is spoken; prefer
  rewording: "a sua fé"); never mix *você* with *te/teu* in one address.
- **Tu** when anyone speaks to God or to Jesus, at every level ("Pai
  nosso, que estás nos céus", "Senhor, se quiseres, podes me purificar",
  "Mestre, sabemos que és sincero"): it is the living form of prayer in
  Brazilian churches, and it keeps every speaker's address to Jesus
  respectful without the ambiguity of *o senhor*. His opponents, Satan and
  Pilate use it too; the words around it show their attitude. With *tu* go
  *te, ti, teu/tua, contigo*, and the verb in the second person singular.
  God speaking to a person uses *tu* too (the prophets, the voice from
  heaven), as the Old Testament does throughout. So do the commandments
  of the Law where the New Testament quotes them, at every level: "Não
  matarás" (L, B), "Não mates", "Honra o teu pai" (R).
- **O senhor / a senhora** when someone speaks up to a human master or
  superior (a slave to his master in a parable, the leaders to Pilate, a
  son to his father where the story stresses respect): "Senhor, o senhor me
  entregou cinco talentos". It is how Brazilians address a superior; *você*
  there sounds rude, and *tu* is kept for God and Jesus.
- These are wording, not meaning, and Brazilian Portuguese has no regional
  alternative worth a setting, so no reader setting is used for address.

## 5. Spelling and typography

- Quotation marks: write straight double quotes `"` for the outer
  quotation and straight single quotes `'` for one inside it, exactly as
  English does; the site curls them into “ ” and ‘ ’, the Brazilian
  marks. A quotation that runs over several sentences opens in the first
  record and closes in the last, as in English. Dialogue dashes are not
  used.
- Apostrophes are rare in Portuguese; write ’ (U+2019) where one is needed
  ("pau-d’arco").
- Capitals: Deus, o Pai, o Filho, o Espírito Santo, o Senhor, o Filho do
  Homem, o Cordeiro de Deus, a Lei (the Law of Moses), as Escrituras, o
  Reino de Deus, o Reino dos céus. Lowercase: fariseus, saduceus, sábado,
  months and days of the week.
- Numbers in words up to *vinte* and for round tens and hundreds in running
  text ("cinco mil homens"); figures for clock times, measures and money
  when the number is long.
- Proper names in their usual Brazilian form: Jesus, Maria, José, João,
  Pedro, André, Tiago, Filipe, Bartolomeu, Tomé, Mateus, Natanael, Judas
  Iscariotes, Simão, Moisés, Elias, Eliseu, Isaías, Jeremias, Abraão,
  Isaque, Jacó, Davi, Salomão, Herodes, Pilatos, Caifás, Belém, Nazaré,
  Cafarnaum, Galileia, Judeia, Samaria, Jerusalém, Betânia, Betsaida,
  Jericó, Egito, Babilônia.

## 6. Words for the whole New Testament

Each passage that first uses one records it in a rendering decision ("for
the whole book"); later passages just follow it. Where the English loosens a
term at Readable with a decision, Portuguese may loosen it the same way.

| Greek (English) | Portuguese | Notes |
|---|---|---|
| grace, truth, glory, peace | a graça, a verdade, a glória, a paz | Key terms: the same word at every level. |
| believe / believe in | crer / crer em (L, B); acreditar em, confiar em (R) | Readable may say *acreditar* where the English Readable says "believe"; *confiar* only where the English Readable says "trust". |
| the Word (John 1) | o Verbo | Every level, recorded as an uncertain decision in John 1:1, as Spanish *el Verbo* and French *le Verbe*: *a Palavra* is feminine and would make the Word *ela* until verse 14. |
| the world; eternal life | o mundo; a vida eterna | |
| sign (*sēmeion*) | sinal | Never "milagre". |
| Son of Man | o Filho do Homem | A title; never under the gender setting. |
| Lamb of God | o Cordeiro de Deus | |
| the Holy Spirit | o Espírito Santo; o Espírito | |
| kingdom of God / of heaven | o Reino de Deus / o Reino dos céus | Every level, as the English keeps "kingdom of heaven" at Readable. |
| scribes (*grammateis*) | os escribas (L, B); os mestres da Lei (R) | Readable follows the English "teachers of the law". |
| Pharisees, Sadducees, Herodians | os fariseus, os saduceus, os herodianos | |
| chief priests; high priest | os chefes dos sacerdotes; o sumo sacerdote | |
| tax collectors | os cobradores de impostos | Every level; not "publicanos". |
| sinners | os pecadores | |
| demon; unclean spirit | um demônio; um espírito impuro | |
| Satan; the devil | Satanás; o diabo | |
| Gehenna / hell; Hades | as the English per level: a geena where it keeps the name, o inferno where it says "hell"; o Hades (L), o mundo dos mortos (B, R) | |
| centurion | um centurião (L, B); um oficial romano (R), as the English | |
| the Council (*synedrion*) | o Sinédrio (L, B); o conselho dos líderes judeus (R) | |
| synagogue; Sabbath; Passover | a sinagoga; o sábado; a Páscoa | |
| Truly I tell you (*amēn legō hymin*) | Em verdade eu lhes digo (L, B); Eu garanto a vocês (R) | One decision per passage. To one person: "Em verdade eu lhe digo" / "Eu garanto a você". John's doubled form: "Em verdade, em verdade eu lhes digo" (L, B). |
| Woe to you | Ai de vocês (L, B); R as the English | |
| the Twelve | os Doze | |
| John the Baptist | João Batista | |
| the law (*nomos*, the Law of Moses) | a Lei | Lowercase "a lei" only for law in general or a principle (Romans 7:23). |
| righteousness; righteous | a justiça; justo | L and B. Readable may say "estar em paz com Deus", "ser aceito por Deus" where the English Readable says "right with God", with a decision. |
| justify (*dikaioō*) | justificar (L); declarar justo (B); as the English at R | |
| flesh (*sarx*) | a carne (L, B); R follows the meaning decision and the English ("a natureza humana", "os próprios desejos") | |
| church (*ekklēsia*) | a Igreja for the whole body of believers; a igreja for one congregation ("a igreja em Corinto", "a igreja que se reúne na casa deles") | |
| God's holy people (*hagioi*) | os santos (L); o povo santo de Deus, os irmãos na fé (B, R) | |
| Gentiles, nations (*ethnē*) | as nações (L); os não judeus (B, R) where the English says "Gentiles"; as nações where it says "nations" | No hyphen in "não judeus" (1990 Agreement). |
| elders; overseer; deacon | os anciãos (Jewish elders), os presbíteros (church elders); o supervisor (L, B), o líder (R); o diácono | |
| repent, repentance | arrepender-se, o arrependimento (L, B); R as the English ("mudar de vida", "voltar-se para Deus") | |
| baptize | batizar | |
| covenant | a aliança | |
| the gospel | o evangelho (L, B); as boas-novas (R) | "The good news of the kingdom" is "as boas-novas do Reino" at every level where the English says "good news". |
| slave (*doulos*, *ʿeved*) | escravo (L); servo, serva (B, R) | As the English: "escravo" at every level where slavery itself is the point. |
| disciples | os discípulos | |
| Rabbi | Rabi | |
| Messiah (where the text says *Messias*) | o Messias | Plainly, no setting. |
| Woman (Jesus to his mother) | Mulher (L, B); Mãe (R) | As the English. |
| Sir / Lord (*kyrie*) | senhor / Senhor | As the English per passage; see section 4 for the address that goes with it. |
| the Lamb; living creatures; elders (Revelation) | o Cordeiro; os quatro seres viventes; os vinte e quatro anciãos | |

## 7. Reader settings in Portuguese

Settings change wording, never meaning, exactly as in English.

- `deity_pronoun`: every pronoun for God or Christ, lowercase default,
  capitalised alternative, only the capitalisation differing. **(checked)**
  The Portuguese forms: `{{deity_pronoun:ele|Ele}}`, `{{deity_pronoun:o|O}}`,
  `{{deity_pronoun:lhe|Lhe}}`, `{{deity_pronoun:dele|Dele}}`,
  `{{deity_pronoun:seu|Seu}}` (and `sua`, `seus`, `suas`),
  `{{deity_pronoun:si mesmo|Si mesmo}}`, an enclitic after a hyphen
  (`adorá-{{deity_pronoun:lo|Lo}}`), and when Jesus speaks of himself or
  is spoken to: `mim|Mim`, `me|Me`, `meu|Meu`, `minha|Minha`, `tu|Tu`,
  `te|Te`, `ti|Ti`, `teu|Teu`, `tua|Tua`, `contigo|Contigo`, `comigo|Comigo`;
  the unstressed `me` before or after a verb takes the span too
  ("quem {{deity_pronoun:me|Me}} negar", "Siga-{{deity_pronoun:me|Me}}"). "Eu" for Jesus
  has no span, and a pronoun at the start of a sentence is written plainly
  with its capital ("Ele estava no princípio com Deus"). Put a span
  wherever the English has one for the same person; Portuguese may need one
  where English does not (an object pronoun "o", "lhe") and the reverse. A
  possessive agrees with the thing possessed, so "his glory" is
  `a {{deity_pronoun:sua|Sua}} glória`.
- `christos`: `{{christos:Cristo|Messias}}` where English Literal has
  `{{christos:Christ|Messiah}}`; with the article,
  `o {{christos:Cristo|Messias}}` ("Eu não sou o {{christos:Cristo|Messias}}").
  Where the English has `Jesus {{christos:Christ|the Messiah}}`, Portuguese
  writes `Jesus {{christos:Cristo|o Messias}}`, as French writes
  `Jésus {{christos:Christ|le Messie}}`. Check that both options read
  naturally.
- `gender`: an inclusive default where the original means men and women,
  with the traditional Portuguese as the alternative:
  `{{gender:irmãos e irmãs|irmãos}}`, `{{gender:as pessoas|os homens}}`,
  `{{gender:todos|todos os homens}}`, `{{gender:ninguém|nenhum homem}}`,
  `{{gender:o ser humano|o homem}}`. Not for specific men, and not where
  Portuguese is already inclusive ("os filhos de Deus", "cada um",
  "ninguém", "quem"). The setting goes on a **noun** Portuguese has to
  choose, usually where the original has *anthrōpos*, *adelphoi* or
  *ʾādām*; words that must agree with it go under the same setting.
  Generic pronouns take none: "quem", "aquele que", "todo aquele que",
  "alguém" already mean anyone, and the "ele" that refers back to them is
  ordinary generic Portuguese. A rendering decision (setting_alternative)
  records a difference from the English the first time it occurs in a
  passage.
- `units`: metric by default, the original unit as the alternative:
  `{{units:de oitenta a cento e vinte litros|duas ou três medidas}}`. Literal
  keeps the original unit. This differs from the English (US units) and
  needs a rendering decision the first time in a passage.
- `divine_name`: `{{divine_name:SENHOR|Javé}}`, at every level, in capitals
  like the English "the LORD", with its article and contractions outside
  the span where Portuguese needs one: `o {{divine_name:SENHOR|Javé}}` reads
  "o Javé" under the alternative, which is wrong, so write the article
  inside both options: `{{divine_name:o SENHOR|Javé}}`,
  `{{divine_name:do SENHOR|de Javé}}`, `{{divine_name:ao SENHOR|a Javé}}`,
  `{{divine_name:pelo SENHOR|por Javé}}`, `{{divine_name:no SENHOR|em Javé}}`.
  At the start of a sentence: `{{divine_name:O SENHOR|Javé}}`. *Jeová* is not
  used. *Adonai* ("Lord") is *Senhor*, never in capitals; *Elohim* is *Deus*.

## 8. Status

A Portuguese rendering added to a record does not change its status. Nothing
is marked reviewed by an AI.

## 9. Section headings and summaries

Where a book's `data/headings/<BOOK>.json` or `data/summaries/<BOOK>.json`
has the languages beside English, add `"pt"` beside them, written from Open
Word Bible's own Portuguese wording. They are AI drafts until reviewed.

## 10. The Old Testament and poetry

- **Lines.** Poetry is set in lines, as `docs/english-style.md` section 10
  describes: mark each break inside a verse with `\q `, following the
  Hebrew accents' division (`python3 scripts/poetry_lines.py` prints it),
  at every level. Portuguese places its own breaks; a verse start is always
  a line start.
- **Titles.** A psalm's title is verse 1, as in the Hebrew: "Salmo de Davi"
  (B, R); Literal keeps the Hebrew's words ("[Um] salmo de Davi").
- **Addressing God.** The psalmist says *eu* and speaks to God with *tu*
  (section 4); God speaking says *eu*.
- Old Testament narrative uses the *pretérito perfeito* at every level, like
  the Gospels; the Hebrew *wayyiqtol* chain is joined with "e" at Literal
  and with ordinary Portuguese connectives at Balanced and Readable, as the
  English does.

## 11. The Gospels: recurring words and names

Settled in Matthew for the four Gospels and Acts.

| English | Portuguese | Notes |
|---|---|---|
| Blessed are ... (*makarioi*) | Bem-aventurados ... (L, B); Felizes ... (R) | *Abençoado* is narrower: someone who has received a blessing. |
| your Father in heaven | o Pai de vocês que [está] nos céus (L); o Pai de vocês, que está no céu (B, R) | "De vocês" where *seu* could mean "his" or "their". |
| you of little faith (*oligopistoi*) | gente de pouca fé (L, B); R as the English | Said to the crowd (6:30) as well as to the disciples, so a word for people, not men. |
| Gentiles, pagans (*ethnikoi*, 5:47; 6:7; 18:17) | os pagãos | |
| the Law and the Prophets | a Lei e os Profetas | |
| this generation | esta geração | |
| demon-possessed | endemoninhado (L, B); R as the English ("dominado por demônios") | |
| leper, skin disease | as the English per level: leproso where it says "leper"; "um homem com uma doença de pele" where it says that | |
| denarius; talent | um denário, um talento (L, B); R as the English ("o salário de um dia") | |
| the sixth hour | a hora sexta (L); meio-dia (B, R); likewise a hora terceira / nove da manhã, a hora nona / três da tarde | |
| Feast of Unleavened Bread | a festa dos Pães sem Fermento | |
| Hosanna; Amen | Hosana; amém | |
| Beelzebul | Belzebu | |
| magi | os magos | |
| Zion | Sião | |
| the Christ (*ho christos*) | o {{christos:Cristo\|Messias}} | As section 7. |

Names: Abraão, Isaque, Jacó, Judá, Tamar, Perez, Raabe, Rute, Boaz, Obede,
Jessé, Davi, Salomão, Urias, Zorobabel, Babilônia, Emanuel, Herodes,
Herodias, Arquelau, Zebedeu, Alfeu, Tadeu, Simão, o zelote, Judas
Iscariotes, Jonas, Elias, Isaías, Jeremias, Sidom, Tiro, Sodoma, Gomorra,
Corazim, Betsaida, Cafarnaum, Nazaré, nazareno, gadarenos, a mulher cananeia,
Cesareia de Filipe, Betfagé, Betânia, Jericó, Getsêmani, Gólgota, Caifás,
Pilatos, Barrabás, Simão de Cirene, José de Arimateia, Maria Madalena.
