#!/usr/bin/env bash
# S1095 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness
# span_pick unit 1c (lane sp1c) RE-ANCHORED: P3's run scan ASKS the run member (window.c
# kit_run_member, U2), so its tie rule lives there; the same mutant (a tie to the LOWER, leftmost
# position, the comparison's operands swapped) is planted on that one spelling, which window.c's
# run_member and translate's ranking also read.
SAB_ID="S1095-scan-tie-leftmost"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            (ms == b.mass && kit_tie_takes(T_MASS_STRETCH, (int32_t)j, b.pos))) {'
SAB_AFTER='            (ms == b.mass && kit_tie_takes(T_MASS_STRETCH, b.pos, (int32_t)j))) {   /* SABOTAGE S1095 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, candoracle:6fail/129pass DETECTED at ebfb5a88a)."
