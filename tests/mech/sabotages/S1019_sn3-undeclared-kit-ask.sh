#!/usr/bin/env bash
# S1019 (SN-3; [MEMFN] R17-b' B1, lane fdb1; r17b_prime.md §8.3 [rev3 D4], §4.5
# rules 4-5) -- G1'S KIT ASK LEFT UNDECLARED IN THE SELECTION DAG.
#
# WHAT IT BREAKS. A predicate that asks the kit about a site (mf_ask) READS the
# selection that describes the site, so the ask must be a declared edge of
# the slot graph (`CandNode.kask`, inside `reads`): that is what keeps the
# `table-read-cycle` walk seeing every ask, so no cycle can close through the
# kit. The plant drops PRESENCE's declared ask of NEXT's site
# (src/gen/emit_dfa.c `cand_nodes`), while G1's reader shadow still asks.
#
# WHERE IT IS SEEN. The trace build's ask trap (`cand_ask_check`) aborts with
# `CANDORACLE undeclared-ask PRESENCE NEXT` at G1's first ask, on every
# witness whose admission evaluates `dominated`: tests/codegen/
# run_cand_oracle.sh (arm candoracle) compiles them with -DPCREC_CAND_TRACE.
SAB_ID="S1019-sn3-undeclared-kit-ask"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candoracle"
SAB_DESC="PRESENCE's ask of the kit about NEXT's site is not declared in the slot graph while G1's reader shadow still makes it"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb1: see docs/dev/lanes/fdb1_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                             /* [MEMFN] R17-b'"'"' B1 G1 asks the kit about the
                              * start-search site NEXT'"'"'s row describes */
                             .kask = { [CAND_SLOT_NEXT] = CAND_ON(CAND_ROUTE_DFA) |
                                                          CAND_ON(CAND_ROUTE_ATTEMPT) },'
SAB_AFTER='                             /* [MEMFN] R17-b'"'"' B1 G1 asks the kit about the
                              * start-search site NEXT'"'"'s row describes */
                             .kask = { 0 },   /* SABOTAGE S1019 */'
