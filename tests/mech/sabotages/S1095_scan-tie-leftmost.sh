#!/usr/bin/env bash
# S1095 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness
# span_pick unit 1c (lane sp1c) RE-ANCHORED: P3's run scan ASKS the run member (window.c
# kit_run_member, U2), so its tie rule lives there; the same mutant (a tie to the LOWER, leftmost
# position, the comparison's operands swapped) is planted on that one spelling, which window.c's
# run_member and translate's ranking also read.
# span_pick unit 1d (lane sp1d) RE-ANCHORED: kit_run_member's pick asks the one before-relation
# kit_pick_takes; the same mutant (a tie to the leftmost position: a strict compare, the first
# met keeps it) replaces that call on the run member's own pick line.
# R-38 K38-1 (lane k381; span_runs_sheet.md rev 1.2 §5's K38-1 row) RE-AIMED onto THE RUN DECISION's
# tie: presence.c kit_run_decide asks kit_run_member with its tie row, so the plant hands it a LOWER
# row (T_MASS_SET's: the leftmost) on that one call. It moves EVERY reader of the decision together
# and no other (the verify-NO prefilter member asks kit_run_member with its own row): counted per
# reader by tests/memfn/run_decide_check.c (memfnfinder), 8 red lines over 5 readers: scan (W1 abcd
# under NONE, W2), the window family's verify-YES member (W1, W2), translate's ranking (W1, W2: no
# ranking left, C-pin's stop, A-mass's T_MASS_STRETCH, no longer the member), P3's window and the
# twin's mass term (W2, the tied stretch over 12 positions; tie-blind on W1's four). pcrec observes it
# as req_run_member's agreement check (the -e utf8 abcd witness: "the window family's run member 0 is
# not the run window's own index 3", every arm with a run part), which stops the compile before
# pres_layout_check's run half.
SAB_ID="S1095-scan-tie-leftmost"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle memfnfinder"
SAB_DESC="SN-6: the run decision drops its tie rule (a tie goes to the leftmost position); every reader moves; caught by the -e utf8 abcd tie witness and the run decision's per-reader check"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_member sc = kit_run_member(rate, at, src, n, 0, after ? &prev : NULL, T_MASS_STRETCH);'
SAB_AFTER='    kit_member sc = kit_run_member(rate, at, src, n, 0, after ? &prev : NULL, T_MASS_SET);   /* SABOTAGE S1095 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane k381 (re-aim onto kit_run_decide's tie; docs/dev/lanes/k381_report.md): the row's plant applied to a git archive of the lane's tip, built with nice make -j2: tests/memfn/run_decide_check.c 8fail/3pass (scan W1 W2, member W1 W2, rank W1 W2, window W2, twin W2); the witness -e utf8 abcd is refused by req_run_member (also under --memfn=no-window-search and --engine=vm). The candoracle and memfnfinder figures are the gate's mech shard's. Earlier: HAND-MEASURED by lane sp1d (re-anchor on kit_pick_takes; docs/dev/lanes/sp1d_report.md): the row's plant applied by tests/mech/lib/replace.py to a git archive of 9eb7d7837, built, tests/codegen/run_cand_oracle.sh: candoracle:31fail/151pass DETECTED (clean 0fail/182pass). Earlier: lane sp1c (re-anchor; docs/dev/lanes/sp1c_report.md): the row's plant applied by tests/mech/lib/replace.py to a git archive of 439c263c8, built, tests/codegen/run_cand_oracle.sh: candoracle:28fail/150pass DETECTED (clean 0fail/178pass). Earlier: lane b3afix, candoracle:6fail/129pass at ebfb5a88a."
