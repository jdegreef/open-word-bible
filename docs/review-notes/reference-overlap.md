# Reference-Bible overlap

Item 21 of the consistency audits. `scripts/ngram_overlap.py` was run over every book, at every level, against every comparison Bible pinned in `vendor/open-bibles`: for English the BSB, WEB, ASV, KJV and YLT (New Testament), for Spanish the Reina-Valera 1909. No other language has a pinned comparison text (open-bibles holds no French, Portuguese, Swahili, Vietnamese, Korean, Amharic, Hindi, Russian, Ukrainian or Japanese Bible), so they could not be measured. A run is a stretch of six or more words shared in order with the same verses of another Bible.

What is expected: Literal shares long runs with the KJV, ASV and YLT, which are literal too; lists of names, numbers and genealogies, formulas ("as the LORD had commanded Moses") and short sayings fixed by the original ("What is sweeter than honey?") are shared by every translation. What looks copied: a long run of ordinary prose at Balanced or Readable shared with one modern translation (the BSB or WEB) and with none of the older ones, since two independent translators rarely choose the same twenty words in the same order.

Measured on main as merged on 14 November 2026, before the rewrites below.

## English

| Book | Literal | Balanced | Readable | Longest run |
|---|---|---|---|---|
| 1CH | 60% | 48% | 22% | 35 (1CH.28.8.s1 L, bsb) |
| 1CO | 48% | 13% | 6% | 36 (1CO.3.21.s1 L, web) |
| 1JN | 65% | 36% | 19% | 28 (1JN.5.13.s1 B, bsb) |
| 1KI | 58% | 45% | 19% | 35 (1KI.13.18.s1 L, bsb) |
| 1PE | 47% | 17% | 7% | 29 (1PE.3.21.s1 L, web) |
| 1SA | 54% | 38% | 19% | 32 (1SA.5.10.s1 L, asv) |
| 1TH | 61% | 27% | 8% | 32 (1TH.4.16.s1 L, web) |
| 1TI | 56% | 34% | 6% | 38 (1TI.1.1.s1 L, bsb) |
| 2CH | 59% | 48% | 20% | 47 (2CH.31.13.s1 L, asv) |
| 2CO | 48% | 12% | 4% | 34 (2CO.3.5.s1 L, web) |
| 2JN | 67% | 26% | 12% | 25 (2JN.1.3.s1 L, web) |
| 2KI | 58% | 46% | 21% | 45 (2KI.23.8.s1 L, web) |
| 2PE | 45% | 20% | 6% | 25 (2PE.1.1.s1 B, bsb) |
| 2SA | 56% | 38% | 17% | 41 (2SA.21.8.s1 L, web) |
| 2TH | 59% | 26% | 13% | 28 (2TH.1.11.s1 L, web) |
| 2TI | 61% | 42% | 6% | 36 (2TI.1.8.s1 L, web) |
| 3JN | 44% | 18% | 3% | 11 (3JN.1.1.s1 L, web) |
| ACT | 59% | 22% | 11% | 41 (ACT.6.5.s1 L, asv) |
| AMO | 47% | 39% | 16% | 31 (AMO.1.1.s1 L, web) |
| COL | 62% | 27% | 6% | 29 (COL.2.9.s1 L, web) |
| DAN | 47% | 40% | 16% | 20 (DAN.11.18.s1 L, bsb) |
| DEU | 54% | 38% | 16% | 31 (DEU.10.8.s1 L, bsb) |
| ECC | 30% | 29% | 5% | 16 (ECC.12.2.s1 L, asv) |
| EPH | 68% | 25% | 7% | 43 (EPH.4.17.s1 L, web) |
| EST | 47% | 47% | 18% | 37 (EST.6.4.s1 L, web) |
| EXO | 52% | 26% | 16% | 39 (EXO.29.21.s1 L, web) |
| EZK | 45% | 39% | 20% | 32 (EZK.43.11.s1 B, bsb) |
| EZR | 62% | 57% | 23% | 35 (EZR.8.21.s1 L, web) |
| GAL | 56% | 24% | 8% | 24 (GAL.1.15.s1 L, web) |
| GEN | 66% | 27% | 16% | 35 (GEN.36.17.s1 L, web) |
| HAB | 31% | 32% | 6% | 18 (HAB.1.12.s1 B, bsb) |
| HAG | 53% | 46% | 21% | 27 (HAG.1.14.s1 L, web) |
| HEB | 52% | 19% | 10% | 32 (HEB.7.1.s1 L, asv) |
| HOS | 45% | 40% | 13% | 26 (HOS.1.1.s1 L, web) |
| ISA | 42% | 16% | 8% | 35 (ISA.19.20.s1 L, bsb) |
| JAS | 43% | 26% | 9% | 21 (JAS.5.7.s2 L, web) |
| JDG | 53% | 36% | 16% | 43 (JDG.9.28.s1 L, bsb) |
| JER | 55% | 37% | 17% | 36 (JER.21.7.s1 L, asv) |
| JHN | 60% | 38% | 21% | 34 (JHN.19.17.s1 L, ylt) |
| JOB | 36% | 33% | 6% | 27 (JOB.1.10.s1 L, web) |
| JOL | 42% | 42% | 12% | 17 (JOL.1.2.s1 L, bsb) |
| JON | 35% | 40% | 17% | 13 (JON.1.14.s1 B, bsb) |
| JOS | 56% | 38% | 20% | 37 (JOS.11.21.s1 L, asv) |
| JUD | 42% | 23% | 4% | 21 (JUD.1.20.s1 L, asv) |
| LAM | 43% | 20% | 8% | 31 (LAM.2.21.s1 L, web) |
| LEV | 48% | 26% | 15% | 41 (LEV.4.34.s1 L, web) |
| LUK | 62% | 25% | 13% | 306 (LUK.3.23.s1 L, bsb) |
| MAL | 48% | 39% | 16% | 15 (MAL.3.24.s1 L, bsb) |
| MAT | 66% | 25% | 14% | 40 (MAT.25.35.s1 L, web) |
| MIC | 48% | 37% | 10% | 22 (MIC.1.1.s1 L, web) |
| MRK | 58% | 19% | 8% | 37 (MRK.8.31.s1 L, asv) |
| NAM | 37% | 38% | 8% | 17 (NAM.1.3.s1 B, web) |
| NEH | 50% | 54% | 21% | 45 (NEH.10.37.s1 L, web) |
| NUM | 52% | 39% | 18% | 33 (NUM.31.54.s1 B, bsb) |
| OBA | 48% | 44% | 15% | 13 (OBA.1.11.s1 B, web) |
| PHM | 76% | 40% | 12% | 20 (PHM.1.15.s1 L, bsb) |
| PHP | 57% | 16% | 5% | 41 (PHP.3.4.s1 L, bsb) |
| PRO | 38% | 11% | 2% | 21 (PRO.30.4.s1 L, bsb) |
| PSA | 37% | 6% | 3% | 25 (PSA.27.4.s1 L, kjv) |
| REV | 72% | 32% | 23% | 87 (REV.7.5.s1 B, bsb) |
| ROM | 59% | 20% | 6% | 28 (ROM.9.26.s1 L, web) |
| RUT | 52% | 31% | 14% | 21 (RUT.2.11.s1 L, web) |
| SNG | 44% | 40% | 18% | 19 (SNG.2.14.s1 R, web) |
| TIT | 60% | 38% | 4% | 24 (TIT.2.11.s1 L, bsb) |
| ZEC | 50% | 42% | 21% | 20 (ZEC.7.5.s1 B, web) |
| ZEP | 43% | 45% | 9% | 18 (ZEP.2.5.s1 B, bsb) |

