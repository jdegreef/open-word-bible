"""Write the built site's _headers and _redirects for Cloudflare
(cloudflare/wrangler.jsonc) from render.yaml's static-site headers and
routes, so the two hosts send the same headers and redirects and there is
one list to keep.

    python3 scripts/build_site.py
    python3 scripts/cloudflare_config.py [site]

Also writes site/_worker/headers.json, the headers of every page ("/*"),
for the pages cloudflare/worker.js draws: Cloudflare sends _headers with
files only.

Reads render.yaml with a small parser for the one shape used there (as
tests/test_headers.py does), so CI needs no YAML library. Fails if
Cloudflare's limits would be passed: 100 header rules, 2,000 characters a
header line, 2,000 static redirects.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEADER_RULES = 100
HEADER_LINE = 2000
REDIRECTS = 2000


def static_site(text):
    """render.yaml's static-site service, as text."""
    start = text.index("runtime: static")
    end = text.index("\n  - type:", start)
    return text[start:end]


def _unquote(value):
    value = value.strip()
    return value[1:-1] if value[:1] == '"' and value[-1:] == '"' else value


def headers(site):
    """[(path, [(name, value), ...]), ...] in render.yaml's order."""
    rules = {}
    block = site[site.index("    headers:"):site.index("    routes:")]
    for m in re.finditer(r"- path: (\S+)\n\s+name: (\S+)\n\s+value: (.+)", block):
        rules.setdefault(m[1], []).append((m[2], _unquote(m[3])))
    return list(rules.items())


def redirects(site):
    """[(source, destination), ...] of the redirect routes."""
    block = site[site.index("    routes:"):]
    return [(m[1], m[2]) for m in re.finditer(
        r"- type: redirect\n\s+source: (\S+)\n\s+destination: (\S+)", block)]


def headers_file(rules):
    lines = []
    for path, pairs in rules:
        lines.append(path)
        lines += [f"  {name}: {value}" for name, value in pairs]
    return "\n".join(lines) + "\n"


def redirects_file(routes):
    return "".join(f"{source} {destination} 301\n" for source, destination in routes)


def check(rules, routes):
    problems = []
    if len(rules) > HEADER_RULES:
        problems.append(f"{len(rules)} header rules, more than Cloudflare's {HEADER_RULES}")
    for path, pairs in rules:
        for name, value in pairs:
            if len(f"{name}: {value}") > HEADER_LINE:
                problems.append(f"{path} {name} is longer than {HEADER_LINE} characters")
    if len(routes) > REDIRECTS:
        problems.append(f"{len(routes)} redirects, more than Cloudflare's {REDIRECTS}")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("site", nargs="?", default=str(ROOT / "site"))
    args = ap.parse_args()
    site = static_site((ROOT / "render.yaml").read_text(encoding="utf-8"))
    rules, routes = headers(site), redirects(site)
    problems = check(rules, routes)
    if problems:
        sys.exit("\n".join(problems))
    out = Path(args.site)
    (out / "_headers").write_text(headers_file(rules), encoding="utf-8")
    (out / "_redirects").write_text(redirects_file(routes), encoding="utf-8")
    (out / "_worker").mkdir(exist_ok=True)
    (out / "_worker" / "headers.json").write_text(json.dumps(dict(rules).get("/*", [])), encoding="utf-8")
    print(f"{len(rules)} header rules, {len(routes)} redirects written to {out}")


if __name__ == "__main__":
    main()
