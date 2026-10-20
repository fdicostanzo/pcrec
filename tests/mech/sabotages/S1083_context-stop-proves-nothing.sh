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
SAB_ID="S1083-context-stop-proves-nothing"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="kit_class writes no proven_prev for a context stop: G1/R4 on ENG_ATTEMPT read no byte"
SAB_DOC_FIGURE="MEASURED 2026-10-17 by lane fdb2land, solo (run_sabotage_matrix.sh S1083) at B2 merged onto the new kit base, after run_finder.sh's summed-count fix: DETECTED, memfnfinder 1fail/901pass (docs/dev/lanes/fdb2land_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        memcpy(out->proven_prev, p->term[0].set, sizeof out->proven_prev);'
SAB_AFTER='        (void)0;   /* SABOTAGE S1083 */'
