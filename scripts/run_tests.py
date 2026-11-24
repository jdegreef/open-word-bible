#!/usr/bin/env python3
"""Run the unit tests in tests/ several modules at a time.

`python3 -m unittest discover -s tests -t .` runs every module one after
another in one process: about half an hour in CI, most of it in a few
modules. This runs each module in a process of its own, the slowest-looking
first, several at once (-j, default the number of CPUs up to 4), and prints
how long each took, so the run takes about as long as its slowest module.

The modules that read a built site share one build: OWB_BUILT_SITE when it
is set (CI builds the site in the step before), otherwise this builds it
once before starting them.

    python3 scripts/run_tests.py                 # every module
    python3 scripts/run_tests.py test_site test_search
    python3 scripts/run_tests.py -j 2 -v
    python3 scripts/run_tests.py --no-site       # those that don't read a built site

Exit status: 0 when every module passed, 1 otherwise. The output of a
module that failed is printed in full as it finishes.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"


def modules(names=()):
    """The test modules to run, the largest file (a fair guess at the
    slowest) first, so that the long ones don't start last."""
    found = sorted(TESTS.glob("test_*.py"), key=lambda p: (-p.stat().st_size, p.name))
    if not names:
        return [p.stem for p in found]
    wanted = [n.removesuffix(".py").removeprefix("tests.").removeprefix("tests/") for n in names]
    unknown = sorted(set(wanted) - {p.stem for p in found})
    if unknown:
        sys.exit(f"no such test module: {', '.join(unknown)}")
    return [p.stem for p in found if p.stem in wanted]


def needs_site(module):
    """Whether a module reads a built site (tests/site_build.py) or builds one."""
    text = (TESTS / f"{module}.py").read_text(encoding="utf-8")
    return "site_build" in text or "build_site.build(" in text


def run(module, env, verbose):
    start = time.monotonic()
    cmd = [sys.executable, "-m", "unittest", *(["-v"] if verbose else []), f"tests.{module}"]
    proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    return module, proc.returncode, time.monotonic() - start, proc.stdout


def summary_line(output):
    """unittest's last lines: "Ran N tests in Xs" and OK / FAILED (...)."""
    lines = [line for line in output.strip().splitlines() if line.strip()]
    ran = next((line for line in reversed(lines) if line.startswith("Ran ")), "")
    return f"{ran.removeprefix('Ran ')}, {lines[-1]}" if lines else "no output"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("modules", nargs="*", help="test modules (default: all of tests/)")
    parser.add_argument("-j", "--jobs", type=int, default=min(os.cpu_count() or 1, 4))
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--site", action="store_true", help="only the modules that read a built site")
    which.add_argument("--no-site", action="store_true",
                       help="only the modules that don't (CI runs these while it builds the site)")
    parser.add_argument("-v", "--verbose", action="store_true", help="unittest -v in each module")
    args = parser.parse_args(argv)

    todo = modules(args.modules)
    if args.site or args.no_site:
        todo = [m for m in todo if needs_site(m) == args.site]
    env = dict(os.environ)
    if not env.get("OWB_BUILT_SITE") and any(needs_site(m) for m in todo):
        out = Path(tempfile.mkdtemp(prefix="owb-site-"))
        print(f"building the site once for the tests that read it ({out})", flush=True)
        start = time.monotonic()
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py"), "--output", str(out)],
                       cwd=ROOT, check=True)
        print(f"built in {time.monotonic() - start:.0f} s", flush=True)
        env["OWB_BUILT_SITE"] = str(out)
    else:
        out = None

    start = time.monotonic()
    failed = []
    try:
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            jobs = [pool.submit(run, m, env, args.verbose) for m in todo]
            for job in as_completed(jobs):
                module, code, seconds, output = job.result()
                status = "ok" if code == 0 else "FAILED"
                print(f"{seconds:7.1f} s  {status:6}  {module}  ({summary_line(output)})", flush=True)
                if args.verbose or code:
                    print(output, flush=True)
                if code:
                    failed.append(module)
    finally:
        if out:
            shutil.rmtree(out, ignore_errors=True)

    print(f"\n{len(todo)} modules in {time.monotonic() - start:.0f} s with {args.jobs} at a time")
    if failed:
        print(f"FAILED: {' '.join(sorted(failed))}")
        print("Re-run one with: python3 -m unittest -v tests.<module>")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
