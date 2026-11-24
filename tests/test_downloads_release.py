"""The download page with the files published as a GitHub release
(build_site.DOWNLOADS_RELEASE, .github/workflows/downloads.yml): links and
sizes come from the release's downloads.json, and the site build makes no
zips; when downloads.json can't be read, the files are made as before."""
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402

RELEASE = "https://github.com/example/owb/releases/download/downloads"
INDEX = {"commit": "abc", "generated_at": "2026-11-23T00:00:00Z", "files": [
    {"lang": lang, "level": level, "fmt": fmt, "name": f"owb-{lang}-{level.lower()}-{fmt}.zip", "size": 2_500_000,
     "manifest": {"verses": 31102, "missing": {"count": 0}, "generated_at": "2026-11-23T00:00:00Z"}}
    for lang in ("en", "es") for level in "LBR" for fmt in build_site.DOWNLOAD_FORMATS]}


class ReleasedDownloadsTest(unittest.TestCase):
    def setUp(self):
        build_site.download_listing.cache_clear()
        self.addCleanup(build_site.download_listing.cache_clear)

    def test_the_page_links_the_release(self):
        with mock.patch.object(build_site, "DOWNLOADS_RELEASE", RELEASE), \
                mock.patch.object(build_site, "_released_downloads", return_value=INDEX), \
                mock.patch.object(build_site, "downloads", side_effect=AssertionError("made the zips")):
            listing, released = build_site.download_listing()
            page = build_site.download_page("es")
        self.assertTrue(released)
        self.assertEqual(len(listing), 12)
        self.assertIn(f'href="{RELEASE}/owb-es-b-usfm.zip" download', page)
        self.assertIn(f'href="{RELEASE}/owb-en-r-json.zip" download', page)
        self.assertNotIn('href="/downloads/', page)
        # Spanish first on the Spanish page.
        self.assertLess(page.index('id="dl-es"'), page.index('id="dl-en"'))

    def test_without_the_index_the_files_are_made_here(self):
        made = {("en", "B", "usfm"): ("owb-en-b-usfm.zip", b"zip", INDEX["files"][0]["manifest"])}
        with mock.patch.object(build_site, "DOWNLOADS_RELEASE", RELEASE), \
                mock.patch.object(build_site, "_released_downloads", return_value=None), \
                mock.patch.object(build_site, "downloads", return_value=made):
            listing, released = build_site.download_listing()
        self.assertFalse(released)
        self.assertEqual(listing[("en", "B", "usfm")][2], "/downloads/owb-en-b-usfm.zip")

    def test_the_index_lists_what_the_page_needs(self):
        made = {("en", "B", "usfm"): ("owb-en-b-usfm.zip", b"12345",
                                      {"verses": 9, "missing": {"count": 1, "verses": ["JHN.1.1"]},
                                       "generated_at": "2026-11-23", "status": {}})}
        index = build_site.downloads_index(made)
        self.assertEqual(index["files"], [{"lang": "en", "level": "B", "fmt": "usfm", "name": "owb-en-b-usfm.zip",
                                           "size": 5, "manifest": {"verses": 9, "missing": {"count": 1},
                                                                   "generated_at": "2026-11-23"}}])


if __name__ == "__main__":
    unittest.main()
