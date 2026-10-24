"""Search (GET /api/search/, translation/search.py): the tables import_content
builds from the site's own search documents, and the endpoint, in each site
language."""
import sys
import time

from django.conf import settings
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase

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
            entries = SearchEntry.objects.filter(language=lang).order_by("position", "sub")
            self.assertEqual(entries.count(), len(docs), lang)
            self.assertEqual(entries.first().doc, docs[0])
            self.assertFalse(entries.filter(vector__isnull=True).exists())

    def test_rebuild_replaces_rather_than_adds(self):
        # One language: a full rebuild of all of them takes minutes.
        before = SearchEntry.objects.count()
        change = search._rebuild_language(search.site_build("sw"), "sw", full=True)
        self.assertEqual(SearchEntry.objects.count(), before)
        self.assertEqual(change.added, change.removed)
        self.assertEqual(change.added, SearchEntry.objects.filter(language="sw").count())

    def test_rebuild_rewrites_only_what_changed(self):
        ids = set(SearchEntry.objects.values_list("id", flat=True))
        changes = search.rebuild()
        self.assertEqual(set(SearchEntry.objects.values_list("id", flat=True)), ids)
        self.assertFalse([c for c in changes.values() if c.added or c.removed])
        # An entry whose document changed, and one the site no longer has,
        # are replaced; the new documents' entries go in their place in order.
        first, second = SearchEntry.objects.filter(language="en", kind="v").order_by("position", "sub")[:2]
        first.doc = {**first.doc, "u": "/stale/"}
        first.save()
        change = search._rebuild_language(search.site_build("en"), "en", full=False)
        self.assertEqual((change.added, change.removed), (1, 1))
        self.assertFalse(SearchEntry.objects.filter(id=first.id).exists())
        self.assertTrue(SearchEntry.objects.filter(id=second.id).exists())
        docs = build_site.search_documents("en")["docs"]
        entries = SearchEntry.objects.filter(language="en").order_by("position", "sub")
        self.assertEqual([e.doc for e in entries], docs)
        self.assertFalse(entries.filter(vector__isnull=True).exists())

    def test_search_budget_leaves_languages_for_the_next_run(self):
        # Past the deadline no language is started, and the ones done stay.
        before = SearchEntry.objects.count()
        self.assertEqual(search.rebuild(until=time.monotonic() - 1), {})
        self.assertEqual(SearchEntry.objects.count(), before)
        # The records loaded for one language don't outlive the rebuild.
        self.assertIsNone(build_site.SEARCH_LANG)

    def test_one_languages_records_give_the_same_documents(self):
        # The rebuild loads only a language's renderings and English's;
        # search_documents must not notice.
        site = search.site_build("pt")
        try:
            one = site.search_documents("pt")
        finally:
            search.site_build()
        self.assertEqual(one, build_site.search_documents("pt"))

    def test_jsonb_text_matches_postgres(self):
        # plan() matches stored entries by this key, worked out here for new
        # documents and by Postgres for stored ones.
        for e in SearchEntry.objects.filter(language="en").order_by("?")[:200]:
            self.assertEqual(search.key(e.config, e.doc),
                             SearchEntry.objects.filter(id=e.id).extra(select={"k": search.KEY_SQL})
                             .values_list("k", flat=True).get())

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

    def test_stems_match_only_in_their_own_language(self):
        # Spanish "verbo" stems to "verb": English notes about verbs must not match.
        results = self.every("verbo", "note", lang="es") + self.every("verbo", "verse", lang="es")
        self.assertTrue(results)
        for doc in results:
            self.assertRegex(search.fold(" ".join(search.fields(doc))), r"(^|[\W_])verbo", doc)

    def test_english_notes_are_found_on_other_language_sites(self):
        # Meaning notes are written in English: "the victor's wreath" (Philippians 4:1).
        notes = self.every("wreath", "note", lang="es")
        self.assertIn("the victor’s wreath", [n["t"] for n in notes])

    def test_note_results_carry_a_marked_passage(self):
        notes = self.get(q="grace", lang="en", type="note")["results"]
        self.assertTrue(any("⟦" in n.get("hl", "") for n in notes))

    def test_articles_come_without_their_whole_text(self):
        articles = self.get(q="grace", lang="en", type="article")["results"]
        self.assertTrue(articles)
        self.assertFalse([a for a in articles if "x" in a])
        self.assertTrue(any("⟦" in a.get("hl", "") for a in articles))
        best = [d for d in self.get(q="grace", lang="en")["results"] if d["k"] == "a"]
        self.assertTrue(best)
        self.assertFalse([a for a in best if "x" in a])

    def test_bible_order_and_paging(self):
        def plain(docs):
            return [{k: v for k, v in d.items() if k != "hl"} for d in docs]
        by_relevance = plain(self.every("grace", "note"))
        in_order = plain(self.every("grace", "note", sort="order"))
        self.assertEqual(len(in_order), self.get(q="grace", lang="en")["totals"]["note"])
        self.assertCountEqual([str(d) for d in in_order], [str(d) for d in by_relevance])
        positions = {str(e.doc): (e.position, e.sub) for e in SearchEntry.objects.filter(language="en", kind="n")}
        order = [positions[str(d)] for d in in_order]
        self.assertEqual(order, sorted(order))
        # A page carries every kind's count too, as the site's filters show them.
        self.assertEqual(self.get(q="grace", lang="en", type="note", limit=2)["totals"],
                         self.get(q="grace", lang="en")["totals"])
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
        # A chapter the site has no page for (Malachi has three), so this
        # holds however much of the Bible has been drafted.
        ref = self.get(q="mal 9:1", lang="en")["reference"]
        self.assertEqual(ref["label"], "Malachi 9:1")
        self.assertNotIn("url", ref)
        ref = self.get(q="John 4:60", lang="en")["reference"]
        self.assertEqual((ref["url"], ref["shown"], ref["sentences"]), ("/jhn/4/", [], []))
        # Words and a number, not the start of any book's name. ("son 3" was
        # the example until Song of Songs was drafted.)
        self.assertIsNone(self.get(q="love 3", lang="en")["reference"])

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


