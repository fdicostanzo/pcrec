#!/bin/bash
# [MEMFN] R4c (memfn/docs/requests.md R-4; lanes r4ccore/r4caxis/r4cchecks/
# r4cfix): THE LINUX VERDICT RUN for the M1 migration (the composite PRE site
# + the offset-skip trio rendered by the kit, ZERO MOVERS). One self-contained
# script for ubuntubudu, run through the pcrec manager's executor channel; the
# Mac run is directional only.
#
#     # on the Mac first: git -C /Users/fdicostanzo/pcrec push ubuntubudu \
#     #     lane/memfn-r4c:refs/heads/lane/memfn-r4c   (and main, for REF)
#     git -C /home/duxevents/pcrec worktree add --detach \
#         /home/duxevents/pcrec/worktrees/r4c-linux lane/memfn-r4c
#     cd /home/duxevents/pcrec/worktrees/r4c-linux
#     nohup gnutimeout 600m bash docs/design/memfn/probes/lxrun/memfn_r4c.sh \
#         TIP > r4c_linux.log 2>&1 &
#
# TIP: the expected `git rev-parse --short HEAD` (the script STOPS on a
# mismatch). Env: REF (e6e6d6eb, main's tip the gate compares against; must
# be in the box's repo), CC (gcc), JOBS (8), LOADWAIT (600 s).
#
# Steps, each under gnutimeout; logs under build/scratch/r4c_lx/:
#   0 preflight  df, load1 < 0.5 waited for (LOADWAIT, then logged and run)
#   1 build      make -j$JOBS
#   2 gate       emit_sweep.py --ref $REF: streams 1-4 MUST be 0 movers /
#                0 asymmetric; stream 5 (dumps) moves by exactly the two
#                declared memfn-simd --list-axes rows. memfn_r4c_gate.py
#                (beside this script) judges the log: gate=0 iff exactly
#                that holds, 1 on anything else (no accepted red)
#   3 make test  the verdict: `*** [(Makefile:N: )?test-` lines must be absent
#                (C4's Linux plants ride test-memfn-arch here)
#   4 mech       the 35 rows (CORE's 23 + S518-S529), ONE PER CALL, every
#                one DETECTED with reach ok
#   5 axes       the memfn-simd pair over tests/axes/run_axes.sh
#   6 C11 full   tests/memfn/run_libc_census.sh (identity half: "identical
#                (no SIMD form)")
#   7 I2         every arm x both comment tiers (Q7), main's C0 interface:
#                (a) `--arms start` once (the start-family arms with their
#                    pinned DIFFER floors, byte and utf8);
#                (b) every flag `--list-axes` spells (the comments pair is
#                    the tier, not an arm) plus the four non-zero --tune
#                    positions, each at base "" and base -fcomments;
#                (c) the M1-relevant denies (bits 16/30/31/32/44/45/46, scope
#                    Q7, plus -fno-lit-run) at base `-e utf8`.
#                (b)/(c) run --no-differ-floor: they assert IDENTITY (0
#                movers), and the DIFFER floors exist only for (a)'s arms.
#                Streams c-default,c-vm,emit-ir,composition; a pre-built ref
#                binary at REF. i2=0 iff every arm exits 0; the failing arms
#                are listed in i2_fail.txt.
# COMPLETION LINE: `R4C-LX-DONE gate=<rc> test=<rc> reds=<n> mech=<rc>
# axes=<rc> c11=<rc> i2=<rc> i2arms=<n> wall=<s>s`. PASS is every rc 0 AND reds=0, the count
# of grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' lines in test.log (GNU
# make on Linux prints the Makefile:N: form); read each step's log, never this line alone.
set -u
TIP=${1:?usage: memfn_r4c.sh EXPECTED_TIP}
REF=${REF:-e6e6d6eb}; CC=${CC:-gcc}; JOBS=${JOBS:-8}; LOADWAIT=${LOADWAIT:-600}
T=gnutimeout; command -v $T >/dev/null || T=timeout
L=build/scratch/r4c_lx; mkdir -p "$L"; export TMPDIR=$PWD/build/scratch
t0=$(date +%s)
head=$(git rev-parse --short HEAD)
[ "${head:0:${#TIP}}" = "$TIP" ] || { echo "STOP: HEAD $head != TIP $TIP"; exit 2; }
git cat-file -e "$REF^{commit}" 2>/dev/null || { echo "STOP: REF $REF not in this repo (push/fetch main)"; exit 2; }
echo "R4C-LX start $(date -u +%FT%TZ) head=$head ref=$REF cc=$($CC --version | head -1)"
df -h / | tail -1
w=0; while [ -r /proc/loadavg ] && awk '{exit !($1>=0.5)}' /proc/loadavg && [ $w -lt $LOADWAIT ]; do sleep 30; w=$((w+30)); done
echo "load1=$(cut -d' ' -f1 /proc/loadavg 2>/dev/null) waited=${w}s"
$T 1800 make -j"$JOBS" CC="$CC" > "$L/build.log" 2>&1 || { echo "STOP: build failed ($L/build.log)"; exit 3; }
$T 1800 python3 scripts/emit_sweep.py --ref "$REF" > "$L/gate.log" 2>&1
echo "emit_sweep rc=$? (1 is its own rc for the declared dump mover; the judge decides)"
python3 "$(dirname "$0")/memfn_r4c_gate.py" "$L/gate.log"; g=$?
echo "gate=$g"; grep -E '^-- stream|movers=' "$L/gate.log" | tail -12
$T 10800 make test CC="$CC" > "$L/test.log" 2>&1; tr=$?
echo "test rc=$tr"; grep -nE '\*\*\* \[(Makefile:[0-9]+: )?test-' "$L/test.log"; tail -4 "$L/test.log"
reds=$(grep -cE '\*\*\* \[(Makefile:[0-9]+: )?test-' "$L/test.log")
# the matrix takes ONE id per call (a prefix match): a list after the first
# id is silently ignored, so loop. m=0 iff every row's run exits 0 AND its
# trailer reads `undetected: 0, unreached: 0`; misses go to mech_fail.txt.
m=0; : > "$L/mech_fail.txt"
for id in S464 S265 S454 S185 S447 S450 S455 S279 S285 S460 S511 S514 S287 S293 S463 S470 S471 S277 S316 S452 S459 S278 S449 S518 S519 S520 S521 S522 S523 S524 S525 S526 S527 S528 S529; do
    $T 1800 bash tests/mech/run_sabotage_matrix.sh "$id" > "$L/mech_$id.log" 2>&1; r=$?
    t=$(grep -m1 '== mech run COMPLETE: 1 rows' "$L/mech_$id.log")
    case "$t" in *"unexpected: 0, undetected: 0, unreached: 0, anomalies: 0"*) [ $r -eq 0 ] || { m=1; echo "$id rc=$r" >> "$L/mech_fail.txt"; } ;;
        *) m=1; echo "$id rc=$r trailer=[$t]" >> "$L/mech_fail.txt" ;; esac
