#!/usr/bin/env bash
# S1824 ([LANDWALK] stage 1, lane p1build; T7) -- ROW 2 (`anchored-A`)
# DROPPED: the walk is admitted without the anchored machine its seed verify
# runs.
#
# WHERE IT IS SEEN. Under `-fno-anchored-dfa` the walk is still selected and
# its emitter refuses (an internal error), so tests/codegen/run_landmark_walk.sh's
# deny cells fail to compile, as does the answer net under the axes sweep.
SAB_ID='S1824-lmwalk-anchored-row-dropped'
SAB_FILE='src/gen/lmwalk.c'
SAB_SUITES='landwalk'
SAB_DESC='the landmark walk is admitted without the anchored machine'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1824.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return st->cx->job->anchored_ok && st->cx->job->adfa.n > 0;'
SAB_AFTER='    return (void)st, true;   /* SABOTAGE S1824 */'
