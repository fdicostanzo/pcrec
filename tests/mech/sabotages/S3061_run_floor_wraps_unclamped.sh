#!/usr/bin/env bash
# S3061 -- R-38 K38-2 (docs/design/memfn/span_runs_sheet.md rev 1.3 §3.3, §3.5 W-K1; lane k382).
# THE FLOOR WRAPS: the run part's floor is spelled `lo - N` in size_t with no clamp
# (precheck.c run_floor), so where lo < -omin it wraps to about 2^64.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), the §3.5 witness W-K1 (run
# `foobar`, omin -3, origin 1: expected candidate 0); the oracle step and layout L red too.
SAB_ID="S3061-run-floor-wraps-unclamped"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="g2pres"
SAB_DESC="the run part's floor spelled lo - N in size_t with no clamp: W-K1 must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3061 RED (W-K1; oracle violations=12060). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3061."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kb_printf(&f, "(%s >= %llu ? %s - %llu : 0)", lo, back, lo, back);'
SAB_AFTER='    kb_printf(&f, "(%s - %llu)", lo, back);   /* SABOTAGE S3061 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-NEG-FLOOR"
