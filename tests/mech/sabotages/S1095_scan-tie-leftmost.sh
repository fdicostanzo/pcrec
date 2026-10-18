#!/usr/bin/env bash
# S1095 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness
SAB_ID="S1095-scan-tie-leftmost"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (scan < 0 || c < sm) { scan = (int)i; sm = c; }'
SAB_AFTER='            if (scan < 0 || c <= sm) { scan = (int)i; sm = c; }   /* SABOTAGE S1095 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, candoracle:6fail/129pass DETECTED at ebfb5a88a)."
