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
    { id: "jobs", label: "Drafting jobs", area: "jobs", group: "Progress" },
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

  function route() {
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
      main.textContent = "";
      add(main, nodes);
      var status = main.querySelector(".admin-note");
      if (FLASH && status) note(status, FLASH);
      FLASH = "";
    }).catch(function (e) {
      main.textContent = "";
      main.appendChild(head("Admin", section.label));
      main.appendChild(h("p", { class: "notice" }, e.message));
    }).then(function () {
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
          b.open_messages && ME.admin.indexOf("inbox") >= 0 ? h("a", { href: "#inbox" }, plural(b.open_messages, "open reader message")) : null),
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
        h("blockquote", null, m.text)]);
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
    "job.file": "filed drafting job", "email.send": "emailed the team:"
  };
  function activityList(actions) {
    return h("ul", { class: "admin-feed" }, actions.map(function (a) {
      var extra = a.detail.role ? " (" + a.detail.role + ")" : a.detail.recipients !== undefined ? " (" + plural(a.detail.recipients, "person", "people") + ")" : "";
      return h("li", null, h("time", { datetime: a.at, title: new Date(a.at).toLocaleString("en-GB") }, when(a.at)),
        h("span", null, h("strong", null, a.actor || "someone"), " " + (ACTION_LABEL[a.action] || a.action) + " " + a.target + extra));
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
    ["Editor", "The progress pages and the reader inbox."],
    ["Reporting", "The progress pages only: dashboard, coverage, languages, content health, engagement."],
    ["User records", "The progress pages and readers' accounts (sign devices out; only a super admin deletes)."],
    ["Email", "The progress pages and team email."],
    ["Scholar reviewer, language reviewer", "The progress pages for now. Review in the admin comes later; until then every sentence stays an AI-assisted draft."]
  ];
  VIEWS.help = function () {
    var sections = SECTIONS.filter(function (s) { return s.id !== "help"; });
    var AREA = { overview: "Anyone on the team", inbox: "Editors", users: "User records", email: "Email",
      jobs: "Super admins", team: "Super admins" };
    var out = [head("Team", "Help & roles", "What each role opens, and where things live. The admin shows you only the sections your roles open; the server checks every request again."),
      h("section", { class: "admin-block" }, h("h2", null, "Roles"),
        table(["Role", "Opens"], ROLES.map(function (r) { return h("tr", null, h("th", { scope: "row" }, r[0]), h("td", null, r[1])); }))),
      h("section", { class: "admin-block" }, h("h2", null, "Sections"),
        table(["Section", "Who"], sections.map(function (s) {
          return h("tr", null, h("th", { scope: "row" }, opens(s) ? h("a", { href: "#" + s.id }, s.label) : s.label), h("td", null, AREA[s.area] + (s.area === "overview" ? "" : " (and super admins)")));
        }))),
      h("section", { class: "admin-block" }, h("h2", null, "Good to know"), h("ul", null,
        h("li", null, "Numbers come from the database, which each deploy brings up to date from content/ on main. A merged pull request shows here after its deploy."),
        h("li", null, "Nothing in the admin marks a sentence reviewed. Every sentence stays AI-assisted until review opens and a named person approves it."),
        h("li", null, "Your roles: " + (ME.roles.length ? ME.roles.map(function (r) { return r.label; }).join(", ") : "none") + ".")))];
    if (ME.is_super_admin) {
      out.push(h("p", null, "Records the admin doesn't cover yet are in the ", h("a", { href: API + "/admin/", rel: "noopener" }, "database admin"),
        " (it needs a password: run manage.py changepassword with your address in the Render shell)."));
    }
    return out;
  };

  // ---- Start ---------------------------------------------------------

  function stop(title, text, link) {
    main.textContent = "";
    main.appendChild(head("Admin", title, text));
    if (link) main.appendChild(h("p", null, h("a", { class: "button", href: link[0] }, link[1])));
  }

  var account = saved();
  if (!account || !account.token) {
    stop("Sign in to use the admin", "The admin is for the Open Word Bible team.", ["/login/?redirect=/admin/", "Sign in"]);
    return;
  }
  api("/api/me").then(function (me) {
    ME = me;
    try { account.user = me; localStorage.setItem(KEY, JSON.stringify(account)); } catch (e) { /* none */ }
    if (!me.admin || !me.admin.length) {
      stop("No admin access", "Your account (" + me.email + ") has no role that opens the admin. A super admin can grant one in Team & access.");
      return;
    }
    window.addEventListener("hashchange", route);
    route();
  }, function (e) {
    if (e.status === 401) {
      try { localStorage.removeItem(KEY); } catch (x) { /* none */ }
      stop("Sign in again", "Your sign-in on this device has ended.", ["/login/?redirect=/admin/", "Sign in"]);
    } else {
      stop("The admin couldn't load", e.message);
    }
  });
})();
