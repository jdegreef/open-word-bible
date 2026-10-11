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

  function t(key) { return UI[key]; }

  // The reading language is the page's (/es/... is Spanish); the footer
  // switches it. The other settings are kept across pages and languages.
  var settings = { level: "B", gender: 0, christos: 0, deity_pronoun: 0, plural_you: 0 };
  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || "{}");
    for (var k in settings) if (k in saved) settings[k] = saved[k];
  } catch (e) { /* storage unavailable: use defaults */ }
  settings.lang = DATA.lang;

  var current = null;   // selected record
  var panelEl = document.getElementById("panel");
  var SPAN = /\{\{([a-z_]+):([^{}]*)\}\}/g;
  var VERSE = /\\v (\d+) ?/;

  function verseOf(id) { return id.split(".")[2]; }

  // A record's verses as "12" or "12\u201313".
  function verseRange(r) {
    var first = verseOf(r.refs[0]), last = verseOf(r.refs[r.refs.length - 1]);
    return first === last ? first : first + "\u2013" + last;
  }

  // Split rendered text at verse markers: [[verse, text], ...].
  function splitVerses(r, text) {
    var parts = text.split(VERSE), out = [[verseOf(r.refs[0]), parts[0].trim()]];
    for (var i = 1; i < parts.length; i += 2) out.push([parts[i], parts[i + 1]]);
    return out;
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
      });
    });
    document.getElementById("hint-level").textContent = t("hint_level")[settings.level];
    ["gender", "christos", "deity_pronoun", "plural_you"].forEach(function (name) {
      document.getElementById("hint-" + name).textContent = t("hint_" + name)[settings[name]];
    });
    // The summary on the phone settings button: each shown choice's label.
    var summary = [];
    document.querySelectorAll(".control:not([hidden]) .seg").forEach(function (seg) {
      var on = seg.querySelector('[aria-pressed="true"]');
      if (on && seg.children.length > 1) summary.push(on.textContent);
    });
    document.getElementById("settings-summary").textContent = summary.join(" \u00b7 ");
  }

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

  function drawText() {
    var box = document.getElementById("text");
    box.textContent = "";
    var partial = DATA.records.some(function (r) { return !r.renderings[settings.lang]; });
    var note = document.getElementById("partial");
    note.hidden = !partial;
    note.textContent = partial ? t("partial") : "";
    document.getElementById("title").textContent = DATA.title;
    var shown = null;   // last verse number printed
    var notes = [];
    DATA.records.forEach(function (r) {
      var ds = decisionsFor(r);
      var marks = ds.meaning.concat(ds.rendering).filter(function (d) { return d.footnote; })
        .map(function (d) {
          var mark = letter(notes.length);
          notes.push({ mark: mark, record: r, decision: d });
          return mark;
        });
      var lang = textLang(r);
      var parts = splitVerses(r, render(r.renderings[lang][settings.level]));
      parts.forEach(function (part, i) {
        var span = el("span", lang === settings.lang ? "verse" : "verse fallback");
        if (lang !== settings.lang) span.lang = lang;
        span.tabIndex = 0;
        span.setAttribute("role", "button");
        span.setAttribute("aria-label", t("verse_label").replace("{v}", part[0]));
        span.dataset.v = part[0];
        if (current && current.id === r.id) span.setAttribute("aria-current", "true");
        if (part[0] !== shown) span.appendChild(el("sup", null, part[0]));
        shown = part[0];
        span.appendChild(document.createTextNode(part[1]));
        if (marks.length && i === parts.length - 1) {
          var sup = el("sup", "fn", marks.join(","));
          sup.setAttribute("aria-label", t("notes") + " " + marks.join(", "));
          span.appendChild(sup);
        }
        span.addEventListener("click", function () { select(r, part[0]); });
        span.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(r, part[0]); }
        });
        box.appendChild(span);
        box.appendChild(document.createTextNode(" "));
      });
    });
    drawNotes(notes);
  }

  function drawNotes(notes) {
    var section = document.getElementById("notes");
    if (!section) return;
    section.textContent = "";
    section.hidden = !notes.length;
    if (!notes.length) return;
    section.appendChild(el("h2", null, t("notes")));
    var list = el("ol");
    notes.forEach(function (n) {
      var item = el("li");
      var button = el("button", "note");
      button.type = "button";
      button.appendChild(el("span", "note-mark", n.mark));
      button.appendChild(el("span", "note-ref", verseRange(n.record)));
      button.appendChild(el("span", "note-text", noteText(n.decision)));
      button.addEventListener("click", function () { select(n.record); });
      item.appendChild(button);
      list.appendChild(item);
    });
    section.appendChild(list);
  }

  function highlight(ids, card) {
    var set = new Set(ids);
    document.querySelectorAll(".word").forEach(function (w) {
      w.classList.toggle("on", set.has(w.dataset.id));
    });
    document.querySelectorAll(".card").forEach(function (c) { c.classList.toggle("on", c === card); });
  }

  function drawCard(d, record) {
    var card = el("div", "card");
    card.tabIndex = 0;
    var cat = el("div", "cat", t("category")[d.category] || d.category);
    if (d.uncertain) cat.appendChild(el("span", "badge unc", t("uncertain")));
    if (d.footnote) cat.appendChild(el("span", "badge", t("footnote")));
    card.appendChild(cat);
    card.appendChild(el("div", "choice", render(d.choice)));
    if (d.alternatives.length) {
      card.appendChild(el("div", "alts", t("also") + d.alternatives.map(render).join("; ")));
    }
    card.appendChild(el("p", "why", d.reason));
    function on() { highlight(d.tokens, card); }
    card.addEventListener("click", on);
    card.addEventListener("focus", on);
    return card;
  }

  function drawPanel() {
    var panel = panelEl;
    panel.textContent = "";
    if (!current) {
      panel.appendChild(el("h2", null, t("empty_title")));
      panel.appendChild(el("p", "empty", t("empty_text")));
      return;
    }
    var close = el("button", "sheet-close", "\u00d7");
    close.type = "button";
    close.setAttribute("aria-label", t("close"));
    close.addEventListener("click", deselect);
    panel.appendChild(close);
    panel.appendChild(el("h2", null, DATA.title.replace(/[\d:\u2013\s]+$/, "") + " " + DATA.chapter + ":" + verseRange(current)));

    panel.appendChild(el("h3", null, t("greek")));
    // Interlinear: each Greek word over its gloss. Tapping one shows its
    // dictionary form, Strong's number and grammar, and lights up every
    // decision that names it.
    var greek = el("div", "interlinear");
    var info = el("div", "wordinfo");
    info.setAttribute("aria-live", "polite");
    info.hidden = true;
    function drawWord(word) {
      var w = el("button", "word iw");
      w.type = "button";
      w.dataset.id = word.id;
      var g = el("span", "iw-g", word.text + word.after.trim());
      g.lang = "grc";
      w.appendChild(g);
      w.appendChild(el("span", "iw-e", word.gloss));
      w.addEventListener("click", function () {
        info.textContent = "";
        var head = el("p", "wi-head");
        var lemma = el("span", "wi-lemma", word.lemma);
        lemma.lang = "grc";
        head.appendChild(lemma);
        head.appendChild(el("span", "wi-label", t("lemma") + (word.strong ? " \u00b7 " + t("strong") + " G" + word.strong : "")));
        info.appendChild(head);
        info.appendChild(el("p", "wi-grammar", DATA.grammar[word.morph][settings.lang]));
        info.appendChild(el("p", "wi-gloss", "\u201c" + word.gloss + "\u201d"));
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
    panel.appendChild(el("p", "hint", t("word_hint")));
    panel.appendChild(greek);
    panel.appendChild(info);

    panel.appendChild(el("h3", null, t("gloss")));
    var gloss = el("p", "gloss");
    splitVerses(current, current.literal_gloss).forEach(function (part, i) {
      if (i > 0) gloss.appendChild(el("sup", null, " " + part[0]));
      gloss.appendChild(document.createTextNode((i > 0 ? " " : "") + part[1]));
    });
    panel.appendChild(gloss);

    var ds = decisionsFor(current);
    panel.appendChild(el("h3", null, t("meaning")));
    if (t("notes_language")) panel.appendChild(el("p", "empty", t("notes_language")));
    if (!ds.meaning.length) panel.appendChild(el("p", "empty", t("no_meaning")));
    ds.meaning.forEach(function (d) { panel.appendChild(drawCard(d, current)); });
    panel.appendChild(el("h3", null, t("rendering").replace("{level}", t(settings.level))));
    if (!ds.rendering.length) panel.appendChild(el("p", "empty", t("no_rendering")));
    ds.rendering.forEach(function (d) { panel.appendChild(drawCard(d, current)); });
  }

  // On narrow screens the panel is a bottom sheet over the text (see .panel
  // in style.css), so opening it never moves the reader's place. The CSS
  // owns the breakpoint: the sheet is the panel when it is position: fixed.
  function narrow() { return getComputedStyle(panelEl).position === "fixed"; }
  function verseEl(v) { return document.querySelector('.verse[data-v="' + v + '"]'); }
  function hashVerse() { var m = /^#v(\d+)$/.exec(location.hash); return m && m[1]; }

  function sheet(open) {
    panelEl.classList.toggle("open", open);
    document.body.classList.toggle("sheet-open", open);
  }

  function select(record, verse) {
    current = record;
    verse = verse || verseOf(record.refs[0]);
    try { history.replaceState(null, "", "#v" + verse); } catch (e) { /* ignore */ }
    drawText();
    drawPanel();
    panelEl.scrollTop = 0;
    sheet(true);
    if (narrow()) {
      var v = verseEl(verse);
      if (v) v.scrollIntoView({ behavior: "smooth", block: "start" });
      // The sheet covers the text below the verse, so take focus into it.
      panelEl.focus({ preventScroll: true });
    }
  }

  function deselect() {
    if (!current) return;
    var verse = hashVerse();
    current = null;
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
    // An Escape that closes a header menu (site.js: the colour menu, a
    // dropdown or the narrow-screen menu) leaves the sheet open.
    var menuOpen = !!document.querySelector('header.site [aria-expanded="true"]');
    if (e.key === "Escape" && !menuOpen && narrow()) deselect();
  });

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
    if (dy > 80) deselect();
  }
  panelEl.addEventListener("touchend", endDrag);
  panelEl.addEventListener("touchcancel", endDrag);

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
        settings[name] = /^\d+$/.test(v) ? Number(v) : v;
        save();
        drawControls();
        drawText();
        drawPanel();
      });
    });
  });

  var start = hashVerse();
  var record = start && DATA.records.find(function (r) {
    return r.refs.some(function (vid) { return verseOf(vid) === start; });
  });
  drawControls();
  if (record) {
    // Opened at a verse on a phone: the verse decides where the page sits,
    // not the browser's scroll restoring (deselect turns it back on), and
    // the jump waits for layout to settle.
    if (narrow()) try { history.scrollRestoration = "manual"; } catch (e) { /* ignore */ }
    select(record, start);
    window.addEventListener("load", function () {
      var v = narrow() && current && verseEl(start);
      if (v) v.scrollIntoView({ block: "start" });
    });
  } else { drawText(); drawPanel(); }
})();
