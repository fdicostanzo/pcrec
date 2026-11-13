#!/usr/bin/env bash
# S3046 -- R-38 K38-2 fix round (review 2026-11-11 r1 k382 F14 (ii); lane k382fix). THE STATEMENT
# RULE's "a tested link lays out its run part" REFUSAL DELETED: compose.c pres_layout_check no
# longer refuses a layout that drops the derived run part where the run's link is tested. A later
# layout rule still refuses such a site, but by another rule's text.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), the generator's control (ii): every
# tested site laid out with no run part must be refused BY THIS RULE (its error names it).
SAB_ID="S3046-tested-link-without-run-part"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2pres"
SAB_DESC="pres_layout_check's run-part slot refusal deleted: G2's control (ii) must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382fix 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3046 RED (F14 (ii): no run part on a tested link, refused by another rule). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3046."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (k >= s->npred || !s->preds[k].fn_ref)
            return "its run part'
SAB_AFTER='        if (0 && (k >= s->npred || !s->preds[k].fn_ref))   /* SABOTAGE S3046 */
            return "its run part'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
