"""MACULA's word-sense columns (Louw-Nida and SDBH, from UBS MARBLE) are used
with permission but not openly licensed. Nothing we publish may carry them:
not the word extracts in data/, not the built site, not the backend's word
table."""
import csv
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from extract_tokens import content_refs  # noqa: E402
from owb.sources import macula_greek, macula_hebrew, read_text  # noqa: E402

RESTRICTED = macula_greek.RESTRICTED + macula_hebrew.RESTRICTED


def keys(obj):
    """Every key anywhere inside parsed JSON."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from keys(v)


def restricted_values():
    """The restricted Greek and Hebrew values for the chapters in content/
    (the extracts hold whole chapters), by token id."""
    wanted = {r.rsplit(".", 1)[0].replace(".", " ") for r in content_refs()}
    out = {}
    for source in (macula_greek, macula_hebrew):
        name = source.__name__.rsplit(".", 1)[1].replace("_", "-")
        reader = csv.DictReader(io.StringIO(read_text(name, source.TSV_PATH)),
                                delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            if row["ref"].split(":")[0] in wanted:
                out[row["xml:id"]] = {row[c] for c in source.RESTRICTED if row[c].strip()}
    return out


class LicensingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.tmp.name) / "site"
        build_site.build(cls.site)
        cls.extracts = {p: json.loads(p.read_text(encoding="utf-8"))
                        for p in sorted((ROOT / "data").rglob("*.json"))}
        # Every text file the site serves; fonts and share images are binary.
        cls.pages = {p: p.read_text(encoding="utf-8") for p in sorted(cls.site.rglob("*"))
                     if p.is_file() and p.suffix not in (".woff2", ".jpg")}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_extracts_have_no_restricted_fields(self):
        self.assertTrue(self.extracts)
        for path, data in self.extracts.items():
            self.assertFalse(set(keys(data)) & set(RESTRICTED), path)

    def test_extracts_hold_no_restricted_values(self):
        values = restricted_values()
        self.assertTrue(any(values.values()), "the check found no values to look for")
        for path, data in self.extracts.items():
            if "verses" not in data:   # not a word extract (e.g. key_terms.json)
                continue
            for words in data["verses"].values():
                for word in words:
                    leaked = values.get(word["id"], set()) & {str(v) for v in word.values()}
                    self.assertFalse(leaked, (path, word["id"], leaked))

    def test_site_has_no_restricted_fields_or_values(self):
        # Field names are checked on every file. Values are checked per word:
        # the restricted codes are short numbers ("3.5"), which also occur in
        # markup (an SVG radius), so a page-wide search would only find
        # coincidences. Each word in a page's embedded data is compared with
        # that same word's restricted values instead.
        values = restricted_values()
        field = re.compile(r'"(%s)"\s*:' % "|".join(RESTRICTED))
        blob = re.compile(r'<script type="application/json" id="owb-data">(.*?)</script>', re.S)
        checked = 0
        for path, text in self.pages.items():
            self.assertIsNone(field.search(text), path)
            m = blob.search(text)
            if not m:
                continue
            for words in json.loads(m[1]).get("words", {}).values():
                for word in words:
                    leaked = values.get(word["id"], set()) & {str(v) for v in word.values()}
                    self.assertFalse(leaked, (path, word["id"], leaked))
                    checked += 1
        self.assertTrue(checked, "no word data found on the site to check")


if __name__ == "__main__":
    unittest.main()
