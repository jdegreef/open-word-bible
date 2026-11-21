// The reasoning panel's map: where the places in the chosen sentence are
// (web/reader.js drawWordCards loads this the first time it needs it).
// Places come from data/places.json through the page's cards (each place
// card has "at": [longitude, latitude], "sure" and "area"); land, lakes and
// rivers from /basemap.json (data/basemap.json, Natural Earth), fetched once.
// A known site is a dot, a site OpenBible.info is unsure of a dashed ring,
// and a region, river or sea a label. drawJourney draws a journey (data/
// journeys.json) on the journeys page (web/journeys.js).
var OWBMap = (function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var W = 400, H = 280;
  var base = null, waiting = [];

  function load(url, done) {
    if (base) return done(base);
    waiting.push(done);
    if (waiting.length > 1) return;
    fetch(url).then(function (r) { return r.json(); }).then(function (data) {
      // Each shape's bounds, so a small map skips the rest of the world.
      ["land", "lakes", "rivers"].forEach(function (kind) {
        data[kind] = data[kind].map(function (flat) {
          var b = [Infinity, Infinity, -Infinity, -Infinity];
          for (var i = 0; i < flat.length; i += 2) {
            b[0] = Math.min(b[0], flat[i]); b[2] = Math.max(b[2], flat[i]);
            b[1] = Math.min(b[1], flat[i + 1]); b[3] = Math.max(b[3], flat[i + 1]);
          }
          return { pts: flat, box: b };
        });
      });
      base = data;
      waiting.splice(0).forEach(function (f) { f(base); });
    }).catch(function () { waiting.splice(0).forEach(function (f) { f(null); }); });
  }

  function node(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }

  // The area to show: around the sentence's places (its sites, or its
  // regions where it names no site), at least about 145 km across, so the
  // coast, the lakes and the towns around it place it, padded,
  // in the map's proportions.
  function frame(places) {
    var pts = places.filter(function (p) { return !p.area; });
    if (!pts.length) pts = places;
    var w = Infinity, s = Infinity, e = -Infinity, n = -Infinity;
    pts.forEach(function (p) {
      w = Math.min(w, p.at[0]); e = Math.max(e, p.at[0]);
      s = Math.min(s, p.at[1]); n = Math.max(n, p.at[1]);
    });
    var mid = (s + n) / 2, k = Math.cos(mid * Math.PI / 180);
    var cx = (w + e) / 2, cy = mid;
    var spanY = Math.max((n - s) * 1.5, ((e - w) * k * 1.5) * H / W, 1.3);
    var spanX = spanY * W / H / k;
    return { w: cx - spanX / 2, e: cx + spanX / 2, s: cy - spanY / 2, n: cy + spanY / 2, k: k };
  }

  function path(flat, f, close) {
    var sx = W / (f.e - f.w), sy = H / (f.n - f.s), d = "";
    for (var i = 0; i < flat.length; i += 2) {
      d += (i ? "L" : "M") + ((flat[i] - f.w) * sx).toFixed(1) + "," + ((f.n - flat[i + 1]) * sy).toFixed(1);
    }
    return close ? d + "Z" : d;
  }

  function overlaps(b, f) { return b[0] <= f.e && b[2] >= f.w && b[1] <= f.n && b[3] >= f.s; }

  function xy(p, f) { return [(p.at[0] - f.w) * W / (f.e - f.w), (f.n - p.at[1]) * H / (f.n - f.s)]; }

  // A name beside its point, or on its left where it would run off the map.
  function label(svg, x, y, text, cls, gap) {
    var right = gap && x + gap + text.length * 7 > W;
    var t = node("text", { x: gap ? (right ? x - gap : x + gap) : x, y: y, "class": cls }, svg);
    if (right) t.setAttribute("text-anchor", "end");
    t.textContent = text;
    return t;
  }

  // The sea, then (once fetched) the land, lakes and rivers under what is drawn.
  function drawBase(svg, f, url) {
    node("rect", { width: W, height: H, "class": "pmap-sea" }, svg);
    load(url, function (data) {
      if (!data) return;
      var under = svg.firstChild.nextSibling;
      data.land.forEach(function (s) {
        if (overlaps(s.box, f)) svg.insertBefore(node("path", { d: path(s.pts, f, true), "class": "pmap-land" }), under);
      });
      data.lakes.forEach(function (s) {
        if (overlaps(s.box, f)) svg.insertBefore(node("path", { d: path(s.pts, f, true), "class": "pmap-lake" }), under);
      });
      data.rivers.forEach(function (s) {
        if (overlaps(s.box, f)) svg.insertBefore(node("path", { d: path(s.pts, f, false), "class": "pmap-river" }), under);
      });
    });
  }

  function key(box, t, sure, unsure) {
    var p = document.createElement("p");
    p.className = "pmap-key";
    if (sure) {
      var a = document.createElement("span");
      a.className = "pmap-key-sure";
      a.textContent = t("map_sure");
      p.appendChild(a);
    }
    if (unsure) {
      var b = document.createElement("span");
      b.className = "pmap-key-unsure";
      b.textContent = t("map_unsure");
      p.appendChild(b);
    }
    var credit = document.createElement("span");
    credit.className = "pmap-credit";
    credit.textContent = t("map_credit");
    p.appendChild(credit);
    box.appendChild(p);
  }

  // A journey (data/journeys.json, through the journeys page): its stops
  // joined in order by a line and numbered. A place visited twice has one
  // mark, numbered for its first visit, with the later numbers by its name.
  // A site OpenBible.info is unsure of is a dashed ring; a dashed line is a
  // route that is itself uncertain (the exodus).
  function drawJourney(box, journey, opts) {
    var t = opts.t;
    box.textContent = "";
    var stops = journey.stops;
    var f = frame(stops.map(function (s) { return { at: s.at }; }));
    var svg = node("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "class": "pmap-svg jmap-svg",
                            "aria-label": t("map_label").replace("{name}", journey.name) });
    box.appendChild(svg);
    drawBase(svg, f, opts.base);
    var d = "";
    stops.forEach(function (s, i) {
      var c = xy(s, f);
      d += (i ? "L" : "M") + c[0].toFixed(1) + "," + c[1].toFixed(1);
    });
    node("path", { d: d, "class": "jmap-route" + (journey.uncertain ? " jmap-route-unsure" : "") }, svg);
    var marks = {}, order = [];
    stops.forEach(function (s, i) {
      var k = s.at.join(",");
      if (!marks[k]) { marks[k] = { stop: s, n: [] }; order.push(k); }
      marks[k].n.push(i + 1);
    });
    order.forEach(function (k) {
      var m = marks[k], c = xy(m.stop, f);
      node("circle", { cx: c[0], cy: c[1], r: 8, "class": "jmap-stop" + (m.stop.sure ? "" : " jmap-stop-unsure") }, svg);
      node("text", { x: c[0], y: c[1] + 3.5, "class": "jmap-num" }, svg).textContent = String(m.n[0]);
      var name = m.stop.title + (m.n.length > 1 ? " (" + m.n.slice(1).join(", ") + ")" : "");
      label(svg, c[0], c[1] + 4, name, "pmap-name jmap-name", 11);
    });
    key(box, t, stops.some(function (s) { return s.sure; }), stops.some(function (s) { return !s.sure; }));
  }

  // Draw into box: places (the sentence's), others (the rest of the page's,
  // shown faintly for context), opts {base, t} (t: the reader's messages).
  function draw(box, places, others, opts) {
    var t = opts.t;
    box.textContent = "";
    var head = document.createElement("h3");
    head.textContent = t("map_title");
    box.appendChild(head);
    var f = frame(places);
    var names = places.map(function (p) { return p.title; }).join(", ");
    var svg = node("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "class": "pmap-svg",
                            "aria-label": t("map_label").replace("{places}", names) });
    box.appendChild(svg);
    drawBase(svg, f, opts.base);
    var mine = {};
    places.forEach(function (p) { mine[p.title] = true; });
    var shown = {};
    others.forEach(function (p) {
      if (mine[p.title] || shown[p.title] || p.area) return;
      var c = xy(p, f);
      if (c[0] < 4 || c[0] > W - 4 || c[1] < 4 || c[1] > H - 4) return;
      shown[p.title] = true;
      node("circle", { cx: c[0], cy: c[1], r: 2.5, "class": "pmap-other" }, svg);
      label(svg, c[0], c[1] + 4, p.title, "pmap-other-name", 5);
    });
    places.forEach(function (p) {
      var c = xy(p, f);
      if (p.area) { label(svg, c[0], c[1], p.title.toUpperCase(), "pmap-area"); return; }
      if (p.sure) node("circle", { cx: c[0], cy: c[1], r: 5, "class": "pmap-site" }, svg);
      else {
        node("circle", { cx: c[0], cy: c[1], r: 10, "class": "pmap-unsure" }, svg);
        node("circle", { cx: c[0], cy: c[1], r: 2.5, "class": "pmap-site" }, svg);
      }
      label(svg, c[0], c[1] + 4, p.title, "pmap-name", p.sure ? 9 : 14);
    });
    key(box, t, true, !places.every(function (p) { return p.sure || p.area; }));
  }

  return { draw: draw, drawJourney: drawJourney };
})();
