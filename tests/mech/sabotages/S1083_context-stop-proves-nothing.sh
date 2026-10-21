#!/usr/bin/env bash
# S1083 (F-B1-3; lane fdb2, [MEMFN] R17-b' B2) -- THE CONTEXT STOP PROVES NOTHING: the
# kit's class of MLINE's FIND (a SET term one byte below the candidate, row
# D1c) leaves `proven_prev` all ones, so G1/R4 on ENG_ATTEMPT lose the
# predecessor byte they read before B2: `(?m)^\n`'s pre-check is no longer
# dominated (a mover).
# Detector (memfnfinder): run_finder.sh's F-B1-3 witness.
# [MEMFN] R-25 (lane memfn-r25, 2026-10-18) RE-ANCHORED: kit_class reads the
# predicate through `p` and only a term the row tests proves (intent unchanged:
# the store of the context stop's set is what is dropped).
# [MEMFN] R-26 Z1 (lane r26z1, 2026-10-21) RE-ANCHORED: kit_class computes the
# per-offset proof proven[] and COPIES proven_prev from proven[-1]; the plant
# writes all ones instead of the copy (proves nothing below the candidate),
# the same intent. Its second detector is run_proof.sh's copy check (family B).
SAB_ID="S1083-context-stop-proves-nothing"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="kit_class writes no proven_prev for a context stop: G1/R4 on ENG_ATTEMPT read no byte"
SAB_DOC_FIGURE="MEASURED 2026-10-17 by lane fdb2land, solo (run_sabotage_matrix.sh S1083) at B2 merged onto the new kit base, after run_finder.sh's summed-count fix: DETECTED, memfnfinder 1fail/901pass (docs/dev/lanes/fdb2land_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    memcpy(out->proven_prev, out->proven[-1 - MF_PROOF_LO], sizeof out->proven_prev);'
SAB_AFTER='    memset(out->proven_prev, 0xFF, sizeof out->proven_prev);   /* SABOTAGE S1083 */'
