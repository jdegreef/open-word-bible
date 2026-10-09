// Open Word Bible chapter reader. Data comes from the JSON block the build
// embeds in the page; all text is inserted with textContent.
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("owb-data").textContent);
  var STORE = "owb.settings";

  var LEVEL_HINT = {
    L: "Follows the Greek closely. Words in [brackets] are added for sense.",
    B: "Natural English that tracks the Greek closely. The default.",
    R: "Plain modern English for first-time and young readers."
  };
  var SETTING_HINT = {
    gender: ["Inclusive: \u201call people\u201d where the original means everyone.",
             "Traditional: \u201cmen\u201d, as older translations read."],
    christos: ["\u201cChrist\u201d: the familiar form.",
               "\u201cMessiah\u201d: shows it is a title meaning \u201canointed king\u201d."]
  };
  var CATEGORY = {
    text_variant: "Manuscript reading", punctuation: "Punctuation",
    word_sense: "Word meaning", grammar: "Grammar", allusion: "Echo of other scripture",
    idiom: "Idiom", culture: "Culture and history", theology: "Theology",
    word_choice: "Word choice", word_order: "Word order", register: "Style",
    supplied_words: "Words added for sense", setting_alternative: "Reader setting"
  };
  var LANG_NAME = { en: "English", es: "Spanish" };
  var LEVEL_NAME = { L: "Literal", B: "Balanced", R: "Readable" };

  var settings = { lang: "en", level: "B", gender: 0, christos: 0 };
  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || "{}");
    for (var k in settings) if (k in saved) settings[k] = saved[k];
  } catch (e) { /* storage unavailable: use defaults */ }
  if (!DATA.languages.includes(settings.lang)) settings.lang = DATA.languages[0];

  var current = null;   // selected record
  var SPAN = /\{\{([a-z_]+):([^{}]*)\}\}/g;

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
    document.getElementById("hint-level").textContent = LEVEL_HINT[settings.level];
    document.getElementById("hint-gender").textContent = SETTING_HINT.gender[settings.gender];
    document.getElementById("hint-christos").textContent = SETTING_HINT.christos[settings.christos];
    document.documentElement.lang = settings.lang;
  }

  function drawText() {
    var box = document.getElementById("text");
    box.textContent = "";
    document.getElementById("title").textContent = DATA.title[settings.lang];
    DATA.records.forEach(function (r) {
      var v = r.refs[0].split(".")[2];
      var span = el("span", "verse");
      span.tabIndex = 0;
      span.setAttribute("role", "button");
      span.setAttribute("aria-label", "Verse " + v + ": show the reasoning");
      span.dataset.id = r.id;
      if (current && current.id === r.id) span.setAttribute("aria-current", "true");
      span.appendChild(el("sup", null, v));
      span.appendChild(document.createTextNode(render(r.renderings[settings.lang][settings.level])));
      var ds = decisionsFor(r);
      if (ds.meaning.concat(ds.rendering).some(function (d) { return d.footnote; })) {
        span.appendChild(el("span", "fn", "\u2020"));
      }
      span.addEventListener("click", function () { select(r); });
      span.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(r); }
      });
      box.appendChild(span);
      box.appendChild(document.createTextNode(" "));
    });
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
    var cat = el("div", "cat", CATEGORY[d.category] || d.category);
    if (d.uncertain) cat.appendChild(el("span", "badge unc", "Uncertain"));
    if (d.footnote) cat.appendChild(el("span", "badge", "Footnote"));
    card.appendChild(cat);
    card.appendChild(el("div", "choice", render(d.choice)));
    if (d.alternatives.length) {
      card.appendChild(el("div", "alts", "Also considered: " + d.alternatives.map(render).join("; ")));
    }
    card.appendChild(el("p", "why", d.reason));
    function on() { highlight(d.tokens, card); }
    card.addEventListener("click", on);
    card.addEventListener("focus", on);
    return card;
  }

  function drawPanel() {
    var panel = document.getElementById("panel");
    panel.textContent = "";
    if (!current) {
      panel.appendChild(el("h2", null, "The reasoning behind each verse"));
      panel.appendChild(el("p", "empty",
        "Tap or click any verse to see the Greek, a word-for-word gloss, and every translation decision with its reason."));
      return;
    }
    var v = current.refs[0].split(".")[2];
    panel.appendChild(el("h2", null, DATA.title[settings.lang].replace(/[\d:\u2013\s]+$/, "") + " " + DATA.chapter + ":" + v));
    panel.appendChild(el("span", "status", "AI draft \u00b7 not yet reviewed"));

    panel.appendChild(el("h3", null, "Greek (SBLGNT)"));
    var greek = el("div", "greek");
    greek.lang = "grc";
    var info = el("p", "wordinfo");
    (DATA.words[current.refs[0]] || []).forEach(function (t) {
      var w = el("span", "word", t.text);
      w.dataset.id = t.id;
      w.tabIndex = 0;
      function show() {
        info.textContent = t.lemma + " \u00b7 " + t.morph + " \u00b7 \u201c" + t.gloss + "\u201d";
        var ids = [];
        current.decisions.forEach(function (d) { if (d.tokens.includes(t.id)) ids = ids.concat(d.tokens); });
        highlight(ids.length ? ids : [t.id], null);
      }
      w.addEventListener("click", show);
      w.addEventListener("focus", show);
      greek.appendChild(w);
      greek.appendChild(document.createTextNode(t.after.trim() ? t.after.trim() + " " : " "));
    });
    panel.appendChild(greek);
    panel.appendChild(info);

    panel.appendChild(el("h3", null, "Word for word"));
    panel.appendChild(el("p", "gloss", current.literal_gloss));

    var ds = decisionsFor(current);
    panel.appendChild(el("h3", null, "What the original means"));
    if (!ds.meaning.length) panel.appendChild(el("p", "empty", "No meaning notes for this verse."));
    ds.meaning.forEach(function (d) { panel.appendChild(drawCard(d, current)); });
    panel.appendChild(el("h3", null, "How " + LANG_NAME[settings.lang] + " " + LEVEL_NAME[settings.level] + " says it"));
    if (!ds.rendering.length) panel.appendChild(el("p", "empty", "No wording notes for this level."));
    ds.rendering.forEach(function (d) { panel.appendChild(drawCard(d, current)); });
  }

  function select(record) {
    current = record;
    try { history.replaceState(null, "", "#v" + record.refs[0].split(".")[2]); } catch (e) { /* ignore */ }
    drawText();
    drawPanel();
    if (window.matchMedia("(max-width: 860px)").matches) {
      document.getElementById("panel").scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

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

  var m = /^#v(\d+)$/.exec(location.hash);
  if (m) current = DATA.records.find(function (r) { return r.refs[0].split(".")[2] === m[1]; }) || null;
  drawControls();
  drawText();
  drawPanel();
})();
