#!/usr/bin/env bash
# S1916 (lane sar1, 2026-11-09; span_arms R1, witness W-R2, docs/design/span_arms.md §3.6) -- THE POWER UNROLLS `n` COPIES.
#
# T2 row 3 (src/facts/req.c `rr_rep_split`) unrolls the copies EVERY match
# takes, `m`. This plant unrolls `n`, so `xy(?:ab){1,3}zw` claims
# `xyababab` and the pre-check deletes `xyabzw`. Detector: the harness on
# tests/litscan/spanarms.rxt (both engines).
SAB_ID="S1916-rep-unrolls-max-copies"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_DESC="the necessary-run walk unrolls a variable repeat's maximum count instead of its minimum, so the run claims copies a match may not take and the pre-check deletes the shorter matches"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1916."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "xy(?:ab){1,3}zw" && grep -qE "^#define RX_REQ_RUN \"61627a77@[0-9]+\"$" "$REACH_TMP/o.c" && echo REACH-WR2-RUN'
SAB_REACH_EXPECT="REACH-WR2-RUN"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    RbRuns p = rr_pow(b, rr_pow_count(&b, m));'
SAB_AFTER='    RbRuns p = rr_pow(b, rr_pow_count(&b, n));   /* SABOTAGE S1916 */'
