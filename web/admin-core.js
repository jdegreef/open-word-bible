// The admin's page-free parts, loaded before admin.js (see its opening comment).

// The page-free part, tested in tests/js/admin.test.mjs: which kept reads a
// change can affect, how kept reads are packed for sessionStorage, and the
// review queue's next and previous sentences.
var OWBAdminCore = (function () {
  "use strict";
  var ADMIN = "/api/admin/";

  // What a change sent to an endpoint can alter, as read paths (under
  // /api/admin/) that start so. The first rule that fits the path is used;
  // a change to anything else forgets every kept read.
  var RULES = [
    // Bulk review (staff/bulk.py): every review read and the counts; a dry
    // run (what "approve the rest of the chapter" would do) changes nothing.
    [/^review\/bulk\/$/, function (m, body) {
      return { paths: body && body.dry_run ? [] : ["review/", "overview/", "coverage/", "books/", "languages/", "health/", "verses/",
        "assignments/"] };
    }],
    [/^assignments\//, ["assignments/", "review/workspace/", "overview/", "activity/"]],
    // A review action on one sentence: its own reads, the queues and flags,
    // the counts that include review states, and the verse inspector's
    // statuses. Another sentence's reads stay, unless its "next" was this one.
    // A flag can put an approved sentence back in the queue, becoming the
    // "next" of any sentence before it, so a flag forgets every sentence;
    // so can taking a step back (undo).
    [/^review\/([^/?]+)\/$/, function (m, body) {
      return { paths: ["review/?", "review/flags/", "review/workspace/", "assignments/",
        body && (body.action === "flag" || body.action === "undo") ? "review/" : "review/" + m[1] + "/",
        "overview/", "coverage/", "books/", "languages/", "health/", "verses/"], next: decodeURIComponent(m[1]) };
    }],
    // A message also shows in the verse inspector (its card), Languages
    // (new messages by language) and the reader's account page.
    [/^inbox\//, ["inbox/", "overview/", "books/", "activity/", "engagement/", "verses/", "languages/", "users/"]],
    [/^fixes\//, ["fixes/", "overview/", "activity/", "verses/", "inbox/", "work/"]],
    [/^articles\//, ["articles/", "overview/", "activity/", "work/"]],
    [/^jobs\//, ["jobs/", "overview/", "activity/", "work/"]],
    [/^emails\//, ["emails/", "activity/"]],
    [/^users\//, ["users/", "team/", "activity/", "overview/", "engagement/", "inbox/"]]
  ];

  // drops("/api/admin/inbox/4/", body), for a change sent there: {paths:
  // [...], next: record or null}, or null for "forget everything".
  function drops(path, body) {
    if (path.indexOf(ADMIN) !== 0) return null;
    var rest = path.slice(ADMIN.length).split("#")[0];
    for (var i = 0; i < RULES.length; i++) {
      var m = RULES[i][0].exec(rest);
      if (!m) continue;
      var r = typeof RULES[i][1] === "function" ? RULES[i][1](m, body) : { paths: RULES[i][1], next: null };
      return { paths: r.paths.map(function (p) { return ADMIN + p; }), next: r.next || null };
    }
    return null;
  }

  // Whether the kept read at key (with its answer, value) goes, given drops().
  function stale(drop, key, value) {
    if (!drop) return true;
    for (var i = 0; i < drop.paths.length; i++) if (key.indexOf(drop.paths[i]) === 0) return true;
    return !!(drop.next && key.indexOf(ADMIN + "review/") === 0 && value && value.next === drop.next);
  }

  // The kept reads as one string of at most limit characters, newest first:
  // entries is [[path, at, value], ...]; the oldest are left out to fit.
  function pack(entries, limit, who) {
    var list = entries.slice().sort(function (a, b) { return b[1] - a[1]; });
    var out = [], size = 0;
    for (var i = 0; i < list.length; i++) {
      var s = JSON.stringify(list[i]);
      if (size + s.length + 1 > limit) continue;
      out.push(list[i]);
      size += s.length + 1;
    }
    return JSON.stringify({ who: who, reads: out });
  }
  // The entries pack() kept, if they are who's and newer than oldest.
  function unpack(text, who, oldest) {
    try {
      var d = JSON.parse(text || "null");
      if (!d || d.who !== who || !Array.isArray(d.reads)) return [];
      return d.reads.filter(function (e) { return Array.isArray(e) && typeof e[0] === "string" && e[1] >= oldest; });
    } catch (e) { return []; }
  }

  // A short tag for an account's token, so one account's kept reads aren't
  // shown to the next to sign in on the tab. Not a secret: a djb2 hash.
  function tag(text) {
    var n = 5381;
    for (var i = 0; i < (text || "").length; i++) n = ((n * 33) ^ text.charCodeAt(i)) >>> 0;
    return n.toString(36);
  }

  // The review queue as last listed: rows [{record, state}], more (whether
  // it goes on past them). step() is the sentence before or after record in
  // it (null at either end or if record isn't listed); todo() the next one
  // after it that isn't approved, undefined when the list is no help.
  function step(rows, record, by) {
    var i = index(rows, record);
    if (i < 0) return null;
    var r = rows[i + by];
    return r ? r.record : null;
  }
  function todo(rows, record, more) {
    var i = index(rows, record);
    if (i < 0) return undefined;
    for (var j = i + 1; j < rows.length; j++) if (rows[j].state !== "approved") return rows[j].record;
    return more ? undefined : null;
  }
  function index(rows, record) {
    for (var i = 0; i < (rows || []).length; i++) if (rows[i].record === record) return i;
    return -1;
  }

  // What a failed request's error says: {status, code, message, id}, from
  // its answer (data, {} when it wasn't JSON). The API answers JSON with a
  // request id when an admin endpoint fails (staff/permissions.py); a proxy
  // in front of it (502, 504) answers HTML.
  function failed(status, data) {
    data = data || {};
    var text = typeof data.detail === "string" ? data.detail : Array.isArray(data.detail) ? data.detail[0] : "";
    if (!text) for (var k in data) if (k !== "code" && k !== "request_id") { text = Array.isArray(data[k]) ? data[k][0] : String(data[k]); break; }
    if (!text) {
      text = status === 502 || status === 503 || status === 504
        ? "The server is restarting or too busy to answer (" + status + "). Try again in a minute."
        : "The server hit an error answering this (" + status + ").";
    }
    return { status: status, code: data.code || "", message: text, id: data.request_id || "" };
  }

  // How a failed section is shown: {title, text, details, retry}. e is an
  // Error from request() (status, code, id, method, path) or from a view.
  function failure(e, at) {
    var status = e.status || 0, code = e.code || "";
    var title = code === "timeout" ? "This took too long"
      : code === "no_answer" ? "The server didn't answer"
      : code === "offline" ? "Can't reach the server"
      : status === 403 ? "Your roles don't open this"
      : status === 404 ? "Not found"
      : status >= 500 ? "The server hit an error" : "This couldn't be loaded";
    var details = [
      e.path ? (e.method || "GET") + " " + e.path.split("?")[0] + (status ? " \u2192 " + status : "") : "",
      code, e.id ? "request " + e.id : "", at ? at.toISOString().slice(0, 19).replace("T", " ") + " UTC" : ""
    ].filter(Boolean).join(" \u00b7 ");
    return { title: title, text: e.message, details: details, retry: status !== 403 && status !== 404 };
  }

  // The Idempotency-Key for a change: the same change (method, path and
  // body) gets the same key, so a double click or a resend of something
  // already filed or emailed is refused by the API (staff/permissions.py
  // once). "" for a read, and for a preview or a test that sends nothing
  // for good (dry_run, test).
  function onceKey(method, path, body) {
    if (!method || method === "GET" || (body && (body.dry_run || body.test))) return "";
    var text = method + " " + path + " " + JSON.stringify(body === undefined ? null : body), hash = 2166136261;
    for (var i = 0; i < text.length; i++) {
      hash ^= text.charCodeAt(i);
      hash = Math.imul(hash, 16777619) >>> 0;
    }
    return "owb-" + hash.toString(36) + "-" + text.length.toString(36);
  }

  return { drops: drops, stale: stale, pack: pack, unpack: unpack, tag: tag, step: step, todo: todo,
    failed: failed, failure: failure, onceKey: onceKey };
})();

// Addresses and the command palette, also page-free (tests/js/admin-nav.test.mjs).
// A section's filters live in its address as query parameters,
// "#review?layer=grc&book=ISA", so a view can be bookmarked and shared; a
// parameter at its default is left out. The palette (Ctrl K or Cmd K)
// ranks the sections, recent items and what a query names directly.
var OWBAdminNav = (function () {
  "use strict";

  function decode(s, plus) {
    try { return decodeURIComponent(plus ? s.replace(/\+/g, " ") : s); } catch (e) { return s; }
  }

  // "#review/en?book=ISA" -> {path: "review/en", name: "review", arg: "en",
  // params: {book: "ISA"}, query: true}; query says whether there was a "?".
  function parse(hash) {
    hash = String(hash || "").replace(/^#/, "");
    var at = hash.indexOf("?");
    var path = at < 0 ? hash : hash.slice(0, at), query = at < 0 ? null : hash.slice(at + 1);
    var parts = path.split("/"), params = {};
    (query || "").split("&").forEach(function (pair) {
      if (!pair) return;
      var eq = pair.indexOf("=");
      params[decode(eq < 0 ? pair : pair.slice(0, eq), true)] = eq < 0 ? "" : decode(pair.slice(eq + 1), true);
    });
    return { path: path, name: parts[0], arg: decode(parts.slice(1).join("/")), params: params, query: query !== null };
  }

  // A section's filters from an address's params: each key of defaults, of
  // its default's type (numbers and true/false), the default when absent.
  function read(params, defaults) {
    var out = {};
    for (var k in defaults) {
      var d = defaults[k], v = params && Object.prototype.hasOwnProperty.call(params, k) ? params[k] : undefined;
      if (v === undefined) out[k] = d;
      else if (typeof d === "number") out[k] = v !== "" && isFinite(+v) ? +v : d;
      else if (typeof d === "boolean") out[k] = v === "1" || v === "true";
      else out[k] = v;
    }
    return out;
  }

  // The address of path with state's filters: each key of defaults whose
  // value differs from its default, in defaults' order.
  function build(path, state, defaults) {
    var q = [];
    for (var k in defaults) {
      var v = state[k];
      if (v === undefined || v === null || v === defaults[k]) continue;
      if (typeof defaults[k] === "number" && +v === defaults[k]) continue;
      q.push(k + "=" + (typeof v === "boolean" ? (v ? "1" : "0") : encodeURIComponent(String(v))));
    }
    return "#" + path + (q.length ? "?" + q.join("&") : "");
  }

  function fold(s) {
    return String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  function boundary(t, i) { return i === 0 || !/[a-z0-9]/.test(t.charAt(i - 1)); }

  // How well query fits text, higher is better, -1 for not at all: the
  // start of the text, then the start of a word, then the words' first
  // letters, then anywhere, then its letters in order (word starts and
  // runs count more).
  function score(query, text) {
    var q = fold(query).trim(), t = fold(text);
    if (!q) return 0;
    var i = t.indexOf(q);
    if (i === 0) return 100 - Math.min(t.length, 50) / 100;
    if (i > 0 && boundary(t, i)) return 80 - Math.min(i, 50) / 100;
    // The words' first letters ("vi" for Verse inspector).
    if (t.split(/[^a-z0-9]+/).map(function (w) { return w.charAt(0); }).join("").indexOf(q.replace(/\s+/g, "")) === 0) return 70;
    if (i > 0) return 60 - Math.min(i, 50) / 100;
    var s = 30, at = -1, prev = -2;
    for (var j = 0; j < q.length; j++) {
      var c = q.charAt(j);
      if (c === " ") continue;
      at = t.indexOf(c, at + 1);
      if (at < 0) return -1;
      s += (at === prev + 1 ? 2 : -1) + (boundary(t, at) ? 3 : 0);
      prev = at;
    }
    return Math.max(1, Math.min(s, 59));
  }

  // items ([{title, words}]) that fit query, best first (in their own order
  // for an empty query), at most limit.
  function rank(query, items, limit) {
    var scored = [];
    items.forEach(function (item, i) {
      var s = Math.max(score(query, item.title), item.words ? score(query, item.words) - 5 : -1);
      if (s >= 0) scored.push([s, i, item]);
    });
    scored.sort(function (a, b) { return b[0] - a[0] || a[1] - b[1]; });
    return scored.slice(0, limit || scored.length).map(function (x) { return x[2]; });
  }

  // What a query names outright: a GitHub issue or pull request ("#123",
  // "pr 45", "issue 9", "123"), or an account by email ("ruth@").
  // github is the repository's address; users whether accounts may be shown.
  function direct(query, github, users) {
    var q = String(query || "").trim(), out = [];
    var m = /^(?:#\s*|(pr|pull|issue|job)\s*#?\s*)?(\d{1,7})$/i.exec(q);
    if (m && github) {
      var pr = !!m[1] && /^p/i.test(m[1]);
      out.push({ title: (pr ? "Pull request #" : "Issue or pull request #") + m[2] + " on GitHub",
        href: github + (pr ? "/pull/" : "/issues/") + m[2], external: true, kind: "github" });
    }
    if (users && q.length > 1 && /^[^\s@]*@[^\s@]*$/.test(q)) {
      out.push({ title: "Accounts matching " + q, href: "#users?q=" + encodeURIComponent(q), kind: "user" });
    }
    return out;
  }

  // The recent list with item first; one entry per page (its address
  // without the query), at most max.
  function remember(list, item, max) {
    var base = item.href.split("?")[0];
    return [item].concat((list || []).filter(function (x) { return x && x.href && x.href.split("?")[0] !== base; }))
      .slice(0, max);
  }

  return { parse: parse, read: read, build: build, score: score, rank: rank, direct: direct, remember: remember };
})();
