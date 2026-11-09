# S1896 ([XARCH-DEV] U3, lane u3d27; D27 region suite F1) -- a spliced compound part writes its header lines with no held mark, so the shell keeps them where the part's text lies: INSIDE the target's region (a compound part's `#include <string.h>`, and `--emit-main`'s `<stdio.h>`/`<string.h>`, repeated in there). match_api.md §6.3.10¶15: the region holds no `#include`.
# Detector (arm memfntargets): tests/memfn/run_targets.sh section 4b's F1 checks on the v3 compound controls c.c and d.c (measured red on the pre-fix build: includes-inside=1 and 5).
SAB_ID="S1896-part-header-not-held"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="memfntargets"
SAB_DESC="a compound part's header lines are written plainly, so they stay inside the shell's target region"
SAB_DOC_FIGURE="memfntargets: run_targets.sh's F1 checks read red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1896."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_is_part(cx) && cx->emit_in->unrendered &&'
SAB_AFTER='    if (0 && pcrec_is_part(cx) && cx->emit_in->unrendered &&   /* SABOTAGE S1896 */'
