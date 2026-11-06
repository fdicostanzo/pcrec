# span_cards/slot/jobs/common.sh — the S2d WINDOW's queue jobs, common part (span_cards.md §3.3, §3.5, §9 S2d;
# [rev1.3 r9-W1], [rev1.3 r9-W2]). The job scripts are COMMITTED here; main copies this directory to a scratch
# job dir, writes `window.env` beside the copies when it clears the window with Frank, and queues the copies
# with scripts/boxqueue. Every --dry-run compares its copy (and this file's) with the tree's: a stale copy
# refuses. window.env sets RUN_ID (seeds every placement, §3.2), FROZEN (the commit the window times; TREE's
# HEAD must equal it), TREE (the checkout) and optionally HOLD (a script whose non-zero exit holds every job).
# READINESS (boxqueue --ready: 0 ready, 75 wait, 77 never): a job waits for its upstream to END (green, failed
# or cancelled), never for it to be green (boxqueue `after` waits forever on a failed upstream, r9 W2); every
# timing job answers 77 once the prep job ended non-green (nothing linked, nothing to time).
set -u
export LC_ALL=C
JOBDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RUN_ID="" FROZEN="" TREE="" HOLD=""
[ -f "$JOBDIR/window.env" ] && . "$JOBDIR/window.env"
export TMPDIR=${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}
SLOT=$TREE/docs/design/memfn/span_cards/slot
RUNDIR=$TMPDIR/scratch/memfn/s2d/${RUN_ID:-unset}
JOBS="J1 J2 J2p J3 J4 J5"
export CODE_COMMIT=$FROZEN

main_tree() { dirname "$(git -C "$TREE" rev-parse --path-format=absolute --git-common-dir)"; }
bq() { bash "$(main_tree)/scripts/boxqueue" "$@"; }

check_inputs() {   # SELF: the window's inputs, and the queued copy is the tree's
    [ -n "$RUN_ID" ] || { echo "RUN_ID is empty in $JOBDIR/window.env (main sets it when the window is cleared)" >&2; return 1; }
    [ -n "$FROZEN" ] || { echo "FROZEN is empty in $JOBDIR/window.env" >&2; return 1; }
    [ -d "$TREE" ] || { echo "TREE ($TREE) is not a directory" >&2; return 1; }
    [ "$(git -C "$TREE" rev-parse HEAD)" = "$(git -C "$TREE" rev-parse "$FROZEN^{commit}")" ] || { echo "$TREE HEAD is not $FROZEN" >&2; return 1; }
    for f in "$1" common.sh; do
        cmp -s "$JOBDIR/$f" "$SLOT/jobs/$f" || { echo "$JOBDIR/$f is not the tree's $SLOT/jobs/$f (a stale copy)" >&2; return 1; }
    done
    [ -f "$SLOT/run.py" ] || { echo "no $SLOT/run.py" >&2; return 1; }
}

hold() { [ -z "$HOLD" ] || bash "$HOLD" || exit 75; }

ended() {          # KEY: 0 if the job ended (green, failed, cancelled)
    case $(bq state "$1") in green|failed|cancelled) return 0 ;; *) return 1 ;; esac
}

ready_after() {    # UPSTREAM-KEY..: 77 if prep ended non-green, 75 until every upstream ended, else 0
    hold
    case $(bq state kit-s2d-prep) in
        green) ;;
        failed|cancelled) echo "kit-s2d-prep ended non-green: nothing linked, never"; exit 77 ;;
        *) echo "waits: kit-s2d-prep"; exit 75 ;;
    esac
    for k in "$@"; do ended "$k" || { echo "waits: $k $(bq state "$k")"; exit 75; }; done
    exit 0
}

timing_dry() {     # JOB EST: inputs only (the work checks the dry run's manifest); `expect groups` from the plan
    local job=$1 est=$2 n
    check_inputs "$(basename "$0")" || exit 1
    n=$(python3 -I "$SLOT/plan.py" groups "$job") || exit 1
    echo "would run: python3 -I $SLOT/run.py run $job $RUNDIR $RUN_ID (the manifest of kit-s2d-prep's dry run, then 7 launches x 7 rounds, quiet-gated)"
    echo "boxqueue: cap 1500"; echo "boxqueue: patience none"; echo "boxqueue: est $est"
    echo "boxqueue: idle-ok"
    echo "boxqueue: expect groups=$n lines=^== s2 GROUP done "
    exit 0
}

timing_job() {     # JOB
    python3 -I "$SLOT/run.py" run "$1" "$RUNDIR" "$RUN_ID"; local rc=$?
    echo "s2d-$1: DONE rc=$rc"
    exit $rc
}
