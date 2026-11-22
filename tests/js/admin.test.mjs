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

test("bulk review forgets every review read and the counts; its dry run forgets nothing", () => {
  const reads = [...READS, A + "review/workspace/?layer=fr", A + "assignments/"];
  const left = kept(A + "review/bulk/", reads, {}, { action: "approve", records: ["JHN.1.1.s1"] });
  assert.ok(!left.some((k) => k.startsWith(A + "review/")));
  for (const gone of [A + "overview/", A + "coverage/", A + "assignments/"]) assert.ok(!left.includes(gone), gone);
  assert.ok(left.includes(A + "users/?offset=0"));
  assert.equal(C.drops(A + "review/bulk/", {}).next, null);
  assert.deepEqual(kept(A + "review/bulk/", reads, {}, { action: "approve", chapter: "JHN.1", dry_run: true }), reads);
});

test("a single review action forgets the workspace and assignments too", () => {
  const left = kept(A + "review/JHN.1.1.s1/", [A + "review/workspace/?layer=grc", A + "assignments/", A + "team/"]);
  assert.deepEqual(left, [A + "team/"]);
});

test("an assignment change forgets assignments, the workspace and the dashboard, not the queue", () => {
  const reads = [...READS, A + "review/workspace/?layer=fr", A + "assignments/?closed=1"];
  const left = kept(A + "assignments/4/", reads);
  for (const gone of [A + "assignments/?closed=1", A + "review/workspace/?layer=fr", A + "overview/"]) assert.ok(!left.includes(gone), gone);
  assert.ok(left.includes(A + "review/?layer=grc&book=&state=todo&offset=0"));
});

test("an inbox reply forgets the inbox and the overview, not the review", () => {
  const left = kept(A + "inbox/12/", READS);
  for (const gone of [A + "inbox/?status=new", A + "overview/", A + "books/JHN/", A + "activity/"]) assert.ok(!left.includes(gone), gone);
  for (const stays of [A + "review/?layer=grc&book=&state=todo&offset=0", A + "coverage/", A + "team/"]) assert.ok(left.includes(stays), stays);
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

test("a failed answer's message: the API's detail, or the status in words when it wasn't JSON", () => {
  assert.deepEqual(plain(C.failed(500, { detail: "The server hit an error answering this.", code: "server_error", request_id: "7f3a9c21" })),
    { status: 500, code: "server_error", message: "The server hit an error answering this.", id: "7f3a9c21" });
  assert.equal(C.failed(400, { reply: ["Keep the reply under 4,000 characters."] }).message, "Keep the reply under 4,000 characters.");
  assert.match(C.failed(502, {}).message, /restarting or too busy to answer \(502\)/);
  assert.match(C.failed(500, {}).message, /\(500\)/);
});

test("a failed section says what happened, offers Try again, and gives details without the query string", () => {
  const at = new Date(Date.UTC(2026, 10, 17, 23, 41, 5));
  const timeout = Object.assign(new Error("Stopped."), { status: 503, code: "timeout", id: "7f3a9c21", method: "GET", path: "/api/admin/coverage/?q=secret" });
  assert.deepEqual(plain(C.failure(timeout, at)), {
    title: "This took too long", text: "Stopped.", retry: true,
    details: "GET /api/admin/coverage/ → 503 · timeout · request 7f3a9c21 · 2026-11-17 23:41:05 UTC" });
  assert.equal(C.failure(Object.assign(new Error("x"), { code: "offline", path: "/api/admin/" })).title, "Can't reach the server");
  assert.equal(C.failure(Object.assign(new Error("x"), { status: 403 })).retry, false);
  assert.equal(C.failure(new Error("A view's own error")).details, "");
});

test("answering a message forgets every read that shows it: the verse inspector, Languages and the reader's page", () => {
  const reads = [A + "inbox/?status=new", A + "verses/JHN.3.16/", A + "languages/", A + "users/7/", A + "coverage/", A + "review/JHN.1.1.s1/?layer=grc"];
  assert.deepEqual(kept(A + "inbox/12/", reads, {}, { reply: "Thanks" }), [A + "coverage/", A + "review/JHN.1.1.s1/?layer=grc"]);
});
