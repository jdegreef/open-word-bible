"""The admin's wording consistency page (staff/consistency.py): how each
language words the key terms across the sentences that use them."""
from unittest import mock

from accounts.models import Role
from texts.models import Edition, Word
from translation.models import Decision, Rendering, Sentence

from .test_admin import AdminTestCase, account, client_for, sentence

K = Role.Kind


class ConsistencyTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.made = []
        for n, (en, fr) in enumerate([("grace and truth", "la grâce"), ("graces to you", "la grâce"),
                                      ("{{gender:kindness|favour}} to you", "la faveur")], start=1):
            s = sentence(f"JHN.1.{n}.s1", ("en", "fr"))
            wid = f"n430010{n:02d}001"
            Word.objects.create(id=wid, edition=Edition.objects.get(code="sblgnt"), book="JHN", chapter=1,
                                verse=n, position=1, seq=n, text="charis", strong="5485", lang="grc")
            Sentence.objects.filter(id=s.id).update(tokens=[wid])
            Rendering.objects.filter(sentence=s, language="en").update(text=en)
            Rendering.objects.filter(sentence=s, language="fr").update(text=fr)
            self.made.append((s, wid))
        # French has no word list: its forms come from the decisions.
        for s, wid in self.made:
            Decision.objects.create(sentence=s, key="r-fr-1", order=0, layer="rendering", language="fr",
                                    levels=["L", "B", "R"], category="word_choice", tokens=[wid],
                                    choice="grâce (L, B); faveur (R)", reason="x")
        # English: "kindness" is no key-term word, but a decision names it.
        s, wid = self.made[2]
        Decision.objects.create(sentence=s, key="r-en-1", order=0, layer="rendering", language="en",
                                levels=["B"], category="word_choice", tokens=[wid], choice="kindness", reason="x")

    def grace(self, query):
        d = self.admin.get("/api/admin/consistency/" + query).json()
        return next(t for t in d["terms"] if t["slug"] == "grace")

    def test_a_term_worded_two_ways_is_split(self):
        grace = self.grace("?lang=en&level=B&min=1")
        self.assertEqual((grace["uses"], grace["rendered"]), (3, 3))
        forms = {f["form"]: f["sentences"] for f in grace["forms"]}
        # "graces" counts as grace; the setting's default ("kindness") is the one counted.
        self.assertEqual(forms, {"grace": 2, "kindness": 1})
        self.assertTrue(grace["split"])
        self.assertEqual(grace["spread"], round(1 - 2 / 3, 3))
        self.assertEqual(grace["forms"][0]["examples"][0], {"record": "JHN.1.1.s1", "verse": "JHN.1.1",
                                                           "label": "John 1:1"})
        self.assertEqual(grace["forms"][0]["books"], ["JHN"])
        # The first split term comes first.
        self.assertEqual(self.admin.get("/api/admin/consistency/?lang=en&min=1").json()["terms"][0]["slug"], "grace")

    def test_min_and_levels(self):
        # One sentence of "kindness" is under min=2: not a split.
        self.assertFalse(self.grace("?lang=en&level=B")["split"])
        # French: the decision's level notes say which form each level uses.
        fr = self.grace("?lang=fr&level=B&min=1")
        self.assertEqual(({f["form"]: f["sentences"] for f in fr["forms"]}, fr["other"]["sentences"]),
                         ({"grâce": 2}, 1))
        fr = self.grace("?lang=fr&level=R&min=1")
        self.assertEqual(({f["form"]: f["sentences"] for f in fr["forms"]}, fr["other"]["sentences"]),
                         ({"faveur": 1}, 2))
        unknown = self.grace("?lang=es&level=B&min=1")
        self.assertEqual((unknown["rendered"], unknown["forms"], unknown["other"]["sentences"]), (0, [], 0))

    def test_unmatched_sentences_are_other(self):
        Rendering.objects.filter(sentence=self.made[0][0], language="en").update(text="something else")
        grace = self.grace("?lang=en&level=B&min=1&term=grace")
        self.assertEqual(grace["other"]["sentences"], 1)
        self.assertEqual(grace["other"]["examples"][0]["verse"], "JHN.1.1")

    def test_cached_until_sentences_change(self):
        self.grace("?lang=en&level=B")
        with mock.patch("staff.consistency.measure", side_effect=AssertionError("measured again")):
            self.grace("?lang=en&level=B")
        Sentence.objects.get(id=self.made[0][0].id).save()
        with mock.patch("staff.consistency.measure", return_value={"terms": []}) as measure:
            self.admin.get("/api/admin/consistency/?lang=en&level=B")
        measure.assert_called_once()

    def test_checks_its_input_and_area(self):
        self.assertEqual(self.admin.get("/api/admin/consistency/?lang=xx").status_code, 400)
        self.assertEqual(self.admin.get("/api/admin/consistency/?level=Q").status_code, 400)
        self.assertEqual(self.admin.get("/api/admin/consistency/?term=nothing").status_code, 400)
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        self.assertEqual(reporter.get("/api/admin/consistency/").status_code, 200)
        reader = client_for(account("reader@example.org"))
        self.assertEqual(reader.get("/api/admin/consistency/").status_code, 403)
