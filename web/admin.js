// The admin (/admin/), after Ochorus's: a rail of sections and the section
// named by the address's #hash, drawn from the API's /api/admin/ endpoints
// (backend/staff/). The rail shows only the areas the account's roles open
// (GET /api/me "admin"); the API checks every request again. All text is
// inserted with textContent. English only, as Ochorus's admin is.

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
    // "next" of any sentence before it, so a flag forgets every sentence.
    [/^review\/([^/?]+)\/$/, function (m, body) {
      return { paths: ["review/?", "review/flags/", "review/workspace/", "assignments/",
        body && body.action === "flag" ? "review/" : "review/" + m[1] + "/",
        "overview/", "coverage/", "books/", "languages/", "health/", "verses/"], next: decodeURIComponent(m[1]) };
    }],
    [/^inbox\//, ["inbox/", "overview/", "books/", "activity/", "engagement/"]],
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

  return { drops: drops, stale: stale, pack: pack, unpack: unpack, tag: tag, step: step, todo: todo,
    failed: failed, failure: failure };
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

(function () {
  "use strict";
  var root = document.getElementById("admin");
  if (!root) return;
  var API = document.querySelector('meta[name="owb-api"]').content;
  var SITE = root.getAttribute("data-site");
  var GITHUB = root.getAttribute("data-github");
  var rail = document.getElementById("admin-rail");
  var main = document.getElementById("admin-main");
  var KEY = "owb.account";

  function saved() {
    try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; }
  }

  // ---- Small helpers -------------------------------------------------

  // h("p", {class: "x"}, "text", child, ...): an element; strings become text.
  function h(tag, attrs) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") n.className = v;
      else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), v);
      else if (k === "hidden" || k === "disabled" || k === "checked" || k === "selected") n[k] = !!v;
      else if (k === "value") n.value = v;
      else n.setAttribute(k, v === true ? "" : v);
    }
    for (var i = 2; i < arguments.length; i++) add(n, arguments[i]);
    return n;
  }
  function add(n, c) {
    if (c === null || c === undefined || c === false) return;
    if (Array.isArray(c)) c.forEach(function (x) { add(n, x); });
    else n.appendChild(typeof c === "object" ? c : document.createTextNode(String(c)));
  }
  function num(n) { return (n || 0).toLocaleString("en"); }
  function pct(a, b) { return b ? Math.round((a / b) * 1000) / 10 : 0; }
  // A bare date ("2026-11-09") is that day wherever the reader is: Date
  // reads it as UTC midnight, which is the day before west of UTC.
  function date(iso, noYear) {
    if (!iso) return "—";
    var opts = { day: "numeric", month: "short" };
    if (!noYear) opts.year = "numeric";
    if (/^\d{4}-\d{2}-\d{2}$/.test(iso)) opts.timeZone = "UTC";
    return new Date(iso).toLocaleDateString("en-GB", opts);
  }
  function when(iso) {
    if (!iso) return "never";
    var s = (Date.now() - new Date(iso).getTime()) / 1000;
    if (s < 90) return "just now";
    if (s < 3600) return Math.round(s / 60) + " min ago";
    if (s < 86400) return Math.round(s / 3600) + " h ago";
    if (s < 86400 * 14) return Math.round(s / 86400) + " days ago";
    return date(iso);
  }
  function plural(n, one, many) { return num(n) + " " + (n === 1 ? one : (many || one + "s")); }
  function ghFile(path) { return GITHUB + "/blob/main/" + path; }

  // Admin reads are kept, so going back to a section (or to one fetched
  // ahead) draws at once. For a minute a kept read is simply used; after
  // that, for up to half an hour, it is drawn at once while the API is asked
  // again, and the section is drawn again if the answer differs (and nothing
  // has been typed into it meanwhile). Kept reads last the tab's session in
  // sessionStorage, so a reload draws at once too; those are always asked
  // again. A change forgets only the reads it can affect
  // (OWBAdminCore.drops). Each caller gets its own copy, as views may change
  // what they are given.
  var C = OWBAdminCore;
  var READ_MS = 60000, STALE_MS = 30 * 60000;
  var STORE = "owb.admin.reads", STORE_MAX = 1500000;
  var reads = {};       // path: {at, data: a promise, value: once answered}
  var WHO = C.tag((saved() || {}).token || "");
  (function restore() {
    var text = null;
    try { text = sessionStorage.getItem(STORE); } catch (e) { /* none */ }
    C.unpack(text, WHO, Date.now() - STALE_MS).forEach(function (e) {
      // Before this page: drawn at once, but asked again.
      reads[e[0]] = { at: Math.min(e[1], Date.now() - READ_MS - 1), data: Promise.resolve(e[2]), value: e[2] };
    });
  })();
  var storing = null;
  function store() {
    clearTimeout(storing);
    storing = setTimeout(function () {
      var entries = [];
      for (var path in reads) {
        var r = reads[path];
        if ("value" in r && path.indexOf("/api/admin/search/") !== 0) entries.push([path, r.at, r.value]);
      }
      try { sessionStorage.setItem(STORE, C.pack(entries, STORE_MAX, WHO)); } catch (e) { /* full or blocked */ }
    }, 400);
  }
  function forget(drop) {
    for (var path in reads) if (C.stale(drop, path, reads[path].value)) delete reads[path];
    store();
  }
  function forgetAll() {
    reads = {};
    try { sessionStorage.removeItem(STORE); } catch (e) { /* none */ }
  }
  function copy(data) { return JSON.parse(JSON.stringify(data)); }

  // The API, with the saved token. A 401 means the token is gone.
  // options.quiet: a read fetched ahead, which never redraws the page.
  function api(path, options) {
    options = options || {};
    var method = options.method || "GET";
    if (method !== "GET") {
      // Forgotten before (a read started meanwhile would be old) and after.
      var drop = C.drops(path, options.body);
      forget(drop);
      return request(path, options).then(function (data) { forget(drop); attention(true); return data; },
        function (e) { forget(drop); throw e; });
    }
    if (path.indexOf("/api/admin/") !== 0) return request(path, options);
    var hit = reads[path], age = hit ? Date.now() - hit.at : 0;
    if (hit && "value" in hit && age > READ_MS && age <= STALE_MS) {
      // Asked while a view is being drawn: that drawing waits on the answer.
      revalidate(path, hit, options.quiet || drawn === drawing ? 0 : drawing);
      return Promise.resolve(copy(hit.value));
    }
    if (!hit || age > READ_MS) {
      var entry = hit = reads[path] = { at: Date.now() };
      entry.data = request(path, options).then(function (data) {
        if (reads[path] === entry) { entry.value = data; store(); }
        return data;
      });
      entry.data.catch(function () { if (reads[path] === entry) delete reads[path]; });
    }
    return hit.data.then(copy);
  }
  // Asks again for a kept read drawn stale; by is the drawing that used it
  // (0 for none), drawn again if the answer differs and it is still shown.
  function revalidate(path, hit, by) {
    hit.by = hit.by || [];
    if (by) hit.by.push(by);
    if (hit.asking) return;
    hit.asking = true;
    request(path, {}).then(function (data) {
      if (reads[path] !== hit) return;   // forgotten or replaced meanwhile
      reads[path] = { at: Date.now(), data: Promise.resolve(data), value: data };
      store();
      if (JSON.stringify(data) !== JSON.stringify(hit.value) && hit.by.indexOf(drawing) >= 0) redraw();
    }, function () { hit.asking = false; });
  }
  // A request the server hasn't answered in this long is given up, so a
  // hung one can't leave the section dimmed for good.
  var REQUEST_MS = 30000;
  function request(path, options) {
    var account = saved();
    var method = options.method || "GET";
    var headers = { "Content-Type": "application/json" };
    if (account && account.token) headers.Authorization = "Bearer " + account.token;
    var abort = typeof AbortController === "function" ? new AbortController() : null;
    var timer = abort ? setTimeout(function () { abort.abort(); }, REQUEST_MS) : null;
    function fail(message, extra) {
      var e = new Error(message);
      e.method = method;
      e.path = path;
      for (var k in extra) e[k] = extra[k];
      return e;
    }
    return fetch(API + path, {
      method: method, headers: headers, signal: abort ? abort.signal : undefined,
      body: options.body ? JSON.stringify(options.body) : undefined
    }).catch(function (err) {
      clearTimeout(timer);
      if (err && err.name === "AbortError") {
        throw fail("No answer after " + REQUEST_MS / 1000 + " seconds. The server may be busy; try again in a minute.",
          { code: "no_answer" });
      }
      throw fail("Can't reach the server. Check your connection and try again.", { code: "offline" });
    }).then(function (r) {
      clearTimeout(timer);
      if (r.status === 204) return null;
      return r.json().catch(function () { return {}; }).then(function (data) {
        if (r.ok) return data;
        var f = C.failed(r.status, data);
        // A sign-in that ended while the admin was open (a long review):
        // every later request would fail too, so ask for a new one now.
        if (r.status === 401 && account && account.token) signedOut();
        throw fail(f.message, { status: f.status, code: f.code, id: f.id });
      });
    });
  }
  // A status line under a form: note(el, "Saved.") or note(el, err, true).
  function note(el, text, bad) {
    el.textContent = text instanceof Error ? text.message : text;
    el.className = "admin-note" + (bad ? " bad" : "");
  }
  function busy(button, on) {
    button.disabled = on;
    button.setAttribute("aria-busy", on ? "true" : "false");
  }

  // A load after the section is drawn (More, Older, a filter): if it fails,
  // the error goes in a line beside button, which is turned back on, rather
  // than nowhere with the button left busy. The line goes once a load works.
  function later(button, promise) {
    function line() {
      var next = button.nextElementSibling;
      return next && next.classList.contains("admin-load-error") ? next : null;
    }
    return promise.then(function (value) {
      var old = line();
      if (old) old.remove();
      return value;
    }, function (e) {
      busy(button, false);
      var shown = line();
      if (!shown) {
        shown = h("p", { class: "admin-note bad admin-load-error", role: "alert" });
        button.after(shown);
      }
      shown.textContent = e.message;
    });
  }

  // Search as you type: run(the trimmed value) a quarter second after the
  // last key. A form's own button runs it at once (with stopLive()).
  var LIVE = null;
  function live(input, run) {
    input.addEventListener("input", function () {
      clearTimeout(LIVE);
      LIVE = setTimeout(function () { typed(function () { run(input.value.trim()); }); }, 250);
    });
  }
  function stopLive() { clearTimeout(LIVE); }

  // A button that asks again before doing something hard to undo.
  function confirmButton(label, ask, run, cls) {
    var wrap = h("span", { class: "admin-confirm" });
    var first = h("button", { type: "button", class: cls || "admin-btn" }, label);
    var yes = h("button", { type: "button", class: "admin-btn danger" }, ask);
    var no = h("button", { type: "button", class: "admin-btn" }, "Cancel");
    var second = h("span", { class: "admin-confirm-ask", hidden: true }, yes, no);
    first.addEventListener("click", function () { first.hidden = true; second.hidden = false; no.focus(); });
    no.addEventListener("click", function () { first.hidden = false; second.hidden = true; first.focus(); });
    yes.addEventListener("click", function () { busy(yes, true); run(yes); });
    wrap.appendChild(first);
    wrap.appendChild(second);
    return wrap;
  }

  function head(eyebrow, title, dek) {
    return h("header", { class: "admin-head" },
      h("p", { class: "eyebrow" }, eyebrow), h("h1", null, title), dek ? h("p", { class: "admin-dek" }, dek) : null);
  }
  function tile(value, label, tone) {
    return h("div", { class: "admin-tile" + (tone ? " " + tone : "") }, h("b", null, value), h("span", null, label));
  }
  function bar(part, whole, cls) {
    var p = pct(part, whole);
    return h("span", { class: "admin-bar", title: p + "%" },
      h("i", { class: cls || "", style: "width:" + Math.min(100, p) + "%" }));
  }
  function table(headings, rows, cls) {
    return h("div", { class: "admin-scroll" },
      h("table", { class: "admin-table" + (cls ? " " + cls : "") },
        h("thead", null, h("tr", null, headings.map(function (x) {
          return typeof x === "string" ? h("th", null, x) : h("th", x[1], x[0]);
        }))),
        h("tbody", null, rows)));
  }
  function pill(text, cls) { return h("span", { class: "admin-pill " + (cls || "") }, text); }
  function empty(text) { return h("p", { class: "admin-empty" }, text); }
  function select(id, options, value) {
    return h("select", { id: id }, options.map(function (o) {
      return h("option", { value: o[0], selected: o[0] === value }, o[1]);
    }));
  }

  // ---- Sections ------------------------------------------------------

  var ME = null;
  // A message for the next drawing of a section ("Role granted."), shown in
  // its first status line.
  var FLASH = "";
  // Grouped by what people come to do: the queues that wait on someone
  // first, then checking the text, progress, publishing and people. A
  // section's group is also the eyebrow over its heading.
  var SECTIONS = [
    { id: "dashboard", label: "Dashboard", area: "overview", group: "" },
    { id: "workspace", label: "My review", area: "review", group: "Queues" },
    { id: "review", label: "Review", area: "review", group: "Queues" },
    { id: "inbox", label: "Reader inbox", area: "inbox", group: "Queues" },
    { id: "flags", label: "Reviewer flags", area: "inbox", group: "Queues" },
    { id: "assignments", label: "Review assignments", area: "inbox", group: "Queues" },
    { id: "fixes", label: "Fix requests", area: "inbox", group: "Queues" },
    { id: "jobs", label: "Drafting jobs", area: "jobs", group: "Queues" },
    { id: "work", label: "Work in progress", area: "overview", group: "Queues" },
    { id: "verse", label: "Verse inspector", area: "overview", group: "Quality" },
    { id: "decisions", label: "Uncertain decisions", area: "overview", group: "Quality" },
    { id: "terms", label: "Key terms", area: "overview", group: "Quality" },
    { id: "consistency", label: "Consistency", area: "overview", group: "Quality" },
    { id: "checks", label: "Checks", area: "overview", group: "Quality" },
    { id: "overlap", label: "Similarity", area: "overview", group: "Quality" },
    { id: "changes", label: "Changes", area: "overview", group: "Quality" },
    { id: "coverage", label: "Coverage", area: "overview", group: "Progress" },
    { id: "languages", label: "Languages", area: "overview", group: "Progress" },
    { id: "health", label: "Content health", area: "overview", group: "Progress" },
    { id: "articles", label: "Articles", area: "overview", group: "Publish" },
    { id: "export", label: "Export", area: "export", group: "Publish" },
    { id: "releases", label: "Release notes", area: "export", group: "Publish" },
    { id: "users", label: "Users", area: "users", group: "People" },
    { id: "engagement", label: "Engagement", area: "overview", group: "People" },
    { id: "team", label: "Team & access", area: "team", group: "People" },
    { id: "emails", label: "Team email", area: "email", group: "People" },
    { id: "activity", label: "Activity log", area: "team", group: "People" },
    { id: "help", label: "Help & roles", area: "", group: "People" }
  ];
  // Drill-downs reached from a section, highlighted under it.
  var PARENT = { book: "coverage", user: "users" };

  function opens(section) { return !section.area || ME.admin.indexOf(section.area) >= 0; }

  function drawRail(current) {
    var open = false;   // a new section closes the phone's list
    rail.textContent = "";
    rail.appendChild(searchBox());
    var here = SECTIONS.filter(function (s) { return s.id === current || PARENT[current] === s.id; })[0];
    // On a phone the sections fold into one button that shows where you are
    // (and, from paintBadges, how many places have something waiting).
    var toggle = h("button", { type: "button", class: "admin-rail-toggle", "aria-expanded": open ? "true" : "false",
      "aria-controls": "admin-rail-sections" },
      h("span", null, "Sections"), h("b", null, here ? here.label : ""));
    toggle.addEventListener("click", function () {
      var now = !rail.classList.contains("open");
      rail.classList.toggle("open", now);
      toggle.setAttribute("aria-expanded", now ? "true" : "false");
    });
    rail.appendChild(toggle);
    var sections = h("div", { class: "admin-rail-sections", id: "admin-rail-sections" });
    rail.appendChild(sections);
    rail.classList.toggle("open", open);
    var group = null, list = null;
    SECTIONS.filter(opens).forEach(function (s) {
      if (s.group !== group || !list) {
        group = s.group;
        if (group) sections.appendChild(h("p", { class: "admin-rail-group" }, group));
        list = h("ul");
        sections.appendChild(list);
      }
      var on = s.id === current || PARENT[current] === s.id;
      list.appendChild(h("li", null, h("a", { href: "#" + s.id, "aria-current": on ? "page" : null, "data-section": s.id }, s.label)));
    });
    rail.hidden = false;
    paintBadges();
  }

  // Each drawing gets a number, so a slow answer for a section that has
  // since been left (or a stop()) doesn't overwrite the page.
  // drawn is the drawing on the page now; shown its address.
  var drawing = 0, drawn = 0, shown = null;
  // Whether anything has been typed into the drawing on the page, which a
  // fresher answer then doesn't redraw.
  var touched = false;
  main.addEventListener("input", function () { touched = true; });
  var redrawing = null;
  function redraw() {
    clearTimeout(redrawing);
    redrawing = setTimeout(function () { if (!touched) route(); }, 0);
  }
  // The field being typed in, carried over when the same section is drawn
  // again (a search as you type, a fresher answer).
  function typingIn() {
    var a = document.activeElement;
    if (!a || !a.id || !main.contains(a) || !/^(INPUT|TEXTAREA)$/.test(a.tagName)) return null;
    var at = null;
    try { at = [a.selectionStart, a.selectionEnd]; } catch (e) { /* not a text field */ }
    return { id: a.id, tag: a.tagName, value: a.value, at: at };
  }
  function carry(was) {
    var n = document.getElementById(was.id);
    if (!n || n.tagName !== was.tag || !main.contains(n)) return;
    if (n.value !== was.value) n.value = was.value;
    n.focus();
    try { if (was.at) n.setSelectionRange(was.at[0], was.at[1]); } catch (e) { /* not a text field */ }
  }

  // The section on the page stays, dimmed, until the next one is ready; a
  // loading line replaces it only if that takes a while.
  function route() {
    var mine = ++drawing;
    var followed = NAVIGATED;
    var hash = address() || "dashboard";
    routed = location.hash;
    var at = N.parse(hash);
    var name = at.name, arg = at.arg;
    var section = SECTIONS.filter(function (s) { return s.id === (PARENT[name] || name); })[0];
    if (!section || !opens(section)) { name = "dashboard"; section = SECTIONS[0]; }
    // A filter changed on the same page isn't a move: the field being
    // typed in keeps its place. Following an address (Back, a link) is.
    var moved = followed || at.path !== (shown || "").split("?")[0];
    drawRail(name);
    attention(false);
    KEYS = null;
    main.setAttribute("aria-busy", "true");
    main.classList.add("admin-stale");
    var slow = setTimeout(function () {
      if (mine !== drawing) return;
      main.classList.remove("admin-stale");
      main.textContent = "";
      main.appendChild(head("Admin", section.label));
      main.appendChild(h("p", { class: "admin-loading" }, "Loading…"));
    }, 300);
    function show(nodes) {
      var was = moved ? null : typingIn();
      main.textContent = "";
      add(main, nodes);
      // The eyebrow over the heading names the section's group in the rail.
      var eyebrow = section.group && main.querySelector(".admin-head .eyebrow");
      if (eyebrow) eyebrow.textContent = section.group;
      drawn = mine;
      shown = hash;
      touched = false;
      if (was) carry(was);
      if (moved && main.getBoundingClientRect().top < 0) window.scrollTo(0, 0);
    }
    var draw = VIEWS[name];
    Promise.resolve().then(function () { return draw(arg); }).then(function (nodes) {
      if (mine !== drawing) return;
      show(nodes);
      var status = main.querySelector(".admin-note");
      if (FLASH && status) note(status, FLASH);
      FLASH = "";
    }).catch(function (e) {
      if (mine !== drawing) return;
      show([head("Admin", section.label), errorPanel(e)]);
    }).then(function () {
      if (mine !== drawing) return;
      clearTimeout(slow);
      main.classList.remove("admin-stale");
      main.removeAttribute("aria-busy");
      document.title = section.label + " · Admin · Open Word Bible";
      visited(name, section, hash);
    });
  }

  // ---- Addresses -------------------------------------------------------

  // Sections whose filters are kept in the address (OWBAdminNav): name:
  // {state (the section's own filter object), defaults, legacy}. legacy(arg,
  // state) takes an older address's path argument ("#inbox/mine",
  // "#review/grc", "#overlap/JHN") into state and returns what is left of
  // it; anything left means the address isn't the filtered list (a review
  // sentence) and is left alone. Registered at the end, once every view's
  // filter object exists.
  var N = OWBAdminNav;
  var FILTERS = {};
  function filtered(name, state, defaults, legacy) {
    FILTERS[name] = { state: state, defaults: defaults || copy(state), legacy: legacy || null };
  }
  // Whether the next route() follows the address (a link, back or forward,
  // the first drawing) rather than a view's own change to its filters; and
  // whether that change was typed (search as you type), which replaces the
  // history entry rather than adding one.
  var NAVIGATED = true, TYPING = false;
  function typed(run) {
    var before = drawing;
    TYPING = true;
    try { run(); } finally { TYPING = false; }
    // Filtered on the page without drawing it again (the inbox's words).
    if (drawing === before) keepAddress(false);
  }
  // The address to draw, made to match the section's filters. Following an
  // address, its parameters are the filters; a bare address ("#users", as
  // the rail links) keeps the filters last used, and the entry is marked
  // as ours, so coming back to it with Back means the defaults. After a
  // view's own change, the filters make the address: a new history entry,
  // or the same one when typed.
  function address() {
    var raw = location.hash.replace(/^#/, "");
    var nav = NAVIGATED, push = !NAVIGATED && !TYPING;
    NAVIGATED = false;
    var at = N.parse(raw), f = FILTERS[at.name];
    if (!f) return raw;
    var ours = !!(history.state && history.state.owb);
    if (nav && (at.query || ours)) assign(f.state, N.read(at.params, f.defaults));
    if (at.arg && (!f.legacy || f.legacy(at.arg, f.state))) return raw;
    var canon = N.build(at.name, f.state, f.defaults).slice(1);
    if (canon !== raw || !ours) {
      try { history[push && canon !== raw ? "pushState" : "replaceState"]({ owb: 1 }, "", "#" + canon); } catch (e) { /* none */ }
    }
    return canon;
  }
  // The address made to match the filters without drawing the page again,
  // for a view that redraws part of itself (push: a new history entry).
  function keepAddress(push) {
    var raw = location.hash.replace(/^#/, "");
    var at = N.parse(raw), f = FILTERS[at.name];
    if (!f || at.arg) return;
    var canon = N.build(at.name, f.state, f.defaults).slice(1);
    if (canon === raw) return;
    try { history[push ? "pushState" : "replaceState"]({ owb: 1 }, "", "#" + canon); } catch (e) { /* none */ }
    shown = canon;
    routed = location.hash;
  }
  function assign(target, from) { for (var k in from) target[k] = from[k]; }
  // A link, Back or Forward. Both popstate and hashchange come for most
  // moves; the second finds the address already drawn.
  var routed = null;
  function navigated() {
    if (location.hash === routed) return;
    NAVIGATED = true;
    route();
  }

  // ---- Attention counts on the rail (GET /api/admin/attention/) --------

  // Asked on each move (at most every 20 seconds) and after every change;
  // never waited on: the badges are painted when the answer comes.
  var ATTENTION = null, attentionAt = 0, attentionAsking = false, attentionAgain = false;
  function attention(force) {
    if (attentionAsking) { attentionAgain = attentionAgain || force; return; }
    if (!force && Date.now() - attentionAt < 20000) return;
    attentionAsking = true;
    attentionAt = Date.now();
    request("/api/admin/attention/", {}).then(function (d) {
      ATTENTION = d.sections || {};
      paintBadges();
    }, function () { /* the rail just shows no counts */ }).then(function () {
      attentionAsking = false;
      if (attentionAgain) { attentionAgain = false; attention(true); }
    });
  }
  function paintBadges() {
    if (!ATTENTION) return;
    rail.querySelectorAll("a[data-section]").forEach(function (a) {
      var old = a.querySelector(".admin-badge");
      if (old) old.remove();
      var c = ATTENTION[a.getAttribute("data-section")];
      a.removeAttribute("title");
      if (!c || !c.count) return;
      a.title = c.title;
      a.appendChild(h("span", { class: "admin-badge", "aria-label": c.title }, c.count > 999 ? "999+" : num(c.count)));
    });
    // The phone's Sections button: how many places have something waiting.
    var toggle = rail.querySelector(".admin-rail-toggle"), places = rail.querySelectorAll("a[data-section] .admin-badge").length;
    if (toggle) {
      var old = toggle.querySelector(".admin-badge");
      if (old) old.remove();
      if (places) toggle.appendChild(h("span", { class: "admin-badge", "aria-label": plural(places, "place") + " with something waiting" }, num(places)));
    }
  }

  // ---- Recent pages, for the palette -------------------------------------

  var RECENT_KEY = "owb.admin.recent";
  function recent() {
    try {
      var d = JSON.parse(localStorage.getItem(RECENT_KEY) || "null");
      return d && d.who === WHO && Array.isArray(d.items) ? d.items : [];
    } catch (e) { return []; }
  }
  function visited(name, section, hash) {
    if (name === "dashboard") return;
    var h1 = main.querySelector("h1");
    var title = h1 ? h1.textContent.trim() : section.label;
    var item = { href: "#" + hash, title: title, detail: title === section.label ? "" : section.label };
    try { localStorage.setItem(RECENT_KEY, JSON.stringify({ who: WHO, items: N.remember(recent(), item, 8) })); } catch (e) { /* none */ }
  }

  // A section that couldn't be drawn: what happened in plain words, Try
  // again, and details to copy into a report (the request id finds the
  // server's log line and Sentry event).
  function errorPanel(e) {
    var f = C.failure(e, new Date());
    var details = h("p", { class: "admin-error-details" }, f.details);
    var actions = h("div", { class: "admin-actions" });
    if (f.retry) {
      var again = h("button", { type: "button", class: "admin-btn primary" }, "Try again");
      again.addEventListener("click", function () { busy(again, true); route(); });
      actions.appendChild(again);
    }
    if (f.details) {
      var copyBtn = h("button", { type: "button", class: "admin-btn" }, "Copy details");
      copyBtn.addEventListener("click", function () {
        var text = f.title + ": " + f.text + "\n" + f.details;
        var done = function () { copyBtn.textContent = "Copied"; };
        var select = function () {
          var range = document.createRange();
          range.selectNodeContents(details);
          var sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(range);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, select);
        else select();
      });
      actions.appendChild(copyBtn);
    }
    return h("div", { class: "admin-error", role: "alert" },
      h("h2", null, f.title), h("p", null, f.text), actions, f.details ? details : null);
  }

  // Keys for the view on the page: KEYS = {at: its drawing, "a": fn, ...},
  // set by a view (the review sentence) and cleared by the next route().
  // Not while typing, and never "/" (the admin search's, below) or with
  // Ctrl, Cmd or Alt.
  var KEYS = null;
  window.addEventListener("keydown", function (e) {
    if (!KEYS || KEYS.at !== drawing || drawn !== drawing || e.ctrlKey || e.metaKey || e.altKey || e.defaultPrevented) return;
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    var run = e.key !== "/" && Object.prototype.hasOwnProperty.call(KEYS, e.key) ? KEYS[e.key] : null;
    if (typeof run !== "function") return;
    e.preventDefault();
    run();
  });

  var VIEWS = {};

  // Dashboard: what needs attention, then progress, then recent activity.
  VIEWS.dashboard = function () {
    return api("/api/admin/overview/").then(function (d) {
      var t = d.totals;
      var name = (ME.display_name || ME.email.split("@")[0]);
      var out = [head("Dashboard", "Welcome back, " + name,
        "Open Word Bible in numbers, from the database as the last deploy imported content/.")];
      if (d.attention.length) {
        out.push(h("section", { class: "admin-block" }, h("h2", null, "Needs attention"),
          h("div", { class: "admin-chips" }, d.attention.map(function (a) {
            return h("a", { class: "admin-chip " + a.tone, href: a.href }, h("b", null, num(a.count)), h("span", null, a.label));
          }))));
      } else {
        out.push(h("p", { class: "admin-ok" }, "Nothing needs attention."));
      }
      // People's approvals as they stand: approving wording changes no
      // sentence status, so these come from the review states, not t.statuses.
      var reviewed = d.reviewed || { meaning: 0, wording: 0 };
      out.push(h("div", { class: "admin-tiles" },
        tile(num(t.sentences), "sentences drafted"),
        tile(num(t.books_started) + " / " + t.books, "books started in English (" + t.books_drafted + " complete)"),
        tile(num(t.chapters_drafted) + " / " + num(t.chapters), "chapters drafted"),
        tile(num(reviewed.meaning), "sentences with their meaning approved by a person"),
        tile(num(reviewed.wording), "sentences with their wording approved in at least one language")));
      out.push(h("section", { class: "admin-block" }, h("h2", null, "Sentences by language"),
        h("div", { class: "admin-bars" }, d.languages.map(function (l) {
          return h("a", { class: "admin-bar-row", href: "#languages" }, h("span", null, l.name), bar(l.sentences, t.sentences),
            h("span", { class: "admin-num" }, num(l.sentences) + " · " + pct(l.sentences, t.sentences) + "%"));
        }))));
      var side = [];
      if (d.last_import) {
        var li = d.last_import;
        side.push(h("p", null, "Last content import ", h("strong", null, when(li.started_at)), ": ",
          li.error ? pill("failed", "bad") : li.finished_at ? pill("ok", "good") : pill("running", "warn"),
          " ", plural(li.files, "file") + " imported, " + plural(li.unchanged, "file") + " unchanged. ",
          h("a", { href: "#health" }, "Content health")));
      }
      if (d.activity.length) {
        side.push(h("h2", null, "Recent activity"), activityList(d.activity),
          h("p", null, h("a", { href: "#activity" }, "All activity")));
      }
      if (side.length) out.push(h("section", { class: "admin-block" }, side));
      // The pages most often opened next, fetched once the dashboard is up.
      setTimeout(function () {
        ["/api/admin/coverage/", "/api/admin/languages/"].forEach(function (path) {
          api(path).catch(function () { /* drawn with its own error if opened */ });
        });
      }, 300);
      return out;
    });
  };

  var STATE_LABEL = { none: "Not started", partial: "Partly drafted", drafted: "Drafted" };

  // Coverage: every book in every language.
  VIEWS.coverage = function () {
    return api("/api/admin/coverage/").then(function (d) {
      var langs = d.languages;
      var tab = COVERAGE.testament;
      var body = h("div");
      function draw(which) {
        body.textContent = "";
        var books = d.books.filter(function (b) { return b.testament === which; });
        var rows = books.map(function (b) {
          return h("tr", null,
            h("th", { scope: "row" }, h("a", { href: "#book/" + b.code }, b.name)),
            h("td", { class: "admin-num" }, b.chapters_drafted + " / " + b.chapters),
            h("td", { class: "admin-num" }, num(b.sentences)),
            langs.map(function (l) {
              var c = b.languages[l.code];
              return h("td", { class: "admin-cell" }, h("span", {
                class: "admin-state " + c.state,
                title: l.name + ": " + STATE_LABEL[c.state] + " (" + num(c.sentences) + " of " + num(b.sentences) + " sentences)"
              }, c.state === "none" ? "" : c.state === "drafted" ? "✓" : pct(c.sentences, b.sentences) + "%"));
            }));
        });
        var done = function (code) {
          return books.filter(function (b) { return b.languages[code].state === "drafted"; }).length;
        };
        rows.push(h("tr", { class: "admin-total" }, h("th", { scope: "row" }, "Books drafted"), h("td"), h("td"),
          langs.map(function (l) { return h("td", { class: "admin-num" }, done(l.code) + " / " + books.length); })));
        body.appendChild(table(["Book", ["Chapters", { class: "admin-num" }], ["Sentences", { class: "admin-num" }]]
          .concat(langs.map(function (l) { return [l.code, { title: l.name, class: "admin-cell" }]; })), rows, "admin-coverage"));
      }
      draw(tab);
      return [head("Progress", "Coverage", "Every book in every language. A tick is a book drafted whole; a percentage is the share of its drafted sentences in that language. Open a book for its chapters."),
        h("div", { class: "admin-toolbar" }, seg([["ot", "Old Testament"], ["nt", "New Testament"]], tab, function (v) {
          COVERAGE.testament = v; rememberTab("coverage", v); keepAddress(true); draw(v);
        }), legend()),
        ME.admin.indexOf("jobs") >= 0 ? h("p", null, h("a", { href: "#jobs" }, "Queue missing books"), " on the drafting jobs board.") : null, body];
    });
  };
  function legend() {
    return h("p", { class: "admin-legend" }, ["none", "partial", "drafted"].map(function (s) {
      return h("span", null, h("span", { class: "admin-state " + s }), STATE_LABEL[s]);
    }));
  }
  function seg(options, value, change) {
    var g = h("div", { class: "seg", role: "group" });
    options.forEach(function (o) {
      var b = h("button", { type: "button", "aria-pressed": o[0] === value ? "true" : "false" }, o[1]);
      b.addEventListener("click", function () {
        g.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        change(o[0]);
      });
      g.appendChild(b);
    });
    return g;
  }
  function sessionTab(name, fallback) {
    try { return sessionStorage.getItem("owb.admin." + name) || fallback; } catch (e) { return fallback; }
  }
  function rememberTab(name, value) {
    try { sessionStorage.setItem("owb.admin." + name, value); } catch (e) { /* none */ }
  }

  // One book, chapter by chapter.
  VIEWS.book = function (code) {
    return api("/api/admin/books/" + encodeURIComponent(code) + "/").then(function (b) {
      var langs = b.languages;
      var drafted = b.chapters.filter(function (c) { return c.sentences; }).length;
      var rows = b.chapters.map(function (c) {
        return h("tr", null,
          h("th", { scope: "row" }, c.sentences ? h("a", { href: SITE + "/" + b.code.toLowerCase() + "/" + c.chapter + "/" }, String(c.chapter)) : String(c.chapter)),
          h("td", { class: "admin-num" }, c.sentences ? num(c.sentences) : "—"),
          langs.map(function (l) {
            var n = c.languages[l.code];
            var state = !n ? "none" : n >= c.sentences ? "drafted" : "partial";
            return h("td", { class: "admin-cell" }, h("span", { class: "admin-state " + state, title: l.name + ": " + num(n) + " of " + num(c.sentences) },
              state === "drafted" ? "✓" : n ? num(n) : ""));
          }));
      });
      var uncertain = Object.keys(b.uncertain).map(function (k) {
        return h("li", null, (k === "meaning" ? "Meaning" : k) + ": " + num(b.uncertain[k]));
      });
      return [
        h("p", { class: "admin-back" }, h("a", { href: "#coverage" }, "‹ Coverage")),
        head(b.testament === "ot" ? "Old Testament" : "New Testament", b.name,
          drafted + " of " + b.chapters.length + " chapters drafted" + (b.updated ? "; last changed " + when(b.updated) : "") + "."),
        h("div", { class: "admin-toolbar" }, legend(),
          h("span", { class: "admin-actions" }, h("a", { href: "#overlap/" + b.code }, "Similarity to reference Bibles"),
            b.open_messages && ME.admin.indexOf("inbox") >= 0 ? h("a", { href: "#inbox" }, plural(b.open_messages, "open reader message")) : null)),
        table(["Chapter", ["Sentences", { class: "admin-num" }]].concat(langs.map(function (l) {
          return [l.code, { title: l.name, class: "admin-cell" }];
        })), rows, "admin-coverage"),
        h("div", { class: "admin-cols" },
          h("section", { class: "admin-block" }, h("h2", null, "Uncertain decisions"),
            uncertain.length ? h("ul", null, uncertain) : empty("None.")),
          h("section", { class: "admin-block" }, h("h2", null, "Files in content/"),
            b.files.length ? h("ul", { class: "admin-files" }, b.files.map(function (f) {
              return h("li", null, h("a", { href: ghFile(f), rel: "noopener" }, f.split("/").pop()));
            })) : empty("None imported yet.")))
      ];
    });
  };

  // Each reading language.
  VIEWS.languages = function () {
    return api("/api/admin/languages/").then(function (d) {
      var rows = d.languages.map(function (l) {
        return h("tr", null,
          h("th", { scope: "row" }, l.name, h("span", { class: "admin-sub", lang: l.code }, l.native)),
          h("td", null, bar(l.sentences, l.of), h("span", { class: "admin-num admin-sub" }, num(l.sentences) + " · " + pct(l.sentences, l.of) + "%")),
          h("td", { class: "admin-num" }, num(l.books_drafted)),
          h("td", { class: "admin-num" }, num(l.books_partial)),
          h("td", { class: "admin-num" }, l.nt_drafted + " / 27"),
          h("td", { class: "admin-num" }, num(l.uncertain)),
          h("td", { class: "admin-num" }, num(l.reviewers)),
          h("td", { class: "admin-num" }, ME.admin.indexOf("inbox") >= 0 && l.messages ? h("a", { href: "#inbox" }, num(l.messages)) : num(l.messages)),
          h("td", null, l.style_brief ? h("a", { href: ghFile(l.style_brief), rel: "noopener" }, "Brief") : "—"));
      });
      return [head("Progress", "Languages", "Each reading language against every sentence drafted so far (English leads). Uncertain counts are that language's own rendering decisions; " + num(d.meaning_uncertain) + " meaning decisions, shared by all, are uncertain too."),
        table(["Language", "Sentences", ["Books drafted", { class: "admin-num" }], ["Partly", { class: "admin-num" }],
          ["NT books", { class: "admin-num" }], ["Uncertain", { class: "admin-num" }], ["Reviewers", { class: "admin-num" }],
          ["New messages", { class: "admin-num" }], "Style brief"], rows)];
    });
  };

  // Content health: imports, texts, CI.
  VIEWS.health = function () {
    return api("/api/admin/health/").then(function (d) {
      var out = [head("Progress", "Content health", "Whether main has reached the database: CI on main, each content import, and the texts the records are checked against.")];
      var ci = d.ci;
      if (ci) {
        var failed = ci.checks.filter(function (c) { return c.conclusion && ["success", "skipped", "neutral"].indexOf(c.conclusion) < 0; });
        out.push(h("section", { class: "admin-block" }, h("h2", null, "CI on main"),
          h("p", null, h("a", { href: ci.url, rel: "noopener" }, ci.sha), " ", ci.message, " · ", when(ci.date)),
          h("ul", { class: "admin-checks" }, ci.checks.map(function (c) {
            var tone = c.status !== "completed" ? "warn" : failed.indexOf(c) >= 0 ? "bad" : "good";
            return h("li", null, pill(c.status !== "completed" ? c.status.replace("_", " ") : c.conclusion, tone), " ",
              h("a", { href: c.url, rel: "noopener" }, c.name));
          }))));
      } else {
        out.push(h("p", { class: "notice" }, "GitHub couldn't be reached, so CI on main isn't shown."));
      }
      out.push(h("section", { class: "admin-block" }, h("h2", null, "Alerts"),
        h("p", { class: "admin-sub" }, "Super admins are emailed once about each of these, and again only when it changes."),
        d.alerts.length ? h("ul", null, d.alerts.map(function (a) {
          return h("li", null, h("a", { href: a.href }, a.title), " · ",
            a.emailed_at ? "emailed " + when(a.emailed_at) : pill("not emailed yet", "warn"));
        })) : h("p", { class: "admin-ok" }, "Nothing has broken.")));
      out.push(h("div", { class: "admin-tiles" },
        tile(num(d.sentences), "sentences in the database"),
        tile(num(d.content_files), "content files imported"),
        tile(when(d.last_sentence_update), "last sentence change")));
      out.push(h("section", { class: "admin-block" }, h("h2", null, "Content imports"),
        d.imports.length ? table(["Started", "Result", ["Files", { class: "admin-num" }], ["Records", { class: "admin-num" }],
          ["Unchanged", { class: "admin-num" }], "Notes"], d.imports.map(function (r) {
          return h("tr", null, h("td", null, when(r.started_at)),
            h("td", null, r.error ? pill("failed", "bad") : r.ok ? pill("ok", "good") : pill("running or stopped", "warn")),
            h("td", { class: "admin-num" }, num(r.files)), h("td", { class: "admin-num" }, num(r.records)),
            h("td", { class: "admin-num" }, num(r.unchanged)),
            h("td", { class: "admin-wrap" }, r.error ? h("code", null, r.error) : "", r.skipped.map(function (s) { return h("div", { class: "admin-sub" }, s); }),
              r.everything ? "Every file (--all)" : ""));
        })) : empty("No imports recorded yet. The next deploy records one.")));
      out.push(h("section", { class: "admin-block" }, h("h2", null, "Texts"),
        table(["Edition", "Kind", "Language", ["Verses", { class: "admin-num" }], "Source", "Loaded"], d.editions.map(function (e) {
          return h("tr", null, h("td", null, e.name, h("span", { class: "admin-sub" }, e.code)), h("td", null, e.kind),
            h("td", null, e.language), h("td", { class: "admin-num" }, num(e.verses)), h("td", null, h("code", null, e.source_commit)),
            h("td", null, date(e.imported_at)));
        }))));
      return out;
    });
  };

  // Engagement: what accounts keep, in totals.
  VIEWS.engagement = function () {
    return api("/api/admin/engagement/").then(function (d) {
      var most = Math.max.apply(null, d.signups.map(function (w) { return w.accounts; }).concat([1]));
      function ranked(rows, label, value) {
        if (!rows.length) return empty("Nothing yet.");
        var top = rows[0][value] || 1;
        return h("div", { class: "admin-bars" }, rows.map(function (r) {
          return h("div", { class: "admin-bar-row" }, h("span", null, r[label]), bar(r[value], top), h("span", { class: "admin-num" }, num(r[value])));
        }));
      }
      return [head("Readers", "Engagement", "Counted from what accounts already keep: sign-ups, sign-ins, bookmarks, highlights and reading places. The site records nothing about reading (the privacy page promises no analytics), so readers without an account aren't counted."),
        h("div", { class: "admin-tiles" },
          tile(num(d.accounts), "accounts"),
          tile(num(d.active_7), "signed in, last 7 days"),
          tile(num(d.active_30), "signed in, last 30 days"),
          tile(num(d.devices_30), "devices used, last 30 days"),
          tile(num(d.marks.bookmarks), "bookmarks"),
          tile(num(d.marks.highlights), "highlights"),
          tile(num(d.messages), "reader messages")),
        h("section", { class: "admin-block" }, h("h2", null, "New accounts by week"),
          d.signups.length ? h("div", { class: "admin-columns", role: "img", "aria-label": "New accounts per week for 12 weeks" },
            d.signups.map(function (w) {
              return h("div", { class: "admin-column", title: "Week of " + date(w.week) + ": " + w.accounts },
                h("span", { class: "admin-num" }, num(w.accounts)),
                h("i", { style: "height:" + Math.max(2, (w.accounts / most) * 100) + "%" }),
                h("span", { class: "admin-sub" }, date(w.week, true)));
            })) : empty("No new accounts in the last 12 weeks.")),
        h("div", { class: "admin-cols" },
          h("section", { class: "admin-block" }, h("h2", null, "Saved verses by book"), ranked(d.marks_by_book, "name", "marks")),
          h("section", { class: "admin-block" }, h("h2", null, "Where readers are reading"), ranked(d.reading_places, "name", "readers")),
          h("section", { class: "admin-block" }, h("h2", null, "Saved verses by language"), ranked(d.marks_by_language, "lang", "n")))];
    });
  };

  // Reader inbox.
  // #inbox/mine opens the messages assigned to you (the dashboard links it).
  var INBOX = { status: "new", kind: "", lang: "", assigned: "", q: "" };
  VIEWS.inbox = function (arg) {
    if (arg === "mine") INBOX.assigned = "me";
    var q = "?status=" + INBOX.status + (INBOX.kind ? "&kind=" + INBOX.kind : "") + (INBOX.lang ? "&lang=" + INBOX.lang : "") +
      (INBOX.assigned ? "&assigned=" + INBOX.assigned : "") + (INBOX.q ? "&q=" + encodeURIComponent(INBOX.q) : "");
    return api("/api/admin/inbox/" + q).then(function (d) {
      var tabs = seg([["new", "New (" + d.counts.new + ")"], ["answered", "Answered (" + d.counts.answered + ")"],
        ["done", "Done (" + d.counts.done + ")"], ["declined", "Declined (" + d.counts.declined + ")"]], INBOX.status, function (v) {
        INBOX.status = v; route();
      });
      var kind = select("inbox-kind", [["", "Suggestions and questions"], ["suggestion", "Suggestions"], ["question", "Questions"]], INBOX.kind);
      kind.addEventListener("change", function () { INBOX.kind = kind.value; route(); });
      kind.setAttribute("aria-label", "Kind");
      var whose = seg([["me", "Mine"], ["none", "Unassigned"], ["", "All"]], INBOX.assigned, function (v) {
        INBOX.assigned = v; location.hash === "#inbox" ? route() : (location.hash = "#inbox");
      });
      // Words to find in every message, not only the page drawn: the API
      // searches (q=), as you type. The tabs' counts are then of what it found.
      var search = h("input", { type: "search", id: "inbox-q", value: INBOX.q, placeholder: "Words, a verse or a reader", "aria-label": "Find in the reader inbox" });
      var found = h("span", { class: "admin-sub", role: "status" }, INBOX.q ? plural(d.total, "message") + " found" : "");
      var form = h("form", { class: "admin-toolbar", role: "search" }, search, h("button", { type: "submit", class: "admin-btn" }, "Find"), found);
      function find(v) { if (v !== INBOX.q) { INBOX.q = v; route(); } }
      form.addEventListener("submit", function (e) { e.preventDefault(); stopLive(); find(search.value.trim()); });
      live(search, find);
      return [head("Readers", "Reader inbox", "Suggestions and questions readers send from a verse. New messages come oldest first; assign one to say you're dealing with it. A reply is emailed to the reader once; mark a message done when it's dealt with."),
        h("div", { class: "admin-toolbar" }, tabs, whose, kind), form,
        d.messages.length ? h("div", { class: "admin-messages" }, d.messages.map(function (m) { return messageCard(m, d.team); })) : empty(INBOX.q ? "No messages here have those words." : "No messages here."),
        d.total > d.messages.length ? h("p", { class: "admin-sub" }, "Showing " + (INBOX.status === "new" ? "the longest waiting " : "the newest ") + d.messages.length + " of " + num(d.total) + ".") : null];
    });
  };
  // team: whom the message can be assigned to, from the answer that listed
  // it (the inbox's or the verse inspector's).
  function messageCard(m, team) {
    var card = h("article", { class: "admin-message" });
    var draft = "";   // the reply being written, kept when the card is drawn again
    function draw() {
      card.textContent = "";
      add(card, [
        h("header", null, pill(m.kind === "question" ? "Question" : "Suggestion", m.kind === "question" ? "info" : ""),
          " ", h("a", { href: m.url, rel: "noopener" }, m.verse_label), " · ", m.language + (m.level ? " " + m.level : ""),
          h("span", { class: "admin-sub" }, " from " + (m.from.name ? m.from.name + " <" + m.from.email + ">" : m.from.email) + ", " + when(m.created_at)),
          m.status === "new" ? [" ", pill(m.age_days ? plural(m.age_days, "day") + " waiting" : "today", m.waiting ? "warn" : "")] : null),
        h("blockquote", null, m.text),
        h("p", { class: "admin-actions" }, h("a", { href: "#verse/" + m.verse }, "Inspect " + m.verse_label),
          (function () {
            var b = h("button", { type: "button", class: "admin-link" }, "Request a fix");
            b.addEventListener("click", function () { FIX_FROM = m; location.hash = "#verse/" + m.verse; });
            return b;
          })())]);
      if (m.fixed_at) {
        card.appendChild(h("p", null, pill("Led to a change", "good"), " ", h("a", { href: m.fix_url, rel: "noopener" }, "the pull request"),
          h("span", { class: "admin-sub" }, " \u00b7 the reader was told " + when(m.fixed_at))));
      }
      if (m.reply) {
        card.appendChild(h("div", { class: "admin-reply" }, h("p", { class: "admin-sub" }, "Answered by " + m.replied_by + ", " + when(m.replied_at)), h("p", null, m.reply)));
      }
      var status = h("p", { class: "admin-note", role: "status" });
      card.appendChild(assignee(status));
      if (!m.reply) {
        var text = h("textarea", { rows: 3, id: "reply-" + m.id, maxlength: 4000, placeholder: "Reply to the reader (emailed to them)",
          value: draft, oninput: function () { draft = text.value; } });
        var saved = select("saved-" + m.id, [["", "Start from a saved reply…"]].concat(m.replies.map(function (r) { return [r.key, r.label]; })), "");
        saved.setAttribute("aria-label", "Saved replies");
        saved.addEventListener("change", function () {
          var r = m.replies.filter(function (x) { return x.key === saved.value; })[0];
          if (r) { text.value = draft = r.text; text.focus(); }
          saved.value = "";
        });
        var send = h("button", { type: "button", class: "admin-btn primary" }, "Send reply");
        send.addEventListener("click", function () {
          if (!text.value.trim()) { note(status, "Write a reply first.", true); return; }
          busy(send, true);
          update({ reply: text.value }).catch(function (e) { busy(send, false); note(status, e, true); });
        });
        card.appendChild(h("label", { class: "admin-label", for: "reply-" + m.id }, "Reply"));
        card.appendChild(saved);
        card.appendChild(text);
        card.appendChild(h("div", { class: "admin-actions" }, send, statusButtons()));
      } else {
        card.appendChild(h("div", { class: "admin-actions" }, statusButtons()));
      }
      var noteField = h("input", { id: "note-" + m.id, value: m.note, maxlength: 4000, placeholder: "A note for editors (not sent)" });
      noteField.addEventListener("change", function () {
        update({ note: noteField.value }).then(function () { note(status, "Note saved."); }, function (e) { note(status, e, true); });
      });
      card.appendChild(h("label", { class: "admin-label", for: "note-" + m.id }, "Editors' note"));
      card.appendChild(noteField);
      card.appendChild(status);
      function assignee(status) {
        var pick = select("assign-" + m.id, [["", "Nobody"]].concat((team || []).map(function (u) {
          return [String(u.id), (u.name ? u.name + " (" + u.email + ")" : u.email) + (u.email === ME.email ? " — you" : "")];
        })), m.assigned_to ? String(m.assigned_to.id) : "");
        pick.addEventListener("change", function () {
          update({ assigned_to: pick.value ? Number(pick.value) : null }).catch(function (e) {
            pick.value = m.assigned_to ? String(m.assigned_to.id) : "";   // still assigned as before
            note(status, e, true);
          });
        });
        return h("p", { class: "admin-actions" }, h("label", { for: "assign-" + m.id }, "Assigned to "), pick,
          m.assigned_to && m.assigned_at ? h("span", { class: "admin-sub" }, " since " + when(m.assigned_at)) : null);
      }
      function statusButtons() {
        return [["done", "Mark done"], ["declined", "Decline"], ["new", "Back to new"]]
          .filter(function (s) { return s[0] !== m.status; }).map(function (s) {
            var b = h("button", { type: "button", class: "admin-btn" }, s[1]);
            b.addEventListener("click", function () { busy(b, true); update({ status: s[0] }).catch(function (e) { busy(b, false); note(status, e, true); }); });
            return b;
          });
      }
    }
    function update(body) {
      return api("/api/admin/inbox/" + m.id + "/", { method: "PATCH", body: body }).then(function (fresh) { m = fresh; draw(); });
    }
    draw();
    return card;
  }

  // ---- The verse inspector and fix requests ----------------------------

  // The reader message a fix request comes from, set by its "Request a fix"
  // button and used by the next verse drawn.
  var FIX_FROM = null;
  var LEVEL_NAMES = { L: "Literal", B: "Balanced", R: "Readable" };

  // A rendering as text, with each reader setting's default shown and its
  // alternative in the tooltip, verse numbers raised and poetry breaks as " / ".
  function rendering(text) {
    var span = h("span");
    var re = /\{\{([a-z_]+):([^{}|]*)\|([^{}]*)\}\}|\\v (\d+) ?|\\q ?/g, last = 0, m;
    while ((m = re.exec(text))) {
      add(span, text.slice(last, m.index));
      if (m[1]) add(span, h("span", { class: "admin-setting", title: m[1].replace(/_/g, " ") + ": " + m[3] }, m[2]));
      else if (m[4]) add(span, h("sup", null, m[4]));
      else add(span, " / ");
      last = re.lastIndex;
    }
    add(span, text.slice(last));
    return span;
  }

  function verseSearch(value) {
    var input = h("input", { type: "search", id: "verse-q", value: value || "", placeholder: "John 1:1, jn 3 16, Juan 3:16 or JHN.1.1",
      "aria-label": "Verse" });
    var status = h("span", { class: "admin-note", role: "status" });
    var form = h("form", { class: "admin-toolbar", role: "search" }, input, h("button", { type: "submit", class: "admin-btn" }, "Inspect"), status);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      api("/api/admin/verses/?q=" + encodeURIComponent(input.value)).then(function (r) {
        location.hash = "#verse/" + r.verse;
      }, function (err) { note(status, err, true); });
    });
    return form;
  }

  VIEWS.verse = function (vid) {
    if (!vid) {
      return [head("Text", "Verse inspector", "Any verse's sentence records whole: the source words, every language at every level, every decision with its reason, and the file it lives in."),
        verseSearch("")];
    }
    return api("/api/admin/verses/" + encodeURIComponent(vid) + "/").then(function (d) {
      var names = {};
      d.languages.forEach(function (l) { names[l.code] = l.name; });
      var from = FIX_FROM && FIX_FROM.verse === d.verse ? FIX_FROM : null;
      FIX_FROM = null;
      var nav = h("div", { class: "admin-actions" },
        d.neighbours[0] ? h("a", { href: "#verse/" + d.neighbours[0] }, "\u2039 " + d.neighbours[0]) : null,
        d.neighbours[1] ? h("a", { href: "#verse/" + d.neighbours[1] }, d.neighbours[1] + " \u203a") : null,
        h("a", { href: d.url, rel: "noopener" }, "Read it on the site"));
      var out = [head("Verse inspector", d.label, d.records.length ? plural(d.records.length, "sentence") + " hold this verse" +
        (d.updated ? "; last changed " + when(d.updated) : "") + "." : "No sentence holds this verse yet."), verseSearch(d.label), nav];
      if (from) {
        out.push(h("div", { class: "admin-reply" }, h("p", { class: "admin-sub" }, "Requesting a fix for " + (from.from.name || from.from.email) +
          "'s " + from.kind + " (" + from.language + "):"), h("p", null, from.text)));
      }
      d.records.forEach(function (r) { out.push(recordCard(r, d, names, from)); });
      if (d.records.length) out.push(approvalHistory(d.verse));
      if (d.messages && d.messages.length) {
        out.push(h("section", { class: "admin-block" }, h("h2", null, "Reader messages"),
          h("div", { class: "admin-messages" }, d.messages.map(function (m) { return messageCard(m, d.team); }))));
      }
      if (d.fixes.length) {
        out.push(h("section", { class: "admin-block" }, h("h2", null, "Fix requests"), h("ul", { class: "admin-feed" }, d.fixes.map(function (f) {
          return h("li", null, h("time", { datetime: f.at }, when(f.at)), h("span", null, h("a", { href: f.url, rel: "noopener" }, "#" + f.number),
            " " + (names[f.language] || f.language) + ", by " + f.by));
        }))));
      }
      return out;
    });
  };

  function recordCard(r, d, names, from) {
    var source = r.source.tokens.map(function (t) { return d.words[t]; });
    var words = source.every(Boolean) && source.length ? h("p", { class: "admin-source", lang: r.source.language, dir: r.source.language === "hbo" ? "rtl" : null },
      source.map(function (w) { return [h("span", { title: [w.lemma, w.gloss, w.morph].filter(Boolean).join(" \u00b7 ") }, w.text), " "]; }))
      : h("p", { class: "admin-source", lang: r.source.language, dir: r.source.language === "hbo" ? "rtl" : null }, r.source.text);
    var langs = Object.keys(r.renderings);
    // Each rendering's "Request a fix" opens the record's fix request form
    // with its language and level chosen.
    var fix = ME.admin.indexOf("inbox") >= 0 ? fixForm(r, langs, names, from, d.verse) : null;
    var rows = langs.map(function (code) {
      return h("tr", null, h("th", { scope: "row" }, names[code] || code), ["L", "B", "R"].map(function (lv) {
        var t = r.renderings[code][lv];
        return h("td", { class: "admin-wrap", lang: code }, t ? rendering(t) : "\u2014",
          t && fix ? h("button", { type: "button", class: "admin-link admin-fix-this", lang: "en",
            "aria-label": "Request a fix to the " + (names[code] || code) + " " + LEVEL_NAMES[lv] + " in " + r.id,
            onclick: function () { fix.prefill(code, lv); } }, "Request a fix") : null);
      }));
    });
    var meaning = r.decisions.filter(function (x) { return x.layer === "meaning"; });
    var byLang = {};
    r.decisions.filter(function (x) { return x.layer !== "meaning"; }).forEach(function (x) { (byLang[x.language] = byLang[x.language] || []).push(x); });
    var file = d.files[r.id];
    var card = h("section", { class: "admin-block admin-record" },
      h("header", { class: "admin-toolbar" }, h("h2", null, r.id), h("span", null, pill(r.status === "ai_draft" ? "AI draft" : r.status.replace(/_/g, " "), r.status === "ai_draft" ? "" : "good"),
        " ", file ? h("a", { href: ghFile(file), rel: "noopener" }, file.split("/").pop()) : null)),
      words, h("p", { class: "admin-gloss" }, "Literal gloss: " + r.literal_gloss),
      table(["Language", "Literal", "Balanced", "Readable"], rows, "admin-renderings"),
      meaning.length ? [h("h3", { class: "admin-h3" }, "Meaning decisions"), h("div", { class: "admin-decisions" }, meaning.map(decision))] : null,
      langs.filter(function (c) { return byLang[c]; }).map(function (c) {
        return [h("h3", { class: "admin-h3" }, (names[c] || c) + " decisions"), h("div", { class: "admin-decisions" }, byLang[c].map(decision))];
      }));
    if (fix) {
      card.appendChild(fix);
      card.appendChild(linksEditor(r, d, names));
    }
    return card;
  }

  // Word links (a record's alignments) for one language and level: the
  // source words above, the rendering below, and the links between them.
  // A reviewer picks source words, selects their words in the rendering and
  // links them; the result is filed as a fix request carrying the links in
  // scripts/align.py's spec form, which a Claude session applies and
  // validates. Nothing here edits content/ or marks anything reviewed.
  var UNSPACED = /[々぀-ヿ㐀-䶿一-鿿豈-﫿ｦ-ﾟ]/;
  var WORDISH = /[\p{L}\p{N}]/u;
  function joined(a, b) { return WORDISH.test(a) && WORDISH.test(b) && !UNSPACED.test(a) && !UNSPACED.test(b); }
  // owb/markup.py alignment_ranges, for showing links already made: each
  // span found after the one before, as a whole word.
  function linkRanges(text, spans) {
    var at = 0, out = [];
    spans.forEach(function (span) {
      var start = text.indexOf(span, at);
      while (start >= 0 && !wholeAt(text, start, start + span.length)) start = text.indexOf(span, start + 1);
      out.push(start < 0 ? null : [start, start + span.length]);
      if (start >= 0) at = start + span.length;
    });
    return out;
  }
  function wholeAt(text, s, e) {
    return !(s > 0 && joined(text[s - 1], text[s])) && !(e < text.length && joined(text[e], text[e - 1]));
  }

  function linksEditor(r, d, names) {
    var langs = Object.keys(r.renderings);
    var box = h("div", { class: "admin-links", hidden: true });
    var toggle = h("button", { type: "button", class: "admin-btn" }, "Edit word links");
    toggle.addEventListener("click", function () { box.hidden = !box.hidden; if (!box.hidden) draw(); });
    var lang = select("links-lang-" + r.id, langs.map(function (c) { return [c, names[c] || c]; }), langs.indexOf("ja") >= 0 ? "ja" : langs[0]);
    var level = select("links-level-" + r.id, [["L", "Literal"], ["B", "Balanced"], ["R", "Readable"]], "B");
    var tokens = h("p", { class: "admin-source admin-link-tokens", lang: r.source.language, dir: r.source.language === "hbo" ? "rtl" : null });
    var textBox = h("p", { class: "admin-link-text" });
    var list = h("ol", { class: "admin-link-list" });
    var status = h("p", { class: "admin-note", role: "status" });
    var reason = h("textarea", { id: "links-reason-" + r.id, rows: 2, maxlength: 4000, placeholder: "Why (optional): what was wrong or missing" });
    var send = h("button", { type: "submit", class: "admin-btn primary" }, "File word-links request");
    var linkBtn = h("button", { type: "button", class: "admin-btn" }, "Link selection");
    var picked = [];   // token numbers, 1-based
    var links = [];    // {start, end, tokens: [numbers]}
    var text = "";

    function load() {
      text = (r.renderings[lang.value] || {})[level.value] || "";
      var mine = (r.alignments || []).filter(function (a) { return a.language === lang.value && a.level === level.value; });
      var ranges = linkRanges(text, mine.map(function (a) { return a.target_span; }));
      links = [];
      mine.forEach(function (a, i) {
        if (!ranges[i]) return;
        links.push({ start: ranges[i][0], end: ranges[i][1], tokens: a.tokens.map(function (t) { return r.source.tokens.indexOf(t) + 1; }) });
      });
      picked = [];
      draw();
    }
    function wordOf(n) { var w = d.words[r.source.tokens[n - 1]]; return w ? w.text : "#" + n; }
    function draw() {
      tokens.textContent = "";
      var used = {};
      links.forEach(function (l) { l.tokens.forEach(function (n) { used[n] = true; }); });
      r.source.tokens.forEach(function (t, i) {
        var n = i + 1, w = d.words[t] || {};
        var b = h("button", { type: "button", class: "admin-link-token" + (picked.indexOf(n) >= 0 ? " on" : "") + (used[n] ? " used" : ""),
          title: n + " · " + [w.lemma, w.gloss].filter(Boolean).join(" · "), "aria-pressed": picked.indexOf(n) >= 0 ? "true" : "false" },
          h("span", null, w.text || "#" + n), h("small", null, String(n)));
        b.addEventListener("click", function () {
          var k = picked.indexOf(n);
          if (k >= 0) picked.splice(k, 1); else picked.push(n);
          picked.sort(function (a, b2) { return a - b2; });
          draw();
        });
        add(tokens, [b, " "]);
      });
      textBox.textContent = "";
      textBox.lang = lang.value;
      var at = 0;
      links.slice().sort(function (a, b) { return a.start - b.start; }).forEach(function (l) {
        add(textBox, text.slice(at, l.start));
        var lit = l.tokens.some(function (n) { return picked.indexOf(n) >= 0; });
        add(textBox, h("mark", { class: "admin-link-span" + (lit ? " lit" : ""), title: l.tokens.map(wordOf).join(" ") }, text.slice(l.start, l.end)));
        at = l.end;
      });
      add(textBox, text.slice(at));
      list.textContent = "";
      links.sort(function (a, b) { return a.start - b.start; }).forEach(function (l, i) {
        var del = h("button", { type: "button", class: "admin-btn small" }, "Remove");
        del.addEventListener("click", function () { links.splice(i, 1); draw(); });
        add(list, h("li", null, h("span", { lang: lang.value }, text.slice(l.start, l.end)), " ← ",
          h("span", { lang: r.source.language }, l.tokens.map(wordOf).join(" ")), " ", h("code", null, l.tokens.join(",")), " ", del));
      });
      var covered = {};
      links.forEach(function (l) { l.tokens.forEach(function (n) { covered[n] = true; }); });
      status.textContent = links.length + " links; " + Object.keys(covered).length + " of " + r.source.tokens.length +
        " source words linked." + (picked.length ? " Selected: " + picked.join(", ") + "." : "");
      status.className = "admin-note";
    }
    // The selection inside the rendering, as offsets into its text.
    function selected() {
      var sel = window.getSelection();
      if (!sel.rangeCount || sel.isCollapsed) return null;
      var range = sel.getRangeAt(0);
      if (!textBox.contains(range.startContainer) || !textBox.contains(range.endContainer)) return null;
      function offset(node, off) {
        var pre = document.createRange();
        pre.selectNodeContents(textBox);
        pre.setEnd(node, off);
        return pre.toString().length;
      }
      var s = offset(range.startContainer, range.startOffset), e = offset(range.endContainer, range.endOffset);
      while (s < e && /\s/.test(text[s])) s++;
      while (e > s && /\s/.test(text[e - 1])) e--;
      return e > s ? [s, e] : null;
    }
    linkBtn.addEventListener("click", function () {
      var span = selected();
      if (!picked.length) { note(status, "Pick the source words first.", true); return; }
      if (!span) { note(status, "Select the words in the rendering to link them to.", true); return; }
      var s = span[0], e = span[1], piece = text.slice(s, e);
      if (/\\v \d|\\q/.test(piece)) { note(status, "A link can't hold a verse or line marker.", true); return; }
      var setting = /\{\{[^{}]*\}\}/g, m;
      while ((m = setting.exec(text))) {
        var a = m.index, b = a + m[0].length;
        if ((a < s && s < b) || (a < e && e < b)) { note(status, "Take a reader setting {{...}} whole, or leave it out.", true); return; }
      }
      if (!wholeAt(text, s, e)) { note(status, "Select whole words.", true); return; }
      if (links.some(function (l) { return s < l.end && l.start < e; })) { note(status, "That overlaps a link; remove it first.", true); return; }
      links.push({ start: s, end: e, tokens: picked.slice() });
      picked = [];
      window.getSelection().removeAllRanges();
      draw();
    });
    function spec() {
      return r.id + ": " + links.slice().sort(function (a, b) { return a.start - b.start; })
        .map(function (l) { return text.slice(l.start, l.end) + "=" + l.tokens.join(","); }).join(" | ");
    }
    [lang, level].forEach(function (s) { s.addEventListener("change", load); });
    var form = h("form", { class: "admin-form stacked" },
      h("div", { class: "admin-toolbar" }, h("label", { class: "admin-field", for: lang.id }, "Language", lang),
        h("label", { class: "admin-field", for: level.id }, "Level", level)),
      h("p", { class: "admin-sub" }, "Pick source words, select what they became in the text, then Link selection. Links show highlighted; picking a word lights its links."),
      tokens, textBox, h("div", { class: "admin-actions" }, linkBtn), list,
      h("label", { class: "admin-field", for: reason.id }, "Reason", reason),
      h("p", { class: "admin-sub" }, "Filed as a fix request with the links in scripts/align.py's form. A Claude session applies and validates them in a pull request; the sentence stays an AI draft."),
      send, status);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!links.length) { note(status, "Make at least one link.", true); return; }
      busy(send, true);
      api("/api/admin/fixes/", { method: "POST", body: { record: r.id, verse: location.hash.split("/")[1], language: lang.value,
        levels: [level.value], links: spec(), reason: reason.value } }).then(function (res) {
        status.textContent = "";
        add(status, ["Filed as ", h("a", { href: res.url, rel: "noopener" }, "#" + res.number), "."]);
        status.className = "admin-note";
        busy(send, false);
      }, function (err) { busy(send, false); note(status, err, true); });
    });
    box.appendChild(form);
    load();
    return h("div", { class: "admin-fix-wrap" }, toggle, box);
  }

  function decision(x) {
    return h("div", { class: "admin-decision" + (x.uncertain ? " uncertain" : "") },
      h("p", null, h("code", null, x.id), " ", h("span", { class: "admin-sub" }, x.category.replace(/_/g, " ") + (x.levels && x.levels.length ? " \u00b7 " + x.levels.join("") : "")),
        x.uncertain ? [" ", pill("uncertain", "warn")] : null, x.footnote ? [" ", pill("footnote", "info")] : null),
      h("p", null, h("strong", null, x.choice), x.alternatives.length ? h("span", { class: "admin-sub" }, " not: " + x.alternatives.join("; ")) : null),
      h("p", { class: "admin-sub" }, x.reason));
  }

  function fixForm(r, langs, names, from, verse) {
    var open = !!from;
    var box = h("div", { class: "admin-fix", hidden: !open });
    var toggle = h("button", { type: "button", class: "admin-btn" }, "Request a fix");
    toggle.addEventListener("click", function () { box.hidden = !box.hidden; if (!box.hidden) change.focus(); });
    var lang = select("fix-lang-" + r.id, langs.map(function (c) { return [c, names[c] || c]; }),
      from && langs.indexOf(from.language) >= 0 ? from.language : langs[0]);
    var levels = h("fieldset", { class: "admin-checks-row" }, h("legend", null, "Levels"), ["L", "B", "R"].map(function (lv) {
      return h("label", null, h("input", { type: "checkbox", value: lv, checked: !from || !from.level || from.level === lv }), " " + LEVEL_NAMES[lv]);
    }));
    var change = h("textarea", { id: "fix-change-" + r.id, rows: 3, maxlength: 2000, placeholder: "What should change, e.g. use “la Parole” for “le Verbe”" });
    var reason = h("textarea", { id: "fix-reason-" + r.id, rows: 3, maxlength: 4000, placeholder: "Why (optional): the source, the style brief, a reader's point" });
    var send = h("button", { type: "submit", class: "admin-btn primary" }, "File fix request");
    var status = h("p", { class: "admin-note", role: "status" });
    var form = h("form", { class: "admin-form stacked" },
      h("label", { class: "admin-field", for: "fix-lang-" + r.id }, "Language", lang), levels,
      h("label", { class: "admin-field", for: "fix-change-" + r.id }, "Change", change),
      h("label", { class: "admin-field", for: "fix-reason-" + r.id }, "Reason", reason),
      h("p", { class: "admin-sub" }, "A Claude session weighs it against the source and the style brief, then opens a pull request or explains why not. The sentence stays an AI draft."),
      send, status);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var picked = Array.prototype.map.call(levels.querySelectorAll("input:checked"), function (x) { return x.value; });
      busy(send, true);
      api("/api/admin/fixes/", { method: "POST", body: { record: r.id, verse: verse || location.hash.split("/")[1], language: lang.value,
        levels: picked, change: change.value, reason: reason.value, message: from ? from.id : null } }).then(function (res) {
        status.textContent = "";
        add(status, ["Filed as ", h("a", { href: res.url, rel: "noopener" }, "#" + res.number), "."]);
        status.className = "admin-note";
        change.value = reason.value = "";
        busy(send, false);
      }, function (err) { busy(send, false); note(status, err, true); });
    });
    box.appendChild(form);
    var wrap = h("div", { class: "admin-fix-wrap" }, toggle, box);
    // Open with one rendering chosen: its language, only its level.
    wrap.prefill = function (code, level) {
      if (langs.indexOf(code) >= 0) lang.value = code;
      levels.querySelectorAll("input").forEach(function (x) { x.checked = x.value === level; });
      box.hidden = false;
      note(status, "");
      wrap.scrollIntoView({ block: "nearest", behavior: "smooth" });
      change.focus({ preventScroll: true });
    };
    return wrap;
  }

  VIEWS.fixes = function () {
    return api("/api/admin/fixes/").then(function (d) {
      var out = [head("Text", "Fix requests", "Wording changes asked for from the verse inspector or the reader inbox. Each is a GitHub issue labelled fix-request that a Claude session works into a pull request; nothing here marks a sentence reviewed."),
        verseSearch("")];
      if (!d.configured) out.push(h("p", { class: "notice" }, "Filing is off: set OWB_GITHUB_TOKEN on the API service in Render (a token that can create issues in " + d.repo + ")."));
      if (d.error) out.push(h("p", { class: "notice" }, d.error));
      out.push(h("section", { class: "admin-block" }, h("h2", null, "Open"),
        d.fixes.length ? table(["Issue", "Sentence", "Language", "Filed", "Taken by"], d.fixes.map(function (f) {
          return h("tr", null, h("td", null, h("a", { href: f.url, rel: "noopener" }, "#" + f.number)),
            h("td", null, f.verse ? h("a", { href: "#verse/" + f.verse }, f.record || f.verse) : f.title),
            h("td", null, f.language || "\u2014"), h("td", null, when(f.created_at)), h("td", null, f.assignees.join(", ") || "\u2014"));
        })) : empty("No open fix requests.")));
      return out;
    });
  };

  // Uncertain decisions, filtered; each opens in the inspector, where a fix
  // can be requested.
  var DECISIONS = { layer: "", category: "", book: "", q: "", offset: 0 };
  VIEWS.decisions = function () {
    var f = DECISIONS;
    var q = "?offset=" + f.offset + ["layer", "category", "book", "q"].map(function (k) {
      return f[k] ? "&" + k + "=" + encodeURIComponent(f[k]) : "";
    }).join("");
    return api("/api/admin/decisions/" + q).then(function (d) {
      function pick(id, label, options, key) {
        var s = select(id, [["", label]].concat(options), f[key]);
        s.setAttribute("aria-label", label);
        s.addEventListener("change", function () {
          f[key] = s.value; f.offset = 0;
          if (key === "layer") { f.category = ""; f.book = ""; }
          route();
        });
        return s;
      }
      var search = h("input", { type: "search", id: "decision-q", value: f.q, placeholder: "Words in the choice or reason", "aria-label": "Search decisions" });
      var form = h("form", { class: "admin-toolbar", role: "search" },
        pick("decision-layer", "Every layer", d.layers.map(function (l) { return [l.code, l.name + " (" + num(l.count) + ")"]; }), "layer"),
        pick("decision-category", "Every category", d.categories.map(function (c) { return [c.code, c.code.replace(/_/g, " ") + " (" + num(c.count) + ")"]; }), "category"),
        pick("decision-book", "Every book", d.books.map(function (b) { return [b.code, b.name + " (" + num(b.count) + ")"]; }), "book"),
        search, h("button", { type: "submit", class: "admin-btn" }, "Search"));
      form.addEventListener("submit", function (e) { e.preventDefault(); stopLive(); f.q = search.value.trim(); f.offset = 0; route(); });
      live(search, function (v) { if (v !== f.q) { f.q = v; f.offset = 0; route(); } });
      var pager = h("div", { class: "admin-actions" });
      if (d.offset > 0) pager.appendChild(h("button", { type: "button", class: "admin-btn", onclick: function () { f.offset = Math.max(0, d.offset - d.page); route(); } }, "\u2039 Earlier"));
      if (d.offset + d.page < d.total) pager.appendChild(h("button", { type: "button", class: "admin-btn", onclick: function () { f.offset = d.offset + d.page; route(); } }, "Later \u203a"));
      var names = {};
      d.layers.forEach(function (l) { names[l.code] = l.name; });
      return [head("Text", "Uncertain decisions", num(d.total) + " decisions the drafts mark uncertain" + (f.layer || f.category || f.book || f.q ? " match" : "") +
        ", in Bible order. Open one in the inspector to read the sentence whole or request a fix."), form,
        d.decisions.length ? h("div", { class: "admin-decisions" }, d.decisions.map(function (x) {
          return h("div", { class: "admin-decision uncertain" },
            h("p", null, h("a", { href: "#verse/" + x.verse }, x.label), " ", h("code", null, x.record + " " + x.key), " ",
              h("span", { class: "admin-sub" }, (x.layer === "meaning" ? "meaning" : names[x.language] || x.language) + " \u00b7 " + x.category.replace(/_/g, " ") +
                (x.levels.length ? " \u00b7 " + x.levels.join("") : "")), x.footnote ? [" ", pill("footnote", "info")] : null),
            h("p", null, h("strong", null, x.choice), x.alternatives.length ? h("span", { class: "admin-sub" }, " not: " + x.alternatives.join("; ")) : null),
            h("p", { class: "admin-sub" }, x.reason));
        })) : empty("No decisions match."),
        h("p", { class: "admin-sub" }, d.total ? "Showing " + num(d.offset + 1) + "\u2013" + num(d.offset + d.decisions.length) + " of " + num(d.total) + "." : ""),
        pager];
    });
  };

  // Key terms: the settled words, and where the drafts use them.
  VIEWS.terms = function () {
    return api("/api/admin/terms/").then(function (d) {
      var rows = d.terms.map(function (t) {
        var english = Array.isArray(t.english) ? t.english.join(", ") : Object.keys(t.english).map(function (lv) {
          return lv + ": " + t.english[lv].join(", ");
        }).join("; ");
        return h("tr", null,
          h("th", { scope: "row" }, h("span", { class: "admin-term", lang: t.language }, t.lemma), h("span", { class: "admin-sub" }, t.sense + " \u00b7 " + (t.language === "hbo" ? "H" : "G") + t.strong)),
          h("td", null, english, h("span", { class: "admin-sub" }, t.note)),
          h("td", { class: "admin-num" }, num(t.uses)),
          h("td", { class: "admin-sub" }, d.languages.filter(function (l) { return l.code !== "en"; }).map(function (l) {
            return l.code + " " + num(t.by_language[l.code]);
          }).join(" \u00b7 ")),
          h("td", { class: "admin-wrap" }, t.first.map(function (v) { return [h("a", { href: "#verse/" + v.verse }, v.label), " "]; }),
            h("a", { href: SITE + "/terms/" + t.slug + "/", rel: "noopener" }, "All on the site")));
      });
      return [head("Text", "Key terms", "Greek and Hebrew words whose English is settled at every level (data/key_terms.json); owb.validate holds the English to them. Changing one is a change for every use, so it goes to the founder, not a single fix request."),
        table(["Term", "English", ["Sentences", { class: "admin-num" }], "In other languages", "First uses"], rows)];
    });
  };

  // Articles: each English article's state in every language, and jobs for
  // the ones missing or behind their English.
  var ARTICLE_STATE = { current: ["Current", "good"], out_of_date: ["Out of date", "warn"],
    not_stamped: ["Not stamped", "warn"], missing: ["Missing", ""] };
  var ARTICLES = { lang: "", todo: false };
  VIEWS.articles = function () {
    return api("/api/admin/articles/").then(function (d) {
      var f = ARTICLES;
      if (!f.lang) f.lang = d.languages[0].code;
      var status = h("p", { class: "admin-note", role: "status" });
      var tiles = h("div", { class: "admin-tiles" }, d.languages.map(function (l) {
        var t = d.totals[l.code], done = d.articles.length - t.missing;
        return tile(done + " / " + d.articles.length, l.name + " translated" + (t.out_of_date ? ", " + t.out_of_date + " out of date" : "") +
          (t.not_stamped ? ", " + t.not_stamped + " not stamped" : ""));
      }));
      var langSel = select("article-lang", d.languages.map(function (l) { return [l.code, l.name]; }), f.lang);
      langSel.setAttribute("aria-label", "Language to act on");
      langSel.addEventListener("change", function () { f.lang = langSel.value; route(); });
      var todo = h("label", null, h("input", { type: "checkbox", id: "article-todo", checked: f.todo }), " Only what needs work in that language");
      todo.querySelector("input").addEventListener("change", function (e) { f.todo = e.target.checked; route(); });
      var shown = d.articles.filter(function (a) { return !f.todo || a.languages[f.lang] !== "current"; });
      var rows = shown.map(function (a) {
        var state = a.languages[f.lang];
        return h("tr", null,
          d.can_file ? h("td", null, state !== "current" ? h("input", { type: "checkbox", value: a.slug, "aria-label": "Choose " + a.title }) : null) : null,
          h("td", null, h("a", { href: SITE + "/articles/" + a.slug + "/", rel: "noopener" }, a.title), h("span", { class: "admin-sub" }, a.slug + " \u00b7 " + num(a.words) + " words \u00b7 " + a.date)),
          d.languages.map(function (l) {
            var st = ARTICLE_STATE[a.languages[l.code]];
            return h("td", { class: "admin-cell" + (l.code === f.lang ? " on" : "") }, pill(st[0], st[1]));
          }));
      });
      var out = [head("Text", "Articles", "Each English article and its translations, from scripts/check_translations.py: a translation is out of date when its English has changed since it was stamped."), tiles,
        h("div", { class: "admin-toolbar" }, h("span", null, "Act on ", langSel), todo)];
      if (d.can_file) {
        if (!d.configured) out.push(h("p", { class: "notice" }, "Filing is off: set OWB_GITHUB_TOKEN on the API service in Render."));
        if (d.error) out.push(h("p", { class: "notice" }, d.error));
        var noteField = h("input", { id: "article-note", maxlength: 2000, placeholder: "A note for the session (optional)", "aria-label": "Note" });
        var file = h("button", { type: "button", class: "admin-btn primary", disabled: !d.configured }, "File a job for the chosen articles");
        var all = h("button", { type: "button", class: "admin-btn" }, "Choose all that need work");
        all.addEventListener("click", function () { main.querySelectorAll("tbody input[type=checkbox]").forEach(function (c) { c.checked = true; }); });
        file.addEventListener("click", function () {
          var slugs = Array.prototype.map.call(main.querySelectorAll("tbody input:checked"), function (c) { return c.value; });
          if (!slugs.length) { note(status, "Choose at least one article.", true); return; }
          busy(file, true);
          api("/api/admin/articles/", { method: "POST", body: { language: f.lang, slugs: slugs, note: noteField.value } }).then(function (r) {
            FLASH = "Filed as #" + r.number + "."; route();
          }, function (err) { busy(file, false); note(status, err, true); });
        });
        out.push(h("div", { class: "admin-actions" }, all, noteField, file), status);
      }
      out.push(table((d.can_file ? [""] : []).concat(["Article"], d.languages.map(function (l) { return [l.code, { class: "admin-cell", title: l.name }]; })), rows));
      if (d.can_file) {
        out.push(h("section", { class: "admin-block" }, h("h2", null, "Open article jobs"),
          d.jobs && d.jobs.length ? table(["Issue", "Language", "Articles", "Filed"], d.jobs.map(function (j) {
            return h("tr", null, h("td", null, h("a", { href: j.url, rel: "noopener" }, "#" + j.number)), h("td", null, j.language || "\u2014"),
              h("td", { class: "admin-wrap" }, (j.slugs || []).join(", ")), h("td", null, when(j.created_at)));
          })) : empty("No open article jobs.")));
      }
      return out;
    });
  };

  // Work in progress: every job handed to Claude sessions, with its pull
  // requests.
  var WORK = { kind: "", state: "open" };
  var PR_TONE = { merged: "good", open: "info", draft: "", closed: "bad" };
  VIEWS.work = function () {
    return api("/api/admin/work/").then(function (d) {
      var items = d.items.filter(function (w) {
        return (!WORK.kind || w.kind === WORK.kind) && (WORK.state === "all" || (WORK.state === "stale" ? w.stale : w.state === WORK.state));
      });
      var kind = select("work-kind", [["", "Every kind"], ["drafting-job", "Drafting jobs"], ["fix-request", "Fix requests"], ["article-job", "Article jobs"]], WORK.kind);
      kind.setAttribute("aria-label", "Kind");
      kind.addEventListener("change", function () { WORK.kind = kind.value; route(); });
      var rows = items.map(function (w) {
        var state = w.state === "closed" ? pill(w.state_reason === "not_planned" ? "Closed, not done" : "Done", w.state_reason === "not_planned" ? "" : "good")
          : w.stale ? pill("Stalled", "bad") : w.prs.length ? pill("In review", "info") : pill("Waiting", "warn");
        return h("tr", null,
          h("td", null, h("a", { href: w.url, rel: "noopener" }, "#" + w.number), h("span", { class: "admin-sub" }, w.kind_label)),
          h("td", { class: "admin-wrap" }, w.title, w.assignees.length ? h("span", { class: "admin-sub" }, "taken by " + w.assignees.join(", ")) : null),
          h("td", null, state),
          h("td", null, w.prs.length ? h("ul", { class: "admin-roles" }, w.prs.map(function (p) {
            return h("li", null, pill(p.state, PR_TONE[p.state]), " ", h("a", { href: p.url, rel: "noopener" }, "#" + p.number));
          })) : "\u2014"),
          h("td", null, when(w.created_at), w.closed_at ? h("span", { class: "admin-sub" }, "closed " + when(w.closed_at)) : null));
      });
      return [head("Progress", "Work in progress", "Drafting jobs, fix requests and article jobs from the last " + d.days + " days, with the pull requests that name them. A job open for more than " + d.stale_hours + " hours with no pull request has stalled."),
        d.error ? h("p", { class: "notice" }, d.error) : null,
        d.counts ? h("div", { class: "admin-tiles" }, tile(num(d.counts.open), "open"), tile(num(d.counts.in_review), "with a pull request open"),
          tile(num(d.counts.stale), "stalled", d.counts.stale ? "bad" : ""), tile(num(d.counts.done), "closed in " + d.days + " days")) : null,
        h("div", { class: "admin-toolbar" }, seg([["open", "Open"], ["stale", "Stalled"], ["closed", "Closed"], ["all", "All"]], WORK.state, function (v) { WORK.state = v; route(); }), kind),
        items.length ? table(["Issue", "What", "State", "Pull requests", "Filed"], rows) : empty("Nothing here.")];
    });
  };

  // Similarity to the reference Bibles, per book (scripts/ngram_overlap.py).
  var OVERLAP = { book: "JHN", lang: "en", min: 6 };
  VIEWS.overlap = function (arg) {
    if (arg) OVERLAP.book = arg.toUpperCase();
    var f = OVERLAP;
    return api("/api/admin/overlap/" + f.book + "/?lang=" + f.lang + "&min=" + f.min).then(function (d) {
      var book = h("input", { id: "overlap-book", value: f.book, size: 6, "aria-label": "Book code", placeholder: "JHN" });
      // Every reading language, from the API; one with no reference Bible loaded says so.
      var lang = select("overlap-lang", (d.languages || [{ code: f.lang, name: f.lang, references: 1 }]).map(function (l) {
        return [l.code, l.references ? l.name : l.name + " (no reference Bible loaded)"];
      }), f.lang);
      lang.setAttribute("aria-label", "Language");
      var min = select("overlap-min", [["5", "5+ words"], ["6", "6+ words"], ["8", "8+ words"], ["10", "10+ words"]], String(f.min));
      min.setAttribute("aria-label", "Shortest run");
      var form = h("form", { class: "admin-toolbar" }, book, lang, min, h("button", { type: "submit", class: "admin-btn" }, "Compare"));
      form.addEventListener("submit", function (e) {
        e.preventDefault(); f.book = book.value.trim().toUpperCase() || "JHN"; f.lang = lang.value; f.min = +min.value;
        // A new address draws through hashchange; the same one needs route().
        if (location.hash === "#overlap/" + f.book) route();
        else location.hash = "#overlap/" + f.book;
      });
      var rows = d.editions.map(function (e) {
        return h("tr", null, h("th", { scope: "row" }, e.name, h("span", { class: "admin-sub" }, e.code)),
          ["L", "B", "R"].map(function (lv) {
            var v = e.share[lv];
            return h("td", { class: "admin-num" + (v >= 50 ? " admin-high" : "") }, v === null ? "\u2014" : v + "%");
          }), h("td", { class: "admin-num" }, num(e.longest) + " words"));
      });
      return [head("Text", "Similarity to reference Bibles", "The share of " + d.name + "'s drafted words that sit in runs of " + d.min + " or more words also found in the same verses of a public-domain Bible. Shared phrasing is often the common heritage of the language's Bible wording; a high share or long runs is where to check a draft wasn't built on a reference Bible."),
        form,
        d.editions.length ? table(["Bible", ["Literal", { class: "admin-num" }], ["Balanced", { class: "admin-num" }], ["Readable", { class: "admin-num" }], ["Longest run", { class: "admin-num" }]], rows)
          : empty("No reference Bibles in this language are loaded, so there's nothing to compare against."),
        h("p", { class: "admin-sub" }, num(d.sentences) + " sentences; words compared: L " + num(d.words.L) + ", B " + num(d.words.B) + ", R " + num(d.words.R) + ". Copyrighted Bibles are compared locally with scripts/ngram_overlap.py --extra."),
        d.longest_runs.length ? h("section", { class: "admin-block" }, h("h2", null, "Longest shared runs"),
          table(["Verse", "Level", "Bible", ["Words", { class: "admin-num" }], "Run"], d.longest_runs.map(function (r) {
            return h("tr", null, h("td", null, h("a", { href: "#verse/" + r.verse }, r.record)), h("td", null, r.level), h("td", null, r.edition),
              h("td", { class: "admin-num" }, num(r.length)), h("td", { class: "admin-wrap" }, r.text));
          }))) : null];
    });
  };

  // Export: the translation as a file (staff/export.py, owb/export.py), for
  // Bible software and the apps that carry our text. The file is fetched
  // with the account's token and saved from the browser.
  var EXPORT = { lang: "en", level: "B", type: "usfm", numbering: "english", books: "", settings: {} };
  var BOOK_SETS = { OT: [0, 39], NT: [39, 66] };
  var SETTING_NAME = { gender: "Gender", christos: "Title", divine_name: "Name of God", deity_pronoun: "Pronouns for God",
    units: "Measures", plural_you: "Plural you", god_term: "Word for God (Chinese)" };
  function exportQuery(d) {
    var f = EXPORT, books = f.books;
    if (BOOK_SETS[books]) books = d.books.slice(BOOK_SETS[books][0], BOOK_SETS[books][1]).map(function (b) { return b.code; }).join(",");
    // Each setting picked here, default or not: the server's default for
    // one is not always its first option (pronouns for God are "He").
    var settings = Object.keys(f.settings).map(function (k) { return k + ":" + f.settings[k]; }).join(",");
    return "?lang=" + f.lang + "&level=" + f.level + "&type=" + f.type + "&numbering=" + f.numbering +
      (books ? "&books=" + books : "") + (settings ? "&settings=" + settings : "");
  }
  function saveFile(path) {
    var account = saved();
    return fetch(API + path, { headers: account && account.token ? { Authorization: "Bearer " + account.token } : {} })
      .catch(function () { throw new Error("Can't reach the server. Check your connection and try again."); })
      .then(function (r) {
        if (!r.ok) return r.json().catch(function () { return {}; }).then(function (data) {
          throw new Error(C.failed(r.status, data).message);
        });
        var m = /filename="([^"]+)"/.exec(r.headers.get("Content-Disposition") || "");
        return r.blob().then(function (blob) {
          var url = URL.createObjectURL(blob);
          var a = h("a", { href: url, download: m ? m[1] : "open-word-bible" });
          document.body.appendChild(a);
          a.click();
          a.remove();
          setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
          return m ? m[1] : "the file";
        });
      });
  }
  VIEWS.export = function () {
    return api("/api/admin/export/").then(function (d) {
      var f = EXPORT;
      var status = h("p", { class: "admin-note", role: "status" });
      var result = h("div");
      function language() { return d.languages.filter(function (l) { return l.code === f.lang; })[0]; }
      var langSel = select("export-lang", d.languages.map(function (l) {
        return [l.code, l.name + " (" + num(l.sentences.B || 0) + " sentences)"];
      }), f.lang);
      var levelSel = select("export-level", d.levels.map(function (l) { return [l.code, l.name]; }), f.level);
      var typeSel = select("export-type", [["usfm", "USFM: a zip of one file per book"], ["json", "JSON: one file"]], f.type);
      var numberingSel = select("export-numbering", [["english", "English Bible verse numbers"],
        ["source", "Ours (Hebrew numbering in the Old Testament)"]], f.numbering);
      var bookSel = select("export-books", [["", "The whole Bible"], ["OT", "Old Testament"], ["NT", "New Testament"]]
        .concat(d.books.map(function (b) { return [b.code, b.name]; })), f.books);
      var settingsBox = h("fieldset", { class: "admin-checks-row" }, h("legend", null, "Wording settings"));
      function drawSettings() {
        settingsBox.querySelectorAll("label").forEach(function (l) { l.remove(); });
        language().settings.forEach(function (s) {
          var sel = select("export-setting-" + s.name, s.options.map(function (o, i) {
            return [String(i), o + (i === (s.default || 0) ? " (default)" : "")];
          }), String(s.name in f.settings ? f.settings[s.name] : s.default || 0));
          sel.addEventListener("change", function () { f.settings[s.name] = +sel.value; changed(); });
          settingsBox.appendChild(h("label", { class: "admin-field" }, SETTING_NAME[s.name] || s.name, sel));
        });
      }
      function changed() {
        f.lang = langSel.value; f.level = levelSel.value; f.type = typeSel.value;
        f.numbering = numberingSel.value; f.books = bookSel.value;
        keepAddress(true);
        var keep = {};
        language().settings.forEach(function (s) { if (s.name in f.settings) keep[s.name] = f.settings[s.name]; });
        f.settings = keep;
        result.textContent = "";
        note(status, "");
      }
      [levelSel, typeSel, numberingSel, bookSel].forEach(function (s) { s.addEventListener("change", changed); });
      langSel.addEventListener("change", function () { f.lang = langSel.value; f.settings = {}; drawSettings(); changed(); });
      drawSettings();

      var previewBtn = h("button", { type: "button", class: "admin-btn" }, "Preview");
      var downloadBtn = h("button", { type: "submit", class: "admin-btn primary" }, "Download");
      previewBtn.addEventListener("click", function () {
        busy(previewBtn, true);
        note(status, "Reading the text…");
        api("/api/admin/export/preview/" + exportQuery(d)).then(function (p) {
          note(status, "");
          result.textContent = "";
          var statuses = Object.keys(p.status).map(function (k) { return num(p.status[k]) + " " + k.replace(/_/g, " "); }).join(", ");
          result.appendChild(h("div", { class: "admin-tiles" }, tile(num(p.verses), "verses"),
            tile(num(p.books.length), "books"), tile(num(p.missing), "verses not translated yet", p.missing ? "warn" : "")));
          result.appendChild(h("p", { class: "admin-sub" }, "Sentences by review state: " + (statuses || "none") + "."));
          if (p.combined.length) {
            result.appendChild(h("p", { class: "admin-sub" }, "Held under one verse, as no verse bridge crosses chapters: " +
              p.combined.map(function (c) { return c.holds.join(" + ") + " (as " + c.verse + ")"; }).join("; ") + "."));
          }
          var missingBooks = Object.keys(p.missing_by_book);
          if (missingBooks.length) {
            result.appendChild(h("p", { class: "admin-sub" }, "Not translated yet, by book: " + missingBooks.slice(0, 20).map(function (b) {
              return b + " " + num(p.missing_by_book[b]);
            }).join(", ") + (missingBooks.length > 20 ? ", and " + (missingBooks.length - 20) + " more books" : "") +
              ". The manifest lists each verse."));
          }
          result.appendChild(p.samples.length ? table(["Verse", "Text (our numbering)"], p.samples.map(function (s) {
            return h("tr", null, h("th", { scope: "row" }, s.label), h("td", { class: "admin-wrap" }, s.text));
          })) : empty("Nothing in this language at this level yet."));
        }, function (err) { note(status, err, true); }).then(function () { busy(previewBtn, false); });
      });
      var form = h("form", { class: "admin-form stacked" },
        h("label", { class: "admin-field", for: "export-lang" }, "Language", langSel),
        h("label", { class: "admin-field", for: "export-level" }, "Level", levelSel),
        h("label", { class: "admin-field", for: "export-books" }, "Books", bookSel),
        h("label", { class: "admin-field", for: "export-type" }, "File", typeSel),
        h("label", { class: "admin-field", for: "export-numbering" }, "Verse numbers", numberingSel),
        settingsBox,
        h("div", { class: "admin-actions" }, previewBtn, downloadBtn), status);
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        busy(downloadBtn, true);
        note(status, "Making the file…");
        saveFile("/api/admin/export/file/" + exportQuery(d)).then(function (name) {
          note(status, "Saved " + name + ".");
        }, function (err) { note(status, err, true); }).then(function () { busy(downloadBtn, false); });
      });
      return [head("Text", "Export", "Download the translation in one language at one level, for Bible software and for the apps that carry our text. Settings are applied, poetry runs on one line, and untranslated verses are left out, never filled from another Bible. A manifest.json in each file says what it holds."),
        h("p", { class: "notice" }, "Every sentence is an AI-assisted draft until a named reviewer approves it, and the manifest says so. " +
          "The text is " + d.licence + ". It is the text as of the last deploy" + (d.imported_at ? " (" + when(d.imported_at) + ")" : "") + "."),
        h("p", null, "Every language at every level, at the default settings, is also on the public ",
          h("a", { href: SITE + "/download/", rel: "noopener" }, "download page"), ", rebuilt with the site; send people there."),
        h("section", { class: "admin-block" }, form, result),
        h("section", { class: "admin-block" }, h("h2", null, "Recent downloads"),
          d.recent.length ? table(["When", "File", "Verses", "By"], d.recent.map(function (a) {
            return h("tr", null, h("td", null, when(a.at)), h("td", null, a.target, h("span", { class: "admin-sub" }, (a.detail.books || []).join(", ") || "whole Bible")),
              h("td", { class: "admin-num" }, num(a.detail.verses)), h("td", null, a.by));
          })) : empty("Nothing downloaded yet."))];
    });
  };

  // Users.
  // System accounts (made by a deploy or a script, not a person) are left
  // out unless "Show system accounts" is ticked.
  var USERS = { q: "", role: "", offset: 0, system: false };
  VIEWS.users = function () {
    var q = "?offset=" + USERS.offset + (USERS.q ? "&q=" + encodeURIComponent(USERS.q) : "") + (USERS.role ? "&role=" + USERS.role : "") +
      (USERS.system ? "&system=1" : "");
    return api("/api/admin/users/" + q).then(function (d) {
      var search = h("input", { type: "search", id: "user-search", value: USERS.q, placeholder: "Search by email or name", "aria-label": "Search accounts" });
      var role = select("user-role", [["", "Everyone"], ["any", "The team (any role)"]].concat(d.roles.map(function (r) { return [r.kind, r.label]; })), USERS.role);
      role.setAttribute("aria-label", "Role");
      var system = h("input", { type: "checkbox", id: "user-system", checked: USERS.system });
      var form = h("form", { class: "admin-toolbar", role: "search" }, search, role,
        h("label", { for: "user-system" }, system, " Show system accounts"), h("button", { type: "submit", class: "admin-btn" }, "Search"));
      form.addEventListener("submit", function (e) { e.preventDefault(); stopLive(); USERS.q = search.value.trim(); USERS.role = role.value; USERS.offset = 0; route(); });
      live(search, function (v) { if (v !== USERS.q) { USERS.q = v; USERS.offset = 0; route(); } });
      role.addEventListener("change", function () { USERS.role = role.value; USERS.offset = 0; route(); });
      system.addEventListener("change", function () { USERS.system = system.checked; USERS.offset = 0; route(); });
      var rows = d.users.map(function (u) {
        return h("tr", null, h("td", null, h("a", { href: "#user/" + u.id }, u.email), u.active ? null : pill("inactive", "warn")),
          h("td", null, userName(u)), h("td", null, u.roles.join(", ") || (u.system ? "System" : "Reader")),
          h("td", null, date(u.joined)), h("td", null, when(u.signed_in)),
          h("td", { class: "admin-num" }, num(u.marks)), h("td", { class: "admin-num" }, num(u.devices)));
      });
      var pager = h("div", { class: "admin-actions" });
      if (d.offset > 0) pager.appendChild(h("button", { type: "button", class: "admin-btn", onclick: function () { USERS.offset = Math.max(0, d.offset - d.page); route(); } }, "‹ Newer"));
      if (d.offset + d.page < d.total) pager.appendChild(h("button", { type: "button", class: "admin-btn", onclick: function () { USERS.offset = d.offset + d.page; route(); } }, "Older ›"));
      return [head("Readers", "Users", num(d.total) + (d.total === 1 ? " account" : " accounts") + (USERS.q || USERS.role ? " match" : "") +
        (d.system_hidden ? " (" + plural(d.system_hidden, "system account") + " hidden)" : "") + ". Saved verses are counted, never listed: they are the reader's own."),
        form, d.users.length ? table(["Email", "Name", "Roles", "Joined", "Last sign-in", ["Saved", { class: "admin-num" }], ["Devices", { class: "admin-num" }]], rows) : empty("No accounts match."),
        pager];
    });
  };

  VIEWS.user = function (id) {
    return api("/api/admin/users/" + encodeURIComponent(id) + "/").then(function (u) {
      var status = h("p", { class: "admin-note", role: "status" });
      var actions = h("div", { class: "admin-actions" });
      if (u.devices.length && u.can_sign_out) {
        actions.appendChild(confirmButton("Sign out every device", "Sign out " + plural(u.devices.length, "device") + "?", function (b) {
          api("/api/admin/users/" + u.id + "/sign-out/", { method: "POST" }).then(function () { route(); }, function (e) { busy(b, false); note(status, e, true); });
        }));
      }
      if (u.can_delete) {
        actions.appendChild(confirmButton("Delete account", "Delete " + u.email + " for good?", function (b) {
          api("/api/admin/users/" + u.id + "/", { method: "DELETE" }).then(function () { location.hash = "#users"; }, function (e) { busy(b, false); note(status, e, true); });
        }, "admin-btn danger"));
      }
      return [
        h("p", { class: "admin-back" }, h("a", { href: "#users" }, "‹ Users")),
        head("Account", u.name || u.email, u.name ? u.email : null),
        h("dl", { class: "admin-facts" },
          fact("Roles", u.roles.length ? u.roles.join(", ") : (u.system ? "System" : "Reader")),
          fact("Name", userName(u)),
          fact("Joined", date(u.joined)),
          fact("Last sign-in", when(u.signed_in)),
          fact("Signs in with", u.ways_in.length ? u.ways_in.join(", ") : "has never signed in"),
          fact("Saved verses", plural(u.marks.bookmarks, "bookmark") + ", " + plural(u.marks.highlights, "highlight")),
          fact("Reading place", u.reading_place ? u.reading_place.book + " " + u.reading_place.chapter : "—")),
        h("section", { class: "admin-block" }, h("h2", null, "Signed-in devices"),
          u.devices.length ? table(["Device", "Signed in", "Last used"], u.devices.map(function (t) {
            return h("tr", null, h("td", { class: "admin-wrap" }, t.label || "Unknown browser"), h("td", null, date(t.created_at)), h("td", null, when(t.last_used_at)));
          })) : empty("None.")),
        u.messages.length ? h("section", { class: "admin-block" }, h("h2", null, "Messages"),
          h("ul", null, u.messages.map(function (m) { return h("li", null, m.kind + " on " + m.verse + " · " + m.status + " · " + date(m.created_at)); }))) : null,
        ME.admin.indexOf("team") >= 0 ? h("p", null, h("a", { href: "#team" }, "Change roles in Team & access")) : null,
        userChanges(u), actions, status];
    });
  };
  function fact(label, value) { return h("div", null, h("dt", null, label), h("dd", null, value)); }

  // An account's name as Users shows it: its display name, or (muted) one
  // made from its address when it has none.
  function userName(u) {
    if (u.name) return u.name;
    if (!u.display_name) return "—";
    return h("span", { class: "admin-sub", title: "No name set: this is from the email address" }, u.display_name);
  }

  // An admin's changes to an account: its display name (which the reader
  // also sets on their account page), and whether it is a system account
  // (a deploy's or a script's, not a person's).
  function userChanges(u) {
    var status = h("p", { class: "admin-note", role: "status" });
    function send(body, button) {
      busy(button, true);
      api("/api/admin/users/" + u.id + "/", { method: "PATCH", body: body }).then(function () { route(); },
        function (e) { busy(button, false); note(status, e, true); });
    }
    var name = h("input", { id: "user-name", value: u.name || "", maxlength: 80, placeholder: u.display_name || "" });
    var save = h("button", { type: "submit", class: "admin-btn" }, "Save name");
    var form = h("form", { class: "admin-toolbar" }, h("label", { class: "admin-field", for: "user-name" }, "Display name", name), save);
    form.addEventListener("submit", function (e) { e.preventDefault(); send({ name: name.value.trim() }, save); });
    var mark = h("button", { type: "button", class: "admin-btn" }, u.system ? "Mark as a person" : "Mark as a system account");
    mark.addEventListener("click", function () { send({ system: !u.system }, mark); });
    return h("section", { class: "admin-block" }, h("h2", null, "Name and kind"),
      h("p", { class: "admin-sub" }, "Readers set their name on their account page; set it here if one asks. " +
        "A system account is one a deploy or a script made: Users and the reader counts leave it out." +
        (u.system_reason ? " Marked: " + u.system_reason + "." : "")),
      form, h("div", { class: "admin-actions" }, mark), status);
  }

  // Team & access.
  VIEWS.team = function () {
    return api("/api/admin/team/").then(function (d) {
      var status = h("p", { class: "admin-note", role: "status" });
      var email = h("input", { type: "email", id: "grant-email", required: true, autocomplete: "off", placeholder: "name@example.org" });
      var kind = select("grant-kind", d.grantable.map(function (g) { return [g.kind, g.label]; }), d.grantable[0].kind);
      var lang = h("select", { id: "grant-lang" });
      var langField = h("label", { class: "admin-field", for: "grant-lang" }, "Language", lang);
      function langs() {
        var g = d.grantable.filter(function (x) { return x.kind === kind.value; })[0];
        lang.textContent = "";
        g.languages.forEach(function (l) { lang.appendChild(h("option", { value: l.code }, l.name)); });
        langField.hidden = !g.languages.length;
        about.textContent = g.about;
      }
      var about = h("p", { class: "admin-sub" });
      kind.addEventListener("change", langs);
      var grant = h("button", { type: "submit", class: "admin-btn primary" }, "Grant role");
      var form = h("form", { class: "admin-form" },
        h("label", { class: "admin-field", for: "grant-email" }, "Email", email),
        h("label", { class: "admin-field", for: "grant-kind" }, "Role", kind),
        langField, grant);
      langs();
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        busy(grant, true);
        api("/api/admin/team/", { method: "POST", body: { email: email.value, kind: kind.value, language: langField.hidden ? "" : lang.value } })
          .then(function (r) {
            FLASH = r.invited === false ? "Role granted, but the invitation email couldn't be sent." :
              r.invited ? "Role granted, and an invitation emailed." : "Role granted.";
            route();
          }, function (err) { busy(grant, false); note(status, err, true); });
      });
      var rows = d.members.map(function (m) {
        return h("tr", null,
          h("td", null, m.email, m.name ? h("span", { class: "admin-sub" }, m.name) : null),
          h("td", null, h("ul", { class: "admin-roles" }, m.roles.map(function (r) {
            var li = h("li", null, pill(r.label, r.kind === "super_admin" ? "warn" : "info"),
              h("span", { class: "admin-sub" }, r.granted_by ? " by " + r.granted_by + ", " + date(r.granted_at) : " " + date(r.granted_at)));
            if (r.kind !== "super_admin") {
              li.appendChild(confirmButton("Remove", "Remove " + r.label + "?", function (b) {
                api("/api/admin/team/roles/" + r.id + "/", { method: "DELETE" }).then(route, function (e) { busy(b, false); note(status, e, true); });
              }, "admin-link"));
            }
            return li;
          }))),
          h("td", null, m.pending ? [pill("Hasn't signed in", "warn"), " ", (function () {
            var b = h("button", { type: "button", class: "admin-link" }, "Resend invitation");
            b.addEventListener("click", function () {
              busy(b, true);
              api("/api/admin/team/invite/", { method: "POST", body: { email: m.email } }).then(function () {
                note(status, "Invitation sent to " + m.email + ".");
              }, function (e) { note(status, e, true); }).then(function () { busy(b, false); });
            });
            return b;
          })()] : when(m.signed_in)));
      });
      return [head("Team", "Team & access", "Grant the roles that open the admin and, when review starts, the reviewer roles. An address that has never signed in gets an invitation by email."),
        h("section", { class: "admin-block" }, h("h2", null, "Grant a role"), form, about, status),
        h("section", { class: "admin-block" }, h("h2", null, "The team"),
          table(["Person", "Roles", "Last sign-in"], rows)),
        teamAssignments(),
        h("p", { class: "admin-sub" }, "Super admins aren't granted here: they're the addresses in " + d.super_admins_from +
          " on the API service in Render, made super admins when they sign in.")];
    });
  };

  // Activity log.
  var ACTION_LABEL = {
    "role.grant": "granted a role to", "role.revoke": "removed a role from", "role.invite": "invited",
    "user.delete": "deleted the account", "user.sign_out": "signed out the devices of",
    "message.reply": "answered", "message.done": "marked done", "message.declined": "declined", "message.new": "reopened",
    "job.file": "filed drafting job", "article.job": "filed article job", "digest.send": "sent the weekly digest to", "message.fixed": "told the reader their message led to a change:", "email.send": "emailed the team:", "fix.request": "requested fix",
    "export.download": "downloaded", "review.assign": "assigned review to", "review.unassign": "took back a review assignment from",
    "review.assignment": "changed a review assignment of"
  };
  function activityList(actions) {
    return h("ul", { class: "admin-feed" }, actions.map(function (a) {
      var extra = a.detail.role ? " (" + a.detail.role + ")" : a.detail.range ? " (" + a.detail.range + ", " + a.detail.layer + ")" : a.detail.recipients !== undefined ? " (" + plural(a.detail.recipients, "person", "people") + ")" : "";
      return h("li", null, h("time", { datetime: a.at, title: new Date(a.at).toLocaleString("en-GB") }, when(a.at)),
        h("span", null, h("strong", null, a.actor || "The admin"), " " + (ACTION_LABEL[a.action] || a.action) + " " + a.target + extra));
    }));
  }
  VIEWS.activity = function () {
    var list = h("div");
    var more = h("button", { type: "button", class: "admin-btn", hidden: true }, "Older");
    var last = null;
    function load() {
      busy(more, true);
      return api("/api/admin/activity/" + (last ? "?before=" + last : "")).then(function (d) {
        if (d.actions.length) last = d.actions[d.actions.length - 1].id;
        list.appendChild(d.actions.length || last ? activityList(d.actions) : empty("Nothing done in the admin yet."));
        more.hidden = !d.more;
        busy(more, false);
      });
    }
    more.addEventListener("click", function () { later(more, load()); });
    return load().then(function () {
      return [head("Team", "Activity log", "What was done in the admin, newest first: roles, accounts, replies, jobs and emails. Reviews keep their own record."), list, more, approvalLog()];
    });
  };

  // Drafting jobs.
  VIEWS.jobs = function () {
    return api("/api/admin/jobs/").then(function (d) {
      var out = [head("Progress", "Drafting jobs", "Ask for a book to be drafted. The admin files a GitHub issue labelled drafting-job, which a Claude session picks up; drafts arrive as pull requests, marked AI-assisted until reviewed.")];
      if (!d.configured) {
        out.push(h("p", { class: "notice" }, "Filing is off: set OWB_GITHUB_TOKEN on the API service in Render (a token that can create issues in " + d.repo + ")."));
      }
      if (d.error) out.push(h("p", { class: "notice" }, d.error));
      var status = h("p", { class: "admin-note", role: "status" });
      var book = select("job-book", d.books.map(function (b) { return [b.code, b.name + " (" + b.chapters + ")"]; }),
        firstUndrafted(d));
      var boxes = h("fieldset", { class: "admin-checks-row" }, h("legend", null, "Languages"));
      function drawBoxes() {
        boxes.querySelectorAll("label").forEach(function (l) { l.remove(); });
        var cov = d.coverage[book.value];
        d.languages.forEach(function (l) {
          var state = cov[l.code];
          boxes.appendChild(h("label", { class: state === "drafted" ? "admin-off" : "" },
            h("input", { type: "checkbox", value: l.code, disabled: state === "drafted" || !d.configured }),
            " " + l.name + " ", h("span", { class: "admin-sub" }, STATE_LABEL[state].toLowerCase())));
        });
      }
      book.addEventListener("change", drawBoxes);
      drawBoxes();
      var text = h("textarea", { id: "job-note", rows: 3, maxlength: 2000, placeholder: "Anything the session should know (optional)" });
      var file = h("button", { type: "submit", class: "admin-btn primary", disabled: !d.configured }, "File job");
      var form = h("form", { class: "admin-form stacked" },
        h("label", { class: "admin-field", for: "job-book" }, "Book", book), boxes,
        h("label", { class: "admin-field", for: "job-note" }, "Note", text), file, status);
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var langs = Array.prototype.map.call(boxes.querySelectorAll("input:checked"), function (x) { return x.value; });
        busy(file, true);
        api("/api/admin/jobs/", { method: "POST", body: { book: book.value, languages: langs, note: text.value } }).then(function (r) {
          FLASH = "Filed as #" + r.number + ".";
          route();
        }, function (err) { busy(file, false); note(status, err, true); });
      });
      out.push(h("section", { class: "admin-block" }, h("h2", null, "New job"), form));
      out.push(jobBoard(d), bulkForm(d));
      out.push(h("section", { class: "admin-block" }, h("h2", null, "Open jobs"),
        d.jobs.length ? table(["Issue", "Book", "Languages", "Filed", "Taken by"], d.jobs.map(function (j) {
          return h("tr", null, h("td", null, h("a", { href: j.url, rel: "noopener" }, "#" + j.number)),
            h("td", null, j.title), h("td", null, (j.languages || []).join(", ")), h("td", null, when(j.created_at)),
            h("td", null, j.assignees.join(", ") || "—"));
        })) : empty("No open drafting jobs.")));
      return out;
    });
  };
  function firstUndrafted(d) {
    var b = d.books.filter(function (x) { return d.coverage[x.code].en === "none"; })[0];
    return b ? b.code : d.books[0].code;
  }

  // The queue board: every book in every language, drafted, with a job
  // filed, or with the job's pull request open.
  var BOARD_LABEL = { none: "Not started", partial: "Partly drafted", filed: "Job filed", pr: "Pull request open", drafted: "Drafted" };
  function jobBoard(d) {
    var tab = sessionTab("jobs-board", "ot");
    var body = h("div");
    function draw(which) {
      body.textContent = "";
      var rows = d.books.filter(function (b) { return b.testament === which; }).map(function (b) {
        return h("tr", null, h("th", { scope: "row" }, h("a", { href: "#book/" + b.code }, b.name)),
          d.languages.map(function (l) {
            var c = (d.board[b.code] || {})[l.code] || { state: "none" };
            var mark = h("span", { class: "admin-state " + c.state, title: l.name + ": " + BOARD_LABEL[c.state] + (c.number ? " (#" + c.number + ")" : "") },
              c.state === "drafted" ? "✓" : c.number ? "#" + c.number : "");
            return h("td", { class: "admin-cell" }, c.url ? h("a", { href: c.url, rel: "noopener" }, mark) : mark);
          }));
      });
      body.appendChild(table(["Book"].concat(d.languages.map(function (l) { return [l.code, { title: l.name, class: "admin-cell" }]; })), rows, "admin-coverage"));
    }
    draw(tab);
    return h("section", { class: "admin-block", id: "queue" }, h("h2", null, "Queue board"),
      h("div", { class: "admin-toolbar" }, seg([["ot", "Old Testament"], ["nt", "New Testament"]], tab, function (v) {
        rememberTab("jobs-board", v); draw(v);
      }), h("p", { class: "admin-legend" }, ["none", "partial", "filed", "pr", "drafted"].map(function (s) {
        return h("span", null, h("span", { class: "admin-state " + s }), BOARD_LABEL[s]);
      }))), body);
  }

  // Queue missing books: one job per book that still lacks any of the
  // languages, previewed first.
  function bulkForm(d) {
    var status = h("p", { class: "admin-note", role: "status" });
    var boxes = h("fieldset", { class: "admin-checks-row" }, h("legend", null, "Languages"),
      d.languages.map(function (l) {
        return h("label", null, h("input", { type: "checkbox", value: l.code, disabled: !d.configured }), " " + l.name);
      }));
    var testament = select("bulk-testament", [["ot", "Old Testament"], ["nt", "New Testament"], ["all", "Whole Bible"]], "ot");
    var text = h("textarea", { id: "bulk-note", rows: 2, maxlength: 2000, placeholder: "Added to every job (optional)" });
    var preview = h("button", { type: "submit", class: "admin-btn", disabled: !d.configured }, "Preview");
    var result = h("div");
    function payload(dry) {
      return { languages: Array.prototype.map.call(boxes.querySelectorAll("input:checked"), function (x) { return x.value; }),
        testament: testament.value, note: text.value, dry_run: dry };
    }
    function line(j) { return h("li", null, bookName(d, j.book) + ": " + j.languages.join(", ")); }
    var form = h("form", { class: "admin-form stacked" }, boxes,
      h("label", { class: "admin-field", for: "bulk-testament" }, "Books", testament),
      h("label", { class: "admin-field", for: "bulk-note" }, "Note", text), preview, status, result);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      busy(preview, true);
      result.textContent = "";
      note(status, "");
      var asked = payload(false);
      api("/api/admin/jobs/bulk/", { method: "POST", body: payload(true) }).then(function (r) {
        if (!r.plan.length) {
          note(status, "Nothing to file: " + (r.skipped.length ? plural(r.skipped.length, "book") + " already drafted or asked for." : "no books."));
          return;
        }
        add(result, [h("p", null, plural(r.plan.length, "job") + " to file" + (r.remaining ? " now; " + r.remaining + " more after these (at most " + r.limit + " at a time)" : "") + ":"),
          h("ul", { class: "admin-roles" }, r.plan.map(line)),
          r.skipped.length ? h("details", null, h("summary", null, plural(r.skipped.length, "book") + " left out"),
            h("ul", null, r.skipped.map(function (s) { return h("li", null, bookName(d, s.book) + ": " + s.reason); }))) : null,
          confirmButton("File " + plural(r.plan.length, "job"), "File them?", function (b) {
            api("/api/admin/jobs/bulk/", { method: "POST", body: asked }).then(function (f) {
              FLASH = "Filed " + plural(f.filed.length, "job") + (f.error ? ". " + f.error : f.remaining ? "; " + f.remaining + " more to queue." : ".");
              route();
            }, function (err) { busy(b, false); note(status, err, true); });
          }, "admin-btn primary")]);
      }, function (err) { note(status, err, true); }).then(function () { busy(preview, false); });
    });
    return h("section", { class: "admin-block" }, h("h2", null, "Queue missing books"),
      h("p", null, "Files one job per book that still lacks any of the languages, in Bible order, skipping languages an open job already asks for."), form);
  }
  function bookName(d, code) {
    var b = d.books.filter(function (x) { return x.code === code; })[0];
    return b ? b.name : code;
  }

  // Team email.
  VIEWS.emails = function () {
    return api("/api/admin/emails/").then(function (d) {
      var status = h("p", { class: "admin-note", role: "status" });
      var audience = select("mail-audience", d.audiences.map(function (a) { return [a.key, a.label + " (" + a.count + ")"]; }), "team");
      var subject = h("input", { id: "mail-subject", maxlength: 200, required: true });
      var body = h("textarea", { id: "mail-body", rows: 10, required: true });
      var test = h("button", { type: "button", class: "admin-btn" }, "Send a test to me");
      var count = function () { return d.audiences.filter(function (a) { return a.key === audience.value; })[0].count; };
      function payload(isTest) { return { subject: subject.value, body: body.value, audience: audience.value, test: isTest }; }
      test.addEventListener("click", function () {
        busy(test, true);
        api("/api/admin/emails/", { method: "POST", body: payload(true) }).then(function () {
          note(status, "Test sent to " + ME.email + ".");
        }, function (e) { note(status, e, true); }).then(function () { busy(test, false); });
      });
      var sendWrap = h("span");
      function drawSend() {
        sendWrap.textContent = "";
        sendWrap.appendChild(confirmButton("Send", "Send to " + plural(count(), "person", "people") + "?", function (b) {
          api("/api/admin/emails/", { method: "POST", body: payload(false) }).then(function (r) {
            FLASH = "Sent to " + plural(r.sent, "person", "people") + (r.failed ? "; " + r.failed + " failed" : "") + ".";
            route();
          }, function (e) { busy(b, false); note(status, e, true); drawSend(); });
        }, "admin-btn primary"));
      }
      audience.addEventListener("change", drawSend);
      drawSend();
      return [head("Team", "Team email", "Email everyone on the team, or everyone with one role. Each person gets their own copy. Readers aren't emailed from here: the privacy page says an account's address is for signing in."),
        h("section", { class: "admin-block" }, h("form", { class: "admin-form stacked", onsubmit: function (e) { e.preventDefault(); } },
          h("label", { class: "admin-field", for: "mail-audience" }, "To", audience),
          h("label", { class: "admin-field", for: "mail-subject" }, "Subject", subject),
          h("label", { class: "admin-field", for: "mail-body" }, "Message (plain text)", body),
          h("div", { class: "admin-actions" }, test, sendWrap), status)),
        h("section", { class: "admin-block" }, h("h2", null, "Sent"),
          d.sent.length ? table(["Sent", "Subject", "To", ["People", { class: "admin-num" }], "By"], d.sent.map(function (b) {
            return h("tr", null, h("td", null, date(b.sent_at)), h("td", null, b.subject), h("td", null, b.audience),
              h("td", { class: "admin-num" }, num(b.recipients) + (b.failed ? " (" + b.failed + " failed)" : "")), h("td", null, b.sent_by));
          })) : empty("Nothing sent yet."))];
    });
  };

  // Help & roles.
  var ROLES = [
    ["Super admin", "Everything, including the team, jobs and deleting accounts. Set by OWB_SUPER_ADMIN_EMAILS on the server."],
    ["Editor", "The progress pages, the reader inbox, fix requests, reviewers' flags and review assignments."],
    ["Reporting", "The progress pages only: dashboard, coverage, languages, content health, engagement."],
    ["User records", "The progress pages and readers' accounts (sign devices out; only a super admin deletes)."],
    ["Email", "The progress pages and team email."],
    ["Scholar reviewer", "The progress pages and Review: approving or flagging the meaning of the sentences translated from their language (Greek: the New Testament; Hebrew: the Old)."],
    ["Language reviewer", "The progress pages and Review: approving or flagging the wording in their language. Approving the meaning moves a sentence on from AI-assisted; wording approvals are kept per language."]
  ];
  VIEWS.help = function () {
    var sections = SECTIONS.filter(function (s) { return s.id !== "help"; });
    var AREA = { overview: "Anyone on the team", export: "Anyone on the team", review: "Reviewers", inbox: "Editors", users: "User records", email: "Email",
      jobs: "Super admins", team: "Super admins" };
    var out = [head("Team", "Help & roles", "What each role opens, and where things live. The admin shows you only the sections your roles open; the server checks every request again."),
      h("section", { class: "admin-block" }, h("h2", null, "Roles"),
        table(["Role", "Opens"], ROLES.map(function (r) { return h("tr", null, h("th", { scope: "row" }, r[0]), h("td", null, r[1])); }))),
      h("section", { class: "admin-block" }, h("h2", null, "Sections"),
        table(["Section", "Who"], sections.map(function (s) {
          return h("tr", null, h("th", { scope: "row" }, opens(s) ? h("a", { href: "#" + s.id }, s.label) : s.label), h("td", null, AREA[s.area] + (AREA[s.area] === "Anyone on the team" ? "" : " (and super admins)")));
        }))),
      h("section", { class: "admin-block" }, h("h2", null, "Good to know"), h("ul", null,
        h("li", null, "Numbers come from the database, which each deploy brings up to date from content/ on main. A merged pull request shows here after its deploy."),
        h("li", null, "Only a person marks a sentence reviewed, in Review, and every approval names who made it. A sentence an import changes after its approval goes back in the reviewer's queue."),
        h("li", null, "Your roles: " + (ME.roles.length ? ME.roles.map(function (r) { return r.label; }).join(", ") : "none") + ".")))];
    if (ME.is_super_admin) {
      out.push(h("p", null, "Records the admin doesn't cover yet are in the ", h("a", { href: API + "/admin/", rel: "noopener" }, "database admin"),
        " (it needs a password: run manage.py changepassword with your address in the Render shell)."));
    }
    return out;
  };

  // Consistency: how one language words each key term across the sentences
  // that use it, the terms split between wordings first.
  var CONSISTENCY = { lang: "en", level: "B" };
  VIEWS.consistency = function () {
    var f = CONSISTENCY;
    return api("/api/admin/consistency/?lang=" + f.lang + "&level=" + f.level).then(function (d) {
      var langSel = select("consistency-lang", d.languages.map(function (l) { return [l.code, l.name]; }), f.lang);
      langSel.setAttribute("aria-label", "Language");
      langSel.addEventListener("change", function () { f.lang = langSel.value; route(); });
      var fixes = ME.admin.indexOf("inbox") >= 0;
      function examples(list) {
        return h("ul", { class: "admin-examples" }, list.map(function (e) {
          return h("li", null, h("a", { href: "#verse/" + e.verse }, e.label), " ", h("span", { class: "admin-sub" }, e.record),
            fixes ? [" \u00b7 ", h("a", { href: "#verse/" + e.verse }, "File a fix request")] : null);
        }));
      }
      var split = d.terms.filter(function (t) { return t.split; }).length;
      var blocks = d.terms.filter(function (t) { return t.rendered; }).map(function (t) {
        return h("section", { class: "admin-block" },
          h("h2", null, h("span", { class: "admin-term", lang: t.language }, t.lemma), " ", t.sense, " ",
            t.split ? pill("split", "warn") : pill("consistent", "good")),
          h("p", { class: "admin-sub" }, plural(t.rendered, "sentence") + " in this language and level, of " + num(t.uses) + " that use the term."),
          h("div", { class: "admin-bars" }, t.forms.map(function (form) {
            return h("details", null, h("summary", { class: "admin-bar-row" }, h("span", null, form.form), bar(form.sentences, t.rendered),
              h("span", { class: "admin-num" }, num(form.sentences) + " \u00b7 " + form.books.join(", "))), examples(form.examples));
          }), t.other.sentences ? h("details", null, h("summary", { class: "admin-bar-row" }, h("span", null, "None of these"),
            bar(t.other.sentences, t.rendered, "warn"), h("span", { class: "admin-num" }, num(t.other.sentences))), examples(t.other.examples)) : null));
      });
      return [head("Text", "Consistency", "How each key term is worded across the sentences that use it, from the wordings the records give it (alignments, decisions and, for English, the key term list). A term worded two ways in two or more sentences each is split; open a wording for its sentences."),
        h("div", { class: "admin-toolbar" }, langSel,
          seg([["L", "Literal"], ["B", "Balanced"], ["R", "Readable"]], f.level, function (v) { f.level = v; route(); })),
        h("p", null, plural(split, "key term") + " split in " + langSel.selectedOptions[0].textContent + " at this level."),
        blocks.length ? blocks : empty("No sentence that uses a key term is drafted in this language yet.")];
    });
  };

  // Checks (GET /api/admin/checks/): footnotes whose verse words the
  // alternative or not the choice, and verses and glossary entries at odds
  // with the language's terms glossary. Heuristics to look at, not rules.
  var CHECKS = { lang: "en", kind: "all" };
  var CHECK_KINDS = {
    alternative: "Words the alternative",
    choice_missing: "Choice not worded",
    different_forms: "Two forms",
    ruled_out: "Uses a ruled-out form"
  };
  VIEWS.checks = function () {
    var f = CHECKS;
    return api("/api/admin/checks/?lang=" + f.lang).then(function (d) {
      var langSel = select("checks-lang", d.languages.map(function (l) {
        return [l.code, l.name + (l.glossary ? " (glossary)" : "")];
      }), f.lang);
      langSel.setAttribute("aria-label", "Language");
      langSel.addEventListener("change", function () { f.lang = langSel.value; f.kind = "all"; route(); });
      var name = d.languages.filter(function (l) { return l.code === d.language; }).map(function (l) { return l.name; })[0] || d.language;
      function verseLink(x) {
        return [h("a", { href: "#verse/" + x.verse }, x.label), h("div", { class: "admin-sub" }, x.record)];
      }
      function levels(x) { return (x.levels || [x.level]).join(", "); }
      function glossaryLine(file, line) {
        return h("a", { href: ghFile(file) + "#L" + line, rel: "noopener" }, "line " + line);
      }

      var notes = d.notes.hits.filter(function (x) { return f.kind === "all" || x.kind === f.kind; });
      var kindSeg = seg([["all", "All (" + num(d.notes.total) + ")"],
        ["alternative", CHECK_KINDS.alternative + " (" + num(d.notes.kinds.alternative) + ")"],
        ["choice_missing", CHECK_KINDS.choice_missing + " (" + num(d.notes.kinds.choice_missing) + ")"]],
        f.kind, function (v) { f.kind = v; route(); });
      var noteRows = notes.map(function (x) {
        var tags = [pill(CHECK_KINDS[x.kind] || x.kind, x.kind === "alternative" ? "warn" : "")];
        if (x.kind === "alternative") {
          tags.push(h("div", { class: "admin-sub" }, x.contrast === "english" ? "The English words the choice" : "Another level words the choice"));
        }
        if (x.english_too) tags.push(" ", pill("English too", "bad"));
        return h("tr", null,
          h("td", null, verseLink(x)),
          h("td", null, levels(x), h("div", { class: "admin-sub" }, x.decision)),
          h("td", null, tags),
          h("td", { class: "admin-wrap" }, h("div", { lang: d.language }, x.choice),
            x.alternative ? h("div", { class: "admin-sub", lang: d.language }, "Alternative: " + x.alternative) : null,
            h("div", { class: "admin-sub" }, (x.kind === "alternative" ? "Verse has: " : "Verse lacks: ") + x.words.join(", "))),
          h("td", { class: "admin-wrap", lang: d.language }, x.text));
      });
      var noteBlock = h("section", { class: "admin-block" },
        h("h2", null, "Footnotes and verses"),
        h("p", { class: "admin-sub" }, "Footnoted meaning decisions whose translated note says one thing while the verse says another: at some level the verse has an alternative's distinctive words and none of the choice's (while the English at that level, or another level of this language, words the choice), or it has none of a short choice's words where the English has them. Text variants, grammar and punctuation are left out. “English too”: the English verse words the alternative as well, so a fix may start there."),
        h("div", { class: "admin-toolbar" }, kindSeg),
        noteRows.length ? table(["Verse", "Levels", "Signal", "Note", "Verse text"], noteRows)
          : empty(d.notes.total ? "None of this kind." : "No footnote and verse at odds in " + name + "."));

      var g = d.glossary, glossBlock;
      if (!g.file) {
        glossBlock = h("section", { class: "admin-block" }, h("h2", null, "Terms glossary"),
          empty(d.language === "en" ? "English has no terms glossary: the glossaries say how other languages word its terms." :
            name + " has no terms glossary (docs/" + name.toLowerCase() + "-terms.md)."));
      } else {
        var verseRows = g.verses.hits.map(function (x) {
          return h("tr", null,
            h("td", null, verseLink(x)),
            h("td", null, levels(x)),
            h("td", null, pill(x.kind === "avoided" ? "Ruled out" : "Alternative only", x.kind === "avoided" ? "bad" : "warn")),
            h("td", null, h("b", { lang: d.language }, x.form), h("div", { class: "admin-sub" }, "for “" + x.term + "”")),
            h("td", { class: "admin-wrap" }, glossaryLine(g.file, x.row.line), " ", h("code", { lang: d.language }, x.row.forms),
              x.allowed_by ? h("div", { class: "admin-sub" }, "This book's own entry gives it: ", glossaryLine(g.file, x.allowed_by)) : null),
            h("td", { class: "admin-wrap", lang: d.language }, x.text));
        });
        var conflictRows = g.rows.map(function (c) {
          return h("tr", null,
            h("td", null, h("b", null, c.term)),
            h("td", null, pill(CHECK_KINDS[c.kind] || c.kind, c.kind === "ruled_out" ? "bad" : "warn"),
              c.forms.length ? h("div", { class: "admin-sub", lang: d.language }, c.forms.join(", ")) : null),
            h("td", { class: "admin-wrap" }, h("ul", { class: "admin-examples" }, c.rows.map(function (r) {
              return h("li", null, glossaryLine(g.file, r.line), " ", r.book ? h("span", { class: "admin-sub" }, r.book + " ") : null,
                r.source + ": ", h("code", { lang: d.language }, r.forms));
            }))));
        });
        glossBlock = h("section", { class: "admin-block" },
          h("h2", null, "Terms glossary"),
          h("p", { class: "admin-sub" }, "From ", h("a", { href: ghFile(g.file), rel: "noopener" }, g.file),
            ": verses that use a form the glossary rules out (“Not *x*”, “never *x*”) or names only as an alternative, where the English verse has the entry's English term. An “Added while drafting” entry counts in its own book only."),
          verseRows.length ? table(["Verse", "Levels", "Signal", "Form", "Glossary entry", "Verse text"], verseRows)
            : empty("No verse uses a form the glossary rules out."),
          h("h3", { class: "admin-h3" }, "Entries at odds"),
          h("p", { class: "admin-sub" }, "Entries for one English term (articles, plurals and asides aside) whose forms share no word, or where one uses a form another rules out. Entries naming different source words are kept apart. Some differences are deliberate (two senses, two people of one name): read the entries' notes."),
          conflictRows.length ? table(["English term", "Signal", "Entries"], conflictRows)
            : empty("No two entries disagree."));
      }
      return [head("Text", "Checks", "Content checks from the database and the files the deploy carries (data/notes/, docs/*-terms.md). They are heuristics for a reviewer and never block a merge; scripts/content_checks.py prints the same lists."),
        h("div", { class: "admin-toolbar" }, langSel),
        h("div", { class: "admin-tiles" },
          tile(num(d.notes.total), "footnote and verse mismatches"),
          tile(g.file ? num(g.verses.total) : "—", "verses against the glossary"),
          tile(g.file ? num(g.rows.length) : "—", "glossary terms at odds")),
        noteBlock, glossBlock];
    });
  };

  // ---- Search --------------------------------------------------------

  // The box at the top of the rail, which is also the admin's command
  // palette. Ctrl K or Cmd K (or "/") opens it on the recent pages and
  // every section the account opens; typing ranks those (OWBAdminNav.rank),
  // offers what the query names outright (a GitHub issue or pull request
  // number, an account by email) and asks GET /api/admin/search/ for
  // verses (by reference in any language the site reads), sentences,
  // terms, articles, decisions, and accounts and reader messages for the
  // roles that open them. Arrows, Enter and Escape work the list. Made once
  // and kept across drawings of the rail.
  var SEARCH = null;
  function searchBox() {
    if (SEARCH) return SEARCH.wrap;
    var input = h("input", { type: "search", id: "admin-search", placeholder: "Search or jump to…", autocomplete: "off",
      spellcheck: "false", role: "combobox", "aria-expanded": "false", "aria-controls": "admin-search-list",
      "aria-autocomplete": "list", "aria-label": "Search or jump to (Ctrl K or /)" });
    var list = h("div", { class: "admin-search-list", id: "admin-search-list", role: "listbox", hidden: true });
    var wrap = h("div", { class: "admin-search", role: "search" }, input, list);
    var timer = null, asked = 0, active = -1, options = [], served = null;

    function close() {
      list.hidden = true;
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
      active = -1;
    }
    function mark(i) {
      if (!options.length) return;
      active = (i + options.length) % options.length;
      options.forEach(function (o, j) { o.setAttribute("aria-selected", j === active ? "true" : "false"); });
      input.setAttribute("aria-activedescendant", options[active].id);
      options[active].scrollIntoView({ block: "nearest" });
    }
    function go(o) {
      var href = o.getAttribute("href");
      close();
      input.value = "";
      input.blur();
      if (o.getAttribute("target")) window.open(href, "_blank", "noopener");
      else if (location.hash === href) route();
      else location.hash = href;
    }
    // The palette's own groups for q: what it names, the sections and the
    // recent pages.
    function local(q) {
      var sections = SECTIONS.filter(opens).map(function (s) {
        return { title: s.label, detail: s.group || "Section", href: "#" + s.id, words: s.id + " " + s.group };
      });
      var here = "#" + (shown || "");
      var mine = recent().filter(function (r) { return r.href !== here; });
      if (!q) {
        return [{ label: "Recent", results: mine.slice(0, 5) }, { label: "Sections", results: sections }];
      }
      return [{ label: "Go to", results: N.direct(q, GITHUB, ME.admin.indexOf("users") >= 0) },
        { label: "Sections", results: N.rank(q, sections, 5) },
        { label: "Recent", results: N.rank(q, mine, 3) }];
    }
    function show(q, groups, waiting) {
      var was = active >= 0 && options[active] ? options[active].getAttribute("href") : null;
      list.textContent = "";
      options = [];
      groups = groups.filter(function (g) { return g.results.length; });
      if (!groups.length) {
        list.appendChild(h("p", { class: "admin-empty" }, waiting ? "Searching…" : "Nothing found for “" + q + "”."));
      }
      groups.forEach(function (g) {
        list.appendChild(h("p", { class: "admin-search-group", role: "presentation" }, g.label));
        g.results.forEach(function (r) {
          var o = h("a", { href: r.href, role: "option", id: "admin-search-" + options.length, "aria-selected": "false",
            tabindex: "-1", target: r.external ? "_blank" : null, rel: r.external ? "noopener" : null },
          h("span", null, r.title), r.detail ? h("span", { class: "admin-sub" }, r.detail) : null);
          o.addEventListener("mousedown", function (e) { e.preventDefault(); });
          o.addEventListener("click", function (e) { e.preventDefault(); go(o); });
          options.push(o);
          list.appendChild(o);
        });
      });
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
      var keep = options.map(function (o) { return o.getAttribute("href"); }).indexOf(was);
      if (options.length) mark(keep > 0 ? keep : 0);
    }
    // The local groups at once, and the API's under them when they come.
    function ask() {
      var q = input.value.trim();
      var mine = ++asked;
      var groups = local(q);
      var server = q.length >= 2;
      show(q, served && served.q === q ? groups.slice(0, 1).concat(served.groups, groups.slice(1)) : groups, server);
      if (!server || (served && served.q === q)) return;
      api("/api/admin/search/?q=" + encodeURIComponent(q)).then(function (d) {
        if (mine !== asked) return;
        served = { q: q, groups: d.groups };
        // What the query names first, then the API's (a verse by reference
        // ranks above a section whose letters it happens to contain).
        show(q, groups.slice(0, 1).concat(d.groups, groups.slice(1)), false);
      }, function (e) {
        if (mine !== asked) return;
        show(q, groups, false);
        list.appendChild(h("p", { class: "admin-empty" }, e.message));
      });
    }
    function open() {
      input.focus();
      input.select();
      clearTimeout(timer);
      ask();
    }
    input.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(ask, 120);
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (list.hidden) { ask(); return; }
        mark(active + (e.key === "ArrowDown" ? 1 : -1));
      } else if (e.key === "Enter") {
        e.preventDefault();
        clearTimeout(timer);
        if (!list.hidden && active >= 0) go(options[active]);
        else ask();
      } else if (e.key === "Escape") {
        if (!list.hidden) close(); else { input.value = ""; input.blur(); }
      }
    });
    input.addEventListener("blur", close);
    input.addEventListener("focus", function () { ask(); });
    // On the window, before the site's search palette (search.js) takes "/"
    // and Ctrl K or Cmd K on the document: in the admin both open this box.
    window.addEventListener("keydown", function (e) {
      if (rail.hidden || !wrap.isConnected) return;
      var k = (e.key || "").toLowerCase();
      var palette = k === "k" && (e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey;
      if (!palette) {
        if (k !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
        var t = e.target;
        if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
      }
      e.preventDefault();
      e.stopPropagation();
      if (palette && document.activeElement === input && !list.hidden) { close(); input.blur(); return; }
      open();
    }, true);
    SEARCH = { wrap: wrap, input: input };
    return wrap;
  }
  // Review: a reviewer's queue for one layer (the meaning of the Greek or
  // Hebrew, or one language's wording), then one sentence at a time.
  var REVIEW_STATE = { not_reviewed: ["Not reviewed", ""], approved: ["Approved", "good"], changed: ["Changed since approval", "warn"],
    flagged: ["Flagged", "bad"] };
  function reviewPill(state) { return pill(REVIEW_STATE[state][0], REVIEW_STATE[state][1]); }
  // The queue as last listed, for a sentence's next and previous (j, k) and
  // the next to review after approving one: {layer, rows: [{record,
  // state}], more}. Kept here, not in the read cache, so it outlives an
  // approval (which forgets the queue's reads) and keeps its order.
  var QUEUE = null;
  // The queue's filters, kept in the address (#review?layer=grc&book=ISA).
  var REVIEW = { layer: sessionTab("review.layer", ""), book: sessionTab("review.book", ""), state: sessionTab("review.state", "todo") };
  VIEWS.review = function (arg) {
    var parts = arg ? arg.split("/") : [];
    return parts[1] ? reviewSentence(parts[0], parts[1]) : reviewQueue(parts[0] || REVIEW.layer);
  };
  // Bulk review in the queue (POST /api/admin/review/bulk/): tick sentences
  // (shift-click ticks the range from the last one ticked) to approve or
  // flag them together, or approve the rest of a chapter after a confirm
  // step that says how many that is. layerOf() is the queue's layer.
  function queuePicker(layerOf, status) {
    var boxes = [], last = -1, chapter = null;
    var count = h("strong");
    var noteBox = h("input", { type: "text", id: "bulk-note", maxlength: 4000, placeholder: "What is wrong (needed to flag)" });
    var approveBtn = h("button", { type: "button", class: "admin-btn primary" }, "Approve selected");
    var flagBtn = h("button", { type: "button", class: "admin-btn" }, "Flag selected");
    var clearBtn = h("button", { type: "button", class: "admin-link" }, "Clear");
    var bar = h("div", { class: "admin-bulk", hidden: true, role: "region", "aria-label": "Selected sentences" },
      count, approveBtn, h("label", { class: "admin-bulk-note" }, "Note ", noteBox), flagBtn, clearBtn);
    var all = h("input", { type: "checkbox", "aria-label": "Select every sentence listed" });
    function picked() { return boxes.filter(function (b) { return b.checked; }).map(function (b) { return b.value; }); }
    function update() {
      var n = picked().length;
      bar.hidden = !n;
      count.textContent = plural(n, "sentence") + " selected";
      all.checked = n > 0 && n === boxes.length;
      all.indeterminate = n > 0 && n < boxes.length;
    }
    function tickAll(on) { boxes.forEach(function (b) { b.checked = on; }); update(); }
    all.addEventListener("change", function () { tickAll(all.checked); });
    clearBtn.addEventListener("click", function () { tickAll(false); });
    function finished(verb) {
      return function (r) {
        FLASH = verb + " " + plural(r.applied, "sentence") + "." +
          (r.skipped ? " " + num(r.skipped) + " already approved, left as they were." : "");
        route();
      };
    }
    function send(body, button, done) {
      busy(button, true);
      body.layer = layerOf();
      return api("/api/admin/review/bulk/", { method: "POST", body: body }).then(done, function (e) {
        busy(button, false);
        note(status, e, true);
      });
    }
    approveBtn.addEventListener("click", function () { send({ action: "approve", records: picked() }, approveBtn, finished("Approved")); });
    flagBtn.addEventListener("click", function () {
      if (!noteBox.value.trim()) { note(status, "Say what is wrong in the note, then flag.", true); noteBox.focus(); return; }
      send({ action: "flag", note: noteBox.value, records: picked() }, flagBtn, finished("Flagged"));
    });
    function box(s) {
      var b = h("input", { type: "checkbox", value: s.record, "aria-label": "Select " + s.label });
      var i = boxes.length;
      boxes.push(b);
      b.addEventListener("click", function (e) {
        if (e.shiftKey && last >= 0 && last !== i) {
          for (var j = Math.min(last, i); j <= Math.max(last, i); j++) boxes[j].checked = b.checked;
        }
        last = i;
        update();
      });
      return h("td", { class: "admin-pick" }, b);
    }
    function rest(id, name) {
      var first = h("button", { type: "button", class: "admin-link" }, "Approve the rest of " + name + "…");
      var ask = h("span", { class: "admin-confirm-ask", hidden: true });
      first.addEventListener("click", function () {
        busy(first, true);
        // A dry run first: how many it would approve, saving nothing.
        api("/api/admin/review/bulk/", { method: "POST", body: { layer: layerOf(), action: "approve", chapter: id, dry_run: true } }).then(function (r) {
          busy(first, false);
          var n = r.results.filter(function (x) { return x.result === "would_apply"; }).length;
          if (!n) { note(status, "Nothing left to approve in " + name + ". Flagged sentences are left to review one by one."); return; }
          var yes = h("button", { type: "button", class: "admin-btn primary" }, "Approve " + plural(n, "sentence"));
          var no = h("button", { type: "button", class: "admin-btn" }, "Cancel");
          yes.addEventListener("click", function () { send({ action: "approve", chapter: id }, yes, finished("Approved")); });
          no.addEventListener("click", function () { ask.hidden = true; first.hidden = false; first.focus(); });
          ask.textContent = "";
          add(ask, [h("span", { class: "admin-sub" }, "Approve every sentence in " + name + " that isn't approved yet? Flagged ones are left."), yes, no]);
          first.hidden = true;
          ask.hidden = false;
          no.focus();
        }, function (e) { busy(first, false); note(status, e, true); });
      });
      return h("span", { class: "admin-confirm" }, first, ask);
    }
    // A heading row where the chapter changes, with its "approve the rest".
    function chapterRow(s) {
      var id = s.verse.split(".").slice(0, 2).join(".");
      if (id === chapter) return null;
      chapter = id;
      var name = s.label.replace(/:[^:]*$/, "");
      return h("tr", { class: "admin-group" }, h("th", { colspan: 5, scope: "rowgroup" }, h("span", null, name), " ", rest(id, name)));
    }
    return {
      bar: bar, box: box, chapterRow: chapterRow,
      head: function () { return h("th", { class: "admin-pick" }, all); },
      reset: function () { boxes = []; last = -1; chapter = null; update(); }
    };
  }
  function reviewQueue(layer) {
    var filters = REVIEW;
    var body = h("div");
    var more = h("button", { type: "button", class: "admin-btn", hidden: true }, "More");
    var offset = 0, d = null, rows = null;
    function query() {
      return "/api/admin/review/?layer=" + encodeURIComponent(layer) + "&book=" + filters.book + "&state=" + filters.state + "&offset=" + offset;
    }
    function draw(page) {
      if (!offset) {
        body.textContent = "";
        rows = h("tbody");
        pick.reset();
        var c = page.counts;
        body.appendChild(h("div", { class: "admin-tiles" },
          tile(num(c.not_reviewed), "not reviewed"), tile(num(c.approved), "approved", "good"),
          tile(num(c.changed), "changed since approval", c.changed ? "warn" : ""), tile(num(c.flagged), "flagged", c.flagged ? "bad" : "")));
        body.appendChild(page.sentences.length ? h("div", { class: "admin-scroll" }, h("table", { class: "admin-table" },
          h("thead", null, h("tr", null, pick.head(), h("th", null, "Sentence"), h("th", null, page.layer.kind === "meaning" ? "Literal gloss" : "Balanced"),
            h("th", null, "State"), h("th", null, "Last"))), rows)) : empty("Nothing here with these filters."));
      }
      if (!offset) QUEUE = { layer: page.layer.code, rows: [], more: false };
      QUEUE.more = page.more;
      page.sentences.forEach(function (s) {
        QUEUE.rows.push({ record: s.record, state: s.state });
        add(rows, pick.chapterRow(s));
        rows.appendChild(h("tr", null, pick.box(s),
          h("th", { scope: "row" }, h("a", { href: "#review/" + layer + "/" + s.record }, s.label), h("div", { class: "admin-sub" }, s.record)),
          h("td", { class: "admin-wrap", lang: page.layer.kind === "meaning" ? "en" : layer }, rendering(s.preview)),
          h("td", null, reviewPill(s.state)),
          h("td", null, h("span", { class: "admin-sub" }, s.last ? s.last.label + ", " + s.last.by + ", " + when(s.last.at) : "—"))));
      });
      more.hidden = !page.more;
    }
    function load() {
      busy(more, true);
      return api(query()).then(function (page) { d = d || page; layer = page.layer.code; draw(page); busy(more, false); return page; });
    }
    more.addEventListener("click", function () {
      offset += 50;
      later(more, load().catch(function (e) { offset -= 50; throw e; }));   // so trying again asks for the same page
    });
    var status = h("p", { class: "admin-note", role: "status" });
    var pick = queuePicker(function () { return layer; }, status);
    function refilter() { offset = 0; rememberTab("review.book", filters.book); rememberTab("review.state", filters.state); keepAddress(true); later(more, load()); }
    // A layer remembered from before may no longer be the account's.
    return load().catch(function (e) {
      if (e.status !== 403 || !layer) throw e;
      layer = "";
      return load();
    }).then(function () {
      rememberTab("review.layer", layer);
      REVIEW.layer = layer;
      keepAddress(false);
      var layerSel = d.layers.length > 1 ? select("review-layer", d.layers.map(function (l) { return [l.code, l.name]; }), layer) : null;
      if (layerSel) layerSel.addEventListener("change", function () { location.hash = "#review/" + layerSel.value; });
      var bookSel = select("review-book", [["", "Every book"]].concat(d.books.map(function (b) { return [b.code, b.name]; })), filters.book);
      bookSel.addEventListener("change", function () { filters.book = bookSel.value; refilter(); });
      var stateSel = select("review-state", [["todo", "To review"], ["", "Every sentence"], ["not_reviewed", "Not reviewed"],
        ["changed", "Changed since approval"], ["flagged", "Flagged"], ["approved", "Approved"]], filters.state);
      stateSel.addEventListener("change", function () { filters.state = stateSel.value; refilter(); });
      return [head("Text", "Review: " + d.layer.name, d.layer.kind === "meaning"
        ? "Check what the " + d.layer.books + " says: the literal gloss and the meaning decisions behind every language. Approving moves a sentence on from AI-assisted."
        : "Check how " + d.layer.name.replace(/ wording$/, "") + " says it, at every level, against the meaning. Each approval names you and holds until the wording changes."),
        h("div", { class: "admin-toolbar" }, layerSel ? h("label", null, "Layer ", layerSel) : null,
          h("label", null, "Book ", bookSel), h("label", null, "Show ", stateSel)),
        status, pick.bar, body, more];
    });
  }
  function reviewSentence(layer, record) {
    var drew = drawing;   // this drawing, for its keys
    return api("/api/admin/review/" + encodeURIComponent(record) + "/?layer=" + encodeURIComponent(layer)).then(function (d) {
      var r = d.record, kind = d.layer.kind;
      var names = {};
      d.languages.forEach(function (l) { names[l.code] = l.name; });
      var source = r.source.tokens.map(function (t) { return d.words[t]; });
      var dir = r.source.language === "hbo" ? "rtl" : null;
      var words = h("p", { class: "admin-source", lang: r.source.language, dir: dir }, source.length && source.every(Boolean)
        ? source.map(function (w) { return [h("span", { title: [w.lemma, w.gloss, w.morph].filter(Boolean).join(" · ") }, w.text), " "]; })
        : r.source.text);
      var langs = kind === "meaning" ? Object.keys(r.renderings) : [layer];
      var renderings = table(["Language", "Literal", "Balanced", "Readable"], langs.map(function (code) {
        return h("tr", null, h("th", { scope: "row" }, names[code] || code), ["L", "B", "R"].map(function (lv) {
          var t = r.renderings[code] && r.renderings[code][lv];
          return h("td", { class: "admin-wrap", lang: code }, t ? rendering(t) : "—");
        }));
      }), "admin-renderings");
      var meaning = r.decisions.filter(function (x) { return x.layer === "meaning"; });
      var mine = r.decisions.filter(function (x) { return x.layer !== "meaning" && x.language === layer; });
      var noteBox = h("textarea", { id: "review-note", rows: 3, maxlength: 4000,
        placeholder: "A note: what is wrong (needed to flag), or anything the next reviewer should know" });
      var status = h("p", { class: "admin-note", role: "status" });
      // Next and previous in the queue as listed (j, k); after approving
      // or flagging, the next one there that isn't approved, else the API's
      // next to review in the layer. Both are fetched ahead.
      var rows = QUEUE && QUEUE.layer === layer ? QUEUE.rows : null;
      var listed = rows ? C.step(rows, record, 0) === record : false;
      var after = listed ? C.step(rows, record, 1) || (QUEUE.more ? d.next : null) : d.next;
      var before = listed ? C.step(rows, record, -1) : null;
      function ahead(next) {
        var t = listed ? C.todo(rows, record, QUEUE.more) : undefined;
        return t === undefined ? next : t;
      }
      function sentencePath(rec) { return "/api/admin/review/" + encodeURIComponent(rec) + "/?layer=" + encodeURIComponent(layer); }
      var busyNow = false;
      function act(action, button) {
        if (busyNow) return;
        busyNow = true;
        busy(button, true);
        api("/api/admin/review/" + encodeURIComponent(record) + "/", { method: "POST", body: { layer: layer, action: action, note: noteBox.value } })
          .then(function (res) {
            if (listed && action !== "comment") rows.filter(function (x) { return x.record === record; })[0].state = res.state;
            var next = ahead(res.next);
            FLASH = { approve: "Approved ", flag: "Flagged ", comment: "Comment added to " }[action] + d.label + "." +
              (action !== "comment" && !next ? " That's the end of the queue." : "");
            if (action === "comment") route();
            else location.hash = next ? "#review/" + layer + "/" + next : "#review/" + layer;
          }, function (e) { busyNow = false; busy(button, false); note(status, e, true); });
      }
      var approveBtn = h("button", { type: "button", class: "admin-btn primary", onclick: function () { act("approve", this); } },
        kind === "meaning" ? "Approve the meaning" : "Approve the " + d.layer.name.replace(/ wording$/, "") + " wording");
      var flagBtn = h("button", { type: "button", class: "admin-btn", onclick: function () { act("flag", this); } }, "Flag a problem");
      var buttons = h("div", { class: "admin-actions" }, approveBtn, flagBtn,
        h("button", { type: "button", class: "admin-btn", onclick: function () { act("comment", this); } }, "Comment"),
        d.next ? h("a", { href: "#review/" + layer + "/" + d.next }, "Skip to the next ›") : null);
      // f: write what's wrong, then Ctrl or Cmd Enter flags it.
      var flagging = false;
      noteBox.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && flagging) { e.preventDefault(); act("flag", flagBtn); }
        else if (e.key === "Escape") { flagging = false; flagBtn.classList.remove("armed"); noteBox.blur(); }
      });
      var help = h("div", { class: "admin-keys-help", id: "review-keys", hidden: true },
        h("h3", { class: "admin-h3" }, "Keyboard shortcuts"),
        h("dl", null, [["a", "Approve, then open the next sentence to review"],
          ["f", "Flag a problem: write it in the note, then Ctrl Enter (⌘ Enter) to flag"],
          ["j", "Next sentence in the queue"], ["k", "Previous sentence in the queue"],
          ["/", "Search the admin"], ["?", "Show or hide these shortcuts"], ["Esc", "Leave the note"]].map(function (k) {
          return [h("dt", null, h("kbd", null, k[0])), h("dd", null, k[1])];
        })));
      function toggleHelp() { help.hidden = !help.hidden; helpBtn.setAttribute("aria-expanded", help.hidden ? "false" : "true"); }
      var helpBtn = h("button", { type: "button", class: "admin-link", "aria-controls": "review-keys", "aria-expanded": "false", onclick: toggleHelp }, "All shortcuts");
      var hint = h("p", { class: "admin-keys" }, "Keys: ", h("kbd", null, "a"), " approve · ", h("kbd", null, "f"), " flag · ",
        h("kbd", null, "j"), " / ", h("kbd", null, "k"), " next / previous · ", h("kbd", null, "/"), " search · ",
        h("kbd", null, "?"), " ", helpBtn);
      function go(rec, none) {
        if (rec) location.hash = "#review/" + layer + "/" + rec;
        else note(status, none);
      }
      KEYS = {
        at: drew,
        a: function () { if (!approveBtn.disabled) act("approve", approveBtn); },
        f: function () {
          flagging = true;
          flagBtn.classList.add("armed");
          noteBox.focus();
          note(status, "Say what is wrong in the note, then press Ctrl Enter (⌘ Enter) or Flag a problem.");
        },
        j: function () { go(after, "That's the last sentence in the queue."); },
        k: function () { go(before, listed ? "That's the first sentence in the queue." : "Open this sentence from the queue to step back through it."); },
        "?": toggleHelp,
        Escape: function () { if (!help.hidden) toggleHelp(); }
      };
      // While the reviewer reads this one, fetch the sentences they are
      // likely to open next, so approving (or j) draws at once.
      setTimeout(function () {
        if (drew !== drawing) return;
        [ahead(d.next), after].forEach(function (rec, i, all) {
          if (rec && all.indexOf(rec) === i) api(sentencePath(rec), { quiet: true }).catch(function () { /* drawn with its error if opened */ });
        });
      }, 200);
      var trail = d.trail.length ? h("ul", { class: "admin-feed" }, d.trail.map(function (e) {
        return h("li", null, h("time", { datetime: e.at, title: new Date(e.at).toLocaleString("en-GB") }, when(e.at)),
          h("span", null, h("strong", null, e.by), " " + e.label.toLowerCase() + " (" + (e.language ? names[e.language] || e.language : "meaning") + ")",
            e.changed ? [" ", pill("changed since", "warn")] : null, e.note ? h("span", { class: "admin-sub" }, ": " + e.note) : null));
      })) : empty("No one has reviewed this sentence yet.");
      return [head("Review: " + d.layer.name, d.label, r.id + " · " + (r.status === "ai_draft" ? "AI-assisted" : r.status.replace(/_/g, " "))),
        h("div", { class: "admin-actions" }, h("a", { href: "#review/" + layer }, "‹ The queue"),
          d.layers.length > 1 ? d.layers.filter(function (l) { return l.code !== layer; }).map(function (l) {
            return h("a", { href: "#review/" + l.code + "/" + record }, l.name);
          }) : null,
          h("a", { href: "#verse/" + d.verse }, ME.admin.indexOf("inbox") >= 0 ? "Request a fix in the verse inspector" : "Verse inspector")),
        h("section", { class: "admin-block admin-record" }, h("header", { class: "admin-toolbar" }, h("h2", null, "State"), reviewPill(d.state)),
          words, h("p", { class: "admin-gloss" }, "Literal gloss: " + r.literal_gloss), renderings,
          meaning.length ? [h("h3", { class: "admin-h3" }, "Meaning decisions"), h("div", { class: "admin-decisions" }, meaning.map(decision))] : null,
          mine.length ? [h("h3", { class: "admin-h3" }, (names[layer] || layer) + " decisions"), h("div", { class: "admin-decisions" }, mine.map(decision))] : null),
        h("section", { class: "admin-block" }, h("h2", null, "Your review"), h("label", { class: "admin-field" }, "Note", noteBox), buttons, status, hint, help),
        h("section", { class: "admin-block" }, h("h2", null, "Review trail"), trail)];
    });
  }

  // My review: a reviewer's workspace for one layer (GET
  // /api/admin/review/workspace/). Each item links to the view that deals
  // with it: the queue (a book's sentences to review), the sentence, the
  // verse inspector, Checks.
  var STANDING = { overdue: ["Overdue", "bad"], open: ["Open", "info"], done: ["Done", "good"], closed: ["Closed", ""] };
  function standingPill(a) { return pill(STANDING[a.standing][0], STANDING[a.standing][1]); }
  function dueText(a) {
    if (!a.due) return "No date";
    var d = "Due " + date(a.due + "T12:00:00");
    if (a.standing === "closed" || a.standing === "done") return d;
    return d + (a.days_left < 0 ? " (" + plural(-a.days_left, "day") + " late)" : a.days_left === 0 ? " (today)" : " (" + plural(a.days_left, "day") + " left)");
  }
  function progressText(p) { return num(p.approved) + " of " + num(p.total) + " approved"; }
  // A link to the layer's review queue, showing one book (or every book)
  // and one state.
  function queueLink(layer, book, state, text) {
    return h("a", { href: "#review/" + layer, onclick: function () { rememberTab("review.book", book); rememberTab("review.state", state); } }, text);
  }
  VIEWS.workspace = function (arg) {
    var layer = arg || sessionTab("review.layer", "");
    function load() { return api("/api/admin/review/workspace/?layer=" + encodeURIComponent(layer)); }
    // A layer remembered from before may no longer be the account's.
    return load().catch(function (e) {
      if (e.status !== 403 || !layer) throw e;
      layer = "";
      return load();
    }).then(function (d) {
      layer = d.layer.code;
      rememberTab("review.layer", layer);
      var c = d.counts, ch = d.changes;
      var names = {};
      d.books.forEach(function (b) { names[b.code] = b.name; });
      var layerSel = d.layers.length > 1 ? select("workspace-layer", d.layers.map(function (l) { return [l.code, l.name]; }), layer) : null;
      if (layerSel) layerSel.addEventListener("change", function () { location.hash = "#workspace/" + layerSel.value; });
      var out = [head("Text", "My review: " + d.layer.name, "Where your layer stands, what is assigned to you, your open flags, what has changed since you approved it, and what the checks found in the books in progress."),
        h("div", { class: "admin-toolbar" }, layerSel ? h("label", null, "Layer ", layerSel) : h("span"),
          queueLink(layer, "", "todo", "Open the queue ›")),
        h("div", { class: "admin-tiles" }, tile(num(c.not_reviewed), "not reviewed"), tile(num(c.approved), "approved", "good"),
          tile(num(c.changed), "changed since approval", c.changed ? "warn" : ""), tile(num(c.flagged), "flagged", c.flagged ? "bad" : ""))];

      out.push(h("section", { class: "admin-block" }, h("h2", null, "Assigned to you"),
        d.assignments.length ? table(["Range", "Progress", "Due", "Standing"], d.assignments.map(function (a) {
          return h("tr", null,
            h("th", { scope: "row" }, queueLink(layer, a.book, "todo", a.label), a.note ? h("div", { class: "admin-sub" }, a.note) : null,
              a.assigned_by ? h("div", { class: "admin-sub" }, "From " + a.assigned_by.name + ", " + date(a.created_at)) : null),
            h("td", null, bar(a.progress.approved, a.progress.total), h("div", { class: "admin-sub" }, progressText(a.progress))),
            h("td", null, dueText(a)),
            h("td", null, standingPill(a)));
        })) : empty("Nothing is assigned to you in this layer.")));

      out.push(h("section", { class: "admin-block" }, h("h2", null, "Your open flags"),
        d.flags.length ? h("ul", { class: "admin-feed" }, d.flags.map(function (f) {
          return h("li", null, h("time", { datetime: f.at, title: new Date(f.at).toLocaleString("en-GB") }, when(f.at)), h("span", null,
            h("a", { href: "#review/" + layer + "/" + f.record }, f.label), " ", h("span", { class: "admin-sub" }, f.record), " · ",
            h("a", { href: "#verse/" + f.verse }, "Verse inspector"), h("br"), f.note));
        })) : h("p", { class: "admin-ok" }, "You have no open flags in this layer.")));

      out.push(h("section", { class: "admin-block" }, h("h2", null, "Changed since you approved"),
        h("p", { class: "admin-sub" }, ch.last_approval ? "Your last approval in this layer was " + when(ch.last_approval) + "." : "You haven't approved anything in this layer yet."),
        ch.items.length ? ch.items.map(function (a) {
          return [sinceApproval(a, true), h("p", null, h("a", { href: "#review/" + layer + "/" + a.record }, "Review " + a.label + " again ›"))];
        }) : h("p", { class: "admin-ok" }, "Nothing you approved has changed since."),
        ch.total > ch.items.length ? h("p", null, "The latest " + ch.items.length + " of " + num(ch.total) + ". ",
          queueLink(layer, "", "changed", "All of them in the queue")) : null));

      if (d.checks) out.push(workspaceChecks(d.checks, d.in_progress, names));

      out.push(h("section", { class: "admin-block" }, h("h2", null, "Book by book"),
        d.books.length ? table(["Book", "Approved", ["Not reviewed", { class: "admin-num" }], ["Changed", { class: "admin-num" }], ["Flagged", { class: "admin-num" }]],
          d.books.map(function (b) {
            var k = b.counts;
            return h("tr", null,
              h("th", { scope: "row" }, queueLink(layer, b.code, "todo", b.name), d.in_progress.indexOf(b.code) >= 0 ? [" ", pill("in progress", "info")] : null),
              h("td", null, bar(k.approved, k.total), h("span", { class: "admin-sub" }, " " + num(k.approved) + " / " + num(k.total))),
              h("td", { class: "admin-num" }, num(k.not_reviewed)), h("td", { class: "admin-num" }, num(k.changed)), h("td", { class: "admin-num" }, num(k.flagged)));
          })) : empty("Nothing in this layer has been drafted yet.")));
      return out;
    });
  };
  // The language's Checks hits (GET /api/admin/checks/, kept as Checks keeps
  // it) in the books in progress, fetched once the workspace is drawn.
  function workspaceChecks(lang, books, names) {
    var title = "Checks in the books in progress";
    var box = h("section", { class: "admin-block" }, h("h2", null, title), h("p", { class: "admin-sub" }, "Loading the checks…"));
    function toChecks() { CHECKS.lang = lang; CHECKS.kind = "all"; }
    function list(heading, hits, describe) {
      if (!hits.length) return null;
      return [h("h3", { class: "admin-h3" }, heading + " (" + num(hits.length) + ")"), h("ul", { class: "admin-feed" }, hits.slice(0, 25).map(function (x) {
        return h("li", null, h("span", null, h("a", { href: "#verse/" + x.verse }, x.label), " ", h("span", { class: "admin-sub" }, x.record), " · ", describe(x)));
      })), hits.length > 25 ? h("p", { class: "admin-sub" }, "And " + num(hits.length - 25) + " more in Checks.") : null];
    }
    api("/api/admin/checks/?lang=" + encodeURIComponent(lang)).then(function (c) {
      function inBooks(x) { return books.indexOf(x.verse.split(".")[0]) >= 0; }
      var notes = c.notes.hits.filter(inBooks), verses = c.glossary.verses.hits.filter(inBooks);
      box.textContent = "";
      add(box, [h("h2", null, title),
        h("p", { class: "admin-sub" }, books.length ? "In " + books.map(function (b) { return names[b] || b; }).join(", ") + ". " : "No book is in progress in this layer yet. ",
          h("a", { href: "#checks", onclick: toChecks }, "Every check in this language ›")),
        list("Footnotes and verses at odds", notes, function (x) {
          return [CHECK_KINDS[x.kind] || x.kind, ": ", h("span", { lang: lang }, x.choice)];
        }),
        list("Verses at odds with the terms glossary", verses, function (x) {
          return [x.kind === "avoided" ? "Ruled out" : "Alternative only", ": ", h("b", { lang: lang }, x.form), " for “" + x.term + "”"];
        }),
        c.glossary.rows.length ? h("p", null, plural(c.glossary.rows.length, "glossary entry", "glossary entries") + " conflict with another. ",
          h("a", { href: "#checks", onclick: toChecks }, "See them in Checks")) : null,
        books.length && !notes.length && !verses.length ? h("p", { class: "admin-ok" }, "No footnote or glossary mismatches in these books.") : null]);
    }, function (e) { box.textContent = ""; add(box, [h("h2", null, title), h("p", { class: "notice" }, e.message)]); });
    return box;
  }

  // Review assignments (staff/assignments.py): an editor or super admin
  // gives a reviewer a book, or some of its chapters, in a layer they
  // review, by a date or not. On their own page and in Team & access.
  function assignmentsManager(d, status) {
    var people = d.reviewers || [];
    var reviewerSel = select("assign-reviewer", people.map(function (p) {
      return [String(p.id), p.name === p.email ? p.email : p.name + " (" + p.email + ")"];
    }), people.length ? String(people[0].id) : "");
    var layerSel = h("select", { id: "assign-layer" });
    var bookSel = h("select", { id: "assign-book" });
    var from = h("input", { type: "number", id: "assign-from", min: 1, placeholder: "Whole book" });
    var to = h("input", { type: "number", id: "assign-to", min: 1, placeholder: "To the end" });
    var due = h("input", { type: "date", id: "assign-due" });
    var noteBox = h("input", { type: "text", id: "assign-note", maxlength: 2000, placeholder: "Anything the reviewer should know" });
    function person() { return people.filter(function (p) { return String(p.id) === reviewerSel.value; })[0]; }
    function books() {
      var was = bookSel.value, code = layerSel.value;
      bookSel.textContent = "";
      d.books.filter(function (b) { return code === "grc" ? b.testament === "nt" : code === "hbo" ? b.testament === "ot" : true; }).forEach(function (b) {
        bookSel.appendChild(h("option", { value: b.code, selected: b.code === was }, b.name));
      });
    }
    function layers() {
      var p = person(), was = layerSel.value;
      layerSel.textContent = "";
      d.layers.filter(function (l) { return p && (p.layers === "any" || p.layers.indexOf(l.code) >= 0); }).forEach(function (l) {
        layerSel.appendChild(h("option", { value: l.code, selected: l.code === was }, l.name));
      });
      books();
    }
    reviewerSel.addEventListener("change", layers);
    layerSel.addEventListener("change", books);
    layers();
    var submit = h("button", { type: "submit", class: "admin-btn primary", disabled: !people.length }, "Assign");
    var form = h("form", { class: "admin-form" },
      h("label", { class: "admin-field", for: "assign-reviewer" }, "Reviewer", reviewerSel),
      h("label", { class: "admin-field", for: "assign-layer" }, "Layer", layerSel),
      h("label", { class: "admin-field", for: "assign-book" }, "Book", bookSel),
      h("label", { class: "admin-field", for: "assign-from" }, "From chapter", from),
      h("label", { class: "admin-field", for: "assign-to" }, "To chapter", to),
      h("label", { class: "admin-field", for: "assign-due" }, "Due (optional)", due),
      h("label", { class: "admin-field", for: "assign-note" }, "Note", noteBox), submit);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      busy(submit, true);
      api("/api/admin/assignments/", { method: "POST", body: { assignee: Number(reviewerSel.value), layer: layerSel.value, book: bookSel.value,
        chapter_from: from.value, chapter_to: to.value, due: due.value, note: noteBox.value } }).then(function (r) {
        var a = r.assignment;
        FLASH = "Assigned " + a.label + " (" + a.layer.name + ") to " + a.assignee.name + ".";
        route();
      }, function (err) { busy(submit, false); note(status, err, true); });
    });
    function patch(a, body, button) {
      return api("/api/admin/assignments/" + a.id + "/", { method: "PATCH", body: body }).then(route, function (e) {
        if (button) busy(button, false);
        note(status, e, true);
      });
    }
    function row(a) {
      var dueIn = h("input", { type: "date", value: a.due || "", "aria-label": "Due date for " + a.label });
      dueIn.addEventListener("change", function () { patch(a, { due: dueIn.value }); });
      var close = h("button", { type: "button", class: "admin-link" }, a.closed_at ? "Reopen" : "Close");
      close.addEventListener("click", function () { busy(close, true); patch(a, { closed: !a.closed_at }, close); });
      return h("tr", null,
        h("td", null, a.assignee.name, a.assignee.name !== a.assignee.email ? h("div", { class: "admin-sub" }, a.assignee.email) : null),
        h("td", null, a.layer.name),
        h("td", null, a.label, a.note ? h("div", { class: "admin-sub" }, a.note) : null),
        h("td", null, bar(a.progress.approved, a.progress.total), h("div", { class: "admin-sub" }, progressText(a.progress))),
        h("td", null, dueIn, a.due && a.standing !== "closed" && a.standing !== "done" ? h("div", { class: "admin-sub" }, dueText(a)) : null),
        h("td", null, standingPill(a)),
        h("td", null, close, " ", confirmButton("Remove", "Remove this assignment?", function (b) {
          api("/api/admin/assignments/" + a.id + "/", { method: "DELETE" }).then(route, function (e) { busy(b, false); note(status, e, true); });
        }, "admin-link")));
    }
    return {
      form: people.length ? form : empty("No one reviews yet: grant a scholar or language reviewer role in Team & access first."),
      list: d.assignments.length ? table(["Reviewer", "Layer", "Range", "Progress", "Due", "Standing", ""], d.assignments.map(row))
        : empty("No review assignments.")
    };
  }
  VIEWS.assignments = function () {
    var closed = sessionTab("assignments.closed", "") === "1";
    return api("/api/admin/assignments/" + (closed ? "?closed=1" : "")).then(function (d) {
      var status = h("p", { class: "admin-note", role: "status" });
      var m = assignmentsManager(d, status);
      var toggle = h("label", null, h("input", { type: "checkbox", checked: closed, onchange: function () {
        rememberTab("assignments.closed", this.checked ? "1" : "");
        route();
      } }), " Show closed ones");
      return [head("Text", "Review assignments", "Give a reviewer a book, or some of its chapters, in the layer they review, by a date if there is one. An assignment is done when every sentence in it is approved, and overdue when its date passes first. Reviewers see theirs in My review and on the dashboard."),
        h("section", { class: "admin-block" }, h("h2", null, "Assign"), m.form, status),
        h("section", { class: "admin-block" }, h("header", { class: "admin-toolbar" }, h("h2", null, "Assignments"), toggle), m.list)];
    });
  };
  // The open assignments in Team & access, fetched once it is drawn.
  function teamAssignments() {
    var box = h("section", { class: "admin-block" }, h("h2", null, "Review assignments"), h("p", { class: "admin-sub" }, "Loading the assignments…"));
    api("/api/admin/assignments/").then(function (d) {
      var status = h("p", { class: "admin-note", role: "status" });
      var m = assignmentsManager(d, status);
      box.textContent = "";
      add(box, [h("h2", null, "Review assignments"),
        h("p", { class: "admin-sub" }, "Open assignments, overdue first. ", h("a", { href: "#assignments" }, "Closed ones are in Review assignments.")),
        m.list, h("details", null, h("summary", null, "Assign review"), m.form), status]);
    }, function (e) { box.textContent = ""; add(box, [h("h2", null, "Review assignments"), h("p", { class: "notice" }, e.message)]); });
    return box;
  }

  // Reviewer flags: problems reviewers have raised, open until the layer is
  // approved again. Editors act on them with a fix request.
  VIEWS.flags = function () {
    return api("/api/admin/review/flags/").then(function (d) {
      var reviews = ME.admin.indexOf("review") >= 0;
      return [head("Text", "Reviewer flags", "Problems reviewers have flagged, newest first. A flag stays open until the layer is approved again; request a fix from the verse inspector."),
        d.flags.length ? h("ul", { class: "admin-feed" }, d.flags.map(function (f) {
          return h("li", null, h("time", { datetime: f.at }, when(f.at)), h("span", null,
            h("a", { href: "#verse/" + f.verse }, f.label), " ", h("span", { class: "admin-sub" }, f.record + " · " + f.layer.name),
            reviews ? [" ", h("a", { href: "#review/" + f.layer.code + "/" + f.record }, "Review")] : null,
            h("br"), h("strong", null, f.by), ": " + f.note));
        })) : h("p", { class: "admin-ok" }, "No open flags.")];
    });
  };

  // Changes: what each import (each deploy) changed in sentences already
  // drafted, word by word.
  function wordDiff(before, after) {
    var a = before.split(/(\s+)/), b = after.split(/(\s+)/);
    var n = a.length, m = b.length, i, j;
    var lcs = [];
    for (i = 0; i <= n; i++) { lcs.push(new Array(m + 1).fill(0)); }
    for (i = n - 1; i >= 0; i--) for (j = m - 1; j >= 0; j--) {
      lcs[i][j] = a[i] === b[j] ? lcs[i + 1][j + 1] + 1 : Math.max(lcs[i + 1][j], lcs[i][j + 1]);
    }
    var out = h("span", { class: "admin-diff" });
    i = 0; j = 0;
    while (i < n || j < m) {
      if (i < n && j < m && a[i] === b[j]) { add(out, a[i]); i++; j++; }
      else if (i < n && (j === m || lcs[i + 1][j] >= lcs[i][j + 1])) { out.appendChild(h("del", null, a[i])); i++; }
      else { out.appendChild(h("ins", null, b[j])); j++; }
    }
    return out;
  }
  var CHANGE_KIND = { added: ["added", "good"], changed: ["changed", "info"], removed: ["removed", "bad"] };
  VIEWS.changes = function (runId) {
    var filters = { lang: "", book: "" };
    return api("/api/admin/changes/" + (runId ? "?run=" + encodeURIComponent(runId) : "")).then(function (d) {
      var names = {};
      d.languages.forEach(function (l) { names[l.code] = l.name; });
      function drafted(counts) {
        return Object.keys(counts).map(function (c) { return (names[c] || c) + " " + num(counts[c]); }).join(", ");
      }
      var runs = table(["Import", ["Files", { class: "admin-num" }], ["Changed renderings", { class: "admin-num" }], "Drafted for the first time"],
        d.runs.map(function (r) {
          return h("tr", { "aria-current": d.run && d.run.id === r.id ? "true" : null },
            h("th", { scope: "row" }, h("a", { href: "#changes/" + r.id }, when(r.started_at)), r.error ? [" ", pill("failed", "bad")] : null),
            h("td", { class: "admin-num" }, num(r.files)), h("td", { class: "admin-num" }, num(r.changed)),
            h("td", { class: "admin-sub" }, drafted(r.drafted) || "—"));
        }));
      var out = [head("Progress", "Changes", "What each deploy's import changed in sentences already drafted, before and after. A sentence drafted in a language for the first time is only counted."),
        h("section", { class: "admin-block" }, h("h2", null, "Imports"), d.runs.length ? runs : empty("No imports yet."))];
      if (!d.run) {
        out.push(empty("No import has changed a drafted sentence yet."));
        return out;
      }
      var run = d.run, list = h("div"), offset = 0;
      var more = h("button", { type: "button", class: "admin-btn", hidden: !d.more }, "More");
      function draw(changes) {
        var byRecord = {}, order = [];
        changes.forEach(function (c) {
          if (!byRecord[c.record]) { byRecord[c.record] = []; order.push(c.record); }
          byRecord[c.record].push(c);
        });
        order.forEach(function (rec) {
          var first = byRecord[rec][0];
          list.appendChild(h("section", { class: "admin-block" },
            h("header", { class: "admin-toolbar" }, h("h3", { class: "admin-h3" }, h("a", { href: "#verse/" + first.verse }, first.label)), h("span", { class: "admin-sub" }, rec)),
            table(["Language", "Level", "Change"], byRecord[rec].map(function (c) {
              return h("tr", null, h("th", { scope: "row" }, names[c.language] || c.language), h("td", null, LEVEL_NAMES[c.level] || c.level),
                h("td", { class: "admin-wrap", lang: c.language }, pill(CHANGE_KIND[c.kind][0], CHANGE_KIND[c.kind][1]), " ",
                  c.kind === "changed" ? wordDiff(c.before, c.after) : c.kind === "added" ? c.after : h("del", null, c.before)));
            }))));
        });
        if (!changes.length && !offset) list.appendChild(empty("No changes with these filters."));
      }
      function load() {
        busy(more, true);
        var q = "?run=" + run.id + "&lang=" + filters.lang + "&book=" + filters.book + "&offset=" + offset;
        return api("/api/admin/changes/" + q).then(function (page) { draw(page.changes); more.hidden = !page.more; busy(more, false); });
      }
      more.addEventListener("click", function () {
      offset += 100;
      later(more, load().catch(function (e) { offset -= 100; throw e; }));   // so trying again asks for the same page
    });
      var langSel = select("changes-lang", [["", "Every language"]].concat(d.languages.map(function (l) { return [l.code, l.name]; })), "");
      var bookSel = select("changes-book", [["", "Every book"]].concat(run.books.map(function (b) { return [b.code, b.name + " (" + b.changes + ")"]; })), "");
      [langSel, bookSel].forEach(function (sel) {
        sel.addEventListener("change", function () { filters.lang = langSel.value; filters.book = bookSel.value; offset = 0; list.textContent = ""; later(more, load()); });
      });
      draw(d.changes);
      out.push(h("section", { class: "admin-block" }, h("h2", null, "Import of " + date(run.started_at) + ": " + plural(run.changed, "changed rendering")),
        run.drafted_books.length ? h("p", { class: "admin-sub" }, "Drafted for the first time: " + run.drafted_books.map(function (b) {
          return b.name + " (" + drafted(b.languages) + ")";
        }).join("; ") + ".") : null,
        h("div", { class: "admin-toolbar" }, h("label", null, "Language ", langSel), h("label", null, "Book ", bookSel))), list, more);
      return out;
    });
  };

  // History (staff/history.py): what has changed since a reviewer approved
  // a sentence, and release notes for one language. The server makes the
  // word diffs; they are drawn here as text, with <ins> and <del>.
  function diffView(segments) {
    return h("span", { class: "admin-diff" }, segments.map(function (s) {
      return s.op === "ins" ? h("ins", null, rendering(s.text)) : s.op === "del" ? h("del", null, rendering(s.text)) : rendering(s.text);
    }));
  }
  var KNOWN = { snapshot: "", unchanged: "", reconstructed: "Worked out from the imports since: this approval is older than the kept text.",
    unknown: "Approved before approvals kept their text: only that something has changed is known." };
  function sinceApproval(a, withVerse) {
    var changedTexts = a.texts.filter(function (t) { return t.changed; });
    var dec = a.decisions, decText = dec ? ["added", "changed", "removed"].filter(function (k) { return dec[k].length; }).map(function (k) {
      return "decisions " + k + ": " + dec[k].join(", ");
    }).join("; ") : "";
    var lang = a.layer.kind === "wording" ? a.layer.code : null;
    return h("div", { class: "admin-block" },
      h("p", null, h("time", { datetime: a.at, title: new Date(a.at).toLocaleString("en-GB") }, when(a.at)), " ",
        withVerse ? [h("a", { href: "#verse/" + a.verse }, a.label), " "] : null,
        h("strong", null, a.by), " approved " + a.layer.name.replace(/^Meaning/, "the meaning") + " ",
        a.changed ? pill("changed since", "warn") : pill("unchanged since", "good"),
        a.note ? h("span", { class: "admin-sub" }, ": " + a.note) : null),
      KNOWN[a.known] ? h("p", { class: "admin-sub" }, KNOWN[a.known]) : null,
      changedTexts.length ? table(["Level", "Approved → now"], changedTexts.map(function (t) {
        return h("tr", null, h("th", { scope: "row" }, t.name), h("td", { class: "admin-wrap", lang: lang }, diffView(t.segments)));
      }), "admin-renderings") : null,
      a.changed && a.known !== "unknown" && !changedTexts.length ? h("p", { class: "admin-sub" }, "The text is the same; " + (decText || "its decisions have changed") + ".") : null,
      changedTexts.length && decText ? h("p", { class: "admin-sub" }, "Also " + decText + ".") : null);
  }
  function approvalHistory(vid) {
    var box = h("section", { class: "admin-block" }, h("h2", null, "Since approval"), h("p", { class: "admin-sub" }, "Loading the approvals…"));
    api("/api/admin/history/verse/" + encodeURIComponent(vid) + "/").then(function (d) {
      box.textContent = "";
      box.appendChild(h("h2", null, "Since approval"));
      var any = false;
      d.sentences.forEach(function (s) {
        if (!s.approvals.length) return;
        any = true;
        box.appendChild(h("h3", { class: "admin-h3" }, s.record));
        s.approvals.forEach(function (a) { box.appendChild(sinceApproval(a, false)); });
      });
      if (!any) box.appendChild(empty("No reviewer has approved these sentences yet."));
    }, function (e) { box.textContent = ""; box.appendChild(h("p", { class: "notice" }, e.message)); });
    return box;
  }
  function approvalLog() {
    var list = h("div");
    var more = h("button", { type: "button", class: "admin-btn", hidden: true }, "Older approvals");
    var last = null;
    function load() {
      busy(more, true);
      api("/api/admin/history/approvals/" + (last ? "?before=" + last : "")).then(function (d) {
        if (d.approvals.length) last = d.approvals[d.approvals.length - 1].id;
        d.approvals.forEach(function (a) { list.appendChild(sinceApproval(a, true)); });
        if (!list.childNodes.length) list.appendChild(empty("No approvals yet."));
        more.hidden = !d.more;
        busy(more, false);
      }, function (e) { busy(more, false); list.appendChild(h("p", { class: "notice" }, e.message)); });
    }
    more.addEventListener("click", load);
    load();
    return h("section", { class: "admin-block" }, h("h2", null, "Approvals"),
      h("p", { class: "admin-sub" }, "Reviewers' approvals, newest first, and what has changed in each sentence since, word by word."), list, more);
  }

  // Release notes: what changed in one language since a date.
  var RELEASES = { lang: "en", since: "", until: "" };
  VIEWS.releases = function () {
    var f = RELEASES;
    if (!f.since) f.since = new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10);
    return api("/api/admin/export/").then(function (opts) {
      var langSel = select("releases-lang", opts.languages.map(function (l) { return [l.code, l.name]; }), f.lang);
      var since = h("input", { type: "date", id: "releases-since", value: f.since, required: true });
      var until = h("input", { type: "date", id: "releases-until", value: f.until });
      var show = h("button", { type: "submit", class: "admin-btn primary" }, "Show");
      var download = h("button", { type: "button", class: "admin-btn" }, "Download Markdown");
      var status = h("p", { class: "admin-note", role: "status" });
      var result = h("div");
      function query() {
        f.lang = langSel.value; f.since = since.value; f.until = until.value;
        return "?lang=" + encodeURIComponent(f.lang) + "&since=" + encodeURIComponent(f.since) + (f.until ? "&until=" + encodeURIComponent(f.until) : "");
      }
      function listed(items, line) { return h("ul", { class: "admin-feed" }, items.map(line)); }
      function drawNotes(d) {
        result.textContent = "";
        var t = d.totals;
        result.appendChild(h("div", { class: "admin-tiles" }, tile(num(t.drafted), "sentences drafted"), tile(num(t.renderings), "renderings changed"),
          tile(num(t.decisions), "decisions added or changed"), tile(num(t.footnotes), "footnotes added"), tile(num(d.imports), "imports")));
        if (!d.books.length) { result.appendChild(empty("Nothing changed in " + d.language.name + " in that time.")); return; }
        d.books.forEach(function (b) {
          var cut = ["added", "renderings", "decisions", "footnotes"].some(function (k) { return b.counts[k] > b[k].length; });
          result.appendChild(h("section", { class: "admin-block" }, h("h2", null, b.name),
            b.drafted || b.counts.added ? h("p", null, h("strong", null, plural(b.drafted || b.counts.added, "sentence") + " drafted"),
              b.added_verses ? h("span", { class: "admin-sub" }, " (" + b.added_verses + ")") : null) : null,
            b.renderings.length ? [h("h3", { class: "admin-h3" }, plural(b.counts.renderings, "rendering") + " changed"),
              table(["Verse", "Level", "Change"], b.renderings.map(function (r) {
                return h("tr", null, h("th", { scope: "row" }, h("a", { href: "#verse/" + r.verse }, r.label)), h("td", null, r.name),
                  h("td", { class: "admin-wrap", lang: d.language.code }, pill(CHANGE_KIND[r.kind][0], CHANGE_KIND[r.kind][1]), " ", diffView(r.segments)));
              }))] : null,
            b.decisions.length ? [h("h3", { class: "admin-h3" }, plural(b.counts.decisions, "decision") + " added, changed or removed"),
              listed(b.decisions, function (x) {
                return h("li", null, h("a", { href: "#verse/" + x.verse }, x.label), h("span", null, h("code", null, x.key), " " + x.layer + " decision " + x.kind + ": ",
                  h("strong", null, x.choice), x.was && x.was !== x.choice ? h("span", { class: "admin-sub" }, " (was: " + x.was + ")") : null,
                  x.fields.length ? h("span", { class: "admin-sub" }, " · " + x.fields.join(", ")) : null));
              })] : null,
            b.footnotes.length ? [h("h3", { class: "admin-h3" }, plural(b.counts.footnotes, "footnote") + " added"),
              listed(b.footnotes, function (x) {
                return h("li", null, h("a", { href: "#verse/" + x.verse }, x.label), h("span", null, h("code", null, x.key), " ", h("strong", null, x.choice),
                  h("span", { class: "admin-sub" }, ": " + x.reason)));
              })] : null,
            cut ? h("p", { class: "admin-sub" }, "The first " + d.shown + " of each are shown; the Markdown file has them all.") : null));
        });
      }
      var form = h("form", { class: "admin-form stacked" },
        h("label", { class: "admin-field", for: "releases-lang" }, "Language", langSel),
        h("label", { class: "admin-field", for: "releases-since" }, "Since", since),
        h("label", { class: "admin-field", for: "releases-until" }, "Until (optional, inclusive)", until),
        h("div", { class: "admin-actions" }, show, download), status);
      function showNotes() {
        busy(show, true);
        note(status, "Reading the imports…");
        api("/api/admin/history/release-notes/" + query()).then(function (d) { note(status, ""); drawNotes(d); },
          function (err) { note(status, err, true); }).then(function () { busy(show, false); });
      }
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        showNotes();
        keepAddress(true);
      });
      // A shared address (#releases?lang=fr&since=...) shows its notes at once.
      if (N.parse(location.hash).query) showNotes();
      download.addEventListener("click", function () {
        busy(download, true);
        saveFile("/api/admin/history/release-notes/" + query() + "&file=md").then(function (name) { note(status, "Saved " + name + "."); },
          function (err) { note(status, err, true); }).then(function () { busy(download, false); });
      });
      return [head("Text", "Release notes", "What changed in one language between two dates, from what each deploy's import recorded: sentences drafted, renderings changed word by word, decisions added or changed, and footnotes added, by book. Nothing here changes a sentence's review state."),
        h("p", { class: "notice" }, "Every sentence is an AI-assisted draft until a named reviewer approves it. Imports before release notes existed recorded rendering changes and how many sentences were drafted, but not which sentences or decisions."),
        form, result];
    });
  };

  // ---- Filters kept in the address -------------------------------------

  var COVERAGE = { testament: sessionTab("coverage", "nt") };
  filtered("coverage", COVERAGE, { testament: "nt" });
  filtered("review", REVIEW, { layer: "", book: "", state: "todo" }, function (arg, f) {
    if (arg.indexOf("/") >= 0) return arg;   // a sentence: #review/grc/JHN.1.1.s1
    f.layer = arg;
    return "";
  });
  filtered("inbox", INBOX, null, function (arg, f) {
    if (arg !== "mine") return arg;
    f.assigned = "me";
    return "";
  });
  filtered("users", USERS);
  filtered("decisions", DECISIONS);
  filtered("checks", CHECKS);
  filtered("consistency", CONSISTENCY);
  filtered("articles", ARTICLES);
  filtered("work", WORK);
  filtered("overlap", OVERLAP, null, function (arg, f) {
    f.book = arg.toUpperCase();
    return "";
  });
  filtered("export", EXPORT, { lang: "en", level: "B", type: "usfm", numbering: "english", books: "" });
  filtered("releases", RELEASES);

  // ---- Start ---------------------------------------------------------

  function signedOut() {
    try { localStorage.removeItem(KEY); } catch (x) { /* none */ }
    forgetAll();
    stop("Sign in again", "Your sign-in on this device has ended.", ["/login/?redirect=/admin/", "Sign in"]);
  }

  function stop(title, text, link) {
    drawing++;
    KEYS = null;
    window.removeEventListener("hashchange", navigated);
    window.removeEventListener("popstate", navigated);
    main.classList.remove("admin-stale");
    rail.hidden = true;
    main.removeAttribute("aria-busy");
    main.textContent = "";
    main.appendChild(head("Admin", title, text));
    if (link) main.appendChild(h("p", null, h("a", { class: "button", href: link[0] }, link[1])));
  }

  var account = saved();
  if (!account || !account.token) {
    forgetAll();
    stop("Sign in to use the admin", "The admin is for the Open Word Bible team.", ["/login/?redirect=/admin/", "Sign in"]);
    return;
  }
  // The account saved at the last visit draws the admin at once, while
  // /api/me checks it; the API checks every request anyway. If the roles
  // have changed since, the admin is drawn again.
  var started = false;
  function start() {
    if (!started) {
      window.addEventListener("hashchange", navigated);
      window.addEventListener("popstate", navigated);
    }
    started = true;
    route();
  }
  function areasOf(me) { return JSON.stringify([me.admin, me.is_super_admin]); }
  var known = account.user;
  if (known && known.email && known.admin && known.admin.length) {
    ME = known;
    start();
  }
  api("/api/me").then(function (me) {
    var changed = !ME || areasOf(ME) !== areasOf(me);
    ME = me;
    try { account.user = me; localStorage.setItem(KEY, JSON.stringify(account)); } catch (e) { /* none */ }
    if (!me.admin || !me.admin.length) {
      stop("No admin access", "Your account (" + me.email + ") has no role that opens the admin. A super admin can grant one in Team & access.");
      return;
    }
    if (!started || changed) start();
  }, function (e) {
    if (e.status === 401) {
      /* request() has asked for a new sign-in */
    } else if (!started) {
      stop("The admin couldn't load", e.message);
    }
  });
})();
