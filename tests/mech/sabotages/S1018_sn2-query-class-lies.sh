#!/usr/bin/env bash
# S1018 (SN-2; [MEMFN] R17-b' B1, lane fdb1; r17b_prime.md §8.3 [rev3 A4], §4.5
# rule 2) -- THE DEFINE-TIME QUERY'S CLASS DIFFERS FROM THE DEFINE'S.
#
# WHAT IT BREAKS. `mf_ask` must answer the class of the text `mf_define` WOULD
# render for the same site, hooks and art state: pcrec's readers (G1, R4, L4)
# switch to it at B2 on that promise. The plant flips one bit of the query's
# `proven0` (memfn/src/compose.c `ask_sel`, the query's own path), so the
# query reports a byte set the rendered form does not prove.
#
# WHERE IT IS SEEN. The query family (tests/memfn/finder_check.py G, arm
# memfnfinder): every fixture asked then defined compares the two classes and
# an independent reading of the site (ASK!=DEFINE / PROVEN0); the traced
# driver's define-time re-ask refuses (§4.5 rule 2's trace-build half).
SAB_ID="S1018-sn2-query-class-lies"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the define-time query reports a proven0 byte set the rendered form does not prove (its class differs from the define's)"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb1: see docs/dev/lanes/fdb1_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_class(row, s, out);
    return 0;'
SAB_AFTER='    kit_class(row, s, out);
    out->proven0[0] ^= 1u;   /* SABOTAGE S1018 */
    return 0;'
