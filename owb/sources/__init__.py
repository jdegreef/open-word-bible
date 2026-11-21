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


# Variables that point git at a particular repository (`git rev-parse
# --local-env-vars`). Git sets some of them for hooks (GIT_DIR and
# GIT_INDEX_FILE in a linked worktree), and a nested `git -C <vendor clone>`
# would then read the outer repository instead of the clone.
GIT_REPO_ENV = (
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_COUNT", "GIT_OBJECT_DIRECTORY", "GIT_DIR", "GIT_WORK_TREE",
    "GIT_IMPLICIT_WORK_TREE", "GIT_GRAFT_FILE", "GIT_INDEX_FILE",
    "GIT_NO_REPLACE_OBJECTS", "GIT_REPLACE_REF_BASE", "GIT_PREFIX",
    "GIT_SHALLOW_FILE", "GIT_COMMON_DIR",
)


def clone_env():
    """os.environ without the variables that would redirect git away from a
    vendor clone."""
    return {k: v for k, v in os.environ.items() if k not in GIT_REPO_ENV}


def vendor_dir():
    return Path(os.environ.get("OWB_VENDOR", ROOT / "vendor"))


def source_dir(name):
    return vendor_dir() / name


def lfs_path(name, relpath):
    """The downloaded copy of a file a source stores with Git LFS:
    <name>-lfs/<relpath>, where scripts/fetch_sources.py puts it."""
    path = vendor_dir() / f"{name}-lfs" / relpath
    if not path.is_file():
        raise FileNotFoundError(f"{path} missing; run scripts/fetch_sources.py {name}")
    return path


def read_text(name, relpath):
    """Return the text of one file of a pinned source.

    Files stored with Git LFS are read from <name>-lfs/<relpath> (lfs_path).
    """
    if relpath in LOCK[name].get("lfs", {}):
        return lfs_path(name, relpath).read_text(encoding="utf-8")
    path = source_dir(name) / relpath
    if path.is_file():
        return path.read_text(encoding="utf-8")
    if (source_dir(name) / ".git").exists():
        commit = LOCK[name]["commit"]
        out = subprocess.run(
            ["git", "-C", str(source_dir(name)), "-c", "gc.auto=0",
             "show", f"{commit}:{relpath}"],
            check=True, capture_output=True, env=clone_env())
        return out.stdout.decode("utf-8")
    raise FileNotFoundError(
        f"{name}/{relpath} not found under {vendor_dir()}; "
        "run scripts/fetch_sources.py or set OWB_VENDOR")
