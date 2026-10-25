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
#
# SIMULATE ([MONITOR-QUEUE], Frank 2026-10-24): `fullsuite_job.sh --simulate NAME[:STAGE] [--dry-run|--ready]`
# runs this SAME script with only each stage's payload faked (scripts/battery.sh BATTERY_SIMULATE; scenarios
# in its header): the setsid detach, battery.pid, trailer, DONE line, summary.txt and this job's own wait loop
# and `== battery_v5 DONE` line are the real code. Differences, all deliberate and all asserted by
# scripts/tests/fullsuite_job.sh.test: it runs the battery.sh NEXT TO THIS SCRIPT (not main's), never freezes or
# creates a worktree (so there is nothing to prune), writes only under build/full_suite_sim/ (or
# $FULLSUITE_SIM_DIR) in that tree, polls every 1 s (FULLSUITE_POLL), --ready is always 0 (it must not wait
# behind or block a real suite) and no box lock is taken. It never touches docs/dev/full_suite_ledger.md
# (neither mode does: the manager copies summary.txt there).
#
# RESUME ([SUITE-RESUME], Frank 2026-10-25: stage-level resume, "auto-restart can go bad"): `fullsuite_job.sh
# [--simulate NAME[:STAGE]] --resume RUNDIR [--dry-run|--ready]` re-runs ONLY the stages of the red run RUNDIR
# (build/full_suite/<tag>/) that were red or never ran, in that run's own frozen worktree, at its SAME commit;
# a stage with a green record (`== stage S rc=0 END` in its trailer) is never re-run. Owner-commanded only:
# nothing in queuemon, boxqueue or the battery starts one. Queue it with scripts/fullsuite_resume RUNDIR (a job
# file that calls this script; a queued job takes no arguments). Its own logdir is <tag>_r<N> (trailer.log,
# summary.txt, frozen.txt, `== logdir` and `== battery_v5 DONE stages=` lines exactly as a full run's, so
# queuewatch/queuemon see it as one) plus resume_of.txt naming the parent and each carried stage's origin run.
# summary.txt shows carried stages as green(@<origin tag>) and ends `resume-of=<parent>`; the DONE line counts
# carried greens, so stages=8 means the COMBINED verdict (parent + this run) is all green. REFUSED (exit 65, in
# --dry-run too, so `boxqueue add` refuses the job): run dir missing trailer.log/summary.txt/frozen.txt; its
# battery still running; a SIMULATED parent for a real resume (or the reverse); the frozen worktree's HEAD !=
# the run's commit, or dirty (beyond the suite's own docs/dev/artifact_size_log.tsv), or gone with the commit unknown to git; summary.txt names a stage green with no
# green record; nothing red or unrun. A resume of a resume chains (carried stages keep their origin run).
set -u
MAIN=/home/pcrec/projects/pcrec
SIM=""
RESUME=""
STAGES="test strict axes san alloc lint mech recidentity"
if [ "${1:-}" = --simulate ]; then
    SIM=${2:?usage: fullsuite_job.sh --simulate NAME[:STAGE] [--dry-run|--ready]}; shift 2
    case ${SIM%%:*} in green|red|quiet|die|burst) ;; *) echo "fullsuite_job: unknown simulate scenario '$SIM'" >&2; exit 64 ;; esac
    MAIN=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
fi
if [ "${1:-}" = --resume ]; then RESUME=${2:?usage: fullsuite_job.sh [--simulate NAME[:STAGE]] --resume RUNDIR [--dry-run|--ready]}; shift 2; fi

