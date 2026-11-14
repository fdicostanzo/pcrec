#!/usr/bin/env bash
# S3108 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p3; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3108 (its plant_spec; one source of the text).
SAB_ID="S3108-decline-on-cube-scan"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="g2pres"
SAB_DESC='a run whose scan is a two-member cube is handed back as having no scan, so PD declines it (G2'"'"'s decline equality reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3108, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3108."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        else if (run_noscan) *run_noscan = 1;'
SAB_AFTER='        else if (run_noscan) *run_noscan = 1;
        if (rr.has_scan && run_noscan && kit_pos_class_of(rs->set[rr.scan]) == KIT_POS_CUBE) *run_noscan = 1;   /* SABOTAGE S3108 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
