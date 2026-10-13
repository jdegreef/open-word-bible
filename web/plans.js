// Reading plans (data/plans.json; plans_page, plan_page, plan_today and
// plan_bar in scripts/build_site.py). A reader's progress is kept in this
// browser only, in localStorage under one key, owb.plans:
//
//   {"active": "mark",                       the plan being read, or null
//    "plans": {"mark": {"start": "2026-10-12", the day it was started
//                       "done": [1, 2, 3]}}}  the days marked done
//
// A day is done only when the reader says so (a button), and "today" is
// simply the first day not done yet: a plan waits for its reader, so there
// are no streaks and nothing is ever overdue. Everything that reads or
// writes owb.plans goes through load() and save() below, which are also
// window.OWBPlans, so account sync can merge progress later; save()
// announces each change as an "owb:plans-change" event on document.
//
// The plans themselves, their names and each day's chapters in the page's
// language, come from /plans-<lang>.json (plans_json); a plan started in
// English that this language cannot offer yet is read from the English file.
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
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* storage blocked: this page only */ }
    try { document.dispatchEvent(new CustomEvent("owb:plans-change")); } catch (e) { /* old browser */ }
  }

  window.OWBPlans = { key: KEY, load: load, save: save };

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

  // {ui, plan, lang}: the plan id, from this language's file or English's,
  // with this language's labels. Rejects when neither has it.
  function planData(box, id) {
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
    var src = document.querySelector("[data-plans]");
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

  var todays = Array.prototype.slice.call(document.querySelectorAll("[data-plan-today]"));
  var bars = Array.prototype.slice.call(document.querySelectorAll("[data-plan-bar]"));
  var pageBox = document.querySelector("[data-plan-page]");
  if (!todays.length && !bars.length && !pageBox && !document.querySelector("[data-plan-card]")) return;
  var renderPage = pageBox ? drawPlanPage(pageBox) : null;

  function drawAll() {
    todays.forEach(drawToday);
    bars.forEach(function (b) { drawBar(b); });
    if (renderPage) renderPage();
    markCards();
  }
  drawAll();
  // Progress changed in another tab.
  window.addEventListener("storage", function (e) { if (e.key === KEY || e.key === null) drawAll(); });
  // ...or here, by the plan's page (the current plan above its list).
  document.addEventListener("owb:plans-change", function () {
    todays.forEach(drawToday);
    markCards();
  });
})();
