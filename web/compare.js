// The comparison page (/compare/, scripts/build_site.py compare_page): one
// verse of ours at its three levels beside public-domain Bibles, and the
// decisions that say why ours reads as it does.
//
// The verse comes from the address (?v=JHN.3.16, or ?ref=John 3:16 from the
// form). Our text and its decisions are read from the verse's chapter page
// (its owb-data), which the reader caches for offline use anyway; the other
// Bibles from /editions/<BOOK>/<chapter>.json. Reader settings (inclusive
// language, Christ or Messiah, ...) are the reader's own, from owb.settings.
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("cmp-data").textContent);
  var UI = DATA.ui;
  var box = document.getElementById("cmp");
  var status = document.getElementById("cmp-status");
  var form = document.getElementById("cmp-form");
  var input = document.getElementById("cmp-ref");
  var heading = document.getElementById("cmp-title");
  var VERSE_ID = /^([1-3]?[A-Z]{2,3})\.(\d+)\.(\d+)$/;
  var LINES = / ?\\q ?/g;

  var settings = { gender: 0, christos: 0, divine_name: 0, deity_pronoun: 0, units: 0, plural_you: 0 };
  try {
    var saved = JSON.parse(localStorage.getItem("owb.settings") || "{}");
    for (var k in settings) if (k in saved) settings[k] = saved[k];
  } catch (e) { /* storage unavailable: the defaults */ }
  function render(text) { return OWBMarkup.render(text, settings).replace(LINES, " "); }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }
  function refName(code, chapter, verse) { return (DATA.books[code] || code) + " " + chapter + ":" + verse; }
  function translated(code, chapter) { return (DATA.chapters[code] || []).indexOf(chapter) >= 0; }
  function chapterPage(code, chapter) { return DATA.chapterUrl + code.toLowerCase() + "/" + chapter + "/"; }

  // "John 3:16", "jn 3.16", "1 Juan 3,16" -> "JHN.3.16" (book names of
  // this language and English, as the reader links them), or a verse id.
  var NAMES = Object.keys(DATA.names).sort(function (a, b) { return b.length - a.length; });
  function parse(q) {
    q = (q || "").trim();
    if (VERSE_ID.test(q)) return q;
    var m = /^(.+?)\s*(\d+)\s*[:.,]\s*(\d+)$/.exec(q);
    if (!m) return null;
    var name = m[1].trim().toLowerCase();
    for (var i = 0; i < NAMES.length; i++) {
      if (NAMES[i].toLowerCase() === name) return DATA.names[NAMES[i]] + "." + Number(m[2]) + "." + Number(m[3]);
    }
    return null;
  }

  var cache = {};
  function getJSON(url) {
    if (!cache[url]) {
      cache[url] = fetch(url).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
      cache[url].catch(function () { delete cache[url]; });
    }
    return cache[url];
  }
  // The reader's data for a chapter, from its page.
  function chapterData(code, chapter) {
    var url = chapterPage(code, chapter);
    if (!cache[url]) {
      cache[url] = fetch(url).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.text();
      }).then(function (page) {
        var m = /<script type="application\/json" id="owb-data">([\s\S]*?)<\/script>/.exec(page);
        if (!m) throw new Error("no data");
        return JSON.parse(m[1].replace(/<\\\//g, "</"));
      });
      cache[url].catch(function () { delete cache[url]; });
    }
    return cache[url];
  }

  // One verse of a record at a level: its part between verse markers. A
  // record's markers follow its refs in order.
  function verseOf(r, lang, level, vid) {
    var text = r.renderings[lang][level];
    var parts = text.split(OWBMarkup.VERSE);
    // split keeps each marker's number: [text, "13", text, ...]
    var texts = [parts[0]];
    for (var i = 2; i < parts.length; i += 2) texts.push(parts[i]);
    var at = r.refs.indexOf(vid);
    return at >= 0 && at < texts.length ? texts[at].trim() : "";
  }

  function section(title, cls) {
    var s = el("section", "cmp-section" + (cls ? " " + cls : ""));
    s.appendChild(el("h2", "label", title));
    return s;
  }
  function row(name, text, lang, extra) {
    var r = el("div", "cmp-row");
    var head = el("p", "cmp-name", name);
    if (extra) head.appendChild(el("span", "cmp-note", extra));
    r.appendChild(head);
    var p = el("p", "cmp-text", text);
    if (lang && lang !== DATA.lang) p.lang = lang;
    r.appendChild(p);
    return r;
  }
  function card(d, level) {
    var c = el("article", "cmp-card");
    var meta = el("p", "cmp-cat", DATA.category[d.category] || d.category);
    if (level) meta.appendChild(el("span", "cmp-levels", " · " + level));
    if (d.uncertain) meta.appendChild(el("span", "badge unc", UI.uncertain));
    c.appendChild(meta);
    c.appendChild(el("h3", "cmp-choice", render(d.choice)));
    if (d.alternatives && d.alternatives.length)
      c.appendChild(el("p", "cmp-also", UI.also + d.alternatives.map(render).join("; ")));
    c.appendChild(el("p", "cmp-reason", render(d.reason)));
    return c;
  }

  // next: the verse id after this one, or null at the end of the book.
  function nav(code, chapter, verse, next) {
    var p = el("p", "cmp-nav");
    function step(label, vid) {
      var a = el("a", "button ghost", label);
      if (vid) a.href = "?v=" + vid; else a.setAttribute("aria-disabled", "true");
      return a;
    }
    p.appendChild(step("← " + UI.prev, verse > 1 ? code + "." + chapter + "." + (verse - 1) : null));
    var read = el("a", "button", UI.read + " →");
    read.href = translated(code, chapter) ? chapterPage(code, chapter) + "#v" + verse : chapterPage(code, chapter);
    if (!translated(code, chapter)) read.hidden = true;
    p.appendChild(read);
    p.appendChild(step(UI.next + " →", next));
    return p;
  }

  function show(vid) {
    var m = VERSE_ID.exec(vid);
    var code = m[1], chapter = Number(m[2]), verse = Number(m[3]);
    var name = refName(code, chapter, verse);
    heading.textContent = UI.title.replace("{ref}", name);
    document.title = heading.textContent + " · Open Word Bible";
    input.value = name;
    box.textContent = "";
    box.setAttribute("aria-busy", "true");
    status.textContent = UI.loading;
    var ours = translated(code, chapter) ? chapterData(code, chapter) : Promise.resolve(null);
    var others = getJSON(DATA.editionsUrl + code + "/" + chapter + ".json").catch(function () { return {}; });
    Promise.all([ours, others]).then(function (got) {
      var data = got[0], editions = got[1];
      var records = data ? data.records.filter(function (r) { return r.refs.indexOf(vid) >= 0; }) : [];
      box.textContent = "";
      if (records.length) {
        var lang = records.every(function (r) { return r.renderings[DATA.lang]; }) ? DATA.lang : "en";
        var mine = section(UI.ours, "cmp-ours");
        if (lang !== DATA.lang) mine.appendChild(el("p", "cmp-note", UI.english));
        ["L", "B", "R"].forEach(function (level) {
          var text = records.map(function (r) { return render(verseOf(r, lang, level, vid)); }).join(" ");
          mine.appendChild(row(DATA.levels[level], text, lang));
        });
        box.appendChild(mine);
      } else {
        box.appendChild(el("p", "notice", UI.not_translated.replace("{ref}", name)));
      }
      var other = section(UI.others, "cmp-others");
      other.appendChild(el("p", "cmp-note", UI.others_note));
      DATA.editions.forEach(function (e) {
        var text = editions[e[0]] && editions[e[0]][String(verse)];
        if (text) other.appendChild(row(e[1], text, e[2]));
      });
      box.appendChild(other);
      if (records.length) {
        var why = section(UI.why, "cmp-why");
        if (DATA.notesLanguage) why.appendChild(el("p", "cmp-note", DATA.notesLanguage));
        var lang2 = records.every(function (r) { return r.renderings[DATA.lang]; }) ? DATA.lang : "en";
        var meaning = [], wording = [];
        records.forEach(function (r) {
          r.decisions.forEach(function (d) {
            if (d.layer === "meaning") meaning.push(d);
            else if (d.language === lang2) wording.push(d);
          });
        });
        if (!meaning.length && !wording.length) why.appendChild(el("p", "cmp-note", UI.none));
        if (meaning.length) {
          why.appendChild(el("h3", "cmp-sub", UI.meaning));
          meaning.forEach(function (d) { why.appendChild(card(d)); });
        }
        if (wording.length) {
          why.appendChild(el("h3", "cmp-sub", UI.wording));
          wording.forEach(function (d) {
            why.appendChild(card(d, (d.levels || []).map(function (l) { return DATA.levels[l]; }).join(", ")));
          });
        }
        box.appendChild(why);
      }
      // The next verse: in this chapter if any Bible here has it, else the
      // next chapter's first.
      var after = code + "." + chapter + "." + (verse + 1);
      var more = DATA.editions.some(function (e) { return editions[e[0]] && editions[e[0]][String(verse + 1)]; }) ||
        (data && data.records.some(function (r) { return r.refs.indexOf(after) >= 0; }));
      var next = more ? after : chapter < (DATA.counts[code] || 0) ? code + "." + (chapter + 1) + ".1" : null;
      box.appendChild(nav(code, chapter, verse, next));
      status.textContent = "";
      box.removeAttribute("aria-busy");
    }).catch(function () {
      box.textContent = "";
      box.appendChild(el("p", "notice", UI.failed));
      status.textContent = UI.failed;
      box.removeAttribute("aria-busy");
    });
  }

  function go(vid, push) {
    if (push) {
      try { history.pushState(null, "", "?v=" + vid); } catch (e) { /* file: */ }
    }
    show(vid);
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var vid = parse(input.value);
    if (!vid) {
      box.textContent = "";
      box.appendChild(el("p", "notice", UI.not_found.replace("{q}", input.value.trim())));
      return;
    }
    go(vid, true);
  });
  window.addEventListener("popstate", start);

  function start() {
    var q = new URLSearchParams(location.search);
    var vid = parse(q.get("v") || q.get("ref") || "") || DATA.start;
    if (q.get("ref") && !q.get("v")) {
      try { history.replaceState(null, "", "?v=" + vid); } catch (e) { /* file: */ }
    }
    show(vid);
  }
  start();
})();
