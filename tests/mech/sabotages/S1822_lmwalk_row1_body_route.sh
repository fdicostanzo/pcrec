#!/usr/bin/env bash
# S1822 ([LANDWALK] stage 1, lane p1build; r5 SLOT-4, T1) -- ROW 1
# (`finisher-dfa`) READS THE BODY'S ROUTE instead of the finisher's.
#
# WHAT IT BREAKS. A VM hybrid's prefilter body is a DFA scan over an erased
# (superset) language whose finisher is the VM; row 1 must decline it. The
# plant asks the body's route, which is the DFA on a hybrid too.
#
# RETIRED UNREACHED 2026-10-30 (lane p1mech, manager ruling in
# docs/dev/lanes/p1mech_rulings.md): see SAB_EXPECT_REASON. Table row 1 stays
# as the declared fact; the re-arm tripwire is cand_rows_check.py's
# [cand-ma-dfa-only] (make test-codegen's run_cand_rows.sh). The text below
# is the row's intent as built, kept for the re-aim.
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
SAB_REACH='python3 "$TREE/tests/codegen/cand_rows_check.py" "$TREE"'
SAB_REACH_EXPECT='is now reachable: re-arm S1822'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='row 2 (anchored-A) implies row 1 (finisher-dfa): build_anchored_dfa builds A only where a FINISH row on the finisher route declares CAND_MA, and only verify-at on the DFA route does, so every VM hybrid row 1 would decline is declined by row 2 right after it (measured on the plant: ([a-z]+)@x and (?![a-z]*b)[a-z]+@x read anchored-A, artifacts unchanged). The probe is cand_rows_check.py [cand-ma-dfa-only], whose FAIL line reads NOW REACHED the day a non-DFA FINISH row declares CAND_MA; then re-aim this row at a witness row 1 alone declines (lane p1mech, 2026-10-30)'
SAB_COUNT=1
SAB_BEFORE='static bool lc_finisher(LmSt *st) { return pcrec_cand_finisher_dfa(st->cx); }'
SAB_AFTER='static bool lc_finisher(LmSt *st) { return pcrec_cand_body_route(st->cx) == CAND_ROUTE_DFA; }   /* SABOTAGE S1822 */'
