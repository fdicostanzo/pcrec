#!/usr/bin/env bash
# fullsuite_job.sh — the full suite (scripts/battery.sh: test strict axes san alloc lint mech recidentity)
# as ONE box-queue job, with a retained verdict (D177; docs/dev/full_suite_ledger.md).
#
# Queue it for the next window:
#   scripts/boxqueue add --name 300-main-fullsuite scripts/fullsuite_job.sh
# (the queue runs a COPY of this script, so it names the main tree by absolute path).
#
# FROZEN COMMIT: the work records `git rev-parse main` ONCE, adds a detached worktree at that commit
# (worktrees/fullsuite-run-<date>_<sha>), and runs battery.sh THERE, so a merge onto main mid-run cannot
# enter the battery. The worktree keeps full git history (recidentity needs it). It is left in place;
# remove it with scripts/wtprune once the verdict is copied to the ledger.
# LOGDIR (retained, gitignored): build/full_suite/<date>_<sha>/ in the main tree. Its trailer.log is
# battery.sh's; summary.txt is the one line the manager copies into the ledger. The job never commits.
#   --ready    the box lock is free and no queue job is running (a long heavy run, not a timing run: no load gate).
set -u
MAIN=/home/pcrec/projects/pcrec
case "${1:-}" in
    --dry-run)
        sha=$(git -C "$MAIN" rev-parse --short=9 main) || { echo "cannot resolve main" >&2; exit 1; }
        [ -x "$MAIN/scripts/battery.sh" ] || { echo "no scripts/battery.sh" >&2; exit 1; }
        echo "would run: freeze main at $sha; git worktree add --detach $MAIN/worktrees/fullsuite-run-<date>_<sha>; scripts/battery.sh $MAIN/build/full_suite/<date>_<sha> there"
        echo "frozen: the battery sees commit $sha only; merges onto main during the run do not enter it"
        echo "stages: test strict axes san alloc lint mech recidentity; summary: build/full_suite/<date>_<sha>/summary.txt"
        # Stage estimates (battery.sh header, docs/dev/gate_census_2026-10-23.md; this box): test ~1100 s,
        # axes ~10400 s batched, san ~3000 s, alloc ~100 s, lint+strict ~60 s, recidentity ~2800 s, full mech
        # UNMEASURED at the current matrix size (an 8 h cap was used earlier, 28800 s). Sum ~46000 s; cap 57600 (16 h).
        echo "boxqueue: cap 57600"
        echo "boxqueue: patience none"
        echo "boxqueue: idle-ok 1800"
        echo "boxqueue: expect stages=8 last=^== battery_v5 DONE stages="
        echo "boxqueue: witness stages=== battery_v5 DONE stages=8"
        exit 0 ;;
    --ready)
        st=$(bash "$MAIN/scripts/boxlock" status 2>&1 | head -1)
        case $st in free*) ;; *) echo "box lock not free: $st"; exit 75 ;; esac
        r=$(ls -A "$(bash "${BOXQUEUE:-$MAIN/scripts/boxqueue}" path)/running" 2>/dev/null | head -1)
        [ -z "$r" ] || { echo "a queue job is running: $r"; exit 75; }
        exit 0 ;;
esac
sha=$(git -C "$MAIN" rev-parse --short=9 main) || exit 1
full=$(git -C "$MAIN" rev-parse main) || exit 1
tag="$(date +%Y%m%d)_$sha"
LOGDIR=$MAIN/build/full_suite/$tag
TREE=$MAIN/worktrees/fullsuite-run-$tag
mkdir -p "$LOGDIR" || exit 1
git -C "$MAIN" worktree add --detach "$TREE" "$full" > "$LOGDIR/worktree.log" 2>&1 || exit 1
echo "== full suite $tag frozen at $full tree $TREE" > "$LOGDIR/frozen.txt"
t0=$(date +%s)
# battery.sh detaches (setsid) and returns at once; wait for its own DONE trailer. It nests under the
# queue's box lock (scripts/boxlock NESTING).
bash "$TREE/scripts/battery.sh" "$LOGDIR" || exit 1
tr=$LOGDIR/trailer.log
while ! command grep -q '^== BATTERY DONE rc=' "$tr" 2>/dev/null; do
    sleep 30
    if [ -s "$LOGDIR/battery.pid" ] && ! kill -0 "$(cat "$LOGDIR/battery.pid")" 2>/dev/null &&
       ! command grep -q '^== BATTERY DONE rc=' "$tr" 2>/dev/null; then
        echo "battery died without a DONE trailer" >&2; break
    fi
done
dur=$(( $(date +%s) - t0 ))
# Per-stage verdict from the trailer's own `== stage S rc=N END` lines; a stage with no END is MISSING.
line="$(date +%F) $sha"
n=0
for s in test strict axes san alloc lint mech recidentity; do
    rc=$(sed -n "s/^== stage $s rc=\([0-9]*\) END.*/\1/p" "$tr" | tail -1)
    case $rc in 0) v=green; n=$((n+1)) ;; "") v=MISSING ;; *) v="RED(rc=$rc)" ;; esac
    line="$line $s=$v"
done
done_rc=$(sed -n 's/^== BATTERY DONE rc=\([0-9]*\).*/\1/p' "$tr" | tail -1)
printf '%s log=%s duration=%ss\n' "$line" "${LOGDIR#$MAIN/}" "$dur" > "$LOGDIR/summary.txt"
cat "$LOGDIR/summary.txt"
echo "== battery_v5 DONE stages=$n rc=${done_rc:-none}"
[ "$n" = 8 ] && [ "${done_rc:-1}" = 0 ]
