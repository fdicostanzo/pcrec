#!/usr/bin/env bash
# S3109 -- R-38 Part D (docs/design/memfn/part_d.md rev 4 section 5.1, plant p4; lane partd).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3109 (its plant_spec; one source of the text).
SAB_ID="S3109-head-rule-reads-run"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2pres"
SAB_DESC='the layout'"'"'s head rule back to run >= 0: a declined run'"'"'s head member reads the run span'"'"'s need (pres_layout_check reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3109, docs/dev/lanes/partd_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3109."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        mf_need need = trun ? (mf_need)s->pspans[head].need : MF_REQUIRED;'
SAB_AFTER='        mf_need need = run >= 0 ? (mf_need)s->pspans[head].need : MF_REQUIRED;   /* SABOTAGE S3109 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
