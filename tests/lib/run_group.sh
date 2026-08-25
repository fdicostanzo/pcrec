#!/usr/bin/env bash
# tests/lib/run_group.sh — [TT-2] run N independent test scripts CONCURRENTLY
# as one Makefile section target, with the same "a lost worker is a HARD
# FAIL, never a pass" discipline tests/harness/run.sh and (since [TT-2])
# tests/reject/run_reject_tests.sh already follow.
#
# Usage: bash tests/lib/run_group.sh SCRIPT [SCRIPT ...]
#   Each SCRIPT is a shell command line run via `bash -c "$SCRIPT"` from
#   whatever cwd run_group.sh itself was invoked from (the repo root, same
#   as every suite script already assumes): this is for scripts that already
#   isolate themselves with their own `mktemp -d` workdir and only ever READ
#   build/pcrec / build/libpcrec.a — the same safety argument PROCS=N already
#   relies on inside run.sh and run_reject_tests.sh. Do not group scripts
#   that share mutable state.
#
# GROUP_PROCS=1 runs the scripts SERIALLY, in argument order, each one's
# output printed as it finishes — this is how a plain `make test` at
# PROCS=1 gets back the historical sequential-script behaviour of a section
# target whose recipe used to just be N lines in a row, byte for byte
# (GROUP_PROCS=1 never backgrounds anything). ANY OTHER VALUE (including
# unset, which defaults to 0) launches every script at once with no
# throttling in between — there are only ever 2-3 scripts in a group here,
# never enough to want real job-pool capping, so GROUP_PROCS's magnitude
# above 1 does not change behaviour; it exists so the Makefile can pass the
# same `PROCS=$${PROCS:-$$(nproc)}` expression every other [TT-2] target
# uses without a special case.
#
# At GROUP_PROCS>1, output is replayed in ARGUMENT ORDER (not completion
# order) once every script has finished, each script's complete
# stdout+stderr as one contiguous block, so nothing interleaves mid-line —
# the same legibility rule the reject/corpus parallel dispatchers follow. A
# script's own exit code is preserved; a script that produced no recorded
# exit code at all (killed, crashed, OOM-killed) is a HARD FAILURE distinct
# from, and never conflated with, an ordinary nonzero exit.
#
# Exit status: 0 iff every script exited 0. Otherwise nonzero, and the
# summary line names how many passed / vanished.
set -u

# [K35, ruled by Frank at the [DD-14] close, 2026-08-25] THE GENERAL FIX:
# NO SCRIPT BELOW THIS ONE INHERITS THE AMBIENT LOCALE. Under `en_US.UTF-8`
# `sort` collates at a level that treats punctuation as IGNORABLE, so for a
# corpus of REGEXES `a{0,0}b` and `(a){0,0}b` compare EQUAL and `sort -u`
# silently drops one — and the survivor is the spelling WITHOUT punctuation,
# i.e. the STRUCTURED half of every collision is what is lost. MEASURED on
# this tree 2026-08-25: the corpus pattern extraction yields 1,784 patterns
# in the ambient locale and 2,758 under LC_ALL=C, a 35% silent shrink.
# K35's own history is why this is here and not only at each site: the
# hazard was written down at tests/cli/run_cli_tests.sh:786 and then recurred
# five times, because a lesson recorded in one file does not reach the next
# author. Every site is ALSO guarded individually (belt and braces — a script
# run directly from a Makefile recipe never passes through here), and
# run_codegen_tests.sh carries a structural check that greps for an
# unguarded `sort` in any tests/**/run_*.sh and fails naming it.
export LC_ALL=C

if [ "$#" -eq 0 ]; then
    echo "run_group: usage: bash tests/lib/run_group.sh SCRIPT [SCRIPT ...]" >&2
    exit 2
fi

GROUP_PROCS="${GROUP_PROCS:-0}"   # 0 sentinel means "unset -> fully parallel"
case "$GROUP_PROCS" in (''|*[!0-9]*) echo "run_group: GROUP_PROCS must be a non-negative integer, got '$GROUP_PROCS'" >&2; exit 2;; esac

n=$#
scripts=("$@")

if [ "$GROUP_PROCS" -eq 1 ]; then
    # Serial path: exactly the pre-[TT-2] behaviour (N lines run in order,
    # each one's output appearing as it happens) — no backgrounding, no
    # temp files, nothing that could behave differently from a bare
    # `bash script1 && bash script2 && ...` recipe.
    fail=0
    for ((k = 0; k < n; k++)); do
        bash -c "${scripts[$k]}"
        rc=$?
        [ "$rc" -eq 0 ] || { echo "run_group: script $k ('${scripts[$k]}') exited $rc" >&2; fail=$((fail + 1)); }
    done
    echo "run_group: $((n - fail))/$n scripts passed (serial)"
    [ "$fail" -eq 0 ]
    exit $?
fi

dir="$(mktemp -d)"
trap 'rm -rf "$dir"' EXIT

for ((k = 0; k < n; k++)); do
    ( bash -c "${scripts[$k]}" > "$dir/$k.out" 2>&1; echo "$?" > "$dir/$k.rc" ) &
done
wait

fail=0
lost=0
for ((k = 0; k < n; k++)); do
    echo "== run_group[$k]: ${scripts[$k]} =="
    cat "$dir/$k.out"
    if [ ! -s "$dir/$k.rc" ]; then
        # [TT-2 discipline] a lost/crashed worker is a HARD FAIL, never read
        # as a pass — it never got the chance to write its own exit code.
        echo "run_group: HARD FAILURE: script $k ('${scripts[$k]}') vanished without an exit code (crashed or killed) — counting as failed" >&2
        lost=$((lost + 1))
        fail=$((fail + 1))
        continue
    fi
    rc="$(cat "$dir/$k.rc")"
    if [ "$rc" -ne 0 ]; then
        echo "run_group: script $k ('${scripts[$k]}') exited $rc" >&2
        fail=$((fail + 1))
    fi
done

if [ "$lost" -gt 0 ]; then
    echo "run_group: $((n - fail))/$n scripts passed, $lost lost"
else
    echo "run_group: $((n - fail))/$n scripts passed"
fi
[ "$fail" -eq 0 ]
