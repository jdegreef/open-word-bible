// The pages cloudflare/worker.js draws: a verse's page in any language
// (the same page as scripts/build_site.py verse_page writes for the verses
// it builds, tests/test_worker.py holds the two to the same HTML) and a
// chapter at its Literal or Readable level. Pure functions of the data the
// Worker loads, so they run in Node for the tests as well as in the Worker.
//
// What they read (build_site.py worker_files, chapter_shared,
// chapter_language_data, verse_files):
//   meta     _worker/meta.json, the same in every language
//   words    _worker/<lang>.json, a language's interface text and names
//   shell    _worker/shell-<lang>.html, a page with slots (meta.slots)
//   shared   chapter-data/<book>/<chapter>.js, the chapter in no language
//   texts    chapter-data/<book>/<chapter>.<lang>.js, the chapter in lang
//   notes    the chapter page's translated notes (its owb-data "notes")
//   verses   verses/<BOOK>/<chapter>.json, every verse at every level

// owb/markup.py's rules (web/markup.js has the reader's copy; the markup
// vectors hold all three to the same answers, tests/js/worker.test.mjs).
const SPAN = /\{\{([a-z_]+):([^{}]*)\}\}/g;
const VERSE = /\\v (\d+) ?/g;
const LINE = / ?\\q ?/g;
export const SETTINGS = ["gender", "christos", "divine_name", "deity_pronoun", "units", "plural_you", "god_term"];
export const DEFAULTS = { deity_pronoun: 1 };

// Text with every setting at its default (markup.render with no settings).
export function render(text) {
  return text.replace(SPAN, (_, name, opts) => {
    const options = opts.split("|");
    const i = SETTINGS.includes(name) && name in DEFAULTS ? DEFAULTS[name] : 0;
    return i < options.length ? options[i] : options[0];
  });
}

// markup.split_verses: [[null, first part], [13, rest], ...].
export function splitVerses(text) {
  const parts = [];
  let verse = null, pos = 0;
  for (const m of text.matchAll(VERSE)) {
    parts.push([verse, rstrip(text.slice(pos, m.index))]);
    verse = Number(m[1]);
    pos = m.index + m[0].length;
  }
  parts.push([verse, text.slice(pos)]);
  return parts;
}

export const flat = (text) => text.replace(LINE, " ");
// Python's whitespace (str.split, str.strip), not JavaScript's (which
// counts U+FEFF and leaves out U+001C to U+001F and U+0085).
const SPACE = "\t\n\v\f\r\x1c-\x20\x85\xa0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000";
const SPACES = new RegExp(`[${SPACE}]+`);
const LEADING = new RegExp(`^[${SPACE}]+`), TRAILING = new RegExp(`[${SPACE}]+$`);
const rstrip = (text) => text.replace(TRAILING, "");
const strip = (text) => rstrip(text).replace(LEADING, "");
const words = (text) => text.split(SPACES).filter(Boolean);
// build_site.plain: one verse as a reader sees it at the default settings,
// on one line. Spaces inside are kept as they are (French sets a narrow
// no-break space before ";").
export const plain = (text) => strip(flat(render(text).replace(VERSE, "")));

// html.escape: quote (the default) escapes quotes too, for attributes.
export function esc(text, quote = true) {
  let s = String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  if (quote) s = s.replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
  return s;
}

const url = (lang, path) => (lang === "en" ? path : `/${lang}${path}`);
const chapterUrl = (book, chapter) => `/${book.toLowerCase()}/${chapter}/`;
const verseUrl = (ref) => `/${ref.book.toLowerCase()}/${ref.chapter}/${ref.verse}/`;
const format = (template, values) => template.replace(/\{(\w+)\}/g, (all, k) => (k in values ? values[k] : all));

export function parseRef(vid) {
  const [book, chapter, verse] = vid.split(".");
  return { book, chapter: Number(chapter), verse: Number(verse) };
}

const refName = (vid, words_) => {
  const ref = parseRef(vid);
  return `${words_.books[ref.book]} ${ref.chapter}:${ref.verse}`;
};

// build_site.ld_script.
const ld = (data) => `<script type="application/ld+json">${JSON.stringify(data).replace(/</g, "\\u003c")}</script>`;

function breadcrumbLd(meta, lang, crumbs) {
  return ld({ "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement:
    crumbs.map(([name, path], i) => ({ "@type": "ListItem", position: i + 1, name, item: meta.siteUrl + url(lang, path) })) });
}

