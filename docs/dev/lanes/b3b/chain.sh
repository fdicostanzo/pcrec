#!/bin/bash
# docs/dev/lanes/b3b/chain.sh -- R17-b' B3b's OWED heavy validation (lane b3b, 2026-10-18), modeled on
# worktrees/memfn-slot/b3aheavy/chain2.sh. The lane ran the light list only (docs/dev/lanes/b3b_report.md);
# this is what the kit manager's heavy slot runs, at a PINNED tip in a detached worktree.
#
# ARMING (the manager's): copy this file and its two siblings (mech_rows.txt, mech_score.sh) into the slot
# directory $B, set W (a detached worktree checked out at PIN) and PIN below, then run it DETACHED
# (`nohup setsid bash $B/chain.sh > /dev/null 2>&1 &`), on its own or behind a `.go` waiter. One waiter per
# worktree (docs/dev/lanes/BOILERPLATE.md). It writes only under $B and the detached worktree $W (perfrun
# also writes its per-run ledger to the main tree's gitignored build/perf/ttune/, by its own design).
#
# THE VERDICT is the LAST line of $B/chain.status, anchored: ^CHAIN (COMPLETE|FAILED) (never a substring
# match: one status file carries several STEP lines). Per-step rc lines are `STEP <name> rc=<n>`.
B=${B:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/b3bheavy}
W=${W:-/home/pcrec/projects/pcrec/worktrees/b3b-mt}
PIN=${PIN:-c6029d596}
BASE=c88537116
L=$B/logs
CS=$B/chain.status
mkdir -p $L $B/mech $B/tmp
echo $$ > $B/chain.pid
export TMPDIR=$B/tmp PYTHONDONTWRITEBYTECODE=1
. $B/mech_score.sh
FAILED=""
now() { date -Is; }
st() { echo "STEP $1 $2 $(now)" >> $CS; }
fin() { st "$1" "rc=$2"; [ "$2" -ne 0 ] && FAILED="$FAILED $1"; }
cd $W || { echo "CHAIN FAILED at cd-worktree $(now)" >> $CS; exit 9; }
if [ "$(git rev-parse --short=9 HEAD)" != "$PIN" ]; then echo "CHAIN FAILED at pin-check (HEAD $(git rev-parse --short=9 HEAD) != $PIN) $(now)" >> $CS; exit 9; fi
echo "CHAIN START $(now) tip $(git rev-parse --short HEAD)" >> $CS
# ARM-TIME ROW CHECK (b3brev finding 1): every non-comment line of mech_rows.txt is ONE mech id with no
# suffix (^S[0-9]+$; BOILERPLATE "MECH IDS ARE PASSED WITHOUT A SUFFIX"). A bare `S` or a suffixed id would
# run the wrong row set (a bare `S` matches every row's prefix in run_sabotage_matrix.sh) and still score.
badrow=$(grep -v '^#' $B/mech_rows.txt | grep -vE '^S[0-9]+$' | head -3 | tr '\n' ' ')
if [ -n "$badrow" ] || [ "$(grep -vc '^#' $B/mech_rows.txt)" -eq 0 ]; then
  echo "CHAIN FAILED at row-list (lines not ^S[0-9]+\$: '$badrow') $(now)" >> $CS; exit 9
fi
ROWS=$(grep -v '^#' $B/mech_rows.txt | tr '\n' ' ')
echo "MECH ($(echo $ROWS | wc -w)): $ROWS" >> $CS
WD="scripts/watchdog -L $L/watchdog.log"

# 1. build + strict
st build START
$WD -s 900 -m 16g -c 7200 -S b3b-build -- make -j16 > $L/build.log 2>&1; fin build $?
st strict START
$WD -s 1200 -m 16g -c 7200 -S b3b-strict -- make strict > $L/strict.log 2>&1; fin strict $?

# 2. full make test via perfrun (rc = make's rc; any GNU make error line is also rc!=0). Read a red WITH the
#    perfrun note: K44-ONLY / LOAD-SUSPECT reds are re-run solo per section (BOILERPLATE "Heavy-chain template").
st test START
scripts/perfrun --label b3b --timeout 7200 -- $L/test.log; rc=$?
if grep -qE '\*\*\* \[(Makefile:[0-9]+: )?test-' $L/test.log; then
  grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' $L/test.log > $L/test.red; [ $rc -eq 0 ] && rc=1
fi
echo "perfrun note: $(tail -3 $L/test.log.perfrun 2>/dev/null | tr '\n' ' ')" >> $L/notes.txt
fin test $rc

# 3. mech, each row SOLO; the verdict from the row's own COMPLETE trailer scored against its DECLARED
#    SAB_EXPECT (mech_score.sh: never a hard-coded id)
git checkout -- docs/dev/artifact_size_log.tsv 2>/dev/null
st mech START
bad=0
for id in $ROWS; do
  lg=$B/mech/$id.log
  gnutimeout 7200 bash tests/mech/run_sabotage_matrix.sh $id > $lg 2>&1; rc=$?
  line=$(mech_score $id $lg $W); r=$?
  echo "$line rc=$rc" >> $B/mech/summary.txt
  [ $r -ne 0 ] && bad=$((bad+1))
