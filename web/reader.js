// Open Word Bible chapter reader. Data comes from the JSON block the build
// embeds in the page; all text is inserted with textContent.
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("owb-data").textContent);
  var STORE = "owb.settings";

  // Interface text in each reading language. Decision notes are written in
  // English for now; Spanish readers are told so in the panel.
  var UI = {
    en: {
      notice: "Sample passage. Every line is an AI draft that has not yet been checked by a reviewer who reads Greek.",
      sub: "Translated from the SBL Greek New Testament. Tap a verse to see why it reads as it does. \u2020 marks a verse with a footnote.",
      language: "Language", level: "Level", gender: "Gender", title: "Title", pronouns: "Pronouns for God",
      L: "Literal", B: "Balanced", R: "Readable",
      inclusive: "Inclusive", traditional: "Traditional", christ: "Christ", messiah: "Messiah", he: "he", He: "He",
      hint_level: {
        L: "Follows the Greek closely. Words in [brackets] are added for sense.",
        B: "Natural English that tracks the Greek closely. The default.",
        R: "Plain modern English for first-time and young readers."
      },
      hint_gender: ["Inclusive: \u201call people\u201d where the original means everyone.",
                    "Traditional: \u201cmen\u201d, as older translations read."],
      hint_christos: ["\u201cChrist\u201d: the familiar form.",
                      "\u201cMessiah\u201d: shows it is a title meaning \u201canointed king\u201d."],
      hint_deity_pronoun: ["\u201che\u201d: lowercase, like the original, which has no capital letters.",
                           "\u201cHe\u201d: capitalised, as some readers prefer out of reverence."],
      plural: "Plural you", hint_plural_you: ["", ""],
      verse_label: "Verse {v}: show the reasoning",
      empty_title: "The reasoning behind each verse",
      empty_text: "Tap or click any verse to see the Greek, a word-for-word gloss, and every translation decision with its reason.",
      status: "AI draft \u00b7 not yet reviewed",
      greek: "Greek (SBLGNT)", gloss: "Word for word", notes_language: "",
      meaning: "What the original means", rendering: "How English {level} says it",
      no_meaning: "No meaning notes for this verse.", no_rendering: "No wording notes for this level.",
      also: "Also considered: ", uncertain: "Uncertain", footnote: "Footnote",
      category: {
        text_variant: "Manuscript reading", punctuation: "Punctuation",
        word_sense: "Word meaning", grammar: "Grammar", allusion: "Echo of other scripture",
        idiom: "Idiom", culture: "Culture and history", theology: "Theology",
        word_choice: "Word choice", word_order: "Word order", register: "Style",
        supplied_words: "Words added for sense", setting_alternative: "Reader setting"
      }
    },
    es: {
      notice: "Pasaje de muestra. Cada l\u00ednea es un borrador hecho con IA que a\u00fan no ha revisado nadie que lea griego.",
      sub: "Traducido del Nuevo Testamento griego de la SBL. Toca un vers\u00edculo para ver por qu\u00e9 dice lo que dice. \u2020 marca un vers\u00edculo con nota al pie.",
      language: "Idioma", level: "Nivel", gender: "G\u00e9nero", title: "T\u00edtulo", pronouns: "Pronombres para Dios",
      L: "Literal", B: "Equilibrada", R: "Sencilla",
      inclusive: "Inclusivo", traditional: "Tradicional", christ: "Cristo", messiah: "Mes\u00edas", he: "\u00e9l", He: "\u00c9l",
      hint_level: {
        L: "Sigue de cerca el griego. Las palabras entre [corchetes] se a\u00f1aden para dar sentido.",
        B: "Espa\u00f1ol natural que sigue de cerca el griego. La opci\u00f3n predeterminada.",
        R: "Espa\u00f1ol sencillo y actual para quienes leen por primera vez y para j\u00f3venes."
      },
      hint_gender: ["Inclusivo: \u00abtoda la humanidad\u00bb donde el original se refiere a todos.",
                    "Tradicional: \u00ablos hombres\u00bb, como en traducciones antiguas."],
      hint_christos: ["\u00abCristo\u00bb: la forma conocida.",
                      "\u00abMes\u00edas\u00bb: muestra que es un t\u00edtulo que significa \u00abrey ungido\u00bb."],
      hint_deity_pronoun: ["\u00ab\u00e9l\u00bb: en min\u00fascula, como el original, que no tiene may\u00fasculas.",
                           "\u00ab\u00c9l\u00bb: con may\u00fascula, como prefieren algunos lectores por reverencia."],
      plural: "Plural", hint_plural_you: ["\u00abustedes\u00bb: como se habla en Am\u00e9rica Latina.",
                                           "\u00abvosotros\u00bb: como se habla en la mayor parte de Espa\u00f1a."],
      verse_label: "Vers\u00edculo {v}: ver el razonamiento",
      empty_title: "El razonamiento detr\u00e1s de cada vers\u00edculo",
      empty_text: "Toca cualquier vers\u00edculo para ver el griego, una glosa palabra por palabra y cada decisi\u00f3n de traducci\u00f3n con su raz\u00f3n.",
      status: "Borrador de IA \u00b7 a\u00fan sin revisar",
      greek: "Griego (SBLGNT)", gloss: "Palabra por palabra (en ingl\u00e9s)",
      notes_language: "Por ahora, las notas est\u00e1n en ingl\u00e9s.",
      meaning: "Lo que significa el original", rendering: "C\u00f3mo lo dice la versi\u00f3n {level} en espa\u00f1ol",
      no_meaning: "No hay notas de significado para este vers\u00edculo.", no_rendering: "No hay notas de redacci\u00f3n para este nivel.",
      also: "Tambi\u00e9n se consider\u00f3: ", uncertain: "Incierto", footnote: "Nota al pie",
      category: {
        text_variant: "Lectura de manuscritos", punctuation: "Puntuaci\u00f3n",
        word_sense: "Significado de la palabra", grammar: "Gram\u00e1tica", allusion: "Eco de otra escritura",
        idiom: "Modismo", culture: "Cultura e historia", theology: "Teolog\u00eda",
        word_choice: "Elecci\u00f3n de palabras", word_order: "Orden de las palabras", register: "Estilo",
        supplied_words: "Palabras a\u00f1adidas para dar sentido", setting_alternative: "Ajuste del lector"
      }
    }
  };

  function t(key) { return UI[settings.lang][key]; }

  var settings = { lang: "en", level: "B", gender: 0, christos: 0, deity_pronoun: 0, plural_you: 0 };
  try {
    var saved = JSON.parse(localStorage.getItem(STORE) || "{}");
    for (var k in settings) if (k in saved) settings[k] = saved[k];
  } catch (e) { /* storage unavailable: use defaults */ }
  if (!DATA.languages.includes(settings.lang)) settings.lang = DATA.languages[0];

  var current = null;   // selected record
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
    document.querySelectorAll("[data-i18n]").forEach(function (n) {
      n.textContent = t(n.getAttribute("data-i18n"));
    });
    document.getElementById("hint-level").textContent = t("hint_level")[settings.level];
    document.querySelectorAll("[data-only-lang]").forEach(function (n) {
      n.hidden = n.getAttribute("data-only-lang") !== settings.lang;
    });
    ["gender", "christos", "deity_pronoun", "plural_you"].forEach(function (name) {
      document.getElementById("hint-" + name).textContent = t("hint_" + name)[settings[name]];
    });
    document.documentElement.lang = settings.lang;
  }

  function drawText() {
    var box = document.getElementById("text");
    box.textContent = "";
    document.getElementById("title").textContent = DATA.title[settings.lang];
    var shown = null;   // last verse number printed
    DATA.records.forEach(function (r) {
      var ds = decisionsFor(r);
      var hasNote = ds.meaning.concat(ds.rendering).some(function (d) { return d.footnote; });
      var parts = splitVerses(r, render(r.renderings[settings.lang][settings.level]));
      parts.forEach(function (part, i) {
        var span = el("span", "verse");
        span.tabIndex = 0;
        span.setAttribute("role", "button");
        span.setAttribute("aria-label", t("verse_label").replace("{v}", part[0]));
        if (current && current.id === r.id) span.setAttribute("aria-current", "true");
        if (part[0] !== shown) span.appendChild(el("sup", null, part[0]));
        shown = part[0];
        span.appendChild(document.createTextNode(part[1]));
        if (hasNote && i === parts.length - 1) span.appendChild(el("span", "fn", "\u2020"));
        span.addEventListener("click", function () { select(r, part[0]); });
        span.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(r, part[0]); }
        });
        box.appendChild(span);
        box.appendChild(document.createTextNode(" "));
      });
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
    var panel = document.getElementById("panel");
    panel.textContent = "";
    if (!current) {
      panel.appendChild(el("h2", null, t("empty_title")));
      panel.appendChild(el("p", "empty", t("empty_text")));
      return;
    }
    panel.appendChild(el("h2", null, DATA.title[settings.lang].replace(/[\d:\u2013\s]+$/, "") + " " + DATA.chapter + ":" + verseRange(current)));
    panel.appendChild(el("span", "status", t("status")));

    panel.appendChild(el("h3", null, t("greek")));
    var greek = el("div", "greek");
    greek.lang = "grc";
    var info = el("p", "wordinfo");
    function drawWord(t) {
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
    }
    var mine = new Set(current.source.tokens);
    current.refs.forEach(function (vid, i) {
      if (i > 0) greek.appendChild(el("sup", null, verseOf(vid)));
      (DATA.words[vid] || []).filter(function (w) { return mine.has(w.id); }).forEach(drawWord);
    });
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

  function select(record, verse) {
    current = record;
    try { history.replaceState(null, "", "#v" + (verse || verseOf(record.refs[0]))); } catch (e) { /* ignore */ }
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
  if (m) current = DATA.records.find(function (r) {
    return r.refs.some(function (vid) { return verseOf(vid) === m[1]; });
  }) || null;
  drawControls();
  drawText();
  drawPanel();
})();
