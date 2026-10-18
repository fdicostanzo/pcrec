#!/usr/bin/env bash
# tests/spec_history/run_spec_history.sh -- `make test-spec-history`: flags
# build history (dated revision notes, ADDENDUM, walkbacks, panel/ruling
# narrative, row-tag-opened paragraphs) in docs/spec/*.md, with an explicit
# allowlist and a known-debt baseline. The logic and the marker list are in
# spec_history.py beside this file; see this directory's CLAUDE.md. Then the
# hook self-test: the same checkers in --staged mode, planted per case.
set -u
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
rc=0
python3 "$ROOT_DIR/tests/spec_history/spec_history.py" "$ROOT_DIR" || rc=1
# [SPEC-HOOK] the pre-commit gate's planted-case self-test (run_hook_selftest.sh)
bash "$ROOT_DIR/tests/spec_history/run_hook_selftest.sh" || rc=1
exit $rc
