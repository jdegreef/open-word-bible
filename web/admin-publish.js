// Publishing and team work: article jobs, work in progress, similarity,
// export, drafting jobs and team email.
// admin.js loads this the first time one of these sections is opened. A is
// what the shell shares (OWBAdmin.module): its helpers, and its state, which
// is read and written as A.ME, A.FLASH, ... so both sides see one value.
OWBAdmin.module(function (A) {
  "use strict";
  var C = A.C, SITE = A.SITE, STATE_LABEL = A.STATE_LABEL, VIEWS = A.VIEWS, add = A.add, api = A.api, bar = A.bar,
      busy = A.busy, confirmButton = A.confirmButton, date = A.date, empty = A.empty, filtered = A.filtered,
      forget = A.forget, h = A.h, head = A.head, keepAddress = A.keepAddress, langName = A.langName, main = A.main,
      note = A.note, num = A.num, pill = A.pill, plural = A.plural, rememberTab = A.rememberTab, request = A.request,
      route = A.route, saveFile = A.saveFile, seg = A.seg, select = A.select, sessionTab = A.sessionTab,
      table = A.table, tile = A.tile, when = A.when;

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
            A.FLASH = "Filed as #" + r.number + "."; route();
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
          })) : empty("No open article jobs. Choose a language and articles above to ask for translations.")));
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
        // Kept from GitHub for a couple of minutes, and refreshed behind the page after that.
        d.fetched_at ? h("p", { class: "admin-sub" }, "Read from GitHub " + when(d.fetched_at) + ".") : null,
        d.counts ? h("div", { class: "admin-tiles" }, tile(num(d.counts.open), "open"), tile(num(d.counts.in_review), "with a pull request open"),
          tile(num(d.counts.stale), "stalled", d.counts.stale ? "bad" : ""), tile(num(d.counts.done), "closed in " + d.days + " days")) : null,
        h("div", { class: "admin-toolbar" }, seg([["open", "Open"], ["stale", "Stalled"], ["closed", "Closed"], ["all", "All"]], WORK.state, function (v) { WORK.state = v; route(); }), kind),
        items.length ? table(["Issue", "What", "State", "Pull requests", "Filed"], rows)
          : empty(WORK.state === "stale" ? "Nothing has stalled: every open job has a pull request, or was filed in the last " + d.stale_hours + " hours."
            : "No " + (WORK.state === "all" ? "" : WORK.state + " ") + "jobs " + (WORK.kind ? "of this kind " : "") + "filed in the last " + d.days + " days.",
            WORK.state !== "all" || WORK.kind ? [["Show all the work", function () { WORK.state = "all"; WORK.kind = ""; route(); }]]
              : [["File a drafting job", "#jobs"]])];
    });
  };

  // Similarity to the reference Bibles, per book (scripts/ngram_overlap.py).
  var OVERLAP = { book: "JHN", lang: "en", min: 6 }, LAST_BOOK = "";   // the last book compared
  VIEWS.overlap = function (arg) {
    var f = OVERLAP, asked = arg ? decodeURIComponent(arg) : f.book;
    function get(code) { return api("/api/admin/overlap/" + encodeURIComponent(code) + "/?lang=" + f.lang + "&min=" + f.min); }
    // A book the address names that isn't one (#overlap/Jon) is said beside
    // the form, which shows the last book compared, not in place of it all.
    var wrong = "";
    return get(asked).catch(function (e) {
      if (e.status !== 404) throw e;
      wrong = e.message;
      return get(LAST_BOOK && LAST_BOOK !== asked ? LAST_BOOK : "JHN");
    }).then(function (d) {
      f.book = d.book || asked.toUpperCase();   // after a wrong one, the book shown
      LAST_BOOK = f.book;
      var book = select("overlap-book", (d.books || [{ code: f.book, name: f.book }]).map(function (b) { return [b.code, b.name]; }), f.book);
      book.setAttribute("aria-label", "Book");
      // Every reading language, from the API; one with no reference Bible loaded says so.
      var lang = select("overlap-lang", (d.languages || [{ code: f.lang, name: f.lang, references: 1 }]).map(function (l) {
        return [l.code, l.references ? l.name : l.name + " (no reference Bible loaded)"];
      }), f.lang);
      lang.setAttribute("aria-label", "Language");
      var min = select("overlap-min", [["5", "5+ words"], ["6", "6+ words"], ["8", "8+ words"], ["10", "10+ words"]], String(f.min));
      min.setAttribute("aria-label", "Shortest run");
      var form = h("form", { class: "admin-toolbar" }, book, lang, min, h("button", { type: "submit", class: "admin-btn" }, "Compare"));
      var problem = h("p", { class: "admin-note" + (wrong ? " bad" : ""), role: "status" }, wrong);
      form.addEventListener("submit", function (e) {
        e.preventDefault(); f.book = book.value; f.lang = lang.value; f.min = +min.value;
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
        form, problem,
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
          A.FLASH = "Filed as #" + r.number + ".";
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
        })) : empty("No open drafting jobs. File one below, or queue every missing book at once.")));
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
    function line(j) { return h("li", null, bookName(d, j.book) + ": " + j.languages.map(langName).join(", ")); }
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
            api("/api/admin/jobs/bulk/", { method: "POST", body: asked }).then(function (run) {
              watchFiling(run, result);
            }, function (err) { busy(b, false); note(status, err, true); });
          }, "admin-btn primary")]);
      }, function (err) { note(status, err, true); }).then(function () { busy(preview, false); });
    });
    return h("section", { class: "admin-block" }, h("h2", null, "Queue missing books"),
      h("p", null, "Files one job per book that still lacks any of the languages, in Bible order, skipping languages an open job already asks for."), form);
  }
  // The server files a bulk request's jobs one by one in the background
  // (GitHub takes up to 10 s a job); this shows how far it has got, asking
  // again every POLL_MS, until it is done or has stopped.
  var POLL_MS = 2000;
  function watchFiling(run, where) {
    var line = h("p", { role: "status" });
    var meter = h("div");
    where.textContent = "";
    add(where, [line, meter]);
    function finish(r) {
      A.FLASH = "Filed " + plural(r.filed.length, "job") + (r.error ? ". " + r.error
        : r.remaining ? "; " + r.remaining + " more to queue." : ".");
      forget(C.drops("/api/admin/jobs/bulk/"));   // the jobs filed since the request
      route();
    }
    function show(r) {
      if (!document.body.contains(where)) return;   // left the page: the jobs list will show them
      if (r.state !== "filing") { finish(r); return; }
      line.textContent = "Filing " + (r.filed.length + 1) + " of " + r.plan.length + "… You can leave this page; filing goes on.";
      meter.textContent = "";
      meter.appendChild(bar(r.filed.length, r.plan.length));
      setTimeout(function () {
        request("/api/admin/jobs/bulk/" + encodeURIComponent(r.id) + "/", {}).then(show, function (e) {
          line.textContent = "";
          note(line, e, true);
        });
      }, POLL_MS);
    }
    show(run);
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
      var subject = A.keepDraft(h("input", { id: "mail-subject", maxlength: 200, required: true }), "mail.subject");
      var body = A.keepDraft(h("textarea", { id: "mail-body", rows: 10, required: true }), "mail.body");
      var test = h("button", { type: "button", class: "admin-btn" }, "Send a test to me");
      var count = function () { return d.audiences.filter(function (a) { return a.key === audience.value; })[0].count; };
      function payload(isTest) { return { subject: subject.value, body: body.value, audience: audience.value, test: isTest }; }
      test.addEventListener("click", function () {
        busy(test, true);
        api("/api/admin/emails/", { method: "POST", body: payload(true) }).then(function () {
          note(status, "Test sent to " + A.ME.email + ".");
        }, function (e) { note(status, e, true); }).then(function () { busy(test, false); });
      });
      var sendWrap = h("span");
      function drawSend() {
        sendWrap.textContent = "";
        sendWrap.appendChild(confirmButton("Send", "Send to " + plural(count(), "person", "people") + "?", function (b) {
          api("/api/admin/emails/", { method: "POST", body: payload(false) }).then(function (r) {
            A.dropDraft("mail.subject", "mail.body");
            A.FLASH = "Sent to " + plural(r.sent, "person", "people") + (r.failed ? "; " + r.failed + " failed" : "") + ".";
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
  filtered("articles", ARTICLES);
  filtered("work", WORK);
  filtered("overlap", OVERLAP, null, function (arg, f) {
    f.book = arg.toUpperCase();
    return "";
  });
  filtered("export", EXPORT, { lang: "en", level: "B", type: "usfm", numbering: "english", books: "" });
});
