# S1896 ([XARCH-DEV] U3, lane u3d27; D27 region suite F1, ruling R2) -- pcrec's own `#include` lines that land inside the target's region are written with no held mark, so they stay there: a compound part's `#include <string.h>` and `--emit-main`'s `<stdio.h>`/`<string.h>` (repeated inside), a `--trace` VM's `<stdio.h>` (first read inside). match_api.md §6.3.10¶15: the region holds no `#include`.
# Detector (arm memfntargets): tests/memfn/run_targets.sh section 4b's F1 checks on the v3 controls c.c, d.c and t.c (measured red on the pre-fix build: includes-inside=1, 5 and 1).
SAB_ID="S1896-include-not-held"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="memfntargets"
SAB_DESC="pcrec's own include lines inside the target region are written with no held mark, so they stay inside it"
SAB_DOC_FIGURE="memfntargets: run_targets.sh's F1 checks read red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1896."
SAB_CATCH_GCC_MIN=15   # cloud run 43108213213 (ubuntu-latest, gcc 13): the fortify cell compiles there, F1 still reads red -> DETECTED; mechtri3
SAB_EXPECT=COMPILE-CATCH   # [MECH-NOCOMPILE] 2026-11-11 (mechtri2): the plant leaves <string.h> inside a target region, which gcc 15's always_inline memcpy refuses to compile in the check's cell (7d74499bc: memfntargets 4fail/38pass AND the cell's compile error); the F1 checks still read red
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_puts(c, PCREC_HELD_HEADER_MARK);'
SAB_AFTER='        ;   /* SABOTAGE S1896 */'
