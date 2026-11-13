#!/usr/bin/env bash
# S3061 -- R-38 K38-2 (docs/design/memfn/span_runs_sheet.md rev 1.3 §3.3, §3.5 W-K1; lane k382).
# THE FLOOR WRAPS: the run part's floor is spelled `lo - N` in size_t with no clamp
# (presence.c kit_run_floor, read by precheck.c and generic.c), so where lo < -omin it wraps
# to about 2^64.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), the witness W-K1b (run `foobar`,
# omin -3, origin 1, scan offset 0 < N - origin: expected candidate 0; review 2026-11-11 r1 k382
# F16, lane k382fix). It reds on the ANSWER: on the generic pass in layout U, on the precheck pass
# in layout L. W-K1 (scan offset 5 >= N - origin) cannot move its answer under this plant (modulo
# 2^64 the wrapped floor lands on the same candidate); it reds only by layout L's faults.
SAB_ID="S3061-run-floor-wraps-unclamped"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="g2pres"
SAB_DESC="the run part's floor spelled lo - N in size_t with no clamp: W-K1b's answer must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382fix 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3061 RED by W-K1b's answer (generic U -1, precheck L -1, want 0; oracle violations=12120). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3061."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kb_printf(&f, "(%s >= %llu ? %s - %llu : 0)", lo, back, lo, back);'
SAB_AFTER='    kb_printf(&f, "(%s - %llu)", lo, back);   /* SABOTAGE S3061 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-NEG-FLOOR"
