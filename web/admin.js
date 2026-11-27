// The admin (/admin/), after Ochorus's: a rail of sections and the section
// named by the address's #hash, drawn from the API's /api/admin/ endpoints
// (backend/staff/). The rail shows only the areas the account's roles open
// (GET /api/me "admin"); the API checks every request again. All text is
// inserted with textContent. English only, as Ochorus's admin is.
//
// The files: admin-core.js (OWBAdminCore and OWBAdminNav, page-free and
// tested on their own), this one (the shell: requests, kept reads, the
// rail, routing, shared helpers and the sections most people open first),
// and admin-review.js, admin-quality.js and admin-publish.js, the other
// sections, loaded when first opened (see "Sections loaded when first
// opened").

(function () {
  "use strict";
  var root = document.getElementById("admin");
  if (!root) return;
  var API = document.querySelector('meta[name="owb-api"]').content;
  var SITE = root.getAttribute("data-site");
  var GITHUB = root.getAttribute("data-github");
  // Names for the codes the API gives (written by build_site.py).
  var NAMES = { languages: {}, books: {} };
  try { NAMES = JSON.parse(root.getAttribute("data-names") || "") || NAMES; } catch (e) { /* codes, then */ }
  function langName(code) { return NAMES.languages[code] || code; }
  // "JHN.3.16" -> "John 3:16"; "JHN.3" -> "John 3"; anything else as it is.
  function verseName(vid) {
    var m = /^([1-3A-Z]{3})\.(\d+)(?:\.(\d+))?$/.exec(vid || "");
    if (!m || !NAMES.books[m[1]]) return vid;
    return NAMES.books[m[1]] + " " + m[2] + (m[3] ? ":" + m[3] : "");
  }
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
    DRAFTS = {};
    try { sessionStorage.removeItem(STORE); sessionStorage.removeItem(DRAFT_STORE); } catch (e) { /* none */ }
  }

  // Writing not sent yet (a reply, a fix request, a team email), kept by
  // what it is for until it is sent, so a click on a tab, a filter, the
  // pager or the rail loses nothing: keepDraft(field, key) fills the field
  // with what was kept and keeps what is typed; dropDraft(key, ...) once it
  // has gone. In this tab only (sessionStorage), and forgotten on signing
  // out. Closing or reloading the tab with any kept asks first.
  var DRAFT_STORE = "owb.admin.drafts", DRAFTS = {};
  try { DRAFTS = JSON.parse(sessionStorage.getItem(DRAFT_STORE) || "{}") || {}; } catch (e) { DRAFTS = {}; }
  function saveDrafts() {
    try { sessionStorage.setItem(DRAFT_STORE, JSON.stringify(DRAFTS)); } catch (e) { /* full or blocked */ }
  }
  function keepDraft(field, key) {
    if (!field.value && DRAFTS[key]) field.value = DRAFTS[key];
    field.addEventListener("input", function () {
      if (field.value.trim()) DRAFTS[key] = field.value; else delete DRAFTS[key];
      saveDrafts();
    });
    return field;
  }
  function dropDraft() {
    for (var i = 0; i < arguments.length; i++) delete DRAFTS[arguments[i]];
    saveDrafts();
  }
  window.addEventListener("beforeunload", function (e) {
    if (!Object.keys(DRAFTS).length) return;
    e.preventDefault();
    e.returnValue = "";
  });
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
    var once = path.indexOf("/api/admin/") === 0 ? C.onceKey(method, path, options.body) : "";
    if (once) headers["Idempotency-Key"] = once;
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

  // A note at the foot of the window that outlives the section it was made
  // in (approving opens the next sentence): text, and an action such as
  // Undo, for `seconds`. One at a time.
  var TOAST = null;
  function toast(text, action, seconds) {
    if (TOAST) TOAST.close();
    var box = h("div", { class: "admin-toast", role: "status" }, h("span", null, text));
    var timer = null;
    var me = { close: function () { clearTimeout(timer); box.remove(); if (TOAST === me) TOAST = null; } };
    if (action) {
      var b = h("button", { type: "button", class: "admin-toast-action" }, action.label);
      var ran = false;
      var run = function () { if (ran) return; ran = true; busy(b, true); action.run(me, b); };
      b.addEventListener("click", run);
      box.appendChild(b);
      if (action.label === "Undo") me.undo = run;
    }
    var x = h("button", { type: "button", class: "admin-toast-close", "aria-label": "Dismiss" }, "\u00d7");
    x.addEventListener("click", me.close);
    box.appendChild(x);
    document.body.appendChild(box);
    // Above the review bar at the foot of the window, not over its buttons.
    var foot = document.querySelector(".admin-review-bar");
    if (foot) {
      var r = foot.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > window.innerHeight - 4) box.style.bottom = Math.round(window.innerHeight - r.top + 12) + "px";
    }
    timer = setTimeout(me.close, (seconds || 8) * 1000);
    // Kept while the pointer or focus is on it, so Undo isn't taken away mid-reach.
    box.addEventListener("mouseenter", function () { clearTimeout(timer); });
    box.addEventListener("focusin", function () { clearTimeout(timer); });
    box.addEventListener("mouseleave", function () { timer = setTimeout(me.close, 4000); });
    TOAST = me;
    return me;
  }

  // After an action redraws what it was done on: focus goes back to the
  // control it was done with, or its row's (an id, or "h1"), and the result
  // is said in the status line of that part of the page, else in a toast;
  // never in a line drawn away or out of sight (landed). redrawThen does
  // the same after route() draws the section again.
  var AFTER = null;
  function landed(text, focus) {
    var el = focus === "h1" ? main.querySelector("h1") : focus ? document.getElementById(focus) : null;
    if (el) {
      if (el.tagName === "H1" || el.tagName === "H2") el.setAttribute("tabindex", "-1");
      el.focus({ preventScroll: true });
      if (el.getBoundingClientRect().bottom < 0 || el.getBoundingClientRect().top > window.innerHeight) el.scrollIntoView({ block: "center" });
    }
    if (!text) return;
    var part = el && el.closest(".admin-message, .admin-block");
    var line = part && part.querySelector(".admin-note");
    var r = line && line.getBoundingClientRect();
    if (line && r.top >= 0 && r.bottom <= window.innerHeight) note(line, text);
    else toast(text, null, 6);
  }
  function redrawThen(text, focus) {
    AFTER = { text: text, focus: focus };
    route();
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

  // One pager for every paged list (the inbox, Users, Decisions): where
  // the page is, "1–50 of 120", then Previous and Next. go(offset) draws
  // that page. Lists that grow at the foot say "Show more" (moreButton).
  function pager(d, shown, what, go) {
    if (!(d.total > d.page || d.offset)) return null;
    var first = d.offset + 1, last = d.offset + shown;
    var prev = h("button", { type: "button", class: "admin-btn", disabled: !d.offset }, "\u2039 Previous");
    var next = h("button", { type: "button", class: "admin-btn", disabled: last >= d.total }, "Next \u203a");
    prev.addEventListener("click", function () { go(Math.max(0, d.offset - d.page)); });
    next.addEventListener("click", function () { go(d.offset + d.page); });
    return h("nav", { class: "admin-pager", "aria-label": "Pages of " + what },
      h("span", { class: "admin-sub" }, num(first) + "\u2013" + num(last) + " of " + num(d.total)), prev, next);
  }
  function moreButton() { return h("button", { type: "button", class: "admin-btn", hidden: true }, "Show more"); }

  // A button that asks again before doing something hard to undo.
  // name: what a screen reader says for the first button when its label
  // ("Remove") is one of a row of the same ("Remove Editor from Ana").
  function confirmButton(label, ask, run, cls, name) {
    var wrap = h("span", { class: "admin-confirm" });
    var first = h("button", { type: "button", class: cls || "admin-btn", "aria-label": name || null }, label);
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
  // An empty list, saying why and what to do next: then is a list of
  // [label, "#address"] links or [label, function] buttons.
  function empty(text, then) {
    var p = h("p", { class: "admin-empty" }, text);
    (then || []).forEach(function (t) {
      p.appendChild(document.createTextNode(" "));
      p.appendChild(typeof t[1] === "function"
        ? h("button", { type: "button", class: "admin-link", onclick: t[1] }, t[0])
        : h("a", { href: t[1] }, t[0]));
    });
    return p;
  }
  // [label, button] that puts section name's filters back to their defaults
  // (but those in keep), for empty().
  function clearing(name, keep, label) {
    return [label || "Clear the filters", function () {
      var f = FILTERS[name];
      for (var k in f.defaults) if (!keep || keep.indexOf(k) < 0) f.state[k] = f.defaults[k];
      route();
    }];
  }
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
    { id: "pace", label: "Review pace", area: "overview", group: "Progress" },
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

  // Escape closes the phone's list of sections, and focus goes back to its
  // button (the rail is drawn again on each move; this is set once).
  rail.addEventListener("keydown", function (e) {
    var toggle = rail.querySelector(".admin-rail-toggle");
    if (e.key !== "Escape" || !toggle || !rail.classList.contains("open")) return;
    rail.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.focus();
  });
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

  function notHere(name, section, why) {
    if (why === "closed") {
      return [head("Admin", section.label, "Your roles don't open this part of the admin. A super admin can grant one in Team & access."),
        h("p", null, h("a", { href: "#dashboard" }, "Go to the dashboard"))];
    }
    // The section whose id or name is closest to what was asked for.
    var want = name.toLowerCase(), guess = SECTIONS.filter(opens).filter(function (s) {
      return s.id.indexOf(want) === 0 || want.indexOf(s.id) === 0 || s.label.toLowerCase().indexOf(want) >= 0;
    })[0];
    return [head("Admin", "Not found", "There's no section called \u201c" + name + "\u201d. Search the admin (Ctrl K) or pick one from the list."),
      h("p", null, guess ? [h("a", { href: "#" + guess.id }, guess.label), " might be what you were after. "] : null,
        h("a", { href: "#dashboard" }, "Go to the dashboard"))];
  }

  var GENERIC_EYEBROWS = ["Admin", "Text", "Progress", "Readers", "Team"];

  // The section on the page stays, dimmed, until the next one is ready; a
  // loading line replaces it only if that takes a while.
  function route() {
    // A section in a module not loaded yet: load it, then route again, so
    // its filters are registered before its address is read.
    var wanted = N.parse(location.hash.replace(/^#/, "")).name;
    if (MODULE_OF[wanted] && !VIEWS[wanted] && !LOAD_ERROR[wanted]) {
      var waiting = ++drawing;
      // The rail moves at once, and a loading line takes the old section's
      // place if the download takes a while, as for any slow section.
      var target = SECTIONS.filter(function (s) { return s.id === (PARENT[wanted] || wanted); })[0];
      drawRail(wanted);
      main.setAttribute("aria-busy", "true");
      main.classList.add("admin-stale");
      setTimeout(function () {
        if (waiting !== drawing) return;
        main.classList.remove("admin-stale");
        main.textContent = "";
        main.appendChild(head("Admin", target ? target.label : "Loading"));
        main.appendChild(h("p", { class: "admin-loading" }, "Loading…"));
      }, 300);
      loadModule(MODULE_OF[wanted]).catch(function (e) { LOAD_ERROR[wanted] = e; }).then(function () {
        if (waiting === drawing) route();
      });
      return;
    }
    var mine = ++drawing;
    var followed = NAVIGATED;
    var hash = address() || "dashboard";
    routed = location.hash;
    var at = N.parse(hash);
    var name = at.name, arg = at.arg;
    var section = SECTIONS.filter(function (s) { return s.id === (PARENT[name] || name); })[0];
    var draw = VIEWS[name];
    if (!draw && LOAD_ERROR[name]) {
      // Its module failed to load: say so, and Try again loads it again.
      var failed = LOAD_ERROR[name];
      delete LOAD_ERROR[name];
      draw = function () { return Promise.reject(failed); };
    }
    // An address that names no section, or one the account's roles don't
    // open, says so (it used to show the dashboard without a word).
    var missing = !section || !draw ? "unknown" : !opens(section) ? "closed" : "";
    if (missing) {
      draw = function () { return notHere(name, section, missing); };
      section = section || { id: name, label: "Not found", group: "" };
    }
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
      // A generic eyebrow over the heading ("Text", "Progress") gives way
      // to the section's group in the rail; one a page sets for itself
      // ("Review: Meaning (Greek)", a book's testament, "Account") stays.
      var eyebrow = section.group && main.querySelector(".admin-head .eyebrow");
      if (eyebrow && GENERIC_EYEBROWS.indexOf(eyebrow.textContent) >= 0) eyebrow.textContent = section.group;
      drawn = mine;
      shown = hash;
      touched = false;
      if (was) carry(was);
      if (moved && main.getBoundingClientRect().top < 0) window.scrollTo(0, 0);
      // A new section: its heading takes focus, so a screen reader says
      // where you are and the keyboard starts there (not on a redraw of the
      // same section, such as a search as you type).
      if (moved && !was) {
        var heading = main.querySelector("h1");
        if (heading) { heading.setAttribute("tabindex", "-1"); heading.focus({ preventScroll: true }); }
      }
    }
    Promise.resolve().then(function () { return draw(arg); }).then(function (nodes) {
      if (mine !== drawing) return;
      show(nodes);
      var status = main.querySelector(".admin-note");
      if (FLASH && status) note(status, FLASH);
      FLASH = "";
      if (AFTER) { var after = AFTER; AFTER = null; landed(after.text, after.focus); }
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
      if (!rested) { rested = true; setTimeout(loadTheRest, 1500); }
    });
  }

  // ---- Addresses -------------------------------------------------------

  // Sections whose filters are kept in the address (OWBAdminNav): name:
  // {state (the section's own filter object), defaults, legacy}. legacy(arg,
  // state) takes an older address's path argument ("#inbox/mine",
  // "#review/grc", "#overlap/JHN") into state and returns what is left of
  // it; anything left means the address isn't the filtered list (a review
  // sentence) and is left alone. Registered at the end, once every view's
  // filter object exists, or by a section's module when it loads.
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
  // "u" anywhere takes back the last step while its Undo toast shows
  // (an approval, a flag, a batch), so a keyboard user needn't Tab to it.
  var KEYS = null;
  window.addEventListener("keydown", function (e) {
    if (e.ctrlKey || e.metaKey || e.altKey || e.defaultPrevented) return;
    var t = e.target;
    if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (e.key === "u" && TOAST && TOAST.undo) { e.preventDefault(); TOAST.undo(); return; }
    if (!KEYS || KEYS.at !== drawing || drawn !== drawing) return;
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
      // How old the totals are: they are kept until the content changes or a review is made.
      if (d.counted_at) {
        var recount = h("button", { type: "button", class: "admin-link" }, "Count again");
        recount.addEventListener("click", function () {
          busy(recount, true);
          request("/api/admin/overview/?fresh=1", {}).then(function () {
            delete reads["/api/admin/overview/"];
            route();
          }, function (e) { busy(recount, false); toast(e.message, null, 8); });
        });
        out.push(h("p", { class: "admin-sub admin-counted" }, "Counted " + when(d.counted_at) + " \u00b7 ", recount));
      }
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
      // A book every language has finished needs nothing; hiding them leaves the work.
      var finished = function (b) { return langs.every(function (l) { return b.languages[l.code].state === "drafted"; }); };
      function draw(which) {
        body.textContent = "";
        var books = d.books.filter(function (b) { return b.testament === which; });
        var shown = COVERAGE.hide ? books.filter(function (b) { return !finished(b); }) : books;
        var rows = shown.map(function (b) {
          return h("tr", null,
            h("th", { scope: "row" }, h("a", { href: "#book/" + b.code }, b.name)),
            h("td", { class: "admin-num" }, b.chapters_drafted + " / " + b.chapters),
            h("td", { class: "admin-num" }, num(b.sentences)),
            langs.map(function (l) {
              var c = b.languages[l.code];
              var said = l.name + ": " + STATE_LABEL[c.state] + " (" + num(c.sentences) + " of " + num(b.sentences) + " sentences)";
              // The colour and mark for the eye; the same words as the tooltip for a screen reader.
              // A cell opens the book, chapter by chapter, in every language.
              return h("td", { class: "admin-cell" }, h("a", { class: "admin-state " + c.state, title: said, href: "#book/" + b.code },
                h("span", { "aria-hidden": "true" }, c.state === "none" ? "" : c.state === "drafted" ? "✓" : pct(c.sentences, b.sentences) + "%"),
                h("span", { class: "sr-only" }, said)));
            }));
        });
        if (!rows.length) rows.push(h("tr", null, h("td", { colspan: 3 + langs.length }, "Every book here is drafted in every language.")));
        var done = function (code) {
          return books.filter(function (b) { return b.languages[code].state === "drafted"; }).length;
        };
        rows.push(h("tr", { class: "admin-total" }, h("th", { scope: "row" }, "Books drafted"), h("td"), h("td"),
          langs.map(function (l) { return h("td", { class: "admin-num" }, done(l.code) + " / " + books.length); })));
        var grid = table(["Book", ["Chapters", { class: "admin-num" }], ["Sentences", { class: "admin-num" }]]
          .concat(langs.map(function (l) { return [l.code, { title: l.name, class: "admin-cell" }]; })), rows, "admin-coverage");
        // Its own scroll box, so the language row and the book column stay in view.
        grid.classList.add("admin-coverage-box");
        body.appendChild(grid);
      }
      draw(tab);
      var hide = h("input", { type: "checkbox", id: "coverage-hide", checked: !!COVERAGE.hide });
      hide.addEventListener("change", function () { COVERAGE.hide = hide.checked ? "1" : ""; keepAddress(true); draw(COVERAGE.testament); });
      return [head("Progress", "Coverage", "Every book in every language. A tick is a book drafted whole; a percentage is the share of its drafted sentences in that language. Open a book for its chapters."),
        h("div", { class: "admin-toolbar" }, seg([["ot", "Old Testament"], ["nt", "New Testament"]], tab, function (v) {
          COVERAGE.testament = v; rememberTab("coverage", v); keepAddress(true); draw(v);
        }), h("label", { class: "admin-check", for: "coverage-hide" }, hide, " Hide books every language has finished"), legend()),
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

  // How fast people are approving, layer by layer, and at that pace how
  // long the rest will take (staff/pace.py).
  VIEWS.pace = function () {
    return api("/api/admin/pace/").then(function (d) {
      var most = Math.max.apply(null, [1].concat(d.layers.map(function (l) { return Math.max.apply(null, l.per_week); })));
      function spark(counts) {
        return h("span", { class: "admin-spark", role: "img", "aria-label": "Approvals each week, oldest first: " + counts.join(", ") },
          counts.map(function (n, i) {
            return h("i", { style: "height:" + (n ? Math.max(8, 100 * n / most) : 0) + "%", title: "Week of " + date(d.weeks[i], true) + ": " + n });
          }));
      }
      function left(l) {
        if (l.weeks_left === 0) return "all approved";
        if (l.weeks_left === null) return "no pace yet";
        if (l.weeks_left > 520) return "over ten years";
        return l.weeks_left > 104 ? "about " + plural(Math.round(l.weeks_left / 52), "year") : "about " + plural(l.weeks_left, "week");
      }
      var rows = d.layers.map(function (l) {
        return h("tr", null, h("th", { scope: "row" }, h("a", { href: "#review/" + l.code }, l.name)),
          h("td", null, bar(l.approved, l.size, "good"), h("span", { class: "admin-sub" }, num(l.approved) + " of " + num(l.size))),
          h("td", null, spark(l.per_week)),
          h("td", { class: "admin-num" }, num(l.recent)),
          h("td", null, left(l)));
      });
      var people = d.reviewers.map(function (r) {
        return h("tr", null, h("th", { scope: "row" }, r.name), h("td", null, r.layer_name), h("td", { class: "admin-num" }, num(r.approvals)));
      });
      return [head("Progress", "Review pace", "Approvals by people in each review layer, week by week for the last " + d.weeks.length +
          " weeks, and at the pace of the last " + d.recent_weeks + " how long the rest of each layer would take. An approval made again after a sentence changed counts again."),
        d.layers.length ? table(["Layer", "Approved", "Each week", ["Per week lately", { class: "admin-num" }], "At this pace"], rows, "admin-pace")
          : empty("Nothing has been drafted to review yet, so there's no pace to measure.", [["File a drafting job", "#jobs"]]),
        h("section", { class: "admin-block" }, h("h2", null, "Reviewers, last " + d.weeks.length + " weeks"),
          people.length ? table(["Reviewer", "Layer", ["Approvals", { class: "admin-num" }]], people)
            : empty("No one has approved a sentence in these weeks.", [["Open the review queue", "#review"], ["Assign reviewers", "#assignments"]]))];
    });
  };

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
            var said = l.name + ": " + num(n) + " of " + num(c.sentences);
            return h("td", { class: "admin-cell" }, h("span", { class: "admin-state " + state, title: said },
              h("span", { "aria-hidden": "true" }, state === "drafted" ? "✓" : n ? num(n) : ""), h("span", { class: "sr-only" }, said)));
          }));
      });
      var uncertain = Object.keys(b.uncertain).map(function (k) {
        return h("li", null, (k === "meaning" ? "Meaning" : langName(k)) + ": " + num(b.uncertain[k]));
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
      out.push(speedBlock(d));
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

  // The admin's slowest pages on the live database, from the times the
  // server keeps (staff/speed.py), so one creeping towards the 15-second
  // limit is seen before it fails.
  function speedBlock(d) {
    var rows = d.speed || [];
    function secs(ms) { return ms >= 1000 ? (ms / 1000).toFixed(1) + " s" : ms + " ms"; }
    return h("section", { class: "admin-block" }, h("h2", null, "Slowest admin pages"),
      h("p", { class: "admin-sub" }, "Each page's reads in the last " + d.speed_hours + " hours, slowest first. A read over 15 seconds fails; over "
        + d.speed_slow + " is worth a look."),
      rows.length ? table(["Address", ["Reads", { class: "admin-num" }], ["Average", { class: "admin-num" }], ["Slowest", { class: "admin-num" }],
        ["Over " + d.speed_slow + " s", { class: "admin-num" }], ["Failed", { class: "admin-num" }]], rows.map(function (r) {
        var tone = r.errors || r.max_ms > 15000 ? "bad" : r.slow ? "warn" : "";
        return h("tr", null, h("td", null, h("code", null, r.route)), h("td", { class: "admin-num" }, num(r.requests)),
          h("td", { class: "admin-num" }, secs(r.average_ms)),
          h("td", { class: "admin-num" }, tone ? pill(secs(r.max_ms), tone) : secs(r.max_ms)),
          h("td", { class: "admin-num" }, num(r.slow)), h("td", { class: "admin-num" }, r.errors ? pill(num(r.errors), "bad") : "0"));
      })) : empty("No admin pages read in the last " + d.speed_hours + " hours, so there's nothing to time yet. They're timed as people use the admin."));
  }

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
  var INBOX = { status: "new", kind: "", lang: "", book: "", assigned: "", q: "", offset: 0 };
  VIEWS.inbox = function (arg) {
    if (arg === "mine") INBOX.assigned = "me";
    var f = INBOX;
    f.offset = Math.max(0, parseInt(f.offset, 10) || 0);
    var q = "?status=" + f.status + (f.kind ? "&kind=" + f.kind : "") + (f.lang ? "&lang=" + f.lang : "") +
      (f.book ? "&book=" + f.book : "") + (f.assigned ? "&assigned=" + f.assigned : "") +
      (f.q ? "&q=" + encodeURIComponent(f.q) : "") + (f.offset ? "&offset=" + f.offset : "");
    // A filter changed: back to the first page (route() writes the address).
    function refilter() { f.offset = 0; route(); }
    return api("/api/admin/inbox/" + q).then(function (d) {
      var counts = d.counts;
      var tabs = h("span");
      function drawTabs() {
        tabs.textContent = "";
        tabs.appendChild(seg([["new", "New (" + counts.new + ")"], ["answered", "Answered (" + counts.answered + ")"],
          ["done", "Done (" + counts.done + ")"], ["declined", "Declined (" + counts.declined + ")"]], f.status, function (v) {
          f.status = v; refilter();
        }));
      }
      drawTabs();
      // A card that leaves this tab (done, declined, answered) moves the counts at once.
      function moved(from, to) {
        if (from in counts) counts[from] = Math.max(0, counts[from] - 1);
        if (to in counts) counts[to] += 1;
        drawTabs();
      }
      var kind = select("inbox-kind", [["", "Suggestions and questions"], ["suggestion", "Suggestions"], ["question", "Questions"]], f.kind);
      kind.addEventListener("change", function () { f.kind = kind.value; refilter(); });
      kind.setAttribute("aria-label", "Kind");
      // The languages and books with messages in this tab (and the one chosen, even if none are left).
      var langs = (d.languages || []).slice();
      if (f.lang && !langs.some(function (l) { return l.code === f.lang; })) langs.push({ code: f.lang, name: f.lang, count: 0 });
      var lang = select("inbox-lang", [["", "Every language"]].concat(langs.map(function (l) { return [l.code, l.name + " (" + l.count + ")"]; })), f.lang);
      lang.setAttribute("aria-label", "Language");
      lang.addEventListener("change", function () { f.lang = lang.value; refilter(); });
      var books = (d.books || []).slice();
      if (f.book && !books.some(function (b) { return b.code === f.book; })) books.push({ code: f.book, name: f.book, count: 0 });
      var book = select("inbox-book", [["", "Every book"]].concat(books.map(function (b) { return [b.code, b.name + " (" + b.count + ")"]; })), f.book);
      book.setAttribute("aria-label", "Book");
      book.addEventListener("change", function () { f.book = book.value; refilter(); });
      var whose = seg([["me", "Mine"], ["none", "Unassigned"], ["", "All"]], f.assigned, function (v) {
        f.assigned = v; f.offset = 0;
        location.hash === "#inbox" ? route() : (location.hash = "#inbox");
      });
      // Words to find in every message, not only the page drawn: the API
      // searches (q=), as you type. The tabs' counts are then of what it found.
      var search = h("input", { type: "search", id: "inbox-q", value: f.q, placeholder: "Words, a verse or a reader", "aria-label": "Find in the reader inbox" });
      var found = h("span", { class: "admin-sub", role: "status" }, f.q ? plural(d.total, "message") + " found" : "");
      var form = h("form", { class: "admin-toolbar", role: "search" }, search, h("button", { type: "submit", class: "admin-btn" }, "Find"), found);
      function find(v) { if (v !== f.q) { f.q = v; refilter(); } }
      form.addEventListener("submit", function (e) { e.preventDefault(); stopLive(); find(search.value.trim()); });
      live(search, find);
      // Several messages at once: a box beside each card, and a bar for what
      // to do with those ticked (a status or an assignee; never a reply).
      var picked = {};
      var bar = h("div", { class: "admin-bulk", hidden: true, role: "region", "aria-label": "Selected messages" });
      var bulkNote = h("span", { class: "admin-note", role: "status" });
      function ids() { return Object.keys(picked).filter(function (k) { return picked[k]; }).map(Number); }
      function bulk(body, button) {
        busy(button, true);
        api("/api/admin/inbox/", { method: "PATCH", body: Object.assign({ ids: ids() }, body) }).then(function (r) {
          FLASH = plural(r.messages.length, "message") + " changed.";
          route();
        }, function (e) { busy(button, false); note(bulkNote, e, true); });
      }
      function drawBar() {
        var n = ids().length;
        bar.hidden = !n;
        bar.textContent = "";
        if (!n) return;
        var who = select("inbox-bulk-assign", [["", "Assign to\u2026"], ["none", "Nobody"]].concat((d.team || []).map(function (u) {
          return [String(u.id), u.name || u.email];
        })), "");
        who.setAttribute("aria-label", "Assign the selected messages to");
        who.addEventListener("change", function () {
          if (who.value) bulk({ assigned_to: who.value === "none" ? null : Number(who.value) }, who);
        });
        var done = h("button", { type: "button", class: "admin-btn" }, "Mark done");
        done.addEventListener("click", function () { bulk({ status: "done" }, done); });
        var decline = h("button", { type: "button", class: "admin-btn" }, "Decline");
        decline.addEventListener("click", function () { bulk({ status: "declined" }, decline); });
        var clear = h("button", { type: "button", class: "admin-link" }, "Clear");
        clear.addEventListener("click", function () {
          picked = {};
          list.querySelectorAll("input.admin-pick-message").forEach(function (b) { b.checked = false; });
          drawBar();
        });
        add(bar, [h("strong", null, plural(n, "message") + " selected"), who,
          f.status !== "done" ? done : null, f.status !== "declined" ? decline : null, clear, bulkNote]);
      }
      var cards = d.messages.map(function (m) {
        var box = h("input", { type: "checkbox", class: "admin-pick-message", "aria-label": "Select the message on " + m.verse_label + " from " + (m.from.name || m.from.email) });
        box.addEventListener("change", function () { picked[m.id] = box.checked; drawBar(); });
        return h("div", { class: "admin-message-row" }, box, messageCard(m, d.team, { listed: f.status, moved: moved }));
      });
      var list = h("div", { class: "admin-messages" }, cards);
      var filtered = f.kind || f.lang || f.book || f.assigned || f.q;
      var pages = pager(d, d.messages.length, "messages", function (o) { f.offset = o; route(); });
      return [head("Readers", "Reader inbox", "Suggestions and questions readers send from a verse. New messages come oldest first; assign one to say you're dealing with it. A reply is emailed to the reader once; mark a message done when it's dealt with."),
        h("div", { class: "admin-toolbar" }, tabs, whose), h("div", { class: "admin-toolbar admin-filters" }, kind, lang, book), form,
        bar,
        cards.length ? list : empty(filtered ? "No messages match these filters." : "No messages here."),
        filtered && !cards.length ? (function () {
          var clear = h("button", { type: "button", class: "admin-btn" }, "Clear filters");
          clear.addEventListener("click", function () { f.kind = f.lang = f.book = f.assigned = f.q = ""; refilter(); });
          return h("p", null, clear);
        })() : null,
        pages];
    });
  };
  // team: whom the message can be assigned to, from the answer that listed
  // it (the inbox's or the verse inspector's).
  // opts.listed: the inbox tab the card is shown in; a change that moves it
  // out (done, declined, answered) folds it to one line, with Undo for a
  // status, and opts.moved(from, to) updates the tab counts.
  function messageCard(m, team, opts) {
    opts = opts || {};
    var card = h("article", { class: "admin-message" });
    function draw() {
      card.textContent = "";
      add(card, [
        h("header", null, pill(m.kind === "question" ? "Question" : "Suggestion", m.kind === "question" ? "info" : ""),
          " ", h("a", { href: m.url, rel: "noopener" }, m.verse_label), " · ", langName(m.language) + (m.level ? ", " + (LEVEL_NAMES[m.level] || m.level) : ""),
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
        });
        keepDraft(text, "reply." + m.id);
        var saved = select("saved-" + m.id, [["", "Start from a saved reply…"]].concat(m.replies.map(function (r) { return [r.key, r.label]; })), "");
        saved.setAttribute("aria-label", "Saved replies");
        saved.addEventListener("change", function () {
          var r = m.replies.filter(function (x) { return x.key === saved.value; })[0];
          if (r) {
            // Into an empty box it is the reply; into one already written,
            // it goes in at the cursor, so nothing written is lost.
            if (!text.value.trim()) text.value = r.text;
            else {
              var at = text.selectionStart != null ? text.selectionStart : text.value.length;
              var before = text.value.slice(0, at).replace(/\s*$/, ""), after = text.value.slice(at).replace(/^\s*/, "");
              text.value = before + "\n\n" + r.text + (after ? "\n\n" + after : "");
            }
            text.dispatchEvent(new Event("input"));   // kept as typing is
            text.focus();
          }
          saved.value = "";
        });
        var send = h("button", { type: "button", class: "admin-btn primary" }, "Send reply");
        // Sending emails the reader at once and can't be taken back, so the
        // reply is shown as it will go, to whom, before it goes.
        var preview = h("div", { class: "admin-reply-preview", hidden: true });
        send.addEventListener("click", function () {
          if (!text.value.trim()) { note(status, "Write a reply first.", true); return; }
          var to = m.from.name ? m.from.name + " <" + m.from.email + ">" : m.from.email;
          var go = h("button", { type: "button", class: "admin-btn primary" }, "Send now");
          var back = h("button", { type: "button", class: "admin-btn" }, "Keep editing");
          preview.textContent = "";
          add(preview, [h("p", null, h("strong", null, "This goes to " + to + ","), " about " + m.verse_label + ", and can't be taken back:"),
            h("blockquote", null, text.value.trim()), h("div", { class: "admin-actions" }, go, back)]);
          preview.hidden = false;
          text.hidden = send.hidden = saved.hidden = true;
          go.focus();
          back.addEventListener("click", function () {
            preview.hidden = true;
            text.hidden = send.hidden = saved.hidden = false;
            text.focus();
          });
          go.addEventListener("click", function () {
            busy(go, true); busy(back, true);
            update({ reply: text.value }).then(function () { dropDraft("reply." + m.id); }, function (e) {
              busy(go, false); busy(back, false);
              note(status, e, true);
            });
          });
        });
        card.appendChild(h("label", { class: "admin-label", for: "reply-" + m.id }, "Reply"));
        card.appendChild(saved);
        card.appendChild(text);
        card.appendChild(preview);
        card.appendChild(h("div", { class: "admin-actions" }, send, statusButtons()));
      } else {
        card.appendChild(h("div", { class: "admin-actions" }, statusButtons()));
      }
      var noteField = h("input", { id: "note-" + m.id, value: m.note, maxlength: 4000, placeholder: "A note for editors (not sent)" });
      noteField.addEventListener("change", function () {
        update({ note: noteField.value }).then(function () { landed("Note saved.", "note-" + m.id); }, function (e) { note(status, e, true); });
      });
      card.appendChild(h("label", { class: "admin-label", for: "note-" + m.id }, "Editors' note"));
      card.appendChild(noteField);
      card.appendChild(status);
      function assignee(status) {
        var pick = select("assign-" + m.id, [["", "Nobody"]].concat((team || []).map(function (u) {
          // An address only for a super admin, or one's own (staff/people.py).
          return [String(u.id), (u.email && u.email !== u.name ? u.name + " (" + u.email + ")" : u.name) + (u.email === ME.email ? " — you" : "")];
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
      var was = m.status;
      return api("/api/admin/inbox/" + m.id + "/", { method: "PATCH", body: body }).then(function (fresh) {
        m = fresh;
        if (opts.listed && was === opts.listed && m.status !== was) folded(was, !!body.reply);
        else draw();
      });
    }
    var DONE_LABEL = { done: "Marked done", declined: "Declined", answered: "Answered", "new": "Back to new" };
    // The card once it has left the tab: what happened, and Undo (not for
    // a reply, which has been emailed).
    function folded(was, replied) {
      if (opts.moved) opts.moved(was, m.status);
      card.textContent = "";
      card.classList.add("admin-message-folded");
      var what = (DONE_LABEL[m.status] || m.status) + ": " + m.verse_label + ", from " + (m.from.name || m.from.email) +
        (replied ? ". The reply was emailed." : ".");
      var line = h("p", { role: "status" }, what);
      if (!replied) {
        var undo = h("button", { type: "button", class: "admin-link" }, "Undo");
        undo.addEventListener("click", function () {
          busy(undo, true);
          var now = m.status;
          api("/api/admin/inbox/" + m.id + "/", { method: "PATCH", body: { status: was } }).then(function (fresh) {
            m = fresh;
            if (opts.moved) opts.moved(now, m.status);
            card.classList.remove("admin-message-folded");
            draw();
          }, function (e) { busy(undo, false); line.appendChild(h("span", { class: "admin-note bad" }, " " + e.message)); });
        });
        add(line, [" ", undo]);
      }
      card.appendChild(line);
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

  function decision(x) {
    return h("div", { class: "admin-decision" + (x.uncertain ? " uncertain" : "") },
      h("p", null, h("code", null, x.id), " ", h("span", { class: "admin-sub" }, x.category.replace(/_/g, " ") + (x.levels && x.levels.length ? " \u00b7 " + x.levels.join("") : "")),
        x.uncertain ? [" ", pill("uncertain", "warn")] : null, x.footnote ? [" ", pill("footnote", "info")] : null),
      h("p", null, h("strong", null, x.choice), x.alternatives.length ? h("span", { class: "admin-sub" }, " not: " + x.alternatives.join("; ")) : null),
      h("p", { class: "admin-sub" }, x.reason));
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
      var pages = pager(d, d.users.length, "accounts", function (o) { USERS.offset = o; route(); });
      return [head("Readers", "Users", num(d.total) + (d.total === 1 ? " account" : " accounts") + (USERS.q || USERS.role ? " match" : "") +
        (d.system_hidden ? " (" + plural(d.system_hidden, "system account") + " hidden)" : "") + ". Saved verses are counted, never listed: they are the reader's own."),
        form, d.users.length ? table(["Email", "Name", "Roles", "Joined", "Last sign-in", ["Saved", { class: "admin-num" }], ["Devices", { class: "admin-num" }]], rows)
          : empty("No accounts match" + (USERS.q ? " “" + USERS.q + "”" : "") + (USERS.role ? " with that role" : "") + ".", USERS.q || USERS.role ? [clearing("users")] : null),
        pages];
    });
  };

  VIEWS.user = function (id) {
    return api("/api/admin/users/" + encodeURIComponent(id) + "/").then(function (u) {
      var status = h("p", { class: "admin-note", role: "status" });
      var actions = h("div", { class: "admin-actions" });
      if (u.devices.length && u.can_sign_out) {
        actions.appendChild(confirmButton("Sign out every device", "Sign out " + plural(u.devices.length, "device") + "?", function (b) {
          api("/api/admin/users/" + u.id + "/sign-out/", { method: "POST" }).then(function () { redrawThen("Signed out of every device.", "h1"); }, function (e) { busy(b, false); note(status, e, true); });
        }));
      }
      // Deactivating keeps the account (and its reviews and messages) but
      // stops it signing in; deleting can't when it has review history.
      if (u.can_deactivate) {
        actions.appendChild(u.active
          ? confirmButton("Deactivate account", "Stop " + u.email + " signing in?", function (b) {
            api("/api/admin/users/" + u.id + "/", { method: "PATCH", body: { active: false } }).then(function () { redrawThen("Deactivated: " + u.email + " can't sign in now.", "h1"); }, function (e) { busy(b, false); note(status, e, true); });
          })
          : confirmButton("Reactivate account", "Let " + u.email + " sign in again?", function (b) {
            api("/api/admin/users/" + u.id + "/", { method: "PATCH", body: { active: true } }).then(function () { redrawThen("Reactivated: " + u.email + " can sign in again.", "h1"); }, function (e) { busy(b, false); note(status, e, true); });
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
          })) : empty("Not signed in on any device.")),
        u.messages.length ? h("section", { class: "admin-block" }, h("h2", null, "Messages"),
          h("ul", null, u.messages.map(function (m) {
            return h("li", null, (m.kind === "question" ? "Question" : "Suggestion") + " on ", h("a", { href: "#verse/" + m.verse }, verseName(m.verse)),
              " · " + m.status + " · " + date(m.created_at));
          }))) : null,
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
    function send(body, button, said) {
      busy(button, true);
      api("/api/admin/users/" + u.id + "/", { method: "PATCH", body: body }).then(function () { redrawThen(said, button.id); },
        function (e) { busy(button, false); note(status, e, true); });
    }
    var name = h("input", { id: "user-name", value: u.name || "", maxlength: 80, placeholder: u.display_name || "" });
    var save = h("button", { type: "submit", class: "admin-btn", id: "user-name-save" }, "Save name");
    var form = h("form", { class: "admin-toolbar" }, h("label", { class: "admin-field", for: "user-name" }, "Display name", name), save);
    form.addEventListener("submit", function (e) { e.preventDefault(); send({ name: name.value.trim() }, save, name.value.trim() ? "Name saved." : "Name cleared."); });
    var mark = h("button", { type: "button", class: "admin-btn", id: "user-kind" }, u.system ? "Mark as a person" : "Mark as a system account");
    mark.addEventListener("click", function () { send({ system: !u.system }, mark, u.system ? "Marked as a person." : "Marked as a system account."); });
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
              li.appendChild(confirmButton("Remove", "Remove " + r.label + " from " + (m.name || m.email) + "?", function (b) {
                api("/api/admin/team/roles/" + r.id + "/", { method: "DELETE" }).then(function () {
                  redrawThen("Removed " + r.label + " from " + (m.name || m.email) + ".", "team-list");
                }, function (e) { busy(b, false); note(status, e, true); });
              }, "admin-link", "Remove " + r.label + " from " + (m.name || m.email)));
            }
            return li;
          }))),
          h("td", null, m.pending ? [pill("Hasn't signed in", "warn"), " ", (function () {
            var b = h("button", { type: "button", class: "admin-link" }, "Resend invitation");
            b.addEventListener("click", function () {
              busy(b, true);
              api("/api/admin/team/invite/", { method: "POST", body: { email: m.email } }).then(function () {
                toast("Invitation sent to " + m.email + ".", null, 6);
              }, function (e) { note(status, e, true); }).then(function () { busy(b, false); });
            });
            return b;
          })()] : when(m.signed_in)));
      });
      return [head("Team", "Team & access", "Grant the roles that open the admin and, when review starts, the reviewer roles. An address that has never signed in gets an invitation by email."),
        h("section", { class: "admin-block" }, h("h2", null, "Grant a role"), form, about, status),
        h("section", { class: "admin-block" }, h("h2", { id: "team-list" }, "The team"),
          table(["Person", "Roles", "Last sign-in"], rows)),
        teamAssignments(),
        h("p", { class: "admin-sub" }, "Super admins aren't granted here: they're the addresses in " + d.super_admins_from +
          " on the API service in Render, made super admins when they sign in.")];
    });
  };

  // Activity log.
  var ACTION_LABEL = {
    "role.grant": "granted a role to", "role.revoke": "removed a role from", "role.invite": "invited",
    "user.delete": "deleted the account", "user.deactivate": "deactivated the account", "user.activate": "reactivated the account", "user.sign_out": "signed out the devices of",
    "message.reply": "answered", "message.done": "marked done", "message.declined": "declined", "message.new": "reopened",
    "job.file": "filed drafting job", "article.job": "filed article job", "digest.send": "sent the weekly digest to", "message.fixed": "told the reader their message led to a change:", "email.send": "emailed the team:", "fix.request": "requested fix",
    "export.download": "downloaded", "review.assign": "assigned review to", "review.unassign": "took back a review assignment from",
    "review.assignment": "changed a review assignment of", "review.undo": "took back"
  };
  function activityList(actions) {
    return h("ul", { class: "admin-feed" }, actions.map(function (a) {
      var extra = a.detail.role ? " (" + a.detail.role + ")" : a.detail.range ? " (" + a.detail.range + ", " + a.detail.layer + ")" : a.detail.recipients !== undefined ? " (" + plural(a.detail.recipients, "person", "people") + ")" : "";
      return h("li", null, h("time", { datetime: a.at, title: new Date(a.at).toLocaleString("en-GB") }, when(a.at)),
        h("span", null, h("strong", null, a.actor || "The admin"), " " + (ACTION_LABEL[a.action] || a.action) + " " + a.target + extra));
    }));
  }
  // The activity log, narrowed by who did it and what kind of thing.
  var ACTIVITY = { by: "", kind: "" };
  var KIND_LABEL = { role: "Roles", user: "Accounts", message: "Reader messages", job: "Drafting jobs", article: "Article jobs",
    fix: "Fix requests", email: "Team email", digest: "Digests", export: "Downloads", review: "Review steps taken back" };
  VIEWS.activity = function () {
    var f = ACTIVITY;
    var list = h("div");
    var more = moreButton();
    var last = null, first = null;
    function load() {
      busy(more, true);
      var q = [last ? "before=" + last : "", f.by ? "by=" + encodeURIComponent(f.by) : "", f.kind ? "kind=" + f.kind : ""].filter(Boolean).join("&");
      return api("/api/admin/activity/" + (q ? "?" + q : "")).then(function (d) {
        first = first || d;
        if (d.actions.length) last = d.actions[d.actions.length - 1].id;
        list.appendChild(d.actions.length || last ? activityList(d.actions)
          : empty(f.by || f.kind ? "Nothing like that in the log." : "Nothing done in the admin yet."));
        more.hidden = !d.more;
        busy(more, false);
      });
    }
    more.addEventListener("click", function () { later(more, load()); });
    return load().then(function () {
      var by = select("activity-by", [["", "Everyone"]].concat(first.people.map(function (p) { return [p, p]; })), f.by);
      by.setAttribute("aria-label", "Who");
      var kind = select("activity-kind", [["", "Everything"]].concat(first.kinds.map(function (k) { return [k, KIND_LABEL[k] || k]; })), f.kind);
      kind.setAttribute("aria-label", "What");
      [by, kind].forEach(function (sel) {
        sel.addEventListener("change", function () { f.by = by.value; f.kind = kind.value; route(); });
      });
      return [head("Team", "Activity log", "What was done in the admin, newest first: roles, accounts, replies, jobs and emails. Reviews keep their own record."),
        h("div", { class: "admin-toolbar admin-filters" }, by, kind), list, more, approvalLog()];
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

  // Review assignments (staff/assignments.py): an editor or super admin
  // gives a reviewer a book, or some of its chapters, in a layer they
  // review, by a date or not. On their own page and in Team & access.
  function assignmentsManager(d, status) {
    var people = d.reviewers || [];
    var reviewerSel = select("assign-reviewer", people.map(function (p) {
      return [String(p.id), p.email && p.email !== p.name ? p.name + " (" + p.email + ")" : p.name];
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
    function patch(a, body, button, said) {
      return api("/api/admin/assignments/" + a.id + "/", { method: "PATCH", body: body }).then(function () {
        redrawThen(said || "Saved.", button ? button.id : "assign-due-" + a.id);
      }, function (e) {
        if (button) busy(button, false);
        note(status, e, true);
      });
    }
    function row(a) {
      var dueIn = h("input", { type: "date", id: "assign-due-" + a.id, value: a.due || "", "aria-label": "Due date for " + a.label + ", " + a.assignee.name });
      // Saved on leaving the field (or Enter), not on "change": typing a
      // date digit by digit is a valid date part-way ("0001-12-01").
      function saveDue() {
        var v = dueIn.value;
        if (v === (a.due || "")) return;
        if (v && Number(v.slice(0, 4)) < 2000) {
          dueIn.value = a.due || "";
          note(status, "That date looks unfinished, so it wasn't saved. Type the whole date.", true);
          return;
        }
        patch(a, { due: v }, null, v ? "Due date saved." : "Due date cleared.");
      }
      dueIn.addEventListener("blur", saveDue);
      dueIn.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); saveDue(); } });
      var who = a.assignee.name + "'s " + a.label;
      var close = h("button", { type: "button", class: "admin-link", id: "assign-close-" + a.id, "aria-label": (a.closed_at ? "Reopen " : "Close ") + who },
        a.closed_at ? "Reopen" : "Close");
      close.addEventListener("click", function () {
        busy(close, true);
        patch(a, { closed: !a.closed_at }, close, (a.closed_at ? "Reopened " : "Closed ") + who + ".");
      });
      return h("tr", null,
        h("td", null, a.assignee.name, a.assignee.email && a.assignee.name !== a.assignee.email ? h("div", { class: "admin-sub" }, a.assignee.email) : null),
        h("td", null, a.layer.name),
        h("td", null, a.label, a.note ? h("div", { class: "admin-sub" }, a.note) : null),
        h("td", null, bar(a.progress.approved, a.progress.total), h("div", { class: "admin-sub" }, progressText(a.progress))),
        h("td", null, dueIn, a.due && a.standing !== "closed" && a.standing !== "done" ? h("div", { class: "admin-sub" }, dueText(a)) : null),
        h("td", null, standingPill(a)),
        h("td", null, close, " ", confirmButton("Remove", "Remove " + who + "?", function (b) {
          api("/api/admin/assignments/" + a.id + "/", { method: "DELETE" }).then(function () { redrawThen("Removed " + who + ".", null); },
            function (e) { busy(b, false); note(status, e, true); });
        }, "admin-link", "Remove " + who)));
    }
    return {
      form: people.length ? form : empty("No one reviews yet: grant a scholar or language reviewer role in Team & access first."),
      list: d.assignments.length ? table(["Reviewer", "Layer", "Range", "Progress", "Due", "Standing", ""], d.assignments.map(row))
        : empty("No review assignments. Choose a reviewer, a layer and books above to give someone a share of the work.")
    };
  }
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
    var more = moreButton();
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

  // ---- Filters kept in the address -------------------------------------

  var COVERAGE = { testament: sessionTab("coverage", "nt"), hide: "" };
  filtered("coverage", COVERAGE, { testament: "nt", hide: "" });
  filtered("inbox", INBOX, null, function (arg, f) {
    if (arg !== "mine") return arg;
    f.assigned = "me";
    return "";
  });
  filtered("users", USERS);
  filtered("checks", CHECKS);
  filtered("activity", ACTIVITY);

  // ---- Sections loaded when first opened ---------------------------------

  // Most sections' code is in admin-<module>.js (review, quality, publish),
  // fetched the first time one of their sections is opened, and the rest
  // fetched quietly once the admin is drawn, so the admin starts on this
  // file alone. build_site.py writes the files' versioned URLs into
  // data-modules. A module gets the helpers and state below as A; what is
  // reassigned here (the account, the flash message, ...) it reads and
  // writes through A, so both sides see one value.
  var MODULE_OF = {};
  [["review", ["review",  "workspace",  "assignments",  "flags",  "changes",  "releases"]],
   ["quality", ["verse",  "fixes",  "decisions",  "terms",  "consistency",  "checks"]],
   ["publish", ["articles",  "work",  "overlap",  "export",  "jobs",  "emails"]]].forEach(function (m) {
    m[1].forEach(function (view) { MODULE_OF[view] = m[0]; });
  });
  var MODULE_URLS = {};
  try { MODULE_URLS = JSON.parse(root.getAttribute("data-modules") || "") || {}; } catch (e) { /* their plain names */ }
  var loading = {}, LOAD_ERROR = {}, rested = false;
  var MODULE_WAIT = 20000;
  function loadModule(name) {
    if (!loading[name]) {
      loading[name] = new Promise(function (resolve, reject) {
        var s = document.createElement("script");
        s.src = MODULE_URLS[name] || "/admin-" + name + ".js";
        // A download that never finishes gives up after MODULE_WAIT, with
        // Try again (errorPanel), rather than leaving the page waiting.
        var gaveUp = setTimeout(function () {
          fail("Loading this section took too long. Check your connection, then try again.", "timeout");
        }, MODULE_WAIT);
        function fail(text, code) {
          clearTimeout(gaveUp);
          if (loading[name] !== promise) return;
          delete loading[name];
          s.onload = s.onerror = null;
          s.remove();
          var e = new Error(text);
          if (code) e.code = code;
          reject(e);
        }
        s.onload = function () { clearTimeout(gaveUp); resolve(); };
        s.onerror = function () { fail("This section couldn't be loaded. Check your connection, then try again."); };
        document.head.appendChild(s);
      });
      var promise = loading[name];
    }
    return loading[name];
  }
  // The modules this account can open, after the first section is drawn,
  // so moving to one later doesn't wait.
  function loadTheRest() {
    var wanted = {};
    SECTIONS.forEach(function (s) { if (MODULE_OF[s.id] && opens(s)) wanted[MODULE_OF[s.id]] = true; });
    Object.keys(wanted).forEach(function (m) { loadModule(m).catch(function () { /* again when opened */ }); });
  }
  var EXPORTS = {
    C: C, CHECKS: CHECKS, CHECK_KINDS: CHECK_KINDS, LEVEL_NAMES: LEVEL_NAMES, N: N, SITE: SITE,
    STATE_LABEL: STATE_LABEL, add: add, api: api, approvalHistory: approvalHistory,
    assignmentsManager: assignmentsManager, bar: bar, busy: busy, clearing: clearing, confirmButton: confirmButton,
    date: date, decision: decision, diffView: diffView, dueText: dueText, empty: empty, filtered: filtered,
    forget: forget, ghFile: ghFile, h: h, head: head, keepAddress: keepAddress, langName: langName, later: later, keepDraft: keepDraft, dropDraft: dropDraft, moreButton: moreButton, pager: pager,
    live: live, main: main, messageCard: messageCard, note: note, num: num, pill: pill, plural: plural,
    progressText: progressText, rememberTab: rememberTab, rendering: rendering, request: request, route: route,
    saveFile: saveFile, seg: seg, select: select, sessionTab: sessionTab, sinceApproval: sinceApproval,
    standingPill: standingPill, stopLive: stopLive, table: table, tile: tile, toast: toast, verseName: verseName,
    when: when, VIEWS: VIEWS
  };
  Object.defineProperty(EXPORTS, "FIX_FROM", { get: function () { return FIX_FROM; }, set: function (v) { FIX_FROM = v; } });
  Object.defineProperty(EXPORTS, "FLASH", { get: function () { return FLASH; }, set: function (v) { FLASH = v; } });
  Object.defineProperty(EXPORTS, "KEYS", { get: function () { return KEYS; }, set: function (v) { KEYS = v; } });
  Object.defineProperty(EXPORTS, "ME", { get: function () { return ME; }, set: function (v) { ME = v; } });
  Object.defineProperty(EXPORTS, "drawing", { get: function () { return drawing; }, set: function (v) { drawing = v; } });
  window.OWBAdmin = { module: function (define) { define(EXPORTS); } };

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
