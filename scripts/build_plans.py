"""Make the longer reading plans in data/plans.json from their outlines.

    python3 scripts/build_plans.py            # rewrite data/plans.json
    python3 scripts/build_plans.py --check    # exit 1 if it would change

The plans written by hand (a book a chapter a day) are kept as they are.
The plans below are made here: each is an outline (which chapters, in what
order, in how many days) and the days are cut from it so that each day's
reading is as close as it can be to an even share of verses, counting each
chapter's verses in content/. A day is always whole chapters, so a long
chapter (Psalm 119) is a day on its own. Running it again gives the same
days unless the outlines, or the verses counted, change.
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import refs  # noqa: E402

PLANS = ROOT / "data" / "plans.json"
BOOKS = json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))["books"]
OT = refs.BOOK_CODES[:39]
NT = refs.BOOK_CODES[39:]


def verse_counts():
    """{(book, chapter): verses}, counted from the records in content/."""
    verses = defaultdict(set)
    for path in sorted((ROOT / "content").glob("*/*.json")):
        for r in json.loads(path.read_text(encoding="utf-8"))["records"]:
            for vid in r["refs"]:
                ref = refs.parse(vid)
                verses[ref.book, ref.chapter].add(ref.verse)
    return {bc: len(vs) for bc, vs in verses.items()}


def ch(book, first=1, last=None):
    """Chapters first..last of book (the whole book by default)."""
    last = BOOKS[book]["chapters"] if last is None else last
    return [(book, c) for c in range(first, last + 1)]


def books(codes):
    return [bc for b in codes for bc in ch(b)]


def psalms(*numbers):
    return [("PSA", n) for n in numbers]


def split(chapters, days, weight, sizes=None):
    """Cut chapters, in order, into days whole chapters each, the days'
    verse loads as even as they can be (least sum of squared differences
    from the mean). sizes, if given, bounds the chapters in a day."""
    n = len(chapters)
    assert days <= n, (days, n)
    lo, hi = sizes or (1, max(8, 4 * -(-n // days)))
    total = [0]
    for bc in chapters:
        total.append(total[-1] + weight[bc])
    mean = total[-1] / days
    inf = float("inf")
    # best[d][i]: the least cost of reading the first i chapters in d days.
    best = [[inf] * (n + 1) for _ in range(days + 1)]
    back = [[0] * (n + 1) for _ in range(days + 1)]
    best[0][0] = 0
    for d in range(1, days + 1):
        for i in range(d, n - (days - d) + 1):
            for j in range(max(d - 1, i - hi), i - lo + 1):
                if best[d - 1][j] == inf:
                    continue
                cost = best[d - 1][j] + (total[i] - total[j] - mean) ** 2
                if cost < best[d][i]:
                    best[d][i], back[d][i] = cost, j
    assert best[days][n] < inf, "no way to cut these chapters into these days"
    cuts, i = [], n
    for d in range(days, 0, -1):
        cuts.append(i)
        i = back[d][i]
    cuts.append(0)
    cuts.reverse()
    return [chapters[a:b] for a, b in zip(cuts, cuts[1:])]


def psalms_and_proverbs(weight):
    """31 days: a chapter of Proverbs and a run of psalms each day, about
    five, Psalm 119 alone on its day with that day's Proverbs."""
    before, after = psalms(*range(1, 119)), psalms(*range(120, 151))
    # Psalm 119's day falls where its place in the Psalter puts it: the
    # psalms before it get their share of the other 30 days by count.
    k = round(30 * len(before) / (len(before) + len(after)))
    groups = split(before, k, weight, (3, 7)) + [[("PSA", 119)]] + split(after, 30 - k, weight, (3, 7))
    return [g + [("PRO", d)] for d, g in enumerate(groups, 1)]


