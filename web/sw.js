// Open Word Bible service worker: reading without a connection.
// scripts/build_site.py writes it to /sw.js with the lists below filled in,
// so every deploy that changes a script or the styles is a new worker.
//
// Caches:
//   owb-shell-<version>  the styles, scripts and offline pages (replaced
//                        by each new worker)
//   owb-books            books a reader saved for offline (web/site.js)
//   owb-pages            pages read lately, kept to the last MAX_PAGES
//   owb-assets           fonts and other files fetched along the way
"use strict";

var VERSION = "__VERSION__";
var SHELL = "owb-shell-" + VERSION;
var PRECACHE = __PRECACHE__;
// The offline page for each language: "/es/" -> "/es/offline/".
var OFFLINE = __OFFLINE__;
// Every file whose address carries a content hash, as this deploy names
// it; an older copy of one is dropped from owb-assets (see activate).
var CURRENT = __CURRENT__;
var MAX_PAGES = 60;
// Past this a slow connection is treated as none, and a saved copy is shown.
var NETWORK_WAIT = 4000;

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(SHELL).then(function (c) { return c.addAll(PRECACHE); }));
  self.skipWaiting();
});

// The old shell goes, and so do older versions of the hashed files (a
// search index runs to tens of megabytes, and main deploys often; see
// scripts/check_budgets.py). Saved books keep theirs.
function prune() {
  var current = {};
  CURRENT.forEach(function (u) { current[u.split("?")[0]] = u; });
  return caches.open("owb-assets").then(function (cache) {
    return cache.keys().then(function (keys) {
      return Promise.all(keys.filter(function (req) {
        var url = new URL(req.url), now = current[url.pathname];
        return now && url.search && now !== url.pathname + url.search;
      }).map(function (req) { return cache.delete(req); }));
    });
  });
}

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) {
      return k.indexOf("owb-shell-") === 0 && k !== SHELL;
    }).map(function (k) { return caches.delete(k); }));
  }).then(prune).then(function () { return self.clients.claim(); }));
});

function trim(cache) {
  return cache.keys().then(function (keys) {
    return Promise.all(keys.slice(0, Math.max(0, keys.length - MAX_PAGES)).map(function (k) { return cache.delete(k); }));
  });
}

// Keep a fresh copy of a page: in owb-books if the reader saved it there,
// otherwise among the pages read lately.
function keepPage(req, res) {
  return caches.open("owb-books").then(function (books) {
    return books.match(req).then(function (saved) {
      if (saved) return books.put(req, res);
      return caches.open("owb-pages").then(function (pages) {
        return pages.delete(req).then(function () { return pages.put(req, res); })
          .then(function () { return trim(pages); });
      });
    });
  });
}

function offlinePage(url) {
  var lang = url.pathname.split("/")[1];
  return caches.match(OFFLINE[lang] || OFFLINE[""]).then(function (res) {
    // The shell cleared by a browser short of space: say so plainly.
    return res || new Response("<!doctype html><meta charset=utf-8><title>Offline</title><p>Offline.</p>",
                               { headers: { "Content-Type": "text/html; charset=utf-8" } });
  });
}

// Pages: the network first, so a reader online always gets the latest
// wording; a saved copy when there is no answer in time.
function page(e) {
  var url = new URL(e.request.url);
  var stored = Promise.resolve();
  var network = fetch(e.request).then(function (res) {
    if (res.ok) stored = keepPage(e.request, res.clone());
    return res;
  });
  // Registered now, while the event is live: the copy is kept even when a
  // saved one answered first because the network was slow.
  e.waitUntil(network.then(function () { return stored; }).catch(function () { /* offline */ }));
  var timer;
  var late = new Promise(function (resolve) { timer = setTimeout(resolve, NETWORK_WAIT); });
  return Promise.race([network.catch(function () { return null; }), late]).then(function (res) {
    clearTimeout(timer);
    if (res) return res;
    return caches.match(e.request, { ignoreSearch: true }).then(function (saved) {
      if (saved) return saved;
      // Nothing saved: wait out the network after all, then the offline page.
      return network.catch(function () { return offlinePage(url); });
    });
  });
}

// Files: a cached copy first. Styles and scripts carry their content hash
// (?v=...), so a copy never goes stale; a page saved before a deploy names
// an older hash, and offline it gets the current file instead.
function file(e) {
  return caches.match(e.request).then(function (hit) {
    if (hit) return hit;
    return fetch(e.request).then(function (res) {
      if (res.ok) {
        var copy = res.clone();
        e.waitUntil(caches.open("owb-assets").then(function (c) { return c.put(e.request, copy); }));
      }
      return res;
    }).catch(function () {
      return caches.match(e.request, { ignoreSearch: true }).then(function (old) {
        return old || Response.error();
      });
    });
  });
}

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  // The API (sign-in, accounts) and other sites are left alone.
  if (url.origin !== self.location.origin) return;
  if (req.mode === "navigate") { e.respondWith(page(e)); return; }
  // Share-card images are for link previews, not for reading; and what
  // site.js fetches to save a book (a page, or any file with cache:
  // "no-cache") it stores itself, in owb-books.
  if (url.pathname.indexOf("/og/") === 0 || /\/$/.test(url.pathname) || req.cache === "no-cache") return;
  e.respondWith(file(e));
});
