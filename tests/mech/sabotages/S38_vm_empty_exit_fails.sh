# S38 — [M4.5b] THE EMPTY ITERATION ROLLED BACK INSTEAD OF EXITING.
# engine_m4.md §3.3: an iteration that consumed nothing must not iterate again,
# and "control takes the EXIT CONTINUATION". The mechanism invites the other
# reading — failing the path lets the trail undo the empty iteration's writes
# for free — and it is wrong. This is not a hypothetical: it is the bug this
# emitter actually shipped in its first draft, found by the oracle sweep, and
# the sabotage restores it verbatim.
#
# Measured effect of the real bug: `(a*)*` on "a" reports group 1 = [0,1) (the
# FIRST iteration's value) where both oracles give [1,1); `(|a)+` additionally
# loses the WHOLE MATCH, giving [0,1) against both oracles' [0,0), because
# rolling the empty iteration back lets the loop go round again.
SAB_ID="S38-vm-empty-exit-fails"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vm"
SAB_DESC="an empty iteration FAILS the path instead of taking the loop's exit continuation (its capture writes are rolled back)"
SAB_DOC_FIGURE="tests/vm/run_vm_tests.sh: the oracle sweep fails across the whole nullable-body family"
SAB_COUNT=1
SAB_BEFORE="                  gslot, v->p, cur);
        vm_goto(v, exit);"
SAB_AFTER="                  gslot, v->p, cur);
        vm_fail(v);  /* SABOTAGE S38 */"
