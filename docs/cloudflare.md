# Serving openwordbible.org from Cloudflare

The reader site is static: `scripts/build_site.py` writes `site/`. CI builds
it on every push to main anyway (`.github/workflows/ci.yml`, about 26
minutes, free for a public repository). Render built it a second time for
each deploy (about 29 minutes, billed as pipeline minutes, inside an 8 GB
build limit) and billed the bandwidth. Deploying CI's build to Cloudflare
Workers static assets ends both bills: assets are served without request or
bandwidth charges.

What is in the repository:

- `cloudflare/wrangler.jsonc`: an assets-only Worker named
  `open-word-bible` serving `site/`.
- `scripts/cloudflare_config.py`: writes `site/_headers` and
  `site/_redirects` from render.yaml's static-site headers and routes, so
  both hosts send the same security and cache headers and redirects.
  `tests/test_cloudflare.py` keeps them in step and within Cloudflare's
  limits (100 header rules, 2,000 redirects).
- The "Deploy to Cloudflare" step at the end of CI's content job, on main
  only, after every check passed. Wrangler uploads only changed files.

## The Worker: pages no file holds

`cloudflare/worker.js` answers only requests no file matches. It draws
two kinds of page the static site has no room for (some 430,000 of them,
past the 100,000 files a version may have):

- every verse's page, `/<book>/<chapter>/<verse>/`, in each language all
  its sentences are in (the build writes only the verses of the day, in
  every language, and in English the verses with a footnoted question of
  meaning);
- each chapter at its Literal and Readable levels,
  `/<book>/<chapter>/literal/` and `/readable/`, in each language the
  chapter is wholly in.

It draws them from files the site already has (`chapter-data/`, `verses/`,
the chapter pages) and from `_worker/`, which the build writes when
`OWB_WORKER_PAGES=1` (CI's build, the one deployed here): a page shell per
language, each language's interface text and names, and what is the same in
all of them. `cloudflare/render.js` holds the drawing, and
`tests/test_worker.py` checks that its verse pages are, byte for byte, the
ones `build_site.py verse_page` writes. With the same flag the chapters
link every verse number and their level pages, and the sitemaps list every
page the Worker draws.

Render's build leaves the flag off, so the site Render serves has none of
these links and nothing changes there. The pages appear for readers once the
domain moves (below).

Requests the Worker answers are billed as Worker requests (the paid plan
includes 10 million a month); files are still served free without it.
The `assets_navigation_has_no_effect` flag in `wrangler.jsonc` is what
lets a browser's visit to a missing file reach the Worker at all.

## Setting it up

1. A Cloudflare account on the **Workers Paid** plan ($5 a month). The site
   has over 50,000 files; the free plan allows 20,000 per version, paid
   100,000 (limits as of November 2026:
   https://developers.cloudflare.com/workers/platform/limits/).
2. An API token with the "Edit Cloudflare Workers" template, and the account
   ID (dashboard, Workers & Pages, right-hand side).
3. Repository secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.
   The next green push to main deploys to
   `open-word-bible.<account>.workers.dev`. Check pages, headers and
   redirects there.

## Moving the domain

1. Add openwordbible.org to Cloudflare (DNS moves to Cloudflare's
   nameservers; copy the existing records first, including
   `api.openwordbible.org`, which stays on Render).
2. On the Worker, Settings, Domains & Routes, add `openwordbible.org` and
   `www.openwordbible.org` as custom domains.
3. Once the site answers from Cloudflare, remove the domains from the
   Render static site, then suspend or delete it (and its entry in
   render.yaml and `deploy.yml`'s site hook).

Until step 3 both hosts are deployed, and nothing changes for readers.

The file count grows by about 2,000 HTML pages and 1,200 chapter data files
for each language; at 100,000 Cloudflare needs fewer files (fewer
placeholder pages, or chapter data combined per book).
