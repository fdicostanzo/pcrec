#!/usr/bin/env bash
# S3094 ([MEMFN] plan_frame.md 3.0b, row (AC); lane b30b) -- FRAMED ASK ALLOCATES IN ART.
#
# WHAT IT BREAKS AND WHO CATCHES IT: a framed ask's plan function allocates in the art's arena instead of the heap: the counting arena grows on an ask (its populations: a framed E-find ask picking PAIR, a refused framed ask reaching why_room, each counted).
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3094-framed-ask-allocates-in-art"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='a framed ask'"'"'s plan function allocates in the art'"'"'s arena instead of the heap: the counting arena grows on an ask (its populations: a framed E-find ask picking PAIR, a refused framed ask reaching why_room, each counted)'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 194 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3094.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        !wf_plan_site(art, &heap, site, def, gphases, 1, d, w, L, fx, &r, &why)) {'
SAB_AFTER='        !wf_plan_site(art, art->a, site, def, gphases, 1, d, w, L, fx, &r, &why)) {   /* SABOTAGE S3094 */'