# The chronological plan's order (see its description below).
def chronological():
    seq = []
    add = seq.extend
    add(ch("GEN", 1, 11) + ch("JOB") + ch("GEN", 12, 50))
    add(ch("EXO") + ch("LEV") + ch("NUM") + ch("DEU") + psalms(90))
    add(ch("JOS") + ch("JDG") + ch("RUT"))
    add(ch("1SA", 1, 19) + psalms(59) + ch("1SA", 20, 21) + psalms(34, 56) + ch("1SA", 22, 22) + psalms(52, 57, 142)
        + ch("1SA", 23, 23) + psalms(54) + ch("1SA", 24, 31) + ch("1CH", 1, 10))
    add(ch("2SA", 1, 5) + ch("1CH", 11, 12) + ch("2SA", 6, 6) + ch("1CH", 13, 16) + psalms(96, 105, 106)
        + ch("2SA", 7, 7) + ch("1CH", 17, 17) + ch("2SA", 8, 9) + ch("1CH", 18, 18) + psalms(60)
        + ch("2SA", 10, 10) + ch("1CH", 19, 19) + ch("2SA", 11, 12) + ch("1CH", 20, 20) + psalms(51, 32)
        + ch("2SA", 13, 15) + psalms(3, 63) + ch("2SA", 16, 22) + psalms(18) + ch("2SA", 23, 24) + ch("1CH", 21, 28))
    placed = {c for b, c in seq if b == "PSA"}
    later = {72, 127, 74, 79, 137, 126}
    add(psalms(*(n for n in range(1, 151) if n not in placed | later)))
    add(ch("1KI", 1, 2) + ch("1CH", 29, 29) + ch("2CH", 1, 1) + ch("1KI", 3, 4) + psalms(72) + ch("1KI", 5, 8)
        + ch("2CH", 2, 7) + psalms(127) + ch("1KI", 9, 10) + ch("2CH", 8, 9) + ch("PRO") + ch("SNG")
        + ch("1KI", 11, 11) + ch("ECC"))
    add(ch("1KI", 12, 14) + ch("2CH", 10, 12) + ch("1KI", 15, 15) + ch("2CH", 13, 16) + ch("1KI", 16, 22)
        + ch("2CH", 17, 20) + ch("2KI", 1, 8) + ch("2CH", 21, 21) + ch("OBA") + ch("2KI", 9, 12) + ch("2CH", 22, 24)
        + ch("JOL") + ch("2KI", 13, 14) + ch("2CH", 25, 25) + ch("JON") + ch("2KI", 15, 15) + ch("2CH", 26, 27)
        + ch("AMO") + ch("HOS") + ch("2KI", 16, 16) + ch("2CH", 28, 28) + ch("MIC") + ch("ISA", 1, 35)
        + ch("2KI", 17, 20) + ch("2CH", 29, 32) + ch("ISA", 36, 66) + ch("2KI", 21, 21) + ch("2CH", 33, 33)
        + ch("NAM") + ch("2KI", 22, 23) + ch("2CH", 34, 35) + ch("ZEP") + ch("HAB") + ch("JER", 1, 39)
        + ch("2KI", 24, 25) + ch("2CH", 36, 36) + ch("JER", 40, 52) + ch("LAM") + psalms(74, 79, 137))
    add(ch("EZK") + ch("DAN") + ch("EZR", 1, 3) + psalms(126) + ch("EZR", 4, 6) + ch("HAG") + ch("ZEC")
        + ch("EST") + ch("EZR", 7, 10) + ch("NEH") + ch("MAL"))
    add(ch("MAT") + ch("MRK") + ch("LUK") + ch("JHN"))
    add(ch("ACT", 1, 12) + ch("JAS") + ch("ACT", 13, 14) + ch("GAL") + ch("ACT", 15, 17) + ch("1TH") + ch("2TH")
        + ch("ACT", 18, 19) + ch("1CO") + ch("ACT", 20, 20) + ch("2CO") + ch("ROM") + ch("ACT", 21, 28)
        + ch("EPH") + ch("COL") + ch("PHM") + ch("PHP") + ch("1TI") + ch("TIT") + ch("1PE") + ch("HEB")
        + ch("2TI") + ch("2PE") + ch("JUD") + ch("1JN") + ch("2JN") + ch("3JN") + ch("REV"))
    return seq


