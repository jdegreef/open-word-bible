"""One build of the site for the whole test run. A build takes minutes,
and the test classes that read built pages only read them, so they share
this one instead of building their own. With OWB_BUILT_SITE set (CI, which
builds the site in the step before), they read that build instead."""
import atexit
import functools
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


@functools.cache
def built_site():
    """The built site's directory, built on first use. Read it; don't change it."""
    if os.environ.get("OWB_BUILT_SITE"):
        return Path(os.environ["OWB_BUILT_SITE"]).resolve()
    out = Path(tempfile.mkdtemp(prefix="owb-site-"))
    atexit.register(shutil.rmtree, out, True)
    build_site.build(out)
    return out
