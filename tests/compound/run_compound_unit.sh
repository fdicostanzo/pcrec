#!/usr/bin/env bash
# tests/compound/run_compound_unit.sh -- `make test-compound`: the
# [COMPOUND] build steps' unit checks (docs/design/compound.md §F).
#
#   B0  check_entries.py: an [EMIT-ENTRIES] request leaves exactly its
#       closure, every corpus pattern under three arms (see its header).
#   B1  check_parts.py: part mode and the parts' options -- the split
#       client's F and Q of six witnesses plus a hand controller in one
#       TU -Werror, run against the plain artifact; the 60-byte prefix; K79;
#       the table-build self-check.
#
# The internal driver (compound_drive.c) links build/libpcrec.a through
# tests/lib/unit_cc.sh. Env: PCREC, CC, JOBS (default PROCS, else
# tests/lib/procs_default.sh),
# EVERY (keep every N-th distinct corpus pattern, default 1), KEEP=1.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/unit_cc.sh"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
JOBS="${JOBS:-${PROCS:-$(bash "$ROOT_DIR/tests/lib/procs_default.sh")}}"
EVERY="${EVERY:-1}"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-compound.XXXXXX")"
[ "${KEEP:-0}" = 1 ] || trap 'rm -rf "$WORKDIR"' EXIT

rc=0
DRIVE="$WORKDIR/compound_drive"
if ! unit_build "$DRIVE" "$SCRIPT_DIR/compound_drive.c"; then
    echo "FAIL: test-compound: compound_drive.c did not build"
    exit 1
fi
echo "== B0: entry requests leave exactly their closure =="
CC="$CC" python3 "$SCRIPT_DIR/check_entries.py" "$DRIVE" "$PCREC" "$ROOT_DIR" \
    "$WORKDIR/b0" --every "$EVERY" --jobs "$JOBS" || rc=1
echo "== B1: part mode, the parts' options, one TU =="
CC="$CC" python3 "$SCRIPT_DIR/check_parts.py" "$DRIVE" "$WORKDIR/b1" || rc=1
[ "$rc" -eq 0 ] && echo "test-compound: PASS" || echo "test-compound: FAIL"
exit $rc
