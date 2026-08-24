# S144 ([DD-14] wave B+C, design SS9.3 S-SR2 and SS5.5's drawn cell) -- THE
# FAIL LABEL RESTORES WHICH ACTIVATION IS CURRENT.
#
# THIS ROW WAS REPRODUCED BEFORE THE LINE EXISTED, which is worth more than
# the prediction: the wave-B+C lane built the whole linkage without this line,
# and the failure it produced is exactly the one below. It is recorded here
# because a sabotage row whose signal has been SEEN is a different kind of
# evidence from one whose signal is predicted.
#
# THE MECHANISM, in SS5.5's own notation. On `^(a(?1)?b)$` / "aaabbb" the
# search reaches depth 3, fails, and retreats:
#
#   pop the innermost CALL frame     -> call_top must go back to the enclosing
#                                       activation's frame
#   pop an ordinary ALTERNATION frame pushed INSIDE that enclosing activation
#                                    -> call_top must STILL name it
#   the enclosing activation now succeeds and RETURNS
#
# Without the restore, `call_top` still names the POPPED call frame, whose
# `trail_mark` is one activation deeper -- so the return reads the WRONG three
# trail entries and restores the inner activation's saved values. Measured on
# the traced artifact: group 1 comes back (2,5) where the truth is (1,5), one
# level off at every depth, and the whole match is lost.
#
# THE PAIR IS WHAT NAMES IT. `"aabb"` (depth 2) stays GREEN under this
# sabotage, because at depth 2 there is only one activation to be current and
# the stale value happens to be right. Only a subject that reaches depth 3
# separates a correct compiler from this one, which is why the detector is the
# corpus rather than the shortest cell in it.
#
# AN ORDINARY FRAME CARRIES `call_top` TOO, and that is the half a reader is
# most likely to think redundant: `RX_PUSH` stores it because the SECOND pop
# above is an alternation frame, not a call frame. Deleting it there is the
# same defect through a different door.
#
# D71.1 AND THE DESIGN'S "TWO LINES". SS5.1/SS5.5 call this "the fail label's
# TWO lines" -- this one and `call_depth = resume_stack[..].call_mark`. Under
# D71.1 the second does not exist in the default artifact at all, because the
# recursion-depth COUNTER moved to a [V-H] diagnostic generation axis and
# calls consume ordinary frames. So there is ONE line here, it is the one
# SS9.3 already records as the one whose deletion changes ANSWERS, and
# S-SR2a (the other line's row) moves to that axis with it.
SAB_ID="S144-fail-label-call-top"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="The fail label stops restoring \`call_top\` from the popped frame, so after a retreat the CURRENT ACTIVATION is whatever the deepest call left behind -- every return then reads its trail_mark one level too deep and restores the wrong values"
SAB_DOC_FIGURE="REPRODUCED BEFORE THE LINE WAS WRITTEN, on this lane's own build: ^(a(?1)?b)\$ on \"aaabbb\" answers NOMATCH where it must be (0,4)... (0,6), and the traced artifact shows group 1 coming back (2,5) where it must be (1,5) -- one level off at EVERY depth. \"aabb\" (depth 2) stays green, which is the pair that names the failure."
SAB_COUNT=1
SAB_BEFORE='            v.has_calls
              ? "        run->call_top = run->resume_stack[frame_index]"
                ".call_top;\n"
              : "");'
SAB_AFTER='            "");   /* SABOTAGE S144: the fail label forgets the activation */'
