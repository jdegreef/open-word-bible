# Text-variant footnotes: what changed

Item 20 of the consistency audits. `docs/text-variants.md` is the policy and `python3 scripts/variants.py` the check; `--fix` set the flags below. Before the fix, 2,742 text_variant decisions: 1,733 with a footnote, 1,009 without, and 448 breaking the policy.

- Footnote added: 89 decisions (a verse added or left out, a well-known English Bible or the New Testament following the other reading, or a reading that changes the sense, such as an ancient translation reading another Hebrew word).
- Footnote removed: 333 decisions whose reason says the sense is the same, or that concern spelling or a written and read form only. The decision stays in the reasoning panel.
- Psalms: 26 changes written to `pending-psalms-patches-b.jsonl` (Psalm 105:27 among them, to match 105:22).
- Not judged by the check, left as written: New Testament manuscript differences whose reason does not say what they change, and hard texts with no other reading.

## By book

| Book | Added | Removed |
|---|---|---|
| 1CH | 2 | 17 |
| 1CO | 0 | 5 |
| 1JN | 0 | 2 |
| 1KI | 3 | 11 |
| 1PE | 0 | 3 |
| 1SA | 6 | 9 |
| 1TH | 1 | 0 |
| 2CH | 1 | 6 |
| 2CO | 3 | 2 |
| 2JN | 0 | 1 |
| 2KI | 0 | 14 |
| 2PE | 0 | 5 |
| 2SA | 4 | 22 |
| ACT | 0 | 8 |
| AMO | 0 | 3 |
| COL | 0 | 1 |
| DAN | 2 | 0 |
| DEU | 2 | 8 |
| ECC | 2 | 1 |
| EPH | 0 | 5 |
| EXO | 0 | 4 |
| EZK | 17 | 8 |
| EZR | 2 | 3 |
| GAL | 1 | 4 |
| GEN | 1 | 9 |
| HAB | 0 | 1 |
| HAG | 1 | 0 |
| HEB | 3 | 1 |
| HOS | 3 | 2 |
| ISA | 1 | 26 |
| JAS | 0 | 3 |
| JDG | 2 | 5 |
| JER | 20 | 23 |
| JHN | 1 | 29 |
| JOB | 2 | 11 |
| JON | 1 | 0 |
| JOS | 1 | 11 |
| LAM | 2 | 1 |
| LEV | 0 | 7 |
| LUK | 2 | 14 |
| MAL | 0 | 1 |
| MAT | 1 | 7 |
| MIC | 0 | 4 |
| NAM | 0 | 1 |
| NEH | 1 | 0 |
| NUM | 1 | 7 |
| PHP | 0 | 2 |
| PRO | 0 | 8 |
| ROM | 0 | 11 |
| RUT | 0 | 4 |
| ZEC | 0 | 3 |

## Decisions changed

Added: 1CH.22.7.s1 m1, 1CH.9.4.s1 m1, 1KI.1.48.s1 m2, 1KI.19.2.s1 m4, 1KI.7.45.s1 m2, 1SA.10.12.s1 m2, 1SA.10.13.s1 m1, 1SA.14.24.s1 m4, 1SA.14.42.s1 m2, 1SA.2.16.s1 m1, 1SA.25.11.s1 m3, 1TH.5.4.s1 m2, 2CH.34.22.s1 m1, 2CO.12.11.s1 m4, 2CO.12.19.s1 m2, 2CO.13.13.s1 m6, 2SA.17.28.s1 m1, 2SA.21.9.s1 m4, 2SA.21.14.s1 m2, 2SA.3.8.s1 m2, DAN.3.7.s1 m1, DAN.5.3.s1 m1, DEU.29.27.s1 m4, DEU.32.6.s1 m1, ECC.9.1.s1 m3, ECC.9.14.s1 m2, EZK.18.14.s1 m1, EZK.24.14.s1 m1, EZK.25.8.s1 m2, EZK.28.16.s1 m3, EZK.32.9.s1 m1, EZK.32.25.s1 m1, EZK.35.15.s1 m3, EZK.36.11.s1 m2, EZK.38.21.s1 m2, EZK.39.28.s1 m2, EZK.4.9.s1 m2, EZK.42.20.s1 m2, EZK.43.11.s1 m1, EZK.44.19.s1 m2, EZK.46.22.s1 m2, EZK.48.13.s1 m1, EZK.7.2.s1 m3, EZR.10.34.s1 m1, EZR.2.66.s1 m1, GAL.5.1.s1 m1, GEN.36.6.s1 m1, HAG.1.10.s1 m3, HEB.12.7.s1 m2, HEB.13.9.s1 m1, HEB.6.3.s1 m2, HOS.10.12.s1 m5, HOS.10.13.s1 m2, HOS.13.4.s1 m3, ISA.25.10.s1 m3, JDG.16.14.s1 m1, JDG.2.1.s1 m3, JER.10.10.s1 m4, JER.19.1.s1 m3, JER.27.17.s1 m3, JER.27.19.s1 m3, JER.27.22.s1 m3, JER.30.10.s1 m3, JER.30.15.s1 m2, JER.30.22.s1 m2, JER.36.1.s1 m2, JER.36.2.s1 m4, JER.37.19.s1 m1, JER.38.11.s1 m1, JER.38.16.s1 m4, JER.39.11.s1 m4, JER.39.13.s1 m4, JER.39.14.s1 m5, JER.43.2.s1 m3, JER.45.5.s1 m4, JER.51.49.s1 m2, JER.7.1.s1 m2, JHN.10.38.s1 m5, JOB.17.15.s1 m2, JOB.38.13.s1 m3, JON.1.8.s1 m1, JOS.20.5.s1 m1, LAM.1.4.s1 m4, LAM.1.16.s1 m1, LUK.22.20.s1 m1, LUK.5.39.s1 m2, MAT.9.34.s1 m2, NEH.10.20.s1 m1, NUM.21.32.s1 m2.

