#!/usr/bin/env bash
# studies/lim2_census/run_census.sh — the census's own driver: finds pcrec's
# .rxt corpus and (read-only, if present) pcrec-bench's altwide pattern set,
# runs the built `lim2_census` binary over the union, and regenerates
# census_data.tsv / census_summary.txt in this directory.
#
# Read-only against pcrec-bench: this script only READS
# bench/altwide/patterns/*.rx, never writes there, and skips it loudly
# (never silently) when the sibling repo is not present, matching PC-3's
# own precedent for an optional external dependency elsewhere in this repo.
#
# Usage: bash run_census.sh   (from this directory, after `make`)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
BIN="$SCRIPT_DIR/lim2_census"
BENCH_ALTWIDE_DIR="/home/duxevents/pcrec-bench/bench/altwide/patterns"

if [ ! -x "$BIN" ]; then
    echo "lim2_census not built -- run 'make' in this directory first" >&2
    exit 1
fi

ARGS=()
while IFS= read -r -d '' f; do ARGS+=("$f"); done \
    < <(find "$ROOT_DIR/tests" -name '*.rxt' -print0 | LC_ALL=C sort -z)

if [ -d "$BENCH_ALTWIDE_DIR" ]; then
    while IFS= read -r -d '' f; do ARGS+=("$f"); done \
        < <(find "$BENCH_ALTWIDE_DIR" -name '*.rx' -print0 | LC_ALL=C sort -z)
    echo "pcrec-bench's altwide set found and included ($(find "$BENCH_ALTWIDE_DIR" -name '*.rx' | wc -l) patterns)"
else
    echo "SKIP: pcrec-bench not reachable at $BENCH_ALTWIDE_DIR -- corpus-only population"
fi

"$BIN" "${ARGS[@]}" > "$SCRIPT_DIR/census_data.tsv" 2> "$SCRIPT_DIR/census_summary.txt"
rc=$?
cat "$SCRIPT_DIR/census_summary.txt"
echo
echo "population rows written to census_data.tsv: $(wc -l < "$SCRIPT_DIR/census_data.tsv")"
exit $rc
