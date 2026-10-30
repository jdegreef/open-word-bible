// The display menu behind the gear in the header (see colour_menu in
// scripts/build_site.py): the colour mode, then the reading text's size,
// typeface and line spacing. Each radiogroup is one setting (data-pref); a
// choice is kept in localStorage as owb-<pref> and applied as data-<pref> on
// <html>, and the default (data-default; "light", Paper, for the colour mode)
// removes both. "auto" is a choice like any other: it follows the device. The inline boot script in each page
// applies saved choices before paint.
(function () {
  "use strict";
  var MODES = ["auto", "light", "sepia", "dark", "night", "contrast"];
  var root = document.documentElement;
  var button = document.querySelector(".prefs-btn");
  var menu = document.getElementById("colour-menu");
  if (!button || !menu) return;
  var groups = Array.prototype.slice.call(menu.querySelectorAll("[data-pref]"));

  function optionsOf(group) {
    return Array.prototype.slice.call(group.querySelectorAll("[data-value]"));
  }

  function current(group) {
    var pref = group.getAttribute("data-pref");
    var v = root.getAttribute("data-" + pref);
    var known = pref === "theme" ? MODES.indexOf(v) >= 0
      : optionsOf(group).some(function (o) { return o.getAttribute("data-value") === v; });
    return known ? v : group.getAttribute("data-default");
  }

  function mark(group) {
    var value = current(group);
    optionsOf(group).forEach(function (o) {
      var on = o.getAttribute("data-value") === value;
      o.setAttribute("aria-checked", on ? "true" : "false");
      o.tabIndex = on ? 0 : -1;
    });
  }

  function choose(group, value) {
    var pref = group.getAttribute("data-pref");
    var isDefault = value === group.getAttribute("data-default");
    if (isDefault) root.removeAttribute("data-" + pref);
    else root.setAttribute("data-" + pref, value);
    try {
      if (isDefault) localStorage.removeItem("owb-" + pref);
      else localStorage.setItem("owb-" + pref, value);
    } catch (e) { /* storage blocked: the choice lasts for this page only */ }
    mark(group);
  }

  function open(show) {
    menu.hidden = !show;
    button.setAttribute("aria-expanded", show ? "true" : "false");
    if (show) {
      var on = optionsOf(groups[0]).filter(function (o) { return o.tabIndex === 0; })[0] || optionsOf(groups[0])[0];
      on.focus();
    }
  }

  button.addEventListener("click", function () { open(menu.hidden); });
  groups.forEach(function (group) {
    var options = optionsOf(group);
    options.forEach(function (o, i) {
      o.addEventListener("click", function () { choose(group, o.getAttribute("data-value")); });
      o.addEventListener("keydown", function (e) {
        var step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
        if (!step) return;
        e.preventDefault();
        var next = options[(i + step + options.length) % options.length];
        choose(group, next.getAttribute("data-value"));
        next.focus();
      });
    });
    mark(group);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !menu.hidden) { open(false); button.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (!menu.hidden && !menu.contains(e.target) && !button.contains(e.target)) open(false);
  });
})();

