# S42 — [M4.5c] a CHOICE POINT that the listing never learns about. Same class
# as S41 and a different section: vm_push_at writes the RX_PUSH and records the
# VE_PUSH event, and this drops the recording while leaving the emitted C
# untouched. The artifact still backtracks exactly as before; only the dump
# stops saying so.
#
# This is the failure mode a program listing is MOST dangerous under, because
# the tool is used precisely when someone is trying to understand why a
# backtracking matcher did what it did — a listing that under-reports choice
# points sends the reader looking for a bug in the wrong place. Nothing about
# the matcher's behaviour changes, so no correctness test anywhere in the tree
# can see it.
SAB_ID="S42-ir-push-unrecorded"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="irlisting"
SAB_DESC="vm_push_at emits RX_PUSH but stops recording the VE_PUSH event (the artifact is unchanged; the listing loses every choice point)"
SAB_DOC_FIGURE="tests/codegen/run_ir_listing.sh: the CHOICE POINTS check fails for every pattern that backtracks"
SAB_COUNT=1
SAB_BEFORE="    vm_ev(v, VE_PUSH, lblid, 0, role);"
SAB_AFTER="    (void)role;  /* SABOTAGE S42: the choice point is emitted but not recorded */"
