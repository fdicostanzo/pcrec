#!/usr/bin/env bash
# S3120 -- R-38 Part D D3 (docs/design/memfn/part_d.md rev 4 section 5.1 D3, plant p12; lane partd2).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3120 (its plant_spec; one source of the text).
SAB_ID="S3120-run-part-record-skips-scanless"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2pres"
SAB_DESC='the derived run part record is not printed for a scan-less part: the census counts fewer every-pos parts than G2 rendered (D3 reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd2 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3120, docs/dev/lanes/partd2_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3120."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!quiet) {
        fprintf(stderr, "MFTRACE run_part_terms'
SAB_AFTER='    if (!quiet && q->plan_hint != MF_NO_PRED) {   /* SABOTAGE S3120 */
        fprintf(stderr, "MFTRACE run_part_terms'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
