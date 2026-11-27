// openwordbible.org on Cloudflare: the built site (site/) is served as it
// is, and this Worker answers only what no file does (wrangler.jsonc): the
// pages the static site has no room for, drawn from the files it already
// has (cloudflare/render.js, build_site.py WORKER_PAGES):
//
//   /<book>/<chapter>/<verse>/            a verse's page, in every language
//   /<lang>/<book>/<chapter>/<verse>/     it is in
//   /<book>/<chapter>/literal/ and        a chapter at the Literal or
//   /<book>/<chapter>/readable/           Readable level, in each language
//                                         it is wholly in
//
// Everything else, and a page that does not exist, goes on to the site's
// 404 page as before. The verses with a page of their own built (the verses
// of the day, and in English every verse with a footnoted question of
// meaning) are files, so they never reach here.
import { levelPage, pageNotes, scriptData, versePage } from "./render.js";

const PAGE = /^\/(?:([a-z]{2,3})\/)?([0-9a-z]{3})\/(\d+)\/(?:(\d+)|(literal|readable))\/$/;

// What is the same for every request of a deploy, kept while this copy of
// the Worker runs (a deploy starts new ones).
const kept = new Map();

async function asset(env, path, as) {
  const response = await env.ASSETS.fetch(new Request(`https://assets.local${path}`));
  if (!response.ok) return null;
  return as === "json" ? response.json() : response.text();
}

function keep(env, path, as) {
  if (!kept.has(path)) {
    kept.set(path, asset(env, path, as).then((value) => {
      if (value === null) kept.delete(path);
      return value;
    }));
  }
  return kept.get(path);
}

async function headers(env) {
  const own = (await keep(env, "/_worker/headers.json", "json")) || [];
  const out = new Headers(own);
  out.set("Content-Type", "text/html; charset=utf-8");
  out.set("Cache-Control", "public, max-age=0, must-revalidate");
  return out;
}

async function draw(env, m) {
  const [, prefix, slug, chapterText, verseText, levelName] = m;
  const meta = await keep(env, "/_worker/meta.json", "json");
  if (!meta) return null;
  const lang = prefix || "en";
  if (prefix === "en" || !meta.languages.includes(lang)) return null;
  const book = slug.toUpperCase();
  const chapter = Number(chapterText);
  const [words, shell] = await Promise.all([keep(env, `/_worker/${lang}.json`, "json"),
                                            keep(env, `/_worker/shell-${lang}.html`, "text")]);
  if (!words || !shell || !(book in words.books) || !words.chapters[`${book}.${chapter}`]) return null;
  const base = `/${slug}/${chapter}`;
  if (levelName) {
    const level = Object.keys(meta.levelPaths).find((code) => meta.levelPaths[code] === levelName);
    const verses = await asset(env, `/verses/${book}/${chapter}.json`, "json");
    return verses && levelPage({ meta, words, shell, verses, lang, book, chapter, level });
  }
  const editionLangs = meta.editions.map(([, , elang]) => elang);
  const [shared, texts, page, editions] = await Promise.all([
    asset(env, `/chapter-data${base}.js`, "text"),
    asset(env, `/chapter-data${base}.${lang}.js`, "text"),
    asset(env, `${lang === "en" ? "" : `/${lang}`}${base}/`, "text"),
    editionLangs.includes(lang) ? asset(env, `/editions/${book}/${chapter}.json`, "json") : null]);
  if (!shared || !texts || !page) return null;
  return versePage({ meta, words, shell, shared: scriptData(shared), texts: scriptData(texts),
                     notes: pageNotes(page), editions, lang, vid: `${book}.${chapter}.${Number(verseText)}` });
}

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    // /jhn/3/16 is /jhn/3/16/, as html_handling has it for files.
    if (!path.endsWith("/") && PAGE.test(`${path}/`)) {
      const to = new URL(request.url);
      to.pathname = `${path}/`;
      return Response.redirect(to.toString(), 301);
    }
    const m = PAGE.exec(path);
    if (m && (request.method === "GET" || request.method === "HEAD")) {
      const html = await draw(env, m);
      if (html) return new Response(request.method === "HEAD" ? null : html, { headers: await headers(env) });
    }
    return env.ASSETS.fetch(request);
  },
};
