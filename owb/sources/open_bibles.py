"""Verse text from the public-domain Bibles in seven1m/open-bibles.

The files come in three XML formats. USFX and OSIS mark verses with
milestones (<v id/> ... <ve/>, <verse sID/> ... <verse eID/>), so we walk the
document in order and collect the text between them; Zefania nests text in
<VERS> elements. Headings, footnotes, cross references and titles are
skipped. Books outside the 66-book canon (e.g. the KJV Apocrypha) are dropped.

Each edition we import is listed in EDITIONS with its file and licence; the
repository itself is pinned in sources.lock.json.
"""
import re
import xml.etree.ElementTree as ET

from owb import refs
from owb.sources import source_dir

# code: (file, format, language, name, licence)
EDITIONS = {
    "bsb": ("eng-bsb.usfx.xml", "usfx", "eng", "Berean Standard Bible", "Public domain"),
    "web": ("eng-web.usfx.xml", "usfx", "eng", "World English Bible", "Public domain"),
    "asv": ("eng-asv.zefania.xml", "zefania", "eng", "American Standard Version (1901)", "Public domain"),
    "kjv": ("eng-kjv.osis.xml", "osis", "eng", "King James Version",
            "Public domain outside the UK (Crown copyright in the UK)"),
    "ylt": ("eng-ylt.zefania.xml", "zefania", "eng", "Young's Literal Translation (New Testament)", "Public domain"),
    "rv1909": ("spa-rv1909.usfx.xml", "usfx", "spa", "Reina-Valera 1909", "Public domain"),
}

# Elements whose content is not Scripture text.
_SKIP = {"f", "x", "s", "h", "toc", "id", "ide", "rem", "fig", "note", "title", "fm",
         "milestone", "table", "d"}
_SPACE = re.compile(r"\s+")


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _clean(parts):
    return _SPACE.sub(" ", "".join(parts)).strip()


def _walk_milestones(root, start, end):
    """Generic walk: start(el) returns a (book, chapter, verse) key or None and
    may update state; end(el) is true where the current verse closes."""
    out, current, buf = {}, None, []

    def flush():
        nonlocal current, buf
        if current is not None:
            text = _clean(buf)
            if text:
                out[current] = (out[current] + " " + text) if current in out else text
        current, buf = None, []

    def visit(el, skipping):
        nonlocal current
        tag = _local(el.tag)
        skip = skipping or tag in _SKIP
        key = start(el)
        if key is not None:
            flush()
            current = key
        elif end(el):
            flush()
        if not skip and current is not None and el.text:
            buf.append(el.text)
        for child in el:
            visit(child, skip)
            if not skip and current is not None and child.tail:
                buf.append(child.tail)

    visit(root, False)
    flush()
    return out


def parse_usfx(path):
    root = ET.parse(path).getroot()
    state = {"book": None, "chapter": None}

    def start(el):
        tag = _local(el.tag)
        if tag == "book":
            state["book"] = el.get("id")
        elif tag == "c":
            state["chapter"] = int(el.get("id"))
        elif tag == "v" and state["book"] in refs.BOOK_NAMES:
            return (state["book"], state["chapter"], int(re.match(r"\d+", el.get("id"))[0]))
        return None

    def end(el):
        return _local(el.tag) in ("ve", "c", "book")

    return _walk_milestones(root, start, end)


def parse_osis(path):
    root = ET.parse(path).getroot()

    def start(el):
        if _local(el.tag) == "verse" and el.get("sID"):
            book, chapter, verse = el.get("osisID").split()[0].split(".")
            code = refs.OSIS_TO_CODE.get(book)
            return (code, int(chapter), int(verse)) if code else None
        return None

    def end(el):
        return _local(el.tag) == "verse" and el.get("eID") is not None

    return _walk_milestones(root, start, end)


def parse_zefania(path):
    out = {}
    root = ET.parse(path).getroot()
    for book in root.iter("BIBLEBOOK"):
        number = int(book.get("bnumber"))
        if not 1 <= number <= len(refs.BOOKS):
            continue
        code = refs.BOOKS[number - 1][0]
        for chapter in book.iter("CHAPTER"):
            for vers in chapter.iter("VERS"):
                parts = [vers.text or ""]
                for child in vers:
                    if _local(child.tag) not in _SKIP:
                        parts.append("".join(child.itertext()))
                    parts.append(child.tail or "")
                text = _clean(parts)
                if text:
                    out[(code, int(chapter.get("cnumber")), int(vers.get("vnumber")))] = text
    return out


PARSERS = {"usfx": parse_usfx, "osis": parse_osis, "zefania": parse_zefania}


def load(code):
    """Return {(book, chapter, verse): text} for one edition in EDITIONS."""
    filename, fmt, *_ = EDITIONS[code]
    return PARSERS[fmt](source_dir("open-bibles") / filename)
