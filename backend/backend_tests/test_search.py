"""Search (GET /api/search/, translation/search.py): the tables import_content
builds from the site's own search documents, and the endpoint, in each site
language."""
import sys

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

from api import views
from backend_tests.test_backend import import_content, load_extract_words
from translation import search
from translation.models import SearchEntry, SearchLanguage

sys.path.insert(0, str(settings.REPO_ROOT / "scripts"))
import build_site  # noqa: E402


def verse_ids(doc):
    return {f"{doc['bk']}.{doc['c']}.{v}" for v in doc["vv"]}


class SearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        load_extract_words()
        import_content(search=True)

    def setUp(self):
        cache.clear()   # the search throttle counts requests in the cache

    def get(self, status=200, **params):
        response = self.client.get("/api/search/", params)
        self.assertEqual(response.status_code, status, response.content[:300])
        return response.json()

    def every(self, q, kind, lang="en", sort="relevance"):
        """Every result of one kind, page by page."""
        docs, offset = [], 0
        while True:
            answer = self.get(q=q, lang=lang, type=kind, sort=sort, offset=offset, limit=50)
            docs += answer["results"]
            offset += 50
            if offset >= answer["total"]:
                return docs

    # ---- The tables -------------------------------------------------------

    def test_import_builds_every_site_languages_documents(self):
        self.assertEqual(sorted(SearchLanguage.objects.values_list("code", flat=True)),
                         sorted(build_site.LANGUAGES))
        for lang in build_site.LANGUAGES:
            docs = build_site.search_documents(lang)["docs"]
            entries = SearchEntry.objects.filter(language=lang).order_by("position")
            self.assertEqual(entries.count(), len(docs), lang)
            self.assertEqual(entries.first().doc, docs[0])
            self.assertFalse(entries.filter(vector__isnull=True).exists())

    def test_rebuild_replaces_rather_than_adds(self):
        before = SearchEntry.objects.count()
        search.rebuild()
        self.assertEqual(SearchEntry.objects.count(), before)

    # ---- Matching ---------------------------------------------------------

    def test_word_search_groups_the_best_of_each_kind(self):
        answer = self.get(q="light", lang="en")
        self.assertIsNone(answer["reference"])
        self.assertGreater(answer["totals"]["verse"], 0)
        self.assertGreater(answer["totals"]["note"], 0)
        kinds = [d["k"] for d in answer["results"]]
        self.assertEqual(kinds, sorted(kinds, key="cvna".index))
        self.assertLessEqual(kinds.count("v"), 8)

    def test_stemming_finds_other_forms(self):
        # "loving" is nowhere in the text; John 3:16 says "love".
        found = set().union(*(verse_ids(d) for d in self.every("loving", "verse")))
        self.assertIn("JHN.3.16", found)

    def test_a_word_matches_as_the_reader_types(self):
        whole = set().union(*(verse_ids(d) for d in self.every("light", "verse")))
        typing = set().union(*(verse_ids(d) for d in self.every("ligh", "verse")))
        self.assertTrue(whole and whole <= typing)
        # A stemmer shortens "running" to "run", so "runn" matches only word for word.
        self.assertGreater(self.get(q="runn", lang="en")["totals"].get("verse", 0), 0)

    def test_words_a_stemmer_drops(self):
        # "I" and "am" are English stop words; John 8:24 and 8:58 say "I am".
        found = set().union(*(verse_ids(d) for d in self.every('"I am"', "verse")))
        self.assertTrue({"JHN.8.24", "JHN.8.58"} <= found, sorted(found)[:10])

    def test_every_option_of_a_setting_is_found(self):
        # Colossians 1:1 reads "Christ" or "Messiah" by the reader's setting.
        found = set().union(*(verse_ids(d) for d in self.every("Messiah", "verse")))
        self.assertIn("COL.1.1", found)

    def test_quoted_phrase(self):
        found = set().union(*(verse_ids(d) for d in self.every('"born from above"', "verse")))
        self.assertTrue({"JHN.3.3", "JHN.3.7"} <= found, found)
        # Not every sentence with "born": English drops "from" and "above".
        self.assertNotIn("JHN.3.6", found)
        self.assertEqual(self.every('"above from born"', "verse"), [])
        # A phrase and a word together.
        both = set().union(*(verse_ids(d) for d in self.every('"born from above" Jesus', "verse")))
        self.assertTrue(both and both <= found)

    def test_accents_are_ignored_in_each_language(self):
        for lang, q in (("es", "senor"), ("fr", "lumiere"), ("sw", "neema")):
            with self.subTest(lang=lang):
                self.assertGreater(self.get(q=q, lang=lang)["totals"].get("verse", 0), 0)

    def test_english_notes_are_found_on_other_language_sites(self):
        # Meaning notes are written in English: "the victor's wreath" (Philippians 4:1).
        notes = self.every("wreath", "note", lang="es")
        self.assertIn("the victor’s wreath", [n["t"] for n in notes])

    def test_note_results_carry_a_marked_passage(self):
        notes = self.get(q="grace", lang="en", type="note")["results"]
        self.assertTrue(any("⟦" in n.get("hl", "") for n in notes))

    def test_bible_order_and_paging(self):
        def plain(docs):
            return [{k: v for k, v in d.items() if k != "hl"} for d in docs]
        by_relevance = plain(self.every("grace", "note"))
        in_order = plain(self.every("grace", "note", sort="order"))
        self.assertEqual(len(in_order), self.get(q="grace", lang="en")["totals"]["note"])
        self.assertCountEqual([str(d) for d in in_order], [str(d) for d in by_relevance])
        positions = {str(e.doc): e.position for e in SearchEntry.objects.filter(language="en", kind="n")}
        order = [positions[str(d)] for d in in_order]
        self.assertEqual(order, sorted(order))
        first = self.get(q="grace", lang="en", type="note", limit=2)["results"]
        second = self.get(q="grace", lang="en", type="note", limit=2, offset=2)["results"]
        self.assertFalse([d for d in first if d in second])

    def test_did_you_mean(self):
        answer = self.get(q="messiahh", lang="en")
        self.assertEqual(answer["totals"], {})
        self.assertEqual(answer["suggestion"], "messiah")

    def test_operators_in_a_query_are_only_text(self):
        for q in ("a & | ! :* ' ( ) <->", "light:* | !grace", "light\x00", "''"):
            with self.subTest(q=q):
                self.get(q=q, lang="en")

    def test_short_or_empty_queries(self):
        self.assertEqual(self.get(q="l", lang="en")["results"], [])
        self.assertEqual(self.get(lang="en")["results"], [])

    # ---- References -------------------------------------------------------

    def test_a_reference_is_answered_by_its_verses_alone(self):
        answer = self.get(q="jn 3:16", lang="en")
        ref = answer["reference"]
        self.assertEqual((ref["label"], ref["url"], ref["shown"]), ("John 3:16", "/jhn/3/#v16", [16]))
        self.assertTrue(all("JHN.3.16" in verse_ids(d) for d in ref["sentences"]))
        self.assertEqual(answer["results"], [])

    def test_references_in_another_language(self):
        ref = self.get(q="Juan 3:16", lang="es")["reference"]
        self.assertEqual((ref["label"], ref["url"]), ("Juan 3:16", "/es/jhn/3/#v16"))
        ref = self.get(q="Filipenses 4:6-7", lang="es")["reference"]
        self.assertEqual(ref["shown"], [6, 7])

    def test_references_not_translated_and_words_that_look_like_one(self):
        ref = self.get(q="rev 3:20", lang="en")["reference"]
        self.assertEqual(ref["label"], "Revelation 3:20")
        self.assertNotIn("url", ref)
        ref = self.get(q="John 4:60", lang="en")["reference"]
        self.assertEqual((ref["url"], ref["shown"], ref["sentences"]), ("/jhn/4/", [], []))
        self.assertIsNone(self.get(q="son 3", lang="en")["reference"])

    # ---- The request ------------------------------------------------------

    def test_bad_parameters(self):
        self.get(status=400, q="light", lang="xx")
        self.get(status=400, q="light", type="sermon")
        self.get(status=400, q="light", sort="newest")
        self.get(status=400, q="light", type="note", offset="two")

    def test_cached_and_throttled(self):
        response = self.client.get("/api/search/", {"q": "light"})
        self.assertEqual(response["Cache-Control"], "public, max-age=300")
        self.assertIn(views.SearchThrottle, views.search.cls.throttle_classes)
        self.assertIn("search", settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"])


class SearchNotReadyTest(TestCase):
    def test_before_the_first_import(self):
        response = self.client.get("/api/search/", {"q": "light"})
        self.assertEqual(response.status_code, 503)