// The header's section dropdowns (Read, Articles, About), and the menu
// button that shows the links on narrow screens, where each dropdown opens
// in place (see site_header in scripts/build_site.py). One dropdown is open
// at a time; Escape, a click elsewhere or tabbing away closes it.
(function () {
  "use strict";
  var nav = document.getElementById("site-nav");
  var menuBtn = document.querySelector(".menu-btn");
  if (!nav) return;
  var triggers = Array.prototype.slice.call(nav.querySelectorAll(".nav-trigger"));

  function panel(t) { return document.getElementById(t.getAttribute("aria-controls")); }

  function setOpen(t, show) {
    var p = panel(t);
    p.hidden = !show;
    t.setAttribute("aria-expanded", show ? "true" : "false");
    if (show) keepOnScreen(p);
  }

  // A panel is centred under its trigger; nudge it back inside the window
  // (16px clear of each edge) when that would run off one side.
  function keepOnScreen(p) {
    p.style.setProperty("--dd-shift", "0px");
    if (getComputedStyle(p).position !== "absolute") return;
    var r = p.getBoundingClientRect();
    var room = document.documentElement.clientWidth - 16;
    var shift = r.left < 16 ? 16 - r.left : r.right > room ? room - r.right : 0;
    p.style.setProperty("--dd-shift", shift + "px");
  }

  function openOne(t) {
    triggers.forEach(function (o) { if (o !== t) setOpen(o, false); });
    setOpen(t, true);
  }

  function closeAll() { triggers.forEach(function (t) { setOpen(t, false); }); }

  function openTrigger() {
    return triggers.filter(function (t) { return t.getAttribute("aria-expanded") === "true"; })[0];
  }

  function showMenu(show) {
    nav.classList.toggle("open", show);
    if (menuBtn) menuBtn.setAttribute("aria-expanded", show ? "true" : "false");
    if (!show) closeAll();
  }

  triggers.forEach(function (t) {
    t.addEventListener("click", function () {
      if (t.getAttribute("aria-expanded") === "true") setOpen(t, false);
      else openOne(t);
    });
    // Down arrow on a closed trigger opens it and moves into the panel.
    t.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowDown") return;
      e.preventDefault();
      openOne(t);
      var first = panel(t).querySelector("a");
      if (first) first.focus();
    });
    // Leaving an open item by keyboard closes its panel.
    t.parentNode.addEventListener("focusout", function (e) {
      var to = e.relatedTarget;
      if (to && !t.parentNode.contains(to)) setOpen(t, false);
    });
  });

  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      var show = !nav.classList.contains("open");
      showMenu(show);
      if (show) nav.querySelector(".nav-link").focus();
    });
  }

  // Following a link closes the menus, so one to a place on this page
  // (About > Help make it, on the home page) isn't left under them.
  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) showMenu(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var t = openTrigger();
    if (t) { setOpen(t, false); t.focus(); }
    else if (nav.classList.contains("open")) { showMenu(false); menuBtn.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (nav.contains(e.target) || (menuBtn && menuBtn.contains(e.target))) return;
    closeAll();
    if (nav.classList.contains("open")) showMenu(false);
  });
  // Tabbing out of the open narrow-screen menu closes it too.
  nav.addEventListener("focusout", function (e) {
    var to = e.relatedTarget;
    if (to && nav.classList.contains("open") && !nav.contains(to) && !(menuBtn && menuBtn.contains(to))) showMenu(false);
  });
})();

// The header's account menu (account_menu in scripts/build_site.py), as on
// Ochorus. Signed out, "Sign in" leads to /login/ and back to this page.
// Signed in (web/account.js keeps a copy of the account in localStorage),
// the reader's initial opens a menu: their name and email, the account
// page, Admin for the team, and signing out.
(function () {
  "use strict";
  var box = document.querySelector(".account-menu");
  if (!box) return;
  var signIn = box.querySelector("[data-login]");
  var account = null;
  try { account = JSON.parse(localStorage.getItem("owb.account") || "null"); } catch (e) { /* none */ }
  if (!account || !account.user) {
    document.documentElement.classList.remove("signed-in");
    // Set now, not on click, so a link opened in a new tab comes back too;
    // and again on click, for a verse picked since (#v12).
    var back = function () {
      if (/\/(login|reset-password)\/$/.test(location.pathname)) return;
      signIn.href = signIn.pathname + "?redirect=" +
        encodeURIComponent(location.pathname + location.search + location.hash);
    };
    back();
    signIn.addEventListener("click", back);
    signIn.addEventListener("auxclick", back);
    return;
  }
  var user = account.user;
  var name = user.display_name || user.email;
  var button = box.querySelector(".avatar-btn");
  var pop = box.querySelector(".account-pop");
  box.querySelector(".account-initial").textContent = name.charAt(0).toUpperCase();
  box.querySelector(".who-name").textContent = user.display_name || "";
  box.querySelector(".who-email").textContent = user.email;
  // Admin for anyone whose roles open part of it (backend/staff/permissions.py).
  box.querySelector(".admin-link").hidden = !(user.is_super_admin || (user.admin && user.admin.length));
  button.setAttribute("aria-label", button.getAttribute("aria-label") + " (" + name + ")");
  signIn.hidden = true;
  button.hidden = false;

  function open(show) {
    pop.hidden = !show;
    button.setAttribute("aria-expanded", show ? "true" : "false");
    if (show) pop.querySelector("a, button").focus();
  }
  button.addEventListener("click", function () { open(pop.hidden); });
  document.addEventListener("click", function (e) {
    if (!pop.hidden && !box.contains(e.target)) open(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !pop.hidden) { open(false); button.focus(); }
  });

  box.querySelector(".sign-out").addEventListener("click", function () {
    var api = document.querySelector('meta[name="owb-api"]').content;
    function done() {
      try { localStorage.removeItem("owb.account"); } catch (e) { /* none */ }
      location.reload();
    }
    fetch(api + "/api/auth/sign-out", { method: "POST", headers: { Authorization: "Bearer " + account.token } })
      .then(done, done);
  });
})();

