#!/usr/bin/env bash
# kit-r30b2-census: lane r30bfix's re-run of [MEMFN] R-30 on the merge of main 5c60e118c (abi 94,
# provisional), stage 2 of 11 (README.md here; docs/dev/lanes/r30btri_report.md "Re-run plan").
# Stage: refbuild of BASE (main 5c60e118c) + r30b_evidence/census.py (movers judged against the BOTH-ASKS population read from the reference's own artifacts).
# After: kit-r30b2-build (green). Expected wall: ~5 min (job 697: ~35 s; larger with main's VMREC).
# One stage per job (BOILERPLATE, Frank 2026-10-30); output under build/r30b2/.
# Correctness run: no quiet gate, no hold. STAGED by lane r30bfix, queued by the kit manager.
set -u
. /home/pcrec/projects/pcrec/worktrees/r30b/docs/dev/lanes/r30b2_jobs/common.sh
case "${1:-}" in
    --dry-run)
        r30b2_dry || exit 1
        python3 -I -c 'import ast,sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]' "$E/census.py" || exit 1
        echo "would run in $TREE: refbuild of BASE (main 5c60e118c) + r30b_evidence/census.py (movers judged against the BOTH-ASKS population read from the reference's own artifacts)"
        echo "boxqueue: cap 1800"
        echo "boxqueue: patience none"
        echo "boxqueue: expect steps=2 lines=^== r30b2 step [a-z_]+ rc=0\$"
        exit 0 ;;
    --ready)
        r30b2_after kit-r30b2-build; exit $? ;;
esac
refbuild() {
    rm -rf "$OUT/ref" && mkdir -p "$OUT/ref" &&
        git -C "$TREE" archive "$BASE" | tar -x -C "$OUT/ref" &&
        make -C "$OUT/ref" -j16 && echo "$BASE" > "$OUT/ref/REV" && echo "refbuild: ref $BASE; tip $TIP"
}
r30b2_enter
step refbuild refbuild || exit 1
step census python3 -I "$E/census.py" --base "$OUT/ref/build/pcrec" --new build/pcrec --harness build/pcrec-harness --tree "$TREE" --out "$OUT/census.txt" --jobs 16
