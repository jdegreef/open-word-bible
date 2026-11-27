"""scripts/cloudflare_config.py: the _headers and _redirects Cloudflare
serves the site with say what render.yaml says, within Cloudflare's limits."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cloudflare_config  # noqa: E402
from tests.test_headers import static_site_headers  # noqa: E402


class CloudflareConfigTest(unittest.TestCase):
    def setUp(self):
        site = cloudflare_config.static_site((ROOT / "render.yaml").read_text(encoding="utf-8"))
        self.rules = cloudflare_config.headers(site)
        self.routes = cloudflare_config.redirects(site)

    def test_same_headers_as_render(self):
        rules = dict(self.rules)
        for path in ("/*", "/sw.js", "/reader.js", "/chapter-data/*"):
            self.assertEqual(dict(rules[path]), static_site_headers(path), path)

    def test_every_redirect(self):
        text = (ROOT / "render.yaml").read_text(encoding="utf-8")
        self.assertEqual(len(self.routes), text.count("- type: redirect"))
        self.assertIn(("/about/status/", "/about/"), self.routes)

    def test_within_cloudflare_limits(self):
        self.assertEqual(cloudflare_config.check(self.rules, self.routes), [])

    def test_files(self):
        with tempfile.TemporaryDirectory() as out:
            sys.argv = ["cloudflare_config.py", out]
            cloudflare_config.main()
            headers = (Path(out) / "_headers").read_text(encoding="utf-8")
            redirects = (Path(out) / "_redirects").read_text(encoding="utf-8")
            worker = json.loads((Path(out) / "_worker" / "headers.json").read_text(encoding="utf-8"))
        self.assertTrue(headers.startswith("/*\n  X-Content-Type-Options: nosniff\n"))
        self.assertIn("/sw.js\n  Cache-Control: no-cache\n", headers)
        self.assertIn("/about/status /about/ 301\n", redirects)
        # The Worker's pages get every page's headers (cloudflare/worker.js).
        self.assertEqual(dict(worker), static_site_headers("/*"))


if __name__ == "__main__":
    unittest.main()
