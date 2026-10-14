"""Size budgets for the built site: fails when a page, a script or style, the
search index or the whole site grows past its limit, so growth like the
search index's (3 MB to 22 MB a language) is noticed when it happens.

    python3 scripts/build_site.py
    python3 scripts/check_budgets.py [site]

Prints each measure, its limit and the headroom left. Sizes over the network
are gzipped (what a reader downloads); the total is the files on disk. When
a budget fails for a good reason, raise its limit in BUDGETS and say why in
the pull request.
"""
import argparse
import gzip
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

KB = 1024
MB = 1024 * KB

# Limits, about 25% above the largest measured on 2026-10-12 (in brackets).
BUDGETS = {
    # The largest chapter page (/<book>/<chapter>/, in any language)
    # [127 KB, es/jhn/6].
    "chapter_page_gz": 160 * KB,
    # The largest script or style sheet [21 KB, reader.js; 26 KB on
    # 2026-10-13 after the verse panel tools, poetry lines and account sync].
    "js_css_asset_gz": 33 * KB,
    # Every file in the site [703 MB; 909 MB on 2026-10-14 with Numbers to
    # Ruth; 1,110 MB on 2026-10-14 with 1 Kings and Ezra to Job]. Grows with
    # each book translated.
    "site_total": 1400 * MB,
    # The largest static search index, search-<lang>.json [5.6 MB; 23 MB
    # unzipped; 7.4 MB on 2026-10-14 with Numbers to Ruth; 9.1 MB with 1 Kings
    # and Ezra to Job]. Delete this entry when the static index goes; nothing
    # else needs to change.
    "search_index_gz": 11.5 * MB,
}


def gzipped(path):
    return len(gzip.compress(path.read_bytes(), compresslevel=6, mtime=0))


def is_chapter_page(rel):
    """<book>/<chapter>/index.html, optionally under a language: /jhn/1/,
    /es/jhn/1/."""
    parts = rel.parts
    return (len(parts) >= 3 and parts[-1] == "index.html" and parts[-2].isdigit()
            and len(parts) <= 4)


def largest(paths, measure):
    best = (0, None)
    for path in paths:
        size = measure(path)
        if size > best[0]:
            best = (size, path)
    return best


def measure(site):
    """{budget name: (size, the file it is from or None)}, for the budgets
    in BUDGETS."""
    files = [p for p in site.rglob("*") if p.is_file()]
    found = {}
    if "chapter_page_gz" in BUDGETS:
        found["chapter_page_gz"] = largest(
            (p for p in files if is_chapter_page(p.relative_to(site))), gzipped)
    if "js_css_asset_gz" in BUDGETS:
        found["js_css_asset_gz"] = largest((p for p in files if p.suffix in (".js", ".css")), gzipped)
    if "site_total" in BUDGETS:
        found["site_total"] = (sum(p.stat().st_size for p in files), None)
    if "search_index_gz" in BUDGETS:
        found["search_index_gz"] = largest(
            (p for p in files if p.name.startswith("search-") and p.suffix == ".json"), gzipped)
    return found


def human(n):
    return f"{n / MB:.1f} MB" if n >= MB else f"{n / KB:.0f} KB"


def check(site, out=None):
    """Prints the report to out (stdout); returns the names of the budgets
    that failed."""
    out = sys.stdout if out is None else out
    failed = []
    for name, (size, path) in measure(site).items():
        limit = BUDGETS[name]
        where = f"  ({path.relative_to(site)})" if path else ""
        if size > limit:
            failed.append(name)
            status = f"OVER by {human(size - limit)}"
        else:
            status = f"{100 * (limit - size) / limit:.0f}% headroom"
        print(f"{name:18} {human(size):>9} of {human(limit):>9}  {status}{where}", file=out)
    return failed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("site", nargs="?", type=Path, default=ROOT / "site",
                        help="the built site (default: site/)")
    args = parser.parse_args(argv)
    if not (args.site / "index.html").is_file():
        parser.error(f"{args.site} is not a built site; run scripts/build_site.py first")
    failed = check(args.site)
    if failed:
        print(f"\nOver budget: {', '.join(failed)}. Make it smaller, or raise the limit "
              "in scripts/check_budgets.py (BUDGETS) and say why.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
