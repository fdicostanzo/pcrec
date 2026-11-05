#!/usr/bin/env bash
# S1095 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness
# span_pick unit 1c (lane sp1c) RE-ANCHORED: P3's run scan ASKS the run member (window.c
# kit_run_member, U2), so its tie rule lives there; the same mutant (a tie to the LOWER, leftmost
# position, the comparison's operands swapped) is planted on that one spelling, which window.c's
# run_member and translate's ranking also read.
# span_pick unit 1d (lane sp1d) RE-ANCHORED: kit_run_member's pick asks the one before-relation
# kit_pick_takes; the same mutant (a tie to the leftmost position: a strict compare, the first
# met keeps it) replaces that call on the run member's own pick line.
SAB_ID="S1095-scan-tie-leftmost"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (kit_pick_takes(&b, c.v, T_MASS_STRETCH, (int32_t)j)) b = c;'
SAB_AFTER='        if (b.pos < 0 || c.v < b.v) b = c;   /* SABOTAGE S1095 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane sp1d (re-anchor on kit_pick_takes; docs/dev/lanes/sp1d_report.md): the row's plant applied by tests/mech/lib/replace.py to a git archive of 9eb7d7837, built, tests/codegen/run_cand_oracle.sh: candoracle:31fail/151pass DETECTED (clean 0fail/182pass). Earlier: lane sp1c (re-anchor; docs/dev/lanes/sp1c_report.md): the row's plant applied by tests/mech/lib/replace.py to a git archive of 439c263c8, built, tests/codegen/run_cand_oracle.sh: candoracle:28fail/150pass DETECTED (clean 0fail/178pass). Earlier: lane b3afix, candoracle:6fail/129pass at ebfb5a88a."
