#!/bin/bash
# The "Before pushing" checks from CLAUDE.md in one command: what CI's content
# job runs (.github/workflows/ci.yml).
#
#   scripts/check.sh          everything CI's content job runs
#   scripts/check.sh --fast   lint, reader tests, and (when content/ changed
#                             since origin/main) validation of those books and
#                             the extract checks; no unit tests or build
#
# OWB_VENDOR defaults to vendor/ (scripts/fetch_sources.py). The backend's
# Postgres tests are not run here; see CLAUDE.md.
set -euo pipefail
cd "$(dirname "$0")/.."
export OWB_VENDOR="${OWB_VENDOR:-$PWD/vendor}"

fast=false
[ "${1:-}" = --fast ] && fast=true

step() { printf '\n== %s\n' "$1"; }

step "Lint"
uvx ruff@0.16.9 check .

step "Reader tests"
node --test tests/js/*.test.mjs

step "Message catalogs match English"
python3 scripts/check_catalogs.py

if $fast; then
  # Every record in a book that has a changed file, committed or not.
  books=$( { git diff --name-only origin/main...HEAD -- content; git diff --name-only HEAD -- content;
             git ls-files --others --exclude-standard content; } | cut -d/ -f2 | sort -u)
  if [ -n "$books" ]; then
    step "Validate changed books: $(echo $books)"
    python3 -m owb.validate $(for b in $books; do for f in content/"$b"/*.json; do [ -e "$f" ] && echo "$f"; done; done)
    step "Word extracts are up to date"
    python3 scripts/extract_tokens.py --check
    python3 scripts/extract_comparison.py --check
  else
    step "No changed books: validation and extract checks skipped"
  fi
  printf '\nFast checks passed. Run scripts/check.sh without --fast before pushing.\n'
  exit 0
fi

step "Validate content"
python3 -m owb.validate content/*/*.json

step "Word extracts are up to date"
python3 scripts/extract_tokens.py --check
python3 scripts/extract_comparison.py --check

step "Build the site"
python3 scripts/build_site.py

step "Site size budgets"
python3 scripts/check_budgets.py site

# The tests read the build above (OWB_BUILT_SITE) rather than building again.
step "Unit tests"
OWB_BUILT_SITE=site python3 -m unittest discover -s tests -t .

printf '\nAll checks passed.\n'
