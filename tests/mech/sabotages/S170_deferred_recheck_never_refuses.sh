# S170 ([DD-14.LB]) -- THE DEFERRED RE-CHECK RESOLVES BUT NEVER REFUSES.
#
# S169's row deletes the pass; this one keeps it and takes away its VERDICT.
# `pcrec_lookaround_fix_widths` still runs, still computes the branch widths
# through the call graph, and simply ACCEPTS a body it just measured as
# variable or unbounded — the shape a "fix" that only wanted the parked cells
# to compile would have.
#
# THE CLAIM IT BREAKS is design SS3.4(d): a RECURSIVE callee inside a
# lookbehind has NO bounded width, and libpcre2 refuses exactly that itself
# (err 125, at the same offset pcrec names). The deferred re-check exists to
# refuse it too, at a pattern offset the hook recorded, and NOT merely to let
# the acyclic cases through.
#
# WHAT THE ARTIFACT DOES, PREDICTED: the three recursive/mutually-recursive/
# reaches-a-cycle blocks in the target file COMPILE. `la_widths` returns false
# part-way, so the width table holds whatever the arena left, and the emitted
# back-step steps back the wrong distance -- on the POSITIVE lookbehinds here
# the SS3.4 end-check turns that into a clean assertion failure, which is a
# WRONG ANSWER and not a crash. The row is therefore scored on the `perr`
# blocks, which is the opposite half of the file from S169's detector: a cell
# asserting a REFUSAL fails exactly when the refusal stops happening.
#
# THE TWO ROWS TOGETHER ARE WHY THE PASS IS NOT ONE STATEMENT. Recording
# without resolving (S169) and resolving without refusing (S170) are different
# failures with different signals, and a single row on either alone would leave
# the other undefended.
SAB_ID="S170-deferred-recheck-never-refuses"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/inlookaround.rxt"
SAB_DESC="the deferred width re-check computes each branch width through the call graph and then accepts the lookbehind whatever it measured, so a recursive callee inside a lookbehind COMPILES instead of being refused"
SAB_DOC_FIGURE="PREDICTED ([DD-14.LB]): the four perr blocks in tests/recursion/inlookaround.rxt fail -- three of them (recursive callee, mutual recursion, acyclic callee that reaches a cycle) now COMPILE where libpcre2 answers err 125, and the fourth (the ruled 1..2 capability limit) compiles too. The seven match blocks still pass, since their widths were resolvable anyway. MEASURED at [DD-14.LB], FINAL corpus: harness corpus:4fail/46pass, DETECTED -- exactly the four perr blocks, and NO match cell moved, which is the half that makes this row S169's complement rather than its duplicate."
SAB_COUNT=1
SAB_BEFORE='    if (!la_widths(cx, a->l, nbr, w, &lo, &hi)) {
        char buf[LA_MSG_MAX];
        la_width_refusal(buf, sizeof buf, lo, hi);
        ctx_fail(cx, a->u.look.at, "%s", buf);
    }'
SAB_AFTER='    (void)la_widths(cx, a->l, nbr, w, &lo, &hi);   /* SABOTAGE S170 */'
