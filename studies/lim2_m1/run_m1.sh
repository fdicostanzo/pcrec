#!/usr/bin/env bash
# studies/lim2_m1/run_m1.sh — the M1 sweep driver.
#
# Population (this lane's brief, §"POPULATION"): the whole pcrec .rxt corpus
# (same file set lim2_census.c's own run_census.sh walks) at the size cuts
# lim2_m1.c enforces itself (>65535 raw table entries, matching lim2_census's
# own PREMUL_MAX_ENTRIES population; OR >1000 raw states, the broader "large-
# DFA tail" cut this lane's brief asks for) -- PLUS two files force-included
# regardless of size, because the charter names them explicitly:
# tests/base/k18_cost_gates.rxt (the census witness plus the nested-counted
# family) and tests/counterk/counterk.rxt (the counted-repeat differential
# tower) -- PLUS pcrec-bench's bench/altwide set, read-only, force-included,
# if the sibling repo is reachable (this box: /Users/fdicostanzo/pcrec-bench;
# skipped loudly, never silently, if absent -- matching lim2_census's own
# precedent for an optional external population).
#
# Usage: bash run_m1.sh   (from this directory, after `make`)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
BIN="$SCRIPT_DIR/lim2_m1"
BENCH_ALTWIDE_DIR="/Users/fdicostanzo/pcrec-bench/bench/altwide/patterns"

if [ ! -x "$BIN" ]; then
    echo "lim2_m1 not built -- run 'make CC=gcc-16' in this directory first" >&2
    exit 1
fi

FORCE_FILES=(
    "$ROOT_DIR/tests/base/k18_cost_gates.rxt"
    "$ROOT_DIR/tests/counterk/counterk.rxt"
    # Control population (the study's own M1 charter: "20 ordinary corpus
    # patterns as a control"): character-class tests, ordinary small
    # patterns with no counted-repeat blowup, force-included so the
    # near-immediate 100%-explored case is represented in the data
    # alongside the heavy-shrink witnesses above.
    "$ROOT_DIR/tests/classes/classes.rxt"
)

ARGS=()
# Force-included files first (their own `--force` flag applies only to the
# ONE file that follows it, matching lim2_m1.c's argv parsing).
for f in "${FORCE_FILES[@]}"; do
    ARGS+=(--force "$f")
done

# The rest of the corpus, ordinary population selection (the size cuts
# decide inclusion). Force files are excluded from this walk so they are
# not measured twice.
while IFS= read -r -d '' f; do
    skip=0
    for ff in "${FORCE_FILES[@]}"; do
        [ "$f" = "$ff" ] && skip=1
    done
    [ "$skip" = 0 ] && ARGS+=("$f")
done < <(find "$ROOT_DIR/tests" -name '*.rxt' -not -path '*/known_fail/*' -print0 | LC_ALL=C sort -z)

if [ -d "$BENCH_ALTWIDE_DIR" ]; then
    while IFS= read -r -d '' f; do
        ARGS+=("$f")
    done < <(find "$BENCH_ALTWIDE_DIR" -name '*.rx' -print0 | LC_ALL=C sort -z)
    echo "pcrec-bench's altwide set found and included ($(find "$BENCH_ALTWIDE_DIR" -name '*.rx' | wc -l) patterns, force-included by lim2_m1.c's do_rx_file)"
else
    echo "SKIP: pcrec-bench not reachable at $BENCH_ALTWIDE_DIR -- corpus-only population"
fi

"$BIN" "${ARGS[@]}" > "$SCRIPT_DIR/m1_data.tsv" 2> "$SCRIPT_DIR/m1_summary.txt"
rc=$?
cat "$SCRIPT_DIR/m1_summary.txt"
echo
echo "population rows written to m1_data.tsv: $(($(wc -l < "$SCRIPT_DIR/m1_data.tsv") - 1))"
exit $rc
