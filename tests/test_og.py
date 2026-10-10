"""Link-preview images (scripts/build_og.py, web/og/)."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_og  # noqa: E402
import build_site  # noqa: E402


class ShareCardTest(unittest.TestCase):
    def test_every_card_is_drawn_and_current(self):
        # A stale card means its passage, article or template changed:
        # run python3 scripts/build_og.py (needs Chrome) and commit web/og/.
        manifest = json.loads(build_og.MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(build_og.stale(build_og.cards(), manifest), [])

    def test_every_page_points_at_its_own_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            build_site.build(out)
            for path in out.rglob("index.html"):
                text = path.read_text(encoding="utf-8")
                if '<link rel="canonical"' not in text:
                    continue   # unlisted pages (the account page) have no preview
                image = re.search(r'<meta property="og:image" content="([^"]+)"', text)
                self.assertTrue(image, path)
                name = image[1].removeprefix(build_site.SITE_URL + "/og/")
                self.assertTrue((out / "og" / name).is_file(), (path, name))
                self.assertIn('content="summary_large_image"', text, path)
            jhn = (out / "jhn" / "1" / "index.html").read_text(encoding="utf-8")
            self.assertIn("/og/jhn-1.jpg", jhn)
            article = (out / "articles" / "the-word-was-god" / "index.html").read_text(encoding="utf-8")
            self.assertIn("/og/article-the-word-was-god.jpg", article)


if __name__ == "__main__":
    unittest.main()
