#!/usr/bin/env bash
# tests/spec_history/run_spec_history.sh -- `make test-spec-history`: flags
# build history (dated revision notes, ADDENDUM, walkbacks, panel/ruling
# narrative, row-tag-opened paragraphs) in docs/spec/*.md, with an explicit
# allowlist and a known-debt baseline. The logic and the marker list are in
# spec_history.py beside this file; see this directory's CLAUDE.md.
set -u
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
exec python3 "$ROOT_DIR/tests/spec_history/spec_history.py" "$ROOT_DIR"
