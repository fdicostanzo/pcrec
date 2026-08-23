#!/usr/bin/env bash
# studies/tt4_batching/census/run_section_census.sh — [TT-4.1] Stage A driver.
#
# Runs each `test-*` Makefile section ONE AT A TIME (never overlapping with
# another section — internal PROCS parallelism WITHIN a section is left as
# the Makefile already sets it, default $(nproc)) with the gcc/cc/pcrec/
# timeout/python3 shims (./shim/) wired onto PATH, and records:
#   - one combined TSV invocation log ($OUTDIR/census.tsv) tagged per line
#     with the section (TT4_SECTION) — see shim/gcc and shim/pcrec headers
#     for the exact column format;
#   - one `/usr/bin/time -v` report per section ($OUTDIR/<section>.time),
#     giving section wall clock AND CPU (user+sys) from a real run, not an
#     estimate.
#
# Usage:
#   bash run_section_census.sh [section ...]      # default: all 21 test: sections
#   bash run_section_census.sh --validate SECTION # shim on/off smoke check
#
# Must be run from the pcrec worktree root (cd there first) with `make all`
# ALREADY built and up to date — this script never builds; the point is that
# rerunning `make test-<x>` with a fresh binary already in place triggers ZERO
# extra gcc/pcrec calls from the `all` prerequisite, so every logged call
# belongs to the section's own test workload, not tree-build noise.
#
# TMPDIR: honours the caller's TMPDIR (the corpus/reject sections' own
# guidance is /var/tmp on this box — /tmp is a quota'd tmpfs); this script
# does not override it.

set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CENSUS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHIM_DIR="$CENSUS_DIR/shim"
OUTDIR="${TT4_OUTDIR:-$ROOT_DIR/build/tt4_census}"
mkdir -p "$OUTDIR"

# All 21 `test:` prerequisite targets (Makefile's `test:` line), in the same
# order `make test` itself runs them.
ALL_SECTIONS=(corpus cli reject registry parse gentimeout codegen vm \
    possessify rungselect counterk mrl prefilter altcls assertions atomic \
    backrefs encseam resource capturediff known-fail thread)

# ---- resolve the REAL compiler, pcrec, timeout, python3 BEFORE the shim
# goes on PATH -----
REAL_GCC="$(command -v gcc)"
REAL_TIMEOUT="$(command -v timeout)"
REAL_PYTHON3="$(command -v python3)"
REAL_PCREC="$ROOT_DIR/build/pcrec"
if [ -z "$REAL_GCC" ] || [ ! -x "$REAL_GCC" ]; then
    echo "run_section_census.sh: cannot resolve real gcc via command -v" >&2
    exit 2
fi
if [ -z "$REAL_TIMEOUT" ] || [ ! -x "$REAL_TIMEOUT" ]; then
    echo "run_section_census.sh: cannot resolve real timeout via command -v" >&2
    exit 2
fi
if [ -z "$REAL_PYTHON3" ] || [ ! -x "$REAL_PYTHON3" ]; then
    echo "run_section_census.sh: cannot resolve real python3 via command -v" >&2
    exit 2
fi
if [ ! -x "$REAL_PCREC" ]; then
    echo "run_section_census.sh: $REAL_PCREC not built — run 'make -j\$(nproc) all' first" >&2
    exit 2
fi
REAL_GCC="$(readlink -f "$REAL_GCC")"
REAL_TIMEOUT="$(readlink -f "$REAL_TIMEOUT")"
REAL_PYTHON3="$(readlink -f "$REAL_PYTHON3")"
REAL_PCREC="$(readlink -f "$REAL_PCREC")"

export TT4_REAL_GCC="$REAL_GCC"
export TT4_REAL_PCREC="$REAL_PCREC"
export TT4_REAL_TIMEOUT="$REAL_TIMEOUT"
export TT4_REAL_PYTHON3="$REAL_PYTHON3"

# NOT exported globally: PATH/PCREC only get the shim wired in for an
# actual census run (run_one_section) or the "WITH shim" validate leg — the
# "WITHOUT shim" validate leg below must see the tree's ordinary PATH/PCREC
# untouched, or the comparison is not testing what it claims to.
SHIMMED_PATH="$SHIM_DIR:$PATH"
SHIMMED_PCREC="$SHIM_DIR/pcrec"

# Per-section timeout: a single stuck/slow section must not silently eat the
# whole run's budget (that is exactly what happened 2026-08-23 -- an outer
# `timeout 1800 run_section_census.sh` fired mid-`assertions`, and every
# section queued after it was simply never reached). `timeout` runs its
# child in a new session, so it can and does deliver the signal to the
# whole `make`/bash/gcc process tree, not just the direct child.
# TT4_SECTION_TIMEOUT is a single default for every section; override per
# invocation for a section known to run long (assertions measured needing
# it — see the memo's "1800s bound" note).
TT4_SECTION_TIMEOUT="${TT4_SECTION_TIMEOUT:-900}"

