#!/usr/bin/env bash
# S3060 -- R-38 K38-2 (docs/design/memfn/span_runs_sheet.md rev 1.3 §3.3 item 1, §3.5 W-L1;
# lane k382). THE CANDIDATE FLOOR IS THE ORIGIN: the run part's floor (precheck.c run_floor) is
# the use's `lo` even where the run span's omin is negative, not max(0, lo + omin), so an
# occurrence whose position 0 lies before the attempt start is never a candidate.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), the §3.5 witnesses W-L1 (run
# `foobar`, omin -3, origin 3: expected candidate 0) and W-L1b (the scan byte below the origin);
# the oracle step reds too.
SAB_ID="S3060-run-floor-is-attempt-start"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="g2pres"
SAB_DESC="the run part's candidate floor is lo, not max(0, lo + omin): W-L1 and W-L1b must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3060 RED (W-L1b: the entry from 3 on \"foobar\" yields -1, the stated rule 0; oracle violations=8529). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3060."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (omin >= 0) return h->lo;'
SAB_AFTER='    return h->lo;   /* SABOTAGE S3060 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-NEG-FLOOR"
