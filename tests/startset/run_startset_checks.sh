#!/usr/bin/env bash
# tests/startset/run_startset_checks.sh — the `start_set` fact's checks
# ([START-SET] stage 1, D148; `make test-startset`). The checks, their
# independence argument, their floors and what they cannot see are in
# `startset_checks.py`'s header; this wrapper resolves PCREC and forwards the
# PASS/FAIL lines and the trailers (the mech `startset` arm reads them).
#
# Env: PCREC (default <root>/build/pcrec), JOBS.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
export PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
exec python3 "$SCRIPT_DIR/startset_checks.py"
