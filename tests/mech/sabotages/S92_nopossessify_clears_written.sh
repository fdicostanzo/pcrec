# S92 — [M6.4.2] `-fno-possessify` CLEARS A USER-WRITTEN POSSESSIVE.
#
# §3.2 RULE 2 IS THAT THE MODULE NEVER WRITES `Ast.possessive`, and this row is
# what that rule buys. That field is possessify's OPTIMISATION mark, deniable
# by `-fno-possessify` and CLEARED by revdet's copy constructor
# (`src/opt/revdet.c:179`). Storing a LANGUAGE FEATURE there would make an
# optimisation flag a MISCOMPILER — a flag whose entire contract is that it
# changes no answer.
#
# THE ROW'S FAILING DIRECTION IS RED ONLY UNDER THE FLAG, and that is why
# tests/atomic_groups/run_atomic_diff.sh has a `-fno-possessify` ARM at all
# (R31 C11): the design's first revision named this row and NOT the arm, and a
# corpus with no flag arm has nowhere for it to be red. The `.rxt` corpus
# cannot carry it either — no `.rxt` block can pass a flag.
SAB_ID="S92-nopossessify-clears-written"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/possessive.rxt"
SAB_DESC="vm_cuts() reads Ast.possessive alone instead of 'possessive OR under an atomic lift', so -fno-possessify -- which denies possessify's REWRITE -- also deletes the cut of a possessive the USER WROTE. The artifact then answers the UNCUT language under a flag whose contract is that it changes no answer: '(?:a|ab)*+c' on \"abc\" gives (0,3) instead of NO MATCH"
SAB_DOC_FIGURE="PREDICTED: RED ONLY under the flag -- atomicdiff's -fno-possessify arm RED with its DEFAULT and --engine=vm arms GREEN, and codegen rule 2 RED. That asymmetry IS the row. Canonical figure owed from run_sabotage_matrix.sh S92."
SAB_COUNT=1
SAB_BEFORE='    return a->u.rep.possessive || under_atomic;'
SAB_AFTER='    (void)under_atomic; return a->u.rep.possessive;   /* SABOTAGE S92 */'