done
git checkout -- docs/dev/artifact_size_log.tsv 2>/dev/null
fin mech $bad

# 4. G2 full
st g2full START
gnutimeout 9000 make test-memfn-g2-full > $L/g2full.log 2>&1; rc=$?
grep -qE '\*\*\* \[(Makefile:[0-9]+: )?test-' $L/g2full.log && [ $rc -eq 0 ] && rc=1
echo "g2full: $(grep -E 'checks (passed|failed)' $L/g2full.log | tail -2 | tr '\n' ' ')" >> $L/notes.txt
fin g2full $rc

# 5. N2 census with floors, then the propose read. --propose PRINTS each row's floor(0.9 x chosen); it pins
#    nothing. Pinning the routed PRES rows' PLACEHOLDER floors (tests/memfn/row_floors.tsv P0 P2 P3 P4 P9) is
#    a FOLLOW-UP COMMIT after this chain, copied from $L/n2_propose.log's `propose` lines (OWED, owner the kit
#    manager). The step's rc folds N2's own rc AND the floor verdict (b3brev finding 4): the propose log must
#    carry `floor_fail=0 ` (a full census; PLACEHOLDER rows count apart, as floor_placeholder=).
st n2 START
N2_LOCK=$B/n2.lock CC=gcc JOBS=16 OUT=$B/n2 gnutimeout 7200 bash docs/design/memfn/probes/rowcon/n2_census.sh > $L/n2.log 2>&1; rc=$?
echo "n2: $(grep -E '== N2 DONE' $L/n2.log | tail -1)" >> $L/notes.txt
python3 -I docs/design/memfn/probes/rowcon/n2_report.py $B/n2 -o $B/n2/n2_results.md --floors tests/memfn/row_floors.tsv --propose > $L/n2_propose.log 2>&1; r2=$?
echo "n2 floors: $(grep -E '^(floor_fail|floors)=' $L/n2_propose.log | tail -1)" >> $L/notes.txt
[ $r2 -ne 0 ] && [ $rc -eq 0 ] && rc=$r2
grep -qE '^floor_fail=0 ' $L/n2_propose.log || { [ $rc -eq 0 ] && rc=6; }
fin n2 $rc

# 6. the memfn arm's reach (the unfiltered form: every kit row incl. B3b's three PRES denies); then the
#    three PRES denies' ANSWER IDENTITY over the whole corpus (b3brev finding 2a: the non-reach pass, no
#    MEMFN_REACH_ONLY; B3b removed req_site_define's guard against a part after a handoff's landmark and
#    `--memfn=no-fd-pres-pick` now lays such parts out); then the form census
st axes-reach START
MEMFN_REACH_ONLY=1 AXES=--memfn gnutimeout 9000 bash tests/axes/run_axes.sh > $L/axes_reach.log 2>&1; rc=$?
fin axes-reach $rc
st axes-pres START
AXES="--memfn=no-fd-pres-pick --memfn=no-fd-pres-g1 --memfn=no-pres-set-lead" gnutimeout 9000 bash tests/axes/run_axes.sh > $L/axes_pres.log 2>&1; rc=$?
grep -q '^AXIS FAIL' $L/axes_pres.log && [ $rc -eq 0 ] && rc=1
fin axes-pres $rc
st form-census START
PROCS=$(bash tests/lib/procs_default.sh) gnutimeout 9000 bash tests/codegen/run_form_census.sh > $L/form_census.log 2>&1; rc=$?
fin form-census $rc

# 7. B3b's own censuses at the pinned tip, with their committed floors (a regression read of the lane's light
#    runs): the KW-8 census on the kit-sourced proof incl. the routed records, and the routed-record count
st censuses START
mkdir -p $B/trace $B/pc $B/rc
make -s -j16 BUILD_DIR=$B/trace CFLAGS="-O2 -g -DPCREC_CAND_TRACE" all > $L/tracebuild.log 2>&1; rc=$?
if [ $rc -eq 0 ]; then
  gnutimeout 3600 python3 -I docs/design/memfn/r17b_prime/b3b/pick_census_b3b.py --bin $B/trace/pcrec --ls-bin build/pcrec \
      --jobs 16 --tmp $B/pc --floors docs/design/memfn/r17b_prime/b3b/pick_floors_B3b.tsv > $L/pick_census.log 2>&1; rc=$?
  gnutimeout 3600 python3 -I docs/design/memfn/r17b_prime/b3b/routed_census_b3b.py --bin $B/trace/pcrec --ls-bin build/pcrec \
      --jobs 16 --tmp $B/rc --floors docs/design/memfn/r17b_prime/b3b/routed_floors_B3b.tsv > $L/routed_census.log 2>&1; r2=$?
  [ $r2 -ne 0 ] && rc=$r2
fi
fin censuses $rc

if [ -z "$FAILED" ]; then echo "CHAIN COMPLETE $(now)" >> $CS; else echo "CHAIN FAILED at$FAILED $(now)" >> $CS; fi
