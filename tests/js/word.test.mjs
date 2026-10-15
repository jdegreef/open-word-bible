// web/word.js's shard of a lemma against build_site.word_shard, which
// tests/word_shard_vectors.json holds (tests/test_site.py checks the
// Python side). A word page fetches the shard this names.
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";

const ROOT = new URL("../../", import.meta.url).pathname;
const read = (rel) => readFileSync(join(ROOT, rel), "utf-8");

// web/word.js is a browser script; without a document it only defines
// its one global, OWBWordShard.
const context = vm.createContext({});
vm.runInContext(read("web/word.js"), context, { filename: "web/word.js" });
const VECTORS = JSON.parse(read("tests/word_shard_vectors.json"));

test("word shards match the build's", () => {
  for (const [lemma, shard] of VECTORS.cases) {
    assert.equal(context.OWBWordShard(lemma, VECTORS.shards), shard, lemma);
  }
});