CHRONOLOGICAL_ABOUT = (
    "The whole Bible in the order its events happened or, for poetry, prophecy and letters, the time they are "
    "usually dated to, on the outline most published chronological plans share. Job is read with the "
    "patriarchs, between Genesis 11 and 12, and Psalm 90 (“of Moses”) after Deuteronomy. 1–2 Samuel, 1–2 Kings "
    "and 1–2 Chronicles are interleaved event by event, Chronicles’ genealogies (1 Chronicles 1–10) at Saul’s "
    "death. Psalms whose titles name an event in David’s life are read beside it (59, 34, 56, 52, 57, 142, 54, "
    "60, 51, 32, 3, 63, 18), as are those 1 Chronicles 16 quotes (96, 105, 106); the other psalms follow David’s "
    "last years (1 Chronicles 21–28), except Psalms 72 and 127 (“of Solomon”), read in his reign, Psalms 74, 79 "
    "and 137, read at the fall of Jerusalem, and Psalm 126, read at the return. Proverbs and the Song of Songs "
    "come in Solomon’s reign and Ecclesiastes in his old age (1 Kings 11). Each prophet is read in the reign "
    "his book names or the one most often proposed: Obadiah under Jehoram, Joel under Joash, Jonah under "
    "Jeroboam II (2 Kings 14:25), Amos and Hosea under Uzziah, Micah and Isaiah 1–35 under Ahaz, Isaiah 36–66 "
    "after Hezekiah, Nahum under Manasseh, Zephaniah and Habakkuk under Josiah, Jeremiah from Josiah to the fall "
    "of Jerusalem and Lamentations after it, then Ezekiel and Daniel in the exile. Ezra 1–6 comes with Haggai "
    "and Zechariah (Ezra 5:1), Esther between Ezra 6 and 7, then Ezra 7–10, Nehemiah and Malachi. The four "
    "Gospels are read whole, one after another, since a day is whole chapters and a harmony would cut them. "
    "Acts is interleaved with Paul’s letters where they were written: James before the Jerusalem council, "
    "Galatians after Acts 14, 1–2 Thessalonians after Acts 17, 1 Corinthians after Acts 19, 2 Corinthians and "
    "Romans after Acts 20, Ephesians, Colossians, Philemon and Philippians after Acts 28; then 1 Timothy, "
    "Titus, 1 Peter, Hebrews, 2 Timothy, 2 Peter, Jude, John’s letters and Revelation. Many of these dates are "
    "debated; this is one defensible order, not the only one. Days are whole chapters, balanced by verse count.")

OT_OVERVIEW = [
    ["GEN.1"], ["GEN.3"], ["GEN.7", "GEN.9"], ["GEN.12"], ["GEN.15"], ["GEN.22"], ["GEN.28"], ["GEN.37"],
    ["GEN.45"], ["GEN.50"], ["EXO.3"], ["EXO.12"], ["EXO.14"], ["EXO.20"], ["EXO.32"], ["LEV.16"],
    ["LEV.19"], ["NUM.13", "NUM.14"], ["DEU.6"], ["DEU.30"], ["JOS.1"], ["JOS.6"], ["JOS.24"], ["JDG.2"],
    ["RUT.1", "RUT.4"], ["1SA.3"], ["1SA.16"], ["1SA.17"], ["2SA.7"], ["2SA.11", "2SA.12"],
    ["PSA.1", "PSA.23"], ["PSA.51"], ["1KI.3"], ["1KI.8"], ["1KI.12"], ["1KI.18"], ["2KI.17"],
    ["2KI.22", "2KI.23"], ["2KI.25"], ["JOB.1", "JOB.2"], ["JOB.38"], ["PRO.3"], ["ECC.3", "ECC.12"],
    ["ISA.6"], ["ISA.11"], ["ISA.40"], ["ISA.53"], ["JER.1"], ["JER.31"], ["LAM.3"], ["EZK.37"],
    ["DAN.3"], ["DAN.6"], ["HOS.11"], ["JON.3", "JON.4"], ["MIC.6"], ["EZR.1", "EZR.3"], ["NEH.8"],
    ["EST.4"], ["MAL.3"],
]


