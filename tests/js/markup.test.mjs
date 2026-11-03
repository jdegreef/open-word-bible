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

test("the defaults match owb/markup.py's", () => {
  assert.deepEqual({ ...M.DEFAULTS }, VECTORS.defaults);
  assert.equal(M.defaults().deity_pronoun, 1);
  assert.equal(M.defaults().gender, 0);
});

test("a copy of the settings saved before capitalised pronouns drops the old default", () => {
  assert.equal("deity_pronoun" in M.fromSaved({ deity_pronoun: 0, gender: 1 }), false);
  assert.equal(M.fromSaved({ deity_pronoun: 0, gender: 1 }).gender, 1);
  assert.equal(M.fromSaved({ deity_pronoun: 0, v: 2 }).deity_pronoun, 0);
  assert.equal(M.fromSaved(null).deity_pronoun, undefined);
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
  // web/reader.js starts each setting at its default: option 0, or the
  // one DEFAULTS names.
  const reader = read("web/reader.js");
  const start = /var settings = \{([^}]*)\}/.exec(reader)[1];
  const link = /var DEFAULTS = \{([^}]*)\}/.exec(reader)[1];
  for (const name of M.SETTINGS) {
    const want = M.DEFAULTS[name] || 0;
    assert.match(start, new RegExp(`\\b${name}: ${want}\\b`), name);
    if (name !== "units") assert.match(link, new RegExp(`\\b${name}: ${want}\\b`), name);
  }
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
