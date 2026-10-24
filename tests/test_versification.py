import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from owb import refs, versification
from owb.sources import macula_hebrew, open_bibles, sblgnt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_versification  # noqa: E402


def ref(verse_id):
    return refs.parse(verse_id)


def ids(refs_):
    return [str(r) for r in refs_]


class VersificationTest(unittest.TestCase):
    def test_psalm_titles_are_verse_one(self):
        self.assertEqual(ids(versification.to_english(ref("PSA.3.1"))), [])
        self.assertEqual(ids(versification.to_english(ref("PSA.3.2"))), ["PSA.3.1"])
        self.assertEqual(ids(versification.to_source(ref("PSA.3.1"))), ["PSA.3.2"])
        self.assertEqual(ids(versification.to_source(ref("PSA.3.8"))), ["PSA.3.9"])
        # Untitled psalms, and psalms whose title shares verse 1, are not renumbered.
        for verse_id in ("PSA.1.1", "PSA.2.12", "PSA.25.1"):
            self.assertEqual(ids(versification.to_english(ref(verse_id))), [verse_id])

    def test_two_verse_titles(self):
        for psalm in (51, 52, 54, 60):
            self.assertEqual(ids(versification.to_english(ref(f"PSA.{psalm}.1"))), [])
            self.assertEqual(ids(versification.to_english(ref(f"PSA.{psalm}.2"))), [])
            self.assertEqual(ids(versification.to_english(ref(f"PSA.{psalm}.3"))), [f"PSA.{psalm}.1"])
            self.assertEqual(ids(versification.to_source(ref(f"PSA.{psalm}.1"))), [f"PSA.{psalm}.3"])

    def test_verses_that_span_two(self):
        self.assertEqual(ids(versification.to_english(ref("PSA.13.6"))), ["PSA.13.5", "PSA.13.6"])
        self.assertEqual(ids(versification.to_source(ref("PSA.13.5"))), ["PSA.13.6"])
        self.assertEqual(ids(versification.to_source(ref("1KI.18.33"))), ["1KI.18.33", "1KI.18.34"])

    def test_other_books_and_chapters(self):
        self.assertEqual(ids(versification.to_english(ref("GEN.32.1"))), ["GEN.31.55"])
        self.assertEqual(ids(versification.to_english(ref("MAL.3.19"))), ["MAL.4.1"])
        self.assertEqual(versification.english_chapters("GEN", 32), [31, 32])
        self.assertEqual(ids(versification.to_source(ref("GEN.31.55"))), ["GEN.32.1"])
        self.assertEqual(ids(versification.to_source(ref("EXO.8.32"))), ["EXO.8.28"])
        self.assertEqual(versification.english_chapters("PSA", 3), [3])
        self.assertEqual(ids(versification.to_english(ref("JHN.1.1"))), ["JHN.1.1"])
        # Nehemiah 7:68 is not in the Leningrad Codex.
        self.assertEqual(versification.to_source(ref("NEH.7.68")), ())

    def test_english_ids(self):
        self.assertEqual(versification.english_ids(["PSA.3.1", "PSA.3.2", "PSA.3.3"]),
                         ["PSA.3.1", "PSA.3.2"])
        self.assertEqual(versification.english_ids(["PSA.13.5", "PSA.13.6"]),
                         ["PSA.13.4", "PSA.13.5", "PSA.13.6"])

    def test_new_testament_verses(self):
        self.assertEqual(ids(versification.to_english(ref("2CO.13.13"))), ["2CO.13.14"])
        self.assertEqual(ids(versification.to_source(ref("2CO.13.14"))), ["2CO.13.13"])
        self.assertEqual(ids(versification.to_source(ref("2CO.13.13"))), ["2CO.13.12"])
        self.assertEqual(ids(versification.to_source(ref("REV.13.1"))), ["REV.12.18", "REV.13.1"])
        self.assertEqual(ids(versification.to_english(ref("JHN.3.16"))), ["JHN.3.16"])
        self.assertEqual(versification.english_chapters("REV", 12), [12, 13])

    def test_derive_from_a_verse_map(self):
        xml = """<verseMap><book osisID="Ps">
        <verse wlc="Ps.3.2" kjv="Ps.3.1" type="full"/><verse wlc="Ps.3.3" kjv="Ps.3.2" type="full"/>
        <verse wlc="Ps.51.2" kjv="Ps.51.1" type="full"/><verse wlc="Ps.51.3" kjv="Ps.51.1" type="full"/>
        <verse wlc="Ps.13.6!a" kjv="Ps.13.5" type="partial"/>
        <verse wlc="Ps.13.6!b" kjv="Ps.13.6" type="partial"/></book>
        <book osisID="1Kgs"><verse wlc="1Kgs.18.34!a" kjv="1Kgs.18.33!b" type="partial"/></book></verseMap>"""
        hebrew = {ref(v) for v in ("PSA.3.1", "PSA.3.2", "PSA.3.3", "PSA.51.1", "PSA.51.2", "PSA.51.3",
                                   "PSA.13.5", "PSA.13.6", "1KI.18.33", "1KI.18.34")}
        table, absent = versification.derive(xml, hebrew - {ref("PSA.3.3")})
        table = {str(h): ids(es) for h, es in table.items()}
        self.assertEqual(table, {
            "PSA.3.1": [], "PSA.3.2": ["PSA.3.1"],
            "PSA.51.1": [], "PSA.51.2": [], "PSA.51.3": ["PSA.51.1"],
            "PSA.13.5": [], "PSA.13.6": ["PSA.13.5", "PSA.13.6"],
            "1KI.18.34": ["1KI.18.33", "1KI.18.34"]})
        self.assertEqual(absent, {ref("PSA.3.3")})


