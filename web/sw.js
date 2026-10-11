// Open Word Bible's service worker: reading offline. The build fills in
// VERSION and PRECACHE (scripts/build_site.py).
//
// Pages: from the network when there is one, kept as they arrive, so every
// chapter a reader has opened is there offline; without a network, the kept
// copy, or the offline page. Scripts, styles, fonts and data files have a
// content hash in their address, so a kept copy is always right: from the
// cache first. The API (another host) is never touched.
"use strict";
var VERSION = "__VERSION__";
var PRECACHE = __PRECACHE__;
var STATIC = "owb-static-" + VERSION;
var RUNTIME = "owb-runtime";

self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(STATIC).then(function (cache) { return cache.addAll(PRECACHE); })
    .then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf("owb-static-") === 0 && k !== STATIC; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

// The offline page in the language of the address ("/es/..." is Spanish).
function offlinePage(url) {
  var m = /^\/(es|fr|sw)\//.exec(new URL(url).pathname);
  return (m ? "/" + m[1] : "") + "/offline/";
}

function keep(request, response) {
  if (response && response.ok && response.type === "basic") {
    var copy = response.clone();
    caches.open(RUNTIME).then(function (cache) { cache.put(request, copy); });
  }
  return response;
}

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET" || new URL(request.url).origin !== self.location.origin) return;
  if (request.mode === "navigate") {
    event.respondWith(fetch(request).then(function (response) { return keep(request, response); })
      .catch(function () {
        return caches.match(request, { ignoreSearch: true }).then(function (hit) {
          return hit || caches.match(offlinePage(request.url));
        });
      }));
    return;
  }
  event.respondWith(caches.match(request).then(function (hit) {
    return hit || fetch(request).then(function (response) { return keep(request, response); });
  }));
});
