// web/admin.js's OWBAdminNav: section filters kept in the address, and the
// command palette's matching.
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";

const ROOT = new URL("../../", import.meta.url).pathname;
const context = vm.createContext({ document: { getElementById: () => null } });
vm.runInContext(readFileSync(join(ROOT, "web/admin.js"), "utf-8"), context, { filename: "web/admin.js" });
const N = context.OWBAdminNav;
const plain = (x) => JSON.parse(JSON.stringify(x));

const REVIEW = { layer: "", book: "", state: "todo" };
const USERS = { q: "", role: "", offset: 0 };

test("an address is parsed into its section, argument and parameters", () => {
  assert.deepEqual(plain(N.parse("#review?layer=grc&book=ISA&state=")), {
    path: "review", name: "review", arg: "", params: { layer: "grc", book: "ISA", state: "" }, query: true });
  assert.deepEqual(plain(N.parse("#inbox/mine")), { path: "inbox/mine", name: "inbox", arg: "mine", params: {}, query: false });
  assert.deepEqual(plain(N.parse("verse/JHN.1.1")).arg, "JHN.1.1");
  assert.deepEqual(plain(N.parse("#review/grc/JHN.1.1.s1")).arg, "grc/JHN.1.1.s1");
  assert.deepEqual(plain(N.parse("#users?q=ruth%40example.org&offset=50")).params, { q: "ruth@example.org", offset: "50" });
  assert.deepEqual(plain(N.parse("#users?q=two+words")).params, { q: "two words" });
  assert.equal(N.parse("#users?").query, true);
  assert.deepEqual(plain(N.parse("#users?q=%E0%A4")).params, { q: "%E0%A4" });   // malformed, kept as is
  assert.equal(N.parse("").name, "");
});

test("filters are read with their defaults' types", () => {
  assert.deepEqual(plain(N.read({ q: "ruth", offset: "50", extra: "x" }, USERS)), { q: "ruth", role: "", offset: 50 });
  assert.deepEqual(plain(N.read({ offset: "junk" }, USERS)), { q: "", role: "", offset: 0 });
  assert.deepEqual(plain(N.read({}, REVIEW)), REVIEW);
  assert.deepEqual(plain(N.read({ state: "" }, REVIEW)), { layer: "", book: "", state: "" });
  assert.deepEqual(plain(N.read({ todo: "1" }, { lang: "", todo: false })), { lang: "", todo: true });
  assert.deepEqual(plain(N.read({ todo: "0" }, { lang: "", todo: false })), { lang: "", todo: false });
});

test("an address leaves out the filters at their defaults", () => {
  assert.equal(N.build("review", REVIEW, REVIEW), "#review");
  assert.equal(N.build("review", { layer: "id", book: "ISA", state: "todo" }, REVIEW), "#review?layer=id&book=ISA");
  // An empty value that isn't the default is kept: "Every sentence".
  assert.equal(N.build("review", { layer: "en", book: "", state: "" }, REVIEW), "#review?layer=en&state=");
  assert.equal(N.build("users", { q: "a b&c", role: "", offset: 50 }, USERS), "#users?q=a%20b%26c&offset=50");
  assert.equal(N.build("articles", { lang: "fr", todo: true }, { lang: "", todo: false }), "#articles?lang=fr&todo=1");
  assert.equal(N.build("overlap", { book: "JHN", lang: "en", min: "6" }, { book: "JHN", lang: "en", min: 6 }), "#overlap");
});

test("build and parse round-trip", () => {
  const defaults = { status: "new", kind: "", lang: "", assigned: "", q: "" };
  const states = [
    { status: "done", kind: "question", lang: "fr", assigned: "me", q: "Où est-il ? 50% & more" },
    { status: "new", kind: "", lang: "", assigned: "", q: "" },
    { status: "", kind: "", lang: "", assigned: "none", q: "#1 = one" },
  ];
  for (const s of states) {
    const at = N.parse(N.build("inbox", s, defaults));
    assert.equal(at.name, "inbox");
    assert.deepEqual(plain(N.read(at.params, defaults)), s);
  }
});