run_one_section() {
    local sec="$1" log="$2"
    local target="test-$sec"
    local before after load_before load_after
    load_before="$(awk '{print $1}' /proc/loadavg)"
    before=$EPOCHREALTIME
    # $REAL_TIMEOUT (absolute path, resolved before the shim went on PATH)
    # here, NOT the bare `timeout` name -- this outer per-section wrapper is
    # THIS SCRIPT's own instrumentation, not the workload being measured,
    # and PATH is already set to SHIMMED_PATH for the command this line
    # launches, so a bare `timeout` would resolve to shim/timeout and
    # self-log an artifact call every section (caught before it shipped:
    # 2026-08-23, Stage A2).
    PATH="$SHIMMED_PATH" PCREC="$SHIMMED_PCREC" TT4_SECTION="$sec" TT4_LOG="$log" \
        "$REAL_TIMEOUT" "$TT4_SECTION_TIMEOUT" \
        /usr/bin/time -v -o "$OUTDIR/$sec.time" \
        make -C "$ROOT_DIR" "$target" \
        > "$OUTDIR/$sec.stdout" 2> "$OUTDIR/$sec.stderr"
    local rc=$?
    if [ "$rc" -eq 124 ]; then
        echo "run_section_census.sh: SECTION TIMEOUT: $sec exceeded TT4_SECTION_TIMEOUT=${TT4_SECTION_TIMEOUT}s -- its census.tsv rows for this run are PARTIAL, do not trust them without re-running with a larger timeout" >&2
    fi
    after=$EPOCHREALTIME
    load_after="$(awk '{print $1}' /proc/loadavg)"
    local wall
    wall="$(awk -v s="$before" -v e="$after" 'BEGIN{printf "%.3f", e - s}')"
    echo "$sec: make rc=$rc wall=${wall}s load_before=$load_before load_after=$load_after" \
        | tee -a "$OUTDIR/run_section_census.summary"
    return "$rc"
}

if [ "${1:-}" = "--validate" ]; then
    sec="${2:?usage: --validate SECTION}"
    target="test-$sec"
    echo "== validate: $target WITHOUT shim ==" >&2
    tstart=$EPOCHREALTIME
    make -C "$ROOT_DIR" "$target" > "$OUTDIR/${sec}.novalidate.out" 2>&1
    rc_off=$?
    tend=$EPOCHREALTIME
    wall_off="$(awk -v s="$tstart" -v e="$tend" 'BEGIN{printf "%.3f", e - s}')"
    grep -E '^cases (passed|failed):|^== Summary ==|PASS|FAIL|passed|failed' "$OUTDIR/${sec}.novalidate.out" \
        > "$OUTDIR/${sec}.novalidate.summary" || true

    echo "== validate: $target WITH shim ==" >&2
    log="$OUTDIR/${sec}.validate.tsv"
    : > "$log"
    tstart=$EPOCHREALTIME
    PATH="$SHIMMED_PATH" PCREC="$SHIMMED_PCREC" TT4_SECTION="$sec" TT4_LOG="$log" \
        make -C "$ROOT_DIR" "$target" > "$OUTDIR/${sec}.withvalidate.out" 2>&1
    rc_on=$?
    tend=$EPOCHREALTIME
    wall_on="$(awk -v s="$tstart" -v e="$tend" 'BEGIN{printf "%.3f", e - s}')"
    grep -E '^cases (passed|failed):|^== Summary ==|PASS|FAIL|passed|failed' "$OUTDIR/${sec}.withvalidate.out" \
        > "$OUTDIR/${sec}.withvalidate.summary" || true

    echo "rc_off=$rc_off rc_on=$rc_on wall_off=${wall_off}s wall_on=${wall_on}s shim_calls=$(wc -l < "$log")"
    if diff -q "$OUTDIR/${sec}.novalidate.summary" "$OUTDIR/${sec}.withvalidate.summary" > /dev/null; then
        echo "VALIDATE OK: identical PASS/FAIL summary with and without the shim"
    else
        echo "VALIDATE MISMATCH: summaries differ" >&2
        diff "$OUTDIR/${sec}.novalidate.summary" "$OUTDIR/${sec}.withvalidate.summary" >&2
        exit 1
    fi
    exit 0
fi

sections=("$@")
fresh_run=0
if [ "${#sections[@]}" -eq 0 ]; then
    sections=("${ALL_SECTIONS[@]}")
    fresh_run=1
fi

# RESUME SAFETY: a call naming EXPLICIT sections (the resume-after-timeout
# shape) APPENDS to the existing census.tsv/summary instead of truncating
# them -- a bound (timeout, kill) firing mid-run must not cost the sections
# that already finished. Only the no-args "run everything" shape starts
# fresh. (Bug found and fixed 2026-08-23: the original version truncated
# unconditionally, which would have discarded 11 already-completed
# sections' records the first time this script was re-invoked to cover a
# timeout's missing tail -- caught before that happened, not after.)
MASTER_LOG="$OUTDIR/census.tsv"
if [ "$fresh_run" -eq 1 ] || [ ! -s "$MASTER_LOG" ]; then
    : > "$MASTER_LOG"
    : > "$OUTDIR/run_section_census.summary"
else
    echo "run_section_census.sh: RESUMING -- appending to existing $MASTER_LOG ($(wc -l < "$MASTER_LOG") records already present)" >&2
fi

overall_rc=0
for sec in "${sections[@]}"; do
    run_one_section "$sec" "$MASTER_LOG" || overall_rc=1
done

echo "run_section_census.sh: done, combined log $MASTER_LOG ($(wc -l < "$MASTER_LOG") records), summary $OUTDIR/run_section_census.summary"
exit "$overall_rc"
