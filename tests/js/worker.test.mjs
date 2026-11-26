// cloudflare/render.js, the Worker's copy of the build's rules, against the
// answers owb/markup.py gives (tests/markup_vectors.json). Whole pages are
// held to the build's by tests/test_worker.py.
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import * as R from "../../cloudflare/render.js";

const ROOT = new URL("../../", import.meta.url).pathname;
const VECTORS = JSON.parse(readFileSync(join(ROOT, "tests/markup_vectors.json"), "utf-8"));

test("the settings and defaults match owb/markup.py's", () => {
  assert.deepEqual(R.SETTINGS, VECTORS.settings);
  assert.deepEqual(R.DEFAULTS, VECTORS.defaults);
});

for (const c of VECTORS.cases) {
  // The Worker draws every setting at its default.
  if (Object.keys(c.settings).length) continue;
  test(c.name, () => {
    assert.equal(R.render(c.text), c.rendered);
    if (c.verses) assert.deepEqual(R.splitVerses(c.rendered), c.verses);
  });
}

for (const c of VECTORS.differences) {
  // Where the reader's copy differs from Python's, the Worker's is Python's.
  if (c.kind !== "split") continue;
  test(`as Python splits: ${c.name}`, () => {
    assert.deepEqual(R.splitVerses(c.text), c.python);
  });
}

test("plain text runs a verse's lines together", () => {
  assert.equal(R.plain("The {{divine_name:LORD|Yahweh}} is my shepherd; \\q I shall not want."),
               "The LORD is my shepherd; I shall not want.");
  // Spaces inside are kept, as build_site.plain keeps them.
  assert.equal(R.plain(" mon berger\u202f; jamais "), "mon berger\u202f; jamais");
});

test("escapes as html.escape does", () => {
  assert.equal(R.esc(`a & <b> "c" 'd'`), "a &amp; &lt;b&gt; &quot;c&quot; &#x27;d&#x27;");
  assert.equal(R.esc(`"c" & <d>`, false), `"c" &amp; &lt;d&gt;`);
});

const META = { wide: [[0x4e00, 0x9fff]], rtl: ["ar", "fa", "hbo", "he"], digits: { fa: "۰۱۲۳۴۵۶۷۸۹" } };

test("shorten keeps text that fits and cuts the rest at a sentence or a word", () => {
  assert.equal(R.shorten(META, "John 3:16: For God so loved the world."), "John 3:16: For God so loved the world.");
  const long = "One two three. " + "word ".repeat(40);
  // build_site.shorten gives the same three answers.
  assert.equal(R.shorten(META, long, 40), "One two three. word word word word…");
  assert.equal(R.shorten(META, "First sentence here. Second sentence that runs on and on and on.", 40),
               "First sentence here.");
  // A Chinese character is two wide.
  assert.equal(R.shorten(META, "神".repeat(30), 21), "神".repeat(10) + "…");
});

test("an element in a language written the other way gets its own dir", () => {
  assert.equal(R.isolateDirections(META, '<p lang="hbo">x</p><p lang="en">y</p>', "ltr"),
               '<p lang="hbo" dir="rtl">x</p><p lang="en">y</p>');
  assert.equal(R.isolateDirections(META, '<p lang="en">y</p>', "rtl"), '<p lang="en" dir="ltr">y</p>');
  assert.equal(R.isolateDirections(META, '<p lang="hbo" dir="rtl">x</p>', "ltr"), '<p lang="hbo" dir="rtl">x</p>');
});

test("numbers are in the digits of the language they are in", () => {
  assert.equal(R.localizeDigits(META, '<p>3:16 <span lang="en">3:16</span> G2316 &#8212;</p>', "fa"),
               '<p>۳:۱۶ <span lang="en">3:16</span> G2316 &#8212;</p>');
  assert.equal(R.localizeDigits(META, "<script>var a = 1;</script>12", "fa"), "<script>var a = 1;</script>۱۲");
});

test("the data scripts and a chapter page's notes read as JSON", () => {
  assert.deepEqual(R.scriptData('window.OWB_CHAPTER={"a":"<\\/b>"};\n'), { a: "</b>" });
  assert.deepEqual(R.scriptData('window.OWB_TEXTS=window.OWB_TEXTS||{};window.OWB_TEXTS["es"]={"x":1};\n'), { x: 1 });
  assert.deepEqual(R.pageNotes('<script type="application/json" id="owb-data">{"notes":{"r":{"d":{"reason":"y"}}}}</script>'),
                   { r: { d: { reason: "y" } } });
});
