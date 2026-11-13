#!/usr/bin/env bash
# S3063 -- R-38 K38-2 (docs/design/memfn/span_runs_sheet.md rev 1.3 §3.2, §3.5 W-K3; lane k382).
# THE TWIN READS K UNSIGNED: the landmark port's admission (presence.c kit_pres_picks) reads
# head_max as unsigned, so a negative K is a huge step back and the bit drops to 0, where the
# stated rule admits by max(K, 0).
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), W-K3 in the generator: on every
# site whose bit at K 0 is 1, the bit at K -1..-32 must equal it.
SAB_ID="S3063-twin-reads-k-unsigned"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="g2pres"
SAB_DESC="the twin admission reads K unsigned: W-K3 (bit at K < 0 equals bit at K 0) must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3063 RED (W-K3: the admission bit at K -1 is 0, at K 0 it is 1). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3063."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        unsigned long long k = s->head_max > 0 ? (unsigned long long)s->head_max : 0;'
SAB_AFTER='        unsigned long long k = (unsigned long long)s->head_max;   /* SABOTAGE S3063 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-TWIN-NEG-K"
