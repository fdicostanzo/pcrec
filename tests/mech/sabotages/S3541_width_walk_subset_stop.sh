#!/usr/bin/env bash
# S3541 (K159, lane k159r81; review r81 CHECK-1, coordinator plant V1) -- the width walk's repeated-frontier test made a SUBSET test: the walk stops (unbounded) as soon as the checkpoint is non-empty, not only when the frontier EQUALS it.
# Detector: run_facts_checks.sh [facts-width-bounded] (`(?:a|bb)c` [2,3], `a{0,30}b` [1,31], `(?:ab){2,5}c` [5,11] go to [x,inf)). NOT [facts-sl1] (its 15 rows held under the plant) and NOT [facts-width-cpu] (an unbounded witness lists [1,inf) either way): [facts-width-bounded] is the only catcher. Same emitted C on most probes: no codegen gate sees it.
SAB_ID='S3541-width-walk-subset-stop'
SAB_FILE='src/facts/kset.c'
SAB_SUITES='facts'
SAB_DESC='pcrec_width_walk stops at any frontier whose checkpoint exists (nck >= 0) instead of one equal to it, so bounded widths with shared states across depths list [lo,inf) (answer-silent in emitted C)'
SAB_DOC_FIGURE='validated by plant at lane k159r81 ([facts-width-bounded] FAILS on 3 of 3 witnesses; [facts-sl1] and [facts-width-cpu] stay green); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3541.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (w.ncur == nck) {'
SAB_AFTER='        if (nck >= 0) {   /* SABOTAGE S3541 */'
