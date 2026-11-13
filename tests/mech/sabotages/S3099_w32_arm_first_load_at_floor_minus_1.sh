#!/usr/bin/env bash
# S3099 -- R-38 K38-3 (docs/design/memfn/span_runs_sheet.md §5's K38-3 row; §3.5 W-K4a/W-K4b;
# lane k383). THE w32 ARM'S FIRST LOAD STARTS AT floor - 1 (W-K4a, UNALIGNED): as S3098 on the w32 level only.
# Detector: G2's presence family, layout L: the entry faults on the x86-64-v3 passes; the x86-64 and generic passes are unchanged. Second detector: the occurrence oracle.
SAB_ID="S3099-w32-arm-first-load-at-floor-minus-1"
SAB_FILE="memfn/src/vrun.c"
SAB_SUITES="g2pres"
SAB_DESC="the w32 arm's first load at floor - 1: layout L's guard page (W-K4a) must fault"
SAB_DOC_FIGURE="HAND-MEASURED by lane k383 2026-11-12 (docs/dev/lanes/k383_report.md): memfn/tests/run_g2_pres.sh --plant S3099 RED (LAYOUT: L ...: the entry faulted; oracle RED violations=219). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3099."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o->puts(o->u, "    size_t i = pos;\n"
                  "    for (;;) {\n"'
SAB_AFTER='    if (d->level == LV_X86_W32) kit_out(o, "    size_t i = pos - %d;\n", ka + 1);   /* SABOTAGE S3099 */
    else o->puts(o->u, "    size_t i = pos;\n");
    o->puts(o->u, "    for (;;) {\n"'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-W32-ARM"
