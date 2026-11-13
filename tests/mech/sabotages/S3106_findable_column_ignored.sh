#!/usr/bin/env bash
# S3106 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p1; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3106 (its plant_spec; one source of the text).
SAB_ID="S3106-findable-column-ignored"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2pres"
SAB_DESC='kit_run_member'"'"'s findable candidates read as every position: the run'"'"'s scan may land on a wide position (G2'"'"'s reply check reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3106, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3106."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (cand == KIT_CAND_EXACT ? count(set) != 1 : !kit_pos_spelled(set)) continue;'
SAB_AFTER='        if (cand == KIT_CAND_EXACT && count(set) != 1) continue;   /* SABOTAGE S3106 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
