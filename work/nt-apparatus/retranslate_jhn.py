# ruff: noqa: E501
"""One-off: bring the five John 1-3 footnoted notes changed by the NT apparatus
pass up to date in the reading languages that have John notes (id is prepared in
work/nt-apparatus/id-JHN.jsonl but not imported: another session's lane). Each English change only removed or narrowed the
closing "check against the apparatus" sentence (and, in 1:28, added that the
Robinson-Pierpont text has Bethany), so each translation is the previous one
without its closing sentence, plus the new sentence(s) below.

    python3 work/nt-apparatus/retranslate_jhn.py IN_DIR OUT_DIR
reads IN_DIR/<lang>.jsonl from `notes.py export <lang> --books JHN
--chapters 1-3 --footnotes-only` and writes filled worklists to OUT_DIR.
"""
import json
import re
import sys
from pathlib import Path

# H1: JHN 1:34 narrowed hedge; H2: JHN 1:28 hedge; C: JHN 1:28 added sentence.
NEW = {
    "am": ("ገምጋሚዎች የጥንት ትርጉሞችንና የቀደሙ ጸሐፊዎችን ከሙሉ የጽሑፍ ትችት ማስረጃ ጋር ማመሳከር አለባቸው።",
           "ገምጋሚዎች የኦሪጀንን አስተያየት ከሙሉ የጽሑፍ ትችት ማስረጃ ጋር ማመሳከር አለባቸው።",
           "የሮቢንሰን-ፒርፖንት የባይዛንታይን ጽሑፍ ቢታንያ ይላል።"),
    "es": ("Los revisores deben contrastar las traducciones antiguas y los escritores antiguos con un aparato crítico completo.",
           "Los revisores deben contrastar el comentario de Orígenes con un aparato crítico completo.",
           "El texto bizantino de Robinson-Pierpont tiene Betania."),
    "fr": ("Les relecteurs doivent vérifier les traductions anciennes et les premiers auteurs dans un apparat critique complet.",
           "Les relecteurs doivent vérifier le commentaire d’Origène dans un apparat critique complet.",
           "Le texte byzantin de Robinson-Pierpont porte Béthanie."),
    "hi": ("समीक्षकों को प्राचीन अनुवादों और आरंभिक लेखकों को पूरे पाठ-आलोचना साक्ष्य से मिलाना चाहिए।",
           "समीक्षकों को ओरिजन की टिप्पणी को पूरे पाठ-आलोचना साक्ष्य से मिलाना चाहिए।",
           "रॉबिन्सन-पियरपॉन्ट के बाइज़ेंटाइन पाठ में बैतनिय्याह है।"),
    "id": ("Peninjau perlu memeriksa terjemahan kuno dan para penulis awal dengan aparatus kritis yang lengkap.",
           "Peninjau perlu memeriksa komentar Origenes dengan aparatus kritis yang lengkap.",
           "Teks Bizantin Robinson-Pierpont membaca Betania."),
    "ja": ("検討者は古代の翻訳と初期の著述家を完全な本文批評資料と照らし合わせるべきである。",
           "検討者はオリゲネスの言及を完全な本文批評資料と照らし合わせるべきである。",
           "ロビンソン＝ピアポントのビザンティン本文はベタニアと読む。"),
    "ko": ("검토자는 고대 번역본과 초기 저술가들을 온전한 본문비평 자료와 대조해야 한다.",
           "검토자는 오리게네스의 언급을 온전한 본문비평 자료와 대조해야 한다.",
           "로빈슨-피어폰트 비잔틴 본문은 베다니로 읽는다."),
    "pt": ("Os revisores devem conferir as traduções antigas e os escritores antigos num aparato crítico completo.",
           "Os revisores devem conferir o comentário de Orígenes num aparato crítico completo.",
           "O texto bizantino de Robinson-Pierpont traz Betânia."),
    "ru": ("Рецензентам стоит сверить древние переводы и ранних писателей с полным критическим аппаратом.",
           "Рецензентам стоит сверить замечание Оригена с полным критическим аппаратом.",
           "В византийском тексте Робинсона — Пирпонта стоит Вифания."),
    "sw": ("Wahakiki walinganishe tafsiri za kale na waandishi wa mwanzo na vyanzo kamili vya ushahidi wa maandishi.",
           "Wahakiki walinganishe maelezo ya Origene na vyanzo kamili vya ushahidi wa maandishi.",
           "Maandishi ya Kibizantini ya Robinson-Pierpont yanasoma Bethania."),
    "uk": ("Рецензентам варто звірити давні переклади та ранніх письменників із повним критичним апаратом.",
           "Рецензентам варто звірити зауваження Орігена з повним критичним апаратом.",
           "У візантійському тексті Робінсона — Пірпонта стоїть Віфанія."),
    "vi": ("Người duyệt nên đối chiếu các bản dịch cổ và các tác giả thời đầu với một bộ chú giải văn bản đầy đủ.",
           "Người duyệt nên đối chiếu lời nhận xét của Ô-ri-gen với một bộ chú giải văn bản đầy đủ.",
           "Bản văn Byzantine của Robinson-Pierpont ghi Bê-tha-ni."),
}
END = {"am": "።", "ja": "。", "hi": "।"}


def sentences(text, lang):
    end = END.get(lang, ".")
    parts = re.split(rf"(?<={re.escape(end)})\s*", text.strip())
    return [p for p in parts if p]


def main(src, dst):
    dst.mkdir(parents=True, exist_ok=True)
    for path in sorted(src.glob("*.jsonl")):
        lang = path.stem
        if lang not in NEW:
            continue
        h1, h2, c = NEW[lang]
        sep = "" if lang == "ja" else " "
        out = []
        for line in path.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            prev = d["previous"]
            body = sentences(prev["reason"], lang)[:-1]   # drop the old closing check
            if d["record"] == "JHN.1.34.s1":
                body.append(h1)
            elif d["record"] == "JHN.1.28.s1":
                body.insert(len(body) - 1, c)
                body.append(h2)
            d["translation"] = {"choice": prev["choice"], "alternatives": prev["alternatives"],
                                "reason": sep.join(body)}
            out.append(json.dumps(d, ensure_ascii=False))
        (dst / path.name).write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
