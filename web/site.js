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
