#!/usr/bin/env bash
# S3113 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p10; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3113 (its plant_spec; one source of the text).
SAB_ID="S3113-every-pos-reads-byte-zero"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="g2pres"
SAB_DESC='the no-scan fact read as a scan of byte 0 and pair_holds left as b >= 0: scan-less parts search for byte 0 (G2 reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3113, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3113."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        *k = *a = *b = -1;'
SAB_AFTER='        *k = *a = *b = 0;   /* SABOTAGE S3113 */'
SAB_FILE2="memfn/src/ofsskip.c"
SAB_COUNT2=1
SAB_BEFORE2='    return x->a >= 0 && x->b >= 0;'
SAB_AFTER2='    return x->b >= 0;'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
