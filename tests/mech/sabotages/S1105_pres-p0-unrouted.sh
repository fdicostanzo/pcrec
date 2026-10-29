#!/usr/bin/env bash
# S1105 (lane b3b, [MEMFN] R17-b' B3b; r17b_prime.md rev 3 §1.6 [rev3 B5],
# §8.3 SN-1 for slot PRES) -- A PRES ROW'S `routed` BIT LEFT 0 AFTER ITS
# ROUTING STEP. P0 (the REQUIRED spans of the route with no DFA scan) is
# unrouted; slot PRES has no pre-table form left, so the kit REFUSES a span no
# routed row decides, and every pre-check on that route fails to compile.
# RE-ANCHORED at B4' (lane b4p, LOCKDOWN): the `routed` bit is deleted, so the
# plant is `fd_row_decides` HOLDING P0 back (intent unchanged).
# RE-ANCHORED at D172 S3 (lane s3): fd_row_decides retired with RPT and the
# R-26.6 preview; the plant is fd_pres declining a P0 decision (intent unchanged).
# Reaches the non-DFA route (P0 holds nowhere else). Detectors: the kit's
# finder check (the routed set at B3b; fd-P0 refused) and the pre-check suite.
SAB_ID="S1105-pres-p0-unrouted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder prechecks"
SAB_DESC="the PRES row P0 is held back from deciding after B3b (fd_pres declines its decision), so a REQUIRED presence span is decided by no row and the kit refuses every pre-check on the no-DFA route (SN-1 for slot PRES)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (d.terminal >= FD_NROWS) {'
SAB_AFTER='        if (d.terminal >= FD_NROWS || !strcmp(fd_rows[d.terminal].id, "P0")) {   /* SABOTAGE S1105 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3b: see docs/dev/lanes/b3b_report.md (the solo mech run of this row). RE-ANCHORED at B4' (lane b4p): read the current figure from a run."
