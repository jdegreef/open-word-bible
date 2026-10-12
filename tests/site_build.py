"""One build of the site for the whole test run. A build takes most of a
minute, and the test classes that read built pages only read them, so they
share this one instead of building their own."""
import atexit
import functools
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
    out = Path(tempfile.mkdtemp(prefix="owb-site-"))
    atexit.register(shutil.rmtree, out, True)
    build_site.build(out)
    return out
