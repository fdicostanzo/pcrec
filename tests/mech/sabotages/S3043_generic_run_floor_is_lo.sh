#!/usr/bin/env bash
# S3043 -- R-38 K38-2 fix round (review 2026-11-11 r1 k382 F1; lane k382fix). THE GENERIC ROW's
# RUN PART STARTS AT `lo`: generic.c's ALL_PRESENT loop starts the run part's candidates at the
# attempt start, not at the run's floor max(0, lo + omin) (kit.h kit_run_floor), so an occurrence
# whose position 0 lies before the attempt start is never a candidate on a site no pre-check row
# admits (on_miss_leaves 0).
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), its GENERIC pass (on_miss_leaves 0,
# every site the generic row's): the uses' PRESENCE rule and the §3.5 witness W-L1.
SAB_ID="S3043-generic-run-floor-is-lo"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="g2pres"
SAB_DESC="the generic row's run part starts at lo, not max(0, lo + omin): the generic pass's PRESENCE and W-L1 must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382fix 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3043 RED (generic.default.oml0 W-L1: the entry from 3 on \"foobar\" yields -1, the stated rule 0). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3043."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            const char *from = s->preds[i].fn_ref ? kit_run_floor(rc->art, rc->LO, s, "generic")
                                                  : rc->LO;'
SAB_AFTER='            const char *from = rc->LO;   /* SABOTAGE S3043 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-GENERIC-FLOOR"
