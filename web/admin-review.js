// Review: the review queue and a sentence's review, the reviewer's workspace,
// assignments, flags, what imports changed and release notes.
// admin.js loads this the first time one of these sections is opened. A is
// what the shell shares (OWBAdmin.module): its helpers, and its state, which
// is read and written as A.ME, A.FLASH, ... so both sides see one value.
OWBAdmin.module(function (A) {
  "use strict";
  var C = A.C, forget = A.forget, CHECKS = A.CHECKS, CHECK_KINDS = A.CHECK_KINDS, LEVEL_NAMES = A.LEVEL_NAMES, N = A.N, VIEWS = A.VIEWS,
      add = A.add, api = A.api, assignmentsManager = A.assignmentsManager, bar = A.bar, busy = A.busy,
      clearing = A.clearing, date = A.date, decision = A.decision, diffView = A.diffView, dueText = A.dueText,
      empty = A.empty, filtered = A.filtered, h = A.h, head = A.head, keepAddress = A.keepAddress, later = A.later,
      note = A.note, num = A.num, pill = A.pill, plural = A.plural, progressText = A.progressText,
      rememberTab = A.rememberTab, rendering = A.rendering, route = A.route, saveFile = A.saveFile,
      select = A.select, sessionTab = A.sessionTab, sinceApproval = A.sinceApproval, standingPill = A.standingPill,
      table = A.table, tile = A.tile, toast = A.toast, when = A.when;

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
  function queuePicker(layerOf, status, nameOf) {
    var boxes = [], last = -1, chapter = null;
    var count = h("strong");
    var noteBox = h("input", { type: "text", id: "bulk-note", maxlength: 4000, placeholder: "What is wrong (needed to flag)" });
    var approveBtn = h("button", { type: "button", class: "admin-btn primary" }, "Approve selected");
    var flagBtn = h("button", { type: "button", class: "admin-btn" }, "Flag selected");
    var clearBtn = h("button", { type: "button", class: "admin-link" }, "Clear");
    // Approving a selection asks first, with the count and the layer, as
    // approving the rest of a chapter does.
    var ask = h("span", { class: "admin-confirm-ask", hidden: true });
    var bar = h("div", { class: "admin-bulk", hidden: true, role: "region", "aria-label": "Selected sentences" },
      count, approveBtn, ask, h("label", { class: "admin-bulk-note" }, "Note ", noteBox), flagBtn, clearBtn);
    var all = h("input", { type: "checkbox", "aria-label": "Select every sentence listed" });
    function picked() { return boxes.filter(function (b) { return b.checked; }).map(function (b) { return b.value; }); }
    function update() {
      var n = picked().length;
      if (!ask.hidden) { ask.hidden = true; approveBtn.hidden = false; }
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
        A.FLASH = verb + " " + plural(r.applied, "sentence") + "." +
          (r.skipped ? " " + num(r.skipped) + " already approved, left as they were." : "");
        // The batch can be taken back for a while, as one approval can
        // (all or nothing; the API allows it for ten minutes).
        var events = {}, layer = layerOf();
        (r.results || []).forEach(function (x) { if (x.result === "applied" && x.event) events[x.record] = x.event.id; });
        if (r.applied) {
          toast(verb + " " + plural(r.applied, "sentence") + ".", { label: "Undo", run: function (t, b) {
            api("/api/admin/review/bulk/", { method: "POST", body: { layer: layer, action: "undo", events: events } })
              .then(function (back) {
                t.close();
                toast("Taken back: " + plural(back.undone, "sentence") + ".", null, 5);
                route();
              }, function (e) { busy(b, false); t.close(); toast(e.message, null, 10); });
          } }, 15);
        }
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
    approveBtn.addEventListener("click", function () {
      var records = picked();
      var yes = h("button", { type: "button", class: "admin-btn primary" }, "Approve " + plural(records.length, "sentence"));
      var no = h("button", { type: "button", class: "admin-btn" }, "Cancel");
      yes.addEventListener("click", function () { send({ action: "approve", records: records }, yes, finished("Approved")); });
      no.addEventListener("click", function () { ask.hidden = true; approveBtn.hidden = false; approveBtn.focus(); });
      ask.textContent = "";
      var name = nameOf ? nameOf() : "";
      add(ask, [h("span", { class: "admin-sub" }, "Approve " + plural(records.length, "sentence") + (name ? " in " + name : "") + "?"), yes, no]);
      approveBtn.hidden = true;
      ask.hidden = false;
      no.focus();
    });
    flagBtn.addEventListener("click", function () {
      if (!noteBox.value.trim()) { note(status, "Say what is wrong in the note, then flag.", true); noteBox.focus(); return; }
      send({ action: "flag", note: noteBox.value, records: picked() }, flagBtn, finished("Flagged"));
    });
    // Without a reviewer role for the layer (a super admin reading it), no
    // boxes nor "approve the rest": the API refuses them (review.reviewing).
    var allowed = true;
    function box(s) {
      if (!allowed) return h("td", { class: "admin-pick" });
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
          // What the preview showed, so a sentence changed since isn't approved unread.
          var seen = {};
          r.results.forEach(function (x) { if (x.digest) seen[x.record] = x.digest; });
          yes.addEventListener("click", function () { send({ action: "approve", chapter: id, seen: seen }, yes, finished("Approved")); });
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
      return h("tr", { class: "admin-group" }, h("th", { colspan: 5, scope: "rowgroup" }, h("span", null, name), allowed ? [" ", rest(id, name)] : null));
    }
    return {
      bar: bar, box: box, chapterRow: chapterRow,
      head: function () { return h("th", { class: "admin-pick" }, allowed ? all : null); },
      allow: function (v) { allowed = v; },
      reset: function () { boxes = []; last = -1; chapter = null; update(); }
    };
  }
  function reviewQueue(layer) {
    var filters = REVIEW;
    var body = h("div");
    var more = A.moreButton();
    var offset = 0, d = null, rows = null;
    function query() {
      return "/api/admin/review/?layer=" + encodeURIComponent(layer) + "&book=" + filters.book + "&state=" + filters.state + "&offset=" + offset;
    }
    function draw(page) {
      if (!offset) {
        body.textContent = "";
        rows = h("tbody");
        pick.allow(page.may_review !== false);
        pick.reset();
        var c = page.counts;
        body.appendChild(h("div", { class: "admin-tiles" },
          tile(num(c.not_reviewed), "not reviewed"), tile(num(c.approved), "approved", "good"),
          tile(num(c.changed), "changed since approval", c.changed ? "warn" : ""), tile(num(c.flagged), "flagged", c.flagged ? "bad" : "")));
        body.appendChild(page.sentences.length ? h("div", { class: "admin-scroll" }, h("table", { class: "admin-table" },
          h("thead", null, h("tr", null, pick.head(), h("th", null, "Sentence"), h("th", null, page.layer.kind === "meaning" ? "Literal gloss" : "Balanced"),
            h("th", null, "State"), h("th", null, "Last"))), rows))
          : empty(REVIEW.state === "todo" ? "Nothing left to review here: every sentence is approved." : "No sentences match these filters.",
            REVIEW.book || REVIEW.state !== "todo" ? [clearing("review", ["layer"], "Show this layer's whole queue")] : null));
      }
      if (!offset) QUEUE = { layer: page.layer.code, rows: [], more: false };
      QUEUE.more = page.more;
      QUEUE.matching = page.matching;   // how many the filters give, for "12 of 340"
      page.sentences.forEach(function (s) {
        QUEUE.rows.push({ record: s.record, state: s.state });
        add(rows, pick.chapterRow(s));
        rows.appendChild(h("tr", null, pick.box(s),
          h("th", { scope: "row" }, h("a", { href: "#review/" + layer + "/" + s.record }, s.label), h("div", { class: "admin-sub" }, s.record)),
          h("td", { class: "admin-wrap", lang: page.layer.kind === "meaning" ? "en" : layer }, rendering(s.preview)),
          h("td", null, reviewPill(s.state), s.meaning && s.meaning !== "approved"
            ? h("div", { class: "admin-sub" }, s.meaning === "flagged" ? "Meaning flagged" : s.meaning === "changed" ? "Meaning changed since approval" : "Meaning not reviewed")
            : null),
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
    var pick = queuePicker(function () { return layer; }, status, function () { return d && d.layer ? d.layer.name : ""; });
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
    var drew = A.drawing;   // this drawing, for its keys
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
      var noteBox = h("textarea", { id: "review-note", rows: 2, maxlength: 4000,
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
      var busyNow = false, reviewBar = null, overMeaning = false;
      // Wording is read against the meaning: where its review stands, and
      // whether this layer's approval stood on a meaning that has changed.
      function meaningLine() {
        if (!d.meaning) return null;
        var m = d.meaning, last = d.trail.filter(function (e) { return e.action === "reviewed" && e.language === layer; }).pop();
        var tone = m.state === "flagged" ? " bad" : m.state === "approved" ? "" : " warn";
        return h("p", { class: "admin-meaning" + tone }, m.layer.name + ": ", reviewPill(m.state), " ",
          h("a", { href: "#review/" + m.layer.code + "/" + record }, "Open the meaning review"),
          m.state === "flagged" ? h("span", { class: "admin-sub" }, " The meaning is flagged; wording approved now may need another look once it is settled.") : null,
          last && last.meaning_changed ? h("span", { class: "admin-sub" }, " The wording was approved before the meaning changed: read it against the meaning as it is now.") : null);
      }
      function act(action, button) {
        if (busyNow) return;
        // A flag or comment says something: with the note empty (on a
        // phone, folded away), open it and ask for the words first.
        // Approving wording over a flagged meaning asks first.
        if (action === "approve" && d.meaning && d.meaning.state === "flagged" && !overMeaning) {
          note(status, "The meaning of this sentence is flagged. Approve the wording anyway? ", true);
          status.appendChild(h("button", { type: "button", class: "admin-link", onclick: function () { overMeaning = true; act("approve", button); } },
            "Approve anyway"));
          return;
        }
        if (action !== "approve" && !noteBox.value.trim()) {
          reviewBar.classList.add("noting");
          if (action === "flag") { flagging = true; flagBtn.classList.add("armed"); }
          noteBox.focus();
          note(status, action === "flag" ? "Say what is wrong in the note, then flag." : "Write the comment in the note, then press Comment.");
          return;
        }
        busyNow = true;
        busy(button, true);
        // seen: the digest of what this page shows, so a sentence changed
        // meanwhile isn't approved unread (409 "changed").
        var body = { layer: layer, action: action, note: noteBox.value };
        if (action === "approve") body.seen = d.digest;
        api("/api/admin/review/" + encodeURIComponent(record) + "/", { method: "POST", body: body })
          .then(function (res) {
            var row = listed ? rows.filter(function (x) { return x.record === record; })[0] : null;
            if (row && action !== "comment") row.state = res.state;
            var next = ahead(res.next);
            var done = { approve: "Approved ", flag: "Flagged ", comment: "Comment added to " }[action] + d.label + ".";
            A.FLASH = action !== "comment" && !next ? "That's the end of the queue." : "";
            // A slip of the a key is put right here, for a while: the step is
            // taken back (the API allows it for ten minutes) and the sentence opened again.
            toast(done, { label: "Undo", run: function (t, b) {
              api("/api/admin/review/" + encodeURIComponent(record) + "/", { method: "POST", body: { layer: layer, action: "undo", event: res.event.id } })
                .then(function (back) {
                  if (row) row.state = back.state;
                  t.close();
                  toast("Taken back: " + d.label + ".", null, 5);
                  var here = "#review/" + layer + "/" + record;
                  if (location.hash === here) route(); else location.hash = here;
                }, function (e) { busy(b, false); t.close(); toast(e.message, null, 8); });
            } }, 12);
            if (action === "comment") route();
            else location.hash = next ? "#review/" + layer + "/" + next : "#review/" + layer;
          }, function (e) {
            busyNow = false;
            busy(button, false);
            note(status, e, true);
            if (e.code === "changed") {
              status.appendChild(document.createTextNode(" "));
              status.appendChild(h("button", { type: "button", class: "admin-link", onclick: function () {
                forget(C.drops("/api/admin/review/" + record + "/"));
                route();
              } }, "Show the new wording"));
            }
          });
      }
      var approveBtn = h("button", { type: "button", class: "admin-btn primary", onclick: function () { act("approve", this); } },
        kind === "meaning" ? "Approve the meaning" : "Approve the " + d.layer.name.replace(/ wording$/, "") + " wording");
      var flagBtn = h("button", { type: "button", class: "admin-btn", onclick: function () { act("flag", this); } }, "Flag a problem");
      // Reading a layer without its reviewer role (a super admin): the
      // charter keeps approving and flagging to reviewers.
      var mayReview = d.may_review !== false;
      approveBtn.disabled = flagBtn.disabled = !mayReview;
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
          ["u", "Take back the last approval, flag or comment (while its Undo shows)"],
          ["j", "Next sentence in the queue"], ["k", "Previous sentence in the queue"],
          ["/", "Search the admin"], ["?", "Show or hide these shortcuts"], ["Esc", "Leave the note"]].map(function (k) {
          return [h("dt", null, h("kbd", null, k[0])), h("dd", null, k[1])];
        })));
      function toggleHelp() { help.hidden = !help.hidden; helpBtn.setAttribute("aria-expanded", help.hidden ? "false" : "true"); }
      var helpBtn = h("button", { type: "button", class: "admin-link", "aria-controls": "review-keys", "aria-expanded": "false", onclick: toggleHelp }, "All shortcuts");
      var hint = h("p", { class: "admin-keys" }, "Keys: ", h("kbd", null, "a"), " approve · ", h("kbd", null, "f"), " flag · ", h("kbd", null, "u"), " undo · ",
        h("kbd", null, "j"), " / ", h("kbd", null, "k"), " next / previous · ", h("kbd", null, "/"), " search · ",
        h("kbd", null, "?"), " ", helpBtn);
      function go(rec, none) {
        if (rec) location.hash = "#review/" + layer + "/" + rec;
        else note(status, none);
      }
      A.KEYS = {
        at: drew,
        a: function () { if (!approveBtn.disabled) act("approve", approveBtn); },
        f: function () {
          if (!mayReview) return;
          flagging = true;
          flagBtn.classList.add("armed");
          reviewBar.classList.add("noting");
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
        if (drew !== A.drawing) return;
        [ahead(d.next), after].forEach(function (rec, i, all) {
          if (rec && all.indexOf(rec) === i) api(sentencePath(rec), { quiet: true }).catch(function () { /* drawn with its error if opened */ });
        });
      }, 200);
      // Where this sentence is in the queue it was opened from.
      var progress = null;
      if (listed && QUEUE.matching) {
        var place = rows.map(function (x) { return x.record; }).indexOf(record) + 1;
        progress = h("span", { class: "admin-review-progress" },
          h("span", null, "Sentence " + num(place) + " of " + num(QUEUE.matching) + " in the queue"),
          h("i", { "aria-hidden": "true" }, h("b", { style: "width:" + Math.min(100, 100 * place / QUEUE.matching) + "%" })));
      }
      var trail = d.trail.length ? h("ul", { class: "admin-feed" }, d.trail.map(function (e) {
        return h("li", null, h("time", { datetime: e.at, title: new Date(e.at).toLocaleString("en-GB") }, when(e.at)),
          h("span", null, h("strong", null, e.by), " " + e.label.toLowerCase() + " (" + (e.language ? names[e.language] || e.language : "meaning") + ")",
            e.changed ? [" ", pill(e.meaning_changed ? "meaning changed since" : "changed since", "warn")] : null,
            e.note ? h("span", { class: "admin-sub" }, ": " + e.note) : null));
      })) : empty("No one has reviewed this sentence yet.");
      return [head("Review: " + d.layer.name, d.label, r.id + " · " + (r.status === "ai_draft" ? "AI-assisted" : r.status.replace(/_/g, " "))),
        h("div", { class: "admin-actions" }, h("a", { href: "#review/" + layer }, "‹ The queue"),
          d.layers.length > 1 ? d.layers.filter(function (l) { return l.code !== layer; }).map(function (l) {
            return h("a", { href: "#review/" + l.code + "/" + record }, l.name);
          }) : null,
          h("a", { href: "#verse/" + d.verse }, A.ME.admin.indexOf("inbox") >= 0 ? "Request a fix in the verse inspector" : "Verse inspector")),
        h("section", { class: "admin-block admin-record" }, h("header", { class: "admin-toolbar" }, h("h2", null, "State"), reviewPill(d.state)),
          meaningLine(), words, h("p", { class: "admin-gloss" }, "Literal gloss: " + r.literal_gloss), renderings,
          meaning.length ? [h("h3", { class: "admin-h3" }, "Meaning decisions"), h("div", { class: "admin-decisions" }, meaning.map(decision))] : null,
          mine.length ? [h("h3", { class: "admin-h3" }, (names[layer] || layer) + " decisions"), h("div", { class: "admin-decisions" }, mine.map(decision))] : null),
        hintsBlock(d.hints, layer),
        // Kept at the foot of the window while the sentence above is read,
        // so approving never means scrolling past every language.
        reviewBar = h("section", { class: "admin-block admin-review-bar" + (noteBox.value ? " noting" : ""), "aria-label": "Your review" },
          h("div", { class: "admin-review-bar-head" }, h("h2", null, "Your review"), progress),
          h("label", { class: "admin-field admin-review-note" }, "Note", noteBox), buttons,
          mayReview ? null : h("p", { class: "admin-sub" }, "You can read and comment here. Approving and flagging take a reviewer role for " +
            d.layer.name + ", for a super admin too, so the reviewed badge always means a qualified person checked it. Grant yourself one in ",
            h("a", { href: "#team" }, "Team & access"), " to review it."),
          status),
        h("div", { class: "admin-review-keys" }, hint, help),
        h("section", { class: "admin-block" }, h("h2", null, "Review trail"), trail)];
    });
  }
  // Start here, in My review: the layer's documents, and what approving
  // and flagging mean (the charter's review rules, in short). Folded away
  // once a reviewer has approved something in the layer.
  function startHere(d) {
    var meaning = d.layer.kind === "meaning";
    var box = h("details", { class: "admin-block admin-start", open: !d.changes.last_approval },
      h("summary", null, h("h2", null, "Start here")),
      d.guide.length ? h("ul", { class: "admin-files" }, d.guide.map(function (g) {
        return h("li", null, h("a", { href: A.ghFile(g.file), rel: "noopener" }, g.label), " ", h("span", { class: "admin-sub" }, g.file));
      })) : null,
      h("dl", { class: "admin-facts" },
        h("div", null, h("dt", null, "Approve"), h("dd", null, meaning
          ? "You have read the literal gloss and the meaning decisions against the " + d.layer.books + " and they say what it says. It moves the sentence on from AI-assisted."
          : "You have read every level against the meaning and it says it well in " + d.layer.name.replace(/ wording$/, "") + ". It holds until the wording, or the meaning beneath it, changes.")),
        h("div", null, h("dt", null, "Flag"), h("dd", null, "Something is wrong: say what in the note. An editor files the fix; the flag stays open until the layer is approved again.")),
        h("div", null, h("dt", null, "Comment"), h("dd", null, "A note for the next reviewer. It changes nothing."))));
    return box;
  }
  // Beside a sentence: its key terms with the form expected, any content
  // check hit on it and any long run it shares with a reference Bible,
  // from what those pages have kept (staff/hints.py).
  function hintsBlock(hints, layer) {
    if (!hints || (!hints.terms.length && !hints.checks.length && !hints.shared.length)) return null;
    var items = [];
    hints.terms.forEach(function (t) {
      items.push(h("li", null, h("strong", null, t.sense), " ", h("span", { class: "admin-sub" }, t.lemma), t.expected.length
        ? [": expected ", h("q", null, t.expected.join(", ")), t.found === false ? [" ", pill("not in Balanced", "warn")] : null]
        : null));
    });
    hints.checks.forEach(function (c) {
      items.push(h("li", null, pill(CHECK_KINDS[c.kind] || c.kind, "warn"), " ", c.term ? h("q", null, c.term) : null,
        " (" + c.levels.join(", ") + ") ", h("a", { href: "#checks?lang=" + layer }, "Checks")));
    });
    hints.shared.forEach(function (r) {
      items.push(h("li", null, pill(r.length + " words shared with " + r.edition, "info"), " (" + r.level + ") ", h("span", { class: "admin-sub" }, r.text)));
    });
    return h("section", { class: "admin-block" }, h("h2", null, "Worth checking"), h("ul", { class: "admin-checks" }, items));
  }
  // A link to the layer's review queue, showing one book (or every book)
  // and one state.
  // The queue's filters are read from its address (OWBAdminNav), so a link
  // to a book or state of it says them there.
  function queueLink(layer, book, state, text) {
    var href = N.build("review", { layer: layer, book: book || "", state: state || "todo" }, { layer: "", book: "", state: "todo" });
    return h("a", { href: href }, text);
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
      out.push(startHere(d));

      out.push(h("section", { class: "admin-block" }, h("h2", null, "Assigned to you"),
        d.assignments.length ? table(["Range", "Progress", "Due", "Standing"], d.assignments.map(function (a) {
          return h("tr", null,
            h("th", { scope: "row" }, queueLink(layer, a.book, "todo", a.label), a.note ? h("div", { class: "admin-sub" }, a.note) : null,
              a.assigned_by ? h("div", { class: "admin-sub" }, "From " + a.assigned_by.name + ", " + date(a.created_at)) : null),
            h("td", null, bar(a.progress.approved, a.progress.total), h("div", { class: "admin-sub" }, progressText(a.progress))),
            h("td", null, dueText(a)),
            h("td", null, standingPill(a)));
        })) : empty("Nothing is assigned to you in this layer. Pick any book below to review, or ask a super admin for an assignment.")));

      out.push(h("section", { class: "admin-block" }, h("h2", null, "Your flags"),
        h("p", { class: "admin-sub" }, "Open ones with what the editors have said, and those settled in the last 30 days."),
        d.flags.length ? h("div", { class: "admin-messages" }, d.flags.map(function (f) { return flagCard(f, true); }))
          : h("p", { class: "admin-ok" }, "You have no open flags in this layer.")));

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
          })) : empty("Nothing in this layer has been drafted yet, so there's nothing to review.", [["See what's drafted", "#coverage"]])));
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

  // Reviewer flags: problems reviewers have raised, open until the layer is
  // approved again. Editors act on them with a fix request.
  // A flag and its thread (staff/flags.py): replies, a fix filed from it,
  // and how it ended. Editors reply, file a fix, decline (with why) or
  // resolve; the reviewer who flagged it replies.
  var FLAG_OUTCOME = { open: ["Open", "bad"], fix: ["Fix requested", "info"], declined: ["Declined", ""],
    resolved: ["Resolved", "good"], approved: ["Approved again", "good"] };
  function flagCard(f, mine) {
    var editor = A.ME.admin.indexOf("inbox") >= 0;
    var card = h("article", { class: "admin-message admin-flag" });
    var status = h("p", { class: "admin-note", role: "status" });
    var o = FLAG_OUTCOME[f.outcome] || FLAG_OUTCOME.open;
    add(card, [
      h("header", null, pill(o[0], o[1]), " ", h("a", { href: "#review/" + f.layer.code + "/" + f.record }, f.label), " ",
        h("span", { class: "admin-sub" }, f.record + " · " + f.layer.name + " · " + when(f.at)), " ", h("a", { href: "#verse/" + f.verse }, "Verse inspector")),
      h("blockquote", null, h("strong", null, f.by + ": "), f.note),
      f.thread.length ? h("ul", { class: "admin-feed" }, f.thread.map(function (t) {
        return h("li", null, h("time", { datetime: t.at, title: new Date(t.at).toLocaleString("en-GB") }, when(t.at)),
          h("span", null, h("strong", null, t.by || "The admin"), " " + t.label.toLowerCase(), t.fix_issue ? " #" + t.fix_issue : "", t.text ? ": " + t.text : ""));
      })) : null]);
    var open = f.outcome === "open" || f.outcome === "fix";
    if (open && (editor || mine)) {
      var box = A.keepDraft(h("textarea", { id: "flag-reply-" + f.id, rows: 2, maxlength: 4000, placeholder: editor ? "A reply, or why the text stays as it is" : "A reply to the editors" }), "flag." + f.id);
      var send = function (action, button, said) {
        if ((action === "reply" || action === "decline") && !box.value.trim()) {
          note(status, action === "decline" ? "Say why the text stays as it is, then decline." : "Write the reply first.", true);
          box.focus();
          return;
        }
        busy(button, true);
        api("/api/admin/review/flags/" + f.id + "/", { method: "POST", body: { action: action, text: box.value } }).then(function () {
          A.dropDraft("flag." + f.id);
          A.FLASH = said;
          route();
        }, function (e) { busy(button, false); note(status, e, true); });
      };
      var reply = h("button", { type: "button", class: "admin-btn" }, "Reply");
      reply.addEventListener("click", function () { send("reply", reply, "Reply sent; " + f.by + " is emailed it."); });
      var buttons = [reply];
      if (editor) {
        var fix = h("button", { type: "button", class: "admin-btn" }, "File a fix from this flag");
        fix.addEventListener("click", function () {
          A.FIX_FROM = { flag: true, id: f.id, verse: f.verse, language: f.layer.kind === "meaning" ? null : f.layer.code, level: null, text: f.note, by: f.by };
          location.hash = "#verse/" + f.verse;
        });
        var decline = h("button", { type: "button", class: "admin-btn" }, "Decline");
        decline.addEventListener("click", function () { send("decline", decline, "Declined; the flag is closed and " + f.by + " is told why."); });
        var resolve = h("button", { type: "button", class: "admin-btn" }, "Resolve");
        resolve.addEventListener("click", function () { send("resolve", resolve, "Resolved; the flag is closed."); });
        buttons.push(fix, decline, resolve);
      }
      add(card, [h("label", { class: "admin-label", for: "flag-reply-" + f.id }, "Reply"), box, h("div", { class: "admin-actions" }, buttons)]);
    }
    card.appendChild(status);
    return card;
  }
  var FLAGS = { closed: "" };
  VIEWS.flags = function () {
    return api("/api/admin/review/flags/" + (FLAGS.closed ? "?closed=1" : "")).then(function (d) {
      var shown = h("label", { class: "admin-check" }, h("input", { type: "checkbox", checked: !!FLAGS.closed, onchange: function () {
        FLAGS.closed = this.checked ? "1" : ""; keepAddress(true); route();
      } }), " Show flags settled in the last 30 days");
      return [head("Text", "Reviewer flags", "Problems reviewers have flagged, newest first, each with its conversation. A flag ends when an editor files a fix that merges, declines it with a reason or resolves it, or when the layer is approved again. The reviewer hears each reply."),
        h("div", { class: "admin-toolbar" }, shown),
        d.flags.length ? h("div", { class: "admin-messages" }, d.flags.map(function (f) { return flagCard(f, false); })) : h("p", { class: "admin-ok" }, "No open flags.")];
    });
  };
  A.filtered("flags", FLAGS);

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
      var more = A.moreButton();
      more.hidden = !d.more;
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
        if (!changes.length && !offset) list.appendChild(empty("This import changed nothing in these languages. Choose another import or language above."));
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
  filtered("review", REVIEW, { layer: "", book: "", state: "todo" }, function (arg, f) {
    if (arg.indexOf("/") >= 0) return arg;   // a sentence: #review/grc/JHN.1.1.s1
    f.layer = arg;
    return "";
  });
  filtered("releases", RELEASES);
});
