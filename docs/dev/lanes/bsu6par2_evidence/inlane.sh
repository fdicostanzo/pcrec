#!/bin/bash
# lane bsu6par2's in-lane proof (run under `scripts/boxlock run -l bsu6par2 -- bash inlane.sh`): the pool's own selftest, then
# a SUBSET of cards.py selftest's units serial (-j 1) vs -j 4, byte-compared; the subset's rows read against job 757's
# serial log (each row present, in order); the planted shared scratch over the same subset. Log: $S/inlane.log.
set -u
S=/var/tmp/pcrec-pcrec/scratch/bsu6par2
W=/home/pcrec/projects/pcrec/worktrees/bsu6par2
CARDS=$W/memfn/tests/span_forms/cards.py
REF=/var/tmp/pcrec-pcrec/scratch/bsu6fix3/selftest_full.log
export TMPDIR=$S/tmp PCREC_TMPDIR=$S/tmp PCREC_TREE=$W
mkdir -p "$TMPDIR"
# drills, F2 (the shared base) and units needing it (G3 1.0 f, H2 hex64 I 1.0 f), a G2 drill, the rule-case block, r38's
# J2 chain (two value units feeding one row unit), rev 11's K6 chain, FORMS8-2 (a subprocess), rev 12's cheap block
# (temp dirs), J2's time_cells drill, J7
SUB=${SUB:-0-23,24,26,35,53,74,159-162,176-179,205,215-217}
mask() { sed -E 's/^((ok  |FAIL) \(r44 E\) .*); draws \[[0-9, ]*\] \/ \[[0-9, ]*\]$/\1; draws <MASKED>/' "$1"; }
{
rc=0
echo "+ parpool selftest"; gnutimeout 120 python3 -I "$W/memfn/tests/parpool.py" selftest || rc=1
for j in 1 4; do
    t0=$(date +%s.%N)
    gnutimeout 1800 python3 -I "$CARDS" selftest -j $j --units "$SUB" > "$S/sub_j$j.out" 2>&1; r=$?
    echo "subset -j $j: rc $r, $(wc -l < "$S/sub_j$j.out") lines, wall $(echo "$(date +%s.%N) - $t0" | bc | cut -c1-6) s; $(tail -1 "$S/sub_j$j.out")"
    [ $r -eq 0 ] || rc=1
done
# the subset label (SUBCHK) and a --units run whose need chain is 4 deep (168 needs 164-167)
grep -q '^selftest (SUBSET [0-9]* of 218 units): 59 checks, 0 failed$' "$S/sub_j4.out" && echo "SUBSET label: ok ($(tail -1 "$S/sub_j4.out"))" || { echo "SUBSET label: MISSING"; rc=1; }
gnutimeout 600 python3 -I "$CARDS" selftest -j 4 --units 168 > "$S/u168.out" 2>&1; echo "units 168 -j 4: rc $?; $(tail -1 "$S/u168.out")"
# the one named exception: the (r44 E) row's draws (os.urandom run ids; differs between two SERIAL runs too)
nm=$(mask "$S/sub_j1.out" | grep -c 'draws <MASKED>')
if diff <(mask "$S/sub_j1.out") <(mask "$S/sub_j4.out") > "$S/sub.diff" && [ "$nm" -eq 1 ]; then echo "IDENTITY subset: -j 1 and -j 4 byte-identical after masking $nm (r44 E) draws line; raw diff lines: $(cmp -l "$S/sub_j1.out" "$S/sub_j4.out" 2>/dev/null | wc -l) bytes differ (that line only: $(diff "$S/sub_j1.out" "$S/sub_j4.out" | grep -c '^<'))"; else echo "IDENTITY subset: DIFFER (masked $nm)"; head "$S/sub.diff"; rc=1; fi
# every subset row in 757's serial log, in the same order (757 complete or not: the rows it has so far)
python3 -I - "$S/sub_j1.out" "$REF" <<'PY' || rc=1
import re, sys
m = lambda l: re.sub(r"; draws \[[0-9, ]*\] / \[[0-9, ]*\]$", "; draws <MASKED>", l)
sub = [m(l) for l in open(sys.argv[1]).read().splitlines()[:-1]]
ref = [m(l) for l in open(sys.argv[2]).read().splitlines()]
pos, miss, absent = 0, [], []
for l in sub:
    try:
        pos = ref.index(l, pos) + 1
    except ValueError:
        (miss if l in ref else absent).append(l)
done = ref and re.match(r"^selftest: \d+ checks", ref[-1])
print("VS 757: %d subset rows; %d found in order; %d out of order; %d not in 757's log%s" % (
    len(sub), len(sub) - len(miss) - len(absent), len(miss), len(absent), "" if done else " (757's log not complete yet)"))
for l in (miss + absent)[:8]:
    print("   ", l[:160])
sys.exit(1 if miss or (absent and done) else 0)
PY
PARPOOL_PLANT=shared-scratch gnutimeout 1800 python3 -I "$CARDS" selftest -j 4 --units "$SUB" > "$S/sub_plant.out" 2>&1
if diff -q <(mask "$S/sub_j1.out") <(mask "$S/sub_plant.out") >/dev/null; then echo "PLANT shared-scratch on the cards subset: IDENTICAL (cards' units name no fixed scratch file: every temp dir is mkdtemp-unique)"; else echo "PLANT shared-scratch on the cards subset: DIFFERS"; fi
echo "INLANE DONE rc=$rc"
} > "$S/inlane.log" 2>&1
tail -1 "$S/inlane.log"
