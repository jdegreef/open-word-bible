"""Draft furigana (data/furigana/) for Japanese renderings with a morphological
analyser, for records that have none yet.

    pip install fugashi unidic-lite
    python3 scripts/draft_furigana.py                 every book, Balanced
    python3 scripts/draft_furigana.py GEN EXO --level L
    python3 scripts/draft_furigana.py --refresh       also redraft readings that no longer fit

MeCab (UniDic) reads each word in its sentence; the reading of each kanji run
is the part of its words' readings that belongs to the kanji, without the
okurigana. On top of that, a few rules give the readings Japanese Bibles use
where everyday Japanese reads otherwise (主 しゅ, 御心 みこころ, 罪人 つみびと,
ユダヤ人 じん, この方 かた, the ritual 汚れ けがれ), and numbers with their
counters are read here (二日 ふつか, 三百 さんびゃく, 一匹 いっぴき), since UniDic
splits them by character. Against the hand-drafted readings of John it agrees
on 99% of runs. A record whose runs the analyser cannot all read is left out,
since a record's readings are all or nothing.

Readings already in data/furigana/ are kept: this only adds records, so a
reviewed reading is never redrafted (unless --refresh, and then only where
the rendering has changed so that the old readings no longer fit). The drafts
are AI drafts like any other text, to be checked by a reader of Japanese.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owb import furigana, markup  # noqa: E402

LANG = "ja"
KANJI_RUN = re.compile(f"[{furigana.KANJI}]+")
KATAKANA_WORD = re.compile(r"^[ァ-ヶー・]+$")

# Whole kanji runs that Japanese Bibles read otherwise than everyday Japanese,
# or that the analyser misreads in this text.
RUNS = {
    "主": "しゅ", "業": "わざ", "御心": "みこころ", "御名": "みな", "御前": "みまえ", "御手": "みて",
    "御国": "みくに", "御業": "みわざ", "御言葉": "みことば", "御霊": "みたま", "悪霊": "あくれい",
    "罪": "つみ", "罪人": "つみびと", "園": "その", "剣": "つるぎ", "亜麻布": "あまぬの", "安息日": "あんそくび",
    "過越祭": "すぎこしさい", "仮庵祭": "かりいおさい", "札": "ふだ", "胎": "たい", "正気": "しょうき",
    "囚人": "しゅうじん", "基": "もとい", "何時": "なんじ", "種": "たね", "初子": "ういご",
    "一人": "ひとり", "二人": "ふたり", "一晩": "ひとばん", "一粒": "ひとつぶ", "一言": "ひとこと",
    "一目": "ひとめ", "大祭司": "だいさいし", "祭司": "さいし", "祭司長": "さいしちょう",
    "律法学者": "りっぽうがくしゃ", "異邦人": "いほうじん", "幕屋": "まくや", "聖所": "せいじょ",
    "至聖所": "しせいじょ", "民": "たみ", "割礼": "かつれい", "無割礼": "むかつれい", "万軍": "ばんぐん",
    "十字架": "じゅうじか", "義人": "ぎじん", "僕": "しもべ", "荒野": "あれの", "長老": "ちょうろう",
}

DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ONES = ["", "いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう"]
NUMBER = re.compile("^[一二三四五六七八九十百千万]+")
DAYS = {"二": "ふつか", "三": "みっか", "四": "よっか", "五": "いつか", "六": "むいか", "七": "なのか",
        "八": "ようか", "九": "ここのか", "十": "とおか", "二十": "はつか", "十四": "じゅうよっか",
        "二十四": "にじゅうよっか"}
NATIVE = {"一": "ひと", "二": "ふた", "三": "みっ", "四": "よっ", "五": "いつ", "六": "むっ", "七": "なな",
          "八": "やっ", "九": "ここの"}
GEMINATE = {"いち": "いっ", "ろく": "ろっ", "はち": "はっ", "じゅう": "じゅっ", "ひゃく": "ひゃっ"}
COUNTERS = "人匹本杯分歳回度個階週日年時月"


def hiragana(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def below_10000(s):
    """Reading of a numeral under 10,000 and how it ends: its last digit, or
    the unit (十, 百, 千) it ends on."""
    out, last = "", None
    for unit in "千百十":
        if unit not in s:
            continue
        head, s = s.split(unit, 1)
        n = DIGITS.get(head, 1) if head else 1
        if unit == "千":
            out += {1: "", 3: "さん", 8: "はっ"}.get(n, ONES[n]) + ("ぜん" if n == 3 else "せん")
        elif unit == "百":
            out += {1: "", 6: "ろっ", 8: "はっ"}.get(n, ONES[n])
            out += {3: "びゃく", 6: "ぴゃく", 8: "ぴゃく"}.get(n, "ひゃく")
        else:
            out += ("" if n == 1 else ONES[n]) + "じゅう"
        last = unit
    if s:
        out += ONES[DIGITS[s]]
        last = DIGITS[s]
    return out, last


def numeral(s):
    if "万" in s:
        head, rest = s.split("万", 1)
        reading = (below_10000(head)[0] if head else "いち") + "まん"
        tail, last = below_10000(rest) if rest else ("", "万")
        return reading + tail, last
    return below_10000(s)


def with_counter(number, counter):
    """Reading of a numeral and the counter after it, or None."""
    if counter == "日" and number in DAYS:
        return DAYS[number]
    if counter == "日" and number == "一":
        return None
    if counter == "人" and number in ("一", "二"):
        return {"一": "ひとり", "二": "ふたり"}[number]
    reading, last = numeral(number)
    if counter == "日" and number.endswith("七"):
        return reading[: -len("なな")] + "しちにち"
    if counter == "時":
        return reading.replace("よん", "よ").replace("きゅう", "く") + "じ"
    if counter == "月":
        return {"よん": "し", "なな": "しち", "きゅう": "く"}.get(reading, reading) + "がつ"
    if counter == "年" and number == "四":
        return "よねん"
    geminates = last in (1, 6, 8, "十", "百")
    if counter in "匹本杯":
        plain, hard, voiced = {"匹": ("ひき", "ぴき", "びき"), "本": ("ほん", "ぽん", "ぼん"),
                               "杯": ("はい", "ぱい", "ばい")}[counter]
        if geminates:
            word = hard
        else:
            return reading + (voiced if last in (3, "千", "万") else plain)
    elif counter == "分":
        if geminates:
            word = "ぷん"
        else:
            return reading + ("ぷん" if last in (3, 4) else "ふん")
    elif counter == "歳":
        word, geminates = "さい", last in (1, 8, "十")
    elif counter in "回個階週":
        word = {"回": "かい", "個": "こ", "階": "かい", "週": "しゅう"}[counter]
    else:
        return reading + {"人": "にん", "度": "ど", "日": "にち", "年": "ねん"}[counter]
    if geminates:
        for plain_end, short in GEMINATE.items():
            if reading.endswith(plain_end):
                reading = reading[: -len(plain_end)] + short
                break
    return reading + word


def word_kanji(surface, reading):
    """[(offset, length, reading)] for the kanji runs inside one word, by
    matching its kana against its reading; None if they do not match."""
    pattern, runs, at = "", [], 0
    for part in re.split(f"([{furigana.KANJI}]+)", surface):
        if not part:
            continue
        if KANJI_RUN.fullmatch(part):
            pattern += "(.+?)"
            runs.append((at, len(part)))
        else:
            pattern += re.escape(hiragana(part))
        at += len(part)
    m = re.fullmatch(pattern, reading)
    if not m:
        return None
    return [(o, n, m.group(i + 1)) for i, (o, n) in enumerate(runs)]


def word_reading(words, i, text, start, end):
    """A word's reading in hiragana, with the Bible's readings where the
    analyser's differ."""
    w = words[i]
    surface, r = w.surface, hiragana(w.feature.kana)
    before, after = text[max(0, start - 3):start], text[end:end + 3]
    previous = words[i - 1].surface if i else ""
    if surface == "人" and KATAKANA_WORD.match(previous):
        return "じん"
    if surface == "川" and KATAKANA_WORD.match(previous):
        return "がわ"
    if surface == "面" and r == "めん" and before.endswith("の") and not after.startswith("前"):
        return "おもて"
    if surface.startswith("汚") and r.startswith("よご"):
        return "けが" + r[2:]
    if surface == "方" and r == "ほう" and not after.startswith(("へ", "に向")):
        return "かた"
    if surface == "何" and r in ("なん", "なに"):
        return "なん" if after[:1] in "でのとだ" else "なに"
    if surface == "実" and r == "じつ" and not after.startswith("は、"):
        return "み"
    if surface in ("言", "証") and w.feature.pos1 == "名詞":
        return {"言": "ことば", "証": "あかし"}[surface]
    if surface == "後" and r == "ご":
        if before.endswith(("その", "この")):
            return "のち"
        if before[-1:] in "たのでて":
            return "あと"
    return r


