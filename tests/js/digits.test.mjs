// web/site.js's OWBDigits: numbers in text the scripts add show in the
// digits of the language the text is in, as build_site.localize_digits
// does for the page as served (tests/test_digits.py).
// Run: node --test tests/js/
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import vm from "node:vm";

const ROOT = new URL("../../", import.meta.url).pathname;
const SITE = readFileSync(join(ROOT, "web/site.js"), "utf-8");
const FA = "۰۱۲۳۴۵۶۷۸۹";

// Just enough of the DOM: elements with attributes and children, text nodes.
class Node {
  get firstChild() { return this.children?.[0] || null; }
  get nextSibling() {
    const p = this.parentElement;
    return p ? p.children[p.children.indexOf(this) + 1] || null : null;
  }
}
class Element extends Node {
  constructor(name = "DIV", attrs = {}, children = []) {
    super();
    this.nodeType = 1;
    this.nodeName = name;
    this.attrs = { ...attrs };
    this.isContentEditable = "contenteditable" in attrs;
    this.parentElement = null;
    this.children = [];
    children.forEach((c) => this.append(c));
  }
  append(child) { child.parentElement = this; this.children.push(child); return child; }
  getAttribute(name) { return name in this.attrs ? this.attrs[name] : null; }
  hasAttribute(name) { return name in this.attrs; }
  setAttribute(name, value) { this.attrs[name] = String(value); }
  removeAttribute(name) { delete this.attrs[name]; }
  querySelectorAll() { return []; }
}
class Text extends Node {
  constructor(value) { super(); this.nodeType = 3; this.nodeValue = value; this.parentElement = null; }
}

function load({ lang = "fa", digits = `fa:${FA}` } = {}) {
  const html = new Element("HTML", { lang });
  const body = html.append(new Element("BODY"));
  const observers = [];
  const document = {
    documentElement: html, body,
    querySelector: (s) => (s === 'meta[name="owb-digits"]' && digits ? new Element("META", { content: digits }) : null),
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
  return { G: context.OWBDigits, html, body, observers };
}

test("without the tag nothing is watched", () => {
  const { G, observers } = load({ lang: "en", digits: null });
  assert.equal(G.of("fa"), null);
  assert.equal(observers.length, 0);
});

test("Persian text added by a script shows Persian digits", () => {
  const { G, body, observers } = load();
  assert.equal(G.of("fa-AF").join(""), FA);
  assert.equal(observers.length, 1);
  const sup = body.append(new Element("SUP", {}, [new Text("16")]));
  const ref = body.append(new Element("SPAN", {}, [new Text("اعمال 3:16, G2316")]));
  observers[0].callback([{ type: "childList", addedNodes: [sup, ref] }]);
  assert.equal(sup.children[0].nodeValue, "۱۶");
  assert.equal(ref.children[0].nodeValue, "اعمال ۳:۱۶, G2316");
});

test("other languages, form fields and editable text keep ASCII", () => {
  const { G, body } = load();
  const en = body.append(new Element("SPAN", { lang: "en" }, [new Text("John 3:16")]));
  const code = body.append(new Element("CODE", {}, [new Text("12")]));
  const note = body.append(new Element("DIV", { contenteditable: "" }, [new Text("12")]));
  [en, code, note].forEach(G.sweep);
  assert.equal(en.children[0].nodeValue, "John 3:16");
  assert.equal(code.children[0].nodeValue, "12");
  assert.equal(note.children[0].nodeValue, "12");
});

test("Persian text on an English page", () => {
  const { G, body } = load({ lang: "en" });
  const fa = body.append(new Element("P", { lang: "fa" }, [new Text("3")]));
  const en = body.append(new Element("P", {}, [new Text("3")]));
  [fa, en].forEach(G.sweep);
  assert.equal(fa.children[0].nodeValue, "۳");
  assert.equal(en.children[0].nodeValue, "3");
});
