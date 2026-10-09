"""Locating and reading pinned source data.

Sources live in vendor/<name> (see scripts/fetch_sources.py), or under the
directory named by the OWB_VENDOR environment variable. A source may be a
plain checkout or a git clone without a working tree; in the second case files
are read with `git show <pinned commit>:<path>`.
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = json.loads((ROOT / "sources.lock.json").read_text(encoding="utf-8"))


def vendor_dir():
    return Path(os.environ.get("OWB_VENDOR", ROOT / "vendor"))


def source_dir(name):
    return vendor_dir() / name


def read_text(name, relpath):
    """Return the text of one file of a pinned source."""
    path = source_dir(name) / relpath
    if path.is_file():
        return path.read_text(encoding="utf-8")
    if (source_dir(name) / ".git").exists():
        commit = LOCK[name]["commit"]
        out = subprocess.run(
            ["git", "-C", str(source_dir(name)), "-c", "gc.auto=0",
             "show", f"{commit}:{relpath}"],
            check=True, capture_output=True)
        return out.stdout.decode("utf-8")
    raise FileNotFoundError(
        f"{name}/{relpath} not found under {vendor_dir()}; "
        "run scripts/fetch_sources.py or set OWB_VENDOR")
