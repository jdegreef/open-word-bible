// Memorizing verses: the reader's own list of verses to learn (owb.memory),
// practice in the page, review on a schedule, and the handoff to the phone
// and to Take Root.
//
// OWBMemoryCore is the part with no page in it (tests/js/memorize.test.mjs):
// words, first-letter cues, which words to hide, phrases, the review
// schedule and a QR code. OWBMemory, in a browser, keeps the list and
// draws what web/reader.js, the memorize page (memorize_page in
// scripts/build_site.py), the home page and the plans page show.
//
// owb.memory is kept in this browser, and with the account when the reader
// is signed in (web/site.js; backend accounts/reading.py), keyed by verse
// or by a range of one chapter's verses ("GAL.6.14", "GAL.6.14-16"):
//
//   {"GAL.6.14": {"t": "But far be it from me ...",  the words as learned
//                 "lang": "en", "lv": "B",           language and level
//                 "r": "Galatians 6:14",               its name, as added
//                 "w": "Inclusive · Christ",          the wording, as named
//                 "q": "title=1",                     its settings, as a link
//                 "a": [[1, "...", "cross"]],          anchor words: phrase,
//                                                     original word, gloss
//                 "add": 1791760739987,                when it was added
//                 "due": 1791760739987,                when it is next due
//                 "iv": 3, "n": 2,                     days between, reviews
//                 "p": "galatians",                    the memory plan, if any
//                 "at": 1791760739987}}                the last change
//
// A verse taken out is kept as {at}, so the reader's other devices take it
// out too. The text is the wording the reader chose when adding it: the
// translation's later revisions do not change what they are learning.
var OWBMemoryCore = (function () {
  "use strict";
  var DAY = 86400000;

  // Text in pieces, words and what is between them: [{w: true, s: "But"},
  // {w: false, s: " "}, ...]. Where the browser can split words (Japanese
  // has no spaces), it does; otherwise a word is a run of letters, marks,
  // digits and inner apostrophes or hyphens.
  var WORD = /[\p{L}\p{M}\p{N}]+(?:['’‐-][\p{L}\p{M}\p{N}]+)*/gu;
  function words(text, lang) {
    var out = [];
    if (typeof Intl !== "undefined" && Intl.Segmenter && lang) {
      try {
        var seg = new Intl.Segmenter(lang, { granularity: "word" });
        Array.from(seg.segment(text)).forEach(function (s) {
          var w = !!s.isWordLike;
          var last = out[out.length - 1];
          if (!w && last && !last.w) last.s += s.segment;
          else out.push({ w: w, s: s.segment });
        });
        return out;
      } catch (e) { out = []; /* unknown language: split below */ }
    }
    var at = 0, m;
    WORD.lastIndex = 0;
    while ((m = WORD.exec(text))) {
      if (m.index > at) out.push({ w: false, s: text.slice(at, m.index) });
      out.push({ w: true, s: m[0] });
      at = m.index + m[0].length;
    }
    if (at < text.length) out.push({ w: false, s: text.slice(at) });
    return out;
  }

  // A word's first letter (with its accents), then a line for the rest.
  function cue(word) {
    var first = Array.from(word.normalize("NFC"))[0] || "";
    var rest = Array.from(word).length - 1;
    return first + (rest > 0 ? " " + new Array(Math.min(rest, 8) + 1).join("_") : "");
  }

  // Which words to hide, as a set of their places among the words, for a
  // share from 0 (none) to 1 (all). Longer words go first, as they carry
  // the meaning; among words as long, a fixed spread through the verse, so
  // the same share always hides the same words and more hides more.
  function hidden(pieces, share) {
    var places = [];
    pieces.forEach(function (p, i) { if (p.w) places.push(i); });
    var order = places.map(function (i, n) {
      return { i: i, len: Array.from(pieces[i].s).length, spread: (n * 7919) % 101 };
    }).sort(function (a, b) { return (b.len - a.len) || (a.spread - b.spread) || (a.i - b.i); });
    var count = Math.round(order.length * Math.max(0, Math.min(1, share)));
    var out = new Set();
    order.slice(0, count).forEach(function (o) { out.add(o.i); });
    return out;
  }

  // The letter to type for a word, for "Type": its first, without accents
  // and in lower case, so "É" is typed as "e".
  function key(text) {
    var c = Array.from(text.normalize("NFD").replace(/[̀-ͯ]/g, ""))[0] || "";
    return c.toLocaleLowerCase();
  }

  // A verse in phrases to learn one at a time: split after a comma, a
  // semicolon, a colon, a full stop or a dash (in any of the site's
  // scripts), then short pieces joined to the one before and long ones
  // halved, so each is a few words to a dozen or so.
  var BREAK = /([,;:.!?—、。，；：！？।።-፦]["'”’」』)]*\s*)/;
  function phrases(text, lang) {
    var parts = text.split(BREAK), out = [];
    for (var i = 0; i < parts.length; i += 2) {
      var s = parts[i] + (parts[i + 1] || "");
      if (s.trim()) out.push(s);
    }
    function size(s) { return words(s, lang).filter(function (p) { return p.w; }).length; }
    var joined = [];
    out.forEach(function (s) {
      if (joined.length && (size(s) < 3 || size(joined[joined.length - 1]) < 3)) joined[joined.length - 1] += s;
      else joined.push(s);
    });
    var done = [];
    joined.forEach(function (s) {
      var pieces = words(s, lang), n = 0, total = size(s);
      if (total <= 14) { done.push(s); return; }
      var half = Math.ceil(total / 2), a = "";
      for (var i = 0; i < pieces.length; i++) {
        if (pieces[i].w && ++n > half && pieces[i - 1] && !pieces[i - 1].w) break;
        a += pieces[i].s;
      }
      done.push(a, s.slice(a.length));
    });
    return done.map(function (s) { return s.trim(); }).filter(Boolean);
  }

  // The review schedule. A grade is 0 (missed it), 1 (nearly) or 2 (got
  // it). Missed: tomorrow; nearly: a little longer than last time; got it:
  // two days the first time, then more than twice as long each time. A
  // verse is "known" once it is three weeks apart.
  function startOfDay(ms) {
    var d = new Date(ms);
    d.setHours(4, 0, 0, 0);   // due from four in the morning, the reader's time
    return d.getTime();
  }
  function review(entry, grade, now) {
    var e = {}, k;
    for (k in entry) e[k] = entry[k];
    var iv = e.iv || 0;
    if (grade <= 0) iv = 1;
    else if (grade === 1) iv = Math.max(1, Math.round(iv * 1.2));
    else iv = iv ? Math.max(iv + 1, Math.round(iv * 2.2)) : 2;
    e.iv = iv;
    e.n = (e.n || 0) + 1;
    e.due = startOfDay(now + iv * DAY);
    e.at = now;
    return e;
  }
  var KNOWN = 21;
  function status(entry) {
    if (!entry.n) return "new";
    return (entry.iv || 0) >= KNOWN ? "known" : "learning";
  }
  function isDue(entry, now) {
    return !!entry.add && (entry.due || entry.add) <= now;
  }

  // "GAL.6.14" or "GAL.6.14-16": {book, chapter, from, to}.
  var ID = /^([1-4A-Z]{3})\.(\d{1,3})\.(\d{1,3})(?:-(\d{1,3}))?$/;
  function parse(id) {
    var m = ID.exec(id || "");
    if (!m) return null;
    var from = +m[3], to = m[4] ? +m[4] : from;
    return to >= from ? { book: m[1], chapter: +m[2], from: from, to: to } : null;
  }
  function makeId(book, chapter, from, to) {
    return book + "." + chapter + "." + from + (to && to !== from ? "-" + to : "");
  }

  // A QR code for text, in byte mode at error correction level M (each
  // code can lose some 15% and still read), version 1 to 40. Returns
  // {size, dark(x, y)}. After ISO/IEC 18004 and Project Nayuki's QR Code
  // generator (MIT), written again for this page.
  var ECC_M = [-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28,
               28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28];
  var BLOCKS_M = [-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25,
                  26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49];
  function rawModules(ver) {
    var n = (16 * ver + 128) * ver + 64;
    if (ver >= 2) {
      var align = Math.floor(ver / 7) + 2;
      n -= (25 * align - 10) * align - 55;
      if (ver >= 7) n -= 36;
    }
    return n;
  }
  function dataCodewords(ver) { return Math.floor(rawModules(ver) / 8) - ECC_M[ver] * BLOCKS_M[ver]; }
  function gfMul(x, y) {
    var z = 0;
    for (var i = 7; i >= 0; i--) {
      z = (z << 1) ^ ((z >>> 7) * 0x11d);
      z ^= ((y >>> i) & 1) * x;
    }
    return z & 0xff;
  }
  function rsDivisor(degree) {
    var r = [];
    for (var i = 0; i < degree - 1; i++) r.push(0);
    r.push(1);
    var root = 1;
    for (i = 0; i < degree; i++) {
      for (var j = 0; j < r.length; j++) {
        r[j] = gfMul(r[j], root);
        if (j + 1 < r.length) r[j] ^= r[j + 1];
      }
      root = gfMul(root, 2);
    }
    return r;
  }
  function rsRemainder(data, divisor) {
    var r = divisor.map(function () { return 0; });
    data.forEach(function (b) {
      var f = b ^ r.shift();
      r.push(0);
      divisor.forEach(function (c, i) { r[i] ^= gfMul(c, f); });
    });
    return r;
  }
  function utf8(text) {
    var out = [];
    unescape(encodeURIComponent(text)).split("").forEach(function (c) { out.push(c.charCodeAt(0)); });
    return out;
  }
  function qr(text) {
    var bytes = utf8(text), ver;
    for (ver = 1; ver <= 40; ver++) {
      var bits = 4 + (ver <= 9 ? 8 : 16) + bytes.length * 8;
      if (bits <= dataCodewords(ver) * 8) break;
    }
    if (ver > 40) return null;
    // The data: mode, length, bytes, terminator, padding.
    var bb = [];
    function put(val, len) { for (var i = len - 1; i >= 0; i--) bb.push((val >>> i) & 1); }
    put(4, 4);
    put(bytes.length, ver <= 9 ? 8 : 16);
    bytes.forEach(function (b) { put(b, 8); });
    var capacity = dataCodewords(ver) * 8;
    put(0, Math.min(4, capacity - bb.length));
    put(0, (8 - bb.length % 8) % 8);
    for (var pad = 0xec; bb.length < capacity; pad ^= 0xec ^ 0x11) put(pad, 8);
    var data = [];
    for (var i = 0; i < bb.length; i += 8) {
      var v = 0;
      for (var j = 0; j < 8; j++) v = (v << 1) | bb[i + j];
      data.push(v);
    }
    // Error correction, block by block, then interleaved.
    var blocks = BLOCKS_M[ver], eccLen = ECC_M[ver], raw = Math.floor(rawModules(ver) / 8);
    var shortBlocks = blocks - raw % blocks, shortLen = Math.floor(raw / blocks);
    var divisor = rsDivisor(eccLen), parts = [], k = 0;
    for (i = 0; i < blocks; i++) {
      var dat = data.slice(k, k + shortLen - eccLen + (i < shortBlocks ? 0 : 1));
      k += dat.length;
      var ecc = rsRemainder(dat, divisor);
      if (i < shortBlocks) dat.push(0);
      parts.push(dat.concat(ecc));
    }
    var codewords = [];
    for (i = 0; i < parts[0].length; i++) {
      for (j = 0; j < parts.length; j++) {
        if (i !== shortLen - eccLen || j >= shortBlocks) codewords.push(parts[j][i]);
      }
    }
    // The fixed patterns.
    var size = ver * 4 + 17, grid = [], fixed = [];
    for (i = 0; i < size; i++) { grid.push(new Array(size).fill(false)); fixed.push(new Array(size).fill(false)); }
    function set(x, y, dark) { grid[y][x] = dark; fixed[y][x] = true; }
    for (i = 0; i < size; i++) { set(6, i, i % 2 === 0); set(i, 6, i % 2 === 0); }
    function finder(x, y) {
      for (var dy = -4; dy <= 4; dy++) {
        for (var dx = -4; dx <= 4; dx++) {
          var d = Math.max(Math.abs(dx), Math.abs(dy)), xx = x + dx, yy = y + dy;
          if (xx >= 0 && xx < size && yy >= 0 && yy < size) set(xx, yy, d !== 2 && d !== 4);
        }
      }
    }
    finder(3, 3); finder(size - 4, 3); finder(3, size - 4);
    var align = [];
    if (ver > 1) {
      var count = Math.floor(ver / 7) + 2;
      var step = ver === 32 ? 26 : Math.ceil((ver * 4 + 4) / (count * 2 - 2)) * 2;
      align = [6];
      for (var pos = size - 7; align.length < count; pos -= step) align.splice(1, 0, pos);
    }
    align.forEach(function (ax, ai) {
      align.forEach(function (ay, aj) {
        if ((ai === 0 && aj === 0) || (ai === 0 && aj === align.length - 1) || (ai === align.length - 1 && aj === 0)) return;
        for (var dy = -2; dy <= 2; dy++) {
          for (var dx = -2; dx <= 2; dx++) set(ax + dx, ay + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
        }
      });
    });
    function bit(x, n) { return ((x >>> n) & 1) !== 0; }
    function format(mask) {
      var d = mask, r = d;   // level M is 00
      for (var n = 0; n < 10; n++) r = (r << 1) ^ ((r >>> 9) * 0x537);
      var f = ((d << 10) | r) ^ 0x5412;
      for (n = 0; n <= 5; n++) set(8, n, bit(f, n));
      set(8, 7, bit(f, 6)); set(8, 8, bit(f, 7)); set(7, 8, bit(f, 8));
      for (n = 9; n < 15; n++) set(14 - n, 8, bit(f, n));
      for (n = 0; n < 8; n++) set(size - 1 - n, 8, bit(f, n));
      for (n = 8; n < 15; n++) set(8, size - 15 + n, bit(f, n));
      set(8, size - 8, true);
    }
    format(0);   // reserves the format areas; drawn again with the mask
    if (ver >= 7) {
      var r = ver;
      for (i = 0; i < 12; i++) r = (r << 1) ^ ((r >>> 11) * 0x1f25);
      var vb = (ver << 12) | r;
      for (i = 0; i < 18; i++) {
        var a = size - 11 + i % 3, b = Math.floor(i / 3);
        set(a, b, bit(vb, i)); set(b, a, bit(vb, i));
      }
    }
    // The codewords, in two-column zigzags from the bottom right.
    k = 0;
    for (var right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5;
      for (var vert = 0; vert < size; vert++) {
        for (j = 0; j < 2; j++) {
          var x = right - j, up = ((right + 1) & 2) === 0, y = up ? size - 1 - vert : vert;
          if (!fixed[y][x] && k < codewords.length * 8) {
            grid[y][x] = bit(codewords[k >>> 3], 7 - (k & 7));
            k++;
          }
        }
      }
    }
    var MASKS = [
      function (x, y) { return (x + y) % 2 === 0; },
      function (x, y) { return y % 2 === 0; },
      function (x) { return x % 3 === 0; },
      function (x, y) { return (x + y) % 3 === 0; },
      function (x, y) { return (Math.floor(x / 3) + Math.floor(y / 2)) % 2 === 0; },
      function (x, y) { return x * y % 2 + x * y % 3 === 0; },
      function (x, y) { return (x * y % 2 + x * y % 3) % 2 === 0; },
      function (x, y) { return ((x + y) % 2 + x * y % 3) % 2 === 0; }
    ];
    function masked(m) {
      var g = grid.map(function (row) { return row.slice(); });
      for (var yy = 0; yy < size; yy++) {
        for (var xx = 0; xx < size; xx++) if (!fixed[yy][xx] && MASKS[m](xx, yy)) g[yy][xx] = !g[yy][xx];
      }
      return g;
    }
    // The mask with the fewest long runs, solid blocks and the least
    // imbalance of dark and light (the standard's rules 1, 2 and 4).
    function penalty(g) {
      var p = 0, dark = 0;
      for (var a = 0; a < size; a++) {
        var runR = 1, runC = 1;
        for (var b = 0; b < size; b++) {
          if (g[a][b]) dark++;
          if (b) {
            if (g[a][b] === g[a][b - 1]) { runR++; if (runR === 5) p += 3; else if (runR > 5) p++; } else runR = 1;
            if (g[b][a] === g[b - 1][a]) { runC++; if (runC === 5) p += 3; else if (runC > 5) p++; } else runC = 1;
          }
          if (a && b && g[a][b] === g[a - 1][b] && g[a][b] === g[a][b - 1] && g[a][b] === g[a - 1][b - 1]) p += 3;
        }
      }
      return p + Math.floor(Math.abs(dark * 20 - size * size * 10) / (size * size)) * 10;
    }
    var best = null, bestP = Infinity, bestM = 0;
    for (var m = 0; m < 8; m++) {
      format(m);
      var g = masked(m), pen = penalty(g);
      if (pen < bestP) { best = g; bestP = pen; bestM = m; }
    }
    format(bestM);
    best = masked(bestM);
    return { size: size, version: ver, dark: function (x, y) { return best[y][x]; } };
  }

  return { DAY: DAY, KNOWN: KNOWN, words: words, cue: cue, hidden: hidden, key: key, phrases: phrases,
           review: review, status: status, isDue: isDue, startOfDay: startOfDay,
           parse: parse, makeId: makeId, qr: qr };
})();

// In a browser: the list, and what the pages draw from it.
var OWBMemory = (function () {
  "use strict";
  if (typeof document === "undefined") return null;
  var C = OWBMemoryCore;
  var KEY = "owb.memory";
  var LANG = document.documentElement.lang;

  function all() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || "null");
      return v && typeof v === "object" && !Array.isArray(v) ? v : {};
    } catch (e) { return {}; }
  }
  function write(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) { /* full or blocked */ }
    document.dispatchEvent(new Event("owb:memory"));
  }
  function kept(e) { return !!(e && e.add); }
  function get(id) { var e = all()[id]; return kept(e) ? e : null; }
  // Add a verse, or change what is kept for it (its wording); its review
  // history stays.
  function put(id, fields) {
    var list = all(), e = kept(list[id]) ? list[id] : {}, now = Date.now();
    Object.keys(fields).forEach(function (k) {
      if (fields[k] === null || fields[k] === undefined) delete e[k]; else e[k] = fields[k];
    });
    if (!e.add) { e.add = now; e.due = e.due || C.startOfDay(now); }
    e.at = now;
    list[id] = e;
    write(list);
    return e;
  }
  function remove(id) {
    var list = all();
    list[id] = { at: Date.now() };
    write(list);
  }
  function grade(id, g) {
    var list = all();
    if (!kept(list[id])) return null;
    list[id] = C.review(list[id], g, Date.now());
    write(list);
    return list[id];
  }
  // The kept verses as [id, entry], those due first (soonest first), then
  // the rest in the order they were added.
  function entries() {
    var list = all(), now = Date.now();
    return Object.keys(list).filter(function (id) { return kept(list[id]) && C.parse(id); }).map(function (id) {
      return [id, list[id]];
    }).sort(function (a, b) {
      var da = C.isDue(a[1], now), db = C.isDue(b[1], now);
      if (da !== db) return da ? -1 : 1;
      if (da) return (a[1].due || a[1].add) - (b[1].due || b[1].add);
      return a[1].add - b[1].add;
    });
  }
  function due() {
    var now = Date.now();
    return entries().filter(function (x) { return C.isDue(x[1], now) && x[1].t; });
  }

  // ---- Small helpers for the pages ----
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function fill(text, values) {
    return String(text).replace(/\{(\w+)\}/g, function (m, k) { return k in values ? values[k] : m; });
  }
  function button(cls, label, onClick) {
    var b = el("button", cls, label);
    b.type = "button";
    if (onClick) b.addEventListener("click", onClick);
    return b;
  }
  function day(ms, lang) {
    try {
      return new Intl.DateTimeFormat(lang || LANG, { weekday: "short", month: "short", day: "numeric" }).format(new Date(ms));
    } catch (e) { return new Date(ms).toDateString(); }
  }
  function copy(text, b, ui, label) {
    function done(ok) {
      b.textContent = ui[ok ? "copied" : "copy_failed"];
      setTimeout(function () { b.textContent = label; }, 2000);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
    } else done(false);
  }

  // Take Root, where the page names it (TAKE_ROOT_URL in
  // scripts/build_site.py): a link that carries the verse as learned, so
  // the app never has to apply the reader's settings itself.
  function takeRootBase() {
    var m = document.querySelector('meta[name="owb-takeroot"]');
    return m && m.content ? m.content : "";
  }
  function takeRootUrl(id, e, ref, back) {
    var base = takeRootBase();
    if (!base) return "";
    var q = new URLSearchParams();
    q.set("ref", id);
    q.set("name", ref);
    q.set("text", e.t || "");
    q.set("lang", e.lang || LANG);
    q.set("level", e.lv || "B");
    if (e.w) q.set("wording", e.w);
    if (e.st) q.set("status", e.st);
    q.set("source", "openwordbible");
    if (back) q.set("back", back);
    return base + (base.indexOf("?") >= 0 ? "&" : "?") + q.toString();
  }

  // The memorize page's address that adds a verse there: for the phone
  // (a QR code) and for links.
  function addUrl(memorizeUrl, id, e) {
    var q = "add=" + encodeURIComponent(id) + "&level=" + (e.lv || "B") + (e.q ? "&" + e.q : "");
    return location.origin + memorizeUrl + "?" + q;
  }

  // A QR code as an SVG, in the page's text colour on its background.
  function qrSvg(text, label) {
    var code = C.qr(text);
    if (!code) return null;
    var NS = "http://www.w3.org/2000/svg", n = code.size + 8;
    var svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 " + n + " " + n);
    svg.setAttribute("class", "memo-qr");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", label);
    svg.setAttribute("shape-rendering", "crispEdges");
    var bg = document.createElementNS(NS, "rect");
    bg.setAttribute("width", n); bg.setAttribute("height", n); bg.setAttribute("class", "memo-qr-bg");
    svg.appendChild(bg);
    var d = "";
    for (var y = 0; y < code.size; y++) {
      for (var x = 0; x < code.size; x++) if (code.dark(x, y)) d += "M" + (x + 4) + " " + (y + 4) + "h1v1h-1z";
    }
    var path = document.createElementNS(NS, "path");
    path.setAttribute("d", d);
    path.setAttribute("class", "memo-qr-fg");
    svg.appendChild(path);
    return svg;
  }

  // ---- Practice ----
  // Read it, then first letters, then blanks, then type it: a box to put
  // in the reader's panel or on the memorize page. opts: {ui, lang, done}.
  var TYPE_LANGS = { en: 1, es: 1, fr: 1, pt: 1, sw: 1, vi: 1, ru: 1, uk: 1 };
  function practice(text, opts) {
    var ui = opts.ui, lang = opts.lang || LANG;
    var box = el("div", "memo-practice");
    var modes = ["read", "letters", "fade"].concat(TYPE_LANGS[lang] ? ["type"] : []);
    var mode = opts.mode || "letters", share = 0.35, shown = new Set(), typed = 0;
    var pieces = C.words(text, lang);
    var total = pieces.filter(function (p) { return p.w; }).length;
    var seg = el("div", "seg memo-modes");
    seg.setAttribute("role", "group");
    seg.setAttribute("aria-label", ui.practise);
    var hint = el("p", "hint memo-hint");
    var area = el("p", "memo-text");
    area.lang = lang;
    area.setAttribute("aria-live", "polite");
    var tools = el("div", "memo-tools");
    box.appendChild(seg); box.appendChild(hint); box.appendChild(area); box.appendChild(tools);
    modes.forEach(function (m) {
      var b = button(null, ui["mode_" + m], function () { mode = m; shown = new Set(); typed = 0; draw(); });
      b.dataset.mode = m;
      seg.appendChild(b);
    });

    function word(i, label) {
      var b = button("memo-w", label, function () { shown.add(i); draw(); });
      b.setAttribute("aria-label", ui.show_word);
      return b;
    }
    function draw() {
      seg.querySelectorAll("button").forEach(function (b) {
        b.setAttribute("aria-pressed", b.dataset.mode === mode ? "true" : "false");
      });
      hint.textContent = ui["hint_" + mode];
      area.textContent = "";
      tools.textContent = "";
      var hide = mode === "fade" ? C.hidden(pieces, share) : null, n = 0;
      pieces.forEach(function (p, i) {
        if (!p.w) { area.appendChild(document.createTextNode(p.s)); return; }
        n++;
        if (mode === "read" || shown.has(i)) { area.appendChild(el("span", shown.has(i) ? "memo-shown" : null, p.s)); return; }
        if (mode === "letters") { area.appendChild(word(i, C.cue(p.s))); return; }
        if (mode === "fade") {
          if (!hide.has(i)) area.appendChild(document.createTextNode(p.s));
          else {
            var blank = word(i, " ");
            blank.classList.add("memo-blank");
            blank.style.minWidth = Math.min(8, Array.from(p.s).length) * 0.55 + "em";
            area.appendChild(blank);
          }
          return;
        }
        // Type: the words so far, then the cue for the rest.
        if (n <= typed) area.appendChild(el("span", "memo-shown", p.s));
        else area.appendChild(el("span", "memo-cue", C.cue(p.s)));
      });
      if (mode === "fade") {
        tools.appendChild(button("copy-link", ui.hide_fewer, function () { share = Math.max(0, share - 0.3); shown = new Set(); draw(); }));
        tools.appendChild(button("copy-link", ui.hide_more, function () { share = Math.min(1, share + 0.3); shown = new Set(); draw(); }));
      }
      if (mode === "letters" || mode === "fade") {
        tools.appendChild(button("copy-link", ui.show_all, function () {
          pieces.forEach(function (p, i) { if (p.w) shown.add(i); });
          draw();
        }));
      }
      if (mode === "type") {
        var input = el("input", "memo-type");
        input.type = "text";
        input.autocomplete = "off";
        input.setAttribute("autocapitalize", "off");
        input.setAttribute("spellcheck", "false");
        input.setAttribute("aria-label", ui.type_label);
        input.placeholder = ui.type_label;
        var meter = el("span", "hint memo-count", fill(ui.progress, { n: typed, total: total }));
        input.addEventListener("input", function () {
          var c = input.value.slice(-1);
          input.value = "";
          if (!c.trim()) return;
          var next = pieces.filter(function (p) { return p.w; })[typed];
          if (next && C.key(c) === C.key(next.s)) {
            typed++;
            draw();
            var again = tools.querySelector(".memo-type");
            if (again) again.focus();
          } else {
            input.classList.remove("memo-wrong");
            void input.offsetWidth;
            input.classList.add("memo-wrong");
          }
        });
        if (typed < total) { tools.appendChild(input); tools.appendChild(meter); }
        else finished();
      }
    }
    function finished() {
      tools.appendChild(el("p", "memo-done", ui.well_done));
      tools.appendChild(button("copy-link", ui.again, function () { typed = 0; draw(); }));
      if (opts.done) opts.done();
    }
    draw();
    return box;
  }

  // The verse in phrases, each with the original word it rests on where
  // the reader gave anchors: [[phrase index, word, gloss], ...].
  function phraseList(text, anchors, opts) {
    var ui = opts.ui, lang = opts.lang || LANG;
    var list = el("ol", "memo-phrases");
    list.lang = lang;
    C.phrases(text, lang).forEach(function (s, i) {
      var li = el("li");
      li.appendChild(el("span", "memo-phrase", s));
      (anchors || []).filter(function (a) { return a[0] === i; }).forEach(function (a) {
        var tag = el("span", "memo-anchor");
        var w = el("span", "memo-anchor-w", a[1]);
        if (opts.source) w.lang = opts.source;
        tag.appendChild(w);
        if (a[2]) tag.appendChild(el("span", "memo-anchor-g", a[2]));
        li.appendChild(tag);
      });
      list.appendChild(li);
    });
    var box = el("div", "memo-phrase-box");
    box.appendChild(el("p", "hint", ui.phrases_hint));
    box.appendChild(list);
    return box;
  }

  // Send to the phone: a QR code of the memorize page's address that adds
  // the verse there, the link to copy, and Take Root.
  function phone(link, opts) {
    var ui = opts.ui;
    var box = el("div", "memo-phone");
    var code = qrSvg(link, ui.qr_label);
    if (code) box.appendChild(code);
    var side = el("div", "memo-phone-side");
    side.appendChild(el("p", "hint", ui.phone_hint));
    var field = el("input", "memo-link");
    field.type = "text";
    field.readOnly = true;
    field.value = link;
    field.setAttribute("aria-label", ui.link_label);
    field.addEventListener("focus", function () { field.select(); });
    side.appendChild(field);
    var row = el("div", "memo-actions");
    var b = button("copy-link", ui.copy_link, function () { copy(link, b, ui, ui.copy_link); });
    row.appendChild(b);
    side.appendChild(row);
    if (takeRootBase()) side.appendChild(el("p", "hint", ui.phone_take_root));
    box.appendChild(side);
    return box;
  }

  // A verse's status for a pill: "New", "Learning · next review Thu 20 Nov".
  function statusLine(e, ui) {
    var s = C.status(e), now = Date.now();
    var line = ui["status_" + s];
    if (C.isDue(e, now)) return line + " · " + ui.due_now;
    if (e.due) line += " · " + fill(ui.next_review, { date: day(e.due) });
    return line;
  }

  // ---- Fetching a verse's words (the memorize page, the plans page) ----
  // /verses/<BOOK>/<chapter>.json (verse_files in scripts/build_site.py):
  // each verse's text in each language and level, with the reader-setting
  // spans that OWBMarkup renders at the reader's settings.
  var files = {};
  function chapterFile(versesUrl, book, chapter) {
    var k = book + "/" + chapter;
    if (!files[k]) {
      files[k] = fetch(versesUrl + k + ".json").then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      });
      files[k].catch(function () { delete files[k]; });
    }
    return files[k];
  }
  // {t, lang} for a verse or range at level and settings, or null.
  function fetchText(versesUrl, id, level, settings, lang) {
    var p = C.parse(id);
    if (!p || !window.OWBMarkup) return Promise.resolve(null);
    return chapterFile(versesUrl, p.book, p.chapter).then(function (file) {
      var parts = [], used = null;
      for (var v = p.from; v <= p.to; v++) {
        var own = file.v && file.v[String(v)];
        var l = own && (own[lang] ? lang : own.en ? "en" : null);
        if (!l) return null;
        used = used || l;
        var levels = own[used] || own[l];
        parts.push(OWBMarkup.render(levels[level] || levels.B, settings).replace(/ ?\\q ?/g, " "));
      }
      return { t: parts.join(" ").replace(/\s+/g, " ").trim(), lang: used };
    }).catch(function () { return null; });
  }

  // The reader's settings (web/reader.js owb.settings) and those a link
  // names (?level=B&title=1, as the reader's links do).
  var PARAMS = { gender: "gender", christos: "title", divine_name: "name", deity_pronoun: "pronoun",
                 plural_you: "plural" };
  function readerSettings() {
    var s = {};
    try { s = OWBMarkup.fromSaved(JSON.parse(localStorage.getItem("owb.settings") || "{}")); } catch (e) { /* defaults */ }
    var out = {};
    OWBMarkup.SETTINGS.forEach(function (k) { if (typeof s[k] === "number") out[k] = s[k]; });
    out.level = /^[LBR]$/.test(s.level) ? s.level : "B";
    return out;
  }
  function settingsFrom(q) {
    var out = {}, query = [];
    Object.keys(PARAMS).forEach(function (k) {
      var v = q.get(PARAMS[k]);
      if (v === "0" || v === "1") { out[k] = +v; query.push(PARAMS[k] + "=" + v); }
    });
    return { settings: out, query: query.join("&") };
  }
  function settingsQuery(settings) {
    var DEF = { gender: 0, christos: 0, divine_name: 0, deity_pronoun: 1, plural_you: 0 };
    return Object.keys(PARAMS).filter(function (k) { return k in settings && settings[k] !== DEF[k]; })
      .map(function (k) { return PARAMS[k] + "=" + settings[k]; }).join("&");
  }

  return { core: C, key: KEY, all: all, get: get, put: put, remove: remove, grade: grade, entries: entries, due: due,
           el: el, fill: fill, button: button, day: day, copy: copy, takeRootBase: takeRootBase,
           takeRootUrl: takeRootUrl, addUrl: addUrl, qrSvg: qrSvg, practice: practice, phraseList: phraseList,
           phone: phone, statusLine: statusLine, fetchText: fetchText, readerSettings: readerSettings,
           settingsFrom: settingsFrom, settingsQuery: settingsQuery };
})();

