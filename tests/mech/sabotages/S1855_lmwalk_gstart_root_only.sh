#!/usr/bin/env bash
# S1855 ([LANDWALK] stage 1, lane p1kind) -- ROW 5 (`g1`) ASKS ONLY THE ROOT.
#
# WHAT IT BREAKS. g1's \G and \K reads must find the node ANYWHERE in R; the
# plant asks the root node alone (the walker descends into nothing), the
# limit of the old hand-written switch whose `default:` stopped at every kind
# it did not list.
#
# WHERE IT IS SEEN. tests/codegen/run_landmark_walk.sh's five g1/gstart
# witnesses (`[a-z]+@x(?:\G){0}` and its siblings: a \G nested in a {0} body,
# a DEFINE's named group, an alternation in a repeat) read "landmark-walk"
# where "unanchored" is expected. No answer moves: a \G only reaches the walk
# dead, so landwalk.rxt's matching cells stay green (lane p1kind's report).
SAB_ID='S1855-lmwalk-gstart-root-only'
SAB_FILE='src/gen/lmwalk.c'
SAB_SUITES='landwalk'
SAB_DESC='the landmark walk reads \G and \K at the root node only, missing nested ones'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1855.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_ast_visit(a, lm_kind_seen, &q);'
SAB_AFTER='    lm_kind_seen(&q, a);   /* SABOTAGE S1855 */'
