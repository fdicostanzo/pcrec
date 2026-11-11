#!/usr/bin/env bash
# S3007 -- R-38 K38-2a (docs/design/memfn/span_runs_sheet.md rev 1.3 §5's K38-2a row, plant A;
# §2.4 C2; lane k382a). THE RUN PART DROPS ONE COMPARE OF ITS EXTENT: the run compare's words
# form (runcmp.c rc_emit_words) never compares the run's position 0 (its mask byte and its
# value byte both 0x00, as a proven position's are), so a candidate whose position 0 does not
# hold is yielded while the reply still says the stretch is verified.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), C2's text classifier: EXTENT,
# an occurrence broken at a position inside the reply's stretch must not be yielded.
SAB_ID="S3007-run-part-drops-one-compare"
SAB_FILE="memfn/src/runcmp.c"
SAB_SUITES="g2pres"
SAB_DESC="the run compare's words form drops position 0 of the verified stretch: C2's classifier (EXTENT) must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382a 2026-11-10 (docs/dev/lanes/k382a_report.md): memfn/tests/run_g2_pres.sh --plant S3007 RED (EXTENT). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3007."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            int skip = proven && (at + i < done || rc_proven(proven, np, at + i));'
SAB_AFTER='            int skip = at + i == 0 || (proven && (at + i < done || rc_proven(proven, np, at + i)));   /* SABOTAGE S3007 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-WORDS-COMPARE"
