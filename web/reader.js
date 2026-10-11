// Open Word Bible chapter reader. Data comes from the JSON block the build
// embeds in the page; all text is inserted with textContent.
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("owb-data").textContent);
  var STORE = "owb.settings";

  // Interface text in the page's language (i18n/<lang>.json, reader.ui).
  // Decision notes are written in English for now; readers of other
  // languages are told so in the panel.
  var UI = DATA.ui;

  // Old Testament pages read from the Hebrew: a string with an _hbo
  // variant uses it there ("Tap a Hebrew word...").
  var HEBREW = DATA.source === "hbo";
  function t(key) { return HEBREW && (key + "_hbo") in UI ? UI[key + "_hbo"] : UI[key]; }

  // The reading language is the page's (/es/... is Spanish); the footer
  // switches it. The other settings are kept across pages and languages.
  var settings = { level: "B", gender: 0, christos: 0, divine_name: 0, deity_pronoun: 0, plural_you: 0, view: 0, uncertain: 0, partner: "" };
  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || "{}");
    for (var k in settings) if (k in saved) settings[k] = saved[k];
  } catch (e) { /* storage unavailable: use defaults */ }
  settings.lang = DATA.lang;

  // A shared link may carry the sender's settings (?level=L&title=1): they
  // apply to this visit and are not saved unless the reader changes one.
  var DEFAULTS = { level: "B", gender: 0, christos: 0, divine_name: 0, deity_pronoun: 0, plural_you: 0 };
  var PARAMS = { level: "level", gender: "gender", christos: "title", divine_name: "name",
                 deity_pronoun: "pronoun", plural_you: "plural" };
  (function () {
    var q = new URLSearchParams(location.search);
    Object.keys(PARAMS).forEach(function (name) {
      var v = q.get(PARAMS[name]);
      if (v === null) return;
      if (name === "level") { if (/^[LBR]$/.test(v)) settings.level = v; }
      else if (v === "0" || v === "1") settings[name] = Number(v);
    });
  })();

  // The query for a link that keeps this reader's settings: only those
  // that differ from the defaults.
  function settingsQuery() {
    var q = new URLSearchParams();
    Object.keys(PARAMS).forEach(function (name) {
      if (settings[name] !== DEFAULTS[name]) q.set(PARAMS[name], settings[name]);
    });
    var s = q.toString();
    return s ? "?" + s : "";
  }

  // Once the reader changes a setting the link's settings no longer apply;
  // take them out of the address (a search's ?q= stays).
  function dropSettingsParams() {
    var q = new URLSearchParams(location.search), changed = false;
    Object.keys(PARAMS).forEach(function (name) {
      if (q.has(PARAMS[name])) { q.delete(PARAMS[name]); changed = true; }
    });
    if (!changed) return;
    var s = q.toString();
    try { history.replaceState(null, "", location.pathname + (s ? "?" + s : "") + location.hash); } catch (e) { /* ignore */ }
  }

  var current = null;   // selected record
  var currentVerse = null;   // the verse within it that was chosen
  var panelEl = document.getElementById("panel");
  var SPAN = /\{\{([a-z_]+):([^{}]*)\}\}/g;
  var VERSE = /\\v (\d+) ?/;

  // A verse as this page names it: "12", or "7:53" for a verse of another
  // chapter that a sentence runs into (John 7:53-8:1 is on both pages).
  function verseOf(id) {
    var p = id.split(".");
    return Number(p[1]) === DATA.chapter ? p[2] : p[1] + ":" + p[2];
  }

  function crossesChapter(r) {
    return r.refs[0].split(".")[1] !== r.refs[r.refs.length - 1].split(".")[1];
  }

  // A record's verses as "12", "12\u201313" or "7:53\u20138:1".
  function verseRange(r) {
    var ends = [r.refs[0], r.refs[r.refs.length - 1]].map(function (id) {
      return crossesChapter(r) ? id.split(".").slice(1).join(":") : verseOf(id);
    });
    return ends[0] === ends[1] ? ends[0] : ends[0] + "\u2013" + ends[1];
  }

  // The verse a marker starts. A marker gives only the verse number, so
  // name it from the record's refs.
  function markerVerse(r, n) {
    var id = r.refs.find(function (v) { return v.split(".")[2] === n; });
    return id ? verseOf(id) : n;
  }

  // Split rendered text at verse markers: [[verse, text], ...].
  function splitVerses(r, text) {
    var parts = text.split(VERSE), out = [[verseOf(r.refs[0]), parts[0].trim()]];
    for (var i = 1; i < parts.length; i += 2) out.push([markerVerse(r, parts[i]), parts[i + 1]]);
    return out;
  }

  // A rendering split at its verse markers, each verse a list of pieces
  // [text, token ids or null]: the pieces with ids are the English that
  // aligned Greek words became (r.links, built from the record's alignments).
  function versePieces(r, lang, level) {
    var raw = r.renderings[lang][level];
    var ranges = (r.links && r.links[lang] && r.links[lang][level]) || [];
    var chunks = [], at = 0;
    ranges.forEach(function (g) {
      if (g[0] > at) chunks.push([raw.slice(at, g[0]), null]);
      chunks.push([raw.slice(g[0], g[1]), g[2]]);
      at = g[1];
    });
    if (at < raw.length) chunks.push([raw.slice(at), null]);
    var out = [[verseOf(r.refs[0]), []]];
    chunks.forEach(function (c) {
      c[0].split(VERSE).forEach(function (part, i) {
        if (i % 2) out.push([markerVerse(r, part), []]);
        else if (part) out[out.length - 1][1].push([part, c[1]]);
      });
    });
    var first = out[0][1][0];
    if (first && !first[1]) first[0] = first[0].replace(/^\s+/, "");
    return out;
  }

  function hasLinks(r) {
    var lang = textLang(r);
    return !!(r.links && r.links[lang] && r.links[lang][settings.level]);
  }

  // Light up a Greek word and the English it became, both ways.
  function light(ids) {
    var set = new Set(ids);
    document.querySelectorAll(".aw").forEach(function (a) {
      a.classList.toggle("lit", a.dataset.tokens.split(" ").some(function (id) { return set.has(id); }));
    });
    document.querySelectorAll(".iw").forEach(function (w) { w.classList.toggle("lit", set.has(w.dataset.id)); });
  }

  function render(text) {
    return text.replace(SPAN, function (_, name, opts) {
      var options = opts.split("|");
      var i = settings[name];
      return typeof i === "number" && i >= 0 && i < options.length ? options[i] : options[0];
    });
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function save() {
    try { localStorage.setItem(STORE, JSON.stringify(settings)); } catch (e) { /* ignore */ }
  }

  function decisionsFor(record) {
    var meaning = [], rendering = [];
    record.decisions.forEach(function (d) {
      if (d.layer === "meaning") meaning.push(d);
      else if (d.language === settings.lang && d.levels.includes(settings.level)) rendering.push(d);
    });
    return { meaning: meaning, rendering: rendering };
  }

  function drawControls() {
    document.querySelectorAll("[data-setting]").forEach(function (seg) {
      var name = seg.getAttribute("data-setting");
      seg.querySelectorAll("button").forEach(function (b) {
        var v = b.getAttribute("data-value");
        var on = String(settings[name]) === v;
        b.setAttribute("aria-pressed", on ? "true" : "false");
        // On wide screens the explanations are tooltips, so the bar stays one row.
        var hint = t("hint_" + name) && t("hint_" + name)[v];
        if (hint) b.title = hint;
      });
    });
    document.getElementById("hint-level").textContent = t("hint_level")[settings.level];
    // A page shows either the divine name (Old Testament) or the title
    // Christ (New Testament), so one of the two hints is missing.
    ["gender", "christos", "divine_name", "deity_pronoun", "plural_you", "view"].forEach(function (name) {
      var hint = document.getElementById("hint-" + name);
      if (hint) hint.textContent = t("hint_" + name)[settings[name]];
    });
    // The summary on the phone settings button: each shown choice's label.
    var summary = [];
    document.querySelectorAll(".control:not([hidden]) .seg").forEach(function (seg) {
      var on = seg.querySelector('[aria-pressed="true"]');
      if (on && seg.children.length > 1) summary.push(on.textContent);
    });
    document.getElementById("settings-summary").textContent = summary.join(" \u00b7 ");
    // On paper: the reference, the settings it was printed with, and where.
    var head = document.getElementById("print-head");
    if (head) head.textContent = DATA.title + " \u00b7 Open Word Bible \u00b7 " + summary.join(" \u00b7 ") +
      " \u00b7 " + location.host + location.pathname;
    document.body.classList.toggle("plain", plain());
    document.body.classList.toggle("view-parallel", parallel());
    document.body.classList.toggle("view-interlinear", interlinear());
    // Offer Parallel only with another language, Interlinear only with links.
    var views = document.querySelector('[data-setting="view"]');
    if (views) {
      views.querySelector('[data-value="2"]').hidden = !partners().length;
      views.querySelector('[data-value="3"]').hidden = !anyLinks();
    }
  }

  // Reading view: the text alone, without verse numbers, footnote letters or
  // the reasoning panel; verses are not buttons.
  // Every view but Study is for reading: no reasoning panel, verses are not
  // buttons. Parallel sets another language beside each sentence;
  // Interlinear sets the original words over the English they became.
  function plain() { return settings.view !== 0; }
  function parallel() { return settings.view === 2 && partners().length > 0; }
  function interlinear() { return settings.view === 3; }

  // Languages to set beside the page's: those any sentence here has.
  function partners() {
    return DATA.languages.filter(function (l) { return l !== settings.lang; });
  }
  function partner() {
    var all = partners();
    return all.indexOf(settings.partner) >= 0 ? settings.partner : all[0];
  }

  // Interlinear needs alignments for this language and level.
  function anyLinks(level) {
    return DATA.records.some(function (r) {
      return r.links && r.links[settings.lang] && (level ? r.links[settings.lang][level] : true);
    });
  }

  var WORD_TEXT = {};
  Object.keys(DATA.words).forEach(function (vid) {
    DATA.words[vid].forEach(function (w) { WORD_TEXT[w.id] = w.text; });
  });

  // The language a record is shown in: the reading language if the record
  // has it yet, otherwise the first language it does have (English runs
  // ahead of the others).
  function textLang(r) {
    if (r.renderings[settings.lang]) return settings.lang;
    return DATA.languages.filter(function (l) { return r.renderings[l]; })[0];
  }

  // Footnote letters: a..z, then aa, ab, ...
  function letter(n) {
    var out = "";
    for (n += 1; n > 0; n = Math.floor((n - 1) / 26)) out = String.fromCharCode(97 + (n - 1) % 26) + out;
    return out;
  }

  // A footnote as a printed Bible would give it: the choice, then the
  // alternatives, labelled for what they are. An uncertain decision's
  // alternative is a real possibility ("Or:"); a variant is another
  // manuscript reading; otherwise the alternatives were considered and set
  // aside, and are never presented as equally possible. The full reasoning is
  // one tap away.
  function noteText(d) {
    var alts = d.alternatives.map(render);
    var text = render(d.choice);
    if (alts.length) {
      var label = d.category === "text_variant" ? "fn_other" : d.uncertain ? "fn_or" : "also";
      text += ". " + t(label) + alts.join("; ");
    }
    if (d.uncertain) text += " (" + t("uncertain") + ")";
    return text + ".";
  }

  // A footnote opens in place, under its letter, so reading never jumps to
  // the foot of the page. "See the reasoning" opens the decision in the panel.
  var popover = null;

  function closeNote(refocus) {
    if (!popover) return;
    var opener = popover.opener;
    popover.remove();
    popover = null;
    if (opener) {
      opener.setAttribute("aria-expanded", "false");
      if (refocus && document.contains(opener)) opener.focus();
    }
  }

  function openNote(button, n) {
    var same = popover && popover.opener === button;
    closeNote(false);
    if (same) return;
    var box = el("div", "fn-pop");
    box.id = "fn-pop";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-label", t("fn_open").replace("{m}", n.mark));
    var head = el("p", "fn-pop-head");
    head.appendChild(el("span", "note-mark", n.mark));
    head.appendChild(el("span", "note-ref", verseRange(n.record)));
    var cat = t("category")[n.decision.category];
    if (cat) head.appendChild(el("span", "fn-pop-cat", cat));
    box.appendChild(head);
    box.appendChild(linked("p", "fn-pop-text", noteText(n.decision)));
    var more = el("button", "fn-pop-more", t("fn_reasoning") + " \u2192");
    more.type = "button";
    more.addEventListener("click", function () {
      closeNote(false);
      select(n.record, null, n.decision.id);
    });
    box.appendChild(more);
    box.addEventListener("click", function (e) { e.stopPropagation(); });
    document.body.appendChild(box);
    popover = box;
    box.opener = button;
    button.setAttribute("aria-expanded", "true");
    button.setAttribute("aria-controls", "fn-pop");
    placeNote();
    more.focus({ preventScroll: true });
  }

  // Under the letter, kept inside the window.
  function placeNote() {
    if (!popover) return;
    var r = popover.opener.getBoundingClientRect();
    var w = popover.offsetWidth, gap = 16;
    var left = Math.min(Math.max(gap, r.left + r.width / 2 - w / 2), document.documentElement.clientWidth - w - gap);
    var top = r.bottom + 8;
    if (top + popover.offsetHeight > window.innerHeight - gap && r.top - popover.offsetHeight - 8 > gap)
      top = r.top - popover.offsetHeight - 8;
    popover.style.left = left + window.scrollX + "px";
    popover.style.top = top + window.scrollY + "px";
  }

  document.addEventListener("click", function () { closeNote(false); });
  window.addEventListener("resize", placeNote);

  function drawText() {
    closeNote(false);
    var box = document.getElementById("text");
    box.textContent = "";
    var partial = DATA.records.some(function (r) { return !r.renderings[settings.lang]; });
    var note = document.getElementById("partial");
    note.hidden = !partial;
    note.textContent = partial ? t("partial") : "";
    document.getElementById("title").textContent = DATA.title;
    if (parallel()) { drawParallel(box); drawUnsureToggle(0); drawViewTools(); drawNotes([]); return; }
    drawViewTools();
    var shown = null;   // last verse number printed
    var notes = [];
    var unsureCount = 0;
    var starts = new Set(DATA.paragraphs);
    var para = null;    // the paragraph being filled
    // A passage whose place in the text is disputed (John 7:53-8:11) is set
    // apart in a block of its own, under a note that says why.
    var disputed = DATA.disputed ? new Set(DATA.disputed.records) : new Set();
    var page = box, inDisputed = false;
    DATA.records.forEach(function (r) {
      if (disputed.has(r.id) !== inDisputed) {
        inDisputed = !inDisputed;
        para = null;
        if (inDisputed) {
          box = el("div", "disputed-block");
          page.appendChild(box);
          box.appendChild(disputedNote());
        } else {
          box = page;
        }
      }
      // A section heading, then a new paragraph where the Greek starts one.
      // The heading is shown in the language its sentence is shown in, and
      // left out until it has that language.
      var heading = DATA.headings[r.id];
      var hlang = heading && [settings.lang, textLang(r)].filter(function (l) { return heading[l]; })[0];
      if (hlang) {
        var h = el("h2", "section-head" + (hlang === settings.lang ? "" : " fallback"), render(heading[hlang]));
        if (hlang !== settings.lang) h.lang = hlang;
        box.appendChild(h);
      }
      if (!para || heading || starts.has(r.id)) {
        para = el("p", "para");
        box.appendChild(para);
      }
      var ds = decisionsFor(r);
      var marks = ds.meaning.concat(ds.rendering).filter(function (d) { return d.footnote; })
        .map(function (d) {
          var mark = letter(notes.length);
          notes.push({ mark: mark, record: r, decision: d });
          return mark;
        });
      var lang = textLang(r);
      var parts = versePieces(r, lang, settings.level);
      // Where a decision is marked uncertain, the meaning is open to question.
      var unsure = ds.meaning.concat(ds.rendering).some(function (d) { return d.uncertain; });
      if (unsure) unsureCount++;
      var chosen = current && current.id === r.id;
      parts.forEach(function (part, i) {
        var span = el("span", (lang === settings.lang ? "verse" : "verse fallback") +
                           (settings.uncertain && unsure ? " unsure" : ""));
        if (lang !== settings.lang) span.lang = lang;
        if (!plain()) {
          span.tabIndex = 0;
          span.setAttribute("role", "button");
          span.setAttribute("aria-label", t("verse_label").replace("{v}", part[0]));
        }
        span.dataset.v = part[0];
        if (current && current.id === r.id) span.setAttribute("aria-current", "true");
        if (part[0] !== shown) span.appendChild(el("sup", null, part[0]));
        shown = part[0];
        part[1].forEach(function (piece) {
          var text = render(piece[0]);
          if (!piece[1]) { span.appendChild(document.createTextNode(text)); return; }
          if (interlinear()) {
            // The original words over the English they became.
            var ruby = el("ruby", "il");
            ruby.appendChild(document.createTextNode(text));
            var rt = el("rt", null, piece[1].map(function (id) { return WORD_TEXT[id] || ""; }).join(" ").trim());
            rt.lang = DATA.source;
            ruby.appendChild(rt);
            span.appendChild(ruby);
            return;
          }
          var w = el("span", "aw", text);
          w.dataset.tokens = piece[1].join(" ");
          // In the chosen sentence, pointing at an English word lights the
          // Greek it came from in the panel.
          if (chosen) {
            w.addEventListener("mouseenter", function () { light(piece[1]); });
            w.addEventListener("mouseleave", function () { light([]); });
            w.addEventListener("click", function (e) { e.stopPropagation(); light(piece[1]); });
          }
          span.appendChild(w);
        });
        if (marks.length && i === parts.length - 1) {
          var sup = el("sup", "fn");
          marks.forEach(function (mark) {
            var n = notes.filter(function (x) { return x.mark === mark; })[0];
            var b = el("button", "fn-mark", mark);
            b.type = "button";
            b.setAttribute("aria-label", t("fn_open").replace("{m}", mark));
            b.setAttribute("aria-expanded", "false");
            b.addEventListener("click", function (e) { e.stopPropagation(); openNote(b, n); });
            b.addEventListener("keydown", function (e) { e.stopPropagation(); });
            sup.appendChild(b);
          });
          span.appendChild(sup);
        }
        span.addEventListener("click", function () {
          // Selecting text is not choosing the verse.
          if (!window.getSelection().isCollapsed) return;
          select(r, part[0]);
        });
        span.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(r, part[0]); }
        });
        para.appendChild(span);
        para.appendChild(document.createTextNode(" "));
      });
    });
    box = page;
    drawUnsureToggle(unsureCount);
    drawNotes(notes);
  }

  function disputedNote() {
    var d = DATA.disputed;
    var note = el("div", "disputed-note");
    note.appendChild(el("p", null, t("disputed_note").replace("{ref}", d.ref)));
    var rec = DATA.records.filter(function (r) { return r.id === d.records[0]; })[0];
    if (d.note && rec && !plain()) {
      var why = el("button", "fn-pop-more", t("fn_reasoning") + " \u2192");
      why.type = "button";
      why.addEventListener("click", function () { select(rec, null, d.note); });
      note.appendChild(why);
    }
    return note;
  }

  // Parallel: each sentence in a row, the page's language beside another.
  function drawParallel(box) {
    var other = partner();
    var starts = new Set(DATA.paragraphs);
    box.appendChild(parallelRow(DATA.languages.indexOf(settings.lang) >= 0 ? settings.lang : "en", other, true));
    DATA.records.forEach(function (r) {
      var heading = DATA.headings[r.id];
      if (heading && (heading[settings.lang] || heading.en)) {
        box.appendChild(el("h2", "section-head", render(heading[settings.lang] || heading.en)));
      }
      var row = el("div", "prow" + (starts.has(r.id) ? " pstart" : ""));
      [textLang(r), other].forEach(function (lang, i) {
        var cell = el("div", "pcell");
        var has = r.renderings[lang];
        if (!has) {
          cell.appendChild(el("span", "pmissing", t("not_in_language")));
        } else {
          cell.lang = lang;
          splitVerses(r, render(has[settings.level])).forEach(function (part, j) {
            cell.appendChild(el("sup", "pv", part[0]));
            cell.appendChild(document.createTextNode(part[1] + " "));
          });
          if (i === 0 && lang !== settings.lang) cell.classList.add("fallback");
        }
        row.appendChild(cell);
      });
      box.appendChild(row);
    });
  }

  function parallelRow(a, b) {
    var row = el("div", "prow phead");
    [a, b].forEach(function (l) { row.appendChild(el("div", "pcell", t("lang_names")[l] || l)); });
    return row;
  }

  // Above the text, in Parallel and Interlinear: the language to set beside
  // the page's, or a word on where interlinear links exist so far.
  function drawViewTools() {
    var tools = document.getElementById("view-tools");
    if (!tools) {
      tools = el("div", "view-tools");
      tools.id = "view-tools";
      var box = document.getElementById("text");
      box.parentNode.insertBefore(tools, box);
    }
    tools.textContent = "";
    tools.hidden = !(parallel() || interlinear());
    if (parallel()) {
      tools.appendChild(el("span", "vt-label", t("parallel_with")));
      partners().forEach(function (l) {
        var b = el("button", "text-tool", t("lang_names")[l] || l);
        b.type = "button";
        b.setAttribute("aria-pressed", l === partner() ? "true" : "false");
        b.addEventListener("click", function () { setSetting("partner", l); });
        tools.appendChild(b);
      });
    } else if (interlinear() && !anyLinks(settings.level)) {
      tools.appendChild(el("span", "vt-label", t("interlinear_none")));
    }
  }

  // Above the text: mark the sentences where a decision is uncertain.
  function drawUnsureToggle(n) {
    var b = document.getElementById("unsure-toggle");
    if (!b) {
      b = el("button", "text-tool");
      b.id = "unsure-toggle";
      b.type = "button";
      b.addEventListener("click", function () { setSetting("uncertain", settings.uncertain ? 0 : 1); });
      var box = document.getElementById("text");
      box.parentNode.insertBefore(b, box);
    }
    b.hidden = !n;
    b.setAttribute("aria-pressed", settings.uncertain ? "true" : "false");
    b.textContent = t("unsure_toggle").replace("{n}", n);
  }

  // Below the passage: its footnotes, or every note in the chapter grouped
  // by topic (meaning notes, and the wording notes for this language and
  // level), with the uncertain ones as a topic of their own.
  var notesTab = "foot", topic = null;

  // Printing shows the footnotes at the end, whatever the notes tab shows.
  var screenTab = null;
  window.addEventListener("beforeprint", function () {
    screenTab = notesTab;
    notesTab = "foot";
    drawText();
  });
  window.addEventListener("afterprint", function () {
    if (screenTab) { notesTab = screenTab; screenTab = null; drawText(); }
  });

  function drawNotes(notes) {
    var section = document.getElementById("notes");
    if (!section) return;
    section.textContent = "";
    var all = [];
    DATA.records.forEach(function (r) {
      var ds = decisionsFor(r);
      ds.meaning.concat(ds.rendering).forEach(function (d) { all.push({ record: r, decision: d }); });
    });
    section.hidden = !all.length;
    if (!all.length) return;
    if (!notes.length) notesTab = "topic";
    var head = el("div", "notes-head");
    head.appendChild(el("h2", null, t("notes")));
    var tabs = el("div", "notes-tabs");
    tabs.setAttribute("role", "group");
    [["foot", t("notes_foot") + " (" + notes.length + ")"], ["topic", t("notes_topic") + " (" + all.length + ")"]]
      .forEach(function (tab) {
        if (tab[0] === "foot" && !notes.length) return;
        var b = el("button", "notes-tab", tab[1]);
        b.type = "button";
        b.setAttribute("aria-pressed", notesTab === tab[0] ? "true" : "false");
        b.addEventListener("click", function () { notesTab = tab[0]; drawNotes(notes); });
        tabs.appendChild(b);
      });
    head.appendChild(tabs);
    section.appendChild(head);

    if (notesTab === "foot") {
      var list = el("ol");
      notes.forEach(function (n) {
        var item = el("li");
        var button = el("button", "note");
        button.type = "button";
        button.appendChild(el("span", "note-mark", n.mark));
        button.appendChild(el("span", "note-ref", verseRange(n.record)));
        button.appendChild(el("span", "note-text", noteText(n.decision)));
        button.addEventListener("click", function () { select(n.record, null, n.decision.id); });
        item.appendChild(button);
        list.appendChild(item);
      });
      section.appendChild(list);
      return;
    }

    // Topics: each category with its count, then "Uncertain".
    var counts = {}, order = [];
    all.forEach(function (n) {
      var c = n.decision.category;
      if (!(c in counts)) { counts[c] = 0; order.push(c); }
      counts[c]++;
    });
    var unsure = all.filter(function (n) { return n.decision.uncertain; }).length;
    var chips = el("div", "topic-chips");
    function chip(value, label, n) {
      var b = el("button", "topic-chip" + (value === "uncertain" ? " unc" : ""), label + " " + n);
      b.type = "button";
      b.setAttribute("aria-pressed", topic === value ? "true" : "false");
      b.addEventListener("click", function () { topic = value; drawNotes(notes); });
      chips.appendChild(b);
    }
    if (topic && topic !== "uncertain" && !(topic in counts)) topic = null;
    chip(null, t("notes_all"), all.length);
    order.sort(function (a, b) { return counts[b] - counts[a]; }).forEach(function (c) {
      chip(c, t("category")[c] || c, counts[c]);
    });
    if (unsure) chip("uncertain", t("uncertain"), unsure);
    section.appendChild(chips);

    var shown = all.filter(function (n) {
      return !topic || (topic === "uncertain" ? n.decision.uncertain : n.decision.category === topic);
    });
    var list2 = el("ul", "topic-list");
    shown.forEach(function (n) {
      var d = n.decision;
      var item = el("li");
      var button = el("button", "note");
      button.type = "button";
      button.appendChild(el("span", "note-ref", verseRange(n.record)));
      var body = el("span", "note-text");
      body.appendChild(el("span", "topic-cat", t("category")[d.category] || d.category));
      if (d.uncertain) body.appendChild(el("span", "badge unc", t("uncertain")));
      body.appendChild(el("span", "topic-choice", render(d.choice)));
      button.appendChild(body);
      button.addEventListener("click", function () { select(n.record, null, d.id); });
      item.appendChild(button);
      list2.appendChild(item);
    });
    section.appendChild(list2);
  }

  function highlight(ids, card) {
    var set = new Set(ids);
    document.querySelectorAll(".word").forEach(function (w) {
      w.classList.toggle("on", set.has(w.dataset.id));
    });
    document.querySelectorAll(".card").forEach(function (c) { c.classList.toggle("on", c === card); });
    document.querySelectorAll(".aw").forEach(function (a) {
      a.classList.toggle("on", a.dataset.tokens.split(" ").some(function (id) { return set.has(id); }));
    });
  }

  // "Mark 14:54" or "2 Corinthians 7:9-10" in a note becomes a link: into
  // the reader where that chapter is translated, otherwise to search (which
  // says it is not translated yet). Book names come from DATA.bookRefs.
  var REF = null;
  function refPattern() {
    if (REF) return REF;
    var names = Object.keys(DATA.bookRefs.names).sort(function (a, b) { return b.length - a.length; })
      .map(function (n) { return n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); });
    REF = new RegExp("\\b(" + names.join("|") + ") (\\d+):(\\d+)(?:[-\u2013](\\d+))?", "g");
    return REF;
  }

  function refUrl(code, chapter, verse, label) {
    var have = DATA.bookRefs.chapters[code] || [];
    if (have.indexOf(chapter) < 0) return DATA.bookRefs.search + "?q=" + encodeURIComponent(label);
    if (code === DATA.book && chapter === DATA.chapter) return "#v" + verse;
    return (DATA.lang === "en" ? "" : "/" + DATA.lang) + "/" + code.toLowerCase() + "/" + chapter + "/#v" + verse;
  }

  function linked(tag, cls, text) {
    var node = el(tag, cls);
    var re = refPattern(), at = 0, m;
    re.lastIndex = 0;
    while ((m = re.exec(text))) {
      node.appendChild(document.createTextNode(text.slice(at, m.index)));
      var a = el("a", "sref", m[0]);
      a.href = refUrl(DATA.bookRefs.names[m[1]], Number(m[2]), Number(m[3]), m[0]);
      a.addEventListener("click", function (e) { e.stopPropagation(); });
      node.appendChild(a);
      at = m.index + m[0].length;
    }
    node.appendChild(document.createTextNode(text.slice(at)));
    return node;
  }

  // Key terms and the people, places and peoples in the chosen sentence
  // (DATA.cards, from data/key_terms.json and data/names.json). Tapping one
  // lights its words in the Greek or Hebrew above.
  function drawWordCards(panel) {
    var byCard = {};
    current.source.tokens.forEach(function (id) {
      var i = DATA.cards.tokens[id];
      if (i !== undefined) (byCard[i] = byCard[i] || []).push(id);
    });
    var found = Object.keys(byCard).map(Number);
    if (!found.length) return;
    panel.appendChild(el("h3", null, t("cards_title")));
    var list = el("div", "wcards");
    found.sort(function (a, b) { return DATA.cards.list[a].type === "term" ? -1 : DATA.cards.list[b].type === "term" ? 1 : a - b; })
      .forEach(function (i) {
        var c = DATA.cards.list[i];
        var card = el("button", "wcard " + c.type);
        card.type = "button";
        var head = el("span", "wcard-head");
        head.appendChild(el("span", "wcard-title", c.title));
        var lemma = el("span", "wcard-lemma", c.lemma);
        lemma.lang = DATA.source;
        head.appendChild(lemma);
        head.appendChild(el("span", "wcard-kind", t("card_kind")[c.type === "term" ? "term" : c.kind] || ""));
        card.appendChild(head);
        // A key term's note is for translators; readers get the rule it keeps.
        if (c.type === "term") card.appendChild(el("span", "wcard-note", t("card_term").replace("{words}", c.english.join(", "))));
        else card.appendChild(el("span", "wcard-note", c.note));
        card.addEventListener("click", function () { highlight(byCard[i], null); light(byCard[i]); });
        list.appendChild(card);
      });
    panel.appendChild(list);
  }

  function drawCard(d, record) {
    var card = el("div", "card");
    card.tabIndex = 0;
    card.dataset.decision = d.id;
    var cat = el("div", "cat", t("category")[d.category] || d.category);
    if (d.uncertain) cat.appendChild(el("span", "badge unc", t("uncertain")));
    if (d.footnote) cat.appendChild(el("span", "badge", t("footnote")));
    card.appendChild(cat);
    card.appendChild(el("div", "choice", render(d.choice)));
    if (d.alternatives.length) {
      card.appendChild(el("div", "alts", t("also") + d.alternatives.map(render).join("; ")));
    }
    card.appendChild(linked("p", "why", d.reason));
    function on() { highlight(d.tokens, card); }
    card.addEventListener("click", on);
    card.addEventListener("focus", on);
    return card;
  }

  // Elsewhere in the translation: every other verse with this dictionary
  // form, from the site-wide index (fetched once, on the first tap).
  var usesIndex = null;
  function loadUses() {
    if (!usesIndex) {
      usesIndex = fetch(DATA.uses).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      });
      usesIndex.catch(function () { usesIndex = null; });
    }
    return usesIndex;
  }

  function verseUrl(vid) {
    var p = vid.split(".");
    if (p[0] === DATA.book && Number(p[1]) === DATA.chapter) return "#v" + p[2];
    return (DATA.lang === "en" ? "" : "/" + DATA.lang) + "/" + p[0].toLowerCase() + "/" + p[1] + "/#v" + p[2];
  }

  function drawUses(word) {
    var box = el("div", "uses");
    box.appendChild(el("p", "uses-title", t("uses_loading")));
    var here = Object.keys(DATA.words).filter(function (vid) {
      return DATA.words[vid].some(function (w) { return w.id === word.id; });
    })[0];
    loadUses().then(function (index) {
      var places = (index[word.lemma] || []).filter(function (vid) { return vid !== here; });
      box.textContent = "";
      var n = places.length;
      box.appendChild(el("p", "uses-title",
        n ? t(n === 1 ? "uses_one" : "uses_many").replace("{n}", n) : t("uses_none")));
      if (!n) return;
      var list = el("p", "uses-list");
      var SHOW = 12;
      function add(from, to) {
        places.slice(from, to).forEach(function (vid) {
          var p = vid.split(".");
          var a = el("a", "use", (DATA.books[p[0]] || p[0]) + " " + p[1] + ":" + p[2]);
          a.href = verseUrl(vid);
          list.insertBefore(a, more);
        });
      }
      var more = null;
      if (n > SHOW) {
        more = el("button", "use use-more", t("uses_all").replace("{n}", n));
        more.type = "button";
        more.addEventListener("click", function () { add(SHOW, n); more.remove(); });
        list.appendChild(more);
      }
      add(0, SHOW);
      box.appendChild(list);
    }, function () {
      box.textContent = "";
      box.appendChild(el("p", "uses-title", t("uses_failed")));
    });
    return box;
  }

  function drawPanel() {
    var panel = panelEl;
    panel.textContent = "";
    if (!current) {
      panel.appendChild(el("h2", null, t("empty_title")));
      panel.appendChild(el("p", "empty", t("empty_text")));
      panel.appendChild(el("p", "keys", t("keys_hint")));
      return;
    }
    var close = el("button", "sheet-close", "\u00d7");
    close.type = "button";
    close.setAttribute("aria-label", t("close"));
    close.addEventListener("click", deselect);
    panel.appendChild(close);
    var handle = el("button", "sheet-handle");
    handle.type = "button";
    handle.setAttribute("aria-expanded", panelEl.classList.contains("full") ? "true" : "false");
    handle.setAttribute("aria-label", t("sheet_expand"));
    handle.addEventListener("click", function () { expand(!panelEl.classList.contains("full")); });
    panel.appendChild(handle);
    var ref = DATA.title.replace(/[\d:\u2013\s]+$/, "") + " " + (crossesChapter(current) ? "" : DATA.chapter + ":") +
      verseRange(current);
    var title = el("h2", "panel-title");
    title.appendChild(el("span", null, ref));
    title.appendChild(linkButton(currentVerse));
    panel.appendChild(title);

    panel.appendChild(el("h3", null, t("greek")));
    // Interlinear: each Greek word (or Hebrew morpheme) over its gloss. Tapping one shows its
    // dictionary form, Strong's number and grammar, and lights up every
    // decision that names it.
    var greek = el("div", "interlinear");
    if (HEBREW) greek.dir = "rtl";
    var info = el("div", "wordinfo");
    info.setAttribute("aria-live", "polite");
    info.hidden = true;
    function drawWord(word) {
      var w = el("button", "word iw");
      w.type = "button";
      w.dataset.id = word.id;
      var g = el("span", "iw-g", word.text + word.after.trim());
      g.lang = DATA.source;
      w.appendChild(g);
      // MACULA Hebrew glosses join words with dots: "he.created".
      w.appendChild(el("span", "iw-e", HEBREW ? word.gloss.replace(/\./g, " ") : word.gloss));
      w.addEventListener("mouseenter", function () { light([word.id]); });
      w.addEventListener("mouseleave", function () { light([]); });
      w.addEventListener("focus", function () { light([word.id]); });
      w.addEventListener("blur", function () { light([]); });
      w.addEventListener("click", function () {
        info.textContent = "";
        var head = el("p", "wi-head");
        var lemma = el("span", "wi-lemma", word.lemma);
        lemma.lang = DATA.source;
        head.appendChild(lemma);
        var strong = word.strong ? (HEBREW ? " H" + word.strong.replace(/^0+/, "") : " G" + word.strong) : "";
        head.appendChild(el("span", "wi-label", t("lemma") + (strong ? " \u00b7 " + t("strong") + strong : "")));
        if (word.transliteration) head.appendChild(el("span", "wi-label", word.transliteration));
        info.appendChild(head);
        var key = (word.lang === "A" ? "A:" : "") + word.morph;
        info.appendChild(el("p", "wi-grammar", DATA.grammar[key][settings.lang]));
        info.appendChild(el("p", "wi-gloss", "\u201c" + (HEBREW ? word.gloss.replace(/\./g, " ") : word.gloss) + "\u201d"));
        info.appendChild(drawUses(word));
        info.hidden = false;
        var ids = [];
        current.decisions.forEach(function (d) { if (d.tokens.includes(word.id)) ids = ids.concat(d.tokens); });
        highlight(ids.length ? ids : [word.id], null);
      });
      greek.appendChild(w);
    }
    var mine = new Set(current.source.tokens);
    current.refs.forEach(function (vid, i) {
      if (i > 0) greek.appendChild(el("sup", "iw-verse", verseOf(vid)));
      (DATA.words[vid] || []).filter(function (w) { return mine.has(w.id); }).forEach(drawWord);
    });
    panel.appendChild(el("p", "hint", t("word_hint") + (hasLinks(current) ? " " + t("align_hint") : "")));
    panel.appendChild(greek);
    panel.appendChild(info);

    panel.appendChild(el("h3", null, t("gloss")));
    var gloss = el("p", "gloss");
    splitVerses(current, current.literal_gloss).forEach(function (part, i) {
      if (i > 0) gloss.appendChild(el("sup", null, " " + part[0]));
      gloss.appendChild(document.createTextNode((i > 0 ? " " : "") + part[1]));
    });
    panel.appendChild(gloss);

    // The same sentence at each level, side by side; choosing one reads the
    // chapter at it.
    panel.appendChild(el("h3", null, t("levels")));
    var lang = textLang(current);
    var levels = el("div", "levels");
    if (lang !== settings.lang) levels.lang = lang;
    ["L", "B", "R"].forEach(function (code) {
      var on = code === settings.level;
      var b = el("button", "lvl-row" + (on ? " on" : ""));
      b.type = "button";
      b.setAttribute("aria-pressed", on ? "true" : "false");
      var name = el("span", "lvl-name", t(code));
      if (on) name.appendChild(el("span", "badge", t("reading")));
      b.appendChild(name);
      var text = el("span", "lvl-text");
      splitVerses(current, render(current.renderings[lang][code])).forEach(function (part, i) {
        if (i > 0) text.appendChild(el("sup", null, " " + part[0] + " "));
        text.appendChild(document.createTextNode(part[1]));
      });
      b.appendChild(text);
      b.addEventListener("click", function () { if (!on) setSetting("level", code); });
      levels.appendChild(b);
    });
    panel.appendChild(el("p", "hint", t("levels_hint")));
    panel.appendChild(levels);
    drawWordCards(panel);

    var ds = decisionsFor(current);
    panel.appendChild(el("h3", null, t("meaning")));
    if (t("notes_language")) panel.appendChild(el("p", "empty", t("notes_language")));
    if (!ds.meaning.length) panel.appendChild(el("p", "empty", t("no_meaning")));
    ds.meaning.forEach(function (d) { panel.appendChild(drawCard(d, current)); });
    panel.appendChild(el("h3", null, t("rendering").replace("{level}", t(settings.level))));
    if (!ds.rendering.length) panel.appendChild(el("p", "empty", t("no_rendering")));
    ds.rendering.forEach(function (d) { panel.appendChild(drawCard(d, current)); });
  }

  // A link to this chapter opened at a verse (#v4). Phones offer the
  // system share sheet; elsewhere the link is copied.
  function linkButton(verse) {
    var b = el("button", "copy-link");
    b.type = "button";
    var share = narrow() && !!navigator.share;
    var label = el("span", null, t(share ? "share" : "copy_link"));
    b.appendChild(label);
    b.addEventListener("click", function () {
      var link = location.origin + location.pathname + settingsQuery() + "#v" + verse;
      var name = DATA.title.replace(/[\d:\u2013\s]+$/, "") + " " + DATA.chapter + ":" + verse;
      function done(ok) {
        label.textContent = t(ok ? "copied" : "copy_failed");
        b.classList.toggle("done", ok);
        setTimeout(function () { label.textContent = t("copy_link"); b.classList.remove("done"); }, 2000);
      }
      if (share) {
        navigator.share({ title: name + " \u00b7 Open Word Bible", url: link }).catch(function () { /* dismissed */ });
      } else if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(link).then(function () { done(true); }, function () { done(false); });
      } else {
        done(false);
      }
    });
    return b;
  }

  // On narrow screens the panel is a bottom sheet over the text (see .panel
  // in style.css), so opening it never moves the reader's place. The CSS
  // owns the breakpoint: the sheet is the panel when it is position: fixed.
  function narrow() { return getComputedStyle(panelEl).position === "fixed"; }
  function verseEl(v) { return document.querySelector('.verse[data-v="' + v + '"]'); }
  // A verse in the address: #v4, or plainly #4 (#v7:53 for a verse
  // of another chapter that a sentence runs into).
  function hashVerse() { var m = /^#v?(\d+(?::\d+)?)$/.exec(location.hash); return m && m[1]; }
  function recordFor(verse) {
    return DATA.records.find(function (r) {
      return r.refs.some(function (vid) { return verseOf(vid) === verse; });
    });
  }

  function sheet(open) {
    panelEl.classList.toggle("open", open);
    document.body.classList.toggle("sheet-open", open);
    if (!open) expand(false);
  }

  function expand(full) {
    panelEl.classList.toggle("full", full);
    var handle = panelEl.querySelector(".sheet-handle");
    if (handle) handle.setAttribute("aria-expanded", full ? "true" : "false");
  }

  function select(record, verse, decision) {
    if (plain()) return;
    current = record;
    verse = verse || verseOf(record.refs[0]);
    currentVerse = verse;
    try { history.replaceState(null, "", "#v" + verse); } catch (e) { /* ignore */ }
    drawText();
    drawPanel();
    panelEl.scrollTop = 0;
    sheet(true);
    var card = decision && panelEl.querySelector('.card[data-decision="' + decision + '"]');
    if (card) {
      card.focus({ preventScroll: true });
      card.scrollIntoView({ block: "nearest" });
      if (!narrow()) return;
    }
    if (narrow()) {
      var v = verseEl(verse);
      if (v) v.scrollIntoView({ behavior: "smooth", block: "start" });
      // The sheet covers the text below the verse, so take focus into it.
      if (!card) panelEl.focus({ preventScroll: true });
    }
  }

  function deselect() {
    if (!current) return;
    var verse = currentVerse;
    current = currentVerse = null;
    try {
      history.replaceState(null, "", location.pathname + location.search);
      history.scrollRestoration = "auto";
    } catch (e) { /* ignore */ }
    sheet(false);
    drawText();
    drawPanel();
    var v = verse && verseEl(verse);
    if (v) v.focus({ preventScroll: true });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && popover) { closeNote(true); return; }
    // Left and right arrows turn to the previous and next passage, unless
    // the reader is typing or a control wants the arrows.
    if ((e.key === "ArrowLeft" || e.key === "ArrowRight") && !e.altKey && !e.ctrlKey && !e.metaKey && !e.shiftKey) {
      if (!typing(e.target)) {
        var turn = document.querySelector('[data-turn="' + (e.key === "ArrowLeft" ? "prev" : "next") + '"]');
        if (turn) { e.preventDefault(); location.href = turn.href; return; }
      }
    }
    // An Escape that closes a header menu (site.js: the colour menu, a
    // dropdown or the narrow-screen menu) leaves the panel open.
    var menuOpen = !!document.querySelector('header.site [aria-expanded="true"]');
    if (e.key === "Escape" && !menuOpen) { deselect(); return; }
    // j and k step to the next and previous verse.
    if ((e.key === "j" || e.key === "k") && !e.altKey && !e.ctrlKey && !e.metaKey && !typing(e.target)) {
      e.preventDefault();
      step(e.key === "j" ? 1 : -1);
    }
  });

  function typing(target) {
    var tag = (target.tagName || "").toLowerCase();
    return tag === "input" || tag === "textarea" || tag === "select" || target.isContentEditable;
  }

  // Every verse on the page in order, with the record it is in. A verse
  // shared by two sentences appears once for each, so j visits both.
  function verses() {
    var out = [];
    DATA.records.forEach(function (r) {
      splitVerses(r, r.renderings[textLang(r)][settings.level]).forEach(function (part) {
        out.push({ record: r, verse: part[0] });
      });
    });
    return out;
  }

  function step(by) {
    var all = verses();
    var i = -1;
    all.forEach(function (v, n) { if (current && v.record === current && v.verse === currentVerse) i = n; });
    var next = all[i < 0 ? (by > 0 ? 0 : all.length - 1) : Math.min(all.length - 1, Math.max(0, i + by))];
    if (!next || (next.record === current && next.verse === currentVerse)) return;
    select(next.record, next.verse);
    var v = verseEl(next.verse);
    if (v && !narrow()) {
      v.focus({ preventScroll: true });
      v.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }

  // A link on the page that changes the verse in the address opens it.
  window.addEventListener("hashchange", function () {
    var verse = hashVerse();
    var r = verse && recordFor(verse);
    if (r && verse !== currentVerse) { select(r, verse); reveal(verse); }
  });

  // Bring a verse opened from the address into view. (On phones select
  // already puts it at the top, above the sheet.)
  function reveal(verse, instant) {
    var v = !narrow() && verseEl(verse);
    if (v) v.scrollIntoView({ block: "center", behavior: instant ? "auto" : "smooth" });
  }

  // Swipe the sheet down to close it, when it is scrolled to its top. The
  // slide transition is off while dragging so the sheet follows the finger.
  var startY = null;
  panelEl.addEventListener("touchstart", function (e) {
    startY = narrow() && panelEl.scrollTop <= 0 ? e.touches[0].clientY : null;
    if (startY !== null) panelEl.style.transition = "none";
  }, { passive: true });
  panelEl.addEventListener("touchmove", function (e) {
    if (startY === null) return;
    var dy = e.touches[0].clientY - startY;
    panelEl.style.transform = dy > 0 ? "translateY(" + dy + "px)" : "";
  }, { passive: true });
  function endDrag(e) {
    if (startY === null) return;
    var dy = e.type === "touchend" ? e.changedTouches[0].clientY - startY : 0;
    panelEl.style.transform = panelEl.style.transition = "";
    startY = null;
    var full = panelEl.classList.contains("full");
    if (dy < -60 && !full) expand(true);
    else if (dy > 80) { if (full) expand(false); else deselect(); }
  }
  panelEl.addEventListener("touchend", endDrag);
  panelEl.addEventListener("touchcancel", endDrag);

  function setSetting(name, value) {
    var top = panelEl.scrollTop;
    settings[name] = value;
    dropSettingsParams();
    save();
    drawControls();
    if (plain() && current) { deselect(); return; }
    drawText();
    drawPanel();
    panelEl.scrollTop = top;
  }

  // Copying from the passage adds where it comes from: "John 2:4 (Open
  // Word Bible, Balanced)". Verse numbers and footnote letters are left out,
  // paragraphs and headings keep their own lines.
  var textBox = document.getElementById("text");

  function selectedRange() {
    var sel = window.getSelection();
    if (!sel.rangeCount || sel.isCollapsed) return null;
    var range = sel.getRangeAt(0);
    return textBox.contains(range.commonAncestorContainer) ? range : null;
  }

  function quote(range) {
    var div = document.createElement("div");
    div.appendChild(range.cloneContents());
    div.querySelectorAll("sup, button").forEach(function (n) { n.remove(); });
    var blocks = div.querySelectorAll("p, h2");
    var parts = blocks.length ? Array.prototype.map.call(blocks, function (b) { return b.textContent; }) : [div.textContent];
    var text = parts.map(function (x) { return x.replace(/\s+/g, " ").trim(); }).filter(Boolean).join("\n\n");
    var verses = Array.prototype.filter.call(textBox.querySelectorAll(".verse"), function (v) {
      return range.intersectsNode(v);
    }).map(function (v) { return Number(v.dataset.v); });
    if (!text || !verses.length) return null;
    var a = Math.min.apply(null, verses), b = Math.max.apply(null, verses);
    var name = (DATA.books && DATA.books[DATA.book]) || DATA.title.replace(/[\d:\u2013\s]+$/, "");
    return text + "\n\u2014 " + name + " " + DATA.chapter + ":" + (a === b ? a : a + "\u2013" + b) +
      " (Open Word Bible, " + t(settings.level) + ")";
  }

  document.addEventListener("copy", function (e) {
    var range = selectedRange();
    var text = range && quote(range);
    if (!text || !e.clipboardData) return;
    e.clipboardData.setData("text/plain", text);
    e.preventDefault();
  });

  // A button by the selection does the same, for readers who do not use
  // the keyboard. On touch screens it sits below, clear of the system menu.
  var copyBtn = el("button", "copy-quote", t("copy_quote"));
  copyBtn.type = "button";
  copyBtn.hidden = true;
  document.body.appendChild(copyBtn);
  copyBtn.addEventListener("mousedown", function (e) { e.preventDefault(); });
  copyBtn.addEventListener("click", function () {
    var range = selectedRange();
    var text = range && quote(range);
    if (!text || !navigator.clipboard) return;
    navigator.clipboard.writeText(text).then(function () {
      copyBtn.textContent = t("copied_quote");
      setTimeout(function () { copyBtn.hidden = true; copyBtn.textContent = t("copy_quote"); }, 1200);
    }, function () { copyBtn.textContent = t("copy_failed"); });
  });
  var placing = null;
  document.addEventListener("selectionchange", function () {
    clearTimeout(placing);
    placing = setTimeout(function () {
      var range = selectedRange();
      if (!range || !navigator.clipboard) { copyBtn.hidden = true; return; }
      var r = range.getBoundingClientRect();
      copyBtn.hidden = false;
      var below = window.matchMedia("(pointer: coarse)").matches || r.top < 120;
      var top = below ? r.bottom + 10 : r.top - copyBtn.offsetHeight - 10;
      var left = Math.min(Math.max(16, r.left + r.width / 2 - copyBtn.offsetWidth / 2),
                          document.documentElement.clientWidth - copyBtn.offsetWidth - 16);
      copyBtn.style.top = top + window.scrollY + "px";
      copyBtn.style.left = left + window.scrollX + "px";
    }, 150);
  });

  // The settings bar sticks under the header; the panel sticks under both,
  // so it needs the bar's height (it changes as the bar wraps).
  var settingsEl = document.getElementById("settings");
  function measure() {
    document.documentElement.style.setProperty("--settings-h", settingsEl.offsetHeight + "px");
  }
  if (window.ResizeObserver) new ResizeObserver(measure).observe(settingsEl);
  measure();

  var toggle = document.getElementById("settings-toggle");
  toggle.addEventListener("click", function () {
    var open = toggle.getAttribute("aria-expanded") !== "true";
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });

  document.querySelectorAll("[data-setting]").forEach(function (seg) {
    var name = seg.getAttribute("data-setting");
    seg.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-value");
        setSetting(name, /^\d+$/.test(v) ? Number(v) : v);
      });
    });
  });

  // On phones the chapter pills are one row that scrolls sideways; bring
  // this chapter's pill into view.
  var pills = document.querySelector(".chapstrip .chap-pills");
  var here = pills && pills.querySelector("[aria-current]");
  if (here && pills.scrollWidth > pills.clientWidth)
    pills.scrollLeft = here.offsetLeft - pills.offsetLeft - pills.clientWidth / 2 + here.offsetWidth / 2;

  var start = hashVerse();
  var record = start && recordFor(start);
  drawControls();
  if (record) {
    // Opened at a verse: the verse decides where the page sits,
    // not the browser's scroll restoring (deselect turns it back on), and
    // the jump waits for layout to settle.
    try { history.scrollRestoration = "manual"; } catch (e) { /* ignore */ }
    select(record, start);
    window.addEventListener("load", function () {
      if (!current) return;
      if (narrow()) { var v = verseEl(start); if (v) v.scrollIntoView({ block: "start" }); }
      else reveal(start, true);
    });
  } else { drawText(); drawPanel(); }
})();