// The footer's language links (language_links in scripts/build_site.py):
// the choice is kept as owb-lang, so the boot script in each page opens
// later pages in that language too, and the verse open in the reader
// (#v12) carries over to the same chapter in the other language.
(function () {
  "use strict";
  document.querySelectorAll("a[data-lang]").forEach(function (a) {
    a.addEventListener("click", function () {
      try { localStorage.setItem("owb-lang", a.getAttribute("data-lang")); } catch (e) { /* this page only */ }
      if (/^#v\d+$/.test(location.hash)) a.hash = location.hash;
    });
  });
})();

// "Continue reading" on the home and Read pages (resume_link in
// scripts/build_site.py): the reader keeps the verse it was last at as
// owb.place (web/reader.js), and the link opens that chapter there
// (#at-12 scrolls to the verse without opening its notes).
(function () {
  "use strict";
  function fill() {
    var place = null;
    try { place = JSON.parse(localStorage.getItem("owb.place") || "null"); } catch (e) { /* none */ }
    if (!place || !place.book || !place.chapter || !place.verse) return;
    // The book names in the page's language, carried once, by the footer's link.
    var carrier = document.querySelector("a[data-resume][data-books]");
    if (!carrier) return;
    var names = JSON.parse(carrier.getAttribute("data-books"));
    document.querySelectorAll("a[data-resume]").forEach(function (a) {
      var name = names[place.book];
      if (!name) return;
      // A verse of the next chapter that a sentence runs into is "8:1".
      var verse = String(place.verse);
      var ref = name + " " + (verse.indexOf(":") >= 0 ? verse : place.chapter + ":" + verse);
      // The chapter's address, as chapter_url in scripts/build_site.py makes it.
      a.href = a.getAttribute("data-prefix") + "/" + place.book.toLowerCase() + "/" + place.chapter + "/#at-" + verse;
      a.querySelector("span").textContent = a.getAttribute("data-label").replace("{ref}", ref);
      a.hidden = false;
    });
  }
  fill();
  // A place from the reader's other devices (the sync below).
  document.addEventListener("owb:synced", fill);
})();

// Reading offline (web/sw.js). The worker keeps the pages read lately; the
// Read page's "Save for offline" button stores a whole book in the
// owb-books cache, and owb.saved remembers which, for the button and for
// the offline page's list.
(function () {
  "use strict";
  if (!("serviceWorker" in navigator) || !("caches" in window)) return;
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("/sw.js").catch(function () { /* no offline reading */ });
  });

  var SAVED = "owb.saved";
  function saved() {
    try { return JSON.parse(localStorage.getItem(SAVED) || "{}"); } catch (e) { return {}; }
  }
  function remember(list) {
    try { localStorage.setItem(SAVED, JSON.stringify(list)); } catch (e) { /* the cache still has it */ }
  }
  // A book is saved per language: "es:JHN".
  var lang = document.documentElement.lang;

  var head = document.querySelector("[data-offline-files]");
  var files = head ? JSON.parse(head.getAttribute("data-offline-files")) : [];
  document.querySelectorAll(".save-book").forEach(function (b) {
    var key = lang + ":" + b.getAttribute("data-book");
    var pages = JSON.parse(b.getAttribute("data-pages"));
    // Each chapter's shared reader data, which its page loads.
    var data = JSON.parse(b.getAttribute("data-files") || "[]");
    var label = b.querySelector("span");
    function show(state, n) {
      b.setAttribute("aria-pressed", state === "saved" ? "true" : "false");
      b.disabled = state === "saving";
      label.textContent = b.getAttribute("data-" + state)
        .replace("{n}", n || 0).replace("{total}", pages.length);
    }

    function save() {
      show("saving", 0);
      caches.open("owb-books").then(function (cache) {
        var done = 0;
        // One at a time, so a slow connection is not swamped.
        return pages.concat(data, files).reduce(function (chain, u) {
          return chain.then(function () {
            return cache.match(u).then(function (hit) {
              // no-cache: past the worker's own cache (web/sw.js), fresh.
              return hit || fetch(u, { credentials: "same-origin", cache: "no-cache" }).then(function (res) {
                if (!res.ok) throw new Error(u + ": " + res.status);
                return cache.put(u, res);
              });
            }).then(function () {
              if (pages.indexOf(u) >= 0) show("saving", ++done);
            });
          });
        }, Promise.resolve());
      }).then(function () {
        var list = saved();
        list[key] = { name: b.getAttribute("data-name"), pages: pages };
        remember(list);
        show("saved");
      }).catch(function () { show("failed"); });
    }

    function remove() {
      var list = saved();
      delete list[key];
      remember(list);
      // The shared files go with the language's last saved book.
      var more = Object.keys(list).some(function (k) { return k.indexOf(lang + ":") === 0; });
      var gone = (more ? pages : pages.concat(files)).concat(data);
      caches.open("owb-books").then(function (cache) {
        return Promise.all(gone.map(function (u) { return cache.delete(u); }));
      }).then(function () { show("save"); });
    }

    b.addEventListener("click", function () {
      if (b.getAttribute("aria-pressed") === "true") remove(); else save();
    });
    // Saved, if the list says so and the cache still has its pages (a
    // browser short of space may have cleared it).
    caches.open("owb-books").then(function (cache) { return cache.match(pages[pages.length - 1]); })
      .then(function (hit) { show(saved()[key] && hit ? "saved" : "save"); b.hidden = false; });
  });

  // The offline page lists the saved books, each with its chapters.
  var box = document.getElementById("saved-books");
  if (box) {
    var list = saved(), ul = box.querySelector("ul");
    Object.keys(list).forEach(function (key) {
      var li = document.createElement("li");
      li.className = "book-row";
      var name = document.createElement("span");
      name.className = "book-name";
      name.textContent = list[key].name;
      var pills = document.createElement("span");
      pills.className = "chap-pills";
      list[key].pages.forEach(function (u) {
        var a = document.createElement("a");
        a.className = "chap";
        a.href = u;
        a.textContent = u.split("/").filter(Boolean).pop();
        pills.appendChild(a);
      });
      li.appendChild(name);
      li.appendChild(pills);
      ul.appendChild(li);
    });
    box.hidden = !ul.children.length;
  }
  // Its link home, only if the home page is saved (else it leads back here).
  document.querySelectorAll("a[data-if-saved]").forEach(function (a) {
    caches.match(a.getAttribute("href")).then(function (hit) { a.hidden = !hit; });
  });
})();