Share of each level's words that fall in a shared run of six or more words, with any comparison Bible.

### Longest Balanced and Readable runs shared only with a modern edition (188 sentences with a run of 20+ words; lists left out)

- NEH.4.8.s1 B, 44 words (bsb): "I stood up and said to the nobles the officials and the rest of the people Do not be afraid of them Remember the Lord who is great and awesome and fight for your brothers your sons and daughters your wives and your homes"
- NUM.31.54.s1 B, 33 words (bsb): "Moses and Eleazar the priest received the gold from the commanders of thousands and of hundreds and brought it into the tent of meeting as a memorial for the Israelites before the LORD"
- EZK.43.11.s1 B, 32 words (bsb): "If they are ashamed of all they have done make known to them the design of the temple its arrangement its exits and entrances its whole design and all its statutes and"
- NUM.4.19.s1 B, 32 words (bsb): "live and not die when they come near the most holy things Aaron and his sons are to go in and assign each man his task and what he is to carry"
- DEU.11.29.s1 B, 30 words (bsb): "When the LORD your God brings you into the land you are entering to possess you are to proclaim the blessing on Mount Gerizim and the curse on Mount Ebal"
- LEV.12.8.s1 B, 30 words (bsb): "two turtledoves or two young pigeons one for a burnt offering and the other for a sin offering The priest will make atonement for her and she will be clean"
- DEU.13.6.s1 B, 29 words (bsb): "rebellion against the LORD your God who brought you out of the land of Egypt and redeemed you from the house of slavery He has tried to turn you"
- GEN.7.4.s1 B, 29 words (bsb): "I will send rain on the earth for forty days and forty nights and I will wipe from the face of the earth every living thing I have made"
- LEV.15.15.s1 R, 29 words (bsb): "as a sin offering and the other as a burnt offering In this way the priest will make atonement for the man before the LORD because of his discharge"
- NEH.10.29.s1 B, 29 words (web): "The rest of the people the priests the Levites the gatekeepers the singers the temple servants and all who had separated themselves from the peoples of the lands to"
- NEH.3.31.s1 B, 29 words (bsb): "one of the goldsmiths made repairs as far as the house of the temple servants and the merchants opposite the Inspection Gate and as far as the upper room"
- 1JN.5.13.s1 B, 28 words (bsb): "I have written these things to you so that you may know that you have eternal life you who believe in the name of the Son of God"
- 2TI.4.1.s1 B, 28 words (bsb): "charge you in the presence of God and of Christ Jesus who will judge the living and the dead and in view of His appearing and His kingdom"
- ACT.26.16.s1 B, 28 words (bsb): "from your own people and from the Gentiles I am sending you to them to open their eyes so that they turn from darkness to light and from"
- GEN.9.15.s1 B, 28 words (bsb): "I will remember My covenant between Me and you and every living creature of every kind Never again will the waters become a flood to destroy all life"
- JDG.14.18.s1 B, 28 words (web): "On the seventh day before the sun went down the men of the city said to him What is sweeter than honey What is stronger than a lion"
- JHN.8.28.s1 B, 28 words (bsb): "So Jesus said When you have lifted up the Son of Man then you will know that I am and that I do nothing on My own but"
- MAT.8.9.s1 B, 28 words (bsb): "I myself am a man under authority with soldiers under me I tell one Go and he goes and another Come and he comes I tell my servant"
- NEH.10.37.s1 B, 28 words (web): "the firstborn of our sons and of our livestock the firstborn of our herds and of our flocks to the house of our God to the priests who"
- 1JN.4.2.s1 B, 27 words (bsb): "has come in the flesh is from God and every spirit that does not confess Jesus is not from God This is the spirit of the antichrist"
- 1PE.5.10.s1 B, 27 words (bsb): "And after you have suffered for a little while the God of all grace who called you to His eternal glory in Christ will Himself restore you"
- EXO.31.18.s1 B, 26 words (bsb): "had finished speaking with Moses on Mount Sinai He gave him the two tablets of the testimony tablets of stone inscribed by the finger of God"
- EXO.40.29.s1 B, 26 words (bsb): "the entrance to the tabernacle the tent of meeting and offered on it the burnt offering and the grain offering just as the LORD had commanded"
- JHN.6.24.s1 B, 26 words (bsb): "So when the crowd saw that neither Jesus nor His disciples were there they got into the boats and went to Capernaum to look for Him"
- JHN.8.24.s1 B, 26 words (bsb): "That is why I told you that you will die in your sins For unless you believe that I am you will die in your sins"
- NUM.11.22.s1 B, 26 words (bsb): "flocks and herds were slaughtered for them would they have enough If all the fish in the sea were caught for them would they have enough"
- NUM.16.26.s1 B, 26 words (bsb): "the congregation Move away now from the tents of these wicked men Do not touch anything that belongs to them or you will be swept away"
- NUM.19.4.s1 B, 26 words (bsb): "Eleazar the priest is to take some of its blood on his finger and sprinkle it seven times toward the front of the tent of meeting"
- NUM.24.9.s1 B, 26 words (bsb): "lies down like a lion like a lioness who dares to rouse him Blessed are those who bless you and cursed are those who curse you"
- NUM.4.33.s1 B, 26 words (bsb): "This is the service of the Merarite clans all their work at the tent of meeting under the direction of Ithamar son of Aaron the priest"
- REV.4.1.s2 B, 26 words (bsb): "in the Spirit and I saw a throne standing in heaven with someone seated on it The one seated there looked like jasper and carnelian and"
- 2PE.1.1.s1 B, 25 words (bsb): "Peter a servant and apostle of Jesus Christ to those who through the righteousness of our God and Savior Jesus Christ have received a faith"
- EST.7.8.s1 B, 25 words (bsb): "Just as the king returned from the palace garden to the banquet hall Haman was falling on the couch where Esther was reclining The king"
- EZR.8.31.s1 B, 25 words (bsb): "On the twelfth day of the first month we set out from the Ahava canal to go to Jerusalem The hand of our God was"
- MAT.7.11.s1 B, 25 words (bsb, web): "know how to give good gifts to your children how much more will your Father in heaven give good things to those who ask Him"
- NUM.24.7.s1 B, 25 words (bsb): "Water will flow from his buckets and his seed will have abundant water His king will be greater than Agag and his kingdom will be"
- NUM.7.89.s1 B, 25 words (web): "voice speaking to him from above the mercy seat on the ark of the testimony from between the two cherubim And He spoke to him"
- REV.17.14.s1 B, 25 words (web): "the Lamb and the Lamb will overcome them for He is Lord of lords and King of kings and those who are with Him are"
- DEU.1.21.s1 B, 24 words (bsb): "the LORD your God has placed the land before you Go up and take possession of it as the LORD the God of your"
- DEU.14.2.s1 B, 24 words (bsb): "holy to the LORD your God Out of all the peoples on the face of the earth the LORD has chosen you to be"

