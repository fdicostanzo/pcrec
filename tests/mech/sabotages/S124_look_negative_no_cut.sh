# S124 ([M6.6.2] wave B+C, design §9.3 S-LA3) — THE NEGATIVE FORM CUTS ON BODY
# SUCCESS, AND THAT CUT IS NOT AN OPTIMISATION.
#
# THE SHAPE (design §3.3). A negative lookaround takes its mark BEFORE pushing
# the "body failed" continuation, so when the body SUCCEEDS — meaning the
# assertion FAILS — the cut discards the body's frames AND that continuation.
#
# WITHOUT IT the failing assertion leaves a LIVE CHOICE POINT. Later, when
# something downstream fails, the resume stack pops back into `L_neg_ok` and
# the whole pattern proceeds AS IF THE NEGATIVE ASSERTION HAD HELD. That is a
# FALSE MATCH, not a missed one, and it is invisible on any subject where
# nothing downstream ever fails — which is most of them.
#
# THE PREDICTION IS TWO-SIDED and that is what makes the row sharp: the
# NEGATIVE cells go red while EVERY POSITIVE CELL STAYS GREEN. A row whose
# whole corpus went red would not distinguish this from S123.
SAB_ID="S124-look-negative-no-cut"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="vm_look's negative arm fails without cutting, so a FAILED negative assertion leaves its body-failed continuation live on the resume stack; a later failure resumes it and the pattern proceeds as if the assertion had held"
SAB_DOC_FIGURE="PREDICTED: the negative cells of lookahead.rxt/captures.rxt/quantified.rxt go red while every positive cell stays green. Canonical figure owed from run_sabotage_matrix.sh S124."
SAB_COUNT=1
SAB_BEFORE='        vm_cut(v, mslot, "cut: the assertion has failed; the body-failed "
                         "continuation must not survive to be resumed later");
        vm_fail(v);'
SAB_AFTER='        /* SABOTAGE S124: the negative form fails without cutting */
        (void)mslot;
        vm_fail(v);'
