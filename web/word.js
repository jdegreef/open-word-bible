// A dictionary-word page (/word/?w=<lemma>, scripts/build_site.py
// word_page): one Greek, Hebrew or Aramaic dictionary form, with its
// glosses, how often and where it occurs in the translation so far, and the
// translation decisions that name it.
//
// The words are in shards, /words/<n>.json; n is shard() of the lemma, the
// same as build_site.word_shard (tests/word_shard_vectors.json).
// The shard of a lemma: FNV-1a (32-bit) of its UTF-16 code units, modulo
// the shard count. A global, so tests/js/word.test.mjs can check it.
function OWBWordShard(lemma, shards) {
  "use strict";
  var h = 0x811c9dc5;
  for (var i = 0; i < lemma.length; i++) {
    h ^= lemma.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h % shards;
}

if (typeof document !== "undefined") (function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("word-data").textContent);
  var UI = DATA.ui;
  var box = document.getElementById("word");
  var status = document.getElementById("word-status");
  var heading = document.getElementById("word-title");
  var dek = document.getElementById("word-dek");

  function shard(lemma) { return OWBWordShard(lemma, DATA.shards); }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }
  function verseName(vid) {
    var p = vid.split(".");
    return (DATA.books[p[0]] || p[0]) + " " + p[1] + ":" + p[2];
  }
  function verseUrl(vid) {
    var p = vid.split(".");
    return DATA.chapterUrl + p[0].toLowerCase() + "/" + p[1] + "/#v" + p[2];
  }
  function section(title) {
    var s = el("section", "word-section");
    s.appendChild(el("h2", "label", title));
    return s;
  }

  function show(lemma, e) {
    var script = e.lang === "grc" ? "grc" : "he";
    heading.textContent = lemma;
    heading.lang = script;
    if (script === "he") heading.dir = "rtl";
    document.title = lemma + " · " + UI.title + " · Open Word Bible";
    var facts = [UI["lang_" + e.lang]];
    if (e.tr) facts.unshift(e.tr);
    if (e.s) facts.push(UI.strong + " " + (e.lang === "grc" ? "G" : "H") + e.s.replace(/^0+/, ""));
    dek.textContent = facts.join(" · ");
    box.textContent = "";

    if (e.g.length) {
      var g = section(UI.glosses);
      var list = el("ul", "tags");
      e.g.forEach(function (pair) {
        var li = el("li", "tag", pair[0]);
        li.appendChild(el("span", "word-count", " " + pair[1]));
        list.appendChild(li);
      });
      g.appendChild(list);
      g.appendChild(el("p", "word-note", UI.glosses_note));
      box.appendChild(g);
    }

    var verses = e.b.reduce(function (n, b) { return n + b[1]; }, 0);
    var where = section(UI.where);
    where.appendChild(el("p", "word-total", e.n === 1 ? UI.count_one
      : UI.count.replace("{n}", e.n).replace("{v}", verses)));
    var books = el("p", "word-books");
    e.b.forEach(function (b, i) {
      if (i) books.appendChild(document.createTextNode(" · "));
      books.appendChild(el("span", null, (DATA.bookNames[b[0]] || b[0]) + " " + b[1]));
    });
    where.appendChild(books);
    var refs = el("p", "uses-list");
    e.v.forEach(function (vid) {
      var a = el("a", "use", verseName(vid));
      a.href = verseUrl(vid);
      refs.appendChild(a);
    });
    where.appendChild(refs);
    if (verses > e.v.length) where.appendChild(el("p", "word-note", UI.more.replace("{n}", verses - e.v.length)));
    box.appendChild(where);

    if (e.t) {
      var term = el("p", "word-term");
      var a = el("a", "button ghost", UI.term + " →");
      a.href = DATA.termUrl + e.t + "/";
      term.appendChild(a);
      box.appendChild(term);
    }

    // Meaning decisions, and the wording decisions for this page's
    // language (English where it has none yet).
    var lang = e.d.some(function (d) { return d.lang === DATA.lang; }) ? DATA.lang : "en";
    var decisions = e.d.filter(function (d) { return d.layer === "meaning" || d.lang === lang; });
    var ds = section(UI.decisions);
    if (DATA.notesLanguage && decisions.length) ds.appendChild(el("p", "word-note", DATA.notesLanguage));
    if (!decisions.length) ds.appendChild(el("p", "word-note", UI.none));
    decisions.forEach(function (d) {
      var c = el("article", "cmp-card");
      var meta = el("p", "cmp-cat");
      var at = el("a", null, verseName(d.v));
      at.href = verseUrl(d.v);
      meta.appendChild(at);
      meta.appendChild(el("span", null, "· " + (d.layer === "meaning" ? UI.meaning : UI.wording) +
        (DATA.category[d.c] ? " · " + DATA.category[d.c] : "")));
      if (d.u) meta.appendChild(el("span", "badge unc", UI.uncertain));
      c.appendChild(meta);
      c.appendChild(el("p", "cmp-choice", d.ch));
      ds.appendChild(c);
    });
    box.appendChild(ds);
  }

  function fail(text) {
    box.textContent = "";
    box.appendChild(el("p", "notice", text));
    status.textContent = text;
  }

  var lemma = new URLSearchParams(location.search).get("w");
  if (!lemma) { box.appendChild(el("p", "word-note", UI.how)); return; }
  lemma = lemma.normalize("NFC");
  status.textContent = UI.loading;
  fetch(DATA.wordsUrl + shard(lemma) + ".json").then(function (r) {
    if (!r.ok) throw new Error(r.status);
    return r.json();
  }).then(function (words) {
    status.textContent = "";
    if (!words[lemma]) { fail(UI.missing); return; }
    show(lemma, words[lemma]);
  }).catch(function () { fail(UI.failed); });
})();
