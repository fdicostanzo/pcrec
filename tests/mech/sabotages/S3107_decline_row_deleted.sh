#!/usr/bin/env bash
# S3107 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p2; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3107 (its plant_spec; one source of the text).
SAB_ID="S3107-decline-row-deleted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="g2pres"
SAB_DESC='the decline row PD deleted: a run with no findable position on an optional route reaches P3, which names no scan-less reply (G2 reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3107, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3107."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "PD", FD_PRES, KN_P, SF_RUN_NOSCAN, 0,'
SAB_AFTER='#if 0   /* SABOTAGE S3107 */
    { "PD", FD_PRES, KN_P, SF_RUN_NOSCAN, 0,'
SAB_FILE2="memfn/src/finder.c"
SAB_COUNT2=1
SAB_BEFORE2='"none: derived from the reply contract (no find tests the run)", &ct_pd },'
SAB_AFTER2='"none: derived from the reply contract (no find tests the run)", &ct_pd },
#endif'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
