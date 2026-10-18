#!/usr/bin/env bash
# S1105 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §1.6 [rev3 B5],
# §8.3 SN-1 for slot PRES) -- A PRES ROW'S `routed` BIT LEFT 0 AFTER ITS
# ROUTING STEP. P0 (the REQUIRED spans of the route with no DFA scan) is
# unrouted; slot PRES has no pre-table form left, so the kit REFUSES a span no
# routed row decides, and every pre-check on that route fails to compile.
# Reaches the non-DFA route (P0 holds nowhere else). Detectors: the kit's
# finder check (the routed set at B3b; fd-P0 refused) and the pre-check suite.
SAB_ID="S1105-pres-p0-unrouted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder prechecks"
SAB_DESC="the PRES row P0's routed bit is left 0 after B3b, so a REQUIRED presence span is decided by no routed row and the kit refuses every pre-check on the no-DFA route (SN-1 for slot PRES)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, 1, NULL, FB_DERIVED, "B3b",'
SAB_AFTER='      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, 0 /* SABOTAGE S1105 */, NULL, FB_DERIVED, "B3b",'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row)."
