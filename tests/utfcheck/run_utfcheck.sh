#!/usr/bin/env bash
# tests/utfcheck/run_utfcheck.sh — [UTF-VALID]'s suite (`make test-utfcheck`):
# the `-futf-check` / `-fstartpos-guard=align` differential against
# libpcre2 10.46 and python, per config, plus LB and the byte-inert
# identity. check.py carries the whole rationale; this is the launcher.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
# shellcheck source=../lib/cc_resolve.sh
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-utfcheck.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT
[ -x "$PCREC" ] || { echo "run_utfcheck.sh: FATAL: $PCREC is not built" >&2; exit 1; }
python3 "$ROOT_DIR/tests/utfcheck/check.py" "$PCREC" "$WORKDIR"   # CC: exported by cc_resolve.sh
