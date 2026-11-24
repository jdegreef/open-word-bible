"""scripts/minify.py: the smaller copies of web/'s scripts and styles that
the site serves mean what the sources mean."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import minify  # noqa: E402

NODE = shutil.which("node")


class ScriptTest(unittest.TestCase):
    def test_comments_and_indentation_go(self):
        self.assertEqual(minify.js("// a note\nfunction f() {\n    /* why */\n    return 1;  // one\n}\n\n\n"),
                         "function f() {\nreturn 1;\n}\n")

    def test_strings_and_templates_stay(self):
        for code in ('var a = "http://x/*y*/";', "var b = 'it\\'s // not a comment';",
                     "var c = `${a}//${b + `/*${c}*/`}`;", "var d = `two  spaces`;"):
            with self.subTest(code=code):
                self.assertEqual(minify.js(code), code + "\n")

    def test_regular_expressions_stay(self):
        for code in ("var r = /\\/\\/[a/]*/g;", "x.replace(/\"/g, '');", "if (!/^a$/.test(s)) return /b/i;",
                     "var q = a / b / c;"):
            with self.subTest(code=code):
                self.assertEqual(minify.js(code), code + "\n")

    def test_lines_stay_apart(self):
        # Every line break is kept, so semicolon insertion reads as before.
        self.assertEqual(minify.js("var a = b\n(c)\nreturn\nx"), "var a = b\n(c)\nreturn\nx\n")

    @unittest.skipUnless(NODE, "node is not installed")
    def test_every_web_script_still_parses(self):
        with tempfile.TemporaryDirectory() as out:
            for path in sorted((ROOT / "web").glob("*.js")):
                small = Path(out) / path.name
                small.write_text(minify.js(path.read_text(encoding="utf-8")), encoding="utf-8")
                run = subprocess.run([NODE, "--check", str(small)], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, f"{path.name}: {run.stderr}")
                self.assertLess(small.stat().st_size, path.stat().st_size, path.name)


class StyleTest(unittest.TestCase):
    def test_comments_and_space_go(self):
        self.assertEqual(minify.css("/* a */\n.a,\n.b  > .c {\n  color: red;\n  margin: 0 auto;\n}\n"),
                         ".a,.b > .c{color: red;margin: 0 auto}\n")

    def test_selectors_and_strings_stay(self):
        self.assertEqual(minify.css('.a :hover { content: "/* x */  y"; }'), '.a :hover{content: "/* x */  y"}\n')
        self.assertEqual(minify.css("@media (min-width: 40em) and (hover: hover) { .a { b: c } }"),
                         "@media (min-width: 40em) and (hover: hover){.a{b: c}}\n")

    def test_the_site_styles_get_smaller(self):
        for name in ("style.css", "admin.css"):
            text = (ROOT / "web" / name).read_text(encoding="utf-8")
            small = minify.css(text)
            self.assertLess(len(small), len(text))
            self.assertEqual(small.count("{"), text.count("{") - _in_comments(text, "{"), name)


def _in_comments(text, char):
    import re
    return sum(c.count(char) for c in re.findall(r"/\*.*?\*/", text, re.S))


if __name__ == "__main__":
    unittest.main()