refuse() { echo "fullsuite_job --resume: REFUSED: $*" >&2; exit 65; }
stage_green() { sed -n "s/^== stage $2 rc=0 END.*/ok/p" "$1/trailer.log" 2>/dev/null | head -1 | grep -q ok; }
is_green() { printf '%s' "$GREENS" | command grep -q "^$1 "; }
# resume_plan: validates RESUME (all refusals), sets PD (abs parent), PFULL, PTREE, TODO (stages to run),
# GREENS (lines "stage origin-logdir"), TREE_EXISTS.
resume_plan() {
    local d f s line o tok
    [ -d "$RESUME" ] || refuse "no such run dir $RESUME"
    PD=$(cd "$RESUME" && pwd)
    for f in trailer.log summary.txt frozen.txt; do [ -s "$PD/$f" ] || refuse "$PD lacks $f (not a full-suite run dir)"; done
    if [ -e "$PD/SIMULATED" ]; then [ -n "$SIM" ] || refuse "$PD is a SIMULATED run; a real resume needs a real run"
    else [ -z "$SIM" ] || refuse "$PD is a real run; a simulated resume needs a SIMULATED parent"; fi
    if [ -s "$PD/battery.pid" ] && kill -0 "$(cat "$PD/battery.pid")" 2>/dev/null; then refuse "the battery of $PD is still running"; fi
    line=$(sed -n 's/^== full suite .* frozen at \([0-9a-f]\{40\}\) tree \(.*\)$/\1 \2/p' "$PD/frozen.txt" | head -1)
    [ -n "$line" ] || refuse "$PD/frozen.txt names no commit and tree"
    PFULL=${line%% *} PTREE=${line#* }
    TREE_EXISTS=0
    if [ -e "$PTREE" ]; then
        o=$(git -C "$PTREE" rev-parse HEAD 2>/dev/null) || refuse "$PTREE is not a git tree"
        [ "$o" = "$PFULL" ] || refuse "the tree's HEAD $o != the run's commit $PFULL"
        # the suite itself rewrites tracked files (measured: make test appends docs/dev/artifact_size_log.tsv), so a
        # finished run's tree is never porcelain-clean; only those named files may differ (RESUME_DIRTY_OK)
        o=$(git -C "$PTREE" status --porcelain 2>/dev/null | cut -c4- | command grep -vxF -f <(printf '%s\n' ${RESUME_DIRTY_OK:-docs/dev/artifact_size_log.tsv}))
        [ -z "$o" ] || refuse "the tree $PTREE is dirty: $(echo "$o" | head -3 | tr '\n' ' ')"
        TREE_EXISTS=1
    else
        [ -z "$SIM" ] || refuse "the tree $PTREE is gone (simulated resume needs it)"
        git -C "$MAIN" cat-file -e "$PFULL^{commit}" 2>/dev/null || refuse "the tree $PTREE is gone and commit $PFULL is unknown to git"
    fi
    GREENS=""
    for s in $STAGES; do
        if stage_green "$PD" "$s"; then GREENS="$GREENS$s $PD
"; fi
    done
    if [ -f "$PD/resume_of.txt" ]; then
        while read -r tok s o; do
            [ "$tok" = carried ] || continue
            stage_green "$o" "$s" || refuse "$PD carries $s from $o, which has no green record for it"
            is_green "$s" || GREENS="$GREENS$s $o
"
        done < "$PD/resume_of.txt"
    fi
    for s in $STAGES; do
        tok=$(grep -o " $s=[^ ]*" "$PD/summary.txt" | head -1)
        case $tok in " $s=green"*) is_green "$s" || refuse "summary.txt names $s green but no run has a green record for it" ;; esac
    done
    TODO=""
    for s in $STAGES; do is_green "$s" || TODO="$TODO $s"; done
    TODO=${TODO# }
    [ -n "$TODO" ] || refuse "nothing to resume: all stages of $PD are green"
}
est_stage() { case $1 in test) echo 1100 ;; strict|lint) echo 60 ;; axes) echo 10400 ;; san) echo 3000 ;; alloc) echo 100 ;; mech) echo 28800 ;; recidentity) echo 2800 ;; esac; }
[ -z "$RESUME" ] || resume_plan
# an argument nobody here knows must never fall through to the REAL run (2026-10-25: an old copy of this script
# ignored `--resume` and started a full suite on the live box)
case "${1:-}" in ""|--dry-run|--ready) ;; *) echo "fullsuite_job: unknown argument '$1'" >&2; exit 64 ;; esac

case "${1:-}" in
    --dry-run)
        if [ -n "$RESUME" ]; then
            cap=0; for s in $TODO; do cap=$((cap + $(est_stage "$s"))); done; cap=$((cap * 5 / 4 + 600))
            [ -z "$SIM" ] || cap=600
            echo "would run: RESUME of $PD at commit $PFULL${SIM:+ (SIMULATED $SIM)}: stages [$TODO] only; carried green: $(printf '%s' "$GREENS" | awk '{printf "%s ", $1}')"
            echo "tree: $PTREE ($([ "$TREE_EXISTS" = 1 ] && echo "exists, HEAD and cleanliness verified" || echo "gone: recreated detached at the commit")); logdir ${PD##*/}_r<N>"
            echo "boxqueue: cap $cap"
            echo "boxqueue: patience none"
            echo "boxqueue: idle-ok 1800"
            echo "boxqueue: expect stages=8 last=^== battery_v5 DONE stages="
            echo "boxqueue: witness stages=== battery_v5 DONE stages=8"
            exit 0
        fi
        if [ -n "$SIM" ]; then
            echo "would run: SIMULATED scenario $SIM; battery.sh $MAIN/scripts/battery.sh with fake stage payloads, no worktree, logdir under ${FULLSUITE_SIM_DIR:-$MAIN/build/full_suite_sim}"
            echo "boxqueue: cap 600"
            echo "boxqueue: patience none"
            echo "boxqueue: idle-ok 1800"
            echo "boxqueue: expect stages=8 last=^== battery_v5 DONE stages="
            echo "boxqueue: witness stages=== battery_v5 DONE stages=8"
            exit 0
        fi
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
        [ -z "$SIM" ] || exit 0
        st=$(bash "$MAIN/scripts/boxlock" status 2>&1 | head -1)
        case $st in free*) ;; *) echo "box lock not free: $st"; exit 75 ;; esac
        r=$(ls -A "$(bash "${BOXQUEUE:-$MAIN/scripts/boxqueue}" path)/running" 2>/dev/null | head -1)
        [ -z "$r" ] || { echo "a queue job is running: $r"; exit 75; }
        exit 0 ;;
