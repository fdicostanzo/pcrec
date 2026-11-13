#!/usr/bin/env bash
# S3112 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p7; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3112 (its plant_spec; one source of the text).
SAB_ID="S3112-stretch-widened-past-wide"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2pres"
SAB_DESC='the direct translation'"'"'s stretch widened past a wide position: the run term reaches a position with no (T, K) spelling (refused)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3112, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3112."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        while (b < hi && kit_pos_spelled(run->set[b])) b++;'
SAB_AFTER='        while (b < hi) b++;   /* SABOTAGE S3112 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
