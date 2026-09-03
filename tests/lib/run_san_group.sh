#!/usr/bin/env bash
# tests/lib/run_san_group.sh — [TT-12] STEP 1 item 3: a bounded `-P` over
# `make san`'s (`ubsan`'s, `asan`'s) serial `for s in $(SAN_SCRIPTS); do ...
# done` loop (Makefile), for the 30 of 34 scripts in tests/lib/san_scripts.txt
# that are structurally single-process (STEP 0's profile,
# docs/dev/tt12_step0_profile.md §2: only tests/harness/run.sh,
# tests/reject/run_reject_tests.sh, tests/lookaround/run_expansion_diff.sh
# and tests/anchored/run_anchored_diff.sh read PROCS themselves) — measured
# at ~1.9 of 12 cores busy through san's 110-minute wall, 18.5 idle
# core-hours, the single biggest number in that profile.
#
# WHY A NEW SCRIPT RATHER THAN tests/lib/run_group.sh: that script's
# GROUP_PROCS is documented, by its own header, as NOT a real throttle above
# 1 ("there are only ever 2-3 scripts in a group here, never enough to want
# real job-pool capping") — every existing call site launches its whole
# (small) group at once. San's list is 34 scripts, several of which are
# ALREADY internally parallel at PROCS=nproc (the four named above) —
# launching all 34 unthrottled would stack a second layer of oversubscription
# on top of that internal fan-out, the exact K44 shape this project is
# already retiring elsewhere ([TT-12] item 4). This script is run_group.sh's
# shape (buffer each script's own stdout+stderr, replay in ARGUMENT order
# once everything has finished so nothing interleaves mid-line, a lost/
# crashed worker is a HARD FAILURE never conflated with a clean nonzero
# exit) plus a REAL bounded job pool, which is the piece san's 34-script,
# partly-already-parallel list actually needs.
#
# Usage: env <SAN_ENV vars> SAN_GROUP_PROCS=N bash tests/lib/run_san_group.sh
#            SCRIPT [SCRIPT ...]
#   Reads its env from the CALLER (the Makefile's `env $(SAN_ENV) ...`
#   prefix, exactly as the original for-loop did) rather than taking it as
#   arguments — this avoids re-quoting SAN_ENV's own already-double-quoted
#   GENCFLAGS/SANFLAGS values a second time, which is fragile the moment a
#   value needs its own quoting (a lesson learned drafting this file: the
#   first shape tried building one "env VAR=val... bash $s" STRING per
#   script and re-parsing it, and SAN_ENV's embedded double quotes broke
#   that immediately).
#   SAN_GROUP_PROCS  max scripts running concurrently (default 4).
#
# Exit status: 0 iff every script exited 0. Otherwise nonzero.
set -u
export LC_ALL=C   # K35 — same reasoning as run_group.sh's own header

if [ "$#" -eq 0 ]; then
    echo "run_san_group: usage: bash tests/lib/run_san_group.sh SCRIPT [SCRIPT ...]" >&2
    exit 2
fi

SAN_GROUP_PROCS="${SAN_GROUP_PROCS:-4}"
case "$SAN_GROUP_PROCS" in
    (''|*[!0-9]*)
        echo "run_san_group: SAN_GROUP_PROCS must be a positive integer, got '$SAN_GROUP_PROCS'" >&2
        exit 2
        ;;
esac
[ "$SAN_GROUP_PROCS" -ge 1 ] || SAN_GROUP_PROCS=1

scripts=("$@")
n=${#scripts[@]}
dir="$(mktemp -d)"
trap 'rm -rf "$dir"' EXIT

# [TT-8 shape, re-applied here] FOUR of these scripts read PROCS themselves
# (tests/harness/run.sh, tests/reject/run_reject_tests.sh,
# tests/lookaround/run_expansion_diff.sh, tests/anchored/run_anchored_diff.sh
# — STEP 0's profile) and SAN_ENV hands every script PROCS=nproc uniformly,
# exactly as the plain serial loop did. Serially that was fine (only one
# script, PROCS-aware or not, ever ran at a time); under a real job pool it
# is the SAME double-parallelism K44/[TT-8]'s mech fix already retired —
# up to SAN_GROUP_PROCS scripts concurrent, any PROCS-aware one among them
# ALSO fanning out to nproc internally. [TT-8]'s own fix (mech's
# INNER_PROCS = ncpu/PROCS) is the general mechanism, not a special case;
# applied here identically: every script (PROCS-aware or not — harmless for
# the 30 that ignore it) runs with PROCS capped to ceil(nproc/SAN_GROUP_PROCS)
# rather than whatever SAN_ENV set.
_nproc="$(nproc 2>/dev/null || echo 1)"
INNER_PROCS=$(( (_nproc + SAN_GROUP_PROCS - 1) / SAN_GROUP_PROCS ))
[ "$INNER_PROCS" -ge 1 ] || INNER_PROCS=1

echo "run_san_group: $n scripts, up to $SAN_GROUP_PROCS concurrent, PROCS=$INNER_PROCS per script"

# Real job-pool: launch up to SAN_GROUP_PROCS at once, then for every
# further script, wait for the OLDEST still-running one before launching
# the next — never more than SAN_GROUP_PROCS in flight at any moment. This
# is FIFO throttling, not a true "whichever finishes first" pool (`wait -n`
# would give that, but needs bash 4.3+; this box's bash is 5.3 but there is
# no reason to depend on a newer builtin than the job needs) — with 30
# candidate scripts and a handful of internally-parallel ones among them
# mixed through the list, FIFO throttling still keeps steady-state
# concurrency at SAN_GROUP_PROCS; it can only ever UNDER-fill a slot
# (waiting on an oldest job that happens to be slower than a newer one that
# finished first), never over-subscribe.
declare -a pids=()
for ((k = 0; k < n; k++)); do
    if [ "${#pids[@]}" -ge "$SAN_GROUP_PROCS" ]; then
        wait "${pids[0]}"
        pids=("${pids[@]:1}")
    fi
    (
        PROCS="$INNER_PROCS" bash "${scripts[$k]}" > "$dir/$k.out" 2>&1
        echo "$?" > "$dir/$k.rc"
    ) &
    pids+=("$!")
done
wait

fail=0
lost=0
for ((k = 0; k < n; k++)); do
    echo
    echo "-- san: ${scripts[$k]} --"
    cat "$dir/$k.out"
    if [ ! -s "$dir/$k.rc" ]; then
        echo "run_san_group: HARD FAILURE: ${scripts[$k]} vanished without an exit code (crashed or killed) — counting as failed" >&2
        lost=$((lost + 1))
        fail=$((fail + 1))
        continue
    fi
    rc="$(cat "$dir/$k.rc")"
    if [ "$rc" -ne 0 ]; then
        echo "run_san_group: ${scripts[$k]} exited $rc" >&2
        fail=$((fail + 1))
    fi
done

echo
if [ "$lost" -gt 0 ]; then
    echo "run_san_group: $((n - fail))/$n scripts passed, $lost lost"
else
    echo "run_san_group: $((n - fail))/$n scripts passed"
fi
[ "$fail" -eq 0 ]
