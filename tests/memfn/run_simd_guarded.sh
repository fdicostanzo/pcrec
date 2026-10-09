#!/usr/bin/env bash
# tests/memfn/run_simd_guarded.sh -- [MEMFN] RQ-3's check (D155 item 9 +
# addendum 2): `make test-memfn-guarded`, in TEST_SECTIONS; mech arm
# `simdguarded` (S699-S703).
#
# Builds the WITNESS compiler (this tree with -DPCREC_SIMD_WITNESS: a
# synthetic CPU-guarded block written through the sink's simd_open/simd_close
# at file scope and at the start of the VM program) and runs
# simd_guarded_check.py over a corpus sample plus named witnesses against the
# tree's own build/pcrec. Two claims:
#   - every artifact's `<PREFIX>_SIMD_GUARDED_BYTES` is at most the sum of its
#     rendered SIMD rows' bounds (simd_bounds.tsv); 0 <= 0 on the plain build
#     today, made non-vacuous by the witness's own row;
#   - the witness build's artifacts equal the plain build's with the blocks
#     and the stamp line removed: every length DECISION (the VM entry-shape
#     knee and VM_PROGRAM_BYTES, the size term and its ladder and trial
#     bound, the caps and the figures they quote) reads the SIMD-off length.
# What it does NOT see: a real SIMD form's own bracket discipline (the kit's
# C18 legs check that its inserted lines are inside its brackets), and a
# length reader that reads a buffer the witness never writes to (the witness
# writes csb at the memfn mark and the VM program buffer at vm_init; a
# reader of hsb or of a scratch buffer is reached only through splices).
#
# Usage: bash tests/memfn/run_simd_guarded.sh [TREE] [--every N]
# Env:   CC (the witness build's compiler), PCREC (default TREE/build/pcrec),
#        SIMD_GUARDED_WITNESS_BIN (skip the build).
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$SCRIPT_DIR/../.."
EVERY=10
while [ $# -gt 0 ]; do
    case "$1" in
        --every) EVERY="$2"; shift 2 ;;
        *) TREE="$1"; shift ;;
    esac
done
TREE="$(cd "$TREE" && pwd)"
. "$TREE/tests/lib/timeout_bin.sh"
. "$TREE/tests/lib/cc_resolve.sh"
PCREC="${PCREC:-$TREE/build/pcrec}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/simdguarded.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

if [ -n "${SIMD_GUARDED_WITNESS_BIN:-}" ]; then
    WIT="$SIMD_GUARDED_WITNESS_BIN"
else
    WIT="$WORK/simdw/pcrec"
    if ! "$TIMEOUT_BIN" 900 make -s -C "$TREE" -j4 CC="${CC:-gcc}" \
            BUILD_DIR="$WORK/simdw" CFLAGS="-O2 -g -DPCREC_SIMD_WITNESS" all \
            > "$WORK/make_simdw.log" 2>&1; then
        echo "FAIL: [simd-guarded-build] the witness build failed (last lines below)"
        tail -20 "$WORK/make_simdw.log"
        echo "checks passed: 0"; echo "checks failed: 1"; exit 1
    fi
fi
if [ ! -x "$PCREC" ] || [ ! -x "$WIT" ]; then
    echo "FAIL: [simd-guarded-build] missing compiler: $PCREC / $WIT"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi
"$TIMEOUT_BIN" 1800 python3 "$TREE/tests/memfn/simd_guarded_check.py" \
    --plain "$PCREC" --witness "$WIT" --every "$EVERY"
