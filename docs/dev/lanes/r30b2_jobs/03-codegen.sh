#!/usr/bin/env bash
# kit-r30b2-codegen: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 3 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: make test-codegen (job 697 red: reqcube k66, triage fix 1).
# After: kit-r30b2-build (green). Expected wall: ~5 min (job 697: 3.5 min).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry test-codegen || exit 1
        echo "would run in $TREE: make test-codegen (job 697 red: reqcube k66, triage fix 1)"
        echo "boxqueue: cap 1200"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=1 lines=^== r30b2 step codegen rc=0\$"
        exit 0 ;;
    --ready)
        r30b2_after kit-r30b2-build; exit $? ;;
esac
r30b2_enter
step codegen make test-codegen
