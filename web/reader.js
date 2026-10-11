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
  var settings = { level: "B", gender: 0, christos: 0, divine_name: 0, deity_pronoun: 0, units: 0, plural_you: 0, view: 0, headings: 0 };
  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || "{}");
    for (var k in settings) if (k in saved) settings[k] = saved[k];
  } catch (e) { /* storage unavailable: use defaults */ }
  settings.lang = DATA.lang;

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
    // Christ (New Testament), and measures only where it has them, so
    // some hints are missing.
    ["gender", "christos", "divine_name", "deity_pronoun", "units", "plural_you", "view", "headings"].forEach(function (name) {
      var hint = document.getElementById("hint-" + name);
      if (hint) hint.textContent = t("hint_" + name)[settings[name]];
    });
    // The summary on the phone settings button: each shown choice's label.
    var summary = [];
    // "Show" or "Hide" means nothing without its label, so headings are left out.
    document.querySelectorAll(".control:not([hidden]) .seg:not([data-setting=headings])").forEach(function (seg) {
      var on = seg.querySelector('[aria-pressed="true"]');
      if (on && seg.children.length > 1) summary.push(on.textContent);
    });
    document.getElementById("settings-summary").textContent = summary.join(" \u00b7 ");
    document.body.classList.toggle("plain", plain());
  }

  // The headings control only where the chapter has headings.
  var headingsSeg = document.querySelector('[data-setting="headings"]');
  if (headingsSeg && !Object.keys(DATA.headings).length) headingsSeg.parentNode.hidden = true;

  // Reading view: the text alone, without verse numbers, footnote letters or
  // the reasoning panel; verses are not buttons.
  function plain() { return settings.view === 1; }

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
    box.appendChild(el("p", "fn-pop-text", noteText(n.decision)));
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
    var shown = null;   // last verse number printed
    var notes = [];
    var starts = new Set(DATA.paragraphs);
    var para = null;    // the paragraph being filled
    DATA.records.forEach(function (r) {
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
      var chosen = current && current.id === r.id;
      parts.forEach(function (part, i) {
        var span = el("span", lang === settings.lang ? "verse" : "verse fallback");
        if (lang !== settings.lang) span.lang = lang;
        if (!plain()) {
          span.tabIndex = 0;
          span.setAttribute("role", "button");
          span.setAttribute("aria-label", t("verse_label").replace("{v}", part[0]));
        }
        span.dataset.v = part[0];
        span.dataset.record = r.id;
        if (current && current.id === r.id) span.setAttribute("aria-current", "true");
        if (part[0] !== shown) span.appendChild(el("sup", null, part[0]));
        shown = part[0];
        part[1].forEach(function (piece) {
          var text = render(piece[0]);
          if (!piece[1]) { span.appendChild(document.createTextNode(text)); return; }
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
    drawNotes(notes);
    if (listen.on) mark(false);
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
    document.querySelectorAll(".aw").forEach(function (a) {
      a.classList.toggle("on", a.dataset.tokens.split(" ").some(function (id) { return set.has(id); }));
    });
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
    card.appendChild(el("p", "why", d.reason));
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
      var link = location.origin + location.pathname + "#v" + verse;
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

  // The reader's place, kept as owb.place for "Continue reading" on the
  // home and Read pages (site.js): the verse at the reading line, a quarter
  // of the way down or just below the sticky header and settings bar (a
  // verse's scroll margin) if that is lower. Saving and resuming both use
  // the line, so a place does not drift.
  function readingLine() {
    var first = document.querySelector("#text .verse");
    var margin = first ? parseFloat(getComputedStyle(first).scrollMarginTop) || 0 : 0;
    return Math.max(margin, window.innerHeight * 0.25);
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
    var place = { book: DATA.book, chapter: DATA.chapter, verse: verse };
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
    var rest = render(r.renderings[lang][settings.level]).replace(new RegExp(VERSE.source, "g"), "").replace(/\s+/g, " ").trim();
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
