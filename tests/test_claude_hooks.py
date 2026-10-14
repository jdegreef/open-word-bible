"""The PreToolUse hook that holds Claude's edits to CLAUDE.md's rules
(.claude/hooks/guard_edits.py)."""
import importlib.util
import json
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("guard_edits", ROOT / ".claude/hooks/guard_edits.py")
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


def _unaccented(word):
    return unicodedata.normalize("NFC", "".join(
        c for c in unicodedata.normalize("NFD", word) if not unicodedata.combining(c)))


# Words copied from the extracts, so this file types no Greek or Hebrew.
_grc = json.loads((ROOT / "data/grc/JHN.1.json").read_text(encoding="utf-8"))["verses"]
LOGOS = _grc["JHN.1.1"][4]["text"]
_hbo_file = sorted((ROOT / "data/hbo").glob("*.json"))[0]
_hbo = next(iter(json.loads(_hbo_file.read_text(encoding="utf-8"))["verses"].values()))
HEBREW = next(t["lemma"] for t in _hbo if len(t["lemma"]) > 2)
FORMS = frozenset({LOGOS, HEBREW})
RECORD = next((ROOT / "content/JHN").glob("*.json"))


def problems(tool, tool_input, forms=FORMS):
    return guard.problems(tool, tool_input, forms=lambda: forms)


def edit(path, new, old="x"):
    return {"file_path": str(ROOT / path), "old_string": old, "new_string": new}


class OriginalLanguage(unittest.TestCase):
    def test_source_forms_pass(self):
        self.assertEqual(problems("Edit", edit("docs/john-terms.md", f"the word {LOGOS}")), [])
        self.assertEqual(problems("Edit", edit("docs/john-terms.md", f"see {HEBREW}")), [])

    def test_typed_word_is_refused(self):
        typed = _unaccented(LOGOS)
        self.assertNotEqual(typed, LOGOS)
        found = problems("Edit", edit("docs/john-terms.md", f"the word {typed}"))
        self.assertEqual(len(found), 1)
        self.assertIn(typed, found[0])

    def test_typed_hebrew_is_refused(self):
        self.assertTrue(problems("Edit", edit("data/key_terms.json", _unaccented(HEBREW) + "א")))

    def test_words_already_there_may_move(self):
        typed = _unaccented(LOGOS)
        self.assertEqual(problems("Edit", edit("docs/john-terms.md", f"  {typed}", old=typed)), [])

    def test_code_is_not_checked(self):
        self.assertEqual(problems("Edit", edit("owb/translit.py", _unaccented(LOGOS))), [])

    def test_shell_commands_naming_text_folders(self):
        typed = _unaccented(LOGOS)
        self.assertTrue(problems("Bash", {"command": f"echo {typed} >> docs/john-terms.md"}))
        self.assertEqual(problems("Bash", {"command": f"grep -rl {LOGOS} content/"}), [])
        self.assertEqual(problems("Bash", {"command": f"python3 -c 'print(\"{typed}\")'"}), [])

    def test_without_sources_the_check_is_skipped(self):
        self.assertEqual(problems("Edit", edit("docs/john-terms.md", _unaccented(LOGOS)), forms=None), [])


class Status(unittest.TestCase):
    def test_edit_marking_reviewed_is_refused(self):
        for status in ("reviewed", "meaning_reviewed", "revised"):
            found = problems("Edit", edit(RECORD.relative_to(ROOT), f'"status": "{status}"',
                                          old='"status": "ai_draft"'))
            self.assertEqual(len(found), 1, status)

    def test_ai_draft_is_fine(self):
        self.assertEqual(problems("Edit", edit(RECORD.relative_to(ROOT), '"status": "ai_draft"')), [])

    def test_write_compares_with_the_file(self):
        text = RECORD.read_text(encoding="utf-8")
        self.assertEqual(problems("Write", {"file_path": str(RECORD), "content": text}), [])
        marked = text.replace('"status": "ai_draft"', '"status": "reviewed"', 1)
        self.assertTrue(problems("Write", {"file_path": str(RECORD), "content": marked}))

    def test_only_content_is_checked(self):
        self.assertEqual(problems("Edit", edit("backend/translation/models.py", '"status": "reviewed"')), [])

    def test_shell_writes(self):
        self.assertTrue(problems("Bash", {"command": "sed -i 's/\"ai_draft\"/\"reviewed\"/' content/JHN/x.json"}))
        self.assertEqual(problems("Bash", {"command": "grep -rl '\"reviewed\"' content/"}), [])


if __name__ == "__main__":
    unittest.main()
