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

test("the reader's presets are the build's, and set only real options", () => {
  const reader = read("web/reader.js");
  const order = JSON.parse(/var PRESET_ORDER = (\[[^\]]*\]);/.exec(reader)[1]);
  const built = /^PRESETS = \(([^)]*)\)/m.exec(read("scripts/build_site.py"))[1];
  assert.deepEqual(order, [...built.matchAll(/"([a-z]+)"/g)].map((m) => m[1]));
  const body = /var PRESETS = \{([\s\S]*?)\n  \};/.exec(reader)[1];
  const presets = vm.runInNewContext("({" + body + "})");
  assert.deepEqual(Object.keys(presets), order);
  for (const [name, values] of Object.entries(presets)) {
    for (const [key, value] of Object.entries(values)) {
      if (key === "level") assert.match(value, /^[LBR]$/, name);
      else {
        assert.ok(M.SETTINGS.includes(key), `${name}: ${key}`);
        assert.ok(value === 0 || value === 1, `${name}: ${key}`);
      }
    }
  }
  // Standard is the defaults.
  for (const name of M.SETTINGS) if (name in presets.standard) assert.equal(presets.standard[name], M.defaults()[name], name);
  assert.equal(presets.standard.level, "B");
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

test("joinWords keeps a Hebrew word's morphemes together and spaces words apart", () => {
  // Genesis 1:1 as MACULA Hebrew divides it: "the" + "earth" is one word in
  // two rows; "God" is a word of its own. Greek words always get a space.
  const hebrew = JSON.parse(read("data/hbo/GEN.1.json")).verses["GEN.1.1"];
  const [god, the, earth] = [hebrew[3], hebrew[9], hebrew[10]];
  assert.equal(the.after, "");
  assert.equal(the.position, earth.position);
  assert.equal(M.joinWords([the, earth]), the.text + earth.text);
  assert.equal(M.joinWords([god, the, earth]), god.text + " " + the.text + earth.text);
  const greek = JSON.parse(read("data/grc/MRK.1.json")).verses["MRK.1.1"];
  assert.equal(M.joinWords([greek[3], greek[4]]), greek[3].text + " " + greek[4].text);
  assert.equal(M.joinWords([]), "");
});
