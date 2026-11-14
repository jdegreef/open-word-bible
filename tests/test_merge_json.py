"""scripts/merge_json.py: the structural merge driver for translation JSON."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import merge_json  # noqa: E402
from merge_json import MISSING, Conflict, merge  # noqa: E402


def record(rid, langs, decisions=()):
    return {"id": rid, "renderings": {lang: {"L": f"{lang} {rid}"} for lang in langs},
            "decisions": [{"id": d, "language": d.split("-")[1]} for d in decisions], "status": "ai_draft"}


class MergeTest(unittest.TestCase):
    def test_two_languages_added_to_one_record(self):
        base = {"records": [record("JUD.1.1.s1", ["en", "ru"], ["r-ru-1"])]}
        ours = {"records": [record("JUD.1.1.s1", ["en", "ru", "uk"], ["r-ru-1", "r-uk-1"])]}
        theirs = {"records": [record("JUD.1.1.s1", ["en", "ru", "ja"], ["r-ru-1", "r-ja-1", "r-ja-2"])]}
        out = merge(base, ours, theirs)["records"][0]
        self.assertEqual(list(out["renderings"]), ["en", "ru", "uk", "ja"])
        self.assertEqual([d["id"] for d in out["decisions"]], ["r-ru-1", "r-uk-1", "r-ja-1", "r-ja-2"])

    def test_keys_theirs_added_stay_where_theirs_put_them(self):
        base = {"a": 1, "c": 3}
        ours = {"a": 1, "c": 3, "z": 26}
        theirs = {"a": 1, "b": 2, "c": 3}
        self.assertEqual(list(merge(base, ours, theirs)), ["a", "b", "c", "z"])

    def test_new_records_on_both_sides(self):
        base = {"records": [record("A", ["en"])]}
        ours = {"records": [record("A", ["en"]), record("B", ["en"])]}
        theirs = {"records": [record("A", ["en"]), record("C", ["en"])]}
        self.assertEqual([r["id"] for r in merge(base, ours, theirs)["records"]], ["A", "B", "C"])

    def test_one_side_changes_a_value(self):
        base = {"headings": {"PHP.1.1.s1": {"en": "Greeting", "ja": "あいさつ"}}}
        ours = {"headings": {"PHP.1.1.s1": {"en": "Greeting", "ja": "挨拶"}}}
        theirs = {"headings": {"PHP.1.1.s1": {"en": "Greeting", "ja": "あいさつ", "uk": "Привітання"}}}
        self.assertEqual(merge(base, ours, theirs)["headings"]["PHP.1.1.s1"],
                         {"en": "Greeting", "ja": "挨拶", "uk": "Привітання"})

    def test_one_side_deletes_a_key(self):
        self.assertEqual(merge({"a": 1, "b": 2}, {"a": 1}, {"a": 1, "b": 2, "c": 3}), {"a": 1, "c": 3})

    def test_lists_without_ids_merge_when_both_append(self):
        self.assertEqual(merge(["L"], ["L", "B"], ["L", "R"]), ["L", "B", "R"])

    def test_both_sides_change_one_value_is_a_conflict(self):
        base = {"headings": {"X": {"ja": "a"}}}
        with self.assertRaises(Conflict) as cm:
            merge(base, {"headings": {"X": {"ja": "b"}}}, {"headings": {"X": {"ja": "c"}}})
        self.assertEqual(str(cm.exception), "headings/X/ja")

    def test_change_against_delete_is_a_conflict(self):
        with self.assertRaises(Conflict):
            merge({"a": 1}, {}, {"a": 2})

    def test_added_on_both_sides(self):
        self.assertEqual(merge(MISSING, {"a": 1}, {"b": 2}), {"a": 1, "b": 2})


class DriverTest(unittest.TestCase):
    """The driver as git runs it, in a throwaway repository."""

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "test")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.hooksPath", "/dev/null")
        self.git("config", "merge.owbjson.driver", f"{sys.executable} {merge_json.__file__} %O %A %B %P")
        (self.repo / ".gitattributes").write_text("*.json merge=owbjson\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, value):
        (self.repo / "PHP.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "x")

    def branches(self, base, ours, theirs):
        self.write(base)
        self.git("checkout", "-q", "-b", "theirs")
        self.write(theirs)
        self.git("checkout", "-q", "main")
        self.write(ours)
        return self.git("merge", "-q", "--no-edit", "theirs")

    def test_languages_from_both_branches_merge_cleanly(self):
        base = {"headings": {"PHP.1.1.s1": {"en": "Greeting"}, "PHP.1.3.s1": {"en": "Thanks and prayer"}}}
        ours = {"headings": {k: {**v, "uk": k} for k, v in base["headings"].items()}}
        theirs = {"headings": {k: {**v, "ja": k} for k, v in base["headings"].items()}}
        result = self.branches(base, ours, theirs)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.repo / "PHP.json").read_text(encoding="utf-8")
        self.assertEqual(json.loads(text)["headings"]["PHP.1.3.s1"],
                         {"en": "Thanks and prayer", "uk": "PHP.1.3.s1", "ja": "PHP.1.3.s1"})
        self.assertTrue(text.endswith("}\n"))

    def test_a_real_conflict_falls_back_to_markers(self):
        result = self.branches({"headings": {"X": {"ja": "a"}}}, {"headings": {"X": {"ja": "b"}}},
                               {"headings": {"X": {"ja": "c"}}})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("<<<<<<<", (self.repo / "PHP.json").read_text(encoding="utf-8"))
        self.assertIn("headings/X/ja", result.stderr)


if __name__ == "__main__":
    unittest.main()
