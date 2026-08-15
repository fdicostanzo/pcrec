# S39 — [M4.5b] THE CURSOR RUNG IGNORES LAZINESS. §2.2 property 3: greedy vs
# lazy is WHICH SIDE IS THE FALLTHROUGH, and D18's "options are compiled away"
# applied to quantifier preference means the emitted code must differ, not a
# run-time flag. The span-loop rung has its own greedy/lazy shapes (scan to the
# furthest position and retreat, vs. start at the low-water mark and extend),
# and it is easy to build only the first — this emitter did, and the oracle
# sweep caught it.
#
# Measured effect of the real bug: `(a*?)a` on "aa" gives [0,2) with group 1 =
# [0,1) where both oracles give [0,1) with group 1 = [0,0); `(a??)` matches one
# byte where it must match zero.
SAB_ID="S39-vm-cursor-always-greedy"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="vm"
SAB_DESC="the span-loop cursor emits its GREEDY shape for lazy quantifiers too (preference ignored on the deterministic-body rung)"
SAB_DOC_FIGURE="tests/vm/run_vm_tests.sh: the oracle sweep fails on every lazy quantifier over a deterministic body"
SAB_COUNT=1
SAB_BEFORE="    if (a->greedy) {
        /* consume greedily to the furthest position */"
SAB_AFTER="    if (1) {  /* SABOTAGE S39 */"
