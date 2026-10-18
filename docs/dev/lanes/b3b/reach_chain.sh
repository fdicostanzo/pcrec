#!/bin/bash
# docs/dev/lanes/b3b/reach_chain.sh -- lane b3breach's OWED heavy pair (2026-10-18): the full N2 census
# (exactly as worktrees/memfn-slot/b3bheavy3/chain.sh step 5 runs it) then `n2_report.py --floors --propose`,
# and the FULL axes-pres pass (the three PRES denies, every row, no MEMFN_EVERY), at a PINNED tip.
#
# ARMING (the lane's last act): copy this file to $B and run it DETACHED
# (`setsid nohup bash $B/reach_chain.sh > $B/chain.out 2>&1 < /dev/null & disown`). It creates its own
# `git worktree add --detach` scratch $W at PIN (never the lane's worktree), writes only under $B and $W
# (plus git's worktree metadata). Box calendar: launched by 22:30, every CPU-bound step bounded by
# gnutimeout AND by DEADLINE (00:25), so nothing runs into the 00:30 bench window.
#
# THE VERDICT is the LAST line of $B/chain.status, anchored: ^CHAIN (COMPLETE|FAILED). Per-step lines are
# `STEP <name> rc=<n>`. Expected N2 verdict at PIN: floor_fail=0 floor_placeholder=5 (P0 P2 P3 P4 P9).
B=${B:-/home/pcrec/projects/pcrec/worktrees/memfn-slot/b3b/reach}
MAIN=/home/pcrec/projects/pcrec
W=${W:-$B/wt}
PIN=${PIN:?PIN required}
L=$B/logs
CS=$B/chain.status
mkdir -p $L $B/tmp
echo $$ > $B/chain.pid
export TMPDIR=$B/tmp PYTHONDONTWRITEBYTECODE=1
FAILED=""
now() { date -Is; }
st() { echo "STEP $1 $2 $(now)" >> $CS; }
fin() { st "$1" "rc=$2"; [ "$2" -ne 0 ] && FAILED="$FAILED $1"; }
DEADLINE=$(date -d 'tomorrow 00:25' +%s)
[ "$(date +%H)" -lt 12 ] && DEADLINE=$(date -d 'today 00:25' +%s)
budget() { local left=$(( DEADLINE - $(date +%s) )); [ "$left" -lt "$1" ] && echo "$left" || echo "$1"; }
echo "CHAIN START $(now) pin $PIN deadline $(date -d @$DEADLINE -Is)" >> $CS
if [ ! -d "$W" ]; then
  git -C $MAIN worktree add --detach "$W" "$PIN" > $L/worktree.log 2>&1 || { echo "CHAIN FAILED at worktree-add $(now)" >> $CS; exit 9; }
fi
if [ "$(git -C $W rev-parse --short=9 HEAD)" != "$(git -C $MAIN rev-parse --short=9 $PIN)" ]; then
  echo "CHAIN FAILED at pin-check (HEAD $(git -C $W rev-parse --short=9 HEAD) != $PIN) $(now)" >> $CS; exit 9
fi

st build START
gnutimeout $(budget 900) make -C $W -j16 > $L/build.log 2>&1; fin build $?
[ -n "$FAILED" ] && { echo "CHAIN FAILED at$FAILED $(now)" >> $CS; exit 1; }

# (a) N2 census with floors, then the propose read (heavy3 step 5's lines; OUT moved under $B/n2). The step's
#     rc folds N2's own rc AND the floor verdict: the propose log must carry `floor_fail=0 `.
st n2 START
( cd $W && N2_LOCK=$B/n2.lock CC=gcc JOBS=16 OUT=$B/n2 gnutimeout $(budget 5400) bash docs/design/memfn/probes/rowcon/n2_census.sh ) > $L/n2.log 2>&1; rc=$?
echo "n2: $(grep -E '== N2 DONE' $L/n2.log | tail -1)" >> $CS
( cd $W && python3 -I docs/design/memfn/probes/rowcon/n2_report.py $B/n2 -o $B/n2/n2_results.md --floors tests/memfn/row_floors.tsv --propose ) > $L/n2_propose.log 2>&1; r2=$?
echo "n2 floors: $(grep -E '^(floor_fail|floors)=' $L/n2_propose.log | tail -1)" >> $CS
[ $r2 -ne 0 ] && [ $rc -eq 0 ] && rc=$r2
grep -qE '^floor_fail=0 ' $L/n2_propose.log || { [ $rc -eq 0 ] && rc=6; }
fin n2 $rc

# (b) the FULL axes-pres pass: the three PRES denies' answer identity over the whole corpus, every row, no
#     MEMFN_EVERY; rc and `^AXIS FAIL` both honoured.
st axes-pres START
( cd $W && AXES="--memfn=no-fd-pres-pick --memfn=no-fd-pres-g1 --memfn=no-pres-set-lead" gnutimeout $(budget 4500) bash tests/axes/run_axes.sh ) > $L/axes_pres.log 2>&1; rc=$?
grep -q '^AXIS FAIL' $L/axes_pres.log && [ $rc -eq 0 ] && rc=1
echo "axes-pres: $(grep -E 'checks (passed|failed)' $L/axes_pres.log | tail -2 | tr '\n' ' ')" >> $CS
fin axes-pres $rc

if [ -z "$FAILED" ]; then echo "CHAIN COMPLETE $(now)" >> $CS; else echo "CHAIN FAILED at$FAILED $(now)" >> $CS; fi
