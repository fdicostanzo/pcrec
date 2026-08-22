# S94 — [M6.4.2] `rd_shape` ACCEPTS AN ATOMIC GROUP INSTEAD OF DECLINING.
#
# §6.5's finding, as a row. An atomic group is NOT reversal-invariant: its cut
# is defined relative to the FORWARD priority order, and "the body's first
# success" is not a property a backwards walk can reproduce. The
# reverse-deterministic rung recovers an iteration boundary by matching the
# REVERSED body from the right, which has its own first success somewhere else.
#
# THE DECLINE IS AT `rd_shape` AND THE OTHER THREE SITES DEPEND ON IT. Accept
# here and `rd_reverse` is reached, whose arm for `A_ATOMIC` ctx_fails LOUDLY
# rather than copying the node — which is itself a designed outcome: without
# that arm, `rd_reverse`'s FALLTHROUGH is `rd_node`, which copies the node and
# NULLs `l` and `r`, producing an EMPTY-BODY ATOMIC GROUP in the reversed body
# the emitter walks. A miscompile produced by a warning nobody turned into an
# error (`-Werror` is `make strict` only, R5-Q1).
#
# So this row's OBSERVED failure is the internal error, and that is the correct
# outcome: the two arms are a pair, and the loud one is what makes removing the
# quiet one survivable.
SAB_ID="S94-rdshape-accepts-atomic"
SAB_FILE="src/opt/revdet.c"
SAB_SUITES="harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_quant.rxt"
SAB_DESC="rd_shape ACCEPTS a body containing an A_ATOMIC instead of declining, so the reverse-deterministic rung is offered a body whose cut a backwards walk cannot reproduce. rd_reverse's own arm then ctx_fails by design -- the pair is deliberate: without the loud arm the fallthrough would build an EMPTY-BODY atomic group in the reversed body and miscompile silently"
SAB_DOC_FIGURE="PREDICTED: the revdet-eligible slice of the atomic corpus RED (an internal error rather than a wrong answer, which is the designed outcome), nothing else moving. Canonical figure owed from run_sabotage_matrix.sh S94."
SAB_COUNT=1
SAB_BEFORE='        case A_ATOMIC:
            S->ok = false;
            return;
        case A_CAP:'
SAB_AFTER='        case A_ATOMIC:
            a = a->l; continue;   /* SABOTAGE S94: accept instead of decline */
        case A_CAP:'
