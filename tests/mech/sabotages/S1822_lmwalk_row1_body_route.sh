#!/usr/bin/env bash
# S1822 ([LANDWALK] stage 1, lane p1build; r5 SLOT-4, T1) -- ROW 1
# (`finisher-dfa`) READS THE BODY'S ROUTE instead of the finisher's.
#
# WHAT IT BREAKS. A VM hybrid's prefilter body is a DFA scan over an erased
# (superset) language whose finisher is the VM; row 1 must decline it. The
# plant asks the body's route, which is the DFA on a hybrid too.
#
# WHERE IT IS SEEN. The answer net's T1 cell (`(?![a-z]*b)[a-z]+@x` on "ba@x" is
# (1,4); the admitted erased body answers NOMATCH) and run_landmark_walk.sh's hybrid witness
# `([a-z]+)@x` (expected "unanchored", no walk text), or its compile.
SAB_ID='S1822-lmwalk-row1-body-route'
SAB_FILE='src/gen/lmwalk.c'
SAB_SUITES='harness landwalk'
SAB_DESC='the landmark walk admission row 1 reads the body route, so a VM hybrid prefilter can take the walk'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1822.'
SAB_HARNESS_TARGET='tests/landwalk/landwalk.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "([a-z]+)@x" | grep -F "#define RX_VM_PREFILTER \"hybrid\""'
SAB_REACH_EXPECT='#define RX_VM_PREFILTER "hybrid"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool lc_finisher(LmSt *st) { return pcrec_cand_finisher_dfa(st->cx); }'
SAB_AFTER='static bool lc_finisher(LmSt *st) { return pcrec_cand_body_route(st->cx) == CAND_ROUTE_DFA; }   /* SABOTAGE S1822 */'
