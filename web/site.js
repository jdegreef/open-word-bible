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

// The menu button that shows the site links on narrow screens (see
// header.site in style.css). Escape or a click elsewhere closes it.
(function () {
  "use strict";
  var button = document.querySelector(".menu-btn");
  var nav = document.getElementById("site-nav");
  if (!button || !nav) return;

  function open(show) {
    nav.classList.toggle("open", show);
    button.setAttribute("aria-expanded", show ? "true" : "false");
  }

  button.addEventListener("click", function () {
    var show = !nav.classList.contains("open");
    open(show);
    if (show) nav.querySelector("a").focus();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav.classList.contains("open")) { open(false); button.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (nav.classList.contains("open") && !nav.contains(e.target) && !button.contains(e.target)) open(false);
  });
})();
