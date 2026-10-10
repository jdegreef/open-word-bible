import tempfile
import unittest
from pathlib import Path

from owb.sources import open_bibles

USFX = """<?xml version="1.0" encoding="utf-8"?><usfx><book id="JHN"><id id="JHN">John</id><h>John</h>
<c id="1"/><s>The Word</s><p><v id="1"/>In the beginning was the Word.<ve/><v id="5"/>The light shines in the darkness,
and the darkness hasn't overcome<f caller="+">A footnote that must not appear.</f> it.<ve/></p>
<c id="2"/><p><v id="1"/>On the third day<x>cross ref</x> there was a wedding.<ve/></p></book>
<book id="TOB"><c id="1"/><p><v id="1"/>Apocrypha is dropped.<ve/></p></book></usfx>"""

OSIS = """<osis><osisText><div type="book" osisID="John"><chapter osisID="John.1">
<p><verse osisID="John.1.1" sID="a" n="1"/>In the beginning <note>no notes</note>was the Word.<verse eID="a"/></p>
<p><verse osisID="John.1.2" sID="b" n="2"/>The same was<verse eID="b"/></p></chapter></div>
<div type="book" osisID="1Macc"><chapter osisID="1Macc.1"><verse osisID="1Macc.1.1" sID="c"/>Dropped.<verse eID="c"/></chapter></div>
</osisText></osis>"""

ZEFANIA = """<XMLBIBLE><BIBLEBOOK bnumber="43"><CHAPTER cnumber="1">
<VERS vnumber="1">In the beginning was the Word.</VERS><VERS vnumber="8">He was not the light, but [came]</VERS>
</CHAPTER></BIBLEBOOK><BIBLEBOOK bnumber="70"><CHAPTER cnumber="1"><VERS vnumber="1">Not canonical</VERS></CHAPTER></BIBLEBOOK></XMLBIBLE>"""


def parse(fmt, text):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / f"sample.{fmt}.xml"
        path.write_text(text, encoding="utf-8")
        return open_bibles.PARSERS[fmt](path)


class OpenBiblesTest(unittest.TestCase):
    def test_usfx_skips_footnotes_headings_and_apocrypha(self):
        verses = parse("usfx", USFX)
        self.assertEqual(verses, {
            ("JHN", 1, 1): "In the beginning was the Word.",
            ("JHN", 1, 5): "The light shines in the darkness, and the darkness hasn't overcome it.",
            ("JHN", 2, 1): "On the third day there was a wedding.",
        })

    def test_osis_milestones_and_notes(self):
        self.assertEqual(parse("osis", OSIS), {
            ("JHN", 1, 1): "In the beginning was the Word.",
            ("JHN", 1, 2): "The same was",
        })

    def test_zefania_book_numbers(self):
        self.assertEqual(parse("zefania", ZEFANIA), {
            ("JHN", 1, 1): "In the beginning was the Word.",
            ("JHN", 1, 8): "He was not the light, but [came]",
        })

    def test_only_public_domain_editions_are_listed(self):
        for code, (_, _, _, _, licence) in open_bibles.EDITIONS.items():
            self.assertTrue(licence.startswith("Public domain"), code)


if __name__ == "__main__":
    unittest.main()
