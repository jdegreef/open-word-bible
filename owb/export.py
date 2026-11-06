"""The translation as a file other software can read: one language at one
level, verse by verse, as USFM (a zip of one file per book, which most
Bible software and importers read) or JSON.

The text is our wording with the reader settings chosen (each span at the
option asked for, else its default), poetry line breaks read as spaces and
verse markers split out, so each verse is plain text. A verse not yet
translated is left out, never filled from another Bible; the manifest lists
which.

Most Bibles and importers number verses as English Bibles do, not as the
Hebrew (and, in five places, the SBLGNT) does, so numbering="english" (the default) moves each
verse to its English number (owb/versification.py); numbering="source" keeps
ours. A
psalm title, which English Bibles print unnumbered, becomes the chapter's
title (USFM \\d); a Hebrew verse that holds two English ones (PSA.13.6 is
Psalm 13:5-6) becomes a verse bridge (\\v 5-6). Given the verses that open
a paragraph (the site's, from the source text's own marks), a USFM chapter
starts a new paragraph (\\p) at each, and a JSON verse says "paragraph".
Given where Jesus speaks (owb/words_of_jesus.py), USFM marks his words
(\\wj ... \\wj*, closed and reopened at a verse boundary) and a JSON verse
lists them as "wj": [[start, end], ...] in its text.

Only our translation is exported: no Greek or Hebrew, no word data.

build() takes records in the content/ file format, of which it reads only
"refs", "renderings" and "status", so the admin (from the database,
backend/staff/export.py) and scripts (from content/) make the same file.
"""
import io
import json
import zipfile
from pathlib import Path

from owb import languages, markup, refs, versification

BOOKS = json.loads((Path(__file__).resolve().parents[1] / "data" / "books.json")
                   .read_text(encoding="utf-8"))["books"]

LEVELS = {"L": "Literal", "B": "Balanced", "R": "Readable"}
FORMATS = ("usfm", "json")
NUMBERINGS = ("english", "source")

# The settings every language has, with the English labels of their options
# (the reader's own, web/reader.js); a language's own settings and labels are
# in data/languages.json.
SETTING_LABELS = {
    "gender": ["Inclusive", "Traditional"],
    "christos": ["Christ", "Messiah"],
    "divine_name": ["LORD", "Yahweh"],
    "deity_pronoun": ["he", "He"],
    "units": ["Modern", "Original"],
}

LICENCE = "CC0 1.0 Universal (public domain dedication)"
LICENCE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
SITE = "https://openwordbible.org"
DRAFT_NOTE = ("Every sentence is an AI-assisted draft until a named reviewer approves it; "
              "\"status\" counts the sentences in this file by review state.")

# Zip entries carry this date, so the same text makes the same bytes.
ZIP_DATE = (2026, 1, 1, 0, 0, 0)


def settings_for(lang):
    """{setting: [option labels]} for the settings lang's text can hold."""
    return {**SETTING_LABELS, **languages.settings(lang)}


# Stand-ins for the start and end of Jesus's words while a rendering is
# rendered and split into verses; no rendering holds them.
WJ_OPEN, WJ_CLOSE = "\x02", "\x03"


def mark_words_of_jesus(text, ranges):
    """text with WJ_OPEN/WJ_CLOSE around each of ranges ([[start, end], ...],
    where Jesus speaks: owb/words_of_jesus.py). Quotation marks never sit
    inside a {{setting:...}} span, so neither do the stand-ins."""
    for start, end in sorted(ranges, reverse=True):
        text = text[:start] + WJ_OPEN + text[start:end] + WJ_CLOSE + text[end:]
    return text


def wj_runs(text):
    """(text without stand-ins, [[start, end], ...]) for one verse. A run
    the verse opens without closing (or closes without opening) runs to its
    end (or from its start)."""
    plain_text, runs, start = "", [], None
    first = next((c for c in text if c in (WJ_OPEN, WJ_CLOSE)), None)
    if first == WJ_CLOSE:
        start = 0
    for c in text:
        if c == WJ_OPEN:
            start = len(plain_text)
        elif c == WJ_CLOSE:
            if start is not None and len(plain_text) > start:
                runs.append([start, len(plain_text)])
            start = None
        else:
            plain_text += c
    if start is not None and len(plain_text) > start:
        runs.append([start, len(plain_text)])
    return plain_text, runs


def usfm_text(text):
    """One verse's text for USFM, its words of Jesus marked \\wj ... \\wj*."""
    plain_text, runs = wj_runs(text)
    for start, end in reversed(runs):
        # Keep the marker off the spaces at either end of a run.
        while end > start and plain_text[end - 1] == " ":
            end -= 1
        while start < end and plain_text[start] == " ":
            start += 1
        plain_text = plain_text[:start] + "\\wj " + plain_text[start:end] + "\\wj*" + plain_text[end:]
    return plain_text


