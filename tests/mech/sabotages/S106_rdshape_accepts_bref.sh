# S106 (design row S-BR4) — `rd_shape` GAINS AN ARM ACCEPTING `A_BREF`.
#
# THE ALARM SAYS AN ARM IS MISSING, NEVER WHICH ARM IS RIGHT, and that is the
# whole reason this is a row. Adding an `AKind` makes `rd_shape`'s switch raise
# `-Wswitch` under `make strict`; the author then has to choose, and ACCEPT is
# the plausible wrong choice.
#
# WHY IT MUST DECLINE. The reverse-deterministic rung recovers an iteration
# boundary by matching the REVERSED body from the right. A backreference's
# operand is not in its text — it is subject bytes a capture published — and
# there is no reversed spelling of "compare against what group k captured".
# `rd_reverse` runs only on a body this scan approved and its fallthrough
# COPIES, so an accepting arm here produces a reversed body that compares the
# same span while the walk runs the other way.
#
# Declining is always available and always safe (this file's own invariant),
# so the sabotage costs nothing to revert and everything to keep.
SAB_ID="S106-rdshape-accepts-bref"
SAB_FILE="src/opt/revdet.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/nested.rxt"
SAB_DESC="rd_shape ACCEPTS a backreference in a quantifier body instead of declining, so the reverse-deterministic rung is offered a body whose reversal has no meaning. rd_reverse then raises its internal-error wall -- or, with that wall also gone, silently emits a backward walk comparing a span the forward walk published"
SAB_DOC_FIGURE="PREDICTED: brefdiff RED and/or a hard internal error on a nested.rxt pattern. Canonical figure owed from run_sabotage_matrix.sh S106."
SAB_COUNT=1
SAB_BEFORE='        case A_BREF:
            S->ok = false;
            return;'
SAB_AFTER='        case A_BREF:
            return;   /* SABOTAGE S106: ACCEPT it */'
