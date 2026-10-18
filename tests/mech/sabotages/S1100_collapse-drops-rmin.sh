#!/usr/bin/env bash
# S1100 (lane b3a, [MEMFN] R17-b' B3a) -- PR-11: the count-collapse drops rmin (X{m,n} to X{0,}): a collapsed hybrid front stops enforcing the bytes inside the repeat; no answer moves (the pre-check still runs), caught by run_pr11.sh
SAB_ID="S1100-collapse-drops-rmin"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="memfnfinder"
SAB_DESC="PR-11: the count-collapse drops rmin (X{m,n} to X{0,}): a collapsed hybrid front stops enforcing the bytes inside the repeat; no answer moves (the pre-check still runs), caught by run_pr11.sh"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            rmin = rmin ? 1 : 0;'
SAB_AFTER='            rmin = 0;   /* SABOTAGE S1100 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, memfnfinder:3fail/950pass DETECTED at ebfb5a88a)."
