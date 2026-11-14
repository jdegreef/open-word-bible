// web/memorize.js's page-free part, OWBMemoryCore: words and cues, which
// words to hide, phrases, the review schedule, verse ids and the QR code.
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";

const ROOT = new URL("../../", import.meta.url).pathname;
// A browser script: OWBMemoryCore is a global; OWBMemory is null with no page.
const context = vm.createContext({ Intl, unescape, encodeURIComponent, URLSearchParams });
vm.runInContext(readFileSync(join(ROOT, "web/memorize.js"), "utf-8"), context, { filename: "web/memorize.js" });
const C = context.OWBMemoryCore;
const VERSE = "But far be it from me to boast of anything except the cross of our Lord Jesus Christ. " +
  "Through that cross the world has been crucified to me, and I to the world.";
const plain = (x) => JSON.parse(JSON.stringify(x));

test("words keep the text whole", () => {
  for (const [text, lang] of [[VERSE, "en"], ["Dieu a tant aimé le monde, qu’il a donné", "fr"], ["神は、実に", "ja"]]) {
    const pieces = C.words(text, lang);
    assert.equal(pieces.map((p) => p.s).join(""), text);
    assert.ok(pieces.some((p) => p.w));
  }
  assert.equal(C.words(VERSE, "en").filter((p) => p.w).length, 33);
  // Without the browser's word splitter, the same words.
  assert.equal(C.words(VERSE).filter((p) => p.w).length, 33);
  assert.deepEqual(plain(C.words("God’s world.", "en").filter((p) => p.w).map((p) => p.s)), ["God’s", "world"]);
});

test("a cue is the first letter and a line", () => {
  assert.equal(C.cue("boast"), "b ____");
  assert.equal(C.cue("I"), "I");
  assert.equal(C.key("Élan"), "e");
  assert.equal(C.key("Ước"), "u");
});

test("hiding more hides the same words and more, longest first", () => {
  const pieces = C.words(VERSE, "en");
  const some = C.hidden(pieces, 0.3), more = C.hidden(pieces, 0.6), all = C.hidden(pieces, 1);
  for (const i of some) assert.ok(more.has(i));
  assert.equal(all.size, 33);
  assert.equal(C.hidden(pieces, 0).size, 0);
  assert.ok([...some].some((i) => pieces[i].s === "crucified"));
  for (const i of some) assert.ok(pieces[i].w);
});

test("phrases split at punctuation, joining the short and halving the long", () => {
  assert.deepEqual(plain(C.phrases(VERSE, "en")), [
    "But far be it from me to boast of",
    "anything except the cross of our Lord Jesus Christ.",
    "Through that cross the world has been crucified to me,",
    "and I to the world."]);
  assert.deepEqual(plain(C.phrases("Jesus wept. Then the people said, See how he loved him!", "en")),
                   ["Jesus wept. Then the people said,", "See how he loved him!"]);
  assert.equal(C.phrases("Amen.", "en").length, 1);
  assert.equal(C.phrases(VERSE, "en").join(" ").replace(/\s+/g, " "), VERSE);
});

test("the review schedule spaces out what is known and brings back what is missed", () => {
  const now = Date.UTC(2026, 10, 14, 12);
  let e = { add: now, at: now };
  assert.equal(C.status(e), "new");
  assert.ok(C.isDue(e, now));
  e = C.review(e, 2, now);
  assert.equal(e.iv, 2);
  assert.equal(e.n, 1);
  assert.equal(C.status(e), "learning");
  assert.ok(!C.isDue(e, now));
  assert.ok(C.isDue(e, now + 3 * C.DAY));
  const ivs = [];
  for (let i = 0; i < 4; i++) { e = C.review(e, 2, now); ivs.push(e.iv); }
  assert.deepEqual(ivs, [4, 9, 20, 44]);
  assert.equal(C.status(e), "known");
  assert.equal(C.review(e, 1, now).iv, 53);
  assert.equal(C.review(e, 0, now).iv, 1);
});

test("verse ids", () => {
  assert.deepEqual(plain(C.parse("GAL.6.14")), { book: "GAL", chapter: 6, from: 14, to: 14 });
  assert.deepEqual(plain(C.parse("1JN.1.9-10")), { book: "1JN", chapter: 1, from: 9, to: 10 });
  assert.equal(C.parse("GAL.6.16-14"), null);
  assert.equal(C.parse("Galatians 6:14"), null);
  assert.equal(C.makeId("GAL", 6, 14, 16), "GAL.6.14-16");
  assert.equal(C.makeId("GAL", 6, 14, 14), "GAL.6.14");
});

test("a QR code has the size and fixed patterns of its version", () => {
  const short = C.qr("https://openwordbible.org/memorize/?add=GAL.6.14&level=B");
  assert.equal(short.size, short.version * 4 + 17);
  // The three finder patterns: dark corners, a light ring, a dark centre.
  for (const [x, y] of [[0, 0], [short.size - 7, 0], [0, short.size - 7]]) {
    assert.ok(short.dark(x, y) && short.dark(x + 6, y + 6) && short.dark(x + 3, y + 3));
    assert.ok(!short.dark(x + 1, y + 1));
  }
  // Timing pattern along row 6.
  for (let x = 8; x < short.size - 8; x++) assert.equal(short.dark(x, 6), x % 2 === 0);
  assert.ok(C.qr("x".repeat(600)).version > short.version);
  assert.equal(C.qr("x".repeat(5000)), null);
});
