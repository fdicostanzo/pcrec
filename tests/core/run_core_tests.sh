#!/usr/bin/env bash
# tests/core/run_core_tests.sh — [REVW.U L5-R0.3] THE DRIVER FOR THIS
# DIRECTORY: unit checks on an internal helper that belongs to no single
# feature (mrl.c/emit_vm.c/callgraph.c's shared saturating-arithmetic
# family is the first; sb.c/arena.c/the growable-array and text-kit
# primitives wave 1 builds are the population this directory is FOR — see
# tests/core/CLAUDE.md). `pcrec_sb_fragf` (wave 2 stage 3) is the second row.
#
# The ten pre-existing unit-shaped checks scattered across six directories
# (tests/codegen/cpset_model_check.c, tests/parse/branch_count_check.c,
# tests/mrl/cwmax_check.c, tests/backrefs/fold_agreement*_check.c,
# tests/utf8/startbnd_backend_check.c, tests/registry/*.c) STAY where they
# are — co-located with the suite that owns their subject, this tree's own
# directory convention. This directory is not a second home for them.
#
# Usage: bash tests/core/run_core_tests.sh
# Env: CC (resolved via cc_resolve.sh), LIBPCREC (default
#   <root>/build/libpcrec.a — SAN-1 override), SANFLAGS (SAN-1, default
#   empty), KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/unit_cc.sh"   # [REVW.U L5-R0] unit_build; also sources cc_resolve.sh
KEEP="${KEEP:-0}"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "core: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---------------------------------------------------------------------------
# [REVW.U L5-R2] the saturating-arithmetic agreement — pcrec_mrl_sat_add/pcrec_vm_fadd/
# pcrec_cg_sat_add and their _mul siblings, checked for cross-family equality and
# the three algebraic laws the callers rely on. See sat_arith_check.c's own
# header for the full argument, the domain choice, and the failing-direction
# story (four sabotages, one of which — the boundary-off-by-one in
# pcrec_mrl_sat_mul — is invisible to every answer-level check in this tree,
# because under-estimating is the safe direction).
# ---------------------------------------------------------------------------
BIN="$WORKDIR/sat_arith_check"
if ! unit_build "$BIN" "$SCRIPT_DIR/sat_arith_check.c"; then
    echo "core: FAILED TO BUILD sat_arith_check.c" >&2
    exit 1
fi
OUT="$WORKDIR/sat_arith_check.out"
"$BIN" | tee "$OUT"
bin_rc="${PIPESTATUS[0]}"   # a pipeline's own $? is tee's, never $BIN's
if [ "$bin_rc" -eq 0 ]; then
    ok "sat_arith_check: $(grep -c '^PASS' "$OUT") sub-checks green"
else
    bad "sat_arith_check: $(grep -c '^FAIL' "$OUT") sub-check(s) failed — see above"
fi

# ---------------------------------------------------------------------------
# [REVW.2] wave 2 stage 3 — `pcrec_sb_fragf`, the fragment primitive. Its promise is
# that truncation is impossible BY CONSTRUCTION, and no answer-level check in
# this tree can see the difference between that holding and an off-by-one in
# its allocation: every corpus test runs at the two-byte prefix `rx`, where
# lens 10 measured that nothing truncates today anyway. See the check's own
# header for the oracle choice and the failing-direction transcript.
# ---------------------------------------------------------------------------
BIN2="$WORKDIR/sb_fragf_check"
if ! unit_build "$BIN2" "$SCRIPT_DIR/sb_fragf_check.c"; then
    echo "core: FAILED TO BUILD sb_fragf_check.c" >&2
    exit 1
fi
OUT2="$WORKDIR/sb_fragf_check.out"
"$BIN2" | tee "$OUT2"
bin2_rc="${PIPESTATUS[0]}"   # a pipeline's own $? is tee's, never $BIN2's
if [ "$bin2_rc" -eq 0 ]; then
    ok "sb_fragf_check: $(grep -c '^PASS' "$OUT2") sub-checks green"
else
    bad "sb_fragf_check: $(grep -c '^FAIL' "$OUT2") sub-check(s) failed — see above"
fi

# ---------------------------------------------------------------------------
# [REVW.2] wave 2, EP2 step 10 / lens 1 X8 — `sb_stampf`/`pcrec_sb_stampwf`/
# `pcrec_sb_stamp_str`, the artifact-stamp primitives. UNLIKE `pcrec_sb_fragf` above,
# every byte these write lands in the emitted `.c`, so the four byte-identity
# gates DO see a defect in them; what this check adds is WHICH PROPERTY broke
# and the width x name-length space the shipped call sites (two widths, one
# two-byte prefix) never reach. See the check's own header for the argument
# and the four-plant failing-direction transcript.
# ---------------------------------------------------------------------------
BIN3="$WORKDIR/sb_stamp_check"
if ! unit_build "$BIN3" "$SCRIPT_DIR/sb_stamp_check.c"; then
    echo "core: FAILED TO BUILD sb_stamp_check.c" >&2
    exit 1
fi
OUT3="$WORKDIR/sb_stamp_check.out"
"$BIN3" | tee "$OUT3"
bin3_rc="${PIPESTATUS[0]}"   # a pipeline's own $? is tee's, never $BIN3's
if [ "$bin3_rc" -eq 0 ]; then
    ok "sb_stamp_check: $(grep -c '^PASS' "$OUT3") sub-checks green"
else
    bad "sb_stamp_check: $(grep -c '^FAIL' "$OUT3") sub-check(s) failed — see above"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
