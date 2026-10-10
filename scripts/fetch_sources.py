"""Fetch each pinned source into vendor/<name> (or $OWB_VENDOR/<name>).

Usage: python3 scripts/fetch_sources.py [name ...]

Each source is fetched shallowly at its pinned commit from sources.lock.json
and checked out detached. A source already at its pinned commit is skipped.
A source with "paths" gets a sparse checkout of just those files and folders.
Files a source stores with Git LFS (listed under "lfs" with their SHA-256)
are downloaded to <name>-lfs/<path> and checked against that hash.
"""
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True)


def head(path):
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path,
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def fetch(name, repo, commit, vendor, paths=None):
    dest = vendor / name
    if dest.exists() and head(dest) == commit:
        print(f"{name}: already at {commit[:12]}")
        return
    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        git("init", "-q", cwd=dest)
        git("remote", "add", "origin", repo, cwd=dest)
    if paths:
        git("sparse-checkout", "set", "--no-cone", *paths, cwd=dest)
        git("fetch", "--depth", "1", "--filter=blob:none", "origin", commit, cwd=dest)
    else:
        git("fetch", "--depth", "1", "origin", commit, cwd=dest)
    git("checkout", "-q", "--detach", commit, cwd=dest)
    print(f"{name}: checked out {commit[:12]}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_lfs(name, repo, commit, files, vendor):
    """Download LFS files from GitHub's media host and verify their hashes."""
    owner_repo = repo.removeprefix("https://github.com/")
    for relpath, digest in files.items():
        dest = vendor / f"{name}-lfs" / relpath
        if dest.exists() and sha256(dest) == digest:
            print(f"{name}: {relpath} already present")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://media.githubusercontent.com/media/{owner_repo}/{commit}/{relpath}"
        urllib.request.urlretrieve(url, dest)
        if sha256(dest) != digest:
            dest.unlink()
            raise SystemExit(f"{name}: {relpath} does not match its pinned SHA-256")
        print(f"{name}: downloaded {relpath}")


def main(names):
    lock = json.loads((ROOT / "sources.lock.json").read_text(encoding="utf-8"))
    vendor = Path(os.environ.get("OWB_VENDOR", ROOT / "vendor"))
    for name in names or lock:
        fetch(name, lock[name]["repo"], lock[name]["commit"], vendor, lock[name].get("paths"))
        if "lfs" in lock[name]:
            fetch_lfs(name, lock[name]["repo"], lock[name]["commit"], lock[name]["lfs"], vendor)


if __name__ == "__main__":
    main(sys.argv[1:])
