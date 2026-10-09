"""Fetch each pinned source into vendor/<name> (or $OWB_VENDOR/<name>).

Usage: python3 scripts/fetch_sources.py [name ...]

Each source is fetched shallowly at its pinned commit from sources.lock.json
and checked out detached. A source already at its pinned commit is skipped.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True)


def head(path):
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path,
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def fetch(name, repo, commit, vendor):
    dest = vendor / name
    if dest.exists() and head(dest) == commit:
        print(f"{name}: already at {commit[:12]}")
        return
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        git("init", "-q", cwd=dest)
        git("remote", "add", "origin", repo, cwd=dest)
    git("fetch", "--depth", "1", "origin", commit, cwd=dest)
    git("checkout", "-q", "--detach", commit, cwd=dest)
    print(f"{name}: checked out {commit[:12]}")


def main(names):
    lock = json.loads((ROOT / "sources.lock.json").read_text(encoding="utf-8"))
    vendor = Path(os.environ.get("OWB_VENDOR", ROOT / "vendor"))
    for name in names or lock:
        fetch(name, lock[name]["repo"], lock[name]["commit"], vendor)


if __name__ == "__main__":
    main(sys.argv[1:])
