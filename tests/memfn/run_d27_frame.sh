#!/usr/bin/env bash
# tests/memfn/run_d27_frame.sh — `make test-memfn-d27frame`: the D27
# spec-first suite of 3.0b's seam contract (tests/memfn/d27_frame/, author
# s1owed-d27, adopted by lane d27fix; plan_frame.md §2.1-§2.3, memfn.h's
# mf_wdecide), then its two self-checked controls.
#
#   (1) the suite: exit 0, "checks failed: 0", every floor held (run.sh's
#       own verdict), and at least D27F_FLOOR passes (K35: a run that built
#       nothing reads as no failure). The QUICK tier (gcc -O2: seeds 1-3 on
#       the plain kit, seed 1 on the traced one) by default, 6,903,004
#       checks on the dev box; D27F_FULL=1 runs run.sh's full tier (gcc,
#       clang, gcc ASan+UBSan: 20,709,012 checks), `make test-memfn-d27frame-full`.
#   (2) the control (learnings §3: the check must be able to go red): the
#       quick tier with D27_CONTROL=1 inverts every check's expectation; the
#       run must exit nonzero and every one of its four runs must report every
#       family failed under the sabotage and none silent.
#   (3) the empty generator (D27_EMPTY=1): the floors alone must turn the
#       run red (every run "floors BROKEN").
# Serial: one driver process at a time (parallelism cap 1). Outputs under
# $TMPDIR, removed on success, kept (and named) on a failure.
set -u
ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
SUITE=$ROOT_DIR/tests/memfn/d27_frame/run.sh
D27F_FLOOR=${D27F_FLOOR:-6500000}
[ -n "${D27F_FULL:-}" ] && D27F_FLOOR=${D27F_FULL_FLOOR:-19500000}
[ -n "${TIMEOUT_BIN:-}" ] || . "$ROOT_DIR/tests/lib/timeout_bin.sh"
export TIMEOUT_BIN
tmproot=${TMPDIR:-/var/tmp/pcrec-$(id -un)}
work=$(mktemp -d -p "$tmproot" d27frame_run.XXXXXX)
fail=0

quick=1
[ -n "${D27F_FULL:-}" ] && quick=
D27_OUT=$work/suite D27_QUICK=$quick "$TIMEOUT_BIN" 1800 bash "$SUITE" >"$work/suite.log" 2>&1
rc=$?
np=$(sed -n 's/^checks passed: //p' "$work/suite.log")
nf=$(sed -n 's/^checks failed: //p' "$work/suite.log")
if [ "$rc" -eq 0 ] && [ "${nf:-x}" = 0 ] && [ "${np:-0}" -ge "$D27F_FLOOR" ]; then
    echo "PASS d27frame: $np checks passed, 0 failed, floors held (floor $D27F_FLOOR)"
else
    echo "FAIL d27frame: rc=$rc passed=${np:-?} failed=${nf:-?} (floor $D27F_FLOOR); log $work/suite.log"
    grep -E '^d27:|^    (FAIL|FLOOR)' "$work/suite.log" | head -40
    fail=1
fi

D27_OUT=$work/ctl D27_QUICK=1 D27_CONTROL=1 "$TIMEOUT_BIN" 1800 bash "$SUITE" >"$work/ctl.log" 2>&1
rc=$?
runs=$(grep -c '^d27: .* seed .*: rc ' "$work/ctl.log")
whole=$(grep -cE '\| control: ([0-9]+) of \1 families failed under the sabotage, 0 red without it, 0 silent$' "$work/ctl.log")
if [ "$rc" -ne 0 ] && [ "$runs" -eq 4 ] && [ "$whole" -eq 4 ]; then
    echo "PASS d27frame control: red, every family failed under the sabotage in all 4 runs"
else
    echo "FAIL d27frame control: rc=$rc, $whole of $runs runs (want 4 of 4) with every family red and none silent; log $work/ctl.log"
    grep '^d27:' "$work/ctl.log" | head -10
    fail=1
fi

D27_OUT=$work/empty D27_QUICK=1 D27_EMPTY=1 "$TIMEOUT_BIN" 1800 bash "$SUITE" >"$work/empty.log" 2>&1
rc=$?
broken=$(grep -c '^d27: .* seed .*floors BROKEN' "$work/empty.log")
if [ "$rc" -ne 0 ] && [ "$broken" -eq 4 ]; then
    echo "PASS d27frame empty: red, the floors broken in all 4 runs"
else
    echo "FAIL d27frame empty: rc=$rc, floors broken in $broken of 4 runs; log $work/empty.log"
    fail=1
fi
[ "$fail" -eq 0 ] && rm -rf -- "$work"
exit "$fail"