const SECTIONS = [
  { title: "Dashboard", words: "dashboard" }, { title: "Coverage", words: "coverage Progress" },
  { title: "Drafting jobs", words: "jobs Progress" }, { title: "Review", words: "review Text" },
  { title: "Verse inspector", words: "verse Text" }, { title: "Fix requests", words: "fixes Text" },
  { title: "Reviewer flags", words: "flags Text" }, { title: "Reader inbox", words: "inbox Readers" },
  { title: "Users", words: "users Readers" }, { title: "Team & access", words: "team Team" },
];
const titles = (q, n) => plain(N.rank(q, SECTIONS, n).map((x) => x.title));

test("the palette ranks the start of a title, then a word, then letters in order", () => {
  assert.deepEqual(titles("rev"), ["Review", "Reviewer flags"]);
  assert.deepEqual(titles("insp")[0], "Verse inspector");
  assert.deepEqual(titles("flags")[0], "Reviewer flags");
  assert.deepEqual(titles("vi")[0], "Verse inspector");    // V... i...
  assert.deepEqual(titles("fxr")[0], "Fix requests");
  assert.deepEqual(titles("inbox")[0], "Reader inbox");
  assert.deepEqual(titles("zzz"), []);
  assert.equal(titles("").length, SECTIONS.length);
  assert.deepEqual(titles("", 3), ["Dashboard", "Coverage", "Drafting jobs"]);
  assert.equal(titles("e", 2).length, 2);
});

test("matching ignores case and accents", () => {
  assert.ok(N.score("genese", "Genèse 1:1") >= 90);
  assert.ok(N.score("JOHN", "John 3:16") >= 90);
  assert.equal(N.score("x", "John"), -1);
  assert.ok(N.score("3:16", "John 3:16") > N.score("j316", "John 3:16"));
});

test("a number goes to GitHub, an email to the accounts", () => {
  const GH = "https://github.com/o/r";
  assert.deepEqual(plain(N.direct("#123", GH, true)), [{ title: "Issue or pull request #123 on GitHub",
    href: GH + "/issues/123", external: true, kind: "github" }]);
  assert.equal(N.direct("pr 45", GH)[0].href, GH + "/pull/45");
  assert.equal(N.direct("PR#45", GH)[0].href, GH + "/pull/45");
  assert.equal(N.direct("issue 9", GH)[0].href, GH + "/issues/9");
  assert.equal(N.direct("1150", GH)[0].href, GH + "/issues/1150");
  assert.deepEqual(plain(N.direct("John 3:16", GH, true)), []);
  assert.deepEqual(plain(N.direct("ruth@example.org", GH, true)), [{ title: "Accounts matching ruth@example.org",
    href: "#users?q=ruth%40example.org", kind: "user" }]);
  assert.deepEqual(plain(N.direct("ruth@", GH, true)).length, 1);
  assert.deepEqual(plain(N.direct("ruth@example.org", GH, false)), []);   // no users area
  assert.deepEqual(plain(N.direct("@", GH, true)), []);
});

test("recent pages: newest first, one per page, at most max", () => {
  let list = [];
  list = N.remember(list, { href: "#verse/JHN.1.1", title: "John 1:1" }, 3);
  list = N.remember(list, { href: "#users?q=a", title: "Users" }, 3);
  list = N.remember(list, { href: "#users?q=ab", title: "Users" }, 3);
  assert.deepEqual(plain(list.map((x) => x.href)), ["#users?q=ab", "#verse/JHN.1.1"]);
  list = N.remember(list, { href: "#verse/JHN.1.2", title: "John 1:2" }, 3);
  list = N.remember(list, { href: "#verse/JHN.1.1", title: "John 1:1" }, 3);
  assert.deepEqual(plain(list.map((x) => x.href)), ["#verse/JHN.1.1", "#verse/JHN.1.2", "#users?q=ab"]);
  list = N.remember(list, { href: "#checks", title: "Checks" }, 3);
  assert.equal(list.length, 3);
  assert.deepEqual(N.remember([null, { nope: 1 }], { href: "#a", title: "A" }, 3).length, 1);
});
