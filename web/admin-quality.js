// Quality: the verse inspector (with fix requests and word links),
// uncertain decisions, key terms, consistency and checks.
// admin.js loads this the first time one of these sections is opened. A is
// what the shell shares (OWBAdmin.module): its helpers, and its state, which
// is read and written as A.ME, A.FLASH, ... so both sides see one value.
OWBAdmin.module(function (A) {
  "use strict";
  var CHECKS = A.CHECKS, CHECK_KINDS = A.CHECK_KINDS, LEVEL_NAMES = A.LEVEL_NAMES, SITE = A.SITE, VIEWS = A.VIEWS,
      add = A.add, api = A.api, approvalHistory = A.approvalHistory, bar = A.bar, busy = A.busy,
      clearing = A.clearing, decision = A.decision, empty = A.empty, filtered = A.filtered, ghFile = A.ghFile,
      h = A.h, head = A.head, langName = A.langName, live = A.live, messageCard = A.messageCard, note = A.note,
      num = A.num, pill = A.pill, plural = A.plural, rendering = A.rendering, route = A.route, seg = A.seg,
      select = A.select, stopLive = A.stopLive, table = A.table, tile = A.tile, verseName = A.verseName,
      when = A.when;

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
      var from = A.FIX_FROM && A.FIX_FROM.verse === d.verse ? A.FIX_FROM : null;
      A.FIX_FROM = null;
      var nav = h("div", { class: "admin-actions" },
        d.neighbours[0] ? h("a", { href: "#verse/" + d.neighbours[0] }, "\u2039 " + verseName(d.neighbours[0])) : null,
        d.neighbours[1] ? h("a", { href: "#verse/" + d.neighbours[1] }, verseName(d.neighbours[1]) + " \u203a") : null,
        h("a", { href: d.url, rel: "noopener" }, "Read it on the site"));
      var out = [head("Verse inspector", d.label, d.records.length ? plural(d.records.length, "sentence") + " hold this verse" +
        (d.updated ? "; last changed " + when(d.updated) : "") + "." : "No sentence holds this verse yet."), verseSearch(d.label), nav];
      if (from && from.flag) {
        out.push(h("div", { class: "admin-reply" }, h("p", { class: "admin-sub" }, "Requesting a fix from " + from.by + "'s flag:"), h("p", null, from.text),
          h("p", { class: "admin-sub" }, "The fix request joins the flag's conversation, and " + from.by + " is told.")));
      } else if (from) {
        out.push(h("div", { class: "admin-reply" }, h("p", { class: "admin-sub" }, "Requesting a fix for " + (from.from.name || from.from.email) +
          "'s " + from.kind + " (" + from.language + "):"), h("p", null, from.text),
          h("p", { class: "admin-sub" }, "The request is a public GitHub issue: it names this message by number but doesn't quote it. Put the reader's point in your own words under Why.")));
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
    var fix = A.ME.admin.indexOf("inbox") >= 0 ? fixForm(r, langs, names, from, d.verse) : null;
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
    var box = h("div", { class: "admin-links", hidden: true, id: "links-" + r.id });
    var toggle = h("button", { type: "button", class: "admin-btn", "aria-expanded": "false", "aria-controls": "links-" + r.id }, "Edit word links");
    toggle.addEventListener("click", function () {
      box.hidden = !box.hidden;
      toggle.setAttribute("aria-expanded", box.hidden ? "false" : "true");
      if (!box.hidden) draw();
    });
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

  function fixForm(r, langs, names, from, verse) {
    var open = !!from;
    var box = h("div", { class: "admin-fix", hidden: !open, id: "fix-" + r.id });
    var toggle = h("button", { type: "button", class: "admin-btn", "aria-expanded": open ? "true" : "false", "aria-controls": "fix-" + r.id }, "Request a fix");
    toggle.addEventListener("click", function () {
      box.hidden = !box.hidden;
      toggle.setAttribute("aria-expanded", box.hidden ? "false" : "true");
      if (!box.hidden) change.focus();
    });
    var lang = select("fix-lang-" + r.id, langs.map(function (c) { return [c, names[c] || c]; }),
      from && langs.indexOf(from.language) >= 0 ? from.language : langs[0]);
    var levels = h("fieldset", { class: "admin-checks-row" }, h("legend", null, "Levels"), ["L", "B", "R"].map(function (lv) {
      return h("label", null, h("input", { type: "checkbox", value: lv, checked: !from || !from.level || from.level === lv }), " " + LEVEL_NAMES[lv]);
    }));
    var change = A.keepDraft(h("textarea", { id: "fix-change-" + r.id, rows: 3, maxlength: 2000, placeholder: "What should change, e.g. use “la Parole” for “le Verbe”" }), "fix." + r.id + ".change");
    var reason = A.keepDraft(h("textarea", { id: "fix-reason-" + r.id, rows: 3, maxlength: 4000, placeholder: "Why (optional): the source, the style brief, a reader's point" }), "fix." + r.id + ".reason");
    if (from && from.flag && !reason.value) reason.value = "A reviewer flagged it: " + from.text;
    if (change.value || reason.value) {   // a request half-written: open, as it was left
      box.hidden = false;
      toggle.setAttribute("aria-expanded", "true");
    }
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
        levels: picked, change: change.value, reason: reason.value, message: from && !from.flag ? from.id : null,
        flag: from && from.flag ? from.id : null } }).then(function (res) {
        status.textContent = "";
        add(status, ["Filed as ", h("a", { href: res.url, rel: "noopener" }, "#" + res.number), "."]);
        status.className = "admin-note";
        change.value = reason.value = "";
        A.dropDraft("fix." + r.id + ".change", "fix." + r.id + ".reason");
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
      toggle.setAttribute("aria-expanded", "true");
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
            h("td", null, f.language ? langName(f.language) : "\u2014"), h("td", null, when(f.created_at)), h("td", null, f.assignees.join(", ") || "\u2014"));
        })) : empty("No open fix requests. They're filed from a verse: open one in the verse inspector and choose Request a fix on a rendering.", [["Open the verse inspector", "#verse"]])));
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
      var pages = A.pager(d, d.decisions.length, "decisions", function (o) { f.offset = o; route(); });
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
        })) : empty("No decisions match these filters.", [clearing("decisions")]),
        pages];
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

  // Consistency: how one language words each key term across the sentences
  // that use it, the terms split between wordings first.
  var CONSISTENCY = { lang: "en", level: "B" };
  VIEWS.consistency = function () {
    var f = CONSISTENCY;
    return api("/api/admin/consistency/?lang=" + f.lang + "&level=" + f.level).then(function (d) {
      var langSel = select("consistency-lang", d.languages.map(function (l) { return [l.code, l.name]; }), f.lang);
      langSel.setAttribute("aria-label", "Language");
      langSel.addEventListener("change", function () { f.lang = langSel.value; route(); });
      var fixes = A.ME.admin.indexOf("inbox") >= 0;
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
  filtered("decisions", DECISIONS);
  filtered("consistency", CONSISTENCY);
});
