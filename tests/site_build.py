"""One build of the site for the whole test run. A build takes minutes,
and the test classes that read built pages only read them, so they share
this one instead of building their own. With OWB_BUILT_SITE set (CI, which
builds the site in the step before), they read that build instead."""
import atexit
import functools
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


@functools.cache
def built_site():
    """The built site's directory, built on first use. Read it; don't change it."""
    if os.environ.get("OWB_BUILT_SITE"):
        return Path(os.environ["OWB_BUILT_SITE"]).resolve()
    out = Path(tempfile.mkdtemp(prefix="owb-site-"))
    atexit.register(shutil.rmtree, out, True)
    build_site.build(out)
    return out


SHARED = re.compile(r'<script src="(/(?:chapter-data/[^"?]+|reader-[a-z]+)\.js\?v=[0-9a-f]+)"></script>')


TEXT = re.compile(r'window\.OWB_TEXTS\["([a-z]+)"\]=')


def page_data(page):
    """A chapter page's reader data as reader.js sees it: the page's own
    (owb-data) with the shared data of its chapter and language added
    (build_site.chapter_shared, reader_shared), and the text of each
    language the page loads (chapter_language_data) joined to the records."""
    data = json.loads(re.search(r'<script type="application/json" id="owb-data">(.*?)</script>', page, re.S)[1])
    loaded = {src.split("?")[0]: src for src in SHARED.findall(page)}

    def shared(text, src):
        path = src.split("?")[0]
        assert path in loaded, (src, loaded)
        # A page of the built site loads that build's copy, which may differ
        # from one made now (a test may have changed what is translated).
        if loaded[path] != src:
            text = (built_site() / path.lstrip("/")).read_text(encoding="utf-8")
        # A language's text sets window.OWB_TEXTS["es"]; the rest one name.
        m = TEXT.search(text)
        start = m.end() if m else text.index("=") + 1
        return (m[1] if m else None), json.loads(text[start:].rstrip().rstrip(";"))

    for text, src in (build_site.chapter_shared(data["book"], data["chapter"]),
                      build_site.reader_shared(data["lang"])):
        data.update(shared(text, src)[1])
    for r in data["records"]:
        r["renderings"], r["links"] = {}, {}
    # As reader.js does: each loaded language's renderings and word links,
    # and the page language's rendering decisions after the meaning ones.
    for code, src in data["texts"].items():
        if src.split("?")[0] not in loaded:
            continue
        code, text = shared(build_site.chapter_language_data(data["book"], data["chapter"], code)[0], src)
        for r in data["records"]:
            if r["id"] in text["renderings"]:
                r["renderings"][code] = text["renderings"][r["id"]]
            if r["id"] in text["links"]:
                r["links"][code] = text["links"][r["id"]]
            if code == data["lang"]:
                r["decisions"] = r["decisions"] + text["decisions"].get(r["id"], [])
    return data
