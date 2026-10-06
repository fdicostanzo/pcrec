#!/usr/bin/env bash
# tests/codegen/run_cand_rows.sh — the candidate table's structural checks
# (`src/gen/emit_dfa.c`'s `dfa_pfs[]`; D148, docs/design/startset.md §8).
# The checks themselves, their populations and what they cannot see are in
# `cand_rows_check.py`'s header; this wrapper resolves the tree and forwards
# the PASS/FAIL lines and the trailers.
#
# Usage: bash tests/codegen/run_cand_rows.sh [TREE]   (default: this repo)
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
exec python3 "$SCRIPT_DIR/cand_rows_check.py" "${1:-$ROOT_DIR}"
