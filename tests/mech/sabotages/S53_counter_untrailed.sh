# S53 — [ENG-BREP counter-K] THE COUNTER SLOT MADE UNTRAILED.
#
# The iteration counter is a TRAILED `stv` slot, and §2.2 is the argument for
# why it cannot be a plain local: one emitted body copy is re-entered at every
# iteration, so a resume into a body-internal choice point must find the counter
# at the value that iteration had. A plain store leaves the LAST value written,
# which is the value of whatever iteration ran most recently — not the one being
# resumed into.
#
# THIS IS THE RUNG'S CENTRAL CORRECTNESS CLAIM, and it is worth having a row
# rather than a paragraph: the note's own first draft proposed an untrailed
# local as a "saving" for the possessive arm, and R25 E5 showed it was a
# mandatory-phase MISCOMPILE. The saving was withdrawn; this row is what keeps
# it withdrawn.
#
# The witness must have a body with an INTERNAL CHOICE POINT — a body with none
# never resumes inside itself and cannot see the difference. `((a)|ab){0,12}c`
# and its siblings in patterns.txt are exactly that, and they select the counter
# rung at the default K (12 > 8), which R25 E2 makes a requirement rather than a
# hope: a witness that does not select the strategy tests the rung below it.
SAB_ID="S53-counter-untrailed"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="counterkdiff"
SAB_DESC="the counter's per-trip increment becomes a plain untrailed store, so a resume into a body choice point reads the wrong iteration count"
SAB_DOC_FIGURE="docs/design/counterk_impl/counterk_design.md §2.2"
SAB_COUNT=1
SAB_BEFORE='            vm_set(v, ctr, val, "counter rung: += K, once per TRIP");'
SAB_AFTER='            sb_printf(v->b, "    stv[%d] = %s;\n", ctr, val);  /* SABOTAGE S53 */'
