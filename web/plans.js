// Reading plans (data/plans.json; plans_page, plan_page, plan_today and
// plan_bar in scripts/build_site.py). A reader's progress is kept in this
// browser only, in localStorage under one key, owb.plans:
//
//   {"active": "mark",                       the plan being read, or null
//    "at": 1791760739987,                     when that last changed
//    "plans": {"mark": {"start": "2026-10-12", the day it was started
//                       "done": [1, 2, 3],    the days marked done
//                       "at": 1791760739987}}} when this plan last changed
//
// A day is done only when the reader says so (a button), and "today" is
// simply the first day not done yet: a plan waits for its reader, so there
// are no streaks and nothing is ever overdue. Everything that reads or
// writes owb.plans goes through load() and save() below, which are also
// window.OWBPlans. save() stamps the times, so a signed-in reader's progress
// merges with their other devices' (site.js; backend accounts/reading.py),
// and announces each change as an "owb:plans-change" event on document; a
// sync that brings changes in announces "owb:synced".
//
// The plans themselves, their names and each day's chapters in the page's
// language, come from /plans-<lang>.json (plans_json); a plan started in
// English that this language cannot offer yet is read from the English file.
//
// The reader's own plans (my_plans_page) are kept as owb.myplans, in the
// shape of data/plans.json, and their progress in owb.plans like any other:
//
//   {"my-k3x9q2": {"name": "Advent", "days": [["LUK.1", "LUK.2"], ...], "at": ...}}
//
// A deleted one is kept as {at}, so the reader's other devices delete it too.
// One is shared as a link to the page, #n=<name>&d=LUK.1,LUK.2;MAT.1 (days
// apart by ";"), which the page offers to save. Any plan's days not yet done
// can be taken into a calendar as an .ics file, a day each from today.
(function () {
  "use strict";
  var KEY = "owb.plans";

  function load() {
    var s = null;
    try { s = JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { /* none, or unreadable */ }
    if (!s || typeof s !== "object") s = {};
    if (!s.plans || typeof s.plans !== "object") s.plans = {};
    Object.keys(s.plans).forEach(function (id) {
      var p = s.plans[id];
      if (!p || typeof p !== "object" || !Array.isArray(p.done)) delete s.plans[id];
    });
    if (typeof s.active !== "string" || !s.plans[s.active]) s.active = null;
    return s;
  }

  function save(s) {
    var before = load(), now = Date.now();
    Object.keys(s.plans).forEach(function (id) {
      var p = s.plans[id], was = before.plans[id];
      p.at = was && was.start === p.start && String(was.done) === String(p.done) ? was.at : now;
    });
    s.at = s.active === before.active ? before.at : now;
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* storage blocked: this page only */ }
    try { document.dispatchEvent(new CustomEvent("owb:plans-change")); } catch (e) { /* old browser */ }
  }

  var MINE = "owb.myplans";
  function mine() {
    var all = null;
    try { all = JSON.parse(localStorage.getItem(MINE) || "null"); } catch (e) { /* none */ }
    return all && typeof all === "object" && !Array.isArray(all) ? all : {};
  }
  function saveMine(all) {
    try { localStorage.setItem(MINE, JSON.stringify(all)); } catch (e) { /* storage blocked */ }
    try { document.dispatchEvent(new CustomEvent("owb:myplans")); } catch (e) { /* old browser */ }
  }

  window.OWBPlans = { key: KEY, load: load, save: save, mine: mine };

  var lang = document.documentElement.lang;

  function today() {
    var d = new Date();
    return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  }

  function startPlan(s, id) {
    if (!s.plans[id]) s.plans[id] = { start: today(), done: [] };
    s.active = id;
  }

  function setDone(rec, day, on) {
    var done = rec.done.filter(function (d) { return d !== day; });
    if (on) done.push(day);
    rec.done = done.sort(function (a, b) { return a - b; });
  }

  // The day a plan has reached: its first day not done (0 once all are).
  function current(rec, total) {
    for (var d = 1; d <= total; d++) if (rec.done.indexOf(d) < 0) return d;
    return 0;
  }

  function fill(text, values) {
    return text.replace(/\{(\w+)\}/g, function (m, k) { return k in values ? values[k] : m; });
  }

  function dateText(iso) {
    var p = String(iso || "").split("-");
    if (p.length !== 3) return "";
    try {
      return new Date(+p[0], p[1] - 1, +p[2]).toLocaleDateString(lang, { day: "numeric", month: "long", year: "numeric" });
    } catch (e) { return iso; }
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  // The plans files, fetched once each.
  var files = {};
  function fetchFile(src) {
    if (!files[src]) {
      files[src] = fetch(src, { credentials: "same-origin" }).then(function (r) {
        if (!r.ok) throw new Error(src + ": " + r.status);
        return r.json();
      });
    }
    return files[src];
  }

  // One of the reader's own plans, as plans_json gives a plan: chapters
  // named and linked in this language (in English where it has not got
  // them yet).
  function ownPlan(file, id, p) {
    var have = {};
    file.books.forEach(function (b) { have[b[0]] = b[2]; });
    return {
      name: p.name, url: file.mine + "#id=" + id, own: true,
      days: p.days.map(function (day) {
        return day.map(function (ref) {
          var b = ref.split(".")[0], c = +ref.split(".")[1];
          var here = (have[b] || []).indexOf(c) >= 0;
          return { b: b, c: c, n: (file.names[b] || b) + " " + c,
                   u: (here ? file.chapter : file.chapter_en).replace("{b}", b.toLowerCase()).replace("{c}", c) };
        });
      })
    };
  }

  // {ui, plan, lang}: the plan id, from this language's file or English's,
  // with this language's labels. Rejects when neither has it.
  function planData(box, id) {
    if (/^my-/.test(id)) {
      return fetchFile(box.getAttribute("data-plans")).then(function (own) {
        var p = mine()[id];
        if (!p || !p.days) throw new Error("no plan " + id);
        return { ui: own.ui, plan: ownPlan(own, id, p), lang: lang };
      });
    }
    return fetchFile(box.getAttribute("data-plans")).then(function (own) {
      if (own.plans[id]) return { ui: own.ui, plan: own.plans[id], lang: lang };
      var en = box.getAttribute("data-plans-en");
      if (lang === "en" || !en) throw new Error("no plan " + id);
      return fetchFile(en).then(function (eng) {
        if (!eng.plans[id]) throw new Error("no plan " + id);
        return { ui: own.ui, plan: eng.plans[id], lang: "en" };
      });
    });
  }

  function refs(day) {
    return day.map(function (c) { return c.n; }).join(", ");
  }

  // A name or chapter shown in English on a page in another language.
  function tagLang(node, textLang) {
    if (textLang !== lang) node.lang = textLang;
    return node;
  }

  // The day ticks: one per day, done, today or to come. The pattern is
  // drawn for the eye; its label says the same in words.
  function ticks(ui, rec, total) {
    var day = current(rec, total);
    var box = el("div", "plan-ticks");
    box.setAttribute("role", "img");
    box.setAttribute("aria-label", day
      ? fill(ui.grid, { done: rec.done.length, total: total, day: day })
      : fill(ui.grid_finished, { total: total }));
    for (var d = 1; d <= total; d++) {
      var state = rec.done.indexOf(d) >= 0 ? "done" : d === day ? "today" : "ahead";
      box.appendChild(el("span", "tick " + state));
    }
    return box;
  }

  function legend(ui) {
    var p = el("p", "plan-legend");
    p.setAttribute("aria-hidden", "true");
    ["done", "today", "ahead"].forEach(function (k) {
      var item = el("span");
      item.appendChild(el("span", "tick " + k));
      item.appendChild(document.createTextNode(ui["legend_" + k]));
      p.appendChild(item);
    });
    return p;
  }

  // Home and plans pages: the reader's current plan.
  function drawToday(box) {
    var s = load();
    var id = s.active;
    if (!id) { box.hidden = true; box.textContent = ""; return; }
    planData(box, id).then(function (d) {
      var rec = load().plans[id];
      if (!rec) { box.hidden = true; return; }
      var ui = d.ui, plan = d.plan, total = plan.days.length, day = current(rec, total);
      box.textContent = "";
      box.appendChild(el("p", "eyebrow", ui.your_plan));
      var h = el("h2");
      h.id = "plan-today-h";
      var name = tagLang(el("a", null, plan.name), d.lang);
      name.href = plan.url;
      h.appendChild(name);
      box.appendChild(h);
      var actions = el("p", "actions");
      if (day) {
        var where = el("p", "plan-where");
        where.appendChild(el("strong", null, fill(ui.day_of, { day: day, total: total })));
        where.appendChild(document.createTextNode(" · "));
        where.appendChild(tagLang(el("span", null, refs(plan.days[day - 1])), d.lang));
        box.appendChild(where);
        var read = tagLang(el("a", "button", fill(ui.read, { ref: refs(plan.days[day - 1]) })), d.lang);
        read.href = plan.days[day - 1][0].u;
        actions.appendChild(read);
      } else {
        var fin = el("p", "plan-where");
        fin.appendChild(document.createTextNode(fill(ui.finished, { plan: plan.name })));
        box.appendChild(fin);
        var more = el("a", "button ghost", ui.another);
        more.href = box.getAttribute("data-plans-page") || plan.url.replace(/[^/]+\/$/, "");
        actions.appendChild(more);
      }
      box.appendChild(ticks(ui, rec, total));
      box.appendChild(legend(ui));
      box.appendChild(actions);
      box.hidden = false;
    }).catch(function () { box.hidden = true; });
  }

  // The end of a chapter that is a day's reading in the current plan.
  function drawBar(box, justMarked, undone) {
    var s = load();
    var id = s.active;
    if (!id) { box.hidden = true; return; }
    var book = box.getAttribute("data-book"), chapter = +box.getAttribute("data-chapter");
    planData(box, id).then(function (d) {
      var rec = load().plans[id];
      if (!rec) { box.hidden = true; return; }
      var ui = d.ui, plan = d.plan, total = plan.days.length;
      function here(n) {
        return plan.days[n - 1].some(function (c) { return c.b === book && c.c === chapter; });
      }
      // Today's day if this chapter is in it, else the first day not done
      // that has it (a reader may read ahead); after marking, that day.
      var day = justMarked || 0, d0 = current(rec, total);
      if (!day && d0 && here(d0)) day = d0;
      for (var n = 1; !day && n <= total; n++) if (rec.done.indexOf(n) < 0 && here(n)) day = n;
      if (!day) { box.hidden = true; return; }
      box.textContent = "";
      var text = el("p", "plan-bar-text");
      var link = el("a", null, fill(ui.bar, { day: day, plan: plan.name }));
      link.href = plan.url;
      text.appendChild(tagLang(link, d.lang));
      box.appendChild(text);
      var focus = null;
      if (rec.done.indexOf(day) < 0) {
        var mark = el("button", "button plan-mark");
        mark.type = "button";
        mark.innerHTML = '<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
          'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';
        mark.appendChild(document.createTextNode(ui.mark_done));
        mark.addEventListener("click", function () {
          var s2 = load();
          if (!s2.plans[id]) return;
          setDone(s2.plans[id], day, true);
          save(s2);
          drawBar(box, day);
        });
        box.appendChild(mark);
      } else {
        var done = el("p", "plan-done");
        done.appendChild(el("span", null, fill(ui.marked, { day: day })));
        var next = current(rec, total);
        if (next) {
          // Read ahead: the link goes back to the day the plan has reached
          // (the home card's "today"), and says so.
          var label = next < day ? ui.still : ui.next;
          var a = tagLang(el("a", "plan-next", fill(label, { ref: refs(plan.days[next - 1]) })), d.lang);
          a.href = plan.days[next - 1][0].u;
          done.appendChild(document.createTextNode(" "));
          done.appendChild(a);
          focus = a;
        } else {
          done.appendChild(document.createTextNode(" " + fill(ui.finished, { plan: plan.name })));
        }
        text.appendChild(done);
        var undo = el("button", "plan-undo", ui.undo);
        undo.type = "button";
        undo.addEventListener("click", function () {
          var s2 = load();
          if (!s2.plans[id]) return;
          setDone(s2.plans[id], day, false);
          save(s2);
          drawBar(box, 0, true);
        });
        box.appendChild(undo);
        if (!focus) focus = undo;
      }
      box.hidden = false;
      // The bar is aria-live from the start (plan_bar), so marking and
      // undoing are announced.
      if (justMarked && focus) focus.focus();
      if (undone) box.querySelector(".plan-mark").focus();
    }).catch(function () { box.hidden = true; });
  }

  // The plan's days not yet done, a day each from today, as a calendar
  // file (RFC 5545) for the reader's own calendar app.
  function icsText(ui, id, plan, rec) {
    function esc(text) { return String(text).replace(/[\\;,]/g, function (c) { return "\\" + c; }).replace(/\n/g, "\\n"); }
    function ymd(d) { return d.getFullYear() + ("0" + (d.getMonth() + 1)).slice(-2) + ("0" + d.getDate()).slice(-2); }
    // Lines over 75 octets are folded; cut by characters, which is safe for
    // the short lines here.
    function fold(line) {
      var out = [];
      while (line.length > 70) { out.push(line.slice(0, 70)); line = " " + line.slice(70); }
      out.push(line);
      return out.join("\r\n");
    }
    var stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+/, "");
    var lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Open Word Bible//Reading plans//EN",
                 "CALSCALE:GREGORIAN", "X-WR-CALNAME:" + esc(plan.name)];
    var at = new Date(), n = 0;
    plan.days.forEach(function (day, i) {
      if (rec && rec.done.indexOf(i + 1) >= 0) return;
      var d = new Date(at.getFullYear(), at.getMonth(), at.getDate() + n++);
      var next = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1);
      var link = location.origin + day[0].u;
      lines.push("BEGIN:VEVENT", "UID:" + id + "-" + (i + 1) + "-" + stamp + "@openwordbible.org", "DTSTAMP:" + stamp,
                 "DTSTART;VALUE=DATE:" + ymd(d), "DTEND;VALUE=DATE:" + ymd(next),
                 "SUMMARY:" + esc(fill(ui.ics_day, { day: i + 1, ref: refs(day), plan: plan.name })),
                 "DESCRIPTION:" + esc(link), "URL:" + link, "TRANSP:TRANSPARENT", "END:VEVENT");
    });
    lines.push("END:VCALENDAR");
    return lines.map(fold).join("\r\n") + "\r\n";
  }
  function downloadIcs(box, id) {
    planData(box, id).then(function (d) {
      var text = icsText(d.ui, id, d.plan, load().plans[id]);
      var a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([text], { type: "text/calendar" }));
      a.download = id + ".ics";
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
    });
  }

  // A plan's own page: start, stop or start over, and tick off days.
  function drawPlanPage(box) {
    var id = box.getAttribute("data-plan-page");
    var total = +box.getAttribute("data-total");
    var startBtn = box.querySelector("[data-plan-start]");
    var readLink = box.querySelector("[data-plan-read]");
    var stopBtn = box.querySelector("[data-plan-stop]");
    var restartBtn = box.querySelector("[data-plan-restart]");
    var status = box.querySelector("[data-plan-status]");
    var startLabel = startBtn.textContent;
    var days = Array.prototype.slice.call(document.querySelectorAll(".plan-day[data-day]"));
    var icsBtn = box.querySelector("[data-plan-ics]");
    if (icsBtn) {
      icsBtn.hidden = !window.Blob;
      icsBtn.addEventListener("click", function () { downloadIcs(box, id); });
    }
    var ui = null;

    function render() {
      var s = load(), rec = s.plans[id], active = s.active === id;
      var day = rec ? current(rec, total) : 0;
      startBtn.hidden = active;
      startBtn.textContent = rec ? startBtn.getAttribute("data-continue") : startLabel;
      stopBtn.hidden = !active;
      restartBtn.hidden = !(rec && rec.done.length);
      readLink.hidden = !(active && day);
      if (active && day) {
        var li = days[day - 1], first = li.querySelector(".plan-day-chs a");
        readLink.href = first.getAttribute("href");
        var chs = Array.prototype.map.call(li.querySelectorAll(".plan-day-chs a"), function (a) { return a.textContent; });
        if (ui) readLink.textContent = fill(ui.read, { ref: chs.join(", ") });
      }
      status.textContent = "";
      if (rec && ui) {
        var bits = [day ? fill(ui.day_of, { day: day, total: total }) : fill(ui.grid_finished, { total: total })];
        if (rec.start) bits.push(fill(ui.started, { date: dateText(rec.start) }));
        status.textContent = bits.join(" · ");
      }
      days.forEach(function (li, i) {
        var n = i + 1, done = !!rec && rec.done.indexOf(n) >= 0;
        var toggle = li.querySelector("[data-plan-toggle]");
        toggle.hidden = !rec;
        toggle.setAttribute("aria-pressed", done ? "true" : "false");
        li.classList.toggle("done", done);
        li.classList.toggle("today", !!rec && n === day);
        if (rec && n === day) li.setAttribute("aria-current", "step");
        else li.removeAttribute("aria-current");
      });
    }

    startBtn.addEventListener("click", function () {
      var s = load();
      startPlan(s, id);
      save(s);
      render();
      (readLink.hidden ? stopBtn : readLink).focus();
    });
    stopBtn.addEventListener("click", function () {
      var s = load();
      if (s.active === id) s.active = null;
      save(s);
      render();
      startBtn.focus();
    });
    restartBtn.addEventListener("click", function () {
      var s = load();
      s.plans[id] = { start: today(), done: [] };
      s.active = id;
      save(s);
      render();
      (readLink.hidden ? stopBtn : readLink).focus();
    });
    days.forEach(function (li, i) {
      var toggle = li.querySelector("[data-plan-toggle]");
      toggle.addEventListener("click", function () {
        var s = load();
        if (!s.plans[id]) return;
        setDone(s.plans[id], i + 1, toggle.getAttribute("aria-pressed") !== "true");
        save(s);
        render();
      });
    });

    render();
    var src = box.hasAttribute("data-plans") ? box : document.querySelector("[data-plans]");
    var file = src ? src.getAttribute("data-plans") : null;
    if (file) fetchFile(file).then(function (f) { ui = f.ui; render(); }).catch(function () { /* labels only */ });
    return render;
  }

  // The plans page: the reader's plan is marked among the others.
  function markCards() {
    var s = load();
    document.querySelectorAll("[data-plan-card]").forEach(function (a) {
      var mine = a.getAttribute("data-plan-card") === s.active;
      a.querySelector(".plan-mine").hidden = !mine;
      a.classList.toggle("mine", mine);
    });
  }

  // The reader's own plans (my_plans_page): the list, one plan opened to
  // read (#id=), a plan shared by link (#n=&d=) to save, and the form that
  // makes or changes one. Returns the open plan's render, if any.
  function newId() {
    var a = "abcdefghijklmnopqrstuvwxyz0123456789", id = "my-";
    var r = new Uint32Array(8);
    (window.crypto || window.msCrypto).getRandomValues(r);
    for (var i = 0; i < 8; i++) id += a[r[i] % a.length];
    return id;
  }
  function shareLink(file, p) {
    return location.origin + file.mine + "#n=" + encodeURIComponent(p.name) +
      "&d=" + p.days.map(function (day) { return day.join(","); }).join(";");
  }
  // A plan from a share link's fragment, or null: only chapters that exist.
  function fromLink(hash, file) {
    var q = {};
    hash.replace(/^#/, "").split("&").forEach(function (kv) {
      var i = kv.indexOf("=");
      if (i > 0) { try { q[kv.slice(0, i)] = decodeURIComponent(kv.slice(i + 1)); } catch (e) { /* bad */ } }
    });
    if (!q.n || !q.d) return null;
    var known = {};
    file.books.forEach(function (b) { known[b[0]] = true; });
    var days = q.d.split(";").map(function (day) {
      return day.split(",").filter(function (ref) {
        return /^[1-4A-Z]{3}\.\d{1,3}$/.test(ref) && (known[ref.split(".")[0]] || file.names[ref.split(".")[0]]);
      }).slice(0, 30);
    }).filter(function (day) { return day.length; }).slice(0, 400);
    return days.length ? { name: q.n.replace(/\s+/g, " ").trim().slice(0, 80), days: days } : null;
  }
  function copy(text, button, done) {
    var label = button.textContent;
    function said(t) { button.textContent = t; setTimeout(function () { button.textContent = label; }, 1600); }
    if (navigator.clipboard && navigator.clipboard.writeText)
      navigator.clipboard.writeText(text).then(function () { said(done); }, function () { window.prompt("", text); });
    else window.prompt("", text);
  }

  function drawMine(root, file) {
    var ui = file.ui;
    var view = root.querySelector(".myplan-view"), shared = root.querySelector(".myplan-shared");
    var listBox = root.querySelector(".myplan-list ul"), emptyNote = root.querySelector(".myplan-empty");
    var form = document.getElementById("myplan-form"), note = document.getElementById("myplan-note");
    var dayList = form.querySelector(".myplan-days");
    var draft = { id: null, name: "", days: [] };
    var openRender = null;

    function length(p) { return fill(ui.length, { n: p.days.length }); }

    function drawList() {
      var all = mine(), s = load();
      var ids = Object.keys(all).filter(function (id) { return all[id].days; })
        .sort(function (a, b) { return all[b].at - all[a].at; });
      listBox.textContent = "";
      emptyNote.hidden = ids.length > 0;
      ids.forEach(function (id) {
        var p = all[id];
        var li = el("li");
        var card = el("div", "a-card plan-card myplan-card" + (s.active === id ? " mine" : ""));
        var title = el("a", "a-title", p.name);
        title.href = file.mine + "#id=" + id;
        card.appendChild(title);
        var meta = el("span", "a-meta", length(p) + (s.active === id ? " \u00b7 " + ui.yours : ""));
        card.appendChild(meta);
        var row = el("p", "myplan-actions");
        var edit = el("button", "plan-undo", ui.edit);
        edit.type = "button";
        edit.addEventListener("click", function () {
          draft = { id: id, name: p.name, days: p.days.map(function (d) { return d.slice(); }) };
          drawDraft();
          form.name.focus();
          form.scrollIntoView({ block: "start" });
        });
        row.appendChild(edit);
        var share = el("button", "plan-undo", ui.share);
        share.type = "button";
        share.addEventListener("click", function () { copy(shareLink(file, p), share, ui.copied); });
        row.appendChild(share);
        var del = el("button", "plan-undo", ui.delete);
        del.type = "button";
        del.addEventListener("click", function () {
          if (!del.classList.contains("armed")) {
            del.classList.add("armed");
            del.textContent = ui.delete_confirm;
            setTimeout(function () { del.classList.remove("armed"); del.textContent = ui.delete; }, 4000);
            return;
          }
          var all2 = mine();
          all2[id] = { at: Date.now() };
          saveMine(all2);
          var s2 = load();
          if (s2.plans[id]) { delete s2.plans[id]; if (s2.active === id) s2.active = null; save(s2); }
          if (location.hash === "#id=" + id) history.replaceState(null, "", location.pathname);
          drawAll2();
        });
        row.appendChild(del);
        card.appendChild(row);
        li.appendChild(card);
        listBox.appendChild(li);
      });
    }

    // The open plan, laid out as a plan's page (plan_page) for drawPlanPage.
    function drawView(id) {
      view.textContent = "";
      openRender = null;
      var p = mine()[id];
      if (!p || !p.days) {
        view.hidden = !id;
        if (id) view.appendChild(el("p", "notice", ui.not_here));
        return;
      }
      var plan = ownPlan(file, id, p);
      view.appendChild(el("h2", null, plan.name));
      view.appendChild(el("p", "dek", length(p)));
      var controls = el("div", "plan-controls");
      controls.setAttribute("data-plan-page", id);
      controls.setAttribute("data-total", plan.days.length);
      controls.setAttribute("data-plans", root.getAttribute("data-plans"));
      var actions = el("p", "actions");
      var start = el("button", "button", ui.start);
      start.type = "button";
      start.setAttribute("data-plan-start", "");
      start.setAttribute("data-continue", ui["continue"]);
      var read = el("a", "button");
      read.setAttribute("data-plan-read", "");
      read.hidden = true;
      read.href = "#";
      var stop = el("button", "button ghost", ui.stop);
      stop.type = "button";
      stop.setAttribute("data-plan-stop", "");
      var restart = el("button", "button ghost", ui.restart);
      restart.type = "button";
      restart.setAttribute("data-plan-restart", "");
      [start, read, stop, restart].forEach(function (b) { actions.appendChild(b); });
      controls.appendChild(actions);
      var status = el("p", "plan-status");
      status.setAttribute("data-plan-status", "");
      status.setAttribute("aria-live", "polite");
      controls.appendChild(status);
      var extras = el("p", "plan-extras");
      var ics = el("button", "plan-undo", ui.ics);
      ics.type = "button";
      ics.setAttribute("data-plan-ics", "");
      extras.appendChild(ics);
      var remind = el("a", "plan-remind", ui.remind);
      remind.href = root.getAttribute("data-account") + "#email";
      extras.appendChild(document.createTextNode(" "));
      extras.appendChild(remind);
      controls.appendChild(extras);
      view.appendChild(controls);
      var ol = el("ol", "plan-days");
      plan.days.forEach(function (day, i) {
        var li = el("li", "plan-day");
        li.setAttribute("data-day", i + 1);
        li.appendChild(el("span", "plan-day-n", fill(ui.day, { n: i + 1 })));
        var chs = el("span", "plan-day-chs");
        day.forEach(function (c, j) {
          if (j) chs.appendChild(document.createTextNode(", "));
          var a = el("a", null, c.n);
          a.href = c.u;
          chs.appendChild(a);
        });
        li.appendChild(chs);
        var tick = el("button", "plan-tick");
        tick.type = "button";
        tick.setAttribute("data-plan-toggle", "");
        tick.setAttribute("aria-pressed", "false");
        tick.setAttribute("aria-label", fill(ui.day_done, { n: i + 1 }));
        tick.hidden = true;
        tick.textContent = "\u2713";
        li.appendChild(tick);
        ol.appendChild(li);
      });
      view.appendChild(ol);
      view.hidden = false;
      openRender = drawPlanPage(controls);
    }

    // A plan shared by link: shown with a button to keep it.
    function drawShared() {
      shared.textContent = "";
      var p = fromLink(location.hash, file);
      shared.hidden = !p;
      if (!p) return;
      shared.appendChild(el("p", "eyebrow", ui.shared));
      shared.appendChild(el("h2", null, p.name));
      shared.appendChild(el("p", "dek", length(p) + " \u00b7 " + p.days.map(function (d) {
        return d.map(function (ref) { return (file.names[ref.split(".")[0]] || ref) + " " + ref.split(".")[1]; }).join(", ");
      }).slice(0, 3).join(" \u00b7 ") + (p.days.length > 3 ? " \u2026" : "")));
      var keep = el("button", "button", ui.shared_save);
      keep.type = "button";
      keep.addEventListener("click", function () {
        var all = mine(), id = newId();
        all[id] = { name: p.name, days: p.days, at: Date.now() };
        saveMine(all);
        location.hash = "#id=" + id;
      });
      shared.appendChild(keep);
    }

    // The form: chapters are added a range at a time, so many a day.
    var books = file.books;
    function bookOf(code) { return books.filter(function (b) { return b[0] === code; })[0]; }
    function chapterOptions() {
      var b = bookOf(form.book.value);
      [form.from, form.to].forEach(function (sel, k) {
        sel.textContent = "";
        (b ? b[2] : []).forEach(function (c) {
          var o = el("option", null, String(c));
          o.value = c;
          sel.appendChild(o);
        });
        if (k === 1 && b) sel.value = b[2][b[2].length - 1];
      });
    }
    books.forEach(function (b) {
      var o = el("option", null, b[1]);
      o.value = b[0];
      form.book.appendChild(o);
    });
    form.book.addEventListener("change", chapterOptions);
    chapterOptions();

    function drawDraft() {
      form.name.value = draft.name;
      dayList.textContent = "";
      draft.days.forEach(function (day, i) {
        var li = el("li", "myplan-day");
        li.appendChild(el("span", "plan-day-n", fill(ui.day, { n: i + 1 })));
        li.appendChild(el("span", "plan-day-chs", day.map(function (ref) {
          return (file.names[ref.split(".")[0]] || ref) + " " + ref.split(".")[1];
        }).join(", ")));
        var x = el("button", "plan-undo", ui.remove_day);
        x.type = "button";
        x.setAttribute("aria-label", fill(ui.remove_day_label, { n: i + 1 }));
        x.addEventListener("click", function () { draft.days.splice(i, 1); drawDraft(); });
        li.appendChild(x);
        dayList.appendChild(li);
      });
      note.textContent = draft.days.length ? length(draft) : ui.no_days;
    }
    form.name.addEventListener("input", function () { draft.name = form.name.value; });
    form.querySelector("[data-add]").addEventListener("click", function () {
      var b = bookOf(form.book.value);
      if (!b) return;
      var from = +form.from.value, to = +form.to.value, per = Math.max(1, Math.min(10, +form.per.value || 1));
      if (to < from) { var x = from; from = to; to = x; }
      var chs = b[2].filter(function (c) { return c >= from && c <= to; });
      for (var i = 0; i < chs.length && draft.days.length < 400; i += per)
        draft.days.push(chs.slice(i, i + per).map(function (c) { return b[0] + "." + c; }));
      drawDraft();
    });
    form.querySelector("[data-clear]").addEventListener("click", function () {
      draft = { id: null, name: "", days: [] };
      drawDraft();
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = form.name.value.replace(/\s+/g, " ").trim();
      if (!name) { note.textContent = ui.need_name; form.name.focus(); return; }
      if (!draft.days.length) { note.textContent = ui.no_days; return; }
      var all = mine(), id = draft.id || newId();
      all[id] = { name: name.slice(0, 80), days: draft.days, at: Date.now() };
      saveMine(all);
      draft = { id: null, name: "", days: [] };
      drawDraft();
      location.hash = "#id=" + id;
      note.textContent = ui.saved;
    });

    function drawAll2() {
      var m = location.hash.match(/^#id=(my-[a-z0-9]+)$/);
      drawShared();
      drawView(m ? m[1] : null);
      drawList();
      if (m) view.scrollIntoView({ block: "start" });
    }
    window.addEventListener("hashchange", drawAll2);
    document.addEventListener("owb:synced", drawAll2);
    window.addEventListener("storage", function (e) { if (e.key === MINE || e.key === KEY) drawAll2(); });
    drawDraft();
    drawAll2();
    return function () { if (openRender) openRender(); drawList(); };
  }

  var todays = Array.prototype.slice.call(document.querySelectorAll("[data-plan-today]"));
  var bars = Array.prototype.slice.call(document.querySelectorAll("[data-plan-bar]"));
  var pageBox = document.querySelector("[data-plan-page]");
  var mineBox = document.getElementById("myplans");
  if (mineBox) {
    fetchFile(mineBox.getAttribute("data-plans")).then(function (file) { drawMine(mineBox, file); });
    return;
  }
  if (!todays.length && !bars.length && !pageBox && !document.querySelector("[data-plan-card]")) return;
  var renderPage = pageBox ? drawPlanPage(pageBox) : null;

  function drawAll() {
    todays.forEach(drawToday);
    bars.forEach(function (b) { drawBar(b); });
    if (renderPage) renderPage();
    markCards();
  }
  drawAll();
  // Progress changed in another tab, or on another device (a sync).
  window.addEventListener("storage", function (e) { if (e.key === KEY || e.key === null) drawAll(); });
  document.addEventListener("owb:synced", drawAll);
  // ...or here, by the plan's page (the current plan above its list).
  document.addEventListener("owb:plans-change", function () {
    todays.forEach(drawToday);
    markCards();
  });
})();
