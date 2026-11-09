#!/usr/bin/env bash
# tests/memfn/run_d27_region.sh — `make test-memfn-d27region`: the D27
# spec-first suite of the CPU-target scaffolding (tests/memfn/d27_region/,
# match_api.md §6.3.10, §10.7; tuning.md §2.43; limits.md §8.3; cli.md
# §1.24, §2.16), then its self-checked control.
#
#   (1) the suite: exit 0, "checks failed: 0", and at least D27_FLOOR passes
#       (K35: a run that built nothing reads as no failure). 8,154 checks on
#       the dev box (Zen 4); the floor leaves room for a host without AVX2,
#       whose v3 consumer runs the suite drops.
#   (2) the control (learnings §3: the check must be able to go red): the
#       same suite at D27_QUICK=1 with D27_CONTROL=1, which adds one
#       deliberately wrong expectation as an ordinary check, must exit 1 with
#       exactly that one failure.
# Both runs write under $TMPDIR; the suite's products are kept only on its
# failure (run.sh says where), the control's always removed.
set -u
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
SUITE=$ROOT_DIR/tests/memfn/d27_region/run.sh
D27_FLOOR=${D27_FLOOR:-8000}
[ -n "${TIMEOUT_BIN:-}" ] || . "$ROOT_DIR/tests/lib/timeout_bin.sh"
export TIMEOUT_BIN
tmproot=${TMPDIR:-/var/tmp/pcrec-$(id -un)}
log=$(mktemp -p "$tmproot" d27region_log.XXXXXX)
ctl=$(mktemp -d -p "$tmproot" d27region_ctl.XXXXXX)
trap 'rm -rf -- "$log" "$ctl"' EXIT
fail=0

"$TIMEOUT_BIN" 1800 bash "$SUITE" >"$log" 2>&1
rc=$?
np=$(sed -n 's/^checks passed: //p' "$log")
nf=$(sed -n 's/^checks failed: //p' "$log")
if [ "$rc" -eq 0 ] && [ "${nf:-x}" = 0 ] && [ "${np:-0}" -ge "$D27_FLOOR" ]; then
    echo "PASS d27region: $np checks passed, 0 failed (floor $D27_FLOOR)"
else
    echo "FAIL d27region: rc=$rc passed=${np:-?} failed=${nf:-?} (floor $D27_FLOOR)"
    grep -E '^(FAIL|# d27region)' "$log" | head -40
    fail=1
fi

D27_OUT=$ctl D27_QUICK=1 D27_CONTROL=1 "$TIMEOUT_BIN" 1800 bash "$SUITE" >"$log" 2>&1
rc=$?
nf=$(sed -n 's/^checks failed: //p' "$log")
if [ "$rc" -eq 1 ] && [ "${nf:-x}" = 1 ] && grep -q '^FAIL control/WRONG-EXPECTATION ' "$log"; then
    echo "PASS d27region control: the deliberately wrong expectation is the run's one failure"
else
    echo "FAIL d27region control: rc=$rc failed=${nf:-?}; expected rc 1 and only control/WRONG-EXPECTATION"
    grep -E '^(FAIL|# d27region)' "$log" | head -20
    fail=1
fi
exit "$fail"
