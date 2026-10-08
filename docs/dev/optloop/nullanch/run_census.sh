#!/bin/bash
# [NULLABLE-ANCH] STEP 0: rebuild everything in this directory from a built
# tree. usage: run_census.sh [TREE_ROOT] [BENCH_DIR] [SCRATCH]   (light, -j4)
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=${1:-$(cd "$HERE/../../../.." && pwd)}
BENCH=${2:-/home/pcrec/projects/pcrec-bench}     # READ-ONLY reference
S=${3:-$ROOT/build/nullanch}; mkdir -p "$S"
[ -x "$ROOT/build/pcrec" ] && [ -f "$ROOT/build/libpcrec.a" ] || { echo "make first"; exit 2; }
gcc -O1 -g -std=gnu11 -Wall -Wextra -I"$ROOT/lib" -I"$ROOT/src" -o "$S/anch_probe" \
    "$HERE/anch_probe.c" "$ROOT/build/libpcrec.a"
python3 -I "$HERE/census.py" "$ROOT/build/pcrec" "$S/anch_probe" "$BENCH" "$S/out" 4
python3 -I "$HERE/summarize.py" "$S/out/census_rows.tsv" | tee "$S/out/census_summary.txt"
"$HERE/timing.sh" "$ROOT/build/pcrec" "$S/timing" | tee "$S/out/timing_results.tsv"
"$HERE/diff.sh" "$ROOT/build/pcrec" "$S/diff" | tee "$S/out/diff_results.txt"