// The memorize page (memorize_page in scripts/build_site.py): what is due
// for review, the reader's verses, and memory plans. A link from the
// reader's QR code (?add=GAL.6.14&level=B&title=1) adds that verse here.
(function () {
  "use strict";
  var M = OWBMemory;
  if (!M) return;
  var box = document.getElementById("memorize");
  if (!box) return;
  var C = M.core, el = M.el, fill = M.fill;
  var data = JSON.parse(box.getAttribute("data-memorize"));
  var ui = JSON.parse(document.getElementById("memory-ui").textContent);
  var LANG = document.documentElement.lang;
  var reviewBox = box.querySelector(".memo-review"), listBox = box.querySelector(".memo-list");
  var note = box.querySelector(".memo-note");
  var open = {};   // id -> "practise" or "phrases": what is unfolded under a verse

  function name(id) {
    var p = C.parse(id);
    if (!p) return id;
    return (data.names[p.book] || p.book) + " " + p.chapter + ":" + p.from + (p.to !== p.from ? "–" + p.to : "");
  }
  function href(id, e) {
    var p = C.parse(id);
    var base = (data.chapters[p.book] || "").replace("{c}", p.chapter);
    var q = "level=" + ((e && e.lv) || "B") + (e && e.q ? "&" + e.q : "");
    return base + "?" + q + "#v" + p.from;
  }
  function say(text) {
    note.textContent = text;
    note.hidden = !text;
  }

  // ---- Due for review: one at a time, say it, then check ----
  var revealed = false;
  function drawReview() {
    reviewBox.textContent = "";
    var due = M.due();
    var head = el("div", "memo-head");
    head.appendChild(el("h2", null, ui.due_heading));
    if (due.length) head.appendChild(el("span", "memo-pill memo-learning", fill(ui.due_count, { n: due.length })));
    reviewBox.appendChild(head);
    if (!due.length) {
      reviewBox.appendChild(el("p", "empty", M.entries().length ? ui.review_done : ui.review_none));
      return;
    }
    var id = due[0][0], e = due[0][1];
    var card = el("div", "memo-card");
    var ref = el("a", "memo-ref", name(id));
    ref.href = href(id, e);
    card.appendChild(ref);
    card.appendChild(el("p", "hint", ui.say_it));
    var text = el("p", "memo-preview" + (revealed ? "" : " memo-veiled"));
    text.lang = e.lang || LANG;
    if (revealed) text.textContent = e.t;
    else text.textContent = C.words(e.t, e.lang).slice(0, 6).map(function (p) { return p.s; }).join("") + "…";
    card.appendChild(text);
    var row = el("div", "memo-actions");
    if (!revealed) {
      row.appendChild(M.button("button", ui.check, function () { revealed = true; drawReview(); focusFirst(".memo-grade"); }));
    } else {
      [[0, "missed"], [1, "shaky"], [2, "got"]].forEach(function (g) {
        row.appendChild(M.button("button memo-grade memo-grade-" + g[1], ui[g[1]], function () {
          M.grade(id, g[0]);
          revealed = false;
          draw();
          focusFirst(".memo-review button");
        }));
      });
    }
    card.appendChild(row);
    reviewBox.appendChild(card);
  }
  function focusFirst(sel) {
    var b = box.querySelector(sel);
    if (b) b.focus();
  }

  // ---- The reader's verses ----
  function drawList() {
    listBox.textContent = "";
    var list = M.entries();
    var head = el("div", "memo-head");
    head.appendChild(el("h2", null, ui.my_verses));
    if (list.length) head.appendChild(el("span", "memo-pill", fill(ui.verse_count, { n: list.length })));
    listBox.appendChild(head);
    if (!list.length) { listBox.appendChild(el("p", "empty", ui.empty)); return; }
    var ul = el("ul", "memo-items");
    list.forEach(function (x) {
      var id = x[0], e = x[1], li = el("li", "memo-item");
      var top = el("div", "memo-item-top");
      var ref = el("a", "memo-ref", name(id));
      ref.href = href(id, e);
      top.appendChild(ref);
      top.appendChild(el("span", "memo-pill memo-" + C.status(e), M.statusLine(e, ui)));
      li.appendChild(top);
      var text = el("p", "memo-item-text", e.t || ui.loading);
      text.lang = e.lang || LANG;
      li.appendChild(text);
      var facts = [];
      if (e.lv) facts.push(data.levels[e.lv] || e.lv);
      if (e.w) facts.push(e.w);
      if (e.p && data.plans[e.p]) facts.push(data.plans[e.p]);
      if (facts.length) li.appendChild(el("p", "hint", facts.join(" · ")));
      var row = el("div", "memo-actions");
      ["practise", "phrases"].forEach(function (what) {
        var b = M.button("copy-link", ui["tab_" + what], function () {
          open[id] = open[id] === what ? null : what;
          drawList();
        });
        b.setAttribute("aria-expanded", open[id] === what ? "true" : "false");
        if (e.t) row.appendChild(b);
      });
      var root = e.t && M.takeRootUrl(id, e, name(id), location.origin + href(id, e));
      if (root) {
        var a = el("a", "copy-link memo-takeroot", ui.take_root + " ↗");
        a.href = root;
        a.target = "_blank";
        a.rel = "noopener";
        row.appendChild(a);
      }
      var del = M.button("copy-link memo-remove", ui.remove);
      del.addEventListener("click", function () {
        if (del.classList.contains("armed")) { M.remove(id); return; }
        del.classList.add("armed");
        del.textContent = ui.remove_confirm;
        setTimeout(function () { del.classList.remove("armed"); del.textContent = ui.remove; }, 4000);
      });
      row.appendChild(del);
      li.appendChild(row);
      if (open[id] === "practise" && e.t) li.appendChild(M.practice(e.t, { ui: ui, lang: e.lang }));
      if (open[id] === "phrases" && e.t) li.appendChild(M.phraseList(e.t, e.a, { ui: ui, lang: e.lang, source: data.source[C.parse(id).book] }));
      ul.appendChild(li);
    });
    listBox.appendChild(ul);
  }

  // ---- Memory plans: one verse or passage a week ----
  function planEntries(pid) {
    return M.entries().filter(function (x) { return x[1].p === pid; });
  }
  function drawPlans() {
    box.querySelectorAll("[data-memo-plan]").forEach(function (card) {
      var pid = card.getAttribute("data-memo-plan");
      var ids = JSON.parse(card.getAttribute("data-verses"));
      var mine = planEntries(pid), have = {};
      mine.forEach(function (x) { have[x[0]] = x[1]; });
      var now = Date.now();
      card.querySelectorAll("[data-week]").forEach(function (wk) {
        var e = have[wk.getAttribute("data-week")];
        wk.classList.toggle("done", !!(e && e.n));
        wk.classList.toggle("now", !!(e && !e.n && C.isDue(e, now)));
      });
      var b = card.querySelector(".memo-plan-start");
      var started = mine.length > 0;
      b.textContent = started ? ui.plan_stop : ui.plan_start;
      b.onclick = function () {
        if (started) { mine.forEach(function (x) { if (!x[1].n) M.remove(x[0]); }); return; }
        startPlan(pid, ids);
      };
      var status = card.querySelector(".memo-plan-status");
      status.textContent = started ? fill(ui.plan_progress, {
        n: mine.filter(function (x) { return x[1].n; }).length, total: ids.length }) : "";
    });
  }
  // Each week's verse goes in now, due on its week's first day; its words
  // are taken at the reader's settings.
  function startPlan(pid, ids) {
    var s = M.readerSettings(), start = C.startOfDay(Date.now());
    var q = M.settingsQuery(s);
    ids.forEach(function (id, i) {
      if (M.get(id)) return;
      M.put(id, { lv: s.level, q: q, p: pid, due: start + i * 7 * C.DAY, lang: LANG, r: name(id) });
    });
    say(ui.plan_started);
    fillTexts();
  }
  // Verses added without their words (a plan, a link) get them here.
  function fillTexts() {
    M.entries().forEach(function (x) {
      var id = x[0], e = x[1];
      if (e.t) return;
      var s = {};
      var q = new URLSearchParams(e.q || "");
      Object.assign(s, M.settingsFrom(q).settings);
      M.fetchText(data.verses, id, e.lv || "B", s, e.lang || LANG).then(function (got) {
        if (!got || !got.t) return;
        var now = M.get(id);
        if (now && !now.t) M.put(id, { t: got.t, lang: got.lang });
      });
    });
  }

  // ---- A verse from a link (the reader's QR code) ----
  function fromLink() {
    var q = new URLSearchParams(location.search);
    var id = q.get("add");
    if (!id || !C.parse(id)) return;
    var level = /^[LBR]$/.test(q.get("level") || "") ? q.get("level") : "B";
    var s = M.settingsFrom(q);
    try { history.replaceState(null, "", location.pathname + location.hash); } catch (e) { /* ignore */ }
    if (M.get(id)) { say(fill(ui.already, { ref: name(id) })); return; }
    say(ui.loading);
    M.fetchText(data.verses, id, level, s.settings, LANG).then(function (got) {
      if (!got) { say(ui.not_found); return; }
      M.put(id, { t: got.t, lang: got.lang, lv: level, q: s.query, r: name(id) });
      say(fill(ui.added_from_link, { ref: name(id) }));
    });
  }

  function draw() { drawReview(); drawList(); drawPlans(); }
  document.addEventListener("owb:memory", draw);
  document.addEventListener("owb:synced", function () { draw(); fillTexts(); });
  fromLink();
  fillTexts();
  draw();
})();

// The home page's card (home_memory in scripts/build_site.py): the verses
// due for review today, when there are any.
(function () {
  "use strict";
  var M = OWBMemory;
  if (!M) return;
  var card = document.querySelector("[data-memo-due]");
  if (!card) return;
  var ui = JSON.parse(card.getAttribute("data-ui"));
  function draw() {
    var due = M.due();
    card.hidden = !due.length;
    if (!due.length) return;
    card.querySelector(".memo-due-count").textContent = M.fill(ui.due_count, { n: due.length });
    var first = due[0][1];
    card.querySelector(".memo-due-ref").textContent = first.r || "";
    var text = card.querySelector(".memo-due-text");
    text.textContent = first.t;
    text.lang = first.lang || document.documentElement.lang;
  }
  document.addEventListener("owb:memory", draw);
  document.addEventListener("owb:synced", draw);
  draw();
})();
