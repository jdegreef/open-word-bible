"""Search (GET /api/search/, translation/search.py): the tables import_content
builds from the site's own search documents, and the endpoint, in each site
language."""
import sys
import time
from datetime import timedelta
from types import SimpleNamespace
from unittest import mock

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from api import views
from backend_tests.test_backend import import_content, load_extract_words
from translation import search
from translation.models import SearchEntry, SearchLanguage

sys.path.insert(0, str(settings.REPO_ROOT / "scripts"))
import build_site  # noqa: E402


def verse_ids(doc):
    return {f"{doc['bk']}.{doc['c']}.{v}" for v in doc["vv"]}


class SearchTest(TestCase):
    def _should_check_constraints(self, connection):
        # Django re-checks every deferred foreign key at the end of each
        # test. Here that means every row setUpTestData imported (the whole
        # Bible in every language): 8 s a test locally and minutes on a CI
        # runner once the review-state indexes made the tables bigger. The
        # import is the same for every test and each test is rolled back.
        return False

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
        self.assertEqual(search.rebuild(until=time.time() - 1), {})
        self.assertEqual(search.rebuild(stop=time.time() - 1), {})
        self.assertEqual(SearchEntry.objects.count(), before)
        # The records loaded for one language don't outlive the rebuild.
        self.assertIsNone(build_site.SEARCH_LANG)

    def test_a_stopped_update_keeps_its_batches_and_the_next_finishes(self):
        # Render stops a pre-deploy at 30 minutes; a language whose update
        # would run past --deadline writes what it can in committed batches
        # and leaves the rest for the next run.
        docs = build_site.search_documents("sw")["docs"]
        self.addCleanup(search.site_build)   # one language's records must not outlive the test
        clock = [0.0]
        write = search._write

        def first_batch_only(*args):
            write(*args)
            clock[0] = 100.0   # the deadline has come

        with mock.patch.object(search, "CHUNK", 100), mock.patch.object(search, "_write", first_batch_only), \
                mock.patch.object(search, "time", SimpleNamespace(time=lambda: clock[0])):
            change = search._rebuild_language(search.site_build("sw"), "sw", full=True, stop=50.0)
        self.assertEqual((change.added, change.left), (100, len(docs) - 100))
        self.assertEqual(SearchEntry.objects.filter(language="sw").count(), 100)
        self.assertIsNone(SearchLanguage.objects.get(code="sw").checked)
        # Left behind, it goes first next time.
        self.assertEqual(search.order(build_site.LANGUAGES)[0], "sw")
        kept = set(SearchEntry.objects.filter(language="sw").values_list("id", flat=True))
        change = search._rebuild_language(search.site_build("sw"), "sw", full=False)
        self.assertEqual((change.added, change.removed, change.left), (len(docs) - 100, 0, 0))
        entries = SearchEntry.objects.filter(language="sw").order_by("position", "sub")
        self.assertEqual([e.doc for e in entries], docs)
        self.assertTrue(kept <= set(entries.values_list("id", flat=True)))
        self.assertIsNotNone(SearchLanguage.objects.get(code="sw").checked)

    def test_an_update_out_of_time_changes_nothing(self):
        self.addCleanup(search.site_build)
        first = SearchEntry.objects.filter(language="en", kind="v").order_by("position", "sub").first()
        first.doc = {**first.doc, "u": "/stale/"}
        first.save()
        change = search._rebuild_language(search.site_build("en"), "en", full=False, stop=time.time() - 1)
        self.assertEqual((change.added, change.removed, change.left), (0, 0, 1))
        self.assertTrue(SearchEntry.objects.filter(id=first.id).exists())

    def test_languages_waiting_longest_go_first(self):
        languages = list(build_site.LANGUAGES)
        SearchLanguage.objects.update(checked=timezone.now())
        SearchLanguage.objects.filter(code=languages[-1]).update(checked=None)
        SearchLanguage.objects.filter(code=languages[0]).update(checked=timezone.now() + timedelta(hours=1))
        self.assertEqual(search.order(languages), [languages[-1], *languages[1:-1], languages[0]])
        # Never brought up to date: the newest language first.
        SearchLanguage.objects.update(checked=None)
        self.assertEqual(search.order(languages), languages[::-1])

    def test_one_languages_records_give_the_same_documents(self):
        # The rebuild loads only a language's renderings (English's where a
        # sentence is not in it yet); search_documents must not notice.
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

    # ---- Japanese ---------------------------------------------------------

    def test_japanese_words_are_found_inside_a_clause(self):
        # Japanese has no spaces: in John 3:16 "ひとり子" and "永遠の命" sit in
        # the middle of a run of kana and kanji, and a single kanji is a word.
        for q in ("ひとり子", "永遠の命", "愛"):
            with self.subTest(q=q):
                found = set().union(*(verse_ids(d) for d in self.every(q, "verse", lang="ja")))
                self.assertIn("JHN.3.16", found)
        # The pairs must follow one another: these are all in the verse, but
        # not in this order.
        found = set().union(*(verse_ids(d) for d in self.every("命永遠", "verse", lang="ja")))
        self.assertNotIn("JHN.3.16", found)

    def test_japanese_voicing_marks_are_kept(self):
        # ガ is not カ: "ガリラヤ" (John 2:1) must not be searched as "カリラヤ".
        found = set().union(*(verse_ids(d) for d in self.every("ガリラヤ", "verse", lang="ja")))
        self.assertIn("JHN.2.1", found)
        self.assertEqual(self.get(q="カリラヤ", lang="ja")["totals"].get("verse", 0), 0)

    def test_indonesian_searches_its_own_text(self):
        # Indonesian now has every book: its site finds its own sentences,
        # and references by its book names and abbreviations. Its entries
        # use the Indonesian stemmer.
        ref = self.get(q="Yohanes 3:16", lang="id")["reference"]
        self.assertEqual((ref["label"], ref["url"]), ("Yohanes 3:16", "/id/jhn/3/#v16"))
        self.assertEqual(self.get(q="Yoh 3:16", lang="id")["reference"]["url"], "/id/jhn/3/#v16")
        self.assertGreater(self.get(q="terang", lang="id")["totals"].get("verse", 0), 0)
        self.assertEqual(search.config("id"), "owb_indonesian")
        with connection.cursor() as cur:
            cur.execute("SELECT to_tsvector('owb_indonesian', 'dikasihi') @@ to_tsquery('owb_indonesian', 'kasih')")
            self.assertTrue(cur.fetchone()[0])

    def test_arabic_is_stemmed_after_it_is_folded(self):
        # owb_arabic (translation 0016) takes off the attached preposition
        # and the article and the ending, on text folded as search.fold
        # folds it, so "كلمة" finds "بِالْكَلِمَةِ" (by the word).
        self.assertEqual(search.config("ar"), "owb_arabic")
        word = search.fold("\u0628\u0650\u0627\u0644\u0652\u0643\u064e\u0644\u0650\u0645\u064e\u0629\u0650")
        query = search.fold("\u0643\u0644\u0645\u0629")
        with connection.cursor() as cur:
            cur.execute("SELECT to_tsvector('owb_arabic', %s) @@ plainto_tsquery('owb_arabic', %s)", [word, query])
            self.assertTrue(cur.fetchone()[0])

    def test_japanese_references_with_full_width_digits(self):
        ref = self.get(q="ヨハネによる福音書３：１６", lang="ja")["reference"]
        self.assertEqual((ref["label"], ref["url"]), ("ヨハネによる福音書 3:16", "/ja/jhn/3/#v16"))
        ref = self.get(q="ガラテヤの信徒への手紙 1:1", lang="ja")["reference"]
        self.assertEqual(ref["label"], "ガラテヤの信徒への手紙 1:1")

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


