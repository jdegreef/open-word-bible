"""The admin's search box (staff/search.py): what each group finds, and the
groups each role sees."""
from django.core.cache import cache

from accounts.models import Role
from feedback.models import ReaderMessage
from translation.models import Decision, Sentence

from .test_admin import AdminTestCase, account, client_for, sentence

K = Role.Kind


class AdminSearchTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        sentence("JHN.3.16.s1")
        Decision.objects.create(sentence=Sentence.objects.get(record_id="JHN.3.16.s1"), key="m-1", order=0,
                                layer="meaning", language="", category="word_choice", choice="only begotten",
                                reason="The unique son, not a generated one.")
        self.reader = account("ruth@example.org")
        self.reader.first_name = "Ruth"
        self.reader.save()
        ReaderMessage.objects.create(user=self.reader, kind="question", verse="JHN.3.16", language="en",
                                     text="Why say one and only?")

    def groups(self, q, client=None):
        data = (client or self.admin).get("/api/admin/search/", {"q": q}).json()
        return {g["kind"]: g["results"] for g in data["groups"]}

    def test_reference_finds_the_verse(self):
        for q in ("John 3:16", "jn 3 16", "JHN.3.16"):
            self.assertEqual(self.groups(q)["verse"][0]["href"], "#verse/JHN.3.16", q)
        self.assertNotIn("verse", self.groups("grace"))

    def test_record_id(self):
        self.assertEqual(self.groups("jhn.3.16.s1")["record"][0]["href"], "#verse/JHN.3.16")
        self.assertNotIn("record", self.groups("JHN.3.17.s1"))

    def test_terms_articles_and_decisions(self):
        terms = self.groups("grace")["term"]
        self.assertTrue(any("grace" in t["title"] for t in terms))
        self.assertEqual(terms[0]["href"], "#terms")
        decisions = self.groups("begotten")["decision"]
        self.assertEqual(decisions[0]["href"], "#verse/JHN.3.16")
        articles = self.groups("scroll")["article"]
        self.assertTrue(articles and all(a["href"] == "#articles" for a in articles))

    def test_accounts_and_messages_for_the_roles_that_open_them(self):
        found = self.groups("ruth")
        self.assertEqual(found["user"][0]["href"], f"#user/{self.reader.id}")
        self.assertEqual(found["message"][0]["href"], "#verse/JHN.3.16")
        self.assertIn("message", self.groups("one and only"))
        reporter = client_for(account("rep@example.org", (K.REPORTING,)))
        found = self.groups("ruth", reporter)
        self.assertNotIn("user", found)
        self.assertNotIn("message", found)
        self.assertIn("decision", self.groups("begotten", reporter))

    def test_short_queries_find_nothing(self):
        self.assertEqual(self.admin.get("/api/admin/search/", {"q": "a"}).json()["groups"], [])
