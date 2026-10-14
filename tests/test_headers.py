"""The reader site's security headers (render.yaml) and the built pages agree:
the Content-Security-Policy allows the boot script and the <noscript> style
by their hashes, and the pages
load nothing the policy would block. A browser check of the same headers is
described in the pull request that added them."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
from tests.site_build import built_site  # noqa: E402


def static_site_headers(path="/*"):
    """The headers render.yaml gives the static site for path ("/*", "/sw.js"),
    as {name: value}. A small reader for the one shape used there, so the
    tests need no YAML library."""
    text = (ROOT / "render.yaml").read_text(encoding="utf-8")
    site = text[text.index("runtime: static"):text.index("    routes:")]
    headers = {}
    for m in re.finditer(r"- path: (\S+)\n\s+name: (\S+)\n\s+value: (.+)", site):
        value = m[3].strip()
        if value[:1] == '"' and value[-1:] == '"':
            value = value[1:-1]
        if m[1] == path:
            headers[m[2]] = value
    return headers


def csp_directives(policy):
    out = {}
    for part in policy.split(";"):
        words = part.split()
        if words:
            out[words[0]] = words[1:]
    return out


class HeadersTest(unittest.TestCase):
    def test_static_site_headers(self):
        headers = static_site_headers()
        self.assertEqual(headers["Strict-Transport-Security"], "max-age=31536000; includeSubDomains")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("camera=()", headers["Permissions-Policy"])
        csp = csp_directives(headers["Content-Security-Policy"])
        self.assertEqual(csp["frame-ancestors"], ["'none'"])
        self.assertEqual(csp["object-src"], ["'none'"])
        self.assertIn(f"'{build_site.BOOT_SCRIPT_HASH}'", csp["script-src"],
                      "The boot script changed: put its new hash, "
                      f"'{build_site.BOOT_SCRIPT_HASH}', in render.yaml's "
                      "Content-Security-Policy (script-src)")
        self.assertNotIn("'unsafe-inline'", csp["script-src"])
        self.assertIn(f"'{build_site.NOSCRIPT_STYLE_HASH}'", csp["style-src-elem"],
                      "The <noscript> style changed: put its new hash, "
                      f"'{build_site.NOSCRIPT_STYLE_HASH}', in render.yaml's "
                      "Content-Security-Policy (style-src-elem)")
        self.assertNotIn("'unsafe-inline'", csp["style-src-elem"])
        self.assertIn("https://api.openwordbible.org", csp["connect-src"])


class PagesFitPolicyTest(unittest.TestCase):
    """What the browser would block, found in the built pages."""

    @classmethod
    def setUpClass(cls):
        cls.out = built_site()

    def test_pages_need_nothing_the_policy_blocks(self):
        inline = re.compile(r"<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", re.S)
        external = re.compile(r'<(?:script|link|img|iframe|source|video|audio|embed|object)\b[^>]*'
                              r'\b(?:src|href)="(https?:)?//', re.I)
        for path in self.out.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            for attrs, body in inline.findall(text):
                if re.search(r'type="application/(?:ld\+)?json"', attrs):
                    continue   # data (JSON, JSON-LD), not run
                self.assertEqual(body, build_site.BOOT_SCRIPT, f"{path}: an inline script")
            self.assertNotRegex(text, r"<[a-z][^>]*\son[a-z]+=", f"{path}: an inline event handler")
            for body in re.findall(r"<style\b[^>]*>(.*?)</style>", text, re.S):
                self.assertEqual(body, build_site.NOSCRIPT_STYLE, f"{path}: a <style> element")
            self.assertNotRegex(text, r"<base\b", f"{path}: a <base> element")
            self.assertNotRegex(text, r'\b(?:href|src|action)="(?:javascript|data):', path)
            for m in re.finditer(r'<form\b[^>]*\baction="([^"]*)"', text):
                self.assertTrue(m[1].startswith("/"), f"{path}: a form sent to {m[1]}")
            # Links to other sites are fine; loading from them is not.
            for m in external.finditer(text):
                tag = text[m.start():text.index(">", m.start()) + 1]
                self.assertRegex(tag, r'^<link\b[^>]*\brel="(?:canonical|alternate)"', f"{path}: {tag}")

    def test_styles_load_nothing_from_elsewhere(self):
        for path in self.out.glob("*.css"):
            for target in re.findall(r"url\(\s*['\"]?([^'\")]+)", path.read_text(encoding="utf-8")):
                self.assertTrue(target.startswith("/"), f"{path.name}: url({target})")


if __name__ == "__main__":
    unittest.main()