def number_prefix(run, after):
    """(reading, length) for a numeral, with its counter, at the start of a
    run, or None."""
    m = NUMBER.match(run)
    if not m or run.startswith("万"):
        return None
    number, rest = m.group(), run[len(m.group()):]
    try:
        if rest and rest[0] in COUNTERS:
            reading = with_counter(number, rest[0])
            return (reading, len(number) + 1) if reading else None
        if rest:
            return numeral(number)[0], len(number)
        if after.startswith("つ") and number in NATIVE:
            return NATIVE[number], len(number)
        if after.startswith(("日", "の")) and number == "十":
            return None
        return numeral(number)[0], len(number)
    except (KeyError, IndexError):
        return None


def draft(tagger, text):
    """[[run, reading], ...] for every kanji run of a rendering, [] if it has
    none, or None if some run cannot be read."""
    runs = furigana.runs(text)
    if not runs:
        return []
    chars = list(text)
    for span in markup.spans(text):
        chars[span.start:span.end] = "　" * (span.end - span.start)
    plain = "".join(chars)
    words = list(tagger(plain))
    pieces, at = [], 0
    for i, w in enumerate(words):
        start = plain.find(w.surface, at)
        if start < 0:
            return None
        at = start + len(w.surface)
        if not KANJI_RUN.search(w.surface):
            continue
        if not w.feature.kana or w.feature.kana == "*":
            return None
        found = word_kanji(w.surface, word_reading(words, i, plain, start, at))
        if found is None:
            return None
        pieces += [(start + o, start + o + n, r) for o, n, r in found]

    def joined(start, end):
        inside = [p for p in pieces if start <= p[0] and p[1] <= end]
        if not inside or inside[0][0] != start or inside[-1][1] != end:
            return None
        if any(a[1] != b[0] for a, b in zip(inside, inside[1:])):
            return None
        return "".join(p[2] for p in inside)

    out = []
    for start, end, run in runs:
        if run in RUNS:
            out.append([run, RUNS[run]])
            continue
        if run == "供" and plain[end:end + 1] == "え":
            out.append([run, "そな"])
            continue
        reading = None
        prefix = number_prefix(run, plain[end:end + 2])
        if run.startswith("一日"):
            prefix = ("ついたち" if plain[max(0, start - 2):start] == "月の" else "いちにち", 2)
        if run.startswith("何") and len(run) > 1 and run[1] in "人匹本度回日年歳時":
            prefix = ("なん" + {"人": "にん", "匹": "びき", "本": "ぼん", "度": "ど", "回": "かい", "日": "にち",
                                 "年": "ねん", "歳": "さい", "時": "じ"}[run[1]], 2)
        if prefix:
            head, n = prefix
            rest = "" if start + n == end else joined(start + n, end)
            reading = None if rest is None else head + rest
        if not reading:
            reading = joined(start, end)
        if not reading:
            return None
        out.append([run, reading])
    return out


