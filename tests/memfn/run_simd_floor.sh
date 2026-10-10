#!/usr/bin/env bash
# tests/memfn/run_simd_floor.sh -- C18, the floor rule's four legs and the
# guard lint, plus C9-x86 ([MEMFN] R4e' batch 1, request R-13;
# docs/design/memfn/integration.md §R4.9.8): `make test-memfn-simdfloor`.
# Builds the levels dumper (tests/memfn/simd_levels.c, linked against
# build/libpcrec.a) and runs simd_floor_check.py over the whole corpus and
# the named batch-1 witnesses (its docstring says what each leg checks
# against). Mech arm `simdfloor` (S716-S730).
#
# Usage: bash tests/memfn/run_simd_floor.sh [TREE] [--every N]
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$SCRIPT_DIR/../.."
EVERY=1
while [ $# -gt 0 ]; do
    case "$1" in
        --every) EVERY="$2"; shift 2 ;;
        *) TREE="$1"; shift ;;
    esac
done
TREE="$(cd "$TREE" && pwd)"
. "$TREE/tests/lib/timeout_bin.sh"
PCREC="${PCREC:-$TREE/build/pcrec}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/simdfloor.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
if ! "$TIMEOUT_BIN" 120 "${CC:-gcc}" -O2 -I "$TREE/memfn/include" -o "$WORK/simd_levels" \
        "$TREE/tests/memfn/simd_levels.c" "$TREE/build/libpcrec.a" 2> "$WORK/cc.log"; then
    echo "FAIL: [simd-floor-build] the levels dumper did not build"; cat "$WORK/cc.log"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi
TMPDIR="$WORK" "$TIMEOUT_BIN" 2400 python3 "$TREE/tests/memfn/simd_floor_check.py" --pcrec "$PCREC" \
    --levels "$WORK/simd_levels" --every "$EVERY" --jobs "${SIMD_FLOOR_JOBS:-4}"
