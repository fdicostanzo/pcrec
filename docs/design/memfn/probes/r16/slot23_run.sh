#!/bin/bash
# slot23: [MEMFN] R-16 (lane/memfn-r16), the heavy chain of r16b_report §6. RUN ONLY on main's GO.
# Judges: SIMD-off identity sweeps (plain/start/variants) 0 artifact movers; -fmemfn-simd movers only in
# __w16 helpers + the guarded stamp (classifier over EVERY pattern, bad=0); -fmemfn-simd --memfn=no-vrun-kb
# 0 movers; G2 quick+full 0 failed; make test no red lines; mech COMPLETE every column.
# Skipped by the kit manager's call: test-axes (SIMD-off byte-identical; it sweeps no --memfn row), N2
# (no row's applicability changed), the re-timing (w16 now IS the no-vrun-kb text; w32 helper unchanged).
W=/home/pcrec/projects/pcrec/worktrees/memfn
cd $W || exit 1
S=/home/pcrec/projects/pcrec/worktrees/memfn-slot/slot23
trap 'grep -E "^(START|BUILD|STRICT|SABANCHOR|SWEEP|CLASSIFY|G2|MAKE_TEST|MECH|SLOT23_DONE|NO_RED|RED)|\*\*\* \[" $S/run.log > $S/verdict.txt; [ -e $S/DONE ] || touch $S/FAILED' EXIT
# REF = main as merged into lane/memfn-r16 just before the slot (post-L1), so the sweeps see R-16 alone.
TIP=$(git rev-parse --short HEAD); REF=$(git rev-parse --short "$(git merge-base HEAD main)")
rm -rf $S/refsrc; mkdir -p $S/refsrc; git archive $REF | tar -x -C $S/refsrc
gnutimeout 600 make -C $S/refsrc -j16 > $S/refbuild.log 2>&1; echo "BUILD ref rc=$?"; REFBIN=$S/refsrc/build/pcrec
echo "START $(date -Is) tip $TIP ref $REF"
gnutimeout 600 make -j16 > $S/build.log 2>&1; echo "BUILD rc=$?"
gnutimeout 1200 make -j16 strict > $S/strict.log 2>&1; echo "STRICT rc=$?"
python3 scripts/m6read_check_sab_anchors.py > $S/sabanchor.log 2>&1; echo "SABANCHOR rc=$? :: $(tail -1 $S/sabanchor.log)"
sw() { n=$1; shift; gnutimeout 7200 python3 scripts/emit_sweep.py --jobs 16 --out build-emitsweep/slot23-$n "$@" > $S/sweep_$n.log 2>&1; rc=$?; echo "SWEEP $n rc=$rc :: $(awk '/^-- stream:/{s=$3} /population=/{for(i=1;i<=NF;i++) if($i ~ /^movers=/){split($i,a,"="); printf "%s=%s ", s, a[2]}}' $S/sweep_$n.log)$(grep -cE 'FLOOR side' $S/sweep_$n.log) floor-lines"; }
sw plain --ref $REF --tree-rev HEAD
sw start --ref $REF --tree-rev HEAD --arms start
sw variants --ref $REF --tree-rev HEAD --variant all --emit-pins $S/variant_pins.py   # main asked: the 2 thin-tag pins
sw simd --ref $REF --tree-rev HEAD --extra=-fmemfn-simd --no-differ-floor
sw nokbsimd --ref $REF --tree-rev HEAD "--extra=-fmemfn-simd --memfn=no-vrun-kb" --no-differ-floor
gnutimeout 7200 python3 docs/dev/lanes/r16b_movers.py $W 1 $REFBIN > $S/classify.log 2>&1; echo "CLASSIFY rc=$? :: $(tail -1 $S/classify.log)"
TMPDIR=$S gnutimeout 7200 make test-memfn-g2 > $S/g2q.log 2>&1; echo "G2Q rc=$? :: $(grep -E 'checks (passed|failed)' $S/g2q.log | tail -2 | tr '\n' ' ')"
TMPDIR=$S gnutimeout 7200 make test-memfn-g2-full > $S/g2.log 2>&1; echo "G2 rc=$? :: $(grep -E 'checks (passed|failed)' $S/g2.log | tail -2 | tr '\n' ' ')"
t0=$(date +%s); scripts/perfrun --label memfn-r16 -- $S/make_test.log; echo "MAKE_TEST rc=$? wall=$(( $(date +%s)-t0 ))s"
grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' $S/make_test.log && echo "RED_LINES make_test" || echo "NO_RED_LINES make_test"
git checkout -- docs/dev/artifact_size_log.tsv 2>/dev/null
m0=$(date +%s); echo "MECH_START $(date -Is)"
PROCS=4 gnutimeout 7200 bash tests/mech/run_sabotage_matrix.sh $(cat $S/mech_rows.txt) > $S/mech.log 2>&1; mrc=$?; grep -q "== mech run COMPLETE" $S/mech.log || mrc=99; echo "MECH rc=$mrc :: $(grep -E '== mech run COMPLETE' $S/mech.log | tail -1 | sed 's/ at [0-9a-f]* ==//')"
echo "MECH_WALL $(( $(date +%s)-m0 ))s"
echo "SLOT23_DONE $(date -Is)"
touch $S/DONE
