// The journeys page (/journeys/, scripts/build_site.py journeys_page): one
// journey at a time, chosen from the list or by the address's #id, drawn by
// web/map.js drawJourney with its numbered stops, and the stops listed with
// links to the verses that take the traveller there.
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("jr-data").textContent);
  var show = document.getElementById("jr-show");
  var links = document.querySelectorAll("[data-journey]");

  function t(key) { return DATA.ui[key] || ""; }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function render() {
    var id = decodeURIComponent(location.hash.slice(1));
    var j = DATA.journeys.filter(function (x) { return x.id === id; })[0] || DATA.journeys[0];
    if (!j) return;
    links.forEach(function (a) {
      if (a.dataset.journey === j.id) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
    show.textContent = "";
    show.appendChild(el("h2", null, j.name));
    show.appendChild(el("p", "dek", j.description));
    if (j.uncertain) show.appendChild(el("p", "notice", t("uncertain")));
    var fig = el("figure", "pmap jmap");
    show.appendChild(fig);
    window.OWBMap.drawJourney(fig, j, { base: DATA.map.base, t: t });
    show.appendChild(el("h3", null, t("stops")));
    var list = el("ol", "jr-stops");
    j.stops.forEach(function (s) {
      var li = el("li", null, s.title + " ");
      var a = el("a", null, s.ref);
      a.href = s.href;
      li.appendChild(a);
      list.appendChild(li);
    });
    show.appendChild(list);
  }

  window.addEventListener("hashchange", render);
  render();
})();
