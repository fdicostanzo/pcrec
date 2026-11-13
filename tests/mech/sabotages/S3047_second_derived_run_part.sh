#!/usr/bin/env bash
# S3047 -- R-38 K38-2 fix round (review 2026-11-11 r1 k382 F14 (iii); lane k382fix). "ONE RUN, ONE
# PART" DELETED: window.c wf_parts_check counts the derived run parts but never refuses a second.
# A later layout rule still refuses such a site, but by another rule's text.
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh), the generator's control (iii):
# every tested site laid out with two derived parts must be refused BY THIS RULE.
SAB_ID="S3047-second-derived-run-part"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2pres"
SAB_DESC="wf_parts_check's second-derived-part refusal deleted: G2's control (iii) must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382fix 2026-11-11: memfn/tests/run_g2_pres.sh --plant S3047 RED (F14 (iii): a second derived run part, refused by another rule). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3047."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (++nderived > 1) return "a second derived run part (one run, one part)";'
SAB_AFTER='            ++nderived;   /* SABOTAGE S3047 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
