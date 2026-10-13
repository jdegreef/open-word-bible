// web/markup.js (the reader's span and verse-marker rules) against the
// cases owb/markup.py is tested on, tests/markup_vectors.json.
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";

const ROOT = new URL("../../", import.meta.url).pathname;
const read = (rel) => readFileSync(join(ROOT, rel), "utf-8");

// web/markup.js is a browser script that defines one global, OWBMarkup.
const context = vm.createContext({});
vm.runInContext(read("web/markup.js"), context, { filename: "web/markup.js" });
const M = context.OWBMarkup;
const VECTORS = JSON.parse(read("tests/markup_vectors.json"));

// [[verse, text]] with verse numbers as numbers (JS keeps the marker's
// digits), in this realm's arrays so deepEqual compares them.
const split = (text) => Array.from(M.splitVerses(text), ([v, t]) => [v === null ? null : Number(v), t]);

test("the settings match owb/markup.py's", () => {
  assert.deepEqual([...M.SETTINGS], VECTORS.settings);
});

for (const c of VECTORS.cases) {
  test(c.name, () => {
    const rendered = M.render(c.text, c.settings);
    assert.equal(rendered, c.rendered);
    if (c.verses) assert.deepEqual(split(rendered), c.verses);
  });
}

for (const c of VECTORS.differences) {
  test(`known difference: ${c.name}`, () => {
    if (c.kind === "render") assert.equal(M.render(c.text, c.settings), c.js);
    else assert.deepEqual(split(c.text), c.js);
  });
}

test("the reader keeps a value for every setting", () => {
  // web/reader.js starts each setting at its default, option 0.
  const defaults = /var settings = \{([^}]*)\}/.exec(read("web/reader.js"))[1];
  for (const name of M.SETTINGS) assert.match(defaults, new RegExp(`\\b${name}: 0\\b`), name);
});

test("every setting used in content/ is one the reader knows", () => {
  const span = new RegExp(M.SPAN.source, "g"), used = new Set();
  for (const dir of readdirSync(join(ROOT, "content"), { withFileTypes: true })) {
    if (!dir.isDirectory()) continue;
    for (const file of readdirSync(join(ROOT, "content", dir.name))) {
      if (!file.endsWith(".json")) continue;
      for (const m of read(join("content", dir.name, file)).matchAll(span)) used.add(m[1]);
    }
  }
  assert.ok(used.size > 0, "no spans found in content/");
  assert.deepEqual([...used].filter((name) => !M.SETTINGS.includes(name)), []);
});
