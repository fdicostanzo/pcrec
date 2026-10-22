#!/usr/bin/env bash
# S1105 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §1.6 [rev3 B5],
# §8.3 SN-1 for slot PRES) -- A PRES ROW'S `routed` BIT LEFT 0 AFTER ITS
# ROUTING STEP. P0 (the REQUIRED spans of the route with no DFA scan) is
# unrouted; slot PRES has no pre-table form left, so the kit REFUSES a span no
# routed row decides, and every pre-check on that route fails to compile.
# RE-ANCHORED at B4' (lane b4p, LOCKDOWN): the `routed` bit is deleted, so the
# plant is `fd_row_decides` HOLDING P0 back (intent unchanged).
# Reaches the non-DFA route (P0 holds nowhere else). Detectors: the kit's
# finder check (the routed set at B3b; fd-P0 refused) and the pre-check suite.
SAB_ID="S1105-pres-p0-unrouted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder prechecks"
SAB_DESC="the PRES row P0 is held back from deciding after B3b (fd_row_decides answers 0 for it), so a REQUIRED presence span is decided by no row and the kit refuses every pre-check on the no-DFA route (SN-1 for slot PRES)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            return art->preview && !strcmp(art->preview, r->step);
    return 1;'
SAB_AFTER='            return art->preview && !strcmp(art->preview, r->step);
    return strcmp(r->id, "P0") != 0;   /* SABOTAGE S1105 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row). RE-ANCHORED at B4' (lane b4p): read the current figure from a run."
