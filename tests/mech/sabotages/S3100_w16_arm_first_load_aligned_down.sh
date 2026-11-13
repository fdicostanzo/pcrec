#!/usr/bin/env bash
# S3100 -- R-38 K38-3 (docs/design/memfn/span_runs_sheet.md §5's K38-3 row; §3.5 W-K4a/W-K4b;
# lane k383). THE w16 ARM'S FIRST LOAD ALIGNED DOWN (W-K4b): the block loop starts where the ADDRESS subject + floor + KA aligned down to 16 lies, so the first load can read up to 15 bytes below the subject and never leaves its page (layout L's guard cannot see it).
# Detector: G2's presence family WITH its ASan+UBSan build (arm g2pres-asan), layout A (the subject at offset 1..W-1 from a W-aligned heap block, the whole granules below it poisoned): an ASan report. Second detector: the occurrence oracle (layout U).
SAB_ID="S3100-w16-arm-first-load-aligned-down"
SAB_FILE="memfn/src/vrun.c"
SAB_SUITES="g2pres-asan"
SAB_DESC="the w16 arm's first load aligned down below the subject: ASan in layout A (W-K4b) must report"
SAB_DOC_FIGURE="HAND-MEASURED by lane k383 2026-11-12 (docs/dev/lanes/k383_report.md): memfn/tests/run_g2_pres.sh --plant S3100 RED (ERROR: AddressSanitizer: use-after-poison; oracle RED violations=1047). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3100."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o->puts(o->u, "    size_t i = pos;\n"
                  "    for (;;) {\n"'
SAB_AFTER='    if (d->level == LV_X86_W16) kit_out(o, "    size_t i = pos - (size_t)((uintptr_t)(subject + pos + %d) & %u);\n", ka, vw - 1);   /* SABOTAGE S3100 */
    else o->puts(o->u, "    size_t i = pos;\n");
    o->puts(o->u, "    for (;;) {\n"'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-W16-ARM"
