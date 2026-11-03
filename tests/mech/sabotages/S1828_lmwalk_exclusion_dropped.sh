#!/usr/bin/env bash
# S1828 ([LANDWALK] stage 1, lane p1build) -- ROW 7 (`exclusion`) DROPPED.
#
# WHAT IT BREAKS. The walk's soundness: a prefix that can consume a byte of
# the landmark lets a match's landmark be a LATER occurrence than the first
# one after its start, and the walk back from an earlier hit can pass other
# hits (no longer linear).
#
# WHERE IT IS SEEN. tests/codegen/run_landmark_walk.sh's `a.*b@c` (expected
# "unanchored", row exclusion).
SAB_ID='S1828-lmwalk-exclusion-dropped'
SAB_FILE='src/gen/lmwalk.c'
SAB_SUITES='landwalk'
SAB_DESC='the landmark walk is admitted where the prefix can consume a landmark byte'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1828.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (st->alpha[k] & st->set[k]) return false;'
SAB_AFTER='        if (0 && (st->alpha[k] & st->set[k])) return false;   /* SABOTAGE S1828 */'