class JapaneseTextTest(SimpleTestCase):
    def test_runs_of_kanji_and_kana_become_pairs(self):
        self.assertEqual(search.ngrams("神の愛を。").split(), ["神の", "の愛", "愛を", "を", "。"])
        # One character stands alone; other text is left as it is; the
        # middle dot between the parts of a name ends a run.
        self.assertEqual(search.ngrams("人").split(), ["人"])
        self.assertEqual(search.ngrams("2人 abc").split(), ["2", "人", "abc"])
        self.assertEqual(search.ngrams("シモン・ペトロ").split(), ["シモ", "モン", "ン", "・", "ペト", "トロ", "ロ"])

    def test_terms_split_at_runs(self):
        self.assertEqual(search.cjk_terms("ペトロ2"), ["ペトロ", "2"])
        self.assertEqual(search.bigrams("永遠の命"), ["永遠", "遠の", "の命"])

    def test_fold_keeps_voicing_marks_and_narrows_wide_letters(self):
        self.assertEqual(search.fold("ガリラヤ"), "ガリラヤ")
        self.assertEqual(search.fold("ポ"), "ポ")
        self.assertEqual(search.fold("３：１６ Ａｂ\u3000x"), "3:16 ab x")
        self.assertEqual(search.fold("Señor"), "senor")
        # The site's book aliases are folded the same way.
        self.assertEqual(build_site.fold("ガラテヤ３"), search.fold("ガラテヤ３"))

    def test_fold_makes_arabic_letters_typed_either_way_one(self):
        # الْكَلِمَةُ with its vowels, أ for ا, Persian ی and ک, tatweel,
        # Arabic-Indic and Persian digits.
        for text in ("\u0627\u0644\u0652\u0643\u064e\u0644\u0650\u0645\u064e\u0629\u064f",
                     "\u0623\u0628\u0631\u0627\u0647\u064a\u0645 \u0645\u0648\u0633\u0649",
                     "\u06a9\u062a\u0627\u0628 \u0639\u06cc\u0633\u06cc \u0627\u0644\u0644\u0640\u0647",
                     "\u0663:\u0661\u0666 \u06f3:\u06f1\u06f6"):
            self.assertEqual(search.fold(text), build_site.fold(text), text)
        self.assertEqual(search.fold("\u0623\u0628\u0631\u0627\u0647\u064a\u0645"),
                         "\u0627\u0628\u0631\u0627\u0647\u064a\u0645")
        self.assertEqual(search.fold("\u06a9\u06cc"), "\u0643\u064a")
        self.assertEqual(search.fold("\u0663:\u0661\u0666"), "3:16")

    def test_arabic_script_is_indexed_folded(self):
        # Postgres's unaccent leaves Arabic marks and letters as they are, so
        # the fields are folded before they are indexed, as a query is.
        fields = ("\u0631\u0627\u0639\u0648\u062b", "", "\u0625\u0650\u0644\u0652\u0647\u064f \u06a9")
        self.assertEqual(search.indexed("owb_simple", fields),
                         ("\u0631\u0627\u0639\u0648\u062b", None, "\u0627\u0644\u0647 \u0643"))
        self.assertEqual(search.indexed("owb_english", ("Ruth", "", "word")), (None, None, None))


