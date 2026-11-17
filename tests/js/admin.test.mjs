// web/admin.js's page-free part, OWBAdminCore: which kept reads a change can
// affect, packing kept reads for sessionStorage, and the review queue's next
// and previous sentences.
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";

const ROOT = new URL("../../", import.meta.url).pathname;
// A browser script: with no #admin on the page, only OWBAdminCore is made.
const context = vm.createContext({ document: { getElementById: () => null } });
vm.runInContext(readFileSync(join(ROOT, "web/admin.js"), "utf-8"), context, { filename: "web/admin.js" });
const C = context.OWBAdminCore;
const A = "/api/admin/";
const plain = (x) => JSON.parse(JSON.stringify(x));
const kept = (path, keys, values = {}, body = { action: "approve" }) => keys.filter((k) => !C.stale(C.drops(path, body), k, values[k]));

const READS = [
  A + "overview/", A + "coverage/", A + "books/JHN/", A + "languages/", A + "users/?offset=0", A + "team/",
  A + "inbox/?status=new", A + "review/?layer=grc&book=&state=todo&offset=0", A + "review/flags/",
  A + "review/JHN.1.1.s1/?layer=grc", A + "review/JHN.1.2.s1/?layer=grc", A + "review/JHN.1.3.s1/?layer=grc",
  A + "verses/JHN.1.1/", A + "activity/", A + "jobs/", A + "decisions/?offset=0",
];

test("a review action forgets its sentence, the queues, flags and counts, not other sentences", () => {
  assert.deepEqual(kept(A + "review/JHN.1.1.s1/", READS), [
    A + "users/?offset=0", A + "team/", A + "inbox/?status=new",
    A + "review/JHN.1.2.s1/?layer=grc", A + "review/JHN.1.3.s1/?layer=grc",
    A + "activity/", A + "jobs/", A + "decisions/?offset=0",
  ]);
});

test("a sentence whose next was the one reviewed is forgotten too", () => {
  const values = { [A + "review/JHN.1.2.s1/?layer=grc"]: { next: "JHN.1.1.s1" },
    [A + "review/JHN.1.3.s1/?layer=grc"]: { next: "JHN.1.4.s1" } };
  const left = kept(A + "review/JHN.1.1.s1/", READS, values);
  assert.ok(!left.includes(A + "review/JHN.1.2.s1/?layer=grc"));
  assert.ok(left.includes(A + "review/JHN.1.3.s1/?layer=grc"));
});

test("a flag forgets every sentence (it can put one back in the queue)", () => {
  const left = kept(A + "review/JHN.1.1.s1/", READS, {}, { action: "flag", note: "x" });
  assert.ok(!left.some((k) => k.startsWith(A + "review/")));
  assert.ok(left.includes(A + "users/?offset=0"));
});

test("an inbox reply forgets the inbox and the overview, not the review", () => {
  const left = kept(A + "inbox/12/", READS);
  for (const gone of [A + "inbox/?status=new", A + "overview/", A + "books/JHN/", A + "activity/"]) assert.ok(!left.includes(gone), gone);
  for (const stays of [A + "review/?layer=grc&book=&state=todo&offset=0", A + "coverage/", A + "users/?offset=0"]) assert.ok(left.includes(stays), stays);
});

test("other changes forget what they touch", () => {
  assert.ok(!kept(A + "users/3/sign-out/", READS).includes(A + "users/?offset=0"));
  assert.ok(!kept(A + "users/3/", READS).includes(A + "team/"));
  assert.ok(!kept(A + "jobs/bulk/", READS).includes(A + "jobs/"));
  assert.ok(kept(A + "jobs/", READS).includes(A + "review/flags/"));
  assert.ok(!kept(A + "fixes/", READS).includes(A + "verses/JHN.1.1/"));
});

test("a change to anything unknown forgets every kept read", () => {
  assert.deepEqual(kept(A + "team/", READS), []);
  assert.deepEqual(kept(A + "team/roles/4/", READS), []);
  assert.deepEqual(kept(A + "something-new/", READS), []);
  assert.deepEqual(kept("/api/me", READS), []);
  assert.equal(C.drops("/api/me"), null);
});

test("pack keeps the newest reads that fit, and unpack only the account's", () => {
  const big = "x".repeat(400);
  const entries = [[A + "a/", 1000, { big }], [A + "b/", 3000, { big }], [A + "c/", 2000, { big }]];
  const text = C.pack(entries, 900, "me");
  assert.ok(text.length < 1000);
  const back = C.unpack(text, "me", 0);
  assert.deepEqual(plain(back.map((e) => e[0])), [A + "b/", A + "c/"]);
  assert.deepEqual(plain(C.unpack(text, "someone else", 0)), []);
  assert.deepEqual(plain(C.unpack(text, "me", 2500).map((e) => e[0])), [A + "b/"]);
  assert.deepEqual(plain(C.unpack("not json", "me", 0)), []);
  assert.deepEqual(plain(C.unpack(null, "me", 0)), []);
  assert.notEqual(C.tag("token-one"), C.tag("token-two"));
  assert.equal(C.tag("token-one"), C.tag("token-one"));
});

test("the queue's next, previous and next to review", () => {
  const rows = [{ record: "a", state: "not_reviewed" }, { record: "b", state: "approved" },
    { record: "c", state: "flagged" }, { record: "d", state: "approved" }];
  assert.equal(C.step(rows, "b", 1), "c");
  assert.equal(C.step(rows, "b", -1), "a");
  assert.equal(C.step(rows, "a", -1), null);
  assert.equal(C.step(rows, "d", 1), null);
  assert.equal(C.step(rows, "z", 1), null);
  assert.equal(C.todo(rows, "a", false), "c");
  assert.equal(C.todo(rows, "c", false), null);
  assert.equal(C.todo(rows, "c", true), undefined);   // past the rows listed: ask the API
  assert.equal(C.todo(rows, "z", false), undefined);
  assert.equal(C.todo(null, "a", false), undefined);
});
