# S90 — [M6.4.2] THE CUT MARK IS RECORDED AFTER THE BODY'S FIRST PUSH.
#
# CUT-INV CLAUSE 2, as a row. The invariant is: every frame with index below
# the mark was pushed BEFORE the body's first trail entry, so unwinding to any
# of them still rewinds everything the body wrote. That holds because the
# mark's `RX_SET` precedes every `RX_PUSH` the body emits — which is a property
# of the EMISSION ORDER in `vm_atomic` and of nothing else.
#
# Move the mark after the body's first push and the cut truncates to a depth
# that ALREADY INCLUDES some of the body's own frames, so those frames survive
# a cut that was supposed to discard them and the group can be re-entered with
# a different answer. That is the uncut language, arrived at from the other
# direction.
#
# THE SECOND CLAUSE THE DESIGN FIRST PROPOSED FOR THIS ROW'S CHECK IS DELETED
# (R31 C15): it asserted that every `RX_CUT(k)` is "textually reachable only
# from labels after it", and this VM dispatches by COMPUTED GOTO, where textual
# position carries no reachability. `[M6.4-ATOMIC rule 3]` keeps the
# mark-before-push clause, which is the one that is both true and checkable.
SAB_ID="S90-mark-after-push"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_basic.rxt"
SAB_DESC="vm_atomic emits the cut mark's RX_SET AFTER the body rather than before it, so the recorded resume depth already includes the body's own frames and the cut discards none of them. CUT-INV clause 2's failing direction: '(?>a|ab)c' on \"abc\" then matches (0,3) where PCRE2 gives NO MATCH, because the group can be re-entered with its second branch"
SAB_DOC_FIGURE="PREDICTED: codegen rule 3 RED (the mark's line number is no longer below the first RX_PUSH's), and the alternation-priority corpus RED. Canonical figure owed from run_sabotage_matrix.sh S90."
SAB_COUNT=1
SAB_BEFORE='    vm_set(v, mslot, "(ptrdiff_t)run->resume_depth",
           "atomic-group cut mark (resume-stack depth at group entry)");
    vm_goto(v, bodyl);

    /* The body'"'"'s follow-min is the GROUP'"'"'s own: the group consumes exactly
     * what the body consumes, so there is nothing to add. `vm_emit` inherits
     * `v->fmin` unchanged, which is A_CAP'"'"'s arm'"'"'s own reading. */
    vm_emit(v, bodyl, a->l, cutl);'
SAB_AFTER='    vm_goto(v, bodyl);   /* SABOTAGE S90: mark moved BELOW the body */
    vm_emit(v, bodyl, a->l, cutl);
    vm_set(v, mslot, "(ptrdiff_t)run->resume_depth",
           "atomic-group cut mark (SABOTAGED: recorded after the body)");'