// text_width and shorten, for a meta description.
function wide(meta, cp) {
  const ranges = meta.wide;
  let lo = 0, hi = ranges.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (cp < ranges[mid][0]) hi = mid - 1;
    else if (cp > ranges[mid][1]) lo = mid + 1;
    else return true;
  }
  return false;
}

const charWidth = (meta, c) => (wide(meta, c.codePointAt(0)) ? 2 : 1);

export function shorten(meta, text, limit = 160) {
  text = words(text).join(" ");
  const chars = Array.from(text);
  if (chars.reduce((n, c) => n + charWidth(meta, c), 0) <= limit) return text;
  const cut = [];
  let width = 0;
  for (const c of chars) {
    width += charWidth(meta, c);
    if (width > limit - 1) break;
    cut.push(c);
  }
  const s = cut.join("");
  const half = Math.floor(cut.length / 2);
  const at = (stop) => {
    const i = s.lastIndexOf(stop);
    return i < 0 ? -1 : Array.from(s.slice(0, i)).length;
  };
  for (const stop of [". ", "。", "। ", "። ", "! ", "? "]) {
    const i = at(stop);
    if (i >= half) return rstrip(cut.slice(0, i + Array.from(stop).length).join(""));
  }
  const i = at(" ");
  return (i >= half ? cut.slice(0, i).join("") : s).replace(/[,;:、，]+$/u, "") + "…";
}

// isolate_directions and localize_digits, for the body a page is given:
// the shell's own header and footer were done when it was built.
const TAG = /<(\/?)([a-zA-Z][a-zA-Z0-9-]*)((?:[^>"']|"[^"]*"|'[^']*')*)>/g;
const ATTR_LANG = /\slang="([^"]*)"/;
const ATTR_DIR = /\sdir="([^"]*)"/;
const VOID = new Set("area base br col embed hr img input link meta source track wbr".split(" "));
const RAW = new Set(["script", "style"]);
const KEEP = new Set(["script", "style", "code", "pre", "textarea"]);
const NUMBER = /&#?[0-9A-Za-z]+;|(?<![A-Za-z0-9])[0-9]+(?![A-Za-z])/g;

const direction = (meta, code) => (meta.rtl.includes(code.split("-")[0]) ? "rtl" : "ltr");
const digitsOf = (meta, code) => (code ? meta.digits[code.split("-")[0]] || null : null);

function popTo(stack, name) {
  const i = stack.map((s) => s[0]).lastIndexOf(name);
  if (i >= 1) stack.length = i;
}

export function isolateDirections(meta, text, base) {
  const out = [], stack = [["", base]];
  let pos = 0;
  for (;;) {
    TAG.lastIndex = pos;
    const m = TAG.exec(text);
    if (!m) break;
    const [whole, closing, rawName, attrs] = m;
    const name = rawName.toLowerCase();
    out.push(text.slice(pos, m.index));
    pos = m.index + whole.length;
    if (closing) {
      out.push(whole);
      popTo(stack, name);
      continue;
    }
    const around = stack[stack.length - 1][1];
    const own = ATTR_DIR.exec(attrs);
    let tag = whole, here;
    if (own && (own[1] === "ltr" || own[1] === "rtl")) here = own[1];
    else if (own) here = around;
    else {
      const code = ATTR_LANG.exec(attrs);
      here = code && code[1] ? direction(meta, code[1]) : around;
      if (here !== around) {
        const at = 1 + closing.length + rawName.length + code.index + code[0].length;
        tag = `${tag.slice(0, at)} dir="${here}"${tag.slice(at)}`;
      }
    }
    out.push(tag);
    if (RAW.has(name)) {
      let end = text.indexOf(`</${name}`, pos);
      if (end < 0) end = text.length;
      out.push(text.slice(pos, end));
      pos = end;
    } else if (!VOID.has(name) && !attrs.trimEnd().endsWith("/")) {
      stack.push([name, here]);
    }
  }
  out.push(text.slice(pos));
  return out.join("");
}