def key(rid):
    _, chapter, verse, sentence = rid.split(".")
    return int(chapter), int(verse), int(sentence[1:])


def write(path, data):
    lines = [f"  {json.dumps(k, ensure_ascii=False)}: {json.dumps(data[k], ensure_ascii=False)}"
             for k in sorted(data, key=key)]
    path.write_text("{\n" + ",\n".join(lines) + "\n}\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("books", nargs="*", help="book codes (default: every book)")
    ap.add_argument("--level", default="B", choices="LBR")
    ap.add_argument("--refresh", action="store_true", help="redraft readings that no longer fit the rendering")
    args = ap.parse_args()
    import fugashi

    tagger = fugashi.Tagger()
    books = args.books or json.loads((ROOT / "data" / "books.json").read_text(encoding="utf-8"))["books"]
    added = skipped = 0
    for book in books:
        path = furigana.DIR / f"{book}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        before = json.dumps(data, sort_keys=True)
        for f in sorted((ROOT / "content" / book).glob("*.json")):
            for r in json.loads(f.read_text(encoding="utf-8"))["records"]:
                text = r["renderings"].get(LANG, {}).get(args.level)
                if text is None:
                    continue
                have = data.get(r["id"], {}).get(LANG, {}).get(args.level)
                if have is not None:
                    try:
                        furigana.ranges(text, have)
                        continue
                    except ValueError:
                        if not args.refresh:
                            continue
                readings = draft(tagger, text)
                if readings is None:
                    skipped += 1
                elif readings:
                    data.setdefault(r["id"], {}).setdefault(LANG, {})[args.level] = readings
                    added += 1
        if data and json.dumps(data, sort_keys=True) != before:
            write(path, data)
    print(f"{added} records drafted, {skipped} left out (a run the analyser could not read)")


if __name__ == "__main__":
    main()
