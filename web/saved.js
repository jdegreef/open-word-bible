// The saved page (saved_page in scripts/build_site.py): the reader's
// bookmarks, highlights, notes and collections (owb.marks), notes on
// passages (owb.notes) and word list (owb.words, owb.lookups), all kept in
// this browser by web/site.js OWBStudy. Verses and passages are listed by
// book in canonical order, each with its words as they were shown when it
// was marked; they can be narrowed to one book or one collection, and what
// is shown can be downloaded as Markdown or printed (or saved as a PDF).
(function () {
  "use strict";
  var box = document.getElementById("saved");
  if (!box || !window.OWBStudy) return;
  var S = window.OWBStudy;
  var data = JSON.parse(box.getAttribute("data-saved"));
  var T = JSON.parse(document.getElementById("saved-text").textContent);
  var LANG = document.documentElement.lang;
  var list = box.querySelector(".saved-list"), empty = box.querySelector(".saved-empty");
  var tagsBox = box.querySelector(".saved-tags"), bookPick = box.querySelector(".saved-book-pick");
  var wordsBox = box.querySelector(".saved-words");
  var filter = "all", tag = "", book = "", view = "verses";

  function el(tag_, cls, text) {
    var n = document.createElement(tag_);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function fill(text, values) {
    return text.replace(/\{(\w+)\}/g, function (m, k) { return k in values ? values[k] : m; });
  }
  // A button that asks to be pressed again within 4 seconds.
  function twice(button, label, again, act) {
    button.addEventListener("click", function () {
      if (button.classList.contains("armed")) { act(); return; }
      button.classList.add("armed");
      button.textContent = again;
      setTimeout(function () { button.classList.remove("armed"); button.textContent = label; }, 4000);
    });
  }

  // Every verse mark and passage note, as items: {id, kind, book, chapter,
  // from, to, m}. A passage note's id is "JHN.3.16-21".
  function items() {
    var out = [];
    var marks = S.read("owb.marks"), notes = S.read("owb.notes");
    Object.keys(marks).forEach(function (id) {
      var p = id.split(".");
      if (data.order.indexOf(p[0]) >= 0 && S.kept(marks[id]))
        out.push({ id: id, kind: "verse", book: p[0], chapter: +p[1], from: +p[2], to: +p[2], m: marks[id] });
    });
    Object.keys(notes).forEach(function (id) {
      var p = id.match(/^([1-4A-Z]{3})\.(\d+)\.(\d+)-(\d+)$/);
      if (p && data.order.indexOf(p[1]) >= 0 && notes[id].n)
        out.push({ id: id, kind: "passage", book: p[1], chapter: +p[2], from: +p[3], to: +p[4], m: notes[id] });
    });
    return out.sort(function (a, b) {
      return (data.order.indexOf(a.book) - data.order.indexOf(b.book)) || (a.chapter - b.chapter) ||
        (a.from - b.from) || (a.to - b.to);
    });
  }
  function shown() {
    return items().filter(function (it) {
      var m = it.m;
      if (book && it.book !== book) return false;
      if (tag && !S.hasTag(m, tag)) return false;
      if (filter === "bookmarks") return m.b;
      if (filter === "highlights") return m.h;
      if (filter === "notes") return m.n;
      return true;
    });
  }
  function ref(it) {
    return data.names[it.book] + " " + it.chapter + ":" + it.from + (it.to !== it.from ? "–" + it.to : "");
  }
  function href(it) {
    return data.chapters[it.book].replace("{c}", it.chapter) + "#v" + it.from;
  }
  function remove(it) {
    var key = it.kind === "verse" ? "owb.marks" : "owb.notes";
    var all = S.read(key);
    all[it.id] = { at: Date.now() };
    S.write(key, all, it.kind === "verse" ? "owb:marks" : "owb:notes");
    draw();
  }

  function drawTags() {
    var names = S.collections();
    tagsBox.textContent = "";
    if (tag && names.indexOf(tag) < 0) tag = "";
    tagsBox.hidden = !names.length;
    if (!names.length) return;
    var row = el("div", "saved-tag-row");
    row.setAttribute("role", "group");
    row.setAttribute("aria-label", T.collections);
    row.appendChild(el("span", "label", T.collections));
    [""].concat(names).forEach(function (name) {
      var b = el("button", "tag-chip", name || T.all_collections);
      b.type = "button";
      b.setAttribute("aria-pressed", name === tag ? "true" : "false");
      b.addEventListener("click", function () { tag = name; draw(); });
      row.appendChild(b);
    });
    tagsBox.appendChild(row);
    if (tag) {
      var count = items().filter(function (it) { return S.hasTag(it.m, tag); }).length;
      var del = el("button", "saved-remove saved-tag-delete", T.delete_collection);
      del.type = "button";
      twice(del, T.delete_collection, fill(T.delete_collection_confirm, { name: tag, n: count }), function () {
        S.dropCollection(tag);
        tag = "";
        draw();
      });
      tagsBox.appendChild(del);
    }
  }

  function drawBooks() {
    var have = {};
    items().forEach(function (it) { have[it.book] = true; });
    if (book && !have[book]) book = "";
    bookPick.textContent = "";
    var all = el("option", null, T.all_books);
    all.value = "";
    bookPick.appendChild(all);
    data.order.forEach(function (b) {
      if (!have[b]) return;
      var o = el("option", null, data.names[b]);
      o.value = b;
      o.selected = b === book;
      bookPick.appendChild(o);
    });
  }

  function drawItems() {
    var its = shown();
    list.textContent = "";
    var anything = items().length > 0;
    empty.hidden = anything;
    if (anything && !its.length) list.appendChild(el("p", "saved-empty", T.empty_filter));
    var group = null, at = null;
    its.forEach(function (it) {
      var m = it.m;
      if (it.book !== at) {
        at = it.book;
        list.appendChild(el("h2", "saved-book", data.names[at]));
        group = el("ul", "saved-items");
        list.appendChild(group);
      }
      var li = el("li", "saved-item" + (m.h ? " hl-" + m.h : "") + (it.kind === "passage" ? " passage" : ""));
      var head = el("p", "saved-head");
      var a = el("a", null, ref(it));
      a.href = href(it);
      head.appendChild(a);
      if (it.kind === "passage") head.appendChild(el("span", "saved-flag", T.passage_note));
      if (m.b) head.appendChild(el("span", "saved-flag", data.bookmark));
      var x = el("button", "saved-remove", data.remove);
      x.type = "button";
      // Removing takes the note too: one with a note asks for a second click.
      if (m.n) twice(x, data.remove, data.confirm, function () { remove(it); });
      else x.addEventListener("click", function () { remove(it); });
      head.appendChild(x);
      li.appendChild(head);
      if (m.text) {
        var q = el("p", "saved-text", m.text);
        if (m.lang && m.lang !== LANG) q.lang = m.lang;
        li.appendChild(q);
      }
      if (m.n) {
        var n = el("p", "saved-note", m.n);
        n.setAttribute("aria-label", data.note);
        li.appendChild(n);
      }
      if (m.t && m.t.length) {
        var tags = el("p", "saved-item-tags");
        tags.setAttribute("aria-label", T.collections);
        m.t.forEach(function (name) {
          var b = el("button", "tag-chip small", name);
          b.type = "button";
          b.addEventListener("click", function () { tag = name; draw(); window.scrollTo(0, box.offsetTop - 80); });
          tags.appendChild(b);
        });
        li.appendChild(tags);
      }
      group.appendChild(li);
    });
  }

  // The word list: saved words and words with a note, then the words looked
  // up lately on this device.
  function wordLang(node, l) {
    node.lang = l === "grc" ? "grc" : "he";
    if (l && l !== "grc") node.dir = "rtl";
    return node;
  }
  function wordLink(lemma, l) {
    var a = wordLang(el("a", "saved-lemma", lemma), l);
    a.href = data.word_url + "?w=" + encodeURIComponent(lemma);
    return a;
  }
  function savedWords() {
    var all = S.read("owb.words");
    return Object.keys(all).filter(function (w) { return all[w].s || all[w].n; })
      .sort(function (a, b) { return a.localeCompare(b); })
      .map(function (w) { return { w: w, e: all[w] }; });
  }
  function drawWords() {
    wordsBox.textContent = "";
    var mine = savedWords();
    wordsBox.appendChild(el("h2", "saved-book", T.words_saved));
    if (!mine.length) wordsBox.appendChild(el("p", "saved-empty", T.words_saved_empty));
    var ul = el("ul", "saved-items");
    mine.forEach(function (x) {
      var li = el("li", "saved-item");
      var head = el("p", "saved-head");
      head.appendChild(wordLink(x.w, x.e.l));
      if (x.e.g) head.appendChild(el("span", "saved-gloss", "“" + x.e.g + "”"));
      var del = el("button", "saved-remove", T.word_remove);
      del.type = "button";
      function drop() { S.setWord(x.w, { s: null, n: null }); draw(); }
      if (x.e.n) twice(del, T.word_remove, data.confirm, drop);
      else del.addEventListener("click", drop);
      head.appendChild(del);
      li.appendChild(head);
      if (x.e.n) {
        var n = el("p", "saved-note", x.e.n);
        n.setAttribute("aria-label", T.word_note);
        li.appendChild(n);
      }
      ul.appendChild(li);
    });
    wordsBox.appendChild(ul);

    var recent = S.lookups();
    var h = el("h2", "saved-book", T.words_recent);
    wordsBox.appendChild(h);
    wordsBox.appendChild(el("p", "fine", T.words_recent_note));
    if (!recent.length) { wordsBox.appendChild(el("p", "saved-empty", T.words_recent_empty)); return; }
    var p = el("p", "uses-list saved-recent");
    recent.forEach(function (x) {
      var a = wordLink(x.w, x.l);
      a.className = "use";
      if (x.g) a.title = x.g;
      p.appendChild(a);
    });
    wordsBox.appendChild(p);
    var forget = el("button", "saved-remove", T.words_forget);
    forget.type = "button";
    forget.addEventListener("click", function () { S.forgetLookups(); draw(); });
    wordsBox.appendChild(forget);
  }

  // What is shown, as a title: "My notes on Romans", "Prayer: Psalms", ...
  function title() {
    if (view === "words") return T.words_title;
    var b = book ? data.names[book] : "";
    if (tag && b) return fill(T.title_book_collection, { collection: tag, book: b });
    if (tag) return tag;
    if (b) return fill(T.title_book, { book: b });
    return T.title_all;
  }
  function today() {
    return new Date().toLocaleDateString(LANG, { year: "numeric", month: "long", day: "numeric" });
  }
  function markdown() {
    var out = ["# " + title(), "", fill(T.exported, { date: today() }), ""];
    function quote(text) { return text.split(/\n/).map(function (l) { return "> " + l; }).join("\n"); }
    if (view === "words") {
      savedWords().forEach(function (x) {
        out.push("## " + x.w + (x.e.g ? " · " + x.e.g : ""), "");
        if (x.e.n) out.push(x.e.n, "");
        out.push(location.origin + data.word_url + "?w=" + encodeURIComponent(x.w), "");
      });
      return out.join("\n");
    }
    var at = null;
    shown().forEach(function (it) {
      var m = it.m;
      if (it.book !== at && !book) { at = it.book; out.push("## " + data.names[at], ""); }
      var flags = [];
      if (it.kind === "passage") flags.push(T.passage_note);
      if (m.b) flags.push(data.bookmark);
      if (m.h) flags.push(T.highlight);
      out.push((book ? "## " : "### ") + ref(it) + (flags.length ? " · " + flags.join(" · ") : ""), "");
      if (m.text) out.push(quote(m.text), "");
      if (m.n) out.push(m.n, "");
      if (m.t && m.t.length) out.push("*" + fill(T.in_collections, { names: m.t.join(", ") }) + "*", "");
      out.push("[" + ref(it) + "](" + location.origin + href(it) + ")", "");
    });
    out.push("---", "", T.footer);
    return out.join("\n");
  }
  function download() {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([markdown()], { type: "text/markdown" }));
    a.download = (title().toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-|-$/g, "") || "saved") + ".md";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }
  box.querySelector("[data-export=markdown]").addEventListener("click", download);
  box.querySelector("[data-export=print]").addEventListener("click", function () {
    var head = document.getElementById("saved-print-head");
    head.querySelector("h1").textContent = title();
    head.querySelector("p").textContent = fill(T.exported, { date: today() });
    window.print();
  });

  function draw() {
    var words = view === "words";
    box.querySelector(".saved-verses").hidden = words;
    wordsBox.hidden = !words;
    box.querySelectorAll("[data-view]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-view") === view ? "true" : "false");
    });
    if (words) { drawWords(); return; }
    drawTags();
    drawBooks();
    drawItems();
  }

  box.querySelectorAll("[data-filter]").forEach(function (b) {
    b.addEventListener("click", function () {
      filter = b.getAttribute("data-filter");
      box.querySelectorAll("[data-filter]").forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
      draw();
    });
  });
  box.querySelectorAll("[data-view]").forEach(function (b) {
    b.addEventListener("click", function () { view = b.getAttribute("data-view"); draw(); });
  });
  bookPick.addEventListener("change", function () { book = bookPick.value; draw(); });
  // A link to one collection or to the word list: /saved/#words, #c=Prayer.
  var hash = decodeURIComponent(location.hash.slice(1));
  if (hash === "words") view = "words";
  else if (hash.indexOf("c=") === 0) tag = hash.slice(2);
  // Changes in another tab, or from another device (a sync).
  window.addEventListener("storage", function (e) {
    if (/^owb\.(marks|notes|words|lookups)$/.test(e.key || "")) draw();
  });
  document.addEventListener("owb:synced", draw);
  draw();
})();
