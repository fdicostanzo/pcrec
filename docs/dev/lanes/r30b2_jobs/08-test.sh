#!/usr/bin/env bash
# kit-r30b2-test: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 8 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: the full make test via scripts/perfrun (the arbiter; after codegen, memfn, compound, regrx).
# After: kit-r30b2-build, kit-r30b2-codegen, kit-r30b2-memfn, kit-r30b2-compound, kit-r30b2-regrx (green). Expected wall: ~25 min (job 697: 1332 s).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry || exit 1
        [ -x "$TREE/scripts/perfrun" ] || { echo "no scripts/perfrun" >&2; exit 1; }
        echo "would run in $TREE: the full make test via scripts/perfrun (the arbiter; after codegen, memfn, compound, regrx)"
        echo "boxqueue: cap 3600"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=1 lines=^== r30b2 step test rc=0\$"
        exit 0 ;;
    --ready)
        r30b2_after kit-r30b2-build kit-r30b2-codegen kit-r30b2-memfn kit-r30b2-compound kit-r30b2-regrx; exit $? ;;
esac
r30b2_enter
step test scripts/perfrun --label r30b2 -- "$OUT/test.make.log"
rc=$?
grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' "$OUT/test.make.log" | sed 's/^/test-red: /'
exit "$rc"
