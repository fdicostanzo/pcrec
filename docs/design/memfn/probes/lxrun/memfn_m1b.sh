#!/bin/bash
# [MEMFN] M1b (request R-5, lane m1b): THE LINUX VERDICT RUN for runcmp's
# migration into the kit (zero movers, no abi event). A thin wrapper over
# memfn_r4c.sh's RERUN mode with every step selected, plus `make strict`:
#   strict  make strict (warnings-as-errors, writes nothing)
#   gate    scripts/emit_sweep.py --ref 993f8c1d, judged by memfn_r4c_gate.py
#           --zero-dumps: 0 movers on EVERY stream, the --list-axes dumps
#           (stream 5, the run-overlap rows now read off the kit) included
#   test    the full `make test`; the verdict is the absence of
#           `*** [(Makefile:N: )?test-` lines
#   mech    the re-pointed rows S267 S443 S444 S445 S279 S285 S454, the
#           adjacent rows S514 S516 S528 and the new rows S570-S573, ONE id
#           per matrix call (the matrix silently ignores a second id)
#   axes    the memfn-simd pair over tests/axes/run_axes.sh
#   c11     tests/memfn/run_libc_census.sh (full)
#   i2      every --list-axes flag (-fno-run-overlap, -fno-lit-run and
#           -fno-alt-island among them) and the four --tune positions at
#           BOTH comment tiers, the start arms, the memfn-simd inertness
#           arms and the M1-relevant denies at -e utf8, against a ref build
#           at 993f8c1d (memfn_r4c.sh step 7; memfn_r4c_i2.py judges each)
# Logs: build/scratch/r4c_lx/ (memfn_r4c.sh's directory); this wrapper's own
# transcript is m1b.log there, make strict's is strict.log.
#
#     # on the Mac first: push the branch (and main at 993f8c1d, the REF)
#     git -C /home/duxevents/pcrec worktree add --detach \
#         /home/duxevents/pcrec/worktrees/m1b-linux lane/memfn-m1b   (or the tip's ref)
#     cd /home/duxevents/pcrec/worktrees/m1b-linux
#     nohup gnutimeout 600m bash docs/design/memfn/probes/lxrun/memfn_m1b.sh \
#         TIP > m1b_linux.log 2>&1 &
#
# TIP: the expected `git rev-parse --short HEAD` (the inner script STOPS on a
# mismatch). Env as memfn_r4c.sh: CC (gcc), JOBS (8), LOADWAIT (600 s); REF
# defaults to 993f8c1d (must be in the box's repo).
# EXPECTED WALL: of the order of 5-8 h on ubuntubudu (make test ~40 min, the
# gate and the I2 arms most of the rest); hence the 600m bound above.
# LAST LINE, exactly: `== m1b-lx DONE rc=N ==`; N is 0 iff make strict passed
# AND the inner completion line reads gate=0 test=0 reds=0 mech=0 axes=0
# c11=0 i2=0 AND no mech row failed (mech_fail.txt empty) AND the inner
# script reached its completion line. Any other outcome is nonzero. Read each
# step's log, never this line alone.
set -u
TIP=${1:?usage: memfn_m1b.sh EXPECTED_TIP}
HERE=$(cd "$(dirname "$0")" && pwd)
L=build/scratch/r4c_lx; mkdir -p "$L"
T=gnutimeout; command -v $T >/dev/null || T=timeout
export REF=${REF:-993f8c1d} GATEFLAGS=--zero-dumps
export STEPS=gate,test,mech,axes,c11,i2
export MECHROWS="S267 S443 S444 S445 S279 S285 S454 S514 S516 S528 S570 S571 S572 S573"
{
    echo "M1B-LX start $(date -u +%FT%TZ) tip=$TIP ref=$REF"
    $T 1800 make strict CC="${CC:-gcc}" > "$L/strict.log" 2>&1; s=$?
    echo "strict rc=$s"; tail -2 "$L/strict.log"
    bash "$HERE/memfn_r4c.sh" "$TIP" 2>&1
} | tee "$L/m1b.log"
s=$(sed -n 's/^strict rc=//p' "$L/m1b.log" | tail -1)
done_line=$(grep '^R4C-LX-DONE ' "$L/m1b.log" | tail -1)
rc=0
[ "${s:-1}" = 0 ] || rc=1
case "$done_line" in
    *"gate=0 test=0 reds=0 mech=0 axes=0 c11=0 i2=0 "*) ;;
    *) rc=1 ;;
esac
[ -s "$L/mech_fail.txt" ] && rc=1
echo "strict: rc=${s:-<none>}"
echo "inner: ${done_line:-<no completion line>}"
echo "== m1b-lx DONE rc=$rc =="
