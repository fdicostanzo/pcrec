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
# RE-ANCHORED 2026-08-21 (sabanchors lane): [M4.6d] (MRL pruning) replaced
# the comment that used to sit right after this `if (a->greedy) {` — "consume
# greedily to the furthest position" moved up into the function's general
# doc comment (~line 1905) and this site's own comment became the MRL clamp
# explanation ("[M4.6d] THE CLAMP, FOLDED INTO THE SCAN'S OWN BOUND"). The
# `if (a->greedy) {` line itself is unmoved and still the span-loop cursor
# rung's greedy/lazy branch (the site vm_rolef/vm_rung_mark tag "span-loop
# cursor" just above it) — there are two other `if (a->greedy) {` sites in
# this file (the frames rung's retreat, the reverse-deterministic rung), and
# the MRL comment line disambiguates this one from those. Intent (the
# deterministic-body cursor rung ignores quantifier preference, always
# emitting its greedy shape) unchanged.
SAB_COUNT=1
SAB_BEFORE="    if (a->greedy) {
        /* [M4.6d] THE CLAMP, FOLDED INTO THE SCAN'S OWN BOUND (§4.6). Two"
SAB_AFTER="    if (1) {  /* SABOTAGE S39 */
        /* [M4.6d] THE CLAMP, FOLDED INTO THE SCAN'S OWN BOUND (§4.6). Two"
