#!/usr/bin/env bash
# S3045 -- R-38 K38-2 fix round (review 2026-11-11 r1 k382 F12; lane k382fix). A RUN-TESTING ROW
# DROPS OUT OF THE STRETCH-MODE TABLE (a renamed P3): finder.c fd_run_modes[] no longer lists P3,
# so every P3 run link's stretch is unlisted. The table has no catch-all row: the ask must be
# REFUSED, never handed a default stretch (memory pcrec-no-silent-defaults).
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh): mf_ask refuses every P3 site.
SAB_ID="S3045-run-mode-row-unlisted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="g2pres"
SAB_DESC="P3 renamed out of fd_run_modes[]: every P3 site's presence ask must be refused (G2 reds)"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382fix 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3045 RED (mf_ask (the presence links): refused). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3045."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "P3", KIT_RUN_WINDOW },   /* the OPTIONAL route'"'"'s pick: its window    */'
SAB_AFTER='    { "P3-renamed", KIT_RUN_WINDOW },   /* SABOTAGE S3045 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
