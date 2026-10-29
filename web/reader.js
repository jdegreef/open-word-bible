// Open Word Bible chapter reader. Data comes from the JSON block the build
// embeds in the page, with what every language's page of the chapter
// shares (window.OWB_CHAPTER: the source words, each sentence's source, the
// cross-references) and what every chapter page of the language shares
// (window.OWB_LANG: the interface text, the book names), from the two
// scripts the page loads first (scripts/build_site.py chapter_shared,
// reader_shared). All text is inserted with textContent.
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("owb-data").textContent);
  [window.OWB_LANG, window.OWB_CHAPTER].forEach(function (shared) {
    for (var k in shared) if (k !== "sources") DATA[k] = shared[k];
  });
  DATA.records.forEach(function (r) { r.source = window.OWB_CHAPTER.sources[r.id]; });
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
  // switches it. The other settings are kept across pages and languages,
  // with "at", when the reader last changed one, so that a signed-in
  // reader's settings follow them to their other devices (site.js syncs
  // owb.settings with the account; the latest device's copy wins whole).
  var settings = { level: "B", gender: 0, christos: 0, divine_name: 0, deity_pronoun: 0, units: 0, plural_you: 0, view: 0,
                   headings: 0, crossrefs: 0, red_letter: 0, uncertain: 0, partner: "", script: 0 };
  var settingsAt = 0;
  function loadSettings() {
    try {
      var saved = JSON.parse(localStorage.getItem(STORE) || "{}") || {};
      for (var k in settings) if (k in saved && k !== "lang") settings[k] = saved[k];
      settingsAt = saved.at || 0;
    } catch (e) { /* storage unavailable: use defaults */ }
  }
  loadSettings();
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
  var VERSE = OWBMarkup.VERSE;   // web/markup.js, loaded before this
  // Poetry: "\q " starts a new line within a verse (owb/markup.py LINE).
  // A verse start is always a line start; text with no marker is prose.
  var LINE = / ?\\q ?/;
  var LINES = / ?\\q ?/g;
  // Text on one line (panel, speech, verse images, copy): a line break reads as a space.
  function flat(text) { return text.replace(LINES, " "); }
  // A record is set as poetry in a language when any of its levels there
  // has line markers, so every verse of it starts its own line even at a
  // level (often Readable) that joins a verse's lines into one.
  function poetic(r, lang) {
    var levels = r.renderings[lang] || {};
    return Object.keys(levels).some(function (l) { return LINE.test(levels[l]); });
  }

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
    return OWBMarkup.splitVerses(flat(text)).map(function (part, i) {
      return [i ? markerVerse(r, part[0]) : verseOf(r.refs[0]), part[1]];
    });
  }

  // A rendering split at its verse markers, each verse a list of pieces
  // [text, token ids or null, words of Jesus]: the pieces with ids are the
  // English that aligned Greek words became (r.links, built from the
  // record's alignments); the third is true where Jesus speaks (r.wj, from
  // data/words_of_jesus/). A poetic line break is the piece [null, null].
  function versePieces(r, lang, level) {
    var raw = r.renderings[lang][level];
    var ranges = (r.links && r.links[lang] && r.links[lang][level]) || [];
    var red = (r.wj && r.wj[lang] && r.wj[lang][level]) || [];
    // Every place a piece starts or ends: the links' ends and the red's.
    var cuts = [0, raw.length];
    ranges.concat(red).forEach(function (g) { cuts.push(g[0], g[1]); });
    cuts = cuts.filter(function (c, i) { return cuts.indexOf(c) === i; }).sort(function (a, b) { return a - b; });
    var chunks = [];
    for (var n = 0; n + 1 < cuts.length; n++) {
      var a = cuts[n], b = cuts[n + 1];
      var link = ranges.filter(function (g) { return g[0] <= a && b <= g[1]; })[0];
      var wj = red.some(function (g) { return g[0] <= a && b <= g[1]; });
      // A link split by the red's edge keeps its ids on both sides.
      chunks.push([raw.slice(a, b), link ? link[2] : null, wj]);
    }
    var out = [[verseOf(r.refs[0]), []]];
    chunks.forEach(function (c) {
      c[0].split(VERSE).forEach(function (part, i) {
        if (i % 2) { out.push([markerVerse(r, part), []]); return; }
        // A line break is a piece of its own: [null, null]. Alignment spans
        // never hold one, so it only ever falls in unlinked text.
        part.split(LINE).forEach(function (bit, j) {
          if (j) out[out.length - 1][1].push([null, null]);
          if (bit) out[out.length - 1][1].push([bit, c[1], c[2]]);
        });
      });
    });
    var first = out[0][1][0];
    if (first && first[0] && !first[1]) first[0] = first[0].replace(/^\s+/, "");
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

  function render(text) { return OWBMarkup.render(text, settings); }

  // Text as a node: a span the red letters colour where Jesus speaks
  // (body.red-letter, the reader's setting), plain text elsewhere.
  function wordsNode(text, wj) {
    return wj ? el("span", "wj", text) : document.createTextNode(text);
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function save() {
    var kept = {};
    for (var k in settings) if (k !== "lang") kept[k] = settings[k];
    kept.at = settingsAt = Date.now();
    try { localStorage.setItem(STORE, JSON.stringify(kept)); } catch (e) { /* ignore */ }
    document.dispatchEvent(new Event("owb:settings"));
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
    // Christ (New Testament), and measures only where it has them, so
    // some hints are missing.
    ["gender", "christos", "divine_name", "deity_pronoun", "units", "plural_you", "view", "headings", "crossrefs", "red_letter"].forEach(function (name) {
      var hint = document.getElementById("hint-" + name);
      if (hint) hint.textContent = t("hint_" + name)[settings[name]];
    });
    // The summary on the phone settings button: each shown choice's label.
    var summary = [];
    // "Show", "Hide" or "Red" means nothing without its label, so headings,
    // cross-references and the words of Jesus are left out.
    var shown = ".control:not([hidden]) .seg:not([data-setting=headings]):not([data-setting=crossrefs])" +
      ":not([data-setting=red_letter])";
    document.querySelectorAll(shown).forEach(function (seg) {
      var on = seg.querySelector('[aria-pressed="true"]');
      if (on && seg.children.length > 1) summary.push(on.textContent);
    });
    document.getElementById("settings-summary").textContent = summary.join(" \u00b7 ");
    // The Wording button names the wording choices it holds.
    var wording = [];
    document.querySelectorAll("#wording " + shown).forEach(function (seg) {
      var on = seg.querySelector('[aria-pressed="true"]');
      if (on) wording.push(on.textContent);
    });
    var ws = document.getElementById("wording-summary");
    if (ws) ws.textContent = wording.join(" \u00b7 ");
    // On paper: the reference, the settings it was printed with, and where.
    var head = document.getElementById("print-head");
    if (head) head.textContent = DATA.title + " \u00b7 Open Word Bible \u00b7 " + summary.join(" \u00b7 ") +
      " \u00b7 " + location.host + location.pathname;
    document.body.classList.toggle("plain", plain());
    document.body.classList.toggle("red-letter", settings.red_letter === 1);
    document.body.classList.toggle("view-parallel", parallel());
    document.body.classList.toggle("view-interlinear", interlinear());
    // Offer Parallel only with another language, Interlinear only with links.
    var views = document.querySelector('[data-setting="view"]');
    if (views) {
      views.querySelector('[data-value="2"]').hidden = !partners().length;
      views.querySelector('[data-value="3"]').hidden = !anyLinks();
    }
  }

  // The headings control only where the chapter has headings.
  var headingsSeg = document.querySelector('[data-setting="headings"]');
  if (headingsSeg && !Object.keys(DATA.headings).length) headingsSeg.parentNode.hidden = true;
  // And the cross-references control only where the chapter has some.
  var crossrefsSeg = document.querySelector('[data-setting="crossrefs"]');
  if (crossrefsSeg && !Object.keys(DATA.crossrefs).length) crossrefsSeg.parentNode.hidden = true;

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
    // Above the opener only where it clears the header.
    var header = document.querySelector("header.site");
    var ceiling = header ? Math.max(gap, header.getBoundingClientRect().bottom + 8) : gap;
    if (top + popover.offsetHeight > window.innerHeight - gap && r.top - popover.offsetHeight - 8 > ceiling)
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
    if (parallel()) { drawParallel(box); drawUnsureToggle(0); drawViewTools(); drawNotes([]); drawMargin(); return; }
    drawViewTools();
    var shown = null;   // last verse number printed
    var marked = marks();
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
      // left out until it has that language. Headings are editorial, not
      // translation, so the reader can hide them; a hidden heading still
      // starts its paragraph, so the text does not reflow.
      var heading = DATA.headings[r.id];
      var hlang = heading && settings.headings === 0 &&
        [settings.lang, textLang(r)].filter(function (l) { return heading[l]; })[0];
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
      var poem = poetic(r, lang);
      parts.forEach(function (part, i) {
        var span = el("span", (lang === settings.lang ? "verse" : "verse fallback") +
                           (poem ? " poem" : "") + (settings.uncertain && unsure ? " unsure" : ""));
        if (lang !== settings.lang) span.lang = lang;
        if (!plain()) {
          span.tabIndex = 0;
          span.setAttribute("role", "button");
          span.setAttribute("aria-label", t("verse_label").replace("{v}", part[0]));
        }
        span.dataset.v = part[0];
        span.dataset.record = r.id;
        var m = marked[verseId(part[0])];
        if (m && m.h) span.classList.add("hl-" + m.h);
        if (m && m.b) span.classList.add("bookmarked");
        if (m && m.n) span.classList.add("noted");
        if (current && current.id === r.id) span.setAttribute("aria-current", "true");
        // Poetry: the verse is a block of lines, each a block with a
        // hanging indent; a space between lines keeps copied text apart.
        var into = span;
        function newLine() {
          if (into !== span) span.appendChild(document.createTextNode(" "));
          into = el("span", "line");
          span.appendChild(into);
        }
        if (poem) newLine();
        if (part[0] !== shown) into.appendChild(verseNumber(part[0]));
        shown = part[0];
        part[1].forEach(function (piece) {
          if (piece[0] === null) {
            if (poem) newLine(); else into.appendChild(document.createTextNode(" "));
            return;
          }
          var text = render(piece[0]);
          if (!piece[1]) { into.appendChild(wordsNode(text, piece[2])); return; }
          if (interlinear()) {
            // The original words over the English they became.
            var ruby = el("ruby", "il" + (piece[2] ? " wj" : ""));
            ruby.appendChild(document.createTextNode(text));
            var rt = el("rt", null, piece[1].map(function (id) { return WORD_TEXT[id] || ""; }).join(" ").trim());
            rt.lang = DATA.source;
            ruby.appendChild(rt);
            into.appendChild(ruby);
            return;
          }
          var w = el("span", "aw" + (piece[2] ? " wj" : ""), text);
          w.dataset.tokens = piece[1].join(" ");
          // In the chosen sentence, pointing at an English word lights the
          // Greek it came from in the panel.
          if (chosen) {
            w.addEventListener("mouseenter", function () { light(piece[1]); });
            w.addEventListener("mouseleave", function () { light([]); });
            w.addEventListener("click", function (e) { e.stopPropagation(); light(piece[1]); });
          }
          into.appendChild(w);
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
          into.appendChild(sup);
        }
        if (i === parts.length - 1 && !plain()) {
          var echoes = echoTags(r);
          if (echoes) into.appendChild(echoes);
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
    drawMargin();
    if (listen.on) mark(false);
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
      if (heading && settings.headings === 0 && (heading[settings.lang] || heading.en)) {
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
          // Each verse its number and words; poetry a block of lines, as in
          // the reading view.
          var poem = poetic(r, lang);
          versePieces(r, lang, settings.level).forEach(function (part) {
            var verse = poem ? el("span", "poem") : cell;
            var line = poem ? el("span", "line") : cell;
            if (poem) verse.appendChild(line);
            line.appendChild(el("sup", "pv", part[0]));
            part[1].forEach(function (piece) {
              if (piece[0] !== null) { line.appendChild(wordsNode(render(piece[0]), piece[2])); return; }
              if (!poem) { line.appendChild(document.createTextNode(" ")); return; }
              verse.appendChild(document.createTextNode(" "));
              line = el("span", "line");
              verse.appendChild(line);
            });
            if (poem) cell.appendChild(verse);
            cell.appendChild(document.createTextNode(" "));
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

  // Above the text: mark the sentences where a decision is uncertain, and
  // list their verses ("5:9, 5:11"); each opens that verse's reasoning.
  function drawUnsureToggle(n) {
    var bar = document.getElementById("unsure-bar");
    var b = document.getElementById("unsure-toggle");
    if (!bar) {
      bar = el("div", "unsure-bar");
      bar.id = "unsure-bar";
      b = el("button", "text-tool");
      b.id = "unsure-toggle";
      b.type = "button";
      b.addEventListener("click", function () { setSetting("uncertain", settings.uncertain ? 0 : 1); });
      bar.appendChild(b);
      var box = document.getElementById("text");
      box.parentNode.insertBefore(bar, box);
    }
    bar.hidden = b.hidden = !n;
    b.setAttribute("aria-pressed", settings.uncertain ? "true" : "false");
    b.textContent = t("unsure_toggle").replace("{n}", n);
    var old = bar.querySelector(".unsure-list");
    if (old) old.remove();
    if (!n) return;
    var list = el("span", "unsure-list");
    list.setAttribute("role", "group");
    list.setAttribute("aria-label", t("unsure_list"));
    DATA.records.forEach(function (r) {
      var ds = decisionsFor(r);
      var d = ds.meaning.concat(ds.rendering).filter(function (x) { return x.uncertain; })[0];
      if (!d) return;
      var verse = verseOf(r.refs[0]);
      if (list.childNodes.length) list.appendChild(document.createTextNode(", "));
      var a = el("a", "unsure-ref", /:/.test(verse) ? verse : DATA.chapter + ":" + verse);
      a.href = "#v" + verse;
      if (current === r) a.setAttribute("aria-current", "true");
      a.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        select(r, verse, d.id);
        reveal(verse);
      });
      list.appendChild(a);
    });
    bar.appendChild(list);
  }

  // After a sentence that echoes other scripture: a quiet tag naming the
  // passage ("Deut 25:4"), from its "Echo of other scripture" decisions that
  // name a chapter and verse. At most two; the tag opens the reasoning.
  function echoTags(r) {
    var seen = {}, out = [];
    r.decisions.forEach(function (d) {
      if (d.layer !== "meaning" || d.category !== "allusion") return;
      var re = refPattern(), text = render(d.choice), m;
      re.lastIndex = 0;
      while ((m = re.exec(text))) {
        var code = DATA.bookRefs.names[m[1]];
        var key = code + " " + m[2] + ":" + m[3] + (m[4] ? "\u2013" + m[4] : "");
        if (seen[key] || (code === DATA.book && Number(m[2]) === DATA.chapter)) continue;
        seen[key] = true;
        out.push({ decision: d, code: code, ref: m[2] + ":" + m[3] + (m[4] ? "\u2013" + m[4] : "") });
      }
    });
    if (!out.length) return null;
    var box = el("span", "echo-tags");
    out.slice(0, 2).forEach(function (x) {
      var names = (DATA.bookRefs.abbr && DATA.bookRefs.abbr[x.code]) || [x.code, x.code];
      var b = el("button", "echo-tag", names[0] + "\u00a0" + x.ref);
      b.type = "button";
      var full = names[1] + " " + x.ref;
      b.title = full;
      b.setAttribute("aria-label", t("echo_tag").replace("{ref}", full));
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        select(r, splitVerses(r, r.renderings[textLang(r)][settings.level]).pop()[0], x.decision.id);
      });
      b.addEventListener("keydown", function (e) { e.stopPropagation(); });
      box.appendChild(b);
    });
    return box;
  }

  // Cross-references (DATA.crossrefs, by verse id, from data/crossrefs/):
  // other passages on the same subject, chosen by the readers of
  // OpenBible.info, most voted first. They are not translation, so they are
  // credited to their source, and the reader can hide them. On wide screens
  // the best few stand in the margin beside their verse; the panel lists a
  // chosen sentence's all. "ISA.40.11", "EZK.34.11-12", "GEN.1.31-2.3".
  var XREF = /^([1-3]?[A-Z]{2,3})\.(\d+)\.(\d+)(?:-(?:(\d+)\.)?(\d+))?$/;
  var XREF_MARGIN = 3;
  var BOOK_ORDER = {};
  Object.keys(DATA.bookRefs.abbr || {}).forEach(function (code, i) { BOOK_ORDER[code] = i; });
  // In Study and Interlinear: Reading and Parallel are for the text alone.
  function xrefsShown() {
    return settings.crossrefs === 0 && (!plain() || interlinear()) && Object.keys(DATA.crossrefs).length > 0;
  }
  function parseXref(text) {
    var m = XREF.exec(text);
    if (!m) return null;
    var cv = m[2] + ":" + m[3] + (m[5] ? "\u2013" + (m[4] ? m[4] + ":" : "") + m[5] : "");
    var names = (DATA.bookRefs.abbr && DATA.bookRefs.abbr[m[1]]) || [m[1], m[1]];
    return { id: text, code: m[1], chapter: Number(m[2]), verse: Number(m[3]),
             short: names[0] + "\u00a0" + cv, full: names[1] + " " + cv };
  }
  // A verse's references, the best max of them, in the Bible's order.
  function xrefs(vid, max) {
    return (DATA.crossrefs[vid] || []).slice(0, max).map(parseXref).filter(Boolean).sort(function (a, b) {
      return (BOOK_ORDER[a.code] - BOOK_ORDER[b.code]) || (a.chapter - b.chapter) || (a.verse - b.verse);
    });
  }
  // Into the reader where that chapter is translated, otherwise to search.
  // Pointing at it shows the passage in a preview; on a touch screen the
  // first tap shows the preview, which has the link on.
  function xrefLink(x, label) {
    var away = !translated(x.code, x.chapter);
    var a = el("a", "xr-link" + (away ? " xr-away" : ""), label);
    a.href = refUrl(x.code, x.chapter, x.verse, x.full);
    a.setAttribute("aria-haspopup", "dialog");
    a.addEventListener("click", function (e) {
      e.stopPropagation();
      if (TOUCH && !(popover && popover.opener === a)) { e.preventDefault(); openXrefs(a, [x], true); }
    });
    a.addEventListener("mouseenter", function () { if (!TOUCH) hoverXrefs(a, [x]); });
    a.addEventListener("mouseleave", leaveXrefs);
    return a;
  }

  // Previews: the passage's words, fetched a chapter at a time from
  // DATA.verses.url (build_site.verse_files) and kept for the visit. Our
  // text at the reader's level and settings, in the reading language or
  // else English; a verse not translated yet in the comparison edition,
  // labelled as not ours. A range shows its first XREF_VERSES verses.
  var TOUCH = window.matchMedia && window.matchMedia("(hover: none)").matches;
  var XREF_VERSES = 4;
  var chapterFiles = {};
  function chapterFile(code, chapter) {
    var key = code + "/" + chapter;
    if (!chapterFiles[key]) {
      chapterFiles[key] = fetch(DATA.verses.url + key + ".json").then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      });
      chapterFiles[key].catch(function () { delete chapterFiles[key]; });
    }
    return chapterFiles[key];
  }
  // The verses of x, at most XREF_VERSES of them, as [chapter, verse, got]:
  // its first chapter from its first verse, then the next chapter's from
  // verse 1 where the range runs on. more: the range is longer than that.
  function xrefVerses(x) {
    var m = XREF.exec(x.id);
    var lastCh = m[5] ? Number(m[4] || m[2]) : x.chapter, lastV = m[5] ? Number(m[5]) : x.verse;
    var out = [];
    function walk(c, v) {
      return chapterFile(x.code, c).then(function (file) {
        for (; out.length < XREF_VERSES && (c < lastCh || v <= lastV); v++) {
          var got = verseFrom(file, String(v));
          if (!got) break;
          out.push([c, v, got]);
        }
        if (out.length < XREF_VERSES && c < lastCh) return walk(c + 1, 1);
        var end = out[out.length - 1];
        return { list: out, more: !end || end[0] !== lastCh || end[1] !== lastV };
      });
    }
    return walk(x.chapter, x.verse);
  }
  // One verse from a chapter file: {text, lang} or {text, compare: name}.
  function verseFrom(file, v) {
    var own = file.v && file.v[v];
    var lang = own && (own[settings.lang] ? settings.lang : own.en ? "en" : null);
    if (lang) {
      var levels = own[lang];
      return { text: flat(render(levels[settings.level] || levels.B)), lang: lang };
    }
    var editions = DATA.verses.compare;
    for (var i = 0; i < editions.length; i++) {
      var c = file.c && file.c[editions[i][0]];
      if (c && c[v]) return { text: c[v], compare: editions[i][1], lang: editions[i][2] };
    }
    return null;
  }
  function fillXref(body, x) {
    xrefVerses(x).then(function (span) {
      if (!span.list.length) throw new Error("no verse");
      body.textContent = "";
      var p = el("p", "xr-pop-text"), source = null;
      span.list.forEach(function (item, i) {
        var got = item[2];
        if (span.list.length > 1) p.appendChild(el("sup", null, (item[0] !== x.chapter ? item[0] + ":" : "") + item[1]));
        var words = el("span", null, got.text + (i < span.list.length - 1 ? " " : ""));
        if (got.lang !== settings.lang) words.lang = got.lang;
        p.appendChild(words);
        if (got.compare) source = got.compare;
      });
      if (span.more) p.appendChild(document.createTextNode(" \u2026"));
      body.appendChild(p);
      if (source) body.appendChild(el("p", "xref-src", t("xref_nt") + ". " + t("xref_source").replace("{name}", source)));
      placeNote();
    }).catch(function () {
      body.textContent = "";
      body.appendChild(el("p", "empty", t("xr_failed")));
      placeNote();
    });
  }
  // A preview of each of list, under opener. focus: move focus into it (a
  // tap or a key), not on a hover.
  function openXrefs(opener, list, focus, label) {
    var same = popover && popover.opener === opener;
    closeNote(false);
    if (same) return;
    var box = el("div", "fn-pop xr-pop");
    box.id = "fn-pop";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-label", label || list[0].full);
    var first = null;
    list.forEach(function (x) {
      var item = el("div", "xr-pop-item");
      var head = el("p", "fn-pop-head");
      head.appendChild(el("span", "note-ref", x.full));
      item.appendChild(head);
      var body = el("div", "xr-pop-body");
      body.appendChild(el("p", "empty", t("xr_loading")));
      item.appendChild(body);
      var go = el("a", "fn-pop-more", t("xr_read") + " \u2192");
      go.href = refUrl(x.code, x.chapter, x.verse, x.full);
      item.appendChild(go);
      if (!first) first = go;
      box.appendChild(item);
      fillXref(body, x);
    });
    box.addEventListener("click", function (e) { e.stopPropagation(); });
    box.addEventListener("mouseenter", function () { clearTimeout(xrefTimer); });
    box.addEventListener("mouseleave", leaveXrefs);
    document.body.appendChild(box);
    popover = box;
    box.opener = opener;
    opener.setAttribute("aria-expanded", "true");
    opener.setAttribute("aria-controls", "fn-pop");
    placeNote();
    if (focus) first.focus({ preventScroll: true });
  }
  // On a hover: open after a moment, close a moment after the pointer leaves
  // both the link and the preview.
  var xrefTimer = null;
  function hoverXrefs(a, list) {
    clearTimeout(xrefTimer);
    if (popover && popover.opener === a) return;
    xrefTimer = setTimeout(function () { openXrefs(a, list, false); }, 300);
  }
  function leaveXrefs() {
    clearTimeout(xrefTimer);
    xrefTimer = setTimeout(function () {
      if (popover && popover.classList.contains("xr-pop") && !popover.matches(":hover")) closeNote(false);
    }, 250);
  }
  function xrefLine(node, list, long) {
    list.forEach(function (x, i) {
      if (i) node.appendChild(document.createTextNode("; "));
      node.appendChild(xrefLink(x, long ? x.full : x.short));
    });
    return node;
  }

  // The margin beside the text (#xr-margin, before #text, so copying the
  // text never takes it along): each verse's number and its best
  // references. The style sheet shows it only where there is room.
  function drawMargin() {
    var box = document.getElementById("xr-margin");
    if (!box) return;
    box.textContent = "";
    document.body.classList.toggle("xr-on", xrefsShown());
    if (!xrefsShown()) { layoutMargin(); return; }
    var seen = {};
    document.querySelectorAll("#text .verse").forEach(function (span) {
      var v = span.dataset.v, vid = verseId(v);
      if (seen[vid] || !DATA.crossrefs[vid]) return;
      seen[vid] = true;
      var note = el("p", "xr-note" + (currentVerse === v ? " on" : ""));
      note.setAttribute("role", "group");
      note.setAttribute("aria-label", t("crossrefs_label").replace("{v}", v));
      note.appendChild(el("span", "xr-v", v));
      xrefLine(note, xrefs(vid, XREF_MARGIN), false);
      note.verse = span;
      box.appendChild(note);
    });
    layoutMargin();
  }

  // Each note level with its verse, or just below the note before it.
  // Notes that run past the end of the text lengthen it, so they never
  // reach the notes below.
  function layoutMargin() {
    var box = document.getElementById("xr-margin"), text = document.getElementById("text");
    if (!box) return;
    var room = getComputedStyle(box).display !== "none" && box.children.length > 0;
    var need = "";
    if (room) {
      box.style.top = text.offsetTop + "px";
      box.style.left = (text.offsetLeft + text.offsetWidth) + "px";
      var top = box.getBoundingClientRect().top, below = 0;
      Array.prototype.forEach.call(box.children, function (note) {
        var y = Math.max(Math.round(note.verse.getBoundingClientRect().top - top), below);
        note.style.top = y + "px";
        below = y + note.offsetHeight + 6;
      });
      var last = text.lastElementChild;
      var height = last ? last.getBoundingClientRect().bottom - text.getBoundingClientRect().top : 0;
      if (below > height) need = Math.ceil(below) + "px";
    }
    if (text.style.minHeight !== need) text.style.minHeight = need;
  }
  if (window.ResizeObserver) new ResizeObserver(layoutMargin).observe(document.getElementById("text"));

  // A verse number in the text. Where the margin has no room (phones), a
  // verse with cross-references carries a small mark by its number that
  // opens their previews; the style sheet shows it only there.
  function verseNumber(v) {
    var sup = el("sup", null, v);
    var vid = verseId(v);
    if (!xrefsShown() || !DATA.crossrefs[vid]) return sup;
    var b = el("button", "xr-mark");
    b.type = "button";
    var label = t("crossrefs_label").replace("{v}", v);
    b.setAttribute("aria-label", label);
    b.setAttribute("aria-haspopup", "dialog");
    b.setAttribute("aria-expanded", "false");
    b.addEventListener("click", function (e) { e.stopPropagation(); openXrefs(b, xrefs(vid), true, label); });
    b.addEventListener("keydown", function (e) { e.stopPropagation(); });
    sup.appendChild(b);
    return sup;
  }

  // In the panel: the chosen sentence's references, each verse's in full.
  function xrefSection(r) {
    if (settings.crossrefs !== 0) return null;
    var vids = r.refs.filter(function (vid) { return DATA.crossrefs[vid]; });
    if (!vids.length) return null;
    var box = el("div", "xr-panel");
    box.appendChild(el("h3", null, t("crossrefs")));
    var list = el("ul", "xr-list");
    vids.forEach(function (vid) {
      var li = el("li");
      if (r.refs.length > 1) li.appendChild(el("span", "xr-v", verseOf(vid)));
      list.appendChild(xrefLine(li, xrefs(vid), true));
    });
    box.appendChild(list);
    box.appendChild(el("p", "hint xr-credit", t("crossrefs_credit")));
    return box;
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

  function translated(code, chapter) {
    return (DATA.bookRefs.chapters[code] || []).indexOf(chapter) >= 0;
  }

  // away, when given, collects the references to chapters not translated
  // yet; they stay plain text, and the caller shows them as cards
  // (refCards) instead of sending the reader to a search that finds nothing.
  function linked(tag, cls, text, away) {
    var node = el(tag, cls);
    var re = refPattern(), at = 0, m;
    re.lastIndex = 0;
    while ((m = re.exec(text))) {
      node.appendChild(document.createTextNode(text.slice(at, m.index)));
      var code = DATA.bookRefs.names[m[1]], chapter = Number(m[2]);
      if (away && !translated(code, chapter)) {
        node.appendChild(el("span", "sref sref-away", m[0]));
        if (!away.some(function (x) { return x.label === m[0]; }))
          away.push({ label: m[0], code: code, chapter: chapter, first: Number(m[3]), last: Number(m[4] || m[3]) });
      } else {
        var a = el("a", "sref", m[0]);
        a.href = refUrl(code, chapter, Number(m[3]), m[0]);
        a.addEventListener("click", function (e) { e.stopPropagation(); });
        node.appendChild(a);
      }
      at = m.index + m[0].length;
    }
    node.appendChild(document.createTextNode(text.slice(at)));
    return node;
  }

  // A reference to a chapter not translated yet: the reference, "Not
  // translated yet", and the verse from a public-domain Bible for comparison
  // (DATA.compare, chosen at build time), labelled as not ours. Search stays
  // as a second way on.
  function refCards(away) {
    var box = el("div", "xrefs");
    away.forEach(function (x) {
      var card = el("div", "xref");
      var head = el("p", "xref-head");
      head.appendChild(el("span", "xref-ref", x.label));
      head.appendChild(el("span", "xref-nt", t("xref_nt")));
      var search = el("a", "xref-search", t("xref_search"));
      search.href = DATA.bookRefs.search + "?q=" + encodeURIComponent(x.label);
      search.addEventListener("click", function (e) { e.stopPropagation(); });
      head.appendChild(search);
      card.appendChild(head);
      var verses = (DATA.compare && DATA.compare.verses) || {};
      var text = el("p", "xref-text");
      text.lang = DATA.compare ? DATA.compare.lang : "en";
      var many = x.last > x.first;
      for (var v = x.first; v <= Math.max(x.first, x.last); v++) {
        var words = verses[x.code + "." + x.chapter + "." + v];
        if (!words) continue;
        if (many) text.appendChild(el("sup", null, v + " "));
        text.appendChild(document.createTextNode(words + " "));
      }
      // The build brings the first few verses of a long range.
      if (text.childNodes.length && x.last - x.first >= 4) text.appendChild(document.createTextNode("…"));
      if (text.childNodes.length) {
        card.appendChild(text);
        card.appendChild(el("p", "xref-src", t("xref_source").replace("{name}", DATA.compare.name)));
      }
      box.appendChild(card);
    });
    return box;
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
        // A term whose English differs by level (gospel) names each level's.
        if (c.type === "term") card.appendChild(el("span", "wcard-note", c.rule || t("card_term").replace("{words}", c.english.join(", "))));
        else card.appendChild(el("span", "wcard-note", c.note));
        card.addEventListener("click", function () { highlight(byCard[i], null); light(byCard[i]); });
        list.appendChild(card);
        // A key term links to its page: every place the translation uses it.
        if (c.href) {
          var more = el("a", "wcard-link", t("card_term_link"));
          more.href = c.href;
          list.appendChild(more);
        }
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
    var away = [];
    card.appendChild(linked("p", "why", d.reason, away));
    if (away.length) card.appendChild(refCards(away));
    var ask = askLink(d);
    ask.classList.add("card-ask");
    card.appendChild(ask);
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
    var at = verseIndex(), count = verses().length;
    title.appendChild(stepButton(-1, at <= 0));
    title.appendChild(el("span", "panel-ref", ref));
    title.appendChild(stepButton(1, at < 0 || at >= count - 1));
    panel.appendChild(title);
    panel.appendChild(toolRow());
    // One row of actions, the rest folded under "More", so the reasoning
    // starts near the top; the sticky title holds only the reference.
    var actions = el("div", "panel-actions");
    actions.appendChild(bookmarkButton(currentVerse));
    actions.appendChild(linkButton(currentVerse));
    actions.appendChild(citeButton());
    actions.appendChild(moreButton());
    panel.appendChild(actions);
    panel.appendChild(citeBox(currentVerse));
    panel.appendChild(moreBox(currentVerse));
    var mine = myNoteBox(currentVerse);
    if (mine) panel.appendChild(mine);
    // On phones the sheet opens at 60% height: its footnotes and uncertain
    // decisions come first, ahead of the word list (hidden on wide screens,
    // where the full notes are a scroll away).
    var key = keyNotes();
    if (key) panel.appendChild(key);

    var wordsHead = el("div", "words-head");
    wordsHead.appendChild(el("h3", null, t("greek")));
    wordsHead.appendChild(scriptControl());
    panel.appendChild(wordsHead);
    // Interlinear: each Greek word (or Hebrew morpheme) over its gloss. Tapping one shows its
    // dictionary form, Strong's number and grammar, and lights up every
    // decision that names it. The Script setting shows the original
    // letters (0), a transliteration (1) or both (2); transliterated
    // Hebrew reads left to right.
    var greek = el("div", "interlinear");
    if (HEBREW && settings.script !== 1) greek.dir = "rtl";
    var info = el("div", "wordinfo");
    info.setAttribute("aria-live", "polite");
    info.hidden = true;
    function drawWord(word) {
      var w = el("button", "word iw");
      w.type = "button";
      w.dataset.id = word.id;
      if (settings.script !== 1) {
        var g = el("span", "iw-g", word.text + word.after.trim());
        g.lang = DATA.source;
        w.appendChild(g);
      }
      if (settings.script !== 0) w.appendChild(el("span", "iw-t", (word.translit + latinAfter(word)) || "\u00a0"));
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
        if (word.translit) head.appendChild(el("span", "wi-label", word.translit));
        info.appendChild(head);
        var key = (word.lang === "A" ? "A:" : "") + word.morph;
        info.appendChild(el("p", "wi-grammar", DATA.grammar[key][settings.lang]));
        info.appendChild(el("p", "wi-gloss", "\u201c" + (HEBREW ? word.gloss.replace(/\./g, " ") : word.gloss) + "\u201d"));
        info.appendChild(drawUses(word));
        // Everything about this dictionary form (/word/).
        var more = el("a", "fn-pop-more", t("word_page") + " \u2192");
        more.href = DATA.word_url + "?w=" + encodeURIComponent(word.lemma);
        info.appendChild(more);
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
    var xr = xrefSection(current);
    if (xr) panel.appendChild(xr);
    panel.appendChild(feedback(currentVerse || verseOf(current.refs[0])));
  }

  // Bookmarks, highlights and the reader's own notes, kept in this browser
  // as owb.marks by verse ("JHN.3.16"), so they hold whatever the settings
  // or language. Each keeps the verse's words as shown when it was marked,
  // for the saved verses page (site.js). {b: true, h: "yellow", n: "note",
  // text, lang, at}; a mark cleared is kept as {at} so a signed-in reader's
  // other devices clear it too (site.js syncs owb.marks with the account).
  // A note is private: only its reader sees it.
  var MARKS = "owb.marks";
  var HUES = ["yellow", "green", "blue", "pink"];
  function marks() {
    try { return JSON.parse(localStorage.getItem(MARKS) || "{}"); } catch (e) { return {}; }
  }
  // "16" -> "JHN.3.16"; "7:53" (another chapter's verse) -> "JHN.7.53".
  function verseId(v) {
    var p = String(v).split(":");
    return DATA.book + "." + (p.length > 1 ? p[0] + "." + p[1] : DATA.chapter + "." + v);
  }
  // A verse's words as shown, without its number or footnote letters
  // or echo tags.
  function verseWords(v) {
    var spans = document.querySelectorAll('#text .verse[data-v="' + v + '"]');
    return Array.prototype.map.call(spans, function (s) {
      var copy = s.cloneNode(true);
      copy.querySelectorAll("sup, .echo-tags").forEach(function (x) { x.remove(); });
      return copy.textContent.trim();
    }).join(" ");
  }
  function setMark(v, change) { setMarks([v], change); }
  // The same change to several verses (a highlight over a selection).
  function setMarks(vs, change) {
    var all = marks();
    vs.forEach(function (v) {
      var id = verseId(v), m = all[id] || {};
      for (var k in change) { if (change[k]) m[k] = change[k]; else delete m[k]; }
      if (m.b || m.h || m.n) {
        var span = verseEl(v);
        m.text = verseWords(v);
        m.lang = (span && span.lang) || settings.lang;
        m.at = Date.now();
        all[id] = m;
      } else {
        all[id] = { at: Date.now() };
      }
    });
    try { localStorage.setItem(MARKS, JSON.stringify(all)); } catch (e) { /* storage full or blocked */ }
    document.dispatchEvent(new Event("owb:marks"));
    var top = panelEl.scrollTop;
    drawText();
    drawPanel();
    panelEl.scrollTop = top;
  }

  // In the panel's actions: bookmark the verse.
  function bookmarkButton(v) {
    var m = marks()[verseId(v)] || {};
    var b = el("button", "mark-bookmark", t(m.b ? "bookmarked" : "bookmark"));
    b.type = "button";
    b.setAttribute("aria-pressed", m.b ? "true" : "false");
    b.addEventListener("click", function () { setMark(v, { b: !m.b }); });
    return b;
  }

  // Under "More": highlight the verse in a colour, add a note.
  function markRow(v) {
    var m = marks()[verseId(v)] || {};
    var row = el("div", "mark-row");
    var hues = el("div", "mark-hues");
    hues.setAttribute("role", "group");
    hues.setAttribute("aria-label", t("highlight"));
    HUES.forEach(function (hue) {
      var h = el("button", "mark-hue hl-" + hue);
      h.type = "button";
      h.setAttribute("aria-label", t("hl_" + hue));
      h.title = t("hl_" + hue);
      h.setAttribute("aria-pressed", m.h === hue ? "true" : "false");
      h.addEventListener("click", function () { setMark(v, { h: m.h === hue ? null : hue }); });
      hues.appendChild(h);
    });
    row.appendChild(hues);
    if (!m.n && myNoteEditing !== verseId(v)) {
      var add = el("button", "mark-note", t("my_note_add"));
      add.type = "button";
      add.addEventListener("click", function () { editMyNote(v, ""); });
      row.appendChild(add);
    }
    var all = el("a", "mark-all", t("saved_all"));
    all.href = DATA.saved;
    row.appendChild(all);
    return row;
  }

  // The reader's own note on the verse, under the mark row: the note with
  // an edit button, or the box to write it in. The draft outlives a redraw
  // (a sync from another device), so nothing typed is lost.
  var myNoteEditing = null, myNoteDraft = "";
  function editMyNote(v, text) {
    myNoteEditing = verseId(v);
    myNoteDraft = text;
    var top = panelEl.scrollTop;
    drawPanel();
    panelEl.scrollTop = top;
    var field = document.getElementById("my-note-text");
    if (field) field.focus();
  }
  function myNoteBox(v) {
    var m = marks()[verseId(v)] || {};
    var box = el("div", "my-note");
    if (myNoteEditing !== verseId(v)) {
      if (!m.n) return null;
      box.appendChild(el("p", "my-note-label", t("my_note")));
      box.appendChild(el("p", "my-note-text", m.n));
      var edit = el("button", "plan-undo", t("my_note_edit"));
      edit.type = "button";
      edit.addEventListener("click", function () { editMyNote(v, m.n); });
      box.appendChild(edit);
      return box;
    }
    var label = el("label", "my-note-label", t("my_note"));
    label.htmlFor = "my-note-text";
    box.appendChild(label);
    var field = el("textarea", "cite-text my-note-field");
    field.id = "my-note-text";
    field.rows = 4;
    field.maxLength = 5000;
    field.value = myNoteDraft;
    field.addEventListener("input", function () { myNoteDraft = field.value; });
    box.appendChild(field);
    box.appendChild(el("p", "fine my-note-private", t("my_note_private")));
    var buttons = el("p", "my-note-buttons");
    function done(change) {
      myNoteEditing = null;
      myNoteDraft = "";
      if (change) setMark(v, change);
      else { var top = panelEl.scrollTop; drawPanel(); panelEl.scrollTop = top; }
    }
    var save = el("button", "button", t("my_note_save"));
    save.type = "button";
    save.addEventListener("click", function () { done({ n: field.value.trim() || null }); });
    buttons.appendChild(save);
    var cancel = el("button", "plan-undo", t("my_note_cancel"));
    cancel.type = "button";
    cancel.addEventListener("click", function () { done(null); });
    buttons.appendChild(cancel);
    if (m.n) {
      var del = el("button", "plan-undo", t("my_note_delete"));
      del.type = "button";
      del.addEventListener("click", function () { done({ n: null }); });
      buttons.appendChild(del);
    }
    box.appendChild(buttons);
    return box;
  }

  // By the panel's title: the previous and next verse (as k and j do).
  function stepButton(by, off) {
    var label = t(by < 0 ? "step_prev" : "step_next");
    var b = el("button", "panel-step", by < 0 ? "\u2039" : "\u203a");
    b.type = "button";
    b.dataset.step = by;
    b.setAttribute("aria-label", label);
    b.title = label + " (" + (by < 0 ? "k" : "j") + ")";
    b.disabled = off;
    b.addEventListener("click", function () { step(by, '[data-step="' + by + '"]'); });
    return b;
  }

  // A sentence worth stopping at: one with a footnote, an uncertain
  // decision or an echo of other scripture, in this language and level.
  function noted(r) {
    var ds = decisionsFor(r);
    return ds.meaning.concat(ds.rendering).some(function (d) {
      return d.footnote || d.uncertain || d.category === "allusion";
    });
  }
  function nextNoted() {
    for (var i = DATA.records.indexOf(current) + 1; i < DATA.records.length; i++)
      if (noted(DATA.records[i])) return DATA.records[i];
    return null;
  }

  // Under the title: how far the sentence has been reviewed, and the next
  // sentence with notes.
  function toolRow() {
    var row = el("div", "panel-tools");
    var statuses = t("review_status");
    var status = el("span", "review-status review-" + current.status, statuses[current.status] || statuses.ai_draft);
    status.title = t("review_hint");
    row.appendChild(status);
    var next = nextNoted();
    var b = el("button", "panel-next-notes", t("step_notes") + " \u203a");
    b.type = "button";
    b.disabled = !next;
    b.title = next ? t("step_notes_hint") : t("step_notes_none");
    b.addEventListener("click", function () {
      var r = nextNoted();
      if (r) goTo(r, null, ".panel-next-notes");
    });
    row.appendChild(b);
    return row;
  }

  // "1 Timothy 5:18" ("John 7:53" for another chapter's verse on this page).
  function verseName(verse) {
    var name = (DATA.books && DATA.books[DATA.book]) || DATA.title.replace(/[\d:\u2013\s]+$/, "");
    return name + " " + (/:/.test(verse) ? verse : DATA.chapter + ":" + verse);
  }
  function pageLink(verse) {
    return location.origin + location.pathname + settingsQuery() + (verse ? "#v" + verse : "");
  }

  // "Question this": a new GitHub issue, filled in with what a reviewer
  // needs to find the sentence and see it as the reader saw it.
  var ISSUES = "https://github.com/jdegreef/open-word-bible/issues/new";
  function settingsLine() {
    var parts = [t(settings.level) + " (" + settings.level + ")", settings.lang];
    Object.keys(PARAMS).forEach(function (name) {
      if (name !== "level" && settings[name] !== DEFAULTS[name]) parts.push(PARAMS[name] + "=" + settings[name]);
    });
    if (settings.units) parts.push("units=" + settings.units);
    return parts.join(" \u00b7 ");
  }
  function clip(s, n) { return s.length > n ? s.slice(0, n - 1) + "\u2026" : s; }
  function issueUrl(d) {
    var ref = verseName(currentVerse);
    var title = t("ask_title").replace("{ref}", ref) + (d ? " \u00b7 " + (t("category")[d.category] || d.category) : "");
    function make(n) {
      var lines = ["**Verse:** " + ref, "**Record:** `" + current.id + "` (" + current.status + ")"];
      if (d) lines.push("**Decision:** `" + d.id + "`: " + clip(render(d.choice), n));
      lines.push("**Reading:** " + settingsLine(), "**Page:** " + pageLink(currentVerse), "",
                 "### " + t("ask_what"), "", "", "### " + t("ask_why"), "", "");
      return ISSUES + "?labels=question&title=" + encodeURIComponent(title) + "&body=" + encodeURIComponent(lines.join("\n"));
    }
    var link = make(300);
    return link.length > 6000 ? make(60) : link;
  }
  function askLink(d) {
    var a = el("a", "ask-link", t("ask"));
    a.href = issueUrl(d);
    a.target = "_blank";
    a.rel = "noopener";
    a.setAttribute("aria-label", t(d ? "ask_decision_label" : "ask_label"));
    // Settings may have changed since the panel was drawn.
    a.addEventListener("click", function (e) { e.stopPropagation(); a.href = issueUrl(d); });
    return a;
  }

  // "Suggest or ask": a suggestion or question about the verse, sent to the
  // editors (POST /api/messages; backend/feedback/), who answer by email.
  // It needs an account, so the reply has somewhere to go; signed out, the
  // box offers sign-in and comes back to the verse.
  // It sits at the end of the reasoning, with "Question this" (a public
  // GitHub issue) under it as the other way to ask.
  var noteKind = "suggestion", noteDraft = "";
  function feedback(verse) {
    var box = el("section", "feedback");
    box.appendChild(el("h3", null, t("note")));
    box.appendChild(noteBox(verse));
    var p = el("p", "feedback-public");
    var ask = askLink(null);
    ask.textContent = t("ask_public");
    p.appendChild(ask);
    box.appendChild(p);
    return box;
  }
  function account() {
    try { return JSON.parse(localStorage.getItem("owb.account") || "null"); } catch (e) { return null; }
  }
  function noteBox(verse) {
    var box = el("div", "note-box");
    box.id = "note-box";
    var me = account();
    if (!me || !me.token) {
      var p = el("p", "note-sign-in", t("note_sign_in") + " ");
      var a = el("a", null, t("note_sign_in_link"));
      a.href = DATA.login + "?redirect=" + encodeURIComponent(location.pathname + "#v" + verse);
      p.appendChild(a);
      box.appendChild(p);
      return box;
    }
    var kinds = el("div", "seg seg-small");
    kinds.setAttribute("role", "group");
    kinds.setAttribute("aria-label", t("note_kind"));
    var field = el("textarea", "cite-text note-text");
    field.id = "note-text";
    field.rows = 3;
    field.maxLength = 2000;
    field.value = noteDraft;
    function setKind(k) {
      noteKind = k;
      kinds.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.kind === k ? "true" : "false"); });
      field.placeholder = t("note_placeholder_" + k);
    }
    ["suggestion", "question"].forEach(function (k) {
      var b = el("button", null, t("note_" + k));
      b.type = "button";
      b.dataset.kind = k;
      b.addEventListener("click", function () { setKind(k); });
      kinds.appendChild(b);
    });
    var label = el("label", "cite-label", t("note_label").replace("{ref}", verseName(verse)));
    label.htmlFor = "note-text";
    field.addEventListener("input", function () { noteDraft = field.value; });
    var send = el("button", "copy-link note-send", t("note_send"));
    send.type = "button";
    var status = el("p", "note-status");
    status.setAttribute("role", "status");
    send.addEventListener("click", function () {
      if (!field.value.trim()) { status.textContent = t("note_empty"); field.focus(); return; }
      send.disabled = true;
      var api = document.querySelector('meta[name="owb-api"]').content;
      fetch(api + "/api/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + me.token },
        body: JSON.stringify({ kind: noteKind, verse: verseId(verse), lang: settings.lang, level: settings.level,
                               text: field.value })
      }).then(function (r) {
        if (r.status === 401) {
          try { localStorage.removeItem("owb.account"); } catch (e) { /* none */ }
          status.textContent = t("note_sign_in");
        } else if (r.status === 429) {
          status.textContent = t("note_limited");
        } else if (!r.ok) {
          status.textContent = t("note_error");
        } else {
          noteDraft = field.value = "";
          status.textContent = t("note_sent");
        }
      }, function () { status.textContent = t("note_error"); }).then(function () { send.disabled = false; });
    });
    box.appendChild(label);
    box.appendChild(kinds);
    box.appendChild(field);
    var row = el("div", "note-row");
    row.appendChild(send);
    row.appendChild(status);
    box.appendChild(row);
    setKind(noteKind);
    return box;
  }

  // Cite: the verse as a citation, as plain text and as Markdown, each
  // ready to copy; and the whole chapter as plain text.
  var citeOpen = false;
  function citeButton() {
    var b = el("button", "copy-link cite-toggle", t("cite"));
    b.type = "button";
    b.setAttribute("aria-expanded", citeOpen ? "true" : "false");
    b.setAttribute("aria-controls", "cite-box");
    b.addEventListener("click", function () {
      citeOpen = !citeOpen;
      b.setAttribute("aria-expanded", citeOpen ? "true" : "false");
      var box = document.getElementById("cite-box");
      if (box) box.hidden = !citeOpen;
    });
    return b;
  }

  // "More": the verse as an image, beside other Bibles (/compare/),
  // highlights and the reader's own note. Open or shut, it stays so from
  // verse to verse.
  var moreOpen = false;
  function moreButton() {
    var b = el("button", "copy-link more-toggle", t("more"));
    b.type = "button";
    b.setAttribute("aria-expanded", moreOpen ? "true" : "false");
    b.setAttribute("aria-controls", "more-box");
    b.addEventListener("click", function () {
      moreOpen = !moreOpen;
      b.setAttribute("aria-expanded", moreOpen ? "true" : "false");
      var box = document.getElementById("more-box");
      if (box) box.hidden = !moreOpen;
    });
    return b;
  }
  function moreBox(v) {
    var box = el("div", "more-box");
    box.id = "more-box";
    box.hidden = !moreOpen;
    var row = el("div", "more-links");
    row.appendChild(imageButton(v));
    var compare = el("a", "copy-link", t("compare"));
    compare.href = DATA.compare_url + "?v=" + verseId(v || verseOf(current.refs[0]));
    row.appendChild(compare);
    box.appendChild(row);
    box.appendChild(markRow(v));
    return box;
  }

  function citation(ref, status, link) {
    var cites = t("review_cite");
    return t("cite_format").replace("{ref}", ref).replace("{level}", t(settings.level))
      .replace("{status}", cites[status] || cites.ai_draft).replace("{url}", link);
  }

  function citeBox(verse) {
    var box = el("div", "cite-box");
    box.id = "cite-box";
    box.hidden = !citeOpen;
    var ref = verseName(verse), link = pageLink(verse), words = verseText(verse);
    var source = ref + " (Open Word Bible, " + t(settings.level) + ")";
    [["cite_citation", citation(ref, current.status, link)],
     ["cite_plain", words + "\n\u2014 " + source],
     ["cite_markdown", "> " + words + "\n>\n> \u2014 [" + source + "](" + link + ")"]].forEach(function (item) {
      var head = el("div", "cite-head");
      var label = el("label", "cite-label", t(item[0]));
      label.htmlFor = "cite-" + item[0];
      head.appendChild(label);
      var copy = el("button", "copy-link", t("cite_copy"));
      copy.type = "button";
      copy.setAttribute("aria-label", t("cite_copy") + ": " + t(item[0]));
      head.appendChild(copy);
      var field = el("textarea", "cite-text");
      field.id = "cite-" + item[0];
      field.readOnly = true;
      field.value = item[1];
      field.rows = Math.min(6, Math.max(2, Math.ceil(item[1].length / 46) + item[1].split("\n").length - 1));
      field.addEventListener("focus", function () { field.select(); });
      copy.addEventListener("click", function () { copyText(item[1], copy, field, t("cite_copy")); });
      box.appendChild(head);
      box.appendChild(field);
    });
    var chapter = el("button", "copy-link cite-chapter", t("cite_chapter"));
    chapter.type = "button";
    chapter.addEventListener("click", function () { copyText(chapterText(), chapter, null, t("cite_chapter")); });
    box.appendChild(chapter);
    return box;
  }

  // The chapter as plain text at the reader's settings: headings if shown,
  // paragraphs, verse numbers; then the citation.
  function chapterText() {
    var starts = new Set(DATA.paragraphs), blocks = [], para = null, shown = null;
    DATA.records.forEach(function (r) {
      var heading = DATA.headings[r.id];
      var hlang = heading && settings.headings === 0 &&
        [settings.lang, textLang(r)].filter(function (l) { return heading[l]; })[0];
      if (hlang) { blocks.push(render(heading[hlang])); para = null; }
      if (!para || starts.has(r.id)) { para = []; blocks.push(para); }
      splitVerses(r, render(r.renderings[textLang(r)][settings.level])).forEach(function (part) {
        var words = part[1].trim();
        if (!words) return;
        para.push((part[0] !== shown ? part[0] + " " : "") + words);
        shown = part[0];
      });
    });
    var draft = DATA.records.some(function (r) { return r.status === "ai_draft"; });
    return blocks.map(function (b) { return typeof b === "string" ? b : b.join(" "); }).filter(Boolean).join("\n\n") +
      "\n\n" + citation(DATA.title, draft ? "ai_draft" : DATA.records[0].status, pageLink(null));
  }

  // Copy with the clipboard API, or else by selecting the text and the
  // browser's copy command; the button says how it went.
  function copyText(text, button, field, label) {
    function done(ok) {
      button.textContent = t(ok ? "cite_copied" : "copy_failed");
      button.classList.toggle("done", ok);
      setTimeout(function () { button.textContent = label; button.classList.remove("done"); }, 1600);
    }
    function fallback() {
      var area = field;
      if (!area) {
        area = el("textarea", "cite-scratch");
        area.value = text;
        area.setAttribute("readonly", "");
        document.body.appendChild(area);
      }
      area.focus({ preventScroll: true });
      area.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      if (area !== field) { area.remove(); button.focus({ preventScroll: true }); }
      done(ok);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
    } else {
      fallback();
    }
  }

  // Footnotes, then uncertain decisions with their alternative: shown first
  // in the phone sheet (style.css hides them on wide screens).
  function keyNotes() {
    var ds = decisionsFor(current);
    var all = ds.meaning.concat(ds.rendering);
    var shown = all.filter(function (d) { return d.footnote; })
      .concat(all.filter(function (d) { return d.uncertain && !d.footnote; }));
    if (!shown.length) return null;
    var box = el("div", "key-notes");
    box.appendChild(el("h3", null, t("key_notes")));
    shown.forEach(function (d) {
      var item = el("div", "key-note" + (d.uncertain ? " unc" : ""));
      var head = el("p", "key-note-head");
      if (d.footnote) head.appendChild(el("span", "badge", t("footnote")));
      if (d.uncertain) head.appendChild(el("span", "badge unc", t("uncertain")));
      head.appendChild(el("span", "key-note-cat", t("category")[d.category] || d.category));
      item.appendChild(head);
      item.appendChild(linked("p", "key-note-text", noteText(d)));
      var more = el("button", "fn-pop-more", t("fn_reasoning") + " \u2193");
      more.type = "button";
      more.addEventListener("click", function () {
        var card = panelEl.querySelector('.card[data-decision="' + d.id + '"]');
        if (!card) return;
        card.focus({ preventScroll: true });
        card.scrollIntoView({ block: "start", behavior: scrollMotion() });
      });
      item.appendChild(more);
      box.appendChild(item);
    });
    return box;
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

  // An image of the verse to share: its text at the reader's settings, the
  // reference and level, in the site's fonts and the reader's colours.
  function imageButton(verse) {
    var b = el("button", "copy-link", t("image"));
    b.type = "button";
    b.addEventListener("click", function () {
      b.disabled = true;
      verseImage(verse).then(function (file) {
        b.disabled = false;
        if (narrow() && navigator.canShare && navigator.canShare({ files: [file] })) {
          navigator.share({ files: [file] }).catch(function () { /* dismissed */ });
          return;
        }
        var a = document.createElement("a");
        a.href = URL.createObjectURL(file);
        a.download = file.name;
        document.body.appendChild(a);
        a.click();
        setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
      }, function () { b.disabled = false; });
    });
    return b;
  }

  function verseText(verse) {
    var out = [];
    DATA.records.forEach(function (r) {
      splitVerses(r, render(r.renderings[textLang(r)][settings.level])).forEach(function (part) {
        if (part[0] === verse) out.push(part[1].trim());
      });
    });
    return out.join(" ");
  }

  function wrapLines(ctx, text, width) {
    var lines = [], line = "";
    text.split(/\s+/).forEach(function (word) {
      var test = line ? line + " " + word : word;
      if (ctx.measureText(test).width > width && line) { lines.push(line); line = word; }
      else line = test;
    });
    if (line) lines.push(line);
    return lines;
  }

  function verseImage(verse) {
    var size = 1200, pad = 100;
    var css = getComputedStyle(document.documentElement);
    function v(name, fallback) { return (css.getPropertyValue(name) || fallback).trim(); }
    var bg = v("--surface", "#fff"), text = v("--text", "#221c15"), accent = v("--accent", "#3f3d9a"), muted = v("--muted", "#6e6358");
    var serif = '"Gentium Book Plus", Georgia, serif', display = '"Fraunces", Georgia, serif', sans = '"Hanken Grotesk", system-ui, sans-serif';
    var name = (DATA.books && DATA.books[DATA.book]) || DATA.title.replace(/[\d:\u2013\s]+$/, "");
    var ref = name + " " + DATA.chapter + ":" + verse;
    var words = verseText(verse);
    return Promise.all([document.fonts.load("56px " + serif), document.fonts.load("600 48px " + display),
                        document.fonts.load("600 28px " + sans)]).then(function () {
      var canvas = document.createElement("canvas");
      canvas.width = canvas.height = size;
      var ctx = canvas.getContext("2d");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = accent;
      ctx.fillRect(pad, pad, 72, 8);
      // The largest text size that fits the space above the reference.
      var fontSize = 64, lines, room = size - pad * 2 - 230;
      do {
        ctx.font = fontSize + "px " + serif;
        lines = wrapLines(ctx, "\u201c" + words + "\u201d", size - pad * 2);
        fontSize -= 2;
      } while (lines.length * fontSize * 1.45 > room && fontSize > 26);
      fontSize += 2;
      ctx.fillStyle = text;
      ctx.textBaseline = "top";
      var y = pad + 60 + (room - lines.length * fontSize * 1.45) / 2;
      lines.forEach(function (line) { ctx.fillText(line, pad, y); y += fontSize * 1.45; });
      ctx.fillStyle = accent;
      ctx.font = "600 48px " + display;
      ctx.fillText(ref, pad, size - pad - 110);
      ctx.fillStyle = muted;
      ctx.font = "600 28px " + sans;
      ctx.fillText("Open Word Bible \u00b7 " + t(settings.level) + " \u00b7 openwordbible.org", pad, size - pad - 40);
      return new Promise(function (resolve, reject) {
        canvas.toBlob(function (blob) {
          if (!blob) return reject(new Error("no image"));
          var file = ref.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") + ".png";
          resolve(new File([blob], file, { type: "image/png" }));
        }, "image/png");
      });
    });
  }

  // A word's punctuation on the Latin line: maqaf joins Hebrew words with
  // a hyphen; the codex's other marks are left out.
  function latinAfter(word) {
    if (!HEBREW) return word.after.trim();
    return word.after.indexOf("\u05be") >= 0 ? "-" : "";
  }

  // The word panel's switch between original letters, transliteration
  // and both (settings.script), kept with the other reader settings.
  function scriptControl() {
    var seg = el("span", "seg seg-small");
    seg.setAttribute("data-setting", "script");
    seg.setAttribute("role", "group");
    seg.setAttribute("aria-label", t("script_label"));
    t("script_options").forEach(function (label, v) {
      var b = el("button", null, label);
      b.type = "button";
      b.setAttribute("data-value", String(v));
      b.setAttribute("aria-pressed", settings.script === v ? "true" : "false");
      b.addEventListener("click", function () { setSetting("script", v); });
      seg.appendChild(b);
    });
    return seg;
  }

  // On narrow screens the panel is a bottom sheet over the text (see .panel
  // in style.css), so opening it never moves the reader's place. The CSS
  // owns the breakpoint: the sheet is the panel when it is position: fixed.
  function narrow() { return getComputedStyle(panelEl).position === "fixed"; }
  // Smooth scrolling, unless the reader asked for less motion (the device
  // setting, or Motion in the gear menu: data-motion on <html>).
  function scrollMotion() {
    var reduce = document.documentElement.getAttribute("data-motion") === "reduce" ||
      (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
    return reduce ? "auto" : "smooth";
  }
  function verseEl(v) { return document.querySelector('.verse[data-v="' + v + '"]'); }
  // A verse in the address: #v4, or plainly #4 (#v7:53 for a verse
  // of another chapter that a sentence runs into). #at-4 (from "Continue
  // reading") only scrolls to it; see resumeAt below.
  var VERSE_ID = "(\\d+(?::\\d+)?)";
  function hashVerse() { var m = new RegExp("^#v?" + VERSE_ID + "$").exec(location.hash); return m && m[1]; }
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
      if (v) v.scrollIntoView({ behavior: scrollMotion(), block: "start" });
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

  // "?" lists the keyboard shortcuts in a small dialog; Esc or the close
  // button shuts it and focus goes back where it was.
  var keysDialog = null, keysReturn = null;
  function showKeys() {
    if (!keysDialog) {
      keysDialog = el("dialog", "keys-dialog");
      keysDialog.id = "keys-dialog";
      keysDialog.setAttribute("aria-labelledby", "keys-title");
      var head = el("div", "keys-head");
      var h = el("h2", null, t("keys_title"));
      h.id = "keys-title";
      head.appendChild(h);
      var x = el("button", "keys-close", "\u00d7");
      x.type = "button";
      x.setAttribute("aria-label", t("close"));
      x.addEventListener("click", hideKeys);
      head.appendChild(x);
      keysDialog.appendChild(head);
      var dl = el("dl", "keys-list");
      t("keys_list").forEach(function (k) {
        var dt = el("dt");
        k[0].split(" ").forEach(function (key) { dt.appendChild(el("kbd", null, key)); });
        dl.appendChild(dt);
        dl.appendChild(el("dd", null, k[1]));
      });
      keysDialog.appendChild(dl);
      keysDialog.addEventListener("click", function (e) { if (e.target === keysDialog) hideKeys(); });
      keysDialog.addEventListener("cancel", function (e) { e.preventDefault(); hideKeys(); });
      document.body.appendChild(keysDialog);
    }
    if (keysDialog.open) return;
    keysReturn = document.activeElement;
    if (keysDialog.showModal) keysDialog.showModal(); else keysDialog.setAttribute("open", "");
    keysDialog.querySelector(".keys-close").focus();
  }
  function hideKeys() {
    if (!keysDialog || !keysDialog.open) return;
    if (keysDialog.close) keysDialog.close(); else keysDialog.removeAttribute("open");
    if (keysReturn && keysReturn.focus && document.contains(keysReturn)) keysReturn.focus({ preventScroll: true });
    keysReturn = null;
  }
  // Ahead of the reader's other keys: while the list is open, Esc closes
  // only it and the other shortcuts wait.
  window.addEventListener("keydown", function (e) {
    if (keysDialog && keysDialog.open) {
      if (e.key === "Escape") { e.preventDefault(); hideKeys(); }
      if (e.key !== "Tab") e.stopPropagation();
      return;
    }
    if (e.key === "?" && !e.ctrlKey && !e.metaKey && !e.altKey && !typing(e.target)) {
      e.preventDefault();
      e.stopPropagation();
      showKeys();
    }
  }, true);

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

  // Where the chosen verse is in verses(), or -1.
  function verseIndex() {
    var i = -1;
    verses().forEach(function (v, n) { if (current && v.record === current && v.verse === currentVerse) i = n; });
    return i;
  }

  // refocus: a selector for the panel control that moved the reader (the
  // panel is drawn again, so focus returns to its new copy).
  function step(by, refocus) {
    var all = verses();
    var i = verseIndex();
    var next = all[i < 0 ? (by > 0 ? 0 : all.length - 1) : Math.min(all.length - 1, Math.max(0, i + by))];
    if (!next || (next.record === current && next.verse === currentVerse)) return;
    goTo(next.record, next.verse, refocus);
  }

  function goTo(record, verse, refocus) {
    select(record, verse);
    var v = verseEl(currentVerse);
    if (v && !narrow()) {
      if (!refocus) v.focus({ preventScroll: true });
      v.scrollIntoView({ block: "nearest", behavior: scrollMotion() });
    }
    if (refocus) {
      var b = panelEl.querySelector(refocus);
      (b && !b.disabled ? b : panelEl).focus({ preventScroll: true });
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
    if (v) v.scrollIntoView({ block: "center", behavior: instant ? "auto" : scrollMotion() });
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

  // Swipe the sheet sideways for the next (left) or previous (right) verse.
  // The direction is settled by the first few pixels: a mostly vertical
  // drag is left to scrolling and to the handle drag above. The sheet
  // follows the finger a little, unless the reader asked for less motion.
  var swipe = null;
  panelEl.addEventListener("touchstart", function (e) {
    var on = e.target.closest && e.target.closest("textarea, input, select, .cite-box");
    swipe = narrow() && current && e.touches.length === 1 && !on
      ? { x: e.touches[0].clientX, y: e.touches[0].clientY, axis: null } : null;
  }, { passive: true });
  panelEl.addEventListener("touchmove", function (e) {
    if (!swipe) return;
    var dx = e.touches[0].clientX - swipe.x, dy = e.touches[0].clientY - swipe.y;
    if (!swipe.axis && (Math.abs(dx) > 10 || Math.abs(dy) > 10)) {
      swipe.axis = Math.abs(dx) > Math.abs(dy) * 1.5 ? "x" : "y";
      if (swipe.axis === "x") {
        startY = null;
        panelEl.style.transform = "";
        panelEl.style.transition = "none";
      }
    }
    if (swipe.axis === "x" && scrollMotion() === "smooth") panelEl.style.transform = "translateX(" + dx / 4 + "px)";
  }, { passive: true });
  function endSwipe(e) {
    var s = swipe;
    swipe = null;
    if (!s || s.axis !== "x") return;
    panelEl.style.transform = panelEl.style.transition = "";
    var dx = e.type === "touchend" ? e.changedTouches[0].clientX - s.x : 0;
    if (Math.abs(dx) > 60) step(dx < 0 ? 1 : -1);
  }
  panelEl.addEventListener("touchend", endSwipe);
  panelEl.addEventListener("touchcancel", endSwipe);

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
    // New wording: read the sentence again as it now stands.
    if (listen.on && !listen.paused) speakRecord(listen.at);
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

  // Selected text gets a bar of what can be done with it, after Ochorus's:
  // copy it with its reference, highlight its verses, see why it reads as it
  // does, or suggest a change to it. The last two open the panel, so they
  // are offered in Study view only. On touch screens the bar sits below the
  // selection, clear of the system menu.
  var selBar = el("div", "sel-bar");
  selBar.setAttribute("role", "toolbar");
  selBar.setAttribute("aria-label", t("sel_actions"));
  selBar.hidden = true;
  document.body.appendChild(selBar);
  // Pressing a button must not clear the selection it acts on.
  selBar.addEventListener("mousedown", function (e) { e.preventDefault(); });

  // The verses the selection touches, in page order: [{v, record}, ...].
  function selectedVerses(range) {
    var seen = {};
    return Array.prototype.filter.call(textBox.querySelectorAll(".verse"), function (s) {
      if (!range.intersectsNode(s) || seen[s.dataset.v]) return false;
      return (seen[s.dataset.v] = true);
    }).map(function (s) {
      return { v: s.dataset.v, record: DATA.records.filter(function (r) { return r.id === s.dataset.record; })[0] };
    });
  }
  // The original words behind the selected words, where they are aligned.
  function selectedTokens(range) {
    var ids = [];
    textBox.querySelectorAll(".aw").forEach(function (a) {
      if (range.intersectsNode(a)) ids = ids.concat(a.dataset.tokens.split(" "));
    });
    return ids;
  }
  function hideBar() { selBar.hidden = true; }

  function barButton(cls, label, onClick) {
    var b = el("button", "sel-btn " + cls, label);
    b.type = "button";
    b.addEventListener("click", onClick);
    return b;
  }
  var copyBtn = barButton("sel-copy", t("copy_quote"), function () {
    var range = selectedRange();
    var text = range && quote(range);
    if (!text || !navigator.clipboard) return;
    navigator.clipboard.writeText(text).then(function () {
      copyBtn.textContent = t("copied_quote");
      setTimeout(function () { hideBar(); copyBtn.textContent = t("copy_quote"); }, 1200);
    }, function () { copyBtn.textContent = t("copy_failed"); });
  });
  var hueBox = el("span", "sel-hues");
  hueBox.setAttribute("role", "group");
  hueBox.setAttribute("aria-label", t("highlight"));
  HUES.forEach(function (hue) {
    var h = barButton("mark-hue hl-" + hue, null, function () {
      var range = selectedRange();
      if (!range) return;
      var vs = selectedVerses(range).map(function (x) { return x.v; });
      // A colour every selected verse already has comes off again.
      var all = marks();
      var off = vs.every(function (v) { return (all[verseId(v)] || {}).h === hue; });
      setMarks(vs, { h: off ? null : hue });
      window.getSelection().removeAllRanges();
      hideBar();
    });
    h.setAttribute("aria-label", t("hl_" + hue));
    h.title = t("hl_" + hue);
    hueBox.appendChild(h);
  });
  // Open the first selected verse's sentence in the panel; with "suggest",
  // with the suggestion box open and the selected words quoted in it.
  function openSelected(suggest) {
    var range = selectedRange();
    var first = range && selectedVerses(range)[0];
    if (!first || !first.record) return;
    var ids = selectedTokens(range);
    if (suggest) {
      noteKind = "suggestion";
      if (!noteDraft.trim()) noteDraft = "“" + clip(quote(range).split("\n— ")[0], 300) + "” — ";
    }
    window.getSelection().removeAllRanges();
    hideBar();
    select(first.record, first.v);
    if (ids.length) light(ids);
    var field = suggest && document.getElementById("note-text");
    if (field) { field.focus(); field.setSelectionRange(field.value.length, field.value.length); }
  }
  var whyBtn = barButton("sel-why", t("sel_why"), function () { openSelected(false); });
  var suggestBtn = barButton("sel-suggest", t("note"), function () { openSelected(true); });
  [copyBtn, hueBox, whyBtn, suggestBtn].forEach(function (b) { selBar.appendChild(b); });

  var placing = null;
  document.addEventListener("selectionchange", function () {
    clearTimeout(placing);
    placing = setTimeout(function () {
      var range = selectedRange();
      if (!range || !quote(range)) { hideBar(); return; }
      copyBtn.hidden = !navigator.clipboard;
      whyBtn.hidden = suggestBtn.hidden = plain();
      var r = range.getBoundingClientRect();
      selBar.hidden = false;
      var below = window.matchMedia("(pointer: coarse)").matches || r.top < 120;
      var top = below ? r.bottom + 10 : r.top - selBar.offsetHeight - 10;
      var left = Math.min(Math.max(16, r.left + r.width / 2 - selBar.offsetWidth / 2),
                          document.documentElement.clientWidth - selBar.offsetWidth - 16);
      selBar.style.top = top + window.scrollY + "px";
      selBar.style.left = Math.max(16, left) + window.scrollX + "px";
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

  // On wide screens the wording settings open from one button, so the bar
  // keeps to one row; Escape or a click elsewhere closes them.
  var wordingBtn = document.getElementById("wording-toggle");
  var wordingBox = document.getElementById("wording");
  function openWording(open) {
    if (wordingBtn) wordingBtn.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (wordingBtn) {
    wordingBtn.addEventListener("click", function () {
      openWording(wordingBtn.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("click", function (e) {
      if (!wordingBtn.contains(e.target) && !wordingBox.contains(e.target)) openWording(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && wordingBtn.getAttribute("aria-expanded") === "true") {
        openWording(false);
        wordingBtn.focus();
      }
    });
  }

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

  // The reader's place, kept as owb.place for "Continue reading" on the
  // home and Read pages (site.js): the verse at the reading line, a quarter
  // of the way down or just below the sticky header and settings bar if
  // that is lower (where scrollIntoView puts a verse: the page's scroll
  // padding plus the verse's scroll margin). Saving and resuming both use
  // the line, so a place does not drift.
  function readingLine() {
    var first = document.querySelector("#text .verse");
    var pad = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
    var margin = first ? parseFloat(getComputedStyle(first).scrollMarginTop) || 0 : 0;
    return Math.max(pad + margin, window.innerHeight * 0.25);
  }
  function topVerse() {
    var line = readingLine() + 1;
    var all = document.querySelectorAll("#text .verse");
    for (var i = 0; i < all.length; i++) {
      if (all[i].getBoundingClientRect().bottom > line) return all[i].dataset.v;
    }
    return all.length ? all[all.length - 1].dataset.v : null;
  }
  var keptVerse = null;
  function keepPlace() {
    var verse = topVerse();
    if (!verse || verse === keptVerse) return;
    keptVerse = verse;
    // at: when, so the latest place wins between a reader's devices.
    var place = { book: DATA.book, chapter: DATA.chapter, verse: verse, at: Date.now() };
    try { localStorage.setItem("owb.place", JSON.stringify(place)); } catch (e) { /* this visit only */ }
  }
  var placeTimer = null;
  window.addEventListener("scroll", function () {
    clearTimeout(placeTimer);
    placeTimer = setTimeout(keepPlace, 400);
  }, { passive: true });
  window.addEventListener("pagehide", keepPlace);

  var resumeAt = new RegExp("^#at-" + VERSE_ID + "$").exec(location.hash);
  if (resumeAt) {
    try {
      history.replaceState(null, "", location.pathname + location.search);
      history.scrollRestoration = "manual";
    } catch (e) { /* ignore */ }
    window.addEventListener("load", function () {
      var v = verseEl(resumeAt[1]);
      if (v) window.scrollBy(0, v.getBoundingClientRect().top - readingLine());
    });
  }

  // Listen: the browser's own voices read the passage aloud, one sentence
  // (record) at a time, in the wording the settings give, from the verse
  // the reader is at. A sentence shown in English on another language's
  // page is read in English. No audio files, so it works offline too.
  // Speed, and a voice per language, are kept as owb.listen.
  var speech = window.speechSynthesis;
  var LISTEN = "owb.listen";
  var RATES = [0.8, 1, 1.25, 1.5, 2];
  var listen = { on: false, paused: false, at: 0, utter: null, rate: 1, voices: {} };
  try {
    var kept = JSON.parse(localStorage.getItem(LISTEN) || "{}");
    if (RATES.indexOf(kept.rate) >= 0) listen.rate = kept.rate;
    if (kept.voices) listen.voices = kept.voices;
  } catch (e) { /* defaults */ }
  function keepListen() {
    try { localStorage.setItem(LISTEN, JSON.stringify({ rate: listen.rate, voices: listen.voices })); } catch (e) { /* ignore */ }
  }

  // A sentence as it is read: its language, and its text without verse
  // markers, in pieces of up to about 220 characters split at punctuation
  // (some voices stop after about fifteen seconds of one utterance).
  function spoken(r) {
    var lang = textLang(r);
    var rest = flat(render(r.renderings[lang][settings.level])).replace(new RegExp(VERSE.source, "g"), "").replace(/\s+/g, " ").trim();
    var parts = [];
    while (rest.length > 220) {
      var cut = -1, re = /[,;:\u2014.!?]\s/g, m;
      while ((m = re.exec(rest)) && m.index < 220) cut = m.index + 1;
      if (cut < 40) cut = rest.lastIndexOf(" ", 220);
      if (cut < 40) cut = 220;
      parts.push(rest.slice(0, cut).trim());
      rest = rest.slice(cut).trim();
    }
    if (rest) parts.push(rest);
    return { lang: lang, parts: parts };
  }

  // The device's voices for a language, the most natural first, without
  // the novelty voices macOS ships (Bells, Bubbles, Zarvox...).
  var NATURAL = /google|neural|natural|premium|enhanced|siri/i;
  // Whole names only: "Flo" is a novelty voice, "Florian" is not.
  var NAMED = /\b(samantha|daniel|karen|moira|tessa|serena|allison|ava|zoe|nicky|aaron|fiona|rishi|monica|paulina|jorge|thomas|amelie|audrey)\b/i;
  var NOVELTY = /^(albert|bad news|bahh|bells|boing|bubbles|cellos|deranged|good news|hysterical|jester|organ|pipe organ|superstar|trinoids|whisper|wobble|zarvox|fred|junior|ralph|kathy|grandma|grandpa|rocko|eddy|flo|reed|sandy|shelley)\b/i;
  function voicesFor(lang) {
    function score(v) { return (NATURAL.test(v.name) ? 4 : 0) + (NAMED.test(v.name) ? 2 : 0) + (v.default ? 1 : 0); }
    var seen = {};
    var all = speech.getVoices().filter(function (v) {
      if (v.lang.toLowerCase().split(/[-_]/)[0] !== lang || seen[v.name]) return false;
      seen[v.name] = true;
      return true;
    });
    var plain = all.filter(function (v) { return !NOVELTY.test(v.name); });
    // Only novelty voices for a language are still better than none.
    return (plain.length ? plain : all).sort(function (a, b) { return score(b) - score(a); });
  }
  function voiceFor(lang) {
    var all = voicesFor(lang);
    return all.filter(function (v) { return v.voiceURI === listen.voices[lang]; })[0] || all[0] || null;
  }

  // Light up the sentence being read, and follow it down the page: always
  // when the reader moved to it, otherwise only while the reader is still
  // watching the one before (not when they have scrolled away to read).
  function inView(v) {
    var box = v.getBoundingClientRect();
    return box.bottom > readingLine() && box.top < window.innerHeight - bar.offsetHeight;
  }
  function mark(follow) {
    var r = DATA.records[listen.at];
    var before = document.querySelector("#text .speaking");
    if (follow === "auto") follow = !before || inView(before);
    var first = null;
    document.querySelectorAll("#text .verse").forEach(function (v) {
      var on = r && v.dataset.record === r.id;
      v.classList.toggle("speaking", on);
      if (on && !first) first = v;
    });
    if (follow && first) {
      var box = first.getBoundingClientRect();
      if (box.top < readingLine() || box.bottom > window.innerHeight - bar.offsetHeight - 16)
        window.scrollBy(0, box.top - readingLine());
    }
    // "John 3:16", or "John 7:53\u20138:11" for a sentence across chapters.
    var range = r ? verseRange(r) : "";
    where.textContent = r ? DATA.books[DATA.book] + " " + (/:/.test(range) ? range : DATA.chapter + ":" + range) : "";
  }

  // jump: the reader moved here (start, previous/next, a new setting), so
  // the page follows; reading on by itself follows only a watching reader.
  function speakRecord(i, jump) {
    listen.utter = null;
    speech.cancel();
    if (i < 0) i = 0;
    if (i >= DATA.records.length) { stopListening(); return; }
    listen.at = i;
    listen.paused = false;
    var s = spoken(DATA.records[i]);
    var voice = voiceFor(s.lang);
    // Voices known but none for this language: say so rather than read
    // the words in another language's voice.
    if (!voice && speech.getVoices().length) {
      note.hidden = false;
      listen.paused = true;
      drawBar();
      return;
    }
    note.hidden = true;
    mark(jump === false ? "auto" : true);
    drawBar();
    (function next(k) {
      var u = new SpeechSynthesisUtterance(s.parts[k]);
      u.lang = s.lang;
      if (voice) u.voice = voice;
      u.rate = listen.rate;
      u.onend = function () {
        if (listen.utter !== u) return;   // stopped or moved on
        if (k + 1 < s.parts.length) next(k + 1);
        else speakRecord(i + 1, false);
      };
      u.onerror = function (e) {
        if (listen.utter === u && e.error !== "interrupted" && e.error !== "canceled") stopListening();
      };
      listen.utter = u;
      speech.speak(u);
    })(0);
  }

  function startListening() {
    // From the sentence chosen, or else the one at the reading line.
    var r = current || recordFor(topVerse());
    listen.on = true;
    bar.hidden = false;
    document.body.classList.add("listening");
    startBtn.setAttribute("aria-pressed", "true");
    voiceMenu();
    speakRecord(Math.max(0, DATA.records.indexOf(r)));
  }

  function stopListening() {
    listen.on = false;
    listen.utter = null;
    speech.cancel();
    bar.hidden = true;
    note.hidden = true;
    document.body.classList.remove("listening");
    document.querySelectorAll("#text .speaking").forEach(function (v) { v.classList.remove("speaking"); });
    startBtn.setAttribute("aria-pressed", "false");
    startBtn.focus({ preventScroll: true });
  }

  // Pausing stops the voice; playing again starts the sentence over (the
  // engine's own pause is unreliable on phones).
  function togglePause() {
    if (listen.paused) { speakRecord(listen.at); return; }
    listen.paused = true;
    listen.utter = null;
    speech.cancel();
    drawBar();
  }

  // The bar at the foot of the window while listening.
  var ICON = {
    play: "M8 5v14l11-7z", pause: "M7 5h3v14H7zM14 5h3v14h-3z",
    prev: "M18 5v14L8 12zM6 5v14", next: "M6 5v14l10-7zM18 5v14", stop: "M18 6 6 18M6 6l12 12"
  };
  function button(name, label, onClick) {
    var b = el("button", "listen-btn");
    b.type = "button";
    b.setAttribute("aria-label", label);
    b.title = label;
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", ICON[name]);
    svg.appendChild(path);
    b.appendChild(svg);
    b.addEventListener("click", onClick);
    return b;
  }
  var bar = el("div", "listen-bar");
  bar.hidden = true;
  bar.setAttribute("role", "region");
  bar.setAttribute("aria-label", t("listen_bar"));
  var row = el("div", "listen-row");
  var prevBtn = button("prev", t("listen_prev"), function () { speakRecord(listen.at - 1); });
  var playBtn = button("pause", t("listen_pause"), togglePause);
  playBtn.classList.add("listen-play");
  var nextBtn = button("next", t("listen_next"), function () { speakRecord(listen.at + 1); });
  var where = el("span", "listen-where");
  var rateBtn = el("button", "listen-rate");
  rateBtn.type = "button";
  rateBtn.setAttribute("aria-label", t("listen_speed"));
  rateBtn.title = t("listen_speed");
  rateBtn.addEventListener("click", function () {
    listen.rate = RATES.filter(function (x) { return x > listen.rate; })[0] || RATES[0];
    keepListen();
    if (!listen.paused) speakRecord(listen.at);
    drawBar();
  });
  var voiceSel = el("select", "listen-voice");
  voiceSel.setAttribute("aria-label", t("listen_voice"));
  voiceSel.addEventListener("change", function () {
    listen.voices[DATA.lang] = voiceSel.value;
    keepListen();
    if (!listen.paused) speakRecord(listen.at);
  });
  var stopBtn = button("stop", t("listen_stop"), stopListening);
  [prevBtn, playBtn, nextBtn, where, rateBtn, voiceSel, stopBtn].forEach(function (n) { row.appendChild(n); });
  var note = el("p", "listen-note", t("listen_no_voice"));
  note.hidden = true;
  bar.appendChild(row);
  bar.appendChild(note);
  document.body.appendChild(bar);
  // The page keeps room for the bar at its foot, however tall it grows.
  if (window.ResizeObserver) new ResizeObserver(function () {
    document.documentElement.style.setProperty("--listen-h", bar.offsetHeight + "px");
  }).observe(bar);

  function drawBar() {
    var paused = listen.paused;
    playBtn.setAttribute("aria-label", t(paused ? "listen_play" : "listen_pause"));
    playBtn.title = playBtn.getAttribute("aria-label");
    playBtn.querySelector("path").setAttribute("d", ICON[paused ? "play" : "pause"]);
    rateBtn.textContent = listen.rate + "\u00d7";
  }

  // The voice menu offers the page language's best few voices, when there
  // is a choice.
  function voiceMenu() {
    var all = voicesFor(DATA.lang).slice(0, 5);
    voiceSel.textContent = "";
    all.forEach(function (v) {
      var o = el("option", null, v.name.replace(/^(Microsoft|Google)\s+/, ""));
      o.value = v.voiceURI;
      voiceSel.appendChild(o);
    });
    var chosen = voiceFor(DATA.lang);
    if (chosen) voiceSel.value = chosen.voiceURI;
    voiceSel.hidden = all.length < 2;
  }

  var startBtn = document.getElementById("listen-start");
  if (speech && window.SpeechSynthesisUtterance && startBtn) {
    startBtn.hidden = false;
    startBtn.setAttribute("aria-pressed", "false");
    startBtn.addEventListener("click", function () {
      if (listen.on) stopListening(); else startListening();
    });
    // Voices arrive after the page in some browsers.
    if (speech.addEventListener) speech.addEventListener("voiceschanged", function () { if (listen.on) voiceMenu(); });
    // Leaving the page stops the voice (some browsers would read on).
    window.addEventListener("pagehide", function () { speech.cancel(); });
    // Back to this page from the browser's cache: the voice has stopped.
    window.addEventListener("pageshow", function (e) { if (e.persisted && listen.on) stopListening(); });
  }

  // Marks and settings from the reader's other devices (site.js, after a
  // sync). Settings a shared link carried give way only to newer ones.
  document.addEventListener("owb:synced", function () {
    var top = panelEl.scrollTop, stored = {};
    try { stored = JSON.parse(localStorage.getItem(STORE) || "{}") || {}; } catch (e) { /* none */ }
    if ((stored.at || 0) > settingsAt) { loadSettings(); drawControls(); }
    drawText();
    if (current) { drawPanel(); panelEl.scrollTop = top; }
  });

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
