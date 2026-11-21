"""Tell search engines which pages changed in the latest deploy (IndexNow).

    python3 scripts/indexnow.py --previous old.json --save new.json [--dry-run]

IndexNow (https://www.indexnow.org) is how Bing, Yandex, Naver, Seznam and
others hear about new and changed pages without waiting to crawl them; Bing's
index is also what ChatGPT search and Copilot read. One submission reaches
every engine that takes part.

The build writes /indexnow.json (build_site.page_fingerprint): every indexed
page's path and a hash of what it says. This fetches the live one, compares
it with the copy saved by the last run (--previous), and submits the pages
that are new or changed, in batches of at most BATCH. The key file the
engines check, /<KEY>.txt, is written by the build too. With no previous
copy, every page is submitted once. .github/workflows/indexnow.yml runs this
after deploys and keeps the copy between runs.
"""
import argparse
import json
import sys
import urllib.request

SITE = "https://openwordbible.org"
# Not a secret: IndexNow checks that the site serves it at /<KEY>.txt.
KEY = "f5db79c9913ffebba9535b132b22b311"
MANIFEST = "indexnow.json"
ENDPOINT = "https://api.indexnow.org/IndexNow"
BATCH = 10000
USER_AGENT = "OpenWordBible-IndexNow/1.0 (+https://openwordbible.org)"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


def changed(previous, current):
    """The paths in current that are new or whose fingerprint differs from
    previous, in order."""
    return sorted(path for path, mark in current.items() if previous.get(path) != mark)


def submit(urls, site=SITE, dry_run=False):
    """POST urls to IndexNow in batches; returns the HTTP statuses."""
    host = site.split("://", 1)[1]
    statuses = []
    for i in range(0, len(urls), BATCH):
        body = {"host": host, "key": KEY, "keyLocation": f"{site}/{KEY}.txt", "urlList": urls[i:i + BATCH]}
        if dry_run:
            statuses.append(None)
            continue
        request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode("utf-8"), method="POST",
                                         headers={"Content-Type": "application/json; charset=utf-8",
                                                  "User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=60) as response:
            statuses.append(response.status)
    return statuses


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--site", default=SITE)
    ap.add_argument("--previous", help="the manifest saved by the last run, if any")
    ap.add_argument("--save", help="where to save the live manifest for the next run")
    ap.add_argument("--dry-run", action="store_true", help="list the pages without submitting them")
    args = ap.parse_args(argv)
    current = json.loads(fetch(f"{args.site}/{MANIFEST}"))
    if fetch(f"{args.site}/{KEY}.txt").strip() != KEY:
        sys.exit(f"{args.site}/{KEY}.txt does not hold the key; the deploy may not be live yet")
    previous = {}
    if args.previous:
        try:
            with open(args.previous, encoding="utf-8") as f:
                previous = json.load(f)
        except FileNotFoundError:
            pass
    paths = changed(previous, current)
    urls = [args.site + path for path in paths]
    print(f"{len(urls)} of {len(current)} pages new or changed")
    for url in urls[:20]:
        print(" ", url)
    if urls:
        print("statuses:", submit(urls, args.site, args.dry_run))
    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            json.dump(current, f, separators=(",", ":"), sort_keys=True)


if __name__ == "__main__":
    main()