export function localizeDigits(meta, text, base) {
  const swap = (segment, table) => segment.replace(NUMBER, (g) =>
    (g[0] === "&" ? g : g.replace(/[0-9]/g, (d) => Array.from(table)[Number(d)])));
  const out = [], stack = [["", base]];
  let pos = 0;
  for (;;) {
    TAG.lastIndex = pos;
    const m = TAG.exec(text);
    const here = digitsOf(meta, stack[stack.length - 1][1]);
    const segment = m ? text.slice(pos, m.index) : text.slice(pos);
    out.push(here && /[0-9]/.test(segment) ? swap(segment, here) : segment);
    if (!m) break;
    const [whole, closing, rawName, attrs] = m;
    const name = rawName.toLowerCase();
    pos = m.index + whole.length;
    out.push(whole);
    if (closing) {
      popTo(stack, name);
      continue;
    }
    if (RAW.has(name) || KEEP.has(name)) {
      let end = text.indexOf(`</${name}`, pos);
      if (end < 0) end = text.length;
      out.push(text.slice(pos, end));
      pos = end;
    } else if (!VOID.has(name) && !attrs.trimEnd().endsWith("/")) {
      const code = ATTR_LANG.exec(attrs);
      stack.push([name, code && code[1] ? code[1] : stack[stack.length - 1][1]]);
    }
  }
  return out.join("");
}

// build_site.page, from the language's shell: the title, description,
// address, preview image, hreflang links and body put in its slots.
// translated is the languages the page is in.
export function fillShell({ meta, words, shell, lang, title, description, path, card, translated, body }) {
  const s = meta.slots;
  const own = path.replace(/^\/|\/$/g, "");
  let text = shell.replaceAll(s.title, esc(title)).replaceAll(s.description, esc(description))
    .replaceAll(s.path, own);
  const link = (code) => `\n<link rel="alternate" hreflang="${code}" href="${esc(meta.siteUrl + url(code, path))}">`;
  let links = translated.map(link).join("");
  if (translated.length) {
    const fallback = url(translated.includes("en") ? "en" : translated[0], path);
    links += `\n<link rel="alternate" hreflang="x-default" href="${esc(meta.siteUrl + fallback)}">`;
  }
  text = text.replace(/(?:\n<link rel="alternate" hreflang="[^"]*" href="[^"]*">)+/, () => links);
  text = text.replace(/<meta name="owb-langs" content="[^"]*">/, () => `<meta name="owb-langs" content="${translated.join(" ")}">`);
  // The language switch leads to Read in a language the page is not in,
  // and the footer's says it is not translated there yet.
  const missing = meta.languages.filter((code) => !translated.includes(code));
  const toRead = (code) => `href="${url(code, "/read/")}" hreflang="${code}"`;
  for (const code of missing) text = text.replaceAll(`href="${url(code, path)}" hreflang="${code}"`, toRead(code));
  const at = text.indexOf('<nav class="foot-langs"');
  if (at >= 0) {
    const end = text.indexOf("</nav>", at);
    let foot = text.slice(at, end);
    for (const code of missing) {
      const quoted = toRead(code).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      foot = foot.replace(new RegExp(`(<a ${quoted}[^>]*>[\\s\\S]*?)</a>`),
                          (_, link) => `${link} <span class="lang-where">${words.notTranslated}</span></a>`);
    }
    text = text.slice(0, at) + foot + text.slice(end);
  }
  if (card && meta.cards.includes(card)) {
    text = text.replaceAll(`${meta.siteUrl}/og/site.jpg`, `${meta.siteUrl}/og/${card}.jpg`);
  }
  if (meta.rtlReading) body = isolateDirections(meta, body, direction(meta, lang));
  text = text.replace(s.body, () => body);
  // Digits once the page is whole, since the address the footer prints
  // (and the body) came in after the shell's own were done; a second pass
  // leaves those as they are.
  const start = text.indexOf("<body>");
  const digitCodes = Object.keys(meta.digits);
  if (digitCodes.length && (digitsOf(meta, lang) || digitCodes.some((code) => text.includes(`lang="${code}`, start)))) {
    text = text.slice(0, start) + localizeDigits(meta, text.slice(start), lang);
  }
  return text;
}

// The chapter's data files as JSON: the scripts set a global to it.
export function scriptData(text) {
  const start = text.indexOf("=", text.lastIndexOf("window.OWB_"));
  return JSON.parse(text.slice(start + 1).trim().replace(/;$/, ""));
}

// The translated notes from a chapter page (its owb-data).
export function pageNotes(html) {
  const m = html.match(/<script type="application\/json" id="owb-data">([\s\S]*?)<\/script>/);
  return m ? JSON.parse(m[1]).notes || {} : {};
}

// export.record_verses for one language: {verse id: {level: text}}.
function recordVerses(r, levels) {
  const out = {};
  for (const [level, text] of Object.entries(levels || {})) {
    const parts = splitVerses(text);
    if (parts.length !== r.refs.length) continue;
    r.refs.forEach((vid, i) => { (out[vid] = out[vid] || {})[level] = strip(parts[i][1]); });
  }
  return out;
}

