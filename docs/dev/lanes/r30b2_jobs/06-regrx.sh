#!/usr/bin/env bash
# kit-r30b2-regrx: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 6 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: make test-registry, then make test-rxtsource (abi/pin readers move with the merge).
# After: kit-r30b2-build (green). Expected wall: ~3 min (job 697: 31 s + 72 s).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry test-registry test-rxtsource || exit 1
        echo "would run in $TREE: make test-registry, then make test-rxtsource (abi/pin readers move with the merge)"
        echo "boxqueue: cap 900"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=2 lines=^== r30b2 step [a-z_]+ rc=0\$"
        exit 0 ;;
    --ready)
        r30b2_after kit-r30b2-build; exit $? ;;
esac
r30b2_enter
bad=0
step registry make test-registry || bad=$((bad + 1))
step rxtsource make test-rxtsource || bad=$((bad + 1))
[ "$bad" -eq 0 ]
