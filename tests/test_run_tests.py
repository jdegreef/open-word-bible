"""scripts/run_tests.py: the parallel runner CI and check.sh use."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_tests  # noqa: E402


class RunTestsTest(unittest.TestCase):
    def test_every_module_once(self):
        found = run_tests.modules()
        self.assertEqual(sorted(found), sorted(p.stem for p in (ROOT / "tests").glob("test_*.py")))
        self.assertEqual(len(found), len(set(found)))
        self.assertEqual(run_tests.modules(["tests/test_markup.py", "test_digits"]),
                         [m for m in found if m in ("test_markup", "test_digits")])

    def test_site_and_no_site_split_every_module(self):
        site = {m for m in run_tests.modules() if run_tests.needs_site(m)}
        self.assertIn("test_site", site)
        self.assertIn("test_morph", site)  # reads chapter pages through site_build
        self.assertNotIn("test_markup", site)

    def test_summary_line(self):
        out = "....\n" + "-" * 70 + "\nRan 4 tests in 0.01s\n\nOK\n"
        self.assertEqual(run_tests.summary_line(out), "4 tests in 0.01s, OK")

    def test_a_failing_module_fails_the_run(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "run_tests.py"), "no_such_module"],
                              capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("no such test module", proc.stderr)
        self.assertEqual(run_tests.main(["--no-site", "test_markup"]), 0)


if __name__ == "__main__":
    unittest.main()
