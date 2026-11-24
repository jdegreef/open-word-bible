# Indonesian review plan

A short brief for the first people reviewing the Indonesian Open Word Bible:
which books to review first, how review works in the admin, what an approval
covers, the choices already settled, and the known places that need a closer
look. The book-wide choices to settle first are in the
[Indonesian review checklist](id-review-checklist.md). This page does not
repeat them.

## Ringkasan (untuk para peninjau)

- **Urutan kerja:** Matius, Markus, Lukas, Yohanes; lalu Kisah Para Rasul dan
  Roma; lalu Kejadian, Mazmur, Yesaya; lalu kitab-kitab lain. Satu peninjau
  mengerjakan satu kitab pada satu waktu, sesuai penugasan di admin.
- **Di admin:** buka *My review*, lalu antrean (*Open the queue*). Tombol
  `a` menyetujui, `f` menandai masalah, `j`/`k` pindah ke kalimat berikut
  atau sebelumnya, `?` menampilkan semua pintasan.
- **Yang Anda setujui** adalah susunan kata bahasa Indonesia pada ketiga
  tingkat (Harfiah, Seimbang, Mudah Dibaca), bukan keputusan makna. Jika Anda
  tidak setuju dengan *makna*, tandai (*Flag*) dan jelaskan; jangan mengubah
  teksnya sendiri.
- **Pengaturan** (TUHAN/Yahweh, Kristus/Mesias, kata ganti untuk Allah)
  hanya mengubah kata, tidak pernah mengubah makna.
- Alkitab lain (TB, BIS, AYT) hanya untuk perbandingan, tidak pernah menjadi
  dasar terjemahan ini.

(Ringkasan ini juga disusun dengan bantuan AI; silakan dikoreksi.)

## 1. Order of work

1. **Matthew, Mark, Luke, John:** the most-read books; they set Jesus's
   speech and the Christ span for the rest.
2. **Acts and Romans:** speeches and letters, *saya* / *aku*, *kita* / *kami*.
3. **Genesis, Psalms, Isaiah:** the divine name, poetry, the quoted passages.
4. **The rest**, in any order the team chooses.

One book per reviewer at a time. An editor or super admin assigns it in the
admin: **Team & access → Review assignments** (or the **Review
assignments** page): reviewer, layer *Indonesian wording*, book, an optional
chapter range, an optional due date and a note. An assignment is done when
every sentence in it is approved and overdue when its date passes first.

## 2. How to review in the admin

Sign in at <https://openwordbible.org/admin/> with the **Language reviewer**
role for Indonesian (a super admin grants it in Team & access).

**My review** is the start page: your layer's counts, what is assigned to
you (progress, due date), your open flags, what has changed since you
approved it, the checks in the books in progress, and each book's progress.

**The queue** (*Open the queue*, or Review → *Indonesian wording*) lists
sentences in Bible order. Filter by book and by state: *To review*, *Not
reviewed*, *Changed since approval*, *Flagged*, *Approved*. Open a sentence
to see the source words (hover for lemma, gloss and grammar), the literal
gloss, the Indonesian at L, B and R, the meaning decisions and the
Indonesian decisions, and the review trail.

Keys on a sentence: `a` approve and open the next to review; `f` flag
(type what is wrong in the note, then Ctrl Enter or ⌘ Enter); `j` / `k`
next / previous in the queue; `/` search; `?` all shortcuts. The message
after an approval or flag offers *Undo* (the server allows it for ten
minutes). *Comment* adds a note without changing the state.

**Bulk review.** In the queue, tick sentences (shift-click ticks a range)
and use *Approve selected* or *Flag selected* (a flag needs a note). Each
chapter heading has *Approve the rest of [chapter]…*: it first says how many
sentences that is, then approves every sentence in the chapter not yet
approved. **Flagged sentences are skipped**, so they are reviewed one by
one. Use bulk approval only for sentences you have read.

