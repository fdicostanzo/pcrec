#!/usr/bin/env bash
# S3102 -- R-38 K38-3 (docs/design/memfn/span_runs_sheet.md §5's K38-3 row; §3.5 W-K4a/W-K4b;
# lane k383). THE CELLS' CONTROL: the w32 arm's entry threshold raised past the generator's longest subject (entered only when n - pos >= run_len + 2W + 24); the text still carries __w32(, so the text census (simd32) stays green.
# Detector: G2's presence family's per-level cells (K38-3): the w32 arm-entry cells (U, L, A) of the x86-64-v3 passes read 0, a named failure.
SAB_ID="S3102-w32-arm-entry-threshold-raised"
SAB_FILE="memfn/src/vrun.c"
SAB_SUITES="g2pres"
SAB_DESC="the w32 arm is rendered but never entered: the per-level arm-entry cells must read 0 and red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k383 2026-11-12 (docs/dev/lanes/k383_report.md): memfn/tests/run_g2_pres.sh --plant S3102 RED (CELL: x86-64-v3.0: w32 A: 0 arm entries (a cell that measures 0)). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3102."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_out(o, "    if (pos >= n || n - pos < %u) return %s(subject, n, pos);\n", r, fall);'
SAB_AFTER='    kit_out(o, "    if (pos >= n || n - pos < %u) return %s(subject, n, pos);\n", d->level == LV_X86_W32 ? r + vw + 25 : r, fall);   /* SABOTAGE S3102 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-W32-ARM"
