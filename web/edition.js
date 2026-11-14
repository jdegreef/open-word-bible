// The reader's edition (/<book>/read/, scripts/build_site.py edition_page):
// a whole book as one continuous text, set like a printed book, with no
// verse numbers, headings, footnotes or notes. Each chapter's verses come
// from /verses/<BOOK>/<chapter>.json (build_site.py verse_files) as the
// reader comes near it. The level and the wording settings are the
// reader's own (owb.settings, web/reader.js); the level can be changed here.
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("edition-data").textContent);
  var STORE = "owb.settings";
  var LINES = / ?\\q ?/;
  var VERSE = / ?\\v \d+ ?/g;

  function saved() {
    try { return OWBMarkup.fromSaved(JSON.parse(localStorage.getItem(STORE) || "{}")); } catch (e) { return {}; }
  }
  var settings = OWBMarkup.defaults();
  settings.level = "B";
  (function () {
    var s = saved();
    for (var k in s) settings[k] = s[k];
    if (!/^[LBR]$/.test(settings.level)) settings.level = "B";
  })();

  // A changed level is saved with the reader's other settings, so the
  // chapter pages open at it too (and site.js syncs it to the account).
  function saveLevel() {
    try {
      var s = saved();
      s.level = settings.level;
      s.v = OWBMarkup.SETTINGS_VERSION;
      s.at = Date.now();
      localStorage.setItem(STORE, JSON.stringify(s));
    } catch (e) { /* storage unavailable: this visit only */ }
    document.dispatchEvent(new Event("owb:settings"));
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  // One verse in the page's language at the reader's level, or in English
  // while it has none yet (as the reader shows it, in grey).
  function verseText(langs) {
    var own = langs[DATA.lang], en = langs.en;
    var pick = own && (own[settings.level] || own.B), lang = DATA.lang;
    if (!pick && en) { pick = en[settings.level] || en.B; lang = "en"; }
    if (!pick) return null;
    return { text: OWBMarkup.render(pick, settings).replace(VERSE, " "), lang: lang };
  }

  // A verse is set as poetry when its sentence is set in lines in the
  // language shown. The verse file lists those verses per language ("q",
  // build_site.py verse_files), so a song inside a prose chapter (Luke 1,
  // Exodus 15) is set in lines and the narrative around it stays prose.
  // A file without the list (cached from an older build) falls back to the
  // verse's own text.
  function poeticVerse(entry, n, levels, lang) {
    if (entry.q) return (entry.q[lang] || []).indexOf(n) >= 0;
    return Object.keys(levels || {}).some(function (l) { return LINES.test(levels[l]); });
  }

  var cache = {};

  function draw(section, entry) {
    var chapter = Number(section.getAttribute("data-chapter"));
    var verses = Object.keys(entry.v).map(function (n) { return [Number(n), entry.v[n]]; })
      .sort(function (a, b) { return a[0] - b[0]; });
    var starts = {};
    (entry.p || []).forEach(function (n) { starts[n] = true; });
    var body = el("div", "ed-body");
    var para = null, first = true, wasPoem = false;
    verses.forEach(function (v) {
      var t = verseText(v[1]);
      if (!t) return;
      var poem = poeticVerse(entry, v[0], v[1][t.lang], t.lang);
      if (poem || wasPoem || !para || starts[v[0]]) {
        // Poetry: each verse its own lines, a gap where a paragraph starts
        // and where poetry and prose meet.
        para = el("p", poem ? "ed-pp" + (starts[v[0]] && !first ? " ed-stanza" : "")
                            : (wasPoem ? "ed-after" : null));
        body.appendChild(para);
      } else {
        para.appendChild(document.createTextNode(" "));
      }
      if (first) {
        // The chapter number as a printed Bible sets it, beside the first
        // line; above it when the chapter opens in poetry.
        if (poem) body.classList.add("ed-poem");
        var num = el("span", "ed-num", String(chapter));
        num.setAttribute("aria-hidden", "true");
        para.appendChild(num);
        first = false;
      }
      var span = el("span", t.lang !== DATA.lang ? "ed-fallback" : null);
      if (t.lang !== DATA.lang) { span.lang = t.lang; span.title = DATA.fallback; }
      t.text.split(LINES).forEach(function (line, i) {
        // A poetic line that wraps hangs under its start, as printed psalms do.
        if (poem) span.appendChild(el("span", "ed-line", line));
        else span.appendChild(document.createTextNode((i ? " " : "") + line));
      });
      para.appendChild(span);
      wasPoem = poem;
    });
    var old = section.querySelector(".ed-body, .ed-loading");
    if (old) section.replaceChild(body, old); else section.appendChild(body);
    section.setAttribute("data-drawn", "");
  }

  function load(section) {
    if (section.hasAttribute("data-loading")) return;
    var chapter = section.getAttribute("data-chapter");
    if (cache[chapter]) { draw(section, cache[chapter]); return; }
    section.setAttribute("data-loading", "");
    fetch(DATA.verses + DATA.book + "/" + chapter + ".json")
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (entry) { cache[chapter] = entry; draw(section, entry); })
      .catch(function () {
        var note = section.querySelector(".ed-loading");
        if (note) note.textContent = DATA.failed;
        section.removeAttribute("data-drawn");
      })
      .then(function () { section.removeAttribute("data-loading"); });
  }

  var sections = Array.prototype.slice.call(document.querySelectorAll(".ed-chapter"));
  // A chapter loads well before it scrolls into view, so reading on finds
  // the next one already there; a chapter that failed tries again when the
  // reader comes back to it.
  if ("IntersectionObserver" in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !e.target.hasAttribute("data-drawn")) load(e.target);
      });
    }, { rootMargin: "1500px 0px" });
    sections.forEach(function (s) { seen.observe(s); });
  } else {
    sections.forEach(load);
  }

  // A link to #c5 opens at chapter 5: load it first, then go there.
  var target = location.hash && document.getElementById(location.hash.slice(1));
  if (target && target.classList.contains("ed-chapter")) {
    load(target);
    target.scrollIntoView();
  }

  var levelButtons = document.querySelectorAll("[data-level]");
  function drawLevel() {
    levelButtons.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-level") === settings.level ? "true" : "false");
    });
  }
  levelButtons.forEach(function (b) {
    b.addEventListener("click", function () {
      settings.level = b.getAttribute("data-level");
      saveLevel();
      drawLevel();
      sections.forEach(function (s) {
        var c = s.getAttribute("data-chapter");
        if (cache[c]) draw(s, cache[c]);
      });
    });
  });
  drawLevel();
})();