## Spanish

| Book | Literal | Balanced | Readable | Longest run |
|---|---|---|---|---|
| 1CH | 16% | 8% | 2% | 30 (1CH.6.50.s1 L, rv1909) |
| 1CO | 15% | 3% | 1% | 22 (1CO.15.41.s1 L, rv1909) |
| 1JN | 32% | 13% | 4% | 19 (1JN.1.1.s1 L, rv1909) |
| 1KI | 20% | 9% | 2% | 33 (1KI.21.29.s1 L, rv1909) |
| 1PE | 10% | 3% | 1% | 13 (1PE.3.12.s1 L, rv1909) |
| 1SA | 13% | 4% | 2% | 26 (1SA.23.17.s1 L, rv1909) |
| 1TH | 10% | 3% | 1% | 19 (1TH.4.16.s1 L, rv1909) |
| 1TI | 14% | 5% | 1% | 16 (1TI.6.11.s1 L, rv1909) |
| 2CH | 18% | 9% | 3% | 29 (2CH.6.33.s1 L, rv1909) |
| 2CO | 14% | 4% | 1% | 26 (2CO.4.17.s1 L, rv1909) |
| 2JN | 11% | 0% | 0% | 7 (2JN.1.5.s1 L, rv1909) |
| 2KI | 20% | 8% | 3% | 22 (2KI.23.24.s1 L, rv1909) |
| 2PE | 15% | 7% | 1% | 12 (2PE.1.11.s1 L, rv1909) |
| 2SA | 16% | 6% | 2% | 24 (2SA.19.6.s1 L, rv1909) |
| 2TH | 16% | 7% | 2% | 12 (2TH.1.11.s1 B, rv1909) |
| 2TI | 23% | 8% | 0% | 16 (2TI.2.15.s1 L, rv1909) |
| 3JN | 8% | 7% | 2% | 11 (3JN.1.3.s1 L, rv1909) |
| ACT | 15% | 4% | 1% | 18 (ACT.1.21.s1 L, rv1909) |
| AMO | 14% | 5% | 1% | 20 (AMO.5.16.s1 L, rv1909) |
| COL | 14% | 3% | 1% | 13 (COL.1.24.s1 L, rv1909) |
| DAN | 20% | 6% | 2% | 21 (DAN.2.41.s1 L, rv1909) |
| DEU | 17% | 5% | 2% | 27 (DEU.21.21.s1 L, rv1909) |
| ECC | 11% | 3% | 1% | 17 (ECC.9.1.s1 L, rv1909) |
| EPH | 20% | 5% | 0% | 16 (EPH.6.2.s1 L, rv1909) |
| EST | 21% | 8% | 3% | 21 (EST.3.8.s1 L, rv1909) |
| EXO | 16% | 6% | 2% | 27 (EXO.38.31.s1 L, rv1909) |
| EZK | 16% | 5% | 2% | 22 (EZK.31.6.s1 L, rv1909) |
| EZR | 25% | 11% | 4% | 24 (EZR.3.2.s1 L, rv1909) |
| GAL | 13% | 6% | 1% | 13 (GAL.1.15.s1 L, rv1909) |
| GEN | 19% | 4% | 2% | 28 (GEN.31.1.s1 L, rv1909) |
| HAB | 11% | 3% | 1% | 12 (HAB.2.20.s1 L, rv1909) |
| HAG | 15% | 9% | 1% | 14 (HAG.2.19.s1 B, rv1909) |
| HEB | 14% | 3% | 1% | 19 (HEB.7.1.s1 L, rv1909) |
| HOS | 13% | 5% | 1% | 24 (HOS.2.7.s1 L, rv1909) |
| ISA | 11% | 3% | 1% | 19 (ISA.11.7.s1 L, rv1909) |
| JAS | 11% | 6% | 1% | 13 (JAS.2.26.s1 L, rv1909) |
| JDG | 15% | 6% | 2% | 26 (JDG.14.3.s1 L, rv1909) |
| JER | 18% | 6% | 2% | 30 (JER.8.1.s1 L, rv1909) |
| JHN | 21% | 9% | 3% | 29 (JHN.12.44.s1 L, rv1909) |
| JOB | 7% | 3% | 0% | 17 (JOB.42.15.s1 L, rv1909) |
| JOL | 13% | 6% | 3% | 15 (JOL.3.3.s1 L, rv1909) |
| JON | 7% | 3% | 0% | 15 (JON.1.7.s1 L, rv1909) |
| JOS | 15% | 6% | 2% | 24 (JOS.22.10.s1 L, rv1909) |
| JUD | 12% | 8% | 1% | 15 (JUD.1.20.s1 L, rv1909) |
| LAM | 11% | 3% | 0% | 14 (LAM.2.20.s1 L, rv1909) |
| LEV | 13% | 4% | 1% | 24 (LEV.26.42.s1 L, rv1909) |
| LUK | 13% | 5% | 2% | 31 (LUK.12.52.s1 B, rv1909) |
| MAL | 15% | 5% | 1% | 21 (MAL.3.19.s1 L, rv1909) |
| MAT | 14% | 5% | 2% | 21 (MAT.22.37.s1 L, rv1909) |
| MIC | 14% | 7% | 1% | 14 (MIC.1.4.s1 L, rv1909) |
| MRK | 16% | 5% | 2% | 17 (MRK.12.26.s1 L, rv1909) |
| NAM | 10% | 6% | 0% | 11 (NAM.2.1.s1 L, rv1909) |
| NEH | 24% | 11% | 4% | 35 (NEH.9.19.s1 L, rv1909) |
| NUM | 15% | 5% | 2% | 18 (NUM.4.32.s1 L, rv1909) |
| OBA | 19% | 9% | 4% | 18 (OBA.1.18.s1 L, rv1909) |
| PHM | 2% | 2% | 1% | 8 (PHM.1.3.s1 L, rv1909) |
| PHP | 13% | 4% | 0% | 13 (PHP.2.9.s1 L, rv1909) |
| PRO | 8% | 2% | 0% | 14 (PRO.31.2.s1 L, rv1909) |
| PSA | 12% | 2% | 0% | 19 (PSA.109.18.s1 L, rv1909) |
| REV | 35% | 15% | 8% | 25 (REV.11.6.s1 L, rv1909) |
| ROM | 13% | 4% | 1% | 21 (ROM.10.6.s1 L, rv1909) |
| RUT | 13% | 4% | 1% | 16 (RUT.2.11.s1 L, rv1909) |
| SNG | 8% | 4% | 2% | 15 (SNG.3.2.s1 L, rv1909) |
| TIT | 6% | 5% | 1% | 15 (TIT.1.1.s1 L, rv1909) |
| ZEC | 18% | 6% | 2% | 19 (ZEC.14.10.s1 L, rv1909) |
| ZEP | 14% | 9% | 1% | 13 (ZEP.3.11.s1 L, rv1909) |

