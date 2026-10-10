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
    """The restricted Greek values for the verses in content/, by token id."""
    wanted = {r.replace(".", " ", 1).replace(".", ":") for r in content_refs()}
    reader = csv.DictReader(io.StringIO(read_text("macula-greek", macula_greek.TSV_PATH)),
                            delimiter="\t", quoting=csv.QUOTE_NONE)
    out = {}
    for row in reader:
        if row["ref"].split("!")[0] in wanted:
            out[row["xml:id"]] = {row[c] for c in macula_greek.RESTRICTED if row[c].strip()}
    return out


class LicensingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.site = Path(cls.tmp.name) / "site"
        build_site.build(cls.site)
        cls.extracts = {p: json.loads(p.read_text(encoding="utf-8"))
                        for p in sorted((ROOT / "data").rglob("*.json"))}
        cls.pages = {p: p.read_text(encoding="utf-8") for p in sorted(cls.site.rglob("*"))
                     if p.is_file()}

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
            for words in data["verses"].values():
                for word in words:
                    leaked = values.get(word["id"], set()) & {str(v) for v in word.values()}
                    self.assertFalse(leaked, (path, word["id"], leaked))

    def test_site_has_no_restricted_fields_or_values(self):
        values = {v for vs in restricted_values().values() for v in vs}
        field = re.compile(r'"(%s)"\s*:' % "|".join(RESTRICTED))
        for path, text in self.pages.items():
            self.assertIsNone(field.search(text), path)
            quoted = set(re.findall(r'"([^"\\]{1,40})"', text))
            self.assertFalse(quoted & values, path)


if __name__ == "__main__":
    unittest.main()
