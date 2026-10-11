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
    signIn.addEventListener("click", function () {
      var here = location.pathname + location.search + location.hash;
      if (!/\/(login|reset-password)\/$/.test(location.pathname)) {
        signIn.href = signIn.pathname + "?redirect=" + encodeURIComponent(here);
      }
    });
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