done
echo "mech=$m rows=35"; cat "$L/mech_fail.txt"
AXES="-fno-memfn-simd -fmemfn-simd" $T 3600 bash tests/axes/run_axes.sh > "$L/axes.log" 2>&1; a=$?
echo "axes rc=$a"; tail -3 "$L/axes.log"
CC="$CC" $T 3600 bash tests/memfn/run_libc_census.sh > "$L/c11.log" 2>&1; c=$?
echo "c11 rc=$c"; tail -3 "$L/c11.log"
# ---- 7: I2 ----
R=$PWD/$L/refsrc; rm -rf "$R"; mkdir -p "$R"
git archive "$REF" | tar -x -C "$R" && $T 1800 make -C "$R" -j"$JOBS" CC="$CC" > "$L/refbuild.log" 2>&1
RB=$R/build/pcrec; : > "$L/i2_fail.txt"; n=0; i2=0
[ -x "$RB" ] || { echo "i2: ref build failed ($L/refbuild.log)"; i2=3; }
arm() {  # $1 label, rest: emit_sweep args
    local lab=$1; shift; n=$((n+1))
    $T 1800 python3 scripts/emit_sweep.py --ref-bin "$RB" --bin build/pcrec --no-self-check "$@" > "$L/i2_$n.log" 2>&1
    local rc=$?; echo "i2 arm $n [$lab] rc=$rc"
    [ $rc -eq 0 ] || { echo "$n $lab rc=$rc $L/i2_$n.log" >> "$L/i2_fail.txt"; i2=1; }
}
if [ "$i2" -eq 0 ]; then
    arm "arms-start" --arms start
    FLAGS=$(build/pcrec --list-axes | awk -F'\t' '{for(i=1;i<=NF;i++) if ($i ~ /^-f[a-z0-9=|-]+$/) print $i}' | tr '|' '\n' | sort -u | grep -vx -e -fcomments -e -fno-comments)
    for tier in "" "-fcomments"; do
        for f in $FLAGS --tune=min-size --tune=size --tune=speed --tune=max-speed; do
            arm "base=${tier:-none} $f" --streams c-default,c-vm,emit-ir,composition --no-differ-floor --extra-base="$tier" --extra="$f"
        done
    done
    arm "tier -fcomments" --streams c-default,c-vm,emit-ir,composition --no-differ-floor --extra=-fcomments
    for f in -fno-offset-skip -fno-run-prefilter -fno-req-byte -fno-req-run -fno-req-run-fold -fno-req-set-lead -fno-req-handoff -fno-lit-run; do
        arm "base=utf8 $f" --streams c-default,c-vm,emit-ir,composition --no-differ-floor --extra-base="-e utf8" --extra="$f"
    done
fi
echo "i2=$i2 arms=$n"; cat "$L/i2_fail.txt"
echo "R4C-LX-DONE gate=$g test=$tr reds=$reds mech=$m axes=$a c11=$c i2=$i2 i2arms=$n wall=$(( $(date +%s) - t0 ))s"
