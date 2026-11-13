#!/usr/bin/env bash
# S3101 -- R-38 K38-3 (docs/design/memfn/span_runs_sheet.md §5's K38-3 row; §3.5 W-K4a/W-K4b;
# lane k383). THE w32 ARM'S FIRST LOAD ALIGNED DOWN (W-K4b): as S3100 on the w32 level (W 32).
# Detector: G2's presence family WITH its ASan+UBSan build (arm g2pres-asan), layout A: an ASan report. Second detector: the occurrence oracle.
SAB_ID="S3101-w32-arm-first-load-aligned-down"
SAB_FILE="memfn/src/vrun.c"
SAB_SUITES="g2pres-asan"
SAB_DESC="the w32 arm's first load aligned down below the subject: ASan in layout A (W-K4b) must report"
SAB_DOC_FIGURE="HAND-MEASURED by lane k383 2026-11-12 (docs/dev/lanes/k383_report.md): memfn/tests/run_g2_pres.sh --plant S3101 RED (ERROR: AddressSanitizer: heap-buffer-overflow; oracle RED violations=332). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3101."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o->puts(o->u, "    size_t i = pos;\n"
                  "    for (;;) {\n"'
SAB_AFTER='    if (d->level == LV_X86_W32) kit_out(o, "    size_t i = pos - (size_t)((uintptr_t)(subject + pos + %d) & %u);\n", ka, vw - 1);   /* SABOTAGE S3101 */
    else o->puts(o->u, "    size_t i = pos;\n");
    o->puts(o->u, "    for (;;) {\n"'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-W32-ARM"
