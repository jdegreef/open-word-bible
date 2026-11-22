// web/site.js's OWBRenumbered: a browser's verses saved before the site
// used NIV numbers move as owb/renumber.py moves them (tests/test_renumber.py).
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const ROOT = new URL("../../", import.meta.url).pathname;
const SITE = readFileSync(ROOT + "web/site.js", "utf8");
const START = SITE.indexOf("window.OWBRenumbered = (function");
const CODE = SITE.slice(START, SITE.indexOf("})();", START) + 5);
const SWITCHED = 1795268400000, OLD = 100, NEW = SWITCHED + 100;
// A few rows of /renumber.json (owb/renumber.py table()).
const TABLE = { switched: SWITCHED, verses: {
  "NUM.25.19": ["NUM.26.1", "NUM.26.1"], "PSA.3.1": ["PSA.3.0", "PSA.3.0"], "PSA.3.2": ["PSA.3.1", "PSA.3.1"],
  "PSA.3.3": ["PSA.3.2", "PSA.3.2"], "MAL.3.23": ["MAL.4.5", "MAL.4.5"], "JOL.3.1": ["JOL.2.28", "JOL.2.28"] } };

async function moved(saved) {
  const store = {};
  for (const [k, v] of Object.entries(saved)) store[k] = JSON.stringify(v);
  let events = 0;
  const window = { fetch: true };
  vm.runInNewContext(CODE, {
    window, Promise, JSON,
    localStorage: { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); } },
    document: { dispatchEvent: () => { events++; } }, Event: function () {},
    fetch: () => Promise.resolve({ ok: true, json: () => TABLE }),
  });
  await window.OWBRenumbered;
  const out = {};
  for (const k of Object.keys(store)) out[k] = k === "owb.numbering" ? store[k] : JSON.parse(store[k]);
  return { out, events };
}

test("what was saved before the switch moves, and only once", async () => {
  const { out, events } = await moved({
    "owb.marks": { "NUM.25.19": { h: "yellow", n: "first", at: OLD }, "NUM.26.1": { b: true, n: "second", at: OLD + 5 },
                   "PSA.3.2": { h: "blue", at: OLD }, "PSA.4.2": { h: "pink", at: NEW } },
    "owb.notes": { "PSA.3.1-3": { n: "Morning", at: OLD }, "JHN.3.16-21": { n: "Love", at: OLD } },
    "owb.memory": { "MAL.3.23": { t: "Elijah", at: OLD } },
    "owb.place": { book: "JOL", chapter: 4, verse: "3:1", at: OLD },
  });
  assert.deepEqual(out["owb.marks"], { "NUM.26.1": { h: "yellow", n: "first\n\nsecond", b: true, at: OLD + 5 },
                                       "PSA.3.1": { h: "blue", at: OLD }, "PSA.4.2": { h: "pink", at: NEW } });
  assert.deepEqual(Object.keys(out["owb.notes"]), ["PSA.3.0-2", "JHN.3.16-21"]);
  assert.deepEqual(Object.keys(out["owb.memory"]), ["MAL.4.5"]);
  assert.deepEqual(out["owb.place"], { book: "JOL", chapter: 2, verse: "28", at: OLD });
  assert.equal(out["owb.numbering"], "niv");
  assert.equal(events, 1);
});

test("a key with no renumbered verse is left as it is", async () => {
  const { out } = await moved({ "owb.notes": { "GAL.6.16-14": { at: OLD } },
                                "owb.place": { book: "JHN", chapter: 8, verse: "7:53", at: OLD } });
  assert.deepEqual(Object.keys(out["owb.notes"]), ["GAL.6.16-14"]);
  assert.equal(out["owb.place"].verse, "7:53");
});
