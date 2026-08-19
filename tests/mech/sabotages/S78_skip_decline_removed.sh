# S78 — [M6.2 wave C] THE SKIP-ELIGIBILITY DECLINE REMOVED (§3.6.1 rows 3
# and 5).
#
# D11 rule 1: a self-loop skip advances `pos` WITHOUT consulting accept flags,
# and is unsound exactly when a state can accept at a position the skip
# passes. Before this module that was only EOL positions, which is why the
# bound is `n-1`. With a CLASS-INDEXED accept the bit can vary INSIDE a
# skipped run, and the `n-1` bound does not fix that.
#
# `pick_skip_states` cures it by DECLINING: a state whose accept bits differ
# across the class axis is not skip-eligible at all. This sabotage removes the
# decline, restoring the pre-wave eligibility test.
#
# WHY THIS ROW IS WAVE C's AND NOT WAVE B's, which is R30 E5 and the reason
# the design MOVED it here. `\b` cannot make this fire: its LEFT operand is
# part of the state identity, so it is constant across any run a skip passes.
# (The design also claimed its RIGHT operand was constant — that a skip set is
# a union of classes and therefore pins next-is-word — and WAVE B MEASURED
# THAT FALSE, which is why the decline exists rather than an intersection.
# Even so, no pattern wave B lands makes the decline observable.) The
# `(?m)$` family does: "is the next byte a newline" genuinely varies inside a
# run a skip set admits, so a state that self-loops on both `a` and `\n` and
# accepts only before the `\n` is skipped straight past its own accepting
# positions.
#
# A Wave B sabotage of this line would have been a check with NO FAILING
# DIRECTION in the wave the design calls most dangerous — exactly the
# check-design failure this project keeps recording. Here it has one.
SAB_ID="S78-skip-decline-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness mlinediff"
SAB_HARNESS_TARGET="tests/assertions/multiline.rxt"
SAB_DESC="pick_skip_states stops declining states whose accept varies across the class axis, so a (?m)\$-family self-loop skip advances past positions where the accept bit was true (D11 rule 1 under a class-indexed accept; the hazard §3.6.1 calls the most dangerous item in the module)"
SAB_DOC_FIGURE="tests/assertions/run_mline_diff.sh: the (?m)\$-with-quantifier patterns diverge from libpcre2; tests/assertions/multiline.rxt section 3 goes red"
SAB_COUNT=1
SAB_BEFORE='            if (state_acc_varies(&d->st[i])) continue;'
SAB_AFTER='            /* SABOTAGE S78: decline removed */'
