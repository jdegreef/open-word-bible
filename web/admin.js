// The admin (/admin/), after Ochorus's: a rail of sections and the section
// named by the address's #hash, drawn from the API's /api/admin/ endpoints
// (backend/staff/). The rail shows only the areas the account's roles open
// (GET /api/me "admin"); the API checks every request again. All text is
// inserted with textContent. English only, as Ochorus's admin is.
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
  function date(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
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

  // The API, with the saved token. A 401 means the token is gone.
  function api(path, options) {
    options = options || {};
    var account = saved();
    var headers = { "Content-Type": "application/json" };
    if (account && account.token) headers.Authorization = "Bearer " + account.token;
    return fetch(API + path, {
      method: options.method || "GET", headers: headers,
      body: options.body ? JSON.stringify(options.body) : undefined
    }).catch(function () {
      throw new Error("Can't reach the server. Check your connection and try again.");
    }).then(function (r) {
      if (r.status === 204) return null;
      return r.json().catch(function () { return {}; }).then(function (data) {
        if (r.ok) return data;
        var e = new Error(message(data) || "Something went wrong (" + r.status + ").");
        e.status = r.status;
        throw e;
      });
    });
  }
  function message(data) {
    if (!data) return "";
    if (data.detail) return Array.isArray(data.detail) ? data.detail[0] : data.detail;
    for (var k in data) if (k !== "code") return Array.isArray(data[k]) ? data[k][0] : String(data[k]);
    return "";
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
  var SECTIONS = [
    { id: "dashboard", label: "Dashboard", area: "overview", group: "" },
    { id: "coverage", label: "Coverage", area: "overview", group: "Progress" },
    { id: "languages", label: "Languages", area: "overview", group: "Progress" },
    { id: "health", label: "Content health", area: "overview", group: "Progress" },
    { id: "changes", label: "Changes", area: "overview", group: "Progress" },
    { id: "jobs", label: "Drafting jobs", area: "jobs", group: "Progress" },
    { id: "work", label: "Work in progress", area: "overview", group: "Progress" },
    { id: "review", label: "Review", area: "review", group: "Text" },
    { id: "verse", label: "Verse inspector", area: "overview", group: "Text" },
    { id: "decisions", label: "Uncertain decisions", area: "overview", group: "Text" },
    { id: "terms", label: "Key terms", area: "overview", group: "Text" },
    { id: "fixes", label: "Fix requests", area: "inbox", group: "Text" },
    { id: "flags", label: "Reviewer flags", area: "inbox", group: "Text" },
    { id: "articles", label: "Articles", area: "overview", group: "Text" },
    { id: "export", label: "Export", area: "export", group: "Text" },
    { id: "overlap", label: "Similarity", area: "overview", group: "Text" },
    { id: "inbox", label: "Reader inbox", area: "inbox", group: "Readers" },
    { id: "users", label: "Users", area: "users", group: "Readers" },
    { id: "engagement", label: "Engagement", area: "overview", group: "Readers" },
    { id: "emails", label: "Team email", area: "email", group: "Team" },
    { id: "team", label: "Team & access", area: "team", group: "Team" },
    { id: "activity", label: "Activity log", area: "team", group: "Team" },
    { id: "help", label: "Help & roles", area: "", group: "Team" }
  ];
  // Drill-downs reached from a section, highlighted under it.
  var PARENT = { book: "coverage", user: "users" };

  function opens(section) { return !section.area || ME.admin.indexOf(section.area) >= 0; }

  function drawRail(current) {
    rail.textContent = "";
    var group = null, list = null;
    SECTIONS.filter(opens).forEach(function (s) {
      if (s.group !== group || !list) {
        group = s.group;
        if (group) rail.appendChild(h("p", { class: "admin-rail-group" }, group));
        list = h("ul");
        rail.appendChild(list);
      }
      var on = s.id === current || PARENT[current] === s.id;
      list.appendChild(h("li", null, h("a", { href: "#" + s.id, "aria-current": on ? "page" : null }, s.label)));
    });
    rail.hidden = false;
  }

  // Each drawing gets a number, so a slow answer for a section that has
  // since been left (or a stop()) doesn't overwrite the page.
  var drawing = 0;

  function route() {
    var mine = ++drawing;
    var hash = location.hash.replace(/^#/, "") || "dashboard";
    var parts = hash.split("/");
    var name = parts[0], arg = decodeURIComponent(parts.slice(1).join("/"));
    var section = SECTIONS.filter(function (s) { return s.id === (PARENT[name] || name); })[0];
    if (!section || !opens(section)) { name = "dashboard"; section = SECTIONS[0]; }
    drawRail(name);
    main.textContent = "";
    main.appendChild(head("Admin", section.label));
    main.setAttribute("aria-busy", "true");
    var draw = VIEWS[name];
    Promise.resolve().then(function () { return draw(arg); }).then(function (nodes) {
      if (mine !== drawing) return;
      main.textContent = "";
      add(main, nodes);
      var status = main.querySelector(".admin-note");
      if (FLASH && status) note(status, FLASH);
      FLASH = "";
    }).catch(function (e) {
      if (mine !== drawing) return;
      main.textContent = "";
      main.appendChild(head("Admin", section.label));
      main.appendChild(h("p", { class: "notice" }, e.message));
    }).then(function () {
      if (mine !== drawing) return;
      main.removeAttribute("aria-busy");
      document.title = section.label + " · Admin · Open Word Bible";
    });
  }

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
      var reviewed = (t.statuses.reviewed || 0) + (t.statuses.revised || 0);
      out.push(h("div", { class: "admin-tiles" },
        tile(num(t.sentences), "sentences drafted"),
        tile(num(t.books_started) + " / " + t.books, "books started in English (" + t.books_drafted + " complete)"),
        tile(num(t.chapters_drafted) + " / " + num(t.chapters), "chapters drafted"),
        tile(num(reviewed), "sentences reviewed by a person")));
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
      return out;
    });
  };

  var STATE_LABEL = { none: "Not started", partial: "Partly drafted", drafted: "Drafted" };

  // Coverage: every book in every language.
  VIEWS.coverage = function () {
    return api("/api/admin/coverage/").then(function (d) {
      var langs = d.languages;
      var tab = sessionTab("coverage", "nt");
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
          rememberTab("coverage", v); draw(v);
        }), legend()), body];
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
                h("span", { class: "admin-sub" }, new Date(w.week).toLocaleDateString("en-GB", { day: "numeric", month: "short" })));
            })) : empty("No new accounts in the last 12 weeks.")),
        h("div", { class: "admin-cols" },
          h("section", { class: "admin-block" }, h("h2", null, "Saved verses by book"), ranked(d.marks_by_book, "name", "marks")),
          h("section", { class: "admin-block" }, h("h2", null, "Where readers are reading"), ranked(d.reading_places, "name", "readers")),
          h("section", { class: "admin-block" }, h("h2", null, "Saved verses by language"), ranked(d.marks_by_language, "lang", "n")))];
    });
  };

  // Reader inbox.
  var INBOX = { status: "new", kind: "", lang: "" };
  VIEWS.inbox = function () {
    var q = "?status=" + INBOX.status + (INBOX.kind ? "&kind=" + INBOX.kind : "") + (INBOX.lang ? "&lang=" + INBOX.lang : "");
    return api("/api/admin/inbox/" + q).then(function (d) {
      var tabs = seg([["new", "New (" + d.counts.new + ")"], ["answered", "Answered (" + d.counts.answered + ")"],
        ["done", "Done (" + d.counts.done + ")"], ["declined", "Declined (" + d.counts.declined + ")"]], INBOX.status, function (v) {
        INBOX.status = v; route();
      });
      var kind = select("inbox-kind", [["", "Suggestions and questions"], ["suggestion", "Suggestions"], ["question", "Questions"]], INBOX.kind);
      kind.addEventListener("change", function () { INBOX.kind = kind.value; route(); });
      kind.setAttribute("aria-label", "Kind");
      return [head("Readers", "Reader inbox", "Suggestions and questions readers send from a verse. A reply is emailed to the reader once; mark a message done when it's dealt with."),
        h("div", { class: "admin-toolbar" }, tabs, kind),
        d.messages.length ? h("div", { class: "admin-messages" }, d.messages.map(messageCard)) : empty("No messages here."),
        d.total > d.messages.length ? h("p", { class: "admin-sub" }, "Showing the newest " + d.messages.length + " of " + num(d.total) + ".") : null];
    });
  };
  function messageCard(m) {
    var card = h("article", { class: "admin-message" });
    function draw() {
      card.textContent = "";
      add(card, [
        h("header", null, pill(m.kind === "question" ? "Question" : "Suggestion", m.kind === "question" ? "info" : ""),
          " ", h("a", { href: m.url, rel: "noopener" }, m.verse_label), " · ", m.language + (m.level ? " " + m.level : ""),
          h("span", { class: "admin-sub" }, " from " + (m.from.name ? m.from.name + " <" + m.from.email + ">" : m.from.email) + ", " + when(m.created_at))),
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
      if (!m.reply) {
        var text = h("textarea", { rows: 3, id: "reply-" + m.id, maxlength: 4000, placeholder: "Reply to the reader (emailed to them)" });
        var send = h("button", { type: "button", class: "admin-btn primary" }, "Send reply");
        send.addEventListener("click", function () {
          if (!text.value.trim()) { note(status, "Write a reply first.", true); return; }
          busy(send, true);
          update({ reply: text.value }).catch(function (e) { busy(send, false); note(status, e, true); });
        });
        card.appendChild(h("label", { class: "admin-label", for: "reply-" + m.id }, "Reply"));
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
      if (d.messages && d.messages.length) {
        out.push(h("section", { class: "admin-block" }, h("h2", null, "Reader messages"),
          h("div", { class: "admin-messages" }, d.messages.map(messageCard))));
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
    var rows = langs.map(function (code) {
      return h("tr", null, h("th", { scope: "row" }, names[code] || code), ["L", "B", "R"].map(function (lv) {
        var t = r.renderings[code][lv];
        return h("td", { class: "admin-wrap", lang: code }, t ? rendering(t) : "\u2014");
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
    if (ME.admin.indexOf("inbox") >= 0) card.appendChild(fixForm(r, langs, names, from));
    return card;
  }

  function decision(x) {
    return h("div", { class: "admin-decision" + (x.uncertain ? " uncertain" : "") },
      h("p", null, h("code", null, x.id), " ", h("span", { class: "admin-sub" }, x.category.replace(/_/g, " ") + (x.levels && x.levels.length ? " \u00b7 " + x.levels.join("") : "")),
        x.uncertain ? [" ", pill("uncertain", "warn")] : null, x.footnote ? [" ", pill("footnote", "info")] : null),
      h("p", null, h("strong", null, x.choice), x.alternatives.length ? h("span", { class: "admin-sub" }, " not: " + x.alternatives.join("; ")) : null),
      h("p", { class: "admin-sub" }, x.reason));
  }

  function fixForm(r, langs, names, from) {
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
      api("/api/admin/fixes/", { method: "POST", body: { record: r.id, verse: location.hash.split("/")[1], language: lang.value,
        levels: picked, change: change.value, reason: reason.value, message: from ? from.id : null } }).then(function (res) {
        status.textContent = "";
        add(status, ["Filed as ", h("a", { href: res.url, rel: "noopener" }, "#" + res.number), "."]);
        status.className = "admin-note";
        change.value = reason.value = "";
        busy(send, false);
      }, function (err) { busy(send, false); note(status, err, true); });
    });
    box.appendChild(form);
    return h("div", { class: "admin-fix-wrap" }, toggle, box);
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
      form.addEventListener("submit", function (e) { e.preventDefault(); f.q = search.value.trim(); f.offset = 0; route(); });
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
      var lang = select("overlap-lang", [["en", "English"], ["es", "Spanish"]], f.lang);
      lang.setAttribute("aria-label", "Language");
      var min = select("overlap-min", [["5", "5+ words"], ["6", "6+ words"], ["8", "8+ words"], ["10", "10+ words"]], String(f.min));
      min.setAttribute("aria-label", "Shortest run");
      var form = h("form", { class: "admin-toolbar" }, book, lang, min, h("button", { type: "submit", class: "admin-btn" }, "Compare"));
      form.addEventListener("submit", function (e) {
        e.preventDefault(); f.book = book.value.trim().toUpperCase() || "JHN"; f.lang = lang.value; f.min = +min.value;
        location.hash = "#overlap/" + f.book; route();
      });
      var rows = d.editions.map(function (e) {
        return h("tr", null, h("th", { scope: "row" }, e.name, h("span", { class: "admin-sub" }, e.code)),
          ["L", "B", "R"].map(function (lv) {
            var v = e.share[lv];
            return h("td", { class: "admin-num" + (v >= 50 ? " admin-high" : "") }, v === null ? "\u2014" : v + "%");
          }), h("td", { class: "admin-num" }, num(e.longest) + " words"));
      });
      return [head("Text", "Similarity to reference Bibles", "The share of " + d.name + "'s drafted words that sit in runs of " + d.min + " or more words also found in the same verses of a public-domain Bible. Shared phrasing is often the common heritage of Bible English; a high share or long runs is where to check a draft wasn't built on a reference Bible."),
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
    units: "Measures", plural_you: "Plural you" };
  function exportQuery(d) {
    var f = EXPORT, books = f.books;
    if (BOOK_SETS[books]) books = d.books.slice(BOOK_SETS[books][0], BOOK_SETS[books][1]).map(function (b) { return b.code; }).join(",");
    var settings = Object.keys(f.settings).filter(function (k) { return f.settings[k] > 0; })
      .map(function (k) { return k + ":" + f.settings[k]; }).join(",");
    return "?lang=" + f.lang + "&level=" + f.level + "&type=" + f.type + "&numbering=" + f.numbering +
      (books ? "&books=" + books : "") + (settings ? "&settings=" + settings : "");
  }
  function saveFile(path) {
    var account = saved();
    return fetch(API + path, { headers: account && account.token ? { Authorization: "Bearer " + account.token } : {} })
      .catch(function () { throw new Error("Can't reach the server. Check your connection and try again."); })
      .then(function (r) {
        if (!r.ok) return r.json().catch(function () { return {}; }).then(function (data) {
          throw new Error(message(data) || "Something went wrong (" + r.status + ").");
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
            return [String(i), o + (i === 0 ? " (default)" : "")];
          }), String(f.settings[s.name] || 0));
          sel.addEventListener("change", function () { f.settings[s.name] = +sel.value; changed(); });
          settingsBox.appendChild(h("label", { class: "admin-field" }, SETTING_NAME[s.name] || s.name, sel));
        });
      }
      function changed() {
        f.lang = langSel.value; f.level = levelSel.value; f.type = typeSel.value;
        f.numbering = numberingSel.value; f.books = bookSel.value;
        var keep = {};
        language().settings.forEach(function (s) { if (f.settings[s.name]) keep[s.name] = f.settings[s.name]; });
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
        h("section", { class: "admin-block" }, form, result),
        h("section", { class: "admin-block" }, h("h2", null, "Recent downloads"),
          d.recent.length ? table(["When", "File", "Verses", "By"], d.recent.map(function (a) {
            return h("tr", null, h("td", null, when(a.at)), h("td", null, a.target, h("span", { class: "admin-sub" }, (a.detail.books || []).join(", ") || "whole Bible")),
              h("td", { class: "admin-num" }, num(a.detail.verses)), h("td", null, a.by));
          })) : empty("Nothing downloaded yet."))];
    });
  };

  // Users.
  var USERS = { q: "", role: "", offset: 0 };
  VIEWS.users = function () {
    var q = "?offset=" + USERS.offset + (USERS.q ? "&q=" + encodeURIComponent(USERS.q) : "") + (USERS.role ? "&role=" + USERS.role : "");
    return api("/api/admin/users/" + q).then(function (d) {
      var search = h("input", { type: "search", id: "user-search", value: USERS.q, placeholder: "Search by email or name", "aria-label": "Search accounts" });
      var role = select("user-role", [["", "Everyone"], ["any", "The team (any role)"]].concat(d.roles.map(function (r) { return [r.kind, r.label]; })), USERS.role);
      role.setAttribute("aria-label", "Role");
      var form = h("form", { class: "admin-toolbar", role: "search" }, search, role, h("button", { type: "submit", class: "admin-btn" }, "Search"));
      form.addEventListener("submit", function (e) { e.preventDefault(); USERS.q = search.value.trim(); USERS.role = role.value; USERS.offset = 0; route(); });
      role.addEventListener("change", function () { USERS.role = role.value; USERS.offset = 0; route(); });
      var rows = d.users.map(function (u) {
        return h("tr", null, h("td", null, h("a", { href: "#user/" + u.id }, u.email), u.active ? null : pill("inactive", "warn")),
          h("td", null, u.name || "—"), h("td", null, u.roles.join(", ") || "Reader"),
          h("td", null, date(u.joined)), h("td", null, when(u.signed_in)),
          h("td", { class: "admin-num" }, num(u.marks)), h("td", { class: "admin-num" }, num(u.devices)));
      });
      var pager = h("div", { class: "admin-actions" });
      if (d.offset > 0) pager.appendChild(h("button", { type: "button", class: "admin-btn", onclick: function () { USERS.offset = Math.max(0, d.offset - d.page); route(); } }, "‹ Newer"));
      if (d.offset + d.page < d.total) pager.appendChild(h("button", { type: "button", class: "admin-btn", onclick: function () { USERS.offset = d.offset + d.page; route(); } }, "Older ›"));
      return [head("Readers", "Users", num(d.total) + (d.total === 1 ? " account" : " accounts") + (USERS.q || USERS.role ? " match" : "") + ". Saved verses are counted, never listed: they are the reader's own."),
        form, d.users.length ? table(["Email", "Name", "Roles", "Joined", "Last sign-in", ["Saved", { class: "admin-num" }], ["Devices", { class: "admin-num" }]], rows) : empty("No accounts match."),
        pager];
    });
  };

  VIEWS.user = function (id) {
    return api("/api/admin/users/" + encodeURIComponent(id) + "/").then(function (u) {
      var status = h("p", { class: "admin-note", role: "status" });
      var actions = h("div", { class: "admin-actions" });
      if (u.devices.length) {
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
          fact("Roles", u.roles.length ? u.roles.join(", ") : "Reader"),
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
        actions, status];
    });
  };
  function fact(label, value) { return h("div", null, h("dt", null, label), h("dd", null, value)); }

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
    "export.download": "downloaded"
  };
  function activityList(actions) {
    return h("ul", { class: "admin-feed" }, actions.map(function (a) {
      var extra = a.detail.role ? " (" + a.detail.role + ")" : a.detail.recipients !== undefined ? " (" + plural(a.detail.recipients, "person", "people") + ")" : "";
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
    more.addEventListener("click", load);
    return load().then(function () {
      return [head("Team", "Activity log", "What was done in the admin, newest first: roles, accounts, replies, jobs and emails. Reviews keep their own record."), list, more];
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
    ["Editor", "The progress pages, the reader inbox, fix requests and reviewers' flags."],
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

  // Review: a reviewer's queue for one layer (the meaning of the Greek or
  // Hebrew, or one language's wording), then one sentence at a time.
  var REVIEW_STATE = { not_reviewed: ["Not reviewed", ""], approved: ["Approved", "good"], changed: ["Changed since approval", "warn"],
    flagged: ["Flagged", "bad"] };
  function reviewPill(state) { return pill(REVIEW_STATE[state][0], REVIEW_STATE[state][1]); }
  VIEWS.review = function (arg) {
    var parts = arg ? arg.split("/") : [];
    return parts[1] ? reviewSentence(parts[0], parts[1]) : reviewQueue(parts[0] || sessionTab("review.layer", ""));
  };
  function reviewQueue(layer) {
    var filters = { book: sessionTab("review.book", ""), state: sessionTab("review.state", "todo") };
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
        var c = page.counts;
        body.appendChild(h("div", { class: "admin-tiles" },
          tile(num(c.not_reviewed), "not reviewed"), tile(num(c.approved), "approved", "good"),
          tile(num(c.changed), "changed since approval", c.changed ? "warn" : ""), tile(num(c.flagged), "flagged", c.flagged ? "bad" : "")));
        body.appendChild(page.sentences.length ? h("div", { class: "admin-scroll" }, h("table", { class: "admin-table" },
          h("thead", null, h("tr", null, h("th", null, "Sentence"), h("th", null, page.layer.kind === "meaning" ? "Literal gloss" : "Balanced"),
            h("th", null, "State"), h("th", null, "Last"))), rows)) : empty("Nothing here with these filters."));
      }
      page.sentences.forEach(function (s) {
        rows.appendChild(h("tr", null,
          h("th", { scope: "row" }, h("a", { href: "#review/" + layer + "/" + s.record }, s.label), h("div", { class: "admin-sub" }, s.record)),
          h("td", { class: "admin-wrap", lang: page.layer.kind === "meaning" ? "en" : layer }, rendering(s.preview)),
          h("td", null, reviewPill(s.state)),
          h("td", { class: "admin-sub" }, s.last ? s.last.label + ", " + s.last.by + ", " + when(s.last.at) : "—")));
      });
      more.hidden = !page.more;
    }
    function load() {
      busy(more, true);
      return api(query()).then(function (page) { d = d || page; layer = page.layer.code; draw(page); busy(more, false); return page; });
    }
    more.addEventListener("click", function () { offset += 50; load(); });
    var status = h("p", { class: "admin-note", role: "status" });
    function refilter() { offset = 0; rememberTab("review.book", filters.book); rememberTab("review.state", filters.state); load(); }
    // A layer remembered from before may no longer be the account's.
    return load().catch(function (e) {
      if (e.status !== 403 || !layer) throw e;
      layer = "";
      return load();
    }).then(function () {
      rememberTab("review.layer", layer);
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
        status, body, more];
    });
  }
  function reviewSentence(layer, record) {
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
      function act(action, button) {
        busy(button, true);
        api("/api/admin/review/" + encodeURIComponent(record) + "/", { method: "POST", body: { layer: layer, action: action, note: noteBox.value } })
          .then(function (res) {
            FLASH = { approve: "Approved ", flag: "Flagged ", comment: "Comment added to " }[action] + d.label + ".";
            if (action === "comment") route();
            else location.hash = res.next ? "#review/" + layer + "/" + res.next : "#review/" + layer;
          }, function (e) { busy(button, false); note(status, e, true); });
      }
      var buttons = h("div", { class: "admin-actions" },
        h("button", { type: "button", class: "admin-btn primary", onclick: function () { act("approve", this); } },
          kind === "meaning" ? "Approve the meaning" : "Approve the " + d.layer.name.replace(/ wording$/, "") + " wording"),
        h("button", { type: "button", class: "admin-btn", onclick: function () { act("flag", this); } }, "Flag a problem"),
        h("button", { type: "button", class: "admin-btn", onclick: function () { act("comment", this); } }, "Comment"),
        d.next ? h("a", { href: "#review/" + layer + "/" + d.next }, "Skip to the next ›") : null);
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
        h("section", { class: "admin-block" }, h("h2", null, "Your review"), h("label", { class: "admin-field" }, "Note", noteBox), buttons, status),
        h("section", { class: "admin-block" }, h("h2", null, "Review trail"), trail)];
    });
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
      more.addEventListener("click", function () { offset += 100; load(); });
      var langSel = select("changes-lang", [["", "Every language"]].concat(d.languages.map(function (l) { return [l.code, l.name]; })), "");
      var bookSel = select("changes-book", [["", "Every book"]].concat(run.books.map(function (b) { return [b.code, b.name + " (" + b.changes + ")"]; })), "");
      [langSel, bookSel].forEach(function (sel) {
        sel.addEventListener("change", function () { filters.lang = langSel.value; filters.book = bookSel.value; offset = 0; list.textContent = ""; load(); });
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

  // ---- Start ---------------------------------------------------------

  function stop(title, text, link) {
    drawing++;
    window.removeEventListener("hashchange", route);
    rail.hidden = true;
    main.removeAttribute("aria-busy");
    main.textContent = "";
    main.appendChild(head("Admin", title, text));
    if (link) main.appendChild(h("p", null, h("a", { class: "button", href: link[0] }, link[1])));
  }

  var account = saved();
  if (!account || !account.token) {
    stop("Sign in to use the admin", "The admin is for the Open Word Bible team.", ["/login/?redirect=/admin/", "Sign in"]);
    return;
  }
  // The account saved at the last visit draws the admin at once, while
  // /api/me checks it; the API checks every request anyway. If the roles
  // have changed since, the admin is drawn again.
  var started = false;
  function start() {
    if (!started) window.addEventListener("hashchange", route);
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
      try { localStorage.removeItem(KEY); } catch (x) { /* none */ }
      stop("Sign in again", "Your sign-in on this device has ended.", ["/login/?redirect=/admin/", "Sign in"]);
    } else if (!started) {
      stop("The admin couldn't load", e.message);
    }
  });
})();
