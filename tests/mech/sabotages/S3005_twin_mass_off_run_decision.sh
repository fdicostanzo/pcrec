#!/usr/bin/env bash
# S3005 -- R-38 K38-1 (docs/design/memfn/span_runs_sheet.md rev 1.2 §5's K38-1 row; lane k381).
# THE TWIN'S MASS OFF THE RUN DECISION: the landmark admission's mass term (presence.c kit_pres_picks,
# the FIFTH) multiplies the masses of a stretch of its own, the run's first positions, instead of the
# run decision's verified stretch [ver_lo, ver_lo + ver_len) (kit_run_decide, P3's window).
# Detector: tests/memfn/run_decide_check.c's twin witness W2 (the sheet's SECOND witness: a tied
# stretch over more than 8 positions, `qzeeeeeeeeeq` under its rate table, the decision's window
# [4,12), h 48, K 30000: bit 0; the head [0,8) gives h 18, bit 1), part `rundec` of memfnfinder.
SAB_ID="S3005-twin-mass-off-run-decision"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the twin admission's mass term reads the run's head instead of the run decision's verified stretch"
SAB_DOC_FIGURE="HAND-MEASURED by lane k381 2026-11-10 (docs/dev/lanes/k381_report.md): the row's plant applied by hand to a git archive of the lane's tip, built, tests/memfn/run_decide_check.c: 1fail (twin W2). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3005."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            for (unsigned j = rr.ver_lo; j < rr.ver_lo + rr.ver_len; j++) {'
SAB_AFTER='            for (unsigned j = 0; j < rr.ver_len; j++) {   /* SABOTAGE S3005 */'
