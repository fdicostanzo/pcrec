# S108 (design row S-BR4) — `rd_shape` GAINS AN ARM ACCEPTING `A_BREF`.
#
# THE ALARM SAYS AN ARM IS MISSING, NEVER WHICH ARM IS RIGHT, and that is the
# whole reason this is a row. Adding an `AKind` makes `rd_shape`'s switch raise
# `-Wswitch` under `make strict`; the author then has to choose, and ACCEPT is
# the plausible wrong choice.
#
# WHY IT MUST DECLINE. The reverse-deterministic rung recovers an iteration
# boundary by matching the REVERSED body from the right. A backreference's
# operand is not in its text — it is subject bytes a capture published — and
# there is no reversed spelling of "compare against what group k captured".
# `rd_reverse` runs only on a body this scan approved and its fallthrough
# COPIES, so an accepting arm here produces a reversed body that compares the
# same span while the walk runs the other way.
#
# Declining is always available and always safe (this file's own invariant),
# so the sabotage costs nothing to revert and everything to keep.
#
# ============================================================================
# THIS ROW IS NOT A CONTROL, AND THE MEASUREMENT SAYING SO IS BELOW.
# Recorded 2026-08-22 after it scored UNDETECTED in the 118-row matrix on
# 5edba64. Unlike S107 (a corpus gap on a real defect), NOTHING is missing
# here: the sabotage is UNOBSERVABLE, and the row's own prediction --
# "rd_reverse then raises its internal-error wall" -- is FALSE, because
# rd_reverse is never reached.
#
# WHAT ACTUALLY HAPPENS. `rd_rep` consults TWO gates in sequence, and this
# sabotage removes only the first:
#
#     rd_shape(&S, a->l);                        <-- this row's edit
#     if (S.ok && pcrec_uniq_iteration(...))     <-- the second gate
#         rev = rd_reverse(...);                 <-- the wall, never reached
#
# `pcrec_uniq_iteration` builds a Glushkov position automaton, and
# src/opt/possessify.c's own `case A_BREF:` sets `g->ok = false` -- a
# backreference consumes a variable amount of text, so it has NO POSITION and
# the (U1)/(U2) argument is not expressible over it. MEASURED with the
# sabotage applied and a probe printf in rd_rep, on four bodies built to be
# revdet-eligible except for the reference:
#
#     (x)(?:ab|\1){2,}y   rd_shape S.ok=1   uniq_iteration=0 why=model-error
#     (x)(?:\1){2,}y      rd_shape S.ok=1   uniq_iteration=0 why=model-error
#     (x)(?:a\1){2,}y     rd_shape S.ok=1   uniq_iteration=0 why=model-error
#     (ab)(?:\1cd){2,}y   rd_shape S.ok=1   uniq_iteration=0 why=model-error
#
# The sabotage DOES flip this arm's verdict (S.ok goes 0 -> 1); the second
# gate then declines every one of them, and the emitted artifact is
# BYTE-IDENTICAL to the clean build's for all four.
#
# THE WALL IS REAL, JUST UNREACHABLE. With BOTH declines removed -- this
# row's edit plus `g->ok = false` deleted from possessify.c's A_BREF arm --
# rd_reverse IS reached and fires exactly as its comment promises:
#
#     pcrec: internal error: a backreference reached the reverse-deterministic
#     body reversal, which its shape scan must decline (pattern offset 0)
#
# on `(x)(?:a\1){2,}y` and `(ab)(?:\1cd){2,}y`, exit 1. (`(x)(?:ab|\1){2,}y`
# still declines, with why=nullable-body: an ALT branch that is a bare
# reference is nullable. So a detecting body must be a CONCATENATION holding a
# reference, not an alternation with one as a branch.)
#
# WHY IT IS LEFT IN PLACE RATHER THAN RE-AIMED. The harness applies ONE
# before/after hunk in ONE file (run_sabotage_matrix.sh:198-220), so the
# two-hunk sabotage that WOULD be a control cannot be expressed today. The
# mirrored single edit -- removing only possessify.c's `g->ok = false` and
# leaving rd_shape intact -- is NOT a substitute for this row either: measured,
# it never reaches revdet (rd_shape still declines first) and its byte
# difference comes from POSSESSIFICATION instead ((x)(?:a\1){2,}y acquires
# "possessified unbounded repeat" and an RX_CUT), which is a different claim
# about a different pass. Both are recorded for the [M6.5] close; neither is
# a change this row can make on its own.
#
# EXPECT THIS ROW TO REPORT UNDETECTED. That is now a DOCUMENTED result, not
# a finding -- the same disposition S19 carries, and for the same reason: the
# honest limit of a one-hunk mutation against a defence-in-depth pair.
# ============================================================================
SAB_ID="S108-rdshape-accepts-bref"
SAB_FILE="src/opt/revdet.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/nested.rxt"
SAB_DESC="rd_shape ACCEPTS a backreference in a quantifier body instead of declining. MEASURED UNOBSERVABLE (2026-08-22): the arm's verdict does flip, but pcrec_uniq_iteration's Glushkov model declines every such body independently (why=model-error, possessify.c's own A_BREF arm), so rd_reverse and its internal-error wall are never reached and the artifact is byte-identical. Documented NOT A CONTROL -- see this row's header for the measurement and for the two-hunk sabotage that would be one"
SAB_DOC_FIGURE="MEASURED 2026-08-22: UNDETECTED, and expected to stay so. Emitted artifact byte-identical to clean on all four probe bodies; rd_reverse never called (uniq_iteration declines first, why=model-error). Not a corpus gap -- see header."
SAB_COUNT=1
SAB_BEFORE='        case A_BREF:
            S->ok = false;
            return;'
SAB_AFTER='        case A_BREF:
            return;   /* SABOTAGE S108: ACCEPT it */'
