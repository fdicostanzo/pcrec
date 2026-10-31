#!/usr/bin/env bash
# kit-r30b2-memfn: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 4 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: the 15 memfn sections (job 697 red: simd-form floor, triage fix 2).
# After: kit-r30b2-build (green). Expected wall: ~10 min (job 697: ~7 min).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry test-memfn-arch test-memfn-arms test-memfn-deleg test-memfn-finder test-memfn-forms test-memfn-g2 test-memfn-guarded test-memfn-link test-memfn-manifest test-memfn-rank test-memfn-reach test-memfn-rows test-memfn-simdfloor test-memfn-stamps test-kitproof || exit 1
        echo "would run in $TREE: the 15 memfn sections (job 697 red: simd-form floor, triage fix 2)"
        echo "boxqueue: cap 1800"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=1 lines=^== r30b2 step memfn rc=0\$"
        exit 0 ;;
    --ready)
        r30b2_after kit-r30b2-build; exit $? ;;
esac
r30b2_enter
step memfn make -k -j16 -Otarget test-memfn-arch test-memfn-arms test-memfn-deleg test-memfn-finder test-memfn-forms test-memfn-g2 test-memfn-guarded test-memfn-link test-memfn-manifest test-memfn-rank test-memfn-reach test-memfn-rows test-memfn-simdfloor test-memfn-stamps test-kitproof
