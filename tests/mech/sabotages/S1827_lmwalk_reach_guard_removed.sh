#!/usr/bin/env bash
# S1827 ([LANDWALK] stage 1, lane p1build; T6) -- THE REACH GUARD REMOVED.
#
# WHAT IT BREAKS. Nothing an answer shows: every hit then runs its own
# anchored verify, which on a subject where each verify reads to the end
# makes the search quadratic (measured at n = 65,536: 5.5 s against 0.00 s).
#
# WHERE IT IS SEEN. tests/codegen/run_landmark_walk.sh §3 (50,000 landmarks
# under a 2 s bound).
SAB_ID='S1827-lmwalk-reach-guard-removed'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='landwalk'
SAB_DESC='the landmark walk never relocates on a landmark the last verify read past, so it runs quadratic'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1827.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_puts(c, "        if (landmark_position < lmwalk_reach) break;\n"'
SAB_AFTER='    pcrec_sb_puts(c, "        if (0 && landmark_position < lmwalk_reach) break;\n"   /* SABOTAGE S1827 */'
