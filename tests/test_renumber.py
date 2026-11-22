"""Moving readers' saved verses to NIV numbers (owb/renumber.py)."""
import unittest

from owb import renumber

OLD, NEW = 100, renumber.SWITCHED_MS + 100


class RenumberTest(unittest.TestCase):
    def test_verses_move_to_the_numbers_readers_see(self):
        self.assertEqual(renumber.verse("PSA.3.1"), "PSA.3.0")      # a psalm's title
        self.assertEqual(renumber.verse("PSA.3.2"), "PSA.3.1")
        self.assertEqual(renumber.verse("MAL.3.19"), "MAL.4.1")
        self.assertEqual(renumber.verse("PSA.13.6"), "PSA.13.5")    # two NIV verses: the first
        self.assertEqual(renumber.verse("JHN.3.16"), "JHN.3.16")
        self.assertNotIn("JHN.3.16", renumber.table())

    def test_passages_stay_in_one_chapter(self):
        self.assertEqual(renumber.passage("PSA.3.1-9"), "PSA.3.0-8")
        self.assertEqual(renumber.passage("MAL.3.19-24"), "MAL.4.1-6")
        self.assertEqual(renumber.passage("PSA.13.1-6"), "PSA.13.0-6")
        self.assertEqual(renumber.passage("PSA.51.1-2"), "PSA.51.0")
        # Hebrew 1 Kings 5:1-20 is NIV 4:21-34 and 5:1-6: the chapter it starts in.
        self.assertEqual(renumber.passage("1KI.5.1-20"), "1KI.4.21-34")
        self.assertEqual(renumber.passage("JHN.3.16-21"), "JHN.3.16-21")

    def test_only_what_was_saved_before_the_switch_moves(self):
        out = renumber.store({"PSA.3.2": {"h": "blue", "at": OLD}, "PSA.4.2": {"h": "pink", "at": NEW}},
                             renumber.verse)
        self.assertEqual(out, {"PSA.3.1": {"h": "blue", "at": OLD}, "PSA.4.2": {"h": "pink", "at": NEW}})

    def test_two_verses_that_meet_keep_both(self):
        # Hebrew Numbers 25:19 and 26:1 are NIV 26:1.
        out = renumber.store({"NUM.25.19": {"h": "yellow", "n": "first", "t": ["Plague"], "at": OLD},
                              "NUM.26.1": {"b": True, "n": "second", "at": OLD + 5}}, renumber.verse)
        self.assertEqual(out, {"NUM.26.1": {"h": "yellow", "b": True, "n": "first\n\nsecond",
                                            "t": ["Plague"], "at": OLD + 5}})

    def test_a_reading_place_moves(self):
        self.assertEqual(renumber.place({"book": "MAL", "chapter": 3, "verse": "20", "at": OLD}),
                         {"book": "MAL", "chapter": 4, "verse": "2", "at": OLD})
        # "3:5": a verse of the chapter before, on Joel 4's page.
        self.assertEqual(renumber.place({"book": "JOL", "chapter": 4, "verse": "3:5", "at": OLD}),
                         {"book": "JOL", "chapter": 2, "verse": "32", "at": OLD})
        place = {"book": "MAL", "chapter": 3, "verse": "20", "at": NEW}
        self.assertEqual(renumber.place(place), place)


if __name__ == "__main__":
    unittest.main()
