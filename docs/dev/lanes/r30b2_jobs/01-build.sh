#!/usr/bin/env bash
# kit-r30b2-build: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 1 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: mechval (both halves' ids) + make -j16 + make strict; records the tip every later stage checks.
# After: nothing (green). Expected wall: ~2 min (job 697: build+strict 16 s).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry strict || exit 1
        n=$(echo $IDS_A $IDS_B | wc -w); [ "$n" = $((NIDS_A + NIDS_B)) ] || { echo "IDS has $n ids, not $((NIDS_A + NIDS_B))" >&2; exit 1; }
        echo "would run in $TREE: mechval (both halves' ids) + make -j16 + make strict; records the tip every later stage checks"
        echo "boxqueue: cap 900"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=3 lines=^== r30b2 step [a-z_]+ rc=0\$"
        exit 0 ;;
    --ready)
        exit 0 ;;
esac
mechval() {
    local out n
    out=$(VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh $IDS_A $IDS_B 2>&1) || { printf '%s\n' "$out" | tail -3; return 1; }
    n=$(printf '%s\n' "$out" | sed -n 's/^== mech FIELD VALIDATION COMPLETE: \([0-9]*\) def.*/\1/p')
    echo "mechval: ${n:-none} ids valid"
    [ "$n" = $((NIDS_A + NIDS_B)) ]
}
r30b2_enter --record
rm -f "$OUT/TIP"
bad=0
step build make -j16 || bad=$((bad + 1))
step strict make strict || bad=$((bad + 1))
step mechval mechval || bad=$((bad + 1))
[ "$bad" -eq 0 ] || { echo "== r30b2 build: $bad step(s) failed; tip NOT recorded"; exit 1; }
echo "$TIP" > "$OUT/TIP"
echo "== r30b2 build: tip $TIP recorded"