// The footer's "Report a problem" (footer_links in scripts/build_site.py)
// opens a GitHub issue that already names the page it was reported from.
(function () {
  "use strict";
  document.querySelectorAll("a[data-report]").forEach(function (a) {
    var title = document.title.replace(/\s*[·|–-]\s*Open Word Bible$/, "");
    a.href += "?title=" + encodeURIComponent(title + ": ") +
      "&body=" + encodeURIComponent("Page: " + location.origin + location.pathname + "\n\nWhat's wrong:\n");
  });
})();

// A link to a folded section (a book's uses on a key-term page, #jhn)
// opens it, in browsers that do not unfold it themselves.
(function () {
  "use strict";
  function unfold() {
    var id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }  // a malformed hash (#100%)
    var target = id && document.getElementById(id);
    if (target && target.tagName === "DETAILS" && !target.open) {
      target.open = true;
      target.scrollIntoView();
    }
  }
  window.addEventListener("hashchange", unfold);
  unfold();
})();

// The articles page (articles_page in scripts/build_site.py): the section
// links filter the list to one section, and a search box narrows it to the
// articles whose title, summary or passages hold every word typed. A
// section link from elsewhere (/articles/#history) opens that section.
(function () {
  "use strict";
  var index = document.getElementById("a-index");
  if (!index) return;
  var links = Array.prototype.slice.call(index.querySelectorAll("[data-filter]"));
  var groups = Array.prototype.slice.call(index.querySelectorAll(".a-group"));
  var input = document.getElementById("a-search");
  var none = document.getElementById("a-none");
  var start = document.getElementById("a-start");
  var filter = "all";

  function fold(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").normalize("NFC").replace(/\u0111/g, "d");
  }
  var texts = groups.map(function (g) {
    return Array.prototype.slice.call(g.querySelectorAll("li")).map(function (li) {
      return { li: li, text: fold(li.textContent) };
    });
  });

  function apply() {
    var words = fold(input.value).split(/\s+/).filter(Boolean);
    var shown = 0;
    groups.forEach(function (g, i) {
      var visible = 0;
      texts[i].forEach(function (item) {
        var match = words.every(function (w) { return item.text.indexOf(w) >= 0; });
        item.li.hidden = !match;
        if (match) visible++;
      });
      g.hidden = !visible || (filter !== "all" && g.getAttribute("data-section") !== filter);
      if (!g.hidden) shown += visible;
    });
    none.hidden = shown > 0;
    if (start) start.hidden = filter !== "all" || words.length > 0;
    links.forEach(function (a) {
      if (a.getAttribute("data-filter") === filter) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  }

  function choose(key) {
    filter = groups.some(function (g) { return g.getAttribute("data-section") === key; }) ? key : "all";
    apply();
  }

  links.forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var key = a.getAttribute("data-filter");
      choose(key);
      history.replaceState(null, "", key === "all" ? location.pathname + location.search : "#" + key);
    });
  });
  input.closest("label").hidden = false;
  input.addEventListener("input", apply);
  window.addEventListener("hashchange", function () { choose(location.hash.slice(1)); });
  choose(location.hash.slice(1));
})();