def record_verses(r):
    """{verse id: {lang: {level: text}}} for one record, split at its verse
    markers. A record's markers follow its refs in order."""
    out = {}
    for lang, levels in r["renderings"].items():
        for level, text in levels.items():
            parts = markup.split_verses(text)
            if len(parts) != len(r["refs"]):
                continue
            for vid, (_, part) in zip(r["refs"], parts):
                out.setdefault(vid, {}).setdefault(lang, {})[level] = part.strip()
    return out


def plain(text, settings=None):
    """One verse's text as plain text: settings chosen, lines run together."""
    return " ".join(markup.flat(markup.render(text, settings)).split())


def verse_texts(records, lang, level, settings=None, words_of_jesus=None):
    """{verse id: plain text}, our numbering, in Bible order. Two sentences
    in one verse (Philippians 4:5) are joined in record order. With
    words_of_jesus ({record id: marking}), his words are between WJ_OPEN and
    WJ_CLOSE: where a record carries them already ("wj", as the site's
    loader adds them before it curls the quotes), those ranges; else
    found from the marking."""
    out = {}
    for r in records:
        text = r["renderings"].get(lang, {}).get(level)
        if words_of_jesus is not None and text is not None:
            ranges = r.get("wj", {}).get(lang, {}).get(level)
            if ranges is None and r.get("id") in words_of_jesus:
                from owb import words_of_jesus as wj
                ranges = wj.ranges(text, words_of_jesus[r["id"]])
            if ranges:
                r = {**r, "renderings": {lang: {level: mark_words_of_jesus(text, ranges)}}}
        for vid, langs in record_verses(r).items():
            text = langs.get(lang, {}).get(level)
            if text:
                text = plain(text, settings)
                out[vid] = f"{out[vid]} {text}" if vid in out else text
    return dict(sorted(out.items(), key=lambda kv: refs.parse(kv[0]).sort_key()))


def numbered(verses, numbering="english", paragraphs=frozenset()):
    """The verses as they are numbered in the file:
    ([{"book", "chapter", "verse", "to"?, "holds"?, "paragraph"?, "text"}],
    {(book, chapter): title}). With English numbering a verse goes to its
    English number; verses whose English numbers overlap are joined into
    one entry, a bridge ("to") when it covers several verses of a chapter,
    else numbered as its first and listing the verses it "holds"; a verse
    with no English number is a title. An entry whose first verse is in
    paragraphs (our verse ids) opens a paragraph."""
    entries, titles = [], {}
    for vid, text in verses.items():
        ref = refs.parse(vid)
        english = list(versification.to_english(ref)) if numbering == "english" else [ref]
        if not english:
            key = (ref.book, ref.chapter)
            text = wj_runs(text)[0]
            titles[key] = f"{titles[key]} {text}" if key in titles else text
            continue
        last = entries[-1] if entries else None
        if last and set(english) & set(last[0]):
            last[0] = sorted(set(last[0]) | set(english), key=refs.Ref.sort_key)
            last[1].append(text)
        else:
            entries.append([english, [text], vid in paragraphs])
    out = []
    for numbers, texts, opens in sorted(entries, key=lambda e: e[0][0].sort_key()):
        first, end = numbers[0], numbers[-1]
        entry = {"book": first.book, "chapter": first.chapter, "verse": first.verse, "text": " ".join(texts)}
        if opens:
            entry["paragraph"] = True
        if end.chapter != first.chapter:
            # A bridge can't cross chapters (Hebrew ISA.63.19 is English
            # Isaiah 63:19 and 64:1): the text goes under the first verse.
            entry["holds"] = [str(n) for n in numbers]
        elif end != first:
            entry["to"] = end.verse
        out.append(entry)
    return out, titles


def book_name(code, lang):
    return BOOKS[code].get(lang) or BOOKS[code]["en"]


def edition_code(lang, level):
    """"owb-en-b": how a file names its edition."""
    return f"owb-{lang}-{level.lower()}"


def usfm_book(code, lang, level, entries, titles):
    """One book as USFM 3."""
    name = book_name(code, lang)
    lines = [f"\\id {code} Open Word Bible, {languages.READING[lang]['name']}, {LEVELS[level]} (OWB-{level})",
             "\\usfm 3.0", "\\ide UTF-8", f"\\h {name}", f"\\toc1 {name}", f"\\toc2 {name}", f"\\mt1 {name}"]
    chapter = None
    for e in entries:
        if e["chapter"] != chapter:
            chapter = e["chapter"]
            lines.append(f"\\c {chapter}")
            if (code, chapter) in titles:
                lines.append(f"\\d {titles[code, chapter]}")
            lines.append("\\p")
        elif e.get("paragraph"):
            lines.append("\\p")
        number = f"{e['verse']}-{e['to']}" if "to" in e else str(e["verse"])
        lines.append(f"\\v {number} {usfm_text(e['text'])}")
    return "\n".join(lines) + "\n"


