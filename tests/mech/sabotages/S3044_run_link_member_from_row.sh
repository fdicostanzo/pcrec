#!/usr/bin/env bash
# S3044 -- R-38 K38-2 fix round (review 2026-11-11 r1 k382 F13; lane k382fix). THE RUN's LINK
# KEEPS ITS ROW TEMPLATE's `member`: finder.c fd_pres no longer zeroes `member` on the run span,
# so P3's template `member` 1 (the retired window encoding) crosses on every P3 run link, against
# memfn.h mf_link ("0 and UNREAD" on the run span).
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), the generator's link check on the
# reply of every site (`member` is not 0 on the run span).
SAB_ID="S3044-run-link-member-from-row"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="g2pres"
SAB_DESC="the run span's link keeps P3's template member 1: the G2 presence generator's link check must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382fix 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3044 RED (the run's link (mf_ask): member is not 0 on the run span). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3044."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (!member) k.member = 0;'
SAB_AFTER='        (void)0;   /* SABOTAGE S3044 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
