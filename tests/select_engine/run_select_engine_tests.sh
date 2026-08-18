#!/usr/bin/env bash
# tests/select_engine/run_select_engine_tests.sh — build and run the [M4.7a]
# SR-8 socket check.
#
# It links against build/libpcrec.a and includes src/core/internal.h, the
# same shape tests/registry/run_registry_tests.sh uses for an internal fact
# no black-box CLI probe can see (see select_engine_check.c's header for
# why this one specifically cannot be a .rxt corpus or a CLI probe).
#
# Usage: bash tests/select_engine/run_select_engine_tests.sh
# Env: CC (default gcc), KEEP=1 to keep the built binary, LIBPCREC (default
#   <repo-root>/build/libpcrec.a — SAN-1 override so this can link a
#   sanitizer-built library), SANFLAGS (default empty — SAN-1: extra flags
#   appended to this file's own test-driver build)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"
SANFLAGS="${SANFLAGS:-}"

LIB="${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}"
if [ ! -f "$LIB" ]; then
    echo "select_engine: $LIB not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "select_engine: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

BIN="$WORKDIR/select_engine_check"
if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" $SANFLAGS \
        -o "$BIN" "$SCRIPT_DIR/select_engine_check.c" "$LIB"; then
    echo "select_engine: FAILED TO BUILD select_engine_check.c" >&2
    exit 1
fi

OUT="$WORKDIR/select_engine_check.out"
"$BIN" 2>&1 | tee "$OUT"
rc=${PIPESTATUS[0]}

# ---- COVERAGE GUARD (the tests/registry/ and tests/reject/ convention: an
# exact count so a deleted check is visible in the diff, plus a manifest so
# it FAILS rather than merely showing up in a diff nobody reads) ----------
n="$(grep -c '^PASS:' "$OUT" || true)"
if [ "${n:-0}" != "3" ]; then
    echo "select_engine: select_engine_check shows $n passing checks (3 expected)." >&2
    rc=1
fi
for needle in \
    "baseline:" \
    "socket: vmonly_seen forces ENGM_VM" \
    "refusal: --engine=dfa refuses through the SHARED"
do
    if ! grep -q "^PASS: $needle" "$OUT"; then
        echo "select_engine: MANIFEST — no passing check matching '$needle'." >&2
        rc=1
    fi
done

exit "$rc"
