// The colour-mode menu behind the gear in the header (see COLOUR_MENU in
// scripts/build_site.py). The choice is kept in localStorage and applied as
// data-theme on <html>; "auto" removes it so the page follows the device.
// The inline boot script in each page applies a saved choice before paint.
(function () {
  "use strict";
  var KEY = "owb-theme";
  var MODES = ["light", "sepia", "dark", "night", "contrast"];
  var root = document.documentElement;
  var button = document.querySelector(".prefs-btn");
  var menu = document.getElementById("colour-menu");
  if (!button || !menu) return;
  var options = Array.prototype.slice.call(menu.querySelectorAll("[data-theme-option]"));

  function current() {
    var t = root.getAttribute("data-theme");
    return MODES.indexOf(t) >= 0 ? t : "auto";
  }

  function mark() {
    var value = current();
    options.forEach(function (o) {
      var on = o.getAttribute("data-theme-option") === value;
      o.setAttribute("aria-checked", on ? "true" : "false");
      o.tabIndex = on ? 0 : -1;
    });
  }

  function choose(value) {
    if (value === "auto") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", value);
    try {
      if (value === "auto") localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, value);
    } catch (e) { /* storage blocked: the choice lasts for this page only */ }
    mark();
  }

  function open(show) {
    menu.hidden = !show;
    button.setAttribute("aria-expanded", show ? "true" : "false");
    if (show) {
      var on = options.filter(function (o) { return o.tabIndex === 0; })[0] || options[0];
      on.focus();
    }
  }

  button.addEventListener("click", function () { open(menu.hidden); });
  options.forEach(function (o, i) {
    o.addEventListener("click", function () { choose(o.getAttribute("data-theme-option")); });
    o.addEventListener("keydown", function (e) {
      var step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
      if (!step) return;
      e.preventDefault();
      var next = options[(i + step + options.length) % options.length];
      choose(next.getAttribute("data-theme-option"));
      next.focus();
    });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !menu.hidden) { open(false); button.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (!menu.hidden && !menu.contains(e.target) && !button.contains(e.target)) open(false);
  });
  mark();
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
    panel(t).hidden = !show;
    t.setAttribute("aria-expanded", show ? "true" : "false");
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

// The header's account button: once signed in (web/account.js keeps a copy
// of the account in localStorage), it shows the reader's initial.
(function () {
  "use strict";
  var link = document.querySelector(".account-btn");
  if (!link) return;
  var account = null;
  try { account = JSON.parse(localStorage.getItem("owb.account") || "null"); } catch (e) { /* none */ }
  if (!account || !account.user) return;
  var name = account.user.display_name || account.user.email;
  var initial = link.querySelector(".account-initial");
  initial.textContent = name.charAt(0).toUpperCase();
  initial.hidden = false;
  link.classList.add("signed-in");
  // The label is in the page's language (data-signed-in, from i18n/).
  var label = link.getAttribute("data-signed-in");
  link.setAttribute("aria-label", label + " (" + name + ")");
  link.title = label;
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
