#!/usr/bin/env bash
# S907 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-17) -- a second global under the lever's reserved prefix, so the lever is reachable through another name in the shipped archive.
SAB_ID='S907-cmp17-second-lever-global'
SAB_FILE='src/core/compile.c'
SAB_SUITES='compound'
SAB_DESC='a second global under the lever'\''s reserved prefix, so the lever is reachable through another name in the shipped archive'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG907@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return compile_driver(pattern, opt, out, err, NULL, NULL, NULL, NULL, NULL,
                          hopt ? &in : NULL);
}'
SAB_AFTER='    return compile_driver(pattern, opt, out, err, NULL, NULL, NULL, NULL, NULL,
                          hopt ? &in : NULL);
}
int pcrec_harness_compile_s907(void);
int pcrec_harness_compile_s907(void) { return 0; }   /* SABOTAGE S907 */'
