#!/usr/bin/env bash
# kit-r30b2-mech-b: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 10 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: mech, second half (39 rows).
# After: kit-r30b2-mech-a (green). Expected wall: ~45 min (job 697: 76 rows in 86 min).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry || exit 1
        n=$(echo $IDS_B | wc -w); [ "$n" = "$NIDS_B" ] || { echo "IDS_B has $n ids, not $NIDS_B" >&2; exit 1; }
        echo "would run in $TREE: mech, second half (39 rows)"
        echo "boxqueue: cap 3600"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=1 lines=^== r30b2 step mech_b rc=0\$"
        exit 0 ;;
    --ready)
        r30b2_after kit-r30b2-mech-a; exit $? ;;
esac
r30b2_enter
step mech_b bash tests/mech/run_sabotage_matrix.sh $IDS_B
