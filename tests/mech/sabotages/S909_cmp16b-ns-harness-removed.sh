#!/usr/bin/env bash
# S909 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-16 (row 3)) -- the namespace table's `harness-lever` row accepts every prefix, so `-p pcrec_harness_x` emits symbols under the lever's reserved prefix and the fence's one-global count can be spoofed by an artifact.
SAB_ID='S909-cmp16b-ns-harness-removed'
SAB_FILE='src/core/compile.c'
SAB_SUITES='compound'
SAB_DESC='the namespace table'\''s `harness-lever` row accepts every prefix, so `-p pcrec_harness_x` emits symbols under the lever'\''s reserved prefix and the fence'\''s one-global count can be spoofed by an artifact'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): compound arm 1 FAIL line (run_shell_checks.sh (2): -p pcrec_harness_x compiled). The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return !strncmp(p, PCREC_HARNESS_PREFIX, sizeof PCREC_HARNESS_PREFIX - 1);'
SAB_AFTER='    (void)p; return false;   /* SABOTAGE S909 */'
