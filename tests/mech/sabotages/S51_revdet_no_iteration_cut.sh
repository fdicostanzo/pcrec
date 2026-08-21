# S51 - [ENG-BREP rung-select] THE PER-ITERATION CUT REMOVED from the forward
# scan.
#
# The scan discards the body's own choice points at every iteration BOUNDARY,
# and that cut is what makes the resume stack O(1) in the iteration count
# instead of O(subject_length) - the property that lets `((a)|b){0,4000}c` exist at all. It
# is licensed by forward unique-iteration: once the body has matched [p,q) there
# is no other way to match an iteration there, so the frames it leaves behind
# are provably dead.
#
# Removing it does NOT produce a wrong answer on a short subject, and that is
# exactly why this needs a failing-direction control rather than trust: the
# leftover frames are dead by the verdict, so re-entering one cannot change the
# result. What it produces is frame EXHAUSTION at a subject length the artifact
# no longer declares - caught by the differential's FAILURE-SURFACE comparison
# (the third item of eng_brep_design.md 5.1, the one a weaker check would drop)
# against the ground-truth build, whose stamped capacity did not move.
#
# The cut at the LAZY extension's own site is deliberately left alone:
# sabotaging both would not say which one carries the cost.
SAB_ID="S51-revdet-no-iteration-cut"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="rungdiff"
SAB_DESC="the revdet scan per-iteration cut removed: the loop frames accumulate per iteration again, so the artifact exhausts its stack below the length it stamps"
SAB_DOC_FIGURE="tests/rungselect/run_rungdiff.sh: the failure surfaces part"
SAB_COUNT=1
SAB_BEFORE='    sb_printf(b, "    run->resume_depth = %s_frame_mark;\n", rv);
    vm_ev(v, VE_NOTE, 0, 0, "cut to the iteration'
SAB_AFTER='    sb_printf(b, "    (void)%s_mk;\n", rv);  /* SABOTAGE S51 */
    vm_ev(v, VE_NOTE, 0, 0, "cut to the iteration'
