# S176 — [DD-14 wave G] THE PREFILTER IS BUILT FOR A LINKED CALL.
#
# S-SR17's TWIN, one wave on. Wave E's row defends "a call-bearing pattern gets
# no prefilter"; wave G NARROWED that to "a pattern with a LINKED call gets no
# prefilter", because a SPLICED call has an exact finite lowering and the
# narrowing is what buys back the 21x-350x design §8.3 measured. This row
# defends the half that survived the narrowing.
#
# WHY IT IS UNSOUND AND NOT MERELY SLOW. Design §8.2's counterexample is one
# line: `a(?1)b` with group 1 = `x` matches "axb", and erasing the call leaves
# `ab`, which does not. ERASURE GIVES A DIFFERENT LANGUAGE, NOT A BIGGER ONE,
# so a prefilter built from it FALSE-NEGATIVES and the hybrid loses matches. A
# recursive callee has no finite inlining at all, so there is nothing to build
# the machine from either way.
#
# THE PRODUCT SIDE ANSWERS WITH A REFUSAL RATHER THAN A LOST MATCH, and that is
# a deliberate choice worth reading: `src/ir/nfa.c`'s `A_CALL` arm inlines a
# SPLICED callee and hard-fails on a LINKED one, so the sabotage below cannot
# quietly emit a filter for the wrong language — it reaches a named internal
# error instead. The alternative (silently emitting the erased machine) is what
# §8.2 says would lose matches, and it is exactly what a version of nfa.c
# written without that arm's `ctx_fail` would do.
SAB_ID="S176-prefilter-for-a-linked-call"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/prefilter.rxt"
SAB_DESC="fit.prefilter stops consulting the call predicate, so a pattern whose calls take the CALL LINKAGE -- a recursive callee, or one the size budget declined -- is handed a capture-erased DFA prefilter. Design 8.2 MEASURED that the erasure is a DIFFERENT language and not a superset ('a(?1)b' with group 1 = x matches axb; the erased 'ab' does not), so the filter would false-negative."
SAB_DOC_FIGURE="PREDICTED: every RECURSIVE call-bearing pattern REFUSES with 'a LINKED subroutine call reached the machine builder; a linked call is VM-only and carries no prefilter' -- nfa.c's arm catching it at compile time rather than emitting a filter for the wrong language. prefilter.rxt, leftrec.rxt, whole.rxt's (?R) cells and mrl.rxt red as compile failures. The SPLICEABLE half of the corpus stays GREEN, which is the pair that separates this row from S-SR17: wave E's version would have taken the whole population red. Canonical figure owed from run_sabotage_matrix.sh S176."
SAB_COUNT=1
SAB_BEFORE='        const bool has_call = pcrec_has_linked_call(root);'
SAB_AFTER='        const bool has_call = false;   /* SABOTAGE S176 */'