def json_books(lang, entries, titles):
    """[{"code", "name", "chapters": [{"chapter", "title"?, "verses": [...]}]}]"""
    books = []
    for e in entries:
        if not books or books[-1]["code"] != e["book"]:
            books.append({"code": e["book"], "name": book_name(e["book"], lang), "chapters": []})
        chapters = books[-1]["chapters"]
        if not chapters or chapters[-1]["chapter"] != e["chapter"]:
            chapter = {"chapter": e["chapter"]}
            if (e["book"], e["chapter"]) in titles:
                chapter["title"] = titles[e["book"], e["chapter"]]
            chapter["verses"] = []
            chapters.append(chapter)
        verse = {k: e[k] for k in ("verse", "to", "holds", "paragraph") if k in e}
        verse["text"], runs = wj_runs(e["text"])
        if runs:
            verse["wj"] = runs
        chapters[-1]["verses"].append(verse)
    return books


def build(records, lang, level, fmt="usfm", numbering="english", settings=None, books=None,
          expected=None, generated_at="", commit="", paragraphs=frozenset(), words_of_jesus=None):
    """The export of records in lang at level: (filename, content type,
    bytes, manifest). books limits it to those book codes (None: all).
    expected, if given, is every verse id the source text has (our
    numbering), so the manifest can list those not yet translated.
    paragraphs is the verse ids (our numbering) that open a paragraph;
    words_of_jesus is {record id: marking} (owb/words_of_jesus.py)."""
    if lang not in languages.READING:
        raise ValueError(f"unknown language {lang!r}")
    if level not in LEVELS:
        raise ValueError(f"unknown level {level!r}")
    if fmt not in FORMATS:
        raise ValueError(f"unknown format {fmt!r}")
    if numbering not in NUMBERINGS:
        raise ValueError(f"unknown numbering {numbering!r}")
    known = settings_for(lang)
    settings = {name: index for name, index in (settings or {}).items() if name in known}
    wanted = set(books) if books else None
    records = [r for r in records if wanted is None or refs.parse(r["refs"][0]).book in wanted]
    verses = verse_texts(records, lang, level, settings, words_of_jesus)
    entries, titles = numbered(verses, numbering, paragraphs)

    status = {}
    for r in records:
        if level in r["renderings"].get(lang, {}):
            status[r.get("status", "ai_draft")] = status.get(r.get("status", "ai_draft"), 0) + 1
    in_file = sorted({e["book"] for e in entries} | {book for book, _ in titles}, key=refs.BOOK_CODES.index)
    manifest = {
        "title": "Open Word Bible",
        "edition": edition_code(lang, level),
        "language": lang,
        "language_name": languages.READING[lang]["name"],
        "level": level,
        "level_name": LEVELS[level],
        "format": fmt,
        "numbering": numbering,
        "numbering_note": ("English Bible (KJV) verse numbers; psalm titles are chapter titles"
                           if numbering == "english" else
                           "the source text's numbers: Hebrew in the Old Testament, so a psalm title is verse 1"),
        "settings": {name: labels[settings.get(name, markup.DEFAULTS.get(name, 0))]
                     for name, labels in known.items()},
        "books": in_file,
        "verses": len(verses),
        "combined": [{"verse": f"{e['book']}.{e['chapter']}.{e['verse']}", "holds": e["holds"]}
                     for e in entries if "holds" in e],
        "status": dict(sorted(status.items())),
        "note": DRAFT_NOTE,
        "licence": LICENCE,
        "licence_url": LICENCE_URL,
        "credit": "Open Word Bible (openwordbible.org)",
        "url": SITE,
        "generated_at": generated_at,
        "commit": commit,
    }
    if expected is not None:
        missing = sorted((v for v in expected if v not in verses
                          and (wanted is None or refs.parse(v).book in wanted)),
                         key=lambda v: refs.parse(v).sort_key())
        by_book = {}
        for v in missing:
            book = v.split(".")[0]
            by_book[book] = by_book.get(book, 0) + 1
        manifest["missing"] = {"count": len(missing), "by_book": by_book, "verses": missing}

    stem = edition_code(lang, level) + ("" if numbering == "english" else "-source")
    if fmt == "json":
        body = {"manifest": manifest, "books": json_books(lang, entries, titles)}
        return f"{stem}.json", "application/json", json.dumps(body, ensure_ascii=False, indent=1).encode(), manifest

    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, text):
            info = zipfile.ZipInfo(name, ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, text.encode())
        put("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")
        for code in in_file:
            book_entries = [e for e in entries if e["book"] == code]
            number = refs.BOOK_CODES.index(code) + 1
            put(f"{number:02d}-{code}.usfm", usfm_book(code, lang, level, book_entries, titles))
    return f"{stem}-usfm.zip", "application/zip", data.getvalue(), manifest