// The records a verse is in, and the languages its page is in.
export function verseRecords(shared, vid) {
  return shared.records.filter((r) => r.refs.includes(vid));
}

export const verseLanguages = (meta, rs) =>
  meta.languages.filter((code) => rs.length && rs.every((r) => (r.languages || []).includes(code)));

// The verses of a chapter with a page in lang (chapter_verse_pages).
export function chapterVersePages(meta, shared, book, chapter, lang) {
  const seen = new Map();
  for (const r of shared.records) {
    for (const vid of r.refs) {
      if (parseRef(vid).chapter !== chapter) continue;
      const have = new Set(r.languages || []);
      seen.set(vid, seen.has(vid) ? new Set([...seen.get(vid)].filter((c) => have.has(c))) : have);
    }
  }
  return [...seen].filter(([, have]) => have.has(lang)).map(([vid]) => vid);
}

function decisionHtml(d, own, lang, cui) {
  const english = lang !== "en" ? ' lang="en"' : "";
  const hasOwn = own && Object.keys(own).length > 0;
  const shown = { ...d, ...(own || {}) };
  const choiceAttr = d.layer === "meaning" && !hasOwn ? english : "";
  const reasonAttr = !(hasOwn && own.reason) ? english : "";
  let out = `<li><p class="vd-choice"${choiceAttr}><strong>${esc(render(shown.choice), false)}</strong>`;
  if (d.uncertain) out += ` <span class="vd-unsure">${esc(cui.uncertain, false)}</span>`;
  out += "</p>";
  if (shown.alternatives && shown.alternatives.length) {
    const alts = shown.alternatives.map(render).join("; ");
    out += `<p class="vd-alts">${esc(cui.also, false)}<span${choiceAttr}>${esc(alts, false)}</span></p>`;
  }
  if (shown.reason) out += `<p class="vd-reason"${reasonAttr}>${esc(render(shown.reason), false)}</p>`;
  return out + "</li>";
}