class PlanTest(SimpleTestCase):
    """search.plan: which stored entries a rebuild keeps, and where new ones go."""

    def test_unchanged_keeps_everything(self):
        old = [(1, 0, 0, "a"), (2, 1, 0, "b")]
        self.assertEqual(search.plan(old, ["a", "b"]), ([], []))

    def test_insert_goes_after_the_entry_before_it(self):
        old = [(1, 0, 0, "a"), (2, 1, 0, "b"), (3, 2, 0, "c")]
        self.assertEqual(search.plan(old, ["a", "x", "y", "b", "c", "z"]),
                         ([], [(1, 0, 1), (2, 0, 2), (5, 2, 1)]))

    def test_changed_and_removed_are_deleted(self):
        old = [(1, 0, 0, "a"), (2, 1, 0, "b"), (3, 2, 0, "c")]
        self.assertEqual(search.plan(old, ["a", "B", "d"]), ([2, 3], [(1, 0, 1), (2, 0, 2)]))

    def test_repeated_keys_match_in_order(self):
        old = [(1, 0, 0, "a"), (2, 1, 0, "a")]
        self.assertEqual(search.plan(old, ["a", "a", "a"]), ([], [(2, 1, 1)]))

    def test_no_room_before_the_first_or_between_subs(self):
        self.assertIsNone(search.plan([(1, 0, 0, "a")], ["x", "a"]))
        self.assertEqual(search.plan([(1, 3, 0, "a")], ["x", "a"]), ([], [(0, 2, 0)]))
        old = [(1, 0, 1, "a"), (2, 0, 2, "b")]
        self.assertIsNone(search.plan(old, ["a", "x", "b"]))

    def test_empty(self):
        self.assertEqual(search.plan([], ["a", "b"]), ([], [(0, 0, 0), (1, 0, 1)]))
        self.assertEqual(search.plan([(1, 0, 0, "a")], []), ([1], []))
