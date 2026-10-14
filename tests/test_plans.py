"""Reading plans: data/plans.json, the plans offered in each language, and
the pages and files the build makes for them (web/plans.js runs them)."""
import html
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from tests.site_build import built_site  # noqa: E402


class PlanDataTest(unittest.TestCase):
    def test_plans_are_well_formed(self):
        data = json.loads(build_site.PLAN_DATA.read_text(encoding="utf-8"))
        self.assertTrue(data["description"])
        ids = [p["id"] for p in data["plans"]]
        self.assertEqual(len(ids), len(set(ids)))
        for plan in build_site.load_plans():
            self.assertRegex(plan.id, r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertEqual(set(plan.name), set(build_site.LANGUAGES), plan.id)
            self.assertTrue(all(plan.name.values()), plan.id)
            self.assertTrue(plan.days, plan.id)
            for day in plan.days:
                self.assertTrue(day, plan.id)
                for book, chapter in day:
                    self.assertIn(book, build_site.BOOK_CHAPTERS, plan.id)
                    self.assertTrue(1 <= chapter <= build_site.BOOK_CHAPTERS[book], (plan.id, book, chapter))

    def test_whole_book_plans_read_every_chapter_once_in_order(self):
        for plan in build_site.load_plans():
            chapters = [bc for day in plan.days for bc in day]
            self.assertEqual(len(chapters), len(set(chapters)), plan.id)
        mark = next(p for p in build_site.load_plans() if p.id == "mark")
        self.assertEqual(mark.days, tuple(((("MRK", c),)) for c in range(1, 17)))
        self.assertEqual(mark.name["en"], "Mark in 16 days")

    def test_a_plan_is_readable_only_when_every_chapter_is_drafted(self):
        plan = build_site.Plan("t", {}, ((("MRK", 1),), (("MRK", 2), ("MRK", 3))))
        self.assertTrue(build_site.plan_readable(plan, {("MRK", 1), ("MRK", 2), ("MRK", 3), ("JHN", 1)}))
        self.assertFalse(build_site.plan_readable(plan, {("MRK", 1), ("MRK", 2)}))
        self.assertFalse(build_site.plan_readable(plan, set()))

    def test_plans_offered_in_each_language_are_drafted_in_it(self):
        for lang in build_site.LANGUAGES:
            drafted = build_site.drafted_chapters(lang)
            offered = build_site.available_plans(lang)
            for plan in offered:
                for day in plan.days:
                    for bc in day:
                        self.assertIn(bc, drafted, (lang, plan.id))
            for plan in build_site.load_plans():
                if plan in offered:
                    continue
                self.assertFalse(build_site.plan_readable(plan, drafted), (lang, plan.id))
        # English runs ahead: whatever another language offers, English does.
        en = {p.id for p in build_site.available_plans("en")}
        self.assertIn("mark", en)
        for lang in build_site.LANGUAGES:
            self.assertLessEqual({p.id for p in build_site.available_plans(lang)}, en, lang)

    def test_a_language_with_no_plans_says_so_and_links_to_english(self):
        page = build_site.plans_page("fr", plans=[])
        self.assertIn(build_site.t("fr", "plans.none"), page)
        self.assertIn(f'<a href="/plans/" hreflang="en">{build_site.t("fr", "plans.none_link")}</a>', page)
        self.assertNotIn('class="a-grid plan-list"', page)


class PlanSiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def read(self, path):
        rel = path.lstrip("/")
        return (self.out / (rel + "index.html" if rel.endswith("/") or not rel else rel)).read_text(encoding="utf-8")

    def test_plans_page_lists_the_plans_offered_in_its_language(self):
        sitemap = self.read("/sitemap.xml")
        for lang in build_site.LANGUAGES:
            page = self.read(build_site.url(lang, "/plans/"))
            offered = build_site.available_plans(lang)
            listed = re.findall(r'data-plan-card="([^"]+)"', page)
            self.assertEqual(listed, [p.id for p in offered], lang)
            for plan in offered:
                self.assertIn(f'href="{build_site.url(lang, build_site.plan_url(plan))}"', page)
                self.assertIn(html.escape(plan.name[lang]), page)
                self.assertIn(build_site.t(lang, "plans.length", n=len(plan.days)), page)
            self.assertEqual(f"<loc>{build_site.SITE_URL}{build_site.url(lang, '/plans/')}</loc>" in sitemap,
                             bool(offered), lang)
            self.assertIn("data-plan-today", page)
            self.assertIn(build_site.asset("plans.js"), page)

    def test_a_plan_page_lists_its_days_in_the_languages_that_offer_it(self):
        for plan in build_site.load_plans():
            for lang in build_site.LANGUAGES:
                path = self.out / build_site.url(lang, build_site.plan_url(plan)).lstrip("/") / "index.html"
                self.assertEqual(path.is_file(), plan in build_site.available_plans(lang), (lang, plan.id))
        mark = next(p for p in build_site.load_plans() if p.id == "mark")
        page = self.read("/plans/mark/")
        days = re.findall(r'<li class="plan-day" data-day="(\d+)">(.*?)</li>', page, re.S)
        self.assertEqual([int(n) for n, _ in days], list(range(1, 17)))
        self.assertIn('<a href="/mrk/7/">Mark 7</a>', days[6][1])
        # Real buttons, each day's with a name a screen reader can say.
        self.assertIn('<button type="button" class="button" data-plan-start', page)
        self.assertIn('aria-pressed="false" hidden aria-label="Day 7 done"', days[6][1])
        self.assertIn(f"<title>{mark.name['en']} · {build_site.SITE_NAME}</title>", page)
        # A plan page links only to the languages it is offered in.
        langs = [lang for lang in build_site.LANGUAGES if mark in build_site.available_plans(lang)]
        for lang in build_site.LANGUAGES:
            href = build_site.SITE_URL + build_site.url(lang, "/plans/mark/")
            self.assertEqual(f'hreflang="{lang}" href="{href}"' in page, lang in langs, lang)
        if "es" not in langs:
            self.assertIn('<a href="/es/plans/" lang="es"', page)

    def test_plans_files_hold_each_offered_plan(self):
        for lang in build_site.LANGUAGES:
            data = json.loads(self.read(f"/plans-{lang}.json"))
            self.assertEqual(data["ui"], build_site.catalog(lang)["plans.ui"])
            offered = build_site.available_plans(lang)
            self.assertEqual(list(data["plans"]), [p.id for p in offered])
            for plan in offered:
                entry = data["plans"][plan.id]
                self.assertEqual(entry["name"], plan.name[lang])
                self.assertEqual(entry["url"], build_site.url(lang, build_site.plan_url(plan)))
                self.assertEqual(len(entry["days"]), len(plan.days))
                for day in entry["days"]:
                    for c in day:
                        self.assertTrue((self.out / c["u"].lstrip("/") / "index.html").is_file(), c["u"])
                        self.assertTrue(c["u"].startswith(build_site.url(lang, "/")), c["u"])
        john = json.loads(self.read("/plans-en.json"))["plans"]["john"]
        self.assertEqual(john["days"][2], [{"b": "JHN", "c": 3, "n": "John 3", "u": "/jhn/3/"}])

    def test_home_and_chapter_pages_carry_the_current_plan(self):
        for lang in build_site.LANGUAGES:
            home = self.read(build_site.url(lang, "/"))
            hero = re.search(r'<section class="hero">(.*?)</section>', home, re.S)[1]
            self.assertIn("data-plan-today", hero)
            self.assertIn(f'data-plans="{build_site.plans_json_url(lang)}"', hero)
            self.assertIn(f'data-plans-en="{build_site.plans_json_url("en")}"', hero)
            self.assertIn(build_site.asset("plans.js"), home)
        chapter = self.read("/mrk/7/")
        bar = re.search(r'<div class="plan-bar"[^>]*>', chapter)[0]
        self.assertIn('data-book="MRK" data-chapter="7"', bar)
        self.assertIn(" hidden", bar)
        # At the end of the chapter, before the turns to the next one.
        self.assertLess(chapter.index('class="plan-bar"'), chapter.index('<nav class="turns"'))
        self.assertIn(build_site.asset("plans.js"), chapter)

    def test_plans_are_linked_from_the_header_footer_and_read_page(self):
        for lang in build_site.LANGUAGES:
            plans = build_site.url(lang, "/plans/")
            page = self.read(build_site.url(lang, "/about/"))
            header = re.search(r'<header class="site">(.*?)</header>', page, re.S)[1]
            footer = re.search(r'<footer class="site">(.*?)</footer>', page, re.S)[1]
            self.assertIn(f'href="{plans}"', header)
            self.assertIn(f'href="{plans}"', footer)
            self.assertIn(f'href="{plans}"', self.read(build_site.url(lang, "/read/")))

    def test_offline_worker_knows_the_plans_files(self):
        sw = self.read("/sw.js")
        current = json.loads(re.search(r"var CURRENT = (.*);", sw)[1])
        precache = json.loads(re.search(r"var PRECACHE = (.*);", sw)[1])
        self.assertIn(build_site.asset("plans.js"), precache)
        for lang in build_site.LANGUAGES:
            self.assertIn(build_site.plans_json_url(lang), current)

    def test_plans_script_keeps_progress_under_its_own_key(self):
        js = (ROOT / "web" / "plans.js").read_text(encoding="utf-8")
        self.assertIn('var KEY = "owb.plans";', js)
        # Every storage access is guarded.
        for m in re.finditer(r"localStorage\.\w+\(", js):
            line = js[js.rindex("\n", 0, m.start()):m.start()]
            self.assertIn("try", line, line)


if __name__ == "__main__":
    unittest.main()
