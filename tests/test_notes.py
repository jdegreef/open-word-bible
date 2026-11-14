"""Translated decision notes and cards (owb/notes.py, scripts/notes.py),
and the article links of notes (data/article_links.json)."""
import collections
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
import notes as notes_script  # noqa: E402
from owb import languages, notes  # noqa: E402

# A run of Greek letters that is no word in the source data (written as
# escapes: Greek in this project is only ever copied from the source data).
NOT_GREEK = "αβγδεζ"


def clear():
    for f in (notes.load_notes, notes.load_cards, notes.book_records, notes.book_decisions,
              notes.english_cards):
        f.cache_clear()


class TempData(unittest.TestCase):
    """Each test writes its translations to a scratch data/notes and data/cards."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, True))
        for name, value in (("NOTES", self.tmp / "notes"), ("CARDS", self.tmp / "cards")):
            patcher = mock.patch.object(notes, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        clear()
        self.addCleanup(clear)

    def run_script(self, *argv):
        err = io.StringIO()
        with redirect_stderr(err):
            code = notes_script.main(list(argv))
        return code, err.getvalue()

    def export(self, *argv):
        out = self.tmp / "work.jsonl"
        self.run_script(*argv, "-o", str(out))
        return [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]

    def write_lines(self, lines):
        path = self.tmp / "filled.jsonl"
        path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lines), encoding="utf-8")
        return path


class DigestTest(unittest.TestCase):
    def test_only_the_translated_fields_count(self):
        d = {"choice": "the Word", "alternatives": ["Reason"], "reason": "Key term.", "uncertain": False}
        self.assertEqual(notes.decision_digest(d), notes.decision_digest({**d, "uncertain": True, "footnote": True}))
        self.assertNotEqual(notes.decision_digest(d), notes.decision_digest({**d, "reason": "Key term!"}))
        self.assertNotEqual(notes.decision_digest(d), notes.decision_digest({**d, "alternatives": []}))
        self.assertRegex(notes.decision_digest(d), r"^[0-9a-f]{12}$")

    def test_slots_round_trip_the_original_words(self):
        r = next(r for r in notes.book_records("JHN") if r["id"] == "JHN.1.1.s1")
        d = next(d for d in r["decisions"] if d["id"] == "m4")
        words = notes.slot_words(notes.decision_texts(d))
        self.assertTrue(words)
        slotted = notes.to_slots(d["reason"], words)
        self.assertFalse(notes.original_words(slotted))
        self.assertIn("⟦1⟧", slotted)
        self.assertEqual(notes.expand(slotted, words), d["reason"])
        with self.assertRaises(KeyError):
            notes.expand("⟦99⟧", words)


class CheckTest(unittest.TestCase):
    D = {"id": "m1", "layer": "meaning", "language": None, "choice": "the Word",
         "alternatives": ["Reason", "the Message"], "reason": "Key term."}

    def errors(self, **entry):
        base = {"source": notes.decision_digest(self.D), "choice": "el Verbo",
                "alternatives": ["la Razón", "el Mensaje"], "reason": "Término clave."}
        found = []
        notes.check_note({**base, **entry}, self.D, "x", found, "es")
        return found

    def test_a_good_note_passes(self):
        self.assertEqual(self.errors(), [])

    def test_the_rules_of_a_note(self):
        self.assertTrue(self.errors(alternatives=["la Razón"]))                  # one too few
        self.assertTrue(self.errors(choice="{{gender:hermanos|hermanos y hermanas}}"))  # a setting
        self.assertTrue(self.errors(reason=""))
        self.assertTrue(self.errors(reason=f"Del griego {NOT_GREEK}."))         # typed Greek
        self.assertTrue(self.errors(reason="Del griego ⟦1⟧."))         # a slot left
        self.assertTrue(self.errors(source="abc"))
        self.assertTrue(self.errors(extra="x"))
        # A stale note (its English changed) need not match the English's count.
        self.assertEqual(self.errors(source="0" * 12, alternatives=["la Razón"]), [])

    def test_another_languages_rendering_decision_is_refused(self):
        found = []
        d = {**self.D, "id": "r-fr-1", "layer": "rendering", "language": "fr"}
        notes.check_note({"source": notes.decision_digest(d), "choice": "a", "alternatives": ["b", "c"],
                          "reason": "d"}, d, "x", found, "es")
        self.assertTrue(found)


class RepositoryTest(unittest.TestCase):
    def test_every_note_and_card_file_is_valid(self):
        # What CI checks: a malformed translation fails here.
        for path in notes.all_files():
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertEqual(notes.check_file(path), [])

    def test_files_are_where_they_belong(self):
        for path in notes.all_files():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn(path.parent.name, languages.READING)
            self.assertEqual(data["language"], path.parent.name)
            self.assertEqual(data["status"], "ai_draft")

    def test_the_merge_driver_covers_the_translations(self):
        attrs = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("data/**/*.json merge=owbjson", attrs)

    def test_the_pilot_translates_john_1_to_3(self):
        # Every footnoted meaning decision of John 1-3 has a current note in
        # every language other than English.
        wanted = [(r["id"], d["id"]) for r in notes.book_records("JHN")
                  if int(r["refs"][0].split(".")[1]) <= 3
                  for d in r["decisions"] if d["layer"] == "meaning" and d["footnote"]]
        self.assertTrue(wanted)
        for lang in languages.CODES[1:]:
            current = notes.current_notes(lang, "JHN")
            missing = [x for x in wanted if x[1] not in current.get(x[0], {})]
            self.assertEqual(missing, [], lang)


class PipelineTest(TempData):
    def test_export_import_and_report(self):
        lines = self.export("export", "es", "--books", "JHN", "--chapters", "1", "--footnotes-only")
        self.assertTrue(lines)
        self.assertTrue(all(x["status"] == "new" and x["footnote"] and x["layer"] == "meaning" for x in lines))
        self.assertTrue(all(x["refs"][0].startswith("JHN.1.") for x in lines))
        line = next(x for x in lines if x["record"] == "JHN.1.1.s1" and x["decision"] == "m3")
        # The context: the record's Spanish, and its Greek as slots.
        self.assertIn("Verbo", line["rendering"]["B"])
        self.assertIn("⟦1⟧", line["english"]["reason"])
        self.assertFalse(notes.original_words(line["english"]["reason"]))
        line["translation"] = {"choice": "con Dios", "alternatives": ["hacia Dios", "cara a cara con Dios"],
                               "reason": "⟦1⟧ con acusativo suele significar «hacia»."}
        code, err = self.run_script("import", "es", str(self.write_lines([line] + lines[:1])))
        self.assertEqual(code, 0, err)
        self.assertIn("imported 1, skipped 1", err)
        written = json.loads(notes.notes_path("es", "JHN").read_text(encoding="utf-8"))
        entry = written["notes"]["JHN.1.1.s1"]["m3"]
        self.assertEqual(written["status"], "ai_draft")
        self.assertEqual(entry["source"], line["source"])
        # The slot is filled with the word copied from the English.
        word = line["original"]["1"]
        self.assertTrue(entry["reason"].startswith(word + " con acusativo"))
        self.assertEqual(notes.check_file(notes.notes_path("es", "JHN")), [])
        self.assertEqual(notes.current_notes("es", "JHN")["JHN.1.1.s1"]["m3"]["choice"], "con Dios")
        # Done, it is no longer exported; the report counts it.
        again = self.export("export", "es", "--books", "JHN", "--chapters", "1", "--footnotes-only")
        self.assertEqual(len(again), len(lines) - 1)
        counts = notes_script.report(["es"])["es"]
        self.assertEqual((counts["footnotes_done"], counts["stale"]), (1, 0))

    def test_a_stale_note_falls_back_and_is_exported_again(self):
        r = next(r for r in notes.book_records("JHN") if r["id"] == "JHN.1.1.s1")
        d = next(d for d in r["decisions"] if d["id"] == "m1")
        data = notes.note_template("fr")
        data["notes"] = {r["id"]: {"m1": {"source": "0" * 12, "choice": "Au commencement",
                                          "alternatives": ["Au début", "Avant le temps"], "reason": "Ancien."}}}
        notes.write_json(notes.notes_path("fr", "JHN"), data)
        clear()
        self.assertEqual(notes.current_notes("fr", "JHN"), {})
        lines = self.export("export", "fr", "--books", "JHN", "--chapters", "1")
        line = next(x for x in lines if x["record"] == r["id"] and x["decision"] == "m1")
        self.assertEqual(line["status"], "stale")
        self.assertEqual(line["previous"]["reason"], "Ancien.")
        self.assertEqual(line["source"], notes.decision_digest(d))
        self.assertEqual(notes_script.report(["fr"])["fr"]["stale"], 1)

    def test_import_refuses_bad_lines(self):
        lines = self.export("export", "es", "--books", "JHN", "--chapters", "1", "--footnotes-only")
        changed = {**lines[0], "source": "0" * 12,
                   "translation": {**lines[0]["translation"], "choice": "x", "reason": "y",
                                   "alternatives": ["z"] * len(lines[0]["english"]["alternatives"])}}
        other = next(x for x in lines[1:] if x["english"]["alternatives"])
        short = {**other, "translation": {"choice": "x", "reason": "y", "alternatives": []}}
        code, err = self.run_script("import", "es", str(self.write_lines([changed, short])))
        self.assertEqual(code, 1)
        self.assertIn("changed after this line was exported", err)
        self.assertIn("the English has", err)
        self.assertFalse(notes.notes_path("es", "JHN").exists())

    def test_cards_round_trip(self):
        lines = self.export("export-cards", "sw", "--kinds", "glossary", "key_terms")
        kinds = collections.Counter(x["kind"] for x in lines)
        self.assertEqual(kinds["glossary"], len(notes.english_cards("glossary")))
        self.assertEqual(kinds["key_terms"], len(notes.english_cards("key_terms")))
        gl = next(x for x in lines if x["kind"] == "glossary")
        gl["translation"] = {"senses": [{"name": f"jina {i}", "note": "Maelezo."}
                                        for i, _ in enumerate(gl["english"]["senses"])]}
        term = next(x for x in lines if x["kind"] == "key_terms" and x["key"] == "grc|5485")
        term["translation"] = {"sense": "neema", "note": "Neno kuu."}
        code, err = self.run_script("import", "sw", str(self.write_lines([gl, term])))
        self.assertEqual(code, 0, err)
        self.assertEqual(notes.current_card("sw", "key_terms", "grc|5485")["sense"], "neema")
        self.assertEqual(notes.current_card("sw", "glossary", gl["key"])["senses"][0]["name"], "jina 0")
        for kind in ("glossary", "key_terms"):
            self.assertEqual(notes.check_file(notes.cards_path("sw", kind)), [])
        self.assertEqual(notes_script.report(["sw"])["sw"]["cards"]["key_terms"]["done"], 1)


class ArticleLinksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "data" / "article_links.json").read_text(encoding="utf-8"))
        cls.words = set()
        for src, prefix in (("grc", "G"), ("hbo", "H")):
            for path in (ROOT / "data" / src).glob("*.json"):
                for ws in json.loads(path.read_text(encoding="utf-8"))["verses"].values():
                    cls.words.update((prefix + (w.get("strong") or "").lstrip("0"), w["lemma"]) for w in ws)

    def test_every_link_names_real_words_and_articles(self):
        articles = {p.stem for p in (ROOT / "articles").glob("*.md")}
        self.assertGreaterEqual(len(self.data["lemmas"]), 30)
        for entry in self.data["lemmas"]:
            self.assertIn(entry["article"], articles)
            for w in entry["words"]:
                # Copied from the word data, never typed.
                self.assertIn((w["strong"], w["lemma"]), self.words, w["strong"])
        for c in self.data["categories"]:
            self.assertIn(c["article"], articles)

    def article_for(self, rid, did):
        book, chapter = rid.split(".")[0], int(rid.split(".")[1])
        records, words = build_site.load_chapter(book, chapter)
        r = next(r for r in records if r["id"] == rid)
        d = next(d for d in r["decisions"] if d["id"] == did)
        return build_site.decision_article(r, d, {w["id"]: w for ws in words.values() for w in ws})

    def test_notes_link_to_their_articles(self):
        self.assertEqual(self.article_for("JHN.1.1.s1", "m2"), "the-word-was-god")
        self.assertEqual(self.article_for("JHN.3.16.s1", "m2"), "how-god-loved-the-world")
        self.assertEqual(self.article_for("JHN.3.8.s1", "m1"), "wind-breath-and-spirit")

    def test_the_page_carries_the_links_in_its_language(self):
        records, words = build_site.load_chapter("JHN", 1)
        links = build_site.note_articles(records, words, "es")
        link = links["JHN.1.1.s1"]["m2"]
        self.assertEqual(link["lang"], "es" if link["url"].startswith("/es/") else "en")
        self.assertIn("/articles/the-word-was-god/", link["url"])
        html = build_site.chapter_notes(records, 1, "es", words)
        self.assertIn('class="note-article"', html)
        self.assertIn(build_site.catalog("es")["reader.ui"]["note_article"], html)


class BuildTest(unittest.TestCase):
    def test_translated_notes_replace_the_english(self):
        records, words = build_site.load_chapter("JHN", 1)
        page = build_site.page_notes(records, "fr")
        r = next(r for r in records if r["id"] == "JHN.1.1.s1")
        d = next(d for d in r["decisions"] if d["id"] == "m1")
        tr = page["JHN.1.1.s1"]["m1"]
        text = build_site.note_html(d, "fr", tr)
        self.assertNotIn('lang="en"', text)
        self.assertIn(build_site.html.escape(tr["choice"], quote=False), text)
        self.assertIn('lang="en"', build_site.note_html(d, "fr"))
        self.assertEqual(build_site.page_notes(records, "en"), {})

    def test_cards_are_translated_where_they_can_be(self):
        term = next(t for t in build_site.validate.KEY_TERMS.values() if t["strong"] == "5485")
        sense, lang = build_site.term_sense(term, "es")
        if notes.current_card("es", "key_terms", "grc|5485"):
            self.assertEqual((sense, lang), (notes.current_card("es", "key_terms", "grc|5485")["sense"], "es"))
        self.assertEqual(build_site.term_sense(term, "en"), (term["sense"], "en"))


if __name__ == "__main__":
    unittest.main()
