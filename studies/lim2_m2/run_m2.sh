#!/usr/bin/env bash
# studies/lim2_m2/run_m2.sh -- the M2 sweep driver. Runs lim2_m2 TWICE (env
# var off, then on) over the SAME file list, matching the study's own M2
# charter population plus this lane's brief: the shipped corpus's DFA-route
# constructions, tests/base/k18_cost_gates.rxt (the census witness), and
# docs/dev/dfamin_m1m2_evidence/k25_chain_ladder.rxt (K25's own chain
# shapes). tests/counterk/counterk.rxt is included too, matching M1's own
# force-included population (docs/dev/lim2_m1_partition_measurement.md §2).
#
# Usage: bash run_m2.sh   (from this directory, after `make CC=gcc-16`)
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
BIN="$SCRIPT_DIR/lim2_m2"

if [ ! -x "$BIN" ]; then
    echo "lim2_m2 not built -- run 'make CC=gcc-16' in this directory first" >&2
    exit 1
fi

FORCE_FILES=(
    "$ROOT_DIR/tests/base/k18_cost_gates.rxt"
    "$ROOT_DIR/tests/counterk/counterk.rxt"
    "$SCRIPT_DIR/../../docs/dev/dfamin_m1m2_evidence/k25_chain_ladder.rxt"
)

FILES=("${FORCE_FILES[@]}")
while IFS= read -r -d '' f; do
    skip=0
    for ff in "${FORCE_FILES[@]}"; do [ "$f" = "$ff" ] && skip=1; done
    [ "$skip" = 0 ] && FILES+=("$f")
done < <(find "$ROOT_DIR/tests" -name '*.rxt' -not -path '*/known_fail/*' -print0 | LC_ALL=C sort -z)

echo "files: ${#FILES[@]}"

"$BIN" "${FILES[@]}" > "$SCRIPT_DIR/m2_baseline.tsv" 2> "$SCRIPT_DIR/m2_baseline.summary.txt"
echo "baseline done, rc=$?"
cat "$SCRIPT_DIR/m2_baseline.summary.txt"

PCREC_PROBE_M2=1 "$BIN" "${FILES[@]}" > "$SCRIPT_DIR/m2_pruned.tsv" 2> "$SCRIPT_DIR/m2_pruned.summary.txt"
echo "pruned done, rc=$?"
cat "$SCRIPT_DIR/m2_pruned.summary.txt"
