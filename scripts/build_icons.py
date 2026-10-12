"""Draw the app icons in web/icons/ from the site's logo (for the web app
manifest: installing the site and reading offline).

The logo is SVG (FAVICON in build_site.py); app icons must be PNG, so each
size is drawn by headless Chrome or Chromium, as build_og.py draws the share
cards. Run it when the logo changes; the icons are committed, because the
site's build on Render has no browser.

    python3 scripts/build_icons.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_og  # noqa: E402
import build_site  # noqa: E402

OUT = ROOT / "web" / "icons"

# The maskable icon fills the whole square with the logo's colour and keeps
# the book inside the middle 70%, so any mask shape leaves it whole.
MASKABLE = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#3f3d9a"/>
<g transform="translate(9.6 9.6) scale(.7)">
<path d="{build_site.BOOK_PATH}" fill="#faf6ef"/>
{build_site.QUOTES.format(fill="#3f3d9a")}
</g>
</svg>
"""

ICONS = (("icon-192.png", build_site.FAVICON, 192), ("icon-512.png", build_site.FAVICON, 512),
         ("maskable-512.png", MASKABLE, 512), ("apple-touch-icon.png", MASKABLE, 180))


def draw(svg, size, png, browser, tmp):
    page = Path(tmp) / "icon.html"
    page.write_text(f'<!doctype html><style>html,body{{margin:0;background:transparent}}'
                    f'svg{{display:block;width:{size}px;height:{size}px}}</style>{svg}', encoding="utf-8")
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--default-background-color=00000000", f"--window-size={size},{size}",
                    f"--screenshot={png}", page.as_uri()], check=True, capture_output=True)


def main():
    browser = build_og.chrome()
    if not browser:
        raise SystemExit("needs Chrome or Chromium (set OWB_CHROME)")
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, svg, size in ICONS:
            draw(svg, size, OUT / name, browser, tmp)
            print(f"drew web/icons/{name}")


if __name__ == "__main__":
    main()
