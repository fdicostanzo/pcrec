#!/bin/bash
# [MEMFN] R4c' (lane r4c2fu): the Linux validation of R4c's review fixes, a
# thin wrapper over memfn_r4c.sh's RERUN mode. Runs
#   gate  scripts/emit_sweep.py --ref 81bc13de, judged by
#         memfn_r4c_gate.py --zero-dumps (0 movers on EVERY stream, dumps
#         and facts included: the ref already carries the memfn-simd rows)
#   mech  S511 S524 S525 S566 S526, ONE id per matrix call (the matrix
#         silently ignores a second id)
# and nothing else (no make test, axes, C11 or I2). Logs: build/scratch/r4c_lx/
# (memfn_r4c.sh's directory; the wrapper's own transcript is r4c2.log there).
#
#     git -C /home/duxevents/pcrec worktree add --detach \
#         /home/duxevents/pcrec/worktrees/r4c2-linux lane/memfn-r4c2   (or the tip's ref)
#     cd /home/duxevents/pcrec/worktrees/r4c2-linux
#     nohup gnutimeout 240m bash docs/design/memfn/probes/lxrun/memfn_r4c2.sh \
#         TIP > r4c2_linux.log 2>&1 &
#
# TIP: the expected `git rev-parse --short HEAD` (the inner script STOPS on a
# mismatch). Env as memfn_r4c.sh: CC, JOBS, LOADWAIT; REF defaults to 81bc13de
# (must be in the box's repo).
# LAST LINE, exactly: `== r4c2-lx DONE rc=N ==`; N is 0 iff the gate judge
# returned 0 AND every mech row's trailer reads unexpected/undetected/
# unreached/anomalies all 0 (memfn_r4c.sh's own mech check: DETECTED with
# reach ok, or the row's definition valid for an expected-valid row) AND
# the inner script reached its completion line. Any other outcome is nonzero.
set -u
TIP=${1:?usage: memfn_r4c2.sh EXPECTED_TIP}
HERE=$(cd "$(dirname "$0")" && pwd)
L=build/scratch/r4c_lx; mkdir -p "$L"
export REF=${REF:-81bc13de} GATEFLAGS=--zero-dumps
export STEPS=gate,mech MECHROWS="S511 S524 S525 S566 S526"
bash "$HERE/memfn_r4c.sh" "$TIP" 2>&1 | tee "$L/r4c2.log"
done_line=$(grep '^R4C-LX-DONE ' "$L/r4c2.log" | tail -1)
rc=0
case "$done_line" in
    *"gate=0 "*"mech=0 "*) ;;
    *) rc=1 ;;
esac
[ -s "$L/mech_fail.txt" ] && rc=1
echo "inner: ${done_line:-<no completion line>}"
echo "== r4c2-lx DONE rc=$rc =="
