import hashlib
import html
import json
import re
import sys
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from owb import crossrefs  # noqa: E402
from tests.site_build import built_site  # noqa: E402


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def chapter_data(self, path="jhn/1"):
        page = (self.out / path / "index.html").read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="owb-data">(.*?)</script>', page, re.S)
        return json.loads(m[1])

    def test_pages_exist(self):
        for rel in ("index.html", "read/index.html", "jhn/1/index.html", "php/4/index.html",
                    "about/index.html", "404.html", "style.css", "reader.js",
                    "sitemap.xml", "robots.txt", "favicon.svg"):
            self.assertTrue((self.out / rel).is_file(), rel)

    def test_poetry_keeps_its_lines_for_the_reader_only(self):
        # The reader gets the line markers to set Psalm 23 as poetry; every
        # text the build writes on one line reads them as spaces.
        data = self.chapter_data("psa/23")
        self.assertTrue(any("\\q " in r["renderings"]["en"]["B"] for r in data["records"]))
        self.assertEqual(build_site.plain("my shepherd; \\q I will never be in need."),
                         "my shepherd; I will never be in need.")
        records = build_site.load_chapter("PSA", 23)[0]
        self.assertNotIn("\\q", build_site.opening_verse(records, 23))
        page = (self.out / "psa" / "23" / "index.html").read_text(encoding="utf-8")
        head = page.split("<body", 1)[0]
        self.assertNotIn("\\q", head)

    def test_account_pages_are_built_but_not_indexed(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        for name, marker in (("account", 'id="name-form"'), ("login", 'id="login-form"'),
                             ("reset-password", 'id="reset-form"')):
            page = (self.out / name / "index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex">', page)
            self.assertIn(marker, page)
            self.assertNotIn(f"/{name}/", sitemap)
        self.assertTrue((self.out / "account.js").is_file())
        login = (self.out / "login" / "index.html").read_text(encoding="utf-8")
        # Sign in, create an account, reset: one page, sign in showing first.
        self.assertIn('<span data-for="sign-in">Welcome back</span>', login)
        self.assertIn('<span data-for="sign-up" hidden>Create your account</span>', login)
        self.assertIn('id="google"', login)
        # Every page knows the API and has the header's account menu.
        for path in self.out.rglob("index.html"):
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'<meta name="owb-api" content="{build_site.API_URL}">', text, path)
            lang = re.search(r'<html lang="([a-z]+)">', text)[1]
            self.assertIn(f'<a class="sign-in-btn" href="{build_site.url(lang, "/login/")}" data-login>', text, path)
            self.assertIn(f'<a class="pop-item" href="{build_site.url(lang, "/account/")}">', text, path)

    def test_account_page_lists_the_readers_messages(self):
        page = (self.out / "es" / "account" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<section class="set-block" id="my-messages" hidden', page)
        self.assertIn(build_site.t("es", "account.messages"), page)
        # Book names in the page's language, for the verse links.
        self.assertIn("&quot;JHN&quot;: &quot;Juan&quot;", page)

    def test_admin_page_is_built_in_english_only_and_not_indexed(self):
        page = (self.out / "admin" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex">', page)
        self.assertIn('id="admin"', page)
        self.assertIn(build_site.asset("admin.js"), page)
        self.assertIn(build_site.asset("admin.css"), page)
        self.assertTrue((self.out / "admin.js").is_file())
        self.assertFalse((self.out / "es" / "admin").exists())
        self.assertNotIn("/admin/", (self.out / "sitemap.xml").read_text(encoding="utf-8"))
        # The account menu's Admin link opens it, for anyone on the team.
        self.assertIn('<a class="pop-item admin-link" href="/admin/" hidden>',
                      (self.out / "es" / "index.html").read_text(encoding="utf-8"))

    def test_chapter_has_every_verse_in_order(self):
        data = self.chapter_data()
        verses = list(dict.fromkeys(v for r in data["records"] for v in r["refs"]))
        self.assertEqual(verses, [f"JHN.1.{v}" for v in range(1, 52)])
        # English for every sentence; Spanish for 1:1-18 so far, French,
        # Swahili, Vietnamese and Korean for the whole chapter.
        self.assertEqual(data["languages"], ["en", "es", "fr", "sw", "vi", "ko"])
        for lang in ("fr", "sw", "vi", "ko"):
            self.assertTrue(all(lang in r["renderings"] for r in data["records"]), lang)
        self.assertTrue(all("en" in r["renderings"] for r in data["records"]))

    def test_each_verse_words_are_covered_once(self):
        # A verse may hold several sentences (1:21 has five) and a sentence
        # may cross verses; together the records cover every word once.
        data = self.chapter_data()
        seen = {}
        for r in data["records"]:
            for tid in r["source"]["tokens"]:
                self.assertNotIn(tid, seen, f"{tid} in {seen.get(tid)} and {r['id']}")
                seen[tid] = r["id"]
        for vid in dict.fromkeys(v for r in data["records"] for v in r["refs"]):
            words = {t["id"] for t in data["words"][vid]}
            self.assertEqual({t for t in seen if t in words}, words, vid)

    def chapter_text(self, path):
        page = (self.out / path / "index.html").read_text(encoding="utf-8")
        return page, re.search(r'<div class="text" id="text">(.*?)</div>\s*<section class="notes"', page, re.S)[1]

    def test_chapter_text_is_in_the_page(self):
        # Without JavaScript the page still has the Balanced text at the
        # default settings, a span per verse as the reader draws it.
        for path in ("1ti/5", "jhn/1", "gen/1"):
            page, text = self.chapter_text(path)
            data = self.chapter_data(path)
            verses = [str(build_site.refs.parse(v).verse) for v in
                      dict.fromkeys(v for r in data["records"] for v in r["refs"])]
            self.assertEqual(list(dict.fromkeys(re.findall(r'data-v="([^"]+)"', text))), verses, path)
            self.assertEqual(re.findall(r"<sup>([^<]+)</sup>", text), verses, path)
            self.assertNotIn("{{", text)
            self.assertNotIn("\\v ", text)
            for r in data["records"]:
                default = build_site.markup.render(r["renderings"]["en"]["B"])
                first = build_site.markup.VERSE.split(default)[0].strip()
                self.assertIn(html.escape(first, quote=False), text, r["id"])
                self.assertIn(f'data-record="{r["id"]}"', text)
            for heading in data["headings"].values():
                shown = html.escape(build_site.markup.render(heading["en"]), quote=False)
                self.assertIn(f'<h2 class="section-head">{shown}</h2>', text)
            self.assertIn("<noscript>", page)
            self.assertIn(build_site.t("en", "reader.noscript", level="Balanced"), page)
        self.assertIn('<sup class="fn" aria-hidden="true"><span class="fn-mark">a</span></sup>',
                      self.chapter_text("1ti/5")[1])

    def test_chapter_text_falls_back_to_english(self):
        # A sentence not yet in the page's language is shown in English, in
        # grey, under the notice that says so.
        for lang in build_site.LANGUAGES:
            for p in build_site.passages():
                missing = [r for r in p.records if lang not in r["renderings"]]
                if not missing:
                    continue
                page, text = self.chapter_text(build_site.url(lang, p.url).strip("/"))
                self.assertIn('class="verse fallback" lang="en" data-v=', text)
                self.assertIn(f'data-record="{missing[0]["id"]}"', text)
                self.assertNotIn('id="partial" hidden', page)
                return
        self.skipTest("every chapter is in every language")

    def test_disputed_passage_is_set_apart_in_the_text(self):
        _, text = self.chapter_text("jhn/8")
        block = re.search(r'<div class="disputed-block"><div class="disputed-note">.*?</div>(.*?)</div>', text, re.S)
        self.assertIsNotNone(block)
        self.assertIn('data-v="7:53"', block[1])
        self.assertIn('data-v="11"', block[1])
        self.assertNotIn('data-v="12"', block[1])

    def test_chapter_pages_carry_linked_data(self):
        for path, source in (("1ti/5", "SBLGNT"), ("gen/1", "Open Scriptures Hebrew Bible"),
                             ("es/jhn/1", "SBLGNT")):
            page = (self.out / path / "index.html").read_text(encoding="utf-8")
            raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)[1]
            data = json.loads(raw)
            self.assertEqual(data["@type"], "Chapter")
            self.assertEqual(data["url"], build_site.SITE_URL + "/" + path + "/")
            self.assertEqual(data["inLanguage"], "es" if path.startswith("es/") else "en")
            self.assertEqual(data["isPartOf"]["name"], "Open Word Bible")
            self.assertEqual(data["license"], "https://creativecommons.org/publicdomain/zero/1.0/")
            # Nothing is reviewed yet.
            self.assertEqual(data["creativeWorkStatus"], "Draft")
            self.assertIn(source, data["isBasedOn"]["name"])
            self.assertEqual(data["translationOfWork"], data["isBasedOn"])
        # Nothing in it can close its script element.
        records = build_site.load_chapter("1TI", 5)[0]
        title = "</script><script>alert(1)</script>"
        script = build_site.chapter_ld(records, "1TI", 5, title)
        self.assertEqual(script.count("</"), 1)
        self.assertEqual(json.loads(script[script.index(">") + 1:-len("</script>")])["name"], title)

    def test_footer_counts_the_books_not_started(self):
        page = (self.out / "1ti" / "5" / "index.html").read_text(encoding="utf-8")
        index = re.search(r'<nav class="foot-books".*?</nav>', page, re.S)[0]
        ot = build_site.refs.OT_CODES
        have = {b for b, _ in build_site.books("en")}
        missing = [code for code in ot if code not in have]
        for code in ot:
            self.assertEqual(f'>{build_site.BOOK_NAMES[code]["en"]}<' in index,
                             code in have or len(missing) == 1, code)
        if len(missing) > 1:
            self.assertIn(f'href="/read/">{build_site.t("en", "footer.not_started", n=len(missing))}</a>', index)

    def notes_section(self, path):
        page = (self.out / path / "index.html").read_text(encoding="utf-8")
        return re.search(r'<section class="notes" id="notes"[^>]*>(.*?)</section>', page, re.S)[1]

    def test_footnotes_are_in_the_page(self):
        # Without JavaScript (and for crawlers) the footnotes the text's
        # letters point to are listed under it, as the reader first lists them.
        for path, book, chapter, lang in (("jhn/3", "JHN", 3, "en"), ("jhn/8", "JHN", 8, "en"),
                                          ("fr/jhn/3", "JHN", 3, "fr")):
            text = self.chapter_text(path)[1]
            notes = self.notes_section(path)
            marks = re.findall(r'<span class="fn-mark">([a-z]+)</span>', text)
            self.assertTrue(marks, path)
            self.assertEqual(re.findall(r'<span class="note-mark">([a-z]+)</span>', notes), marks, path)
            records = build_site.load_chapter(book, chapter)[0]
            r, d = next((r, d) for r in records for d in build_site.footnote_decisions(r, lang))
            self.assertIn(f'<span class="note-text">{build_site.note_html(d, lang)}</span>', notes)
            self.assertIn(html.escape(build_site.markup.render(d["choice"]), quote=False), notes)
            self.assertNotIn("{{", notes)
        # A note spans chapters as the reader's verse ranges do.
        self.assertIn('<span class="note-ref">7:53–8:1</span>', self.notes_section("jhn/8"))
        # Meaning notes are written in English; another language's page says so.
        self.assertIn('<span class="note-text"><span lang="en">', self.notes_section("fr/jhn/3"))
        self.assertNotIn('lang="en"', self.notes_section("jhn/3"))

    def test_footnote_text_follows_the_reader(self):
        # build_site.note_html() writes what reader.js's noteText() writes.
        d = {"layer": "meaning", "category": "lexical", "choice": "from above",
             "alternatives": ["again", "anew"], "uncertain": True}
        self.assertEqual(build_site.note_html(d, "en"), "from above. Or: again; anew (Uncertain).")
        self.assertEqual(build_site.note_html({**d, "uncertain": False}, "en"),
                         "from above. Also considered: again; anew.")
        self.assertEqual(build_site.note_html({**d, "category": "text_variant", "uncertain": False}, "en"),
                         "from above. Other manuscripts: again; anew.")
        self.assertEqual(build_site.note_html({**d, "alternatives": []}, "fr"),
                         '<span lang="en">from above</span> (Incertain).')
        reader = (self.out / "reader.js").read_text(encoding="utf-8")
        self.assertIn('text += ". " + t(label) + alts.join("; ");', reader)
        self.assertIn('if (d.uncertain) text += " (" + t("uncertain") + ")";', reader)

    def test_status_page_counts_the_records(self):
        counts = build_site.status_counts()
        records = build_site._all_records()
        self.assertEqual(counts["all"], len(records))
        self.assertEqual(sum(counts["statuses"].values()), len(records))
        self.assertEqual(sum(b["all"] for b in counts["books"].values()), len(records))
        approved = sum(r["status"] in build_site.APPROVED for r in records)
        self.assertEqual(counts["approved"], approved)
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        for lang in build_site.LANGUAGES:
            path = build_site.url(lang, "/about/status/")
            page = (self.out / path.strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn(f"<b>{build_site.number(len(records), lang)}</b>", page)
            self.assertIn(f"<b>{build_site.number(approved, lang)}</b>", page)
            self.assertIn(f"<loc>{build_site.SITE_URL}{path}</loc>", sitemap)
            self.assertIn(f'href="{path}"', (self.out / build_site.url(lang, "/").strip("/") / "index.html")
                          .read_text(encoding="utf-8"))
            # The article on review, in the page's language where it has one.
            has = any(a["slug"] == build_site.REVIEW_ARTICLE for a in build_site.load_articles(lang))
            review = build_site.url(lang if has else "en", "/articles/" + build_site.REVIEW_ARTICLE + "/")
            self.assertIn(f'href="{review}"', page)

    def test_downloads_are_built_for_every_language_and_level(self):
        records = build_site._all_records()
        languages = build_site.status_counts()["languages"]
        built = build_site.downloads()
        self.assertEqual(set(built), {(lang, level, fmt) for lang in languages for level in "LBR"
                                      for fmt in build_site.DOWNLOAD_FORMATS})
        # Each zip holds its text, the manifest, a README and the licence.
        name, data, manifest = built["en", "B", "usfm"]
        self.assertEqual(name, "owb-en-b-usfm.zip")
        self.assertEqual((self.out / "downloads" / name).read_bytes(), data)
        z = zipfile.ZipFile(self.out / "downloads" / name)
        self.assertIn("43-JHN.usfm", z.namelist())
        self.assertIn("CC0", z.read("LICENSE").decode())
        self.assertIn("AI-assisted", z.read("README.txt").decode())
        self.assertEqual(json.loads(z.read("manifest.json")), manifest)
        name, _, manifest = built["fr", "R", "json"]
        self.assertEqual(name, "owb-fr-r-json.zip")
        z = zipfile.ZipFile(self.out / "downloads" / name)
        self.assertEqual(sorted(z.namelist()), ["LICENSE", "README.txt", "manifest.json", "owb-fr-r.json"])
        self.assertEqual(json.loads(z.read("owb-fr-r.json"))["manifest"], manifest)
        # The manifest counts statuses and lists what isn't translated yet.
        self.assertEqual(manifest["licence"], "CC0 1.0 Universal (public domain dedication)")
        self.assertEqual(sum(manifest["status"].values()),
                         sum(1 for r in records if "R" in r["renderings"].get("fr", {})))
        self.assertEqual(manifest["missing"]["count"], len(manifest["missing"]["verses"]))
        self.assertGreater(manifest["missing"]["count"], 0)
        self.assertEqual(built["en", "L", "json"][2]["missing"]["count"], 0)
        # The page lists every file, in every site language, and the footer links it.
        for lang in build_site.LANGUAGES:
            path = build_site.url(lang, "/download/")
            page = (self.out / path.strip("/") / "index.html").read_text(encoding="utf-8")
            for name, _, _ in built.values():
                self.assertIn(f'href="/downloads/{name}" download', page)
            self.assertIn(f'href="{path}"', (self.out / build_site.url(lang, "/").strip("/") / "index.html")
                          .read_text(encoding="utf-8"))
        # The service worker never keeps them.
        self.assertIn('"/downloads/"', (self.out / "sw.js").read_text(encoding="utf-8"))

    def ld(self, path, kind):
        page = (self.out / path / "index.html").read_text(encoding="utf-8")
        found = [json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page)]
        return next((d for d in found if d["@type"] == kind), None)

    def test_articles_and_the_dataset_have_linked_data(self):
        article = self.ld("articles/showing-the-work", "Article")
        self.assertEqual(article["url"], build_site.SITE_URL + "/articles/showing-the-work/")
        self.assertEqual(article["author"]["@type"], "Organization")
        self.assertRegex(article["datePublished"], r"^\d{4}-\d\d-\d\d$")
        self.assertEqual(self.ld("fr/articles/showing-the-work", "Article")["inLanguage"], "fr")
        dataset = self.ld("about", "Dataset")
        self.assertEqual(dataset["license"], build_site.CC0_URL)
        self.assertIn("own licences", dataset["description"])
        self.assertTrue(dataset["distribution"][0]["contentUrl"].startswith(build_site.GITHUB_URL))
        self.assertIsNone(self.ld("fr/about", "Dataset"))
        self.assertEqual(self.ld("jhn/3", "Chapter")["license"], build_site.CC0_URL)

    def test_book_pages_introduce_the_books_that_have_one(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        intros = sorted(p.stem for p in build_site.INTROS.glob("*.md"))
        self.assertTrue(intros)
        for book in intros:
            path = self.out / book.lower() / "index.html"
            page = path.read_text(encoding="utf-8")
            self.assertIn(f"<h1>{build_site.BOOK_NAMES[book]['en']}</h1>", page)
            self.assertIn(build_site.catalog("en")["book_page"]["draft"], page)
            self.assertNotIn("{{", page)
            self.assertIn(f"<loc>{build_site.SITE_URL}/{book.lower()}/</loc>", sitemap)
            # Every chapter in the outline, each with its section headings.
            chaps = dict(build_site.books("en"))[book]
            self.assertEqual(re.findall(r'<li><a href="/[a-z0-9]+/(\d+)/">', page), [str(p.chapter) for p in chaps])
            for href in re.findall(r'href="(/[^"#?]*)', page):
                target = self.out / href.lstrip("/")
                self.assertTrue(target.is_file() or (target / "index.html").is_file(), (book, href))
            # Only in the languages the introduction is written in.
            for lang in build_site.LANGUAGES:
                if lang != "en" and not build_site.load_intro(book, lang):
                    self.assertFalse((self.out / lang / book.lower() / "index.html").exists(), (lang, book))
            # Its chapters and the Read page lead to it.
            first = (self.out / book.lower() / str(chaps[0].chapter) / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'class="chap-book" href="/{book.lower()}/"', first)
            read = (self.out / "read" / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'<h2 id="book-{book.lower()}"><a href="/{book.lower()}/">', read)
            llms = (self.out / "llms.txt").read_text(encoding="utf-8")
            self.assertIn(f"({build_site.SITE_URL}/{book.lower()}/)", llms)

    def test_intros_type_no_greek_or_hebrew(self):
        for path in sorted(build_site.INTROS.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for script, (pattern, _) in build_site.validate._SCRIPTS.items():
                self.assertEqual(pattern.findall(text), [], f"{path.name}: {script} typed by hand")

    def test_chapters_have_a_breadcrumb_trail(self):
        def trail(path):
            return [(i["name"], i["item"]) for i in self.ld(path, "BreadcrumbList")["itemListElement"]]

        site = build_site.SITE_URL
        self.assertEqual(trail("php/2"), [("Open Word Bible", site + "/"), ("Read", site + "/read/"),
                                          ("Philippians", site + "/php/"), ("Philippians 2", site + "/php/2/")])
        # A book without a page goes straight from Read to the chapter.
        self.assertEqual(trail("mrk/2"), [("Open Word Bible", site + "/"), ("Read", site + "/read/"),
                                          ("Mark 2", site + "/mrk/2/")])
        mark = (self.out / "mrk" / "2" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="chap-book" href="/read/#mrk"', mark)
        self.assertEqual(trail("fr/php/2")[-1][1], site + "/fr/php/2/")
        self.assertEqual(len(trail("fr/php/2")), 3)

    def test_llms_txt_describes_the_site(self):
        text = (self.out / "llms.txt").read_text(encoding="utf-8")
        counts = build_site.status_counts()
        self.assertTrue(text.startswith("# Open Word Bible\n\n> "))
        self.assertIn(f"{counts['all']:,} sentences are drafted and {counts['approved']:,} are reviewed", text)
        self.assertIn(f"({build_site.SITE_URL}/about/status/)", text)
        self.assertIn(f"({build_site.SITE_URL}/articles/showing-the-work/)", text)

    def test_chapter_has_a_notes_section(self):
        page = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="notes"', page)
        self.assertIn("Tap a small letter to read its footnote", page)
        reader = (self.out / "reader.js").read_text(encoding="utf-8")
        # Alternatives a decision set aside are never offered as possible.
        self.assertIn('d.uncertain ? "fn_or" : "also"', reader)

    def test_read_page_lists_every_passage(self):
        read = (self.out / "read" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/jhn/1/"', read)
        self.assertIn('href="/php/4/"', read)
        # Each card opens with its passage's first verse, from the content.
        self.assertEqual(read.count('class="a-card p-card"'), len(build_site.chapters()))
        first = build_site.load_chapter("JHN", 1)[0][0]
        self.assertIn(build_site.plain(first["renderings"]["en"]["B"]), read)

    def test_a_sentence_across_a_chapter_break_is_on_both_pages(self):
        # John 7:53-8:1 is one sentence. It opens the bracketed, disputed
        # passage 7:53-8:11 with "[" and the note on the manuscripts, so John
        # 8 needs it as much as John 7 does.
        seven, eight = self.chapter_data("jhn/7"), self.chapter_data("jhn/8")
        self.assertEqual(seven["records"][-1]["id"], "JHN.7.53.s1")
        first = eight["records"][0]
        self.assertEqual(first["id"], "JHN.7.53.s1")
        self.assertTrue(first["renderings"]["en"]["B"].startswith("["))
        self.assertTrue(any(d["category"] == "text_variant" and d["footnote"] for d in first["decisions"]))
        self.assertEqual(eight["title"], "John 8")
        names = {p.chapter: (p.name, p.complete) for p in build_site.passages() if p.book == "JHN"}
        self.assertEqual(names[7], ("John 7", True))
        self.assertEqual(names[8], ("John 8", True))
        # Counted once on the home page.
        ids = [r["id"] for r in build_site.all_records()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_cards_quote_the_first_verse_outside_a_disputed_passage(self):
        records = build_site.load_chapter("JHN", 8)[0]
        self.assertEqual(build_site.opening(records, 8)[1], "JHN.8.12")
        self.assertIn("I am the light of the world", build_site.opening_verse(records, 8))
        records = build_site.load_chapter("JHN", 7)[0]
        self.assertEqual(build_site.opening(records, 7)[1], "JHN.7.1")

    def test_sentence_records_split_a_verse(self):
        data = self.chapter_data("php/4")
        five = [r for r in data["records"] if r["refs"] == ["PHP.4.5"]]
        self.assertEqual([r["id"] for r in five], ["PHP.4.5.s1", "PHP.4.5.s2"])
        self.assertFalse(set(five[0]["source"]["tokens"]) & set(five[1]["source"]["tokens"]))

    def test_pages_have_canonical_urls_and_a_sitemap(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        for path in ("", "read/", "about/", "jhn/1/", "php/4/"):
            url = f"{build_site.SITE_URL}/{path}"
            self.assertIn(f"<loc>{url}</loc>", sitemap)
            page = (self.out / path / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'<link rel="canonical" href="{url}">', page)
        self.assertNotIn("canonical", (self.out / "404.html").read_text(encoding="utf-8"))
        robots = (self.out / "robots.txt").read_text(encoding="utf-8")
        self.assertIn(f"Sitemap: {build_site.SITE_URL}/sitemap.xml", robots)
        self.assertTrue((self.out / "favicon.svg").is_file())

    def test_home_page_example_comes_from_the_content(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        example = home[home.index('class="example"'):home.index('class="points-wrap"')]
        # The text as read, without the tags that mark aligned words and settings.
        text = re.sub(r"<[^>]+>", "", example)
        self.assertEqual(len(build_site.EXAMPLES), 3)
        for book, chapter, record_id, decision_id in build_site.EXAMPLES:
            records, words = build_site.load_chapter(book, chapter)
            record = next(r for r in records if r["id"] == record_id)
            decision = next(d for d in record["decisions"] if d["id"] == decision_id)
            for level in "LBR":
                self.assertIn(html.escape(build_site.plain(record["renderings"]["en"][level]), quote=False), text)
            marked = [w["text"] for v in record["refs"] for w in words[v] if w["id"] in decision["tokens"]]
            self.assertTrue(marked)
            for word in marked:
                self.assertIn(f"<mark>{word}</mark>", example)
            for tid in record["source"]["tokens"]:
                if any(w["id"] == tid for v in record["refs"] for w in words[v]):
                    self.assertIn(f'data-t="{tid}"', example)
            self.assertIn(f'href="/{book.lower()}/{chapter}/"', example)
        # Aligned words light up their English; the divine name can switch.
        self.assertIn('class="al" data-t="n43001001002"', example)
        self.assertIn('data-switch="divine_name"', example)
        # One example is a call marked uncertain, with its other reading as "Or:".
        self.assertEqual(example.count('class="card decision uncertain"'), 1)
        self.assertIn(build_site.t("en", "home.tab_uncertain"), example)
        self.assertIn(build_site.t("en", "home.example_uncertain"), example)
        self.assertIn(f'<p class="alts">{build_site.catalog("en")["reader.ui"]["fn_or"]}', example)
        self.assertIn(f"<b>{len(build_site.all_records())}</b>", home)

    def test_fonts_are_self_hosted_with_their_licences(self):
        css = (self.out / "style.css").read_text(encoding="utf-8")
        files = re.findall(r"url\(/fonts/([^)]+)\)", css)
        self.assertTrue(files)
        for name in files:
            self.assertTrue((self.out / "fonts" / name).is_file(), name)
        for script in ("greek", "greek-ext"):
            self.assertIn(f"gentium-book-plus-{script}-400-normal.woff2", files)
        self.assertIn("noto-serif-hebrew-hebrew-400-normal.woff2", files)
        for licence in ("OFL-Gentium.txt", "OFL-NotoSerifHebrew.txt"):
            self.assertIn("SIL Open Font License", (ROOT / "web" / "fonts" / licence).read_text(encoding="utf-8"))
        home = (self.out / "index.html").read_text(encoding="utf-8")
        preload = re.search(r'<link rel="preload" href="/fonts/([^"]+)"', home)[1]
        self.assertIn(preload, files)

    def test_about_page_credits_sources(self):
        about = (self.out / "about" / "index.html").read_text(encoding="utf-8")
        for name in ("SBL Greek New Testament", "MACULA Greek", "Open Scriptures Hebrew Bible", "OpenBible.info"):
            self.assertIn(name, about)

    def test_beliefs_page_sets_out_the_creed_vision_and_values(self):
        page = (self.out / "about" / "beliefs" / "index.html").read_text(encoding="utf-8")
        self.assertIn("I believe in God, the Father almighty", page)
        self.assertIn("Apostles' Creed", page)
        for heading in ("Our vision", "Our mission", "What guides the work"):
            self.assertIn(f"<h2>{heading}</h2>", page)
        self.assertEqual(page.count("<li><strong>"), 5)
        # The About menu and the footer both link to it.
        self.assertGreaterEqual(page.count('href="/about/beliefs/"'), 2)

    def test_privacy_and_terms_of_use_pages(self):
        privacy = (self.out / "about" / "privacy" / "index.html").read_text(encoding="utf-8")
        self.assertIn("<h1>Privacy</h1>", privacy)
        self.assertIn('<a href="/account/">account page</a>', privacy)
        terms = (self.out / "about" / "terms-of-use" / "index.html").read_text(encoding="utf-8")
        self.assertIn("<h1>Terms of use</h1>", terms)
        self.assertIn('<a href="/about/#credits">Sources and credits</a>', terms)
        self.assertIn('<a href="/about/privacy/">privacy notice</a>', terms)
        # Every placeholder became a link.
        self.assertNotIn("{", re.search(r'<div class="prose legal">.*?</div>', terms, re.S)[0])
        # The footer links to both, in each language.
        self.assertIn('href="/about/terms-of-use/"', privacy)
        es = (self.out / "es" / "about" / "privacy" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<a href="/es/about/terms-of-use/">Condiciones de uso</a>', es)

    def test_about_page_renders_markdown_links(self):
        about = (self.out / "about" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<a href="https://github.com/seven1m/open-bibles">seven1m/open-bibles</a>', about)
        self.assertNotIn("](", about)

    def test_home_page_example_has_curly_quotes(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        why = re.search(r'<p class="why">(.*?)</p>', home, re.S)[1]
        self.assertNotIn('"', why)
        self.assertNotIn("&quot;", why)

    def test_home_page_searches_in_its_language(self):
        for lang in build_site.LANGUAGES:
            home = (self.out / build_site.url(lang, "/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            form = re.search(r'<form class="hero-search" action="([^"]+)"', home)
            self.assertEqual(form[1], build_site.url(lang, "/search/"))
            for q in build_site.catalog(lang)["search.examples"]:
                self.assertIn(f'?q={html.escape(q.replace(" ", "+"))}"', home)

    def test_home_page_offers_the_data(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        data = home[home.index('class="data"'):home.index('class="involve"')]
        self.assertIn(f'href="{build_site.GITHUB_URL}/archive/refs/heads/main.zip"', data)
        self.assertIn(f'href="{build_site.API_URL}/api/passages/JHN/1/"', data)
        self.assertIn("schema/sentence-record.schema.json", data)

    def test_home_page_shows_key_terms(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        terms = home[home.index('class="home-terms"'):]
        terms = terms[:terms.index("</section>")]
        self.assertIn('href="/terms/"', terms)
        self.assertEqual(terms.count('class="term-row"'), 6)
        self.assertIn('href="/terms/the-divine-name-yhwh/"', terms)

    def test_home_page_suggests_plans_offered_in_its_language(self):
        for lang in build_site.LANGUAGES:
            home = (self.out / build_site.url(lang, "/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            offered = build_site.available_plans(lang)
            cards = re.findall(r'data-plan-card="([^"]+)"', home)
            self.assertEqual(len(cards), min(3, len(offered)), lang)
            self.assertLessEqual(set(cards), {p.id for p in offered})

    def test_header_switches_language_and_offers_each_in_its_own_words(self):
        for lang in build_site.LANGUAGES:
            page = (self.out / build_site.url(lang, "/jhn/1/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            header = re.search(r'<header class="site">(.*?)</header>', page, re.S)[1]
            menu = re.search(r'<div id="lang-pop".*?</div>', header, re.S)[0]
            self.assertIn(f'<span class="lang-code">{lang.upper()}</span>', header)
            for code in build_site.LANGUAGES:
                if code == lang:
                    self.assertNotIn(f'data-lang="{code}"', menu)
                    continue
                self.assertIn(f'href="{build_site.url(code, "/jhn/1/")}"', menu)
                self.assertIn(f'data-lang="{code}" data-offer="{html.escape(build_site.t(code, "lang.offer"))}"', menu)

    def test_verses_of_the_day_are_drafted_whole_sentences(self):
        self.assertEqual(len(build_site.VERSES_OF_THE_DAY), len(set(build_site.VERSES_OF_THE_DAY)))
        for lang in build_site.LANGUAGES:
            verses = build_site.verses_of_the_day(lang)
            # A language shows only the verses translated into it: never
            # one in English (Vietnamese and Korean have John so far).
            self.assertEqual(len(verses), len(build_site.votd_refs(lang)))
            self.assertTrue(all("l" not in v for v in verses), lang)
            for vid, v in zip(build_site.votd_refs(lang), verses):
                # The verse ends a sentence, so it reads on its own (a closing
                # quotation mark may follow: ” ’, or French » after a no-break space).
                self.assertRegex(v["t"], r"[.?!](?:[”’]|\u00a0»)?$", vid)
        home = (self.out / "index.html").read_text(encoding="utf-8")
        data = re.search(r'<script type="application/json" class="votd-data">(.*?)</script>', home, re.S)[1]
        self.assertEqual(json.loads(data), build_site.verses_of_the_day("en"))

    def test_chapter_data_has_curly_quotes(self):
        for r in self.chapter_data()["records"]:
            texts = [t for levels in r["renderings"].values() for t in levels.values()]
            texts += [r["literal_gloss"]] + [d["reason"] for d in r["decisions"]]
            for text in texts:
                self.assertNotRegex(text, "[\"']", r["id"])

    def test_measures_control_only_where_a_passage_has_units(self):
        gen6 = (self.out / "gen" / "6" / "index.html").read_text(encoding="utf-8")
        gen1 = (self.out / "gen" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-setting="units"', gen6)
        self.assertNotIn('data-setting="units"', gen1)
        self.assertIn("{{units:450 feet|300 cubits}}", json.dumps(self.chapter_data("gen/6")["records"]))

    def test_old_testament_pages_offer_the_divine_name(self):
        # The divine name (the LORD or Yahweh) on Old Testament pages, the
        # title Christ (Christ or Messiah) on New Testament ones.
        gen = (self.out / "gen" / "2" / "index.html").read_text(encoding="utf-8")
        jhn = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-setting="divine_name"', gen)
        self.assertIn('id="hint-divine_name"', gen)
        self.assertNotIn('data-setting="christos"', gen)
        self.assertIn('data-setting="christos"', jhn)
        self.assertNotIn('data-setting="divine_name"', jhn)
        text = json.dumps(self.chapter_data("gen/2")["records"])
        self.assertIn("{{divine_name:the LORD|Yahweh}}", text)

    def test_chapter_settings_fold_behind_a_toggle(self):
        page = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        self.assertIn('aria-controls="settings"', page)
        self.assertIn('<div class="settings" id="settings">', page)

    def test_assets_are_versioned_by_content(self):
        # A deploy must never pair new pages with a stylesheet the browser
        # kept from the last one: each asset URL carries its content hash.
        home = (self.out / "index.html").read_text(encoding="utf-8")
        chapter = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        for name, page in (("style.css", home), ("site.js", home), ("markup.js", chapter),
                           ("reader.js", chapter)):
            m = re.search(r'"/%s\?v=([0-9a-f]{10})"' % re.escape(name), page)
            self.assertTrue(m, name)
            digest = hashlib.sha256((self.out / name).read_bytes()).hexdigest()[:10]
            self.assertEqual(m[1], digest, name)

    def test_header_dropdowns_list_passages_and_articles(self):
        home = (self.out / "index.html").read_text(encoding="utf-8")
        header = re.search(r'<header class="site">(.*?)</header>', home, re.S)[1]
        for key in ("read", "articles", "about"):
            self.assertIn(f'aria-controls="dd-{key}"', header)
            self.assertIn('<div class="dropdown', header)
        # A line per book, linking to its chapters on the Read page.
        self.assertIn('href="/read/#jhn"', header)
        self.assertIn('href="/read/#php"', header)
        self.assertNotIn('class="chap', header)
        # Continue reading heads the Read menu, hidden until web/site.js
        # finds a place; GitHub is under About, not a header button.
        read_panel = header[header.index('id="dd-read"'):header.index('id="dd-articles"')]
        self.assertIn('<a class="dd-resume" data-resume hidden', read_panel)
        self.assertNotIn(f'class="tool-btn" href="{build_site.GITHUB_URL}"', header)
        about_panel = header[header.index('id="dd-about"'):]
        self.assertIn(f'href="{build_site.GITHUB_URL}"', about_panel)
        # ...grouped by testament, Old before New.
        read = header[header.index('id="dd-read"'):header.index('id="dd-articles"')]
        self.assertLess(read.index(">Old Testament<"), read.index('href="/read/#gen"'))
        self.assertLess(read.index('href="/read/#gen"'), read.index(">New Testament<"))
        self.assertLess(read.index(">New Testament<"), read.index('href="/read/#jhn"'))
        # The first few articles of each section, and a link to the rest.
        articles_ = sorted(build_site.load_articles(), key=lambda a: a["order"])
        for key in build_site.SECTIONS:
            section = [a for a in articles_ if a["section"] == key]
            for i, a in enumerate(section):
                linked = f'href="{build_site.article_url(a)}"' in header
                self.assertEqual(linked, i < build_site.MENU_ARTICLES, a["slug"])
            if len(section) > build_site.MENU_ARTICLES:
                self.assertIn(f'href="/articles/#{key}"', header)
        self.assertNotIn("min read", header)
        # The current section's trigger is marked on its pages.
        articles = (self.out / "articles" / "index.html").read_text(encoding="utf-8")
        self.assertRegex(articles, r'class="nav-link nav-trigger active"[^>]*aria-controls="dd-articles"')
        # ...and the dropdown link to the page itself tells a screen reader.
        chapter = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        chapter_header = re.search(r'<header class="site">(.*?)</header>', chapter, re.S)[1]
        self.assertIn('data-book="jhn" aria-current="true"', chapter_header)
        self.assertNotIn('data-book="php" aria-current', chapter_header)

    def test_interface_fonts_are_self_hosted_with_their_licences(self):
        css = (self.out / "style.css").read_text(encoding="utf-8")
        files = re.findall(r"url\(/fonts/([^)]+)\)", css)
        self.assertTrue(files)
        for name in files:
            self.assertTrue((self.out / "fonts" / name).is_file(), name)
        self.assertIn("atkinson-hyperlegible-latin-400-normal.woff2", files)
        for licence in ("OFL-Fraunces.txt", "OFL-HankenGrotesk.txt", "OFL-AtkinsonHyperlegible.txt"):
            self.assertIn("SIL Open Font License", (ROOT / "web" / "fonts" / licence).read_text(encoding="utf-8"))
        home = (self.out / "index.html").read_text(encoding="utf-8")
        preload = re.search(r'<link rel="preload" href="/fonts/([^"]+)"', home)[1]
        self.assertIn(preload, files)

    def test_whole_chapters_are_named_without_a_verse_range(self):
        names = {(p.book, p.chapter): (p.name, p.complete) for p in build_site.passages()}
        self.assertEqual(names[("PHP", 2)], ("Philippians 2", True))
        page = (self.out / "php" / "2" / "index.html").read_text(encoding="utf-8")
        self.assertIn("<title>Philippians 2 · Open Word Bible</title>", page)
        self.assertNotIn("Sample passage", page)

    def test_reader_links_every_chapter_and_its_neighbours(self):
        ps = build_site.passages()
        for i, p in enumerate(ps):
            page = (self.out / p.url.strip("/") / "index.html").read_text(encoding="utf-8")
            strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
            for q in ps:
                if q.book == p.book:
                    self.assertIn(f'href="{q.url}"', strip)
            self.assertIn(f'href="{p.url}" aria-current=page', strip)
            turns = re.search(r'<nav class="turns"(.*?)</nav>', page, re.S)[1]
            if i > 0:
                self.assertIn(f'href="{ps[i - 1].url}" rel="prev"', turns)
            if i + 1 < len(ps):
                self.assertIn(f'href="{ps[i + 1].url}" rel="next"', turns)

    def test_home_page_progress_is_for_its_language(self):
        every, passages = build_site.all_records(), build_site.passages()
        for lang in build_site.LANGUAGES:
            home = (self.out / build_site.url(lang, "/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            progress = home[home.index('class="progress"'):home.index('class="involve"')]
            records = [r for r in every if lang in r["renderings"]]
            decisions = sum(d["language"] in (None, lang) for r in records for d in r["decisions"])
            self.assertIn(f"<b>{len(records)}</b>", progress)
            self.assertIn(f"<b>{decisions}</b>", progress)
            # The map has a tile for every book, linked once it has a
            # sentence in lang, and no chapter links.
            shown = {build_site.refs.parse(r["refs"][0]).book for r in records}
            self.assertEqual(progress.count('<li><a class="map-book') + progress.count('<li><span class="map-book'),
                             len(build_site.refs.BOOK_CODES))
            for book in build_site.refs.BOOK_CODES:
                link = f'href="{build_site.url(lang, f"/read/#{book.lower()}")}"'
                self.assertEqual(link in progress, book in shown, (lang, book))
            for p in passages:
                self.assertNotIn(f'href="{build_site.url(lang, p.url)}"', progress, (lang, p.url))

    def test_header_footer_and_read_page_list_only_the_page_language(self):
        for lang in build_site.LANGUAGES:
            shown = {(p.book, p.chapter) for p in build_site.passages_in(lang)}
            books = {b for b, _ in shown}
            read = (self.out / build_site.url(lang, "/read/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            header = re.search(r"<header.*?</header>", read, re.S)[0]
            footer = re.search(r"<footer.*?</footer>", read, re.S)[0]
            for p in build_site.passages():
                self.assertEqual(f'id="{p.book.lower()}"' in read, p.book in books, (lang, p.book))
                book_link = f'href="{build_site.url(lang, f"/read/#{p.book.lower()}")}"'
                self.assertEqual(book_link in header, p.book in books, (lang, p.book))
                self.assertEqual(book_link in footer, p.book in books, (lang, p.book))

    def test_reader_navigation_lists_only_the_page_language(self):
        for lang in build_site.LANGUAGES:
            shown = {(p.book, p.chapter) for p in build_site.passages_in(lang)}
            for p in build_site.passages():
                page = (self.out / build_site.url(lang, p.url).lstrip("/") / "index.html").read_text(encoding="utf-8")
                strip = re.search(r'<nav class="chapstrip".*?</nav>', page, re.S)[0]
                turns = re.search(r'<nav class="turns".*?</nav>', page, re.S)[0]
                linked = {(q.book, q.chapter) for q in build_site.passages()
                          if f'href="{build_site.url(lang, q.url)}"' in strip + turns}
                if (p.book, p.chapter) in shown:
                    self.assertLessEqual(linked, shown, (lang, p.url))
                else:  # a page not yet in lang is in English, and links like one
                    self.assertIn((p.book, p.chapter), linked, (lang, p.url))

    def test_read_page_cards_count_the_page_language(self):
        for lang in build_site.LANGUAGES:
            for p in build_site.passages_in(lang):
                card = build_site.passage_card(p.book, p.chapter, lang)
                shown = [d for r in p.records for d in r["decisions"] if d["language"] in (None, lang)]
                self.assertIn(build_site.t(lang, "card.meta", verses=p.verses, sentences=len(p.records),
                                           decisions=len(shown),
                                           uncertain=sum(d["uncertain"] for d in shown)), card)

    def test_paragraphs_follow_the_greek(self):
        # SBLGNT capitalises a paragraph's first word; John 2 has four.
        self.assertEqual(self.chapter_data("jhn/2")["paragraphs"],
                         ["JHN.2.1.s1", "JHN.2.12.s1", "JHN.2.13.s1", "JHN.2.23.s1"])
        # A capitalised quotation after a raised dot does not open one.
        self.assertNotIn("JHN.4.29.s1", self.chapter_data("jhn/4")["paragraphs"])
        # The Hebrew codex marks paragraphs with pe or samekh: Genesis 1's days.
        self.assertEqual(self.chapter_data("gen/1")["paragraphs"],
                         ["GEN.1.1.s1", "GEN.1.6.s1", "GEN.1.9.s1", "GEN.1.14.s1", "GEN.1.20.s1", "GEN.1.24.s1"])

    def test_headings_stand_above_paragraphs(self):
        ids = {r["id"] for b, c in build_site.chapters() for r in build_site.load_chapter(b, c)[0]}
        for rid, heading in build_site.headings().items():
            self.assertIn(rid, ids, rid)
            self.assertIn("en", heading, rid)
            book, chapter = rid.split(".")[:2]
            data = self.chapter_data(f"{book.lower()}/{chapter}")
            self.assertIn(rid, data["paragraphs"], rid)
            self.assertEqual(data["headings"][rid], heading)

    def test_chapter_pages_carry_their_cross_references(self):
        # Every verse on the page with references has them, and only those:
        # Psalm 3:1 is the title, so the first references are verse 2's.
        for path, book in (("jhn/3", "JHN"), ("psa/3", "PSA"), ("es/jhn/3", "JHN")):
            data = self.chapter_data(path)
            vids = {vid for r in data["records"] for vid in r["refs"]}
            table = crossrefs.load(book)
            self.assertEqual(data["crossrefs"], {v: table[v] for v in vids if v in table}, path)
        self.assertEqual(self.chapter_data("jhn/3")["crossrefs"]["JHN.3.16"][0], "ROM.5.8")
        self.assertNotIn("PSA.3.1", self.chapter_data("psa/3")["crossrefs"])
        page = (self.out / "jhn" / "3" / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-setting="crossrefs"', page)
        self.assertIn('id="xr-margin"', page)

    def test_verse_of_the_day_feed(self):
        # One Atom feed per language: the home page's verse for each of the
        # last days, linking to that verse in the reader, which is built.
        import datetime
        import xml.etree.ElementTree as ET
        atom = "{http://www.w3.org/2005/Atom}"
        for lang in build_site.LANGUAGES:
            rel = build_site.votd_feed_url(lang).lstrip("/")
            feed = ET.parse(self.out / rel).getroot()
            entries = feed.findall(atom + "entry")
            self.assertEqual(len(entries), build_site.VOTD_FEED_DAYS, lang)
            for entry in entries:
                day = datetime.date.fromisoformat(entry.find(atom + "updated").text[:10])
                vid = build_site.votd_for_day(day, lang)
                ref = build_site.refs.parse(vid)
                link = entry.find(atom + "link").get("href")
                self.assertTrue(link.endswith(f"/{ref.book.lower()}/{ref.chapter}/#v{ref.verse}"), link)
                page = link.removeprefix(build_site.SITE_URL).split("#")[0].strip("/")
                self.assertTrue((self.out / page / "index.html").is_file(), link)
            home = (self.out / build_site.url(lang, "/").strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn('type="application/atom+xml"', home)
            self.assertIn(f'href="{build_site.votd_feed_url(lang)}"', home)

    def test_compare_page_and_its_editions(self):
        # One page per language takes the verse from its address; the other
        # Bibles come from a file per chapter, in our verse numbering.
        for lang in build_site.LANGUAGES:
            page = (self.out / build_site.url(lang, "/compare/").strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="cmp-data"', page)
            self.assertIn("compare.js?v=", page)
        files = sorted((self.out / build_site.EDITIONS_DIR).glob("*/*.json"))
        self.assertEqual(len(files), sum(build_site.BOOK_CHAPTERS.values()))
        john = json.loads((self.out / "editions" / "JHN" / "3.json").read_text(encoding="utf-8"))
        self.assertEqual(set(john), {code for code, _, _ in build_site.EDITIONS})
        self.assertIn("loved the world", john["bsb"]["16"])
        # English Psalm 3:1 is our 3:2; our 3:1 is the title, which they lack.
        psalm = json.loads((self.out / "editions" / "PSA" / "3.json").read_text(encoding="utf-8"))
        self.assertNotIn("1", psalm["bsb"])
        self.assertTrue(psalm["bsb"]["2"].startswith("O LORD"))
        # The reader's panel links each verse here.
        self.assertEqual(self.chapter_data("jhn/3")["compare_url"], "/compare/")
        self.assertEqual(self.chapter_data("es/jhn/3")["compare_url"], "/es/compare/")

    def test_word_pages_and_their_shards(self):
        # Each dictionary form is in the shard its hash names; the hash must
        # agree with web/word.js (tests/js/word.test.mjs, same vectors).
        vectors = json.loads((ROOT / "tests" / "word_shard_vectors.json").read_text(encoding="utf-8"))
        self.assertEqual(vectors["shards"], build_site.WORD_SHARDS)
        for lemma, shard in vectors["cases"]:
            self.assertEqual(build_site.word_shard(lemma), shard, lemma)
        shards = {int(p.stem): json.loads(p.read_text(encoding="utf-8"))
                  for p in (self.out / build_site.WORDS_DIR).glob("*.json")}
        self.assertEqual(set(shards), set(range(build_site.WORD_SHARDS)))
        uses = json.loads((self.out / "word-uses.json").read_text(encoding="utf-8"))
        for lemma, verses in uses.items():
            entry = shards[build_site.word_shard(lemma)].get(lemma)
            self.assertIsNotNone(entry, lemma)
            self.assertEqual(sum(n for _, n in entry["b"]), len(verses), lemma)
            self.assertEqual(entry["v"], verses[:build_site.WORD_VERSES], lemma)
        for lang in build_site.LANGUAGES:
            page = (self.out / build_site.url(lang, "/word/").strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="word-data"', page)
        self.assertEqual(self.chapter_data("jhn/3")["word_url"], "/word/")

    def test_every_chapter_has_a_preview_file(self):
        # Cross-reference previews fetch /verses/<BOOK>/<chapter>.json: one
        # for every chapter of the Bible, ours where translated, otherwise
        # the comparison text in our verse numbering.
        files = sorted((self.out / build_site.VERSES_DIR).glob("*/*.json"))
        self.assertEqual(len(files), sum(build_site.BOOK_CHAPTERS.values()))
        john = json.loads((self.out / "verses" / "JHN" / "3.json").read_text(encoding="utf-8"))
        record = next(r for r in build_site.load_chapter("JHN", 3)[0] if "JHN.3.16" in r["refs"])
        self.assertEqual(set(john["v"]["16"]["en"]), {"L", "B", "R"})
        self.assertIn("{{", john["v"]["16"]["en"]["B"])   # settings kept for the reader
        self.assertEqual(john["v"]["16"]["en"]["B"], build_site.record_verses(record)["JHN.3.16"]["en"]["B"])
        self.assertNotIn("c", john)
        data = self.chapter_data("es/jhn/3")
        self.assertEqual(data["verses"]["url"], "/verses/")
        self.assertEqual(data["verses"]["compare"][0][0], "rv1909")

    def test_preview_files_number_untranslated_verses_as_we_do(self):
        # A chapter with comparison text has it under our verse numbers:
        # English Psalm 3:1 is our Psalm 3:2, after the title.
        for path in sorted((self.out / build_site.VERSES_DIR).glob("*/*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for code, verses in data.get("c", {}).items():
                self.assertIn(code, build_site.COMPARISON_EDITIONS)
                self.assertFalse(set(verses) & set(data.get("v", {})), path)
        moved = build_site.versification.to_source(build_site.refs.parse("PSA.3.1"))
        self.assertEqual([str(r) for r in moved], ["PSA.3.2"])

    def test_summary_stands_under_the_title(self):
        page = (self.out / "1ti" / "5" / "index.html").read_text(encoding="utf-8")
        summary = html.escape(build_site.summaries()[("1TI", 5)]["en"])
        self.assertRegex(page, r'<h1 id="title">[^<]*</h1>\s*<p class="chapter-summary">' + re.escape(summary))
        # A page in another language shows the English summary only where the
        # chapter itself reads in English, and marks it so.
        records = build_site.load_chapter("1TI", 5)[0]
        if not any("es" in r["renderings"] for r in records) and "es" not in build_site.summaries()[("1TI", 5)]:
            page = (self.out / "es" / "1ti" / "5" / "index.html").read_text(encoding="utf-8")
            self.assertIn('<p class="chapter-summary" lang="en">', page)
        with_es = [{"renderings": {"en": {}, "es": {}}}]
        self.assertEqual(build_site.chapter_summary("1TI", 5, with_es, "es"), "")
        self.assertEqual(build_site.chapter_summary("JHN", 999, records, "en"), "")

    def test_chapter_strip_shows_the_whole_book(self):
        page = (self.out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
        strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
        done = {p.chapter for p in build_site.passages() if p.book == "JHN"}
        pills = re.findall(r'class="chap[^"]*"[^>]*>(\d+)<', strip)
        self.assertEqual([int(n) for n in pills], list(range(1, build_site.BOOK_CHAPTERS["JHN"] + 1)))
        self.assertEqual(len(re.findall(r'class="chap none"', strip)), 21 - len(done))

    def test_aligned_records_carry_their_ranges(self):
        records = self.chapter_data("jhn/2")["records"]
        linked = [r for r in records if r["links"]]
        self.assertTrue(linked)
        for r in linked:
            text = r["renderings"]["en"]["B"]
            for (start, end, tokens), al in zip(r["links"]["en"]["B"], r["alignments"]):
                self.assertEqual(al["tokens"], tokens)
                # Curly quotes on the page keep every range in place.
                self.assertEqual(build_site.smart_quotes(al["target_span"]), text[start:end])

    def test_word_uses_index(self):
        text = (self.out / "word-uses.json").read_text(encoding="utf-8")
        index = json.loads(text)
        data = self.chapter_data("jhn/2")
        # Each page points at this build's copy of the index.
        self.assertEqual(data["uses"], build_site.word_uses()[1])
        self.assertIn(hashlib.sha256(text.encode()).hexdigest()[:10], data["uses"])
        # Every word of a translated sentence is listed at its verse, once.
        record = data["records"][0]
        for word in data["words"]["JHN.2.1"]:
            if word["id"] in record["source"]["tokens"]:
                self.assertIn("JHN.2.1", index[word["lemma"]])
        for places in index.values():
            self.assertEqual(len(places), len(set(places)))

    def test_reader_has_a_reading_view(self):
        page = (self.out / "jhn" / "2" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<span class="seg" data-setting="view">', page)
        self.assertIn('id="hint-view"', page)
        reader = (self.out / "reader.js").read_text(encoding="utf-8")
        # Copying from the passage adds its reference and level.
        self.assertIn('addEventListener("copy"', reader)
        self.assertIn('" (Open Word Bible, "', reader)

    def test_reader_can_go_to_a_reference(self):
        page = (self.out / "jhn" / "2" / "index.html").read_text(encoding="utf-8")
        strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
        self.assertIn('class="chap-goto" data-open-search', strip)
        search = (self.out / "search.js").read_text(encoding="utf-8")
        # A reference is the palette's first row, so Enter goes straight to it.
        self.assertLess(search.index('fill(ui("go_to")'), search.index('fill(ui("show_all")'))

    def test_name_cards_match_the_word_data(self):
        import glob
        words = {}
        for path in glob.glob(str(build_site.ROOT / "data" / "*" / "*.json")):
            if "/grc/" in path or "/hbo/" in path:
                for vid, ws in json.loads(Path(path).read_text(encoding="utf-8"))["verses"].items():
                    for w in ws:
                        words.setdefault((build_site.word_strong(w), w["lemma"]), set()).add(vid)
        for (strong, lemma), senses in build_site.name_cards().items():
            # Every lemma is copied from the source data, never typed.
            self.assertIn((strong, lemma), words, (strong, lemma))
            listed = [v for s in senses for v in s.get("verses", [])]
            self.assertEqual(len(listed), len(set(listed)), strong)
            self.assertLessEqual(sum("verses" not in s for s in senses), 1, strong)
            self.assertTrue(set(listed) <= words[(strong, lemma)], strong)
        # A page's cards resolve a shared name by verse: two Lamechs.
        gen4 = self.chapter_data("gen/4")["cards"]["list"]
        gen5 = self.chapter_data("gen/5")["cards"]["list"]
        self.assertIn("Lamech, descendant of Cain", [c["title"] for c in gen4])
        self.assertIn("Lamech, father of Noah", [c["title"] for c in gen5])

    def test_site_can_be_installed_and_read_offline(self):
        manifest = json.loads((self.out / "manifest.webmanifest").read_text(encoding="utf-8"))
        for icon in manifest["icons"]:
            self.assertTrue((self.out / icon["src"].lstrip("/")).is_file(), icon["src"])
        sw = (self.out / "sw.js").read_text(encoding="utf-8")
        self.assertNotIn("__PRECACHE__", sw)
        self.assertNotIn("__VERSION__", sw)
        precache = json.loads(re.search(r"var PRECACHE = (\[.*?\]);", sw)[1])
        for u in precache:
            path = u.split("?")[0].lstrip("/")
            self.assertTrue((self.out / path).is_file() or (self.out / path / "index.html").is_file(), u)
        for lang in build_site.LANGUAGES:
            self.assertIn(build_site.url(lang, "/offline/"), precache)
        page = (self.out / "jhn" / "2" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="manifest" href="/manifest.webmanifest">', page)
        self.assertNotIn("/offline/", (self.out / "sitemap.xml").read_text(encoding="utf-8"))

    def test_reader_can_read_aloud(self):
        for code in build_site.LANGUAGES:
            page = (self.out / build_site.url(code, "/jhn/2/").lstrip("/") / "index.html").read_text(encoding="utf-8")
            strip = re.search(r'<nav class="chapstrip"(.*?)</nav>', page, re.S)[1]
            # Hidden until reader.js finds the browser can speak.
            self.assertIn('id="listen-start" hidden', strip)
            ui = self.chapter_data(build_site.url(code, "/jhn/2").lstrip("/"))["ui"]
            for key in ("listen_bar", "listen_play", "listen_pause", "listen_prev", "listen_next",
                        "listen_speed", "listen_voice", "listen_stop", "listen_no_voice"):
                self.assertTrue(ui.get(key), (code, key))

    def test_saved_verses_page(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("/saved/", sitemap)
        for code in build_site.LANGUAGES:
            rel = build_site.url(code, "/saved/").lstrip("/")
            page = (self.out / rel / "index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex">', page)
            data = json.loads(html.unescape(re.search(r'data-saved="([^"]*)"', page)[1]))
            self.assertEqual(data["order"], [b for b, _ in build_site.books()])
            # Each book's chapter address is the reader's, in the page language.
            self.assertEqual(data["chapters"]["JHN"].replace("{c}", "3"), build_site.url(code, "/jhn/3/"))
            self.assertTrue((self.out / build_site.url(code, "/jhn/3/").lstrip("/") / "index.html").is_file())
            chapter = self.chapter_data(build_site.url(code, "/jhn/2").lstrip("/"))
            self.assertEqual(chapter["saved"], build_site.url(code, "/saved/"))
            for key in ("bookmark", "bookmarked", "highlight", "hl_yellow", "hl_green", "hl_blue",
                        "hl_pink", "saved_all"):
                self.assertTrue(chapter["ui"].get(key), (code, key))

    def test_read_page_groups_chapters_by_book(self):
        read = (self.out / "read" / "index.html").read_text(encoding="utf-8")
        for book, chaps in build_site.books():
            section = re.search(rf'<section class="book-group" id="{book.lower()}"(.*?)</section>', read, re.S)[1]
            for p in chaps:
                self.assertIn(f'href="{p.url}"', section)
        self.assertIn("4 of 4 chapters, complete", read)
        self.assertIn("1 chapter, complete", read)
        self.assertNotIn("1 of 1 chapters", read)
        # An index of the books first, each linked to its section.
        index = re.search(r'<nav class="book-index".*?</nav>', read, re.S)[0]
        for book, _ in build_site.books():
            self.assertIn(f'href="#{book.lower()}"', index)

    def test_card_quotes_alternate_and_keep_apostrophes(self):
        # Speech inside the verse's speech turns to double quotes.
        self.assertEqual(build_site.inner_quotes("He said, \u201cThey will say, \u2018No.\u2019\u201d"),
                         "He said, \u2018They will say, \u201cNo.\u201d\u2019")
        # An apostrophe is not a closing quote.
        self.assertEqual(build_site.inner_quotes("Moses\u2019 father-in-law and Aaron\u2019s sons"),
                         "Moses\u2019 father-in-law and Aaron\u2019s sons")
        # Speech that runs on into the next verse is closed, inner first.
        self.assertEqual(build_site.inner_quotes("He said, \u201cTell him, \u2018Go"),
                         "He said, \u2018Tell him, \u201cGo\u201d\u2019")

    def built(self, path):
        """The built file a site path names ("/es/offline/", "/style.css?v=...")."""
        rel = path.split("?")[0].lstrip("/")
        return self.out / (rel + "index.html" if rel.endswith("/") or not rel else rel)

    def test_offline_worker_keeps_files_that_exist(self):
        sw = (self.out / "sw.js").read_text(encoding="utf-8")
        self.assertNotIn("__", sw.split('"use strict";')[1])
        precache = json.loads(re.search(r"var PRECACHE = (.*);", sw)[1])
        offline = json.loads(re.search(r"var OFFLINE = (.*);", sw)[1])
        for path in precache + list(offline.values()):
            self.assertTrue(self.built(path).is_file(), path)
        self.assertIn(build_site.asset("reader.js"), precache)
        self.assertIn(build_site.asset("markup.js"), precache)
        self.assertEqual(set(offline), {"" if code == "en" else code for code in build_site.LANGUAGES})
        manifest = json.loads((self.out / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["start_url"], "/")
        self.assertIn('<link rel="manifest" href="/manifest.webmanifest">',
                      (self.out / "index.html").read_text(encoding="utf-8"))

    def test_offline_pages_are_built_but_not_indexed(self):
        sitemap = (self.out / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotIn("/offline/", sitemap)
        for code in build_site.LANGUAGES:
            page = self.built(build_site.url(code, "/offline/")).read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex">', page)
            self.assertIn('id="saved-books"', page)

    def test_read_page_can_save_each_book(self):
        for code in build_site.LANGUAGES:
            read = self.built(build_site.url(code, "/read/")).read_text(encoding="utf-8")
            files = json.loads(html.unescape(re.search(r'data-offline-files="([^"]*)"', read)[1]))
            for path in files:
                self.assertTrue(self.built(path).is_file(), path)
            buttons = re.findall(r'class="save-book" hidden data-book="([A-Z0-9]+)"[^>]*data-pages="([^"]*)"', read)
            self.assertEqual([b for b, _ in buttons], [b for b, _ in build_site.books(code)])
            for _, pages in buttons:
                for path in json.loads(html.unescape(pages)):
                    self.assertTrue(path.startswith(build_site.url(code, "/")), path)
                    self.assertTrue(self.built(path).is_file(), path)


def note(reason, alternatives=()):
    return {"decisions": [{"choice": "x", "alternatives": list(alternatives), "reason": reason}]}


class ComparisonTest(unittest.TestCase):
    """A note's reference to a chapter not translated yet carries that
    verse from a public-domain Bible, for comparison: only the verses the
    page's notes name, so the page stays small. Every book now has English,
    so these tests take Ecclesiastes out of the translated chapters."""

    def setUp(self):
        real = build_site.book_refs

        def without_ecclesiastes(lang="en"):
            out = dict(real(lang))
            out["chapters"] = {b: c for b, c in out["chapters"].items() if b != "ECC"}
            return out

        patcher = mock.patch.object(build_site, "book_refs", without_ecclesiastes)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_notes_bring_only_untranslated_verses(self):
        records, _ = build_site.load_chapter("PRO", 21)
        compare = build_site.comparison_verses(records, "en")
        self.assertEqual((compare["name"], compare["lang"]), ("World English Bible", "en"))
        # Proverbs 21:6's note points to Ecclesiastes 1:2.
        self.assertEqual(compare["verses"]["ECC.1.2"], build_site.comparison_text("web")["ECC.1.2"])
        have = build_site.book_refs("en")["chapters"]
        for vid in compare["verses"]:
            book, chapter, _ = vid.split(".")
            self.assertNotIn(int(chapter), have.get(book, []), vid)

    def test_spanish_pages_compare_with_the_reina_valera(self):
        records, _ = build_site.load_chapter("PRO", 21)
        compare = build_site.comparison_verses(records, "es")
        self.assertEqual((compare["name"], compare["lang"]), ("Reina-Valera 1909", "es"))
        self.assertEqual(compare["verses"]["ECC.1.2"], build_site.comparison_text("rv1909")["ECC.1.2"])

    def test_ranges_are_capped_and_translated_chapters_skipped(self):
        have = build_site.book_refs("en")["chapters"]
        self.assertIn(10, have["LUK"])
        self.assertNotIn(9, have.get("ECC", []))
        self.assertNotIn(3, have.get("ECC", []))
        compare = build_site.comparison_verses(
            [note("As in Ecclesiastes 9:9-18, and Luke 10:7.", alternatives=["Ecclesiastes 3:4"])], "en")
        self.assertEqual(set(compare["verses"]),
                         {"ECC.3.4"} | {f"ECC.9.{v}" for v in range(9, 9 + build_site.COMPARE_MAX_VERSES)})
        self.assertIsNone(build_site.comparison_verses([note("Luke 10:7 only.")], "en"))
        self.assertIsNone(build_site.comparison_verses([note("No references here.")], "en"))

    def test_chapter_pages_embed_the_comparison(self):
        page = build_site.chapter_page("PRO", 21)
        data = json.loads(re.search(r'<script type="application/json" id="owb-data">(.*?)</script>', page, re.S)[1])
        self.assertIn("ECC.1.2", data["compare"]["verses"])
        # A page's comparison verses are a few kilobytes at most.
        self.assertLess(len(json.dumps(data["compare"], ensure_ascii=False)), 25000)


class SharedDataTest(unittest.TestCase):
    """Book data that pull requests adding chapters would otherwise all edit."""

    def test_every_book_is_named_in_every_language(self):
        from owb import refs
        self.assertEqual(list(build_site.BOOK_NAMES), refs.BOOK_CODES)
        for code, names in build_site.BOOK_NAMES.items():
            self.assertEqual(set(names), set(build_site.LANGUAGES), code)
            self.assertEqual(names["en"], refs.BOOK_NAMES[code])
            self.assertGreater(build_site.BOOK_CHAPTERS[code], 0, code)

    def test_headings_are_filed_by_book(self):
        for path in (ROOT / "data" / "headings").glob("*.json"):
            for rid in json.loads(path.read_text(encoding="utf-8"))["headings"]:
                self.assertEqual(rid.split(".")[0], path.stem, path.name)

    def test_summaries_are_well_formed(self):
        done = set(build_site.chapters())
        for path in (ROOT / "data" / "summaries").glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "ai_draft", path.name)
            self.assertTrue(data["description"], path.name)
            for chapter, summary in data["summaries"].items():
                where = f"{path.name} {chapter}"
                self.assertRegex(chapter, r"^[1-9][0-9]*$", where)
                self.assertIn((path.stem, int(chapter)), done, where)
                self.assertIn("en", summary, where)
                for lang, text in summary.items():
                    self.assertIn(lang, build_site.LANGUAGES, where)
                    self.assertTrue(text.strip(), where)
                    # Shown as plain text under the title: no reader settings.
                    self.assertNotIn("{{", text, where)


if __name__ == "__main__":
    unittest.main()
