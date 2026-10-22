#!/usr/bin/env bash
# S922 ([MEMFN] R17-b' B2, lane fdb2; r17b_prime.md §8.3 [rev3 D6], §1.6) --
# A FINDER ROW DECIDING BEFORE ITS STEP.
#
# RE-AIMED at B4' (lane b4p, LOCKDOWN): the `routed` bit this row planted
# (R7 carrying routed 1 at B2) is deleted with R7 and with the bit; the intent
# (a row decides before its step) survives in the one gate that remains, the
# preview hold of fd_row_decides. The plant makes the REPORT row (RPT, held
# for the R-26.6 preview) decide on EVERY art, as run_proof.sh's ZK6 does.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c): a REPORT site on
# a plain art is no longer refused as unrouted.
SAB_ID="S922-fd-row-routed-early"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the finder REPORT row (held for its preview step) decides on every art: a row decides before its step"
SAB_DOC_FIGURE="MEASURED 2026-10-17 by lane fdb2land (R7 routed early form): DETECTED. RE-AIMED at B4' (lane b4p): read the current figure from a run."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            return art->preview && !strcmp(art->preview, r->step);'
SAB_AFTER='            return 1;   /* SABOTAGE S922 */'