class ChineseTextTest(SimpleTestCase):
    def test_chinese_is_searched_by_bigrams(self):
        self.assertEqual(search.config("zh"), search.CJK)
        self.assertEqual(search.ngrams("神爱世人。").split(), ["神爱", "爱世", "世人", "人", "。"])
        self.assertEqual(search.cjk_terms("约翰福音3"), ["约翰福音", "3"])

    def test_each_setting_option_is_indexed_beside_its_neighbours(self):
        # The word for God and the divine name are setting spans: 神的国 and
        # 上帝的国 must both be bigrams of the sentence, not 神 and 上帝 side
        # by side before 的国.
        doc = {"k": "v", "x": {"B": "{{god_term:神|上帝}}的国降临，{{divine_name:上主|雅威}}说"}}
        _, _, body = search.indexed(search.CJK, search.fields(doc), doc)
        for pair in ("神的", "上帝", "帝的", "主说", "威说"):
            self.assertIn(pair, body.split())
        self.assertEqual(search.readings(doc["x"]).split(search.GAP),
                         ["神的国降临，上主说", "上帝的国降临，上主说", "神的国降临，雅威说", "上帝的国降临，雅威说"])
        # The entry's own text is unchanged; other configurations index the fields as they are.
        self.assertIn("神 上帝的国", search.fields(doc)[2])
        self.assertEqual(search.indexed("owb_english", search.fields(doc), doc), (None, None, None))


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
