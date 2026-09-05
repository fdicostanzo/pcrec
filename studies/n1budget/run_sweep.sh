#!/usr/bin/env bash
# studies/n1budget/run_sweep.sh — finds pcrec's .rxt corpus and (read-only,
# if present) pcrec-bench's altwide pattern set, runs the built n1_measure
# binary over the union, and regenerates n1_data.tsv / n1_summary.txt in
# this directory. Modelled directly on studies/lim2_census/run_census.sh.
#
# BENCH_ALTWIDE_DIR defaults to the sibling repo's path on the project's
# main Linux dev box (matching lim2_census.c's/lim2_m1.c's own hardcoded
# default); override it for a different box (e.g. this lane's own macOS
# box: `BENCH_ALTWIDE_DIR=/Users/you/pcrec-bench/bench/altwide/patterns`).
#
# Usage: bash run_sweep.sh   (from this directory, after `make`)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
BIN="$SCRIPT_DIR/n1_measure"
BENCH_ALTWIDE_DIR="${BENCH_ALTWIDE_DIR:-/home/duxevents/pcrec-bench/bench/altwide/patterns}"

if [ ! -x "$BIN" ]; then
    echo "n1_measure not built -- run 'make' in this directory first" >&2
    exit 1
fi

# Run from ROOT_DIR so every corpus id is REPO-RELATIVE (census_data.tsv's
# own convention) rather than embedding this checkout's absolute path.
cd "$ROOT_DIR" || exit 1

ARGS=()
while IFS= read -r -d '' f; do ARGS+=("$f"); done \
    < <(find tests -name '*.rxt' -print0 | LC_ALL=C sort -z)

if [ -d "$BENCH_ALTWIDE_DIR" ]; then
    while IFS= read -r -d '' f; do ARGS+=("$f"); done \
        < <(find "$BENCH_ALTWIDE_DIR" -name '*.rx' -print0 | LC_ALL=C sort -z)
    echo "pcrec-bench's altwide set found and included ($(find "$BENCH_ALTWIDE_DIR" -name '*.rx' | wc -l) patterns)"
else
    echo "SKIP: pcrec-bench not reachable at $BENCH_ALTWIDE_DIR -- corpus-only population"
fi

"$BIN" "${ARGS[@]}" > "$SCRIPT_DIR/n1_data.tsv" 2> "$SCRIPT_DIR/n1_summary.txt"
rc=$?
cat "$SCRIPT_DIR/n1_summary.txt"
echo
echo "rows written to n1_data.tsv: $(wc -l < "$SCRIPT_DIR/n1_data.tsv")"
exit $rc