// build_site.verse_page: the page of vid (a verse of book chapter) in lang.
// Null when its sentences are not all in lang.
export function versePage({ meta, words: w, shell, shared, texts, notes, editions, lang, vid }) {
  const ref = parseRef(vid);
  const { book, chapter } = ref;
  const rs = verseRecords(shared, vid);
  if (!rs.length || !rs.every((r) => texts.renderings[r.id])) return null;
  const { ui, cui, levels: names } = w;
  const source = meta.ot.includes(book) ? "hbo" : "grc";
  const suffix = source === "hbo" ? "_hbo" : "";
  const name = refName(vid, w);
  const levels = {};
  for (const r of rs) {
    for (const [level, text] of Object.entries(recordVerses(r, texts.renderings[r.id])[vid] || {})) {
      const p = plain(text);
      levels[level] = level in levels ? `${levels[level]} ${p}` : p;
    }
  }
  const levelRows = [..."BLR"].filter((c) => c in levels)
    .map((c) => `<div class="vl-row"><dt>${names[c]}</dt><dd>${esc(levels[c], false)}</dd></div>`).join("");
  let gloss = "";
  if (lang === "en" && rs.length === 1 && rs[0].refs.length === 1 && rs[0].refs[0] === vid && rs[0].literal_gloss) {
    gloss = `<section class="verse-section"><h2>${ui.gloss}</h2>`
      + `<p class="verse-gloss">${esc(rs[0].literal_gloss, false)}</p></section>`;
  }
  const verseWords = shared.words[vid] || [];
  const original = strip(verseWords.map((x) => {
    const after = "after" in x ? x.after : " ";
    return x.text + (source === "hbo" || after.endsWith(" ") ? after : after + " ");
  }).join(""));
  const dir = source === "hbo" ? ' dir="rtl"' : "";
  const hebrew = meta.hebrewNumbers[vid];
  const numbering = hebrew && source === "hbo"
    ? `<p class="fine">${format(ui.hebrew_number, { ref: esc(refName(hebrew, w)) })}</p>` : "";
  const inVerse = new Set(verseWords.map((x) => x.id));
  const about = (d) => !(d.tokens && d.tokens.length) || d.tokens.some((t) => inVerse.has(t));
  const own = (r, d) => (notes[r.id] || {})[d.id];
  const meaning = rs.flatMap((r) => r.decisions.filter((d) => d.layer === "meaning" && about(d))
    .map((d) => decisionHtml(d, own(r, d), lang, cui))).join("");
  const wording = rs.flatMap((r) => (texts.decisions[r.id] || [])
    .filter((d) => d.layer !== "meaning" && d.language === lang && about(d))
    .map((d) => decisionHtml(d, own(r, d), lang, cui))).join("");
  let why = "";
  if (meaning || wording) {
    why = `<section class="verse-section"><h2>${esc(format(ui.meaning_q, { ref: name }), false)}</h2>`
      + (meaning ? `<h3>${cui.meaning}</h3><ul class="verse-decisions">${meaning}</ul>` : "")
      + (wording ? `<h3>${cui.wording}</h3><ul class="verse-decisions">${wording}</ul>` : "")
      + "</section>";
  }
  const chapterLink = url(lang, chapterUrl(book, chapter)) + `#v${ref.verse}`;
  const near = chapterVersePages(meta, shared, book, chapter, lang);
  const at = near.indexOf(vid);
  const turns = [[at > 0 ? near[at - 1] : null, "prev"], [at + 1 < near.length ? near[at + 1] : null, "next"]]
    .filter(([v]) => v)
    .map(([v, rel]) => `<a class="button ghost" href="${url(lang, verseUrl(parseRef(v)))}" rel="${rel}">${esc(refName(v, w))}</a>`)
    .join("");
  const path = verseUrl(ref);
  const chapterName = w.chapters[`${book}.${chapter}`];
  const site = meta.siteUrl;
  const sourceText = meta.sources[source];
  const verseLd = ld({ "@context": "https://schema.org", "@type": "CreativeWork", "@id": `${site}${url(lang, path)}#verse`,
    name, url: site + url(lang, path), inLanguage: lang, text: levels.B || "", license: meta.cc0,
    creativeWorkStatus: rs.some((r) => r.status === "ai_draft") ? "Draft" : "Published",
    isPartOf: { "@type": "Chapter", "@id": `${site}${url(lang, chapterUrl(book, chapter))}#chapter`,
                name: `${w.books[book]} ${chapter}`, url: site + url(lang, chapterUrl(book, chapter)) },
    translationOfWork: sourceText, isBasedOn: sourceText });
  const crumbs = breadcrumbLd(meta, lang, [...w.crumbs[book], [chapterName, chapterUrl(book, chapter)], [name, path]]);
  // The verse in the public-domain Bibles in the page's language
  // (build_site.verse_comparison_html), for comparison only.
  const verse = String(ref.verse);
  const others = meta.editions.filter(([code, , elang]) => elang === lang && editions?.[code]?.[verse])
    .map(([code, title]) => `<div class="vl-row"><dt>${esc(title)}</dt><dd>${esc(editions[code][verse], false)}</dd></div>`)
    .join("");
  // The topics whose passages include the verse (build_site.verse_topics_html).
  const found = w.topics.filter((x) => x.verses.includes(vid));
  const topics = found.length
    ? `<p class="verse-pages">${w.topicsTitle}: ${found.map((x) => `<a href="${x.href}">${esc(x.name)}</a>`).join(" · ")}</p>`
    : "";
  const compared = others
    ? `<section class="verse-section verse-others"><h2>${esc(cui.title.replace("{ref}", name), false)}</h2>`
      + `<dl class="verse-levels">${others}</dl></section>`
    : "";
  const body = `
<article class="article verse-page">
<header class="article-head">
<p class="eyebrow"><a href="${url(lang, chapterUrl(book, chapter))}">${esc(`${w.books[book]} ${chapter}`)}</a></p>
<h1>${esc(name)}</h1>
<p class="notice">${ui.draft}</p>
</header>
<dl class="verse-levels">${levelRows}</dl>
${numbering}
<section class="verse-section"><h2>${ui["original" + suffix]}</h2>
<p class="verse-original" lang="${source}"${dir}>${esc(original, false)}</p></section>
${gloss}
${why}
${compared}
${topics}
<p class="actions"><a class="button" href="${chapterLink}">${cui.read}&nbsp;${w.forward}</a>
<a class="button ghost" href="${url(lang, "/compare/")}?v=${vid}">${esc(cui.title.replace("{ref}", name))}</a></p>
${turns ? `<p class="actions verse-turns">${turns}</p>` : ""}
</article>
${verseLd}
${crumbs}
`;
  return fillShell({ meta, words: w, shell, lang, path, body, translated: verseLanguages(meta, rs),
    title: format(ui["title" + suffix] || ui.title, { ref: name }),
    description: levels.B ? shorten(meta, `${name}: ${levels.B}`) : format(ui["description" + suffix], { ref: name }),
    card: `${book.toLowerCase()}-${chapter}` });
}

