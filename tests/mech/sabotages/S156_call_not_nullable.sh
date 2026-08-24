# S156 ([DD-14] wave B+C, design SS9.3 S-SR9) -- `vm_nullable` ANSWERS TRUE FOR
# A NULLABLE CALLEE.
#
# THE CLAIM (design SS2.6, MEASURED on 10.46): a call is a REPEATABLE ITEM, and
# a quantifier over one terminates because something bounds the empty
# iteration.
#
#     (?(DEFINE)(?<g>a?))(?&g)*   on "aaa"  -> (0,3)   a NULLABLE callee
#     (?(DEFINE)(?<g>))(?&g)*     on ""     -> (0,0)   an EMPTY callee
#     ^(a?)(?1)*$                 on "aaa"  -> (0,3)
#
# So `vm_nullable` needs an `A_CALL` arm whose answer is "nullable iff the
# CALLEE's body is" -- a FIXPOINT over the call graph with cycle bottom
# `false` iterated up, and for `(?R)` the question "is the whole pattern
# nullable".
#
# THE FIELD'S POLARITY IS WHAT THIS ROW SABOTAGES PAST. `u.call.nonnullable`
# is stored INVERTED so the arena's zero reads NULLABLE -- the direction that
# EMITS the guard, which costs a slot and a test on a call that never needed
# one and can never lose a match. `false` here is the other direction, and it
# is the one that hangs: the guard is denied to a quantifier above a nullable
# callee.
#
# ITS SIGNAL IS AN ERROR AND NOT A MISMATCH, which is why the detector has to
# be read carefully. Without the guard the loop re-enters at zero consumption
# and the STEP BUDGET is what ends the search -- `PCREC_ERR_STEPS`, scored
# through SS10.3's `gu` directive or as a harness failure, never as a wrong
# span. A row read as "the answer changed" would be looking for the wrong
# thing.
#
# AND IT IS NOT S157's ROW. SS2.6 has a SECOND ruling riding on this arm --
# `vm_poss_star` emits NO empty-iteration guard and NO work charge at all, so a
# nullable callee routed onto the POSSESSIVE rung loops forever whatever this
# arm answers. What keeps that unreachable is the RUNG DECLINE in
# `src/opt/possessify.c`, which is S157, and the two are separate rows because
# they defend different lines against different failures (a budget give-up
# here, a HANG there).
SAB_ID="S156-call-not-nullable"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/quantified.rxt"
SAB_DESC="vm_nullable's A_CALL arm answers FALSE unconditionally, so a quantifier over a NULLABLE callee loses its empty-iteration guard and the loop re-enters at zero width until the step budget ends the search"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR9): on the nullable-callee-under-* cells the lost guard makes the loop re-enter at zero width and the STEP BUDGET ends it -- PCREC_ERR_STEPS, an ERROR rather than a wrong span, so the detector must notice a failure and not a mismatch. The row must be compiled onto the BACKTRACKING rung, which 2.6's own ruling guarantees (S157 is the row for the rung decline itself)."
SAB_COUNT=1
SAB_BEFORE='        case A_CALL: return !a->u.call.nonnullable;'
SAB_AFTER='        case A_CALL: return false;   /* SABOTAGE S156 */'