Removed: 1CH.1.22.s1 m1, 1CH.1.42.s1 m1, 1CH.11.11.s1 m2, 1CH.12.19.s1 m2, 1CH.20.5.s1 m2, 1CH.23.9.s1 m1, 1CH.26.25.s1 m2, 1CH.26.28.s1 m3, 1CH.27.29.s1 m1, 1CH.4.7.s1 m1, 1CH.4.41.s1 m2, 1CH.6.11.s1 m1, 1CH.6.13.s1 m1, 1CH.6.43.s1 m1, 1CH.7.1.s1 m2, 1CH.7.10.s1 m1, 1CH.7.31.s1 m1, 1CO.14.34.s1 m1, 1CO.14.37.s1 m1, 1CO.15.49.s1 m1, 1CO.5.1.s1 m3, 1CO.5.7.s2 m3, 1JN.3.14.s1 m4, 1JN.4.2.s1 m5, 1KI.1.18.s1 m1, 1KI.1.20.s1 m1, 1KI.1.27.s1 m2, 1KI.13.12.s1 m1, 1KI.13.34.s1 m1, 1KI.15.15.s1 m1, 1KI.19.3.s1 m1, 1KI.2.22.s1 m3, 1KI.5.17.s1 m1, 1KI.8.16.s1 m2, 1KI.9.18.s1 m1, 1PE.1.24.s1 m4, 1PE.3.14.s2 m8, 1PE.3.21.s1 m2, 1SA.10.19.s1 m2, 1SA.2.10.s1 m2, 1SA.23.7.s1 m2, 1SA.25.3.s1 m4, 1SA.27.8.s1 m2, 1SA.3.2.s1 m1, 1SA.4.13.s1 m1, 1SA.6.4.s1 m2, 1SA.9.16.s1 m4, 2CH.13.19.s1 m3, 2CH.28.3.s1 m2, 2CH.33.16.s1 m1, 2CH.34.6.s1 m1, 2CH.34.9.s1 m3, 2CH.6.42.s1 m2, 2CO.10.10.s1 m3, 2CO.13.2.s1 m6, 2JN.1.12.s1 m3, 2KI.14.2.s1 m2, 2KI.14.13.s1 m2, 2KI.16.6.s1 m1, 2KI.18.27.s1 m2, 2KI.19.23.s1 m4, 2KI.19.31.s1 m3, 2KI.19.37.s1 m4, 2KI.20.4.s1 m1, 2KI.23.10.s1 m2, 2KI.23.33.s1 m1, 2KI.23.36.s1 m1, 2KI.3.24.s1 m1, 2KI.5.12.s1 m1, 2KI.7.13.s1 m1, 2PE.1.12.s1 m1, 2PE.1.17.s1 m4, 2PE.2.4.s1 m2, 2PE.2.4.s1 m8, 2PE.2.12.s1 m3, 2SA.10.9.s1 m2, 2SA.11.1.s1 m1, 2SA.12.9.s1 m1, 2SA.12.24.s1 m1, 2SA.12.31.s1 m2, 2SA.14.4.s1 m1, 2SA.14.30.s1 m3, 2SA.15.28.s1 m1, 2SA.16.10.s1 m3, 2SA.17.3.s1 m1, 2SA.17.16.s1 m1, 2SA.18.12.s1 m1, 2SA.18.13.s1 m1, 2SA.21.16.s1 m1, 2SA.22.51.s1 m1, 2SA.23.8.s1 m3, 2SA.23.18.s1 m1, 2SA.24.16.s1 m3, 2SA.3.18.s1 m1, 2SA.6.2.s1 m2, 2SA.6.2.s1 m3, 2SA.9.11.s1 m1, ACT.10.36.s1 m2, ACT.13.44.s1 m2, ACT.19.40.s1 m2, ACT.23.20.s1 m1, ACT.25.13.s1 m3, ACT.26.16.s1 m6, ACT.27.39.s1 m2, ACT.7.43.s1 m3, AMO.6.12.s1 m1, AMO.7.4.s1 m1, AMO.8.8.s1 m1, COL.3.4.s1 m1, DEU.13.7.s1 m1, DEU.2.33.s1 m1, DEU.21.7.s1 m1, DEU.29.28.s1 m3, DEU.33.2.s1 m3, DEU.4.37.s1 m1, DEU.5.10.s1 m1, DEU.8.2.s1 m3, ECC.7.27.s1 m2, EPH.4.9.s1 m3, EPH.4.32.s1 m4, EPH.5.15.s1 m3, EPH.5.17.s1 m2, EPH.5.22.s1 m1, EXO.17.11.s1 m2, EXO.18.6.s1 m2, EXO.21.8.s1 m1, EXO.32.19.s1 m2, EZK.23.42.s1 m1, EZK.36.14.s1 m1, EZK.36.15.s1 m1, EZK.42.16.s1 m1, EZK.43.7.s1 m4, EZK.44.7.s1 m3, EZK.44.28.s1 m2, EZK.8.2.s1 m2, EZR.4.9.s1 m4, EZR.8.14.s1 m1, EZR.8.17.s1 m1, GAL.1.3.s1 m1, GAL.1.15.s1 m1, GAL.3.21.s1 m1, GAL.4.7.s1 m1, GEN.24.33.s1 m1, GEN.30.11.s1 m1, GEN.36.2.s1 m2, GEN.36.5.s1 m1, GEN.36.26.s1 m1, GEN.37.36.s1 m1, GEN.46.13.s1 m1, GEN.47.5.s1 m1, GEN.49.25.s1 m1, HAB.3.14.s1 m1, HEB.1.11.s1 m2, HOS.11.3.s1 m2, HOS.6.5.s1 m2, ISA.11.1.s1 m3, ISA.11.6.s1 m3, ISA.13.16.s1 m1, ISA.13.22.s1 m1, ISA.14.4.s1 m2, ISA.14.30.s1 m2, ISA.26.16.s1 m1, ISA.30.5.s1 m1, ISA.35.8.s1 m3, ISA.36.5.s1 m1, ISA.36.12.s1 m1, ISA.42.20.s1 m1, ISA.44.24.s1 m1, ISA.49.5.s1 m1, ISA.52.2.s1 m2, ISA.52.5.s1 m1, ISA.53.11.s1 m1, ISA.54.9.s1 m2, ISA.55.9.s1 m2, ISA.60.19.s1 m1, ISA.60.21.s1 m1, ISA.65.1.s1 m3, ISA.66.17.s1 m2, ISA.7.11.s1 m2, ISA.8.11.s1 m2, ISA.9.6.s1 m1, JAS.2.2.s1 m3, JAS.4.14.s1 m2, JAS.5.4.s1 m2, JDG.15.6.s1 m3, JDG.16.2.s1 m1, JDG.16.18.s1 m1, JDG.18.30.s1 m1, JDG.20.48.s1 m1, JER.11.14.s1 m3, JER.16.7.s1 m1, JER.17.8.s1 m2, JER.2.11.s1 m2, JER.2.20.s1 m1, JER.25.38.s1 m2, JER.26.10.s1 m3, JER.28.1.s1 m2, JER.3.2.s1 m1, JER.31.21.s1 m1, JER.31.38.s1 m1, JER.31.40.s1 m2, JER.33.3.s1 m1, JER.41.17.s1 m1, JER.42.20.s1 m1, JER.49.25.s1 m1, JER.49.36.s1 m2, JER.50.6.s1 m2, JER.51.34.s1 m2, JER.7.3.s1 m2, JER.7.18.s1 m2, JER.8.3.s1 m3, JER.9.7.s1 m1, JHN.10.14.s1 m4, JHN.10.16.s1 m5, JHN.10.34.s1 m1, JHN.12.17.s1 m1, JHN.12.31.s1 m4, JHN.13.24.s1 m1, JHN.13.26.s1 m3, JHN.13.32.s1 m1, JHN.14.28.s2 m3, JHN.15.8.s1 m1, JHN.16.3.s1 m3, JHN.16.22.s1 m3, JHN.16.27.s1 m4, JHN.17.1.s1 m3, JHN.17.20.s1 m5, JHN.17.24.s1 m2, JHN.19.20.s1 m4, JHN.21.16.s3 m2, JHN.21.17.s4 m2, JHN.5.2.s1 m2, JHN.5.44.s1 m3, JHN.6.47.s1 m1, JHN.6.58.s1 m1, JHN.7.46.s1 m1, JHN.8.3.s1 m4, JHN.8.16.s1 m1, JHN.8.34.s1 m3, JHN.8.54.s1 m2, JHN.9.27.s1 m2, JOB.10.20.s1 m1, JOB.13.15.s1 m1, JOB.19.28.s1 m2, JOB.21.13.s1 m1, JOB.22.11.s1 m1, JOB.30.22.s1 m2, JOB.33.19.s1 m3, JOB.33.28.s1 m1, JOB.41.4.s1 m1, JOB.42.2.s1 m1, JOB.6.21.s1 m1, JOS.15.28.s1 m2, JOS.15.40.s1 m1, JOS.15.52.s1 m1, JOS.15.59.s1 m1, JOS.18.12.s1 m4, JOS.18.19.s1 m3, JOS.18.24.s1 m1, JOS.3.16.s1 m1, JOS.5.1.s1 m1, JOS.6.7.s1 m1, JOS.6.18.s1 m1, LAM.3.20.s1 m2, LEV.11.21.s1 m1, LEV.15.3.s1 m2, LEV.16.1.s1 m2, LEV.21.5.s1 m3, LEV.25.30.s1 m1, LEV.7.21.s1 m2, LEV.9.22.s1 m2, LUK.10.15.s2 m3, LUK.10.38.s1 m1, LUK.12.31.s1 m1, LUK.13.27.s1 m1, LUK.15.16.s1 m2, LUK.21.19.s1 m1, LUK.23.15.s1 m1, LUK.24.32.s1 m2, LUK.24.45.s1 m5, LUK.5.17.s1 m3, LUK.5.33.s1 m1, LUK.6.1.s1 m1, LUK.7.7.s1 m4, LUK.9.54.s1 m2, MAL.1.13.s1 m2, MAT.1.6.s1 m2, MAT.10.25.s2 m2, MAT.13.9.s1 m2, MAT.13.35.s1 m3, MAT.14.24.s1 m1, MAT.14.30.s1 m1, MAT.22.44.s1 m4, MIC.6.9.s1 m1, MIC.6.10.s1 m1, MIC.6.16.s1 m4, MIC.7.19.s1 m3, NAM.2.9.s1 m1, NUM.1.14.s1 m1, NUM.14.36.s1 m1, NUM.21.30.s1 m1, NUM.24.17.s1 m7, NUM.26.39.s1 m1, NUM.3.39.s1 m1, NUM.9.16.s1 m1, PHP.1.12.s1 m6, PHP.4.23.s1 m1, PRO.17.27.s1 m1, PRO.19.7.s1 m1, PRO.20.21.s1 m1, PRO.21.29.s1 m2, PRO.23.26.s1 m1, PRO.23.31.s1 m1, PRO.26.2.s1 m1, PRO.8.16.s1 m1, ROM.10.5.s1 m2, ROM.11.17.s1 m4, ROM.12.14.s1 m1, ROM.14.12.s1 m2, ROM.15.7.s1 m2, ROM.15.18.s1 m4, ROM.15.30.s1 m5, ROM.5.1.s1 m1, ROM.5.1.s1 m5, ROM.7.25.s1 m2, ROM.8.26.s1 m5, RUT.3.3.s1 m1, RUT.3.4.s1 m2, RUT.3.12.s1 m1, RUT.4.5.s1 m1, ZEC.13.5.s1 m2, ZEC.14.6.s1 m1, ZEC.5.6.s1 m2.