Share of each level's words that fall in a shared run of six or more words, with any comparison Bible.

### Longest Balanced and Readable runs shared only with a modern edition (78 sentences with a run of 14+ words; lists left out)

- LUK.12.52.s1 B, 31 words (rv1909): "contra el hijo y el hijo contra el padre la madre contra la hija y la hija contra la madre la suegra contra su nuera y la nuera contra su suegra"
- EXO.13.21.s1 B, 26 words (rv1909): "iba delante de ellos de día en una columna de nube para guiarlos por el camino y de noche en una columna de fuego para alumbrarles"
- REV.7.15.s1 B, 23 words (rv1909): "están delante del trono de Dios y Le sirven día y noche en Su templo y el que está sentado en el trono"
- 2CH.36.23.s1 B, 22 words (rv1909): "el Dios de los cielos me ha dado todos los reinos de la tierra y Él me ha encargado que Le edifique"
- EZR.3.2.s1 B, 21 words (rv1909): "y edificaron el altar del Dios de Israel para ofrecer sobre él holocaustos como está escrito en la ley de Moisés"
- NEH.13.31.s1 B, 21 words (rv1909): "para la ofrenda de la leña en los tiempos señalados y para las primicias Acuérdate de mí Dios mío para bien"
- NEH.9.19.s1 B, 19 words (rv1909): "no los abandonaste en el desierto La columna de nube no se apartó de ellos de día para guiarlos"
- REV.3.12.s1 B, 19 words (rv1909): "Escribiré sobre él el nombre de Mi Dios y el nombre de la ciudad de Mi Dios la nueva"
- 1KI.21.22.s1 B, 18 words (rv1909): "tu casa como la casa de Jeroboam hijo de Nabat y como la casa de Baasa hijo de"
- NEH.5.14.s1 B, 18 words (rv1909): "gobernador de ellos en la tierra de Judá desde el año veinte hasta el año treinta y dos"
- NEH.9.6.s1 B, 18 words (rv1909): "la tierra y todo lo que hay en ella los mares y todo lo que hay en ellos"
- 1CH.5.14.s1 B, 17 words (rv1909): "Estos fueron los hijos de Abihail hijo de Huri hijo de Jaroa hijo de Galaad hijo de"
- 1KI.8.23.s1 B, 17 words (rv1909): "Dios de Israel no hay Dios como Tú arriba en los cielos ni abajo en la tierra"
- EST.3.8.s1 B, 17 words (rv1909): "entre los pueblos en todas las provincias de tu reino Sus leyes son diferentes de las de"
- ISA.37.16.s1 R, 17 words (rv1909): "Tú eres Dios sobre todos los reinos de la tierra Tú hiciste los cielos y la tierra"
- LUK.19.37.s1 B, 17 words (rv1909): "Bendito el Rey que viene en el nombre del Señor Paz en el cielo y gloria en"
- NEH.8.16.s1 B, 17 words (rv1909): "en la plaza de la puerta de las Aguas y en la plaza de la puerta de"
- NEH.8.16.s1 R, 17 words (rv1909): "en la plaza de la puerta de las Aguas y en la plaza de la puerta de"
- REV.3.5.s1 B, 17 words (rv1909): "borraré su nombre del libro de la vida Delante de Mi Padre y delante de Sus ángeles"
- EST.3.7.s1 B, 16 words (rv1909): "En el mes primero que es el mes de Nisán en el año duodécimo del rey"
- EZR.5.14.s1 B, 16 words (rv1909): "de oro y de plata de la casa de Dios que Nabucodonosor había sacado del templo"
- JER.33.4.s1 B, 16 words (rv1909): "acerca de las casas de esta ciudad y de las casas de los reyes de Judá"
- JHN.5.32.s1 B, 16 words (rv1909): "que da testimonio de Mí y sé que el testimonio que da de Mí es verdadero"
- JOB.1.18.s1 B, 16 words (rv1909): "dijo Tus hijos y tus hijas estaban comiendo y bebiendo vino en casa de su hermano"
- LUK.11.49.s1 B, 16 words (rv1909): "desde la sangre de Abel hasta la sangre de Zacarías que murió entre el altar y"
- NEH.6.10.s1 B, 16 words (rv1909): "en la casa de Dios dentro del templo y cerremos las puertas del templo porque vienen"
- REV.7.15.s1 R, 16 words (rv1909): "Le sirven día y noche en Su templo Y el que está sentado en el trono"
- 1CH.26.20.s1 B, 15 words (rv1909): "cargo de los tesoros de la casa de Dios y de los tesoros de las"
- 1KI.22.10.s1 B, 15 words (rv1909): "la entrada de la puerta de Samaria y todos los profetas profetizaban delante de ellos"
- 1SA.30.16.s1 B, 15 words (rv1909): "que habían tomado de la tierra de los filisteos y de la tierra de Judá"
- 2CH.18.9.s1 B, 15 words (rv1909): "la entrada de la puerta de Samaria y todos los profetas profetizaban delante de ellos"
- 2CO.3.3.s1 B, 15 words (rv1909): "el Espíritu del Dios vivo no en tablas de piedra sino en tablas de carne"
- 2SA.3.29.s1 B, 15 words (rv1909): "caiga sobre la cabeza de Joab y sobre toda la casa de su padre Que"
- 2SA.7.11.s1 B, 15 words (rv1909): "que puse jueces sobre Mi pueblo Israel Y te daré descanso de todos tus enemigos"
- DEU.12.14.s1 B, 15 words (rv1909): "en una de tus tribus Allí ofrecerás tus holocaustos y allí harás todo lo que"
- DEU.19.21.s1 B, 15 words (rv1909): "vida por vida ojo por ojo diente por diente mano por mano pie por pie"
- DEU.30.1.s1 B, 15 words (rv1909): "todas estas cosas la bendición y la maldición que he puesto delante de ti y"
- EZR.6.5.s1 B, 15 words (rv1909): "de oro y de plata de la casa de Dios que Nabucodonosor sacó del templo"
- GEN.3.22.s1 B, 15 words (rv1909): "mano y tome también del árbol de la vida y coma y viva para siempre"
- JDG.6.20.s1 B, 15 words (rv1909): "El ángel de Dios le dijo Toma la carne y los panes sin levadura y"