def made(weight):
    """The generated plans, in the order they follow the hand-made ones."""
    def days(chapters, n, sizes=None):
        return [[f"{b}.{c}" for b, c in day] for day in split(chapters, n, weight, sizes)]

    wisdom = books(["JOB", "PRO", "ECC", "SNG"])
    return [
        {"id": "bible-in-a-year",
         "name": {"en": "The Bible in a year", "es": "La Biblia en un año", "fr": "La Bible en un an",
                  "sw": "Biblia kwa mwaka mmoja", "vi": "Kinh Thánh trong một năm", "ko": "성경 1년 읽기",
                  "pt": "A Bíblia em um ano", "am": "መጽሐፍ ቅዱስ በአንድ ዓመት", "hi": "बाइबल एक वर्ष में",
                  "ru": "Библия за год", "uk": "Біблія за рік", "ja": "聖書を1年で"},
         "days": days(books(refs.BOOK_CODES), 365)},
        {"id": "bible-chronological",
         "name": {"en": "The Bible in a year, in time order", "es": "La Biblia en un año, en orden cronológico",
                  "fr": "La Bible en un an, dans l’ordre chronologique",
                  "sw": "Biblia kwa mwaka mmoja, kwa mpangilio wa wakati",
                  "vi": "Kinh Thánh trong một năm, theo thứ tự thời gian", "ko": "성경 1년 읽기, 연대순",
                  "pt": "A Bíblia em um ano, em ordem cronológica", "am": "መጽሐፍ ቅዱስ በአንድ ዓመት፣ በዘመን ቅደም ተከተል",
                  "hi": "बाइबल एक वर्ष में, समय के क्रम से", "ru": "Библия за год в хронологическом порядке",
                  "uk": "Біблія за рік у хронологічному порядку", "ja": "聖書を1年で、年代順に"},
         "description": CHRONOLOGICAL_ABOUT,
         "days": days(chronological(), 365)},
        {"id": "new-testament-90",
         "name": {"en": "The New Testament in 90 days", "es": "El Nuevo Testamento en 90 días",
                  "fr": "Le Nouveau Testament en 90 jours", "sw": "Agano Jipya kwa siku 90",
                  "vi": "Tân Ước trong 90 ngày", "ko": "신약 90일 읽기", "pt": "O Novo Testamento em 90 dias",
                  "am": "አዲስ ኪዳን በ90 ቀናት", "hi": "नया नियम 90 दिनों में", "ru": "Новый Завет за 90 дней",
                  "uk": "Новий Заповіт за 90 днів", "ja": "新約聖書を90日で"},
         "days": days(books(NT), 90)},
        {"id": "gospels-40",
         "name": {"en": "The four Gospels in 40 days", "es": "Los cuatro Evangelios en 40 días",
                  "fr": "Les quatre Évangiles en 40 jours", "sw": "Injili nne kwa siku 40",
                  "vi": "Bốn sách Phúc Âm trong 40 ngày", "ko": "네 복음서 40일 읽기",
                  "pt": "Os quatro Evangelhos em 40 dias", "am": "አራቱ ወንጌላት በ40 ቀናት",
                  "hi": "चारों सुसमाचार 40 दिनों में", "ru": "Четыре Евангелия за 40 дней",
                  "uk": "Чотири Євангелія за 40 днів", "ja": "四つの福音書を40日で"},
         "days": days(books(["MAT", "MRK", "LUK", "JHN"]), 40)},
        {"id": "psalms-proverbs-month",
         "name": {"en": "Psalms and Proverbs in a month", "es": "Salmos y Proverbios en un mes",
                  "fr": "Les Psaumes et les Proverbes en un mois", "sw": "Zaburi na Mithali kwa mwezi mmoja",
                  "vi": "Thi Thiên và Châm Ngôn trong một tháng", "ko": "시편과 잠언 한 달 읽기",
                  "pt": "Salmos e Provérbios em um mês", "am": "መዝሙረ ዳዊትና ምሳሌ በአንድ ወር",
                  "hi": "भजन संहिता और नीतिवचन एक महीने में", "ru": "Псалтирь и Притчи за месяц",
                  "uk": "Псалми та Приповісті за місяць", "ja": "詩編と箴言を1か月で"},
         "days": [[f"{b}.{c}" for b, c in day] for day in psalms_and_proverbs(weight)]},
        {"id": "old-testament-overview",
         "name": {"en": "The Old Testament in 60 days: the key chapters",
                  "es": "El Antiguo Testamento en 60 días: los capítulos clave",
                  "fr": "L’Ancien Testament en 60 jours : les chapitres clés",
                  "sw": "Agano la Kale kwa siku 60: sura muhimu",
                  "vi": "Cựu Ước trong 60 ngày: những chương then chốt", "ko": "구약 핵심 장 60일 읽기",
                  "pt": "O Antigo Testamento em 60 dias: os capítulos-chave",
                  "am": "ብሉይ ኪዳን በ60 ቀናት፦ ዋና ዋና ምዕራፎች", "hi": "पुराना नियम 60 दिनों में: मुख्य अध्याय",
                  "ru": "Ветхий Завет за 60 дней: главные главы",
                  "uk": "Старий Заповіт за 60 днів: ключові розділи", "ja": "旧約聖書を60日で：要となる章"},
         "days": OT_OVERVIEW},
        {"id": "wisdom-books",
         "name": {"en": "The Wisdom books in 60 days", "es": "Los libros sapienciales en 60 días",
                  "fr": "Les livres de sagesse en 60 jours", "sw": "Vitabu vya hekima kwa siku 60",
                  "vi": "Các sách Khôn Ngoan trong 60 ngày", "ko": "지혜서 60일 읽기",
                  "pt": "Os livros sapienciais em 60 dias", "am": "የጥበብ መጻሕፍት በ60 ቀናት",
                  "hi": "ज्ञान की पुस्तकें 60 दिनों में", "ru": "Книги мудрости за 60 дней",
                  "uk": "Книги мудрості за 60 днів", "ja": "知恵の書を60日で"},
         "days": days(wisdom, 60)},
    ]


