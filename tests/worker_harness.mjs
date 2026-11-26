// Runs cloudflare/worker.js against a directory standing in for the built
// site, for tests/test_worker.py:
//   node tests/worker_harness.mjs <site dir> <path> [<path> ...]
// prints {path: {status, location, body}} as JSON.
import { readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import worker from "../cloudflare/worker.js";

const [dir, ...paths] = process.argv.slice(2);

async function file(path) {
  let full = join(dir, decodeURIComponent(path));
  try {
    if ((await stat(full)).isDirectory()) full = join(full, "index.html");
    return await readFile(full);
  } catch {
    return null;
  }
}

const env = {
  ASSETS: {
    async fetch(request) {
      const body = await file(new URL(request.url).pathname);
      return body === null ? new Response("not found", { status: 404 }) : new Response(body);
    },
  },
};

const out = {};
for (const path of paths) {
  const response = await worker.fetch(new Request(`https://openwordbible.org${path}`), env);
  out[path] = { status: response.status, location: response.headers.get("Location"),
                type: response.headers.get("Content-Type"), body: await response.text() };
}
process.stdout.write(JSON.stringify(out));
