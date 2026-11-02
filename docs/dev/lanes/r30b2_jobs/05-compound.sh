#!/usr/bin/env bash
# kit-r30b2-compound: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 5 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: make test-compound (job 697 red inside make test: G7 lever fence, triage fix 3).
# After: kit-r30b2-build (green). Expected wall: ~10 min (an inference; it was not a step of job 697).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry test-compound || exit 1
        echo "would run in $TREE: make test-compound (job 697 red inside make test: G7 lever fence, triage fix 3)"
        echo "boxqueue: cap 1800"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=1 lines=^== r30b2 step compound rc=0\$"
        exit 0 ;;
    --ready)
        r30b2_after kit-r30b2-build; exit $? ;;
esac
r30b2_enter
step compound make test-compound