// The reader's own study, kept in this browser for every page that shows
// or changes it (web/reader.js, web/saved.js, web/word.js, web/plans.js):
//
//   owb.marks    {verse: {b, h, n, t, text, lang, at}}   bookmarks, highlights,
//                                                       notes, collections (t)
//   owb.notes    {"JHN.3.16-21": {n, t, text, lang, at}} notes on a passage
//   owb.words    {lemma: {s, n, g, l, at}}               the word list: saved (s),
//                                                       a note (n), gloss, language
//   owb.lookups  [{w: lemma, g, l, at}, ...]             words looked up lately,
//                                                       newest first; this device only
//
// Anything cleared is kept as {at}, so a signed-in reader's other devices
// clear it too (the sync below; backend accounts/reading.py). A change is
// announced on document as owb:marks, owb:notes or owb:words.
window.OWBStudy = (function () {
  "use strict";
  var HISTORY = 100;
  function read(key) {
    try {
      var v = JSON.parse(localStorage.getItem(key) || "null");
      return v && typeof v === "object" && !Array.isArray(v) ? v : {};
    } catch (e) { return {}; }
  }
  function write(key, value, event) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* full or blocked */ }
    if (event) document.dispatchEvent(new Event(event));
  }
  // A mark or note that is still there, not one kept only to sync its clearing.
  function kept(m) { return !!(m && (m.b || m.h || m.n || (m.t && m.t.length))); }
  // The reader's collections, from every mark and note, case kept as first written.
  function collections() {
    var names = {};
    [read("owb.marks"), read("owb.notes")].forEach(function (all) {
      Object.keys(all).forEach(function (id) {
        (all[id].t || []).forEach(function (name) {
          var k = name.toLowerCase();
          if (!names[k]) names[k] = name;
        });
      });
    });
    return Object.keys(names).map(function (k) { return names[k]; })
      .sort(function (a, b) { return a.localeCompare(b, document.documentElement.lang); });
  }
  function cleanTag(name) { return String(name || "").replace(/\s+/g, " ").trim().slice(0, 40); }
  function hasTag(m, name) {
    return (m.t || []).some(function (x) { return x.toLowerCase() === name.toLowerCase(); });
  }
  function withTag(tags, name, on) {
    var out = (tags || []).filter(function (x) { return x.toLowerCase() !== name.toLowerCase(); });
    if (on) out.push(name);
    return out.slice(0, 20);
  }
  // Take a collection off every mark and note (the saved page's "Delete").
  function dropCollection(name) {
    [["owb.marks", "owb:marks"], ["owb.notes", "owb:notes"]].forEach(function (k) {
      var all = read(k[0]), changed = false;
      Object.keys(all).forEach(function (id) {
        var m = all[id];
        if (!hasTag(m, name)) return;
        m.t = withTag(m.t, name, false);
        if (!m.t.length) delete m.t;
        m.at = Date.now();
        all[id] = kept(m) ? m : { at: m.at };
        changed = true;
      });
      if (changed) write(k[0], all, k[1]);
    });
  }

  // The word list.
  function word(lemma) { return read("owb.words")[lemma] || null; }
  function setWord(lemma, change, info) {
    var all = read("owb.words"), w = all[lemma] || {};
    Object.keys(change).forEach(function (k) { if (change[k]) w[k] = change[k]; else delete w[k]; });
    if (info && info.g) w.g = String(info.g).slice(0, 120);
    if (info && info.l) w.l = info.l;
    w.at = Date.now();
    all[lemma] = w.s || w.n ? w : { at: w.at };
    write("owb.words", all, "owb:words");
    return all[lemma];
  }
  function lookups() {
    try {
      var v = JSON.parse(localStorage.getItem("owb.lookups") || "[]");
      return Array.isArray(v) ? v : [];
    } catch (e) { return []; }
  }
  function lookedUp(lemma, info) {
    var list = lookups().filter(function (x) { return x && x.w !== lemma; });
    list.unshift({ w: lemma, g: (info && info.g) || "", l: (info && info.l) || "", at: Date.now() });
    try { localStorage.setItem("owb.lookups", JSON.stringify(list.slice(0, HISTORY))); } catch (e) { /* blocked */ }
  }
  function forgetLookups() {
    try { localStorage.removeItem("owb.lookups"); } catch (e) { /* blocked */ }
  }

  return { read: read, write: write, kept: kept, collections: collections, cleanTag: cleanTag,
           hasTag: hasTag, withTag: withTag, dropCollection: dropCollection,
           word: word, setWord: setWord, lookups: lookups, lookedUp: lookedUp, forgetLookups: forgetLookups };
})();

