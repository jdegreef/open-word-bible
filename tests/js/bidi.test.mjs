// web/site.js's OWBDir: the page's direction, and a dir on each element the
// scripts tag with a language written the other way from what surrounds it,
// as build_site.isolate_directions does for the page as served
// (tests/test_rtl.py). No reading language is right to left yet; these
// pages name a made-up one (Arabic) in their owb-rtl tag.
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";

const ROOT = new URL("../../", import.meta.url).pathname;
const SITE = readFileSync(join(ROOT, "web/site.js"), "utf-8");

// Just enough of an element for OWBDir: attributes, a parent, children.
class Element {
  constructor(attrs = {}, children = []) {
    this.nodeType = 1;
    this.attrs = { ...attrs };
    this.parentElement = null;
    this.children = [];
    children.forEach((c) => this.append(c));
  }
  append(child) { child.parentElement = this; this.children.push(child); return child; }
  getAttribute(name) { return name in this.attrs ? this.attrs[name] : null; }
  hasAttribute(name) { return name in this.attrs; }
  setAttribute(name, value) { this.attrs[name] = String(value); }
  removeAttribute(name) { delete this.attrs[name]; }
  querySelectorAll(selector) {
    assert.equal(selector, "[lang]");
    const found = [];
    const walk = (node) => node.children.forEach((c) => { if (c.hasAttribute("lang")) found.push(c); walk(c); });
    walk(this);
    return found;
  }
}

// A page: <html lang dir?> with a <body>, and its owb-rtl tag if any.
function load({ lang = "en", dir = null, rtl = null } = {}) {
  const html = new Element(dir ? { lang, dir } : { lang });
  const body = html.append(new Element());
  const observers = [];
  const document = {
    documentElement: html, body,
    querySelector: (s) => (s === 'meta[name="owb-rtl"]' && rtl ? new Element({ content: rtl }) : null),
    querySelectorAll: () => [], getElementById: () => null, addEventListener() {},
  };
  class MutationObserver {
    constructor(callback) { this.callback = callback; observers.push(this); }
    observe(target, options) { this.target = target; this.options = options; }
  }
  const context = vm.createContext({ document, MutationObserver, WeakSet, navigator: {}, addEventListener() {},
                                     location: { pathname: "/", search: "", hash: "" }, localStorage: { getItem: () => null } });
  context.window = context;
  vm.runInContext(SITE, context, { filename: "web/site.js" });
  return { D: context.OWBDir, html, body, observers };
}

test("a left-to-right page with no right-to-left language watches nothing", () => {
  const { D, observers } = load();
  assert.equal(D.rtl, false);
  assert.equal(D.sign, 1);
  assert.equal(D.of("en"), "ltr");
  assert.equal(observers.length, 0);
});

test("a right-to-left page", () => {
  const { D, observers } = load({ lang: "ar", dir: "rtl", rtl: "ar arc hbo he" });
  assert.equal(D.rtl, true);
  assert.equal(D.sign, -1);
  assert.equal(D.of("ar"), "rtl");
  assert.equal(D.of("ar-EG"), "rtl");
  assert.equal(D.of("hbo"), "rtl");
  assert.equal(D.of("grc"), "ltr");
  assert.equal(observers.length, 1);
  assert.deepEqual([...observers[0].options.attributeFilter], ["lang"]);
});

test("added text in the other direction gets a dir, relative to the nearest one", () => {
  const { body, observers } = load({ lang: "en", rtl: "ar arc hbo he" });
  const inner = new Element({ lang: "en" }, [new Element({ lang: "ar" })]);
  const cell = new Element({ lang: "ar" }, [inner]);
  const greek = new Element({ lang: "grc" });
  const hebrew = new Element({ lang: "hbo", dir: "rtl" });
  [cell, greek, hebrew].forEach((n) => body.append(n));
  observers[0].callback([{ type: "childList", addedNodes: [cell, greek, hebrew] }]);
  assert.equal(cell.getAttribute("dir"), "rtl");
  assert.equal(inner.getAttribute("dir"), "ltr");
  assert.equal(inner.children[0].getAttribute("dir"), "rtl");
  assert.equal(greek.getAttribute("dir"), null);
  assert.equal(hebrew.getAttribute("dir"), "rtl");
});

test("on a right-to-left page, left-to-right text is isolated", () => {
  const { body, observers } = load({ lang: "ar", dir: "rtl", rtl: "ar arc hbo he" });
  const fallback = body.append(new Element({ lang: "en" }));
  const own = body.append(new Element({ lang: "ar" }));
  observers[0].callback([{ type: "childList", addedNodes: [fallback, own] }]);
  assert.equal(fallback.getAttribute("dir"), "ltr");
  assert.equal(own.getAttribute("dir"), null);
});

test("a changed lang changes the dir it was given, not one a script set", () => {
  const { body, observers } = load({ lang: "en", rtl: "ar arc hbo he" });
  const verse = body.append(new Element({ lang: "ar" }));
  const set = body.append(new Element({ lang: "en", dir: "rtl" }));
  observers[0].callback([{ type: "childList", addedNodes: [verse, set] }]);
  assert.equal(verse.getAttribute("dir"), "rtl");
  verse.setAttribute("lang", "en");
  set.setAttribute("lang", "ar");
  observers[0].callback([{ type: "attributes", target: verse }, { type: "attributes", target: set }]);
  assert.equal(verse.getAttribute("dir"), null);
  assert.equal(set.getAttribute("dir"), "rtl");
});
