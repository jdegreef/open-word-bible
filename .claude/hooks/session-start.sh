#!/bin/bash
# Cloud sessions start from a fresh clone: fetch the pinned sources
# (scripts/fetch_sources.py; already-fetched sources are skipped) and the
# backend's Python packages, so the "Before pushing" checks in CLAUDE.md run.
# The backend tests also need Postgres (DATABASE_URL), which this doesn't set up.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
export OWB_VENDOR="$CLAUDE_PROJECT_DIR/vendor"
echo "export OWB_VENDOR=\"$OWB_VENDOR\"" >> "$CLAUDE_ENV_FILE"

python3 scripts/fetch_sources.py
python3 -m pip install --quiet --disable-pip-version-check -r backend/requirements.txt
# The Greek/Hebrew word list guard_edits.py checks edits against (cached in vendor/).
python3 .claude/hooks/guard_edits.py --build-cache
# Lint and validate what Claude commits (scripts/git-hooks/pre-commit).
git config core.hooksPath scripts/git-hooks
