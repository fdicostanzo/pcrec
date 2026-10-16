#!/usr/bin/env bash
# tests/memfn/run_finder.sh — [MEMFN] R17-b' B1 (lane fdb1): `make
# test-memfn-finder`, the kit's finder table and its B1 entries (the
# define-time query, the measurement set's channel, form hashes, the
# reader declarations, method cards, the pay rule's arithmetic). The checks
# and what each is held against are tests/memfn/finder_check.py's header.
#
# Builds two fixture drivers (tests/memfn/arm_fixtures.c): one against
# build/libpcrec.a (`LIB=` overrides), one against the kit's sources compiled
# here with -DMF_TRACE (every memfn/src/*.c, found, so a new kit file joins),
# whose stderr carries the finder shadow's records. Seconds.
#
# Env: CC (tests/lib/cc_resolve.sh's), LIB, TMPDIR.
set -u
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT/tests/lib/cc_resolve.sh"
LIB="${LIB:-$ROOT/build/libpcrec.a}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/finder.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

if [ ! -f "$LIB" ]; then
    echo "FAIL: $LIB not built (make all first)"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi
"$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" "$ROOT/tests/memfn/arm_fixtures.c" "$LIB" \
    -o "$WORK/fx" || { echo "FAIL: the plain fixture driver does not build"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
mkdir -p "$WORK/kit"
n=0
for s in "$ROOT"/memfn/src/*.c; do
    "$CC" -std=gnu11 -O1 -DMF_TRACE -c -o "$WORK/kit/$(basename "${s%.c}").o" "$s" \
        || { echo "FAIL: $s does not compile with -DMF_TRACE"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
    n=$((n + 1))
done
"$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" "$ROOT/tests/memfn/arm_fixtures.c" "$WORK"/kit/*.o \
    -o "$WORK/fxt" || { echo "FAIL: the traced fixture driver does not build"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
echo "run_finder: $n kit sources traced"
python3 -I "$ROOT/tests/memfn/finder_check.py" --root "$ROOT" --fx "$WORK/fx" \
    --fxt "$WORK/fxt" --tmp "$WORK"
rc=$?
# R17-b' B2 (lane fdb2): R-MS6, the harness-only arm-entry counter
# (tests/memfn/run_arm_reach.sh; needs build/pcrec-harness)
echo "run_finder: the arm-entry counter (R-MS6)"
TMPDIR="$WORK" bash "$ROOT/tests/memfn/run_arm_reach.sh" || rc=1
exit $rc