class VersificationDataTest(unittest.TestCase):
    """The checked-in table against the pinned sources."""

    @classmethod
    def setUpClass(cls):
        cls.hebrew = set(macula_hebrew.verses())
        # Each Bible parsed once: {code: {Ref}} for the Old Testament.
        cls.bibles = {code: {refs.Ref(*key) for key in open_bibles.load(code) if key[0] in refs.OT_CODES}
                      for code in open_bibles.EDITIONS}

    def test_table_is_up_to_date(self):
        self.assertEqual(build_versification.build(),
                         versification.DATA.read_text(encoding="utf-8"),
                         "run scripts/build_versification.py")

    def mapped(self, book=None):
        """How many of our verses hold each English verse."""
        return Counter(e for h in self.hebrew if book in (None, h.book)
                       for e in versification.to_english(h))

    def test_english_bibles_have_every_mapped_verse_once(self):
        # Every Hebrew verse lands on English verses the English Bibles have,
        # and every English Old Testament verse is covered, except Nehemiah
        # 7:68, which the Leningrad Codex lacks.
        mapped = self.mapped()
        for code in ("bsb", "web", "kjv", "asv"):
            english = self.bibles[code]
            with self.subTest(code):
                self.assertEqual(set(mapped) - english, set())
                self.assertEqual(english - set(mapped), {ref("NEH.7.68")})

    def test_psalms_in_every_reference_bible(self):
        mapped = self.mapped("PSA")
        # Only Hebrew 13:6 holds two English verses, and no English verse is
        # split between two Hebrew ones.
        self.assertEqual(set(mapped.values()), {1})
        for code, verses in self.bibles.items():
            psalms = {r for r in verses if r.book == "PSA"}
            if psalms:
                with self.subTest(code):
                    self.assertEqual(psalms, set(mapped))

    def test_title_verses_match_the_verse_counts(self):
        # Where a psalm has n more verses in Hebrew than in English, its first
        # n verses are the title (Psalm 13 has as many in both but its title
        # is verse 1 and its last verse holds two English ones).
        hebrew, english, titles = Counter(), Counter(), defaultdict(list)
        for h in self.hebrew:
            if h.book == "PSA":
                hebrew[h.chapter] += 1
                if not versification.to_english(h):
                    titles[h.chapter].append(h.verse)
        english.update(r.chapter for r in self.bibles["bsb"] if r.book == "PSA")
        for psalm in range(1, 151):
            with self.subTest(psalm=psalm):
                expected = 1 if psalm == 13 else hebrew[psalm] - english[psalm]
                self.assertEqual(sorted(titles[psalm]), list(range(1, expected + 1)))


class NewTestamentNumberingTest(unittest.TestCase):
    """versification.NEW_TESTAMENT against the SBLGNT and the KJV: every
    SBLGNT verse lands on KJV verses, and every KJV verse is covered except
    those the SBLGNT leaves out."""

    # Not renumbered: absent from the SBLGNT's text.
    OMITTED = {"MAT.17.21", "MAT.18.11", "MAT.23.14", "MRK.7.16", "MRK.9.44", "MRK.9.46",
               "MRK.11.26", "MRK.15.28", "LUK.17.36", "LUK.23.17", "JHN.5.4", "ACT.8.37",
               "ACT.15.34", "ACT.24.7", "ACT.28.29", "ROM.16.25", "ROM.16.26", "ROM.16.27"}

    def test_every_verse_lands_once(self):
        nt = refs.BOOK_CODES[refs.BOOK_CODES.index("MAT"):]
        greek = [r for code in nt for r in sblgnt.load_book(code)]
        kjv = {refs.Ref(*key) for key in open_bibles.load("kjv") if key[0] in nt}
        mapped = {e for r in greek for e in versification.to_english(r)}
        self.assertEqual(mapped - kjv, set())
        self.assertEqual({str(r) for r in kjv - mapped}, self.OMITTED)
        for r in kjv - {ref(v) for v in self.OMITTED}:
            with self.subTest(str(r)):
                self.assertTrue(versification.to_source(r))
                self.assertTrue(set(versification.to_source(r)) <= set(greek))


if __name__ == "__main__":
    unittest.main()