// A key term's "Save to word list" (save_word_button in
// scripts/build_site.py); opening the page counts as looking the word up.
(function () {
  "use strict";
  var S = window.OWBStudy;
  document.querySelectorAll("[data-save-word]").forEach(function (b) {
    var lemma = b.getAttribute("data-save-word");
    var info = { g: b.getAttribute("data-gloss"), l: b.getAttribute("data-l") };
    function show() {
      var on = !!(S.word(lemma) || {}).s;
      b.textContent = b.getAttribute(on ? "data-label-saved" : "data-label-save");
      b.setAttribute("aria-pressed", on ? "true" : "false");
    }
    b.addEventListener("click", function () { S.setWord(lemma, { s: !(S.word(lemma) || {}).s }, info); show(); });
    S.lookedUp(lemma, info);
    show();
    b.hidden = false;
  });
})();

// Sync for a signed-in reader (backend accounts/reading.py): bookmarks,
// highlights, notes and collections (owb.marks), passage notes (owb.notes),
// the word list (owb.words), the reading place (owb.place), reading-plan
// progress (owb.plans, web/plans.js), the reader's own plans (owb.myplans)
// and the reader's settings (owb.settings, web/reader.js) go to the account
// and come back merged, the latest change to each verse, note, word and plan
// winning, and the latest copy of the settings, so they follow the reader
// between devices. A sync sends this
// browser's whole copy; it runs on loading a page when anything changed since
// the last sync (or every two minutes, for the other devices' changes), soon
// after a mark, a plan or a setting changes, on signing in, and, as best it
// can, when the page is hidden.
// Offline, or signed out, everything stays in this browser as before.
(function () {
  "use strict";
  var meta = document.querySelector('meta[name="owb-api"]');
  if (!meta || !window.fetch) return;
  var API = meta.content;
  var SINCE = "owb.synced";   // sessionStorage: when this tab last synced
  var SENT = "owb.sent";      // sessionStorage: a hash of what it sent
  var running = false, again = false, timer = null, stopped = false;

  function read(key, empty) {
    try { return JSON.parse(localStorage.getItem(key) || "null") || empty; } catch (e) { return empty; }
  }
  function write(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* full or blocked */ }
  }
  function token() { var a = read("owb.account", null); return a && a.token; }
  // Settings are sent once the reader has changed one here (they carry its
  // time), without the page's language.
  function settings() {
    var all = read("owb.settings", null), v = {};
    if (!all || !all.at) return null;
    Object.keys(all).forEach(function (k) { if (k !== "at" && k !== "lang") v[k] = all[k]; });
    return { v: v, at: all.at };
  }
  function body() {
    return JSON.stringify({ marks: read("owb.marks", {}), place: read("owb.place", null),
                            plans: read("owb.plans", null), settings: settings(),
                            notes: read("owb.notes", {}), words: read("owb.words", {}),
                            myplans: read("owb.myplans", {}) });
  }
  function hash(text) {
    for (var h = 5381, i = 0; i < text.length; i++) h = (h * 33 + text.charCodeAt(i)) | 0;
    return text.length + ":" + h;
  }
  function session(key) { try { return sessionStorage.getItem(key); } catch (e) { return null; } }

  // The account's merged copy, taken in the same way: the later of each.
  // A store keyed by id ({id: {..., at}}): true if anything came in.
  function takeEach(key, theirs) {
    var ours = read(key, {}), moved = false;
    Object.keys(theirs || {}).forEach(function (id) {
      if (!ours[id] || theirs[id].at > (ours[id].at || 0)) { ours[id] = theirs[id]; moved = true; }
    });
    if (moved) write(key, ours);
    return moved;
  }
  function take(merged) {
    var changed = takeEach("owb.marks", merged.marks);
    changed = takeEach("owb.notes", merged.notes) || changed;
    changed = takeEach("owb.words", merged.words) || changed;
    changed = takeEach("owb.myplans", merged.myplans) || changed;
    var place = read("owb.place", null);
    if (merged.place && (!place || merged.place.at > (place.at || 0))) { write("owb.place", merged.place); changed = true; }
    if (merged.plans) {
      var plans = read("owb.plans", {}), moved = false;
      if (!plans.plans) plans.plans = {};
      Object.keys(merged.plans.plans || {}).forEach(function (id) {
        var theirs = merged.plans.plans[id], ours = plans.plans[id];
        if (!ours || theirs.at > (ours.at || 0)) { plans.plans[id] = theirs; moved = true; }
      });
      if (merged.plans.at > (plans.at || 0)) { plans.active = merged.plans.active; plans.at = merged.plans.at; moved = true; }
      if (moved) { write("owb.plans", plans); changed = true; }
    }
    var mine = settings();
    if (merged.settings && merged.settings.at > (mine ? mine.at : 0)) {
      var kept = read("owb.settings", {}) || {};
      Object.keys(merged.settings.v).forEach(function (k) { kept[k] = merged.settings.v[k]; });
      kept.at = merged.settings.at;
      write("owb.settings", kept);
      changed = true;
    }
    try { sessionStorage.setItem(SINCE, String(Date.now())); } catch (e) { /* ignore */ }
    if (changed) document.dispatchEvent(new Event("owb:synced"));
  }

  function sync(leaving) {
    var key = token();
    if (!key || stopped) return;
    var data = body();
    if (leaving && hash(data) === session(SENT)) return;
    if (running) { again = true; return; }
    running = true;
    // keepalive lets the request finish after the page is gone; browsers
    // allow it for small bodies only.
    fetch(API + "/api/reading", {
      method: "POST", body: data, keepalive: !!leaving && data.length < 60000,
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + key }
    }).then(function (r) {
      // The token was signed out elsewhere: forget it, as the account page does.
      if (r.status === 401) {
        stopped = true;
        try { localStorage.removeItem("owb.account"); } catch (e) { /* ignore */ }
        throw new Error("signed out");
      }
      if (!r.ok) throw new Error(String(r.status));
      return r.json();
    }).then(function (merged) {
      try { sessionStorage.setItem(SENT, hash(data)); } catch (e) { /* ignore */ }
      take(merged);
    }).catch(function () { /* offline or signed out: try again later */ })
      .then(function () {
        running = false;
        if (again) { again = false; sync(); }
      });
  }

  function soon() { clearTimeout(timer); timer = setTimeout(sync, 1500); }
  ["owb:marks", "owb:notes", "owb:words", "owb:myplans"].forEach(function (e) { document.addEventListener(e, soon); });
  document.addEventListener("owb:plans-change", soon);
  document.addEventListener("owb:settings", soon);
  document.addEventListener("owb:account", function () { stopped = false; sync(); });
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") sync(true); });
  window.addEventListener("online", soon);
  if (hash(body()) !== session(SENT) || Date.now() - (Number(session(SINCE)) || 0) > 120000) sync();
})();

