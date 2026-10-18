#!/usr/bin/env bash
# S1094 (lane b3a, [MEMFN] R17-b' B3a) -- S980 / PR-7: the set port breaks a mass tie toward the member EARLIER in pattern order; caught by the -e utf8 ba tie witness
SAB_ID="S1094-set-tie-order-swapped"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="S980 / PR-7: the set port breaks a mass tie toward the member EARLIER in pattern order; caught by the -e utf8 ba tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (oa != ob) return oa > ob;'
SAB_AFTER='    if (oa != ob) return oa < ob;   /* SABOTAGE S1094 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, candoracle:5fail/131pass DETECTED at ebfb5a88a)."