def dump(data):
    """data/plans.json as it is laid out: a plan to a few lines, its days on one."""
    plans = []
    for p in data["plans"]:
        lines = [f'  {{"id": {json.dumps(p["id"])},']
        lines += [f"   {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}," for k, v in p.items() if k != "id"]
        lines[-1] = lines[-1][:-1] + "}"
        plans.append("\n".join(lines))
    return "\n".join(["{", f' "description": {json.dumps(data["description"], ensure_ascii=False)},',
                      ' "plans": [', ",\n".join(plans), " ]", "}"]) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if data/plans.json is not up to date")
    args = ap.parse_args(argv)
    old = PLANS.read_text(encoding="utf-8")
    data = json.loads(old)
    new_plans = made(verse_counts())
    ids = {p["id"] for p in new_plans}
    data["plans"] = [p for p in data["plans"] if p["id"] not in ids] + new_plans
    for p in new_plans:
        chapters = [c for day in p["days"] for c in day]
        assert len(chapters) == len(set(chapters)), p["id"]
    if p := next((p for p in new_plans if p["id"] == "bible-chronological"), None):
        whole = sorted(f"{b}.{c}" for b, c in books(refs.BOOK_CODES))
        assert sorted(c for day in p["days"] for c in day) == whole, "the chronological plan misses or repeats chapters"
    text = dump(data)
    if args.check:
        if text != old:
            print("data/plans.json is not what scripts/build_plans.py makes; run it.")
            return 1
        return 0
    PLANS.write_text(text, encoding="utf-8")
    for p in new_plans:
        print(f"{p['id']}: {len(p['days'])} days")
    return 0


if __name__ == "__main__":
    sys.exit(main())