// The home page's verse of the day (verse_of_the_day in
// scripts/build_site.py): the page is built with the build day's verse,
// and the list in the page gives the reader's own day, in their time zone.
(function () {
  "use strict";
  var box = document.querySelector("[data-votd]");
  if (!box) return;
  var verses;
  try { verses = JSON.parse(box.querySelector(".votd-data").textContent); } catch (e) { return; }
  var now = new Date();
  var day = Math.floor((now.getTime() - now.getTimezoneOffset() * 60000) / 86400000);
  var v = verses[day % verses.length];
  var text = box.querySelector(".votd-text");
  text.textContent = v.t;
  if (v.l) text.setAttribute("lang", v.l); else text.removeAttribute("lang");
  var ref = box.querySelector(".votd-ref");
  ref.textContent = v.r;
  ref.href = v.u;
  box.querySelector(".votd-why").href = v.u;
})();

// The home page's worked examples (example_html in scripts/build_site.py):
// a tab each; tapping a source word shows its lemma and sense and lights
// up the English it became (where the sentence is aligned); a setting
// switch shows the wording's options. The switch starts at the reader's
// own setting and changes only this example.
(function () {
  "use strict";
  var box = document.querySelector("[data-example]");
  if (!box) return;
  var tabs = Array.prototype.slice.call(box.querySelectorAll("[role=tab]"));
  var panels = Array.prototype.slice.call(box.querySelectorAll("[role=tabpanel]"));
  function select(i, focus) {
    tabs.forEach(function (tab, n) {
      tab.setAttribute("aria-selected", n === i ? "true" : "false");
      tab.tabIndex = n === i ? 0 : -1;
      panels[n].hidden = n !== i;
    });
    if (focus) tabs[i].focus();
  }
  if (tabs.length) {
    box.querySelector("[role=tablist]").hidden = false;
    tabs.forEach(function (tab, n) {
      tab.addEventListener("click", function () { select(n); });
      tab.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (d) { e.preventDefault(); select((n + d + tabs.length) % tabs.length, true); }
      });
    });
    select(0);
  }

  panels.forEach(function (panel) {
    var info = panel.querySelector(".w-info");
    var hint = info.innerHTML;
    var current = null;
    panel.querySelectorAll("button.w").forEach(function (w) {
      w.setAttribute("aria-pressed", "false");
      w.addEventListener("click", function () {
        var on = current !== w;
        if (current) current.setAttribute("aria-pressed", "false");
        current = on ? w : null;
        w.setAttribute("aria-pressed", on ? "true" : "false");
        var id = w.getAttribute("data-t");
        panel.querySelectorAll(".al").forEach(function (al) {
          al.classList.toggle("on", on && (" " + al.getAttribute("data-t") + " ").indexOf(" " + id + " ") >= 0);
        });
        if (!on) { info.innerHTML = hint; return; }
        info.textContent = "";
        var word = document.createElement("b");
        word.textContent = w.textContent;
        word.lang = panel.querySelector("[dir=rtl], .greek").getAttribute("lang");
        var lemma = document.createElement("span");
        lemma.className = "w-lemma";
        lemma.lang = word.lang;
        lemma.textContent = w.getAttribute("data-l");
        var sense = document.createElement("span");
        sense.lang = "en";
        sense.textContent = "“" + w.getAttribute("data-g").replace(/\./g, " ") + "”";
        info.appendChild(word);
        info.appendChild(document.createTextNode(" · "));
        info.appendChild(lemma);
        info.appendChild(document.createTextNode(" · "));
        info.appendChild(sense);
      });
    });

    var saved = {};
    try { saved = JSON.parse(localStorage.getItem("owb.settings") || "{}") || {}; } catch (e) { /* defaults */ }
    panel.querySelectorAll("[data-switch]").forEach(function (sw) {
      var key = sw.getAttribute("data-switch");
      var buttons = Array.prototype.slice.call(sw.querySelectorAll("button"));
      function set(v) {
        buttons.forEach(function (b) { b.setAttribute("aria-pressed", +b.getAttribute("data-v") === v ? "true" : "false"); });
        panel.querySelectorAll('.set[data-set="' + key + '"]').forEach(function (span) {
          var options = JSON.parse(span.getAttribute("data-o"));
          span.textContent = options[v] || options[0];
        });
      }
      buttons.forEach(function (b) { b.addEventListener("click", function () { set(+b.getAttribute("data-v")); }); });
      if (saved[key] === 1) set(1);
    });
  });
})();