// A chapter at the Literal (L) or Readable (R) level, set as the reader's
// edition sets it (web/edition.js): paragraphs, poetry in lines, and each
// verse number a link to its page. Null when the chapter is not wholly in
// lang.
export function levelPage({ meta, words: w, shell, verses, lang, book, chapter, level }) {
  const key = `${book}.${chapter}`;
  const translated = meta.chapterLanguages[key] || [];
  if (!translated.includes(lang)) return null;
  const lp = w.levelPage;
  const chapterName = w.chapters[key];
  const title = format(lp[`title_${level}`], { chapter: chapterName });
  const path = `${chapterUrl(book, chapter)}${meta.levelPaths[level]}/`;
  const starts = new Set(verses.p || []);
  const poetry = new Set(((verses.q || {})[lang]) || []);
  const list = Object.keys(verses.v).map(Number).sort((a, b) => a - b)
    .map((n) => [n, ((verses.v[String(n)] || {})[lang] || {})[level]]).filter(([, t]) => t);
  const paras = [];
  let para = null, wasPoem = false, first = "";
  for (const [n, raw] of list) {
    const text = render(raw).replace(VERSE, " ");
    const poem = poetry.has(n);
    if (poem || wasPoem || !para || starts.has(n)) {
      para = { cls: poem ? "ed-pp" + (starts.has(n) && paras.length ? " ed-stanza" : "") : (wasPoem ? "ed-after" : ""), parts: [] };
      paras.push(para);
    }
    const number = n ? `<sup><a class="vn-link" href="${url(lang, `${chapterUrl(book, chapter)}${n}/`)}">${n}</a></sup>` : "";
    const lines = text.split(LINE).map((l) => esc(l.trim(), false));
    para.parts.push(poem ? number + lines.map((l) => `<span class="ed-line">${l}</span>`).join("")
                         : number + lines.join(" "));
    if (!first) first = plain(raw);
    wasPoem = poem;
  }
  const text = paras.map((p) => `<p${p.cls ? ` class="${p.cls}"` : ""}>${p.parts.join(" ")}</p>`).join("\n");
  const names = w.levels;
  const other = Object.keys(meta.levelPaths).filter((c) => c !== level)
    .map((c) => `<a href="${url(lang, `${chapterUrl(book, chapter)}${meta.levelPaths[c]}/`)}">${esc(names[c])}</a>`);
  other.push(`<a href="${url(lang, chapterUrl(book, chapter))}">${esc(names.B)}</a>`);
  const site = meta.siteUrl;
  const source = meta.sources[meta.ot.includes(book) ? "hbo" : "grc"];
  const pageLd = ld({ "@context": "https://schema.org", "@type": "Chapter", "@id": `${site}${url(lang, path)}#chapter`,
    name: title, url: site + url(lang, path), inLanguage: lang, license: meta.cc0,
    creativeWorkStatus: "Draft", version: names[level],
    workExample: { "@id": `${site}${url(lang, chapterUrl(book, chapter))}#chapter` },
    translationOfWork: source, isBasedOn: source });
  const crumbs = breadcrumbLd(meta, lang, [...w.crumbs[book], [chapterName, chapterUrl(book, chapter)], [title, path]]);
  const body = `
<article class="edition level-page" lang="${lang}">
<header class="edition-head">
<p class="eyebrow"><a href="${url(lang, chapterUrl(book, chapter))}">${esc(chapterName)}</a></p>
<h1>${esc(title)}</h1>
<p class="dek">${esc(lp[`dek_${level}`], false)}</p>
<p class="notice">${w.ui.draft}</p>
<p class="level-pages">${lp.links} ${other.join(" ")}</p>
</header>
<div class="edition-text"><div class="ed-body${poetry.has(list.length ? list[0][0] : -1) ? " ed-poem" : ""}">
${text}
</div></div>
<p class="actions"><a class="button" href="${url(lang, chapterUrl(book, chapter))}?level=${level}">${lp.study}&nbsp;${w.forward}</a></p>
</article>
${pageLd}
${crumbs}
`;
  return fillShell({ meta, words: w, shell, lang, path, body, translated, title,
    description: shorten(meta, `${title}: ${first}`), card: `${book.toLowerCase()}-${chapter}` });
}