## Rewritten

The worst cases were reworded from the source meaning (the Hebrew or Greek, the literal gloss and the meaning decisions), not from any reference Bible, keeping the record's settings, key terms and decisions. John 6:24 and 8:28 were left: their wording is tied to alignments and rendering decisions, and the shared words are the Greek's own order.

- NEH.4.8.s1 en B: "said to the nobles, the officials and the rest of the people, "Do not be afraid of them. Remember the Lord, who is great and awesome, and fight for your brothers, your sons and daughters, your wives and your homes."" -> "spoke to the nobles, the officials and the rest of the people: "Do not fear them. Keep in mind the Lord, great and awesome, and fight for your brothers, for your sons and your daughters, for your wives and your homes.""
- NUM.31.54.s1 en B: "Moses and Eleazar the priest received the gold from the commanders of thousands and of hundreds and brought it into the tent of meeting as a memorial for the" -> "So Moses and Eleazar the priest accepted the gold from the commanders over thousands and over hundreds and took it into the tent of meeting, to be a reminder of the"
- EZK.43.11.s1 en B: "make known to them the design of the temple, its arrangement, its exits and entrances, its whole design, and all its statutes and laws. Write it down where they can see it, so that they may keep its whole design and all its statutes and carry them out." -> "show them the plan of the temple: how it is laid out, its ways out and its ways in, its whole plan, with all its statutes and laws. Write it out in front of them, so that they hold to its whole plan and all its statutes and carry them out."
- NUM.4.19.s1 en B: "This is what you must do for them, so that they will live and not die when they come near the most holy things: Aaron and his sons are to go in and assign each man his task and what he is to carry." -> "Do this for them, so that they live and do not die when they approach the most holy things: Aaron and his sons are to go in and give each man his work and his load."
- DEU.11.29.s1 en B: "brings you into the land you are entering to possess, you are to proclaim the blessing" -> "has brought you into the land you are going in to take, you are to pronounce the blessing"
- DEU.13.6.s1 en B: "because he has urged rebellion against {{divine_name:the LORD|Yahweh}} your God, who brought you out of the land of Egypt" -> "because he has preached rebellion against {{divine_name:the LORD|Yahweh}} your God, who led you out of the land of Egypt"
- GEN.7.4.s1 en B: "In seven days I will send rain on the earth for forty days and forty nights, and I will wipe from the face of the earth every living thing I have made."" -> "Seven days from now I will send rain on the earth for forty days and forty nights, and I will wipe off the face of the ground every living thing I have made.""
- NEH.3.31.s1 en B: "After him Malkijah, one of the goldsmiths, made repairs as far as the house of the temple servants and the merchants, opposite the Inspection Gate, and as far as the upper room at the corner." -> "Next to him Malkijah, a goldsmith, repaired the wall up to the house of the temple servants and the merchants, across from the Inspection Gate, and up to the upper room at the corner."
- 1JN.5.13.s1 en B: "I have written these things to you so that you may know that you have eternal life—you who believe in the name of the Son of God." -> "I have written these things to you who believe in the name of the Son of God, so that you may know that you have eternal life."
- 2TI.4.1.s1 en B: "I solemnly charge you in the presence of God and of {{christos:Christ|the Messiah}} Jesus, who will judge the living and the dead, and in view of {{deity_pronoun:his|His}} appearing and {{deity_pronoun:his|His}} kingdom:" -> "Before God and {{christos:Christ|the Messiah}} Jesus, who is going to judge the living and the dead, and by {{deity_pronoun:his|His}} appearing and {{deity_pronoun:his|His}} kingdom, I solemnly charge you:"
- GEN.9.15.s1 en B: "I will remember {{deity_pronoun:my|My}} covenant between {{deity_pronoun:me|Me}} and you and every living creature of every kind. Never again will the waters become a flood to destroy all life." -> "I will remember {{deity_pronoun:my|My}} covenant between {{deity_pronoun:me|Me}} and you and all living creatures of every kind, and never again will the waters turn into a flood that destroys all life."
- MAT.8.9.s1 en B: "I myself am a man under authority, with soldiers under me. I tell one, 'Go,' and he goes, and another, 'Come,' and he comes. I tell my servant, 'Do this,' and he does it."" -> "I too am a man placed under authority, and I have soldiers under me. I say to one, 'Go,' and he goes; to another, 'Come,' and he comes; and to my servant, 'Do this,' and he does it.""
- 1PE.5.10.s1 en B: "And after you have suffered for a little while, the God of all grace" -> "And when you have suffered a little while, the God of all grace"
- EXO.31.18.s1 en B: "When {{deity_pronoun:he|He}} had finished speaking with Moses on Mount Sinai, {{deity_pronoun:he|He}} gave him the two tablets of the testimony, tablets of stone inscribed by the finger of God." -> "When {{deity_pronoun:he|He}} finished speaking with Moses on Mount Sinai, {{deity_pronoun:he|He}} handed him the two tablets of the testimony, stone tablets written by the finger of God."
- EXO.40.29.s1 en B: "He set the altar of burnt offering at the entrance to the tabernacle, the tent of meeting, and offered on it the burnt offering and the grain offering," -> "He placed the altar of burnt offering at the entrance of the tabernacle, the tent of meeting, and on it he offered up the burnt offering and the grain offering,"
- NUM.11.22.s1 en B: "If flocks and herds were slaughtered for them, would they have enough? If all the fish in the sea were caught for them, would they have enough?"" -> "Could flocks and herds be slaughtered for them and be enough? Could all the fish of the sea be gathered for them and be enough?""
- NUM.16.26.s1 en B: "He told the congregation, "Move away now from the tents of these wicked men! Do not touch anything that belongs to them," -> "He said to the congregation, "Get away from the tents of these wicked men! Touch nothing of theirs,"
- NUM.19.4.s1 en B: "Eleazar the priest is to take some of its blood on his finger and sprinkle it seven times toward the front of the tent of meeting." -> "Eleazar the priest is to dip his finger in its blood and sprinkle some of it seven times toward the front of the tent of meeting."
- NUM.4.33.s1 en B: "This is the service of the Merarite clans, all their work at the tent of meeting, under the direction of Ithamar son of Aaron the priest."" -> "This is the work of the clans of the Merarites, all their service at the tent of meeting, overseen by Ithamar son of Aaron the priest.""
- REV.4.1.s2 en B: "and I saw a throne standing in heaven, with someone seated on it. \v 3 The one seated there looked like jasper and carnelian," -> "and there in heaven stood a throne, and someone was sitting on the throne. \v 3 The one sitting there shone like jasper and carnelian,"
- 1JN.5.13.s1 en B: "I have written these things to you who believe in the name of the Son of God, so that you may know that you have eternal life." -> "I have written this to you who believe in the name of the Son of God, so that you may be sure you have eternal life."
- GEN.7.4.s1 en B: "Seven days from now I will send rain on the earth for forty days and forty nights," -> "Seven days from now I am going to make it rain on the earth forty days and forty nights,"
- DEU.13.6.s1 en B: "He has tried to turn you aside from the way" -> "He wanted to drive you off the road"
- EXO.13.21.s1 es B: "iba delante de ellos, de día en una columna de nube para guiarlos por el camino, y de noche en una columna de fuego para alumbrarles el camino." -> "los precedía: de día, en una columna de nube que les mostraba el camino; de noche, en una columna de fuego que les daba luz."
- REV.7.15.s1 es B: "Por eso están delante del trono de Dios y {{deity_pronoun:le|Le}} sirven día y noche en {{deity_pronoun:su|Su}} templo, y el que está sentado en el trono" -> "Por eso se encuentran ante el trono de Dios y {{deity_pronoun:le|Le}} rinden culto día y noche en {{deity_pronoun:su|Su}} templo, y el que se sienta en el trono"
- 2CH.36.23.s1 es B: "me ha dado todos los reinos de la tierra, y {{deity_pronoun:él|Él}} me ha encargado que {{deity_pronoun:le|Le}} edifique" -> "ha puesto en mis manos todos los reinos de la tierra, y {{deity_pronoun:él|Él}} me ha mandado que {{deity_pronoun:le|Le}} construya"

After the rewrite no sentence in this list shares a run of more than 16 words with the BSB at Balanced, except where the Hebrew fixes the wording (a formula or a list).

