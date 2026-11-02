#!/usr/bin/env bash
# 200-kit-r32-mech-s526: lane r32's one-row proof of [MEMFN] R-32 on worktrees/r32
# Stage: mech row S526 (must read DETECTED), make strict, make test-memfn-forms. One stage, ~2-3 min. STAGED, NOT queued.
set -u
TREE=/home/pcrec/projects/pcrec/worktrees/r32 IDS="S526"
case "${1:-}" in
    --dry-run)
        out=$(cd "$TREE" && VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh $IDS 2>&1) ||
            { printf '%s\n' "$out" | tail -3 >&2; exit 1; }
        n=$(printf '%s\n' "$out" | sed -n 's/^== mech FIELD VALIDATION COMPLETE: \([0-9]*\) def.*/\1/p')
        [ -n "$n" ] || { echo "no field-validation line" >&2; exit 1; }
        echo "would run in $TREE: bash tests/mech/run_sabotage_matrix.sh $IDS; make strict; make test-memfn-forms"
        echo "boxqueue: cap 900"
        echo "boxqueue: patience none"
        echo "boxqueue: est 180"
        echo "boxqueue: expect steps=3 lines=^== r32 step [a-z_]+ rc=0\$"
        exit 0 ;;
    --ready)
        exit 0 ;;
esac
cd "$TREE" || exit 1
export MECH_SCRATCH=/var/tmp/pcrec-pcrec/scratch/memfn/r32m
mkdir -p "$MECH_SCRATCH"
bad=0
step() {
    local name="$1"; shift
    "$@"; local rc=$?
    echo "== r32 step $name rc=$rc"
    [ "$rc" -eq 0 ] || bad=$((bad + 1))
}
mech() {
    local log="$MECH_SCRATCH/mech.log" rc
    bash tests/mech/run_sabotage_matrix.sh $IDS > "$log" 2>&1; rc=$?
    cat "$log"
    [ "$rc" -eq 0 ] || return 1
    grep -q '^== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, ' "$log"
}
step mech mech
step strict make strict
step forms make test-memfn-forms
[ "$bad" -eq 0 ]
