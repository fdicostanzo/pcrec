# S1895 ([XARCH-DEV] U3, lane u3crit; review 2026-11-08-r5-xarch X-1, X-2) -- the target headers' render writes nothing: a level's vector header and a compound part's own `#include <string.h>` are then never written ahead of the region, so the header's inline functions are first read inside it (the part's own line) or not at all, and a gcc consumer that #includes a v3 artifact and then uses SSE2 intrinsics, a second artifact or a fortified memcpy fails to compile ("inlining failed ... target specific option mismatch").
# Detector (arm memfntargets): tests/memfn/run_targets.sh section 4b's consumer-TU cells (intrin, two-O2, two-O0, fortify; measured red on the pre-fix build).
SAB_ID="S1895-target-headers-dropped"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="memfntargets"
SAB_DESC="the target headers ahead of the region are never written, so the region reads them first (or a level's helper finds no header) and a consumer TU after the artifact fails to compile"
SAB_DOC_FIGURE="memfntargets: run_targets.sh's consumer-TU cells read red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1895."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        text = pcrec_sb_fragf(&cx->arena, "%s%s", text, line);'
SAB_AFTER='        (void)line;   /* SABOTAGE S1895 */'
