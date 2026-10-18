#!/usr/bin/env bash
# S1104 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §8.2 KW-10's
# presence family, "absent-at-end discovery") -- THE LAST PRESENCE SPAN OF THE
# CHAIN IS NEVER TESTED. The pre-check composite's set rest (the REST links,
# K65's every remaining member, tested after the run in one loop: memfn/src/
# precheck.c `set_rest`) stops one member short, so a span absent from the
# subject at the END of the chain is never discovered: on the route with no
# DFA scan a subject lacking only that member gives up on the step budget
# where the answer is NOMATCH. K65's byte witness has a one-member rest (`@`),
# so the plant drops it there. Detector: the harness on K65's file.
SAB_ID="S1104-pres-rest-last-untested"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/base/k65_precheck_whole_set.rxt"
SAB_DESC="the pre-check's set-rest loop stops before its last member, so a REQUIRED span absent at the end of the chain is never discovered and NOMATCH turns into a step give-up on the no-DFA route (KW-10, absent-at-end)"
SAB_REACH='"$PCREC" --features all -e byte -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+Z.@\\1" && grep -q "rq_i < sizeof rq_set; rq_i++" "$REACH_TMP/o.c" && echo REACH-REST-LOOP'
SAB_REACH_EXPECT="REACH-REST-LOOP"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "%s    for (size_t rq_i = 0; rq_i < sizeof rq_set; rq_i++)\n"'
SAB_AFTER='        "%s    for (size_t rq_i = 0; rq_i + 1 < sizeof rq_set; rq_i++)\n"   /* SABOTAGE S1104 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
