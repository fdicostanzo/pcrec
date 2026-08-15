# S36 — [M4.5b] THE NEUTERED UNDO. engine_m4.md §3.2's second bullet is that
# capture undo is EXACT RESTORE of the previous value, never a clear, and that
# the naive version is wrong in BOTH directions: `(a)*` on "aa" must report the
# SECOND `a` (a later iteration overwrites and the overwrite must stand), while
# `(a)b|(a)c` on "ac" must return group 1 to unset before branch 2 runs — and
# `((a)|b)+` on "ab" must restore group 2 to the value the SUCCESSFUL earlier
# iteration left, not to unset. Only a per-write old-value trail gets all
# three.
#
# The sabotage removes the rewind at the fail label, so a backtrack restores
# `pos` but leaves every capture write standing. Nothing about the emitted
# code's SHAPE changes — the trail is still built, the frames still carry their
# marks — so no structural check can see it; only spans can.
SAB_ID="S36-vm-undo-neutered"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vm"
SAB_DESC="the emitted fail label no longer rewinds the capture trail (undo becomes a no-op; pos is still restored)"
SAB_DOC_FIGURE="tests/vm/run_vm_tests.sh: the oracle sweep fails (wrong spans across the backtracking families)"
SAB_COUNT=1
SAB_BEFORE="        \"        while (w->trn > w->bt[b_].mark) {\\n\""
SAB_AFTER="        \"        while (0 \&\& w->trn > w->bt[b_].mark) {  /* SABOTAGE S36 */\\n\""
