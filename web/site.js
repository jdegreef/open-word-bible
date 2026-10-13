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
// page, Admin for a super admin, and signing out.
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
  box.querySelector(".admin-link").hidden = !user.is_super_admin;
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
    document.querySelectorAll("a[data-resume]").forEach(function (a) {
      var names = JSON.parse(a.getAttribute("data-books"));
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
        return pages.concat(files).reduce(function (chain, u) {
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
      var gone = more ? pages : pages.concat(files);
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

// The saved verses page (saved_page in scripts/build_site.py): the
// bookmarks and highlights web/reader.js keeps as owb.marks, by book in
// canonical order, each with its words as they were shown when marked.
(function () {
  "use strict";
  var box = document.getElementById("saved");
  if (!box) return;
  var data = JSON.parse(box.getAttribute("data-saved"));
  var list = box.querySelector(".saved-list"), empty = box.querySelector(".saved-empty");
  var filter = "all";

  function load() {
    try { return JSON.parse(localStorage.getItem("owb.marks") || "{}"); } catch (e) { return {}; }
  }
  function remove(id) {
    var all = load();
    all[id] = { at: Date.now() };
    try { localStorage.setItem("owb.marks", JSON.stringify(all)); } catch (e) { /* ignore */ }
    document.dispatchEvent(new Event("owb:marks"));
    draw();
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function draw() {
    var all = load();
    var ids = Object.keys(all).filter(function (id) {
      var m = all[id], book = id.split(".")[0];
      if (data.order.indexOf(book) < 0) return false;
      // A cleared mark ({at}) is kept only for syncing.
      return filter === "all" ? m.b || m.h : filter === "bookmarks" ? m.b : m.h;
    }).sort(function (a, b) {
      var p = a.split("."), q = b.split(".");
      return (data.order.indexOf(p[0]) - data.order.indexOf(q[0])) || (p[1] - q[1]) || (p[2] - q[2]);
    });
    list.textContent = "";
    empty.hidden = ids.length > 0;
    var group = null, book = null;
    ids.forEach(function (id) {
      var m = all[id], p = id.split(".");
      if (p[0] !== book) {
        book = p[0];
        list.appendChild(el("h2", "saved-book", data.names[book]));
        group = el("ul", "saved-items");
        list.appendChild(group);
      }
      var li = el("li", "saved-item" + (m.h ? " hl-" + m.h : ""));
      var head = el("p", "saved-head");
      var a = el("a", null, data.names[book] + " " + p[1] + ":" + p[2]);
      a.href = data.chapters[book].replace("{c}", p[1]) + "#v" + p[2];
      head.appendChild(a);
      if (m.b) {
        var b = el("span", "saved-flag", data.bookmark);
        head.appendChild(b);
      }
      var x = el("button", "saved-remove", data.remove);
      x.type = "button";
      x.addEventListener("click", function () { remove(id); });
      head.appendChild(x);
      li.appendChild(head);
      if (m.text) {
        var q = el("p", "saved-text", m.text);
        if (m.lang && m.lang !== document.documentElement.lang) q.lang = m.lang;
        li.appendChild(q);
      }
      group.appendChild(li);
    });
  }

  box.querySelectorAll("[data-filter]").forEach(function (b) {
    b.addEventListener("click", function () {
      filter = b.getAttribute("data-filter");
      box.querySelectorAll("[data-filter]").forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
      draw();
    });
  });
  // Marks made or removed in another tab.
  window.addEventListener("storage", function (e) { if (e.key === "owb.marks") draw(); });
  document.addEventListener("owb:synced", draw);
  draw();
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
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
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

// Sync for a signed-in reader (backend accounts/reading.py): bookmarks,
// highlights (owb.marks) and the reading place (owb.place) go to the account
// and come back merged, the latest change to each verse winning, so they
// follow the reader between devices. A sync sends this browser's whole copy;
// it runs on loading a page when anything changed since the last sync (or
// every two minutes, for the other devices' changes), soon after a mark
// changes, on signing in, and, as best it can, when the page is hidden.
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
  function body() { return JSON.stringify({ marks: read("owb.marks", {}), place: read("owb.place", null) }); }
  function hash(text) {
    for (var h = 5381, i = 0; i < text.length; i++) h = (h * 33 + text.charCodeAt(i)) | 0;
    return text.length + ":" + h;
  }
  function session(key) { try { return sessionStorage.getItem(key); } catch (e) { return null; } }

  // The account's merged copy, taken in the same way: the later of each.
  function take(merged) {
    var marks = read("owb.marks", {}), changed = false;
    Object.keys(merged.marks || {}).forEach(function (id) {
      var theirs = merged.marks[id], ours = marks[id];
      if (!ours || theirs.at > (ours.at || 0)) { marks[id] = theirs; changed = true; }
    });
    if (changed) write("owb.marks", marks);
    var place = read("owb.place", null);
    if (merged.place && (!place || merged.place.at > (place.at || 0))) { write("owb.place", merged.place); changed = true; }
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
  document.addEventListener("owb:marks", soon);
  document.addEventListener("owb:account", function () { stopped = false; sync(); });
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") sync(true); });
  window.addEventListener("online", soon);
  if (hash(body()) !== session(SENT) || Date.now() - (Number(session(SINCE)) || 0) > 120000) sync();
})();
