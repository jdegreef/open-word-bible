"""The speaker layer pilot: data/speakers/ (owb/speakers.py)."""
import json
import unittest
from pathlib import Path

from owb import languages, speakers

ROOT = Path(__file__).resolve().parents[1]


def records(book):
    return [r for p in sorted((ROOT / "content" / book).glob("*.json"))
            for r in json.loads(p.read_text(encoding="utf-8"))["records"]]


class SpeakersTest(unittest.TestCase):
    def test_pilot_files_cover_every_record(self):
        codes = list(languages.CODES)
        paths = sorted(speakers.DIR.glob("*.json"))
        self.assertEqual([p.stem for p in paths], ["JER", "JOB"])
        for path in paths:
            self.assertEqual(speakers.errors(path.stem, records(path.stem), codes), [], path.stem)

    def test_job_follows_the_book_s_own_headings(self):
        data = speakers.load("JOB")["records"]
        self.assertEqual(data["JOB.4.1.s1"], "narrator")   # "Then Eliphaz the Temanite answered:"
        self.assertEqual(data["JOB.4.2.s1"], "eliphaz")
        self.assertEqual(data["JOB.5.27.s1"], "eliphaz")
        self.assertEqual(data["JOB.38.1.s1"], "narrator")
        self.assertEqual(data["JOB.38.2.s1"], "god")
        self.assertEqual(data["JOB.40.4.s1"], "job")
        self.assertEqual(data["JOB.42.17.s1"], "narrator")
        jer = speakers.load("JER")["records"]
        self.assertEqual(jer["JER.1.1.s1"], "narrator")
        self.assertEqual(jer["JER.1.6.s1"], "jeremiah")    # "I said, 'Oh, Lord GOD! ...'"
        self.assertEqual(jer["JER.1.7.s1"], "god")

    def test_a_label_where_the_voice_changes(self):
        ids = ["JOB.4.1.s1", "JOB.4.2.s1", "JOB.4.3.s1", "JOB.4.4.s1"]
        self.assertEqual(speakers.labels("JOB", ids, "es"), {"JOB.4.1.s1": "Narrador", "JOB.4.2.s1": "Elifaz"})
        self.assertEqual(speakers.labels("JOB", ids[2:], "en"), {"JOB.4.3.s1": "Eliphaz"})
        self.assertEqual(speakers.labels("GEN", ["GEN.1.1.s1"], "en"), {})

    def test_errors(self):
        # A record the file names that the book no longer has; a language a
        # speaker has no name in.
        found = speakers.errors("JOB", records("JOB")[1:], ["en", "xx"])
        self.assertIn("JOB.1.1.s1: no such record", found)
        self.assertTrue(any("no name in xx" in e for e in found))


if __name__ == "__main__":
    unittest.main()
