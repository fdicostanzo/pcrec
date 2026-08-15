# S40 — [M4.5b] A CAPTURE-FREE PATTERN ROUTED ONTO THE VM. engine_m4.md §5.4's
# zero-regression claim is not "the VM is fast enough for them", it is that
# capture-free patterns DO NOT TOUCH ANY NEW CODE — same AST, same NFA, same
# DFA, same emitter, same bytes. That is a property of SELECTION, and selection
# is one line; a change that routes the wrong population is invisible to every
# correctness test in the tree, because the VM computes the same spans.
#
# The sabotage makes `auto` prefer the VM whenever the VM can compile the
# pattern, which is always. Every corpus pattern's emitted bytes move, at no
# cost in correctness — exactly the silent regression §5.4 exists to catch, and
# exactly the shape the TS-1 sabotages already showed can pass a whole suite.
SAB_ID="S40-vm-capfree-routed-to-vm"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="vmidentity"
SAB_DESC="engine selection under --engine=auto prefers the VM whenever it CAN compile, instead of only when the DFA cannot"
SAB_DOC_FIGURE="tests/codegen/run_vm_identity.sh: the §5.4 byte-identity gate fails (every capture-free corpus pattern's emitted C moves)"
SAB_COUNT=1
SAB_BEFORE="        fit.chosen = (mask & ENGM_DFA) ? ENGM_DFA : ENGM_VM;"
SAB_AFTER="        fit.chosen = ENGM_VM;  /* SABOTAGE S40 */"
