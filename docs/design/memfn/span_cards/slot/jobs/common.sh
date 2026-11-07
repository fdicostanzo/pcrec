# span_cards/slot/jobs/common.sh — the S2d WINDOW's queue jobs, common part (span_cards.md §3.3, §3.5, §9 S2d;
# [rev1.3 r9-W1], [rev1.3 r9-W2]). The job scripts are COMMITTED here; main copies this directory to a scratch
# job dir, writes `window.vars` beside the copies when it clears the window with Frank, and queues the copies
# with scripts/boxqueue. Every --dry-run compares its copy (and this file's) with the tree's: a stale copy
# refuses. window.vars sets RUN_ID (seeds every placement, §3.2), FROZEN (the commit the window times, a hex object
# name; TREE's HEAD must equal it), TREE (the checkout) and optionally HOLD (a script whose non-zero exit holds every
# job). FROZEN is RESOLVED to its full sha here ([rev1.3 r9fc-FIX-3]): CODE_COMMIT, the value every job writes into
# the run record, is that sha, and a FROZEN that is not hex (a branch name) refuses at the dry run.
# READINESS (boxqueue --ready: 0 ready, 75 wait, 77 never): a job waits for its upstream to END (green, failed
# or cancelled), never for it to be green (boxqueue `after` waits forever on a failed upstream, r9 W2); every
# timing job answers 77 once the prep job ended non-green (nothing linked, nothing to time), and once the
# PLACEMENT SCREEN (480-kit-s2d-screen, after the prep) ended non-green: over the half gate, the window is HELD
# for the kit manager's ruling (§3.5 HELD), so J1..J5 never start ([rev1.3 r9fc-FIX-7]).
set -u
export LC_ALL=C
JOBDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
RUN_ID="" FROZEN="" TREE="" HOLD=""
[ -f "$JOBDIR/window.vars" ] && . "$JOBDIR/window.vars"
export TMPDIR=${PCREC_TMPDIR:-/var/tmp/pcrec-$(id -un)}
SLOT=$TREE/docs/design/memfn/span_cards/slot
RUNDIR=$TMPDIR/scratch/memfn/s2d/${RUN_ID:-unset}
JOBS="J1 J2 J2p J3 J4 J5"
CODE_COMMIT=""
case $FROZEN in
    *[!0-9a-f]*|"") ;;
    *) CODE_COMMIT=$(git -C "$TREE" rev-parse --verify -q "$FROZEN^{commit}" 2>/dev/null) ;;
esac
export CODE_COMMIT

main_tree() { dirname "$(git -C "$TREE" rev-parse --path-format=absolute --git-common-dir)"; }
bq() { bash "$(main_tree)/scripts/boxqueue" "$@"; }

check_inputs() {   # SELF: the window's inputs, and the queued copy is the tree's
    [ -n "$RUN_ID" ] || { echo "RUN_ID is empty in $JOBDIR/window.vars (main sets it when the window is cleared)" >&2; return 1; }
    [ -n "$FROZEN" ] || { echo "FROZEN is empty in $JOBDIR/window.vars" >&2; return 1; }
    [ -d "$TREE" ] || { echo "TREE ($TREE) is not a directory" >&2; return 1; }
    case $FROZEN in *[!0-9a-f]*) echo "FROZEN ($FROZEN) is not a hex object name (a commit sha, never a ref name)" >&2; return 1 ;; esac
    [ ${#CODE_COMMIT} -eq 40 ] || { echo "FROZEN ($FROZEN) resolves to no commit in $TREE" >&2; return 1; }
    [ "$(git -C "$TREE" rev-parse HEAD)" = "$CODE_COMMIT" ] || { echo "$TREE HEAD is not $FROZEN" >&2; return 1; }
    # the RUNNING copy ($0, boxqueue's own copy) against the tree's file of the job's canonical name ($1), and this file
    cmp -s "$0" "$SLOT/jobs/$1" || { echo "$0 (job $1) is not the tree's $SLOT/jobs/$1 (a stale copy)" >&2; return 1; }
    cmp -s "$JOBDIR/common.sh" "$SLOT/jobs/common.sh" || { echo "$JOBDIR/common.sh is not the tree's $SLOT/jobs/common.sh (a stale copy)" >&2; return 1; }
    [ -f "$SLOT/run.py" ] || { echo "no $SLOT/run.py" >&2; return 1; }
}

hold() { [ -z "$HOLD" ] || bash "$HOLD" || exit 75; }

ended() {          # KEY: 0 if the job ended (green, failed, cancelled)
    case $(bq state "$1") in green|failed|cancelled) return 0 ;; *) return 1 ;; esac
}

ready_prep() {     # the screen's readiness: 77 if prep ended non-green, 75 until it ended green, else 0
    hold
    case $(bq state kit-s2d-prep) in
        green) ;;
        failed|cancelled) echo "kit-s2d-prep ended non-green: nothing linked, never"; exit 77 ;;
        *) echo "waits: kit-s2d-prep"; exit 75 ;;
    esac
}

ready_after() {    # UPSTREAM-KEY..: ready_prep, then 77 if the screen ended non-green, 75 until it and every
                   # upstream ended, else 0
    ready_prep
    case $(bq state kit-s2d-screen) in
        green) ;;
        failed|cancelled) echo "kit-s2d-screen ended non-green: the unit's placement noise is over its half gate (or the screen failed): HELD, never"; exit 77 ;;
        *) echo "waits: kit-s2d-screen"; exit 75 ;;
    esac
    for k in "$@"; do ended "$k" || { echo "waits: $k $(bq state "$k")"; exit 75; }; done
    exit 0
}

timing_dry() {     # JOB EST: inputs only (the work checks the dry run's manifest); `expect groups` from the plan
    local job=$1 est=$2 n
    check_inputs "$JOB" || exit 1
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
