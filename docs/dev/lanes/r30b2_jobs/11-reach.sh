#!/usr/bin/env bash
# kit-r30b2-reach: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 11 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: REACH_ONLY=1 over the whole matrix, MECH_SCRATCH KEPT under build/r30b2/ (job 697 red: S1760/S1761 reach:MISSING, cause unknown; the kept per-row reach.log says why if it recurs).
# After: kit-r30b2-build (green). Expected wall: ~5 min (job 697: ~1.7 min).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry || exit 1
        echo "would run in $TREE: REACH_ONLY=1 over the whole matrix, MECH_SCRATCH KEPT under build/r30b2/ (job 697 red: S1760/S1761 reach:MISSING, cause unknown; the kept per-row reach.log says why if it recurs)"
        echo "boxqueue: cap 1200"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=1 lines=^== r30b2 step reach rc=0\$"
        exit 0 ;;
    --ready)
        r30b2_after kit-r30b2-build; exit $? ;;
esac
r30b2_enter
mkdir -p "$OUT/reach_scratch"
step reach env REACH_ONLY=1 KEEP=1 MECH_SCRATCH="$OUT/reach_scratch" bash tests/mech/run_sabotage_matrix.sh
