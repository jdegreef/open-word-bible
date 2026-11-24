"""build_site.Stages: each part of the build says how long it took and the
peak memory, and the summary warns when Render's limits are near."""
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


class StagesTest(unittest.TestCase):
    def test_lines_and_summary(self):
        out = io.StringIO()
        stage = build_site.Stages(out)
        with stage("chapter data files"):
            pass
        stage.start("pages en")
        stage.end()
        self.assertEqual(stage.summary(), [])
        lines = out.getvalue().splitlines()
        self.assertRegex(lines[0], r"^stage chapter data files: \d+\.\d s, peak memory \d+ MB$")
        self.assertRegex(lines[1], r"^stage pages en: ")
        self.assertRegex(lines[2], r"^build: \d+\.\d min, peak memory \d+ MB; slowest stages: ")

    def test_warns_near_renders_limits(self):
        out = io.StringIO()
        stage = build_site.Stages(out)
        stage.began -= 100 * 60
        with mock.patch.object(build_site, "peak_memory_mb", return_value=7000):
            warnings = stage.summary()
        self.assertEqual(len(warnings), 2)
        self.assertIn("WARNING: the build took 100 min of Render's 120", out.getvalue())
        self.assertIn("WARNING: the build peaked at 7000 MB", out.getvalue())


if __name__ == "__main__":
    unittest.main()
