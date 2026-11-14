#!/usr/bin/env bash
# S3114 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p13; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3114 (its plant_spec; one source of the text).
SAB_ID="S3114-p2-dominates-noscan-run-less"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="g2pres"
SAB_DESC='P2 keeps rs && !proof->run on a run with no findable position: those dominated sites are no longer dominated (G2'"'"'s floor reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3114, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3114."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        else if (rsc && !proof->run) dom = 0;'
SAB_AFTER='        else if (rs && !proof->run) dom = 0;   /* SABOTAGE S3114 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
