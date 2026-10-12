"""One build of the site for the whole test run. A build takes most of a
minute, and the test classes that read built pages only read them, so they
share this one instead of building their own."""
import atexit
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402

_out = None


def built_site():
    """The built site's directory, built on first use. Read it; don't change it."""
    global _out
    if _out is None:
        tmp = Path(tempfile.mkdtemp(prefix="owb-site-"))
        atexit.register(shutil.rmtree, tmp, True)
        build_site.build(tmp / "site")
        _out = tmp / "site"
    return _out