esac
if [ -n "$SIM" ]; then
    tag="sim_$(date +%Y%m%d_%H%M%S)_${SIM//[^A-Za-z0-9]/-}_$$"; sha=$tag
    [ -z "$RESUME" ] || { tag=${tag}_resume; sha=${PFULL:0:9}; }
    LOGDIR=${FULLSUITE_SIM_DIR:-$MAIN/build/full_suite_sim}/$tag
    TREE=$MAIN
    mkdir -p "$LOGDIR" || exit 1
    echo "== SIMULATED $SIM: no frozen worktree, battery.sh of $TREE" > "$LOGDIR/SIMULATED"
    export BATTERY_SIMULATE=$SIM
    POLL=${FULLSUITE_POLL:-1}
elif [ -n "$RESUME" ]; then
    unset BATTERY_SIMULATE
    sha=${PFULL:0:9}
    root=$(basename "$PD" | sed 's/_r[0-9][0-9]*$//')
    n=1; while [ -e "$MAIN/build/full_suite/${root}_r$n" ]; do n=$((n+1)); done
    tag=${root}_r$n
    LOGDIR=$MAIN/build/full_suite/$tag
    TREE=$PTREE
    mkdir -p "$LOGDIR" || exit 1
    if [ "$TREE_EXISTS" = 1 ]; then echo "reusing the parent's frozen worktree $TREE" > "$LOGDIR/worktree.log"
    else git -C "$MAIN" worktree add --detach "$TREE" "$PFULL" > "$LOGDIR/worktree.log" 2>&1 || exit 1; fi
    POLL=${FULLSUITE_POLL:-30}
else
    unset BATTERY_SIMULATE    # a stray env var must never turn a real run into a fake green
    sha=$(git -C "$MAIN" rev-parse --short=9 main) || exit 1
    full=$(git -C "$MAIN" rev-parse main) || exit 1
    tag="$(date +%Y%m%d)_$sha"
    LOGDIR=$MAIN/build/full_suite/$tag
    TREE=$MAIN/worktrees/fullsuite-run-$tag
    mkdir -p "$LOGDIR" || exit 1
    git -C "$MAIN" worktree add --detach "$TREE" "$full" > "$LOGDIR/worktree.log" 2>&1 || exit 1
    echo "== full suite $tag frozen at $full tree $TREE" > "$LOGDIR/frozen.txt"
    POLL=${FULLSUITE_POLL:-30}
fi
if [ -n "$RESUME" ]; then
    echo "== full suite $tag resume of $PD frozen at $PFULL tree $PTREE" > "$LOGDIR/frozen.txt"
    { echo "resume-of $PD"; echo "commit $PFULL"; echo "rerun $TODO"; printf '%s' "$GREENS" | while read -r s o; do echo "carried $s $o"; done; } > "$LOGDIR/resume_of.txt"
    export BATTERY_STAGES="$TODO"
fi
echo "== logdir $LOGDIR"    # the box-queue watcher (scripts/queuewatch) finds the trailer from this line
t0=$(date +%s)
# battery.sh detaches (setsid) and returns at once; wait for its own DONE trailer. It nests under the
# queue's box lock (scripts/boxlock NESTING).
bash "$TREE/scripts/battery.sh" "$LOGDIR" || exit 1
tr=$LOGDIR/trailer.log
while ! command grep -q '^== BATTERY DONE rc=' "$tr" 2>/dev/null; do
    sleep "$POLL"
    if [ -s "$LOGDIR/battery.pid" ] && ! kill -0 "$(cat "$LOGDIR/battery.pid")" 2>/dev/null &&
       ! command grep -q '^== BATTERY DONE rc=' "$tr" 2>/dev/null; then
        echo "battery died without a DONE trailer" >&2; break
    fi
done
dur=$(( $(date +%s) - t0 ))
# Per-stage verdict from the trailer's own `== stage S rc=N END` lines; a stage with no END is MISSING.
line="$(date +%F) $sha"
n=0
for s in $STAGES; do
    if [ -n "$RESUME" ] && is_green "$s"; then
        o=$(printf '%s' "$GREENS" | sed -n "s/^$s //p" | head -1)
        line="$line $s=green(@${o##*/})"; n=$((n+1)); continue
    fi
    rc=$(sed -n "s/^== stage $s rc=\([0-9]*\) END.*/\1/p" "$tr" | tail -1)
    case $rc in 0) v=green; n=$((n+1)) ;; "") v=MISSING ;; *) v="RED(rc=$rc)" ;; esac
    line="$line $s=$v"
done
done_rc=$(sed -n 's/^== BATTERY DONE rc=\([0-9]*\).*/\1/p' "$tr" | tail -1)
printf '%s log=%s%s duration=%ss\n' "$line" "${LOGDIR#$MAIN/}" "${RESUME:+ resume-of=${PD#$MAIN/}}" "$dur" > "$LOGDIR/summary.txt"
cat "$LOGDIR/summary.txt"
echo "== battery_v5 DONE stages=$n rc=${done_rc:-none}"
[ "$n" = 8 ] && [ "${done_rc:-1}" = 0 ]
