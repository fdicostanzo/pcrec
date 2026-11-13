#!/usr/bin/env bash
# S3119 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1 and requests.md R-41, plant R-41; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3119 (its plant_spec; one source of the text).
SAB_ID="S3119-unbounded-head-not-declined"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="g2pres"
SAB_DESC='a stated unbounded K (MF_HEAD_MAX_UNBOUNDED, R-41) no longer declines the presence landmark: the bit is read as at K 0 (G2'"'"'s R-41 case reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3119, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3119."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (s->head_max == MF_HEAD_MAX_UNBOUNDED) out->landmark = 0;'
SAB_AFTER='        if (0) out->landmark = 0;   /* SABOTAGE S3119 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
