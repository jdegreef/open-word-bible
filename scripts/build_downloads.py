"""Make the site's ready-made downloads (build_site.downloads(): every
reading language at every level, as USFM and as JSON zips) and
downloads.json listing them, for the GitHub release the site links to
(.github/workflows/downloads.yml, build_site.DOWNLOADS_RELEASE).

    python3 scripts/build_downloads.py out/
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    files = build_site.downloads()
    for name, data, _ in files.values():
        (out / name).write_bytes(data)
    index = build_site.downloads_index(files)
    (out / build_site.DOWNLOADS_INDEX).write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                  encoding="utf-8")
    print(f"{len(files)} files, {sum(f['size'] for f in index['files']) / 1e6:.1f} MB, in {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "downloads")