**Word diffs since approval.** Each approval keeps the exact text approved.
If the sentence changes later it returns to the queue as *Changed since
approval*, and My review (and the verse inspector's *Since approval*) shows
the change word by word, approved → now, with any decisions added, changed
or removed. Read the diff, then approve again or flag.

**Checks** (Quality → Checks, Indonesian; the books in progress also show
in My review) lists heuristics that never block anything: *footnotes and
verses at odds* (a footnoted meaning decision chooses one reading, but the
verse words its alternative or lacks the choice's words), and *terms
glossary* hits (a verse using a form the glossary rules out or gives only as
an alternative, and glossary entries that conflict with each other).

**Asking for a change.** Flag the sentence with the level(s), what is wrong
and the Indonesian you propose. A flag stays open until the sentence is
approved again. Editors see open flags in *Reviewer flags* and can file the
change from the **verse inspector** with *Request a fix* (pick language and
levels, say what should change and why). That files a GitHub issue that a
Claude session works into a pull request. A reviewer who is also an editor
gets *Request a fix in the verse inspector* on the sentence page.
**Uncertain decisions** (Quality) lists every Indonesian decision marked
uncertain.

## 3. What an approval covers

- **You approve the Indonesian wording** of a sentence, at all three
  levels: **Harfiah** (L), **Seimbang** (B) and **Mudah Dibaca** (R),
  together with its Indonesian rendering decisions. Your name and a digest
  of what you approved are recorded.
- **You do not approve the meaning.** The meaning decisions (what the Hebrew
  or Greek says) are shared by every language and reviewed by scholars. If
  you think a meaning decision is wrong, **flag it** and explain; do not
  reword the Indonesian to say something else.
- **Settings change wording, never meaning.** `{{divine_name:TUHAN|Yahweh}}`,
  `{{christos:Kristus|Mesias}}`, the capitalised pronouns for God
  (`{{deity_pronoun:aku|Aku}}`, `-{{deity_pronoun:nya|Nya}}`), units and
  the few gender spans each let a reader choose a form of the same meaning.
  Check both forms read well; a disagreement about meaning is a flag, not a
  setting.
- Records stay `ai_draft` until a named reviewer approves them. Nothing is
  marked reviewed by Claude.

## 4. Settled choices to know

These are decided (`docs/indonesian-style.md`, "Style"; `docs/indonesian-terms.md`,
"Terms"). Changing one means changing the doc and every passage drafted
under it, not one verse; raise it with the team.

- **kebenaran** for both truth and righteousness (Style §7; Terms §2).
  Where truth stands right beside righteousness, truth is **kejujuran**
  (Psalm 45:5 *kejujuran ... kebenaran*). Isaiah 48:1 L, Ephesians 5:9 B and
  6:14 still say *keadilan* there and are being brought in line. *keadilan*
  is justice (*mishpat*), and righteousness only where a meaning decision
  says court justice or just rule.
- **The -Nya form** for God (*firman-Nya*; *Dia*, never *Ia*) in the
  deity_pronoun span, but plain at the start of a sentence (Style §4);
  **Allah** for God at every level; **kalian** for plural "you" (Style §5).
- **perhimpunan** (*qahal*) and **umat** (*edah*), **never *jemaah***;
  the church is *jemaat* (Terms §2).
- **bupati** for the Persian-era governor (*pechah*); **gubernur** only for
  the Roman governor (Terms §2).
- **si Penuduh** for "the satan" in Job 1–2 and Zechariah 3, a title, not a
  name; *Iblis* for *diabolos*; *Satan* where it is a name (1 Chronicles 21:1).
- **sy for Hebrew "sh"** in names (*Syalum*, *Syemaya*) and **one spelling
  per name across books** (Terms §13); Hiram / Huram and Syama / Syimea stay
  apart because the Hebrew differs.
- **Yunia** in Romans 16:7, a woman, as the meaning decision reads it.
- **Isaiah 7:14 *perempuan muda*** for *almah*, footnoted: the note says
  the Septuagint and Matthew 1:23 read "virgin". Matthew 1:23 says *anak
  dara*, and its footnote explains the Hebrew of Isaiah.
- **Isaiah 9:5:** the titles follow the project's fresh English renderings
  (B: *Perencana Hal-hal Ajaib, Allah Sang Pahlawan Perkasa, Bapa Sepanjang
  Masa, Penguasa Damai Sejahtera*), not the familiar church forms.
- **Reference Bibles** (TB, BIS, AYT and others) are for comparison only,
  never the basis for wording. Where a familiar verse matches TB clause for
  clause, flag it (Style §1).

## 5. Known items worth a closer look

From the drafters' and footnote translators' notes, checked against main
after the consistency pass (#1237, #1238, #1240, #1241), which fixed the
rest. "(u)" means the Indonesian decision is marked uncertain.

**Gospels**
- Matthew 5:32; 19:9: *porneia* is *perzinaan* / *zina*, the root of
  *berzina* ("commit adultery") beside it.
- Matthew 6:27: *satu hasta* (L), *satu jam* (B, R) added to life (u).
- Matthew 24:51: L *membunuh dia* (kill), B *memotong-motong* (cut up).
- Matthew and John, Readable: *Bait Allah* for the temple, where the
  glossary gives *rumah Allah* (R). Decide whether to make them uniform.
- Luke 5:39 B *Yang tua lebih baik* (better), English "good"; 24:3 B
  *mayat Tuhan Yesus*, English Balanced only "no body".
- John 8:24, 8:28, 13:19: *Akulah Dia* for "I am" (u).

**Acts and letters**
- Acts 5:37 R says the Romans took the census; the text names no one.
- Acts 19:9 B: *di depan jemaah* for the crowd, against "never *jemaah*".
- Acts 26:2–7: Paul says *saya*; the king is *Tuanku* / *Baginda* (u).
- 2 Corinthians 3:7: *memudar* for the glory "being set aside" (u).
- Titus 1:6 B: *setia kepada istrinya yang satu* interprets "husband of
  one wife".
- Hebrews 2:7 B *untuk sesaat lebih rendah* (for a while), English "a
  little lower"; 12:7 B "endure" as a command (*harus tabah*); 12:18
  *sangkakala*, R names *Gunung Sinai* (u).
- James 2:1 B: a command (*janganlah*) where the English keeps the
  question; 5:3 B joins "like fire" to devouring the flesh.
- 1 Peter 3:7: *kaum yang lebih lemah* for "the weaker vessel" (u).
- 2 Peter 1:1 B: *keadilan* for God's righteousness, by its meaning
  decision (u).

**Revelation**
- 2:9; 3:9: *jemaah Iblis*, against "never *jemaah*" (u).
- 9:13 B *keempat tanduk* (four horns), English "the horns"; 22:21 B
  *kalian semua*, English "everyone".
- 14:4: *murni* (L, B), *murni, seperti perawan* (R) for "virgins" (u).

**Genesis to Joshua**
- Genesis 37:28: the unclear "they" kept (u).
- Genesis 41:10 B and other speech to Pharaoh: *hamba* as "I", which Style
  §5 keeps to Literal.
- Exodus 20:26 *aurat* (u) and 28:42 *ketelanjangan*, the same nakedness.
- Exodus 23:28 B: `{{divine_name:ALLAH|Yahweh}}ku` where the English says
  "I"; a bug, being fixed.

**Judges to 2 Samuel**
- Judges 6 and 13: the angel of the LORD takes God's pronouns in 6, a
  messenger's in 13; check where the line falls.
- Judges 11:31 B *apa pun* (whatever), English "whoever or whatever".
- Judges 15:4 *serigala* for foxes; the glossary is split between
  *serigala* and *anjing hutan* for the jackal.
- Judges 19: read the assault scene for tone and register.
- 1 Samuel 8:9 *hak-hak raja* for "the ways of the king"; 22:14 David's post
  in the guard differs at each level (u); 27:10 B asks "where", the English
  "Did you not ...?".
- 2 Samuel 2:9: *orang Asyuri* (Ashurites) reads as Assyrians (u).
- 2 Samuel 7:11 *keluarga* (B, R) against 1 Chronicles 17:10 *rumah* for
  the house the LORD builds (both u).
- 2 Samuel 21:4 L: a statement where B and R ask (u); 21:6, 9, 13 R
  describe the impaling as hanging the bodies on a pole.
- 2 Samuel 23:31 *orang Araba*, 1 Chronicles 11:32 *orang Arbat* (the
  Arbathite).

**Kings, Chronicles, Esther, Job**
- 1 Kings 3:9 *memimpin* (B, R) for "judge"; 15:2 *Abisyalom* (u); 19:10
  *sangat giat bekerja* for "very zealous" (u); 19:12 *bunyi keheningan
  yang tipis* (L); 22:8 *Mikhaya* (u).
- Joram / Jehoram are both *Yoram*; Joash / Jehoash both *Yoas*.
- 1 Chronicles 1:48 *Saul* for the Edomite Shaul (u); 20:3 *memotong ...
  dengan gergaji* against 2 Samuel 12:31 *dipekerjakannya* (u).
- 2 Chronicles 7:14: reworded after a look at the familiar wording; check it
  does not echo TB (u). 9:5; 24:6 *engkau* to Solomon and Jehoiada (u).
  26:22 *Yesaya anak Amos* for Amoz reads as the prophet Amos (u).
- Esther 5:14 and after: *tiang* (L), *tiang gantungan* (B, R).
- Job 13:15 (u), 19:25 *Penebusku* (u), 42:6 *menyesal* (u).

**Poetry and wisdom**
- Psalms 2 and 45: the king takes God's pronoun span at every level (u);
  45:7 *Takhta-Mu, ya Allah* (u); 50:1 *Yang Mahakuasa* for *El* (u).
- Psalm 80:18 *anak manusia* lowercase (u); 91:14–16 singular *ia*, English
  plural; 91:14 *Kuluputkan* without a span.
- Proverbs 8:22 *menjadikan* (B, R) (u); 14:31; 24:12 *Dia yang
  menciptakan*, *Dia yang menimbang hati* capitalised outside a span (u);
  31:10 *istri yang cakap* matches TB (u).
- Ecclesiastes 1:1 *Kohelet* (L), *sang Pengajar* (B, R); 1:2 *napas* for
  *hevel* through the book (both u). Song of Songs 2:1 *bunga krokus* (u).

**Prophets**
- Isaiah 22:11: *Pembuatnya*, *Dia* capitalised as God; English lowercase.
- Jeremiah 7:18: *ratu langit* (u).
- Ezekiel 1:4 and after *ambar* (L) for the gleaming metal (u); 4:9 *sekoi*
  for spelt, millet in common speech, where Exodus says *gandum spelt* (u);
  8:16 *Bait Suci* (B) for the *hekhal* (u); 45:11 litres in the units
  span (u).

**Open glossary pairs**, one form each to choose: *juru tenung* / *tukang
tenung*; *menumpas* / *mengkhususkan untuk dimusnahkan*; *mentahbiskan* /
*menahbiskan*; *kerja paksa* / *pekerja rodi*; *pencatat sejarah* / *juru
catat* / *bentara*; *pengatur* / *para pejabat*; *pemuka* / *para
bangsawan*; *sukat* / *sea*.

**Left on purpose** because the English level says the same (#1237): 1 Kings
14:10, 21:21 and 2 Kings 9:8 (B, R); Psalm 68:24 B; Hosea 13:5 (B, R); Joel
4:21 B; *hamba* in Philippians 1:1, 2 Peter 1:1, Jude 1 (B, R). Raise the
English first if you disagree.