// The header's language switch (language_menu in scripts/build_site.py),
// and, once, an offer to read in the language the browser prefers when it
// is one of the site's and not the page's. Choosing a language (the
// footer's handler above keeps it as owb-lang) or saying no ends the offer.
(function () {
  "use strict";
  var button = document.querySelector(".lang-btn");
  var pop = document.getElementById("lang-pop");
  if (!button || !pop) return;
  function open(show) {
    pop.hidden = !show;
    button.setAttribute("aria-expanded", show ? "true" : "false");
    if (show) (pop.querySelector("a") || pop).focus();
  }
  button.addEventListener("click", function () { open(pop.hidden); });
  document.addEventListener("click", function (e) {
    if (!pop.hidden && !pop.contains(e.target) && !button.contains(e.target)) open(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !pop.hidden) { open(false); button.focus(); }
  });

  var asked = null;
  try { asked = localStorage.getItem("owb-lang") || localStorage.getItem("owb-lang-offer"); } catch (e) { return; }
  if (asked) return;
  var page = document.documentElement.lang;
  var wanted = (navigator.languages || [navigator.language || ""]).map(function (l) { return String(l).slice(0, 2).toLowerCase(); });
  var link = null;
  for (var i = 0; i < wanted.length && !link; i++) {
    if (wanted[i] === page) return;
    link = pop.querySelector('a[data-lang="' + wanted[i] + '"][data-offer]');
  }
  if (!link) return;
  var bar = document.createElement("div");
  bar.className = "lang-offer";
  bar.setAttribute("role", "region");
  bar.setAttribute("aria-label", button.getAttribute("aria-label"));
  bar.lang = link.getAttribute("data-lang");
  var go = document.createElement("a");
  go.className = "button";
  go.href = link.href;
  go.textContent = link.getAttribute("data-offer");
  go.addEventListener("click", function () {
    try { localStorage.setItem("owb-lang", link.getAttribute("data-lang")); } catch (e) { /* this page only */ }
  });
  var no = document.createElement("button");
  no.type = "button";
  no.className = "lang-offer-no";
  no.textContent = link.getAttribute("data-offer-no");
  no.addEventListener("click", function () {
    try { localStorage.setItem("owb-lang-offer", "no"); } catch (e) { /* asked again next page */ }
    bar.remove();
  });
  bar.appendChild(go);
  bar.appendChild(no);
  document.body.appendChild(bar);
})();
