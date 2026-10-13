// Search, as Ochorus has it: a palette that Ctrl K or Cmd K (or "/") opens
// on any page, the /search/ page, and the query's words marked in a passage
// opened from a result. The site is static, so the search runs here, over
// the index the build writes for the page's language (search_index in
// scripts/build_site.py; its address is in <meta name="owb-search">). All
// text is inserted with textContent.
(function () {
  "use strict";
  var meta = document.querySelector('meta[name="owb-search"]');
  if (!meta) return;
  var INDEX_URL = meta.getAttribute("content");
  var RECENT = "owb.searches";
  var MIN = 2;
  var SPAN = /\{\{([a-z_]+):([^{}]*)\}\}/g;
  var VERSE = /\\v (\d+) ?/;
  var GROUPS = ["c", "v", "n", "a"];
  // In the "All" view, how many of each kind show before "Show all".
  var CAPS = { c: 6, v: 8, n: 5, a: 4 };
  var PAGE = 20;
  var LEVELS = ["B", "L", "R"];
  var WORD = /[\p{L}\p{N}]/u;

  // ---- Text --------------------------------------------------------------

  // Lower case, accents removed, curly quotes straightened: what matching
  // compares, so "corazon" finds "corazón".
  function fold(s) {
    return s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
      .replace(/[\u2018\u2019\u02bc]/g, "'").replace(/[\u201c\u201d\u00ab\u00bb]/g, '"');
  }

  // s folded, with where each folded character came from, so a match in
  // the folded text can be marked in the original.
  function foldMap(s) {
    var out = "", start = [], end = [], i = 0;
    for (var ch of s) {
      var f = fold(ch);
      for (var j = 0; j < f.length; j++) { start.push(i); end.push(i + ch.length); }
      out += f;
      i += ch.length;
    }
    return { text: out, start: start, end: end };
  }

  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  // The query's terms: "quoted phrases" whole, other words one by one. A
  // term matches at the start of a word, so "love" finds "loved".
  function parse(q) {
    var terms = [], m, re = /"([^"]+)"|(\S+)/g, f = fold(q);
    while ((m = re.exec(f))) {
      var parts = m[1] ? [m[1].trim()] : m[2].split(/[^\p{L}\p{N}']+/u);
      parts.forEach(function (p) {
        p = p.replace(/^'+|'+$/g, "");
        if (p && terms.indexOf(p) < 0) terms.push(p);
      });
    }
    return terms.map(function (t) {
      return { text: t, re: new RegExp("(^|[^\\p{L}\\p{N}])(" + escapeRe(t).replace(/ +/g, "\\s+") + ")", "gu") };
    });
  }

  // Where term matches in folded text: [[from, to], ...], at most max.
  function matches(term, text, max) {
    var out = [], m;
    term.re.lastIndex = 0;
    while ((m = term.re.exec(text)) && out.length < (max || 1000)) {
      var from = m.index + m[1].length;
      out.push([from, from + m[2].length]);
      if (m[0].length === 0) term.re.lastIndex++;
    }
    return out;
  }

  function has(term, text) { return matches(term, text, 1).length > 0; }

  // Append text to el with the terms' matches in <mark>.
  function marked(el, text, terms) {
    var map = foldMap(text), ranges = [];
    terms.forEach(function (t) { ranges = ranges.concat(matches(t, map.text)); });
    ranges.sort(function (a, b) { return a[0] - b[0]; });
    var at = 0;
    ranges.forEach(function (r) {
      var from = map.start[r[0]], to = map.end[r[1] - 1];
      if (from < at) return;
      if (from > at) el.appendChild(document.createTextNode(text.slice(at, from)));
      var m = document.createElement("mark");
      m.textContent = text.slice(from, to);
      el.appendChild(m);
      at = to;
    });
    if (at < text.length) el.appendChild(document.createTextNode(text.slice(at)));
    return el;
  }

  // About radius characters of text either side of the first match, cut at
  // word breaks, with "…" where it was cut.
  function excerpt(text, terms, radius) {
    radius = radius || 110;
    if (text.length <= radius * 2) return text;
    var map = foldMap(text), first = Infinity;
    terms.forEach(function (t) {
      var m = matches(t, map.text, 1)[0];
      if (m && map.start[m[0]] < first) first = map.start[m[0]];
    });
    if (first === Infinity) first = 0;
    var from = Math.max(0, first - radius), to = Math.min(text.length, first + radius);
    if (from > 0) { var sp = text.indexOf(" ", from); if (sp > 0 && sp < first) from = sp + 1; }
    if (to < text.length) { var e = text.lastIndexOf(" ", to); if (e > first) to = e; }
    return (from > 0 ? "\u2026" : "") + text.slice(from, to).trim() + (to < text.length ? "\u2026" : "");
  }

  function fill(s, values) {
    return s.replace(/\{(\w+)\}/g, function (_, k) { return k in values ? values[k] : "{" + k + "}"; });
  }

  // ---- Reader settings ---------------------------------------------------

  // The reader's settings (web/reader.js keeps them as owb.settings), so a
  // verse reads here as it does in the reader.
  function settings() {
    var s = { level: "B" };
    try {
      var saved = JSON.parse(localStorage.getItem("owb.settings") || "{}");
      for (var k in saved) s[k] = saved[k];
    } catch (e) { /* defaults */ }
    if (LEVELS.indexOf(s.level) < 0) s.level = "B";
    return s;
  }

  // Rendering text with each {{setting:a|b}} span at the reader's choice,
  // or at the option the query found when that is another one.
  function render(text, set, terms) {
    return text.replace(SPAN, function (_, name, opts) {
      var options = opts.split("|"), i = set[name];
      var pick = typeof i === "number" && i >= 0 && i < options.length ? options[i] : options[0];
      if (terms && !terms.some(function (t) { return has(t, fold(pick)); })) {
        var other = options.filter(function (o) { return terms.some(function (t) { return has(t, fold(o)); }); })[0];
        if (other) pick = other;
      }
      return pick;
    });
  }

  // Every word a sentence can show: all levels, every option of each span.
  function everything(levels) {
    return Object.keys(levels).map(function (l) {
      return levels[l].replace(SPAN, function (_, n, opts) { return opts.split("|").join(" "); })
        .replace(/\\v \d+ ?/g, " ").replace(/ ?\\q ?/g, " ");
    }).join(" \u2016 ");
  }

  // [[verse, text], ...] for rendered text with \v markers.
  function verses(first, text) {
    // The build already turns poetic line markers (\q) into spaces; this
    // keeps an index built before that from showing them.
    var parts = text.replace(/ ?\\q ?/g, " ").split(VERSE), out = [[first, parts[0].trim()]];
    for (var i = 1; i < parts.length; i += 2) out.push([Number(parts[i]), parts[i + 1].trim()]);
    return out;
  }

  // ---- The index ---------------------------------------------------------

  var loading = null, INDEX = null;

  function load() {
    if (!loading) {
      loading = fetch(INDEX_URL, { credentials: "same-origin" })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(prepare)
        .catch(function (e) { loading = null; throw e; });
    }
    return loading;
  }

  // Each document's searchable fields, folded once, with their weights.
  function prepare(data) {
    data.names = {};
    data.books.forEach(function (b) { data.names[b.code] = b.name; });
    data.docs.forEach(function (d, i) {
      d.i = i;
      if (d.k === "c") d.f = [[fold(d.h), 4]];
      else if (d.k === "v") d.f = [[fold(everything(d.x)), 1]];
      else if (d.k === "n") d.f = [[fold(d.t), 2.5], [fold(d.al.join(" \u2016 ")), 1.5], [fold(d.s), 1]];
      else d.f = [[fold(d.t), 3], [fold(d.s), 1.5], [fold(d.x), 0.5]];
    });
    INDEX = data;
    return data;
  }

  function ui(key) { return INDEX.ui[key]; }

  function refLabel(d, verse) {
    return INDEX.names[d.bk] + " " + d.c + (verse ? ":" + verse : "");
  }

  // Every document that has every term, best first: matches in a title
  // count for more, and a whole word for more than the start of one.
  function find(terms) {
    var hits = [];
    INDEX.docs.forEach(function (d) {
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var got = 0;
        d.f.forEach(function (field) {
          var ms = matches(terms[i], field[0], 5);
          ms.forEach(function (m) {
            var whole = m[1] >= field[0].length || !WORD.test(field[0].charAt(m[1]));
            got += field[1] * (whole ? 1.5 : 1);
          });
        });
        if (!got) return;
        score += got;
      }
      hits.push({ doc: d, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score || a.doc.i - b.doc.i; });
    return hits;
  }

  // "John 3:16", "jn 3 16", "Filipenses 4:7-9", "1 John 2": a passage.
  function reference(q) {
    var m = /^\s*(.+?)\.?\s*(\d+)(?:\s*[:.,\s]\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?)?\s*$/.exec(fold(q));
    if (!m) return null;
    var key = m[1].replace(/[\s.]+/g, "");
    if (!key || /^\d+$/.test(key)) return null;
    var book = INDEX.books.filter(function (b) { return b.aliases.indexOf(key) >= 0; })[0];
    var chapter = Number(m[2]), verse = m[3] ? Number(m[3]) : null;
    // The start of a name ("phil") counts only for a book with passages, or
    // with a verse given, so "son 3" stays a search for words.
    if (!book && key.replace(/^\d/, "").length >= 3) {
      book = INDEX.books.filter(function (b) {
        return (b.chapters || verse) && b.aliases.some(function (a) { return a.indexOf(key) === 0; });
      })[0];
    }
    if (!book) return null;
    var end = m[4] ? Math.max(Number(m[4]), verse) : verse;
    var label = book.name + " " + chapter + (verse ? ":" + verse + (end !== verse ? "\u2013" + end : "") : "");
    var ch = book.chapters && book.chapters[chapter];
    var ref = { book: book, chapter: chapter, verse: verse, end: end, label: label, chapterInfo: ch,
                chapterLabel: book.name + " " + chapter };
    if (ch) {
      ref.shown = verse ? ch.verses.filter(function (v) { return v >= verse && v <= end; }) : [];
      ref.url = ch.url + (ref.shown.length ? "#v" + ref.shown[0] : "");
    }
    return ref;
  }

  // A reference's verses, as the reader's settings show them (at most 6).
  function refVerses(ref) {
    var set = settings(), out = [];
    INDEX.docs.forEach(function (d) {
      if (d.k !== "v" || d.bk !== ref.book.code || d.c !== ref.chapter) return;
      if (!d.vv.some(function (v) { return ref.shown.indexOf(v) >= 0; })) return;
      verses(d.v, render(d.x[set.level] || d.x.B, set)).forEach(function (pair) {
        if (ref.shown.indexOf(pair[0]) >= 0 && out.length < 6) out.push({ verse: pair[0], text: pair[1], lang: d.l });
      });
    });
    return out;
  }

  // ---- Hits as rows --------------------------------------------------------

  // What a result shows, whichever list it is in: kind, title, a line
  // about it, a snippet, and where it goes.
  function row(hit, terms, q) {
    var d = hit.doc, qs = "?q=" + encodeURIComponent(q);
    if (d.k === "c") return { kind: "c", title: d.t, meta: d.s, href: d.u };
    if (d.k === "v") {
      var set = settings(), order = [set.level].concat(LEVELS.filter(function (l) { return l !== set.level; }));
      // The reader's level, unless only another level has the words.
      var shown = order.map(function (level) {
        var text = render(d.x[level], set, terms), f = fold(text);
        return { level: level, text: text,
                 all: terms.every(function (t) { return has(t, f); }),
                 any: terms.some(function (t) { return has(t, f); }) };
      });
      var best = shown.filter(function (c) { return c.all; })[0]
        || shown.filter(function (c) { return c.any; })[0] || shown[0];
      var parts = verses(d.v, best.text);
      var at = parts.filter(function (p) { return terms.some(function (t) { return has(t, fold(p[1])); }); })[0] || parts[0];
      var meta = best.level !== set.level ? ui("levels")[best.level] : "";
      if (d.l) meta = (meta ? meta + " \u00b7 " : "") + ui("english");
      return { kind: "v", title: refLabel(d, at[0]), meta: meta, snippet: excerpt(at[1], terms, 140),
               href: d.u + qs + "#v" + at[0], lang: d.l, serif: true };
    }
    if (d.k === "n") {
      var label = ui(d.y === "meaning" ? "meaning" : "rendering") + " \u00b7 " + (ui("category")[d.g] || d.g);
      var also = terms.some(function (t) { return has(t, fold(d.al.join(" "))); }) && d.al.length
        ? ui("also") + d.al.join("; ") : "";
      return { kind: "n", title: d.t, eyebrow: refLabel(d, d.v), meta: label,
               snippet: excerpt(d.s, terms), extra: also, href: d.u + qs + "#v" + d.v, lang: d.l };
    }
    var inBody = !terms.every(function (t) { return has(t, d.f[0][0]) || has(t, d.f[1][0]); });
    return { kind: "a", title: d.t, eyebrow: d.sec, snippet: inBody ? excerpt(d.x, terms) : d.s,
             href: d.u, lang: d.l };
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  // ---- Recent searches -------------------------------------------------

  function recent() {
    try {
      var list = JSON.parse(localStorage.getItem(RECENT) || "[]");
      return Array.isArray(list) ? list.filter(function (s) { return typeof s === "string"; }) : [];
    } catch (e) { return []; }
  }

  function remember(q) {
    q = (q || "").trim();
    if (q.length < MIN) return;
    var list = recent().filter(function (s) { return fold(s) !== fold(q); });
    list.unshift(q);
    try { localStorage.setItem(RECENT, JSON.stringify(list.slice(0, 6))); } catch (e) { /* this visit only */ }
  }

  function forget(q) {
    var list = q == null ? [] : recent().filter(function (s) { return s !== q; });
    try { localStorage.setItem(RECENT, JSON.stringify(list)); } catch (e) { /* ignore */ }
  }

  function searchUrl(base, q) {
    return base + (q ? "?q=" + encodeURIComponent(q).replace(/%20/g, "+") : "");
  }

  var paletteForm = document.querySelector(".palette-form");
  var SEARCH_BASE = paletteForm ? paletteForm.getAttribute("action") : "/search/";
  var onSearchPage = !!document.getElementById("search-q");

  // ---- The palette -----------------------------------------------------

  (function () {
    var box = document.getElementById("palette");
    var input = document.getElementById("palette-q");
    var list = document.getElementById("palette-list");
    var button = document.querySelector(".search-btn");
    if (!box || !input) return;
    var rows = [], active = 0, opener = null, seq = 0, timer = null;

    var kbd = button && button.querySelector(".search-kbd");
    if (kbd) {
      kbd.textContent = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent) ? "\u2318K" : "Ctrl K";
      kbd.hidden = false;
    }

    function option(r, i) {
      var li = el("li");
      li.setAttribute("role", "option");
      li.id = "pal-" + i;
      var a = el("a", "pal-row" + (r.all ? " pal-all" : ""));
      a.href = r.href;
      a.tabIndex = -1;
      a.appendChild(el("span", "pal-kind", r.kindLabel));
      var text = el("span", "pal-text");
      var title = el("span", "pal-title");
      if (r.terms) marked(title, r.title, r.terms); else title.textContent = r.title;
      text.appendChild(title);
      if (r.snippet) {
        var sn = el("span", "pal-meta" + (r.serif ? " serif" : ""));
        if (r.lang) sn.lang = r.lang;
        marked(sn, r.snippet, r.terms || []);
        text.appendChild(sn);
      }
      a.appendChild(text);
      // A link within this page (/#help on the home page) does not unload it.
      a.addEventListener("click", function () { remember(input.value); close(); });
      li.appendChild(a);
      return li;
    }

    function draw() {
      list.textContent = "";
      rows.forEach(function (r, i) { list.appendChild(option(r, i)); });
      if (!rows.length) list.appendChild(el("li", "pal-empty", INDEX ? ui("no_matches") : ""));
      mark();
    }

    function mark() {
      Array.prototype.forEach.call(list.children, function (li, i) {
        li.setAttribute("aria-selected", i === active ? "true" : "false");
        if (i === active) li.scrollIntoView({ block: "nearest" });
      });
      if (rows[active]) input.setAttribute("aria-activedescendant", "pal-" + active);
      else input.removeAttribute("aria-activedescendant");
    }

    function pages(q) {
      var f = fold(q);
      return INDEX.pages.filter(function (p) { return !f || fold(p[0]).indexOf(f) >= 0; })
        .map(function (p) { return { kindLabel: ui("kind").g, title: p[0], href: p[1] }; });
    }

    function update() {
      var q = input.value.trim(), mine = ++seq;
      load().then(function () {
        if (mine !== seq) return;
        rows = [];
        if (q.length >= MIN) {
          var terms = parse(q), ref = reference(q);
          // A reference ("John 3:16") comes first, so Enter goes to it.
          if (ref && ref.url) {
            rows.push(ref.shown.length
              ? { kindLabel: ui("kind").v, title: fill(ui("go_to"), { ref: ref.label }), href: ref.url }
              : { kindLabel: ui("kind").c, title: fill(ui("read_passage"), { ref: ref.chapterLabel }), href: ref.url });
          }
          rows.push({ all: true, kindLabel: "\u21b5", title: fill(ui("show_all"), { q: q }), href: searchUrl(SEARCH_BASE, q) });
          rows = rows.concat(pages(q));
          // The best few of each kind, in a fixed order: passages, verses,
          // notes, articles. A reference is answered by its own row: its
          // numbers would otherwise match any note that mentions a 3 and a 16.
          var hits = terms.length && !ref ? find(terms) : [], few = { c: 2, v: 3, n: 2, a: 2 };
          var add = function (h) {
            var r = row(h, terms, q);
            rows.push({ kindLabel: ui("kind")[r.kind], title: r.title, snippet: r.kind === "c" ? r.meta : r.snippet,
                        href: r.href, terms: terms, lang: r.lang, serif: r.serif });
          };
          GROUPS.forEach(function (g) {
            hits.filter(function (h) { return h.doc.k === g; }).slice(0, few[g]).forEach(add);
          });
        } else {
          rows = pages("");
        }
        active = 0;
        draw();
      }, function () {
        if (mine !== seq) return;
        // The index did not load: Enter still goes to the search page.
        rows = q ? [{ all: true, kindLabel: "\u21b5", title: q, href: searchUrl(SEARCH_BASE, q) }] : [];
        draw();
      });
    }

    function open() {
      if (!box.hidden) return;
      opener = document.activeElement;
      box.hidden = false;
      document.documentElement.classList.add("palette-open");
      input.value = "";
      rows = [];
      list.textContent = "";
      input.focus();
      update();
    }

    function close() {
      if (box.hidden) return;
      box.hidden = true;
      document.documentElement.classList.remove("palette-open");
      if (opener && opener.focus) opener.focus();
    }

    function go(r) {
      if (!r) return;
      remember(input.value);
      close();
      location.href = r.href;
    }

    input.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(update, 120);
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (!rows.length) return;
        active = (active + (e.key === "ArrowDown" ? 1 : -1) + rows.length) % rows.length;
        mark();
      } else if (e.key === "Enter") {
        e.preventDefault();
        var q = input.value.trim();
        if (rows[active]) go(rows[active]);
        else if (q.length >= MIN) go({ href: searchUrl(SEARCH_BASE, q) });
      } else if (e.key === "Tab") {
        e.preventDefault();
      }
    });
    box.addEventListener("click", function (e) { if (e.target === box) close(); });
    box.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); }
    });

    function typing(t) {
      return t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
    }

    document.addEventListener("keydown", function (e) {
      var k = (e.key || "").toLowerCase();
      if ((e.metaKey || e.ctrlKey) && !e.altKey && !e.shiftKey && k === "k") {
        e.preventDefault();
        if (onSearchPage) { close(); var q = document.getElementById("search-q"); q.focus(); q.select(); }
        else if (box.hidden) open(); else close();
      } else if (k === "/" && !e.metaKey && !e.ctrlKey && !e.altKey && !typing(e.target) && box.hidden) {
        e.preventDefault();
        if (onSearchPage) document.getElementById("search-q").focus(); else open();
      }
    });
    // The reader's "Go to" button opens the palette too.
    document.querySelectorAll("[data-open-search]").forEach(function (b) {
      b.addEventListener("click", function () { open(); });
      b.addEventListener("pointerenter", function () { load().catch(function () {}); }, { once: true });
    });
    if (button) {
      button.addEventListener("click", function (e) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
        e.preventDefault();
        if (onSearchPage) document.getElementById("search-q").focus(); else open();
      });
      // Fetch the index as soon as the reader shows an interest.
      ["pointerenter", "focus"].forEach(function (t) {
        button.addEventListener(t, function () { load().catch(function () {}); }, { once: true });
      });
    }
  })();

  // ---- The /search/ page -------------------------------------------------

  (function () {
    var input = document.getElementById("search-q");
    if (!input) return;
    var form = document.getElementById("search-form");
    var results = document.getElementById("search-results");
    var start = document.getElementById("search-start");
    var status = document.getElementById("search-status");
    var recentBox = document.getElementById("search-recent");
    var recentList = document.getElementById("recent-list");
    var state = { q: "", type: "all", sort: "rel", more: PAGE };
    var timer = null, links = [], active = -1, lastUrl = null;

    function readUrl() {
      var p = new URLSearchParams(location.search);
      var type = p.get("type"), sort = p.get("sort");
      state.q = (p.get("q") || "").slice(0, 200);
      state.type = GROUPS.indexOf(type) >= 0 && state.q ? type : "all";
      state.sort = sort === "order" && state.q ? "order" : "rel";
      state.more = PAGE;
      lastUrl = location.search;
    }

    // The search in the address, defaults left out, so it can be shared.
    function writeUrl() {
      var p = new URLSearchParams(), q = state.q.trim();
      if (q) p.set("q", q);
      if (q && state.type !== "all") p.set("type", state.type);
      if (q && state.sort !== "rel") p.set("sort", state.sort);
      var s = p.toString() ? "?" + p.toString() : "";
      if (s === location.search) return;
      lastUrl = s;
      try { history.replaceState(null, "", location.pathname + s); } catch (e) { /* ignore */ }
    }

    function drawRecent() {
      var list = recent();
      recentBox.hidden = !list.length;
      recentList.textContent = "";
      list.forEach(function (q) {
        var li = el("li", "recent-item");
        var a = el("a", "tag", q);
        a.href = searchUrl(location.pathname, q);
        a.addEventListener("click", function (e) {
          e.preventDefault();
          input.value = q;
          state.q = q; state.type = "all"; state.sort = "rel"; state.more = PAGE;
          writeUrl();
          run();
        });
        var x = el("button", "tag-x", "\u00d7");
        x.type = "button";
        x.setAttribute("aria-label", fill(results.getAttribute("data-remove"), { q: q }));
        x.addEventListener("click", function () { forget(q); drawRecent(); });
        li.appendChild(a);
        li.appendChild(x);
        recentList.appendChild(li);
      });
    }
    document.getElementById("recent-clear").addEventListener("click", function () { forget(null); drawRecent(); });

    function say(text) { status.textContent = text; }

    function countLabel(n) { return fill(ui(n === 1 ? "results_one" : "results_many"), { n: n }); }

    function hitEl(r, terms) {
      var li = el("li", "hit hit-" + r.kind);
      var a = el("a", "hit-link");
      a.href = r.href;
      if (r.eyebrow || (r.kind === "v")) {
        var eb = el("span", "hit-eyebrow");
        eb.textContent = r.kind === "v" ? r.title : r.eyebrow;
        if (r.kind === "v" && r.meta) eb.appendChild(el("span", "hit-level", " \u00b7 " + r.meta));
        a.appendChild(eb);
      }
      if (r.kind !== "v") marked(a.appendChild(el("span", "hit-title")), r.title, terms);
      if (r.kind === "c" && r.meta) a.appendChild(el("span", "hit-meta", r.meta));
      if (r.snippet) {
        var sn = el("span", "hit-snippet" + (r.serif ? " serif" : ""));
        if (r.lang) sn.lang = r.lang;
        marked(sn, r.snippet, terms);
        a.appendChild(sn);
      }
      if (r.extra) marked(a.appendChild(el("span", "hit-meta")), r.extra, terms);
      if (r.kind === "n" && r.meta) a.appendChild(el("span", "hit-meta", r.meta));
      li.appendChild(a);
      return li;
    }

    function chip(label, on, onclick, count) {
      var b = el("button", "facet");
      b.type = "button";
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.appendChild(el("span", null, label));
      if (count != null) b.appendChild(el("span", "facet-n", String(count)));
      b.addEventListener("click", onclick);
      return b;
    }

    function setType(type) {
      state.type = type; state.sort = "rel"; state.more = PAGE;
      writeUrl(); draw(); window.scrollTo({ top: 0 });
    }

    function refCard(ref, terms) {
      var card = el("section", "ref-card");
      card.setAttribute("aria-label", ref.label);
      if (ref.url) {
        var head = el("div", "ref-head");
        head.appendChild(el("h2", null, ref.label));
        var go = el("a", "button ref-go", ref.shown.length ? fill(ui("go_to"), { ref: ref.label })
          : fill(ui("read_passage"), { ref: ref.chapterLabel }));
        go.href = ref.url;
        head.appendChild(go);
        card.appendChild(head);
        if (ref.verse && !ref.shown.length) card.appendChild(el("p", "ref-note", fill(ui("not_yet"), { ref: ref.label })));
        var vs = ref.shown.length ? refVerses(ref) : [];
        if (vs.length) {
          var p = el("p", "ref-text serif");
          vs.forEach(function (v) {
            var span = el("span");
            if (v.lang) span.lang = v.lang;
            span.appendChild(el("sup", null, String(v.verse)));
            span.appendChild(document.createTextNode(" " + v.text + " "));
            p.appendChild(span);
          });
          card.appendChild(p);
        }
      } else {
        card.appendChild(el("p", "ref-note", fill(ui("not_yet"), { ref: ref.label })));
        var read = el("a", null, ui("see_translated"));
        read.href = ui("read_url");
        card.appendChild(read);
      }
      return card;
    }

    // "Did you mean": each term that found nothing, swapped for the
    // commonest word in the index within an edit or two of it.
    var vocab = null;
    function suggest(q, terms) {
      if (!vocab) {
        vocab = {};
        INDEX.docs.forEach(function (d) {
          d.f.forEach(function (f) {
            (f[0].match(/[\p{L}\p{N}']{3,}/gu) || []).forEach(function (w) { vocab[w] = (vocab[w] || 0) + 1; });
          });
        });
      }
      var changed = false, words = terms.map(function (t) {
        if (find([t]).length || / /.test(t.text) || t.text.length < 3) return t.text;
        var limit = t.text.length > 5 ? 2 : 1, best = null, bestD = limit + 1;
        for (var w in vocab) {
          if (Math.abs(w.length - t.text.length) > limit) continue;
          var dist = distance(t.text, w, limit);
          if (dist < bestD || (dist === bestD && vocab[w] > vocab[best])) { best = w; bestD = dist; }
        }
        if (!best) return t.text;
        changed = true;
        return best;
      });
      if (!changed) return null;
      var s = words.join(" ");
      return find(parse(s)).length ? s : null;
    }

    function distance(a, b, max) {
      var prev = [], cur, i, j;
      for (j = 0; j <= b.length; j++) prev[j] = j;
      for (i = 1; i <= a.length; i++) {
        cur = [i];
        var low = i;
        for (j = 1; j <= b.length; j++) {
          cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
          if (cur[j] < low) low = cur[j];
        }
        if (low > max) return max + 1;
        prev = cur;
      }
      return prev[b.length];
    }

    function draw() {
      var q = state.q.trim();
      links = []; active = -1;
      results.textContent = "";
      if (q.length < MIN) {
        results.hidden = true;
        start.hidden = false;
        drawRecent();
        say(q ? ui("prompt") : "");
        return;
      }
      // A reference ("John 3:16") is answered by its card alone: its words
      // and numbers would otherwise match every note that mentions them.
      var terms = parse(q), ref = reference(q), hits = terms.length && !ref ? find(terms) : [];
      var by = {};
      GROUPS.forEach(function (g) { by[g] = []; });
      hits.forEach(function (h) { by[h.doc.k].push(h); });
      results.hidden = false;
      start.hidden = hits.length > 0 || !!ref;
      recentBox.hidden = true;

      var main = el("div", "search-main");
      if (ref) main.appendChild(refCard(ref, terms));

      if (!hits.length && ref) {
        results.appendChild(main);
        say(ref.label);
        return;
      }
      if (!hits.length) {
        var none = el("div", "no-results");
        none.appendChild(el("p", "no-results-q", fill(ui("no_results"), { q: q })));
        var s = suggest(q, terms);
        if (s) {
          var p = el("p");
          p.appendChild(document.createTextNode(ui("did_you_mean") + " "));
          var a = el("a", null, s);
          a.href = searchUrl(location.pathname, s);
          a.addEventListener("click", function (e) {
            e.preventDefault();
            input.value = s; state.q = s; state.type = "all"; state.more = PAGE;
            writeUrl(); draw();
          });
          p.appendChild(a);
          p.appendChild(document.createTextNode("?"));
          none.appendChild(p);
        }
        main.appendChild(none);
        results.appendChild(main);
        say(fill(ui("no_results"), { q: q }));
        return;
      }

      var kinds = GROUPS.filter(function (g) { return by[g].length; });
      var type = state.type !== "all" && by[state.type].length ? state.type : "all";
      if (type !== state.type) { state.type = type; state.sort = "rel"; writeUrl(); }
      var layout = results;
      if (kinds.length > 1) {
        var rail = el("aside", "facets");
        rail.setAttribute("aria-label", ui("filter"));
        var chips = el("div", "facet-list");
        chips.appendChild(chip(ui("all"), type === "all", function () { setType("all"); }, hits.length));
        kinds.forEach(function (g) {
          chips.appendChild(chip(ui("group")[g], type === g, function () { setType(g); }, by[g].length));
        });
        rail.appendChild(chips);
        results.appendChild(rail);
      }
      if (type === "v" || type === "n") {
        var seg = el("div", "facet-sort");
        seg.appendChild(el("span", "facet-sort-label", ui("sort")));
        var segBtns = el("span", "seg");
        [["rel", ui("relevance")], ["order", ui("in_order")]].forEach(function (o) {
          var b = el("button", null, o[1]);
          b.type = "button";
          b.setAttribute("aria-pressed", state.sort === o[0] ? "true" : "false");
          b.addEventListener("click", function () { state.sort = o[0]; state.more = PAGE; writeUrl(); draw(); });
          segBtns.appendChild(b);
        });
        seg.appendChild(segBtns);
        main.appendChild(seg);
      }
      results.classList.toggle("has-facets", kinds.length > 1);

      (type === "all" ? kinds : [type]).forEach(function (g) {
        var list = by[g].slice();
        if (state.sort === "order" && type !== "all") list.sort(function (a, b) { return a.doc.i - b.doc.i; });
        var cap = type === "all" ? CAPS[g] : state.more;
        var section = el("section", "hit-group");
        var h = el("h2", "section-label");
        h.appendChild(document.createTextNode(ui("group")[g] + " "));
        h.appendChild(el("span", "section-n", String(list.length)));
        section.appendChild(h);
        var ul = el("ul", "hits");
        list.slice(0, cap).forEach(function (hit) { ul.appendChild(hitEl(row(hit, terms, q), terms)); });
        section.appendChild(ul);
        if (list.length > cap) {
          var more = el("button", "more-btn", type === "all" ? fill(ui("show_all_n"), { n: list.length }) : ui("show_more"));
          more.type = "button";
          more.addEventListener("click", function () {
            if (type === "all") setType(g);
            else { state.more += PAGE; draw(); }
          });
          section.appendChild(more);
        }
        main.appendChild(section);
      });
      results.appendChild(main);
      links = Array.prototype.slice.call(results.querySelectorAll(".ref-go, .hit-link"));
      var shown = type === "all" ? hits.length : by[type].length;
      say(countLabel(shown));
    }

    function run() {
      var q = state.q.trim();
      if (q.length < MIN) { if (INDEX) draw(); else { results.hidden = true; start.hidden = false; drawRecent(); } return; }
      results.setAttribute("aria-busy", "true");
      if (!INDEX) say("");
      load().then(function () {
        results.removeAttribute("aria-busy");
        draw();
      }, function () {
        results.removeAttribute("aria-busy");
        results.hidden = false;
        results.textContent = "";
        var p = el("p", "notice", results.getAttribute("data-error"));
        var b = el("button", "more-btn", results.getAttribute("data-retry"));
        b.type = "button";
        b.addEventListener("click", run);
        results.appendChild(p);
        results.appendChild(b);
      });
    }

    function setActive(i) {
      links.forEach(function (a) { a.classList.remove("active"); });
      active = i;
      if (i < 0 || !links[i]) return;
      var a = links[i];
      a.classList.add("active");
      a.scrollIntoView({ block: "nearest" });
      // Keep it clear of the search box pinned under the header.
      var below = document.querySelector(".search-bar").getBoundingClientRect().bottom;
      var top = a.getBoundingClientRect().top;
      if (top < below) window.scrollBy(0, top - below - 8);
      var title = (a.querySelector(".hit-title, .hit-eyebrow, h2") || a).textContent;
      say(fill(ui("announce"), { i: i + 1, n: links.length, title: title }));
    }

    input.addEventListener("input", function () {
      clearTimeout(timer);
      state.q = input.value;
      state.type = "all"; state.sort = "rel"; state.more = PAGE;
      timer = setTimeout(function () { writeUrl(); run(); }, 200);
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearTimeout(timer);
      state.q = input.value;
      writeUrl();
      remember(state.q);
      if (active >= 0 && links[active]) { location.href = links[active].href; return; }
      run();
    });
    document.addEventListener("keydown", function (e) {
      if (!links.length || !document.getElementById("palette").hidden) return;
      // From the box or a result only: elsewhere the arrows scroll the page.
      if (e.target !== input && !(e.target.closest && e.target.closest(".hit-link, .ref-go"))) return;
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        var n = links.length, i = active < 0 ? (e.key === "ArrowDown" ? 0 : n - 1)
          : (active + (e.key === "ArrowDown" ? 1 : -1) + n) % n;
        setActive(i);
      } else if (e.key === "Escape" && active >= 0) {
        setActive(-1);
        input.focus();
      }
    });
    results.addEventListener("click", function (e) {
      if (e.target.closest("a")) remember(state.q);
    });
    window.addEventListener("popstate", function () {
      if (location.search === lastUrl) return;
      readUrl(); input.value = state.q; run();
    });

    readUrl();
    input.value = state.q;
    run();
    if (window.matchMedia && matchMedia("(pointer: fine)").matches) {
      requestAnimationFrame(function () { input.focus(); });
    }
    if (!state.q) load().catch(function () {});
  })();

  // ---- A passage opened from a result: the query's words marked ----------

  (function () {
    var text = document.getElementById("text");
    var q = new URLSearchParams(location.search).get("q");
    if (!text || !q) return;
    var terms = parse(q.slice(0, 200));
    if (!terms.length) return;
    var observer = new MutationObserver(apply);

    // Mark matches in each verse's text nodes (reader.js redraws the text
    // when a setting changes, so this runs again after each redraw).
    function apply() {
      observer.disconnect();
      var walker = document.createTreeWalker(text, NodeFilter.SHOW_TEXT, {
        acceptNode: function (n) {
          return n.parentNode.closest("sup, mark") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
        }
      });
      var nodes = [], n, count = 0;
      while ((n = walker.nextNode())) nodes.push(n);
      nodes.forEach(function (node) {
        if (count > 200) return;
        var f = fold(node.nodeValue);
        if (!terms.some(function (t) { return has(t, f); })) return;
        var frag = marked(document.createDocumentFragment(), node.nodeValue, terms);
        count += frag.querySelectorAll("mark").length;
        frag.querySelectorAll("mark").forEach(function (m) { m.className = "q-hit"; });
        node.parentNode.replaceChild(frag, node);
      });
      observer.observe(text, { childList: true, subtree: true });
    }
    apply();
  })();
})();
